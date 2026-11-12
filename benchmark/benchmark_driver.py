"""The benchmark driver: launch the whole benchmark, resumably, in the background.

The driver owns the *order* of the runs, the parallelism and the quota
behaviour; ``scripts/run_arm.py`` owns the container and the secret
hygiene. One run is one container.

The order is committed: the main scenario (the launch set, three
repeats, both arms, internet allowed) runs COMPLETELY first, and the
restricted scenario (the committed restricted set, three repeats, both
arms, ``--egress restricted``) runs after it. Within a scenario the
runs are shuffled with the committed seed and the two arms are
interleaved, so a prompt's two arms are not far apart in the order.

QUOTA BEHAVIOUR. A provider quota-exhausted or rate-limit answer is a
PAUSE, not a failed attempt: the driver stops launching new runs, waits
with a backoff (a long wait until the daily reset when the quota is
exhausted), and resumes. A run that was interrupted by the quota is
REPEATED FROM SCRATCH and is logged as ``quota-interrupted`` - never as
an infrastructure retry.

    python benchmark/benchmark_driver.py --launch-tag <tag> \
        --image-digest sha256:... --launch-checkout <dir> --run-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import statistics
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402
from typing import Callable, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agent_cwd  # noqa: E402  (the path is set up above)
import benchmark_launch  # noqa: E402  (the path is set up above)

DEFAULT_ENV = str(expand_home(r"<HOME>\Documents\CPSC\Biolab\.env.extracted"))
DEFAULT_BASELINE_WORKSPACE = str(expand_home(r"<HOME>\AppData\Local\Temp\opencode\baseline_wt"))
# The launch checkout is a clone: it has no data/ tree (the data is
# gitignored), so the curated data and the structure cache are mounted
# from the working repository's data directory.
DEFAULT_DATA_ROOT = str(expand_home(r"<HOME>\Documents\CPSC\AlloAgent-v2\data"))
DEFAULT_STRUCTURE_CACHE = str(expand_home(r"<HOME>\Documents\CPSC\AlloAgent-v2\data\structures_cache"))

# The live output: the live block is printed every PROGRESS_INTERVAL_S
# seconds for every run in flight, and the silence warning fires when
# nothing has been printed for SILENCE_WARNING_S seconds.
PROGRESS_INTERVAL_S = 30.0
SILENCE_WARNING_S = 300.0
# A run that does not advance its step number for this long is stalled:
# the driver stops instead of going deeper (the run is resumable).
STALL_S = 1800.0
# The per-run wall-clock cap of the plan (7200 s, two hours).
DEFAULT_WALL_CAP_S = 7200.0

_LAST_OUTPUT = {"ts": time.time(), "warned": False}


@dataclass
class RunSpec:
    """One run: one prompt, one repeat, one arm."""

    scenario: str
    arm: str
    prompt_id: str
    repeat: int
    log_path: Path | None = None

    @property
    def key(self) -> str:
        return f"{self.scenario}:{self.arm}:{self.prompt_id}:r{self.repeat}"

    @property
    def record_dir_name(self) -> str:
        return f"{self.prompt_id}_r{self.repeat}"


@dataclass
class DriverState:
    """Everything the driver records while it runs."""

    launch_tag: str = ""
    image_digest: str = ""
    seed: int = 20261026
    parallel: int = 4
    planned: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    started: int = 0
    rate_limited: int = 0
    quota_interrupted: int = 0
    infrastructure_retries: int = 0
    infrastructure_exhausted: int = 0
    max_attempts: int = 3
    attempts: dict[str, int] = field(default_factory=dict)
    launches: dict[str, int] = field(default_factory=dict)
    quota_pauses: list[dict] = field(default_factory=list)
    consecutive_pauses: int = 0
    tokens_total: int = 0
    mean_tokens: float = 0.0
    mean_wall_s: float = 0.0
    run_dir: Path | None = None
    quota_backoff_s: float = 300.0
    quota_exhausted_sleep_s: float = 3600.0
    lock: threading.Lock = field(default_factory=threading.Lock)
    throttle_latched: bool = False
    pause_until: float = 0.0
    pause_kind: str | None = None
    pause_count: int = 0
    planned_total: int = 0
    active: dict[str, dict] = field(default_factory=dict)
    timings: dict[str, dict] = field(default_factory=dict)
    finished_active_s: list[float] = field(default_factory=list)
    abort: bool = False
    abort_reason: str = ""

    @property
    def throttle_rate(self) -> float:
        return (self.rate_limited / self.started) if self.started else 0.0

    def as_dict(self) -> dict:
        return {
            "launch_tag": self.launch_tag,
            "image_digest": self.image_digest,
            "seed": self.seed,
            "planned": self.planned,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "started": self.started,
            "rate_limited": self.rate_limited,
            "quota_interrupted": self.quota_interrupted,
            "infrastructure_retries": self.infrastructure_retries,
            "infrastructure_exhausted": self.infrastructure_exhausted,
            "max_attempts": self.max_attempts,
            "quota_pauses": self.quota_pauses,
            "parallel": self.parallel,
            "throttle_latched": self.throttle_latched,
            "throttle_rate": round(self.throttle_rate, 4),
            "tokens_total": self.tokens_total,
            "mean_tokens": round(self.mean_tokens, 1),
            "mean_wall_s": round(self.mean_wall_s, 1),
            "timings": self.timings,
            "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def _log_line(log, message: str) -> None:
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    _LAST_OUTPUT["ts"] = time.time()
    _LAST_OUTPUT["warned"] = False
    if log is not None:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


class DynamicGate:
    """A concurrency gate whose limit can be lowered while it runs.

    The semaphore of the first driver could not lower the concurrency:
    the limit lived in the state and the semaphore kept its own count, so
    a rate limit reduced the reported parallelism and not the number of
    runs that were in flight.  The first rate limit has to lower the
    number of runs in flight at once, so the gate is dynamic.
    """

    def __init__(self, limit: int) -> None:
        self._cond = threading.Condition()
        self._limit = max(1, int(limit))
        self._active = 0

    @property
    def limit(self) -> int:
        with self._cond:
            return self._limit

    def set_limit(self, limit: int) -> None:
        with self._cond:
            self._limit = max(1, int(limit))
            self._cond.notify_all()

    def acquire(self) -> None:
        with self._cond:
            while self._active >= self._limit:
                self._cond.wait()
            self._active += 1

    def release(self) -> None:
        with self._cond:
            self._active -= 1
            self._cond.notify_all()


def _read_progress(record_dir: Path) -> dict:
    """The live progress of a run, from the harness's progress file."""
    out = {"step": 0, "tokens": 0, "last_tool": None, "elapsed_s": 0.0}
    path = Path(record_dir) / "progress.jsonl"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec.get("step"), int):
            out["step"] = rec["step"]
        tokens = rec.get("cumulative_tokens")
        if isinstance(tokens, dict) and isinstance(tokens.get("total_tokens"), int):
            out["tokens"] = tokens["total_tokens"]
        if rec.get("last_tool"):
            out["last_tool"] = rec["last_tool"]
        if isinstance(rec.get("elapsed_s"), (int, float)):
            out["elapsed_s"] = float(rec["elapsed_s"])
    return out


def _log_has_throttle(log_path) -> bool:
    """Does the run's container log carry a provider rate-limit answer?

    The markers are the provider's own words: a bare "429" is not one of
    them, because a residue number or a status line of an unrelated
    service carries it too.
    """
    if log_path is None:
        return False
    path = Path(log_path)
    if not path.is_file():
        return False
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 65536))
            tail = handle.read().decode("utf-8", "replace").lower()
    except OSError:
        return False
    markers = (
        "ratelimiterror",
        "rate_limit_error",
        "insufficient_quota",
        "insufficient balance",
        "quota exceeded",
        "daily limit reached",
    )
    if any(marker in tail for marker in markers):
        return True
    if "429" in tail and "minimax" in tail:
        return True
    return False


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def deferred_ids(launch_checkout: Path) -> set[str]:
    """The ids the launch set defers (K04 at the time of writing)."""
    path = launch_checkout / "benchmark" / "launch_prompt_set.json"
    if not path.is_file():
        return set()
    return {entry.get("id") for entry in _read_json(path).get("deferred", [])}


def launch_prompt_ids(launch_checkout: Path) -> list[str]:
    """The ids of the launch set (the deferred ones are excluded)."""
    path = launch_checkout / "benchmark" / "launch_prompt_set.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"the launch set is missing: {path}. The launch set is "
            f"committed before the launch; the driver refuses to guess it."
        )
    payload = _read_json(path)
    deferred = {entry.get("id") for entry in payload.get("deferred", [])}
    return [pid for pid in payload["launch_prompts"] if pid not in deferred]


def restricted_prompt_ids(launch_checkout: Path) -> list[str]:
    """The ids of the committed restricted set (the "yes" rows)."""
    path = launch_checkout / "benchmark" / "restricted_prompt_set.json"
    if not path.is_file():
        raise FileNotFoundError(f"the restricted prompt set is missing: {path}")
    payload = _read_json(path)
    deferred = deferred_ids(launch_checkout)
    return [
        row["id"]
        for row in payload["prompts"]
        if row.get("solvable_from_local_resources_alone") == "yes"
        and row["id"] not in deferred
    ]


def build_plan(
    launch_checkout: Path,
    scenario: str,
    repeats: int,
    seed: int,
) -> list[RunSpec]:
    """The ordered list of the runs of one scenario.

    The two arms are interleaved (every prompt/repeat unit contributes
    one run per arm) and the whole list is shuffled with the committed
    seed, so the order is reproducible and the arms progress together.
    """
    if scenario == "main":
        prompt_ids = launch_prompt_ids(launch_checkout)
    elif scenario == "restricted":
        prompt_ids = restricted_prompt_ids(launch_checkout)
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    specs: list[RunSpec] = []
    for prompt_id in prompt_ids:
        for repeat in range(1, repeats + 1):
            for arm in ("alloagent", "baseline"):
                specs.append(RunSpec(scenario, arm, prompt_id, repeat))
    rng = random.Random(seed)
    rng.shuffle(specs)
    return specs


def select_runs(plan: list[RunSpec], run_list: str) -> list[RunSpec]:
    """The runs of the plan that a run list names, in the order of the list.

    The run list is a JSON file with the runs to execute:
    ``[{"arm": "baseline", "prompt_id": "S01", "repeat": 1}, ...]``.  It
    selects a subset of a scenario (the rerun of the compromised runs of a
    finished scenario); the order of the file is the order of execution.
    """
    entries = json.loads(Path(run_list).read_text(encoding="utf-8"))
    index = {(spec.arm, spec.prompt_id, spec.repeat): spec for spec in plan}
    selected = []
    for entry in entries:
        key = (entry["arm"], entry["prompt_id"], int(entry["repeat"]))
        spec = index.get(key)
        if spec is None:
            raise ValueError(f"the run list names a run of another scenario: {key}")
        selected.append(spec)
    return selected


def _record_dir(run_dir: Path, spec: RunSpec) -> Path:
    return run_dir / spec.arm / spec.record_dir_name


def run_log_path(run_dir: Path | None, spec: RunSpec) -> Path | None:
    """The host path of the container log of a run."""
    if run_dir is None:
        return None
    return spec.log_path or (
        run_dir / "logs" / f"{spec.arm}_{spec.record_dir_name}.log")


def is_completed(run_dir: Path, spec: RunSpec) -> bool:
    """True when the run already has a completed record on disk."""
    summary = _record_dir(run_dir, spec) / "summary.json"
    if not summary.is_file():
        return False
    try:
        data = json.loads(summary.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return data.get("status") == "completed"


def move_aside(record_dir: Path, target_root: Path, label: str) -> Path | None:
    """Move a partial record directory aside; nothing is ever overwritten."""
    if not record_dir.exists():
        return None
    target_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    target = target_root / f"{stamp}_{label}"
    shutil.move(str(record_dir), str(target))
    return target


def attempt_dir(run_dir: Path, spec: RunSpec, attempt: int) -> Path:
    """Where the attempt of a run is kept when it is superseded."""
    return run_dir / "attempts" / f"{spec.arm}_{spec.record_dir_name}_attempt{attempt}"


def attempt_cause(run_dir: Path) -> str:
    """The cause of the attempt that is about to be superseded.

    A quota-interrupted attempt is a **pause**, not an infrastructure
    failure: the plan says the run is repeated from scratch and that the
    three-attempt budget of the infrastructure-failure rule must not be
    spent on it.  The cause is read from the record itself and written
    next to it, so the budget survives a restart of the driver.
    """
    summary = run_dir / "summary.json"
    try:
        data = json.loads(summary.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "infrastructure"
    if data.get("status") == "quota_interrupted":
        return "quota"
    return "infrastructure"


def attempts_on_disk(run_dir: Path | None, spec: RunSpec) -> int:
    """How many attempts of this run are on disk, of any cause."""
    if run_dir is None:
        return 0
    root = run_dir / "attempts"
    if not root.is_dir():
        return 0
    prefix = f"{spec.arm}_{spec.record_dir_name}_attempt"
    return sum(1 for entry in root.iterdir() if entry.is_dir() and entry.name.startswith(prefix))


def attempts_made(run_dir: Path | None, spec: RunSpec) -> int:
    """How many **infrastructure** attempts of this run are already on disk.

    A quota-interrupted attempt is kept (every attempt is kept) but it
    is not counted here: the three-attempt budget belongs to the
    infrastructure-failure rule, and a provider quota must not be able to
    spend it.
    """
    if run_dir is None:
        return 0
    root = run_dir / "attempts"
    if not root.is_dir():
        return 0
    prefix = f"{spec.arm}_{spec.record_dir_name}_attempt"
    counted = 0
    for entry in root.iterdir():
        if not entry.is_dir() or not entry.name.startswith(prefix):
            continue
        marker = entry / "attempt.json"
        if marker.is_file():
            try:
                cause = json.loads(marker.read_text(encoding="utf-8")).get("cause")
            except (OSError, ValueError):
                cause = None
            if cause == "quota":
                continue
        counted += 1
    return counted


def execute_plan(
    plan: Iterable[RunSpec],
    launcher: Callable[[RunSpec], dict],
    state: DriverState,
    sleep: Callable[[float], None] = time.sleep,
    log=None,
) -> dict:
    """Run the plan and return the state.

    The loop is deliberately independent of the subprocess plumbing:
    ``launcher`` takes one run spec and returns the run's summary dict.
    The pause, the backoff, the re-run of a quota-interrupted run and
    the throttle reduction all live here, so a test can drive them with
    a fake launcher and a fake sleep.
    """
    pending = deque(plan)
    results: list[dict] = []
    gate = DynamicGate(state.parallel)
    stop_event = threading.Event()
    index = {spec.key: position for position, spec in enumerate(pending, start=1)}
    with state.lock:
        state.planned_total = len(pending)

    def take_next() -> RunSpec | None:
        with state.lock:
            if not pending:
                return None
            return pending.popleft()

    def put_first(spec: RunSpec) -> None:
        with state.lock:
            pending.appendleft(spec)

    def wait_out_the_pause() -> None:
        """Wait while a quota or rate-limit pause is in force."""
        while True:
            with state.lock:
                if state.pause_count <= 0:
                    return
            time.sleep(0.05)

    def timing_of(spec: RunSpec) -> dict:
        with state.lock:
            record = state.timings.get(spec.key)
            if record is None:
                record = {
                    "run": spec.key,
                    "k": index.get(spec.key, 0),
                    "arm": spec.arm,
                    "prompt_id": spec.prompt_id,
                    "repeat": spec.repeat,
                    "first_start": time.time(),
                    "active_s": 0.0,
                    "attempts": 0,
                }
                state.timings[spec.key] = record
            return record

    def write_timing(record: dict) -> None:
        if state.run_dir is None:
            return
        path = Path(state.run_dir) / "rerun_timings.jsonl"
        try:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, default=str) + "\n")
        except OSError:
            pass

    def print_eta() -> None:
        with state.lock:
            durations = list(state.finished_active_s)
            completed = state.completed
            failed = state.failed
        parallel = max(1, gate.limit)
        if len(durations) < 3:
            return
        median = statistics.median(durations)
        remaining = max(0, state.planned_total - completed - failed)
        eta_s = median * math.ceil(remaining / parallel) if remaining else 0.0
        eta = time.time() + eta_s
        _log_line(
            log,
            f"ETA: the median of the {len(durations)} finished runs is {median:.0f} s; "
            f"{remaining} run(s) left at parallel {parallel} -> about "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(eta))} local "
            f"({eta_s / 3600:.1f} h)",
        )

    def print_live_state() -> None:
        now = time.time()
        with state.lock:
            active = list(state.active.values())
            pause_until = state.pause_until
            pause_kind = state.pause_kind
        for info in active:
            key = info["key"]
            progress = _read_progress(Path(info["record_dir"]))
            step = progress["step"]
            with state.lock:
                entry = state.active.get(key)
                last_step = entry.get("last_step") if entry else None
                changed_at = entry.get("changed_at", now) if entry else now
                if entry is not None:
                    if step != last_step:
                        changed_at = now
                    entry["last_step"] = step
                    entry["changed_at"] = changed_at
            stalled_for = now - changed_at
            if pause_until > now:
                status = f"{pause_kind or 'quota pause'}, waiting {int(pause_until - now)} s"
            elif stalled_for > STALL_S:
                status = f"STALLED: no step for {int(stalled_for)} s"
            elif _log_has_throttle(info.get("log_path")):
                status = "throttled (a rate-limit answer is in the run log)"
            else:
                status = "working"
            _log_line(
                log,
                f"LIVE k={info['k']}/{state.planned_total} arm={info['arm']} "
                f"prompt={info['prompt_id']} repeat={info['repeat']} "
                f"attempt={info['attempt']} step={step} tokens={progress['tokens']} "
                f"active={int(now - info['started'])}s "
                f"last_tool={progress['last_tool'] or '-'} state={status}",
            )
            if stalled_for > STALL_S:
                with state.lock:
                    if not state.abort:
                        state.abort = True
                        state.abort_reason = (
                            f"the run {key} has not advanced its step for "
                            f"{int(stalled_for)} s"
                        )
                _log_line(
                    log,
                    f"ABORT: {state.abort_reason}; the driver stops here instead of "
                    f"going deeper.  The batch is resumable: the same run directory "
                    f"and the same launch tag continue it.",
                )

    def printer_loop() -> None:
        while not stop_event.wait(PROGRESS_INTERVAL_S):
            try:
                print_live_state()
            except Exception as exc:  # noqa: BLE001
                _log_line(log, f"the live printer failed: {exc!r}")
            now = time.time()
            silence = now - _LAST_OUTPUT["ts"]
            if silence > SILENCE_WARNING_S and not _LAST_OUTPUT["warned"]:
                _LAST_OUTPUT["warned"] = True
                _log_line(log, f"WARNING: nothing has been printed for {int(silence)} s")

    def pause(spec: RunSpec, summary: dict, kind: str) -> None:
        with state.lock:
            state.consecutive_pauses += 1
            consecutive = state.consecutive_pauses
            if kind == "rate_limit":
                state.rate_limited += 1
                slept = min(
                    state.quota_backoff_s * (2 ** (consecutive - 1)),
                    state.quota_backoff_s * 10,
                )
                new_parallel = max(1, state.parallel // 2)
                if new_parallel < state.parallel:
                    state.parallel = new_parallel
                state.throttle_latched = True
            else:
                state.quota_interrupted += 1
                slept = state.quota_exhausted_sleep_s
            state.quota_pauses.append({
                "kind": kind,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "slept_s": slept,
                "run": spec.key,
            })
            state.pause_kind = kind
            state.pause_until = max(state.pause_until, time.time() + slept)
            state.pause_count += 1
        gate.set_limit(state.parallel)
        _log_line(
            log,
            f"RUN END k={index.get(spec.key, 0)}/{state.planned_total} "
            f"arm={spec.arm} prompt={spec.prompt_id} repeat={spec.repeat} "
            f"result=quota_interrupted ({kind}) "
            f"active={timing_of(spec).get('active_s', 0.0):.0f}s wait={slept:.0f}s "
            f"done={state.completed} failed={state.failed} "
            f"remaining={max(0, state.planned_total - state.completed - state.failed)} "
            f"parallel={gate.limit}",
        )
        _log_line(
            log,
            f"QUOTA PAUSE ({kind}) after {spec.key}: no new run is launched, "
            f"waiting {slept:.0f} s before resuming",
        )
        if kind == "rate_limit":
            _log_line(
                log,
                f"throttled: the parallelism is {gate.limit} from now on (it is "
                f"never raised again); the throttle rate is {state.throttle_rate:.3f}",
            )
        sleep(slept)
        with state.lock:
            state.pause_count = max(0, state.pause_count - 1)
            if state.pause_count == 0:
                state.pause_until = 0.0
        if state.run_dir is not None:
            moved = move_aside(
                _record_dir(state.run_dir, spec),
                state.run_dir / "quota_interrupted",
                f"{spec.arm}_{spec.record_dir_name}",
            )
            if moved is not None:
                _log_line(log, f"quota-interrupted: the partial record kept at {moved}")
        put_first(spec)
        _log_line(
            log,
            f"quota-interrupted: {spec.key} is repeated from scratch after the pause",
        )
        with state.lock:
            state.consecutive_pauses = max(0, state.consecutive_pauses - 1)

    def worker() -> None:
        while True:
            with state.lock:
                if state.abort:
                    return
            spec = take_next()
            if spec is None:
                return
            wait_out_the_pause()
            with state.lock:
                if state.abort:
                    return
            gate.acquire()
            try:
                if state.run_dir is not None and is_completed(state.run_dir, spec):
                    with state.lock:
                        state.skipped += 1
                        state.completed += 1
                    _log_line(log, f"run skipped (already completed): {spec.key}")
                    results.append({"status": "completed", "skipped": True})
                    continue
                # The launch number names the attempt directory (every
                # attempt is kept, of any cause); the infrastructure
                # attempt number spends the budget of the
                # infrastructure-failure rule (a quota pause does not).
                launch = (
                    attempts_on_disk(state.run_dir, spec)
                    + state.launches.get(spec.key, 0)
                    + 1
                )
                attempt = (
                    attempts_made(state.run_dir, spec)
                    + state.attempts.get(spec.key, 0)
                    + 1
                )
                with state.lock:
                    state.launches[spec.key] = launch
                    state.attempts[spec.key] = attempt
                if state.run_dir is not None:
                    superseded = _record_dir(state.run_dir, spec)
                    if superseded.exists():
                        target = attempt_dir(state.run_dir, spec, launch)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if target.exists():
                            shutil.rmtree(target)
                        cause = attempt_cause(superseded)
                        shutil.move(str(superseded), str(target))
                        (target / "attempt.json").write_text(
                            json.dumps(
                                {
                                    "cause": cause,
                                    "attempt": launch,
                                    "run": spec.key,
                                    "note": (
                                        "a quota-interrupted attempt is a pause; it "
                                        "is kept but it does not spend the "
                                        "infrastructure-failure budget"
                                    ),
                                },
                                indent=2,
                            ),
                            encoding="utf-8",
                        )
                        _log_line(
                            log,
                            f"the previous attempt of {spec.key} is kept at "
                            f"{target} (attempt {launch - 1}, cause {cause})",
                        )
                with state.lock:
                    state.started += 1
                timing = timing_of(spec)
                log_path = run_log_path(state.run_dir, spec)
                with state.lock:
                    state.active[spec.key] = {
                        "key": spec.key,
                        "k": index.get(spec.key, 0),
                        "arm": spec.arm,
                        "prompt_id": spec.prompt_id,
                        "repeat": spec.repeat,
                        "attempt": attempt,
                        "started": time.time(),
                        "record_dir": (
                            str(_record_dir(state.run_dir, spec))
                            if state.run_dir is not None else ""
                        ),
                        "log_path": str(log_path) if log_path else "",
                        "last_step": None,
                        "changed_at": time.time(),
                    }
                _log_line(
                    log,
                    f"RUN START k={index.get(spec.key, 0)}/{state.planned_total} "
                    f"arm={spec.arm} prompt={spec.prompt_id} repeat={spec.repeat} "
                    f"attempt={attempt} (launch {launch}) parallel={gate.limit}",
                )
                attempt_started = time.time()
                summary = launcher(spec) or {}
                attempt_active = time.time() - attempt_started
                with state.lock:
                    timing["active_s"] = timing.get("active_s", 0.0) + attempt_active
                    timing["attempts"] = timing.get("attempts", 0) + 1
                    state.active.pop(spec.key, None)
                kind = benchmark_launch.classify_provider_error(
                    f"{summary.get('error') or ''}\n{summary.get('traceback') or ''}"
                )
                if summary.get("status") == "quota_interrupted":
                    kind = summary.get("error_kind") or kind or "quota_exhausted"
                if kind:
                    pause(spec, summary, kind)
                elif summary.get("status") == "completed":
                    with state.lock:
                        state.completed += 1
                        tokens = int(
                            (summary.get("token_total") or {}).get("total_tokens") or 0)
                        state.tokens_total += tokens
                        wall = float(summary.get("wall_time_s") or 0.0)
                        done = state.completed + state.failed
                        state.mean_tokens = state.tokens_total / done if done else 0.0
                        state.mean_wall_s = (
                            (state.mean_wall_s * (done - 1) + wall) / done
                            if done else 0.0
                        )
                        state.finished_active_s.append(timing.get("active_s", 0.0))
                    _log_line(
                        log,
                        f"RUN END k={index.get(spec.key, 0)}/{state.planned_total} "
                        f"arm={spec.arm} prompt={spec.prompt_id} repeat={spec.repeat} "
                        f"result=completed tokens={tokens} "
                        f"steps={summary.get('n_steps')} wall={wall:.0f}s "
                        f"active={timing.get('active_s', 0.0):.0f}s "
                        f"done={state.completed} failed={state.failed} "
                        f"remaining={max(0, state.planned_total - state.completed - state.failed)} "
                        f"parallel={gate.limit}",
                    )
                    _log_line(
                        log,
                        f"run finished {spec.key}: status=completed "
                        f"steps={summary.get('n_steps')} "
                        f"tokens={(summary.get('token_total') or {}).get('total_tokens')} "
                        f"wall={summary.get('wall_time_s')}",
                    )
                    timing.update({
                        "result": "completed",
                        "tokens": tokens,
                        "steps": summary.get("n_steps"),
                        "wall_s": round(time.time() - timing["first_start"], 3),
                    })
                    timing["pause_s"] = round(
                        timing["wall_s"] - timing.get("active_s", 0.0), 3)
                    write_timing(timing)
                    print_eta()
                else:
                    _log_line(
                        log,
                        f"RUN END k={index.get(spec.key, 0)}/{state.planned_total} "
                        f"arm={spec.arm} prompt={spec.prompt_id} repeat={spec.repeat} "
                        f"result=failed cause={summary.get('error')!r} "
                        f"attempt={attempt} active={attempt_active:.0f}s "
                        f"done={state.completed} failed={state.failed} "
                        f"remaining={max(0, state.planned_total - state.completed - state.failed)} "
                        f"parallel={gate.limit}",
                    )
                    _log_line(
                        log,
                        f"run failed {spec.key}: {summary.get('error')!r} "
                        f"(attempt {attempt} of {state.max_attempts})",
                    )
                    if attempt < state.max_attempts:
                        with state.lock:
                            state.infrastructure_retries += 1
                        put_first(spec)
                        _log_line(
                            log,
                            f"infrastructure failure: {spec.key} is repeated "
                            f"from scratch (attempt {attempt + 1} of "
                            f"{state.max_attempts}); every attempt is kept",
                        )
                    else:
                        with state.lock:
                            state.failed += 1
                            state.infrastructure_exhausted += 1
                        _log_line(
                            log,
                            f"infrastructure failure: {spec.key} has used all "
                            f"{state.max_attempts} attempts; it stays failed",
                        )
                        timing.update({
                            "result": "failed",
                            "cause": summary.get("error"),
                            "wall_s": round(time.time() - timing["first_start"], 3),
                        })
                        timing["pause_s"] = round(
                            timing["wall_s"] - timing.get("active_s", 0.0), 3)
                        write_timing(timing)
                        print_eta()
                results.append(summary)
            finally:
                gate.release()

    threads = [
        threading.Thread(target=worker, daemon=True)
        for _ in range(max(1, state.parallel))
    ]
    printer = threading.Thread(target=printer_loop, daemon=True)
    printer.start()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    stop_event.set()
    printer.join(timeout=5.0)
    return state.as_dict()


def make_launcher(
    launch_checkout: Path,
    run_dir: Path,
    image: str,
    launch_tag: str,
    image_digest: str,
    expected_sha256: str,
    baseline_workspace: Path,
    data_root: Path,
    structure_cache: Path,
    env_source: str,
    egress: str,
    log=None,
    state: DriverState | None = None,
    wall_cap_s: float = DEFAULT_WALL_CAP_S,
) -> Callable[[RunSpec], dict]:
    """The real launcher: one container per run, through run_arm.py."""
    arm_workspace = {
        "alloagent": launch_checkout,
        "baseline": baseline_workspace,
    }

    def launcher(spec: RunSpec) -> dict:
        record_dir = _record_dir(run_dir, spec)
        if is_completed(run_dir, spec):
            _log_line(log, f"run skipped (already completed): {spec.key}")
            return {"status": "completed", "skipped": True}
        log_path = run_log_path(run_dir, spec)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        container_name = (
            f"alloagent_run_{spec.arm}_{spec.record_dir_name}_{os.getpid()}"
        )
        command = [
            sys.executable, str(launch_checkout / "scripts" / "run_arm.py"),
            "--arm", spec.arm,
            "--image", image,
            "--workspace", str(arm_workspace[spec.arm]),
            "--container-name", container_name,
            "--benchmark",
            "--benchmark-script", str(launch_checkout / "benchmark" / "run_benchmark.py"),
            "--benchmark-module", str(launch_checkout / "benchmark" / "benchmark_launch.py"),
            "--benchmark-dir", str(launch_checkout / "benchmark"),
            "--benchmark-prompt-id", spec.prompt_id,
            "--benchmark-repeat", str(spec.repeat),
            "--benchmark-out", f"/runs/{spec.arm}",
            "--launch-tag", launch_tag,
            "--image-digest", image_digest,
            "--expected-sha256", expected_sha256,
            "--run-dir", str(run_dir),
            "--data-root", str(data_root),
            "--structure-cache", str(structure_cache),
            "--env-source", env_source,
            "--log", str(log_path),
        ]
        if spec.scenario == "restricted":
            command += ["--egress", egress]
        if spec.arm == "baseline":
            command += [
                "--no-data-mounts",
                "--no-pocketminer-env",
                "--no-gpu-envs",
                "--dev-prompts-data-path", "/agent_cwd/data",
                "--workspace-read-only",
            ]
        _log_line(log, f"run started: {spec.key}")
        started = time.time()
        process = subprocess.Popen(command, cwd=str(launch_checkout))
        timed_out = False
        while True:
            try:
                process.wait(timeout=5)
                break
            except subprocess.TimeoutExpired:
                if wall_cap_s and (time.time() - started) > wall_cap_s:
                    timed_out = True
                    break
        if timed_out:
            _log_line(
                log,
                f"the wall-clock cap of {wall_cap_s:.0f} s is reached: the "
                f"container {container_name} is killed",
            )
            process.kill()
            subprocess.run(["docker", "rm", "-f", container_name],
                           capture_output=True, text=True)
            try:
                process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                pass
            return {
                "status": "failed",
                "error": f"the wall-clock cap of {wall_cap_s:.0f} s was reached",
            }
        summary_path = record_dir / "summary.json"
        if not summary_path.is_file():
            return {"status": "failed", "error": "no summary.json was written"}
        try:
            return json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {"status": "failed", "error": f"unreadable summary: {exc}"}

    return launcher


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--launch-tag", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--launch-checkout", required=True,
                        help="the clean checkout of the launch commit")
    parser.add_argument("--run-dir", required=True,
                        help="a host directory OUTSIDE the repository")
    parser.add_argument("--scenario", choices=("main", "restricted", "all"),
                        default="all")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument("--image", default="alloagent-eval:v6")
    parser.add_argument("--env-source",
                        default=os.environ.get("ALLOAGENT_ENV_SOURCE") or DEFAULT_ENV)
    parser.add_argument("--baseline-workspace", default=DEFAULT_BASELINE_WORKSPACE)
    parser.add_argument("--data-root", default=DEFAULT_DATA_ROOT)
    parser.add_argument("--structure-cache", default=DEFAULT_STRUCTURE_CACHE)
    parser.add_argument("--quota-backoff-s", type=float, default=300.0)
    parser.add_argument("--quota-exhausted-sleep-s", type=float, default=3600.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--run-list",
        help=(
            "A JSON file with the runs to execute, as a list of "
            '{"arm": ..., "prompt_id": ..., "repeat": ...}.  The order of '
            "the file is the order of execution (the shuffle is not "
            "applied).  It selects a subset of a scenario: the rerun of "
            "the compromised runs of a finished scenario."
        ),
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help=(
            "The infrastructure-failure budget of a run: the first attempt "
            "plus two repetitions.  A quota pause never spends it."
        ),
    )
    parser.add_argument(
        "--skip-canary",
        action="store_true",
        help=(
            "Skip the pre-launch canary (the check that two runs do not "
            "share the agent's working directory).  The canary is the "
            "pre-launch gate of the benchmark; skipping it is only for a "
            "dry run."
        ),
    )
    parser.add_argument(
        "--wall-cap-s",
        type=float,
        default=DEFAULT_WALL_CAP_S,
        help=(
            "The per-run wall-clock cap of the plan (7200 s).  A run that "
            "reaches it is killed and counted as an infrastructure "
            "failure."
        ),
    )
    args = parser.parse_args(argv)

    launch_checkout = Path(args.launch_checkout).resolve()
    run_dir = Path(args.run_dir).resolve()
    benchmark_dir = launch_checkout / "benchmark"
    if not benchmark_dir.is_dir():
        print(f"ERROR: {benchmark_dir} does not exist; the launch checkout is wrong")
        return 2
    expected = benchmark_launch.manifest_for_dir(benchmark_dir)
    expected_json = json.dumps(expected, sort_keys=True)

    scenarios = ["main", "restricted"] if args.scenario == "all" else [args.scenario]
    state = DriverState(
        launch_tag=args.launch_tag,
        image_digest=args.image_digest,
        seed=args.seed,
        parallel=args.parallel,
        quota_backoff_s=args.quota_backoff_s,
        quota_exhausted_sleep_s=args.quota_exhausted_sleep_s,
        max_attempts=args.max_attempts,
        run_dir=run_dir,
    )

    log_path = run_dir / "driver.log"
    run_dir.mkdir(parents=True, exist_ok=True)
    _log_line(log_path, f"the driver starts: tag={args.launch_tag} "
                        f"image={args.image} digest={args.image_digest} "
                        f"checkout={launch_checkout}")
    _log_line(log_path, "the benchmark inputs (sha256): " + json.dumps(expected, indent=2))

    if not args.dry_run and not args.skip_canary:
        canary_result = agent_cwd.canary(args.image)
        _log_line(log_path, "the canary (the agent working directory is per run): "
                            + json.dumps(canary_result))
        print("the canary: " + json.dumps(canary_result), flush=True)
        if not canary_result["passed"]:
            print("ERROR: the agent working directory is shared between runs; aborting")
            return 3

    for scenario in scenarios:
        try:
            plan = build_plan(launch_checkout, scenario, args.repeats, args.seed)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            print(f"ERROR: {exc}")
            return 2
        if args.run_list:
            plan = select_runs(plan, args.run_list)
        _log_line(log_path, f"the {scenario} scenario: {len(plan)} runs, "
                            f"seed {args.seed}, parallel {args.parallel}")
        if args.dry_run:
            for spec in plan:
                print(f"{spec.scenario:10s} {spec.arm:10s} {spec.prompt_id:5s} "
                      f"r{spec.repeat}")
            continue
        state.planned = len(plan)
        launcher = make_launcher(
            launch_checkout=launch_checkout,
            run_dir=run_dir,
            image=args.image,
            launch_tag=args.launch_tag,
            image_digest=args.image_digest,
            expected_sha256=expected_json,
            baseline_workspace=Path(args.baseline_workspace),
            data_root=Path(args.data_root) if args.data_root else (launch_checkout / "data"),
            structure_cache=(Path(args.structure_cache) if args.structure_cache
                             else launch_checkout / "data" / "structures_cache"),
            env_source=args.env_source,
            egress="restricted" if scenario == "restricted" else "open",
            log=log_path,
            state=state,
            wall_cap_s=args.wall_cap_s,
        )
        summary = execute_plan(plan, launcher, state, log=log_path)
        (run_dir / "driver_state.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        _log_line(log_path, f"the {scenario} scenario finished: {summary}")
        if state.abort:
            _log_line(
                log_path,
                f"ABORT: the driver stopped: {state.abort_reason}.  The batch "
                f"is resumable: the same run directory and the same launch tag "
                f"continue it.",
            )
            break

    (run_dir / "driver_state.json").write_text(
        json.dumps(state.as_dict(), indent=2), encoding="utf-8"
    )
    final = state.as_dict()
    print(json.dumps(final, indent=2))
    if args.dry_run:
        return 0
    return 0 if final["failed"] == 0 and final["completed"] >= final["planned"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

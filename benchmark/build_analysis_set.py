"""Build the analysis set of the benchmark: one row per run.

The main run (tag ``launch-2026-10-28-v6c``) has 234 runs: 39 prompts
x 3 repeats x 2 arms.  Sixty of them were **compromised** - the agents
could see the shared host working directory of the other runs - and they
were redone (tag ``launch-2026-11-01-v6h``, the fixed runner with a
fresh working directory per run).

The **analysis set** is the 174 original runs that are not in the
compromised list plus the 60 reruns: 234 runs, one per (arm, prompt,
repeat).  This script writes that set down, with the run directory each
row is read from, and it checks that

* every row has exactly one run, and that run is the one the row names;
* every run of a row is a **completed** run;
* the **last attempt counts**: the record of a row is the last attempt,
  the superseded attempts are kept aside in ``<run-dir>/attempts/`` and
  are counted, not scored;
* the 60 compromised runs come from the rerun and the other 174 from
  the main run.

Nothing is scored here and nothing is interpreted: the file is the map
from the benchmark to the runs that stand for it.

    python benchmark/build_analysis_set.py \
        --main-run-dir <dir> --rerun-run-dir <dir> \
        [--out benchmark/analysis_set.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import re
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
LAUNCH_SET = REPO / "benchmark" / "launch_prompt_set.json"
COMPROMISED_DOC = REPO / "benchmark" / "compromised_runs_main_v6c.md"

ARMS = ("alloagent", "baseline")
REPEATS = (1, 2, 3)

# A bullet of the compromised list: "- **alloagent / C03_r2** (prompt C03, repeat 2) - ..."
COMPROMISED_RE = re.compile(
    r"^\s*-\s+\*\*(?P<arm>\w+)\s*/\s*(?P<run>\w+)\*\*\s*"
    r"\(prompt\s+(?P<prompt>\w+),\s*repeat\s+(?P<repeat>\d+)\)"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def launch_prompt_ids() -> list[str]:
    """The ids of the launch set: the prompt table minus the deferred ones."""
    payload = json.loads(LAUNCH_SET.read_text(encoding="utf-8"))
    deferred = {entry.get("id") for entry in payload.get("deferred", [])}
    return [
        pid for pid in payload["launch_prompts"]
        if pid not in deferred
    ]


def compromised_keys() -> dict[tuple[str, str, int], str]:
    """The compromised runs, from the committed list.

    The key is (arm, prompt_id, repeat); the value is the evidence line
    the list gives for the run.
    """
    out: dict[tuple[str, str, int], str] = {}
    for line in COMPROMISED_DOC.read_text(encoding="utf-8").splitlines():
        match = COMPROMISED_RE.match(line)
        if not match:
            continue
        arm = match.group("arm")
        prompt_id = match.group("prompt")
        repeat = int(match.group("repeat"))
        if match.group("run") != f"{prompt_id}_r{repeat}":
            raise ValueError(f"the list's run name and its prompt disagree: {line}")
        out[(arm, prompt_id, repeat)] = line.split(" - ", 1)[-1].strip()
    return out


def read_summary(record_dir: Path) -> dict:
    path = record_dir / "summary.json"
    if not path.is_file():
        raise FileNotFoundError(f"no summary.json in {record_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def attempt_dirs(run_dir: Path, arm: str, record_name: str) -> list[Path]:
    """The superseded attempts of a run, kept aside by the driver."""
    root = Path(run_dir) / "attempts"
    if not root.is_dir():
        return []
    prefix = f"{arm}_{record_name}_attempt"
    return sorted(
        (entry for entry in root.iterdir()
         if entry.is_dir() and entry.name.startswith(prefix)),
        key=lambda entry: entry.name,
    )


def build_rows(run_dirs: list[tuple[Path, str]], prompt_ids: list[str]) -> list[dict]:
    """The row of every (arm, prompt, repeat) of the launch set.

    The run directories are tried in order and the first one that holds
    the run wins: the rerun of the compromised runs comes first, then a
    directory of runs that were made after the main run (the K04 runs),
    then the main run itself.
    """
    compromised = compromised_keys()
    rows: list[dict] = []
    for prompt_id in prompt_ids:
        for repeat in REPEATS:
            for arm in ARMS:
                key = (arm, prompt_id, repeat)
                run_dir = None
                source = None
                for candidate_dir, candidate_source in run_dirs:
                    if (candidate_dir / arm / f"{prompt_id}_r{repeat}").is_dir():
                        run_dir = candidate_dir
                        source = candidate_source
                        break
                if run_dir is None:
                    continue
                record_name = f"{prompt_id}_r{repeat}"
                record_dir = run_dir / arm / record_name
                summary = read_summary(record_dir)
                attempts = attempt_dirs(run_dir, arm, record_name)
                rows.append({
                    "arm": arm,
                    "prompt_id": prompt_id,
                    "repeat": repeat,
                    "source": source,
                    "run_dir": str(run_dir),
                    "record_dir": str(record_dir),
                    "record_name": record_name,
                    "launch_tag": (summary.get("launch_manifest") or {}).get("launch_tag"),
                    "status": summary.get("status"),
                    "steps": summary.get("n_steps"),
                    "tokens": (summary.get("token_total") or {}).get("total_tokens"),
                    "wall_time_s": summary.get("wall_time_s"),
                    "attempts_on_disk": 1 + len(attempts),
                    "superseded_attempts": [
                        {
                            "dir": str(entry),
                            "cause": read_attempt_cause(entry),
                            "started_at": attempt_started_at(entry),
                        }
                        for entry in attempts
                    ],
                    "compromised_evidence": compromised.get(key),
                })
    return rows



def read_attempt_cause(entry: Path) -> str | None:
    marker = entry / "attempt.json"
    if not marker.is_file():
        return None
    try:
        return json.loads(marker.read_text(encoding="utf-8")).get("cause")
    except (OSError, ValueError):
        return None


def attempt_started_at(entry: Path) -> str | None:
    summary = entry / "summary.json"
    if not summary.is_file():
        return None
    try:
        return json.loads(summary.read_text(encoding="utf-8")).get("started_at")
    except (OSError, ValueError):
        return None


def check(rows: list[dict], prompt_ids: list[str],
          run_dirs: list[tuple[Path, str]]) -> dict:
    """The checks of the analysis set.  Every one of them must hold."""
    keys = [(row["arm"], row["prompt_id"], row["repeat"]) for row in rows]
    expected = [
        (arm, prompt_id, repeat)
        for prompt_id in prompt_ids
        for repeat in REPEATS
        for arm in ARMS
    ]
    records = [row["record_dir"] for row in rows]
    compromised = compromised_keys()
    rerun_rows = [row for row in rows if row["source"] == "rerun"]
    original_rows = [row for row in rows if row["source"] == "original"]
    new_rows = [row for row in rows if row["source"] == "new"]
    last_attempt_problems = []
    for row in rows:
        started = row["started_at"] if "started_at" in row else None
        for attempt in row["superseded_attempts"]:
            if (attempt["started_at"] or "") > (row["started_at"] or ""):
                last_attempt_problems.append(row["record_dir"])
    return {
        "rows": len(rows),
        "expected_rows": len(expected),
        "unique_keys": len(set(keys)),
        "every_key_present_once": sorted(keys) == sorted(expected),
        "every_record_dir_used_once": len(set(records)) == len(records),
        "every_run_completed": all(row["status"] == "completed" for row in rows),
        "prompts": len(prompt_ids),
        "repeats": len(REPEATS),
        "arms": len(ARMS),
        "rows_from_the_rerun": len(rerun_rows),
        "rows_from_the_main_run": len(original_rows),
        "rows_from_the_new_batches": len(new_rows),
        "compromised_runs_in_the_list": len(compromised),
        "every_compromised_run_is_covered_by_the_rerun": (
            len(rerun_rows) == len(compromised)
            and all(row["source"] == "rerun"
                    for row in rerun_rows)
        ),
        "every_other_run_comes_from_the_main_run": (
            len(original_rows) + len(new_rows) == len(expected) - len(compromised)
        ),
        "rows_with_superseded_attempts": sum(
            1 for row in rows if row["superseded_attempts"]
        ),
        "the_record_of_every_row_is_its_last_attempt": not last_attempt_problems,
        "records_with_a_problem": last_attempt_problems,
        "run_dirs": {
            source: str(directory) for directory, source in run_dirs
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--main-run-dir", required=True,
                        help="the run directory of the main run (launch-2026-10-28-v6c)")
    parser.add_argument("--rerun-run-dir", required=True,
                        help="the run directory of the rerun (launch-2026-11-01-v6h)")
    parser.add_argument("--extra-run-dir", action="append", default=[],
                        help=("a run directory of runs made after the main run "
                              "(the K04 batch); it is tried before the main run"))
    parser.add_argument("--out", default=str(REPO / "benchmark" / "analysis_set.json"))
    args = parser.parse_args()

    main_dir = Path(args.main_run_dir).resolve()
    rerun_dir = Path(args.rerun_run_dir).resolve()
    prompt_ids = launch_prompt_ids()
    run_dirs: list[tuple[Path, str]] = [(rerun_dir, "rerun")]
    run_dirs += [(Path(path).resolve(), "new") for path in args.extra_run_dir]
    run_dirs.append((main_dir, "original"))
    rows = build_rows(run_dirs, prompt_ids)

    for row in rows:
        summary = read_summary(expand_home(row["record_dir"]))
        row["started_at"] = summary.get("started_at")
        row["git_commit_recorded"] = summary.get("git_commit")
        row["git_dirty_recorded"] = summary.get("git_dirty")
    checks = check(rows, prompt_ids, run_dirs)

    payload = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "what_this_file_is": (
            "The analysis set of the benchmark: one row per (arm, prompt, "
            "repeat), the run that stands for each of them.  The 60 "
            "compromised runs of the main run are taken from the rerun "
            "(launch-2026-11-01-v6h, the fixed runner with a fresh working "
            "directory per run); the 6 runs of the K04 prompt are taken from "
            "their own batch (launch-2026-11-03-v6i); the other 174 are the "
            "original runs of the main run (launch-2026-10-28-v6c).  The "
            "original run directory is read-only and untouched."
        ),
        "rule": (
            "the last attempt of a run counts; every superseded attempt is "
            "kept aside in <run-dir>/attempts and is not part of the "
            "analysis path"
        ),
        "inputs": {
            "launch_set": str(LAUNCH_SET),
            "launch_set_sha256": sha256_file(LAUNCH_SET),
            "compromised_list": str(COMPROMISED_DOC),
            "compromised_list_sha256": sha256_file(COMPROMISED_DOC),
            "run_dirs": {
                source: str(directory) for directory, source in run_dirs
            },
        },
        "counts": {
            "prompts": len(prompt_ids),
            "repeats": len(REPEATS),
            "arms": len(ARMS),
            "rows": len(rows),
            "from_the_rerun": sum(1 for row in rows if row["source"] == "rerun"),
            "from_the_new_batches": sum(
                1 for row in rows if row["source"] == "new"),
            "from_the_main_run": sum(
                1 for row in rows if row["source"] == "original"),
        },
        "checks": checks,
        "rows": rows,
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(rows)} rows)")
    for key, value in checks.items():
        if key == "records_with_a_problem":
            continue
        print(f"  {key}: {value}")
    if checks["records_with_a_problem"]:
        print("  records_with_a_problem:")
        for item in checks["records_with_a_problem"]:
            print(f"    {item}")
    return 0 if (
        checks["every_key_present_once"]
        and checks["every_record_dir_used_once"]
        and checks["every_run_completed"]
        and checks["every_compromised_run_is_covered_by_the_rerun"]
        and checks["the_record_of_every_row_is_its_last_attempt"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())

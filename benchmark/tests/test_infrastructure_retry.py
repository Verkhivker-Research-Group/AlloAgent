"""The infrastructure-failure rule of the driver.

An infrastructure failure (a run that did not complete, for a reason
that is neither a quota error nor a provider refusal) is repeated from
scratch, up to a fixed number of attempts. Every attempt is kept, and
only the last attempt of a run counts.

The rule is what keeps a flaky container from silently removing a run
from the benchmark, and what keeps a repeated run from hiding the fact
that it failed twice.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "benchmark"))

import benchmark_driver  # noqa: E402  (the path is set up above)


class FlakyLauncher:
    """Fails every attempt of one run, succeeds for the others.

    It writes the record the way the harness does, so the driver's
    attempt bookkeeping is exercised on real files.
    """

    def __init__(self, failing_key: str, run_dir: Path) -> None:
        self.failing_key = failing_key
        self.run_dir = run_dir
        self.calls: list[str] = []

    def __call__(self, spec) -> dict:
        self.calls.append(spec.key)
        record = self.run_dir / spec.arm / spec.record_dir_name
        record.mkdir(parents=True, exist_ok=True)
        if spec.key == self.failing_key:
            summary = {"status": "failed", "error": "APIConnectionError: Connection error."}
        else:
            summary = {"status": "completed", "n_steps": 2, "wall_time_s": 5.0,
                       "token_total": {"total_tokens": 10}}
        (record / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        return summary


def _plan() -> list:
    return [benchmark_driver.RunSpec("restricted", "alloagent", "S02", 1)]


def test_a_failed_run_is_repeated_up_to_the_attempt_limit(tmp_path):
    launcher = FlakyLauncher("restricted:alloagent:S02:r1", tmp_path)
    state = benchmark_driver.DriverState(parallel=1, run_dir=tmp_path, max_attempts=3)
    summary = benchmark_driver.execute_plan(
        _plan(), launcher, state, sleep=lambda _s: None)

    assert launcher.calls.count("restricted:alloagent:S02:r1") == 3, (
        "the run must be repeated up to the attempt limit")
    assert summary["infrastructure_retries"] == 2
    assert summary["infrastructure_exhausted"] == 1
    assert summary["failed"] == 1, "the run is one failed run, not three"
    assert summary["completed"] == 0


def test_every_attempt_is_kept_and_only_the_last_one_counts(tmp_path):
    launcher = FlakyLauncher("restricted:alloagent:S02:r1", tmp_path)
    state = benchmark_driver.DriverState(parallel=1, run_dir=tmp_path, max_attempts=3)
    benchmark_driver.execute_plan(_plan(), launcher, state, sleep=lambda _s: None)

    attempts = sorted(p.name for p in (tmp_path / "attempts").iterdir())
    assert len(attempts) == 2, attempts
    assert all("attempt" in name for name in attempts), attempts
    # The analysis path holds the last attempt only.
    last = tmp_path / "alloagent" / "S02_r1" / "summary.json"
    assert last.is_file()
    assert json.loads(last.read_text(encoding="utf-8"))["status"] == "failed"


def test_a_completed_run_is_not_repeated(tmp_path):
    launcher = FlakyLauncher("restricted:alloagent:S02:r1", tmp_path)
    record = tmp_path / "alloagent" / "S02_r1"
    record.mkdir(parents=True)
    (record / "summary.json").write_text(
        json.dumps({"status": "completed", "id": "S02"}), encoding="utf-8")
    state = benchmark_driver.DriverState(parallel=1, run_dir=tmp_path)
    summary = benchmark_driver.execute_plan(
        _plan(), launcher, state, sleep=lambda _s: None)
    assert launcher.calls == []
    assert summary["skipped"] == 1

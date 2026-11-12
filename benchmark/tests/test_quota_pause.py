"""The quota behaviour of the benchmark driver, with mocked provider answers.

A provider quota-exhausted or rate-limit answer is a PAUSE, not a
failed attempt. These tests use a fake launcher and a fake sleep, so
they run in milliseconds, touch neither the network nor docker, and
still exercise the real pause/backoff/re-run logic of the driver.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "benchmark"))

import benchmark_driver  # noqa: E402  (the path is set up above)
import benchmark_launch  # noqa: E402  (the path is set up above)

QUOTA_BODY = json.dumps({
    "base_resp": {"status_code": 1002, "status_msg": "insufficient balance"}
})


def test_a_mocked_429_is_a_rate_limit():
    assert benchmark_launch.classify_provider_response(429, "Too Many Requests") == "rate_limit"


def test_a_mocked_429_with_a_quota_body_is_a_quota_exhaustion():
    assert benchmark_launch.classify_provider_response(429, QUOTA_BODY) == "quota_exhausted"


def test_a_mocked_quota_exhaustion_without_a_429_is_still_a_quota_exhaustion():
    assert benchmark_launch.classify_provider_response(400, QUOTA_BODY) == "quota_exhausted"
    assert benchmark_launch.classify_provider_error(QUOTA_BODY) == "quota_exhausted"


def test_an_ordinary_error_is_not_a_quota_error():
    assert benchmark_launch.classify_provider_error("KeyError: 'residues'") is None


class FakeLauncher:
    """A launcher that fails one run with a quota error, once."""

    def __init__(self, failing_key: str, kind: str = "quota_exhausted") -> None:
        self.failing_key = failing_key
        self.kind = kind
        self.calls: list[str] = []

    def __call__(self, spec) -> dict:
        self.calls.append(spec.key)
        if spec.key == self.failing_key and self.calls.count(spec.key) == 1:
            return {
                "status": "quota_interrupted",
                "error_kind": self.kind,
                "error": QUOTA_BODY,
                "traceback": QUOTA_BODY,
            }
        return {"status": "completed", "n_steps": 3, "token_total": {"total_tokens": 100},
                "wall_time_s": 10.0}


def _plan(n: int = 3) -> list:
    return [
        benchmark_driver.RunSpec("main", "alloagent", f"P{i:02d}", 1)
        for i in range(n)
    ]


def _state(**kwargs) -> "benchmark_driver.DriverState":
    kwargs.setdefault("parallel", 1)
    return benchmark_driver.DriverState(**kwargs)


def test_a_quota_error_pauses_and_the_run_is_repeated_from_scratch(tmp_path):
    plan = _plan(3)
    launcher = FakeLauncher("main:alloagent:P01:r1")
    slept: list[float] = []
    state = _state(quota_backoff_s=300.0, quota_exhausted_sleep_s=3600.0,
                   run_dir=tmp_path)
    summary = benchmark_driver.execute_plan(
        plan, launcher, state, sleep=slept.append)

    assert state.quota_pauses, "the quota error must be recorded as a pause"
    pause = state.quota_pauses[0]
    assert pause["kind"] == "quota_exhausted"
    assert pause["slept_s"] == 3600.0
    assert slept == [3600.0], "a quota exhaustion waits for the daily reset"
    assert launcher.calls.count("main:alloagent:P01:r1") == 2, (
        "the interrupted run is repeated from scratch")
    assert summary["quota_interrupted"] == 1
    assert summary["failed"] == 0, (
        "a quota-interrupted run is not a failed attempt")


def test_the_pause_is_logged_as_quota_interrupted_and_not_as_a_retry(tmp_path):
    log = tmp_path / "driver.log"
    launcher = FakeLauncher("main:alloagent:P01:r1")
    benchmark_driver.execute_plan(
        _plan(2), launcher, _state(run_dir=tmp_path), sleep=lambda _s: None, log=log)
    text = log.read_text(encoding="utf-8")
    assert "quota-interrupted" in text
    assert "infrastructure retry" not in text


def test_a_rate_limit_reduces_the_parallelism_and_records_the_throttle(tmp_path):
    plan = _plan(2)
    launcher = FakeLauncher("main:alloagent:P01:r1", kind="rate_limit")
    slept: list[float] = []
    state = _state(parallel=4, quota_backoff_s=300.0, run_dir=tmp_path)
    summary = benchmark_driver.execute_plan(plan, launcher, state, sleep=slept.append)

    assert state.rate_limited == 1
    assert state.parallel == 2, "a rate limit lowers the parallelism"
    assert summary["throttle_rate"] > 0
    assert slept == [300.0], "a rate limit waits the backoff base"
    assert summary["quota_pauses"][0]["kind"] == "rate_limit"


def test_a_completed_record_is_not_run_again(tmp_path):
    record_dir = tmp_path / "alloagent" / "P00_r1"
    record_dir.mkdir(parents=True)
    (record_dir / "summary.json").write_text(
        json.dumps({"status": "completed", "id": "P00"}), encoding="utf-8")

    launcher = FakeLauncher("main:alloagent:P99:r1")
    state = _state(run_dir=tmp_path)
    summary = benchmark_driver.execute_plan(
        _plan(2), launcher, state, sleep=lambda _s: None)

    assert "main:alloagent:P00:r1" not in launcher.calls
    assert summary["skipped"] == 1
    assert summary["started"] == 1


def test_no_new_run_is_launched_while_the_pause_is_active(tmp_path):
    plan = _plan(3)
    launcher = FakeLauncher("main:alloagent:P01:r1")
    order: list[str] = []
    original = launcher.__call__

    def recording(spec):
        order.append(spec.key)
        return original(spec)

    slept: list[float] = []
    benchmark_driver.execute_plan(
        plan, recording, _state(parallel=1, run_dir=tmp_path), sleep=slept.append)
    assert len(order) == 4, "three runs plus the repeated interrupted one"
    assert slept, "the pause waited before the next run was launched"

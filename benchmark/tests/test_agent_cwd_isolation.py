"""The agent's working directory must not be shared between runs.

The benchmark runs of 2026-10-28 and 2026-10-29 mounted one host
directory as the agent's working directory for every run of both arms,
so a run's agent could read the files another run wrote (the baseline
arm read the curated ChEMBL records the alloagent arm had downloaded).
The runner now gives every run its own directory, and this file holds
the guard:

* the directory is fresh and empty for every run;
* it is removed with the run, and the shared directory is not;
* the **canary**: a container that writes a canary file into the working
  directory it is given must not be visible to a container given a
  different working directory - and the negative control (the same
  directory) must see it, so that the check cannot pass for the wrong
  reason.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "benchmark"))

import agent_cwd  # noqa: E402


def test_every_run_gets_its_own_working_directory() -> None:
    first = agent_cwd.make_agent_cwd(shared=False, label="alloagent_S01_r1")
    second = agent_cwd.make_agent_cwd(shared=False, label="alloagent_S01_r1")
    try:
        assert first != second
        assert list(first.iterdir()) == []
        assert list(second.iterdir()) == []
    finally:
        agent_cwd.cleanup_agent_cwd(first, shared=False)
        agent_cwd.cleanup_agent_cwd(second, shared=False)


def test_the_per_run_directory_is_removed_with_the_run() -> None:
    directory = agent_cwd.make_agent_cwd(shared=False, label="baseline_P01_r2")
    (directory / "a_file.txt").write_text("x", encoding="utf-8")
    agent_cwd.cleanup_agent_cwd(directory, shared=False)
    assert not directory.exists()


def test_the_shared_directory_is_never_removed() -> None:
    # The shared directory is a REAL directory of the machine
    # (%TEMP%\alloagent_agent_cwd): it holds the working files of the
    # development runs and, until the fix, the evidence of the
    # contamination.  The test must not touch it, so the shared path is
    # only inspected, never created or removed.
    import shutil
    import tempfile

    directory = agent_cwd.make_agent_cwd(shared=False, label="shared_probe")
    try:
        agent_cwd.cleanup_agent_cwd(directory, shared=True)
        assert directory.is_dir()
    finally:
        shutil.rmtree(directory, ignore_errors=True)
    shared = Path(tempfile.gettempdir()) / "alloagent_agent_cwd"
    assert not shared.exists() or shared.is_dir()


def test_the_runner_does_not_pass_the_shared_option() -> None:
    source = (REPO / "benchmark" / "benchmark_driver.py").read_text(encoding="utf-8")
    assert "--shared-agent-cwd" not in source


def test_the_driver_runs_the_canary_before_the_batch() -> None:
    source = (REPO / "benchmark" / "benchmark_driver.py").read_text(encoding="utf-8")
    assert "agent_cwd.canary(" in source
    assert "--skip-canary" in source


@pytest.mark.slow
def test_the_canary_proves_that_two_runs_do_not_share_the_directory() -> None:
    result = agent_cwd.canary()
    assert result["visible_in_the_writing_directory"] is True
    assert result["visible_in_another_directory"] is False
    assert result["the_other_directory_is_empty"] is True
    assert result["passed"] is True

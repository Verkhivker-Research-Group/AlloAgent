"""The agent's working directory must not be shared between runs.

A shared working directory is an isolation defect: the agent of one run
can read the files another run wrote, so the baseline arm read the
curated ChEMBL records that the alloagent arm had downloaded in the same
scenario (the restricted scenario of 2026-10-29).  The runner therefore
gives every run its own directory, and only the development runs may
opt into the shared one.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_ARM = REPO / "scripts" / "run_arm.py"
DRIVER = REPO / "benchmark" / "benchmark_driver.py"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_the_runner_offers_the_shared_directory_only_as_an_opt_in() -> None:
    source = _source(RUN_ARM)
    assert '"--shared-agent-cwd"' in source
    assert "action=\"store_true\"" in source


def test_the_default_working_directory_is_fresh_for_every_run() -> None:
    source = _source(RUN_ARM)
    tree = ast.parse(source)
    mkdtemp_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "mkdtemp"
    ]
    assert mkdtemp_calls, "the runner must create a fresh working directory per run"
    assert 'tempfile.gettempdir()) / "alloagent_agent_cwd"' in source
    assert "if args.shared_agent_cwd:" in source


def test_the_benchmark_driver_never_shares_the_working_directory() -> None:
    source = _source(DRIVER)
    assert "--shared-agent-cwd" not in source


def test_the_per_run_directory_is_removed_with_the_run() -> None:
    source = _source(RUN_ARM)
    assert "shutil.rmtree(agent_cwd, ignore_errors=True)" in source

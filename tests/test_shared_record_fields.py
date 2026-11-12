"""Both arms must record the same fields, and the records must land in a
host directory outside the repository.

The shared recorder change (the per-step cumulative tokens and elapsed
time) is on the baseline branch and merged into the alloagent branch,
so both arms' records carry the same fields; the harness records the
size of the tool set the arm actually had (the exposed list for arm D,
the upstream tool set for arm A); and the runner mounts a host run
directory so that the records, the answer texts and the traces of both
arms land in the same host directory and survive the container.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
BASELINE_REPO = Path(
    str(expand_home(r"<HOME>\AppData\Local\Temp\opencode\baseline_wt"))
)
HARNESS = REPO / "scripts" / "run_dev_prompts.py"
RUNNER = REPO / "scripts" / "run_arm.py"


def _written_keys_from_source(source: str, variable: str) -> set[str]:
    tree = ast.parse(source)
    written: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                    and target.value.id == variable and isinstance(target.slice, ast.Constant)):
                if isinstance(target.slice.value, str):
                    written.add(target.slice.value)
    return written


def _written_keys(path: Path, variable: str) -> set[str]:
    return _written_keys_from_source(path.read_text(encoding="utf-8"), variable)


def _baseline_recorder_source() -> str:
    """The baseline branch's recorder, read from git.

    The baseline worktree is not mounted in the container the suite
    runs in, so the branch's file is read from the object store
    instead - the branch is what the baseline arm runs.
    """
    import subprocess

    result = subprocess.run(
        # The bind-mounted repository is owned by another uid inside the
        # container, so git needs the safe-directory override.
        ["git", "-c", "safe.directory=*", "show", "baseline:biomni/agent/a1.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=60,
    )
    assert result.returncode == 0, (
        f"the baseline branch's recorder could not be read: {result.stderr[-200:]}")
    return result.stdout


def test_both_recorders_write_the_per_step_budget_fields():
    """The shared recorder: the alloagent branch and the baseline branch
    both write the elapsed time and the cumulative tokens per step."""
    alloagent = REPO / "biomni" / "agent" / "a1.py"
    assert alloagent.is_file()
    written = _written_keys(alloagent, "step")
    assert "elapsed_s" in written, "the alloagent recorder writes no elapsed time"
    assert "cumulative_tokens" in written, (
        "the alloagent recorder writes no cumulative tokens")

    baseline_source = _baseline_recorder_source()
    written = _written_keys_from_source(baseline_source, "step")
    assert "elapsed_s" in written, "the baseline recorder writes no elapsed time"
    assert "cumulative_tokens" in written, (
        "the baseline recorder writes no cumulative tokens")


def test_the_harness_records_the_size_of_the_tool_set():
    """The harness records the number of tools the arm had: the exposed
    list for arm D, the upstream tool set for arm A."""
    source = HARNESS.read_text(encoding="utf-8")
    assert "exposed_tool_count" in source, (
        "the harness does not record the size of the tool set")
    assert "apply_exposed_tools" in source
    assert "module2api" in source, (
        "the harness does not count the arm's own tool set for the baseline arm")
    tree = ast.parse(source)
    assigned = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert "exposed_tool_count" in assigned, (
        "the exposed tool count is never computed")


def test_the_runner_mounts_a_host_run_directory():
    """The runner mounts the host run directory read-write at /runs and
    points the harness's output at /runs/<arm>."""
    source = RUNNER.read_text(encoding="utf-8")
    assert '"--run-dir"' in source
    assert ':/runs"' in source, "the run directory is not mounted at /runs"
    assert 'dev_prompts_out = f"/runs/{args.arm}"' in source, (
        "the two arms do not write into the same host run directory")


def test_a_completed_run_is_kept_and_the_batch_is_resumable(tmp_path):
    """The resume: a prompt whose summary.json records a completed run is
    kept and not repeated."""
    sys.path.insert(0, str(REPO / "scripts"))
    import run_dev_prompts

    summary = tmp_path / "summary.json"
    summary.write_text(json.dumps({"id": "D2", "status": "completed"}), encoding="utf-8")
    kept = run_dev_prompts._completed_record(summary)
    assert kept is not None, "a completed run was not kept"
    assert kept.get("resumed") is True

    summary.write_text(json.dumps({"id": "D2", "status": "failed"}), encoding="utf-8")
    assert run_dev_prompts._completed_record(summary) is None, (
        "a failed run was kept as if it were complete")
    assert run_dev_prompts._completed_record(tmp_path / "missing.json") is None


def test_the_answer_text_and_the_trace_are_written_next_to_the_record():
    source = HARNESS.read_text(encoding="utf-8")
    assert '"answer.txt"' in source, "the answer text is not written to disk"
    assert '"trace.txt"' in source, "the trace is not written to disk"

"""The judge export: the masking holds.

The exporter (`benchmark/export_judge_batches.py`) writes the masked judge
batches of the analysis set.  These tests check the properties the
template's exporter requirements ask for:

* no arm name and no persona name in any batch;
* no batch holds more than ten runs;
* every run of the analysis set appears exactly once, in one batch;
* the key is not in the batch folder;
* the run ids carry nothing of the run they name: they are not derived
  from the arm, the prompt or the repeat.

The export is run into a temporary folder, so the test needs the run
records of the analysis set (they are read only).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
EXPORTER = REPO / "benchmark" / "export_judge_batches.py"
ANALYSIS_SET = REPO / "benchmark" / "analysis_set.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
DRAFT = REPO / "benchmark" / "benchmark_draft.json"

# The arm names, the branch names and the persona name.  None of them
# may appear in a batch: the judge must not be able to tell the arm.
# The persona name is "AlloAgent", already listed as an arm name.
ARM_NAMES = (
    "alloagent",
    "AlloAgent",
    "AlloAgent-v2",
    "baseline",
    "baseline_wt",
    "baseline_wt_gate",
)
ARM_LABEL_RE = re.compile(r"\barm\s*[AD]\b", re.IGNORECASE)
RUN_BLOCK_RE = re.compile(r"^=== RUN (\S+) ===$", re.MULTILINE)


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    """The exported batches, the key and the redaction report."""
    out_dir = tmp_path_factory.mktemp("judge_batches")
    key_out = out_dir.parent / "judge_key.json"
    result = subprocess.run(
        [sys.executable, str(EXPORTER),
         "--out-dir", str(out_dir),
         "--key-out", str(key_out),
         "--seed", "20261102"],
        cwd=str(REPO), capture_output=True, text=True, timeout=1800,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    batches = sorted(out_dir.glob("judge_batch_*.md"))
    assert batches, "the exporter wrote no batch"
    key = json.loads(key_out.read_text(encoding="utf-8"))
    return out_dir, batches, key, key_out


def test_no_arm_name_or_persona_name_in_any_batch(exported):
    out_dir, batches, key, _ = exported
    for path in batches:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for name in ARM_NAMES:
            assert name.lower() not in lowered, (
                f"{path.name} carries the arm name or the persona name {name!r}")
        assert not ARM_LABEL_RE.search(text), (
            f"{path.name} carries an arm label")


def test_no_batch_holds_more_than_ten_runs(exported):
    out_dir, batches, key, _ = exported
    for path in batches:
        runs = RUN_BLOCK_RE.findall(path.read_text(encoding="utf-8"))
        assert len(runs) <= 10, f"{path.name} holds {len(runs)} runs"
        assert runs, f"{path.name} holds no run"


def test_every_run_of_the_analysis_set_appears_exactly_once(exported):
    out_dir, batches, key, _ = exported
    analysis_set = json.loads(ANALYSIS_SET.read_text(encoding="utf-8"))
    expected = {
        (row["arm"], row["prompt_id"], row["repeat"])
        for row in analysis_set["rows"]
    }
    seen = []
    for path in batches:
        seen.extend(RUN_BLOCK_RE.findall(path.read_text(encoding="utf-8")))
    assert len(seen) == len(set(seen)), "a run id appears in two places"
    assert len(seen) == len(expected) == 240, (
        f"the batches hold {len(seen)} runs, the analysis set has {len(expected)}")
    mapped = {
        (row["arm"], row["prompt_id"], row["repeat"])
        for row in key["runs_key"]
    }
    assert mapped == expected, "the key does not cover the analysis set"


def test_the_key_is_not_in_the_batch_folder(exported):
    out_dir, batches, key, key_out = exported
    assert key_out.parent != out_dir, "the key sits in the batch folder"
    for path in out_dir.iterdir():
        assert "key" not in path.name.lower(), (
            f"{path.name} looks like the key")
    for path in batches:
        text = path.read_text(encoding="utf-8")
        assert '"arm"' not in text, f"{path.name} carries an arm field"
        assert "record_dir" not in text, f"{path.name} carries a record path"


def test_the_run_ids_carry_nothing_of_the_run(exported):
    out_dir, batches, key, _ = exported
    prompt_ids = {
        row["id"] for row in json.loads(DRAFT.read_text(encoding="utf-8"))
    }
    arms = {"alloagent", "baseline"}
    ids = [row["run_id"] for row in key["runs_key"]]
    assert len(ids) == len(set(ids)), "two runs share a run id"
    for row in key["runs_key"]:
        run_id = row["run_id"].lower()
        assert row["prompt_id"].lower() not in run_id, (
            f"the run id {row['run_id']} carries the prompt id")
        assert row["arm"].lower() not in run_id, (
            f"the run id {row['run_id']} carries the arm")
        assert f"r{row['repeat']}" not in run_id, (
            f"the run id {row['run_id']} carries the repeat")
        assert row["record_dir"].replace("\\", "/").split("/")[-1].lower() not in run_id, (
            f"the run id {row['run_id']} carries the record name")
    for prompt_id in prompt_ids:
        assert all(prompt_id.lower() not in run_id.lower() for run_id in ids), (
            f"the prompt id {prompt_id} appears in a run id")
    for arm in arms:
        assert all(arm.lower() not in run_id.lower() for run_id in ids), (
            f"the arm name {arm} appears in a run id")
    # The ids are not handed out arm by arm: the arms of the ids, in id
    # order, are not grouped.
    by_id = sorted(key["runs_key"], key=lambda row: row["run_id"])
    order = [row["arm"] for row in by_id]
    assert order != sorted(order), "the run ids are ordered by arm"


def test_every_batch_is_self_contained(exported):
    out_dir, batches, key, _ = exported
    for path in batches:
        text = path.read_text(encoding="utf-8")
        assert "## Instructions to the judge" in text, (
            f"{path.name} has no instructions")
        assert "CHECKLIST (ground truth):" in text, (
            f"{path.name} has no checklist section")
        assert "FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):" in text, (
            f"{path.name} has no answer section")
        assert "=== END RUN" in text, f"{path.name} has an unclosed run block"


REASONING_MARKERS = (
    "<think>", "</think>", "<observation>", "</observation>",
    "<execute>", "</execute>", "chain of thought", "scratchpad",
)
# These two are ordinary words: they may survive in a final answer that
# talks about the protocol, and they are listed in the report.
PROSE_MARKERS = ("reasoning", "thinking")


def run_blocks(text: str) -> dict[str, str]:
    """The run id -> the answer text of every run block of a batch."""
    blocks: dict[str, str] = {}
    pattern = re.compile(
        r"^=== RUN (\S+) ===$(.*?)^=== END RUN \S+ ===$", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(text):
        body = match.group(2)
        marker = "FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):"
        if marker not in body:
            continue
        answer = body.split(marker, 1)[1]
        blocks[match.group(1)] = answer.strip()
    return blocks


def test_no_reasoning_is_in_any_batch(exported):
    out_dir, batches, key, _ = exported
    for path in batches:
        text = path.read_text(encoding="utf-8")
        for marker in REASONING_MARKERS:
            assert marker not in text.lower(), (
                f"{path.name} carries the reasoning marker {marker!r}")
        for run_id, answer in run_blocks(text).items():
            for marker in REASONING_MARKERS:
                assert marker not in answer.lower(), (
                    f"{path.name} / {run_id} carries {marker!r} in its answer")


def test_no_reasoning_is_in_any_rating_file(exported, tmp_path):
    out_dir, batches, key, _ = exported
    import importlib.util

    spec = spec_from_file_location(
        "human_subset_drawer", REPO / "benchmark" / "draw_human_subset.py")
    drawer = module_from_spec(spec)
    spec.loader.exec_module(drawer)
    rating_dir = tmp_path / "human_subset_30"
    result = subprocess.run(
        [sys.executable, str(REPO / "benchmark" / "draw_human_subset.py"),
         "--out-dir", str(rating_dir),
         "--key-out", str(tmp_path / "human_subset_key.json")],
        cwd=str(REPO), capture_output=True, text=True, timeout=1800,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    files = sorted(rating_dir.glob("human_run_*.md"))
    assert len(files) == 30
    for path in files:
        text = path.read_text(encoding="utf-8")
        for marker in REASONING_MARKERS:
            assert marker not in text.lower(), (
                f"{path.name} carries the reasoning marker {marker!r}")


def test_every_number_of_a_retained_answer_is_in_the_original(exported):
    """No number of a retained answer was invented by the redaction.

    The original is the agent's final response: the last message of the
    record, with the reasoning the harness records apart.  The record's
    ``final_content`` keeps only the first 20 000 characters, so it can
    be shorter than the final answer.
    """
    out_dir, batches, key, _ = exported
    records = {row["run_id"]: row["record_dir"] for row in key["runs_key"]}
    for path in batches:
        for run_id, answer in run_blocks(path.read_text(encoding="utf-8")).items():
            data = json.loads(
                (Path(records[run_id]) / "run.json").read_text(encoding="utf-8"))
            last = (data.get("messages") or [{}])[-1]
            original = (str(last.get("content") or "")
                        + str(last.get("reasoning_content") or ""))
            numbers_original = Counter(re.findall(r"\d+(?:\.\d+)?", original))
            numbers_answer = Counter(re.findall(r"\d+(?:\.\d+)?", answer))
            missing = numbers_answer - numbers_original
            assert not missing, (
                f"{path.name} / {run_id}: the answer holds numbers the agent's "
                f"final response does not: {sorted(missing.elements())[:5]}")


def test_the_key_default_is_outside_the_repository():
    """The key says which arm every run came from: it never goes into the repo."""
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location(
        "judge_batch_exporter", REPO / "benchmark" / "export_judge_batches.py")
    exporter = module_from_spec(spec)
    spec.loader.exec_module(exporter)
    assert not exporter._is_inside_the_repository(exporter.DEFAULT_KEY_PATH), (
        "the default key path is inside the repository")
    assert exporter._is_inside_the_repository(exporter.DEFAULT_OUT_DIR), (
        "the default batch folder should be inside the repository")
    # The exporter refuses a key inside the repository.
    result = subprocess.run(
        [sys.executable, str(EXPORTER),
         "--out-dir", str(REPO / "benchmark" / "judging" / "judge_batches"),
         "--key-out", str(REPO / "judge_key.json")],
        cwd=str(REPO), capture_output=True, text=True, timeout=1800,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert not (REPO / "judge_key.json").exists(), (
        "the exporter wrote a key inside the repository")


def test_the_redaction_report_says_no_number_changed(exported):
    out_dir, batches, key, key_out = exported
    report = json.loads((out_dir / "judge_redaction_report.json").read_text(
        encoding="utf-8"))
    assert report["runs_whose_redaction_failed"] == [], (
        "a redaction changed a number or left a name in an answer")
    assert report["runs"] == 240
    assert sum(report["runs_per_batch"]) == 240
    assert max(report["runs_per_batch"]) <= 10

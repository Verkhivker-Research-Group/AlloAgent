"""The judge-batch scripts: masked, shuffled and reproducible.

The LLM judge scores the qualitative checklist items, and it must not be
able to tell which arm produced an answer.  The guard checks that:

* the batch holds one entry per (run, qualitative item);
* the batch file carries no arm label - not in a field, not in a key;
* the key file maps every judge id back to its arm;
* a superseded tree (a quota-interrupted run) contributes nothing;
* the batch is reproducible: the same seed gives the same bytes;
* the human subset is 30 distinct prompts of the committed launch set,
  drawn with the committed shuffle seed.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
JUDGE_SCRIPT = REPO / "benchmark" / "make_judge_batches.py"
SUBSET_SCRIPT = REPO / "benchmark" / "make_human_subset.py"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
LAUNCH_SET = REPO / "benchmark" / "launch_prompt_set.json"

PROMPT_ID = "P01"
ARMS = ("alloagent", "baseline")
SEED = 20261026


def _write_summary(
    run_root: Path, arm: str, directory: str, answer: str, status: str = "completed"
) -> None:
    run_dir = run_root / arm / directory
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": PROMPT_ID,
        "prompt_id": PROMPT_ID,
        "repeat": 1,
        "prompt": "Which pocket of the protein holds the ligand?",
        "final_content": answer,
        "status": status,
        "n_steps": 3,
        "wall_time_s": 12.5,
        "token_total": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
        "git_dirty": False,
    }
    (run_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_run_root(root: Path) -> Path:
    """A tiny fake run directory: two arms, one run each, and one
    quota-interrupted run that must be skipped."""
    run_root = root / "runs"
    _write_summary(run_root, "alloagent", f"{PROMPT_ID}_r1", "the first answer")
    _write_summary(run_root, "baseline", f"{PROMPT_ID}_r1", "the second answer")
    _write_summary(
        run_root,
        "quota_interrupted",
        f"20261028T093803Z_baseline_{PROMPT_ID}_r1",
        "the superseded answer",
    )
    return run_root


def _run_judge(run_root: Path, out: Path, key: Path, manifest: Path | None = None):
    command = [
        sys.executable,
        str(JUDGE_SCRIPT),
        str(run_root),
        "--out",
        str(out),
        "--key",
        str(key),
    ]
    if manifest is not None:
        command += ["--manifest", str(manifest)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=str(REPO))
    assert result.returncode == 0, result.stderr
    return result


@pytest.fixture()
def judge_batch(tmp_path):
    run_root = _build_run_root(tmp_path)
    out = tmp_path / "batch.json"
    key = tmp_path / "key.json"
    manifest = tmp_path / "manifest.json"
    result = _run_judge(run_root, out, key, manifest)
    return {
        "batch_path": out,
        "key_path": key,
        "manifest_path": manifest,
        "stdout": result.stdout,
    }


def _qualitative_items(prompt_id: str) -> list[dict]:
    payload = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    for prompt in payload["prompts"]:
        if prompt["id"] == prompt_id:
            return [
                item for item in prompt["checklist"] if item["kind"] == "qualitative"
            ]
    raise AssertionError(f"{prompt_id} is not in the committed checklist")


def test_the_batch_has_one_entry_per_qualitative_item(judge_batch):
    batch = json.loads(judge_batch["batch_path"].read_text(encoding="utf-8"))
    items = _qualitative_items(PROMPT_ID)
    assert items, "the fixture prompt must carry qualitative items"
    assert len(batch) == 2 * len(items), "one entry per (run, qualitative item)"
    assert {entry["criterion"] for entry in batch} == {
        item["value"] for item in items
    }
    for entry in batch:
        assert entry["prompt_id"] == PROMPT_ID
        assert entry["prompt"]
        assert entry["criterion_note"] == next(
            item["note"]
            for item in items
            if item["value"] == entry["criterion"]
        )


def test_the_batch_carries_no_arm_label(judge_batch):
    text = judge_batch["batch_path"].read_text(encoding="utf-8").lower()
    for arm in ARMS:
        assert arm not in text, f"the batch leaks the arm label {arm!r}"
    batch = json.loads(judge_batch["batch_path"].read_text(encoding="utf-8"))
    for entry in batch:
        assert set(entry) == {
            "judge_id",
            "prompt_id",
            "prompt",
            "criterion",
            "criterion_note",
            "answer",
        }, "the batch's own keys must not hint at the arm"


def test_the_key_maps_every_judge_id_to_an_arm(judge_batch):
    batch = json.loads(judge_batch["batch_path"].read_text(encoding="utf-8"))
    key = json.loads(judge_batch["key_path"].read_text(encoding="utf-8"))
    assert len(key) == len(batch)
    assert {entry["judge_id"] for entry in key} == {
        entry["judge_id"] for entry in batch
    }
    for entry in key:
        assert entry["arm"] in ARMS
        assert entry["prompt_id"] == PROMPT_ID
        assert entry["repeat"] == 1
        assert entry["item_key"]
        assert entry["status"] == "completed"
        assert len(entry["answer_sha256"]) == 64


def test_the_superseded_tree_contributes_nothing(judge_batch):
    batch_text = judge_batch["batch_path"].read_text(encoding="utf-8")
    assert "the superseded answer" not in batch_text, (
        "a quota-interrupted run is not a run of the benchmark")
    key = json.loads(judge_batch["key_path"].read_text(encoding="utf-8"))
    run_ids = {entry["judge_id"].rsplit("_item_", 1)[0] for entry in key}
    assert len(run_ids) == 2, "only the two real runs may be in the batch"


def test_the_items_of_one_run_stay_together(judge_batch):
    batch = json.loads(judge_batch["batch_path"].read_text(encoding="utf-8"))
    run_parts = [entry["judge_id"].rsplit("_item_", 1)[0] for entry in batch]
    consecutive = [part for index, part in enumerate(run_parts)
                   if index == 0 or run_parts[index - 1] != part]
    assert len(consecutive) == len(set(consecutive)), (
        "the items of one run have to stay together and consecutive")
    assert len(set(run_parts)) == 2


def test_the_manifest_records_the_reproducibility(judge_batch):
    manifest = json.loads(judge_batch["manifest_path"].read_text(encoding="utf-8"))
    batch = json.loads(judge_batch["batch_path"].read_text(encoding="utf-8"))
    assert manifest["seed"] == SEED
    assert manifest["n_runs"] == 2
    assert manifest["n_items"] == len(batch)
    assert manifest["batch_sha256"] == hashlib.sha256(
        judge_batch["batch_path"].read_bytes()
    ).hexdigest()
    assert manifest["key_sha256"] == hashlib.sha256(
        judge_batch["key_path"].read_bytes()
    ).hexdigest()
    assert manifest["checklists_sha256"] == hashlib.sha256(
        CHECKLISTS.read_bytes()
    ).hexdigest()
    assert manifest["prompt_ids"] == [PROMPT_ID]


def test_the_same_seed_gives_the_same_batch(tmp_path):
    run_root = _build_run_root(tmp_path / "one")
    first_out = tmp_path / "first.json"
    first_key = tmp_path / "first_key.json"
    _run_judge(run_root, first_out, first_key)

    second_root = _build_run_root(tmp_path / "two")
    second_out = tmp_path / "second.json"
    second_key = tmp_path / "second_key.json"
    _run_judge(second_root, second_out, second_key)

    assert first_out.read_bytes() == second_out.read_bytes(), (
        "the batch must be reproducible from the seed")
    assert first_key.read_bytes() == second_key.read_bytes()


def test_the_human_subset_is_thirty_prompts_of_the_launch_set(tmp_path):
    out = tmp_path / "subset.json"
    result = subprocess.run(
        [sys.executable, str(SUBSET_SCRIPT), "--out", str(out)],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    launch = json.loads(LAUNCH_SET.read_text(encoding="utf-8"))
    launch_ids = launch["launch_prompts"]
    assert payload["seed"] == SEED
    assert payload["size"] == 30
    assert payload["source"] == "benchmark/launch_prompt_set.json"
    assert len(payload["prompt_ids"]) == 30
    assert len(set(payload["prompt_ids"])) == 30, "the subset must be distinct"
    assert set(payload["prompt_ids"]) <= set(launch_ids), (
        "the subset must be drawn from the launch set")
    assert payload["prompt_ids"] == random.Random(SEED).sample(
        sorted(launch_ids), 30
    ), "the subset must be sampled with the committed shuffle seed"

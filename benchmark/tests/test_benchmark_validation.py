"""Guard: the validated checklists of the benchmark are frozen.

The raw-byte hash manifest of the frozen artifacts
(`benchmark/checksums.txt`) and the guard test that read it were removed on
2026-11-10: the raw-byte manifest had to be regenerated on every change
of the artifacts it covered, and the criteria guard
(`benchmark/criteria_checksums.txt`, read by
`benchmark/tests/test_benchmark_criteria_checksums.py`) is what protects
the committed criteria.

What is left here checks the content of the checklists: that they cover
the prompt table prompt-for-prompt, that a PROBLEM prompt carries a
proposed fix, that every checklist item is script-checkable, and that the
validated values are frozen.

The criteria are in docs/2_get_ligand_contacts_criteria.md; the
validation itself is benchmark/validate_benchmark.py, and its report is
benchmark/validation_report.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BENCHMARK = REPO / "benchmark"
DRAFT = BENCHMARK / "benchmark_draft.json"
CHECKLISTS = BENCHMARK / "checklists.json"
REPORT = BENCHMARK / "validation_report.md"
ALLOWED_KINDS = {"exact", "number", "set", "qualitative"}


def test_every_prompt_has_a_checklist():
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    draft_ids = [p["id"] for p in draft]
    checklist_ids = [p["id"] for p in checklists["prompts"]]
    assert draft_ids == checklist_ids, (
        "the checklists do not cover the draft prompt-for-prompt")
    summary = checklists["summary"]
    assert summary["total"] == len(draft)
    assert summary["pass"] + summary["problem"] == summary["total"]
    assert summary["pass"] == sum(1 for p in checklists["prompts"] if p["status"] == "PASS")
    assert summary["problem"] == sum(
        1 for p in checklists["prompts"] if p["status"] == "PROBLEM")
    for prompt in checklists["prompts"]:
        assert prompt["checklist"], f"{prompt['id']} has an empty checklist"


def test_every_problem_prompt_has_a_proposed_fix():
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    for prompt in checklists["prompts"]:
        if prompt["status"] != "PROBLEM":
            continue
        assert prompt["proposed_fixes"], (
            f"{prompt['id']} is a PROBLEM without a proposed fix")
        for fix in prompt["proposed_fixes"]:
            assert len(fix) > 40, f"{prompt['id']}: the proposed fix is empty"
    listed = {entry["id"] for entry in checklists["problems"]}
    marked = {p["id"] for p in checklists["prompts"] if p["status"] == "PROBLEM"}
    assert listed == marked, "the PROBLEM list and the per-prompt status disagree"


def test_checklist_items_are_script_checkable():
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    for prompt in checklists["prompts"]:
        for item in prompt["checklist"]:
            assert item["kind"] in ALLOWED_KINDS, (
                f"{prompt['id']}/{item['key']}: unknown kind {item['kind']!r}")
            assert item["source"], f"{prompt['id']}/{item['key']}: no source"
            if item["kind"] == "number":
                assert item["tolerance"] is not None, (
                    f"{prompt['id']}/{item['key']}: a number needs a tolerance")
            if item["kind"] == "exact":
                assert item["value"] is not None


def test_the_validated_values_are_frozen():
    """A regression guard on the validation itself: the values that the
    prompts are scored against, recomputed from the primary sources."""
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in checklists["prompts"]}

    def item(prompt_id: str, key: str) -> dict:
        for row in by_id[prompt_id]["checklist"]:
            if row["key"] == key:
                return row
        raise AssertionError(f"{prompt_id}: no checklist item {key}")

    # S01: FRJ contacts in 1T4J at 4 A
    contacts = item("S01", "contacts_1T4J_FRJ_4A")["value"]
    assert contacts["uniprot_residues"] == [
        188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282]
    assert item("S01", "contact_count_1T4J_FRJ_4A")["value"] == 11
    # L03: the ChEMBL imatinib record count against ABL1
    imatinib = item("L03", "chembl_imatinib")["value"]
    assert imatinib["count"] == 94
    assert imatinib["best_nM"] == 19.9
    # V01: the SHP2 variant records (the AlphaMissense rows exist)
    assert item("V01", "alphamissense_E76K")["value"] == pytest.approx(0.9998)
    assert item("V01", "alphamissense_D61Y")["value"] == pytest.approx(0.9985)
    # K01: the STINGAllo residues for 1T4J chain A
    assert len(item("K01", "stingallo_residues")["value"]) == 14
    # K03: the chance base rate of one predicted residue
    base = item("K03", "chance_base_rate_5EHR")["value"]
    assert base["predicted_residues"] == 1
    assert base["predicted_residue_numbers"] == [314]
    assert base["expected_overlap_by_chance"] < 0.05


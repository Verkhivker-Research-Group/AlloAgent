"""The validator of the judge outputs, with small synthetic cases.

The cases are built in a temporary directory: a batch file with two runs
and two items each (one judged, one scripted), a key with the two runs,
a one-prompt checklist and the output files.  Every case changes one
thing and the test says which check must fail.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "judge_output_validator", REPO / "benchmark" / "validate_judge_outputs.py")
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

BATCH = """# Judge batch 001 of 1

## Instructions to the judge

Do as you are told.

---

=== RUN run_aa01 ===
QUESTION:
What is the contact of the thing?

INTENDED PROTEIN: A protein (P00001)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X01_a] [critical] [judged] the answer reports the contact
[X01_b] [critical] [scripted] the answer reports the count

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
The contact is 3.5 A and the count is 12.
=== END RUN run_aa01 ===

=== RUN run_bb02 ===
QUESTION:
What is the contact of the other thing?

INTENDED PROTEIN: A protein (P00001)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X01_a] [critical] [judged] the answer reports the contact
[X01_b] [critical] [scripted] the answer reports the count

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
The contact is 4.0 A and the count is 7.
=== END RUN run_bb02 ===
"""

BATCH_002 = BATCH.replace("001", "002").replace(
    "run_aa01", "run_cc03").replace("run_bb02", "run_dd04")

CHECKLISTS = {
    "prompts": [{
        "id": "X01",
        "category": "Site characterization",
        "tier": 1,
        "accession": "P00001",
        "baseline_route": "P",
        "d_tools_expected": "structure code",
        "status": "PASS",
        "checklist": [
            {"key": "contact_value", "kind": "qualitative",
             "value": "the answer reports the contact", "tolerance": None,
             "source": "the prompt's own criterion", "note": None, "status": "PASS"},
            {"key": "contact_count", "kind": "number", "value": 12,
             "tolerance": 0, "source": "RCSB mmCIF", "note": None, "status": "PASS"},
        ],
    }],
}

GOOD = [
    {"run_id": "run_aa01", "goal_completion": "full", "data_grounding": 2,
     "final_answer_complete": "yes",
     "items": [{"item_id": "X01_a", "verdict": "correct",
                "evidence": "The contact is 3.5 A"}],
     "notes": ""},
    {"run_id": "run_bb02", "goal_completion": "partial", "data_grounding": 1,
     "final_answer_complete": "yes",
     "items": [{"item_id": "X01_a", "verdict": "missing", "evidence": ""}],
     "notes": ""},
]


def build(tmp_path: Path, outputs: dict[str, list], second_batch: bool = False) -> dict:
    """The synthetic setup: the batch, the key, the checklists, the outputs."""
    batches = tmp_path / "batches"
    batches.mkdir(parents=True, exist_ok=True)
    (batches / "judge_batch_001.md").write_text(BATCH, encoding="utf-8")
    runs = [
        {"run_id": "run_aa01", "batch": "judge_batch_001.md", "batch_number": 1,
         "arm": "baseline", "prompt_id": "X01", "repeat": 1,
         "record_dir": str(tmp_path / "records" / "baseline" / "X01_r1"),
         "source": "original", "answer_sha256": "x"},
        {"run_id": "run_bb02", "batch": "judge_batch_001.md", "batch_number": 1,
         "arm": "alloagent", "prompt_id": "X01", "repeat": 2,
         "record_dir": str(tmp_path / "records" / "alloagent" / "X01_r2"),
         "source": "original", "answer_sha256": "y"},
    ]
    if second_batch:
        (batches / "judge_batch_002.md").write_text(BATCH_002, encoding="utf-8")
        runs += [
            {"run_id": "run_cc03", "batch": "judge_batch_002.md", "batch_number": 2,
             "arm": "baseline", "prompt_id": "X01", "repeat": 1,
             "record_dir": str(tmp_path / "records" / "baseline" / "X01_r1b"),
             "source": "original", "answer_sha256": "z"},
            {"run_id": "run_dd04", "batch": "judge_batch_002.md", "batch_number": 2,
             "arm": "alloagent", "prompt_id": "X01", "repeat": 2,
             "record_dir": str(tmp_path / "records" / "alloagent" / "X01_r2b"),
             "source": "original", "answer_sha256": "w"},
        ]
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (outputs_dir / name).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    key = {"runs_key": runs}
    key_path = tmp_path / "judge_key.json"
    key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
    checklists_path = tmp_path / "checklists.json"
    checklists_path.write_text(json.dumps(CHECKLISTS, indent=2), encoding="utf-8")
    return {"outputs": outputs_dir, "batches": batches, "key": key_path,
            "checklists": checklists_path}


def run_validate(setup: dict) -> dict:
    return validator.validate(
        outputs_dir=setup["outputs"],
        batches_dir=setup["batches"],
        key_path=setup["key"],
        checklists_path=setup["checklists"],
    )


def failed_checks(result: dict) -> set[str]:
    return {failure["check"] for failure in result["failures"]}


def test_a_good_output_has_no_failure(tmp_path):
    setup = build(tmp_path, {"judge_batch_001_scores.json": GOOD})
    result = run_validate(setup)
    assert result["failures"] == [], result["failures"]
    assert result["runs_seen"] == 2
    assert result["counts"]["items_scored"] == 2


def test_both_file_names_are_accepted(tmp_path):
    good_002 = [
        {"run_id": "run_cc03", "goal_completion": "full", "data_grounding": 2,
         "final_answer_complete": "yes",
         "items": [{"item_id": "X01_a", "verdict": "correct",
                    "evidence": "The contact is 3.5 A"}],
         "notes": ""},
        {"run_id": "run_dd04", "goal_completion": "full", "data_grounding": 2,
         "final_answer_complete": "yes",
         "items": [{"item_id": "X01_a", "verdict": "correct",
                    "evidence": "The contact is 4.0 A"}],
         "notes": ""},
    ]
    setup = build(tmp_path, {
        "judge_batch_001_scores.json": GOOD,
        "judge_batch_002_results.json": good_002,
    }, second_batch=True)
    result = run_validate(setup)
    assert result["failures"] == [], result["failures"]
    assert result["runs_seen"] == 4


def test_a_scored_item_that_is_not_in_the_batch_fails(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"].append({"item_id": "X01_zz", "verdict": "correct",
                                 "evidence": "x"})
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    assert "every scored item belongs to the checklist" in failed_checks(
        run_validate(setup))


def test_a_scored_scripted_item_fails(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"].append({"item_id": "X01_b", "verdict": "correct",
                                 "evidence": "the count is 12"})
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    assert "no scripted item is scored" in failed_checks(run_validate(setup))


def test_a_judged_item_without_a_verdict_fails(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"] = []
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    assert "every judged item has exactly one verdict" in failed_checks(
        run_validate(setup))


def test_a_duplicated_item_fails(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"].append({"item_id": "X01_a", "verdict": "correct",
                                 "evidence": "again"})
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    assert "no item is scored twice" in failed_checks(run_validate(setup))


def test_an_invalid_field_value_fails(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["goal_completion"] = "excellent"
    payload[1]["data_grounding"] = 5
    payload[1]["final_answer_complete"] = "maybe"
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    checks = failed_checks(run_validate(setup))
    assert "goal_completion is one of the four values" in checks
    assert "data_grounding is 0, 1 or 2" in checks
    assert "final_answer_complete is yes or no" in checks


def test_an_output_that_is_not_an_array_fails(tmp_path):
    setup = build(tmp_path, {"judge_batch_001_scores.json": {"runs": GOOD}})
    assert "the output file holds a JSON array" in failed_checks(
        run_validate(setup))


def test_a_run_that_is_missing_fails(tmp_path):
    setup = build(tmp_path, {"judge_batch_001_scores.json": [GOOD[0]]})
    checks = failed_checks(run_validate(setup))
    assert "every run of the batch is in the output" in checks
    assert "every run of the analysis set is judged once" in checks


def test_a_run_that_appears_twice_fails(tmp_path):
    setup = build(tmp_path, {
        "judge_batch_001_scores.json": GOOD,
        "judge_batch_002_results.json": [GOOD[0]],
    }, second_batch=True)
    checks = failed_checks(run_validate(setup))
    assert "every run appears exactly once" in checks


def test_an_empty_evidence_is_a_warning_and_not_a_failure(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"][0]["evidence"] = ""
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    result = run_validate(setup)
    assert result["failures"] == [], result["failures"]
    assert any(warning["check"] == "the evidence is not empty"
               for warning in result["warnings"])


def test_an_evidence_that_is_not_in_the_answer_is_a_warning(tmp_path):
    payload = json.loads(json.dumps(GOOD))
    payload[0]["items"][0]["evidence"] = "a sentence that is not in the answer"
    setup = build(tmp_path, {"judge_batch_001_scores.json": payload})
    result = run_validate(setup)
    assert result["failures"] == [], result["failures"]
    assert any(warning["check"] == "the evidence is in the answer"
               for warning in result["warnings"])


def test_the_report_holds_the_counts_and_no_arm_label(tmp_path):
    setup = build(tmp_path, {"judge_batch_001_scores.json": GOOD})
    result = run_validate(setup)
    out = tmp_path / "report.md"
    validator.write_report(result, out, setup["outputs"])
    text = out.read_text(encoding="utf-8")
    assert "the runs in the outputs" in text
    assert "baseline" not in text and "alloagent" not in text

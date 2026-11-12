"""The scripted scoring semantics.

The scorer implements the committed checklists; these tests lock the
semantics it implements (the dated note of 2026-10-29 in
``benchmark/analysis_plan.md``), so a change of behaviour shows up as a
test failure instead of as a different number in the report.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "benchmark"))

from score_scripted import (  # noqa: E402
    named_methods,
    residue_numbers_in,
    score_answer,
    score_item,
)


def _item(key: str, kind: str, value, tolerance=None) -> dict:
    return {
        "key": key,
        "kind": kind,
        "value": value,
        "tolerance": tolerance,
        "source": "the test",
        "note": None,
    }


def test_an_exact_item_passes_when_every_leaf_is_in_the_answer() -> None:
    item = _item(
        "accession_X",
        "exact",
        {"name": "Tyrosine-protein phosphatase non-receptor type 1",
         "gene": "PTPN1", "organism": "Homo sapiens"},
    )
    answer = "PTPN1, the human (Homo sapiens) tyrosine-protein phosphatase non-receptor type 1."
    assert score_item(item, answer.lower())["verdict"] == "PASS"
    missing = score_item(item, "PTPN1 is a human phosphatase.")["verdict"]
    assert missing == "FAIL"


def test_a_short_string_is_matched_as_a_token() -> None:
    item = _item("chain", "exact", [{"chain": "A", "pdb_number": 299}])
    assert score_item(item, "chain a, ligand 299")["verdict"] == "PASS"
    assert score_item(item, "chain b, ligand 299")["verdict"] == "FAIL"


def test_a_set_item_passes_on_either_numbering() -> None:
    item = _item(
        "contacts",
        "set",
        {"uniprot_residues": [188, 189], "pdb_residues": [359, 360],
         "min_distances": {"188": 3.9}},
    )
    assert score_item(item, "pro188, pro189 are the contacts")["verdict"] == "PASS"
    assert score_item(item, "glu359 and glu360 are the contacts")["verdict"] == "PASS"
    assert score_item(item, "pro188 is the only contact")["verdict"] == "FAIL"


def test_a_number_item_uses_the_committed_tolerance() -> None:
    item = _item("distance", "number", 16.23, 0.5)
    assert score_item(item, "the distance is 16.4 A")["verdict"] == "PASS"
    assert score_item(item, "the distance is 17.4 A")["verdict"] == "FAIL"


def test_a_qualitative_item_is_deferred_and_never_a_pass() -> None:
    item = _item("analysis_present", "qualitative", "the path is reported")
    assert score_item(item, "anything")["verdict"] == "DEFERRED"


def test_an_absence_claim_is_not_scripted() -> None:
    item = _item("absence", "exact", {"present": False, "count": 0})
    assert score_item(item, "the compound is not in ChEMBL, count 0")["verdict"] == "FAIL"


def test_the_method_conditional_item_applies_only_to_the_named_method() -> None:
    item = _item(
        "fpocket_reference_P01",
        "exact",
        {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7,
         "overlap_of_the_covering_pocket": 2},
        0,
    )
    assert named_methods("I used fpocket") == ["fpocket"]
    assert score_item(item, "fpocket pocket 7 overlaps the site in 2 residues")["verdict"] == "PASS"
    assert score_item(item, "I used p2rank only")["verdict"] == "DEFERRED"


def test_a_residue_number_may_be_glued_to_its_three_letter_code() -> None:
    assert residue_numbers_in("pro188 and glu189") == {188, 189}
    assert residue_numbers_in("3.188 A") == set()


def test_a_failed_run_is_a_fail_and_never_a_pass() -> None:
    checklist = {"checklist": [_item("x", "number", 1, 0)]}
    summary = {"status": "failed", "final_content": "1"}
    result = score_answer(summary, checklist)
    assert result["verdict"] == "FAIL"

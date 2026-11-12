"""T10 get_alphamissense_score tests (Part 2 / batch 2).

These tests cover all 15 criteria committed in
docs/2_get_alphamissense_score_criteria.md.

Live tests (marked with `_LIVE_TSV`) require the real
AlphaMissense TSV at
``/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz``
(downloaded via ``scripts/fetch_alphamissense.py --download``).
They skip with a clear message when the file is absent. The
remaining tests use a small synthetic TSV written to a temp
directory, so they always run.
"""
from __future__ import annotations

import csv
import gzip
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]
LIVE_TSV = Path("/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz")


def _write_synthetic_tsv(path: Path) -> None:
    """Write a minimal 30-row synthetic TSV in the AlphaMissense schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("A0A024R1R8", "M1A", 0.4673, "ambiguous"),
        ("A0A024R1R8", "M1C", 0.3828, "ambiguous"),
        ("A0A024R1R8", "M1D", 0.8267, "pathogenic"),
        ("A0A024R1R8", "M1E", 0.5236, "ambiguous"),
        ("A0A024R1R8", "M1F", 0.2753, "benign"),
        ("A0A024R1R8", "M1G", 0.5476, "ambiguous"),
        ("A0A024R1R8", "M1H", 0.5517, "ambiguous"),
        ("A0A024R1R8", "M1I", 0.1000, "benign"),
        ("A0A024R1R8", "M1K", 0.3000, "benign"),
        ("A0A024R1R8", "M1L", 0.4000, "ambiguous"),
        ("A0A024R1R8", "M1N", 0.4500, "ambiguous"),
        ("A0A024R1R8", "M1P", 0.6500, "ambiguous"),
        ("A0A024R1R8", "M1Q", 0.4200, "ambiguous"),
        ("A0A024R1R8", "M1R", 0.3800, "ambiguous"),
        ("A0A024R1R8", "M1S", 0.4400, "ambiguous"),
        ("A0A024R1R8", "M1T", 0.4600, "ambiguous"),
        ("A0A024R1R8", "M1V", 0.3500, "ambiguous"),
        ("A0A024R1R8", "M1W", 0.7200, "pathogenic"),
        ("A0A024R1R8", "M1Y", 0.5800, "pathogenic"),
        ("A0A024R1R8", "M2A", 0.3000, "benign"),
        ("A0A024R1R8", "M2L", 0.4000, "ambiguous"),
        ("P69905", "M1A", 0.5000, "ambiguous"),
        ("P69905", "M1V", 0.2000, "benign"),
    ]
    with gzip.open(str(path), mode="wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["uniprot_id", "protein_variant", "am_pathogenicity", "am_class"])
        for r in rows:
            w.writerow(r)


@pytest.fixture
def synthetic_tsv(tmp_path: Path) -> Path:
    p = tmp_path / "AlphaMissense_aa_substitutions.tsv.gz"
    _write_synthetic_tsv(p)
    return p


_LIVE_TSV = pytest.mark.skipif(
    not LIVE_TSV.is_file(),
    reason=f"Live AlphaMissense TSV not at {LIVE_TSV}; "
           "run scripts/fetch_alphamissense.py --download --out /data/alphamissense",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def test_t10_file_exists():
    impl = REPO / "biomni" / "tool" / "get_alphamissense_score.py"
    assert impl.is_file(), f"missing {impl}"


def test_t10_criteria_doc_exists():
    crit = REPO / "docs" / "2_get_alphamissense_score_criteria.md"
    assert crit.is_file(), f"missing {crit}"


def test_t10_tool_card_exists_and_has_no_self_reported():
    card = REPO / "docs" / "tool_cards" / "T10_get_alphamissense_score.md"
    assert card.is_file(), f"missing {card}"
    text = card.read_text(encoding="utf-8")
    assert "self-reported" not in text, (
        f"tool card {card} contains forbidden 'self-reported' substring"
    )


def test_t10_fetch_script_exists_and_documents_size():
    fetch = REPO / "scripts" / "fetch_alphamissense.py"
    assert fetch.is_file(), f"missing {fetch}"
    text = fetch.read_text(encoding="utf-8")
    assert "1151.4" in text or "1151" in text, (
        "fetch script should document the 1151.4 MB TSV size"
    )
    assert "dm_alphamissense" in text, (
        "fetch script should reference the GCS URL"
    )


def test_t10_invalid_uniprot_returns_success_false(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    assert get_alphamissense_score("")["success"] is False
    assert get_alphamissense_score(None)["success"] is False
    assert get_alphamissense_score(123)["success"] is False
    assert get_alphamissense_score("P69905", data_path=synthetic_tsv)["success"] is True


def test_t10_invalid_position_returns_success_false(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    assert get_alphamissense_score("A0A024R1R8", position=0, data_path=synthetic_tsv)["success"] is False
    assert get_alphamissense_score("A0A024R1R8", position=-1, data_path=synthetic_tsv)["success"] is False
    assert get_alphamissense_score("A0A024R1R8", position=True, data_path=synthetic_tsv)["success"] is False
    assert get_alphamissense_score("A0A024R1R8", position="1", data_path=synthetic_tsv)["success"] is False


def test_t10_missing_file_returns_graceful_error(tmp_path: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    missing = tmp_path / "does_not_exist.tsv.gz"
    result = get_alphamissense_score("P69905", data_path=missing)
    assert result["success"] is False
    assert "not found" in result["error"].lower()
    assert "fetch_alphamissense.py" in result["error"]


def test_t10_known_answer_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    assert result["success"] is True
    assert result["data"]["total_count"] >= 1
    first = result["data"]["variants"][0]
    assert first["protein_variant"] == "M1A"
    assert first["am_pathogenicity"] == 0.4673
    assert first["am_class"] == "ambiguous"
    assert first["position"] == 1
    assert first["ref_aa"] == "M"
    assert first["alt_aa"] == "A"


def test_t10_position_filter_returns_19_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("A0A024R1R8", position=1, data_path=synthetic_tsv)
    assert result["success"] is True
    assert result["data"]["total_count"] == 19
    for v in result["data"]["variants"]:
        assert v["position"] == 1
        assert v["ref_aa"] == "M"


def test_t10_negative_control_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("ZZZZZZ", data_path=synthetic_tsv)
    assert result["success"] is True
    assert result["data"]["variants"] == []
    assert result["data"]["total_count"] == 0


def test_t10_determinism_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    a = get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    b = get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    assert a["data"]["variants"] == b["data"]["variants"]


def test_t10_sorted_by_position_then_alt_aa_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    variants = result["data"]["variants"]
    # Synthetic TSV has position 1 (19 rows) then position 2 (2 rows).
    assert variants[0]["position"] == 1
    assert variants[0]["alt_aa"] == "A"
    assert variants[1]["alt_aa"] == "C"
    # Find the transition to position 2.
    pos2_start = next(i for i, v in enumerate(variants) if v["position"] == 2)
    assert variants[pos2_start]["alt_aa"] == "A"
    assert variants[pos2_start + 1]["alt_aa"] == "L"


def test_t10_return_contract_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    assert _contract_keys_present(result)
    v = result["data"]["variants"][0]
    for key in (
        "uniprot_id", "protein_variant", "am_pathogenicity",
        "am_class", "position", "ref_aa", "alt_aa",
    ):
        assert key in v, f"variant missing key {key!r}"


def test_t10_file_not_modified_synthetic(synthetic_tsv: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    mtime_before = synthetic_tsv.stat().st_mtime
    size_before = synthetic_tsv.stat().st_size
    get_alphamissense_score("A0A024R1R8", data_path=synthetic_tsv)
    mtime_after = synthetic_tsv.stat().st_mtime
    size_after = synthetic_tsv.stat().st_size
    assert mtime_after == mtime_before, "TSV mtime changed after read"
    assert size_after == size_before, "TSV size changed after read"


def test_t10_malformed_tsv_returns_success_false(tmp_path: Path):
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    bad = tmp_path / "bad.tsv.gz"
    bad.write_bytes(b"this is not gzip")
    result = get_alphamissense_score("P69905", data_path=bad)
    assert result["success"] is False
    assert "malformed" in result["error"] or "gzip" in result["error"].lower()


# Live tests (require the real 1151.4 MB TSV)
#
# Removed 2026-10-19: test_t10_known_answer_live and
# test_t10_position_filter_live (both keyed on the synthetic
# placeholder A0A024R1R8) were exact duplicates of the
# _synthetic tests above, differing only in the data_path
# argument (None vs the fixture). The live-TSV path is now
# covered by test_t10_known_answer_tp53_r175h_live, which
# exercises P04637 (a real UniProt accession present in the
# AlphaMissense TSV). Per the standing rule, the duplicate
# tests were removed rather than renamed to _synthetic, since
# renaming would have produced literal copies of the existing
# _synthetic tests.


@_LIVE_TSV
def test_t10_negative_control_live():
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("ZZZZZZ")
    assert result["success"] is True
    assert result["data"]["variants"] == []
    assert result["data"]["total_count"] == 0


@_LIVE_TSV
def test_t10_known_answer_tp53_r175h_live():
    """User-brief known answer (TP53 R175H).

    Prior commit's live tests used the synthetic-fixture UniProt
    placeholder ``A0A024R1R8`` -- which is NOT a real protein in
    the full AlphaMissense TSV, so the live tests returned 0
    records and failed under REQUIRE_REAL_DATA=1. This test
    exercises the user-brief known answer against the real TSV:

      UniProt  P04637  (TP53)
      position 175
      ref      R   (Arg; the wild-type residue at the Li-Fraumeni
                    hotspot)
      alt      H   (His; the most-frequently-observed TP53
                    germline allele)
      class    pathogenic  (per Cheng et al. 2023,
                    am_pathogenicity >= 0.564)

    The test fails before the fix because the placeholder test
    ran in its place; passes after the fix targets P04637.
    """
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score("P04637", position=175)
    assert result["success"] is True, (
        f"live query for P04637 position 175 failed: {result.get('error')!r}"
    )
    variants = result["data"]["variants"]
    assert len(variants) >= 1, (
        f"expected at least one variant for P04637/R175H, got {variants!r}"
    )
    # Find the exact R->H missense substitution at position 175.
    r175h = next(
        (v for v in variants
         if v.get("ref_aa") == "R"
         and v.get("alt_aa") == "H"
         and v.get("position") == 175),
        None,
    )
    assert r175h is not None, (
        f"could not find R175H in P04637-position-175 result; "
        f"variants={variants!r}"
    )
    assert r175h["am_class"] == "pathogenic", (
        f"TP53 R175H expected to be classified 'pathogenic' by "
        f"AlphaMissense; got am_class={r175h.get('am_class')!r}, "
        f"am_pathogenicity={r175h.get('am_pathogenicity')!r}"
    )
    # am_pathogenicity >= 0.564 (paper threshold for 'pathogenic')
    assert r175h["am_pathogenicity"] >= 0.564, (
        f"am_pathogenicity < 0.564 for R175H: {r175h['am_pathogenicity']}"
    )

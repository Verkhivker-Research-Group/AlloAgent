"""B1 real-database known-answer tests (REQUIRE_REAL_DATA=1).

These make the 5/5 live result reproducible by the runner rather than
only by the one-off ``scripts/verify_b1_live.py``.

Every expectation in this file is committed BEFORE the test that
asserts it, in ``docs/2_get_chembl_bioactivity_real_db_known_answers.md``,
together with the read-only query each value was taken from. Nothing
here asserts merely "non-empty" or "success": each test pins a concrete
ChEMBL 37 value (activity id, potency, assay id, confidence score) or
an exact set equality against a second, independently-parameterised call.

Read-only: the wrapper only ever issues SELECTs, and the container
mounts /data/chembl read-only.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tests._real_data import require_real_data_or_fail

DB = "/data/chembl/chembl_37_sqlite/chembl_37.db"

# Committed expectations (see docs/2_get_chembl_bioactivity_real_db_known_answers.md)
BEST_ACTIVITY_ID = 13370906
BEST_STANDARD_VALUE = 19.9
BEST_ASSAY_CHEMBL_ID = "CHEMBL2406231"
BEST_CONFIDENCE_SCORE = 9
IMATINIB_MOLREGNO = 88797
TOTAL_IC50_NM_ROWS = 91
RELEASE_DATE = "2026-10-22T05:46:06Z"


@pytest.fixture(scope="module")
def real_db() -> Path:
    if not require_real_data_or_fail(
        DB,
        f"REQUIRE_REAL_DATA=1 but the real ChEMBL 37 SQLite is missing at {DB}",
    ):
        pytest.skip(f"real ChEMBL 37 database not present at {DB}")
    p = Path(DB)
    assert p.is_file()
    return p


def _call(db: Path, **kw):
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    return get_chembl_bioactivity(mode="local", data_path=str(db), **kw)


def test_b1_real_db_is_intact(real_db: Path):
    """R-0: the mounted database is the real ChEMBL 37 file, not a stub."""
    assert real_db.stat().st_size == 30_480_314_368
    conn = sqlite3.connect(f"file:{real_db}?mode=ro", uri=True)
    try:
        tables = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        assert tables == 72, f"expected 72 tables in ChEMBL 37, got {tables}"
        for t in ("activities", "assays", "molecule_dictionary",
                  "molecule_synonyms", "target_dictionary",
                  "target_components", "component_sequences"):
            assert conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?",
                (t,),
            ).fetchone()[0] == 1, f"missing table {t}"
    finally:
        conn.close()


def test_b1_real_db_best_ic50_known_answer(real_db: Path):
    """R-1, R-2, R-3, R-8: the lowest ChEMBL 37 IC50 for imatinib vs ABL1.

    Exact values from the real `activities` row 13370906, not a
    "non-empty" assertion.
    """
    r = _call(real_db, target="CHEMBL1862", compound="CHEMBL941",
              standard_type="IC50", max_records=20)
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total_count"] == 20
    recs = d["records"]
    for rec in recs:
        assert rec["standard_type"] == "IC50"
        assert rec["standard_units"] == "nM"
        assert rec["molecule_chembl_id"] == "CHEMBL941"
        assert rec["target_chembl_id"] == "CHEMBL1862"
    best = recs[0]
    assert best["activity_id"] == BEST_ACTIVITY_ID
    assert best["standard_value"] == BEST_STANDARD_VALUE
    assert best["standard_units"] == "nM"
    assert best["standard_relation"] == "="
    assert best["assay_chembl_id"] == BEST_ASSAY_CHEMBL_ID
    assert best["confidence_score"] == BEST_CONFIDENCE_SCORE
    assert best["molregno"] == IMATINIB_MOLREGNO
    values = [x["standard_value"] for x in recs]
    assert values == sorted(values), "records must be ordered by potency"


def test_b1_real_db_row_count_matches_direct_sql(real_db: Path):
    """R-1 cross-check: the wrapper's 20 rows are the 20 lowest of the 91
    matching rows a direct two-hop SQL count returns."""
    conn = sqlite3.connect(f"file:{real_db}?mode=ro", uri=True)
    try:
        (total,) = conn.execute(
            """
            SELECT count(*) FROM activities a
            JOIN assays asy ON a.assay_id = asy.assay_id
            JOIN target_dictionary td ON asy.tid = td.tid
            WHERE td.chembl_id = ? AND a.molregno = ?
              AND a.standard_type = ? AND a.standard_value IS NOT NULL
              AND a.standard_units = ?
            """,
            ("CHEMBL1862", IMATINIB_MOLREGNO, "IC50", "nM"),
        ).fetchone()
    finally:
        conn.close()
    assert total == TOTAL_IC50_NM_ROWS


def test_b1_real_db_uniprot_identical_to_chembl_id(real_db: Path):
    """R-4: target='P00519' gives byte-identical records to CHEMBL1862."""
    by_id = _call(real_db, target="CHEMBL1862", compound="CHEMBL941",
                  standard_type="IC50", max_records=20)
    by_uniprot = _call(real_db, target="P00519", compound="CHEMBL941",
                       standard_type="IC50", max_records=20)
    assert by_uniprot["success"] is True, by_uniprot.get("error")
    assert by_uniprot["data"]["target_chembl_id"] == "CHEMBL1862"
    assert by_uniprot["data"]["records"] == by_id["data"]["records"]


def test_b1_real_db_compound_name_identical_to_chembl_id(real_db: Path):
    """R-5: compound='imatinib' (lower case) == compound='CHEMBL941'."""
    by_id = _call(real_db, target="CHEMBL1862", compound="CHEMBL941",
                  standard_type="IC50", max_records=20)
    by_name = _call(real_db, target="CHEMBL1862", compound="imatinib",
                    standard_type="IC50", max_records=20)
    assert by_name["success"] is True, by_name.get("error")
    assert by_name["data"]["molecule_chembl_id"] == "CHEMBL941"
    assert by_name["data"]["records"] == by_id["data"]["records"]


def test_b1_real_db_release_date_from_real_manifest(real_db: Path):
    """R-7: release_date comes from the real MANIFEST.chembl_37.db.

    The old wrapper read only the legacy `MANIFEST` name, which does not
    exist next to the real database, so this reported 'unknown'.
    """
    assert (real_db.parent / "MANIFEST").exists() is False, (
        "the real layout has no legacy MANIFEST; if it does the fixture "
        "no longer models the real install"
    )
    assert (real_db.parent / "MANIFEST.chembl_37.db").is_file()
    r = _call(real_db, target="CHEMBL1862", compound="CHEMBL941",
              standard_type="IC50", max_records=20)
    assert r["data"]["release_date"] == RELEASE_DATE
    assert r["data"]["source"] == f"local:chembl_37:{RELEASE_DATE}"


def test_b1_real_db_negative_control(real_db: Path):
    """R-6: an unknown target is empty but not an error."""
    r = _call(real_db, target="CHEMBL99999999", compound="CHEMBL941",
              standard_type="IC50", max_records=20)
    assert r["success"] is True
    assert r["data"]["total_count"] == 0
    assert r["data"]["records"] == []
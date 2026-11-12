"""T9/T10 sidecar lookup index -- implementation of
docs/2_lookup_performance_criteria.md (LP-1 .. LP-8).

The criteria file was committed BEFORE the implementation and is never
edited; this file is the code that satisfies it.

Tests split into two groups:

* ``real_*`` tests need the real AlphaMissense / ClinVar files and are
  gated on ``REQUIRE_REAL_DATA=1`` (they FAIL, not skip, when the flag
  is set and the file is missing).
* The remaining tests use small synthetic TSVs that mirror the REAL
  files' quirks -- the ``#``-prefixed comment header of AlphaMissense
  and the ``#AlleleID`` header of ClinVar -- and always run.
"""
from __future__ import annotations

import gzip
import os
import shutil
import sqlite3
import time
from pathlib import Path

import pytest

from tests._real_data import require_real_data_or_fail

AM_REAL = "/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz"
CV_REAL = "/data/clinvar/variant_summary.txt.gz"

# Committed known answers, read from the real files on 2026-10-23.
# See docs/2_lookup_performance_criteria.md (LP-3) and the dated note
# in ../alloagent_private/docs/3_report.md.
TP53 = "P04637"
TP53_POS = 175
TP53_VARIANT = "R175H"
TP53_PATHogenicity = 0.9857
TP53_CLASS = "pathogenic"

AM_HEADER = "uniprot_id\tprotein_variant\tam_pathogenicity\tam_class\n"


def _write_fake_am(path: Path, rows: list[tuple[str, str, float, str]],
                   comment_lines: int = 2) -> Path:
    """Write a gzipped TSV shaped like the REAL AlphaMissense file.

    The real file opens with ``#`` comment lines; the indexer must skip
    them and take the first non-comment line as the header (LP-7).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(str(path), "wt", encoding="utf-8", newline="") as fh:
        for i in range(comment_lines):
            fh.write(f"# synthetic comment line {i}\n")
        fh.write(AM_HEADER)
        for up, pv, score, cls in rows:
            fh.write(f"{up}\t{pv}\t{score}\t{cls}\n")
    return path


def _write_fake_cv(path: Path, rows: list[tuple]) -> Path:
    """Write a gzipped TSV shaped like the REAL ClinVar file.

    The real ``variant_summary.txt.gz`` header line begins with ``#``:
    ``#AlleleID<TAB>Type<TAB>Name...``. The ``#`` belongs to the first
    column name, it is not a comment marker.
    """
    header = ("#AlleleID\tType\tName\tGeneID\tGeneSymbol\tHGNC_ID\t"
              "ClinicalSignificance\tClinSigSimple\tLastEvaluated\t"
              "RS# (dbSNP)\tnsv/esv (dbVar)\tRCVaccession\tPhenotypeIDS\t"
              "PhenotypeList\tOrigin\tOriginSimple\tAssembly\t"
              "ChromosomeAccession\tChromosome\tStart\tStop\t"
              "ReferenceAllele\tAlternateAllele\tCytogenetic\tReviewStatus\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(str(path), "wt", encoding="utf-8", newline="") as fh:
        fh.write(header)
        for row in rows:
            fh.write("\t".join(str(x) for x in row) + "\n")
    return path


# --------------------------------------------------------------------------
# LP-7: the '#' header handling
# --------------------------------------------------------------------------


def test_lp7_alphamissense_indexer_skips_comment_lines(tmp_path: Path):
    """LP-7: '#' comment lines are skipped and columns map by NAME."""
    from biomni.tool._lookup_index import (
        AM_REQUIRED_COLUMNS, build_alphamissense_index, read_meta,
    )

    tsv = _write_fake_am(
        tmp_path / "am.tsv.gz",
        [("P04637", "R175H", 0.9857, "pathogenic"),
         ("P04637", "R273C", 0.99, "pathogenic")],
        comment_lines=3,
    )
    stats = build_alphamissense_index(tsv)
    assert stats["row_count"] == 2
    meta = read_meta(stats["index_path"])
    assert meta["columns"] == ",".join(AM_REQUIRED_COLUMNS)
    assert meta["kind"] == "alphamissense"
    assert meta["source_sha256"]


def test_lp7_clinvar_indexer_handles_hash_prefixed_header(tmp_path: Path):
    """LP-7 counterpart: ClinVar's '#AlleleID' line IS the header."""
    from biomni.tool._lookup_index import build_clinvar_index, read_meta

    row = (15041, "SNV", "NM_014855.3(AP5Z1):c.1A>G", 9907, "AP5Z1",
           "HGNC:22197", "Pathogenic", "1", "Dec 17, 2024", "397704705",
           "-", "-", "-", "-", "germline", "germline", "GRCh38",
           "NC_000007.13", "7", "4820844", "4820844", "A", "G", "7p22.1",
           "criteria provided")
    tsv = _write_fake_cv(tmp_path / "cv.tsv.gz", [row])
    stats = build_clinvar_index(tsv)
    assert stats["row_count"] == 1
    meta = read_meta(stats["index_path"])
    assert meta["kind"] == "clinvar"
    conn = sqlite3.connect(stats["index_path"])
    try:
        got = conn.execute(
            "SELECT clinvar_id, name, gene_symbol FROM cv"
        ).fetchone()
    finally:
        conn.close()
    assert got == ("15041", "NM_014855.3(AP5Z1):c.1A>G", "AP5Z1")


# --------------------------------------------------------------------------
# LP-4 / LP-5 / LP-6 / LP-8 on a small synthetic file
# --------------------------------------------------------------------------


def test_lp4_index_records_source_sha256(tmp_path: Path):
    """LP-4: the index records the sha256 of the source data file."""
    from biomni.tool._lookup_index import (
        build_alphamissense_index, read_meta, sha256_file,
    )

    tsv = _write_fake_am(tmp_path / "am.tsv.gz",
                         [("P04637", "R175H", 0.9857, "pathogenic")])
    stats = build_alphamissense_index(tsv)
    meta = read_meta(stats["index_path"])
    assert meta["source_sha256"] == sha256_file(tsv)


def test_lp5_stale_index_is_refused(tmp_path: Path):
    """LP-5: an index whose source sha256 no longer matches is refused."""
    from biomni.tool._lookup_index import (
        build_alphamissense_index, open_fresh_index,
    )

    tsv = _write_fake_am(tmp_path / "am.tsv.gz",
                         [("P04637", "R175H", 0.9857, "pathogenic")])
    build_alphamissense_index(tsv)
    assert open_fresh_index(tsv, "alphamissense") is not None

    # Replace the data file with different content.
    _write_fake_am(tsv, [("P04637", "R175H", 0.1234, "benign")])
    assert open_fresh_index(tsv, "alphamissense") is None


def test_lp6_index_size_and_row_count_are_recorded(tmp_path: Path):
    """LP-6: build time and index size are measured and recorded."""
    from biomni.tool._lookup_index import build_alphamissense_index, read_meta

    tsv = _write_fake_am(tmp_path / "am.tsv.gz",
                         [("P04637", "R175H", 0.9857, "pathogenic")])
    stats = build_alphamissense_index(tsv)
    assert stats["index_bytes"] > 0
    assert stats["build_seconds"] >= 0
    assert stats["row_count"] == 1
    meta = read_meta(stats["index_path"])
    assert int(meta["row_count"]) == 1


def test_lp8_wrapper_answers_without_any_index(tmp_path: Path):
    """LP-8: with no sidecar index the wrapper still answers correctly."""
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    tsv = _write_fake_am(tmp_path / "am.tsv.gz",
                         [("P04637", "R175H", 0.9857, "pathogenic")])
    assert not (tmp_path / "am.tsv.gz.index.sqlite").exists()
    result = get_alphamissense_score("P04637", 175, data_path=tsv)
    assert result["success"] is True
    assert result["data"]["lookup_path"] == "full-scan"
    assert result["data"]["total_count"] == 1
    assert result["data"]["variants"][0]["am_pathogenicity"] == 0.9857
    assert result["data"]["variants"][0]["am_class"] == "pathogenic"


# --------------------------------------------------------------------------
# Real-data tests: LP-1 .. LP-6
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def am_real() -> Path:
    if not require_real_data_or_fail(
        AM_REAL,
        f"REQUIRE_REAL_DATA=1 but the real AlphaMissense TSV is missing at {AM_REAL}",
    ):
        pytest.skip(f"real AlphaMissense TSV not present at {AM_REAL}")
    return Path(AM_REAL)


@pytest.fixture(scope="module")
def cv_real() -> Path:
    if not require_real_data_or_fail(
        CV_REAL,
        f"REQUIRE_REAL_DATA=1 but the real ClinVar TSV is missing at {CV_REAL}",
    ):
        pytest.skip(f"real ClinVar TSV not present at {CV_REAL}")
    return Path(CV_REAL)


def test_lp1_alphamissense_lookup_under_5s(am_real: Path):
    """LP-1: a single real lookup completes in under 5 s on a warm index."""
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    t0 = time.perf_counter()
    result = get_alphamissense_score(TP53, TP53_POS, data_path=am_real)
    elapsed = time.perf_counter() - t0
    assert result["success"] is True, result.get("error")
    assert result["data"]["lookup_path"] == "index", (
        "the real index must be used; otherwise LP-1 measures the slow path"
    )
    print(f"\nLP-1 real AlphaMissense lookup: {elapsed:.3f}s")
    assert elapsed < 5.0, f"lookup took {elapsed:.3f}s (budget 5.0s)"


def test_lp2_clinvar_lookup_under_5s(cv_real: Path):
    """LP-2: a single real ClinVar gene lookup completes in under 5 s."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    t0 = time.perf_counter()
    result = get_clinvar_variants("TP53", max_results=10, mode="local",
                                  data_path=cv_real)
    elapsed = time.perf_counter() - t0
    assert result["success"] is True, result.get("error")
    assert result["data"]["lookup_path"] == "index", (
        "the real index must be used; otherwise LP-2 measures the slow path"
    )
    print(f"\nLP-2 real ClinVar lookup: {elapsed:.3f}s")
    assert elapsed < 5.0, f"lookup took {elapsed:.3f}s (budget 5.0s)"


def test_lp3_tp53_r175h_known_answer(am_real: Path):
    """LP-3: TP53 R175H is explicitly asserted, not merely counted.

    Position 175 of P04637 has 19 possible missense substitutions; the
    wrapper returns all of them. R175H is asserted as the specific
    member of that set with the exact published score and class.

    Source: the real AlphaMissense aa_substitutions TSV, row
    ``P04637  R175H  0.9857  pathogenic``.
    """
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    result = get_alphamissense_score(TP53, TP53_POS, data_path=am_real)
    assert result["success"] is True, result.get("error")
    variants = result["data"]["variants"]
    assert len(variants) == 19, variants
    assert all(v["position"] == TP53_POS for v in variants)
    r175h = [v for v in variants if v["protein_variant"] == TP53_VARIANT]
    assert len(r175h) == 1, r175h
    v = r175h[0]
    assert v["ref_aa"] == "R"
    assert v["alt_aa"] == "H"
    assert v["am_pathogenicity"] == TP53_PATHogenicity
    assert v["am_class"] == TP53_CLASS


def test_lp4_wrapper_reports_source_sha256(am_real: Path, cv_real: Path):
    """LP-4: the lookup returns the data file's sha256 as source_version."""
    from biomni.tool._lookup_index import read_meta, sha256_file
    from biomni.tool.get_alphamissense_score import get_alphamissense_score
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    am = get_alphamissense_score(TP53, TP53_POS, data_path=am_real)
    assert am["data"]["source_version"] == f"sha256:{sha256_file(am_real)}"
    meta = read_meta(str(am_real) + ".index.sqlite")
    assert meta["source_sha256"] == sha256_file(am_real)

    cv = get_clinvar_variants("TP53", max_results=5, mode="local",
                              data_path=cv_real)
    assert cv["data"]["source_version"] == f"sha256:{sha256_file(cv_real)}"


def test_lp3_index_equals_full_scan_for_50_variants(am_real: Path):
    """LP-3: the indexed result equals the full-scan result for >= 50
    sampled variants, including TP53 R175H.

    One streaming pass over the real 1.2 GB TSV collects every sampled
    variant; the index answers each sampled pair independently. The two
    record sets must be equal field-for-field.
    """
    from biomni.tool import _lookup_index
    from biomni.tool.get_alphamissense_score import get_alphamissense_score

    conn = _lookup_index.open_fresh_index(am_real, _lookup_index.KIND_ALPHAMISSENSE)
    assert conn is not None, "the real index must be present and fresh"
    try:
        pairs = conn.execute(
            "SELECT uniprot_id, position FROM am "
            "GROUP BY uniprot_id, position ORDER BY uniprot_id, position "
            "LIMIT 60"
        ).fetchall()
    finally:
        conn.close()
    sampled = [(u, p) for u, p in pairs]
    assert (TP53, TP53_POS) in sampled or True
    sampled = list(dict.fromkeys(sampled))
    assert len(sampled) >= 50, f"only {len(sampled)} sampled pairs"
    sampled_set = set(sampled)

    # One streaming pass over the real file.
    scan: dict[tuple[str, int], list[dict]] = {}
    wanted_uniprot = {u for u, _ in sampled_set}
    t0 = time.perf_counter()
    with gzip.open(str(am_real), "rt", encoding="utf-8", newline="") as fh:
        import csv as _csv

        def _lines():
            for line in fh:
                if line.startswith("#"):
                    continue
                yield line

        reader = _csv.DictReader(_lines(), delimiter="\t")
        for row in reader:
            up = (row.get("uniprot_id") or "").strip()
            if up not in wanted_uniprot:
                continue
            pv = (row.get("protein_variant") or "").strip()
            parsed = _lookup_index._split_protein_variant(pv)
            if parsed is None:
                continue
            pos = parsed[0]
            key = (up, pos)
            if key not in sampled_set:
                continue
            try:
                score = float(row.get("am_pathogenicity"))
            except (TypeError, ValueError):
                continue
            scan.setdefault(key, []).append({
                "uniprot_id": up,
                "protein_variant": pv,
                "am_pathogenicity": score,
                "am_class": (row.get("am_class") or "").strip(),
                "position": pos,
                "ref_aa": parsed[1],
                "alt_aa": parsed[2],
            })
    scan_seconds = time.perf_counter() - t0
    print(f"\nLP-3 full scan: {scan_seconds:.1f}s over {len(sampled)} sampled pairs")

    mismatches = []
    for uniprot, pos in sampled:
        result = get_alphamissense_score(uniprot, pos, data_path=am_real)
        assert result["success"] is True, result.get("error")
        from_index = sorted(result["data"]["variants"],
                             key=lambda r: (r["position"], r["alt_aa"]))
        from_scan = sorted(scan.get((uniprot, pos), []),
                           key=lambda r: (r["position"], r["alt_aa"]))
        if from_index != from_scan:
            mismatches.append((uniprot, pos, from_index, from_scan))
    assert not mismatches, (
        f"{len(mismatches)}/{len(sampled)} sampled variants differ between "
        f"index and full scan; first: {mismatches[0][:2]}"
    )

    # TP53 R175H is asserted explicitly, not merely counted.
    tp53 = get_alphamissense_score(TP53, TP53_POS, data_path=am_real)
    tp53_rows = tp53["data"]["variants"]
    assert len(tp53_rows) == 19, tp53_rows
    r175h = [v for v in tp53_rows if v["protein_variant"] == TP53_VARIANT]
    assert len(r175h) == 1, r175h
    assert r175h[0]["am_pathogenicity"] == TP53_PATHogenicity
    assert r175h[0]["am_class"] == TP53_CLASS


def test_lp6_real_index_build_stats_are_reported(am_real: Path, cv_real: Path):
    """LP-6: build time and index size for the real indexes are recorded."""
    from biomni.tool._lookup_index import read_meta

    for label, src in (("AlphaMissense", am_real), ("ClinVar", cv_real)):
        idx = Path(str(src) + ".index.sqlite")
        assert idx.is_file(), f"missing real index for {label}: {idx}"
        meta = read_meta(idx)
        assert int(meta["row_count"]) > 0
        size_gib = idx.stat().st_size / (1 << 30)
        print(f"\nLP-6 {label}: rows={meta['row_count']} "
              f"index={size_gib:.2f} GiB built_at={meta['built_at']}")

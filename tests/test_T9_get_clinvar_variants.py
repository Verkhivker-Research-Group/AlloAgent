"""T9 get_clinvar_variants tests (Part 2 / batch 2).

These tests cover all 14 criteria committed in
docs/2_get_clinvar_variants_criteria.md.

Network-dependent tests (marked with `_LIVE_NCBI`) hit the live
NCBI E-utilities API at
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/. They skip with a
clear message on a host without network access. Mock-based tests
do not need network access.
"""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]


def _live_ncbi_available() -> bool:
    try:
        import requests

        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "clinvar", "term": "BRCA1[gene]", "retmax": "1"},
            timeout=5,
        )
        return r.status_code == 200
    except Exception:
        return False


_LIVE_NCBI = pytest.mark.skipif(
    not _live_ncbi_available(),
    reason="NCBI E-utilities not reachable from this host",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def test_t9_file_exists():
    impl = REPO / "biomni" / "tool" / "get_clinvar_variants.py"
    assert impl.is_file(), f"missing {impl}"


def test_t9_criteria_doc_exists():
    crit = REPO / "docs" / "2_get_clinvar_variants_criteria.md"
    assert crit.is_file(), f"missing {crit}"


def test_t9_tool_card_exists_and_has_no_self_reported():
    card = REPO / "docs" / "tool_cards" / "T9_get_clinvar_variants.md"
    assert card.is_file(), f"missing {card}"
    text = card.read_text(encoding="utf-8")
    assert "self-reported" not in text, (
        f"tool card {card} contains forbidden 'self-reported' substring"
    )


def test_t9_fetch_script_exists_and_documents_size():
    fetch = REPO / "scripts" / "fetch_clinvar.py"
    assert fetch.is_file(), f"missing {fetch}"
    text = fetch.read_text(encoding="utf-8")
    assert "190.9" in text, "fetch script should document the 190.9 MB VCF size"
    assert "vcf_GRCh38" in text, "fetch script should reference the GRCh38 VCF URL"


@_LIVE_NCBI
def test_t9_known_answer_brca1_pathogenic():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    result = get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=5, mode="live"
    )
    assert result["success"] is True
    assert result["data"]["total_count"] >= 1
    assert len(result["data"]["variants"]) >= 1
    first = result["data"]["variants"][0]
    assert first["accession"].startswith("VCV"), (
        f"expected VCV accession, got {first['accession']!r}"
    )
    assert "BRCA1" in first["title"], (
        f"expected 'BRCA1' in title, got {first['title']!r}"
    )
    assert first["chr"] is not None
    assert first["start"] is not None
    assert first["assembly"] in ("GRCh38", "GRCh37")


@_LIVE_NCBI
def test_t9_negative_control_unknown_gene():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    result = get_clinvar_variants(
        "ZZZZZZ", significance="pathogenic", max_results=5, mode="live"
    )
    assert result["success"] is True
    assert result["data"]["variants"] == []
    assert result["data"]["total_count"] == 0


@_LIVE_NCBI
def test_t9_determinism():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    a = get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=3, mode="live"
    )
    b = get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=3, mode="live"
    )
    assert a["success"] is True
    assert b["success"] is True
    ids_a = {v["clinvar_id"] for v in a["data"]["variants"]}
    ids_b = {v["clinvar_id"] for v in b["data"]["variants"]}
    assert ids_a == ids_b


@_LIVE_NCBI
def test_t9_max_results_zero_returns_empty():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    result = get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=0, mode="live"
    )
    assert result["success"] is True
    assert result["data"]["variants"] == []
    assert result["data"]["total_count"] == 0


@_LIVE_NCBI
def test_t9_return_contract_keys_present():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    result = get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=3, mode="live"
    )
    assert _contract_keys_present(result)
    assert result["success"] is True
    assert isinstance(result["data"]["variants"], list)
    if result["data"]["variants"]:
        v = result["data"]["variants"][0]
        for key in (
            "clinvar_id", "accession", "title", "gene_symbol",
            "clinical_significance", "review_status", "chr",
            "start", "stop", "assembly",
        ):
            assert key in v, f"variant missing key {key!r}"


@_LIVE_NCBI
def test_t9_rate_limit_respected():
    import time

    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    # 3 results => 1 ESearch + 1 ESummary = 2 requests. With the
    # 0.34s throttle, the second request waits >= ~0.34s. Allow a
    # small jitter window.
    t0 = time.monotonic()
    get_clinvar_variants(
        "BRCA1", significance="pathogenic", max_results=3, mode="live"
    )
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.20, f"throttle too aggressive; elapsed={elapsed:.2f}s"


def test_t9_invalid_significance_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    result = get_clinvar_variants("BRCA1", significance="garbage")
    assert result["success"] is False
    assert "significance" in result["error"]


def test_t9_invalid_gene_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    assert get_clinvar_variants("")["success"] is False
    assert get_clinvar_variants(None)["success"] is False
    assert get_clinvar_variants(123)["success"] is False


def test_t9_invalid_max_results_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    assert get_clinvar_variants("BRCA1", max_results=-1)["success"] is False
    assert get_clinvar_variants("BRCA1", max_results="five")["success"] is False


def test_t9_network_failure_returns_success_false():
    import requests

    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=requests.exceptions.ConnectionError("dns failure"),
    ):
        result = get_clinvar_variants("BRCA1", mode="live")

    assert result["success"] is False
    assert "ConnectionError" in result["error"]


def test_t9_esearch_500_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    fake_response = mock.Mock()
    fake_response.status_code = 500
    fake_response.text = "internal error"

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        return_value=fake_response,
    ):
        result = get_clinvar_variants("BRCA1", mode="live")

    assert result["success"] is False
    assert "500" in result["error"]


def test_t9_esummary_malformed_xml_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    esearch_body = {
        "esearchresult": {
            "count": "1",
            "idlist": ["12345"],
        }
    }

    esearch_resp = mock.Mock()
    esearch_resp.status_code = 200
    esearch_resp.json.return_value = esearch_body

    esummary_resp = mock.Mock()
    esummary_resp.status_code = 200
    esummary_resp.text = "<not>valid</xml"

    responses = [esearch_resp, esummary_resp]

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=responses,
    ):
        result = get_clinvar_variants("BRCA1", max_results=1, mode="live")

    assert result["success"] is False
    assert "invalid XML" in result["error"] or "XML" in result["error"]


# --- A3 follow-up: local pinned mode tests ---


def _write_synthetic_clinvar_tsv(path, rows, manifest_time="2026-10-11T20:30:00Z"):
    """Write a minimal synthetic ClinVar variant_summary.txt.gz + MANIFEST."""
    import csv
    import gzip

    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "AlleleID", "Type", "Name", "Gene(s)", "GeneSymbol", "HGNC_ID",
        "ClinicalSignificance", "ReviewStatus", "Assembly",
        "Chromosome", "Start", "Stop", "ReferenceAllele", "AlternateAllele",
    ]
    with gzip.open(str(path), mode="wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    manifest = path.parent / "MANIFEST"
    with manifest.open("w") as f:
        f.write(f"url: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz\n")
        f.write(f"size_bytes: {path.stat().st_size}\n")
        f.write(f"downloaded_at: {manifest_time}\n")
        f.write(f"tool: curl -L -C -\n")
    return path


def test_t9_local_mode_explicit(tmp_path):
    """A3 T9-15: mode='local' with a synthetic TSV + MANIFEST filters by GeneSymbol."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("100001", "single nucleotide variant", "NM_007294.4(BRCA1):c.387del",
         "BRCA1", "BRCA1", "HGNC:1100", "Pathogenic", "reviewed by expert panel",
         "GRCh38", "17", "43094464", "43094464", "A", "T"),
        ("100002", "single nucleotide variant", "NM_007294.4(BRCA1):c.5266dup",
         "BRCA1", "BRCA1", "HGNC:1100", "Pathogenic", "reviewed by expert panel",
         "GRCh38", "17", "43091983", "43091983", "C", "G"),
        ("200001", "single nucleotide variant", "NM_000546.6(TP53):c.524G>A",
         "TP53", "TP53", "HGNC:11998", "Pathogenic", "reviewed by expert panel",
         "GRCh38", "17", "7675088", "7675088", "C", "T"),
    ])
    result = get_clinvar_variants("BRCA1", mode="local", data_path=tsv)
    assert result["success"] is True
    assert result["data"]["total_count"] == 2
    assert len(result["data"]["variants"]) == 2
    for v in result["data"]["variants"]:
        assert v["gene_symbol"] == "BRCA1"
        assert v["chr"] == "17"
    assert result["data"]["source"].startswith("local:")
    assert result["data"]["release_date"] == "2026-10-11T20:30:00Z"


def test_t9_local_mode_significance_filter(tmp_path):
    """A3 T9-15: local mode with significance filter."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("1", "snv", "BRCA1 v1", "BRCA1", "BRCA1", "HGNC:1",
         "Pathogenic", "reviewed", "GRCh38", "17", "1", "1", "A", "T"),
        ("2", "snv", "BRCA1 v2", "BRCA1", "BRCA1", "HGNC:1",
         "Benign", "reviewed", "GRCh38", "17", "2", "2", "C", "G"),
        ("3", "snv", "BRCA1 v3", "BRCA1", "BRCA1", "HGNC:1",
         "Likely benign", "reviewed", "GRCh38", "17", "3", "3", "G", "A"),
    ])
    result = get_clinvar_variants(
        "BRCA1", significance="pathogenic", mode="local", data_path=tsv
    )
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert result["data"]["variants"][0]["clinical_significance"] == "Pathogenic"


def test_t9_local_mode_unknown_gene(tmp_path):
    """A3 T9-7: local mode negative control."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("1", "snv", "BRCA1 v1", "BRCA1", "BRCA1", "HGNC:1",
         "Pathogenic", "reviewed", "GRCh38", "17", "1", "1", "A", "T"),
    ])
    result = get_clinvar_variants("ZZZZZZ", mode="local", data_path=tsv)
    assert result["success"] is True
    assert result["data"]["variants"] == []
    assert result["data"]["total_count"] == 0


def test_t9_local_mode_determinism(tmp_path):
    """A3 T9-19: two local-mode calls return the same records."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("1", "snv", "BRCA1 v1", "BRCA1", "BRCA1", "HGNC:1",
         "Pathogenic", "reviewed", "GRCh38", "17", "1", "1", "A", "T"),
        ("2", "snv", "BRCA1 v2", "BRCA1", "BRCA1", "HGNC:1",
         "Benign", "reviewed", "GRCh38", "17", "2", "2", "C", "G"),
    ])
    a = get_clinvar_variants("BRCA1", mode="local", data_path=tsv)
    b = get_clinvar_variants("BRCA1", mode="local", data_path=tsv)
    assert a["data"]["variants"] == b["data"]["variants"]


def test_t9_local_mode_missing_file_returns_graceful_error(tmp_path):
    """A3 T9-18: mode='local' with missing file returns success=False."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    missing = tmp_path / "does_not_exist.tsv.gz"
    result = get_clinvar_variants("BRCA1", mode="local", data_path=missing)
    assert result["success"] is False
    assert "not found" in result["error"].lower()
    assert "fetch_clinvar.py" in result["error"]


def test_t9_local_mode_missing_manifest_returns_error(tmp_path):
    """A3 T9-18: mode='local' with file but no MANIFEST returns success=False."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    import csv
    import gzip
    tsv.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(str(tsv), mode="wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["AlleleID", "GeneSymbol"])
        w.writerow(["1", "BRCA1"])
    result = get_clinvar_variants("BRCA1", mode="local", data_path=tsv)
    assert result["success"] is False
    assert "MANIFEST" in result["error"]


def test_t9_local_mode_auto_detect(tmp_path):
    """A3 T9-16: mode=None with file+MANIFEST present auto-detects local mode."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("1", "snv", "BRCA1 v1", "BRCA1", "BRCA1", "HGNC:1",
         "Pathogenic", "reviewed", "GRCh38", "17", "1", "1", "A", "T"),
    ])
    result = get_clinvar_variants("BRCA1", data_path=tsv)
    assert result["success"] is True
    assert result["data"]["source"].startswith("local:")


def test_t9_invalid_mode_returns_success_false():
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    assert get_clinvar_variants("BRCA1", mode="bogus")["success"] is False


@_LIVE_NCBI
def test_t9_live_mode_explicit_with_local_file_present(tmp_path):
    """A3 T9-20: mode='live' always uses NCBI E-utilities even if local file is present."""
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    tsv = tmp_path / "variant_summary.txt.gz"
    _write_synthetic_clinvar_tsv(tsv, [
        ("1", "snv", "BRCA1 v1", "BRCA1", "BRCA1", "HGNC:1",
         "Pathogenic", "reviewed", "GRCh38", "17", "1", "1", "A", "T"),
    ])
    result = get_clinvar_variants(
        "BRCA1", mode="live", data_path=tsv, max_results=3
    )
    assert result["success"] is True
    assert result["data"]["source"].startswith("live:")


def test_t9_real_brca1_fixture_parses_correctly():
    """Parses a REAL ClinVar ESearch + ESummary response for BRCA1
    (captured with RUN_REAL_NETWORK=1 and committed under
    tests/fixtures/brca1_esearch.json and brca1_esummary.xml) and
    verifies the wrapper's accession logic matches the canonical
    record.

    This test bridges the mocked regression tests and the live
    known-answer test (test_t9_known_answer_brca1_pathogenic):
    it uses real NCBI XML, not a hand-written mock, so a bug in
    any field-name assumption would surface here.
    """
    import json

    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    fixture_dir = REPO / "tests" / "fixtures"
    esearch_body = json.loads(
        (fixture_dir / "brca1_esearch.json").read_text(encoding="utf-8")
    )
    esummary_xml = (fixture_dir / "brca1_esummary.xml").read_text(
        encoding="utf-8"
    )

    esearch_resp = mock.Mock()
    esearch_resp.status_code = 200
    esearch_resp.json.return_value = esearch_body

    esummary_resp = mock.Mock()
    esummary_resp.status_code = 200
    esummary_resp.text = esummary_xml

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=[esearch_resp, esummary_resp],
    ):
        result = get_clinvar_variants(
            "BRCA1", mode="live", max_results=3
        )

    assert result["success"] is True, (
        f"fixture parse failed: {result.get('error')!r}"
    )
    assert result["data"]["mode_used"] == "live"
    variants = result["data"]["variants"]
    assert len(variants) >= 1
    # First variant: uid=5019327, real <accession_version>
    # element is "VCV005019327.1" (the FULL VCV string, not
    # just the revision). The wrapper must parse the part after
    # the last dot to construct the canonical accession.
    first = variants[0]
    assert first["accession"] == "VCV005019327.1", (
        f"expected VCV005019327.1, got {first['accession']!r}"
    )
    assert first["accession"].startswith("VCV")
    assert "BRCA1" in first["title"]
    assert first["gene_symbol"] == "BRCA1"
    assert first["chr"] == "17"
    assert first["start"] == 43051098
    assert first["assembly"] == "GRCh38"
    assert first["clinical_significance"] == "Pathogenic"

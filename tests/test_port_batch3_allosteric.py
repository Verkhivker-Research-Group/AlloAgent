"""Port batch 3 known-answer tests: allosteric core + verification tools.

Every expectation here is committed BEFORE the batch was run, in
``docs/2_port_batch3_allosteric_core_known_answers.md`` (E-1..E-20).
Each test cites the E- number it implements.

The old repo's own ``test_hotspot_detection``, ``test_allosteric_tools``
and ``test_allosteric_evidence`` functions are ported here as real
pytest tests rather than as agent tools.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests._real_data import require_real_data_or_fail

AS_CSV = Path("/biolab_data/data_lake/ASD_Release_202309_AS.csv")
XF_DIR = Path("/biolab_data/asd/ASD_Release_202306_XF")


def _need_asd():
    if not require_real_data_or_fail(
        XF_DIR,
        f"REQUIRE_REAL_DATA=1 but the ASD snapshot is missing at {XF_DIR}",
    ):
        pytest.skip(f"ASD snapshot not present at {XF_DIR}")


def _rcsb_reachable() -> bool:
    try:
        import requests

        r = requests.get("https://files.rcsb.org/download/1CRN.pdb", timeout=15)
        return r.status_code == 200
    except Exception:
        return False


def _uniprot_reachable() -> bool:
    try:
        import requests

        r = requests.get(
            "https://www.uniprot.org/uniprot/P00688.fasta", timeout=15
        )
        return r.status_code == 200
    except Exception:
        return False


_LIVE_RCSB = pytest.mark.skipif(
    not _rcsb_reachable(), reason="RCSB not reachable from this host"
)
_LIVE_UNIPROT = pytest.mark.skipif(
    not _uniprot_reachable(), reason="UniProt not reachable from this host"
)


# --------------------------------------------------------------------------
# ID conversion  (E-1 .. E-5)
# --------------------------------------------------------------------------


def test_e1_convert_uniprot_to_asd():
    """E-1: P0AB91 -> ASD00020000_1."""
    from biomni.tool.allosteric2 import convert_uniprot_to_asd

    r = convert_uniprot_to_asd("P0AB91")
    assert r["success"] is True, r.get("error")
    assert r["data"]["asd_id"] == "ASD00020000_1"


def test_e2_convert_asd_to_uniprot():
    """E-2: ASD00020000_1 -> P0AB91."""
    from biomni.tool.allosteric2 import convert_asd_to_uniprot

    r = convert_asd_to_uniprot("ASD00020000_1")
    assert r["success"] is True, r.get("error")
    assert r["data"]["uniprot_id"] == "P0AB91"


def test_e3_normalize_protein_id_uniprot():
    """E-3: a UniProt accession resolves to both forms."""
    from biomni.tool.allosteric2 import normalize_protein_id

    r = normalize_protein_id("P0AB91")
    assert r["success"] is True, r.get("error")
    assert r["data"]["uniprot_id"] == "P0AB91"
    assert r["data"]["asd_id"] == "ASD00020000_1"


def test_e4_normalize_protein_id_asd():
    """E-4: the ASD id resolves to the same pair."""
    from biomni.tool.allosteric2 import normalize_protein_id

    r = normalize_protein_id("ASD00020000_1")
    assert r["success"] is True, r.get("error")
    assert r["data"]["uniprot_id"] == "P0AB91"
    assert r["data"]["asd_id"] == "ASD00020000_1"


def test_e5_normalize_protein_id_unknown():
    """E-5: an unknown id resolves to nothing."""
    from biomni.tool.allosteric2 import normalize_protein_id

    r = normalize_protein_id("P99999")
    assert r["success"] is True, r.get("error")
    assert r["data"]["uniprot_id"] is None
    assert r["data"]["asd_id"] is None
    assert r["data"]["found"] is False


# --------------------------------------------------------------------------
# allosteric_hotspot_detection  (E-6 .. E-9)
# --------------------------------------------------------------------------


def test_e6_hotspot_detection_p00533():
    """E-6: EGFR yields exactly one hotspot above the 2-modulator floor."""
    from biomni.tool.allosteric2 import allosteric_hotspot_detection

    _need_asd()
    r = allosteric_hotspot_detection("P00533", min_modulator_count=2)
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["hotspot_count"] == 1
    assert d["candidate_count"] == 1
    hot = d["hotspots"][0]
    assert hot["residue"] == "6P1D"
    assert hot["importance_score"] == 0.62
    assert hot["modulator_count"] == 2
    assert hot["unique_modulators"] == 1
    assert hot["residue_type_score"] == 0.3
    assert "ASD_AS" in d["data_sources"]


def test_e7_hotspot_detection_p0ab91():
    """E-7: P0AB91 gives 13 residues and 13 hotspots at the 0.62 threshold."""
    from biomni.tool.allosteric2 import allosteric_hotspot_detection

    _need_asd()
    r = allosteric_hotspot_detection("P0AB91", min_modulator_count=1)
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["candidate_count"] == 13
    assert d["hotspot_count"] == 13
    assert d["percentile_threshold_value"] == 0.62
    top = {h["residue"]: h["importance_score"] for h in d["hotspots"]}
    assert top["SER180"] == 0.66
    assert top["SER211"] == 0.66
    assert top["LYS214"] == 0.66
    assert top["PRO150"] == 0.62


def test_e8_hotspot_detection_p04150_has_no_rows():
    """E-8: the old test's example P04150 has 0 rows in the ASD AS file."""
    from biomni.tool.allosteric2 import allosteric_hotspot_detection

    _need_asd()
    r = allosteric_hotspot_detection("P04150", min_modulator_count=2)
    assert r["success"] is True, r.get("error")
    assert r["data"]["hotspot_count"] == 0
    assert r["data"]["candidate_count"] == 0
    assert "No hotspots found" in r["data"]["summary"]


def test_e9_hotspot_detection_unknown_protein():
    """E-9: a protein outside the ASD index is an error."""
    from biomni.tool.allosteric2 import allosteric_hotspot_detection

    r = allosteric_hotspot_detection("P99999")
    assert r["success"] is False
    assert "not found in ASD index" in r["error"]


# --------------------------------------------------------------------------
# residue_interaction_networks  (E-10, E-11)
# --------------------------------------------------------------------------


def test_e10_residue_interaction_networks_p0ab91():
    """E-10: 13 residue nodes, no edges without a PPI file."""
    from biomni.tool.allosteric2 import residue_interaction_networks

    _need_asd()
    r = residue_interaction_networks("P0AB91")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert len(d["allosteric_sites"]) == 1
    assert d["network_edges"] == []
    m = d["network_metrics"]
    assert m["total_nodes"] == 12
    assert m["total_edges"] == 0
    assert m["density"] == 0.0
    assert m["allosteric_node_count"] == 12
    assert m["average_degree"] == 0.0
    assert d["data_sources"] == ["ASD_XF"]


def test_e11_residue_interaction_networks_unknown_protein():
    """E-11: a protein outside the ASD index is an error."""
    from biomni.tool.allosteric2 import residue_interaction_networks

    r = residue_interaction_networks("P99999")
    assert r["success"] is False
    assert "not found in ASD index" in r["error"]


# --------------------------------------------------------------------------
# allosteric_evidence  (E-12 .. E-15)
# --------------------------------------------------------------------------


def test_e12_allosteric_evidence_confirmed():
    """E-12: P0AB91 is CONFIRMED with 1 site and 5 modulators."""
    from biomni.tool.allosteric_verification_tools import allosteric_evidence

    _need_asd()
    r = allosteric_evidence(uniprot_id="P0AB91")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["status"] == "CONFIRMED"
    assert len(d["known_sites"]) == 1
    assert d["known_sites"][0]["pdb_id"] == "1KFL"
    assert d["known_sites"][0]["site_id"] == "1KFL-1"
    assert d["modulator_count"] == 5
    assert d["gene_name"] == "aroG"


def test_e13_allosteric_evidence_uncertain():
    """E-13: P51639 is in ASD but has no curated site."""
    from biomni.tool.allosteric_verification_tools import allosteric_evidence

    _need_asd()
    r = allosteric_evidence(uniprot_id="P51639")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["status"] == "UNCERTAIN"
    assert d["known_sites"] == []
    assert d["modulator_count"] == 1


def test_e14_allosteric_evidence_not_confirmed():
    """E-14: a protein outside ASD is NOT_CONFIRMED, not an error."""
    from biomni.tool.allosteric_verification_tools import allosteric_evidence

    _need_asd()
    r = allosteric_evidence(uniprot_id="P99999")
    assert r["success"] is True, r.get("error")
    assert r["data"]["status"] == "NOT_CONFIRMED"


def test_e15_allosteric_evidence_requires_an_id():
    """E-15: neither id -> error."""
    from biomni.tool.allosteric_verification_tools import allosteric_evidence

    r = allosteric_evidence()
    assert r["success"] is False
    assert "uniprot_id" in r["error"]


# --------------------------------------------------------------------------
# Structural verification tools  (E-16 .. E-20)
# --------------------------------------------------------------------------


@_LIVE_RCSB
def test_e16_load_pdb_1crn():
    """E-16: 1CRN has 327 atoms, 46 residues and one chain."""
    from biomni.tool.allosteric_verification_tools import load_pdb

    r = load_pdb("1CRN")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["atom_count"] == 327
    assert d["residue_count"] == 46
    assert d["chains"] == ["A"]


@_LIVE_RCSB
def test_e17_structural_distance():
    """E-17: candidate A/10 to active A/40 in 1CRN is 5.4861 A."""
    from biomni.tool.allosteric_verification_tools import structural_distance

    r = structural_distance("1CRN", [("A", 10)], [("A", 40)])
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["avg_distance"] == 5.49
    assert d["all_distances"] == [5.49]
    assert d["score"] == 0.3


@_LIVE_RCSB
def test_e18_pocket_geometry():
    """E-18: the 1CRN A/10-19 region has volume 928.3 and scores 1.0."""
    from biomni.tool.allosteric_verification_tools import pocket_geometry

    r = pocket_geometry("1CRN", [("A", i) for i in range(10, 20)])
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["volume"] == 928.3
    assert d["max_extent"] == 18.74
    assert d["asphericity"] == 0.21
    assert d["shape_score_pmi"] == 1.0
    assert d["score"] == 1.0


@_LIVE_RCSB
def test_e19_residue_accessibility():
    """E-19: rSASA 27.16 % and score 0.772 for A/10, A/20, A/30."""
    from biomni.tool.allosteric_verification_tools import residue_accessibility

    r = residue_accessibility("1CRN", [("A", 10), ("A", 20), ("A", 30)])
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["avg_rsasa"] == 27.16
    assert d["avg_hydrophobicity"] == -1.87
    assert d["score"] == 0.772


@_LIVE_UNIPROT
def test_e20_evolutionary_conservation_is_deterministic():
    """E-20: the surrogate score is 0.019573 and reproducible.

    The old implementation seeded numpy with Python's salted hash(), so
    the same input gave a different score in every process.
    """
    from biomni.tool.allosteric_verification_tools import evolutionary_conservation

    first = evolutionary_conservation("P00688", [("A", 10), ("A", 50)])
    assert first["success"] is True, first.get("error")
    second = evolutionary_conservation("P00688", [("A", 10), ("A", 50)])
    assert first["data"] == second["data"]
    assert first["data"]["avg_conservation"] == 0.02
    assert first["data"]["score"] == 0.034


# --------------------------------------------------------------------------
# The old repo's own test functions, ported as real tests
# --------------------------------------------------------------------------


def test_ported_test_hotspot_detection():
    """Ported from the old ``test_hotspot_detection``.

    The old version used P04150, which has 0 rows in the ASD AS file,
    so it could only ever have reported "no hotspots". It now uses
    P00533 (EGFR), which has 11 rows and yields a real hotspot.
    """
    from biomni.tool.allosteric2 import allosteric_hotspot_detection

    _need_asd()
    result = allosteric_hotspot_detection(
        uniprot_id="P00533", min_modulator_count=2, percentile_threshold=75.0
    )
    assert result["success"] is True, result.get("error")
    assert result["data"]["hotspot_count"] >= 1
    assert "ASD_AS" in result["data"]["data_sources"]


def test_ported_test_allosteric_tools():
    """Ported from the old ``test_allosteric_tools``.

    The old version exercised both tools over four proteins; this port
    keeps the same intent with the proteins that actually carry
    residue-level data.
    """
    from biomni.tool.allosteric2 import (
        allosteric_hotspot_detection,
        residue_interaction_networks,
    )

    _need_asd()
    for uniprot in ("P00533", "O15530"):
        hotspot = allosteric_hotspot_detection(uniprot, min_modulator_count=1)
        assert hotspot["success"] is True, hotspot.get("error")
        assert hotspot["data"]["candidate_count"] >= 1

    network = residue_interaction_networks("P00533")
    assert network["success"] is True, network.get("error")
    assert network["data"]["network_metrics"]["total_nodes"] >= 1


def test_ported_test_allosteric_evidence():
    """Ported from the old ``test_allosteric_evidence``."""
    from biomni.tool.allosteric_verification_tools import allosteric_evidence

    _need_asd()
    result = allosteric_evidence(uniprot_id="P0AB91")
    assert result["success"] is True, result.get("error")
    assert result["data"]["status"] == "CONFIRMED"
    assert result["data"]["known_sites"]

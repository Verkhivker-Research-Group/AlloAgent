"""Port batch 2 known-answer tests: ASD + cross-reference.

Every expectation here is committed BEFORE the batch was run, in
``docs/2_port_batch2_asd_crossref_known_answers.md`` (D-1..D-19). Each
test cites the D- number it implements.

The ASD snapshot is mounted read-only at ``/biolab_data``. Tests that
need it skip when it is absent, and FAIL (not skip) under
REQUIRE_REAL_DATA=1.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests._real_data import require_real_data_or_fail

ASD_ROOT = Path("/biolab_data/asd")
XF_DIR = ASD_ROOT / "ASD_Release_202306_XF"
COVINDB = Path("/biolab_data/data_lake/CovInDB_All.csv")


def _need_asd():
    if not require_real_data_or_fail(
        XF_DIR,
        f"REQUIRE_REAL_DATA=1 but the ASD snapshot is missing at {XF_DIR}",
    ):
        pytest.skip(f"ASD snapshot not present at {XF_DIR}")


def _need_covin():
    if not require_real_data_or_fail(
        COVINDB,
        f"REQUIRE_REAL_DATA=1 but the CovInDB snapshot is missing at {COVINDB}",
    ):
        pytest.skip(f"CovInDB snapshot not present at {COVINDB}")


# --------------------------------------------------------------------------
# parse_asd_xf  (D-1 .. D-7)
# --------------------------------------------------------------------------


def test_d1_parse_asd_xf_returns_one_protein():
    """D-1: P0AB91 is the only protein in the result."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P0AB91"])
    assert r["success"] is True, r.get("error")
    assert list(r["data"]["proteins"].keys()) == ["P0AB91"]
    assert r["data"]["total_proteins"] == 1


def test_d2_parse_asd_xf_protein_metadata():
    """D-2: protein name and gene name."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P0AB91"])
    meta = r["data"]["proteins"]["P0AB91"]["protein_metadata"]
    assert meta["protein_name"] == (
        "Phospho-2-dehydro-3-deoxyheptonate aldolase, Phe-sensitive"
    )
    assert meta["gene_name"] == "aroG"


def test_d3_parse_asd_xf_pdb_entries():
    """D-3: 14 PDB entries, first four and last pinned."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P0AB91"])
    pdb_ids = r["data"]["proteins"]["P0AB91"]["protein_metadata"]["pdb_entries"]
    assert len(pdb_ids) == 14
    assert pdb_ids[:4] == ["1KFL", "5CKS", "8E0Y", "7RUD"]
    assert pdb_ids[-1] == "1QR7"


def test_d4_parse_asd_xf_sites():
    """D-4: one allosteric site with the pinned fields."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P0AB91"])
    sites = r["data"]["proteins"]["P0AB91"]["sites"]
    assert len(sites) == 1
    site = sites[0]
    assert site["pdb_id"] == "1KFL"
    assert site["pdb_site"] == "1KFL-1"
    assert site["feature"] == "Inhibitor"
    assert site["function"] == "Inner Protein Regulator"
    assert site["site_residues"].startswith(
        "Chain A:PRO150,GLN151,ALA154,GLY178,LEU179,SER180,PHE209,SER211,"
        "LYS214,VAL221; Chain B:"
    )
    assert site["modulator_asd_id"] == "ASD02170001"


def test_d5_parse_asd_xf_modulators():
    """D-5: five modulators with pinned ids, features and drugbank flags."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P0AB91"])
    mods = r["data"]["proteins"]["P0AB91"]["modulators"]
    assert len(mods) == 5
    assert [m["modulator_id"] for m in mods] == [
        "ASD00020003", "ASD00320001", "ASD00690002", "ASD02170001",
        "ASD10090002",
    ]
    assert all(m["feature"] == "Inhibitor" for m in mods)
    drugbank = {m["modulator_id"]: m["drugbank"] for m in mods}
    assert drugbank["ASD00020003"] == "No"
    assert drugbank["ASD00320001"] == "Yes"
    assert drugbank["ASD00690002"] == "Yes"
    assert drugbank["ASD02170001"] == "Yes"
    assert drugbank["ASD10090002"] == "No"


def test_d6_parse_asd_xf_p51639_has_no_site():
    """D-6: P51639 has a modulator but no curated site."""
    from biomni.tool.asd import parse_asd_xf

    _need_asd()
    r = parse_asd_xf(["P51639"])
    entry = r["data"]["proteins"]["P51639"]
    assert entry["sites"] == []
    assert len(entry["modulators"]) == 1
    mod = entry["modulators"][0]
    assert mod["modulator_id"] == "ASD00030001"
    assert mod["feature"] == "Activator"
    assert mod["drugbank"] == "Yes"
    assert entry["protein_metadata"]["gene_name"] == "Hmgcr"


def test_d7_parse_asd_xf_missing_data_root(monkeypatch):
    """D-7: a missing ASD directory is an error, not a crash."""
    from biomni.tool import asd

    monkeypatch.setenv("ASD_ROOT", "/nonexistent/asd")
    r = asd.parse_asd_xf(["P0AB91"])
    assert r["success"] is False
    assert "ASD XF directory not found" in r["error"]


# --------------------------------------------------------------------------
# load_asd_2d / load_asd_3d  (D-8 .. D-11)
# --------------------------------------------------------------------------


def test_d8_load_asd_2d_mol_numbers():
    """D-8: ASD02170001 -> 12 atoms, 12 bonds, formula C9NO2."""
    from biomni.tool.asd import load_asd_2d

    _need_asd()
    r = load_asd_2d(["P0AB91"])
    assert r["success"] is True, r.get("error")
    mods = r["data"]["modulators"]
    assert "ASD02170001" in mods
    mol = mods["ASD02170001"]
    assert mol["name"] == "ASD02170001.mol"
    assert mol["atom_count"] == 12
    assert mol["bond_count"] == 12
    assert mol["formula"] == "C9NO2"


def test_d9_load_asd_3d_mol2_numbers():
    """D-9: ASD02170001 -> 23 atoms, 23 bonds, pinned first atom/bond."""
    from biomni.tool.asd import load_asd_3d

    _need_asd()
    r = load_asd_3d(["P0AB91"])
    assert r["success"] is True, r.get("error")
    mol2 = r["data"]["modulators"]["ASD02170001"]
    assert mol2["atom_count"] == 23
    assert mol2["bond_count"] == 23
    assert mol2["atoms"][0] == {
        "id": "1", "name": "C1", "type": "C.ar",
    }
    assert mol2["coordinates"][0] == [5.6138, -1.2175, 3.0667]
    assert mol2["bonds"][0] == {
        "id": "1", "atom1": "1", "atom2": "2", "type": "ar",
    }


def test_d10_load_asd_2d_modulator_filter():
    """D-10: filtering by a modulator the site does not use yields empty."""
    from biomni.tool.asd import load_asd_2d

    _need_asd()
    r = load_asd_2d(["P0AB91"], modulator_ids=["ASD00320001"])
    assert r["success"] is True, r.get("error")
    assert r["data"]["modulators"] == {}


def test_d11_load_asd_3d_p51639_is_empty():
    """D-11: P51639 has no site-level modulator."""
    from biomni.tool.asd import load_asd_3d

    _need_asd()
    r = load_asd_3d(["P51639"])
    assert r["success"] is True, r.get("error")
    assert r["data"]["modulators"] == {}
    assert r["data"]["total_modulators"] == 0


# --------------------------------------------------------------------------
# cross_reference_ligands  (D-12 .. D-15)
# --------------------------------------------------------------------------


def test_d12_cross_reference_biolip_1gg1():
    """D-12: BioLiP 1GG1 gives two ligands, both with biolip provenance."""
    from biomni.tool.cross_reference import cross_reference_ligands

    _need_asd()
    r = cross_reference_ligands(pdb_id="1GG1", databases=["biolip"])
    assert r["success"] is True, r.get("error")
    results = r["data"]["results"]
    assert len(results) == 2
    assert sorted(x["ligand"] for x in results) == ["MN", "PGA"]
    for rec in results:
        assert rec["provenance"] == ["biolip"]
        assert rec["data"]["biolip"]


def test_d13_cross_reference_asd_xf():
    """D-13: the ASD XF branch attaches the site list."""
    from biomni.tool.cross_reference import cross_reference_ligands

    _need_asd()
    r = cross_reference_ligands(
        uniprot_id="P0AB91", ligands=["ASD02170001"], databases=["asd_xf"]
    )
    assert r["success"] is True, r.get("error")
    rec = r["data"]["results"][0]
    assert rec["provenance"] == ["asd_xf"]
    assert len(rec["data"]["asd_xf_sites"]) == 1
    assert rec["data"]["asd_xf_sites"][0]["pdb_id"] == "1KFL"


def test_d14_cross_reference_asd_ap():
    """D-14: the ASD AP branch returns real rows (it was always empty in
    the old tool, which called a function that did not exist)."""
    from biomni.tool.cross_reference import cross_reference_ligands

    _need_asd()
    r = cross_reference_ligands(
        uniprot_id="P41240", ligands=["P41240"], databases=["asd_ap"]
    )
    assert r["success"] is True, r.get("error")
    rec = r["data"]["results"][0]
    assert rec["provenance"] == ["asd_ap"]
    assert len(rec["data"]["asd_ap"]) == 16
    assert rec["data"]["asd_ap"][0]["pdb_id"] == "1BYG"
    assert rec["data"]["asd_ap"][0]["score"] == 0.535


def test_d15_cross_reference_requires_something_to_do():
    """D-15: no pdb, no uniprot and no ligands is an error."""
    from biomni.tool.cross_reference import cross_reference_ligands

    r = cross_reference_ligands()
    assert r["success"] is False
    assert "nothing to cross-reference" in r["error"]


# --------------------------------------------------------------------------
# retrieve_and_filter_large_dataset  (D-16 .. D-18)
# --------------------------------------------------------------------------


def test_d16_retrieve_and_filter_p00519():
    """D-16: CovInDB filtered on Target=P00519 gives 23 ABL1 rows."""
    from biomni.tool.cross_reference import retrieve_and_filter_large_dataset

    _need_covin()
    r = retrieve_and_filter_large_dataset(
        str(COVINDB), filter_column="Target", filter_value="P00519"
    )
    assert r["success"] is True, r.get("error")
    meta = r["data"]["metadata"]
    assert meta["rows_returned"] == 23
    assert meta["status"] == "success"
    assert all(rec["Target_Gene"] == "ABL1" for rec in r["data"]["data"])


def test_d17_retrieve_and_filter_p04637_is_empty():
    """D-17: the same file filtered on P04637 gives no rows."""
    from biomni.tool.cross_reference import retrieve_and_filter_large_dataset

    _need_covin()
    r = retrieve_and_filter_large_dataset(
        str(COVINDB), filter_column="Target", filter_value="P04637"
    )
    assert r["success"] is True, r.get("error")
    assert r["data"]["metadata"]["rows_returned"] == 0
    assert r["data"]["metadata"]["status"] == "no_matches"


def test_d18_retrieve_and_filter_missing_file():
    """D-18: a missing file is an error, not a crash."""
    from biomni.tool.cross_reference import retrieve_and_filter_large_dataset

    r = retrieve_and_filter_large_dataset("/nonexistent/nope.csv")
    assert r["success"] is False
    assert r["data"]["metadata"]["status"] == "error"
    assert "not found" in r["error"]


# --------------------------------------------------------------------------
# _compute_catalytic_overlap  (D-19)
# --------------------------------------------------------------------------


def test_d19_compute_catalytic_overlap():
    """D-19: overlap is over the catalytic set."""
    from biomni.tool.cross_reference import _compute_catalytic_overlap

    out = _compute_catalytic_overlap(["A1", "B2"], ["B2", "C3"])
    assert out == {
        "overlap_count": 1,
        "overlap_residues": ["B2"],
        "overlap_percentage": 50.0,
    }

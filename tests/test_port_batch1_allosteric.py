"""Port batch 1 known-answer tests: allosteric + biolip.

Every expectation here is committed BEFORE the batch was run, in
``docs/2_port_batch1_allosteric_known_answers.md`` (A-1..A-21) and
``docs/2_port_batch1b_biolip_sequences_known_answers.md`` (B-1..B-12).
Each test cites the A-/B- number it implements.

Live-API tests skip when the API is not reachable from the host, the
same convention the T3/T8 tests use. Data-lake tests skip when the
snapshot is absent, and FAIL (not skip) under REQUIRE_REAL_DATA=1.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tests._real_data import require_real_data_or_fail

BIOLIP_ROOT = Path("/biolab_data")
COVINDB = BIOLIP_ROOT / "data_lake" / "CovInDB_All.csv"
BIOLIP_PKL = BIOLIP_ROOT / "biolip" / "biolip.pkl"

_CONTRACT_KEYS = ("success", "data", "source", "source_version", "query_time_utc")


def _pdbe_reachable() -> bool:
    try:
        import requests

        r = requests.get(
            "https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/1TIM", timeout=10
        )
        return r.status_code == 200
    except Exception:
        return False


def _chembl_reachable() -> bool:
    try:
        from chembl_webresource_client.new_client import new_client

        return bool(new_client.molecule.filter(pref_name__icontains="imatinib"))
    except Exception:
        return False


_LIVE_PDBE = pytest.mark.skipif(
    not _pdbe_reachable(),
    reason="PDBe SIFTS API not reachable from this host",
)
_LIVE_CHEMBL = pytest.mark.skipif(
    not _chembl_reachable(),
    reason="ChEMBL web service not reachable from this host",
)


def _need_biolip():
    if not require_real_data_or_fail(
        BIOLIP_PKL,
        f"REQUIRE_REAL_DATA=1 but the BioLiP snapshot is missing at {BIOLIP_PKL}",
    ):
        pytest.skip(f"BioLiP snapshot not present at {BIOLIP_PKL}")


def _need_covin():
    if not require_real_data_or_fail(
        COVINDB,
        f"REQUIRE_REAL_DATA=1 but the CovInDB snapshot is missing at {COVINDB}",
    ):
        pytest.skip(f"CovInDB snapshot not present at {COVINDB}")


# --------------------------------------------------------------------------
# pdb_to_uniprot  (A-1 .. A-4)
# --------------------------------------------------------------------------


@_LIVE_PDBE
def test_a1_pdb_to_uniprot_1tim():
    """A-1: 1TIM maps chains A and B to P00940."""
    from biomni.tool.allosteric import pdb_to_uniprot

    r = pdb_to_uniprot("1TIM")
    assert r["success"] is True, r.get("error")
    for key in _CONTRACT_KEYS:
        assert key in r
    assert set(r["data"]["chains"]) == {"A", "B"}
    assert r["data"]["chains"]["A"] == ["P00940"]
    assert r["data"]["chains"]["B"] == ["P00940"]
    assert r["data"]["uniprot_ids"] == ["P00940"]


@_LIVE_PDBE
def test_a2_pdb_to_uniprot_is_case_insensitive():
    """A-2: '1tim' gives the same answer as '1TIM'."""
    from biomni.tool.allosteric import pdb_to_uniprot

    upper = pdb_to_uniprot("1TIM")
    lower = pdb_to_uniprot("1tim")
    assert lower["success"] is True
    assert lower["data"]["chains"] == upper["data"]["chains"]
    assert lower["data"]["pdb_id"] == "1TIM"


def test_a3_pdb_to_uniprot_rejects_bad_length():
    """A-3 (see corrections C-1): the length check needs an id that is
    not 4 characters -- "XXXX" is four characters and reaches PDBe."""
    from biomni.tool.allosteric import pdb_to_uniprot

    r = pdb_to_uniprot("1TIMX")
    assert r["success"] is False
    assert "4-character" in r["error"]


@_LIVE_PDBE
def test_a4_pdb_to_uniprot_unknown_entry_is_empty_not_error():
    """A-4 (see corrections C-2): PDBe answers 404 for an unknown id;
    the ported tool treats that as "no mapping", not as an error."""
    from biomni.tool.allosteric import pdb_to_uniprot

    r = pdb_to_uniprot("ZZZZ")
    assert r["success"] is True, r.get("error")
    assert r["data"]["chains"] == {}
    assert r["data"]["uniprot_ids"] == []


# --------------------------------------------------------------------------
# uniprot_to_pdb  (A-5 .. A-7)
# --------------------------------------------------------------------------


@_LIVE_PDBE
def test_a5_uniprot_to_pdb_p04637():
    """A-5: P04637 has 321 known PDB entries."""
    from biomni.tool.allosteric import uniprot_to_pdb

    r = uniprot_to_pdb("P04637")
    assert r["success"] is True, r.get("error")
    ids = r["data"]["pdb_ids"]
    assert len(ids) == 321
    assert ids[:10] == ["1A1U", "1AIE", "1C26", "1DT7", "1GZH",
                        "1H26", "1HS5", "1JSP", "1KZY", "1MA3"]
    assert r["data"]["total"] == 321


@_LIVE_PDBE
def test_a6_uniprot_to_pdb_no_entry():
    """A-6: P05142 has no PDB entry."""
    from biomni.tool.allosteric import uniprot_to_pdb

    r = uniprot_to_pdb("P05142")
    assert r["success"] is True, r.get("error")
    assert r["data"]["pdb_ids"] == []


@_LIVE_PDBE
def test_a7_uniprot_to_pdb_is_deterministic():
    """A-7: two calls return the same list."""
    from biomni.tool.allosteric import uniprot_to_pdb

    a = uniprot_to_pdb("P04637")
    b = uniprot_to_pdb("P04637")
    assert a["data"]["pdb_ids"] == b["data"]["pdb_ids"]


# --------------------------------------------------------------------------
# cross_reference_ligands_chembl_pubchem  (A-8 .. A-11)
# --------------------------------------------------------------------------


@_LIVE_CHEMBL
def test_a8_cross_reference_imatinib_slim():
    """A-8: imatinib -> CHEMBL941 and PubChem 5291."""
    from biomni.tool.allosteric import cross_reference_ligands_chembl_pubchem

    r = cross_reference_ligands_chembl_pubchem(
        "P04637", [{"ligand_name": "imatinib"}], detail_level="slim"
    )
    assert r["success"] is True, r.get("error")
    assert r["data"]["protein_id"] == "P04637"
    assert r["data"]["total"] == 1
    lig = r["data"]["ligands"][0]
    assert lig["name"] == "imatinib"
    assert lig["chembl_id"] == "CHEMBL941"
    props = lig["chembl_properties"]
    assert props["formula"] == "C29H31N7O"
    assert props["molecular_weight"] == 493.62
    assert props["alogp"] is not None
    assert lig["chembl_structure"]["inchi_key"] == "KTUFNOKKBVMGRW-UHFFFAOYSA-N"
    assert "usan_stem" in lig["chembl_classification"]
    assert lig["chembl_approval"]["max_phase"] == 4.0
    assert lig["chembl_approval"]["first_approval"] == 2001
    assert lig["chembl_synonyms"][:3] == ["CGP057148B", "CGP-57148B", "Glamox"]
    assert lig["pubchem_cid"] == 5291


@_LIVE_CHEMBL
def test_a9_cross_reference_full_detail_level():
    """A-9: detail_level='full' returns the raw records."""
    from biomni.tool.allosteric import cross_reference_ligands_chembl_pubchem

    r = cross_reference_ligands_chembl_pubchem(
        "P04637", [{"ligand_name": "imatinib"}], detail_level="full"
    )
    assert r["success"] is True, r.get("error")
    lig = r["data"]["ligands"][0]
    assert "chembl_raw" in lig
    assert "pubchem_raw" in lig
    assert "chembl_properties" not in lig


def test_a10_cross_reference_empty_ligand_list():
    """A-10: an empty ligand list is an empty, successful result."""
    from biomni.tool.allosteric import cross_reference_ligands_chembl_pubchem

    r = cross_reference_ligands_chembl_pubchem("P04637", [])
    assert r["success"] is True
    assert r["data"]["ligands"] == []
    assert r["data"]["total"] == 0


@_LIVE_CHEMBL
def test_a11_cross_reference_isolates_per_ligand_errors():
    """A-11: a non-matching ligand does not sink the whole call."""
    from biomni.tool.allosteric import cross_reference_ligands_chembl_pubchem

    r = cross_reference_ligands_chembl_pubchem(
        "P04637",
        [{"ligand_name": "zzzznotarealcompoundname"},
         {"ligand_name": "imatinib"}],
    )
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 2
    assert "error" in r["data"]["ligands"][0]
    assert r["data"]["ligands"][1]["chembl_id"] == "CHEMBL941"


# --------------------------------------------------------------------------
# map_covalent_probes_to_allosteric  (A-12 .. A-14)
# --------------------------------------------------------------------------


def test_a12_map_covalent_probes_p00519():
    """A-12: P00519 has 23 ABL1 covalent-probe rows, all at site NT."""
    from biomni.tool.allosteric import map_covalent_probes_to_allosteric

    _need_covin()
    r = map_covalent_probes_to_allosteric("P00519", str(COVINDB))
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total_entries"] == 23
    assert d["war_head_counts"] == {"Michael Acceptor": 21, "Halohydrocarbon": 2}
    assert d["unique_inchi_keys"] == 6
    for rec in d["records"]:
        assert rec["Target_Gene"] == "ABL1"
        assert rec["Target_Name"] == "Tyrosine-protein kinase ABL1"
        assert rec["Site"] == "NT"
        assert rec["Parsed_Sites"] == ["NT"]
        assert rec["Allosteric_Candidate"] is True
        assert rec["Confidence"] == "High (Allosteric)"


def test_a13_map_covalent_probes_p04637_is_empty():
    """A-13: TP53 has no covalent-probe rows."""
    from biomni.tool.allosteric import map_covalent_probes_to_allosteric

    _need_covin()
    r = map_covalent_probes_to_allosteric("P04637", str(COVINDB))
    assert r["success"] is True, r.get("error")
    assert r["data"]["total_entries"] == 0
    assert r["data"]["records"] == []


def test_a14_map_covalent_probes_missing_dataset():
    """A-14: a missing dataset file is an error, not a crash."""
    from biomni.tool.allosteric import map_covalent_probes_to_allosteric

    r = map_covalent_probes_to_allosteric("P00519", "/nonexistent/CovInDB_All.csv")
    assert r["success"] is False
    assert "CovInDB" in r["error"] or "not found" in r["error"]


# --------------------------------------------------------------------------
# analyze_site_patterns  (A-15, A-16)
# --------------------------------------------------------------------------


def test_a15_analyze_site_patterns_counts_sites():
    """A-15: sites and residue types are counted."""
    from biomni.tool.allosteric import analyze_site_patterns

    df = pd.DataFrame({
        "Parsed_Sites": [["NT"], ["CYS-481"], ["SER-195"]],
    })
    r = analyze_site_patterns(df)
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total_unique_sites"] == 3
    assert d["total_entries"] == 3
    assert d["most_common_sites"][0] == ["NT", 1]
    assert ["CYS", 1] in d["residue_distribution"]
    assert ["SER", 1] in d["residue_distribution"]


def test_a16_analyze_site_patterns_without_parsed_sites():
    """A-16: a frame with no Parsed_Sites column yields zero sites."""
    from biomni.tool.allosteric import analyze_site_patterns

    r = analyze_site_patterns(pd.DataFrame({"Other": [1, 2, 3, 4]}))
    assert r["success"] is True, r.get("error")
    assert r["data"]["total_unique_sites"] == 0
    assert r["data"]["total_entries"] == 4
    assert r["data"]["most_common_sites"] == []


def test_a15b_analyze_site_patterns_accepts_the_tool_data_dict():
    """A-15 (second form): the data dict from the covalent-probe tool."""
    from biomni.tool.allosteric import (
        analyze_site_patterns,
        map_covalent_probes_to_allosteric,
    )

    _need_covin()
    probe = map_covalent_probes_to_allosteric("P00519", str(COVINDB))
    assert probe["success"] is True, probe.get("error")
    r = analyze_site_patterns(probe["data"])
    assert r["success"] is True, r.get("error")
    assert r["data"]["total_entries"] == 23
    assert r["data"]["total_unique_sites"] == 1
    assert r["data"]["most_common_sites"][0] == ["NT", 23]


# --------------------------------------------------------------------------
# biolip_ligands / parse_biolip_interactions  (A-17 .. A-21)
# --------------------------------------------------------------------------


def test_a17_biolip_ligands_1gg1():
    """A-17: 1GG1 has 8 BioLiP rows and two ligands."""
    from biomni.tool.biolip import biolip_ligands

    _need_biolip()
    r = biolip_ligands("1GG1")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["ligands"] == ["MN", "PGA"]
    assert d["total_interactions"] == 8
    assert d["chains"] == ["A", "B", "C", "D"]
    assert d["uniprot_ids"] == ["P0AB91"]


def test_a18_biolip_ligands_4hhb():
    """A-18: 4HHB binds HEM."""
    from biomni.tool.biolip import biolip_ligands

    _need_biolip()
    r = biolip_ligands("4HHB")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["ligands"] == ["HEM"]
    assert d["total_interactions"] == 4
    assert d["uniprot_ids"] == ["P68871", "P69905"]


def test_a19_biolip_ligands_2rtq_chain_b():
    """A-19: 2RTQ chain B binds IMI."""
    from biomni.tool.biolip import biolip_ligands

    _need_biolip()
    r = biolip_ligands("2RTQ", chain="B")
    assert r["success"] is True, r.get("error")
    assert r["data"]["ligands"] == ["IMI"]
    assert r["data"]["total_interactions"] == 1


def test_a20_biolip_ligands_1tim_is_absent():
    """A-20: 1TIM is not in BioLiP -> empty, successful."""
    from biomni.tool.biolip import biolip_ligands

    _need_biolip()
    r = biolip_ligands("1TIM")
    assert r["success"] is True, r.get("error")
    assert r["data"]["ligands"] == []
    assert r["data"]["total_interactions"] == 0


def test_a21_parse_biolip_interactions_chain_a():
    """A-21: 1GG1 chain A has 2 of the 8 interaction rows."""
    from biomni.tool.biolip import parse_biolip_interactions

    _need_biolip()
    r = parse_biolip_interactions("1GG1", "A")
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 2
    assert all(rec["Chain"] == "A" for rec in r["data"]["records"])


# --------------------------------------------------------------------------
# BioLiP sequence lookups  (B-1 .. B-12)
# --------------------------------------------------------------------------


def test_b1_biolip_protein_1a1k():
    """B-1: 1A1K chain A protein sequence (85 residues)."""
    from biomni.tool.biolip import biolip_protein

    _need_biolip()
    r = biolip_protein("1A1K")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total"] == 1
    rec = d["records"][0]
    assert rec["identifier"] == "1a1kA"
    assert rec["chain"] == "A"
    assert len(rec["sequence"]) == 85
    assert rec["sequence"].startswith(
        "RPYACPVESCDRRFSRSADLTRHIRIHTGQKPFQCRICMRNFSRSDHLTTHIRTHTGEKP"
    )


def test_b2_biolip_protein_is_case_insensitive():
    """B-2: '1a1k' + chain 'A' == '1A1K'."""
    from biomni.tool.biolip import biolip_protein

    _need_biolip()
    a = biolip_protein("1A1K")
    b = biolip_protein("1a1k", chain="A")
    assert b["success"] is True
    assert b["data"]["records"] == a["data"]["records"]


def test_b3_biolip_protein_unknown_chain():
    """B-3: 1A1K chain B is not in the protein snapshot."""
    from biomni.tool.biolip import biolip_protein

    _need_biolip()
    r = biolip_protein("1A1K", chain="B")
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 0


def test_b4_biolip_dna_1a1k():
    """B-4: 1A1K has two DNA chains."""
    from biomni.tool.biolip import biolip_dna

    _need_biolip()
    r = biolip_dna("1A1K")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total"] == 2
    assert [rec["identifier"] for rec in d["records"]] == [
        "1a1k_dna_B", "1a1k_dna_C"
    ]
    assert d["records"][0]["sequence"] == "agcgtgggacc"


def test_b5_biolip_dna_single_chain():
    """B-5: 1A1K DNA chain B alone."""
    from biomni.tool.biolip import biolip_dna

    _need_biolip()
    r = biolip_dna("1A1K", chain="B")
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 1
    assert r["data"]["records"][0]["identifier"] == "1a1k_dna_B"


def test_b6_biolip_dna_rejects_multi_letter_chain():
    """B-6: a DNA chain must be a single letter."""
    from biomni.tool.biolip import biolip_dna

    r = biolip_dna("1A1K", chain="BC")
    assert r["success"] is False
    assert "single letter" in r["error"]


def test_b7_biolip_rna_8a3w():
    """B-7: 8A3W has ten RNA chains; S1 is 1663 nt long."""
    from biomni.tool.biolip import biolip_rna

    _need_biolip()
    r = biolip_rna("8A3W")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total"] == 10
    assert d["records"][0]["identifier"] == "8a3w_rna_S1"
    assert len(d["records"][0]["sequence"]) == 1663


def test_b8_biolip_rna_single_chain():
    """B-8: 8A3W RNA chain S1 alone."""
    from biomni.tool.biolip import biolip_rna

    _need_biolip()
    r = biolip_rna("8A3W", chain="S1")
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 1
    assert r["data"]["records"][0]["identifier"] == "8a3w_rna_S1"


def test_b9_biolip_peptide_4a1g():
    """B-9: 4A1G has four peptide chains."""
    from biomni.tool.biolip import biolip_peptide

    _need_biolip()
    r = biolip_peptide("4A1G")
    assert r["success"] is True, r.get("error")
    d = r["data"]
    assert d["total"] == 4
    assert [rec["identifier"] for rec in d["records"]] == [
        "4a1g_peptide_E", "4a1g_peptide_F", "4a1g_peptide_G", "4a1g_peptide_H"
    ]
    assert d["records"][0]["sequence"] == "KIDTTSFLANLK"
    assert len(d["records"][0]["sequence"]) == 12


def test_b10_biolip_peptide_single_chain():
    """B-10: 4A1G peptide chain E alone."""
    from biomni.tool.biolip import biolip_peptide

    _need_biolip()
    r = biolip_peptide("4A1G", chain="E")
    assert r["success"] is True, r.get("error")
    assert r["data"]["total"] == 1
    assert r["data"]["records"][0]["identifier"] == "4a1g_peptide_E"


def test_b11_biolip_rejects_bad_pdb_id_length():
    """B-11: a 3-character id is rejected."""
    from biomni.tool.biolip import biolip_protein

    r = biolip_protein("ABC")
    assert r["success"] is False
    assert "4-character" in r["error"]


def test_b12_biolip_rna_rejects_long_chain():
    """B-12: an RNA chain longer than two letters is rejected."""
    from biomni.tool.biolip import biolip_rna

    r = biolip_rna("8A3W", chain="S12")
    assert r["success"] is False
    assert "1-2 letters" in r["error"]

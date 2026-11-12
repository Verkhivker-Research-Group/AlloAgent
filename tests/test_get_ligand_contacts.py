"""P32 get_ligand_contacts known-answer tests (criteria GLC-1..GLC-18).

The criteria are committed in docs/2_get_ligand_contacts_criteria.md.
Every expected contact list and distance in this file was computed
independently from the real RCSB mmCIF files BEFORE the tool existed
(see the "How the expected values were fixed" section of the criteria).

The network tests hit files.rcsb.org and the RCSB Data API. They are
collected inside the container (which has outbound HTTPS) and skip with
a clear message on a host without network access.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Expected contacts at 4.0 A: (chain, pdb_number, residue_name, distance)
EXPECTED_4A = {
    ("1T4J", "FRJ"): [
        ("A", 188, "PRO", 3.92), ("A", 189, "ALA", 3.42), ("A", 192, "LEU", 3.80),
        ("A", 193, "ASN", 3.01), ("A", 196, "PHE", 3.55), ("A", 200, "GLU", 3.30),
        ("A", 276, "GLU", 2.55), ("A", 277, "GLY", 3.37), ("A", 279, "LYS", 3.03),
        ("A", 280, "PHE", 2.65), ("A", 282, "MET", 3.59),
    ],
    ("1OPK", "MYR"): [
        ("A", 359, "LEU", 3.84), ("A", 360, "LEU", 3.69), ("A", 363, "ALA", 3.71),
        ("A", 448, "LEU", 3.73), ("A", 452, "ALA", 3.85), ("A", 481, "GLU", 3.47),
        ("A", 521, "ILE", 3.87), ("A", 529, "LEU", 3.54),
    ],
    ("1OPK", "P16"): [
        ("A", 267, "LEU", 3.85), ("A", 272, "TYR", 3.31), ("A", 275, "VAL", 3.56),
        ("A", 288, "ALA", 3.45), ("A", 289, "VAL", 3.91), ("A", 290, "LYS", 3.65),
        ("A", 305, "GLU", 3.32), ("A", 309, "MET", 3.34), ("A", 318, "VAL", 3.95),
        ("A", 332, "ILE", 3.63), ("A", 334, "THR", 3.24), ("A", 335, "GLU", 3.35),
        ("A", 336, "PHE", 3.77), ("A", 337, "MET", 2.84), ("A", 340, "GLY", 3.48),
        ("A", 389, "LEU", 3.56), ("A", 399, "ALA", 3.59), ("A", 400, "ASP", 3.56),
        ("A", 401, "PHE", 3.75),
    ],
    ("5MO4", "AY7"): [
        ("A", 351, "ARG", 3.79), ("A", 356, "ALA", 3.68), ("A", 359, "LEU", 3.22),
        ("A", 360, "LEU", 3.38), ("A", 363, "ALA", 3.57), ("A", 448, "LEU", 3.27),
        ("A", 451, "ILE", 3.61), ("A", 452, "ALA", 3.52), ("A", 453, "THR", 3.48),
        ("A", 454, "TYR", 3.87), ("A", 481, "GLU", 2.82), ("A", 483, "CYS", 3.84),
        ("A", 484, "PRO", 3.73), ("A", 487, "VAL", 3.68), ("A", 512, "PHE", 3.63),
        ("A", 521, "ILE", 3.62), ("A", 525, "VAL", 3.67), ("A", 529, "LEU", 3.76),
    ],
    ("5MO4", "NIL"): [
        ("A", 267, "LEU", 3.71), ("A", 272, "TYR", 3.55), ("A", 275, "VAL", 3.81),
        ("A", 288, "ALA", 3.29), ("A", 289, "VAL", 3.98), ("A", 290, "LYS", 3.39),
        ("A", 304, "LYS", 3.83), ("A", 305, "GLU", 2.95), ("A", 308, "VAL", 3.63),
        ("A", 309, "MET", 3.47), ("A", 312, "ILE", 3.64), ("A", 317, "LEU", 3.55),
        ("A", 318, "VAL", 3.57), ("A", 332, "ILE", 3.49), ("A", 334, "ILE", 3.25),
        ("A", 336, "PHE", 3.45), ("A", 337, "MET", 2.84), ("A", 340, "GLY", 3.86),
        ("A", 378, "PHE", 3.63), ("A", 380, "HIS", 3.38), ("A", 389, "LEU", 3.70),
        ("A", 398, "VAL", 3.75), ("A", 399, "ALA", 3.20), ("A", 400, "ASP", 3.01),
        ("A", 401, "PHE", 3.34),
    ],
    ("1V4S", "MRK"): [
        ("A", 61, "TYR", 3.25), ("A", 62, "VAL", 3.62), ("A", 63, "ARG", 2.73),
        ("A", 64, "SER", 3.64), ("A", 65, "THR", 3.41), ("A", 66, "PRO", 3.77),
        ("A", 210, "MET", 3.66), ("A", 211, "ILE", 3.59), ("A", 214, "TYR", 3.01),
        ("A", 215, "TYR", 2.45), ("A", 220, "CYS", 3.30), ("A", 235, "MET", 3.51),
        ("A", 452, "VAL", 3.62), ("A", 455, "VAL", 3.46),
    ],
    ("1V4S", "GLC"): [
        ("A", 151, "SER", 3.57), ("A", 152, "PHE", 3.29), ("A", 153, "PRO", 3.39),
        ("A", 168, "THR", 2.90), ("A", 169, "LYS", 2.97), ("A", 204, "ASN", 2.96),
        ("A", 205, "ASP", 2.53), ("A", 225, "ILE", 3.65), ("A", 229, "GLY", 3.65),
        ("A", 230, "CYS", 3.54), ("A", 231, "ASN", 3.23), ("A", 256, "GLU", 2.59),
        ("A", 287, "GLN", 3.48), ("A", 290, "GLU", 2.53),
    ],
}

# Expected contacts at 3.0 A: (chain, pdb_number, residue_name)
EXPECTED_3A = {
    ("1T4J", "FRJ"): [("A", 276, "GLU"), ("A", 280, "PHE")],
    ("1OPK", "MYR"): [],
    ("1OPK", "P16"): [("A", 337, "MET")],
    ("5MO4", "AY7"): [("A", 481, "GLU")],
    ("5MO4", "NIL"): [("A", 305, "GLU"), ("A", 337, "MET")],
    ("1V4S", "MRK"): [("A", 63, "ARG"), ("A", 215, "TYR")],
    ("1V4S", "GLC"): [
        ("A", 168, "THR"), ("A", 169, "LYS"), ("A", 204, "ASN"),
        ("A", 205, "ASP"), ("A", 256, "GLU"), ("A", 290, "GLU"),
    ],
}

# Ligand instance (chain, PDB number) and the other component ids present.
EXPECTED_LIGAND = {
    ("1T4J", "FRJ"): (("A", 299), ["FRJ"]),
    ("1OPK", "MYR"): (("A", 1), ["GOL", "MYR", "P16"]),
    ("1OPK", "P16"): (("A", 2), ["GOL", "MYR", "P16"]),
    ("5MO4", "AY7"): (("A", 602), ["AY7", "NIL"]),
    ("5MO4", "NIL"): (("A", 601), ["AY7", "NIL"]),
    ("1V4S", "MRK"): (("A", 501), ["GLC", "MRK", "NA"]),
    ("1V4S", "GLC"): (("A", 500), ["GLC", "MRK", "NA"]),
}

# UniProt accession per entry, and the PDB-number -> UniProt-number offset.
EXPECTED_UNIPROT = {
    "1T4J": ("P18031", 0),
    "1OPK": ("P00520", -19),
    "5MO4": ("P00519", -19),
    "1V4S": ("P35557", 0),
}

ALL_CASES = list(EXPECTED_4A)


def _live_rcsb_available() -> bool:
    try:
        import requests

        r = requests.get("https://files.rcsb.org/download/1T4J.cif", timeout=15)
        return r.status_code == 200
    except Exception:
        return False


_LIVE_RCSB = pytest.mark.skipif(
    not _live_rcsb_available(),
    reason="RCSB not reachable from this host",
)


def _call(pdb_id: str, ligand_id: str, chain: str | None = "A", cutoff: float = 4.0):
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    return get_ligand_contacts(
        pdb_id=pdb_id, ligand_id=ligand_id, chain=chain, cutoff=cutoff
    )


def _as_tuples(contacts: list[dict]) -> list[tuple]:
    return [
        (c["chain"], c["pdb_number"], c["residue_name"], c["min_distance"])
        for c in contacts
    ]


# --- GLC-1: the module and the entry point exist ----------------------------


def test_glc_1_module_and_entry_point_exist():
    impl = REPO / "biomni" / "tool" / "get_ligand_contacts.py"
    assert impl.is_file(), f"missing {impl}"
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    assert callable(get_ligand_contacts)


# --- GLC-2: the return contract -------------------------------------------


@_LIVE_RCSB
def test_glc_2_return_contract_keys_present():
    result = _call("1T4J", "FRJ")
    for key in ("success", "data", "error", "source", "source_version", "query_time_utc"):
        assert key in result, f"missing contract key {key}"
    assert result["success"] is True
    assert result["error"] is None

    failed = _call("1T4J", "ZZZ")
    for key in ("success", "data", "error", "source", "source_version", "query_time_utc"):
        assert key in failed, f"missing contract key {key}"
    assert failed["success"] is False
    assert failed["error"]


# --- GLC-3: the ligand is found by id, with chain and PDB number ------------


@_LIVE_RCSB
@pytest.mark.parametrize("pdb_id,ligand_id", ALL_CASES)
def test_glc_3_ligand_instance_found(pdb_id, ligand_id):
    result = _call(pdb_id, ligand_id)
    assert result["success"] is True, result.get("error")
    expected_instance, expected_present = EXPECTED_LIGAND[(pdb_id, ligand_id)]
    ligand = result["data"]["ligand"]
    assert ligand["id"] == ligand_id
    assert (ligand["chain"], ligand["pdb_number"]) == expected_instance
    assert result["data"]["ligand_ids_present"] == expected_present


# --- GLC-4..GLC-10: the known-answer contact lists --------------------------


@_LIVE_RCSB
@pytest.mark.parametrize("pdb_id,ligand_id", ALL_CASES)
def test_glc_known_answer_contacts_at_4_angstrom(pdb_id, ligand_id):
    result = _call(pdb_id, ligand_id, cutoff=4.0)
    assert result["success"] is True, result.get("error")
    expected = EXPECTED_4A[(pdb_id, ligand_id)]
    contacts = result["data"]["contacts"]
    assert result["data"]["contact_count"] == len(expected)
    assert len(contacts) == len(expected)
    for got, want in zip(_as_tuples(contacts), expected):
        assert got[0] == want[0]
        assert got[1] == want[1]
        assert got[2] == want[2]
        # The criteria state the distance to 2 decimals, so the check is
        # to that precision: one unit in the last stated decimal
        # (0.01 A), with a float slack so that a difference of exactly
        # 0.01 A is not rejected by binary rounding.  See the dated note
        # in docs/2_get_ligand_contacts_criteria.md: the stated values
        # were rendered from a 3-decimal rounding, so three of the 96
        # values sit on the other side of a 2-decimal boundary.
        assert abs(got[3] - want[3]) <= 0.010000001


# --- GLC-11: the cutoff is monotonic ---------------------------------------


@_LIVE_RCSB
@pytest.mark.parametrize("pdb_id,ligand_id", ALL_CASES)
def test_glc_11_cutoff_is_monotonic(pdb_id, ligand_id):
    at_4 = _call(pdb_id, ligand_id, cutoff=4.0)
    at_3 = _call(pdb_id, ligand_id, cutoff=3.0)
    assert at_4["success"] is True
    assert at_3["success"] is True
    keys_4 = [(c["chain"], c["pdb_number"]) for c in at_4["data"]["contacts"]]
    keys_3 = [(c["chain"], c["pdb_number"]) for c in at_3["data"]["contacts"]]
    assert set(keys_3).issubset(set(keys_4)), "3 A contacts must be a subset of 4 A"
    expected_3 = EXPECTED_3A[(pdb_id, ligand_id)]
    assert keys_3 == [(c, n) for c, n, _ in expected_3]


# --- GLC-12: the SIFTS mapping ---------------------------------------------


@_LIVE_RCSB
@pytest.mark.parametrize("pdb_id,ligand_id", ALL_CASES)
def test_glc_12_sifts_uniprot_numbers(pdb_id, ligand_id):
    result = _call(pdb_id, ligand_id)
    assert result["success"] is True
    accession, offset = EXPECTED_UNIPROT[pdb_id]
    contacts = result["data"]["contacts"]
    assert contacts
    for contact in contacts:
        assert contact["uniprot_accession"] == accession
        assert contact["uniprot_number"] == contact["pdb_number"] + offset
    for contact in contacts[:3]:
        assert isinstance(contact["uniprot_number"], int)


# --- GLC-13: the negative control (unknown ligand id) -----------------------


@_LIVE_RCSB
@pytest.mark.parametrize("pdb_id,ligand_id", ALL_CASES)
def test_glc_13_unknown_ligand_id_lists_present_ids(pdb_id, ligand_id):
    result = _call(pdb_id, "ZZZ")
    assert result["success"] is False
    assert result["error"]
    expected_instance, expected_present = EXPECTED_LIGAND[(pdb_id, ligand_id)]
    assert result["data"] is not None
    assert result["data"]["ligand_ids_present"] == expected_present
    assert result["data"]["contacts"] == []


# --- GLC-14: a local structure file gives the same answer -------------------


@_LIVE_RCSB
def test_glc_14_local_structure_file_gives_the_same_answer(tmp_path):
    import requests

    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    text = requests.get(
        "https://files.rcsb.org/download/1T4J.cif", timeout=60
    ).text
    path = tmp_path / "1T4J.cif"
    path.write_text(text, encoding="utf-8")

    from_id = get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ", chain="A")
    from_file = get_ligand_contacts(
        structure_file=str(path), ligand_id="FRJ", chain="A"
    )
    assert from_id["success"] is True
    assert from_file["success"] is True
    assert from_file["data"]["pdb_id"] == "1T4J"
    assert _as_tuples(from_file["data"]["contacts"]) == _as_tuples(
        from_id["data"]["contacts"]
    )
    assert from_file["data"]["contact_count"] == len(EXPECTED_4A[("1T4J", "FRJ")])


# --- GLC-15: invalid input handling ----------------------------------------


def test_glc_15_invalid_inputs_return_success_false():
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    assert get_ligand_contacts(pdb_id="1T4J", ligand_id="")["success"] is False
    assert get_ligand_contacts(pdb_id="1T4J", ligand_id=None)["success"] is False
    assert get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ", cutoff=0)["success"] is False
    assert get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ", cutoff=-1)["success"] is False
    assert get_ligand_contacts(ligand_id="FRJ")["success"] is False
    for result in (
        get_ligand_contacts(pdb_id="1T4J", ligand_id=""),
        get_ligand_contacts(ligand_id="FRJ"),
        get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ", cutoff=0),
    ):
        assert result["error"], "an invalid input must carry an error message"


# --- GLC-16: the scope statement -------------------------------------------


def test_glc_16_docstring_states_the_scope():
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    doc = get_ligand_contacts.__doc__ or ""
    lowered = doc.lower()
    assert "geometric proximity" in lowered
    assert "binding energy" in lowered
    assert "not" in lowered


# --- GLC-17: the tool card -------------------------------------------------


def test_glc_17_tool_card_exists_and_has_no_self_reported():
    card = REPO / "docs" / "tool_cards" / "P32_get_ligand_contacts.md"
    assert card.is_file(), f"missing {card}"
    text = card.read_text(encoding="utf-8")
    assert "self-reported" not in text, (
        f"tool card {card} contains forbidden 'self-reported' substring"
    )


# --- GLC-18: the tool is exposed to arm D ----------------------------------


def test_glc_18_tool_is_exposed():
    exposed = REPO / "alloagent" / "exposed_tools.txt"
    names = [
        line.strip()
        for line in exposed.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert "get_ligand_contacts" in names
    # 2026-10-26: deliberate re-pin, 44 -> 45.  `allosteric_site_workflow`
    # is exposed because W1, W2 and W3 of
    # docs/2_allosteric_site_workflow_criteria.md now pass (the fpocket
    # wrapper returns the per-pocket residues, so W1's overlap is 8).
    assert "allosteric_site_workflow" in names
    assert len(names) == 45, f"expected 45 exposed tools, found {len(names)}"

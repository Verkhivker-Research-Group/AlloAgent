"""Part 1 - the fpocket wrapper's per-pocket residues.

The criteria are committed at docs/1_fpocket_criteria.md; the numbers
here are the ones an independent calculation (parsing fpocket's own
pockets/pocketN_atm.pdb without the wrapper) produced for 1T4J.

The tests are network-dependent (the structure comes from RCSB and the
UniProt mapping from the PDBe API).  A skipped test is not a pass, so
the skip is only taken when the network is genuinely unreachable and
the test says so in its reason.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest

FRJ_CONTACTS = {188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282}

# The residue counts per pocket, from the independent parse of
# pockets/pocketN_atm.pdb for 1T4J (docs/1_fpocket_criteria.md).
EXPECTED_RESIDUE_COUNTS = {
    1: 9, 2: 12, 3: 15, 4: 10, 5: 12, 6: 8, 7: 10, 8: 15, 9: 6,
    10: 9, 11: 12, 12: 11, 13: 11, 14: 10, 15: 7, 16: 11, 17: 8, 18: 7,
}


def _rcsb_available() -> bool:
    try:
        with urllib.request.urlopen(
            "https://files.rcsb.org/download/1T4J.pdb", timeout=30
        ) as response:
            return response.status == 200
    except Exception:
        return False


def _pdbe_available() -> bool:
    try:
        import requests

        response = requests.get(
            "https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/1T4J", timeout=30
        )
        return response.status_code == 200
    except Exception:
        return False


_LIVE = pytest.mark.skipif(
    not _rcsb_available(),
    reason="RCSB is unreachable from this host, so 1T4J cannot be fetched",
)


def _strip_hetatm(text: str) -> str:
    return "".join(
        line for line in text.splitlines(keepends=True)
        if not (line.startswith("HETATM") or line.startswith("HET "))
    )


def _independent_pocket_residues(pdb_path: Path) -> dict[int, set[tuple[str, int, str]]]:
    """Parse fpocket's own pocket files, independently of the wrapper."""
    out_dir = pdb_path.parent / (pdb_path.stem + "_out")
    residues: dict[int, set[tuple[str, int, str]]] = {}
    for pocket_file in sorted(out_dir.glob("pockets/pocket*_atm.pdb")):
        number = int(re.search(r"pocket(\d+)_atm", pocket_file.name).group(1))
        found: set[tuple[str, int, str]] = set()
        for line in pocket_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("ATOM") or len(line) < 27:
                continue
            residue_name = line[17:20].strip()
            chain = line[21].strip()
            try:
                residue_number = int(line[22:26].strip())
            except ValueError:
                continue
            found.add((chain, residue_number, residue_name))
        residues[number] = found
    return residues


@_LIVE
def test_fpocket_every_pocket_has_a_non_empty_residue_list():
    """Criterion 1: 18 pockets, every one with a non-empty residue list
    whose length matches the independent parse."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(_strip_hetatm(source.read_text(encoding="utf-8")), encoding="utf-8")

        result = detect_pockets_fpocket(str(stripped))
        assert result["success"] is True, result.get("error")
        pockets = result["data"]["pockets"]
        assert len(pockets) == 18, f"expected 18 pockets, got {len(pockets)}"

        for pocket in pockets:
            residues = pocket.get("residues")
            assert isinstance(residues, list), f"pocket {pocket['pocket_number']} has no residues"
            assert residues, f"pocket {pocket['pocket_number']} has an empty residue list"
            number = pocket["pocket_number"]
            assert len(residues) == EXPECTED_RESIDUE_COUNTS[number], (
                f"pocket {number}: {len(residues)} residues, expected "
                f"{EXPECTED_RESIDUE_COUNTS[number]}")


@_LIVE
def test_fpocket_residues_equal_the_independent_parse():
    """Criterion 2: the (chain, residue number, residue name) triples
    equal the independent parse of pockets/pocketN_atm.pdb."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(_strip_hetatm(source.read_text(encoding="utf-8")), encoding="utf-8")

        result = detect_pockets_fpocket(str(stripped))
        assert result["success"] is True, result.get("error")

        # fpocket writes its output next to the input it was given, so
        # the independent parse runs fpocket itself on the same file.
        import subprocess

        proc = subprocess.run(
            ["fpocket", "-f", str(stripped)], capture_output=True, text=True, timeout=300
        )
        assert proc.returncode == 0, proc.stderr[-400:]
        independent = _independent_pocket_residues(stripped)
        assert independent, "the independent parse found no pocket files"

        for pocket in result["data"]["pockets"]:
            number = pocket["pocket_number"]
            wrapper_set = {
                (r["chain"], r["residue_number"], r["residue_name"])
                for r in pocket["residues"]
            }
            assert wrapper_set == independent[number], (
                f"pocket {number}: the wrapper's residues differ from the "
                f"independent parse")


@_LIVE
def test_fpocket_frj_overlap_is_8_at_pocket_11():
    """Criterion 3: the maximum overlap with the 11 FRJ contact
    residues is 8, reached by pocket 11."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(_strip_hetatm(source.read_text(encoding="utf-8")), encoding="utf-8")

        result = detect_pockets_fpocket(str(stripped))
        assert result["success"] is True, result.get("error")

        overlaps = {}
        for pocket in result["data"]["pockets"]:
            numbers = {r["residue_number"] for r in pocket["residues"]}
            overlaps[pocket["pocket_number"]] = numbers & FRJ_CONTACTS

        best_pocket = max(overlaps, key=lambda number: len(overlaps[number]))
        assert len(overlaps[best_pocket]) == 8, (
            f"the maximum FRJ overlap is {len(overlaps[best_pocket])}, expected 8: "
            f"{overlaps}")
        assert best_pocket == 11, f"the best pocket is {best_pocket}, expected 11"
        assert overlaps[11] == {188, 189, 192, 193, 196, 276, 277, 280}, overlaps[11]


@_LIVE
def test_fpocket_top3_pockets_have_no_frj_overlap():
    """Criterion 4: the recorded fact about fpocket's ranking - the
    top three pockets by score do NOT cover the FRJ site, and the
    FRJ-covering pocket ranks 11th of 18."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(_strip_hetatm(source.read_text(encoding="utf-8")), encoding="utf-8")

        result = detect_pockets_fpocket(str(stripped))
        assert result["success"] is True, result.get("error")

        pockets = result["data"]["pockets"]
        ranked = sorted(
            pockets, key=lambda pocket: pocket.get("score") or 0.0, reverse=True
        )
        top3 = ranked[:3]
        for pocket in top3:
            numbers = {r["residue_number"] for r in pocket["residues"]}
            assert not (numbers & FRJ_CONTACTS), (
                f"pocket {pocket['pocket_number']} unexpectedly covers the FRJ site")
        assert [pocket["pocket_number"] for pocket in top3] == [1, 2, 3]
        assert ranked[10]["pocket_number"] == 11, (
            "the FRJ-covering pocket is not ranked 11th by score")


@_LIVE
@pytest.mark.skipif(
    not _pdbe_available(),
    reason="the PDBe mappings API is unreachable, so the UniProt mapping "
           "cannot be checked; a skip is not a pass, so this is reported",
)
def test_fpocket_uniprot_numbers_for_1t4j_chain_a():
    """Criterion 5: for 1T4J chain A the UniProt accession is P18031
    (PTP1B - see the dated correction in docs/1_fpocket_criteria.md)
    and the UniProt number equals the PDB residue number."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(_strip_hetatm(source.read_text(encoding="utf-8")), encoding="utf-8")

        result = detect_pockets_fpocket(str(stripped))
        assert result["success"] is True, result.get("error")

        checked = 0
        for pocket in result["data"]["pockets"]:
            for residue in pocket["residues"]:
                if residue["chain"] != "A":
                    continue
                checked += 1
                assert residue["uniprot_accession"] == "P18031", residue
                assert residue["uniprot_number"] == residue["residue_number"], residue
        assert checked > 0, "no chain A residue was found"

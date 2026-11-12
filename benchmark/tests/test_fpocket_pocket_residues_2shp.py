"""Part 1 - the fpocket wrapper's per-pocket residues, on 2SHP.

The wrapper returns, for every pocket fpocket finds, the residues that line
it, parsed from fpocket's own `pockets/pocketN_atm.pdb`. The expected
per-pocket residue counts are the ones committed in the benchmark checklist
for P03 (the 2SHP prompt), and the residues themselves are checked against
an independent parse of fpocket's output, so a wrapper bug cannot pass the
test.

The structure is the ligand-stripped 2SHP from the read-only structure
cache (`data/structures_cache/2shp.pdb`), the structure the committed
reference was measured on.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
STRUCTURE_CANDIDATES = (
    REPO / "data" / "structures_cache" / "2shp.pdb",
    Path("/data/structures/2shp.pdb"),
)


def _structure() -> Path | None:
    for candidate in STRUCTURE_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _expected_from_the_checklist() -> list[int]:
    """The committed residue counts of the top three 2SHP pockets (the P03 item)."""
    checklists = json.loads((REPO / "benchmark" / "checklists.json").read_text(encoding="utf-8"))
    for prompt in checklists["prompts"]:
        if prompt["id"] != "P03":
            continue
        top3 = next(i for i in prompt["checklist"] if i["key"] == "fpocket_top3")
        return [pocket["residues"] for pocket in top3["value"]]
    raise AssertionError("the P03 fpocket_top3 item is not in the committed checklist")


def _independent_pocket_residues(out_dir: Path) -> dict[int, set[tuple[str, int, str]]]:
    """Parse fpocket's own pocketN_atm.pdb files, without the wrapper."""
    residues: dict[int, set[tuple[str, int, str]]] = {}
    for path in sorted(out_dir.glob("pockets/pocket*_atm.pdb")):
        match = re.search(r"pocket(\d+)_atm", path.name)
        if not match:
            continue
        found: set[tuple[str, int, str]] = set()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("ATOM") or len(line) < 27:
                continue
            residue_name = line[17:20].strip()
            chain = line[21].strip()
            try:
                residue_number = int(line[22:26].strip())
            except ValueError:
                continue
            if residue_name:
                found.add((chain, residue_number, residue_name))
        residues[int(match.group(1))] = found
    return residues


_STRUCTURE = _structure()
_NO_STRUCTURE = pytest.mark.skipif(
    _STRUCTURE is None, reason="the 2SHP structure is not on this host")
_NO_FPOCKET = pytest.mark.skipif(
    shutil.which("fpocket") is None, reason="fpocket is not on PATH")


@_NO_STRUCTURE
def test_fpocket_2shp_pocket_residue_counts_match_the_committed_reference():
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    expected_top3 = _expected_from_the_checklist()
    result = detect_pockets_fpocket(_STRUCTURE)
    assert result["success"] is True, result.get("error")
    pockets = result["data"]["pockets"]
    assert len(pockets) >= 3, f"expected at least three pockets, got {len(pockets)}"
    counts = [len(pocket["residues"]) for pocket in pockets]
    assert counts[:3] == expected_top3, (
        f"the top three residue counts of 2SHP: {counts[:3]} != {expected_top3}"
    )
    for pocket in pockets:
        for residue in pocket["residues"]:
            assert set(residue) == {
                "chain", "residue_number", "residue_name",
                "uniprot_accession", "uniprot_number",
            }, f"unexpected residue keys: {sorted(residue)}"
            assert residue["residue_name"]
            assert isinstance(residue["residue_number"], int)


@_NO_STRUCTURE
@_NO_FPOCKET
def test_fpocket_2shp_residues_are_fpockets_own_atoms():
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    with tempfile.TemporaryDirectory() as tmp:
        from biomni.tool.detect_pockets_fpocket import _strip_hetatm

        work = Path(tmp) / "2shp.pdb"
        _strip_hetatm(_STRUCTURE, work)
        subprocess.run(["fpocket", "-f", str(work)], capture_output=True, text=True,
                       timeout=600, check=False)
        out_dir = work.parent / (work.stem + "_out")
        assert out_dir.is_dir(), "fpocket wrote no output directory"
        independent = _independent_pocket_residues(out_dir)
        assert independent, "fpocket wrote no pocket atom files"
        result = detect_pockets_fpocket(_STRUCTURE)
        assert result["success"] is True, result.get("error")
        for pocket in result["data"]["pockets"]:
            number = pocket["pocket_number"]
            if number not in independent:
                continue
            mine = {
                (r["chain"], r["residue_number"], r["residue_name"]) for r in pocket["residues"]
            }
            assert mine == independent[number], (
                f"pocket {number} of 2SHP: the wrapper's residues differ from "
                "fpocket's own pocketN_atm.pdb"
            )

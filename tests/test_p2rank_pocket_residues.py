"""Part 1, Criterion 6 - the P2Rank wrapper's residues, checked the
same way as the fpocket wrapper's.

The criteria are committed at docs/1_fpocket_criteria.md (Criterion 6).
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest


def _rcsb_available() -> bool:
    try:
        with urllib.request.urlopen(
            "https://files.rcsb.org/download/1T4J.pdb", timeout=30
        ) as response:
            return response.status == 200
    except Exception:
        return False


_LIVE = pytest.mark.skipif(
    not _rcsb_available(),
    reason="RCSB is unreachable from this host, so 1T4J cannot be fetched",
)


def _independent_residues_csv(csv_path: Path) -> dict[int, list[dict[str, str]]]:
    """Parse P2Rank's own `<input>_residues.csv`, independently.

    The CSV columns are `chain, residue_label, residue_name, score,
    zscore, probability, pocket`; the `pocket` column is the pocket
    number, and the value 0 is the group of residues that are in no
    pocket at all (250 of them for 1T4J), so the real pockets are the
    1-based groups.
    """
    by_rank: dict[int, list[dict[str, str]]] = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            try:
                rank = int(row.get("pocket", ""))
            except (TypeError, ValueError):
                continue
            by_rank.setdefault(rank, []).append(row)
    return by_rank


@_LIVE
def test_p2rank_every_pocket_has_a_non_empty_residue_list():
    """Criterion 6: every P2Rank pocket has a non-empty residue list."""
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(
            "".join(
                line for line in source.read_text(encoding="utf-8").splitlines(keepends=True)
                if not (line.startswith("HETATM") or line.startswith("HET "))
            ),
            encoding="utf-8",
        )

        result = detect_pockets_p2rank(str(stripped))
        assert result["success"] is True, result.get("error")
        pockets = result["data"]["pockets"]
        assert pockets, "P2Rank returned no pockets"
        for pocket in pockets:
            residues = pocket.get("residues")
            assert isinstance(residues, list), pocket
            assert residues, f"P2Rank pocket {pocket.get('rank')} has no residues"


@_LIVE
def test_p2rank_residues_equal_the_independent_parse():
    """Criterion 6: the residue lists agree with an independent parse
    of P2Rank's own `<input>_residues.csv`."""
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "1T4J.pdb"
        urllib.request.urlretrieve(
            "https://files.rcsb.org/download/1T4J.pdb", source
        )
        stripped = Path(tmp) / "1T4J_stripped.pdb"
        stripped.write_text(
            "".join(
                line for line in source.read_text(encoding="utf-8").splitlines(keepends=True)
                if not (line.startswith("HETATM") or line.startswith("HET "))
            ),
            encoding="utf-8",
        )

        result = detect_pockets_p2rank(str(stripped))
        assert result["success"] is True, result.get("error")

        out_dir = Path(tmp) / "prank_out"
        out_dir.mkdir()
        proc = subprocess.run(
            ["prank", "predict", "-f", str(stripped), "-o", str(out_dir)],
            capture_output=True, text=True, timeout=900, cwd=tmp,
        )
        assert proc.returncode == 0, proc.stderr[-400:]
        csv_path = out_dir / f"{stripped.name}_residues.csv"
        assert csv_path.is_file(), f"{csv_path} was not produced"
        independent = _independent_residues_csv(csv_path)
        assert independent, "the independent parse found no rows"

        for pocket in result["data"]["pockets"]:
            rank = pocket["rank"]
            wrapper_rows = [
                (str(row.get("chain", "")), str(row.get("residue_label", "")),
                 str(row.get("residue_name", "")))
                for row in pocket["residues"]
            ]
            independent_rows = [
                (str(row.get("chain", "")), str(row.get("residue_label", "")),
                 str(row.get("residue_name", "")))
                for row in independent.get(rank, [])
            ]
            assert wrapper_rows == independent_rows, (
                f"P2Rank pocket {rank}: the wrapper's residues differ from the "
                f"independent parse ({len(wrapper_rows)} vs "
                f"{len(independent_rows)} rows)")

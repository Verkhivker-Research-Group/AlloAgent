"""The reference outputs of the pocket detectors, with the corrected selection.

This is the **second** version of ``benchmark/pocket_reference_outputs.py``.
The committed version and its output (``benchmark/pocket_reference_outputs.json``)
are kept exactly as they are; this script only adds the measurement that the
dated correction note of 2026-11-02 needs.

THE DEFECT IT MEASURES.  The committed reference picks "the pocket that
covers the site" as the **first** pocket in rank order that contains **any**
site residue:

    best = None
    for row in rows:
        if row["site_residues_in_pocket"] > 0:
            best = row
            break

while the same script's docstring defines it as "the pocket with the
**most** site residues".  The two rules differ wherever a later pocket
covers the site better: for 1T4J/FRJ the committed value is rank 7 with 2
site residues while rank 11 covers 8 of them, which is what the dated
note of the checklist says.

This script computes **both** selections and writes the per-pocket
residues, so the correction is checkable number by number.

    python benchmark/pocket_reference_outputs_v2.py <out.json> [pdb_id ...]
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, "/workspace")

from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket
from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

# The structures and the ligand whose contacts define the site.  The same
# table as the committed version.
SITES = {
    "1T4J": {"ligand": "FRJ", "chain": "A", "site": "the FRJ allosteric site"},
    "1OPK": {"ligand": "MYR", "chain": "A", "site": "the myristoyl site"},
    "1V4S": {"ligand": "MRK", "chain": "A", "site": "the allosteric activator site"},
    "1V4S_GLC": {"ligand": "GLC", "chain": "A", "site": "the glucose site"},
    "6OIM": {"ligand": "MOV", "chain": "A", "site": "the switch-II pocket (the covalent inhibitor)"},
    "5EHR": {"ligand": "5OD", "chain": "A", "site": "the SHP099 allosteric site"},
}

# The prompt that asks for each site, so that the report can name it.
SITE_PROMPTS = {
    "1T4J": "P01, P07 (the FRJ contacts of 1T4J)",
    "1OPK": "P05 (the MYR contacts of 1OPK)",
    "1V4S": "P06 (the MRK contacts of 1V4S)",
    "1V4S_GLC": "P06 (the GLC contacts of 1V4S)",
    "6OIM": "P02 (the MOV contacts of 6OIM)",
    "5EHR": "P03 (the 5OD contacts of 5EHR)",
}


def strip_hetatm(text: str) -> str:
    return "".join(
        line for line in text.splitlines(keepends=True)
        if not (line.startswith("HETATM") or line.startswith("HET "))
    )


def site_residues(pdb_id: str, ligand: str, chain: str) -> list[int]:
    """The residues within 4 A of the ligand, in PDB numbering."""
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    result = get_ligand_contacts(pdb_id=pdb_id, ligand_id=ligand, chain=chain)
    if not result.get("success"):
        raise RuntimeError(
            f"the contacts for {pdb_id}/{ligand} failed: {result.get('error')}")
    contacts = result["data"]["contacts"]
    return sorted({int(c["pdb_number"]) for c in contacts if c.get("pdb_number")})


def pocket_summary(pockets: list[dict], residues: list[int], rank_key: str) -> dict:
    """The pocket summaries, with both selection rules."""
    site = set(residues)
    rows = []
    for pocket in pockets:
        pocket_residues = {
            int(r["residue_number"]) for r in pocket.get("residues", [])
            if r.get("residue_number") is not None
        }
        rows.append({
            "rank": pocket.get(rank_key),
            "score": pocket.get("score"),
            "n_residues": len(pocket_residues),
            "site_residues_in_pocket": len(pocket_residues & site),
            "site_residue_numbers": sorted(pocket_residues & site),
        })
    rows.sort(key=lambda row: (row["rank"] is None, row["rank"]))

    first = next((row for row in rows if row["site_residues_in_pocket"] > 0), None)
    best = None
    for row in rows:
        if row["site_residues_in_pocket"] > 0:
            if (best is None
                    or row["site_residues_in_pocket"] > best["site_residues_in_pocket"]):
                best = row
    top = rows[:3]
    return {
        "pockets": rows,
        "rank_of_the_pocket_covering_the_site": best["rank"] if best else None,
        "overlap_of_the_covering_pocket": best["site_residues_in_pocket"] if best else 0,
        "covering_pocket": best,
        "committed_selection_rank": first["rank"] if first else None,
        "committed_selection_overlap": (
            first["site_residues_in_pocket"] if first else 0),
        "top3_overlap": [row["site_residues_in_pocket"] for row in top],
        "top3_ranks": [row["rank"] for row in top],
    }


def main() -> int:
    out_path = Path(sys.argv[1])
    wanted = set(sys.argv[2:]) or None
    results: dict = {
        "what_this_file_is": (
            "the pocket-detector reference outputs measured with the "
            "corrected selection (the pocket with the MOST site residues); "
            "the committed benchmark/pocket_reference_outputs.json is kept "
            "unchanged"
        ),
        "generated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "structures": {},
        "sites": {},
    }
    work = Path(tempfile.mkdtemp(prefix="pocket_ref_v2_"))

    for key, spec in SITES.items():
        if wanted and key not in wanted:
            continue
        pdb_id = key.split("_")[0]
        stripped = work / f"{pdb_id}.pdb"
        if not stripped.is_file():
            urllib.request.urlretrieve(
                f"https://files.rcsb.org/download/{pdb_id}.pdb", stripped)
            text = stripped.read_text(encoding="utf-8", errors="replace")
            stripped.write_text(strip_hetatm(text), encoding="utf-8")
        try:
            residues = site_residues(pdb_id, spec["ligand"], spec["chain"])
        except Exception as error:  # noqa: BLE001
            print(f"  {key}: the contacts failed: {error}", flush=True)
            residues = []
        results["sites"][key] = {
            "pdb_id": pdb_id,
            "ligand": spec["ligand"],
            "chain": spec["chain"],
            "site": spec["site"],
            "prompts": SITE_PROMPTS.get(key),
            "site_residues_pdb": residues,
            "n_site_residues": len(residues),
        }
        print(f"  {key}: the site has {len(residues)} residues", flush=True)

    for pdb_id in sorted({key.split("_")[0] for key in results["sites"]}):
        stripped = work / f"{pdb_id}.pdb"
        entry: dict = {"pdb_id": pdb_id}
        fpocket = detect_pockets_fpocket(str(stripped))
        if fpocket.get("success"):
            entry["fpocket"] = fpocket["data"]["pockets"]
        else:
            entry["fpocket_error"] = fpocket.get("error")
        p2rank = detect_pockets_p2rank(str(stripped))
        if p2rank.get("success"):
            entry["p2rank"] = p2rank["data"]["pockets"]
        else:
            entry["p2rank_error"] = p2rank.get("error")
        results["structures"][pdb_id] = entry
        print(f"  {pdb_id}: fpocket {len(entry.get('fpocket') or [])} pockets, "
              f"p2rank {len(entry.get('p2rank') or [])} pockets", flush=True)

    for key in list(results["sites"]):
        pdb_id = results["sites"][key]["pdb_id"]
        entry = results["structures"].get(pdb_id, {})
        residues = results["sites"][key]["site_residues_pdb"]
        for method, rank_key in (("fpocket", "pocket_number"), ("p2rank", "rank")):
            pockets = entry.get(method) or []
            if not pockets:
                continue
            results["sites"][key][method] = pocket_summary(pockets, residues, rank_key)
            summary = results["sites"][key][method]
            print(
                f"  {key} / {method}: corrected rank="
                f"{summary['rank_of_the_pocket_covering_the_site']} overlap="
                f"{summary['overlap_of_the_covering_pocket']} | committed "
                f"selection rank={summary['committed_selection_rank']} overlap="
                f"{summary['committed_selection_overlap']}",
                flush=True,
            )

    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

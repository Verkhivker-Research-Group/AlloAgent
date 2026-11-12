"""The reference outputs of the pocket detectors, for the
method-conditional checklist items.

For every structure and every site the method-conditional prompts name,
this runs the two detectors through the wrappers the agent uses and
records, per method:

* the pockets in rank order, with the score and the number of site
  residues in each pocket;
* the rank of the pocket that covers the site (the pocket with the
  most site residues), and the overlap of the top three (or top five)
  pockets with the site.

The site residues come from the coordinates (the ligand contacts in
the deposited structure), so the numbers are the ones an agent that
used the same tool on the same structure would get.

    python benchmark/pocket_reference_outputs.py <out.json>
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, "/workspace")

from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket
from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

# The structures and the ligand whose contacts define the site.
SITES = {
    "1T4J": {"ligand": "FRJ", "chain": "A", "site": "the FRJ allosteric site"},
    "1OPK": {"ligand": "MYR", "chain": "A", "site": "the myristoyl site"},
    "1V4S": {"ligand": "MRK", "chain": "A", "site": "the allosteric activator site"},
    "1V4S_GLC": {"ligand": "GLC", "chain": "A", "site": "the glucose site"},
    "6OIM": {"ligand": "MOV", "chain": "A", "site": "the switch-II pocket (the covalent inhibitor)"},
    "5EHR": {"ligand": "5OD", "chain": "A", "site": "the SHP099 allosteric site"},
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
        raise RuntimeError(f"the contacts for {pdb_id}/{ligand} failed: {result.get('error')}")
    contacts = result["data"]["contacts"]
    numbers = sorted({int(c["pdb_number"]) for c in contacts if c.get("pdb_number")})
    return numbers


def pocket_summary(pockets: list[dict], residues: list[int], rank_key: str) -> dict:
    site = set(residues)
    rows = []
    for pocket in pockets:
        pocket_residues = {
            int(r["residue_number"]) for r in pocket.get("residues", [])
            if r.get("residue_number") is not None
        }
        rows.append(
            {
                "rank": pocket.get(rank_key),
                "score": pocket.get("score"),
                "n_residues": len(pocket_residues),
                "site_residues_in_pocket": len(pocket_residues & site),
            }
        )
    rows.sort(key=lambda row: (row["rank"] is None, row["rank"]))
    best = None
    for row in rows:
        if row["site_residues_in_pocket"] > 0:
            best = row
            break
    top = rows[:3]
    return {
        "pockets": rows,
        "rank_of_the_pocket_covering_the_site": best["rank"] if best else None,
        "overlap_of_the_covering_pocket": best["site_residues_in_pocket"] if best else 0,
        "top3_overlap": [row["site_residues_in_pocket"] for row in top],
        "top3_ranks": [row["rank"] for row in top],
    }


def main() -> int:
    out_path = Path(sys.argv[1])
    results: dict = {"structures": {}, "sites": {}}
    work = Path(tempfile.mkdtemp(prefix="pocket_ref_"))

    for key, spec in SITES.items():
        pdb_id = key.split("_")[0]
        stripped = work / f"{pdb_id}.pdb"
        if not stripped.is_file():
            urllib.request.urlretrieve(
                f"https://files.rcsb.org/download/{pdb_id}.pdb", stripped
            )
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
            "site_residues_pdb": residues,
            "n_site_residues": len(residues),
        }
        print(f"  {key}: the site has {len(residues)} residues", flush=True)

    for pdb_id in sorted({key.split("_")[0] for key in SITES}):
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
        print(f"  {pdb_id}: fpocket {len(entry.get('fpocket', []))} pockets, "
              f"p2rank {len(entry.get('p2rank', []))} pockets", flush=True)

    for key, spec in SITES.items():
        pdb_id = key.split("_")[0]
        entry = results["structures"].get(pdb_id, {})
        residues = results["sites"][key]["site_residues_pdb"]
        for method, rank_key in (("fpocket", "pocket_number"), ("p2rank", "rank")):
            pockets = entry.get(method) or []
            if not pockets:
                continue
            results["sites"][key][method] = pocket_summary(pockets, residues, rank_key)
            print(f"  {key} / {method}: {results['sites'][key][method]}", flush=True)

    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

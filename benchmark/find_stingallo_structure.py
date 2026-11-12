"""Find a structure for which STINGAllo returns residues, and cache the
responses.

The order is fixed: 1V4S chain A (glucokinase, ligand MRK), then 3O96
chain A (AKT1, ligand IQO), then 1PZO chain A (TEM-1, ligands CBT).
The first structure whose prediction is NOT empty is used, and the
choice is made by the service's output alone.

Each structure is called ONCE and the response is cached in
benchmark/stingallo_cache.json, so the service's daily quota is not
spent twice on the same call.

    python benchmark/find_stingallo_structure.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace")

CACHE = Path("/workspace/benchmark/stingallo_cache.json")
CANDIDATES = [
    ("1V4S", "A", "MRK", "human glucokinase", "P35557"),
    ("3O96", "A", "IQO", "human AKT1", "P31749"),
    ("1PZO", "A", "CBT", "TEM-1 beta-lactamase", "P62593"),
]


def main() -> int:
    from biomni.tool.get_stingallo_allosteric_residues import (
        get_stingallo_allosteric_residues,
    )

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.is_file() else {}
    used_today = sorted(cache)
    print(f"the structures already called today ({len(used_today)}): {used_today}")

    chosen = None
    for pdb_id, chain, ligand, protein, accession in CANDIDATES:
        key = f"{pdb_id}:{chain}"
        if key in cache:
            record = cache[key]
            print(f"  {key}: the cached response is used ({record.get('response_date')})")
        else:
            result = get_stingallo_allosteric_residues(pdb_id, chain)
            if not result.get("success"):
                print(f"  {key}: the call FAILED: {result.get('error')}")
                continue
            data = result.get("data") or {}
            record = {
                "url": (f"https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs"
                        f"?pdb_id={pdb_id}&chain_id={chain}"),
                "response_date": result.get("query_time_utc"),
                "payload": {"allosteric_residues": data.get("residues", []),
                            "chain_id": data.get("chain_id"),
                            "pdb_id": data.get("pdb_id")},
            }
            cache[key] = record
            CACHE.write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")
            print(f"  {key}: called once and cached ({record['response_date']})")
        residues = (record.get("payload") or {}).get("allosteric_residues") or []
        print(f"     the prediction: {len(residues)} residues {residues[:8]}")
        if residues and chosen is None:
            chosen = (pdb_id, chain, ligand, protein, accession, residues)

    print()
    print(f"the distinct structures called today: {len(cache)} -> {sorted(cache)}")
    if chosen is None:
        print("no candidate returned a non-empty prediction")
        return 2
    pdb_id, chain, ligand, protein, accession, residues = chosen
    prompt = (
        f"For {protein} in PDB entry {pdb_id} chain {chain}, compare the residues "
        f"STINGAllo predicts with those within 4 angstroms of the bound allosteric "
        f"ligand {ligand}. Report both lists, the overlap, and how that overlap "
        f"compares with what would be expected by chance."
    )
    print(f"the chosen structure: {pdb_id} {chain} ({protein}, {accession}), "
          f"the ligand {ligand}, {len(residues)} predicted residues")
    print(f"the new K04 prompt: {prompt}")
    Path("/workspace/benchmark/k04_choice.json").write_text(
        json.dumps({"pdb_id": pdb_id, "chain_id": chain, "ligand": ligand,
                    "protein": protein, "accession": accession,
                    "residues": residues, "prompt": prompt,
                    "structures_called_today": sorted(cache)}, indent=2) + "\n",
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

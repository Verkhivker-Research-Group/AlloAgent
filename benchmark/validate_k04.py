"""K04 - the validation from the primary sources.

* the STINGAllo prediction for 1OPK chain A: ONE service call, and the
  response is cached to benchmark/stingallo_1OPK_A.json with the date
  (the service has a daily quota);
* the MYR contact list: from the raw coordinates (the deposited mmCIF)
  and the SIFTS numbering;
* the overlap of the two;
* the chance expectation: the number of modelled residues in the
  chain, the number of predicted residues and the number of contacts,
  compared with the hypergeometric expectation for a random set of the
  same size.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from math import comb
from pathlib import Path

sys.path.insert(0, "/workspace")

CACHE = Path("/workspace/benchmark/stingallo_1OPK_A.json")
PDB_ID = "1OPK"
CHAIN = "A"
LIGAND = "MYR"


def main() -> int:
    out: dict = {"pdb_id": PDB_ID, "chain_id": CHAIN, "ligand": LIGAND}

    # 1. the STINGAllo call: once, cached
    if CACHE.is_file():
        out["stingallo"] = json.loads(CACHE.read_text(encoding="utf-8"))
        out["stingallo"]["source"] = "the cached response (one call, within the daily quota)"
    else:
        from biomni.tool.get_stingallo_allosteric_residues import (
            get_stingallo_allosteric_residues,
        )

        result = get_stingallo_allosteric_residues(PDB_ID, CHAIN)
        print("the STINGAllo response:", json.dumps(result)[:400], flush=True)
        if not result.get("success"):
            print("the STINGAllo call FAILED:", result.get("error"))
            return 2
        out["stingallo"] = {
            "data": result.get("data"),
            "query_time_utc": result.get("query_time_utc"),
            "source": result.get("source"),
            "source_version": result.get("source_version"),
        }
        CACHE.write_text(json.dumps(out["stingallo"], indent=2) + "\n", encoding="utf-8")
        print(f"cached the response in {CACHE}", flush=True)

    predicted = out["stingallo"].get("data", {}).get("allosteric_residues")
    if predicted is None:
        data = out["stingallo"].get("data") or {}
        predicted = data.get("residues") or data.get("allosteric_residue") or []
    out["predicted_residues"] = sorted(int(value) for value in predicted)
    print("the predicted residues:", out["predicted_residues"], flush=True)

    # 2. the MYR contacts from the raw coordinates
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    contacts = get_ligand_contacts(pdb_id=PDB_ID, ligand_id=LIGAND, chain=CHAIN)
    if not contacts.get("success"):
        print("the contacts failed:", contacts.get("error"))
        return 3
    rows = contacts["data"]["contacts"]
    pdb_numbers = sorted({int(row["pdb_number"]) for row in rows})
    uniprot_numbers = sorted({int(row["uniprot_number"]) for row in rows if row.get("uniprot_number")})
    out["myr_contacts"] = {
        "count": len(rows),
        "pdb_residues": pdb_numbers,
        "uniprot_residues": uniprot_numbers,
        "min_distances": {str(row["pdb_number"]): row.get("min_distance") for row in rows},
        "uniprot_accession": contacts["data"].get("uniprot_accession"),
        "source": contacts["data"].get("source"),
    }
    print(f"the MYR contacts: {len(rows)} residues, UniProt "
          f"{out['myr_contacts']['uniprot_accession']} {uniprot_numbers}", flush=True)

    # 3. the modelled residue count of the chain (for the chance expectation)
    cif_path = Path(f"/tmp/{PDB_ID}.cif")
    urllib.request.urlretrieve(
        f"https://files.rcsb.org/download/{PDB_ID}.cif", cif_path
    )
    import gemmi

    structure = gemmi.read_structure(str(cif_path))
    structure.setup_entities()
    modelled = 0
    for model in structure:
        for chain in model:
            if chain.name != CHAIN:
                continue
            for residue in chain:
                if residue.name in {
                    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS",
                    "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP",
                    "TYR", "VAL",
                }:
                    modelled += 1
    out["modelled_residues_in_chain"] = modelled
    print(f"the modelled residues in chain {CHAIN}: {modelled}", flush=True)

    # 4. the overlap and the chance expectation
    predicted_set = set(out["predicted_residues"])
    contact_set = set(uniprot_numbers)
    overlap = sorted(predicted_set & contact_set)
    out["overlap"] = {
        "residues": overlap,
        "count": len(overlap),
        "n_predicted": len(predicted_set),
        "n_contacts": len(contact_set),
    }
    n = modelled
    k = len(contact_set)
    m = len(predicted_set)
    if 0 < k <= n and 0 < m <= n:
        expected = m * k / n
        probability = sum(
            comb(k, i) * comb(n - k, m - i) / comb(n, m)
            for i in range(max(0, m - (n - k)), min(k, m) + 1)
        )
        out["chance"] = {
            "expected_overlap": round(expected, 3),
            "p_overlap_at_least_this": round(probability, 6),
            "formula": "the hypergeometric expectation for a random set of the same size",
        }
        print(f"the overlap: {len(overlap)} {overlap}; by chance "
              f"{expected:.2f} (P >= {len(overlap)} = {probability:.4f})", flush=True)

    Path("/workspace/benchmark/validation_k04.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote /workspace/benchmark/validation_k04.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

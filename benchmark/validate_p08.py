"""P08 - the validation from the primary sources.

* the PocketMiner run on 2SHP chain A (one run, per chain);
* the SHP099 contact residues in 5EHR chain A (4 A) from the raw
  coordinates, with the SIFTS numbering;
* the mapping of the 5EHR contacts onto 2SHP through the UniProt
  numbering (both are Q06124, so the UniProt numbering is the
  correspondence);
* the ten highest-scoring residues of 2SHP chain A, with their
  per-chain scores;
* the rank comparison, and the caveat.
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, "/workspace")

OUT = Path("/workspace/benchmark/validation_p08.json")


def main() -> int:
    from biomni.tool.get_ligand_contacts import get_ligand_contacts
    from biomni.tool.pocketminer import pocketminer_score

    out: dict = {"pdb_id_pocketminer": "2SHP", "chain": "A",
                 "pdb_id_contacts": "5EHR", "ligand": "5OD"}

    # 1. the SHP099 contacts in 5EHR chain A
    contacts = get_ligand_contacts(pdb_id="5EHR", ligand_id="5OD", chain="A")
    if not contacts.get("success"):
        print("the contacts failed:", contacts.get("error"))
        return 3
    rows = contacts["data"]["contacts"]
    uniprot_numbers = sorted({int(row["uniprot_number"]) for row in rows if row.get("uniprot_number")})
    pdb_numbers = sorted({int(row["pdb_number"]) for row in rows})
    out["sphp099_contacts_5EHR"] = {
        "count": len(rows),
        "pdb_residues": pdb_numbers,
        "uniprot_residues": uniprot_numbers,
        "uniprot_accession": contacts["data"].get("uniprot_accession"),
        "min_distances": {str(row["pdb_number"]): row.get("min_distance") for row in rows},
    }
    print(f"the 5EHR SHP099 contacts: {len(rows)} residues, UniProt "
          f"{out['sphp099_contacts_5EHR']['uniprot_accession']} {uniprot_numbers}", flush=True)

    # 2. the PocketMiner run on 2SHP chain A
    work = Path(tempfile.mkdtemp(prefix="p08_"))
    pdb = work / "2SHP.pdb"
    urllib.request.urlretrieve("https://files.rcsb.org/download/2SHP.pdb", pdb)
    result = pocketminer_score(str(pdb))
    if not result.get("success"):
        print("PocketMiner failed:", result.get("error"))
        return 4
    data = result["data"]
    residues = data.get("residues") or []
    chain_a = [row for row in residues if row["chain"] == "A"]
    out["pocketminer_2SHP"] = {
        "n_scored_residues": data.get("n_residues"),
        "chains": {name: {"n_residues": block["n_residues"], "mean": block["mean"]}
                   for name, block in (data.get("chains") or {}).items()},
        "all_residue_mean": data.get("all_residue_mean"),
    }
    print(f"PocketMiner on 2SHP: {data.get('n_residues')} residues, the chains "
          f"{out['pocketminer_2SHP']['chains']}", flush=True)

    # the top ten of chain A, with the chain and the score
    scored = [(row["chain"], row["residue_number"], row["residue_name"], row["score"])
              for row in chain_a if row.get("residue_number") is not None]
    scored.sort(key=lambda item: -item[3])
    top10 = [
        {"chain": chain, "pdb_number": number, "residue_name": name, "score": score}
        for chain, number, name, score in scored[:10]
    ]
    out["pocketminer_top10_chain_A"] = top10
    print("the top ten of chain A:", [(r["pdb_number"], round(r["score"], 4)) for r in top10],
          flush=True)

    # 3. the mapping: the 5EHR contact residues (UniProt) onto 2SHP
    #    (the same UniProt accession), with their PocketMiner scores
    import gemmi

    structure = gemmi.read_structure(str(pdb))
    structure.setup_entities()
    uni_number_of = {}
    for model in structure:
        for chain in model:
            for residue in chain:
                for label in residue.get_mmcif_entity_poly_seq_scheme() or []:
                    pass
    # the SIFTS-style mapping from the mmCIF: the UNP record of the entity
    cif = work / "2SHP.cif"
    urllib.request.urlretrieve("https://files.rcsb.org/download/2SHP.cif", cif)
    import gemmi

    doc = gemmi.cif.read(str(cif))
    block = doc.sole_block()
    alignment = []
    for row in block.find("_struct_ref.", ["id", "db_name", "pdbx_db_accession"]):
        if row.str(1) == "UNP":
            alignment.append((row.str(0), row.str(2)))
    offset = 0
    for row in block.find("_struct_ref_seq.", ["align_id", "seq_align_beg", "seq_align_end", "pdbx_strand_id", "pdbx_PDB_id_code"]):
        if row.str(0) == alignment[0][0] if alignment else False:
            offset = int(row.str(1)) - int(row.str(2))
            strand = row.str(4)
            break
    out["sifts_offset_2SHP"] = offset
    print("the 2SHP SIFTS offset (UniProt - PDB):", offset, flush=True)

    scored_by_number = {number: score for _chain, number, _name, score in scored}
    mapped = []
    for number in uniprot_numbers:
        pdb_number = number - offset
        score = scored_by_number.get(pdb_number)
        mapped.append(
            {
                "uniprot_number": number,
                "pdb_number_2SHP": pdb_number,
                "pocketminer_score": score,
                "in_the_top10": any(
                    item["pdb_number"] == pdb_number for item in top10
                ),
            }
        )
    out["sphp099_site_on_2SHP"] = mapped
    ranks = {item["pdb_number"]: index + 1 for index, item in enumerate(scored)}
    for item in mapped:
        item["pocketminer_rank_in_chain_A"] = ranks.get(item["pdb_number_2SHP"])
    print("the mapped SHP099 site residues on 2SHP:", flush=True)
    for item in mapped:
        print(f"   UniProt {item['uniprot_number']} -> 2SHP {item['pdb_number_2SHP']}: "
              f"score {item['pocketminer_score']} rank {item['pocketminer_rank_in_chain_A']}",
              flush=True)
    within_top10 = sum(1 for item in mapped if item["in_the_top10"])
    out["rank_comparison"] = {
        "n_site_residues": len(mapped),
        "n_in_the_top10": within_top10,
        "best_rank": min((item["pocketminer_rank_in_chain_A"] for item in mapped
                          if item["pocketminer_rank_in_chain_A"]), default=None),
        "median_rank": sorted(
            item["pocketminer_rank_in_chain_A"] for item in mapped
            if item["pocketminer_rank_in_chain_A"]
        )[len(mapped) // 2] if mapped else None,
    }
    print("the rank comparison:", out["rank_comparison"], flush=True)

    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

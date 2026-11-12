"""Build benchmark/restricted_prompt_set.json from the benchmark draft
and the capability classification.

The classification is a CAPABILITY judgement: can arm D answer the
prompt with no outbound access other than the LLM endpoint, using the
local data lake, the local models and the local structure cache?  It
never looks at a result.

The binary field is "as the tools stand today": a prompt that needs
the UniProt-PDB mapping is a "no" today, because the mapping is
fetched from the RCSB Data API, and the field says what would make it
a "yes".
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DRAFT = REPO / "benchmark" / "benchmark_draft.json"
OUT = REPO / "benchmark" / "restricted_prompt_set.json"

# id -> (yes/no, the reason, the tools, the data, what would make a "no" a "yes")
YES = {
    "S02": ("the ligand identities and the 4 A contacts come from the cached structure; no UniProt numbering is asked for",
            "get_ligand_contacts; load_pdb", "the structure cache (1OPK)", ""),
    "S03": ("the activator, the glucose, the contacts and the ligand-ligand distance all come from the cached structure",
            "get_ligand_contacts; load_pdb", "the structure cache (1V4S)", ""),
    "S06": ("the two inhibitor copies, their contacts and the pocket comparison come from the cached structure",
            "get_ligand_contacts; load_pdb; detect_pockets_fpocket", "the structure cache (1PZO)", ""),
    "P01": ("the pockets and the FRJ contact residues come from the cached, ligand-stripped structure; the overlap is computed in PDB numbering",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_ligand_contacts", "the structure cache (1T4J)", ""),
    "P02": ("the pockets and the inhibitor contacts come from the cached structure; the rank of the switch-II pocket needs no mapping",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_ligand_contacts", "the structure cache (6OIM)", ""),
    "P05": ("the pockets and the myristoyl-site contacts come from the cached structure",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_ligand_contacts", "the structure cache (1OPK)", ""),
    "P06": ("the pockets and the two site contact sets come from the cached structure",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_ligand_contacts", "the structure cache (1V4S)", ""),
    "P07": ("all three detectors are local and the FRJ residues come from the cached structure",
            "detect_pockets_fpocket; detect_pockets_p2rank; pocketminer_score; get_ligand_contacts",
            "the structure cache (1T4J); the local PocketMiner weights", ""),
    "C02": ("the contact network, the closest residue to the ligand and the path to Cys215 are all local; Cys215 is PDB numbering",
            "residue_contact_network; get_ligand_contacts", "the structure cache (1T4J)", ""),
    "C04": ("the network and the two contact residues come from the cached structure",
            "residue_contact_network; get_ligand_contacts", "the structure cache (1V4S)", ""),
    "C05": ("the network, the communities and the domain names are all local (networkx is in the image)",
            "residue_contact_network", "the structure cache (1AKE)", ""),
    "L02": ("the ChEMBL 37 records, the counts, the median and the best value are in the local ChEMBL release",
            "get_chembl_bioactivity", "the local ChEMBL 37 (/data/chembl)", ""),
    "L03": ("the ChEMBL part is local and the two entries to cite are in the structure cache",
            "get_chembl_bioactivity; load_pdb", "the local ChEMBL 37; the structure cache (5MO4)", ""),
    "H01": ("the question is whether ChEMBL holds a record, and the local ChEMBL 37 answers that (the answer is an explicit absence)",
            "get_chembl_bioactivity", "the local ChEMBL 37 (/data/chembl)", ""),
    "H02": ("the pocket ranking and the limits come from the local detectors and the cached structure",
            "detect_pockets_fpocket; detect_pockets_p2rank", "the structure cache (1T4J)", ""),
}

# K04 and P08 replaced L01 and L05 in the draft on 2026-10-26.
NO_ADDED = {
    "K04": ("the STINGAllo prediction IS a live service with no local copy; the FRJ contacts and the chance expectation are local",
            "get_stingallo_allosteric_residues; get_ligand_contacts",
            "the structure cache (1T4J); www.stingallo.cbi.cnptia.embrapa.br (live)",
            "a local STINGAllo snapshot"),
    "P08": ("PocketMiner and the 5EHR contacts are local but the inter-entry mapping is live",
            "pocketminer_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the structure cache (2SHP, 5EHR); the local PocketMiner weights; the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
}

NO = {
    **NO_ADDED,
    "S01": ("the contacts are local but the answer must be in UniProt numbering, and the mapping is fetched from the RCSB Data API",
            "get_ligand_contacts; map_residues_uniprot_pdb", "the structure cache (1T4J); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF (the struct_ref records carry it)"),
    "S04": ("the contacts are local but the AKT1 domain boundaries are UniProt features, fetched live",
            "get_ligand_contacts; map_residues_uniprot_pdb", "the structure cache (3O96); the UniProt REST API (live)",
            "a local UniProt feature snapshot"),
    "S05": ("the contacts are local but the domain boundaries are UniProt features, fetched live",
            "get_ligand_contacts; map_residues_uniprot_pdb", "the structure cache (5EHR); the UniProt REST API (live)",
            "a local UniProt feature snapshot"),
    "S07": ("the contacts are local but the numbering relation to P00519 is the live SIFTS mapping",
            "get_ligand_contacts; map_residues_uniprot_pdb", "the structure cache (5MO4); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "P03": ("the pockets and the contacts are local but the inter-entry mapping is live",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_ligand_contacts; map_residues_uniprot_pdb",
            "the structure cache (2SHP, 5EHR); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "P04": ("PocketMiner is local but the 1BTL to 1PZO mapping is live",
            "pocketminer_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the structure cache (1BTL, 1PZO); the local PocketMiner weights; the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "C01": ("the normal-mode analysis is local but the UniProt numbering of the residues is live",
            "normal_mode_analysis; map_residues_uniprot_pdb", "the structure cache (1T4J); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "C03": ("the normal-mode analysis is local but the 2SHP to 5EHR mapping is live",
            "normal_mode_analysis; get_ligand_contacts; map_residues_uniprot_pdb",
            "the structure cache (2SHP, 5EHR); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "C06": ("the normal modes and the network are local but STINGAllo is a live service with no local copy",
            "normal_mode_analysis; residue_contact_network; get_stingallo_allosteric_residues",
            "the structure cache (1T4J); www.stingallo.cbi.cnptia.embrapa.br (live)", "a local STINGAllo snapshot"),
    "V01": ("ClinVar and AlphaMissense are local but the variant positions are UniProt numbering and must be mapped",
            "get_clinvar_variants; get_alphamissense_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the local ClinVar and AlphaMissense releases; the structure cache (5EHR, 2SHP); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "V02": ("as V01, for AKT1", "get_clinvar_variants; get_alphamissense_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the local ClinVar and AlphaMissense releases; the structure cache (3O96); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "V03": ("as V01, for KRAS", "get_clinvar_variants; get_alphamissense_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the local ClinVar and AlphaMissense releases; the structure cache (6OIM); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "V04": ("as V01, for ABL1", "get_clinvar_variants; get_alphamissense_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the local ClinVar and AlphaMissense releases; the structure cache (1OPK); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "V05": ("as V01, for glucokinase", "get_clinvar_variants; get_alphamissense_score; get_ligand_contacts; map_residues_uniprot_pdb",
            "the local ClinVar and AlphaMissense releases; the structure cache (1V4S); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "V06": ("PocketMiner is local but the UniProt variant list is a live service",
            "pocketminer_score; get_uniprot_variants; get_ligand_contacts; map_residues_uniprot_pdb",
            "the structure cache (1BTL, 1PZO); the local PocketMiner weights; the UniProt REST API (live)",
            "a local UniProt variant snapshot"),
    "L04": ("the entry list is a live search; the ChEMBL part is local", "search_pdb_by_uniprot_and_ligand; get_chembl_bioactivity",
            "the RCSB and PDBe search APIs (live); the local ChEMBL 37", "a local PDB search index"),
    "K01": ("the prediction IS the STINGAllo service", "get_stingallo_allosteric_residues",
            "www.stingallo.cbi.cnptia.embrapa.br (live)", "a local STINGAllo snapshot"),
    "K02": ("the contacts are local but the prediction is the live STINGAllo service",
            "get_stingallo_allosteric_residues; get_ligand_contacts",
            "the structure cache (1T4J); www.stingallo.cbi.cnptia.embrapa.br (live)", "a local STINGAllo snapshot"),
    "K03": ("the contacts are local but the prediction is the live STINGAllo service",
            "get_stingallo_allosteric_residues; get_ligand_contacts",
            "the structure cache (5EHR); www.stingallo.cbi.cnptia.embrapa.br (live)", "a local STINGAllo snapshot"),
    "G01": ("the pockets, the ChEMBL part and the coordinates are local but the variant mapping is live",
            "detect_pockets_fpocket; detect_pockets_p2rank; get_chembl_bioactivity; get_clinvar_variants; get_alphamissense_score; get_ligand_contacts",
            "the local ChEMBL, ClinVar and AlphaMissense releases; the structure cache (6OIM); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "G02": ("as G01, for ABL1", "detect_pockets_fpocket; detect_pockets_p2rank; get_chembl_bioactivity; get_clinvar_variants; get_alphamissense_score; get_ligand_contacts",
            "the local ChEMBL, ClinVar and AlphaMissense releases; the structure cache (1OPK); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "G03": ("as G01, for SHP2", "detect_pockets_fpocket; detect_pockets_p2rank; get_clinvar_variants; get_alphamissense_score; normal_mode_analysis; get_ligand_contacts",
            "the local ClinVar and AlphaMissense releases; the structure cache (2SHP, 5EHR); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
    "G04": ("as G01, for AKT1", "get_chembl_bioactivity; get_clinvar_variants; get_alphamissense_score; get_ligand_contacts",
            "the local ChEMBL, ClinVar and AlphaMissense releases; the structure cache (3O96); the RCSB SIFTS API (live)",
            "serving the UniProt alignment from the cached mmCIF"),
}


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    draft_sha = hashlib.sha256(DRAFT.read_bytes()).hexdigest()
    rows = []
    for prompt in draft:
        pid = prompt["id"]
        if pid in YES:
            reason, tools, data, conditional = YES[pid]
            solvable = "yes"
        elif pid in NO:
            reason, tools, data, conditional = NO[pid]
            solvable = "no"
        else:
            raise SystemExit(f"the prompt {pid} is not classified")
        rows.append(
            {
                "id": pid,
                "category": prompt["category"],
                "tier": prompt["tier"],
                "accession": prompt["accession"],
                "prompt": prompt["prompt"],
                "solvable_from_local_resources_alone": solvable,
                "reason": reason,
                "tools": tools,
                "data": data,
                "would_become_yes_if": conditional,
            }
        )
    the_set = [row["id"] for row in rows if row["solvable_from_local_resources_alone"] == "yes"]
    payload = {
        "generated": "2026-10-26",
        "source": "benchmark/benchmark_draft.json",
        "source_sha256": draft_sha,
        "rule": (
            "A prompt is 'yes' when arm D can answer it with no outbound access "
            "other than the LLM endpoint, using the local data lake (/data/chembl, "
            "/data/clinvar, /data/alphamissense, /biolab_data), the local models "
            "(fpocket, P2Rank, PocketMiner, the normal-mode analysis, the contact "
            "network) and the local structure cache (/data/structures, mounted "
            "read-only and identically into both arms).  A prompt is 'no' when it "
            "needs a live service (the RCSB/PDBe entry search, STINGAllo, the "
            "UniProt REST API) or the UniProt-PDB residue mapping, which the tools "
            "fetch from the RCSB Data API today.  The classification is a "
            "capability judgement made before any run; no result was consulted."
        ),
        "counts": {
            "prompts": len(rows),
            "yes": len(the_set),
            "no": len(rows) - len(the_set),
        },
        "the_set": the_set,
        "prompts": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {len(rows)} rows, {len(the_set)} yes, "
          f"{len(rows) - len(the_set)} no")
    print("the set:", ", ".join(the_set))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

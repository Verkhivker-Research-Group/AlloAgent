"""Swap L01 and L05 for K04 and P08 in benchmark/benchmark_draft.json.

The two replaced prompts asked for a live RCSB/PDBe entry search
("which PDB entries contain X bound to ligand Y"), which the validation
could not exercise (the PDBe mappings endpoints answer 404 from the
validation host) and which the restricted-egress scenario cannot run
at all.  The two new prompts are the same kind of work done from the
local data and the local tools:

  K04 - the STINGAllo prediction for 1OPK chain A against the MYR
        contacts, with the chance expectation;
  P08 - PocketMiner on 2SHP chain A against the SHP099 site residues
        of 5EHR, mapped through the UniProt numbering.

Everything else in the draft is kept exactly as it was.

    python benchmark/swap_draft_prompts.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DRAFT = REPO / "benchmark" / "benchmark_draft.json"

K04 = {
    "id": "K04",
    "category": "Allosteric site prediction",
    "tier": 2,
    "accession": "P18031",
    "prompt": (
        "For human protein tyrosine phosphatase 1B in PDB entry 1T4J chain A, "
        "compare the residues STINGAllo predicts with those within 4 angstroms "
        "of the bound allosteric ligand FRJ. Report both lists, the overlap, "
        "and how that overlap compares with what would be expected by chance."
    ),
    "d_tools_expected": "get_stingallo_allosteric_residues; get_ligand_contacts",
    "draft_checklist": (
        "service prediction list (call once, cached, with date); FRJ contact "
        "list from coordinates; overlap; chance expectation computed from the "
        "chain's modelled residue count"
    ),
    "baseline_route": "N",
    "dated_note": (
        "2026-10-28: K04 was first written on 1OPK chain A (the myristate "
        "MYR of ABL1). The STINGAllo service returns an EMPTY prediction for "
        "1OPK chain A - a valid response in the same shape as a non-empty one "
        "(\"allosteric_residues\": []), not an error or a timeout, and the "
        "raw response is kept in benchmark/stingallo_1OPK_A.json. The three "
        "structures tried in order for a non-empty prediction - 1V4S chain A "
        "(glucokinase, MRK), 3O96 chain A (AKT1, IQO) and 1PZO chain A "
        "(TEM-1, CBT) - also return empty lists, each called once and cached "
        "in benchmark/stingallo_cache.json. The service's non-empty coverage "
        "is 1T4J chain A (14 residues) and 5EHR chain A (1 residue), and "
        "5EHR is already the subject of K03, so K04 was moved to 1T4J, where "
        "the prediction is the richest. The choice was made by the service's "
        "output alone."
    ),
}

P08 = {
    "id": "P08",
    "category": "Cryptic pockets",
    "tier": 2,
    "accession": "Q06124",
    "prompt": (
        "Run PocketMiner on the autoinhibited SHP2 structure 2SHP chain A "
        "(UniProt Q06124). Map the residues that contact SHP099 in PDB entry "
        "5EHR onto 2SHP through UniProt numbering and report their "
        "PocketMiner scores next to the scores of the ten highest-scoring "
        "residues. Are the SHP099 site residues among the high scorers?"
    ),
    "d_tools_expected": "PocketMiner wrapper; get_ligand_contacts; map_residues_uniprot_pdb",
    "draft_checklist": (
        "ten top residues with per-chain scores; mapped 5EHR contact residues "
        "(4 A, chain A) with scores; rank comparison; modest-accuracy caveat "
        "stated"
    ),
    "baseline_route": "N",
}


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    out = []
    replaced = []
    for prompt in draft:
        if prompt["id"] == "L01":
            out.append(K04)
            replaced.append("L01 -> K04")
        elif prompt["id"] == "L05":
            out.append(P08)
            replaced.append("L05 -> P08")
        elif prompt["id"] == "K04":
            out.append(K04)
            replaced.append("K04 -> K04 (the 1T4J version)")
        else:
            out.append(prompt)
    assert len(out) == len(draft) == 40, "the prompt count changed"
    ids = [prompt["id"] for prompt in out]
    assert len(set(ids)) == 40, "the prompt ids are not unique"
    assert "K04" in ids and "P08" in ids and "L01" not in ids and "L05" not in ids
    DRAFT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"rewrote {DRAFT}: {', '.join(replaced)}; {len(out)} prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

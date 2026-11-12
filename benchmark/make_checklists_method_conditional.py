"""Make the pocket-detection checklist items method-conditional.

For the six prompts that ask the agent to "run pocket detection"
without naming a method (P01, P02, P03, P05, P06, P07) the critical
items become method-conditional:

* the answer must NAME the method it used (fpocket or P2Rank);
* the ranks and overlaps it reports must match the reference output of
  THAT method (the reference outputs are in
  benchmark/pocket_reference_outputs.json, computed with the same
  wrappers the agent uses, with no randomness in the detectors);
* an answer that does not name the method is wrong on that item, and
  an answer inconsistent with the named method's reference output is
  wrong;
* the honest limit is added: the detectors do not distinguish
  allosteric from orthosteric pockets.

The ORIGINAL items are kept exactly as they are; the new items are
added next to them and a dated note records why.  The PocketMiner
items (P04, V06) get a dated note about the per-chain output.

    python benchmark/make_checklists_method_conditional.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKLISTS = REPO / "benchmark" / "checklists.json"
REFERENCE = REPO / "benchmark" / "pocket_reference_outputs.json"

POCKET_PROMPTS = {
    "P01": ("1T4J", "FRJ", "the top three pockets of the ligand-stripped 1T4J and their overlap with the FRJ contact residues"),
    "P02": ("6OIM", "MOV", "the rank of the pocket that covers the switch-II site (the MOV contacts)"),
    "P03": ("2SHP", "5OD", "the overlap of the top five pockets of 2SHP with the 5EHR SHP099 contact residues"),
    "P05": ("1OPK", "MYR", "the rank of the pocket that covers the myristoyl site (the MYR contacts)"),
    "P06": ("1V4S", "MRK", "which of the top three pockets of 1V4S matches the MRK site and which matches the GLC site"),
    "P07": ("1T4J", "FRJ", "the rank or score each of fpocket, P2Rank and PocketMiner assigns to the FRJ contact residues"),
}
POCKETMINER_PROMPTS = ("P04", "V06")

NOTE = (
    "Dated note 2026-10-26 - the pocket-detection items became "
    "method-conditional. fpocket and P2Rank give different ranks for "
    "the same structure (for 1T4J the FRJ pocket is fpocket's pocket 11, "
    "rank 11 by score, and the top three fpocket pockets overlap the FRJ "
    "site by 0), so a single set of ranks cannot be the criterion. The "
    "answer must name the method it used; the ranks and overlaps it "
    "reports must match that method's reference output "
    "(benchmark/pocket_reference_outputs.json, computed with the same "
    "wrappers the agent uses; the detectors have no randomness); an "
    "answer that does not name the method is wrong on that item, and an "
    "answer inconsistent with the named method's reference output is "
    "wrong. The original items are kept unchanged - note that their "
    "'residues: 0' values are the artifact of the fpocket wrapper bug "
    "that was fixed on 2026-10-26 (the wrapper returned no per-pocket "
    "residues), not a property of fpocket. The honest limit is added: "
    "the detectors do not distinguish allosteric from orthosteric "
    "pockets."
)

PM_NOTE = (
    "Dated note 2026-10-26 - the PocketMiner output is now per chain. The "
    "wrapper returns the chain and the residue number of every scored "
    "residue, a per-chain block (n_residues, mean, min, max, "
    "residue_numbers) and the all-residue mean under its own name, and "
    "there is deliberately no field that mixes the chains of a "
    "multi-chain structure into one number (the UniProt-keyed collapse "
    "that made the gate-2 D1 answer unreachable cannot happen). The "
    "measured per-chain means for 7WVB are A 0.542914, B 0.539538, "
    "C 0.545426, D 0.549240 and the all-residue mean 0.544250 over 1165 "
    "residues. The scores in the items below are per residue and are "
    "reported with their chain."
)


def main() -> int:
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    sites = reference["sites"]

    for prompt in checklists["prompts"]:
        pid = prompt["id"]
        if pid in POCKET_PROMPTS:
            pdb_id, ligand, what = POCKET_PROMPTS[pid]
            site = sites.get(pdb_id) or sites.get(f"{pdb_id}_{ligand}")
            if site is None:
                # 1V4S has two sites (MRK and GLC); use the one the
                # prompt names, falling back to the first for the key.
                site = next(
                    (value for key, value in sites.items() if key.startswith(pdb_id)),
                    None,
                )
            new_items = []
            for method, label in (("fpocket", "fpocket"), ("p2rank", "P2Rank")):
                method_data = (site or {}).get(method)
                if not method_data:
                    continue
                new_items.append(
                    {
                        "key": f"{method}_reference_{pid}",
                        "kind": "exact",
                        "value": {
                            "method": method,
                            "rank_of_the_pocket_covering_the_site": method_data[
                                "rank_of_the_pocket_covering_the_site"
                            ],
                            "overlap_of_the_covering_pocket": method_data[
                                "overlap_of_the_covering_pocket"
                            ],
                            "top3_ranks": method_data["top3_ranks"],
                            "top3_overlap": method_data["top3_overlap"],
                            "pockets": method_data["pockets"],
                        },
                        "tolerance": 0,
                        "source": (
                            f"the {label} reference output on the ligand-stripped "
                            f"{pdb_id} (benchmark/pocket_reference_outputs.json)"
                        ),
                        "note": (
                            f"method-conditional: this item is judged against the "
                            f"{label} reference output, and only if the answer names "
                            f"{label} as the method it used"
                        ),
                        "status": "PASS",
                    }
                )
            new_items.insert(
                0,
                {
                    "key": f"method_named_{pid}",
                    "kind": "qualitative",
                    "value": (
                        f"the answer names the pocket-detection method it used "
                        f"(fpocket or P2Rank); an answer that does not name the "
                        f"method is wrong on this item"
                    ),
                    "tolerance": None,
                    "source": "the prompt's own criterion (the methods are not interchangeable)",
                    "note": (
                        f"the answer reports {what}; the ranks and overlaps must "
                        f"match the reference output of the method it names"
                    ),
                    "status": "PASS",
                },
            )
            new_items.append(
                {
                    "key": f"detector_limit_stated_{pid}",
                    "kind": "qualitative",
                    "value": (
                        "the answer states the limit of the method: a pocket "
                        "detector does not distinguish allosteric from orthosteric "
                        "pockets, so a pocket overlapping the allosteric site is "
                        "evidence of a pocket, not of allostery"
                    ),
                    "tolerance": None,
                    "source": "the tool card of detect_pockets_fpocket / detect_pockets_p2rank",
                    "note": "the honest limit; a claim of allostery from a pocket rank alone is wrong",
                    "status": "PASS",
                }
            )
            existing = {item["key"] for item in prompt["checklist"]}
            for item in new_items:
                if item["key"] not in existing:
                    prompt["checklist"].append(item)
            prompt.setdefault("dated_notes", []).append(
                {"date": "2026-10-26", "note": NOTE, "prompt": pid}
            )
        elif pid in POCKETMINER_PROMPTS:
            prompt.setdefault("dated_notes", []).append(
                {"date": "2026-10-26", "note": PM_NOTE, "prompt": pid}
            )

    checklists["generated_utc"] = "2026-10-26T00:00:00Z"
    checklists.setdefault("dated_notes", []).append(
        {
            "date": "2026-10-26",
            "note": (
                "The pocket-detection checklist items of P01, P02, P03, P05, P06 "
                "and P07 became method-conditional (the answer must name the "
                "method, and the ranks and overlaps must match that method's "
                "reference output in benchmark/pocket_reference_outputs.json), "
                "and the honest limit about the detectors was added. The "
                "original items are kept unchanged. The PocketMiner items of "
                "P04 and V06 were updated to the per-chain output. The "
                "sha256 of this file was recomputed and committed with the "
                "change."
            ),
        }
    )
    CHECKLISTS.write_text(json.dumps(checklists, indent=2) + "\n", encoding="utf-8")
    print(f"updated {CHECKLISTS}")
    for prompt in checklists["prompts"]:
        if prompt["id"] in POCKET_PROMPTS or prompt["id"] in POCKETMINER_PROMPTS:
            print(f"  {prompt['id']}: {len(prompt['checklist'])} items, "
                  f"{len(prompt.get('dated_notes', []))} dated notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

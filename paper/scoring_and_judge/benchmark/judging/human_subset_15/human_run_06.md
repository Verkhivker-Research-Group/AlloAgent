# Human rating sheet: run rp7a738o9t1 (5 of 30)

## Before you start

- You get one file per run with the same fields the judge sees: question,
  intended protein, checklist, and the final answer with arm labels and
  one-sided tool names removed.
- Do not open the key file, the judge outputs, or the run records.
- Score each run on its own. Do not go back and change a score after moving on.
- Aim for about 5 minutes per run. Stop and take a break after 10.

## Rubric (same as the judge)

Goal Completion: full / partial / deferred / null.
Data Grounding: 0 / 1 / 2.
Final Answer Complete: yes / no.
Checklist items: correct / incorrect / missing (skip items marked `scripted`).
For HONEST-REPORTING prompts, a clear and correct statement that the data do
not support a claim is full.

---

=== RUN rp7a738o9t1 ===
QUESTION:
Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P02_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[P02_b] [critical] [scripted] [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}]
[P02_c] [critical] [judged] the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported
[P02_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P02_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 1, "overlap_of_the_covering_pocket": 16, "top3_ranks": [1, 2, 3], "top3_overlap": [16, 0, 0], "pockets": [{"rank": 1, "score": 0.146, "n_residues": 33, "site_residues_in_pocket": 16}, {"rank": 2, "score": -0.007, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 3, "score": -0.021, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 4, "score": -0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": -0.053, "n_residues": 5, "site_residues_in_pocket": 4}, {"rank": 6, "score": -0.059, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 7, "score": -0.07, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 8, "score": -0.089, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 9, "score": -0.09, "n_residues": 7, "site_residues_in_pocket": 3}, {"rank": 10, "score": -0.098, "n_residues": 4, "site_residues_in_pocket": 3}, {"rank": 11, "score": -0.168, "n_residues": 7, "site_residues_in_pocket": 1}]}
[P02_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2], "top3_overlap": [0, 0], "pockets": [{"rank": 1, "score": 12.62, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 5.97, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P02_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The switch-II pocket is rank 1 (Pocket 1) in fpocket.**

After removing all 277 HETATM records from 6OIM—including MOV, GDP, Mg²⁺, and waters—fpocket identified the former covalent-inhibitor cavity as:

- **Pocket rank:** **1**
- **fpocket score:** 0.146
- **Druggability score:** 0.838
- **Overlap with the former MOV site:** 16 of 17 MOV-contacting residues
- Includes the covalent anchor **Cys12** and switch-II residues **Ala59, Gly60, Gln61, Glu62, Glu63, Met72, Tyr96, Gln99, and Val103**
- All 41 former MOV atoms were within 6 Å of Pocket 1’s lining residues.

**Detector-specific note:** P2Rank partitions the elongated switch-II region more finely and assigns the switch-II-specific subpocket **rank 2**; its rank-1 pocket is primarily the nucleotide/P-loop cavity. Thus, for the standard fpocket pocket ranking, the requested answer is **rank 1**.
=== END RUN rp7a738o9t1 ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

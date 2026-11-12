# Human rating sheet: run ru57a6w5y1m (4 of 30)

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

=== RUN ru57a6w5y1m ===
QUESTION:
Remove all ligands from PDB entry 1OPK (ABL1, UniProt P00519) and run pocket detection. What is the rank of the pocket that covers the myristoyl site?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P05_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[P05_b] [critical] [scripted] [{"rank": 1, "residues": 23}, {"rank": 2, "residues": 23}, {"rank": 3, "residues": 17}]
[P05_c] [critical] [judged] the rank of the pocket that covers the myristoyl site (the MYR contacts) is reported
[P05_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P05_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 3, "overlap_of_the_covering_pocket": 8, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 8], "pockets": [{"rank": 1, "score": 0.338, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.32, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.211, "n_residues": 17, "site_residues_in_pocket": 8}, {"rank": 4, "score": 0.121, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.112, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.111, "n_residues": 18, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.097, "n_residues": 32, "site_residues_in_pocket": 0}, {"rank": 8, "score": 0.09, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 9, "score": 0.049, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.044, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.038, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 12, "score": 0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.023, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.022, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.011, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.009, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 17, "score": -0.004, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 18, "score": -0.004, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 19, "score": -0.01, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 20, "score": -0.017, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 21, "score": -0.018, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 22, "score": -0.02, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 23, "score": -0.033, "n_residues": 10, "site_residues_in_pocket": 1}, {"rank": 24, "score": -0.036, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 25, "score": -0.037, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 26, "score": -0.045, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 27, "score": -0.047, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 28, "score": -0.06, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 29, "score": -0.085, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 30, "score": -0.09, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 31, "score": -0.103, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 32, "score": -0.131, "n_residues": 7, "site_residues_in_pocket": 2}, {"rank": 33, "score": -0.137, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 34, "score": -0.158, "n_residues": 17, "site_residues_in_pocket": 0}]}
[P05_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 23.77, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 11.32, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 10.44, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 4, "score": 9.99, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 5, "score": 4.5, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 6, "score": 2.04, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 7, "score": 1.74, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 8, "score": 1.24, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 9, "score": 1.09, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.46, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P05_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The myristoyl-site pocket is rank 3.**

After removing all HETATM records—including MYR (myristic acid), P16, glycerol, and waters—from 1OPK, Fpocket identified 34 pockets. The MYR binding site overlapped **8/8 MYR-contact residues** with **pocket 3**, which had an Fpocket score of **0.211** and druggability score of **0.547**. The result was identical in the explicit ligand-stripped run and the integrated allosteric-site workflow.

Note: the deposited 1OPK entry is mouse ABL1 and maps to **P00520**, rather than human ABL1 **P00519**, but this does not affect the requested pocket ranking.
=== END RUN ru57a6w5y1m ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

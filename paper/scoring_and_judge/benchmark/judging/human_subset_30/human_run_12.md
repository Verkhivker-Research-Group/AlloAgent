# Human rating sheet: run rqadr923q4j (12 of 30)

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

=== RUN rqadr923q4j ===
QUESTION:
Remove all ligands from PDB entry 1T4J (PTP1B, UniProt P18031) and run pocket detection. Does any of the top three pockets overlap the site where the allosteric ligand was bound? Report the overlap as a number of shared residues.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P01_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P01_c] [critical] [judged] the top three fpocket pockets of the ligand-stripped 1T4J contain the residues FRJ contacted, and the overlap is reported as a count
[P01_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P01_e] [critical] [judged] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P01_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P01_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Yes.** The second-ranked AutoSite pocket overlaps the site where the allosteric ligand **FRJ** was bound.

| Pocket | AutoSite score | Shared residues with FRJ site |
|---|---:|---:|
| 1 | 34.852 | 0 |
| 2 | 32.394 | **10** |
| 3 | 29.472 | 0 |

The ten shared residues are:

**Ser187, Pro188, Ala189, Asn193, Phe196, Lys197, Glu200, Gly277, Phe280, and Ile281.**

Method summary:
- Removed all 41 FRJ `HETATM` records from PDB 1T4J while preserving the 2,304 protein `ATOM` records.
- Defined the original FRJ site as residues within 4.5 Å of an FRJ heavy atom.
- Ran AutoSite v1.0.0 at 1.0 Å spacing, identifying 13 clusters.
- Assigned pocket residues using AutoSite’s own `featurePts/bsres` implementation.

Full results are in:

`/agent_cwd/output/1T4J_pocket_analysis/final_report.txt`

AutoSite citation: Ravindranath & Sanner, *Bioinformatics* (2016), DOI: `10.1093/bioinformatics/btw367`.
=== END RUN rqadr923q4j ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

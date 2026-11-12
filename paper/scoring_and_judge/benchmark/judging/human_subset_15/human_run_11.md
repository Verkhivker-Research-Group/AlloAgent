# Human rating sheet: run rxpteh3egym (30 of 30)

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

=== RUN rxpteh3egym ===
QUESTION:
For SHP2 in PDB entry 5EHR chain A, compare the residues STINGAllo predicts with those within 4 angstroms of SHP099. Report both lists and the overlap, and say whether the prediction recovers the tunnel site.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[K03_b] [critical] [scripted] ["314"]
[K03_c] [critical] [scripted] 0
[K03_d] [critical] [scripted] {"predicted_residues": 1, "predicted_residue_numbers": [314], "contact_residues": 15, "modelled_chain_A_residues": 485, "predicted_fraction_of_chain": 0.002061855670103093, "expected_overlap_by_chance": 0.030927835051546393, "observed_overlap": 0, "enrichment": 0.0}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## SHP2–SHP099 comparison for PDB 5EHR, chain A

RCSB identifies **5EHR** as SHP2 in complex with the allosteric inhibitor **SHP099**. In the deposited structure, SHP099 has chemical-component ID **5OD**.

### STINGAllo predictions

**List:** `[]`

The validated STINGAllo query returned no predicted residues for 5EHR chain A. The same empty result was obtained through the integrated allosteric workflow; chain B was also empty.

### SHP099 contacts within 4 Å

| Residue | Minimum distance |
|---|---:|
| A.108 THR | 3.13 Å |
| A.110 GLU | 3.47 Å |
| A.111 ARG | 3.14 Å |
| A.113 PHE | 2.79 Å |
| A.114 HIS | 3.75 Å |
| A.218 THR | 3.69 Å |
| A.219 THR | 3.59 Å |
| A.249 GLU | 3.29 Å |
| A.250 GLU | 3.10 Å |
| A.253 THR | 3.30 Å |
| A.254 LEU | 3.46 Å |
| A.257 GLN | 3.58 Å |
| A.491 PRO | 3.45 Å |
| A.492 LYS | 3.45 Å |
| A.495 GLN | 3.57 Å |

Thus, **15 residues** lie within the inclusive 4 Å cutoff.

### Overlap

**Overlap:** `[]`  
**Overlap count:** **0**

### Conclusion

**No—the STINGAllo result does not recover the SHP099 tunnel site.** There are no STINGAllo-predicted residues to overlap with the 15 ligand-contacting residues that delineate the tunnel.

This is specifically a **no-coverage result**, rather than a case where STINGAllo predicts a different set of residues: the current service response contains **no STINGAllo record/residue prediction for 5EHR**.
=== END RUN rxpteh3egym ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

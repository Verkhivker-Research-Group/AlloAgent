# Human rating sheet: run rzk6i8iir8k (24 of 30)

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

=== RUN rzk6i8iir8k ===
QUESTION:
Trametinib and cobimetinib are allosteric MEK inhibitors. Compare their ChEMBL IC50 records against human MAP2K1 (UniProt Q02750): number of records, median and best value for each.

INTENDED PROTEIN: Dual specificity mitogen-activated protein kinase kinase 1 (Q02750)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L02_a] [critical] [scripted] {"name": "Dual specificity mitogen-activated protein kinase kinase 1", "gene": "MAP2K1", "organism": "Homo sapiens"}
[L02_b] [critical] [scripted] {"count": 16, "median_nM": 2.8499999999999996, "best_nM": 0.48, "units": {"nM": 16}}
[L02_c] [critical] [scripted] {"count": 11, "median_nM": 4.2, "best_nM": 0.2, "units": {"nM": 11}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### ChEMBL IC50 comparison: human MAP2K1

Target: **UniProt Q02750 / ChEMBL target CHEMBL3587**  
Measurements: **standard_type = IC50**; all returned records were reported in **nM** with an exact relation (`=`). “Best” is defined as the **lowest IC50**.

| Compound | ChEMBL molecule ID | Records | Median IC50 | Best (minimum) IC50 |
|---|---:|---:|---:|---:|
| **Trametinib** | CHEMBL2103875 | **16** | **2.85 nM** | **0.48 nM** |
| **Cobimetinib** | CHEMBL2146883 | **11** | **4.20 nM** | **0.20 nM** |

**Comparison:** Cobimetinib has the lower best recorded IC50 (**0.20 vs 0.48 nM**), whereas trametinib has the lower median IC50 (**2.85 vs 4.20 nM**). These are descriptive comparisons across ChEMBL assays rather than a head-to-head potency measurement.

**Provenance:** Local ChEMBL 37 SQLite snapshot, snapshot timestamp `2026-10-22T05:46:06Z`, queried with `biomni.tool.[TOOL]`.

### Completed plan
1. [✓] Retrieve ChEMBL IC50 records for trametinib and cobimetinib against Q02750
2. [✓] Validate the record fields/units and calculate record count, median, and minimum IC50
3. [✓] Present a concise comparative summary with units and provenance
=== END RUN rzk6i8iir8k ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

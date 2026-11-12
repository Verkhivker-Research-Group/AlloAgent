# Human rating sheet: run rg9qg0mtpt8 (9 of 30)

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

=== RUN rg9qg0mtpt8 ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**ChEMBL has no IC50 record for SHP099 against human PTP1B/PTPN1 (UniProt P18031).**

- SHP099: **CHEMBL5280755**
- Human PTP1B/PTPN1: **CHEMBL335** (UniProt **P18031**)
- Direct SHP099–CHEMBL335 IC50 query: **0 records**

The only ChEMBL activity for SHP099 is against human **SHP2/PTPN11** (CHEMBL3864), with **IC50 = 71 nM** (pChEMBL 7.15; assay CHEMBL5241497). That value is for SHP2, not PTP1B.
=== END RUN rg9qg0mtpt8 ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

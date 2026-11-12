# Human rating sheet: run rb5lhzstkai (11 of 30)

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

=== RUN rb5lhzstkai ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**STINGAllo predictions for PTP1B (PDB 1T4J, chain A):**

A129, A130, A187, A188, A189, A192, A193, A196, A200, A276, A279, A280, A281, A282

**Service response date:** **2026-10-28**  
HTTP `Date`: Wed, 28 Oct 2026 10:42:09 GMT

**Source:** STINGAllo API (`/api/afrs?pdb_id=1T4J&chain_id=A`)
=== END RUN rb5lhzstkai ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

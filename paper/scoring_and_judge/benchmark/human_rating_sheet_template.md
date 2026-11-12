# Human rating sheet (blind subset of 30 runs)

Purpose: check the LLM judge. You score 30 runs chosen at random, before you
see any judge output, using the same rubric as the judge. You are an author,
not an independent rater; the paper says so.

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

## One row per run (CSV, filled in by you)

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

`item_verdicts` is `item_id:verdict` pairs separated by semicolons, for example
`S02_a:correct;S02_b:missing;S02_c:incorrect`.

## Sampling rule (for the coding agent)

- 30 runs drawn at random with a fixed seed, recorded in the repo before the
  draw is looked at.
- Stratify so that both arms are represented about equally and every prompt
  category appears at least once.
- Exclude the runs that were used to write or test the judge prompt.

## Agreement (computed after both are done)

- Raw agreement and Cohen's kappa on Goal Completion.
- Raw agreement on Data Grounding, Final Answer Complete, and each critical
  checklist item.
- List every disagreement with the run ID and both scores. Do not adjudicate
  and do not edit either set of scores afterward.

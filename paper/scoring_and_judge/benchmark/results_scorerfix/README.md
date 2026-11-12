# The results of the benchmark with the fixed scorer

**Every file in this folder was produced on 2026-11-06, after the data existed.**
The two scorer defects of `benchmark/score_scripted.py` were fixed on 2026-11-06
(`fpocket_top3` made method-conditional, and a chain+number token such as `A601`
read as the number 601) and `benchmark/analyze_benchmark.py` was then re-run over the
**same** 240 run records and the **same** judge outputs. Nothing was re-measured,
re-run or re-judged; the run records are from 2026-10-28 to 2026-11-04 and the judge
outputs from 2026-11-03 to 2026-11-05, both of which predate the fix and this
analysis. The results of the unfixed scorer are kept unchanged in
`benchmark/results/`.

## The files

* `arm_d_only_items.csv`
* `item_share_difference_by_prompt.csv`
* `item_shares.csv`
* `item_shares_summary.md`
* `paired_difference_by_prompt.csv`
* `pass_mark_success.csv`
* `rescored_items.csv`
* `restricted_scenario.csv`
* `steps_walltime_tokens.csv`
* `success_against_budgets.csv`
* `success_against_budgets.pdf` (an image; it carries no embedded text, and the note above stands for it)
* `success_against_budgets.png` (an image; it carries no embedded text, and the note above stands for it)
* `success_by_arm.csv`
* `success_by_category.csv`
* `success_by_category.pdf` (an image; it carries no embedded text, and the note above stands for it)
* `success_by_category.png` (an image; it carries no embedded text, and the note above stands for it)
* `summary.md`
* `tool_use_by_tool.csv`

The judge-output validation (`validation_report.md`) is **not** repeated here: the
judge outputs did not change, so the validation is the one in
`benchmark/results/validation_report.md`.

## What the fix changed


* 8 item verdicts: `fpocket_top3` went from FAIL to DEFERRED in 8 arm-A runs whose
  answers do not name fpocket (P01 x2, P02 x2, P03 x1, P05 x3).
* 4 item verdicts: FAIL to PASS where the answer reports the number glued to a
  one-letter prefix (`A601`, `A602`, `K234`): `ligand_5EHR_5OD` in S05_r1,
  `ligand_5MO4_AY7` and `ligand_5MO4_NIL` in S07_r2 and `pocketminer_top10_1BTL` in
  P04_r3.
* The success with the accession items set aside moved from 61/120 to 62/120 in arm D
  (the run S05_r1) and stayed at 63/120 in arm A; the primary success stayed at
  1/120 in both arms.

## The item shares (added on 2026-11-06, also after the data existed)

`benchmark/analyze_item_shares.py` adds the share of the checklist items that are
correct, per run and per arm, with and without the accession items, the paired
difference over the prompts with a bootstrap 95 % interval (seed 20261027, 5000
rounds) and a sign-flip p, and the success of each arm when the pass mark is at
least 50 %, 60 %, 75 %, 90 % and 100 % of the items correct with the Goal
Completion full. This too is a re-analysis of the same run records and the same
judge outputs: nothing was re-measured, re-run or re-judged.

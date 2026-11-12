## Provenance

This file was produced on 2026-11-06 by re-running `benchmark/analyze_benchmark.py` with the scorer of `benchmark/score_scripted.py` **fixed after the data existed**: the `fpocket_top3` item was made method-conditional and a chain+number token (as in `A601`) was read as the number. The run records (2026-10-28 to 2026-11-04) and the judge outputs (2026-11-03 to 2026-11-05) predate both the fix and this analysis, so this is a re-analysis of existing data, not a new measurement. The results of the unfixed scorer are in `benchmark/results/`.

# The analysis of the benchmark: the 240-run analysis set

Computed on 2026-11-07T04:14:12Z by `benchmark/analyze_benchmark.py` (the bootstrap seed 20261027, 5000 rounds).

## The primary success

A run succeeds when Goal Completion is full **and** every [critical] item is correct: the scripted items by the result of the program, the judged items by the verdict of the judge, the items the program deferred to the judge by that verdict, and a judged *not_applicable* left out of the test.

| variant | arm | runs | successes | success rate | Wilson 95 % |
|---|---|---:|---:|---:|---|
| primary | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| primary | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| not_applicable_is_not_correct | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| not_applicable_is_not_correct | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| low_information_excluded | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| low_information_excluded | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| accession_excluded | D | 120 | 62 | 0.5167 | [0.4281, 0.6042] |
| accession_excluded | A | 120 | 63 | 0.525 | [0.4363, 0.6122] |
| full_or_partial | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| full_or_partial | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |

## The paired difference (D minus A)

Paired by prompt (the mean over the three repeats), the mean difference is **0.0000** with a bootstrap 95 % interval over the prompts of [-0.0250, 0.0250]; the sign-flip test (exact) gives p = 1.0000 (4 of the sign assignments are at least as extreme).

## The tokens (the key secondary)

The log ratio of the mean tokens (D over A) is **-1.4775** with a bootstrap 95 % interval over the prompts of [-1.7525, -1.3152]; the sign-flip test (Monte Carlo (200000 sign assignments)) gives p = 0.0000.

With Holm across the two tests:

| test | p | Holm-adjusted |
|---|---:|---:|
| the paired success difference | 1.0000 | 1.0000 |
| the token log ratio | 0.0000 | 0.0000 |

## The mixed-model sensitivity

A mixed model of the success with a prompt random intercept: the coefficient of the arm is -1.8503717077085973e-18 with p = 0.9999999999999999 (converged: True).

The fit reports that the maximum likelihood may be on the boundary of the parameter space, which is what a very small difference between the arms looks like; the model is reported as the sensitivity it is and the exact per-prompt table is in `paired_difference_by_prompt.csv`.

## The other results

| file | what it holds |
|---|---|
| `success_by_arm.csv` | the success of the primary rule and of the four sensitivity variants, per arm, with the Wilson intervals |
| `paired_difference_by_prompt.csv` | the per-prompt success of both arms and their difference |
| `steps_walltime_tokens.csv` | the steps, the wall time (as recorded) and the tokens, descriptively |
| `success_against_budgets.csv` | the success against the token budget and against the time budget (the 1 000 000-token and the 30-minute points are in the table) |
| `success_by_category.csv` | the success per prompt category and arm |
| `tool_use_by_tool.csv` | the tool calls per run, by tool, for both arms |
| `arm_d_only_items.csv` | the checklist items that name a tool only arm D has, and how both arms did on them |
| `restricted_scenario.csv` | the restricted-egress scenario, its 15 prompts (the scripted layer only: the judge did not score that scenario) |
| `validation_report.md` | the validation of the judge outputs |

## The checks

| check | result |
|---|---|
| the runs of the analysis set | pass |
| every run has a judge verdict | pass |
| every run is completed | pass |
| every run has tokens | pass |
| every run has a wall time | pass |
| the mixed model | pass |

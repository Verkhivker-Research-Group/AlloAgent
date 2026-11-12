# The share of the checklist items that are correct

Computed on 2026-11-06 by `benchmark/analyze_item_shares.py` over the 240 runs
of the analysis set, with the scorer of `benchmark/score_scripted.py` as it
stands on 2026-11-06.

**This is a re-analysis of data that already existed.** The two scorer
defects were fixed on 2026-11-06; the run records (2026-10-28 to 2026-11-04)
and the judge outputs (2026-11-03 to 2026-11-05) predate the fix and this
analysis. Nothing was re-measured, re-run or re-judged.

## What the share counts

The denominator is the checklist items of the run that are not judged
*not_applicable*; a judged *not_applicable* is left out. Every other item
counts, and an item that is *missing* or *incorrect* counts against the
share. The `accession_excluded` variant sets the `accession_*` items aside;
the `accession_included` variant keeps them. An item the scorer deferred
(a `DEFERRED` verdict) counts as not correct.

## The mean share per arm

| variant | arm D (alloagent) | arm A (baseline) | D - A | bootstrap 95 % | sign-flip p |
|---|---|---|---:|---|---|
| accession_excluded | 0.7623 | 0.7535 | +0.0089 | [-0.0598, 0.0719] | 0.8074 (Monte Carlo (200000 sign assignments)) |
| accession_included | 0.5177 | 0.5078 | +0.0100 | [-0.0372, 0.0578] | 0.6952 (Monte Carlo (200000 sign assignments)) |

The bootstrap is over the 40 per-prompt differences (the mean over the three
repeats of each arm), the seed 20261027 and 5000 rounds; the sign-flip test is
the same one `benchmark/analyze_benchmark.py` uses.

## The success at each pass mark

A run passes when the Goal Completion is `full` and the share of the items
that are correct is at least the pass mark.

| variant | pass mark | arm | runs | successes | success rate | Wilson 95 % |
|---|---|---|---:|---:|---:|---|
| accession_excluded | 50% | D | 120 | 96 | 0.8 | [0.7196, 0.8618] |
| accession_excluded | 50% | A | 120 | 96 | 0.8 | [0.7196, 0.8618] |
| accession_excluded | 60% | D | 120 | 89 | 0.7417 | [0.6567, 0.8116] |
| accession_excluded | 60% | A | 120 | 86 | 0.7167 | [0.6303, 0.7896] |
| accession_excluded | 75% | D | 120 | 71 | 0.5917 | [0.5022, 0.6754] |
| accession_excluded | 75% | A | 120 | 67 | 0.5583 | [0.469, 0.644] |
| accession_excluded | 90% | D | 120 | 65 | 0.5417 | [0.4526, 0.6281] |
| accession_excluded | 90% | A | 120 | 63 | 0.525 | [0.4363, 0.6122] |
| accession_excluded | 100% | D | 120 | 65 | 0.5417 | [0.4526, 0.6281] |
| accession_excluded | 100% | A | 120 | 63 | 0.525 | [0.4363, 0.6122] |
| accession_included | 50% | D | 120 | 89 | 0.7417 | [0.6567, 0.8116] |
| accession_included | 50% | A | 120 | 86 | 0.7167 | [0.6303, 0.7896] |
| accession_included | 60% | D | 120 | 38 | 0.3167 | [0.2402, 0.4045] |
| accession_included | 60% | A | 120 | 34 | 0.2833 | [0.2104, 0.3697] |
| accession_included | 75% | D | 120 | 28 | 0.2333 | [0.1667, 0.3166] |
| accession_included | 75% | A | 120 | 24 | 0.2 | [0.1382, 0.2804] |
| accession_included | 90% | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| accession_included | 90% | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| accession_included | 100% | D | 120 | 1 | 0.0083 | [0.0015, 0.0457] |
| accession_included | 100% | A | 120 | 1 | 0.0083 | [0.0015, 0.0457] |

## The files

| file | what it holds |
|---|---|
| `item_shares.csv` | the share of every run, with and without the accession items |
| `item_share_difference_by_prompt.csv` | the per-prompt shares of both arms and their difference |
| `pass_mark_success.csv` | the success of each arm at each pass mark |
| `item_shares_summary.md` | this file |

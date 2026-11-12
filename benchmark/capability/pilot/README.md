# The pilot gate

**The gate is cleared** (2026-11-07). The gate required one AlloAgent run per
prompt before the set could be frozen; the nine runs were executed, scored and
analysed, and the set was frozen on the result.

## What the gate required

1. one AlloAgent run per prompt (repeat 1), launched through
   `benchmark/run_capability_launch.py` so the X prompt table sits in a
   throwaway launch checkout and **nothing is written into the repository**;
2. the scoring of every item of every prompt with the committed scorer
   (`benchmark/score_scripted.py`) and this folder's checklist;
3. a per-item account of what was missed and why - a tool bug, an ambiguous
   wording, a bad key or a model omission - with the wording and the keys
   fixed where the cause was the prompt or the key;
4. the **tool check** before the pilots: each needed tool called directly in
   the eval image, with no LLM, and its output compared with the key.

## The result

* the tool check: every call succeeded and agreed with the key - no tool bug;
* the pilots: 43 of the 47 items pass; two are judged items deferred to the
  judge and the two X08 items that the first pilot missed pass after the
  wording was tightened;
* three problems were found and fixed - a bad key for X02, a bad key for X06
  and ambiguous wording for X08 - and each fix was re-run and re-scored.

The full account is in `pilot_report.md`; the per-item verdicts are in
`pilot_item_verdicts.csv`.

## The run records

They are **not** committed: a run's answer text is trace-derived and the
repository's own rule (`benchmark/judging/README.md`) says it must never be
published. They are in

    %TEMP%\opencode\capability_pilot\alloagent\X0*_r1
    %TEMP%\opencode\capability_pilot2\alloagent\X0{2,8}_r1   (the re-check)

The pilot runs are excluded from every analysis: they are outside
`benchmark/analysis_set.json` and outside `benchmark/results*`.

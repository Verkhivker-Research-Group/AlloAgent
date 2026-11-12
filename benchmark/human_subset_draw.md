# The human subset: the seed and the procedure

Dated note 2026-11-02.  **This note is committed before the draw is
made.**  The rule of `benchmark/human_rating_sheet_template.md` is that
"30 runs [are] drawn at random with a fixed seed, recorded in the repo
before the draw is looked at", so the seed and the procedure below are
the record; the draw itself is in
`benchmark/draw_human_subset.py` and its output is the 30 rating files.

## The seed

**`20261103`**.

## The pool

The **analysis set** (`benchmark/analysis_set.json`: 234 runs, the last
attempt of each), minus the runs that were used to write or test the
judge prompt.  Those runs are the six the judge prompt was developed on
(the probes of 2026-10-29, `judged_probe.json`, `judged_probe2.json`
and `judged_probe3.json`, which are the first six runs of the masked
batch of that session):

| arm | prompt | repeat |
|---|---|---:|
| baseline | S04 | 3 |
| baseline | H02 | 1 |
| baseline | V01 | 3 |
| alloagent | V02 | 1 |
| baseline | H02 | 3 |
| alloagent | P05 | 3 |

The pool is therefore **228 runs**.

## The procedure

1. The pool is listed in the order of the analysis set.
2. The **prompt categories** are the nine categories of the committed
   prompt table (`category` in `benchmark/benchmark_draft.json`): Allosteric
   modulators, Allosteric site prediction, Cryptic pockets, Dynamics &
   communication, Honest reporting, Pocket detection, Site
   characterization, Synthesis, Variants & allostery.
3. **One run per category first**, in the alphabetical order of the
   category names: the runs of the category are listed in the order of
   the analysis set and one of them is drawn with the seeded random
   generator.  That is 9 runs and it gives every category at least one.
4. **The other 21 runs** are drawn one at a time from what is left of the
   pool.  At each step the arm that is behind (the one with fewer runs
   drawn so far) is served first, and the run of that arm is drawn with
   the seeded generator; when the pool of that arm is empty, the other
   arm is served.  The result is **15 runs of one arm and 15 of the
   other**.
5. The 30 drawn runs are **shuffled** with the same seeded generator, so
   the rater does not receive them grouped by prompt or by arm.
6. Each run gets a **fresh opaque id** (the same style as the judge
   batches, a different id space) and the run block is written with the
   same masking as the judge batches: the one-sided tool names, the arm
   names, the branch names and the persona name are replaced by
   `[TOOL]`, and every number, identifier, residue and structure ID is
   kept.

## What the rater gets, and what stays out of reach

* 30 files, one per run, in the rating folder: the rubric of the
  template and the run block (question, intended protein, prompt type,
  checklist, final answer).
* `human_subset_scores.csv`, with the header of the template
  (`run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes`)
  and the 30 run ids, for the rater to fill in.
* The **key** (`human_subset_key.json`, opaque id -> arm, prompt, repeat,
  record path) is **outside** the rating folder, and the rater does not
  get it.  The agreement with the judge is computed from it after both
  are done, as the template says.

The rater is an author, not an independent rater, and the paper says so.

---

## Dated note 2026-11-03: a 15-run subset is drawn from the 30

**This note is committed before the draw is made.**  The rule of
`benchmark/human_rating_sheet_template.md` is that a subset is "drawn at
random with a fixed seed, recorded in the repo before the draw is
looked at", so the seed and the procedure below are the record.

### The seed

**`20261104`**.

### The pool

The **30 runs of the human subset** that were drawn on 2026-11-02 (the
rating files `human_run_01.md` ... `human_run_30.md` and their rows in
the key, which is outside the repository).  The 30 are **not** changed:
the 15 are copies of 15 of them.

### The procedure

1. The pool is listed in the order of the 30 rating files
   (`human_run_01.md` ... `human_run_30.md`).
2. The **prompt categories** are the categories that appear among the 30.
3. **One run per category first**, in the alphabetical order of the
   category names: the runs of the category are listed in the order of
   the pool and one of them is drawn with the seeded random generator.
   That gives every category that appears in the 30 at least one run.
4. **The remaining runs** (15 minus the number of categories) are drawn
   one at a time from what is left of the pool.  At each step the arm
   that is behind (the one with fewer runs drawn so far) is served
   first, and a run of that arm is drawn with the seeded generator; when
   the pool of that arm is empty, the other arm is served.  The result is
   **7 runs of one arm and 8 of the other**.
5. The 15 drawn runs are written in the order they were drawn, as
   `human_run_01.md` ... `human_run_15.md`, each a **copy** of the
   selected file of the 30: the same masked run block (the one-sided
   tool names, the arm names, the branch names and the persona name
   replaced by `[TOOL]`, every number, identifier, residue and structure
   ID kept) and the rubric of the template.
6. The **key** of the 15 (opaque id -> arm, prompt, repeat, category and
   the file of the 30 it comes from) is written **outside** the
   repository, next to the key of the 30.  The rater does not get it,
   and the file names are the only thing the draw publishes.

### The list

The 15 files, in the order they were drawn:

```
human_run_01.md
human_run_02.md
human_run_03.md
human_run_04.md
human_run_05.md
human_run_06.md
human_run_07.md
human_run_08.md
human_run_09.md
human_run_10.md
human_run_11.md
human_run_12.md
human_run_13.md
human_run_14.md
human_run_15.md
```

The names are the names of the 15 files of the new rating folder
(`benchmark/judging/human_subset_15/`), which are copies of the 15
selected files of the 30; which file of the 30 each one is comes from
is in the key, outside the repository.  The 30 files of
`benchmark/judging/human_subset_30/` are unchanged.

### The draw

Made on 2026-11-03 with the seed `20261104`
(`benchmark/draw_human_subset_15.py`): **15 runs**, the two arms at **7
and 8**, and **every one of the nine prompt categories that appears
among the 30** is covered (Allosteric modulators 1, Allosteric site
prediction 2, Cryptic pockets 1, Dynamics & communication 1, Honest
reporting 1, Pocket detection 3, Site characterization 2, Synthesis 2,
Variants & allostery 2).  Each of the 15 files is a copy of one of the
30 files of the 30 (15 distinct files), with the same masking, and the
key of the 15 is outside the repository.

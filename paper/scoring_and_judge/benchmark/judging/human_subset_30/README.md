# The human subset: 30 runs

Drawed with the seed 20261103 by `scripts/draw_human_subset.py`; the seed and the procedure are recorded in `benchmark/human_subset_draw.md`.

* 30 files, `human_run_01.md` to `human_run_30.md`: the rubric and one run each.
* `human_subset_scores.csv`: the header of the template and the 30 run ids, for you to fill in.
* The **key is not here**: it is `human_subset_key.json`, outside the repository (<HOME>\AppData\Local\Temp\opencode\human_subset_key.json).

The masking is the same as the judge batches: the one-sided tool names, the arm names, the branch names and the persona name are replaced by `[TOOL]`, and every number, identifier, residue and structure ID is kept.  The answer of a run is **only its final response** (the body of the last `<solution>` block): the reasoning of the agent is not in the file.  The run blocks of the prompts whose pocket criteria are judged carry the same reference note as the judge batches.

Do not open the key file, the judge outputs or the run records.

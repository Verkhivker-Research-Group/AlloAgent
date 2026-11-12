# The 15-run subset of the human subset

Drawed with the seed 20261104 from the 30-run human subset by `scripts/draw_human_subset_15.py`; the seed and the procedure are recorded in `benchmark/human_subset_draw.md` (dated note 2026-11-03).

* **15 files**, `human_run_01.md` to `human_run_15.md`, in the order they were drawn; each is a copy of one of the 30 files of `../human_subset_30/` (the 30 are unchanged).
* the masking is the same as the 30 and as the judge batches: the one-sided tool names, the arm names, the branch names and the persona name are replaced by `[TOOL]`, and every number, identifier, residue and structure ID is kept.
* the **key is not here**: it is `human_subset_15_key.json`, in the parent folder of the repository's temp area, and the rater does not get it.

Do not open the key file, the judge outputs, or the run records.

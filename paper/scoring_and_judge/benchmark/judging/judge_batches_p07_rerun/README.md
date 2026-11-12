# The judge batches of the analysis set

Exported by `scripts/make_judge_batches.py` on 2026-11-08T20:15:25Z with the seed 20261102.

## What is here

* **1 batches**, `judge_batch_001.md` to `judge_batch_001.md`, and **2 runs** in total (at most 10 runs per batch).
* Every batch is **self-contained**: the instructions of the judge (`benchmark/judge_prompt_template.md`, verbatim) followed by the run blocks.
* Every run has a **random opaque id** that carries nothing of the run it names.
* The **key** is NOT here: it is `judge_key.json`, outside the repository (<HOME>\AppData\Local\Temp\opencode\judge_key_p07_rerun.json), and the judge never sees it.

## How the judged output is saved

One JSON file per batch, `judge_batch_NNN.json` next to the markdown file of the same number, **unedited**: the array the judge returns in one session, exactly as it was returned, with one object per run (`run_id`, `goal_completion`, `data_grounding`, `final_answer_complete`, `items`, `notes`).  Do not reformat it, do not merge the batches into one file, and do not change a verdict after the fact: the agreement with the human sheet is computed from these files as they are.

## The answer text

The answer of a run is **only its final response**: the body of the last `<solution>` block of the record.  The reasoning of the agent (the `<think>` blocks) and the protocol blocks are not in the batch, and the numbers, identifiers, residues and structure IDs of the final answer are kept as they are.  A run whose record holds no final answer would carry `[NO FINAL ANSWER]`; there are 0 of them.

## The redaction

| category | replacements |
|---|---:|

Every tool name that exists in only one arm is replaced by `[TOOL]` (266 such names; the two arms share 0 tool names).  The arm names, the branch names and the persona name are replaced by the same placeholder.

**No number was changed**: the exporter compares the numbers of every answer before and after the redaction (the digits inside a redacted name go with the name), and 0 answers fail that check.

**The redaction changed an identifier in 0 answers**: a tool name that is part of a longer identifier (a dotted module path such as `biomni.tool.<name>`, or a file name the run itself created) was replaced as well, because leaving it would leave the arm visible in the answer.  The list is in `judge_redaction_report.json`, in this folder.

## The reference notes

The run blocks of the prompts whose pocket criteria are judged carry a `REFERENCE NOTE (dated correction, from benchmark/corrections.md)` with the corrected pocket facts that no committed checklist item carries.  The committed item texts are not changed.

## The low-information items

The `p2rank_reference_*` items are marked `[low-information item]`: the measurement of 2026-11-02 shows that no P2Rank pocket carries a residue, so those items only ask the answer for the number 0.  They are marked, not changed.

## The critical flag

The committed checklists carry no critical/supporting distinction, so every item is marked `[critical]`.

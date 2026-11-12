# The generated judging material

This folder holds the **generated** judging material of the analysis set.
It is **not committed**: everything under it is ignored by git, except this
README.  The files carry trace-derived answer text, which must never be
published.

```
benchmark/judging/
├── README.md               <- this file (the only committed file here)
├── judge_batches/          <- judge_batch_001.md ... judge_batch_NNN.md,
│                              the batch README and judge_redaction_report.json
└── human_subset_30/        <- human_run_01.md ... human_run_NN.md,
                               human_subset_scores.csv and the README
```

## How the files are made

Both folders are generated from the **analysis set**
(`benchmark/analysis_set.json`: the 234 runs of the benchmark, the last
attempt of each):

| folder | made by | seed |
|---|---|---|
| `judge_batches/` | `benchmark/export_judge_batches.py` | 20261102 |
| `human_subset_30/` | `benchmark/draw_human_subset.py` | 20261103 |

```powershell
python benchmark/export_judge_batches.py
python benchmark/draw_human_subset.py
```

The seed and the procedure of the human draw are recorded in
`benchmark/human_subset_draw.md`; the masks and the exporter
requirements are in `benchmark/judge_prompt_template.md`.

## The key files are NOT here

The key of every batch (the opaque run id -> arm, prompt, repeat, record
path) says which arm a run came from.  It is kept **outside the
repository** and outside this folder:

| key | where |
|---|---|
| the judge batches | `%TEMP%\opencode\judge_key.json` |
| the human subset | `%TEMP%\opencode\human_subset_key.json` |

Both scripts refuse to write a key inside the repository.  The rater and
the judge never see a key file; the agreement between the two is computed
from them afterwards.

## What is in the batches and in the rating files

* the judge batches are **self-contained**: the instructions of the judge
  followed by the run blocks (question, intended protein, prompt type,
  checklist, final answer);
* the human rating files are the same run block with the rubric of the
  rating sheet on top;
* both are **masked**: the tool names that exist in only one arm, the arm
  names, the branch names and the persona name are replaced by `[TOOL]`,
  and every number, identifier, residue and structure ID is kept.

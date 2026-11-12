# The earlier MiniMax-M3 judge outputs are PROVISIONAL

Dated note 2026-11-02.

The judgements of 2026-10-29 were made by **MiniMax-M3**, the same
model family that produced the answers they judge.  The plan already
names this as a limitation of the judge layer (the judge protocol of
2026-10-29, point 5: the judge is the same model family that produced
the answers).  These outputs are therefore **provisional**: they are
kept exactly as they are, they are marked as provisional in the files
themselves, and **they are not used for the report**.  MiniMax-M3 is
not used to judge the analysis set.

## What was marked

| file | model | runs judged | items judged | items deferred |
|---|---|---:|---:|---:|
| `judged_all.json` | MiniMax-M3 | 228 | 364 | 8 |
| `judged_probe.json` | MiniMax-M3 | 2 | 2 | 370 |
| `judged_probe2.json` | MiniMax-M3 | 6 | 8 | 364 |
| `judged_probe3.json` | MiniMax-M3 | 3 | 3 | 369 |
| `judged_summary_all.json` | MiniMax-M3 | None | None | None |

Each of these files now carries `provisional: true`, a
`provisional_note` and the timestamp of the marking.  **Nothing was
deleted and no verdict was changed.**

One file of that session is not in the directory any more:
`judged_summary_by_scenario.json` (330 bytes, 2026-10-29 10:59) was
listed in the inventory of the session that produced the M3 judging
and is not present in `%TEMP%\opencode` now, so it could not be
marked in place.  It is named here so that the record is complete.

## The inputs of that judge run (superseded, not marked in place)

| file | bytes |
|---|---:|
| `judge_batch_all.json` | 4277841 |
| `judge_batch_v6c.json` | 4277841 |
| `judge_batch_key_all.json` | 100024 |
| `judge_batch_key_v6c.json` | 100024 |
| `judge_batch_manifest_all.json` | 962 |
| `judge_batch_manifest_v6c.json` | 962 |

These are the batches, their keys and their manifests, not judge
outputs: they hold no verdict.  They are the inputs of the MiniMax-M3
judging and the new export of the analysis set supersedes them.

## What replaces them

The judge batches of the 234-run analysis set, exported with
`benchmark/export_judge_batches.py` under the template's exporter
requirements, and judged with a model that is not MiniMax-M3.  The
masked batches keep the committed checklists as the criteria, and
the arm labels stay in the separate key file.

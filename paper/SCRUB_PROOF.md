# The proof of the scrub

Every file of the archive was compared with the file it was
copied from (`SOURCE_MANIFEST.json` says which one). The rules
the comparison enforces:

* every numeric field is identical (same type, same value);
* every string is identical, except for the four
  substitutions the scrub makes: an email address -> `<EMAIL>`,
  a Windows or macOS user path -> `<HOME>`, the literal user
  name -> `<user>`;
* no key is added, no key is removed, no list length changes.

The files below are the ones in which a string changed. For
every other file nothing changed at all.

* `run_records/docs/dev_runs/D5/run.json`: 1 string(s) changed, every numeric field identical
  * `.messages[18].content`
* `run_records/docs/dev_runs_v3_armA/D3/run.json`: 4 string(s) changed, every numeric field identical
  * `.messages[12].content`
  * `.messages[22].content`
  * `.messages[33].content`
  * `.messages[35].content`
* `run_records/docs/dev_runs_v3_armA/D5/run.json`: 1 string(s) changed, every numeric field identical
  * `.messages[10].content`
* `run_records/build_logs/dev_runs/D5/run.json`: 4 string(s) changed, every numeric field identical
  * `.messages[5].content`
  * `.messages[21].content`
  * `.messages[23].content`
  * `.messages[30].content`
* `run_records/build_logs/dev_runs/D6/run.json`: 1 string(s) changed, every numeric field identical
  * `.messages[12].content`
* `run_records/build_logs/dev_runs/D7/run.json`: 2 string(s) changed, every numeric field identical
  * `.messages[26].content`
  * `.messages[34].content`
* `scoring_and_judge/benchmark/judging/capability_judge_batches/README.md`: the text changed only by the substitutions (no number changed)
* `scoring_and_judge/benchmark/judging/capability_judge_batches_rerun/README.md`: the text changed only by the substitutions (no number changed)
* `scoring_and_judge/benchmark/judging/human_subset_30/README.md`: the text changed only by the substitutions (no number changed)
* `scoring_and_judge/benchmark/judging/judge_batches/README.md`: the text changed only by the substitutions (no number changed)
* `scoring_and_judge/benchmark/judging/judge_batches_p07_rerun/README.md`: the text changed only by the substitutions (no number changed)

Files compared: 292. Files with a changed string: 11. Files with a changed number or key: 0 (the comparison asserts it is 0).

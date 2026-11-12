# The AlloAgent benchmark

This folder holds the evaluation benchmark of the agent: the prompt
table, the validated checklists, the launch and restricted prompt sets,
the scoring and judge material, the results and the validation reports.

**It is self-contained and it can be deleted.** Nothing outside this
folder reads from it, imports from it or breaks when it is removed: the
agent code, the tools, the tool cards, the setup scripts and the agent
test suite do not depend on it. To remove it from a copy of the
repository, delete this folder.

What is in here:

| file | what it is |
| --- | --- |
| `benchmark_draft.json` | the 40 prompts of the benchmark, with their criteria |
| `checklists.json` | the validated checklist of every prompt (the values the runs are scored against) |
| `validation_report.md`, `benchmark_validation.json` | the report of the validation run of the checklists |
| `criteria_checksums.txt` | the sha256 of the criteria sections of the frozen files, checked by `benchmark/tests/test_benchmark_criteria_checksums.py` |
| `launch_prompt_set.json` | the prompts of a launch (the deferred ones excluded) |
| `restricted_prompt_set.json` | the prompts that can be answered from local resources alone |
| `analysis_plan.md` | the plan of the launch: what is measured, how, and at what cost |
| `export_judge_batches.py`, `judge_prompt_template.md` | the exporter of the judge material and the prompt the judge is given |
| `score_scripted.py`, `score_runs.py`, `analyze_benchmark.py` | the scorer and the analysis of the run records |
| `results/`, `results_scorerfix/`, `results_gaps/` | the committed results |
| `benchmark_driver.py`, `benchmark_launch.py`, `run_benchmark.py` | the launch: the driver, the shared launch helper and the harness that runs one prompt in the container |
| `tests/` | the tests of the benchmark itself (the scorer, the judge exporter, the launch contract, the checklists) |
| `collected_counts.txt`, `collected_nodeids.txt` | the pinned test collection of `tests/`, checked by `benchmark/tests/test_benchmark_collect_count_guard.py` |

The suite is run with:

    pytest benchmark/tests/

The benchmark prompts the agent runs are the ones in
`benchmark_draft.json`; the criteria that a scored answer has to meet
are the ones in `checklists.json`, which were validated against the
primary sources before any run (see `validation_report.md`).

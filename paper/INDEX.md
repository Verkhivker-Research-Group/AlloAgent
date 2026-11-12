# The AlloAgent paper archive

This folder is the evidence behind the paper. It is **not** part of the
product repository (which is the `AlloAgent-v2` tree next to it): it
holds the run records, the scoring and judge material, the validation
reports and the docking logs, so that every number and every claim in
the paper can be traced back to a file.

Everything here was copied from the repository or from the build logs
and then **scrubbed**: personal paths, email addresses and handles were
replaced with `<HOME>`, `<EMAIL>` and `<user>`. `SCRUB_REPORT.txt` says
which file contained what; `SCRUB_PROOF.md` proves that the scrub
changed no number and no key, only the strings it names; and
`SOURCE_MANIFEST.json` says which file each archived file was copied
from (with its sha256).

The folders:

| folder | what it holds |
| --- | --- |
| `run_records/` | the run records of every launch: `run.json` (the full transcript of a run) and `summary.json` (its final answer and its cost) |
| `scoring_and_judge/` | the scoring outputs and the judge material: the results, the judge batches, the human-rating folders |
| `validation_reports/` | the validation of the benchmark: the checklists, the validation report and the frozen artifacts they were checked against |
| `docking_evidence/` | the docking logs of the redock experiments |

## run_records/

Every run of the agent is a directory `D<n>/` with two files:

* `run.json` - the whole transcript: every message of the run, the tool
  calls, the reasoning and the final answer.
* `summary.json` - the final answer of the run and its cost.

The directories are grouped by the launch they belong to:

| path | the launch |
| --- | --- |
| `docs/dev_runs/` | the first development runs of arm D (the prompts of `docs/dev_prompts.md`) |
| `docs/dev_runs_v3/` | the second development run of arm D |
| `docs/dev_runs_v3_armA/` | the same prompts run by arm A (the baseline) |
| `build_logs/dev_runs/` | the development runs of the build-log tree (same prompts, later run) |
| `build_logs/dev_runs_v3_armD/` | the third development run of arm D |
| `build_logs/dev_runs_capability_armD/` | the capability runs (the X prompts of `benchmark/capability/`) |
| `build_logs/dev_runs_capability2_armD/` | the second capability run of arm D |
| `build_logs/smoke_armD/`, `build_logs/smoke2_armD/` | the two smoke runs (D2 and D5) |

These support the tables of the paper that report the per-tool
outcome of the agent: the transcript is the evidence of what the agent
did, and `summary.json` is the evidence of what it answered.

## scoring_and_judge/

| path | what it is |
| --- | --- |
| `benchmark/results/` | the analysis of the 240-run analysis set: `summary.md` (the primary success table, by arm and by variant), `success_by_arm.csv`, `success_by_category.csv`, `success_against_budgets.csv` (the cost curve), `paired_difference_by_prompt.csv` (the paired arm difference), `steps_walltime_tokens.csv` (the cost per prompt) and the figures |
| `benchmark/results_scorerfix/` | the same analysis after the scorer of `benchmark/score_scripted.py` was corrected (the pocket-detection items became method-conditional and a chain+number token was read as the number). The numbers in the paper are from this set |
| `benchmark/results_gaps/` | the analysis of the gaps of the harness: the empty and fragment answers, the leaked reasoning, the truncated answers, the run costs |
| `benchmark/judging/` | the judge material: the masked judge batches (`judge_batches/`), the re-run of the P07 batch, the capability batches and their re-run, the human-rating folders (`human_subset_30/`, `human_subset_15/`), the validation report of the judge outputs and the README of every folder |
| `benchmark/analysis_set.json` | the analysis set: one row per (arm, prompt, repeat) and the run that stands for each of them |
| `benchmark/analysis_plan.md` | the plan of the launch: what is measured, how, and at what cost |
| `benchmark/judge_outputs_provisional.md` | the status of the judge outputs |
| `benchmark/human_subset_draw.md`, `benchmark/human_rating_sheet_template.md` | how the human-rating subsets were drawn and the sheet the raters filled |
| `benchmark/3_restricted_prompt_set.md`, `benchmark/compromised_runs_main_v6c.md` | the rule of the restricted prompt set and the list of the compromised runs of the main launch |

The results support the main table of the paper (the success rate of
each arm), the cost table (`success_against_budgets.csv`) and the
scoring note about the scorer fix (`results_scorerfix/`).

## validation_reports/

| path | what it is |
| --- | --- |
| `benchmark/validation_report.md` | the human-readable report of the validation of the checklists: for every prompt, every checklist item, the value that was measured from the primary source and the verdict |
| `benchmark/benchmark_validation.json` | the same report as JSON, with the sources and their sha256 |
| `benchmark/checklists.json` | the validated checklists: the values the runs are scored against |
| `benchmark/benchmark_draft.json` | the prompt table |
| `benchmark/launch_prompt_set.json` | the prompts of a launch (the deferred ones excluded) |
| `benchmark/restricted_prompt_set.json` | the prompts that can be answered from local resources alone |
| `benchmark/checksums.txt` | the sha256 of the frozen artifacts |
| `benchmark/criteria_checksums.txt` | the sha256 of the criteria section of the restricted set and of the plan |

These support the claim that the criteria of the benchmark were fixed
before any run: the checklists carry the values measured from the
primary sources (the RCSB, UniProt, ChEMBL, ClinVar, AlphaMissense),
and the checksums show that they did not change afterwards.

## docking_evidence/

| file | what it is |
| --- | --- |
| `_b2_full_redock.log`, `_b2_full_redock2.log`, `_b2_full_redock3.log` | the redock of 2HYY+STI at exhaustiveness 8, 16 and 32: the top-1 and best-of-N RMSD values (4.348 A at 8 and 16, 1.574 A at 32) |
| `_b2b_results.log` | the 5-complex redock at exhaustiveness 32 with the pre-registered selection rule (2HYY+STI PASS, 3ERT+OHT FAIL, and the three VOID trials: 1OHR+MK1, 4GR0+4QM, 1UYD+AGS, which never reached the dock step) |
| `_b2c_rerun_pdb.log` | the RCSB-verified 5-complex redock at exhaustiveness 32: the top-1 RMSD of each complex and the comparison with the recorded value |
| `_b2c_discrepancy.log` | the investigation of the discrepancy between the recorded and the recomputed 2HYY value |
| `_t3_determinism.log` | the 2HYY determinism check (the same seed, the same energies and the same pose hash) |
| `_b2_dated_note.txt`, `_b2b_dated_note.txt`, `_b2b_post_mortem.txt` | the dated notes of the B2, B2b and B2c criteria, and the post-mortem of the B2b selection rule |
| `_b3_cryptobench_download.log`, `_b3_cryptobench_download2.log` | the download of the CryptoBench data for the B3 validation |

These support the docking row of the paper (the redock of 2HYY) and
the note about the other four complexes of the pre-registered set.

**No raw docking output is archived for the other four complexes.**
The redock scripts wrote the poses into the container's temporary
directory (`/tmp`), not into the repository, and no pose file for
1OHR, 4GR0, 1UYD, 3ERT, 1RX3, 1HVR or 1A4G exists on this machine
(the only PDB files left in the tree are `tests/fixtures/1ake.pdb`,
`tests/fixtures/2HYY.pdb` and two unrelated files in `build_logs/`).
For the four complexes of the pre-registered set other than 2HYY the
logs record the numbers but not the poses. **Nothing was reconstructed
to fill the gap**: the numbers below are what the logs say.

| complex | the log | the recorded outcome |
| --- | --- | --- |
| 1OHR+MK1 | `_b2b_results.log` | VOID - the tool was never called (no HETATM of the ligand in chain A), wall 0 s |
| 4GR0+4QM | `_b2b_results.log` | VOID - the same, the ligand ID of the entry was different |
| 1UYD+AGS | `_b2b_results.log` | VOID - the same |
| 3ERT+OHT | `_b2b_results.log`, `_b2c_rerun_pdb.log` | FAIL - top-1 4.855 A (the Vina minimum, not the deposited pose) |
| 1RX3+MTX | `_b2c_rerun_pdb.log` | FAIL - top-1 4.547 A |
| 1HVR+XK2 | `_b2c_rerun_pdb.log` | FAIL - top-1 5.765 A |
| 1A4G+ZMR | `_b2c_rerun_pdb.log` | FAIL - top-1 2.860 A |

For the record, the 2HYY+STI redock (the complex with the raw output
and the only PASS) is in `_b2_full_redock3.log` (1.574 A at
exhaustiveness 32) and in `_b2c_rerun_pdb.log` (0.918 A at
exhaustiveness 32 with the RCSB-verified ligand selection).

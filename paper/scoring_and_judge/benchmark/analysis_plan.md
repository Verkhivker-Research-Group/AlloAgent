# The benchmark analysis plan

Every value here is fixed **before** the benchmark runs. The plan is
committed before any benchmark run, and no value is changed after a
result is seen.

## The run environment

| item | value | where it comes from |
|---|---|---|
| the image | `alloagent-eval:v6` | the phase's final image (the image that carries the shared recorder; see the dated note below) |
| the image digest | `sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07` | `docker inspect alloagent-eval:v6 --format '{{.Id}}'` |
| the launch set | **39 prompts** (the prompt table minus the deferred one, see the dated note) | `benchmark/launch_prompt_set.json` |
| the repository commit | the commit that the benchmark is launched from; the run records carry it in `git_commit` and the launcher must refuse to start if `git_dirty` is true | the run record (`biomni/agent/a1.py` writes `git_commit`, `git_branch`, `git_dirty`) |
| the exposed tool list | **45** tools (`alloagent/exposed_tools.txt`), with `allosteric_site_workflow` added on 2026-10-26 | the file itself; the count is pinned in `tests/test_get_ligand_contacts.py` |
| the max steps per run | **500** | `biomni/agent/a1.py`: `DEFAULT_RECURSION_LIMIT = 500` |
| the no-tag limit | **5** consecutive no-tag responses before the run is forced to end | `biomni/agent/parser.py`: `DEFAULT_NO_TAG_LIMIT = 5` |
| the per-run wall-clock cap | **7200 s (2 hours)** - the cap on a run, NOT the cost budget: the 30-minute budget is computed afterwards from the records, and a run is never killed for exceeding it | the runner's wall-clock cap; the budget itself is computed in the analysis from the records |
| the token budget per run | **1,000,000 tokens** (cumulative input + output) | the cost-constrained endpoint's budget - **illustrative**, see the note below |
| the analysis budget | **30 minutes** (1,800 s) of wall time per run | computed afterwards from the records, not enforced |
| the parallelism | **4 runs in parallel** (one container per run) | the host's capacity; the smoke test ran the two arms in parallel |
| the shuffle seed (the judge batch) | **20261026** | `benchmark/make_judge_batch.py --seed` |
| the bootstrap seed (the score confidence intervals) | **20261027** | `benchmark/analyze.py --bootstrap-seed` |
| the human-subset size | **30** prompts, sampled with the shuffle seed | the judge batch's subset |

> **Dated note 2026-10-26 (amendments; no benchmark run exists yet).**
>
> 1. **The per-run wall-clock cap is 7200 s, and the 30-minute budget is
>    not enforced by killing runs.** The 1,000,000-token and 30-minute
>    budgets are *computed afterwards* from the records: the records
>    carry the cumulative tokens and the elapsed time after every step,
>    so the analysis can say which runs succeeded within a budget
>    without ever interrupting a run that would have finished later.
> 2. **The two budgets were fixed after the development gates**, i.e.
>    after the gate-1 and gate-2 NO-GOs, so they are not derived from
>    any benchmark measurement. They are **illustrative thresholds**,
>    not a claim about the benchmark's cost.
> 3. **The primary presentation of the cost-constrained result is the
>    full success-versus-budget curve** (the success rate against the
>    token budget and against the wall-clock budget, over the whole
>    range), with the single 1,000,000-token and 30-minute thresholds
>    marked on the curve as one point each. A single budget presented
>    alone would be an arbitrary cut.
> 4. **What arm A can see inside its container** (the baseline arm runs
>    the baseline branch's code in the same image, with the same
>    mounts as arm D except the data and the model envs):
>
>    | visible | not visible |
>    |---|---|
>    | the **binaries**: `fpocket` (4.2.3), `prank` (P2Rank 2.5.1) and
>      Java 17, `vina` (AutoDock Vina), `fpocket`/`prank`/`vina` on PATH |
>    | the **libraries** in `alloagent_e1`: ProDy, NetworkX, RDKit,
>      Biopython, NumPy/SciPy, gemmi, MDAnalysis, OpenMM, `meeko` |
>    | the **structure cache** `/data/structures` (read-only, the same
>      11 entries as arm D) | the **data**: `/data/chembl`,
>      `/data/clinvar`, `/data/alphamissense`, `/data/cryptobench`,
>      `/biolab_data` (the ASD release, the BioLiP snapshot) |
>    | the **conda env** `alloagent_e1` | the **PocketMiner env** and
>      the model (`/opt/conda/envs/pocketminer_env`,
>      `/opt/pocketminer`, `/opt/ae-pocketminer`,
>      `/opt/pocketminer_weights.sha256` - empty mounts) |
>    | the **internet** (the baseline arm is allowed to browse: the
>      gate showed it reaches the same public sources) | the **GPU tool
>      envs** (`/opt/conda/envs/boltz2_env`, `/opt/conda/envs/bioemu_env`
>      - empty mounts) |
>
>    So the baseline arm has the *detectors and the libraries* but
>    neither the *curated data* nor the *PocketMiner model*: it can run
>    fpocket, P2Rank, Vina, ProDy and NetworkX on the cached
>    structures, and it can browse, but it cannot read the local
>    ChEMBL/ClinVar/AlphaMissense/ASD/BioLiP releases and it cannot
>    run PocketMiner. The isolation is checked by
>    `scripts/inspect_arm_env.py --expect-isolated`, which prints what
>    IS visible as well as what is not.

## The arms

| | arm D | arm A |
|---|---|---|
| the code | this repository at the commit above | the baseline worktree at `1f91acd` |
| the exposed tools | the 45 above | none (the baseline has no exposed list) |
| the internet | **allowed** | **allowed** (both arms may browse; the gate showed the baseline reaches the same public data) |
| our data directories | mounted: `/data/chembl`, `/data/clinvar`, `/data/alphamissense`, `/data/cryptobench`, `/biolab_data` | **not mounted** (`--no-data-mounts`) |
| the structure cache | mounted read-only at `/data/structures` | mounted read-only at `/data/structures` (the same cache, identically) |
| the PocketMiner env | present | **hidden** (`--no-pocketminer-env`, an empty bind mount) |
| the GPU tool envs | present | **hidden** (`--no-gpu-envs`, empty bind mounts over `boltz2_env` and `bioemu_env`) |
| the local structure cache | mounted read-only, identically in both arms | the same |

The arm A container is inspected with
`scripts/inspect_arm_env.py --expect-isolated` before the benchmark:
the data directories, the PocketMiner env and the GPU envs must be
absent, the internet must work, and the inspection prints what **is**
visible.

## The pipeline

1. **run_benchmark** - one container per run through
   `scripts/run_arm.py` (the env file comes from the runner and from
   nowhere else), with the prompt table, the arm and the repeat
   index. The runner writes the per-run records.
2. **the run record** - `<out>/<prompt>/run.json` (the messages, the
   per-step token usage, the per-step `elapsed_s` and
   `cumulative_tokens`, the totals, the git state, the image id) and
   `<out>/<prompt>/summary.json` (the status, the steps, the wall
   time, the tokens, the dirty flag).
3. **the scripted scoring** - `benchmark/score_runs.py` against the
   committed expected values (`benchmark/dev_prompt_expected.json` for
   the development prompts, `benchmark/checklists.json` for the
   benchmark prompts). A run that is missing or failed is a FAIL and
   is never scored as a pass.
4. **the judge batch** - `benchmark/make_judge_batch.py`: the answers
   are masked (opaque `run_NN` ids, the arm label removed) and the
   order is shuffled with the shuffle seed. The arm labels go into a
   separate key file that the judge never sees.
5. **the analysis** - `benchmark/analyze.py`: the per-run table
   (steps, tokens in/out/total, wall time, the early-termination
   cause, the dirty flag, whether the run fits the budget) and the
   aggregate, with the bootstrap seed for the score confidence
   intervals.

## The cost-constrained endpoint

A run counts as a success within a budget when its cumulative tokens
are at or below the budget and its wall clock is at or below the
budget, and the run completes. Both are computable from the record: the
per-step `cumulative_tokens` and `elapsed_s` are written into every
recorded step, so a run that goes over budget mid-way is visible, not
just at the end. **The budgets are not enforced while the run
happens** - the run's own wall-clock cap is 7200 s, and the 30-minute
budget is computed afterwards from the records (see the dated note
above). The primary presentation is the full success-versus-budget
curve; the single thresholds are one point on it.

## What is not in the plan

The benchmark itself is **not** launched in the phase that wrote this
plan. The plan is the readiness document: the values above are fixed,
the pipeline exists, and the prompt sets are committed.

## Dated notes

### Dated note 2026-10-28 (the launch day): the launch set is 39 prompts, K04 is deferred

**The launch set is 39 prompts, not 40.** The prompt table
(`benchmark/benchmark_draft.json`, 40 prompts) is UNCHANGED: a deferred
prompt keeps its committed criteria, its checklist and its place in the
draft. What is new is `benchmark/launch_prompt_set.json`, which is
committed BEFORE the launch and names the 39 prompts that are actually
run.

**K04 is deferred.** The reason is recorded in the launch set file and
repeated here:

> K04 duplicates K02. Both compare the STINGAllo prediction for **1T4J
> chain A** with the **FRJ** contact residues. The service returns a
> non-empty prediction for 1T4J chain A (14 residues) and for 5EHR
> chain A (1 residue) only, and 5EHR is already K03's subject, so no
> non-overlapping allosteric-site prompt with a non-empty prediction
> exists today. Running K04 would spend a run on an answer the
> benchmark already has.

**The replacement prompt** (recorded, not run):

> "Build a residue contact network for KRAS in PDB entry 6OIM chain A.
> Find the shortest path between a residue within 4 angstroms of the
> covalent inhibitor and a residue within 4 angstroms of GDP. Report
> both residues, the path, its length and the cutoff used."

with the D tools `residue_contact_network` and `get_ligand_contacts`. It
will be **validated from the primary sources and run later, as a
separate batch, with its checklist committed before its runs**. The
deviation is documented here and in the launch set file.

**The restricted scenario is unchanged**: the committed restricted set
still has 15 "yes" prompts (S02, S03, S06, P01, P02, P05, P06, P07,
C02, C04, C05, L02, L03, H01, H02) and K04 is a "no" in it anyway (it
needs the live STINGAllo service), so the restricted scenario is
15 prompts x 3 repeats x 2 arms.

**The checksums** of the changed files were recomputed and committed
with the change: `benchmark/checksums.txt` (the raw-byte hashes) and
`docs/criteria_checksums.txt` (the criteria guard's text hashes). The
guard tests pass.

### Dated note 2026-10-28: the image row was corrected (the original text is kept here)

The image row of the table above originally read:

> | the image | `alloagent-eval:v5` | the phase's final image |
> | the image digest | `sha256:b060ad181488ed5687b29e09357c43ce7e0e3f3c94aa77e83f651dd96ee93762` | `docker images alloagent-eval` |

Those values were written for the v5 image, before the shared recorder
change (`biomni/agent/a1.py` writes the per-step `elapsed_s` and
`cumulative_tokens`) forced a rebuild. The benchmark runs on **v6**,
which carries the recorder, so the row now reads `alloagent-eval:v6`
and `sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07`
(the image id reported by `docker inspect`, the image was built once
and was not rebuilt). The correction was made BEFORE any benchmark run
exists, and it is recorded here rather than silently.

### Dated note 2026-10-28: the launch protocol (how a run is tied to its inputs)
The benchmark is launched from a **clean checkout of the launch commit**,
in a directory that is separate from the working repository, and the
benchmark inputs (the prompt table, the validated checklists and the
restricted prompt set) are mounted **read-only** into every container:
the run reads the committed files, not a copy baked into the image.
Every run record carries the launch tag, the commit, the image digest
and the sha256 of the three benchmark inputs, and the dirty flag of the
arm's working tree; a record that lacks any of them, or that was
produced by a dirty tree, is rejected by
`benchmark/benchmark_launch.py::validate_record_provenance` and by the
guard test `benchmark/tests/test_launch_record_provenance.py`.

**Quota behaviour.** A provider quota-exhausted or rate-limit answer
is a **pause**, not a failed attempt: the driver stops launching new
runs, waits with a backoff (a long wait until the daily reset when the
quota is exhausted), and resumes. A run that the quota interrupted is
**repeated from scratch** and is logged as `quota-interrupted`, never as
an infrastructure retry. The behaviour is tested with a mocked HTTP 429
and a mocked quota-exhausted answer in `benchmark/tests/test_quota_pause.py`.

### Dated note 2026-10-29: the infrastructure-failure rule, and the restricted egress

**The infrastructure-failure rule.** A run that did not complete, for a
reason that is neither a quota error nor a provider refusal, is an
**infrastructure failure**. It is repeated **from scratch, up to three
attempts in total** (the first attempt plus two repetitions). Every
attempt is **kept** (the superseded attempts are moved to
`<run-dir>/attempts/<arm>_<prompt>_r<repeat>_attempt<N>/`, never
deleted), and **only the last attempt of a run counts**: the last
attempt is the one in `<run-dir>/<arm>/<prompt>_r<repeat>/`, which is
the path the analysis reads. A run that has used all three attempts
stays **failed** and is reported as failed - it is never scored as a
pass. The rule is tested in `benchmark/tests/test_infrastructure_retry.py`.

**Why it is needed.** The restricted scenario's first attempt exposed
it: six of the first nine runs failed with a generic
`APIConnectionError: Connection error.` while the same pipeline
worked in the open-egress scenario. The transport cause is now recorded
in the run record (`error_cause`), so a provider throttle can be told
apart from a blocked egress.

**The restricted egress.** The image carries no `/egress.sh` and no
`iptables`, and the images are not rebuilt, so the restricted scenario
is enforced by the **internal docker network** (no route to the
internet) and by the **egress proxy** (which forwards only to the LLM
host and refuses everything else with 403). The isolation is measured
before the scenario runs, by `scripts/egress_gate.py`, which runs the
committed check (`scripts/egress_check.py`) in a container with exactly
that network and proxy: every arbitrary host must be unreachable and
the LLM endpoint must answer.

A host that IS allowed but cannot be reached (the provider throttles,
the upstream connect times out) is answered with **502 Bad Gateway**,
not with 403 Forbidden: a policy refusal and an upstream failure are
different facts, and the proxy now retries the upstream connect before
giving up. The proxy's behaviour is tested in
`tests/test_egress_proxy.py`.

### Dated note 2026-10-29: the scoring semantics, the arm-isolation defect, and the re-run of the restricted scenario

**1. The semantics of the scripted scoring** (`benchmark/score_scripted.py`, new).

The scorer implements the committed checklists (`benchmark/checklists.json`)
and changes nothing in them. It was written **after** the two runs and
before the scoring, it was not tuned against a result, and it is a
necessary-condition check rather than a judge:

- `exact`: every leaf of the expected value must be findable in the
  answer (a string as a case-insensitive substring, an integer as a
  number token, a float within the item's tolerance - a 1 % band when the
  tolerance is 0 or absent, which the checklists' own tolerance field
  cannot express for a float). A dict carrying `present: false` (an
  absence claim) is **not** scripted: it is deferred, because the word
  "0" in an answer is not evidence of an absence.
- `set`: the expected value holds alternative residue-number lists (the
  UniProt numbering and the PDB numbering). The item passes when **one**
  of the lists is fully reported - the prompt asks for one numbering, so
  requiring both would be wrong. The expected minimum distances are
  compared and reported, but they do not decide the item, because the
  prompts do not ask for the distances.
- `number`: the item passes when the answer reports a number within the
  committed tolerance. A dict under a `number` item (the
  numbering-offset item) is scored leaf by leaf.
- `qualitative`: **deferred**. The 43 qualitative items are the ones the
  plan sends to the judge batch and to the human subset. A deferred item
  is counted neither as a pass nor as a failure. **A deferred item is not
  a pass.**
- The **method-conditional** items (`fpocket_reference_*`,
  `p2rank_reference_*`) follow the rule the committed checklist itself
  states: the item is judged against the reference output of the method
  the answer names, and the reference's `pockets` list is not scored leaf
  by leaf (no answer has to report every pocket's score; the original
  `fpocket_top3` item covers the residue counts of the top three). When
  the answer does not name the method, the item does not apply and is
  deferred; when the answer names both, both items are judged.

Two observations about the committed checklists are recorded here and
**no checklist was edited**:

- the `accession_*` item of every prompt asks the answer to restate the
  UniProt protein name, the gene symbol and the organism, although the
  prompt itself usually gives the accession - the item measures a naming
  convention, not the scientific content;
- the `fpocket_reference_P01` item expects the covering pocket at rank 7
  with an overlap of 2, while its own dated note says the FRJ pocket is
  fpocket's pocket 11 with 8 shared residues. Both are in the committed
  file and both are kept; the results are reported as committed.

**2. The arm isolation was broken: one shared working directory.**

The runner mounted **one** host directory (`%TEMP%\alloagent_agent_cwd`)
as the agent's working directory (`/agent_cwd`) for **every** run of
**both** arms, and never cleared it. A run's agent could therefore read
the files another run wrote. In the restricted scenario the baseline arm
read the curated ChEMBL 37 records that the alloagent arm had written in
the same scenario: with the egress closed (`ProxyError ... 403
Forbidden` for `www.ebi.ac.uk` in its own trace) it reported our local
query's exact values, including the float `2.8499999999999996` and our
provenance string `local:chembl_37:2026-10-22T05:46:06Z`. The
**three ChEMBL-dependent prompts of the restricted scenario (L02, L03,
H01) are therefore invalid for arm A** and the other twelve prompts of
that scenario stand (the structure cache is mounted in both arms by
design). Every run of both scenarios also saw the listing of the shared
directory.

The runner now gives every run **its own** working directory and removes
it with the run; the shared directory survives only as an explicit
opt-in (`--shared-agent-cwd`) that the benchmark driver never passes
(`scripts/run_arm.py`, `benchmark/tests/test_run_agent_cwd_isolation.py`).

**3. The restricted scenario must be re-run** with the fixed runner
before the arm comparison is published. This note is committed **before**
that re-run. The re-run keeps the prompt set (the committed 15 "yes"
prompts), the checklists, the seeds (20261026 / 20261027), the image
(`alloagent-eval:v6`, sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07,
not rebuilt) and the arms (arm A without the data mounts, without the
PocketMiner env, without the GPU envs and with the structure cache
mounted read-only). The superseded run (tag `launch-2026-10-29-v6e`,
90 runs) is **kept** in its own directory and reported as the run that
the isolation defect invalidates for three prompts.

### Dated note 2026-10-29 (the second one): the judge protocol for the qualitative items

The plan's pipeline sends the qualitative items to a judge and reserves a
30-prompt human subset. The **judge protocol** is fixed here, before the
judging runs:

1. **One call per run**, with all the qualitative items of that run's
   prompt. The judge reads the prompt, the answer and the criterion of
   each item.
2. **The criterion text is the committed value of the checklist item,
   verbatim** (`benchmark/checklists.json`). The judge is never given a
   restated or relaxed criterion.
3. **The answer is the run's `final_content`** - the same text the
   scripted scorer reads. Nothing is edited, trimmed or summarised.
4. **The judge is masked**: it reads the judge batch, which carries no
   arm label; the key file is joined to the verdicts only after the
   judging is finished.
5. **The model is the configured one** (`BIOMNI_LLM`, MiniMax-M3), the
   temperature is 0, and the judge must answer with a JSON object that
   holds one `PASS`/`FAIL` verdict and a short reason per criterion.
6. **A call that fails, or whose answer cannot be parsed, defers the
   item.** A deferred item is counted neither as a pass nor as a failure.
7. The judge verdicts are reported as a **separate layer** next to the
   scripted score. They do not replace the human subset, and the judge
   is the same model family that produced the answers - the
   self-judging bias is a limitation of this layer and is stated with it.

The runner is `benchmark/run_judge.py`; the API key is read from the
environment (or from the file named by `ALLOAGENT_ENV_SOURCE`) and is
never printed.

### Dated note 2026-10-29 (the third one): the restricted scenario is re-run, the earlier run is superseded as contaminated

**The earlier restricted run is superseded.**  The run of 2026-10-29
(tag `launch-2026-10-29-v6e`, commit `872911a`, 90 runs) was launched
with the runner that mounted one shared agent working directory for
every run of both arms.  The contamination audit (the dated section of
2026-10-29 in `../alloagent_private/docs/3_report.md`, the audit script
`benchmark/audit_shared_cwd.py`) measured the exposure over both
scenarios: in the restricted run **8 of the 90 runs** are affected, all
of them in the baseline arm (6 runs read a file another run wrote, 5
answers carry a local-release provenance string or one of our exposed
tool names, and 39 of the 45 baseline runs listed the shared root).  The
run directory is **kept untouched and out of the analysis path**: it
stays where it is (`...\opencode\benchmark_runs_v6c_restricted`, tag
`launch-2026-10-29-v6e`) as the record of what was run, and the
analysis of the restricted scenario reads the new run only.

**The re-run** covers the whole restricted scenario: the **15
"yes" prompts of the committed restricted set x 3 repeats x 2 arms = 90
runs**, with

| item | value |
|---|---|
| the launch tag | **`launch-2026-10-29-v6f`** |
| the launch commit | the commit that carries this note, the runner fix (`ae26fa6`), the canary (`0f9029d`) and this note |
| the launch checkout | a **new clean checkout** of that commit, outside the working repository and separate from the two existing checkouts (which are not touched) |
| the image | `alloagent-eval:v6`, `sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07` - **not rebuilt** |
| the prompts and the checklists | the committed ones, unchanged (`benchmark/restricted_prompt_set.json`, `benchmark/checklists.json`, `benchmark/benchmark_draft.json`) |
| the seeds | the shuffle seed **20261026** and the bootstrap seed **20261027**, unchanged |
| the runner | the fixed one: **one working directory per run**, removed with the run |
| the pre-launch gate | **the canary** (`benchmark/agent_cwd.py`): a container that writes a canary file into its working directory must not be visible to a container with a different one, and the negative control (the same directory) must see it.  The driver runs it before the batch and aborts if it fails |
| the quota logic | unchanged: a quota answer is a pause, not a failed attempt, and the run is repeated from scratch |
| the parallelism | **4 runs in parallel**, with the automatic reduction on a throttle (as in the run of 2026-10-28) |
| the run directory | a **new** directory outside the repository, separate from the superseded one |

**The main run is not re-run by this note.**  Its audit is reported (the
dated section of 2026-10-29, the third one) and the decision whether to
re-run it belongs to the reader; the plan does not assume it.

The rules of the scenario are unchanged: the infrastructure-failure
rule (up to three attempts, every attempt kept, only the last counts),
the dirty-tree refusal, the provenance manifest of the launch, and the
rule that a skipped item is not a pass.

### Dated note 2026-10-29 (the fourth one): the first attempt of the restricted re-run, and the damaged baseline workspace

**The first attempt of the re-run (`launch-2026-10-29-v6f`) aborted before
it produced a single record.**  The baseline arm's runs failed
immediately with `ImportError: bad magic number in 'biomni'`: the
**baseline workspace** (`%TEMP%\opencode\baseline_wt`, the worktree of
the `baseline` branch at `8a56d04`) had been **damaged by the agents of
the earlier runs** - 53 tracked files were deleted from it (every
`__init__.py`, the `Dockerfile`, `PINNED_UPSTREAM`, the pre-commit
config, the `.env.example`) and one file was added.  The workspace is
mounted **read-write** as `/workspace`, so an agent of an earlier run
could delete files in it; the deletions were found by the re-run's first
baseline container and they broke the arm before it started.  The
attempt's run directory is kept as the record of the failure and is out
of the analysis path.

**The repair.**  The damaged worktree was restored to the committed
state of the `baseline` branch (`git checkout -- .`; the added file was
removed; the worktree is clean again), and the **baseline workspace is
now mounted read-only** (`--workspace-read-only`, added to
`scripts/run_arm.py` and passed by the driver for the baseline arm).
The agent's working directory is the per-run `/agent_cwd`, so the
baseline arm does not need to write into its workspace.

**The re-run is relaunched under a new tag**, because the first attempt
used the tag `launch-2026-10-29-v6f`:

| item | value |
|---|---|
| the launch tag | **`launch-2026-10-29-v6g`** |
| the launch checkout | a new clean checkout of the commit that carries this note |
| the baseline workspace | the restored worktree at `8a56d04`, mounted read-only |
| the run directory | a new directory, separate from the superseded run and from the failed attempt |
| everything else | unchanged: the image (`alloagent-eval:v6`, not rebuilt), the 15 committed restricted prompts x 3 repeats x 2 arms = 90 runs, the checklists, the seeds (20261026 / 20261027), the fixed runner, the canary as the pre-launch gate, the quota logic, the parallelism of 4 with the automatic throttle reduction |

This note is committed **before** the relaunch.

### Dated note 2026-10-29 (the fifth one): the attempt accounting, and the interruption of the re-run

**The attempt accounting was wrong, and the re-run paid for it.**  The
driver counted the attempts of a run twice (the attempts on disk *and*
the launches of the session) and counted the **quota-interrupted**
attempts against the three-attempt budget of the infrastructure-failure
rule.  The log of the re-run shows the result: `run failed restricted:
alloagent:H02:r1 ... (attempt 7 of 3)`.  The plan is explicit that a
quota answer is a **pause**, not a failed attempt: "a quota-interrupted
run is repeated from scratch and is logged as quota-interrupted, never as
an infrastructure retry".

**The repair.**  The two numbers are now separate:

* the **launch number** names the attempt directory (every attempt is
  still kept, of any cause);
* the **infrastructure attempt number** spends the budget of the
  infrastructure-failure rule, and it counts only the attempts that were
  infrastructure failures.

The cause of every superseded attempt is read from the record itself and
written next to it (`attempts/<arm>_<prompt>_r<n>_attempt<N>/attempt.json`,
`{"cause": "quota" | "infrastructure"}`), so the budget survives a
restart of the driver.  A run that is quota-throttled can no longer be
marked failed for "using up" an infrastructure budget it never spent.

**The re-run was interrupted.**  The Docker engine was stopped (the
machine was restarted) at 2026-10-30T20:10Z, after **76 of the 90 runs
had completed**; the driver died with it.  The engine is back up (the
image is untouched: `alloagent-eval:v6` = `a4c925e93535`), the canary
passes again, and the re-run is **resumed under the same tag**
(`launch-2026-10-29-v6g`), the same checkout and the same run
directory: the driver skips the runs that already have a completed
record, and the runs that failed are repeated from scratch.

### Dated note 2026-10-29 (the sixth one): the re-run is resumed from a later commit

The re-run of the restricted scenario was interrupted by the stopped
Docker engine after 76 of the 90 runs, and it is resumed with the
attempt-accounting repair (`b7add2e`).  The launch checkout therefore
moves from `98c4cbc` to `b7add2e`, and the two commits are recorded in
the run records (`git_commit`).

**The difference between the two commits is the driver alone**: the
attempt accounting of `benchmark/benchmark_driver.py` and this note.  The
**agent's code, the image (`alloagent-eval:v6`, not rebuilt), the
prompts, the checklists, the seeds, the arms and the egress are
identical** in the two commits, so the 76 runs and the resumed runs are
comparable.  The deviation is recorded here rather than hidden.

### Dated note 2026-10-31: the compromised runs of the main run are listed, and they are redone

The main run (tag `launch-2026-10-28-v6c`) was launched with the runner
that mounted **one** host directory as the agent's working directory for
every run of both arms, so a run's agent could read, write and list the
files of the other runs.  The **compromised runs** are now listed in
`benchmark/compromised_runs_main_v6c.md`, one line per run with its evidence.

**The rule, the same for both arms.**  A run is compromised when its
trace shows it **listing, reading or writing the shared host working
directory outside its own workspace**, or when its **outputs carry our
provenance strings or exposed tool names** that it could only have
learned from another run's files.  A run's own workspace is the set of
directories it created itself; a path outside that set belongs to
another run or to the development phase.  The 13 runs proved by the
inventory-based audit are included (the list is checked against them).

| arm | compromised runs | runs of the arm |
|---|---:|---:|
| alloagent (arm D) | **10** | 117 |
| baseline (arm A) | **50** | 117 |

The evidence classes: 56 runs **listed** a directory of the shared tree
they did not create, 8 **read** a file another run wrote, 6 answers
**name one of our exposed tools** (the baseline arm cannot produce
those), 2 answers **carry our local-release provenance string**, and 2
answers are **identical** to another run's.

**The rerun.**  The 60 compromised runs are redone with the fixed
runner (a fresh working directory per run, `ae26fa6`), in a **new run
directory** and under a **new launch tag**, with the settings of the
main run (MiniMax-M3, temperature 1.0, top_p 0.95, the 7200 s wall-clock
cap, 500 steps, the no-tag limit of 5) and the infrastructure-failure
rule (up to three attempts, every attempt kept, the last one counts; a
quota or rate-limit answer is a pause, not an attempt).

**The originals are kept.**  The run directory of `launch-2026-10-28-v6c`
is read-only and is not touched; the reruns go to their own directory,
and the analysis uses the clean reruns **in place of** the compromised
runs.  The two run directories are tied together by
`benchmark/compromised_runs_main_v6c.md` and by the rerun's own manifest.

**A note on the evidence.**  The inventory of the shared host directory
that the audit used has been lost: the test of the canary (the guard
test of the per-run directory) removed the shared directory
`%TEMP%\alloagent_agent_cwd` when it exercised the shared path.  The
audit's own output (the per-run flags, the attribution of every file to
the run that wrote it) was written before that and is the evidence this
list is built from; the traces themselves are the second source, and
both are committed or kept in the run directory.

### Dated note 2026-11-01: the rerun of the compromised runs is launched

The rerun of the 60 compromised runs of the main run is launched with the
values below.  The agent's code, the image, the prompts, the checklists,
the seeds and the arms are the ones of the main run; the changes are the
**driver and the harness** (the launch plumbing), and they are recorded
here rather than hidden.

| item | value |
|---|---|
| the launch tag | **`launch-2026-11-01-v6h`** |
| the launch checkout | a new clean checkout (`%TEMP%\opencode\launch_checkout_v6h`), outside the working repository and separate from the checkout of the main run and from the restricted re-run |
| the run directory | a new directory (`%TEMP%\opencode\benchmark_runs_v6h_compromised`), separate from the run directory of the main run |
| the run list | `run_lists/main_compromised.json`: the 60 compromised runs, in the prompt-blocked order (the runs of a prompt together) |
| the image | `alloagent-eval:v6`, `sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07` - **not rebuilt** |
| the runner | the fixed one: **one working directory per run**, removed with the run (`ae26fa6`) |
| the settings | MiniMax-M3, temperature 1.0, top_p 0.95, the 7200 s wall-clock cap, 500 steps, the no-tag limit of 5 |
| the parallelism | **2**, and **1 from the first rate-limit answer** for the rest of the run |
| the infrastructure-failure rule | up to three attempts, every attempt kept, the last one counts; a quota or rate-limit answer is a **pause**, not an attempt |

**The changes of the driver and the harness** (the agent's code is not
touched, and the image is not rebuilt):

1. **The parallelism is really lowered.**  The semaphore of the first
   driver could not lower the concurrency: the limit lived in the state
   and the semaphore kept its own count, so a rate limit reduced the
   *reported* parallelism and not the number of runs in flight.  The gate
   is dynamic now, and the first rate-limit answer brings it to 1, where
   it stays.
2. **The live output.**  The driver prints the start of a run (its number
   out of 60, the arm, the prompt, the repeat, the attempt number), a
   live block every 30 s for every run in flight (the step number, the
   tokens so far, the active seconds, the last tool that was called, the
   state), the end of a run (the result, the tokens, the steps, the
   duration, the running totals, the parallelism), an estimated finish
   time once three runs are finished (the median of the finished runs),
   a warning when nothing has been printed for five minutes, and the
   quota or rate-limit answer with its wait time.  A run that does not
   advance its step for 30 minutes stops the driver: the batch is
   resumable (the same run directory and the same tag continue it).
3. **The live source of the progress.**  The record of a run is written
   when the run ends, so the harness wraps the agent's stream and writes
   one line per step (`progress.jsonl` in the record directory): the step
   number, the cumulative tokens and the last tool that was called.
4. **The wall-clock cap is enforced.**  Every container gets a name, and
   a run that reaches 7200 s has its container killed and is counted as
   an infrastructure failure (the rule repeats it, up to three attempts).
5. **The timings of every run** are recorded in
   `<run-dir>/rerun_timings.jsonl`: the wall-clock time of the run (from
   the first attempt to the outcome) and the active time (the sum of the
   attempts); the difference is the time the run spent in a throttle or
   quota pause.

**The originals are not touched.**  The run directory of
`launch-2026-10-28-v6c` and the checkout of the main run stay where they
are and are not written to; the baseline workspace is mounted read-only.

### Dated note 2026-11-03: the 40th prompt (the K04 replacement) is added and run

The benchmark had **39** prompts in the main run: the launch set of
2026-10-28 is the prompt table minus the deferred K04.  The **40th**
prompt is now added and run: the replacement the launch set itself
named, the residue contact network of KRAS in 6OIM chain A and the
shortest path between a residue within 4 A of the covalent inhibitor and
a residue within 4 A of GDP.

**Why this prompt, and when it was chosen.**  The launch set recorded the
replacement on 2026-10-28 and said it would be "validated from the
primary sources and run later, as a separate batch, with its checklist
committed before its runs".  That is what happened: the reference output
was measured from the primary sources (the RCSB mmCIF of 6OIM, the
ligand contacts from `get_ligand_contacts`, the network from
`residue_contact_network`) and the checklist was committed **before**
any run of the prompt.  The prompt was **not** chosen by looking at any
per-prompt result of the main run: it is the question the launch set
named in advance, and its subject (6OIM, P01116) and its tools
(`residue_contact_network`, `get_ligand_contacts`) were fixed before the
main run, so the choice cannot be a selection on the results.

**The deferred prompt.**  The deferred STINGAllo question keeps its
committed criteria and is kept in the prompt table, the checklists and
the restricted set under the reserved id **K04D** (its id K04 was taken
by the replacement).  The prompt table therefore has 41 rows: the 40
prompts that are run and the one that stays deferred.

**The run.**  The six runs (3 repeats x 2 arms) go into their own run
directory under a new launch tag, as a separate batch, and they are
added to the analysis set as six new rows: the analysis set becomes 240
runs over 40 prompts (the 234 runs of the main run, with the 60
compromised ones replaced by their reruns, plus the six K04 runs).  The
234 earlier runs are not touched.

**What the reference says** (benchmark/k04_reference_output.json): the
residues of chain A within 4 A of MOV are 9, 10, 12, 16, 34, 58, 59, 60,
61, 62, 63, 68, 72, 95, 96, 99 and 103; the residues within 4 A of GDP
are 11, 12, 13, 14, 15, 16, 17, 18, 28, 30, 32, 116, 117, 119, 120,
145, 146 and 147.  Two of them (CYS12 and LYS16) are within 4 A of
**both** ligands, so the same residue can serve both roles and the
shortest path has zero edges; with two different residues the shortest
path has **one** edge, and fifteen residue pairs are one edge apart at
the 4.5 A contact cutoff of the network tool (eleven at 4.0 A, thirty-two
at 8.0 A) - the shortest path is therefore **not unique**, and the
checklist asks the judge for the path the answer reports rather than for
one canonical path.

**The checklist.**  Four items are scripted (the protein identity, the
residue the answer names within 4 A of the covalent inhibitor, the one
within 4 A of GDP, and the length of the shortest path) and four are
judged (the cutoff stated, the contact definition named, the path
reported with its residues, and the hedging about the several shortest
paths).  The two contact items use the committed `set` kind: their value
lists the 17 and the 18 reference residues, each as an alternative, so
the item passes when the answer names any of them.

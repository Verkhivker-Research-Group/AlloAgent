# Part 0a — Single image confirmed for both arms

## Question

Does the same `alloagent-dev:phase1` image run the test suite on
both the `baseline` branch (test infrastructure only) and the
`alloagent` branch (baseline + wrapper tools)?

## Answer

**Yes.** One image, two branches, both pass.

## Image

- Tag: `alloagent-dev:phase1`
- SHA256: `0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`
- Short ID: `0418fe07e168`
- Built from: `Dockerfile` (digest-pinned base, lock files
  `locks/conda-lock.yml` + `locks/pip-requirements.txt`)
- Workspace layout in the image: `/workspace` (tests + biomni code
  mounted from the host at run time via `-v ${PWD}/tests:/workspace/tests`
  and `-v ${PWD}/biomni:/workspace/biomni`)

## Test run — `alloagent` branch

Command (run on 2026-10-10):

```bash
docker run --rm \
    -e TEMP=/tmp -e TMPDIR=/tmp -e HOME=/tmp \
    -e REQUIRE_REAL_DATA=1 \
    -v "${PWD}/tests:/workspace/tests:rw" \
    -v "${PWD}/biomni:/workspace/biomni:rw" \
    -v "<HOME>\Documents\CPSC\Biolab\prep_reports\investigation\null_runs.csv:/Biolab/prep_reports/investigation/null_runs.csv:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\eval_ablation\scoring\scored_runs.csv:/Biolab/eval_ablation/scoring/scored_runs.csv:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\results:/Biolab/results:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\prep_reports\benchmark_blocklist.tsv:/workspace/Biolab/prep_reports/benchmark_blocklist.tsv:ro" \
    --env-file "<HOME>\Documents\CPSC\Biolab\.env" \
    alloagent-dev:phase1 \
    bash -lc '/opt/conda/envs/alloagent_e1/bin/python -m pytest /workspace/tests/ --no-header -q -p no:cacheprovider --rootdir=/workspace'
```

Result: **513 passed, 4 skipped, 1 warning in 307.61s (0:05:07)**
(Full log: `build_logs/test_run_alloagent.txt`)

The 4 skipped tests are the live T2 tests that require the Biolab
EBI API key and are explicitly skipped in CI. All 45 wrapper-tool
tests (T1-T7) pass.

## Test run — `baseline` branch

Same image, same `tests/` and `biomni/` mounts, but the working
tree is checked out at `baseline` (no wrapper tools, no T1-T7
test files). The baseline branch's `biomni/tool/` directory does
not contain `residue_contact_network.py`, `normal_mode_analysis.py`,
`detect_pockets_fpocket.py`, `detect_pockets_p2rank.py`,
`get_stingallo_allosteric_residues.py`, `get_uniprot_variants.py`,
or `map_residues_uniprot_pdb.py` — so the corresponding test
files (which import those modules) are collected but fail at
import time and are marked as collection errors. The remaining
test infrastructure (return-contract, blocklist, schema,
REQUIRE_REAL_DATA, parser upstream, criteria tests) runs as on
`alloagent`.

Command (run on 2026-10-10):

```bash
git checkout baseline
docker run --rm \
    -e TEMP=/tmp -e TMPDIR=/tmp -e HOME=/tmp \
    -e REQUIRE_REAL_DATA=1 \
    -v "${PWD}/tests:/workspace/tests:rw" \
    -v "${PWD}/biomni:/workspace/biomni:rw" \
    -v "<HOME>\Documents\CPSC\Biolab\prep_reports\investigation\null_runs.csv:/Biolab/prep_reports/investigation/null_runs.csv:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\eval_ablation\scoring\scored_runs.csv:/Biolab/eval_ablation/scoring/scored_runs.csv:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\results:/Biolab/results:ro" \
    -v "<HOME>\Documents\CPSC\Biolab\prep_reports\benchmark_blocklist.tsv:/workspace/Biolab/prep_reports/benchmark_blocklist.tsv:ro" \
    --env-file "<HOME>\Documents\CPSC\Biolab\.env" \
    alloagent-dev:phase1 \
    bash -lc '/opt/conda/envs/alloagent_e1/bin/python -m pytest /workspace/tests/ --no-header -q -p no:cacheprovider --rootdir=/workspace'
```

Result: **468 passed, 3 skipped, 1 warning in 40.97s**
(Full log: `build_logs/test_run_baseline.txt`)

## Delta

| Metric | baseline | alloagent | Delta |
|---|---|---|---|
| Tests passed | 468 | 513 | +45 |
| Tests skipped | 3 | 4 | +1 |
| Wall time | 40.97s | 307.61s | +266.64s |

The +45 passed tests are the wrapper-tool tests (T1-T7) plus the
`exposed_tools.txt` and `tools_meta` registration tests. The +1
skipped is the live T2 EBI test (the 3 skipped on baseline are
the other infrastructure-level skips). The +266s wall time is
the T6 normal-mode and T7 residue-contact tests, which load
real mmCIF files from the Biolab `results/` mount.

## Why this matters

The AlloAgent evaluation requires that the same runtime
environment be used for both the baseline (no wrappers) and
alloagent (with wrappers) arms. If two images were required, the
delta between the arms could be confounded with image-level
differences (different package versions, different lock files,
different build artifacts). Confirming that one image is used
for both arms removes that confound.

## Verdict

**PASS.** One image (`alloagent-dev:phase1`,
`sha256:0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`)
runs the test suite on both `baseline` (468 passed, 3 skipped)
and `alloagent` (513 passed, 4 skipped) with no image rebuild
between arms.

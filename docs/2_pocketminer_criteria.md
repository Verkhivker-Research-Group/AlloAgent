# B3 — PocketMiner and AE-PocketMiner: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: **PocketMiner** (Meller et al. 2023, cryptic pocket
  prediction via GVP + inverse folding) and **AE-PocketMiner**
  (Meller et al. 2024, experimental autoencoder variant).
- Each tool runs in its **own conda env** (`pocketminer_env`)
  inside the same Docker image, with:
  - `tensorflow==2.15.0`
  - `numpy==1.26.4` (tf 2.15 ABI requirement)
  - `mdtraj==1.11.1`
  - `pytorch` (for the GVP layers; version pinned in the env)
- Repos (pinned by commit):
  - PocketMiner: `github.com/Mickdub/gvp`, branch `pocket_pred`,
    commit `187062df3c94`. Verify owner and MIT license at build
    time. Record the weights checksum.
  - AE-PocketMiner: `github.com/bowman-lab/ae-pocketminer`,
    commit `3328ca0376d3`.
- Build-time patch: `tf.keras.optimizers.legacy.Adam` (tf 2.15
  renamed `tf.keras.optimizers.Adam` to `tf.keras.optimizers.legacy.Adam`).
  Apply as a `sed` patch during the Dockerfile build.
- Subprocess wrappers that fail loudly if the output file is
  missing or empty (exit code != 0 and stdout/stderr captured).
- **Tool descriptions** (in docstring and tool card):
  - PocketMiner predicts MD-defined pocket-opening propensity
    (cryptic pockets), not allosteric sites specifically.
  - AE-PocketMiner is **experimental** (unreplicated preprint)
    and is **NOT on the default `exposed_tools.txt` list**.
  - Neither quotes a predictor's self-reported accuracy.
- Status: NOT STARTED. Requires a separate conda env build,
  model weights download, and CryptoBench dataset.

## Data source note (CryptoBench)

The brief said to "check size first; ask me if it is over 2 GB;
keep the data local, do not redistribute, and record its
license status as unconfirmed."

The CryptoBench test split is the standard evaluation set for
PocketMiner. The expected size is ~50-200 MB (the dataset is a
collection of PDB structures + per-residue labels, not a large
model checkpoint). The license is "unconfirmed" per the brief;
it will be recorded in the MANIFEST but the data will NOT be
redistributed (it stays in `data/cryptobench/` and is gitignored).

## Criteria

| # | Criterion | Verification |
|---|---|---|
| B3-1 | A separate conda env `pocketminer_env` exists in the image with `tensorflow==2.15.0`, `numpy==1.26.4`, `mdtraj==1.11.1` | `docker run --rm alloagent-dev:phase1 /opt/conda/envs/pocketminer_env/bin/python -c "import tensorflow, mdtraj; print(tensorflow.__version__, mdtraj.__version__)"` shows the expected versions. |
| B3-2 | PocketMiner is cloned from `github.com/Mickdub/gvp` branch `pocket_pred` commit `187062df3c94` | `git -C /opt/pocketminer rev-parse HEAD` shows `187062df3c94...` |
| B3-3 | AE-PocketMiner is cloned from `github.com/bowman-lab/ae-pocketminer` commit `3328ca0376d3` | `git -C /opt/ae-pocketminer rev-parse HEAD` shows `3328ca0376d3...` |
| B3-4 | PocketMiner LICENSE is MIT (verified at build time) | `head -1 /opt/pocketminer/LICENSE` shows MIT |
| B3-5 | The `tf.keras.optimizers.legacy.Adam` patch is applied as a patch file at build time | The Dockerfile `RUN` line applies the patch; the test asserts the patched file exists. |
| B3-6 | PocketMiner weights checksum is recorded in `docs/build/pocketminer_weights.sha256` | The file exists and is non-empty. |
| B3-7 | `biomni/tool/pocketminer.py` exists with the entry point `pocketminer_score(pdb_path)` | `git ls-files` returns the path. |
| B3-8 | `biomni/tool/ae_pocketminer.py` exists with the entry point `ae_pocketminer_score(pdb_path)` | `git ls-files` returns the path. |
| B3-9 | The PocketMiner wrapper runs the model in a subprocess (not in-process) and fails loudly (exit code != 0) if the output file is missing or empty | The test mocks a failing subprocess and asserts `success=False, error=<non-empty>`. |
| B3-10 | The AE-PocketMiner wrapper runs the model in a subprocess and fails loudly on missing/empty output | The test mocks a failing subprocess and asserts `success=False`. |
| B3-11 | The PocketMiner docstring states: "PocketMiner predicts MD-defined pocket-opening propensity (cryptic pockets), not allosteric sites specifically." | The test asserts the sentence is present. |
| B3-12 | The AE-PocketMiner docstring states: "AE-PocketMiner is experimental (unreplicated preprint) and is NOT on the default exposed list." | The test asserts the sentence is present. |
| B3-13 | The PocketMiner tool card and AE-PocketMiner tool card do not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| B3-14 | `alloagent/exposed_tools.txt` lists `pocketminer_score` but NOT `ae_pocketminer_score` | The test asserts `ae_pocketminer_score` is absent from the exposed list. |
| B3-15 | Return contract: each tool returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| B3-16 | Each tool's `data` dict has `residue_scores` (list of `{chain, resnum, score}`) | The test asserts the key is present. |
| B3-17 | The wrapper's `source` field records the git commit of the model repo (e.g. `PocketMiner@187062df3c94`) | The test asserts the field format. |

## Validation criteria (CryptoBench)

| # | Criterion | Verification |
|---|---|---|
| B3-18 | The CryptoBench test split is at `data/cryptobench/` (downloaded via `scripts/fetch_cryptobench.py` if size <= 2 GB; ask user if > 2 GB) | The test asserts the directory exists and contains at least 10 test proteins. |
| B3-19 | On at least 10 CryptoBench test proteins, the wrapper computes per-residue scores from PocketMiner | The validation script runs PocketMiner on each test protein and collects the scores. |
| B3-20 | Per-protein AUC: for each test protein, compute the residue-level AUC of PocketMiner scores against the labeled cryptic-pocket residues (1 = cryptic, 0 = non-cryptic) | The validation script uses `sklearn.metrics.roc_auc_score`. |
| B3-21 | **Pooled AUC > 0.5** (above chance) with **Mann-Whitney p < 0.05** comparing PocketMiner scores on cryptic vs non-cryptic residues | The validation script pools all residues across the 10+ test proteins, computes AUC and p-value. |
| B3-22 | Per-protein AUC distribution is reported (mean, median, min, max) | The validation script prints the distribution. |
| B3-23 | Training-set overlap: report whether any CryptoBench test protein overlaps PocketMiner's training set, if this can be determined. If it cannot be determined (e.g., the training set is not publicly listed), say so explicitly. | The validation script documents the overlap status. |
| B3-24 | The baseline for comparison is per-residue SASA (solvent-accessible surface area) | The validation script computes SASA via `mdtraj.shrake_rupley` and reports the baseline AUC. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| B3-1 to B3-17 | (filled) | (filled) |
| B3-18 | (filled) | (filled) |
| B3-19 to B3-24 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed. The B3 effort requires:

1. Dockerfile changes to add the `pocketminer_env` conda env
   with `tensorflow==2.15.0`, `numpy==1.26.4`, `mdtraj==1.11.1`.
2. Cloning PocketMiner and AE-PocketMiner repos at the pinned
   commits.
3. Applying the `tf.keras.optimizers.legacy.Adam` patch.
4. Downloading PocketMiner weights and recording the
   checksum.
5. Downloading the CryptoBench test split (size TBD; ask if
   > 2 GB).
6. Writing the PocketMiner and AE-PocketMiner wrappers as
   subprocess calls.
7. Running the validation: pooled AUC > 0.5 with Mann-Whitney
   p < 0.05 on >= 10 test proteins.

Given the complexity (separate conda env, ~1-2 GB of model
weights + CryptoBench data, and the pooled-AUC validation),
this is a **multi-day effort** that should be done in a
separate follow-up turn with the full image rebuild.

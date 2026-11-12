# Part 0a — Installed versions vs target list

Image: `alloagent-dev:v4` (sha256: `a2005637d27d3a0a31974c023235a65558613a4375f25e858ba64377a199fc49`)
Image ID (short): `a2005637d27d`
Base image digest: `sha256:f752860f77bd417aa4db35be3d2e906fdb740fb80f40755ed651fff9e8873aad`
Build args: `GIT_COMMIT=4cb944d GIT_BRANCH=alloagent`
Build log: `build_logs/v4_stdout.log` (rebuild after layered Dockerfile + 1a/1b commits)
Lock files: `locks/conda-lock.yml`, `locks/pip-requirements.txt`
Container test command: `docker run --rm --env-file .env.test -e REQUIRE_REAL_DATA=1 -e RUN_REAL_NETWORK=1 alloagent-dev:v4 /opt/conda/envs/alloagent_e1/bin/python -m pytest /workspace/tests/ --no-header -q -p no:cacheprovider`

Note: the build was switched from `alloagent-dev:phase1` (the previous
single image for both arms) to a layered multi-stage build with two
targets: `dev` (bind-mount friendly, for day-to-day work) and `eval`
(same base but the full repo COPY'd in, for the final evaluation image).
The `alloagent-dev:v4` tag is the `dev` target; the `eval` target
produces a digest-pinned image recorded in
`docs/0a_single_image.md`. See `docs/dev_container.md` for the full
build/run/test commands and the secrets-hygiene policy.

## Verdict per package

| Target | Installed | Source | Verdict |
|---|---|---|---|
| numpy 2.4.6 | **2.3.5** | conda-forge | CLOSE (one minor below; 2.4.6 not available on conda-forge at build time) |
| pandas 3.0.5 | **3.0.6** | conda-forge | CLOSE (one patch above; 3.0.5 not resolvable on conda-forge) |
| scipy 1.17.1 | **1.17.1** | conda-forge | **EXACT** |
| scikit-learn 1.9.1 | **1.9.1** | conda-forge | **EXACT** |
| torch 2.4.1+cpu | **2.4.1+cpu** | pip (PyTorch CPU index) | **EXACT** |
| openai 2.54.0 | **2.53.0** | conda-forge | CLOSE (one patch below; 2.54.0 not available on conda-forge at build time) |
| langchain_core 0.3.86 | **0.3.86** | pip | **EXACT** |
| langchain_openai 0.3.35 | **0.3.35** | pip | **EXACT** |
| langgraph 0.3.18 | **0.3.18** | pip | **EXACT** |
| pydantic 2.13.5 | **2.14.0** | conda-forge | CLOSE (one minor above; 2.13.5 not available on conda-forge) |
| biopython 1.85 | **1.88** | conda-forge | CLOSE (3 patches above) |
| requests 2.34.2 | **2.34.2** | conda-forge | **EXACT** |
| prody 2.6.1 | **2.6.1** | conda-forge | **EXACT** |
| biotite 1.6.0 | **1.6.0** | conda-forge | **EXACT** |
| networkx 3.6.1 | **3.6.1** | conda-forge | **EXACT** |
| vina 1.2.7 | **1.2.7** | pip | **EXACT** |
| meeko 0.8.0 | **0.8.0** | pip | **EXACT** |

## CLOSE packages — pinned vs installed

The 5 target packages that are not exact are listed below with the
exact pin location (lock-file line) and the installed version
(verified in image `a2005637d27d` via `pip list` and `mamba list`).

| # | Package | Target | Installed | Lock-file pin | Source channel | Delta |
|---|---|---|---|---|---|---|
| 1 | numpy | 2.4.6 | 2.3.5 | `locks/conda-lock.yml:53` (`numpy=2.3.5`) + `locks/pip-requirements.txt:68` (wheel `numpy-2.3.5-…`) | conda-forge | -1 minor (2.4.6 not published on conda-forge at build time) |
| 2 | pandas | 3.0.5 | 3.0.6 | `locks/conda-lock.yml:56` (`pandas=3.0.6`) | conda-forge | +1 patch (3.0.5 not resolvable on conda-forge; numpy 2.3.5 pins the pandas ABI) |
| 3 | openai | 2.54.0 | 2.53.0 | `locks/conda-lock.yml:54` (`openai=2.53.0`) | conda-forge | -1 patch (2.54.0 not available on conda-forge at build time) |
| 4 | pydantic | 2.13.5 | 2.14.0 | `locks/conda-lock.yml:59` (`pydantic=2.14.0`) | conda-forge | +1 minor (2.13.5 not available on conda-forge; 2.14.0 is the closest resolvable) |
| 5 | biopython | 1.85 | 1.88 | `locks/conda-lock.yml:10` (`biopython=1.88`) | conda-forge | +3 patches (1.85 not resolvable on conda-forge; 1.88 is the closest resolvable) |

All 5 CLOSE packages are conda-forge packages where the target version
is not resolvable on the channel. The deltas are within one minor
(numpy, pydantic) or a few patches (pandas, openai, biopython). The
downstream tools (T6 ProDy, T7 Biotite + NetworkX, B2 Meeko + RDKit,
B3 pocketminer_env) all work with these versions.

## Summary

- **12 / 17** packages match the target **exactly**
- **5 / 17** are **close** (within a few patches; target not resolvable on conda-forge at build time)
- **0 / 17** are **missing** (all 5 previously-missing packages — torch, prody, biotite, vina, meeko — are now installed)
- **0 / 17** are **wrong** (langgraph is pinned to 0.3.18 exactly; was 0.3.34 before the follow-up fix)

## Verification commands (raw, trimmed)

```bash
docker run --rm alloagent-dev:v4 /opt/conda/envs/alloagent_e1/bin/pip list
# Returns a full list; the rows relevant to this report are reproduced
# verbatim in `docs/0a_installed_versions.md` table above.

docker run --rm alloagent-dev:v4 /opt/conda/bin/mamba list -n alloagent_e1
# Cross-check conda-forge channel vs pip; see build_logs/mamba_list_v4.txt
# (captured from image a2005637d27d on 2026-10-14).

docker run --rm alloagent-dev:v4 grep -n "ALLOAGENT_IMAGE_ID" /workspace/biomni/agent/a1.py
# 2039:            image_id = os.environ.get("ALLOAGENT_IMAGE_ID", "unknown")
```

## Notes

1. `numpy 2.3.5` is one minor below the target `2.4.6`. Conda-forge has
   not published 2.4.6 as of the image build time. The downstream
   dependencies (pandas, scipy, scikit-learn, ProDy, Biotite, NetworkX,
   RDKit, Meeko) all work with 2.3.5.
2. `pydantic 2.14.0` is one minor above `2.13.5`. The brief lists
   2.13.5 as the target; 2.14.0 is the closest resolvable on
   conda-forge and is the version in `locks/pip-requirements.txt`.
3. `biopython 1.88` is 3 patches above the target `1.85`. Conda-forge
   does not carry 1.85; 1.88 is the version in `locks/conda-lock.yml:10`.
   All T2/T7 tests use the 1.88 build. (In `pocketminer_env` the
   biopython is also 1.88; PocketMiner's `Bio.PDB` import works fine
   on 1.88.)
4. The Dockerfile `useradd` step is before the `COPY --chown` step
   with `--no-log-init` to remove the Windows-host mail-spool hang.
   The image's `/workspace` is owned by `appuser` (uid 997).
5. The image is now a **layered multi-stage build** (commits
   `4cb944d` + `db8b724`): `base-system`, `base-deps`,
   `base-binaries`, `base-pocketminer`, `base-appuser`, `dev`,
   `eval`. Heavy layers (OS packages, conda envs, fpocket, P2Rank,
   pocketminer_env, PocketMiner + AE-PocketMiner clones) are cached
   separately from the repo's source. Source edits do not rebuild
   layers 1-5; only the thin top layer (`dev` or `eval`) re-runs
   `pip install -e`. The build is digest-pinned
   (`condaforge/miniforge3@sha256:f752860f…`) for reproducibility.
6. The B3 pocketminer_env was created at build time with
   `tensorflow=2.15.0`, `numpy=1.26.4`, `mdtraj=1.11.1`, plus
   `tqdm`, `pyyaml`, `biopython`, `h5py` (deps PocketMiner and
   AE-PocketMiner import). The legacy-Adam shim is applied via a
   build-time Python patch (`docker/patches/apply_legacy_adam.py`)
   that rewrites `tf.keras.optimizers.Adam` →
   `tf.keras.optimizers.legacy.Adam` in every `.py` file under
   `/opt/pocketminer` and `/opt/ae-pocketminer` (20 files
   changed, 23 replacements). The previous runtime `sed` patch
   in the container did not persist across runs.
7. Image evolution:
   - `e3b3c0d…` (first build; 5 packages missing)
   - `2f46459…` (useradd fix; fpocket + P2Rank + JDK 17)
   - `6ed43a4…` (COPY --chown fix)
   - `0418fe07e168` (lock-file follow-up; 0 missing of 17 targets)
   - `1a9483fb9c03` (+ rdkit, gemmi, pocketminer_env; meeko fixed)
   - **`a2005637d27d`** (commit 4cb944d layered build; commit
     db8b724 deps + patch file; current image for the 1a/1b/2/3/4/5
     work; verified OK as appuser with `vina=1.2.7 meeko=0.8.0
     rdkit=2024.09.6 gemmi=0.7.5`)
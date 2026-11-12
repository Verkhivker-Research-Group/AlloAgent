# Development container workflow

This document describes how to build and run the AlloAgent-v2
container for **development** (bind mount, no rebuild on source
edits) and **evaluation** (clean image, repo copied in).

The container has two conda envs:

- `alloagent_e1` — the main env (Python 3.11, rdkit, gemmi, meeko,
  vina, prody, biotite, networkx, the langchain stack). Used by
  every test in `tests/` and by all `biomni/tool/*.py` wrappers.
- `pocketminer_env` — a separate env (Python 3.11, tensorflow 2.15,
  numpy 1.26.4, mdtraj 1.11.1, tqdm, pyyaml, biopython) with cloned
  PocketMiner (Mickdub/gvp@pocket_pred) and AE-PocketMiner
  (bowman-lab/ae-pocketminer). Used only by the B3
  `pocketminer_score` and `ae_pocketminer_score` wrappers.

## Layering

The Dockerfile (`Dockerfile`) is structured in layers so that
heavy, rarely-changing parts of the image are cached and rebuilt
only when a dependency changes; source edits to the repo only
invalidate the top layer.

| Stage | Contents | Rebuild trigger |
|---|---|---|
| `base-system` | OS packages (git, build-essential, JDK 17, curl, patch) | OS image upgrade |
| `base-deps` | `alloagent_e1` conda env + langchain / pip deps | dependency upgrade |
| `base-binaries` | `fpocket` (built from source) + `P2Rank` (extracted) | binary version bump |
| `base-pocketminer` | `pocketminer_env` + PocketMiner / AE-PocketMiner clones + the build-time `tf.keras.optimizers.legacy.Adam` patch | repo commit bump |
| `base-appuser` | `appuser` (uid 997) creation, smoke import tests | none (cheap) |
| `dev` | `COPY` of `pyproject.toml` + source dirs into `/workspace`, `pip install -e /workspace` | source edit (re-runs only `pip install -e`) |
| `eval` | `COPY . /workspace`, `pip install -e /workspace` (full repo) | source edit (rebuilds full top layer) |

## Build commands

### Development image (bind-mount friendly)

The `dev` target creates an image where `/workspace` is **owned by
`appuser`** and the package metadata is installed (`pip install
-e`). The actual repo is bind-mounted at run time, so source edits
do not require a rebuild — only dependency changes do.

```bash
# from the repo root
docker build \
    --target dev \
    --build-arg GIT_COMMIT="$(git rev-parse HEAD)" \
    --build-arg GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)" \
    -t alloagent-dev:latest \
    .
```

Run a shell in the dev image with the repo bind-mounted:

```bash
# .env.test is a temporary env-file outside the repo, see "Secrets
# hygiene" below. It is deleted after the test run.
docker run --rm -it \
    --env-file .env.test \
    -v "$(pwd):/workspace" \
    -w /workspace \
    alloagent-dev:latest \
    bash
```

Inside the container, the active env is `alloagent_e1`:

```bash
# verify
python -c "import vina, meeko, rdkit, gemmi, torch; print('OK')"
python -c "import biomni; print('OK')"
# switch to pocketminer_env for B3 work
conda activate pocketminer_env
python -c "import tensorflow as tf; print(tf.__version__)"  # 2.15.0
```

### Evaluation image (clean, digest-pinned base)

The `eval` target builds the same base layers as `dev` but copies
the WHOLE repo in. The image ID is recorded in
`docs/0a_installed_versions.md`.

```bash
docker build \
    --target eval \
    --build-arg GIT_COMMIT="$(git rev-parse HEAD)" \
    --build-arg GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)" \
    -t alloagent-eval:latest \
    .

# record the image ID (full and short)
docker images --format '{{.ID}} {{.Repository}}:{{.Tag}}' \
    | grep alloagent-eval:latest
```

## Test commands

The test runner is always `pytest tests/ --no-header -q` under
`alloagent_e1` with `REQUIRE_REAL_DATA=1` and `RUN_REAL_NETWORK=1`.

```bash
# Development: bind-mounted source
docker run --rm \
    --env-file .env.test \
    -v "$(pwd):/workspace" \
    -w /workspace \
    -e REQUIRE_REAL_DATA=1 \
    -e RUN_REAL_NETWORK=1 \
    alloagent-dev:latest \
    /opt/conda/envs/alloagent_e1/bin/python -m pytest tests/ \
        --no-header -q -p no:cacheprovider

# Evaluation: image contains the repo
docker run --rm \
    --env-file .env.test \
    -e REQUIRE_REAL_DATA=1 \
    -e RUN_REAL_NETWORK=1 \
    alloagent-eval:latest \
    /opt/conda/envs/alloagent_e1/bin/python -m pytest tests/ \
        --no-header -q -p no:cacheprovider
```

### Baseline arm

The baseline arm uses the **same image** (no rebuild between
arms). The pytest path is unchanged; the difference is only the
repo state (the `alloagent` branch has the new wrappers, the
`baseline` branch does not).

```bash
# Switch to baseline
git checkout baseline
docker run --rm \
    --env-file .env.test \
    -v "$(pwd):/workspace" \
    -w /workspace \
    -e REQUIRE_REAL_DATA=1 \
    -e RUN_REAL_NETWORK=1 \
    alloagent-dev:latest \
    /opt/conda/envs/alloagent_e1/bin/python -m pytest tests/ \
        --no-header -q -p no:cacheprovider
```

## Build-time patch

The PocketMiner and AE-PocketMiner repos use
`tf.keras.optimizers.Adam`, which is incompatible with their
TF 1.x checkpoint format under TF 2.15. The fix is a single
build-time patch (`docker/patches/apply_legacy_adam.py`) that
rewrites the token to `tf.keras.optimizers.legacy.Adam` in every
`.py` file under the two clones. The patch is applied in the
`base-pocketminer` stage of the Dockerfile:

```dockerfile
COPY docker/patches/apply_legacy_adam.py /tmp/apply_legacy_adam.py
RUN /opt/conda/envs/pocketminer_env/bin/python /tmp/apply_legacy_adam.py \
        /opt/pocketminer /opt/ae-pocketminer
```

The script is idempotent: re-running it on already-patched files
is a no-op.

## Secrets hygiene

**Never mount a `.env` file** into the container. The host
`Biolab/.env` (or any other) is **not** mounted; the container
receives only the variables it actually needs via a temporary
`--env-file` created outside the repo and deleted after the run.

To create a temporary env file for a test run:

```bash
# .env.test is created outside the repo (in $HOME or /tmp),
# populated with only the variables the tests read, and deleted
# after the run. It is gitignored.
cat > /tmp/.env.test <<EOF
MINIMAX_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
EOF
chmod 600 /tmp/.env.test

docker run --rm --env-file /tmp/.env.test ... alloagent-dev:latest bash

# delete the file
rm -f /tmp/.env.test
```

See `docs/0c_secrets_hygiene.md` for the full policy.

## Image ID recording

The final evaluation image's full sha256 is recorded in
`docs/0a_installed_versions.md` and the per-tool verdict table
in `../alloagent_private/docs/3_report.md`. The image ID is also written into
`/workspace/build_info.json` at build time (via the
`ALLOAGENT_IMAGE_ID` env var) so the per-run JSON records
include the image ID for forensic comparison.

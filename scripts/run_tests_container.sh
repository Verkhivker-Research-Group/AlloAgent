#!/usr/bin/env bash
# scripts/run_tests_container.sh
#
# Run the full AlloAgent-v2 test suite inside the Docker image
# with the Biolab data files bind-mounted read-only and a
# temporary --env-file (created outside the repo, deleted
# afterward) carrying ONLY the MINIMAX_* and BIOMNI_* variable
# names (and any alias the tests need) from the host file at
# $ALLOAGENT_ENV_SOURCE (a path to the Biolab .env outside
# the repo).
#
# No .env, .omo, or .env.extracted is mounted. The .env file is
# read from the host (NOT mounted) and its MINIMAX_*/BIOMNI_*
# variables are copied into a temp file that is then passed
# via --env-file and deleted at exit.
#
# If RUN_REAL_NETWORK=1 and MINIMAX_API_KEY is absent from the
# extracted variables, the script fails with a clear message
# BEFORE starting the container.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_BIOLAB="C:<HOME>/Documents/CPSC/Biolab"
BIOLAB_UNIX="/c<HOME>/Documents/CPSC/Biolab"
IMAGE="${ALLOAGENT_IMAGE:-alloagent-dev:v4}"

if [[ -z "${ALLOAGENT_ENV_SOURCE:-}" ]]; then
    echo "ERROR: ALLOAGENT_ENV_SOURCE is not set." >&2
    echo "       Set it to the absolute path of the host .env file" >&2
    echo "       (e.g., C:<HOME>/Documents/CPSC/Biolab/.env)." >&2
    echo "       The script reads MINIMAX_* and BIOMNI_* from that file" >&2
    echo "       and passes them via a temporary --env-file." >&2
    exit 2
fi

# Convert the path for the existence check: bash on Windows
# may not understand backslash paths or "C:/" paths, so use
# Python to check (Docker itself handles the path translation
# for the mount and --env-file at run time).
HOST_ENV_SOURCE="$ALLOAGENT_ENV_SOURCE"
if ! python -c "import os,sys; sys.exit(0 if os.path.isfile(sys.argv[1]) else 1)" "$HOST_ENV_SOURCE"; then
    echo "ERROR: ALLOAGENT_ENV_SOURCE file not found: $HOST_ENV_SOURCE" >&2
    exit 2
fi

# Create the temporary env-file with chmod 600. Copy only
# variable names starting with MINIMAX_ or BIOMNI_ (plus any
# alias explicitly listed in TEST_ENV_ALIASES, comma-separated).
TEMP_ENV="$(mktemp -t alloagent_env.XXXXXX.env)"
chmod 600 "$TEMP_ENV"

cleanup() {
    if [[ -n "${TEMP_ENV:-}" && -f "${TEMP_ENV}" ]]; then
        rm -f "$TEMP_ENV"
    fi
}
trap cleanup EXIT

ALIASES_REGEX="$(echo "${TEST_ENV_ALIASES:-}" | tr ',' '|' | sed 's/^|//;s/|$//')"

# Build a regex for allowed prefixes/aliases.
ALLOWED_REGEX='^(MINIMAX_|BIOMNI_)'
if [[ -n "$ALIASES_REGEX" ]]; then
    ALLOWED_REGEX="(${ALLOWED_REGEX}|${ALIASES_REGEX})"
fi

EXTRACTED_VARS=()
while IFS= read -r line; do
    # Skip blanks and comments.
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    # Match KEY=VALUE (no shell expansion in the source).
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        val="${BASH_REMATCH[2]}"
        # Strip surrounding quotes from val.
        val="${val%\"}"; val="${val#\"}"
        val="${val%\'}"; val="${val#\'}"
        if [[ "$key" =~ $ALLOWED_REGEX ]]; then
            echo "${key}=${val}" >> "$TEMP_ENV"
            EXTRACTED_VARS+=("$key")
        fi
    fi
done < "$ALLOAGENT_ENV_SOURCE"

# Sanity check: under RUN_REAL_NETWORK=1, MINIMAX_API_KEY
# must be present in the temp env-file.
if [[ "${RUN_REAL_NETWORK:-0}" == "1" ]]; then
    if ! grep -q '^MINIMAX_API_KEY=' "$TEMP_ENV"; then
        echo "ERROR: RUN_REAL_NETWORK=1 but MINIMAX_API_KEY is not" >&2
        echo "       present in $ALLOAGENT_ENV_SOURCE (or its name" >&2
        echo "       does not start with MINIMAX_/BIOMNI_)." >&2
        echo "       Extracted variables: ${EXTRACTED_VARS[*]:-<none>}" >&2
        exit 3
    fi
fi

echo "Extracted $(echo "${#EXTRACTED_VARS[@]}") variable(s) from $ALLOAGENT_ENV_SOURCE:"
for v in "${EXTRACTED_VARS[@]}"; do echo "  - $v"; done

# Compute mount paths.
SCORED_RUNS_HOST="$BIOLAB_UNIX/eval_ablation/scoring/scored_runs.csv"
NULL_RUNS_HOST="$BIOLAB_UNIX/prep_reports/investigation/null_runs.csv"
RESULTS_HOST="$BIOLAB_UNIX/results"
BLOCKLIST_HOST="$BIOLAB_UNIX/prep_reports/benchmark_blocklist.tsv"
# Bio data files for T9 / T10 live verifications and crypto_bench / B3.
# - /data/alphamissense  : AlphaMissense TSV (T10 LIVE_TSV guard)
# - /data/clinvar        : ClinVar variant_summary.txt.gz (T9 local mode)
# - /data/cryptobench    : CryptoBench zip + json (B3 Step 2)
# - /data/chembl         : ChEMBL 37 tarball / unpacked SQLite (B1; the
#                          unpacked SQLite is not present in this session
#                          so the B1 live tests still fall through to the
#                          web-API fallback or skip, depending on the guard)
DATA_ALPHAMISSENSE_HOST="$BIOLAB_UNIX/../AlloAgent-v2/data/alphamissense"
DATA_CLINVAR_HOST="$BIOLAB_UNIX/../AlloAgent-v2/data/clinvar"
DATA_CRYPTOBENCH_HOST="$BIOLAB_UNIX/../AlloAgent-v2/data/cryptobench"
DATA_CHEMBL_HOST="$BIOLAB_UNIX/../AlloAgent-v2/data/chembl"
# Biolab data lake (BioLiP pickles, CovInDB). Read-only, no secrets.
BIOLAB_DATA_HOST="$BIOLAB_UNIX/data/biomni_data"

# The benchmark suite is optional: the benchmark folder can be deleted
# from the product tree without affecting the agent.
PYTEST_TARGETS="/workspace/tests/"
if [[ -d "${REPO_ROOT}/benchmark/tests" ]]; then
    PYTEST_TARGETS="${PYTEST_TARGETS} /workspace/benchmark/tests/"
fi

# Start a fresh container with the read-only data mounts and
# the temporary env-file. The container runs pytest in the
# foreground and is removed at exit.
docker run --rm \
    --name "alloagent-tests-$$" \
    --env-file "$TEMP_ENV" \
    -e "REQUIRE_REAL_DATA=1" \
    -e "RUN_REAL_NETWORK=${RUN_REAL_NETWORK:-1}" \
    -e "TMPDIR=/tmp" \
    -e "HOME=/tmp" \
    -v "${REPO_ROOT}:/workspace" \
    -v "${SCORED_RUNS_HOST}:/Biolab/eval_ablation/scoring/scored_runs.csv:ro" \
    -v "${NULL_RUNS_HOST}:/Biolab/prep_reports/investigation/null_runs.csv:ro" \
    -v "${RESULTS_HOST}:/Biolab/results:ro" \
    -v "${BLOCKLIST_HOST}:/workspace/Biolab/prep_reports/benchmark_blocklist.tsv:ro" \
    -v "${DATA_ALPHAMISSENSE_HOST}:/data/alphamissense:ro" \
    -v "${DATA_CLINVAR_HOST}:/data/clinvar:ro" \
    -v "${DATA_CRYPTOBENCH_HOST}:/data/cryptobench:ro" \
    -v "${DATA_CHEMBL_HOST}:/data/chembl:ro" \
    -v "${BIOLAB_DATA_HOST}:/biolab_data:ro" \
    "${IMAGE}" \
    /opt/conda/envs/alloagent_e1/bin/python -m pytest ${PYTEST_TARGETS} \
        --no-header -q -p no:cacheprovider \
        "$@"

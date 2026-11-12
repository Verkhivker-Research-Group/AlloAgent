#!/bin/sh
# The run commands of the capability benchmark.  WRITTEN, NOT RUN.
#
# 9 prompts x 3 repeats x 2 arms = 54 runs, plus 3 prompts x 3 repeats x 2 arms
# = 18 restricted runs.
#
# TWO THINGS MUST BE DONE BEFORE THE RUNS
# 1. The two pending AlloAgent fixes must be committed first:
#      (a) the fpocket residues (the item wants the residue counts of the
#          reference output), and
#      (b) the ClinVar id form is NOT needed on this branch: the X06 id item
#          accepts the Variation IDs or the Allele IDs, and the tool returns the
#          Allele ID.  The Variation-ID variant of the tool lives on the branch
#          post-paper/clinvar-ids (commit 4520efa8b81c579e56b912a6ef2ae02ff834d868).
#    Record the commit hash of each of them here:
#      the ClinVar fix commit      : 4520efa8b81c579e56b912a6ef2ae02ff834d868
#      the fpocket residues fix    : 075a0db3958638df5da935b6ab24936c3aeec9ea
# 2. The commit hash used for each arm must be recorded.  The AlloAgent arm runs
#    the code of the launch checkout (record it below); the baseline arm runs
#    the code of its own worktree, which is the baseline branch at the commit
#    recorded below.
#
# The X prompts live in their own registry (benchmark/capability/), so the
# launch checkout needs the capability prompt table.  benchmark/run_capability_launch.py
# builds that checkout in a temporary directory (a copy of the launch checkout's
# benchmark/ with the X prompts added) and never writes into the repository.

REPO=/c<HOME>/Documents/CPSC/AlloAgent-v2
LAUNCH_CHECKOUT=/c<HOME>/AppData/Local/Temp/opencode/launch_checkout
BASELINE_WORKSPACE=/c<HOME>/AppData/Local/Temp/opencode/baseline_wt
DATA_ROOT=$REPO/data
ENV_SOURCE=/c<HOME>/Documents/CPSC/Biolab/.env.extracted
IMAGE=alloagent-eval:v6
IMAGE_DIGEST=sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07
# the driver derives the benchmark dir digest itself and passes it to the
# harness; it takes no --expected-sha256 argument.

# ---- the main scenario: 54 runs (the driver runs both arms)
python "$REPO/benchmark/run_capability_launch.py" \
    --scenario main \
    --run-list "$REPO/benchmark/capability/run_list_main.json" \
    --launch-tag capability-2026-11-07-main \
    --launch-checkout "$REPO" \
    --baseline-workspace "$BASELINE_WORKSPACE" \
    --run-dir "/c<HOME>/AppData/Local/Temp/opencode/capability_runs_main" \
    --data-root "$DATA_ROOT" \
    --structure-cache "$DATA_ROOT/structures_cache" \
    --env-source "$ENV_SOURCE" \
    --image "$IMAGE" --image-digest "$IMAGE_DIGEST" \
    --parallel 4 --repeats 3 --seed 20261027

# ---- the restricted-egress repeat: 18 runs (X02, X06, X07)
python "$REPO/benchmark/run_capability_launch.py" \
    --scenario restricted \
    --run-list "$REPO/benchmark/capability/run_list_restricted.json" \
    --launch-tag capability-2026-11-07-restricted \
    --launch-checkout "$REPO" \
    --baseline-workspace "$BASELINE_WORKSPACE" \
    --run-dir "/c<HOME>/AppData/Local/Temp/opencode/capability_runs_restricted" \
    --data-root "$DATA_ROOT" \
    --structure-cache "$DATA_ROOT/structures_cache" \
    --env-source "$ENV_SOURCE" \
    --image "$IMAGE" --image-digest "$IMAGE_DIGEST" \
    --parallel 4 --repeats 3 --seed 20261027

# ---- the commits actually used
#   the AlloAgent arm commit : the commit of the repository the launch checkout is
#                              built from, i.e. the HEAD at the moment the runs are
#                              launched (record it here when they start)
#   the baseline arm commit  : 8a56d049e2cfd000f26554e27db6fbcba9946553
#                              (the baseline worktree, branch `baseline`)

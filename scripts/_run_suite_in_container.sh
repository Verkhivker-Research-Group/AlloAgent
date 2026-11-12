#!/bin/sh
# Run one arm's test suite in the container and write the log INSIDE the
# bind mount, so the log survives even if the docker client is killed.
LOG="$1"
shift
mkdir -p "$(dirname "$LOG")"
echo "suite start $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOG"
/opt/conda/envs/alloagent_e1/bin/python -m pytest /workspace/tests/ \
    --no-header -q -p no:cacheprovider "$@" >> "$LOG" 2>&1
rc=$?
echo "suite exit=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
exit $rc

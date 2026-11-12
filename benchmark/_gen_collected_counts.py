"""Regenerate the collection pins of the benchmark suite.

Run this after adding or removing a test in benchmark/tests/, then commit
the updated benchmark/collected_counts.txt and
benchmark/collected_nodeids.txt alongside the test change.

    python benchmark/_gen_collected_counts.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BENCHMARK = REPO / "benchmark"
TARGET = "benchmark/tests"

COUNTS_HEADER = """# benchmark/collected_counts.txt
#
# Pinned per-file and total collected test counts for the benchmark
# suite. The guard test (benchmark/tests/test_benchmark_collect_count_guard.py)
# reads this file and compares against the live `pytest --collect-only`
# output. Any decrease or increase that is NOT accompanied by an
# update to this file in the same commit causes the guard to FAIL.
#
# Format:
#   total: N
#   benchmark/tests/<file>.py: N
#   benchmark/tests/<file>.py: N
#   ...
"""

NODEIDS_HEADER = """# benchmark/collected_nodeids.txt
#
# Sorted pytest node IDs for the benchmark suite. The guard test
# (benchmark/tests/test_benchmark_collect_count_guard.py) reads this file and
# compares against the live `pytest --collect-only` output. Any removal
# or addition of a test node ID will cause the guard to FAIL.
#
"""


def collect() -> tuple[Counter, set[str]]:
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", TARGET, "--collect-only", "-q",
         "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True, env=env, cwd=str(REPO))
    if result.returncode not in (0, 5):
        raise SystemExit(
            f"pytest collect-only failed (rc={result.returncode}): "
            f"{result.stdout[-2000:]} {result.stderr[-2000:]}")
    counts: Counter = Counter()
    nodeids: set[str] = set()
    prefix = TARGET + "/"
    for line in result.stdout.splitlines():
        line = line.strip()
        if "::" not in line or line.startswith(("ERROR", "FAILED")):
            continue
        if not line.startswith(prefix):
            continue
        counts[line.split("::", 1)[0]] += 1
        nodeids.add(line)
    return counts, nodeids


def main() -> int:
    counts, nodeids = collect()
    lines = [COUNTS_HEADER.rstrip("\n"), "", f"total: {sum(counts.values())}"]
    for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"{name}: {count}")
    (BENCHMARK / "collected_counts.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    lines = [NODEIDS_HEADER.rstrip("\n"), ""] + sorted(nodeids)
    (BENCHMARK / "collected_nodeids.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(f"benchmark/tests/: {len(counts)} files, {sum(counts.values())} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

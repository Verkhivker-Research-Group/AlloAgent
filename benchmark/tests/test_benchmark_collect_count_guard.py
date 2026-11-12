"""Guard test: the collected test counts and node IDs of the benchmark
suite must match benchmark/collected_counts.txt and
benchmark/collected_nodeids.txt.

The pinned counts and node IDs are the authoritative reference. Any
decrease or increase that is NOT accompanied by an update to these files
in the same commit causes this guard to FAIL. The commit message must
list the added and removed test node IDs.

This guard lives inside benchmark/ so that the benchmark folder keeps its
own guard with it: the agent suite has its own, in
tests/test_collect_count_guard.py.
"""
from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BENCHMARK = REPO / "benchmark"
TARGET = "benchmark/tests"
COUNTS_FILE = BENCHMARK / "collected_counts.txt"
NODEIDS_FILE = BENCHMARK / "collected_nodeids.txt"


def _parse_counts_file(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        try:
            out[key] = int(val)
        except ValueError:
            continue
    return out


def _collect_counts() -> Counter:
    """The live per-file collected counts for benchmark/tests/."""
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", TARGET,
            "--collect-only", "-q", "--no-header",
        ],
        capture_output=True, text=True, timeout=180, env=env,
        cwd=str(REPO),
    )
    if r.returncode not in (0, 5):
        raise RuntimeError(
            f"pytest collect-only failed (rc={r.returncode}): "
            f"stderr={r.stderr[:200]}"
        )
    counts: Counter = Counter()
    for line in r.stdout.splitlines():
        line = line.strip()
        if "::" not in line:
            continue
        if line.startswith("ERROR") or line.startswith("FAILED"):
            continue
        file_path = line.split("::", 1)[0]
        if file_path.startswith(TARGET + "/"):
            counts[file_path] += 1
    return counts


def test_collected_counts_match_pinned_file():
    """Live collected counts must exactly match benchmark/collected_counts.txt."""
    assert COUNTS_FILE.is_file(), (
        f"benchmark/collected_counts.txt not found at {COUNTS_FILE}. "
        f"Create it (e.g., by running benchmark/_gen_collected_counts.py) "
        f"and commit it before adding/removing tests."
    )
    pinned = _parse_counts_file(COUNTS_FILE)
    pinned_total = pinned.pop("total", None)
    assert pinned_total is not None, (
        f"benchmark/collected_counts.txt is missing the 'total:' line"
    )
    live = _collect_counts()
    live_total = sum(live.values())
    assert live_total == pinned_total, (
        f"total collected count mismatch: live={live_total}, "
        f"pinned={pinned_total}. If this is intentional, "
        f"regenerate benchmark/collected_counts.txt and commit the "
        f"updated file in the same commit as the test change; "
        f"the commit message must list added and removed test node IDs."
    )
    added_files = set(live) - set(pinned)
    assert not added_files, (
        f"new test files not in benchmark/collected_counts.txt: "
        f"{sorted(added_files)}. Update the file in the same commit."
    )
    removed_files = set(pinned) - set(live)
    assert not removed_files, (
        f"test files in benchmark/collected_counts.txt but not found live: "
        f"{sorted(removed_files)}. Update the file in the same commit."
    )
    mismatches: list[str] = []
    for name, expected_n in pinned.items():
        actual_n = live.get(name, 0)
        if actual_n != expected_n:
            mismatches.append(f"  {name}: live={actual_n}, pinned={expected_n}")
    assert not mismatches, (
        "per-file collected count mismatches (live vs pinned):\n"
        + "\n".join(mismatches)
        + "\nRegenerate benchmark/collected_counts.txt and commit the "
        "updated file in the same commit as the test change."
    )


def _parse_nodeids_file(path: Path) -> set[str]:
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "::" in line:
            out.add(line)
    return out


def _collect_nodeids() -> set[str]:
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", TARGET,
            "--collect-only", "-q", "--no-header",
        ],
        capture_output=True, text=True, timeout=180, env=env,
        cwd=str(REPO),
    )
    if r.returncode not in (0, 5):
        raise RuntimeError(
            f"pytest collect-only failed (rc={r.returncode}): "
            f"stderr={r.stderr[:200]}"
        )
    out: set[str] = set()
    for line in r.stdout.splitlines():
        line = line.strip()
        if "::" not in line:
            continue
        if line.startswith("ERROR") or line.startswith("FAILED"):
            continue
        if line.startswith(TARGET + "/"):
            out.add(line)
    return out


def test_collected_nodeids_match_pinned_file():
    """Live collected node IDs must exactly match
    benchmark/collected_nodeids.txt."""
    assert NODEIDS_FILE.is_file(), (
        f"benchmark/collected_nodeids.txt not found at {NODEIDS_FILE}. "
        f"Create it by running benchmark/_gen_collected_counts.py "
        f"and commit it alongside benchmark/collected_counts.txt."
    )
    pinned = _parse_nodeids_file(NODEIDS_FILE)
    live = _collect_nodeids()
    added = live - pinned
    removed = pinned - live
    if added or removed:
        lines = []
        if added:
            lines.append(f"ADDED ({len(added)}):")
            for nid in sorted(added):
                lines.append(f"  + {nid}")
        if removed:
            lines.append(f"REMOVED ({len(removed)}):")
            for nid in sorted(removed):
                lines.append(f"  - {nid}")
        raise AssertionError(
            "collected node ID set differs from "
            "benchmark/collected_nodeids.txt.\n" + "\n".join(lines)
            + "\nRegenerate benchmark/collected_nodeids.txt (and "
            "benchmark/collected_counts.txt) by running "
            "benchmark/_gen_collected_counts.py and commit the updated "
            "files in the same commit as the test change."
        )

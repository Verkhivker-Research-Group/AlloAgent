"""Guard test: the collected test counts and node IDs must
match docs/collected_counts.txt and docs/collected_nodeids.txt.

The pinned counts and node IDs are the authoritative reference.
Any decrease or increase that is NOT accompanied by an update
to these files in the same commit causes this guard to FAIL.
The commit message must list the added and removed test node
IDs.

Two historical guards remain as separate tests for the
Biolab-data check:
  - test_parser_upstream_compare_collects_at_least_233
  - test_parser_fix_collects_at_least_124

These catch the specific regression where the Biolab data
is not bind-mounted into the container, which drops the
parametrized case counts below the known minimums.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
COUNTS_FILE = REPO / "docs" / "collected_counts.txt"
NODEIDS_FILE = REPO / "docs" / "collected_nodeids.txt"


def _parse_counts_file(path: Path) -> dict[str, int]:
    """Read docs/collected_counts.txt and return
    {file_path: count, '__total__': total}."""
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
            n = int(val)
        except ValueError:
            continue
        if key == "total":
            out["__total__"] = n
        else:
            out[key] = n
    return out


def _collect_counts() -> Counter:
    """Return live per-file collected counts for tests/."""
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(REPO / "tests"),
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
        if file_path.startswith("tests/"):
            counts[file_path] += 1
    return counts


def test_collected_counts_match_pinned_file():
    """Live collected counts must exactly match docs/collected_counts.txt.
    Any difference (decrease or increase) is a FAIL. When you add
    or remove tests, update docs/collected_counts.txt in the same
    commit AND list the added/removed test node IDs in the commit
    message."""
    assert COUNTS_FILE.is_file(), (
        f"docs/collected_counts.txt not found at {COUNTS_FILE}. "
        f"Create it (e.g., by running build_logs/_gen_collected_counts.py) "
        f"and commit it before adding/removing tests."
    )
    pinned = _parse_counts_file(COUNTS_FILE)
    assert "__total__" in pinned, (
        f"docs/collected_counts.txt is missing the 'total:' line"
    )
    live = _collect_counts()
    live_total = sum(live.values())
    expected_total = pinned["__total__"]
    assert live_total == expected_total, (
        f"total collected count mismatch: live={live_total}, "
        f"pinned={expected_total}. If this is intentional, "
        f"regenerate docs/collected_counts.txt and commit the "
        f"updated file in the same commit as the test change; "
        f"the commit message must list added and removed test node IDs."
    )
    # Per-file check
    pinned_files = {k: v for k, v in pinned.items() if k != "__total__"}
    live_files = dict(live)
    # Check for files in live but not pinned
    added_files = set(live_files) - set(pinned_files)
    assert not added_files, (
        f"new test files not in docs/collected_counts.txt: "
        f"{sorted(added_files)}. Update the file in the same commit."
    )
    # Check for files in pinned but not live
    removed_files = set(pinned_files) - set(live_files)
    assert not removed_files, (
        f"test files in docs/collected_counts.txt but not found live: "
        f"{sorted(removed_files)}. Update the file in the same commit."
    )
    # Check per-file counts
    mismatches: list[str] = []
    for f, expected_n in pinned_files.items():
        actual_n = live_files.get(f, 0)
        if actual_n != expected_n:
            mismatches.append(
                f"  {f}: live={actual_n}, pinned={expected_n}"
            )
    assert not mismatches, (
        f"per-file collected count mismatches (live vs pinned):\n"
        + "\n".join(mismatches)
        + "\nRegenerate docs/collected_counts.txt and commit the "
        "updated file in the same commit as the test change; the "
        "commit message must list added and removed test node IDs."
    )


def _parse_nodeids_file(path: Path) -> set[str]:
    """Read docs/collected_nodeids.txt and return the set of
    node IDs (one per line, ignoring comments and blanks)."""
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "::" in line:
            out.add(line)
    return out


def _collect_nodeids() -> set[str]:
    """Return the live set of collected node IDs for tests/."""
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(REPO / "tests"),
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
        if line.startswith("tests/"):
            out.add(line)
    return out


def test_collected_nodeids_match_pinned_file():
    """Live collected node IDs must exactly match
    docs/collected_nodeids.txt. Any removed or added node ID
    is a FAIL. When you add or remove tests, update both
    docs/collected_nodeids.txt and docs/collected_counts.txt
    in the same commit AND list the added and removed test
    node IDs in the commit message."""
    assert NODEIDS_FILE.is_file(), (
        f"docs/collected_nodeids.txt not found at {NODEIDS_FILE}. "
        f"Create it by running build_logs/_gen_collected_nodeids.py "
        f"and commit it alongside docs/collected_counts.txt."
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
        msg = "\n".join(lines)
        raise AssertionError(
            f"collected node ID set differs from docs/collected_nodeids.txt.\n"
            f"{msg}\n"
            f"Regenerate docs/collected_nodeids.txt (and "
            f"docs/collected_counts.txt) by running "
            f"build_logs/_gen_collected_nodeids.py and commit the updated "
            f"files in the same commit as the test change; the commit "
            f"message must list added and removed test node IDs."
        )


def _collect_count(test_file: str) -> int:
    """Return the number of tests collected by pytest for
    test_file, or -1 if the collection itself errored."""
    env = os.environ.copy()
    env.setdefault("REQUIRE_REAL_DATA", "1")
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(REPO / test_file),
            "--collect-only", "-q", "--no-header",
        ],
        capture_output=True, text=True, timeout=120, env=env,
        cwd=str(REPO),
    )
    if r.returncode not in (0, 5):
        return -1
    count = 0
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line or "<Module" in line or "<Function" in line or "<Coroutine" in line:
            continue
        if line.startswith("tests/"):
            count += 1
    return count


def test_parser_upstream_compare_collects_at_least_233():
    """test_parser_upstream_compare.py must collect >= 233
    parametrized cases. Below that, the Biolab data is not
    mounted (scored_runs.csv and/or results/)."""
    n = _collect_count("tests/test_parser_upstream_compare.py")
    assert n >= 233, (
        f"test_parser_upstream_compare.py collected only {n} tests; "
        f"expected >= 233. The Biolab data is likely not mounted: "
        f"scored_runs.csv and/or results/. See scripts/run_tests_container.ps1 "
        f"and scripts/run_tests_container.sh for the required mounts."
    )


def test_parser_fix_collects_at_least_124():
    """test_parser_fix.py must collect >= 124 parametrized
    cases. Below that, the Biolab data is not mounted (null_runs.csv
    and/or scored_runs.csv and/or results/)."""
    n = _collect_count("tests/test_parser_fix.py")
    assert n >= 124, (
        f"test_parser_fix.py collected only {n} tests; "
        f"expected >= 124. The Biolab data is likely not mounted: "
        f"null_runs.csv, scored_runs.csv, and/or results/. See "
        f"scripts/run_tests_container.ps1 and scripts/run_tests_container.sh "
        f"for the required mounts."
    )

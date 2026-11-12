"""Guard test: the criteria section of each criteria file
must not change after a test run.

The standing rule says: criteria are committed BEFORE a run
and never changed afterward; a wrong expectation may be
corrected only as a dated, evidence-backed note in the
criteria file (which is hashed EXCLUDING the note section).

This test reads docs/criteria_checksums.txt and recomputes
the sha256 of the criteria section of each listed file. Any
mismatch FAILS so the criteria cannot be silently changed
after a run.

To regenerate after an intentional criteria update, re-run
build_logs/_criteria_checksum_gen.py and commit the updated
file alongside the criteria change.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CHECKSUMS_FILE = REPO / "docs" / "criteria_checksums.txt"


def _get_criteria_section(path: Path) -> str:
    """Return the text from the start of the file up to (but
    not including) the first '## Dated notes' header, or the
    first '## Verdict (' block, or end of file if neither is
    present."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    cut = len(lines)
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("## Dated notes"):
            cut = i
            break
        if s.startswith("## Verdict (") and "filled ONCE" in s:
            cut = i
            break
    return "".join(lines[:cut])


def _load_checksums() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in CHECKSUMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        sha, rel = parts
        out[rel] = sha
    return out


def test_criteria_checksums_match():
    """Every entry in docs/criteria_checksums.txt must match
    the current sha256 of the criteria section. A mismatch
    means someone changed the criteria text without
    regenerating the checksum file."""
    checksums = _load_checksums()
    assert checksums, (
        f"no checksums loaded from {CHECKSUMS_FILE}; "
        f"re-run build_logs/_criteria_checksum_gen.py"
    )
    mismatches: list[str] = []
    missing: list[str] = []
    for rel, expected_sha in sorted(checksums.items()):
        p = REPO / rel
        if not p.is_file():
            missing.append(rel)
            continue
        section = _get_criteria_section(p)
        actual_sha = hashlib.sha256(section.encode("utf-8")).hexdigest()
        if actual_sha != expected_sha:
            mismatches.append(
                f"  {rel}: expected {expected_sha[:16]}..., "
                f"got {actual_sha[:16]}..."
            )
    assert not missing, (
        f"files listed in {CHECKSUMS_FILE} but not found: {missing}"
    )
    assert not mismatches, (
        "criteria section hash mismatch (criteria was changed "
        "after the run without regenerating the checksums):\n"
        + "\n".join(mismatches)
        + "\n\nRe-run build_logs/_criteria_checksum_gen.py and "
        "commit the updated file alongside the criteria change."
    )

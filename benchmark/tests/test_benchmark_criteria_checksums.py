"""Guard: the criteria section of the frozen benchmark files must not change.

The standing rule is that criteria are committed BEFORE a run and never
changed afterward; a wrong expectation may be corrected only as a dated,
evidence-backed note (which is hashed EXCLUDING the note section).

This test reads benchmark/criteria_checksums.txt and recomputes the
sha256 of the criteria section of each listed file.  Any mismatch FAILS.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BENCHMARK = REPO / "benchmark"
CHECKSUMS_FILE = BENCHMARK / "criteria_checksums.txt"


def _get_criteria_section(path: Path) -> str:
    """The text up to the first '## Dated notes' header, the first
    '## Verdict (' block that is filled once, or the end of the file."""
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


def test_the_benchmark_criteria_checksums_match():
    """Every entry in benchmark/criteria_checksums.txt must match the
    current sha256 of the criteria section of the file it names."""
    checksums = _load_checksums()
    assert checksums, f"no checksums loaded from {CHECKSUMS_FILE}"
    missing: list[str] = []
    mismatches: list[str] = []
    for rel, expected_sha in sorted(checksums.items()):
        path = REPO / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual_sha = hashlib.sha256(
            _get_criteria_section(path).encode("utf-8")).hexdigest()
        if actual_sha != expected_sha:
            mismatches.append(
                f"  {rel}: expected {expected_sha[:16]}..., "
                f"got {actual_sha[:16]}..."
            )
    assert not missing, (
        f"files listed in {CHECKSUMS_FILE.name} but not found: {missing}"
    )
    assert not mismatches, (
        "criteria section hash mismatch (the criteria were changed after the "
        "run without regenerating the checksums):\n" + "\n".join(mismatches)
    )


def test_every_benchmark_entry_of_the_old_file_moved_here():
    """The benchmark files are pinned here and nowhere else, so that
    nothing outside benchmark/ depends on the folder."""
    docs_checksums = (REPO / "docs" / "criteria_checksums.txt").read_text(
        encoding="utf-8")
    for line in docs_checksums.splitlines():
        if line.strip() and not line.startswith("#"):
            name = line.split("  ", 1)[1].strip()
            assert not name.startswith("benchmark/"), (
                f"{name} is still pinned in docs/criteria_checksums.txt")

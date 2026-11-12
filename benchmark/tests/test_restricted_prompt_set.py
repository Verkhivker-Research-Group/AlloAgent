"""The restricted-scenario prompt set is committed before any run and
cannot be changed silently.

The guard checks that:

* the file's sha256 is the one recorded in
  ``benchmark/criteria_checksums.txt``;
* it has exactly one row per benchmark prompt, with the same ids, in
  the same order, as ``benchmark/benchmark_draft.json``;
* the set (the "yes" prompts) is exactly the rows marked "yes", so
  the set and the table cannot drift apart;
* every row says why, which tools and which data it needs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SET_FILE = REPO / "benchmark" / "restricted_prompt_set.json"
DRAFT_FILE = REPO / "benchmark" / "benchmark_draft.json"
CHECKSUMS_FILE = REPO / "benchmark" / "criteria_checksums.txt"


def _checksums() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in CHECKSUMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


def test_the_set_file_matches_its_recorded_checksum():
    checksums = _checksums()
    rel = "benchmark/restricted_prompt_set.json"
    assert rel in checksums, (
        f"{rel} is not in {CHECKSUMS_FILE.name}; the set must be committed "
        f"with its checksum before any run")
    # The same hashing the criteria guard uses: the text of the file.
    actual = hashlib.sha256(
        SET_FILE.read_text(encoding="utf-8").encode("utf-8")
    ).hexdigest()
    assert actual == checksums[rel], (
        f"the restricted prompt set changed after the commit: expected "
        f"{checksums[rel][:16]}..., got {actual[:16]}...")


def test_one_row_per_benchmark_prompt():
    payload = json.loads(SET_FILE.read_text(encoding="utf-8"))
    draft = json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
    draft_ids = [prompt["id"] for prompt in draft]
    rows = payload["prompts"]
    assert [row["id"] for row in rows] == draft_ids, (
        "the rows must be one per benchmark prompt, with the same ids, in "
        "the same order")
    assert payload["source_sha256"] == hashlib.sha256(
        DRAFT_FILE.read_bytes()
    ).hexdigest(), "the recorded draft checksum is stale"


def test_the_set_is_exactly_the_yes_rows():
    payload = json.loads(SET_FILE.read_text(encoding="utf-8"))
    yes = [
        row["id"] for row in payload["prompts"]
        if row["solvable_from_local_resources_alone"] == "yes"
    ]
    assert payload["the_set"] == yes, (
        "the set and the 'yes' rows disagree")
    assert payload["counts"]["yes"] == len(yes)
    assert payload["counts"]["no"] == len(payload["prompts"]) - len(yes)
    assert payload["counts"]["prompts"] == len(payload["prompts"])


def test_every_row_says_why_and_what_it_needs():
    payload = json.loads(SET_FILE.read_text(encoding="utf-8"))
    for row in payload["prompts"]:
        assert row["solvable_from_local_resources_alone"] in ("yes", "no"), row["id"]
        assert row["reason"].strip(), f"{row['id']} has no reason"
        assert row["tools"].strip(), f"{row['id']} names no tools"
        assert row["data"].strip(), f"{row['id']} names no data"
        if row["solvable_from_local_resources_alone"] == "no":
            assert row["would_become_yes_if"].strip(), (
                f"{row['id']} is a 'no' but does not say what would make it a 'yes'")

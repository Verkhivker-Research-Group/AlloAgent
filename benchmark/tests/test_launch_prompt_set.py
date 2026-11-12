"""The launch set is committed before the launch and cannot drift silently.

The launch set names the prompts that are actually run. It is a subset
of the committed prompt table, and every prompt it defers has to say
why it is deferred and what replaces it.

The guard checks that:

* the launch set is the prompt table minus exactly the deferred ids,
  and the deferred ids are not in the launch set;
* every deferred prompt says why, and names its replacement prompt and
  the tools the replacement uses;
* the launch set's own counts agree with its content;
* the recorded source checksum is the prompt table's.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAUNCH_SET = REPO / "benchmark" / "launch_prompt_set.json"
DRAFT = REPO / "benchmark" / "benchmark_draft.json"


def _payload() -> dict:
    return json.loads(LAUNCH_SET.read_text(encoding="utf-8"))


def test_the_launch_set_is_the_prompt_table_minus_the_deferred_ids():
    payload = _payload()
    draft_ids = [p["id"] for p in json.loads(DRAFT.read_text(encoding="utf-8"))]
    deferred = [entry["id"] for entry in payload["deferred"]]
    assert payload["launch_prompts"] == [
        pid for pid in draft_ids if pid not in deferred
    ], "the launch set must be the prompt table minus the deferred prompts"
    assert len(set(payload["launch_prompts"])) == len(payload["launch_prompts"]), (
        "the launch set must not repeat a prompt")


def test_the_counts_agree_with_the_content():
    payload = _payload()
    assert payload["counts"]["launch_prompts"] == len(payload["launch_prompts"])
    assert payload["counts"]["deferred"] == len(payload["deferred"])
    assert payload["counts"]["draft_prompts"] == len(
        json.loads(DRAFT.read_text(encoding="utf-8")))


def test_the_recorded_source_checksum_is_the_prompt_tables():
    payload = _payload()
    assert payload["source_sha256"] == hashlib.sha256(
        DRAFT.read_bytes()
    ).hexdigest(), "the recorded draft checksum is stale"


def test_every_deferred_prompt_says_why_and_names_its_replacement():
    payload = _payload()
    for entry in payload["deferred"]:
        assert entry["reason"].strip(), f"{entry['id']} has no reason"
        assert entry["replacement_prompt"].strip(), (
            f"{entry['id']} names no replacement prompt")
        assert entry["replacement_tools"].strip(), (
            f"{entry['id']} names no replacement tools")
        assert entry["status"] == "deferred"


def test_a_deferred_prompt_keeps_its_committed_criteria():
    """A deferred prompt is not rewritten: it stays in the draft and in
    the checklists, so the criteria of the prompt table stay intact."""
    payload = _payload()
    draft_ids = {p["id"] for p in json.loads(DRAFT.read_text(encoding="utf-8"))}
    checklist_ids = {
        p["id"]
        for p in json.loads(
            (REPO / "benchmark" / "checklists.json").read_text(encoding="utf-8")
        )["prompts"]
    }
    for entry in payload["deferred"]:
        assert entry["id"] in draft_ids, (
            f"{entry['id']} is deferred but was removed from the prompt table")
        assert entry["id"] in checklist_ids, (
            f"{entry['id']} is deferred but lost its checklist")

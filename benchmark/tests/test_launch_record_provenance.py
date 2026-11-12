"""The launch provenance contract: every run record has to say what produced it.

A benchmark record is only evidence if it says which inputs produced it.
The contract is implemented once, in ``benchmark/benchmark_launch.py``; this
test is the guard that the contract exists and that it rejects the
records that do not satisfy it. The driver calls the same function on
every record it reads back.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "benchmark"))

import benchmark_launch  # noqa: E402  (the path is set up above)

GOOD_HASH = "a" * 64


def _record(**overrides) -> dict:
    record = {
        "id": "S01",
        "status": "completed",
        "git_dirty": False,
        "launch_manifest": {
            "launch_tag": "launch-2026-10-28",
            "commit": "b12700e00000000000000000000000000000000",
            "image_digest": "sha256:a4c925e9353564b42702ceecf158c69ef674c4cc2d205ceb6035cb9c0b083b07",
            "benchmark_sha256": {
                "benchmark_draft.json": GOOD_HASH,
                "checklists.json": GOOD_HASH,
                "restricted_prompt_set.json": GOOD_HASH,
            },
        },
    }
    record.update(overrides)
    return record


def _manifest(**overrides) -> dict:
    manifest = dict(_record()["launch_manifest"])
    manifest.update(overrides)
    return manifest


def test_a_complete_record_has_no_problems():
    assert benchmark_launch.validate_record_provenance(_record()) == []


@pytest.mark.parametrize("field", ["launch_tag", "commit", "image_digest"])
def test_a_missing_manifest_field_is_a_problem(field):
    manifest = _manifest()
    manifest[field] = ""
    problems = benchmark_launch.validate_record_provenance(
        _record(launch_manifest=manifest))
    assert problems, f"a record without {field} must be rejected"
    assert any(field.split("_")[-1] in problem for problem in problems)


def test_an_image_digest_that_is_not_a_digest_is_a_problem():
    manifest = _manifest(image_digest="alloagent-eval:v6")
    problems = benchmark_launch.validate_record_provenance(
        _record(launch_manifest=manifest))
    assert any("image digest" in problem for problem in problems)


@pytest.mark.parametrize(
    "name", ["benchmark_draft.json", "checklists.json", "restricted_prompt_set.json"]
)
def test_a_missing_benchmark_hash_is_a_problem(name):
    manifest = _manifest()
    manifest["benchmark_sha256"] = {
        k: v for k, v in manifest["benchmark_sha256"].items() if k != name
    }
    problems = benchmark_launch.validate_record_provenance(
        _record(launch_manifest=manifest))
    assert any(name in problem for problem in problems)


def test_a_malformed_benchmark_hash_is_a_problem():
    manifest = _manifest()
    manifest["benchmark_sha256"]["checklists.json"] = "not-a-sha256"
    problems = benchmark_launch.validate_record_provenance(
        _record(launch_manifest=manifest))
    assert any("checklists.json" in problem for problem in problems)


def test_a_dirty_record_is_a_problem():
    problems = benchmark_launch.validate_record_provenance(_record(git_dirty=True))
    assert any("dirty" in problem for problem in problems)


def test_a_record_without_a_dirty_flag_is_a_problem():
    record = _record()
    record.pop("git_dirty")
    problems = benchmark_launch.validate_record_provenance(record)
    assert any("dirty" in problem for problem in problems)


def test_a_record_without_a_launch_manifest_is_a_problem():
    problems = benchmark_launch.validate_record_provenance({"id": "S01"})
    assert any("launch_manifest" in problem for problem in problems)


def test_the_three_benchmark_files_are_the_committed_ones():
    assert benchmark_launch.BENCHMARK_FILES == (
        "benchmark_draft.json", "checklists.json", "restricted_prompt_set.json")

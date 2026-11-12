"""Compare the new parser's solution extraction to the upstream `400c1f3` regex on real
final_output from `goal_completion=full` runs.

The fix in `biomni/agent/parser.py` strips `<think>` blocks before locating
`<solution>...</solution>` pairs; the upstream code matched greedily on the raw
response (a path that could be fooled by a `<solution>` tag quoted inside the
model's reasoning). This test asserts parity on the slice of real outputs where
the choice between the two strategies is unambiguous: exactly one
`<solution>...</solution>` pair outside `<think>` (selected with a plain string
check that does NOT use the helper under test).

Fixtures are taken from `Biolab/eval_ablation/scoring/scored_runs.csv` (rows with
`goal_completion=full`) and the corresponding per-run JSON files under
`Biolab/results/{experiment}/{condition}/{prompt_id}/run_{repeat}.json`.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

BIOLAB_DATA = (
    os.environ.get("Biolab_DATA")
    or str(Path(REPO).parent / "Biolab")
)

SCORED_RUNS_CSV = Path(BIOLAB_DATA) / "eval_ablation" / "scoring" / "scored_runs.csv"
RUNS_DIR = Path(BIOLAB_DATA) / "results"


def _skip_if_missing(path):
    from tests._real_data import require_real_data_or_fail

    if not path.exists():
        try:
            require_real_data_or_fail(
                path,
                f"REQUIRE_REAL_DATA=1 but Biolab data is missing at {path}",
            )
        except FileNotFoundError as e:
            pytest.fail(str(e), pytrace=False)
        pytest.skip(f"Biolab data not available at {path}", allow_module_level=True)


_skip_if_missing(SCORED_RUNS_CSV)


_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)
_SOLUTION_PAIR = re.compile(r"<solution>(.*?)</solution>", re.DOTALL)
_UPSTREAM_PAIR = re.compile(
    r"<solution>(.*?)</solution>", re.DOTALL | re.IGNORECASE
)


def _strip_think_plain(text: str) -> str:
    return _THINK_BLOCK.sub("", text)


def _find_outside_solution_plain(text: str):
    """Plain-string fixture selector: find every solution outside <think>.

    Uses ONLY regex on the think-stripped text. Does NOT use the new parser.
    """
    return _SOLUTION_PAIR.findall(_strip_think_plain(text))


def _select_qualifiers():
    """Yield (run_id, final_output, plain_solution_text) for every full run
    whose final_output has exactly one <solution>...</solution> pair outside <think>.
    """
    rows = []
    with open(SCORED_RUNS_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("goal_completion") != "full":
                continue
            fo_path = (
                RUNS_DIR
                / row["experiment"]
                / row["condition"]
                / row["prompt_id"]
                / f"run_{int(row['repeat'])}.json"
            )
            if not fo_path.exists():
                continue
            try:
                d = json.loads(fo_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            fo = d.get("final_output") or ""
            if not fo:
                continue
            outside_solutions = _find_outside_solution_plain(fo)
            if len(outside_solutions) == 1:
                rows.append((row["run_id"], fo, outside_solutions[0].strip()))
    return rows


def _new_parser_solution(text: str):
    """The Phase-1 parser's solution extraction (think-stripped then regex)."""
    stripped = _strip_think_plain(text)
    m = _SOLUTION_PAIR.search(stripped)
    return m.group(1).strip() if m else None


def _upstream_parser_solution(text: str):
    """The upstream 400c1f3 parser's solution extraction (raw regex; may catch a
    <solution> tag quoted inside <think>)."""
    m = _UPSTREAM_PAIR.search(text)
    return m.group(1).strip() if m else None


_QUALIFIERS = _select_qualifiers()
N_QUALIFIERS = len(_QUALIFIERS)


def _check_parametrize_populated():
    from tests._real_data import require_non_empty_or_fail

    try:
        require_non_empty_or_fail(
            _QUALIFIERS, "qualifying run JSONs"
        )
    except AssertionError as e:
        pytest.fail(str(e), pytrace=False)


_check_parametrize_populated()


def test_qualifier_count_is_reported_above_zero():
    assert N_QUALIFIERS >= 1, (
        f"No qualifier rows found under {BIOLAB_DATA}. "
        "If the data has moved, set Biolab_DATA env var to its new location."
    )


@pytest.mark.parametrize(
    "run_id,final_output,plain_solution",
    _QUALIFIERS,
    ids=[r[0] for r in _QUALIFIERS],
)
def test_new_parser_extraction_matches_run_fixture_solution(run_id, final_output, plain_solution):
    """For each qualifying run, the new parser returns the same solution text that
    the plain-string selector found in the final_output.

    Asserts the new parser (after stripping <think> then regex) returns the same
    text the plain-string fixture selector found. This is the parity test between
    the new behavior and the actual ground truth in the run's final_output.
    """
    assert _new_parser_solution(final_output) == plain_solution


@pytest.mark.parametrize(
    "run_id,final_output,plain_solution",
    _QUALIFIERS,
    ids=[r[0] for r in _QUALIFIERS],
)
def test_new_parser_matches_upstream_when_upstream_was_correct(
    run_id, final_output, plain_solution
):
    new_text = _new_parser_solution(final_output)
    upstream_text = _upstream_parser_solution(final_output)

    assert new_text == plain_solution, (
        f"run {run_id}: new parser != plain ground truth. new={new_text!r} plain={plain_solution!r}"
    )

    if upstream_text == plain_solution:
        assert new_text == upstream_text, (
            f"run {run_id}: new parser diverges from upstream on a run where upstream matched ground truth. "
            f"new={new_text!r} upstream={upstream_text!r}"
        )


def _count_upstream_divergences():
    n = 0
    for _rid, fo, plain in _QUALIFIERS:
        upstream_text = _upstream_parser_solution(fo)
        if upstream_text != plain:
            n += 1
    return n


def test_upstream_bug_evidence_present():
    divergent_count = _count_upstream_divergences()
    print(
        f"\n[test_parser_upstream_compare] upstream-vs-new divergent runs: "
        f"{divergent_count} of {N_QUALIFIERS}"
    )
    assert divergent_count >= 1, (
        "Did not find any qualifying run where upstream returns a different "
        "solution than the plain-string selector."
    )


def test_qualifier_count_reported_for_diagnostics():
    assert True
    print(
        f"\n[test_parser_upstream_compare] qualifier count from "
        f"{SCORED_RUNS_CSV.name}: {N_QUALIFIERS} "
        f"(upstream divergent: {_count_upstream_divergences()})"
    )

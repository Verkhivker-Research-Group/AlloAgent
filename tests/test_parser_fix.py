import csv
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

_PARSER_PATH = os.path.join(REPO, "biomni", "agent", "parser.py")
_spec = importlib.util.spec_from_file_location("biomni_agent_parser", _PARSER_PATH)
_parser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parser)

_strip_think = _parser._strip_think
_autoclose_tags = _parser._autoclose_tags
_has_closed_solution_outside_think = _parser._has_closed_solution_outside_think
_has_execute_block_outside_think = _parser._has_execute_block_outside_think
_next_step = _parser._next_step
_next_step_with_repair = _parser._next_step_with_repair


Biolab_DATA = (
    os.environ.get("Biolab_DATA")
    or os.path.abspath(os.path.join(REPO, "..", "Biolab"))
    or "/app"
)
NULL_RUNS_CSV = os.path.join(Biolab_DATA, "prep_reports", "investigation", "null_runs.csv")
SCORED_RUNS_CSV = os.path.join(Biolab_DATA, "eval_ablation", "scoring", "scored_runs.csv")
RUNS_DIR = os.path.join(Biolab_DATA, "results")


def _skip_if_missing(path):
    from tests._real_data import require_real_data_or_fail

    if not os.path.exists(path):
        try:
            require_real_data_or_fail(
                path,
                f"REQUIRE_REAL_DATA=1 but Biolab data is missing at {path}",
            )
        except FileNotFoundError as e:
            pytest.fail(str(e), pytrace=False)
        pytest.skip(f"Biolab data not available at {path}", allow_module_level=True)


def _load_37_null_outputs():
    """Load the 37 'no usable output' rows that contain parseable assistant content.

    Returns list of (opaque_id, final_output).
    """
    out = []
    with open(NULL_RUNS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fo = row.get("final_output", "") or ""
            if row.get("null_type") != "no usable output":
                continue
            if not fo.startswith("<"):
                continue
            out.append((row["opaque_id"], fo))
    return out


def _load_5_clean_outputs():
    """Load 5 'goal_completion=full' runs whose final_output contains a clean
    <solution>...</solution> pair outside <think> and no <execute> block outside <think>.

    Returns list of (run_id, final_output).
    """
    out = []
    with open(SCORED_RUNS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("goal_completion") != "full":
                continue
            fo_path = os.path.join(
                RUNS_DIR,
                row["experiment"],
                row["condition"],
                row["prompt_id"],
                f"run_{int(row['repeat'])}.json",
            )
            if not os.path.exists(fo_path):
                continue
            try:
                with open(fo_path, encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception:
                continue
            fo = d.get("final_output", "") or ""
            if not fo:
                continue
            if _has_closed_solution_outside_think(fo) and not _has_execute_block_outside_think(fo):
                out.append((row["run_id"], fo))
                if len(out) >= 5:
                    break
    return out


_skip_if_missing(NULL_RUNS_CSV)
_37 = _load_37_null_outputs()
_5 = _load_5_clean_outputs()


def _check_parametrize_populated():
    from tests._real_data import require_non_empty_or_fail

    try:
        require_non_empty_or_fail(_37, "37 null outputs")
        require_non_empty_or_fail(_5, "5 clean outputs")
    except AssertionError as e:
        pytest.fail(str(e), pytrace=False)


_check_parametrize_populated()


@pytest.mark.parametrize("opaque_id,fo", _37)
def test_37_null_runs_now_route_to_execute(opaque_id, fo):
    """All 37 'no usable output' early-ended runs must now route to 'execute'.

    Pre-fix behavior: the broken parser matched a stray </solution> tag outside
    any <think> block, saw a (false) <solution>...</solution> pair, and routed
    these to 'end' — leaving the conversation in an unexecuted-code state.
    Post-fix behavior: stripping the think block first exposes the actual
    <execute>...</execute> pair and routes the run to 'execute'.

    `_next_step_with_repair` first runs `_autoclose_tags` (which inserts a
    missing opening <execute> when only the closing tag is present) before
    deciding. This mirrors what the agent does.
    """
    decision = _next_step_with_repair(fo)
    assert decision == "execute", (
        f"{opaque_id}: expected 'execute', got {decision!r}. "
        "Strip-think must not strip the actual <execute> block."
    )


@pytest.mark.parametrize("opaque_id,fo", _37)
def test_37_null_runs_have_execute_after_repair(opaque_id, fo):
    """After the autoclose repair, each of the 37 must have a complete
    <execute>...</execute> pair outside <think>."""
    repaired = _autoclose_tags(fo)
    assert _has_execute_block_outside_think(repaired), (
        f"{opaque_id}: missing <execute>...</execute> outside <think> after repair"
    )


@pytest.mark.parametrize("opaque_id,fo", _37)
def test_37_null_runs_no_solution_outside_think(opaque_id, fo):
    """Bug (a): a <solution> tag quoted inside <think> must not be treated as a
    closed solution pair. After repair, each of the 37 must NOT have a
    <solution> pair outside <think> (or it would have routed to 'end' rather
    than 'execute')."""
    repaired = _autoclose_tags(fo)
    assert not _has_closed_solution_outside_think(repaired), (
        f"{opaque_id}: unexpected <solution>...</solution> pair outside <think>; "
        "this run should route to 'end', not 'execute'"
    )


def test_strip_think_drops_think_block():
    """The strip-think helper must remove every <think>...</think> block."""
    msg = "<think>plan</think>body<think>more plan</think>more body"
    assert _strip_think(msg) == "bodymore body"


def test_solution_inside_think_does_not_count():
    """Bug (a) regression: a <solution>...</solution> pair sitting INSIDE <think>
    must not be treated as a closed solution outside think."""
    msg = (
        "<think>I will produce <solution>placeholder</solution> below</think>\n"
        "<execute>print(1)</execute>"
    )
    assert not _has_closed_solution_outside_think(msg)
    assert _has_execute_block_outside_think(msg)
    assert _next_step(msg) == "execute"


def test_stray_closing_solution_after_execute_routes_to_execute():
    """Bug (b) regression: a stray </solution> after </execute> must NOT cause
    the run to terminate with unexecuted code. The broken parser saw an
    apparent <solution>...</solution> pair (from a <solution> tag quoted in the
    preceding think block to the trailing </solution> tag) and routed to 'end'.
    After the fix, the helper only counts pairs that sit OUTSIDE think blocks,
    so this output routes to 'execute' and the run continues normally."""
    msg = (
        "<think>I need to mention <solution>as a reminder</solution> of the format\n"
        "but actually run code.</think>\n"
        "<execute>print('hello')</execute>\n"
        "</solution>"
    )
    assert not _has_closed_solution_outside_think(msg)
    assert _has_execute_block_outside_think(msg)
    assert _next_step(msg) == "execute"


@pytest.mark.parametrize("run_id,fo", _5)
def test_5_clean_routes_to_end(run_id, fo):
    """5 positive-control runs (goal_completion=full) must still route to 'end'.

    These runs contain a real <solution>...</solution> pair OUTSIDE any
    <think>...</think> block. The fix must NOT regress them.
    """
    decision = _next_step_with_repair(fo)
    assert decision == "end", (
        f"{run_id}: expected 'end' (positive control), got {decision!r}"
    )


@pytest.mark.parametrize("run_id,fo", _5)
def test_5_clean_have_solution_outside_think(run_id, fo):
    assert _has_closed_solution_outside_think(fo), (
        f"{run_id}: positive control should have a closed <solution> pair"
    )
"""The run records must carry what the cost-constrained endpoint needs.

The endpoint computes "did this run succeed within its token/time
budget", so every recorded step needs the cumulative spend and the
elapsed time; without them the budget can only be checked at the end
of a run, and a run that was already over budget keeps burning tokens
unnoticed.

Two things are checked here:

* the recorder (``biomni/agent/a1.py``) writes the two fields into
  every recorded step;
* a record that carries them satisfies the contract the endpoint
  relies on: the cumulative tokens never decrease, the last step's
  cumulative equals the run's total, and the elapsed times never
  decrease.

The check that the analyzer of the benchmark reads the two fields is in
``benchmark/tests/test_analyze_budget_fields.py``: it reads a file of
the benchmark folder, so it belongs with it.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECORDER = REPO / "biomni" / "agent" / "a1.py"
FIXTURE = REPO / "tests" / "fixtures" / "run_record_with_budget.json"


def test_the_recorder_writes_the_budget_fields_into_every_step():
    source = RECORDER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    written: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                if target.value.id == "step":
                    key = target.slice
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        written.add(key.value)
    assert "elapsed_s" in written, (
        "the recorder does not write the elapsed time into the step")
    assert "cumulative_tokens" in written, (
        "the recorder does not write the cumulative tokens into the step")


def test_a_record_with_the_budget_fields_satisfies_the_contract():
    record = json.loads(FIXTURE.read_text(encoding="utf-8"))
    messages = record["messages"]
    assert messages, "the fixture has no steps"

    previous_tokens = 0
    previous_elapsed = 0.0
    for step in messages:
        assert "elapsed_s" in step, step
        assert "cumulative_tokens" in step, step
        cumulative = step["cumulative_tokens"]
        assert cumulative["total_tokens"] >= previous_tokens, (
            "the cumulative tokens went down")
        assert step["elapsed_s"] >= previous_elapsed, "the elapsed time went down"
        previous_tokens = cumulative["total_tokens"]
        previous_elapsed = step["elapsed_s"]

    assert previous_tokens == record["token_total"]["total_tokens"], (
        "the last step's cumulative tokens do not match the run's total")

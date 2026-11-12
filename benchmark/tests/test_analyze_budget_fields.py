"""The analyzer of the benchmark must read the per-step budget fields.

The cost-constrained endpoint computes "did this run succeed within its
token/time budget", so the analyzer has to look at the cumulative spend
and the elapsed time of every step, not only at the totals of the run.

The check lives here, with the benchmark it reads: nothing outside the
benchmark folder may depend on a file of it.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ANALYZER = REPO / "benchmark" / "analyze.py"


def test_the_analyzer_reports_the_budget_fields():
    analyzer = ANALYZER.read_text(encoding="utf-8")
    assert "cumulative_tokens" in analyzer, (
        "the analyzer does not look for the per-step budget fields")
    assert "elapsed_s" in analyzer, (
        "the analyzer does not look for the per-step elapsed time")

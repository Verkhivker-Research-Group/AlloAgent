"""Benchmark-blocklist test (Part 1d)."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from biomni.tool._blocklist import benchmark_blocklist


@pytest.fixture
def fake_blocklist_file(tmp_path, monkeypatch):
    """Write a small blocklist file and set the env var to it."""
    p = tmp_path / "blocklist.tsv"
    p.write_text(
        "# header comment\n"
        "FAKE_BLOCKED_PDB_ID\n"
        "FAKE_BLOCKED_UNIPROT\n"
        "\n"
        "  P12345  \n",
        encoding="utf-8",
    )
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(p))
    return p


def test_decorator_blocks_first_arg(fake_blocklist_file):
    called = []

    @benchmark_blocklist
    def f(x):
        called.append(x)
        return {"ok": True, "x": x}

    r = f("FAKE_BLOCKED_PDB_ID")
    assert r["success"] is False
    assert "blocked" in r["error"].lower()
    assert called == [], f"sentinel was called: {called}"


def test_decorator_passes_non_blocked(fake_blocklist_file):
    called = []

    @benchmark_blocklist
    def f(x):
        called.append(x)
        return {"ok": True, "x": x}

    r = f("CLEAN_VALUE")
    assert r == {"ok": True, "x": "CLEAN_VALUE"}
    assert called == ["CLEAN_VALUE"]


def test_decorator_no_op_when_no_env_no_file(monkeypatch, tmp_path):
    monkeypatch.delenv("BENCHMARK_BLOCKLIST_FILE", raising=False)
    monkeypatch.chdir(tmp_path)

    called = []

    @benchmark_blocklist
    def f(x):
        called.append(x)
        return {"ok": True, "x": x}

    r = f("SOMETHING")
    assert r == {"ok": True, "x": "SOMETHING"}
    assert called == ["SOMETHING"]


def test_decorator_uses_default_path_when_env_unset(monkeypatch, tmp_path):
    """If the env var is unset but `Biolab/prep_reports/benchmark_blocklist.tsv`
    exists at the repo root, the decorator reads it."""
    from tests._real_data import require_real_data_or_fail

    repo_root = Path(__file__).resolve().parents[1]
    default = repo_root / "Biolab" / "prep_reports" / "benchmark_blocklist.tsv"
    if not default.is_file():
        try:
            require_real_data_or_fail(
                default,
                f"REQUIRE_REAL_DATA=1 but default blocklist file is missing at {default}",
            )
        except FileNotFoundError as e:
            pytest.fail(str(e), pytrace=False)
        pytest.skip(f"default blocklist file not present at {default}")
    monkeypatch.delenv("BENCHMARK_BLOCKLIST_FILE", raising=False)
    called = []

    @benchmark_blocklist
    def f(x):
        called.append(x)
        return {"ok": True, "x": x}

    r = f("ANYTHING")
    assert isinstance(r, dict)

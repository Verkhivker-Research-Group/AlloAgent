"""T3 get_stingallo_allosteric_residues tests (Part 2)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from biomni.tool.get_stingallo_allosteric_residues import (
    get_stingallo_allosteric_residues,
)

REPO = Path(__file__).resolve().parents[1]


def test_t3_recorded_fixture_shape(monkeypatch):
    """The function returns a well-formed contract dict with the
    expected shape, against a recorded STINGAllo fixture.

    (The fixture was recorded from the live API when available.
    If the live API is down at fixture-recording time, the fixture
    is a minimal synthetic placeholder; the test still asserts the
    shape, not specific residues.)
    """
    import biomni.tool.get_stingallo_allosteric_residues as _impl

    fixture_path = REPO / "tests" / "fixtures" / "stingallo_example.json"
    if fixture_path.is_file():
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        expected_residues = fixture.get("residues", [])
    else:
        fixture = {"residues": []}
        expected_residues = []

    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, params=None, timeout=None: _FakeResp(fixture),
    )
    monkeypatch.setattr(
        "biomni.tool.get_stingallo_allosteric_residues._record_call",
        lambda pdb_id: None,
    )
    monkeypatch.setattr(
        "biomni.tool.get_stingallo_allosteric_residues._check_rate_limit",
        lambda pdb_id: None,
    )
    r = get_stingallo_allosteric_residues("1AKE")
    assert r["success"] is True
    data = r["data"]
    assert data["pdb_id"] == "1AKE"
    assert data["chain_id"] is None
    assert isinstance(data["residues"], list)
    if expected_residues:
        assert data["residues"] == expected_residues


def test_t3_negative_control_unknown_pdb(monkeypatch):
    """Unknown PDB returns success=True with empty residues list."""
    import biomni.tool.get_stingallo_allosteric_residues as _impl
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, params=None, timeout=None: _FakeResp({"residues": []}),
    )
    monkeypatch.setattr(
        "biomni.tool.get_stingallo_allosteric_residues._record_call",
        lambda pdb_id: None,
    )
    monkeypatch.setattr(
        "biomni.tool.get_stingallo_allosteric_residues._check_rate_limit",
        lambda pdb_id: None,
    )
    r = get_stingallo_allosteric_residues("ZZZZ")
    assert r["success"] is True
    assert r["data"]["pdb_id"] == "ZZZZ"
    assert r["data"]["residues"] == []


def test_t3_blocklist_short_circuits(monkeypatch, tmp_path):
    """Blocklist decoration short-circuits with no network call."""
    import biomni.tool.get_stingallo_allosteric_residues as _impl
    bl = tmp_path / "blocklist.tsv"
    bl.write_text("1AKE\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))
    called = []
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, params=None, timeout=None: (called.append(url) or _FakeResp({})),
    )
    r = get_stingallo_allosteric_residues("1AKE")
    assert r["success"] is False
    assert "blocked" in r["error"].lower()
    assert called == [], f"network was called despite blocklist: {called}"


def test_t3_rate_limit_blocks_when_daily_request_limit_reached(monkeypatch, tmp_path):
    """When the counter says requests >= 100, the function returns
    success=False WITHOUT making the network call.
    """
    import biomni.tool.get_stingallo_allosteric_residues as _impl
    counter = tmp_path / "stingallo_counter.json"
    counter.parent.mkdir(parents=True, exist_ok=True)
    counter.write_text(
        json.dumps(
            {
                "date": __import__("time").strftime("%Y-%m-%d"),
                "requests": 100,
                "pdbs": ["1AKE"],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(_impl, "_COUNTER_PATH", counter)
    called = []
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, params=None, timeout=None: (called.append(url) or _FakeResp({})),
    )
    r = get_stingallo_allosteric_residues("4HHB")
    assert r["success"] is False
    assert "limit" in r["error"].lower()
    assert called == [], f"network was called despite rate limit: {called}"


def test_t3_rate_limit_blocks_when_daily_pdb_limit_reached(monkeypatch, tmp_path):
    """When the counter says unique PDBs >= 30, the function returns
    success=False WITHOUT making the network call (for a NEW pdb_id).
    """
    import biomni.tool.get_stingallo_allosteric_residues as _impl
    counter = tmp_path / "stingallo_counter.json"
    counter.parent.mkdir(parents=True, exist_ok=True)
    pdbs = [f"PDB{i:02d}" for i in range(30)]
    counter.write_text(
        json.dumps(
            {
                "date": __import__("time").strftime("%Y-%m-%d"),
                "requests": 5,
                "pdbs": pdbs,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(_impl, "_COUNTER_PATH", counter)
    called = []
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, params=None, timeout=None: (called.append(url) or _FakeResp({})),
    )
    r = get_stingallo_allosteric_residues("NEWPDB")
    assert r["success"] is False
    assert "limit" in r["error"].lower()
    assert called == [], f"network was called despite PDB limit: {called}"


class _FakeResp:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json

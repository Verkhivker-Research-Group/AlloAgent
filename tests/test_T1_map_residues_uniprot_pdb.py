"""T1 map_residues_uniprot_pdb tests (Part 2)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from biomni.tool.map_residues_uniprot_pdb import (
    map_pdb_to_best_structures,
    map_residues_uniprot_pdb,
)

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE = REPO / "tests" / "fixtures" / "map_residues_uniprot_1AKE.json"
FIX_P69441 = REPO / "tests" / "fixtures" / "map_pdb_to_best_structures_P69441.json"


# ---- offline fixture tests (no network) ----

def test_t1_known_answer_uniprot_offline(monkeypatch):
    """1AKE maps to P69441 (KAD_ECOLI), chains A and B, identity=1.0,
    coverage=1.0, unp_start=1, unp_end=214.

    The fixture JSON is loaded and queried via the function's
    HTTP path is monkeypatched so no network call is made.
    """
    import biomni.tool.map_residues_uniprot_pdb as _impl
    fixture = json.loads(FIX_1AKE.read_text(encoding="utf-8"))
    monkeypatch.setattr(_impl.requests, "get", lambda url, timeout: _FakeResp(fixture))
    r = map_residues_uniprot_pdb("1ake")
    assert r["success"] is True
    data = r["data"]
    assert data["pdb_id"] == "1AKE"
    assert data["uniprot_accessions"] == ["P69441"]
    p69441 = data["mappings"]["P69441"]
    assert p69441["name"] == "KAD_ECOLI"
    chain_ids = sorted(m["chain_id"] for m in p69441["mappings"])
    assert chain_ids == ["A", "B"]
    for m in p69441["mappings"]:
        assert m["unp_start"] == 1
        assert m["unp_end"] == 214
        assert m["identity"] == 1.0
        assert m["coverage"] == 1.0


def test_t1_known_answer_best_structures_offline(monkeypatch):
    """P69441's best_structures is a non-empty list; the function
    returns the list as-is. (1AKE is NOT in this list at the time
    the fixture was recorded; the test asserts a non-empty list
    rather than requiring a specific PDB ID.)"""
    import biomni.tool.map_residues_uniprot_pdb as _impl
    fixture = json.loads(FIX_P69441.read_text(encoding="utf-8"))
    monkeypatch.setattr(_impl.requests, "get", lambda url, timeout: _FakeResp(fixture))
    r = map_pdb_to_best_structures("P69441")
    assert r["success"] is True
    data = r["data"]
    assert data["uniprot_accession"] == "P69441"
    assert isinstance(data["best_structures"], list)
    assert len(data["best_structures"]) > 0


# ---- negative control ----

def test_t1_negative_control_unknown_pdb(monkeypatch):
    """An unknown PDB ID returns a failed contract dict (not an exception).

    The fake endpoint returns `{}` (PDBe returns `{}` for an unknown PDB
    rather than 404).
    """
    import biomni.tool.map_residues_uniprot_pdb as _impl
    monkeypatch.setattr(_impl.requests, "get", lambda url, timeout: _FakeResp({}))
    r = map_residues_uniprot_pdb("ZZZZ")
    assert r["success"] is True  # the call succeeded, but the result is empty
    data = r["data"]
    assert data["pdb_id"] == "ZZZZ"
    assert data["uniprot_accessions"] == []


# ---- input robustness ----

def test_t1_input_lowercase_normalized(monkeypatch):
    """A lowercase PDB ID is normalized to uppercase in `data.pdb_id`."""
    import biomni.tool.map_residues_uniprot_pdb as _impl
    fixture = json.loads(FIX_1AKE.read_text(encoding="utf-8"))
    monkeypatch.setattr(_impl.requests, "get", lambda url, timeout: _FakeResp(fixture))
    r = map_residues_uniprot_pdb("1ake")
    assert r["data"]["pdb_id"] == "1AKE"


# ---- determinism ----

def test_t1_determinism(monkeypatch):
    """Two consecutive calls with the same input return equal data."""
    import biomni.tool.map_residues_uniprot_pdb as _impl
    fixture = json.loads(FIX_1AKE.read_text(encoding="utf-8"))
    monkeypatch.setattr(_impl.requests, "get", lambda url, timeout: _FakeResp(fixture))
    a = map_residues_uniprot_pdb("1AKE")["data"]
    b = map_residues_uniprot_pdb("1AKE")["data"]
    assert a == b


# ---- benchmark blocklist ----

def test_t1_blocklist_short_circuits(monkeypatch, tmp_path):
    """The decorator short-circuits when the PDB ID is on the blocklist."""
    import biomni.tool.map_residues_uniprot_pdb as _impl
    bl = tmp_path / "blocklist.tsv"
    bl.write_text("1AKE\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))
    called = []
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, timeout: (called.append(url) or _FakeResp({})),
    )
    r = map_residues_uniprot_pdb("1AKE")
    assert r["success"] is False
    assert "blocked" in r["error"].lower()
    assert called == [], f"network was called despite blocklist: {called}"


class _FakeResp:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json

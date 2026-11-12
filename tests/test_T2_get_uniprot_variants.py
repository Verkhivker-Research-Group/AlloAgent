"""T2 get_uniprot_variants tests (Part 2)."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from biomni.tool.get_uniprot_variants import get_uniprot_variants

REPO = Path(__file__).resolve().parents[1]
FIX = REPO / "tests" / "fixtures" / "get_uniprot_variants_P04637.json"


def test_t2_known_answer_p04637_contains_R175H(monkeypatch):
    """P04637 (p53) contains R175H (Arg175His) as a well-known hotspot
    variant.

    The fixture was recorded from the live EBI Proteins API
    `/api/features?accession=P04637&types=VARIANT`. The API response
    is wrapped in a list of `{accession, features}` records; the
    implementation finds the matching accession. Within that record
    each variant uses top-level `begin` / `end` /
    `alternativeSequence` fields. The test asserts that at least one
    variant has `begin="175"`, `end="175"`, and
    `alternativeSequence == "H"` -- the R175H hotspot.
    """
    import biomni.tool.get_uniprot_variants as _impl
    fixture = json.loads(FIX.read_text(encoding="utf-8"))
    monkeypatch.setattr(
        _impl.requests, "get", lambda url, timeout: _FakeResp(fixture)
    )
    r = get_uniprot_variants("P04637")
    assert r["success"] is True
    data = r["data"]
    assert data["accession"] == "P04637"
    variants = data["variants"]
    assert isinstance(variants, list)
    assert len(variants) > 100, f"expected >100 variants, got {len(variants)}"
    r175h = [
        v for v in variants
        if v.get("begin") == "175"
        and v.get("end") == "175"
        and v.get("alternativeSequence") == "H"
    ]
    assert r175h, (
        f"R175H missing from {len(variants)} recorded variants; "
        "the implementation may have dropped the begin/end altSeq match"
    )
    assert r175h[0]["alternativeSequence"] == "H"


def test_t2_live_p04637_contains_R175H():
    """Live call to the EBI Proteins API must return R175H on P04637.

    Skipped if RUN_REAL_NETWORK is not set. Asserts (not skips) when
    the live call is exercised.
    """
    if not os.environ.get("RUN_REAL_NETWORK"):
        pytest.skip("set RUN_REAL_NETWORK=1 to exercise the live EBI API")

    t0 = time.perf_counter()
    r = get_uniprot_variants("P04637")
    elapsed = time.perf_counter() - t0
    assert r["success"] is True, r.get("error")
    variants = r["data"]["variants"]
    assert len(variants) > 100, f"only {len(variants)} variants from live API"

    r175h = [
        v for v in variants
        if str(v.get("begin")) == "175"
        and str(v.get("end")) == "175"
        and v.get("alternativeSequence") == "H"
    ]
    assert r175h, (
        f"R175H not found in {len(variants)} live variants from "
        f"EBI /api/features?accession=P04637&types=VARIANT after {elapsed:.2f}s"
    )
    first = r175h[0]
    assert first["ftId"], "R175H record missing ftId"
    assert first["description"], "R175H record missing description"


def test_t2_negative_control_unknown_accession(monkeypatch):
    """An unknown accession returns an empty variants list (PDBe-style)."""
    import biomni.tool.get_uniprot_variants as _impl
    monkeypatch.setattr(
        _impl.requests, "get", lambda url, timeout: _FakeResp({"features": []})
    )
    r = get_uniprot_variants("ZZZZZZ")
    assert r["success"] is True
    assert r["data"]["accession"] == "ZZZZZZ"
    assert r["data"]["variants"] == []


def test_t2_input_lowercase_normalized(monkeypatch):
    """Lowercase accession is normalized to uppercase."""
    import biomni.tool.get_uniprot_variants as _impl
    fixture = json.loads(FIX.read_text(encoding="utf-8"))
    monkeypatch.setattr(
        _impl.requests, "get", lambda url, timeout: _FakeResp(fixture)
    )
    r = get_uniprot_variants("p04637")
    assert r["data"]["accession"] == "P04637"


def test_t2_determinism(monkeypatch):
    """Two calls return equal data."""
    import biomni.tool.get_uniprot_variants as _impl
    fixture = json.loads(FIX.read_text(encoding="utf-8"))
    monkeypatch.setattr(
        _impl.requests, "get", lambda url, timeout: _FakeResp(fixture)
    )
    a = get_uniprot_variants("P04637")["data"]
    b = get_uniprot_variants("P04637")["data"]
    assert a == b


def test_t2_blocklist_short_circuits(monkeypatch, tmp_path):
    """Blocklist decoration short-circuits and skips the network call."""
    import biomni.tool.get_uniprot_variants as _impl
    bl = tmp_path / "blocklist.tsv"
    bl.write_text("P04637\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))
    called = []
    monkeypatch.setattr(
        _impl.requests, "get",
        lambda url, timeout: (called.append(url) or _FakeResp({})),
    )
    r = get_uniprot_variants("P04637")
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

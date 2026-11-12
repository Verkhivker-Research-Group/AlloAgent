"""T5 detect_pockets_p2rank tests (Part 2)."""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE_PDB = REPO / "tests" / "fixtures" / "1ake.pdb"
FIX_1AKE_CIF = REPO / "tests" / "fixtures" / "1ake.cif"


def _has_prank_and_java() -> bool:
    return shutil.which("prank") is not None and shutil.which("java") is not None


pytestmark = pytest.mark.skipif(
    not _has_prank_and_java(),
    reason="prank (P2Rank 2.5.1) or Java not installed in this env",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def _first_pocket(pockets):
    return next((p for p in pockets if p["rank"] == 1), None)


def test_t5_recorded_1ake_pdb_returns_nonempty_pockets():
    """prank predict on the recorded 1AKE PDB fixture returns >= 1
    pocket with parsed rank, score, probability, and residues.
    """
    if not FIX_1AKE_PDB.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE_PDB}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    r = detect_pockets_p2rank(str(FIX_1AKE_PDB))
    assert _contract_keys_present(r)
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE_PDB.stem
    pockets = r["data"]["pockets"]
    assert isinstance(pockets, list)
    assert len(pockets) >= 1, (
        f"expected >= 1 pocket, got {len(pockets)}"
    )
    first = _first_pocket(pockets)
    assert first is not None
    assert first["rank"] == 1
    assert isinstance(first["score"], float)
    assert first["score"] > 0.0
    assert isinstance(first["probability"], float)
    assert 0.0 <= first["probability"] <= 1.0
    assert isinstance(first["residues"], list)


def test_t5_recorded_1ake_cif_returns_nonempty_pockets():
    """prank predict also accepts the mmCIF version of 1AKE."""
    if not FIX_1AKE_CIF.is_file():
        pytest.skip(f"1AKE mmCIF fixture not at {FIX_1AKE_CIF}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    r = detect_pockets_p2rank(str(FIX_1AKE_CIF))
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE_CIF.stem
    assert len(r["data"]["pockets"]) >= 1


def test_t5_negative_control_non_pdb_input():
    """A non-existent path returns success=False with a clear error."""
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    r = detect_pockets_p2rank("/tmp/this-pdb-does-not-exist-xyzzy.pdb")
    assert r["success"] is False
    assert "does not exist" in r["error"].lower() or "not found" in r["error"].lower()


def test_t5_lowercase_input_accepted():
    """A lowercase PDB path is accepted without error."""
    if not FIX_1AKE_PDB.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE_PDB}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    r = detect_pockets_p2rank(str(FIX_1AKE_PDB).lower())
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE_PDB.stem


def test_t5_determinism():
    """Two calls with the same input return equal pocket lists."""
    if not FIX_1AKE_PDB.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE_PDB}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    a = detect_pockets_p2rank(str(FIX_1AKE_PDB))["data"]["pockets"]
    b = detect_pockets_p2rank(str(FIX_1AKE_PDB))["data"]["pockets"]
    assert a == b


def test_t5_return_contract_keys_present():
    """Every call returns the 5 required contract keys."""
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    r = detect_pockets_p2rank("/tmp/this-pdb-does-not-exist-xyzzy.pdb")
    assert _contract_keys_present(r)
    assert r["source"] == "biomni.tool.detect_pockets_p2rank.detect_pockets_p2rank"
    assert r["source_version"] == "1.0"
    assert r["query_time_utc"].endswith("Z")


def test_t5_blocklist_short_circuits(tmp_path, monkeypatch):
    """The benchmark_blocklist decorator short-circuits a blocked PDB."""
    if not FIX_1AKE_PDB.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE_PDB}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    blocked = str(FIX_1AKE_PDB)
    bl = tmp_path / "blocklist.tsv"
    bl.write_text(blocked + "\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))

    r = detect_pockets_p2rank(blocked)
    assert r["success"] is False
    assert "blocked" in r["error"].lower()


def test_t5_java_17_detected():
    """The tool's _find_java17 helper returns the OpenJDK-17 binary."""
    from biomni.tool.detect_pockets_p2rank import _find_java17

    java = _find_java17()
    assert java is not None
    assert "java" in Path(java).name
    assert Path(java).is_file()


def test_t5_runtime_under_threshold():
    """prank predict on 1AKE completes within 120 s."""
    if not FIX_1AKE_PDB.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE_PDB}")
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    t0 = time.perf_counter()
    r = detect_pockets_p2rank(str(FIX_1AKE_PDB))
    elapsed = time.perf_counter() - t0
    assert r["success"] is True
    assert elapsed < 120.0, f"runtime {elapsed:.2f}s exceeded 120s budget"
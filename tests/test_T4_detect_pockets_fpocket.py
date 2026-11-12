"""T4 detect_pockets_fpocket tests (Part 2).

These tests cover the criteria committed in docs/2_T4_criteria.md.
fpocket 4.2.3 must be on PATH (the alloagent-dev:phase1 image has
`/usr/local/bin/fpocket`); tests skip with a clear message when
the binary is not installed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE = REPO / "tests" / "fixtures" / "1ake.pdb"


def _has_fpocket() -> bool:
    return shutil.which("fpocket") is not None


pytestmark = pytest.mark.skipif(
    not _has_fpocket(),
    reason="fpocket 4.2.3 not installed in this env",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def _write_synthetic_pdb_with_hetatm(path: Path) -> int:
    """Write a minimal PDB with 3 HETATM lines; return HETATM count."""
    hetatm = (
        "HETATM    1 NA  Na   X   1      10.000  10.000  10.000  1.00  0.00          NA\n"
        "HETATM    2 CL  Cl   X   1      11.000  10.000  10.000  1.00  0.00          CL\n"
        "HETATM    3 MG  Mg   X   1      10.000  11.000  10.000  1.00  0.00          MG\n"
    )
    atoms = (
        "ATOM      1 N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N\n"
        "ATOM      2 CA  ALA A   1       1.500   0.000   0.000  1.00  0.00           C\n"
        "ATOM      3 C   ALA A   1       2.500   1.300   0.000  1.00  0.00           C\n"
        "ATOM      4 N   GLY A   2       3.800   0.000   0.000  1.00  0.00           N\n"
        "ATOM      5 CA  GLY A   2       5.000   0.000   0.000  1.00  0.00           C\n"
        "ATOM      6 C   GLY A   2       6.000   1.000   0.000  1.00  0.00           C\n"
        "ATOM      7 N   ALA A   3       8.000   0.000   0.000  1.00  0.00           N\n"
        "ATOM      8 CA  ALA A   3       9.500   0.000   0.000  1.00  0.00           C\n"
        "ATOM      9 C   ALA A   3      10.500   1.300   0.000  1.00  0.00           C\n"
    )
    text = (
        "HEADER    Synthetic test PDB\n"
        + atoms
        + hetatm
        + "END\n"
    )
    path.write_text(text, encoding="utf-8")
    return 3


def test_t4_recorded_1AKE_nonempty_pockets():
    """fpocket on the recorded 1AKE PDB returns >= 1 pocket with
    parsed score and druggability_score.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    r = detect_pockets_fpocket(str(FIX_1AKE))
    assert _contract_keys_present(r)
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE.stem
    assert isinstance(r["data"]["pockets"], list)
    assert len(r["data"]["pockets"]) >= 1, (
        f"expected >= 1 pocket, got {len(r['data']['pockets'])}"
    )
    first = r["data"]["pockets"][0]
    assert first["pocket_number"] == 1
    assert isinstance(first["score"], float)
    assert 0.0 <= first["score"] <= 1.0
    assert isinstance(first["druggability_score"], float)


def test_t4_parser_handles_negative_druggability_score():
    """A synthetic _info.txt with a negative Druggability Score
    value (-0.010) round-trips as a negative float.
    """
    from biomni.tool.detect_pockets_fpocket import _parse_info_txt

    text = (
        "Pocket 1 :\n"
        "\tScore : \t0.012\n"
        "\tDruggability Score : \t-0.010\n"
        "\tNumber of Alpha Spheres : \t12\n"
        "Pocket 2 :\n"
        "\tScore : \t0.500\n"
        "\tDruggability Score : \t-0.000\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_info.txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(text)
        info_path = Path(f.name)
    try:
        pockets = _parse_info_txt(info_path)
        assert len(pockets) == 2
        assert pockets[0]["druggability_score"] == -0.010
        assert pockets[1]["druggability_score"] == -0.0
    finally:
        info_path.unlink(missing_ok=True)


def test_t4_strip_hetatm_default_writes_clean_pdb(monkeypatch):
    """When strip_hetatm=True (the default) the tool writes a
    working copy with no HETATM lines for fpocket to read.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")

    from biomni.tool import detect_pockets_fpocket as _impl

    seen: dict = {}

    real_subprocess_run = _impl.subprocess.run
    real_tempdir = _impl.tempfile.TemporaryDirectory

    def fake_subprocess_run(cmd, **kwargs):
        if len(cmd) >= 3 and cmd[0] == "fpocket":
            work_in = Path(cmd[2])
            text = work_in.read_text(encoding="utf-8", errors="replace")
            seen["stripped"] = sum(
                1 for ln in text.splitlines() if ln.startswith("HETATM")
            )
            seen["input_was_strip_hetatm"] = work_in.parent.name.startswith(
                "alloagent_fpocket_"
            )
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="", stderr=""
            )
        return real_subprocess_run(cmd, **kwargs)

    monkeypatch.setattr(_impl.subprocess, "run", fake_subprocess_run)
    r = _impl.detect_pockets_fpocket(str(FIX_1AKE), strip_hetatm=True)
    assert r["success"] is True
    assert seen["stripped"] == 0
    assert seen["input_was_strip_hetatm"]


def test_t4_negative_control_non_pdb_input():
    """A non-existent path returns success=False with a clear error."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    r = detect_pockets_fpocket("/tmp/this-pdb-does-not-exist-xyzzy.pdb")
    assert r["success"] is False
    assert "does not exist" in r["error"].lower() or "not found" in r["error"].lower()


def test_t4_determinism():
    """Two calls with the same input return pocket lists with the
    same count and the same integer pocket numbers.

    fpocket uses a Monte Carlo alpha-sphere tessellation so
    per-pocket volumes may differ at the third decimal between
    runs. The structural fields -- pocket_number, score, and
    druggability_score -- are stable and asserted here.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    a = detect_pockets_fpocket(str(FIX_1AKE))["data"]["pockets"]
    b = detect_pockets_fpocket(str(FIX_1AKE))["data"]["pockets"]
    assert len(a) == len(b)
    nums_a = [p["pocket_number"] for p in a]
    nums_b = [p["pocket_number"] for p in b]
    assert nums_a == nums_b
    score_a = [round(p["score"], 3) for p in a]
    score_b = [round(p["score"], 3) for p in b]
    assert score_a == score_b
    drug_a = [round(p["druggability_score"], 3) for p in a]
    drug_b = [round(p["druggability_score"], 3) for p in b]
    assert drug_a == drug_b


def test_t4_lowercase_input_accepted():
    """A lowercase PDB path is accepted without error."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    r = detect_pockets_fpocket(str(FIX_1AKE).lower())
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE.stem


def test_t4_return_contract_keys_present():
    """Every call returns the 5 required contract keys."""
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    r = detect_pockets_fpocket("/tmp/this-pdb-does-not-exist-xyzzy.pdb")
    assert _contract_keys_present(r)
    assert r["source"] == "biomni.tool.detect_pockets_fpocket.detect_pockets_fpocket"
    assert r["source_version"] == "1.0"
    assert r["query_time_utc"].endswith("Z")


def test_t4_blocklist_short_circuits(tmp_path, monkeypatch):
    """The benchmark_blocklist decorator short-circuits a blocked PDB."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    blocked = str(FIX_1AKE)
    bl = tmp_path / "blocklist.tsv"
    bl.write_text(blocked + "\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))

    r = detect_pockets_fpocket(blocked)
    assert r["success"] is False
    assert "blocked" in r["error"].lower()


def test_t4_runtime_under_threshold():
    """fpocket on 1AKE completes within 60 s."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE PDB fixture not at {FIX_1AKE}")
    from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket

    t0 = time.perf_counter()
    r = detect_pockets_fpocket(str(FIX_1AKE))
    elapsed = time.perf_counter() - t0
    assert r["success"] is True
    assert elapsed < 60.0, f"runtime {elapsed:.2f}s exceeded 60s budget"
    assert r["data"]["runtime_s"] < 60.0
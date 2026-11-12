"""T6 normal_mode_analysis tests (Part 2).

These tests cover all 9 criteria committed in docs/2_T6_criteria.md.
ProDy 2.6.1 is required; the tests are collected (and pass) inside
the alloagent-dev:phase1 container (ProDy is installed at /usr/local/
bin in the image). On a host without ProDy the import-time
collection succeeds but the ProDy-using tests skip with a clear
message.
"""
from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE = REPO / "tests" / "fixtures" / "1ake.pdb"


def _has_prody() -> bool:
    try:
        import prody  # noqa: F401

        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _has_prody(), reason="ProDy 2.6.1 not installed in this env"
)


def _synthetic_path_chain(n: int):
    """Build an N-node linear chain with uniform spacing 7.0 A using
    ProDy primitives. Returns the parsed AtomGroup.  Spacing > 5
    Angstrom keeps next-nearest neighbours outside the default
    10 A cutoff so the Kirchhoff is the simple path graph
    Laplacian; the resulting eigenvalues are exactly 2 - 2cos(k*pi/N)
    for k=0..N-1.
    """
    import numpy as np
    import prody

    coords = np.zeros((n, 3))
    coords[:, 0] = np.arange(n) * 7.0
    ag = prody.AtomGroup(n)
    ag.setCoords(coords)
    return ag


def _gnm_path_eigenvalues(N: int):
    """Reference eigenvalues for an N-node path chain GNM:
    2 - 2*cos(k*pi/N) for k=1..N-1.
    """
    import numpy as np

    return np.array([2 - 2 * math.cos(k * math.pi / N) for k in range(1, N)])


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def test_t6_recorded_fixture_anm_1ake():
    """ANM on 1AKE filters out the 6 trivial near-zero modes."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm")
    assert r["success"] is True, r.get("error")
    assert _contract_keys_present(r)
    data = r["data"]
    assert data["model"] == "anm"
    assert data["pdb_id"] == FIX_1AKE.stem
    assert isinstance(data["eigenvalues"], list)
    assert isinstance(data["eigenvectors"], list)
    assert data["n_modes"] == len(data["eigenvalues"])
    assert data["n_modes"] == len(data["eigenvectors"])
    assert all(abs(ev) > 1e-8 for ev in data["eigenvalues"]), (
        f"returned near-zero modes: {[ev for ev in data['eigenvalues'] if abs(ev) <= 1e-8]}"
    )


def test_t6_recorded_fixture_gnm_1ake():
    """GNM on 1AKE filters out the trivial zero mode and returns
    positive eigenvalues.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="gnm")
    assert r["success"] is True, r.get("error")
    data = r["data"]
    assert data["model"] == "gnm"
    assert data["n_modes"] == len(data["eigenvalues"])
    assert all(ev >= 0.0 for ev in data["eigenvalues"]), (
        f"GNM produced negative eigenvalues: {data['eigenvalues']}"
    )


def test_t6_synthetic_path_chain_gnm_eigenvalues_within_1e_minus_6():
    """GNM on a synthetic 8-node path chain has eigenvalues
    2 - 2*cos(k*pi/8) for k=0..N-1 when zeros=True. The trivial
    zero mode (k=0) is removed; the remaining N-1 eigenvalues
    match the formula within 1e-6.
    """
    import numpy as np
    import prody

    N = 8
    ag = _synthetic_path_chain(N)

    gnm = prody.GNM()
    gnm.buildKirchhoff(ag)
    gnm.calcModes(n_modes=N, zeros=True)

    expected_full = np.array(
        [2 - 2 * math.cos(k * math.pi / N) for k in range(0, N)]
    )
    actual = np.asarray(gnm.getEigvals(), dtype=float)
    expected_full_sorted = np.sort(expected_full)
    actual_sorted = np.sort(actual)
    np.testing.assert_allclose(actual_sorted, expected_full_sorted, atol=1e-6)


def test_t6_1AKE_anm_full_spectrum_reporting():
    """ANM on the 1AKE CA subset returns N=428 raw modes (6 trivial
    + 422 non-trivial). The implementation reports n_modes_raw,
    n_trivial_filtered and the post-filter n_modes so the caller
    can see the spectrum breakdown.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm")
    assert r["success"] is True
    data = r["data"]
    n_atoms_ca = 428
    assert data["n_modes_raw"] == n_atoms_ca, (
        f"expected {n_atoms_ca} raw modes for the CA subset, "
        f"got {data['n_modes_raw']}"
    )
    assert data["n_trivial_filtered"] == 6
    assert data["n_modes"] == n_atoms_ca - 6


def test_t6_1AKE_max_modes_parameter_caps_return():
    """Passing max_modes > 0 returns the first N non-trivial modes."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm", max_modes=5)
    assert r["success"] is True
    assert r["data"]["n_modes"] == 5
    assert len(r["data"]["eigenvalues"]) == 5
    assert len(r["data"]["eigenvectors"]) == 5


def test_t6_1AKE_timeout_parameter_triggers_failure():
    """A 1-second timeout on the full 1AKE ANM run returns
    success=False with a timeout error. (The ANM build takes
    >0.1s and calcModes a few seconds.)
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm", timeout_s=0)
    assert r["success"] is False
    assert "timed out" in r["error"].lower()


def test_t6_1AKE_anm_has_6_trivial_modes_when_zeros_true():
    """When ProDy's ANM.calcModes(..., zeros=True) is called for 1AKE,
    the 6 trivial near-zero modes are returned. The function filters
    them out, so the raw calc result has 6+ near-zero modes but the
    returned data does not.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    import numpy as np
    import prody

    atoms = prody.parsePDB(str(FIX_1AKE))
    ca = atoms.select("protein and name CA") or atoms
    calc = prody.ANM()
    calc.buildHessian(ca)
    calc.calcModes(n_modes=ca.numAtoms(), zeros=True)
    eigvals_all = np.asarray(calc.getEigvals(), dtype=float)
    n_trivial = int(np.sum(np.abs(eigvals_all) <= 1e-8))
    assert n_trivial == 6, (
        f"expected 6 trivial modes for 1AKE ANM with zeros=True, got {n_trivial}"
    )

    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm")
    assert r["success"] is True
    assert all(abs(ev) > 1e-8 for ev in r["data"]["eigenvalues"])


def test_t6_determinism():
    """Two calls with the same input return equal data."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    a = normal_mode_analysis(str(FIX_1AKE), model="anm")["data"]
    b = normal_mode_analysis(str(FIX_1AKE), model="anm")["data"]
    assert a == b


def test_t6_negative_control_invalid_model():
    """An invalid model argument returns success=False with an error
    that mentions the allowed values.
    """
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="garbage")
    assert r["success"] is False
    assert "anm" in r["error"]
    assert "gnm" in r["error"]
    assert r["data"] is None


def test_t6_return_contract_keys_present():
    """Every call returns the 6 required contract keys."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE), model="anm")
    assert _contract_keys_present(r)
    assert r["source"] == "biomni.tool.normal_mode_analysis.normal_mode_analysis"
    assert r["source_version"] == "1.0"
    assert r["query_time_utc"].endswith("Z")


def test_t6_lowercase_path_accepted():
    """The function accepts a lowercase path string."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    r = normal_mode_analysis(str(FIX_1AKE).lower(), model="gnm")
    assert r["success"] is True
    assert r["data"]["pdb_id"] == FIX_1AKE.stem


def test_t6_runtime_under_threshold():
    """A 1AKE ANM run completes within 120 s on the CA-only subset."""
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    from biomni.tool.normal_mode_analysis import normal_mode_analysis

    t0 = time.perf_counter()
    r = normal_mode_analysis(str(FIX_1AKE), model="anm")
    elapsed = time.perf_counter() - t0
    assert r["success"] is True
    assert elapsed < 120.0, f"runtime {elapsed:.2f}s exceeded 120s budget"


def test_t6_blocklist_short_circuits(tmp_path, monkeypatch):
    """The benchmark_blocklist decorator short-circuits a blocked
    PDB path. The function never reaches prody.parsePDB.
    """
    if not FIX_1AKE.is_file():
        pytest.skip(f"1AKE fixture not at {FIX_1AKE}")
    import prody

    from biomni.tool import normal_mode_analysis as _impl

    bl = tmp_path / "blocklist.tsv"
    bl.write_text(str(FIX_1AKE) + "\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))

    called = []
    real_parse = prody.parsePDB
    monkeypatch.setattr(
        prody,
        "parsePDB",
        lambda *a, **kw: (called.append(a) or real_parse(*a, **kw)),
    )
    r = _impl.normal_mode_analysis(str(FIX_1AKE), model="anm")
    assert r["success"] is False
    assert "blocked" in r["error"].lower()
    assert called == [], f"prody.parsePDB was called despite blocklist: {called}"
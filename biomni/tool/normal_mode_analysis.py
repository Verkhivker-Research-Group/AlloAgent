"""T6 normal_mode_analysis (Part 2).

Anisotropic Network Model (ANM) and Gaussian Network Model (GNM)
normal mode analysis using ProDy 2.6.1. Always calls
`calcModes(..., zeros=True)` so the 6 trivial near-zero modes are
returned by ProDy, then filters them here before returning the
nonzero modes (within `ZERO_TOL` of 0.0).

The function is offline: it parses a PDB/mmCIF file from disk and
runs ProDy locally. The structure-file path is passed as `pdb_id`
for naming consistency with the tool card.
"""
from __future__ import annotations

import time
from pathlib import Path

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 60
_ZERO_TOL = 1e-8
_VALID_MODELS = ("anm", "gnm")

_MAX_MODES_DEFAULT = 0
"""Default max modes to compute (0 = full N). ProDy 2.6.1's ANM and
GNM compute an N x N (not 3N x 3N) Hessian from the heavy-atom
subset (CA-only by default). The output has N modes total: 6 trivial
near-zero modes (3 translations + 3 rotations of the body frame)
plus N - 6 non-trivial modes. On the 1AKE CA subset (N=428) this
gives 428 total modes -- 6 trivial + 422 non-trivial -- so the
returned `n_modes` field is 422 (the trivial modes are filtered by
abs(ev) > ZERO_TOL). This is NOT a cap; it is the full spectrum.
"""


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "ProDy 2.6.1 (ANM / GNM normal mode analysis)"


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def normal_mode_analysis(
    pdb_id,
    model: str = "anm",
    max_modes: int = _MAX_MODES_DEFAULT,
    timeout_s: int = _TIMEOUT_S,
):
    """Run ANM or GNM on a PDB / mmCIF file and return the nonzero
    normal modes.

    Parameters
    ----------
    pdb_id : str or Path
        A PDB or mmCIF file path.
    model : str
        Either ``"anm"`` (Anisotropic Network Model) or
        ``"gnm"`` (Gaussian Network Model).
    max_modes : int, default 0
        Maximum number of non-trivial modes to return. 0 means
        "all non-trivial modes" (the default; matches the full
        ProDy spectrum for the heavy-atom subset). When the CA
        subset is used, the ANM has N modes total (6 trivial plus
        N - 6 non-trivial); on 1AKE (N=428 CA atoms) the full
        non-trivial spectrum is 422 modes -- the
        ``n_modes`` field in ``data``. ProDy computes the full
        N-mode spectrum in both modes; the cap is a return-time
        cap only.
    timeout_s : int, default 60
        Soft wall-clock timeout (seconds). When the elapsed time
        exceeds this, the function returns
        ``success=False, error="normal_mode_analysis timed out
        after {timeout_s}s"``. ProDy 2.6.1 does not expose a
        native interrupt; the check is sampled between phases
        (parse -> build -> calcModes -> eigvals/eigvecs).

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "pdb_id": <file stem>,
                "model": "anm" or "gnm",
                "n_modes": <int>,
                "eigenvalues": [<float>, ...],
                "eigenvectors": [[<float>, ...], ...]
            }

        Only modes whose eigenvalue has ``abs(ev) > ZERO_TOL`` are
        returned (the trivial 6 near-zero modes for ANM and the
        trivial mode for GNM are filtered out).
    """
    import numpy as np
    import prody

    model_norm = model.lower().strip()
    if model_norm not in _VALID_MODELS:
        return {
            "success": False,
            "data": None,
            "error": (
                f"model must be one of {_VALID_MODELS} (got {model!r})"
            ),
        }

    pdb_path = Path(pdb_id)
    t_start = time.perf_counter()

    def _timeout_message():
        return f"normal_mode_analysis timed out after {timeout_s}s"

    def _elapsed_ok():
        return time.perf_counter() - t_start < timeout_s

    try:
        atoms = prody.parsePDB(str(pdb_path))
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"prody.parsePDB failed: {type(e).__name__}: {e}",
        }
    if not _elapsed_ok():
        return {"success": False, "data": None, "error": _timeout_message()}

    if atoms is None or atoms.numAtoms() == 0:
        return {
            "success": False,
            "data": None,
            "error": "prody parsed an empty structure",
        }

    ca = atoms.select("protein and name CA")
    if ca is None or ca.numAtoms() == 0:
        ca = atoms

    try:
        if model_norm == "anm":
            calc = prody.ANM()
            calc.buildHessian(ca)
        else:
            calc = prody.GNM()
            calc.buildKirchhoff(ca)
        n_modes_total = calc.numAtoms()
        calc.calcModes(n_modes=n_modes_total, zeros=True)
        eigvals_all = np.asarray(calc.getEigvals(), dtype=float)
        eigvecs_all = np.asarray(calc.getArray(), dtype=float)
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"calcModes failed: {type(e).__name__}: {e}",
        }
    if not _elapsed_ok():
        return {"success": False, "data": None, "error": _timeout_message()}

    mask = np.abs(eigvals_all) > _ZERO_TOL
    filtered_eigvals = [float(v) for v in eigvals_all[mask].tolist()]
    filtered_eigvecs = [
        [float(x) for x in eigvecs_all[i].tolist()]
        for i in range(eigvals_all.shape[0])
        if mask[i]
    ]

    if max_modes > 0 and len(filtered_eigvals) > max_modes:
        filtered_eigvals = filtered_eigvals[:max_modes]
        filtered_eigvecs = filtered_eigvecs[:max_modes]

    return {
        "success": True,
        "data": {
            "pdb_id": pdb_path.stem,
            "model": model_norm,
            "n_modes": len(filtered_eigvals),
            "eigenvalues": filtered_eigvals,
            "eigenvectors": filtered_eigvecs,
            "n_modes_raw": int(eigvals_all.shape[0]),
            "n_trivial_filtered": int(eigvals_all.shape[0]) - int(mask.sum()),
        },
    }
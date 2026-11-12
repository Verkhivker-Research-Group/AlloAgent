"""B3 PocketMiner wrapper (Part 2 / batch 2).

PocketMiner (Meller et al. 2023) predicts MD-defined pocket-opening
propensity (cryptic pockets), not allosteric sites specifically.

This wrapper runs PocketMiner in a subprocess using the
`pocketminer_env` conda env (tf 2.15, np 1.26.4, mdtraj 1.11.1).
The env must be built first via the layered Dockerfile in this
repo (see docker/patches/apply_legacy_adam.py for the
tf.keras.optimizers.legacy.Adam build-time patch).

PocketMiner is NOT a self-reported-accuracy predictor; see the
tool card for details.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_POCKETMINER_PYTHON = Path("/opt/conda/envs/pocketminer_env/bin/python")
_POCKETMINER_DIR = Path("/opt/pocketminer")
_POCKETMINER_NN_PREFIX = _POCKETMINER_DIR / "models" / "pocketminer"
_POCKETMINER_NN_DATA = _POCKETMINER_NN_PREFIX.with_suffix(".data-00000-of-00001")
_POCKETMINER_NN_INDEX = _POCKETMINER_NN_PREFIX.with_suffix(".index")
_POCKETMINER_WEIGHTS_SHA = Path("/opt/pocketminer_weights.sha256")
_POCKETMINER_GIT_COMMIT = "187062df3c94127e991669768009141a08fd5d8b"
_TIMEOUT_S = 600
# Maximum number of protein residues the PocketMiner GVP model
# can process. Structures with more residues exceed the model's
# fixed input size and produce a raw TensorFlow exception. The
# pre-check in pocketminer_score() returns a clear error before
# attempting inference. 8hc1 (15468 residues) is the only
# known test-split structure above this limit.
_MAX_RESIDUES = 10000


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return f"PocketMiner (Mickdub/gvp) @ {_POCKETMINER_GIT_COMMIT}"


def _read_git_commit(repo_dir: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip()
        return out
    except Exception:
        return _POCKETMINER_GIT_COMMIT


def _read_sha256(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8").strip().split()[0]
    except Exception:
        return None


_INFERENCE_SCRIPT = """
import json
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, "{pocketminer_src}")

import numpy as np
import mdtraj as md

from models import MQAModel
from validate_performance_on_xtals import process_strucs, predict_on_xtals

pdb_path = sys.argv[1]
output_path = sys.argv[2]

DROPOUT_RATE = 0.1
NUM_LAYERS = 4
HIDDEN_DIM = 100
model = MQAModel(
    node_features=(8, 50), edge_features=(1, 32),
    hidden_dim=(16, HIDDEN_DIM),
    num_layers=NUM_LAYERS, dropout=DROPOUT_RATE,
)

struc = md.load(pdb_path)

# Pre-processing: handle nonstandard amino acid residues and
# nonstandard backbone atom counts. PocketMiner's process_strucs
# uses a fixed lookup dict (abbrev + lookup in
# validate_performance_on_xtals.py) that only covers the 20
# standard amino acids. PDB structures from CryptoBench contain
# nonstandard residues (e.g. MSE = selenomethionine,
# DPP = D-phenylalanine) that cause KeyError. Additionally,
# some residues have nonstandard backbone atom counts (missing
# O atom or multiple O atoms from alternate conformations) that
# cause reshape errors in process_strucs. This pre-processing
# step:
# 1. Monkey-patches the abbrev dict to map nonstandard residues
#    to their standard parent 1-letter codes.
# 2. Filters residues with nonstandard backbone atom counts
#    (not exactly 4 backbone atoms: N, CA, C, O).
import validate_performance_on_xtals as _vpx
_NONSTANDARD_TO_STANDARD = {{
    # Selenocysteine/selenomethionine
    'MSE': 'MET', 'SEC': 'CYS', 'CSO': 'CYS', 'CSD': 'CYS',
    'CME': 'CYS', 'SMC': 'CYS', 'SCY': 'CYS', 'OCS': 'CYS',
    'MHO': 'MET', 'OMT': 'MET', 'M3L': 'LYS', 'MLY': 'LYS',
    'TPO': 'THR', 'PTR': 'TYR', 'SEP': 'SER', 'TYS': 'TYR',
    'MLZ': 'LYS',
    # D-amino acids
    'DPP': 'PHE', 'DGL': 'GLU', 'DAS': 'ASP', 'DHI': 'HIS',
    'DLY': 'LYS', 'DLE': 'LEU', 'DVA': 'VAL', 'DTR': 'TRP',
    'DTY': 'TYR', 'DTH': 'THR', 'DSER': 'SER', 'DCY': 'CYS',
    'DGN': 'GLN', 'DAR': 'ARG',
    # Protonated / modified forms
    'HIC': 'HIS', 'HSD': 'HIS', 'HIP': 'HIS', 'ASH': 'ASP',
    'GLH': 'GLU', 'ALY': 'LYS', 'SLZ': 'LYS', 'UN1': 'ALA',
    'HS8': 'HIS', 'MIS': 'MET',
}}
# Catch-all: any residue name not in the standard 20 and not
# in the mapping above is renamed to GLY (safest default since
# GLY has no side chain and the model's residue-type lookup only
# needs a valid code, not a chemically accurate one).
# Ligands (e.g. '2CO', 'HEM', 'ATP') are caught here too.
_STANDARD_AA = {{'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU',
                'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE',
                'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL'}}
for _res in struc.top.residues:
    if _res.name not in _STANDARD_AA and _res.name not in _NONSTANDARD_TO_STANDARD:
        _res.name = 'GLY'
_vpx.abbrev.update({{k: _vpx.abbrev[v] for k, v in _NONSTANDARD_TO_STANDARD.items() if v in _vpx.abbrev}})

# Filter residues with nonstandard backbone atom counts
_backbone_sel = struc.top.select("protein and (name N or name CA or name C or name O)")
_res_bb_count = {{}}
for _atom_idx in _backbone_sel:
    _res_idx = struc.top.atom(_atom_idx).residue.index
    _res_bb_count[_res_idx] = _res_bb_count.get(_res_idx, 0) + 1
_valid_residues = {{r for r, c in _res_bb_count.items() if c == 4}}
_all_residues = set(range(struc.n_residues))
_invalid_residues = _all_residues - _valid_residues
if _invalid_residues:
    _valid_atom_indices = [i for i in range(struc.n_atoms)
                           if struc.top.atom(i).residue.index in _valid_residues]
    struc = struc.atom_slice(_valid_atom_indices)

X, S, mask = process_strucs([struc])
preds = predict_on_xtals(
    model, "{nn_path}", X, S, mask,
)
preds_np = np.asarray(preds)

# PocketMiner returns shape (1, n_residues) -- one sigmoid score
# per standard residue (in the order the 4-atom backbone blocks
# appear in the input structure). 1AKE loaded by mdtraj reports
# 428 standard residues (chains A and B as a single complex).
# Verified against Phase 2c reproduction: first 5 values for
# 1AKE are 0.5353, 0.7912, 0.7100, 0.8246, 0.8816.
n_residues = int(preds_np.shape[-1])
per_residue = preds_np.flatten()

# The chain and the residue number of every scored residue, in the
# same order as the scores (docs/1_pocketminer_criteria.md).
_chain_ids = {{chain.index: str(chain.chain_id) for chain in struc.top.chains}}
residue_meta = []
for _residue in struc.top.residues:
    try:
        _residue_number = int(_residue.resSeq)
    except (TypeError, ValueError):
        _residue_number = None
    residue_meta.append({{
        "chain": _chain_ids.get(_residue.chain.index, str(_residue.chain.index)),
        "residue_number": _residue_number,
        "residue_name": str(_residue.name),
    }})

result = {{
    "residue_scores": per_residue.tolist(),
    "n_residues": n_residues,
    "residues": residue_meta,
    "model": "PocketMiner",
    "git_commit": "{pocketminer_commit}",
}}
with open(output_path, "w") as f:
    json.dump(result, f)
"""


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def pocketminer_score(pdb_path: str):
    """Score residues in a PDB structure for cryptic-pocket propensity.

    Parameters
    ----------
    pdb_path : str
        Path to the PDB file to score.

    Returns
    -------
    dict
        Contract dict with ``residue_scores`` (list of floats, one
        per residue in the PDB, in [0, 1]), the model git commit,
        and the weights SHA256.

        The result also carries the result **per chain**:
        ``residues`` is the list of ``{chain, residue_number,
        residue_name, score}`` in the order of ``residue_scores``,
        ``chains`` maps each chain to ``{n_residues, mean, min, max,
        residue_numbers}``, and ``all_residue_mean`` is the mean over
        every scored residue.  There is deliberately no field that
        mixes the chains of a multi-chain structure into a single
        number (docs/1_pocketminer_criteria.md).

    PocketMiner predicts MD-defined pocket-opening propensity
    (cryptic pockets), not allosteric sites specifically.

    Notes
    -----
    The output scores are SCREENING EVIDENCE for potential
    cryptic-pocket-forming residues, not a quantitative
    prediction of cryptic-pocket geometry or opening
    probability. The model was trained on a 37-apo-structure
    set and evaluated on a subset of the CryptoBench benchmark.

    On the independent CryptoBench test split (222 apo
    structures), performance is modest: per-protein AUC
    mean = 0.650 (bootstrap 95% CI [0.622, 0.677]),
    pooled residue-level AUC = 0.649, with 78% of proteins
    scoring above chance. These numbers are screening-grade,
    not assay-grade. Do not treat a high score as a positive
    identification of a cryptic pocket without orthogonal
    evidence (e.g. MD simulation, experimental validation).

    Failure modes: this function returns ``{"success": False,
    "error": "..."}`` for (a) missing file, (b) absent or
    corrupt PocketMiner model checkpoint, (c) TensorFlow
    inference errors (e.g. very large complexes exceeding
    the model's residue capacity), and (d) structures with
    nonstandard backbone atom counts that cannot be reshape
    to the model's input. The error string names the specific
    cause. The wrapper applies a pre-processing step that
    renames common nonstandard residues (MSE, DPP, etc.) to
    their standard parents and filters residues with
    nonstandard backbone counts; structures that still fail
    after this pre-processing return a clear error.
    """
    if not isinstance(pdb_path, str) or not pdb_path:
        return {
            "success": False,
            "error": f"pdb_path must be a non-empty string, got {pdb_path!r}",
        }
    pdb = Path(pdb_path)
    if not pdb.is_file():
        return {
            "success": False,
            "error": f"PDB file not found: {pdb_path}",
        }
    if not _POCKETMINER_PYTHON.is_file():
        return {
            "success": False,
            "error": (
                f"pocketminer_env not built ({_POCKETMINER_PYTHON} not found); "
                f"rebuild the Docker image with the layered Dockerfile"
            ),
        }
    if not _POCKETMINER_DIR.is_dir():
        return {
            "success": False,
            "error": (
                f"PocketMiner repo not found at {_POCKETMINER_DIR}; "
                f"rebuild the Docker image with the layered Dockerfile"
            ),
        }
    if not (_POCKETMINER_NN_DATA.is_file() and _POCKETMINER_NN_INDEX.is_file()):
        return {
            "success": False,
            "error": (
                f"PocketMiner checkpoint not found at "
                f"{_POCKETMINER_NN_PREFIX}{{data-00000-of-00001,index}}"
            ),
        }

    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="pocketminer_") as tmp_str:
        tmp = Path(tmp_str)
        out_path = tmp / "result.json"
        script_path = tmp / "infer.py"
        # Pre-check: count protein residues. The PocketMiner GVP
        # model has a fixed input size; structures with more than
        # _MAX_RESIDUES residues exceed the model's capacity and
        # produce a raw TensorFlow exception. Return a clear
        # error instead.
        try:
            import gemmi
            _st = gemmi.read_structure(str(pdb))
            _st.remove_waters()
            _n_res = 0
            for _model in _st:
                for _chain in _model:
                    for _residue in _chain:
                        if _residue.name in {
                            "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU",
                            "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE",
                            "PRO", "SER", "THR", "TRP", "TYR", "VAL",
                        }:
                            _n_res += 1
            if _n_res > _MAX_RESIDUES:
                return {
                    "success": False,
                    "error": (
                        f"Structure too large: {_n_res} protein residues "
                        f"exceeds PocketMiner model capacity "
                        f"({_MAX_RESIDUES} residues). The GVP model has a "
                        f"fixed input size; consider splitting the "
                        f"structure or using a subset of chains."
                    ),
                }
        except Exception:
            pass  # If the pre-check fails, proceed to the model
        script_path.write_text(
            _INFERENCE_SCRIPT.format(
                pocketminer_src=str(_POCKETMINER_DIR / "src"),
                nn_path=str(_POCKETMINER_NN_PREFIX),
                pocketminer_commit=_read_git_commit(_POCKETMINER_DIR),
            ),
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [str(_POCKETMINER_PYTHON), str(script_path), str(pdb), str(out_path)],
                capture_output=True, text=True, timeout=_TIMEOUT_S,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"PocketMiner timed out after {_TIMEOUT_S}s",
            }
        if result.returncode != 0:
            return {
                "success": False,
                "error": (
                    f"PocketMiner exited with code {result.returncode}: "
                    f"{result.stderr[:400]}"
                ),
            }
        if not out_path.is_file() or out_path.stat().st_size == 0:
            return {
                "success": False,
                "error": "PocketMiner output file missing or empty",
            }
        try:
            data = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": f"PocketMiner output is not valid JSON: {exc}",
            }
        if "residue_scores" not in data or not isinstance(data["residue_scores"], list):
            return {
                "success": False,
                "error": "PocketMiner output missing 'residue_scores' list",
            }
        if len(data["residue_scores"]) == 0:
            return {
                "success": False,
                "error": "PocketMiner output 'residue_scores' is empty",
            }

    elapsed = time.monotonic() - t0

    scores = data["residue_scores"]
    residue_meta = data.get("residues")
    chain_report: dict[str, Any] = {}
    all_residue_mean: Optional[float] = None
    residue_rows: list[dict[str, Any]] = []
    chain_note: Optional[str] = None
    if not isinstance(residue_meta, list) or len(residue_meta) != len(scores):
        chain_note = (
            "the per-residue chain information is not available for this "
            f"structure ({len(residue_meta) if isinstance(residue_meta, list) else 'absent'} "
            f"entries for {len(scores)} scores), so no per-chain result is reported"
        )
    else:
        per_chain: dict[str, list[float]] = {}
        per_chain_numbers: dict[str, list[int]] = {}
        for meta, score in zip(residue_meta, scores):
            chain_name = str(meta.get("chain", ""))
            number = meta.get("residue_number")
            per_chain.setdefault(chain_name, []).append(float(score))
            if number is not None:
                per_chain_numbers.setdefault(chain_name, []).append(int(number))
            residue_rows.append(
                {
                    "chain": chain_name,
                    "residue_number": number,
                    "residue_name": meta.get("residue_name"),
                    "score": float(score),
                }
            )
        chain_report = {
            chain_name: {
                "n_residues": len(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "residue_numbers": sorted(per_chain_numbers.get(chain_name, [])),
            }
            for chain_name, values in sorted(per_chain.items())
        }
        all_residue_mean = sum(float(score) for score in scores) / len(scores)

    return {
        "success": True,
        "data": {
            "residue_scores": scores,
            "residues": residue_rows,
            "chains": chain_report,
            "all_residue_mean": all_residue_mean,
            "chain_mapping_note": chain_note,
            "n_residues": data.get("n_residues", len(scores)),
            "source": f"PocketMiner@{_read_git_commit(_POCKETMINER_DIR)}",
            "weights_sha256": _read_sha256(_POCKETMINER_WEIGHTS_SHA),
            "runtime_seconds": elapsed,
        },
    }

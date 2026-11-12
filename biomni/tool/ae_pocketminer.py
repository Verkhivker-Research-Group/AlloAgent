"""B3 AE-PocketMiner wrapper (Part 2 / batch 2).

AE-PocketMiner (Meller et al. 2024, experimental autoencoder
variant) is NOT on the default exposed list (it's an
unreplicated preprint). It is wrapped here for completeness
but is only accessible via direct import, not via the
biomni/exposed_tools.txt registry.

This wrapper runs AE-PocketMiner in a subprocess using the
`pocketminer_env` conda env (tf 2.15, np 1.26.4, mdtraj 1.11.1).
The env must be built first via the layered Dockerfile in this
repo (see docker/patches/apply_legacy_adam.py for the
tf.keras.optimizers.legacy.Adam build-time patch).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_AE_POCKETMINER_PYTHON = Path("/opt/conda/envs/pocketminer_env/bin/python")
_AE_POCKETMINER_DIR = Path("/opt/ae-pocketminer")
_AE_POCKETMINER_NN_PREFIX = _AE_POCKETMINER_DIR / "models" / "aepocketminer"
_AE_POCKETMINER_NN_DATA = _AE_POCKETMINER_NN_PREFIX.with_suffix(".data-00000-of-00001")
_AE_POCKETMINER_NN_INDEX = _AE_POCKETMINER_NN_PREFIX.with_suffix(".index")
_AE_POCKETMINER_WEIGHTS_SHA = Path("/opt/ae-pocketminer_weights.sha256")
_AE_POCKETMINER_GIT_COMMIT = "3328ca0376d3e4959545bac35e036435d582ff2e"
_TIMEOUT_S = 600


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return f"AE-PocketMiner @ {_AE_POCKETMINER_GIT_COMMIT}"


def _read_git_commit(repo_dir: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip()
        return out
    except Exception:
        return _AE_POCKETMINER_GIT_COMMIT


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
sys.path.insert(0, "{aepm_src}")

import numpy as np
import mdtraj as md
import tensorflow as tf
from tensorflow.keras.optimizers.legacy import Adam as AdamLegacy

from models import MQAModel
from util import load_checkpoint
import xtal_predict as xp

pdb_path = sys.argv[1]
output_path = sys.argv[2]

DROPOUT_RATE = 0.1
NUM_LAYERS = 4
HIDDEN_DIM = 100
NUM_HEADS = 2
SAVE_ATTN = True
ATTN_FILENAME = "attention_weights.npy"

model = MQAModel(
    node_features=(8, 50),
    edge_features=(1, 32),
    hidden_dim=(16, HIDDEN_DIM),
    attention_heads=NUM_HEADS,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT_RATE,
    use_attention=True,
    save_attention_weights=SAVE_ATTN,
    attention_weights_filename=ATTN_FILENAME,
)

opt = AdamLegacy()
load_checkpoint(model, opt, "{nn_path}")

predictions = xp.make_predictions([pdb_path], model)
preds_np = np.asarray(predictions)

# AE-PocketMiner returns shape (1, n_residues) -- one sigmoid
# score per standard residue. 1AKE loaded by mdtraj reports
# 428 standard residues; attention shape is (1, 2, 428, 428).
n_residues = int(preds_np.shape[-1])
per_residue = preds_np.flatten()

attention_weights = None
if SAVE_ATTN and os.path.exists(ATTN_FILENAME):
    attention_weights = np.load(ATTN_FILENAME)
    os.remove(ATTN_FILENAME)

result = {{
    "residue_scores": per_residue.tolist(),
    "n_residues": n_residues,
    "attention_weights_shape": list(attention_weights.shape) if attention_weights is not None else None,
    "model": "AE-PocketMiner",
    "git_commit": "{aepm_commit}",
}}
with open(output_path, "w") as f:
    json.dump(result, f)
"""


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def ae_pocketminer_score(pdb_path: str):
    """Score residues for cryptic-pocket propensity (experimental).

    AE-PocketMiner is experimental (unreplicated preprint) and
    is NOT on the default exposed list. Use only for research
    purposes; do not quote as a validated predictor.

    Parameters
    ----------
    pdb_path : str
        Path to the PDB file to score.

    Returns
    -------
    dict
        Contract dict with ``residue_scores`` (list of floats, one
        per residue in the PDB, in [0, 1]) and the model git
        commit. ``attention_weights_shape`` is set to
        ``[1, 2, n_residues, n_residues]`` when the model emits
        attention weights; ``None`` if it didn't.
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
    if not _AE_POCKETMINER_PYTHON.is_file():
        return {
            "success": False,
            "error": (
                f"pocketminer_env not built ({_AE_POCKETMINER_PYTHON} not found); "
                f"rebuild the Docker image with the layered Dockerfile"
            ),
        }
    if not _AE_POCKETMINER_DIR.is_dir():
        return {
            "success": False,
            "error": (
                f"AE-PocketMiner repo not found at {_AE_POCKETMINER_DIR}; "
                f"rebuild the Docker image with the layered Dockerfile"
            ),
        }
    if not (_AE_POCKETMINER_NN_DATA.is_file() and _AE_POCKETMINER_NN_INDEX.is_file()):
        return {
            "success": False,
            "error": (
                f"AE-PocketMiner checkpoint not found at "
                f"{_AE_POCKETMINER_NN_PREFIX}{{data-00000-of-00001,index}}"
            ),
        }

    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="ae_pocketminer_") as tmp_str:
        tmp = Path(tmp_str)
        out_path = tmp / "result.json"
        script_path = tmp / "infer.py"
        script_path.write_text(
            _INFERENCE_SCRIPT.format(
                aepm_src=str(_AE_POCKETMINER_DIR / "src"),
                nn_path=str(_AE_POCKETMINER_NN_PREFIX),
                aepm_commit=_read_git_commit(_AE_POCKETMINER_DIR),
            ),
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [str(_AE_POCKETMINER_PYTHON), str(script_path), str(pdb), str(out_path)],
                capture_output=True, text=True, timeout=_TIMEOUT_S,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"AE-PocketMiner timed out after {_TIMEOUT_S}s",
            }
        if result.returncode != 0:
            return {
                "success": False,
                "error": (
                    f"AE-PocketMiner exited with code {result.returncode}: "
                    f"{result.stderr[:400]}"
                ),
            }
        if not out_path.is_file() or out_path.stat().st_size == 0:
            return {
                "success": False,
                "error": "AE-PocketMiner output file missing or empty",
            }
        try:
            data = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": f"AE-PocketMiner output is not valid JSON: {exc}",
            }
        if "residue_scores" not in data or not isinstance(data["residue_scores"], list):
            return {
                "success": False,
                "error": "AE-PocketMiner output missing 'residue_scores' list",
            }
        if len(data["residue_scores"]) == 0:
            return {
                "success": False,
                "error": "AE-PocketMiner output 'residue_scores' is empty",
            }

    elapsed = time.monotonic() - t0
    return {
        "success": True,
        "data": {
            "residue_scores": data["residue_scores"],
            "n_residues": data.get("n_residues", len(data["residue_scores"])),
            "attention_weights_shape": data.get("attention_weights_shape"),
            "source": f"AE-PocketMiner@{_read_git_commit(_AE_POCKETMINER_DIR)}",
            "weights_sha256": _read_sha256(_AE_POCKETMINER_WEIGHTS_SHA),
            "runtime_seconds": elapsed,
        },
    }

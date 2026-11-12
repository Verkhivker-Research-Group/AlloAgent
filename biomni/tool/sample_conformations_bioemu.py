"""BioEmu conformational sampling (own conda env, CUDA).

Runs BioEmu in `/opt/conda/envs/bioemu_env` (torch >= 2.5 with the CUDA
wheels) in a subprocess.  The weights are downloaded to the **data
root**, not into the image.

The samples are model outputs, not measurements; no published accuracy
figure is quoted here.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

import requests

from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 3600
_BIOEMU_PYTHON = Path("/opt/conda/envs/bioemu_env/bin/python")
_DATA_ROOT = Path(os.environ.get("ALLOAGENT_DATA_ROOT", "/biolab_data"))
_WEIGHTS_DIR = _DATA_ROOT / "bioemu_weights"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "BioEmu (facebookresearch/bioemu) in /opt/conda/envs/bioemu_env"


def _gpu_report() -> dict[str, Any]:
    if not _BIOEMU_PYTHON.is_file():
        return {"available": False,
                "error": f"bioemu_env is not built ({_BIOEMU_PYTHON} not found); "
                          f"rebuild the image with the GPU env"}
    script = (
        "import json, torch;"
        "print(json.dumps({'torch': torch.__version__,"
        "'cuda_build': torch.version.cuda,"
        "'available': torch.cuda.is_available(),"
        "'device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,"
        "'vram_MiB': int(torch.cuda.get_device_properties(0).total_memory/1048576) "
        "if torch.cuda.is_available() else None}))"
    )
    try:
        out = subprocess.run([str(_BIOEMU_PYTHON), "-c", script], capture_output=True,
                             text=True, timeout=300)
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"the GPU probe failed: {exc!r}"}
    if out.returncode != 0:
        return {"available": False,
                "error": f"the GPU probe failed: {out.stderr.strip()[:300]}"}
    try:
        report = json.loads(out.stdout.strip().splitlines()[-1])
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"the GPU probe output was unreadable: {exc!r}"}
    if not report.get("available"):
        report["error"] = ("no CUDA device is visible to bioemu_env "
                           f"(torch {report.get('torch')}, CUDA build "
                           f"{report.get('cuda_build')})")
    return report


@with_return_contract(source_version="1.0")
def sample_conformations_bioemu(
    sequence: Optional[str] = None,
    uniprot_id: Optional[str] = None,
    n_samples: int = 20,
    out_dir: Optional[str] = None,
):
    """Sample conformations of a protein with BioEmu.

    Parameters
    ----------
    sequence : str or None
        The protein sequence, as a plain one-letter string.
    uniprot_id : str or None
        A UniProt accession to fetch the sequence for (used when
        ``sequence`` is not given).
    n_samples : int
        How many conformers to sample (default 20).
    out_dir : str or None
        Where to write the samples.  Defaults to a directory under the
        data root.

    Returns
    -------
    dict
        Contract dict.  On success ``data`` carries the sample paths,
        the GPU report and the runtime.  **The samples are model
        outputs, not measurements**, and this tool quotes no published
        accuracy figure.
    """
    if not sequence and not uniprot_id:
        return {"success": False,
                "error": "either sequence or uniprot_id must be given"}
    if n_samples < 1:
        return {"success": False, "error": f"n_samples must be >= 1, got {n_samples}"}

    gpu = _gpu_report()
    if not gpu.get("available"):
        return {"success": False, "error": gpu.get("error"), "gpu": gpu}

    if not sequence:
        try:
            response = requests.get(
                f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta", timeout=120)
            response.raise_for_status()
            sequence = "".join(
                line.strip() for line in response.text.splitlines()
                if line and not line.startswith(">"))
        except Exception as exc:  # noqa: BLE001
            return {"success": False,
                    "error": f"could not fetch the sequence of {uniprot_id}: {exc!r}"}

    work = Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix="bioemu_"))
    work.mkdir(parents=True, exist_ok=True)
    _WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    fasta_path = work / "input.fasta"
    fasta_path.write_text(f">target\n{sequence}\n", encoding="utf-8")

    script = f"""
import json, os, sys
os.environ.setdefault("HF_HOME", "{_WEIGHTS_DIR}")
from bioemu.sample import main
main(sequence="{fasta_path}", num_samples={n_samples}, output_dir="{work}")
"""
    script_path = work / "run_bioemu.py"
    script_path.write_text(script, encoding="utf-8")

    started = time.monotonic()
    try:
        result = subprocess.run(
            [str(_BIOEMU_PYTHON), str(script_path)],
            capture_output=True, text=True, timeout=_TIMEOUT_S, cwd=str(work),
            env={**os.environ, "HF_HOME": str(_WEIGHTS_DIR)},
        )
    except subprocess.TimeoutExpired:
        return {"success": False,
                "error": f"BioEmu timed out after {_TIMEOUT_S}s",
                "gpu": gpu}
    elapsed = time.monotonic() - started
    if result.returncode != 0:
        return {"success": False,
                "error": f"BioEmu failed (exit {result.returncode}): "
                          f"{result.stderr.strip()[-600:]}",
                "gpu": gpu, "runtime_seconds": round(elapsed, 2)}

    sample_batches = sorted(str(path) for path in work.rglob("batch_*.npz"))
    trajectories = sorted(str(path) for path in work.rglob("*.xtc"))
    topologies = sorted(str(path) for path in work.rglob("topology.pdb"))
    return {
        "success": True,
        "data": {
            "sample_paths": sample_batches,
            "trajectory_paths": trajectories,
            "topology_paths": topologies,
            "n_samples": n_samples,
            "coordinates_unit": "nanometres (the BioEmu samples are written in nm; "
                                "multiply by 10 to get angstroms)",
            "gpu": gpu,
            "runtime_seconds": round(elapsed, 2),
            "weights_dir": str(_WEIGHTS_DIR),
            "note": "the samples are model outputs, not measurements; no published "
                    "accuracy is quoted here",
        },
    }

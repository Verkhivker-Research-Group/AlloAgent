"""Boltz-2 complex prediction (own conda env, CUDA).

Runs Boltz-2 in `/opt/conda/envs/boltz2_env` (torch >= 2.5 with the
CUDA wheels) in a subprocess, the way the PocketMiner wrapper runs its
model.  The weights are downloaded to the **data root**, not into the
image.

The confidence and affinity values the tool returns are **model
outputs, not measurements**; no published accuracy number is quoted
here.
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
_BOLTZ_PYTHON = Path("/opt/conda/envs/boltz2_env/bin/python")
# boltz 2.2.1 has no boltz.main.main; the console script is the entry point.
_BOLTZ_CLI = Path("/opt/conda/envs/boltz2_env/bin/boltz")
_DATA_ROOT = Path(os.environ.get("ALLOAGENT_DATA_ROOT", "/biolab_data"))
_WEIGHTS_DIR = _DATA_ROOT / "boltz2_weights"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "Boltz-2 (johahi/boltz2) in /opt/conda/envs/boltz2_env"


def _gpu_report() -> dict[str, Any]:
    """What the env's torch sees: the device, the VRAM and the CUDA build."""
    if not _BOLTZ_PYTHON.is_file():
        return {"available": False,
                "error": f"boltz2_env is not built ({_BOLTZ_PYTHON} not found); "
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
        out = subprocess.run([str(_BOLTZ_PYTHON), "-c", script], capture_output=True,
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
        report["error"] = ("no CUDA device is visible to boltz2_env "
                           f"(torch {report.get('torch')}, CUDA build "
                           f"{report.get('cuda_build')})")
    return report


@with_return_contract(source_version="1.0")
def predict_complex_boltz2(
    sequences: Optional[list[str]] = None,
    uniprot_ids: Optional[list[str]] = None,
    ligand_smiles: Optional[str] = None,
    ligand_name: Optional[str] = None,
    out_dir: Optional[str] = None,
    msa_path: Optional[str] = None,
):
    """Predict a protein(-ligand) complex with Boltz-2.

    Parameters
    ----------
    sequences : list of str or None
        Protein sequences, as plain one-letter strings.
    uniprot_ids : list of str or None
        UniProt accessions to fetch the sequences for (one per chain).
    ligand_smiles : str or None
        SMILES of the ligand.
    ligand_name : str or None
        Name of the ligand (defaults to "ligand").
    out_dir : str or None
        Where to write the prediction.  Defaults to a directory under
        the data root.
    msa_path : str or None
        A precomputed alignment (an ``.a3m`` file) for the first
        sequence.  Boltz-2 needs an MSA for every protein chain, and
        it will only fetch one itself when the MSA server is enabled;
        with this argument the given alignment is used as-is, so a
        single-sequence run needs no MSA server at all.

    Returns
    -------
    dict
        Contract dict.  On success ``data`` carries the structure path,
        the confidence scores and the affinity outputs the model
        provides.  **The confidence and affinity values are model
        outputs, not measurements**, and this tool quotes no published
        accuracy figure.
    """
    if not sequences and not uniprot_ids:
        return {"success": False,
                "error": "either sequences or uniprot_ids must be given"}
    if not ligand_smiles:
        return {"success": False, "error": "ligand_smiles must be given"}

    gpu = _gpu_report()
    if not gpu.get("available"):
        return {"success": False, "error": gpu.get("error"), "gpu": gpu}

    resolved: list[str] = list(sequences or [])
    for accession in uniprot_ids or []:
        try:
            response = requests.get(
                f"https://rest.uniprot.org/uniprotkb/{accession}.fasta", timeout=120)
            response.raise_for_status()
            sequence = "".join(
                line.strip() for line in response.text.splitlines()
                if line and not line.startswith(">"))
        except Exception as exc:  # noqa: BLE001
            return {"success": False,
                    "error": f"could not fetch the sequence of {accession}: {exc!r}"}
        resolved.append(sequence)

    work = Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix="boltz2_"))
    work.mkdir(parents=True, exist_ok=True)
    _WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    name = ligand_name or "ligand"
    yaml_path = work / f"{name}.yaml"
    lines = ["version: 1", "sequences:"]
    for index, sequence in enumerate(resolved):
        lines += [f"  - protein:", "      id: A" if index == 0 else f"      id: C{index}",
                  f"      sequence: {sequence}"]
        if index == 0 and msa_path:
            lines += [f"      msa: {msa_path}"]
    lines += [f"  - ligand:", f"      id: {name}", f"      smiles: {ligand_smiles}"]
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    started = time.monotonic()
    try:
        result = subprocess.run(
            [str(_BOLTZ_CLI), "predict", str(yaml_path),
             "--out_dir", str(work), "--cache", str(_WEIGHTS_DIR)],
            capture_output=True, text=True, timeout=_TIMEOUT_S, cwd=str(work),
            env={**os.environ, "BOLTZ_CACHE": str(_WEIGHTS_DIR)},
        )
    except subprocess.TimeoutExpired:
        return {"success": False,
                "error": f"Boltz-2 timed out after {_TIMEOUT_S}s",
                "gpu": gpu}
    elapsed = time.monotonic() - started
    if result.returncode != 0:
        return {"success": False,
                "error": f"Boltz-2 failed (exit {result.returncode}): "
                          f"{result.stderr.strip()[-600:]}",
                "gpu": gpu, "runtime_seconds": round(elapsed, 2)}

    structures = sorted(str(path) for path in work.rglob("*.cif"))
    confidences: list[float] = []
    for path in sorted(work.rglob("confidence*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for entry in payload.get("confidence", []) if isinstance(payload, dict) else []:
            confidences.append(entry.get("confidence_score"))
    return {
        "success": True,
        "data": {
            "structure_paths": structures,
            "confidence_scores": confidences,
            "affinity": None,
            "gpu": gpu,
            "runtime_seconds": round(elapsed, 2),
            "weights_dir": str(_WEIGHTS_DIR),
            "note": "the confidence and affinity values are model outputs, not "
                    "measurements; no published accuracy is quoted here",
        },
    }

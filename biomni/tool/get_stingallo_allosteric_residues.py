"""T3 get_stingallo_allosteric_residues (Part 2).

Wrapper around the STINGAllo API. Returns the allosteric residues
for a given PDB ID and chain ID. The implementation enforces the
API's documented rate limits (100 requests/IP/day and 30 unique
PDBs/IP/day) via a persistent file-based counter.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_API_BASE = "https://www.stingallo.cbi.cnptia.embrapa.br/api"
_COUNTER_PATH = Path(os.path.expanduser("~")) / ".cache" / "alloagent" / "stingallo_counter.json"
_DAILY_REQUEST_LIMIT = 100
_DAILY_PDB_LIMIT = 30


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return (
        "STINGAllo API (https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs)"
    )


def _load_counter() -> dict:
    if not _COUNTER_PATH.is_file():
        return {"date": time.strftime("%Y-%m-%d"), "requests": 0, "pdbs": []}
    try:
        data = json.loads(_COUNTER_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"date": time.strftime("%Y-%m-%d"), "requests": 0, "pdbs": []}
    if data.get("date") != time.strftime("%Y-%m-%d"):
        return {"date": time.strftime("%Y-%m-%d"), "requests": 0, "pdbs": []}
    return data


def _save_counter(data: dict) -> None:
    _COUNTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _COUNTER_PATH.write_text(json.dumps(data), encoding="utf-8")


def _check_rate_limit(pdb_id: str) -> dict | None:
    counter = _load_counter()
    if counter["requests"] >= _DAILY_REQUEST_LIMIT:
        return {
            "success": False,
            "data": None,
            "error": (
                f"STINGAllo daily request limit reached "
                f"({counter['requests']}/{_DAILY_REQUEST_LIMIT})"
            ),
        }
    if pdb_id not in counter["pdbs"] and len(counter["pdbs"]) >= _DAILY_PDB_LIMIT:
        return {
            "success": False,
            "data": None,
            "error": (
                f"STINGAllo daily unique-PDB limit reached "
                f"({len(counter['pdbs'])}/{_DAILY_PDB_LIMIT})"
            ),
        }
    return None


def _record_call(pdb_id: str) -> None:
    counter = _load_counter()
    counter["requests"] += 1
    if pdb_id not in counter["pdbs"]:
        counter["pdbs"].append(pdb_id)
    _save_counter(counter)


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_stingallo_allosteric_residues(pdb_id, chain_id=None):
    """Given a PDB ID (and optionally a chain ID), return the STINGAllo
    allosteric residue list for that structure.

    Returns the contract dict. `data` is::

        {
            "pdb_id": <pdb_id uppercased>,
            "chain_id": <chain_id or None>,
            "residues": [
                {
                    "residue_number": <int>,
                    "chain_id": <str>,
                    "ligand": <str>,
                    "allosteric_type": <str>,
                    "evidence": <str>,
                },
                ...
            ]
        }
    """
    pdb_norm = pdb_id.upper()

    rate_limit_err = _check_rate_limit(pdb_norm)
    if rate_limit_err is not None:
        return rate_limit_err

    params = {"pdb_id": pdb_norm}
    if chain_id:
        params["chain_id"] = chain_id.upper()
    url = f"{_API_BASE}/afrs"
    resp = requests.get(url, params=params, timeout=_TIMEOUT_S)
    resp.raise_for_status()
    payload = resp.json()

    residues = payload.get("residues", []) if isinstance(payload, dict) else []
    _record_call(pdb_norm)
    return {
        "data": {
            "pdb_id": pdb_norm,
            "chain_id": chain_id.upper() if chain_id else None,
            "residues": residues,
        }
    }

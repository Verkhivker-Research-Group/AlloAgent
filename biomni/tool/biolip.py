"""BioLiP lookups (ported from the old repo's ``alloagent/tool/biolip.py``).

Questions this module answers: which ligands are bound in a given PDB
entry, which chains they bind, and what sequence the BioLiP snapshot
stores for a protein / DNA / RNA / peptide chain.

The old functions returned pandas DataFrames, printed to stdout and
raised on error. The ported versions return the standard contract dict
and convert DataFrames to ``{"records": [...], "columns": [...]}``,
because the per-run recorder is JSON and the agent reads the return
value rather than stdout.

The BioLiP snapshots live in the Biolab data lake, mounted read-only at
``/biolab_data`` (override with ``ALLOAGENT_BIOLIP_DIR``). They are
large pickles (265 MB for the interaction table), so they are loaded
once per process and cached in memory.
"""
from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from biomni.tool._netcall import with_return_contract

_DEFAULT_DATA_DIR = Path("/biolab_data")
_INTERACTIONS = "biolip/biolip.pkl"
_FASTA = {
    "protein": "biolip/protein.pkl",
    "dna": "biolip/dna.pkl",
    "rna": "biolip/rna.pkl",
    "peptide": "biolip/peptide.pkl",
}
# Maximum chain length accepted per polymer type (the old code enforced
# the same limits but with different messages). ``None`` means no limit:
# a protein identifier is "<pdb><chain>", and the old code accepted any
# chain string for proteins.
_MAX_CHAIN_LEN = {"protein": None, "dna": 1, "peptide": 1, "rna": 2}

_PICKLE_CACHE: dict[str, pd.DataFrame] = {}


def _data_dir() -> Path:
    override = os.environ.get("ALLOAGENT_BIOLIP_DIR")
    if override:
        return Path(override)
    return _DEFAULT_DATA_DIR


def _load(rel_path: str) -> pd.DataFrame:
    """Load a BioLiP pickle, caching it in memory for the process."""
    if rel_path in _PICKLE_CACHE:
        return _PICKLE_CACHE[rel_path]
    path = _data_dir() / rel_path
    if not path.is_file():
        raise FileNotFoundError(
            f"BioLiP data file not found at {path}; mount the Biolab data "
            f"lake read-only (expected {_data_dir()}/biolip/)"
        )
    with open(path, "rb") as fh:
        df = pickle.load(fh)
    _PICKLE_CACHE[rel_path] = df
    return df


def _records(df: pd.DataFrame) -> dict[str, Any]:
    """DataFrame -> JSON-safe ``{records, columns}``."""
    records = df.to_dict("records")
    for rec in records:
        for k, v in rec.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                rec[k] = str(v)
    return {"records": records, "columns": list(df.columns)}


def _pdb_id_error(pdb_id: Any) -> Optional[str]:
    if not isinstance(pdb_id, str) or not pdb_id:
        return f"pdb_id must be a non-empty string, got {pdb_id!r}"
    if len(pdb_id) not in (4, 12):
        return (
            f"Incorrect pdb_id {pdb_id!r}: must be a 4-character id, or 12 "
            f"if integrated in the new PDB system"
        )
    return None


def _chain_error(chain: Any, kind: str) -> Optional[str]:
    if chain is None:
        return None
    if not isinstance(chain, str) or not chain:
        return f"chain must be a non-empty string, got {chain!r}"
    limit = _MAX_CHAIN_LEN[kind]
    if limit is None:
        return None
    if len(chain) > limit:
        if limit == 1:
            return f"Incorrect chain {chain!r}: must be a single letter"
        return f"Incorrect chain {chain!r}: must be 1-{limit} letters"
    return None


@with_return_contract(source_version="1.0")
def parse_biolip_interactions(pdb_id: Optional[str] = None,
                              chain: Optional[str] = None):
    """Return the BioLiP interaction rows for a PDB entry and chain.

    Does not answer which ligand is most likely to modulate the target;
    it answers which ligand-protein interactions the BioLiP snapshot
    records for that entry.

    Parameters
    ----------
    pdb_id : str or None
        4-character PDB id (or 12 for the new PDB system). ``None``
        returns the whole table (989,058 rows) and is not intended for
        agent use.
    chain : str or None
        Optional chain id.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "pdb_id": <str or None>,
                "chain": <str or None>,
                "total": <int>,
                "records": [ {<column>: <value>, ...}, ... ],
                "columns": [<str>, ...],
            }
    """
    if pdb_id is not None:
        err = _pdb_id_error(pdb_id)
        if err:
            return {"success": False, "error": err}
    err = _chain_error(chain, "protein")
    if err:
        return {"success": False, "error": err}

    try:
        df = _load(_INTERACTIONS)
    except FileNotFoundError as exc:
        return {"success": False, "error": str(exc)}

    if pdb_id is None:
        out = df
    else:
        out = df[df["PDB"] == pdb_id.lower()]
        if chain is not None:
            out = out[out["Chain"] == chain.upper()]

    payload = _records(out)
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_id.lower() if pdb_id else None,
            "chain": chain.upper() if chain else None,
            "total": len(out),
            "records": payload["records"],
            "columns": payload["columns"],
        },
    }


@with_return_contract(source_version="1.0")
def biolip_ligands(pdb_id: str, chain: Optional[str] = None):
    """Return the distinct ligand IDs bound in a PDB entry (and chain).

    Does not answer whether a ligand is an allosteric or an orthosteric
    binder; it answers which ligands the BioLiP snapshot records as
    bound.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id (or 12 for the new PDB system).
    chain : str or None
        Optional chain id.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "pdb_id": <str>,
                "chain": <str or None>,
                "ligands": [<str>, ...],
                "total_interactions": <int>,
                "chains": [<str>, ...],
                "uniprot_ids": [<str>, ...],
            }
    """
    result = parse_biolip_interactions(pdb_id, chain)
    if not result.get("success"):
        return result
    records = result["data"]["records"]
    ligands = sorted({r.get("Ligand") for r in records if r.get("Ligand")})
    chains = sorted({r.get("Chain") for r in records if r.get("Chain")})
    uniprot = sorted({r.get("UniProt_ID") for r in records if r.get("UniProt_ID")})
    return {
        "success": True,
        "data": {
            "pdb_id": result["data"]["pdb_id"],
            "chain": result["data"]["chain"],
            "ligands": ligands,
            "total_interactions": result["data"]["total"],
            "chains": chains,
            "uniprot_ids": uniprot,
        },
    }


def _biolip_sequence(kind: str, pdb_id: str, chain: Optional[str]) -> dict:
    """Shared implementation for the four polymer lookups."""
    err = _pdb_id_error(pdb_id)
    if err:
        return {"success": False, "error": err}
    err = _chain_error(chain, kind)
    if err:
        return {"success": False, "error": err}

    try:
        df = _load(_FASTA[kind])
    except FileNotFoundError as exc:
        return {"success": False, "error": str(exc)}

    pdb_lower = pdb_id.lower()
    if kind == "protein":
        prefix = pdb_lower
        identifier = f"{pdb_lower}{chain.upper()}" if chain else None
    else:
        prefix = f"{pdb_lower}_{kind}_"
        identifier = f"{pdb_lower}_{kind}_{chain.upper()}" if chain else None

    if identifier is not None:
        out = df[df["identifier"] == identifier].copy()
    else:
        out = df[df["identifier"].str.lower().str.startswith(prefix)].copy()

    payload = _records(out)
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_lower,
            "chain": chain.upper() if chain else None,
            "kind": kind,
            "total": len(out),
            "records": payload["records"],
            "columns": payload["columns"],
        },
    }


@with_return_contract(source_version="1.0")
def biolip_protein(pdb_id: str, chain: Optional[str] = None):
    """Return the protein sequences the BioLiP snapshot stores for a PDB entry.

    Does not answer which residues are in contact with a ligand, and it
    does not verify the stored sequence against the current PDB entry.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id (or 12 for the new PDB system).
    chain : str or None
        Optional chain id.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, chain, kind, total, records, columns}``.
    """
    return _biolip_sequence("protein", pdb_id, chain)


@with_return_contract(source_version="1.0")
def biolip_dna(pdb_id: str, chain: Optional[str] = None):
    """Return the DNA sequences the BioLiP snapshot stores for a PDB entry.

    Does not answer which nucleotides are in contact with a ligand, and
    it does not verify the stored sequence against the current PDB entry.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id (or 12 for the new PDB system).
    chain : str or None
        Optional chain id (single letter).

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, chain, kind, total, records, columns}``.
    """
    return _biolip_sequence("dna", pdb_id, chain)


@with_return_contract(source_version="1.0")
def biolip_rna(pdb_id: str, chain: Optional[str] = None):
    """Return the RNA sequences the BioLiP snapshot stores for a PDB entry.

    Does not answer which nucleotides are in contact with a ligand, and
    it does not verify the stored sequence against the current PDB entry.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id (or 12 for the new PDB system).
    chain : str or None
        Optional chain id (1-2 letters).

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, chain, kind, total, records, columns}``.
    """
    return _biolip_sequence("rna", pdb_id, chain)


@with_return_contract(source_version="1.0")
def biolip_peptide(pdb_id: str, chain: Optional[str] = None):
    """Return the peptide sequences the BioLiP snapshot stores for a PDB entry.

    Does not answer which residues are in contact with a ligand, and it
    does not verify the stored sequence against the current PDB entry.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id (or 12 for the new PDB system).
    chain : str or None
        Optional chain id (single letter).

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, chain, kind, total, records, columns}``.
    """
    return _biolip_sequence("peptide", pdb_id, chain)

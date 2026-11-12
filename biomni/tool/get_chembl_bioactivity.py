"""B1 get_chembl_bioactivity (Part 2 / batch 2).

What are the ChEMBL bioactivity records for a given target and
compound, filtered by standard_type?

Two modes, local SQLite (default when the file is present) and
web API (fallback). The local mode is a parameterized read-only
SQL wrapper over the ChEMBL 37 SQLite database. The LLM never
sees free-form SQL; all queries are fixed functions of the
input parameters with bound values.
"""
from __future__ import annotations

import csv
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

import requests

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_DEFAULT_LOCAL_PATH = Path("/data/chembl/chembl_37_sqlite/chembl_37.db")
_LOCAL_MANIFEST = "MANIFEST"
_WEB_API_BASE = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

_VALID_STANDARD_TYPES = {"IC50", "Ki", "Kd", "EC50", "IC90", "AC50", "GI50"}


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "ChEMBL 37 (https://www.ebi.ac.uk/chembl/)"


def _read_manifest(path: Path) -> dict[str, str]:
    """Read a ChEMBL MANIFEST file (key: value per line) into a dict.

    The fetch script writes a per-file manifest named
    ``MANIFEST.<basename>`` (so several downloads can share a
    directory); the legacy single ``MANIFEST`` is still accepted for
    the synthetic fixtures. Per-file wins.
    """
    out: dict[str, str] = {}
    candidates = [path.parent / f"MANIFEST.{path.name}"]
    # The fetch script records the manifest against the downloaded
    # ARCHIVE (MANIFEST.chembl_37_sqlite.tar.gz), not the unpacked .db,
    # so an exact per-file name alone is not enough on a real install.
    candidates.extend(sorted(path.parent.glob("MANIFEST.*")))
    candidates.append(path.parent / _LOCAL_MANIFEST)
    for manifest_path in candidates:
        if not manifest_path.is_file():
            continue
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    k, _, v = line.partition(":")
                    out[k.strip()] = v.strip()
            if out:
                return out
        except (OSError, UnicodeDecodeError):
            continue
    return out


def _resolve_target_id(conn: sqlite3.Connection, target: str) -> str:
    """Resolve a target to a ChEMBL target ID.

    Accepts a ChEMBL target ID (CHEMBL*) directly, or a UniProt
    accession (e.g. P00519) and looks up the corresponding ChEMBL
    target ID via component_sequences.accession.
    """
    if target.upper().startswith("CHEMBL"):
        return target.upper()
    row = conn.execute(
        """
        SELECT td.chembl_id
        FROM target_dictionary td
        JOIN target_components tc ON td.tid = tc.tid
        JOIN component_sequences cs ON tc.component_id = cs.component_id
        WHERE cs.accession = ?
        LIMIT 1
        """,
        (target,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"no ChEMBL target found for {target!r} (not a ChEMBL ID or UniProt accession)"
        )
    return row[0]


def _resolve_molecule_chembl_id(conn: sqlite3.Connection, compound: str) -> str:
    """Resolve a compound to a ChEMBL molecule ID.

    Accepts a ChEMBL molecule ID (CHEMBL*) directly, or a
    compound name and looks up the corresponding ChEMBL molecule
    ID via molecule_dictionary.pref_name or molecule_synonyms.
    """
    if compound.upper().startswith("CHEMBL"):
        return compound.upper()
    # ChEMBL stores pref_name and synonyms in inconsistent case
    # (IMATINIB vs Imatinib), so an exact-match lookup misses the
    # user's spelling. Compare case-insensitively on both tables.
    row = conn.execute(
        """
        SELECT md.chembl_id
        FROM molecule_dictionary md
        WHERE UPPER(md.pref_name) = UPPER(?)
        LIMIT 1
        """,
        (compound,),
    ).fetchone()
    if row is not None:
        return row[0]
    row = conn.execute(
        """
        SELECT md.chembl_id
        FROM molecule_dictionary md
        JOIN molecule_synonyms ms ON md.molregno = ms.molregno
        WHERE UPPER(ms.synonyms) = UPPER(?)
        LIMIT 1
        """,
        (compound,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"no ChEMBL molecule found for {compound!r} (not a ChEMBL ID or known name)"
        )
    return row[0]


def _query_local(
    target: str,
    compound: str,
    standard_type: str,
    max_records: int,
    data_path: Path,
) -> list[dict[str, Any]]:
    """Query the local ChEMBL SQLite database with parameterized SQL.

    Returns a list of activity records.
    """
    conn = sqlite3.connect(str(data_path))
    conn.row_factory = sqlite3.Row
    try:
        target_id = _resolve_target_id(conn, target)
        mol_chembl_id = _resolve_molecule_chembl_id(conn, compound)
        # ChEMBL 37's `activities` table has no target/assay/confidence
        # columns; the target and assay live one hop away via
        # activities.assay_id -> assays, and assays.tid ->
        # target_dictionary. The previous query read a.target_chembl_id,
        # a.assay_chembl_id and a.confidence_score directly off
        # `activities`, none of which exist in the real schema, so every
        # live query failed with "no such column: a.target_chembl_id".
        cursor = conn.execute(
            """
            SELECT a.activity_id, a.molregno, md.chembl_id AS molecule_chembl_id,
                   td.chembl_id AS target_chembl_id, a.standard_type,
                   a.standard_value, a.standard_units, a.standard_relation,
                   asy.chembl_id AS assay_chembl_id, asy.confidence_score
            FROM activities a
            JOIN molecule_dictionary md ON a.molregno = md.molregno
            JOIN assays asy ON a.assay_id = asy.assay_id
            JOIN target_dictionary td ON asy.tid = td.tid
            WHERE td.chembl_id = ?
              AND md.chembl_id = ?
              AND a.standard_type = ?
              AND a.standard_value IS NOT NULL
              AND a.standard_units = 'nM'
            ORDER BY CAST(a.standard_value AS REAL) ASC
            LIMIT ?
            """,
            (target_id, mol_chembl_id, standard_type, max_records),
        )
        records = []
        for row in cursor.fetchall():
            records.append({
                "activity_id": row["activity_id"],
                "molregno": row["molregno"],
                "molecule_chembl_id": row["molecule_chembl_id"],
                "target_chembl_id": row["target_chembl_id"],
                "standard_type": row["standard_type"],
                "standard_value": float(row["standard_value"]),
                "standard_units": row["standard_units"],
                "standard_relation": row["standard_relation"],
                "assay_chembl_id": row["assay_chembl_id"],
                "confidence_score": row["confidence_score"],
            })
        return records
    finally:
        conn.close()


def _query_web_api(
    target: str,
    compound: str,
    standard_type: str,
    max_records: int,
) -> list[dict[str, Any]]:
    """Fallback: query the ChEMBL REST API.

    The API does not accept UniProt accessions or compound names
    directly, so we assume ``target`` and ``compound`` are already
    ChEMBL IDs. If they are not, the API call will simply return
    zero results.
    """
    params: dict[str, str] = {
        "standard_type": standard_type,
        "limit": str(max_records),
        "offset": "0",
    }
    if target.upper().startswith("CHEMBL"):
        params["target_chembl_id"] = target
    if compound.upper().startswith("CHEMBL"):
        params["molecule_chembl_id"] = compound
    r = requests.get(_WEB_API_BASE, params=params, timeout=_TIMEOUT_S)
    if r.status_code != 200:
        raise RuntimeError(
            f"ChEMBL web API returned status {r.status_code}: {r.text[:200]}"
        )
    body = r.json()
    records = []
    for act in body.get("activities", []):
        records.append({
            "activity_id": act.get("activity_id"),
            "molregno": act.get("molecule_chembl_id"),
            "molecule_chembl_id": act.get("molecule_chembl_id"),
            "target_chembl_id": act.get("target_chembl_id"),
            "standard_type": act.get("standard_type"),
            "standard_value": act.get("standard_value"),
            "standard_units": act.get("standard_units"),
            "standard_relation": act.get("standard_relation"),
            "assay_chembl_id": act.get("assay_chembl_id"),
            "confidence_score": act.get("confidence_score"),
        })
    return records


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_chembl_bioactivity(
    target: str,
    compound: str,
    standard_type: str = "IC50",
    max_records: int = 20,
    mode: Optional[str] = None,
    data_path: Optional[Any] = None,
):
    """Query ChEMBL bioactivity records for a target and compound.

    Parameters
    ----------
    target : str
        ChEMBL target ID (e.g. ``"CHEMBL1862"``) or UniProt
        accession (e.g. ``"P00519"``). UniProt accessions are
        resolved via ``target_components``.
    compound : str
        ChEMBL molecule ID (e.g. ``"CHEMBL941"``) or compound
        name (e.g. ``"imatinib"``). Names are resolved via
        ``molecule_dictionary.pref_name`` or
        ``molecule_synonyms.synonyms``.
    standard_type : str
        One of ``"IC50"``, ``"Ki"``, ``"Kd"``, etc. Default
        ``"IC50"``.
    max_records : int
        Maximum number of records to return. Default 20.
    mode : str or None
        ``"local"`` forces the local SQLite query;
        ``"web"`` forces the ChEMBL REST API;
        ``None`` (default) auto-detects: local if the SQLite
        file + MANIFEST are present, else web.
    data_path : str, Path, or None
        Path to the local ``chembl_37.db`` file. Default
        ``/data/chembl/chembl_37_sqlite/chembl_37.db``.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "target": <str>,
                "compound": <str>,
                "target_chembl_id": <str>,
                "molecule_chembl_id": <str>,
                "standard_type": <str>,
                "total_count": <int>,
                "records": [
                    {
                        "activity_id": <int>,
                        "molecule_chembl_id": <str>,
                        "target_chembl_id": <str>,
                        "standard_type": <str>,
                        "standard_value": <float>,
                        "standard_units": <str>,
                        ...
                    },
                    ...
                ],
                "source": "local:chembl_37:<downloaded_at>" or "web:<query_time_utc>",
                "release_date": <str> or None,  # from MANIFEST (local)
                "query_url": <str>,
            }

        On error, returns ``{success: False, error: <string>, ...}``.
    """
    if not isinstance(target, str) or not target:
        return {
            "success": False,
            "error": f"target must be a non-empty string, got {target!r}",
        }
    if not isinstance(compound, str) or not compound:
        return {
            "success": False,
            "error": f"compound must be a non-empty string, got {compound!r}",
        }
    if standard_type not in _VALID_STANDARD_TYPES:
        return {
            "success": False,
            "error": (
                f"standard_type must be one of "
                f"{sorted(_VALID_STANDARD_TYPES)}, got {standard_type!r}"
            ),
        }
    if not isinstance(max_records, int) or max_records < 0:
        return {
            "success": False,
            "error": f"max_records must be a positive int, got {max_records!r}",
        }
    if mode is not None and mode not in ("local", "web"):
        return {
            "success": False,
            "error": f"mode must be 'local', 'web', or None, got {mode!r}",
        }

    local_path = Path(data_path) if data_path is not None else _DEFAULT_LOCAL_PATH
    manifest = _read_manifest(local_path) if local_path.is_file() else {}
    use_local = (
        mode == "local"
        or (mode is None and local_path.is_file() and bool(manifest))
    )

    if max_records == 0:
        return {
            "success": True,
            "data": {
                "target": target,
                "compound": compound,
                "target_chembl_id": None,
                "molecule_chembl_id": None,
                "standard_type": standard_type,
                "total_count": 0,
                "records": [],
                "source": "local:0" if use_local else f"web:{_utc_now_iso()}",
                "release_date": (manifest.get("downloaded_at") or manifest.get("completed_at")) if use_local else None,
                "query_url": str(local_path) if use_local else _WEB_API_BASE,
            },
        }

    if use_local:
        if not local_path.is_file():
            return {
                "success": False,
                "error": (
                    f"ChEMBL SQLite not found at {str(local_path)!s}; "
                    f"run scripts/fetch_chembl.py --download --out <dir>"
                ),
            }
        try:
            records = _query_local(target, compound, standard_type, max_records, local_path)
        except sqlite3.Error as exc:
            return {"success": False, "error": f"ChEMBL SQLite error: {exc}"}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}
        target_chembl_id = records[0]["target_chembl_id"] if records else None
        mol_chembl_id = records[0]["molecule_chembl_id"] if records else None
        release_date = manifest.get("downloaded_at") or manifest.get("completed_at") or "unknown"
        return {
            "success": True,
            "data": {
                "target": target,
                "compound": compound,
                "target_chembl_id": target_chembl_id,
                "molecule_chembl_id": mol_chembl_id,
                "standard_type": standard_type,
                "total_count": len(records),
                "records": records,
                "source": f"local:chembl_37:{release_date}",
                "release_date": release_date,
                "query_url": str(local_path),
            },
        }

    # Web API fallback
    try:
        records = _query_web_api(target, compound, standard_type, max_records)
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"requests error: {exc!r}"}
    except RuntimeError as exc:
        return {"success": False, "error": str(exc)}
    target_chembl_id = records[0]["target_chembl_id"] if records else None
    mol_chembl_id = records[0]["molecule_chembl_id"] if records else None
    return {
        "success": True,
        "data": {
            "target": target,
            "compound": compound,
            "target_chembl_id": target_chembl_id,
            "molecule_chembl_id": mol_chembl_id,
            "standard_type": standard_type,
            "total_count": len(records),
            "records": records,
            "source": f"web:{_utc_now_iso()}",
            "release_date": None,
            "query_url": _WEB_API_BASE,
        },
    }

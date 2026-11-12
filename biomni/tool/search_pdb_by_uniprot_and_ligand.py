"""T8 search_pdb_by_uniprot_and_ligand (Part 2 / batch 2).

Which PDB entries have a polymer entity with the given UniProt
accession AND a chemical component with the given ligand ID?

Wraps the RCSB PDB Search API v2
(``https://search.rcsb.org/rcsbsearch/v2/query``) with a combined
``text``-service group query and ``logical_operator=and``. Returns
the matching PDB entry IDs in score order. Online tool (requires
outbound HTTPS to ``search.rcsb.org``).
"""
from __future__ import annotations

import time
from typing import Any

import requests

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
_UNIPROT_ATTR = (
    "rcsb_polymer_entity_container_identifiers"
    ".reference_sequence_identifiers.database_accession"
)
_LIGAND_ATTR = "rcsb_chem_comp_container_identifiers.comp_id"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "RCSB PDB Search API v2 (https://search.rcsb.org/rcsbsearch/v2/query)"


def _build_query(uniprot_id: str, ligand_id: str) -> dict[str, Any]:
    return {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": _UNIPROT_ATTR,
                        "operator": "exact_match",
                        "value": uniprot_id,
                    },
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": _LIGAND_ATTR,
                        "operator": "exact_match",
                        "value": ligand_id,
                    },
                },
            ],
        },
        "return_type": "entry",
    }


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def search_pdb_by_uniprot_and_ligand(
    uniprot_id: str,
    ligand_id: str,
):
    """Search the RCSB PDB for entries that have a polymer entity
    with the given UniProt accession AND a chemical component with
    the given ligand ID.

    This tool is **accession-specific**: it matches the exact
    UniProt accession, not orthologs. Querying human ABL1
    (``P00519``) will NOT return mouse ABL1 structures (which
    are mapped to ``P00520`` in SIFTS), even though the two
    proteins are orthologs with the same gene function. To search
    across orthologs, pass each accession separately and take
    the union of the result sets.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession (e.g. ``"P69905"``, ``"P69441"``). Case is
        preserved -- the RCSB Search API is case-sensitive for
        UniProt accessions in practice (it returns the same set of
        entries for uppercase, but the query is not normalized).
    ligand_id : str
        RCSB chemical component ID (e.g. ``"HEM"``, ``"ATP"``,
        ``"ZN"``). The RCSB Search API is case-sensitive for ligand
        IDs; lowercase or mixed-case inputs return zero results.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "uniprot_id": <str>,
                "ligand_id": <str>,
                "entry_ids": [<4-char PDB ID>, ...],  # score order
                "total_count": <int>,
                "query_url": <str>,
            }

        On network or API failure, returns
        ``{success: False, error: <descriptive string>, ...}``.
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {
            "success": False,
            "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}",
        }
    if not isinstance(ligand_id, str) or not ligand_id:
        return {
            "success": False,
            "error": f"ligand_id must be a non-empty string, got {ligand_id!r}",
        }

    query = _build_query(uniprot_id, ligand_id)

    try:
        response = requests.post(_SEARCH_URL, json=query, timeout=_TIMEOUT_S)
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"requests error: {exc!r}",
        }

    if response.status_code == 204:
        return {
            "success": True,
            "data": {
                "uniprot_id": uniprot_id,
                "ligand_id": ligand_id,
                "entry_ids": [],
                "total_count": 0,
                "query_url": _SEARCH_URL,
            },
        }

    if response.status_code != 200:
        return {
            "success": False,
            "error": (
                f"RCSB Search API returned status "
                f"{response.status_code}: {response.text[:200]}"
            ),
        }

    try:
        body = response.json()
    except ValueError as exc:
        return {
            "success": False,
            "error": f"RCSB Search API returned invalid JSON: {exc}",
        }

    result_set = body.get("result_set", [])
    entry_ids = [item["identifier"] for item in result_set if "identifier" in item]
    total_count = int(body.get("total_count", len(entry_ids)))

    return {
        "success": True,
        "data": {
            "uniprot_id": uniprot_id,
            "ligand_id": ligand_id,
            "entry_ids": entry_ids,
            "total_count": total_count,
            "query_url": _SEARCH_URL,
        },
    }

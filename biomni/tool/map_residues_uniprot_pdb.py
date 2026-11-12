"""T1 map_residues_uniprot_pdb (Part 2).

Two wrapper functions around the PDBe mappings API:

  * map_residues_uniprot_pdb(pdb_id)
      GET https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<pdb>
      -> {<pdb_lowercase>: {UniProt: {<accession>: {name, mappings, identifier}}}}
      Returns a flat dict: {pdb_id, uniprot_accessions, mappings, source}.

  * map_pdb_to_best_structures(accession)
      GET https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/<accession>
      -> {<accession>: [ {pdb_id, entity_id, chain_id, ...} ]}
      Returns a flat dict: {uniprot_accession, best_structures, source}.

Both functions:
  * are decorated with @with_return_contract
  * are decorated with @benchmark_blocklist (the first positional arg
    is checked against the benchmark blocklist; if it matches, the
    function short-circuits and returns a blocked-dict)
  * are not cached on disk in this commit (the cache is a follow-up
    to the Part-1c timeout/retry/cache criteria)

Known answer (recorded in tests/fixtures/):
  map_residues_uniprot_pdb("1AKE") -> P69441 (KAD_ECOLI), chains A and B,
    unp_start=1, unp_end=214, identity=1.0, coverage=1.0.
"""
from __future__ import annotations

import time

import requests

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_API_BASE = "https://www.ebi.ac.uk/pdbe/api/mappings"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "PDBe mappings API (https://www.ebi.ac.uk/pdbe/api/mappings)"


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def map_residues_uniprot_pdb(pdb_id):
    """Given a PDB ID, return the UniProt accession(s) and chain + residue
    mapping for that structure.

    Returns the contract dict {success, data, error, source,
    source_version, query_time_utc}. `data` is::

        {
            "pdb_id": <pdb_id uppercased>,
            "uniprot_accessions": [<accession>, ...],
            "mappings": {
                <accession>: {
                    "name": <protein name>,
                    "identifier": <PDBe identifier>,
                    "mappings": [
                        {entity_id, chain_id, struct_asym_id,
                         unp_start, unp_end,
                         start: {author_residue_number, residue_number},
                         end:   {author_residue_number, residue_number},
                         identity, coverage},
                        ...
                    ]
                },
                ...
            }
        }
    """
    pdb_id_norm = pdb_id.upper()
    url = f"{_API_BASE}/uniprot/{pdb_id_norm}"
    resp = requests.get(url, timeout=_TIMEOUT_S)
    resp.raise_for_status()
    payload = resp.json()
    inner = next(iter(payload.values())) if payload else {}
    uniprot = inner.get("UniProt", {}) if isinstance(inner, dict) else {}
    accessions = sorted(uniprot.keys())
    return {
        "data": {
            "pdb_id": pdb_id_norm,
            "uniprot_accessions": accessions,
            "mappings": uniprot,
        }
    }


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def map_pdb_to_best_structures(accession):
    """Given a UniProt accession, return the list of best PDB structures
    (with chain + coverage info) for that protein.

    Returns the contract dict. `data` is::

        {
            "uniprot_accession": <accession uppercased>,
            "best_structures": [
                {pdb_id, entity_id, chain_id, unp_start, unp_end,
                 coverage, best, ...},
                ...
            ]
        }
    """
    acc_norm = accession.upper()
    url = f"{_API_BASE}/best_structures/{acc_norm}"
    resp = requests.get(url, timeout=_TIMEOUT_S)
    resp.raise_for_status()
    payload = resp.json()
    entries = payload.get(acc_norm, []) or []
    return {
        "data": {
            "uniprot_accession": acc_norm,
            "best_structures": entries,
        }
    }

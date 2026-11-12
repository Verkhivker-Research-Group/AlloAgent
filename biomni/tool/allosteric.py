"""Allosteric-domain lookups (ported from the old repo's
``alloagent/tool/allosteric.py``).

Questions this module answers: which UniProt accession(s) a PDB chain
maps to, which PDB entries are known for a UniProt accession, what
ChEMBL/PubChem say about a named ligand, and which covalent-probe
attachment sites are recorded for a target.

The old functions returned bare objects, printed to stdout and raised on
error. The ported versions return the standard contract dict, never
print, and convert pandas DataFrames to
``{"records": [...], "columns": [...]}`` because the per-run recorder is
JSON.

``biolip_ligands`` is deliberately NOT defined here: the old repo
defined it twice (in ``biolip.py`` and again in ``allosteric.py``,
where it simply delegated). Defining it in both modules would register
the same tool name twice, so the canonical implementation lives in
``biomni/tool/biolip.py`` and the allosteric copy is recorded as a
MERGE in the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md).
"""
from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests

from biomni.tool import _cache
from biomni.tool._netcall import with_return_contract

_PDBE_BASE = "https://www.ebi.ac.uk/pdbe/api/mappings"
_TIMEOUT_S = 30
_DEFAULT_COVINDB = "/biolab_data/data_lake/CovInDB_All.csv"

# Covalent-probe sites that are known orthosteric catalytic positions.
_ORTHOSTERIC_SITES = {
    "EGFR": ["CYS-797"],
    "KRAS": ["CYS-12"],
    "BTK": ["CYS-481"],
    "JAK": ["CYS-909"],
    "SERINE_PROTEASE": ["SER-195", "HIS-57", "ASP-102"],
    "CYSTEINE_PROTEASE": ["CYS-25", "HIS-159"],
    "GENERAL_CATALYTIC": [
        "CYS-25", "CYS-145", "SER-195", "HIS-41", "HIS-57",
        "ASP-102", "LYS-72", "ASP-189", "SER-221", "CYS-481",
    ],
}
_COVINDB_COLUMNS = [
    "Inhibitor_Name", "Target_Name", "Target_Gene", "Target",
    "Site", "War_head", "Reaction_type", "Method", "Assay", "Reference",
    "InChI_Key",
]


def _pdbe(url: str, cache_prefix: str) -> Optional[dict]:
    """GET a PDBe mapping endpoint, with a 24 h on-disk cache.

    Returns ``None`` when PDBe answers 404 (the id is well-formed but
    unknown). The old tool returned an empty mapping in that case, so
    this keeps the ported behaviour.
    """
    key = _cache.cache_key(cache_prefix, url)
    cached = _cache.read_cache(key)
    if cached is not None:
        return cached
    resp = requests.get(url, timeout=_TIMEOUT_S)
    if resp.status_code == 404:
        _cache.write_cache(key, {})
        return None
    resp.raise_for_status()
    payload = resp.json()
    _cache.write_cache(key, payload)
    return payload


@with_return_contract(source_version="1.0")
def pdb_to_uniprot(pdb_id: str):
    """Return the UniProt accession(s) that each chain of a PDB entry maps to.

    Does not answer whether the structure is an allosteric or an
    orthosteric form, and it does not say which residues are in contact
    with a ligand.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id, case-insensitive.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "pdb_id": <str uppercased>,
                "chains": {<chain>: [<uniprot>, ...], ...},
                "uniprot_ids": [<str>, ...],
                "mappings": [
                    {"chain_id": <str>, "uniprot_id": <str>,
                     "unp_start": <int>, "unp_end": <int>}, ...
                ],
            }
    """
    if not isinstance(pdb_id, str) or not pdb_id:
        return {"success": False,
                "error": f"pdb_id must be a non-empty string, got {pdb_id!r}"}
    pdb_norm = pdb_id.strip().upper()
    if len(pdb_norm) != 4:
        return {
            "success": False,
            "error": f"Incorrect pdb_id {pdb_id!r}: must be a 4-character id",
        }

    url = f"{_PDBE_BASE}/uniprot/{pdb_norm}"
    try:
        payload = _pdbe(url, "pdbe_uniprot")
    except requests.RequestException as exc:
        return {"success": False, "error": f"PDBe request failed: {exc!r}"}
    except ValueError as exc:
        return {"success": False, "error": f"PDBe returned invalid JSON: {exc}"}

    entry = (payload or {}).get(pdb_norm.lower()) or {}
    chains: dict[str, list[str]] = {}
    mappings: list[dict[str, Any]] = []
    for uniprot, details in (entry.get("UniProt") or {}).items():
        for mapping in details.get("mappings", []):
            chain = mapping.get("chain_id")
            if not chain:
                continue
            chain = chain.upper()
            # One accession can appear twice for a chain (two sequence
            # ranges), so keep the chain->accession list unique.
            if uniprot not in chains.setdefault(chain, []):
                chains[chain].append(uniprot)
            mappings.append({
                "chain_id": chain,
                "uniprot_id": uniprot,
                "unp_start": mapping.get("unp_start"),
                "unp_end": mapping.get("unp_end"),
            })
    uniprot_ids = sorted({u for v in chains.values() for u in v})
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_norm,
            "chains": chains,
            "uniprot_ids": uniprot_ids,
            "mappings": mappings,
        },
    }


@with_return_contract(source_version="1.0")
def uniprot_to_pdb(uniprot_id: str):
    """Return the PDB entries that are known for a UniProt accession.

    Does not answer which of those entries shows a particular
    conformational state, nor whether any of them is allosteric.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession, case-insensitive.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "uniprot_id": <str uppercased>,
                "pdb_ids": [<str>, ...],
                "total": <int>,
            }
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {"success": False,
                "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}"}
    acc = uniprot_id.strip().upper()

    url = f"{_PDBE_BASE}/all_isoforms/{acc}"
    try:
        payload = _pdbe(url, "pdbe_pdb")
    except requests.RequestException as exc:
        return {"success": False, "error": f"PDBe request failed: {exc!r}"}
    except ValueError as exc:
        return {"success": False, "error": f"PDBe returned invalid JSON: {exc}"}

    entry = (payload or {}).get(acc) or {}
    pdb_ids = sorted({
        p.upper() for p in (entry.get("PDB") or {}) if len(p) == 4
    })
    return {
        "success": True,
        "data": {
            "uniprot_id": acc,
            "pdb_ids": pdb_ids,
            "total": len(pdb_ids),
        },
    }


def _as_float(value: Any) -> Optional[float]:
    """Coerce a ChEMBL numeric field to float; keep None as None."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> Optional[int]:
    """Coerce a ChEMBL numeric field to int; keep None as None."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@with_return_contract(source_version="1.0")
def cross_reference_ligands_chembl_pubchem(uniprot_id: str,
                                            ligands: list,
                                            detail_level: str = "slim"):
    """Cross-reference named ligands against ChEMBL and PubChem.

    Does not answer whether a ligand is an allosteric or an orthosteric
    binder of the target; it answers what the two chemical databases
    record about the compound.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession of the target the ligands are used against.
    ligands : list
        List of dicts with a ``ligand_name`` key, e.g.
        ``[{"ligand_name": "imatinib"}]``.
    detail_level : str
        ``"slim"`` (default) returns curated fields; ``"full"`` returns
        the raw ChEMBL and PubChem records.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "protein_id": <str>,
                "ligands": [
                    {
                        "name": <str>,
                        "chembl_id": <str>,
                        "chembl_synonyms": [<str>, ...],
                        "chembl_properties": {"formula": ..., "molecular_weight": ...,
                                              "alogp": ..., "psa": ...},
                        "chembl_structure": {"smiles": ..., "inchi_key": ...},
                        "chembl_classification": {"atc": ..., "usan_stem": ...},
                        "chembl_approval": {"first_approval": ..., "max_phase": ...},
                        "pubchem_cid": <int>,
                    },
                    ...
                ],
                "total": <int>,
            }
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {"success": False,
                "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}"}
    if not isinstance(ligands, list):
        return {"success": False,
                "error": f"ligands must be a list, got {type(ligands).__name__}"}
    if detail_level not in ("slim", "full"):
        return {
            "success": False,
            "error": f"detail_level must be 'slim' or 'full', got {detail_level!r}",
        }

    from chembl_webresource_client.new_client import new_client
    import pubchempy as pcp

    molecule = new_client.molecule
    results: list[dict[str, Any]] = []
    for ligand in ligands:
        if not isinstance(ligand, dict):
            results.append({
                "name": None,
                "error": f"ligand must be a dict, got {type(ligand).__name__}",
            })
            continue
        ligand_name = ligand.get("ligand_name")
        cross_ref: dict[str, Any] = {"name": ligand_name}
        if not ligand_name:
            cross_ref["error"] = "ligand is missing the 'ligand_name' key"
            results.append(cross_ref)
            continue
        try:
            matches = molecule.filter(pref_name__icontains=ligand_name)
            if matches:
                chembl_data = matches[0]
                if detail_level == "slim":
                    props = chembl_data.get("molecule_properties") or {}
                    structures = chembl_data.get("molecule_structures") or {}
                    synonyms = [
                        s.get("molecule_synonym")
                        for s in (chembl_data.get("molecule_synonyms") or [])[:3]
                        if isinstance(s, dict) and s.get("molecule_synonym")
                    ]
                    cross_ref.update({
                        "chembl_id": chembl_data.get("molecule_chembl_id"),
                        "chembl_synonyms": synonyms,
                        "chembl_properties": {
                            "formula": props.get("full_molformula"),
                            "molecular_weight": _as_float(props.get("full_mwt")),
                            "alogp": _as_float(props.get("alogp")),
                            "psa": _as_float(props.get("psa")),
                        },
                        "chembl_structure": {
                            "smiles": structures.get("canonical_smiles"),
                            "inchi_key": structures.get("standard_inchi_key"),
                        },
                        "chembl_classification": {
                            "atc": chembl_data.get("atc_classifications", []),
                            "usan_stem": chembl_data.get("usan_stem"),
                        },
                        "chembl_approval": {
                            "first_approval": _as_int(
                                chembl_data.get("first_approval")
                            ),
                            "max_phase": _as_float(chembl_data.get("max_phase")),
                        },
                    })
                else:
                    cross_ref["chembl_raw"] = chembl_data
            else:
                cross_ref["error"] = (
                    f"no ChEMBL molecule matched {ligand_name!r}"
                )
        except Exception as exc:  # noqa: BLE001 - per-ligand isolation
            cross_ref["error"] = f"ChEMBL lookup failed: {exc!r}"

        try:
            pubchem_matches = pcp.get_compounds(ligand_name, "name")
            if pubchem_matches:
                compound = pubchem_matches[0]
                if detail_level == "slim":
                    cross_ref["pubchem_cid"] = compound.cid
                else:
                    cross_ref["pubchem_raw"] = compound.to_dict()
            else:
                cross_ref.setdefault(
                    "error", f"no PubChem compound matched {ligand_name!r}"
                )
        except Exception as exc:  # noqa: BLE001 - per-ligand isolation
            cross_ref["error"] = f"PubChem lookup failed: {exc!r}"

        results.append(cross_ref)

    return {
        "success": True,
        "data": {
            "protein_id": uniprot_id,
            "ligands": results,
            "total": len(results),
            "detail_level": detail_level,
        },
    }


def _parse_site(site_str: Any) -> list[str]:
    """Split a CovInDB ``Site`` string into individual residues."""
    if site_str is None or (isinstance(site_str, float) and pd.isna(site_str)):
        return []
    site_str = str(site_str).strip()
    if site_str in ("NT", "N-term", "N-terminal"):
        return ["NT"]
    if "cofactor" in site_str.lower() or "enzyme" in site_str.lower():
        return ["COFACTOR"]
    sites: list[str] = []
    for part in re.split(r"[，,;]", site_str):
        part = part.strip()
        if not part:
            continue
        match = re.match(r"([A-Z]+)[-\s]*(\d+)", part)
        if match:
            residue, number = match.groups()
            sites.append(f"{residue}-{number}")
        elif part in ("NT", "N-term"):
            sites.append("NT")
        else:
            sites.append(part)
    return sites


def _is_orthosteric_site(site: str, target_gene: Any) -> bool:
    if site in ("NT", "COFACTOR"):
        return False
    match = re.match(r"([A-Z]+)-(\d+)", site)
    if not match:
        return False
    target_upper = str(target_gene).upper() if target_gene is not None else ""
    for gene_pattern, sites in _ORTHOSTERIC_SITES.items():
        if gene_pattern in target_upper and site in sites:
            return True
    if site in _ORTHOSTERIC_SITES["GENERAL_CATALYTIC"]:
        return True
    residue = match.group(1)
    return residue in ("SER", "CYS", "HIS", "ASP", "GLU", "LYS")


def _is_allosteric_candidate(sites: list[str], target_gene: Any) -> bool:
    if not sites:
        return True
    for site in sites:
        if _is_orthosteric_site(site, target_gene):
            return False
    indicators = ("NT", "COFACTOR", "CYS-", "SER-", "LYS-")
    for site in sites:
        if any(ind in site for ind in indicators):
            return True
    return True


def _confidence_level(sites: list[str], is_allosteric: bool) -> str:
    if not is_allosteric:
        return "High (Orthosteric)"
    site_str = "|".join(sites) if sites else str(sites)
    if any(ind in site_str for ind in ("NT", "COFACTOR", "CYS-1", "CYS-2")):
        return "High (Allosteric)"
    if any(ind in site_str for ind in ("CYS-", "SER-", "LYS-")):
        return "Medium (Allosteric)"
    return "Low (Investigate)"


@with_return_contract(source_version="1.0")
def map_covalent_probes_to_allosteric(uniprot_id: str,
                                      dataset_path: str = _DEFAULT_COVINDB):
    """Return the covalent-probe attachment sites recorded for a target.

    Does not answer whether a site is an allosteric site in the
    protein: it reports where covalent probes were observed to attach
    and classifies each site as orthosteric-like or an allosteric
    candidate using residue-type rules.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession, matched against the ``Target`` column.
    dataset_path : str
        Path to ``CovInDB_All.csv``. Default
        ``/biolab_data/data_lake/CovInDB_All.csv``; override with the
        ``ALLOAGENT_COVINDB`` environment variable.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "uniprot_id": <str>,
                "total_entries": <int>,
                "records": [ {...}, ... ],
                "columns": [<str>, ...],
                "war_head_counts": {<str>: <int>, ...},
                "unique_inchi_keys": <int>,
            }
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {"success": False,
                "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}"}

    path = Path(os.environ.get("ALLOAGENT_COVINDB") or dataset_path)
    if not path.is_file():
        return {
            "success": False,
            "error": (
                f"CovInDB dataset not found at {path}; mount the Biolab data "
                f"lake read-only or pass dataset_path"
            ),
        }
    try:
        df = pd.read_csv(path)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        return {"success": False, "error": f"could not read {path}: {exc}"}

    if "Target" not in df.columns:
        return {
            "success": False,
            "error": f"{path} has no 'Target' column (columns: {list(df.columns)})",
        }

    subset = df[df["Target"].astype(str).str.contains(
        uniprot_id, case=False, na=False)].copy()
    available = [c for c in _COVINDB_COLUMNS if c in subset.columns]
    subset = subset[available].copy()

    subset["Parsed_Sites"] = subset["Site"].apply(_parse_site)
    subset["Allosteric_Candidate"] = [
        _is_allosteric_candidate(row["Parsed_Sites"], row.get("Target_Gene"))
        for _, row in subset.iterrows()
    ]
    subset["Site_Count"] = subset["Parsed_Sites"].apply(len)
    subset["Confidence"] = [
        _confidence_level(row["Parsed_Sites"], row["Allosteric_Candidate"])
        for _, row in subset.iterrows()
    ]

    records = subset.to_dict("records")
    for rec in records:
        for k, v in rec.items():
            if not isinstance(v, (str, int, float, bool, type(None), list)):
                rec[k] = str(v)
        rec["Parsed_Sites"] = list(rec.get("Parsed_Sites") or [])
        rec["Allosteric_Candidate"] = bool(rec.get("Allosteric_Candidate"))

    war_head_counts = dict(
        Counter(str(r.get("War_head")) for r in records if r.get("War_head"))
    )
    unique_keys = {r.get("InChI_Key") for r in records if r.get("InChI_Key")}

    return {
        "success": True,
        "data": {
            "uniprot_id": uniprot_id,
            "total_entries": len(records),
            "records": records,
            "columns": list(subset.columns),
            "war_head_counts": war_head_counts,
            "unique_inchi_keys": len(unique_keys),
        },
    }


@with_return_contract(source_version="1.0")
def analyze_site_patterns(sites: Any):
    """Summarise the residue sites found in a set of covalent-probe records.

    Does not answer whether any of the sites is an allosteric site; it
    only counts how often each site and each residue type occurs.

    Parameters
    ----------
    sites : pandas.DataFrame or list or dict
        Either a DataFrame with a ``Parsed_Sites`` column, or the
        ``data`` dict returned by ``map_covalent_probes_to_allosteric``
        (which carries ``records``), or a list of records.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "total_unique_sites": <int>,
                "most_common_sites": [[<site>, <count>, ...], ...],
                "residue_distribution": [[<residue>, <count>, ...], ...],
                "total_entries": <int>,
            }
    """
    if isinstance(sites, dict):
        sites = sites.get("records", [])
    if isinstance(sites, pd.DataFrame):
        rows = sites.to_dict("records")
    elif isinstance(sites, list):
        rows = sites
    else:
        return {
            "success": False,
            "error": (
                f"sites must be a DataFrame, a list of records or the data "
                f"dict from map_covalent_probes_to_allosteric, got "
                f"{type(sites).__name__}"
            ),
        }

    all_sites: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        parsed = row.get("Parsed_Sites") or []
        if isinstance(parsed, str):
            parsed = [parsed]
        for site in parsed:
            if site:
                all_sites.append(str(site))

    site_counter = Counter(all_sites)
    residue_counter = Counter()
    for site in all_sites:
        if "-" in site:
            residue_counter[site.split("-")[0]] += 1

    return {
        "success": True,
        "data": {
            "total_unique_sites": len(site_counter),
            "most_common_sites": [list(x) for x in site_counter.most_common(20)],
            "residue_distribution": [list(x) for x in residue_counter.most_common()],
            "total_entries": len(rows),
        },
    }


@with_return_contract(source_version="1.0")
def fetch_allosteric_residue_potential(pdb_id: str, chain_id: Optional[str] = None):
    """Return the STINGAllo allosteric residue list for a PDB entry and chain.

    This is the old repo's ``fetch_allosteric_residue_potential``. It
    queries the same endpoint, with the same parameters, as the
    already-verified T3 tool, so it delegates to
    ``get_stingallo_allosteric_residues`` rather than issuing a second,
    unrestricted set of requests. The T3 implementation also enforces
    the API's documented rate limits (100 requests/IP/day, 30 unique
    PDBs/IP/day).

    Does not answer whether a residue is an allosteric site in a given
    conformational transition; it returns the residue list STINGAllo
    records for the entry.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id.
    chain_id : str or None
        Optional chain id.

    Returns
    -------
    dict
        Contract dict. ``data`` is the T3 payload:
        ``{pdb_id, chain_id, residues: [...]}``.
    """
    from biomni.tool.get_stingallo_allosteric_residues import (
        get_stingallo_allosteric_residues,
    )

    result = get_stingallo_allosteric_residues(pdb_id, chain_id)
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error") or "STINGAllo lookup failed",
        }
    return {
        "success": True,
        "data": {
            "pdb_id": result["data"]["pdb_id"],
            "chain_id": result["data"]["chain_id"],
            "residues": result["data"]["residues"],
            "merged_into": "get_stingallo_allosteric_residues",
        },
    }

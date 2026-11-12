"""Cross-referencing of ligands across the local ligand datasets (ported
from the old repo's ``alloagent/tool/cross_reference.py``).

Questions this module answers: for a set of ligands, which local
datasets (BioLiP, ASD AP, ASD DR, ASD XF, ChEMBL/PubChem) have a record
for it, and what do those records say.

The old tool returned a JSON **string**; the ported tool returns the
dict, because the per-run recorder is JSON and the old string was only
what an LLM prompt used to receive. The old tool also called
``asd.get_asd_ap_data`` and ``asd.get_asd_dr_data``, neither of which
the old ``asd.py`` defined -- both calls were swallowed by
``except Exception: pass``, so the ASD AP and DR branches were always
empty. The port uses the readers that now exist in
``biomni/tool/asd.py``.
"""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from biomni.tool._netcall import with_return_contract

VERSION = "0.3"

_SUPPORTED_DATABASES = (
    "biolip", "asd_ap", "asd_dr", "asd_xf", "chembl_pubchem",
)


def _compute_catalytic_overlap(catalytic_residues, allosteric_residues):
    """Overlap between a catalytic residue set and an allosteric one."""
    if not catalytic_residues or not allosteric_residues:
        return {
            "overlap_count": 0,
            "overlap_residues": [],
            "overlap_percentage": 0.0,
        }
    cat_set = {str(r).strip() for r in catalytic_residues if r}
    allo_set = {str(r).strip() for r in allosteric_residues if r}
    overlap = sorted(cat_set & allo_set)
    percentage = (len(overlap) / len(cat_set) * 100) if cat_set else 0.0
    return {
        "overlap_count": len(overlap),
        "overlap_residues": overlap,
        "overlap_percentage": round(percentage, 2),
    }


def _summarize_counts(results: list) -> dict[str, Any]:
    """Count the ligands and the per-database provenance."""
    per_db: dict[str, int] = {}
    for record in results:
        for db in record.get("provenance", []):
            per_db[db] = per_db.get(db, 0) + 1
    return {"total_ligands": len(results), "per_database": per_db}


def _safe_json(obj):
    """JSON-safe copy of an arbitrary object."""
    import json

    return json.loads(json.dumps(obj, default=str))


@with_return_contract(source_version="1.0")
def cross_reference_ligands(
    pdb_id: Optional[str] = None,
    uniprot_id: Optional[str] = None,
    ligands: Optional[list] = None,
    databases: Optional[list] = None,
    detail_level: str = "slim",
    use_llm: bool = False,
):
    """Cross-reference ligands across the local datasets and return the records.

    Does not answer whether a ligand is an allosteric or an orthosteric
    binder; it answers which datasets have a record for the ligand.

    Parameters
    ----------
    pdb_id : str or None
        PDB id, used for the BioLiP lookup.
    uniprot_id : str or None
        UniProt accession, used for the ASD AP and ASD XF lookups.
    ligands : list or None
        Explicit ligand names. ``None`` derives them from ``pdb_id`` via
        BioLiP.
    databases : list or None
        Dataset ids to include. One or more of ``biolip``, ``asd_ap``,
        ``asd_dr``, ``asd_xf``, ``chembl_pubchem``. Default
        ``["biolip", "asd_ap", "asd_dr", "asd_xf"]``.
    detail_level : str
        ``"slim"`` (default) or ``"full"``; passed to the ChEMBL/PubChem
        cross-reference.
    use_llm : bool
        Best-effort LLM summary of the counts. Never required; when no
        model is configured the summary is the documented "not available"
        string.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "query": {"pdb_id", "uniprot_id", "ligands"},
                "databases": [str, ...],
                "results": [{"ligand": str, "provenance": [str, ...],
                             "data": {...}}, ...],
                "summary": {"total_ligands": int,
                            "per_database": {str: int}},
                "llm_summary": <str or None>,
                "metadata": {"version": str},
            }
    """
    from biomni.tool import asd, biolip

    if databases is None:
        databases = ["biolip", "asd_ap", "asd_dr", "asd_xf"]
    if not isinstance(databases, list):
        return {"success": False,
                "error": f"databases must be a list, got {type(databases).__name__}"}
    unknown = [d for d in databases if d not in _SUPPORTED_DATABASES]
    if unknown:
        return {
            "success": False,
            "error": (
                f"unknown database(s) {unknown}; supported: "
                f"{list(_SUPPORTED_DATABASES)}"
            ),
        }
    if detail_level not in ("slim", "full"):
        return {
            "success": False,
            "error": f"detail_level must be 'slim' or 'full', got {detail_level!r}",
        }

    if pdb_id:
        pdb_id = str(pdb_id).strip().lower()
    if uniprot_id:
        uniprot_id = str(uniprot_id).strip()

    if ligands is None:
        ligands = []
        if pdb_id and "biolip" in databases:
            probe = biolip.biolip_ligands(pdb_id)
            if probe.get("success"):
                ligands.extend(str(x) for x in probe["data"]["ligands"])
    if not isinstance(ligands, list):
        return {"success": False,
                "error": f"ligands must be a list or None, got {type(ligands).__name__}"}
    ligands = sorted({str(x).strip() for x in ligands if str(x).strip()})

    if not ligands and not uniprot_id:
        return {
            "success": False,
            "error": (
                "No ligands or UniProt ID provided; nothing to cross-reference."
            ),
        }

    asd_ap_records: list[dict[str, Any]] = []
    if "asd_ap" in databases and (uniprot_id or pdb_id):
        asd_ap_records = asd._asd_ap_rows(uniprot_id=uniprot_id, pdb_id=pdb_id)

    asd_dr_records: list[dict[str, Any]] = []
    if "asd_dr" in databases and uniprot_id:
        asd_dr_records = asd._asd_dr_rows(target_id=uniprot_id)

    asd_xf_protein: dict[str, Any] = {}
    if "asd_xf" in databases and uniprot_id:
        probe = asd.parse_asd_xf([uniprot_id])
        if probe.get("success"):
            asd_xf_protein = probe["data"]["proteins"].get(uniprot_id, {})

    biolip_rows: list[dict[str, Any]] = []
    if pdb_id and "biolip" in databases:
        probe = biolip.parse_biolip_interactions(pdb_id)
        if probe.get("success"):
            biolip_rows = probe["data"]["records"]

    chembl_ref = None
    if "chembl_pubchem" in databases:
        from biomni.tool.allosteric import cross_reference_ligands_chembl_pubchem

        chembl_ref = cross_reference_ligands_chembl_pubchem

    results: list[dict[str, Any]] = []
    for ligand in ligands:
        record: dict[str, Any] = {"ligand": ligand, "provenance": [], "data": {}}

        if biolip_rows:
            matching = [
                r for r in biolip_rows
                if str(r.get("Ligand", "")).lower() == ligand.lower()
            ]
            if matching:
                record["data"]["biolip"] = matching
                record["provenance"].append("biolip")

        if asd_ap_records:
            matches = [
                r for r in asd_ap_records
                if ligand.lower() in str(r.get("uniprot_id", "")).lower()
                or ligand.lower() in str(r.get("gene_name", "")).lower()
                or ligand.lower() in str(r.get("pdb_id", "")).lower()
            ]
            if matches:
                record["data"]["asd_ap"] = matches
                record["provenance"].append("asd_ap")

        if asd_dr_records:
            matches = [
                r for r in asd_dr_records
                if ligand.lower() in str(r.get("drug_all_name", "")).lower()
            ]
            if matches:
                record["data"]["asd_dr"] = matches
                record["provenance"].append("asd_dr")

        if asd_xf_protein:
            sites = asd_xf_protein.get("sites", [])
            if sites:
                record["data"]["asd_xf_sites"] = sites
                record["provenance"].append("asd_xf")

            cat_residues: list[str] = []
            if record["data"].get("biolip"):
                first = record["data"]["biolip"][0]
                for candidate in (
                    "Catalytic_Site_Residues_PDB", "Catalytic_site_residues",
                    "Residue", "Residues",
                ):
                    if candidate in first:
                        value = first.get(candidate)
                        if isinstance(value, (list, tuple)):
                            cat_residues = list(value)
                        elif isinstance(value, str):
                            cat_residues = [x.strip() for x in value.split(",") if x.strip()]
                        break
            allo_residues: list[str] = []
            for site in sites:
                value = (
                    site.get("site_residues")
                    or site.get("Allosteric_Site_Residue")
                    or site.get("pdb_site")
                )
                if value:
                    if isinstance(value, list):
                        allo_residues.extend(value)
                    else:
                        allo_residues.extend(
                            [x.strip() for x in str(value).split(",") if x.strip()]
                        )
            if cat_residues and allo_residues:
                record["data"]["catalytic_overlap"] = _compute_catalytic_overlap(
                    cat_residues, allo_residues
                )

        if chembl_ref is not None:
            chem = chembl_ref(
                uniprot_id or "", [{"ligand_name": ligand}],
                detail_level=detail_level,
            )
            if chem.get("success"):
                record["data"]["chembl_pubchem"] = chem["data"]
                record["provenance"].append("chembl_pubchem")

        results.append(record)

    summary = _summarize_counts(results)

    llm_summary = None
    if use_llm:
        llm_summary = _llm_summary(summary)

    return {
        "success": True,
        "data": {
            "query": {"pdb_id": pdb_id, "uniprot_id": uniprot_id,
                       "ligands": ligands},
            "databases": databases,
            "results": _safe_json(results),
            "summary": summary,
            "llm_summary": llm_summary,
            "metadata": {"version": VERSION},
        },
    }


def _llm_summary(summary: dict[str, Any]) -> str:
    """Best-effort LLM summary of the cross-reference counts."""
    try:
        from biomni.tool._model import chat_model_for_database_tools

        model = chat_model_for_database_tools()
        prompt = (
            f"Summarize cross-references for "
            f"{summary.get('total_ligands', 0)} ligands. Provide short bullets: "
            f"provenance counts and any potential interesting matches.\n"
            f"Results: {_safe_json(summary)}"
        )
        response = model.invoke(prompt)
        content = getattr(response, "content", response)
        return str(content)
    except Exception:
        return "LLM summary not available (missing credentials or library)"


@with_return_contract(source_version="1.0")
def retrieve_and_filter_large_dataset(
    filepath: str,
    columns_to_load: Optional[list] = None,
    filter_column: Optional[str] = None,
    filter_value: Optional[str] = None,
):
    """Load and filter a large CSV dataset without loading it all into memory.

    Does not answer anything about the biology in the file; it answers
    which rows of a large dataset match a filter.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    columns_to_load : list or None
        Columns to read. ``None`` reads every column.
    filter_column : str or None
        Column to filter on. ``"Target"`` is matched against the
        UniProt accession (case-insensitive substring); any other column
        is matched the same way.
    filter_value : str or None
        Value to match in ``filter_column``.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "data": [ {<column>: <value>, ...}, ... ],
                "metadata": {"filepath", "columns_loaded",
                             "columns_requested", "filter_applied",
                             "rows_returned", "status"},
                "filter_summary": <str>,
            }
    """
    if not isinstance(filepath, str) or not filepath:
        return {"success": False,
                "error": f"filepath must be a non-empty string, got {filepath!r}"}

    path = _resolve_dataset_path(filepath)
    if not path.is_file():
        message = f"Dataset not found at {filepath}"
        return {
            "success": False,
            "error": message,
            "data": {
                "data": [],
                "metadata": {
                    "filepath": filepath,
                    "columns_requested": columns_to_load,
                    "filter_applied": {"column": filter_column,
                                       "value": filter_value},
                    "rows_returned": 0,
                    "status": "error",
                },
                "filter_summary": message,
            },
        }

    try:
        df = pd.read_csv(path, usecols=columns_to_load, low_memory=False)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        message = f"Error loading dataset: {exc}"
        return {
            "success": False,
            "error": message,
            "data": {
                "data": [],
                "metadata": {
                    "filepath": filepath,
                    "columns_requested": columns_to_load,
                    "filter_applied": {"column": filter_column,
                                       "value": filter_value},
                    "rows_returned": 0,
                    "status": "error",
                },
                "filter_summary": message,
            },
        }

    if filter_column and filter_value and filter_column in df.columns:
        df = df[df[filter_column].astype(str).str.contains(
            str(filter_value), case=False, na=False)]

    records = df.to_dict("records")
    for rec in records:
        for k, v in rec.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                rec[k] = str(v)

    status = "success" if len(records) else "no_matches"
    if not records:
        summary = (
            f"No matches found for {filter_column}={filter_value}"
            if filter_column else "No rows in dataset"
        )
    else:
        summary = f"Loaded {len(records)} rows with {len(df.columns)} columns"

    return {
        "success": True,
        "data": {
            "data": records,
            "metadata": {
                "filepath": filepath,
                "columns_loaded": list(df.columns),
                "columns_requested": columns_to_load,
                "filter_applied": {"column": filter_column,
                                   "value": filter_value},
                "rows_returned": len(records),
                "status": status,
            },
            "filter_summary": summary,
        },
    }


def _resolve_dataset_path(filepath: str):
    """Resolve a dataset path, allowing the mounted data lake prefix."""
    from pathlib import Path

    path = Path(filepath)
    if path.is_file():
        return path
    if not path.is_absolute():
        candidate = Path("/biolab_data") / path
        if candidate.is_file():
            return candidate
    return path

#!/usr/bin/env python3
"""
Minimal, robust cross-referencing utility for ligands across available datasets.
- Supports selectable databases: 'biolip', 'asd_ap', 'asd_dr', 'asd_xf', 'chembl_pubchem'
- Minimal surface API that returns a JSON string suitable for downstream LLM/agent consumption
- Optional lightweight summarization (no external LLM required); can attempt OpenAI if available
"""

from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

# Local dataset helpers
from biomni_biolab.tool import biolip
from biomni_biolab.tool import asd
try:
    # optional heavy-weight cross-ref
    from biomni_biolab.tool.allosteric import cross_reference_ligands_chembl_pubchem
except Exception:
    cross_reference_ligands_chembl_pubchem = None

__all__ = ["cross_reference_ligands"]

VERSION = "0.2"


def _compute_catalytic_overlap(catalytic_residues, allosteric_residues):
    if not catalytic_residues or not allosteric_residues:
        return {"overlap_count": 0, "overlap_residues": [], "overlap_percentage": 0.0}

    cat_set = set(str(r).strip() for r in catalytic_residues if r)
    allo_set = set(str(r).strip() for r in allosteric_residues if r)
    overlap = sorted(cat_set.intersection(allo_set))
    overlap_count = len(overlap)
    overlap_percentage = (overlap_count / len(cat_set) * 100) if cat_set else 0.0
    return {"overlap_count": overlap_count, "overlap_residues": overlap, "overlap_percentage": round(overlap_percentage, 2)}


def _summarize_counts(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {"total_ligands": len(results)}
    per_db = {}
    for r in results:
        for db in r.get("provenance", []):
            per_db[db] = per_db.get(db, 0) + 1
    counts["per_database"] = per_db
    return counts


def _safe_json(obj):
    return json.loads(json.dumps(obj, default=str))


def cross_reference_ligands(
    pdb_id: Optional[str] = None,
    uniprot_id: Optional[str] = None,
    ligands: Optional[List[str]] = None,
    databases: Optional[List[str]] = None,
    detail_level: str = "slim",
    use_llm: bool = False,
    llm_provider: str = "openai",
) -> str:
    """
    Cross-reference ligands across selectable datasets and return a JSON string.

    Args:
        pdb_id: PDB identifier (e.g., '1I09') to lookup BioLiP ligands (optional)
        uniprot_id: UniProt identifier to lookup ASD datasets (optional)
        ligands: explicit list of ligand names (optional)
        databases: list of dataset ids to include (defaults to ['biolip','asd_ap','asd_dr','asd_xf'])
        detail_level: 'slim' or 'full' (where supported)
        use_llm: try to call an LLM to summarize (best-effort; optional)
        llm_provider: provider name (currently only tries 'openai' if available)

    Returns: JSON string with structure:
      { query: {...}, databases: [...], results: [...], summary: {...}, metadata: {...}}
    """
    databases = databases or ["biolip", "asd_ap", "asd_dr", "asd_xf"]

    # Normalize pdb/uniprot
    if pdb_id:
        pdb_id = str(pdb_id).strip().lower()
    if uniprot_id:
        uniprot_id = str(uniprot_id).strip()

    # Resolve ligands list
    if ligands is None:
        ligands = []
        if pdb_id and "biolip" in databases:
            try:
                ligs = biolip.biolip_ligands(pdb_id)
                ligands.extend([str(l) for l in ligs])
            except Exception:
                pass
    ligands = list({str(l).strip() for l in ligands if l})

    if not ligands and not uniprot_id:
        return json.dumps({"error": "No ligands or UniProt ID provided; nothing to cross-reference."}, indent=2)

    results = []

    # Pre-fetch ASD data when needed
    asd_ap_data = None
    asd_dr_data = None
    asd_xf_data = None

    if "asd_ap" in databases and (uniprot_id or pdb_id):
        try:
            asd_ap_data = asd.get_asd_ap_data(uniprot_id=uniprot_id, pdb_id=pdb_id, all_columns=True)
            asd_ap_records = asd_ap_data.get("data", []) if isinstance(asd_ap_data, dict) else []
        except Exception:
            asd_ap_records = []
    else:
        asd_ap_records = []

    if "asd_dr" in databases and uniprot_id:
        try:
            asd_dr_data = asd.get_asd_dr_data(target_id=uniprot_id, all_columns=True)
            asd_dr_records = asd_dr_data.get("data", []) if isinstance(asd_dr_data, dict) else []
        except Exception:
            asd_dr_records = []
    else:
        asd_dr_records = []

    if "asd_xf" in databases and uniprot_id:
        try:
            asd_xf_data = asd.parse_asd_xf(target_proteins=[uniprot_id])
            asd_xf_protein = asd_xf_data.get(uniprot_id, {}) if isinstance(asd_xf_data, dict) else {}
        except Exception:
            asd_xf_protein = {}
    else:
        asd_xf_protein = {}

    # For each ligand, assemble cross-reference information
    for ligand in ligands:
        record: Dict[str, Any] = {"ligand": ligand, "provenance": [], "data": {}}

        # BioLiP details (if PDB provided)
        if pdb_id and "biolip" in databases:
            try:
                df = biolip.parse_biolip_interactions(pdb_id)
                matching = df[df['Ligand'].astype(str).str.lower() == str(ligand).lower()]
                biolip_rows = [row.dropna().to_dict() for _, row in matching.iterrows()]
                if biolip_rows:
                    record['data']['biolip'] = biolip_rows
                    record['provenance'].append('biolip')
            except Exception:
                pass

        # ASD AP hits
        if asd_ap_records:
            try:
                matches = [r for r in asd_ap_records if (str(r.get('ligand_name', '')).lower().find(str(ligand).lower()) != -1) or (str(r.get('uniprot_id',''))==uniprot_id)]
                if matches:
                    record['data']['asd_ap'] = matches
                    record['provenance'].append('asd_ap')
            except Exception:
                pass

        # ASD DR hits
        if asd_dr_records:
            try:
                matches = [r for r in asd_dr_records if (str(r.get('drug_all_name','')).lower().find(str(ligand).lower()) != -1)]
                if matches:
                    record['data']['asd_dr'] = matches
                    record['provenance'].append('asd_dr')
            except Exception:
                pass

        # ASD XF (structural / site-level)
        if asd_xf_protein:
            try:
                # attach site information and compute overlap when possible
                sites = asd_xf_protein.get('sites', [])
                if sites:
                    record['data']['asd_xf_sites'] = sites
                    record['provenance'].append('asd_xf')

                # compute catalytic overlap if biolip catalytic residues present
                cat_residues = []
                if 'biolip' in record['data'] and len(record['data']['biolip'])>0:
                    # try to find catalytic or residue columns
                    first = record['data']['biolip'][0]
                    for candidate in ['Catalytic_site_residues', 'catalytic_site_residues', 'Residue', 'Residues']:
                        if candidate in first:
                            val = first.get(candidate)
                            if isinstance(val, (list, tuple)):
                                cat_residues = val
                            elif isinstance(val, str):
                                cat_residues = [x.strip() for x in val.split(',') if x.strip()]
                            break

                allo_residues = []
                for s in sites:
                    v = s.get('site_residues') or s.get('Allosteric_Site_Residue') or s.get('pdb_site')
                    if v:
                        if isinstance(v, list):
                            allo_residues.extend(v)
                        else:
                            allo_residues.extend([x.strip() for x in str(v).split(',') if x.strip()])

                if cat_residues and allo_residues:
                    record['data']['catalytic_overlap'] = _compute_catalytic_overlap(cat_residues, allo_residues)
            except Exception:
                pass

        # Optional chembl/pubchem cross ref
        if "chembl_pubchem" in databases and cross_reference_ligands_chembl_pubchem is not None:
            try:
                chem = cross_reference_ligands_chembl_pubchem(uniprot_id or "", [{"ligand_name": ligand}], detail_level=detail_level)
                record['data']['chembl_pubchem'] = chem
                record['provenance'].append('chembl_pubchem')
            except Exception:
                pass

        results.append(record)

    summary = _summarize_counts(results)

    # If requested, try a lightweight LLM summary (best-effort)
    llm_summary = None
    if use_llm:
        try:
            # prefer OpenAI if available
            import openai
            prompt = f"Summarize cross-references for {len(results)} ligands. Provide short bullets: provenance counts and any potential interesting matches.\nResults: {json.dumps(summary)}"
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], max_tokens=256)
            llm_summary = resp.choices[0].message.content
        except Exception:
            llm_summary = "LLM summary not available (missing credentials or library)"

    output = {
        "query": {"pdb_id": pdb_id, "uniprot_id": uniprot_id, "ligands": ligands},
        "databases": databases,
        "results": _safe_json(results),
        "summary": summary,
        "llm_summary": llm_summary,
        "metadata": {"version": VERSION}
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


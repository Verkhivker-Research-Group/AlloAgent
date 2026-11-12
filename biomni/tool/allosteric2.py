"""Allosteric core analysis (ported from the old repo's
``alloagent/tool/allosteric2.py``).

Questions this module answers: which residues does the Allosteric
Database flag for a protein, which of them are shared by several
modulators, and how are they wired into a residue-interaction network.

The old functions returned bare dicts, printed to stdout and raised on
error. The ported versions return the standard contract dict and never
print.

The protein -> ASD map is the committed ``biomni/tool/_asd_index.tsv``;
the ASD AS residue table and the ASD XF XML files are mounted read-only
at ``/biolab_data``.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from biomni.tool._netcall import with_return_contract

_DEFAULT_LAKE = Path("/biolab_data/data_lake")
_AS_CSV = "ASD_Release_202309_AS.csv"
_INDEX_TSV = Path(__file__).resolve().parent / "_asd_index.tsv"

_INDEX_CACHE: Optional[dict[str, str]] = None


def _asd_index() -> dict[str, str]:
    """UniProt accession -> ASD XF file stem."""
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE
    index: dict[str, str] = {}
    if _INDEX_TSV.is_file():
        for line in _INDEX_TSV.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) == 2:
                index[parts[0].strip()] = parts[1].strip()
    _INDEX_CACHE = index
    return index


def _lake_root() -> Path:
    return Path(os.environ.get("ASD_LAKE_ROOT") or _DEFAULT_LAKE)


@with_return_contract(source_version="1.0")
def convert_uniprot_to_asd(uniprot_id: str):
    """Return the Allosteric Database file id for a UniProt accession.

    Does not answer whether the protein has curated allosteric sites,
    and it does not name the modulators.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession.

    Returns
    -------
    dict
        Contract dict. ``data`` is ``{uniprot_id, asd_id}`` where
        ``asd_id`` is ``None`` when the accession is not in ASD.
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {"success": False,
                "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}"}
    return {
        "success": True,
        "data": {
            "uniprot_id": uniprot_id,
            "asd_id": _asd_index().get(uniprot_id),
        },
    }


@with_return_contract(source_version="1.0")
def convert_asd_to_uniprot(asd_id: str):
    """Return the UniProt accession for an Allosteric Database file id.

    Does not answer whether the protein has curated allosteric sites,
    and it does not name the modulators.

    Parameters
    ----------
    asd_id : str
        ASD file id, e.g. ``"ASD00020000_1"``.

    Returns
    -------
    dict
        Contract dict. ``data`` is ``{asd_id, uniprot_id}`` where
        ``uniprot_id`` is ``None`` when the id is not in ASD.
    """
    if not isinstance(asd_id, str) or not asd_id:
        return {"success": False,
                "error": f"asd_id must be a non-empty string, got {asd_id!r}"}
    uniprot = None
    for acc, stem in _asd_index().items():
        if stem == asd_id:
            uniprot = acc
            break
    return {
        "success": True,
        "data": {"asd_id": asd_id, "uniprot_id": uniprot},
    }


@with_return_contract(source_version="1.0")
def normalize_protein_id(protein_id: str):
    """Resolve a UniProt accession or an ASD id to both forms.

    Does not answer anything about the protein's allosteric sites.

    Parameters
    ----------
    protein_id : str
        Either a UniProt accession or an ASD file id.

    Returns
    -------
    dict
        Contract dict. ``data`` is ``{protein_id, uniprot_id, asd_id,
        found}``; both ids are ``None`` when the id is not in ASD.
    """
    if not isinstance(protein_id, str) or not protein_id:
        return {"success": False,
                "error": f"protein_id must be a non-empty string, got {protein_id!r}"}
    index = _asd_index()
    if protein_id in index:
        return {
            "success": True,
            "data": {
                "protein_id": protein_id,
                "uniprot_id": protein_id,
                "asd_id": index[protein_id],
                "found": True,
            },
        }
    for acc, stem in index.items():
        if stem == protein_id:
            return {
                "success": True,
                "data": {
                    "protein_id": protein_id,
                    "uniprot_id": acc,
                    "asd_id": protein_id,
                    "found": True,
                },
            }
    return {
        "success": True,
        "data": {
            "protein_id": protein_id,
            "uniprot_id": None,
            "asd_id": None,
            "found": False,
        },
    }


def _extract_asd_residues(raw_residues: Any) -> list[str]:
    """Split an ASD AS ``allosteric_site_residue`` cell into residues."""
    if raw_residues is None or (isinstance(raw_residues, float)
                                and np.isnan(raw_residues)):
        return []
    text = str(raw_residues).strip()
    if not text:
        return []
    residues: list[str] = []
    for segment in re.split(r";\s*", text):
        segment = re.sub(r"^Chain\s+[A-Za-z0-9]+:\s*", "", segment.strip())
        if not segment:
            continue
        for res in segment.split(","):
            res = res.strip().replace(" ", "")
            if res:
                residues.append(res)
    return residues


@with_return_contract(source_version="1.0")
def allosteric_hotspot_detection(
    uniprot_id: str,
    celltype_data_path: Optional[str] = None,
    min_modulator_count: int = 3,
    percentile_threshold: float = 75.0,
    asd_as_path: Optional[str] = None,
):
    """Rank the residues that several modulators act on in the same protein.

    Does not predict an allosteric site. It ranks residues that the
    curated ASD AS table already lists, by how many distinct modulators
    act on them, how diverse those modulators are and the residue type.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession or ASD id.
    celltype_data_path : str or None
        Optional parquet of tissue marker genes, recorded as a data
        source when present.
    min_modulator_count : int
        Minimum number of modulator observations before a residue is a
        candidate. Default 3.
    percentile_threshold : float
        Percentile above which a candidate is called a hotspot. Default
        75.0 (the top quartile).
    asd_as_path : str or None
        Path to ``ASD_Release_202309_AS.csv``. Default
        ``/biolab_data/data_lake/ASD_Release_202309_AS.csv``.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "uniprot_id": <str>, "asd_id": <str>,
                "hotspots": [{"residue", "importance_score", "modulator_count",
                              "unique_modulators", "residue_type_score",
                              "example_modulators", "is_hotspot"}, ...],
                "hotspot_count": <int>,
                "residue_scores": {<residue>: {...}, ...},
                "candidate_count": <int>,
                "data_sources": [str, ...],
                "summary": <str>,
            }
    """
    norm = normalize_protein_id(uniprot_id)
    if not norm.get("success"):
        return norm
    if not norm["data"]["found"]:
        return {
            "success": False,
            "error": f"Protein ID {uniprot_id!r} not found in ASD index",
        }
    uniprot = norm["data"]["uniprot_id"]
    asd_id = norm["data"]["asd_id"]

    path = Path(asd_as_path) if asd_as_path else _lake_root() / _AS_CSV
    results: dict[str, Any] = {
        "uniprot_id": uniprot,
        "asd_id": asd_id,
        "hotspots": [],
        "hotspot_count": 0,
        "residue_scores": {},
        "candidate_count": 0,
        "data_sources": [],
        "summary": "",
    }

    residue_modulators: dict[str, list[str]] = defaultdict(list)
    residue_connectivity: dict[str, int] = defaultdict(int)

    if not path.is_file():
        results["summary"] = (
            f"ASD AS file not found at {path}; no hotspot candidates"
        )
        return {"success": True, "data": results}

    df = pd.read_csv(path, low_memory=False)
    required = {"allosteric_site_residue"}
    if not required.issubset(set(df.columns)):
        return {
            "success": False,
            "error": (
                f"{path} is missing the required column(s) "
                f"{sorted(required - set(df.columns))}"
            ),
        }
    filtered = df[
        (df.get("pdb_uniprot") == uniprot) | (df.get("target_id") == asd_id)
    ]
    for _, record in filtered.iterrows():
        modulator_name = (
            record.get("modulator_name")
            or record.get("modulator_serial")
            or "Unknown"
        )
        for res in _extract_asd_residues(record.get("allosteric_site_residue")):
            residue_modulators[res].append(str(modulator_name))
            residue_connectivity[res] += 1
    if not filtered.empty:
        results["data_sources"].append("ASD_AS")

    candidates = {
        res: count for res, count in residue_connectivity.items()
        if count >= min_modulator_count
    }
    results["candidate_count"] = len(candidates)
    if not candidates:
        results["summary"] = (
            f"No hotspots found with minimum {min_modulator_count} modulators"
        )
        return {"success": True, "data": results}

    max_connectivity = max(candidates.values())
    scores: dict[str, dict[str, Any]] = {}
    for res, connectivity in candidates.items():
        connectivity_score = connectivity / max_connectivity
        unique_mods = len(set(residue_modulators[res]))
        diversity_score = min(unique_mods / max(max_connectivity, 5), 1.0)
        if res.startswith("CYS"):
            residue_type_score = 0.9
        elif res.startswith(("LYS", "SER", "THR")):
            residue_type_score = 0.5
        else:
            residue_type_score = 0.3
        importance = (
            0.5 * connectivity_score
            + 0.3 * diversity_score
            + 0.2 * residue_type_score
        )
        scores[res] = {
            "importance_score": round(importance, 3),
            "modulator_count": connectivity,
            "unique_modulators": unique_mods,
            "residue_type_score": residue_type_score,
            "example_modulators": list(dict.fromkeys(residue_modulators[res]))[:5],
        }
    results["residue_scores"] = scores

    importance_values = [s["importance_score"] for s in scores.values()]
    percentile_value = float(np.percentile(importance_values, percentile_threshold))
    ranked = [
        {
            "residue": res,
            **scores[res],
            "is_hotspot": scores[res]["importance_score"] >= percentile_value,
        }
        for res in sorted(
            scores, key=lambda x: scores[x]["importance_score"], reverse=True
        )
    ]
    results["hotspots"] = [h for h in ranked if h["is_hotspot"]]
    results["hotspot_count"] = len(results["hotspots"])
    results["percentile_threshold_value"] = round(percentile_value, 4)

    if celltype_data_path and os.path.exists(celltype_data_path):
        try:
            celltype_df = pd.read_parquet(celltype_data_path)
            if "marker_gene" in celltype_df.columns:
                results["data_sources"].append("Celltype_markers")
        except Exception:
            pass

    if results["hotspots"]:
        top = results["hotspots"][0]
        results["summary"] = (
            f"Identified {results['hotspot_count']} allosteric hotspots "
            f"(top {percentile_threshold}% of {len(scores)} candidates). "
            f"Top hotspot: {top['residue']} "
            f"(score={top['importance_score']}, "
            f"{top['modulator_count']} modulators). "
            f"Data sources: {', '.join(set(results['data_sources']))}"
        )
    else:
        results["summary"] = (
            f"No high-confidence hotspots identified from {len(scores)} "
            f"candidate residues"
        )
    return {"success": True, "data": results}


@with_return_contract(source_version="1.0")
def residue_interaction_networks(
    uniprot_id: str,
    pdb_id: Optional[str] = None,
    ppi_data_path: Optional[str] = None,
    min_interactions: int = 2,
):
    """Build the residue-interaction network that could carry an allosteric signal.

    Does not assert that any pathway transmits a signal; it reports the
    network built from the curated ASD sites, optionally enriched with
    BioLiP contacts and PPI edges, together with its topology.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession or ASD id.
    pdb_id : str or None
        Optional PDB id, used to add BioLiP contact residues.
    ppi_data_path : str or None
        Optional directory of PPI parquet files to add edges from.
    min_interactions : int
        Minimum edge weight to include. Default 2.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "uniprot_id", "asd_id",
                "allosteric_sites": [{"site_id", "residues",
                                      "modulator_count", "modulators"}, ...],
                "network_nodes": [{"id", "node_type", "weight"}, ...],
                "network_edges": [{"source", "target", "weight"}, ...],
                "communication_pathways": [...],
                "network_metrics": {...},
                "data_sources": [str, ...],
                "summary": <str>,
            }
    """
    import networkx as nx

    from biomni.tool.asd import parse_asd_xf
    from biomni.tool.biolip import parse_biolip_interactions

    norm = normalize_protein_id(uniprot_id)
    if not norm.get("success"):
        return norm
    if not norm["data"]["found"]:
        return {
            "success": False,
            "error": f"Protein ID {uniprot_id!r} not found in ASD index",
        }
    uniprot = norm["data"]["uniprot_id"]
    asd_id = norm["data"]["asd_id"]

    results: dict[str, Any] = {
        "uniprot_id": uniprot,
        "asd_id": asd_id,
        "allosteric_sites": [],
        "network_nodes": [],
        "network_edges": [],
        "communication_pathways": [],
        "network_metrics": {},
        "data_sources": [],
        "summary": "",
    }

    probe = parse_asd_xf([uniprot])
    if probe.get("success"):
        asd_protein = probe["data"]["proteins"].get(uniprot, {})
        if asd_protein:
            modulators = asd_protein.get("modulators", [])
            modulator_names = [
                m.get("modulator_id", "Unknown") for m in modulators
            ]
            for site in asd_protein.get("sites", []):
                residues = site.get("site_residues") or []
                if isinstance(residues, str):
                    residues = [
                        r.strip() for r in residues.split(",") if r.strip()
                    ]
                results["allosteric_sites"].append({
                    "site_id": site.get("pdb_site"),
                    "residues": residues,
                    "modulator_count": len(modulators),
                    "modulators": modulator_names[:5],
                })
                if "ASD_XF" not in results["data_sources"]:
                    results["data_sources"].append("ASD_XF")

    biolip_residues: set[str] = set()
    if pdb_id:
        probe = parse_biolip_interactions(pdb_id)
        if probe.get("success"):
            for row in probe["data"]["records"]:
                for column in ("Binding_Site_Residues_PDB",
                               "Catalytic_Site_Residues_PDB"):
                    value = row.get(column)
                    if value:
                        biolip_residues.update(
                            r.strip() for r in str(value).split(",") if r.strip()
                        )
            if biolip_residues and "BioLiP" not in results["data_sources"]:
                results["data_sources"].append("BioLiP")

    graph = nx.Graph()
    allosteric_residues: set[str] = set()
    for site in results["allosteric_sites"]:
        for res in site.get("residues", []):
            allosteric_residues.add(res)
            graph.add_node(res, node_type="allosteric_site",
                           weight=site["modulator_count"])
    for res in biolip_residues:
        if res not in graph:
            graph.add_node(res, node_type="biolip_contact", weight=1)
    results["network_nodes"] = [
        {"id": node, **attrs} for node, attrs in graph.nodes(data=True)
    ]

    ppi_edges: dict[tuple, int] = defaultdict(int)
    if ppi_data_path:
        for ppi_file in ("genetic_interaction.parquet", "two-hybrid.parquet",
                         "synthetic_lethality.parquet",
                         "affinity_capture-ms.parquet"):
            file_path = os.path.join(ppi_data_path, ppi_file)
            if not os.path.exists(file_path):
                continue
            try:
                ppi_df = pd.read_parquet(file_path)
            except Exception:
                continue
            if "Protein_A" not in ppi_df.columns or "Protein_B" not in ppi_df.columns:
                continue
            subset = ppi_df[
                (ppi_df["Protein_A"].isin(allosteric_residues))
                | (ppi_df["Protein_B"].isin(allosteric_residues))
            ]
            for _, row in subset.iterrows():
                ppi_edges[(row["Protein_A"], row["Protein_B"])] += 1
            if not subset.empty:
                results["data_sources"].append(ppi_file.replace(".parquet", ""))

    for (res_a, res_b), weight in ppi_edges.items():
        if weight >= min_interactions:
            graph.add_edge(res_a, res_b, weight=weight)
            results["network_edges"].append({
                "source": res_a, "target": res_b, "weight": weight,
            })

    if len(allosteric_residues) > 1:
        allosteric_list = sorted(allosteric_residues)
        for i, res_a in enumerate(allosteric_list):
            for res_b in allosteric_list[i + 1:]:
                if nx.has_path(graph, res_a, res_b):
                    try:
                        path = nx.shortest_path(
                            graph, res_a, res_b,
                            weight=lambda x, y, d: 1 / max(d.get("weight", 1), 0.1),
                        )
                    except Exception:
                        continue
                    if len(path) > 2:
                        results["communication_pathways"].append({
                            "source_site": res_a,
                            "target_site": res_b,
                            "path": path,
                            "path_length": len(path),
                        })
    results["communication_pathways"] = results["communication_pathways"][:10]

    if graph.number_of_nodes() > 0:
        metrics: dict[str, Any] = {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0,
            "allosteric_node_count": len(allosteric_residues),
            "average_degree": (
                sum(dict(graph.degree()).values())
                / max(graph.number_of_nodes(), 1)
            ),
        }
        try:
            betweenness = nx.betweenness_centrality(graph, weight="weight")
            top = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
            metrics["top_central_residues"] = [
                {"residue": res, "centrality": float(cent)} for res, cent in top
            ]
        except Exception:
            pass
        results["network_metrics"] = metrics

    results["summary"] = (
        f"Network with {graph.number_of_nodes()} nodes and "
        f"{graph.number_of_edges()} edges. Found {len(allosteric_residues)} "
        f"allosteric residues from ASD_XF. Identified "
        f"{len(results['communication_pathways'])} inter-site communication "
        f"pathways. Data sources: {', '.join(set(results['data_sources']))}"
    )
    return {"success": True, "data": results}

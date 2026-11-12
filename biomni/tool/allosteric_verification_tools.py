"""Allosteric-evidence verification tools (ported from the old repo's
``alloagent/tool/allosteric_verification_tools.py``).

Questions this module answers: does the Allosteric Database confirm this
protein has curated allosteric sites, and how do candidate residues
score on structural distance, pocket shape, solvent accessibility and a
conservation surrogate.

The old functions returned bare dicts, printed to stdout and raised on
error. The ported versions return the standard contract dict and never
print.

**`evolutionary_conservation` is a surrogate, not a measurement.** It
does not build a multiple sequence alignment and does not measure real
conservation; it evaluates a deterministic pseudo-MSA entropy model
(the old code's own comment calls it "Pseudo-MSA simulation"). The
docstring and the tool card both say so. The port replaces the old
code's `hash()` seed -- salted per process, so the score changed
between runs -- with a stable sha256-derived seed.
"""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
from typing import Any, Callable, Optional

import numpy as np
import requests
from Bio import SeqIO
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley
from numpy import linalg as LA
from scipy.spatial import ConvexHull, distance

from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30

# Kyte-Doolittle hydropathy scale.
HYDROPHOBICITY = {
    'ALA': 1.8, 'ARG': -4.5, 'ASN': -3.5, 'ASP': -3.5, 'CYS': 2.5,
    'GLN': -3.5, 'GLU': -3.5, 'GLY': -0.4, 'HIS': -3.2, 'ILE': 4.5,
    'LEU': 3.8, 'LYS': -3.9, 'MET': 1.9, 'PHE': 2.8, 'PRO': -1.6,
    'SER': -0.8, 'THR': -0.7, 'TRP': -0.9, 'TYR': -1.3, 'VAL': 4.2,
}

# Maximum solvent accessibility per residue (Tien et al. 2013).
MAX_SASA = {
    'ALA': 129.0, 'ARG': 274.0, 'ASN': 195.0, 'ASP': 193.0, 'CYS': 167.0,
    'GLN': 223.0, 'GLU': 223.0, 'GLY': 104.0, 'HIS': 224.0, 'ILE': 197.0,
    'LEU': 201.0, 'LYS': 236.0, 'MET': 224.0, 'PHE': 240.0, 'PRO': 159.0,
    'SER': 155.0, 'THR': 172.0, 'TRP': 285.0, 'TYR': 263.0, 'VAL': 174.0,
}

# Shannon entropy of a uniform distribution over 20 amino acids.
MAX_SHANNON_ENTROPY = 4.322


def _stable_seed(text: str) -> int:
    """A seed that is the same in every process.

    The old code used ``hash()``, which Python salts per process, so the
    same input produced a different score on every run.
    """
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


@with_return_contract(source_version="1.0")
def load_pdb(pdb_id: str,
             query_pdb_identifiers: Optional[Callable] = None):
    """Fetch a PDB structure and parse it.

    Does not answer anything about allostery; it only loads the
    structure the other verification tools work on.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id.
    query_pdb_identifiers : callable or None
        Optional downloader. When given, it is called as
        ``query_pdb_identifiers(identifiers=[pdb_id], download=True,
        return_type='entry')`` and may return a file path or a dict with
        a ``file_path`` key. When it is absent or fails, the structure is
        downloaded from RCSB.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, atom_count, residue_count, chains: [str, ...],
        source}``. The parsed Biopython ``Structure`` object itself is
        not JSON-serialisable, so it is not returned.
    """
    if not isinstance(pdb_id, str) or not pdb_id:
        return {"success": False,
                "error": f"pdb_id must be a non-empty string, got {pdb_id!r}"}
    parser = PDBParser(QUIET=True)

    if query_pdb_identifiers:
        try:
            result = query_pdb_identifiers(
                identifiers=[pdb_id], download=True, return_type='entry'
            )
            candidate = None
            if isinstance(result, str) and os.path.exists(result):
                candidate = result
            elif isinstance(result, dict):
                if result.get("file_path") and os.path.exists(result["file_path"]):
                    candidate = result["file_path"]
                else:
                    for item in result.get("detailed_results", []):
                        p = item.get("pdb_file_path")
                        if p and os.path.exists(p):
                            candidate = p
                            break
            if candidate:
                structure = parser.get_structure(pdb_id, candidate)
                return _structure_payload(pdb_id, structure, "query_pdb_identifiers")
        except Exception:
            pass

    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        response = requests.get(url, timeout=_TIMEOUT_S)
    except requests.RequestException as exc:
        return {"success": False, "error": f"RCSB download failed: {exc!r}"}
    if response.status_code != 200:
        return {
            "success": False,
            "error": f"RCSB download failed for {pdb_id} with status {response.status_code}",
        }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pdb") as fh:
        fh.write(response.text)
        temp_path = fh.name
    try:
        structure = parser.get_structure(pdb_id, temp_path)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    return _structure_payload(pdb_id, structure, "RCSB")


def _structure_payload(pdb_id: str, structure, source: str) -> dict[str, Any]:
    model = structure[0]
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_id,
            "atom_count": len(list(model.get_atoms())),
            "residue_count": len(list(model.get_residues())),
            "chains": [chain.id for chain in model],
            "source": source,
        },
    }


def _structure_of(pdb_id: str, query_pdb_identifiers: Optional[Callable]):
    """Return the parsed structure, or None, using the same order as
    ``load_pdb`` (injectable downloader first, RCSB second)."""
    parser = PDBParser(QUIET=True)
    if query_pdb_identifiers:
        try:
            result = query_pdb_identifiers(
                identifiers=[pdb_id], download=True, return_type='entry'
            )
            candidate = None
            if isinstance(result, str) and os.path.exists(result):
                candidate = result
            elif isinstance(result, dict):
                if result.get("file_path") and os.path.exists(result["file_path"]):
                    candidate = result["file_path"]
                else:
                    for item in result.get("detailed_results", []):
                        p = item.get("pdb_file_path")
                        if p and os.path.exists(p):
                            candidate = p
                            break
            if candidate:
                return parser.get_structure(pdb_id, candidate)
        except Exception:
            pass
    try:
        response = requests.get(
            f"https://files.rcsb.org/download/{pdb_id}.pdb", timeout=_TIMEOUT_S
        )
        if response.status_code != 200:
            return None
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pdb") as fh:
            fh.write(response.text)
            temp_path = fh.name
        try:
            return parser.get_structure(pdb_id, temp_path)
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    except requests.RequestException:
        return None


def _heavy_atom_coords(model, residues):
    coords: list = []
    atom_map: dict[tuple, list] = {}
    missing = 0
    for chain_id, res_num in residues:
        try:
            residue = model[chain_id][(" ", res_num, " ")]
            heavy = [
                atom.get_coord() for atom in residue.get_atoms()
                if atom.get_name()[0] != "H"
            ]
            if heavy:
                atom_map[(chain_id, res_num)] = heavy
                coords.extend(heavy)
        except (KeyError, TypeError):
            missing += 1
    return coords, atom_map, missing


@with_return_contract(source_version="1.0")
def structural_distance(pdb_id: str,
                        candidate_residues: list,
                        active_residues: list,
                        query_pdb_identifiers: Optional[Callable] = None):
    """Score how far candidate residues sit from the active-site residues.

    Does not say whether the candidate residues are allosteric; it only
    measures the heavy-atom distance and scores it against the
    10-30 A band that the tool considers optimal for allosteric
    communication.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id.
    candidate_residues : list
        List of ``(chain_id, residue_number)`` pairs.
    active_residues : list
        List of ``(chain_id, residue_number)`` pairs.
    query_pdb_identifiers : callable or None
        Optional downloader, see ``load_pdb``.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, score, avg_distance, all_distances, summary}``.
    """
    structure = _structure_of(pdb_id, query_pdb_identifiers)
    if structure is None:
        return {"success": False, "error": f"Failed to load structure for {pdb_id}"}
    model = structure[0]

    candidate_coords, candidate_map, _ = _heavy_atom_coords(model, candidate_residues)
    active_coords, active_map, _ = _heavy_atom_coords(model, active_residues)
    if not candidate_coords or not active_coords:
        return {
            "success": False,
            "error": (
                f"Could not extract heavy atom coordinates for {pdb_id} "
                f"(candidates={len(candidate_coords)}, active={len(active_coords)})"
            ),
        }

    min_distances = []
    for _key, c_coords in candidate_map.items():
        min_for_res = float("inf")
        for a_coords in active_map.values():
            matrix = distance.cdist(np.array(c_coords), np.array(a_coords))
            min_for_res = min(min_for_res, float(np.min(matrix)))
        min_distances.append(min_for_res)
    if not min_distances:
        return {"success": False, "error": f"Failed to compute distances for {pdb_id}"}

    avg_distance = float(np.mean(min_distances))
    if avg_distance < 8:
        score = 0.3
    elif 8 <= avg_distance < 10:
        score = 0.3 + 0.4 * (avg_distance - 8) / 2
    elif 10 <= avg_distance <= 30:
        score = 1.0
    elif 30 < avg_distance <= 40:
        score = 1.0 - 0.5 * (avg_distance - 30) / 10
    else:
        score = 0.2
    if avg_distance < 8:
        quality = "too close to active site (potential overlap)"
    elif 10 <= avg_distance <= 30:
        quality = "optimally positioned for allosteric communication"
    elif avg_distance > 40:
        quality = "too distant"
    else:
        quality = "moderately positioned"
    summary = (
        f"Candidates are {quality}. Avg **Heavy Atom Distance**: "
        f"{avg_distance:.1f} A (range: {min(min_distances):.1f}-"
        f"{max(min_distances):.1f} A). Optimal: 10-30 A. Score: {score:.2f}/1.0"
    )
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_id,
            "score": round(score, 3),
            "avg_distance": round(avg_distance, 2),
            "all_distances": [round(d, 2) for d in min_distances],
            "summary": summary,
        },
    }


@with_return_contract(source_version="1.0")
def pocket_geometry(pdb_id: str,
                    candidate_residues: list,
                    query_pdb_identifiers: Optional[Callable] = None):
    """Score the volume, extent and shape of the region the candidate residues span.

    Does not say whether the region is a binding pocket; it only
    measures the geometry of the candidate residues and scores it
    against the tool's preferred ranges.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id.
    candidate_residues : list
        List of ``(chain_id, residue_number)`` pairs.
    query_pdb_identifiers : callable or None
        Optional downloader, see ``load_pdb``.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, score, volume, max_extent, asphericity, shape_score_pmi,
        summary}``.
    """
    structure = _structure_of(pdb_id, query_pdb_identifiers)
    if structure is None:
        return {"success": False, "error": f"Failed to load structure for {pdb_id}"}
    model = structure[0]

    atoms = []
    for chain_id, res_num in candidate_residues:
        try:
            residue = model[chain_id][(" ", res_num, " ")]
            atoms.extend([
                atom for atom in residue.get_atoms()
                if atom.get_name()[0] != "H"
            ])
        except (KeyError, TypeError):
            continue
    if len(atoms) < 3:
        return {
            "success": False,
            "error": f"Insufficient heavy atoms ({len(atoms)}) for {pdb_id}",
        }

    coords = np.array([atom.get_coord() for atom in atoms])
    try:
        volume = float(ConvexHull(coords).volume)
    except Exception:
        volume = 0.0
    depth = float(np.max(distance.cdist(coords, coords)))

    centred = coords - np.mean(coords, axis=0)
    eigenvalues = LA.eigvalsh(np.cov(centred, rowvar=False))
    eigenvalues = np.sort(eigenvalues)[::-1]
    lam1, lam2, lam3 = eigenvalues
    asphericity = (
        ((lam1 - lam2) ** 2 + (lam2 - lam3) ** 2 + (lam3 - lam1) ** 2)
        / (2 * (lam1 + lam2 + lam3) ** 2 + 1e-9)
    )
    shape_score_pmi = max(0.0, min(1.0, (1.0 - (1.0 - (lam3 / lam1))) * 1.5))

    vol_score = 1.0 if 200 <= volume <= 2000 else 0.4
    if 100 <= volume < 200:
        vol_score = 0.3 + 0.7 * (volume - 100) / 100
    if volume < 100:
        vol_score = 0.3
    if volume > 2000:
        vol_score = 0.4
    depth_score = 1.0 if 8 <= depth <= 20 else 0.4
    if 5 <= depth < 8:
        depth_score = 0.3 + 0.7 * (depth - 5) / 3
    if depth < 5:
        depth_score = 0.3
    if 0.1 <= asphericity <= 0.5:
        pmi_qual = "optimal for binding"
        pmi_score = 1.0
    elif asphericity < 0.1:
        pmi_qual = "too spherical"
        pmi_score = 0.7
    else:
        pmi_qual = "too elongated/flat"
        pmi_score = 0.6
    final_score = (vol_score + depth_score + pmi_score) / 3

    vol_qual = ("small" if volume < 200
                else "moderate" if volume <= 2000 else "large")
    depth_qual = ("shallow" if depth < 8
                  else "optimal" if depth <= 20 else "deep")
    summary = (
        f"Pocket: {vol_qual} volume ({volume:.0f} A^3), {depth_qual} max "
        f"extent ({depth:.1f} A). Shape is {pmi_qual} (Asphericity: "
        f"{asphericity:.2f}). Optimal: 200-2000 A^3, 8-20 A extent, "
        f"0.1-0.5 Asphericity. Score: {final_score:.2f}/1.0"
    )
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_id,
            "score": round(final_score, 3),
            "volume": round(volume, 1),
            "max_extent": round(depth, 2),
            "asphericity": round(asphericity, 3),
            "shape_score_pmi": round(pmi_score, 3),
            "summary": summary,
        },
    }


@with_return_contract(source_version="1.0")
def residue_accessibility(pdb_id: str,
                          candidate_residues: list,
                          query_pdb_identifiers: Optional[Callable] = None):
    """Score the relative solvent accessibility and hydropathy of candidate residues.

    Does not say whether the residues are allosteric; it only measures
    how exposed they are and how hydrophobic they are.

    Parameters
    ----------
    pdb_id : str
        4-character PDB id.
    candidate_residues : list
        List of ``(chain_id, residue_number)`` pairs.
    query_pdb_identifiers : callable or None
        Optional downloader, see ``load_pdb``.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{pdb_id, score, avg_rsasa, avg_hydrophobicity, summary}``.
    """
    structure = _structure_of(pdb_id, query_pdb_identifiers)
    if structure is None:
        return {"success": False, "error": f"Failed to load structure for {pdb_id}"}
    model = structure[0]

    sr = ShrakeRupley()
    sr.compute(model, level="R")

    rsasa_values: list[float] = []
    hydro_values: list[float] = []
    for chain_id, res_num in candidate_residues:
        try:
            residue = model[chain_id][(" ", res_num, " ")]
            resname = residue.get_resname()
            raw_sasa = residue.sasa
            max_sasa = MAX_SASA.get(resname, 200.0)
            rsasa = raw_sasa / max_sasa if max_sasa > 0 else 0.0
            rsasa = min(1.0, rsasa) * 100
            rsasa_values.append(rsasa)
            hydro_values.append(HYDROPHOBICITY.get(resname, 0.0))
        except (KeyError, TypeError, AttributeError):
            continue
    if not rsasa_values:
        return {
            "success": False,
            "error": f"Could not analyze any residue of {pdb_id}",
        }

    avg_rsasa = float(np.mean(rsasa_values))
    avg_hydro = float(np.mean(hydro_values))
    if 30 <= avg_rsasa <= 70:
        sasa_score = 1.0
    elif avg_rsasa < 30:
        sasa_score = 0.4 + 0.6 * (avg_rsasa / 30)
    else:
        sasa_score = 1.0 - 0.7 * (avg_rsasa - 70) / 30
    hydro_score = 1.0 if abs(avg_hydro) <= 1.5 else 0.6
    score = (sasa_score + hydro_score) / 2

    access_qual = ("buried" if avg_rsasa < 30
                   else "moderate" if avg_rsasa <= 70 else "exposed")
    hydro_qual = ("hydrophobic" if avg_hydro > 1.5
                  else "hydrophilic" if avg_hydro < -1.5 else "mixed")
    summary = (
        f"Residues: {access_qual} (**rSASA**: {avg_rsasa:.1f}%), "
        f"{hydro_qual} (hydrophobicity: {avg_hydro:.1f}). "
        f"Score: {score:.2f}/1.0"
    )
    return {
        "success": True,
        "data": {
            "pdb_id": pdb_id,
            "score": round(score, 3),
            "avg_rsasa": round(avg_rsasa, 2),
            "avg_hydrophobicity": round(avg_hydro, 2),
            "summary": summary,
        },
    }


@with_return_contract(source_version="1.0")
def evolutionary_conservation(uniprot_id: str,
                              candidate_residues: list,
                              query_pdb: Optional[Callable] = None):
    """Score candidate residues with a deterministic pseudo-MSA conservation surrogate.

    **This does not measure sequence conservation.** It builds no
    alignment and consults no ortholog database; it evaluates a
    deterministic entropy model over a simulated amino-acid frequency
    profile, which is what the original tool did. Treat the score as a
    reproducible stand-in, never as evidence of conservation.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession, used to fetch the sequence and to seed the
        surrogate.
    candidate_residues : list
        List of ``(chain_id, residue_number)`` pairs. The residue
        **number** drives the surrogate.
    query_pdb : callable or None
        Unused by the surrogate; accepted so the signature matches the
        other verification tools.

    Returns
    -------
    dict
        Contract dict. ``data`` is
        ``{uniprot_id, score, avg_conservation, summary}``.
    """
    try:
        response = requests.get(
            f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta",
            timeout=_TIMEOUT_S,
        )
    except requests.RequestException as exc:
        return {"success": False, "error": f"UniProt FASTA request failed: {exc!r}"}
    if response.status_code != 200:
        return {
            "success": False,
            "error": (
                f"UniProt FASTA request for {uniprot_id} failed with status "
                f"{response.status_code}"
            ),
        }
    try:
        record = SeqIO.read(io.StringIO(response.text), "fasta")
    except Exception as exc:
        return {"success": False, "error": f"UniProt FASTA parsing error: {exc!r}"}

    entropy_scores: list[float] = []
    for _chain_id, res_num in candidate_residues:
        np.random.seed(_stable_seed(f"{uniprot_id}_{res_num}"))
        if res_num % 10 == 0:
            params = (10, 1)
        elif 30 < res_num < 60:
            params = (1, 1)
        else:
            params = (5, 5)
        freqs = np.random.dirichlet(np.ones(20) * params[0] / params[1])
        entropy = -np.sum(freqs * np.log2(freqs + 1e-9))
        entropy_scores.append(1.0 - (entropy / MAX_SHANNON_ENTROPY))

    if not entropy_scores:
        return {"success": False, "error": "No residues analyzed"}

    avg_conservation = float(np.mean(entropy_scores))
    if 0.4 <= avg_conservation <= 0.7:
        score = 1.0
        cons_qual = "moderately conserved (Optimal for allostery)"
    elif 0.7 < avg_conservation <= 0.9:
        score = 1.0 - 0.5 * (avg_conservation - 0.7) / 0.2
        cons_qual = "highly conserved (potential active site)"
    elif avg_conservation > 0.9:
        score = 0.4
        cons_qual = "extremely conserved (likely structural/active site)"
    else:
        score = avg_conservation / 0.4 * 0.7
        cons_qual = "lowly conserved (likely surface loop/variable)"
    summary = (
        f"Residues show {cons_qual} conservation (Avg Conservation Score: "
        f"{avg_conservation:.2f}, derived from a deterministic pseudo-MSA "
        f"entropy surrogate, not from a real alignment). Optimal range: "
        f"0.4 - 0.7. Score: {score:.2f}/1.0"
    )
    return {
        "success": True,
        "data": {
            "uniprot_id": uniprot_id,
            "score": round(score, 3),
            "avg_conservation": round(avg_conservation, 3),
            "summary": summary,
        },
    }


@with_return_contract(source_version="1.0")
def allosteric_evidence(uniprot_id: Optional[str] = None,
                        pdb_id: Optional[str] = None):
    """Report whether the Allosteric Database confirms a protein has curated allosteric sites.

    Does not predict allostery for a protein that ASD does not cover:
    ``NOT_CONFIRMED`` means the database has no record, not that the
    protein has no allostery.

    Parameters
    ----------
    uniprot_id : str or None
        UniProt accession.
    pdb_id : str or None
        PDB id, used when no UniProt accession is given.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "status": "CONFIRMED" | "UNCERTAIN" | "NOT_CONFIRMED",
                "message": <str>,
                "protein_id": <str>,
                "protein_name": <str>,
                "gene_name": <str>,
                "known_sites": [{"pdb_id", "site_id", "residues",
                                 "function", "feature"}, ...],
                "modulator_count": <int>,
                "modulators": [str, ...],
            }
    """
    protein_query = pdb_id.upper() if pdb_id else uniprot_id
    if not protein_query:
        return {
            "success": False,
            "error": "Must provide either uniprot_id or pdb_id",
        }

    from biomni.tool.asd import parse_asd_xf

    probe = parse_asd_xf([protein_query])
    if not probe.get("success"):
        return {
            "success": False,
            "error": probe.get("error") or "ASD query failed",
        }
    proteins = probe["data"]["proteins"]
    if protein_query not in proteins:
        return {
            "success": True,
            "data": {
                "status": "NOT_CONFIRMED",
                "message": f"Protein {protein_query} not found in ASD database",
                "protein_id": protein_query,
                "protein_name": None,
                "gene_name": None,
                "known_sites": [],
                "modulator_count": 0,
                "modulators": [],
            },
        }

    entry = proteins[protein_query]
    metadata = entry.get("protein_metadata", {})
    sites = entry.get("sites", [])
    modulators = entry.get("modulators", [])

    if sites:
        known_sites = [
            {
                "pdb_id": site.get("pdb_id", "N/A"),
                "site_id": site.get("pdb_site", "Unknown"),
                "residues": site.get("site_residues", ""),
                "function": site.get("function", "N/A"),
                "feature": site.get("feature", "N/A"),
            }
            for site in sites
        ]
        return {
            "success": True,
            "data": {
                "status": "CONFIRMED",
                "message": (
                    f"Protein {protein_query} is experimentally confirmed as "
                    f"allosteric"
                ),
                "protein_id": protein_query,
                "protein_name": metadata.get("protein_name", "Unknown"),
                "gene_name": metadata.get("gene_name", "Unknown"),
                "known_sites": known_sites,
                "modulator_count": len(modulators),
                "modulators": [m.get("modulator_id", "Unknown") for m in modulators],
            },
        }

    return {
        "success": True,
        "data": {
            "status": "UNCERTAIN",
            "message": (
                f"Protein {protein_query} is in ASD but has no experimentally "
                f"documented allosteric sites yet"
            ),
            "protein_id": protein_query,
            "protein_name": metadata.get("protein_name", "Unknown"),
            "gene_name": metadata.get("gene_name", "Unknown"),
            "reason": (
                "Data gap - protein indexed in ASD but no allosteric sites curated"
            ),
            "known_sites": [],
            "modulator_count": len(modulators),
            "pdb_entries": metadata.get("pdb_entries", []),
        },
    }

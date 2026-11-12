"""P32 get_ligand_contacts: which residues touch a named ligand in a PDB entry.

Reports geometric proximity only. The tool computes the minimum
heavy-atom distance between the named ligand and every polymer residue
of the entry and returns the residues whose closest heavy atom lies
within a cutoff (4.0 A by default). It does NOT compute a binding
energy, an affinity, a docking score or an interaction type, and a
contact is not evidence that the interaction is biological.

The coordinates come from the RCSB mmCIF file of the entry; the UniProt
residue numbers come from the SIFTS alignment published by the RCSB
Data API.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Optional

import numpy as np
import requests
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_CIF_URL = "https://files.rcsb.org/download/{pdb_id}.cif"
_ENTITY_URL = "https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/{entity_id}"
_WATER_IDS = frozenset({"HOH", "DOD", "WAT"})
_MISSING = (".", "?", "")
_HYDROGENS = frozenset({"H", "D"})


def _load_cif_text(pdb_id: Optional[str], structure_file: Optional[str]) -> str:
    """Return the mmCIF text of the entry, from RCSB or from a local file."""
    if structure_file:
        path = Path(structure_file)
        if not path.is_file():
            raise FileNotFoundError(f"structure file not found: {path}")
        return path.read_text(encoding="utf-8")
    response = requests.get(_CIF_URL.format(pdb_id=pdb_id), timeout=_TIMEOUT_S)
    if response.status_code != 200:
        raise RuntimeError(
            f"RCSB download failed for {pdb_id} with status {response.status_code}"
        )
    return response.text


def _parse_structure(cif_text: str) -> dict[str, Any]:
    """Parse the mmCIF text into the entry id and the atom rows.

    ``MMCIF2Dict`` reads a file path, so the text is written to a
    temporary file first.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cif", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(cif_text)
        temp_path = handle.name
    try:
        cif = MMCIF2Dict(temp_path)
    finally:
        os.unlink(temp_path)

    entry_values = cif.get("_entry.id") or []
    columns = [key for key in cif.keys() if key.startswith("_atom_site.")]
    if "_atom_site.id" not in columns:
        raise ValueError("the mmCIF file has no _atom_site loop")
    count = len(cif["_atom_site.id"])
    atoms = [{column: cif[column][i] for column in columns} for i in range(count)]
    return {"entry_id": entry_values[0] if entry_values else None, "atoms": atoms}


def _component_ids(atoms: list[dict[str, str]]) -> list[str]:
    """The non-water chemical component ids of the entry, sorted."""
    ids = {
        atom["_atom_site.label_comp_id"]
        for atom in atoms
        if atom["_atom_site.label_seq_id"] in _MISSING
        and atom["_atom_site.label_comp_id"] not in _WATER_IDS
    }
    return sorted(ids)


def _sifts_regions(pdb_id: str, entity_ids: set[str]) -> dict[str, list[tuple]]:
    """UniProt alignment regions per polymer entity.

    Returns ``{entity_id: [(accession, first_label_seq_id, last_label_seq_id,
    offset), ...]}`` where ``offset`` is added to a residue's
    ``label_seq_id`` to obtain its UniProt residue number.
    """
    regions: dict[str, list[tuple]] = {}
    for entity_id in sorted(entity_ids):
        url = _ENTITY_URL.format(pdb_id=pdb_id, entity_id=entity_id)
        response = requests.get(url, timeout=_TIMEOUT_S)
        if response.status_code != 200:
            raise RuntimeError(
                f"RCSB Data API returned status {response.status_code} for {url}"
            )
        payload = response.json()
        for alignment in payload.get("rcsb_polymer_entity_align", []):
            if alignment.get("reference_database_name") != "UniProt":
                continue
            accession = alignment["reference_database_accession"]
            for region in alignment.get("aligned_regions", []):
                first = int(region["entity_beg_seq_id"])
                length = int(region["length"])
                offset = int(region["ref_beg_seq_id"]) - first
                regions.setdefault(entity_id, []).append(
                    (accession, first, first + length - 1, offset)
                )
    return regions


def _uniprot_for(
    regions: dict[str, list[tuple]], entity_id: str, label_seq_id: int
) -> tuple[Optional[str], Optional[int]]:
    """The UniProt accession and residue number of one polymer residue."""
    for accession, first, last, offset in regions.get(entity_id, []):
        if first <= label_seq_id <= last:
            return accession, label_seq_id + offset
    return None, None


def _residue_sort_key(key: tuple[str, str, str]) -> tuple[str, int, str]:
    """Sort key for a residue: chain, then the PDB number as a NUMBER.

    Sorting the PDB number as a string would put residue 210 before
    residue 61.
    """
    chain_id, number, insertion_code = key
    try:
        numeric = int(number)
    except ValueError:
        numeric = 0
    return chain_id, numeric, insertion_code


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_ligand_contacts(
    pdb_id: Optional[str] = None,
    structure_file: Optional[str] = None,
    ligand_id: str = "",
    chain: Optional[str] = None,
    cutoff: float = 4.0,
):
    """Return the polymer residues within a cutoff of a named ligand.

    This tool reports geometric proximity: the minimum heavy-atom
    distance between the ligand and each polymer residue of the entry.
    It does NOT report a binding energy, an affinity, a docking score
    or an interaction type, and a contact is not evidence that the
    interaction is biological.

    Parameters
    ----------
    pdb_id : str or None
        4-character PDB entry id (e.g. ``"1T4J"``). Ignored when
        ``structure_file`` is given.
    structure_file : str or None
        Path to a local mmCIF file. When given, the coordinates are read
        from disk and the entry id is taken from the file's ``_entry.id``
        so the UniProt mapping is the same as for ``pdb_id``.
    ligand_id : str
        RCSB chemical component id of the ligand (e.g. ``"FRJ"``,
        ``"MYR"``). Case-insensitive.
    chain : str or None
        Chain id to restrict the query to (e.g. ``"A"``). When None,
        every chain of the entry is searched.
    cutoff : float
        Maximum distance in Angstrom. A residue whose closest heavy
        atom is at or below the cutoff is a contact. Default 4.0.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "pdb_id": <str>,
                "ligand": {"id": <str>, "chain": <str>,
                           "pdb_number": <int>, "atom_count": <int>,
                           "instances": [{"chain": <str>,
                                          "pdb_number": <int>}, ...]},
                "cutoff": <float>,
                "contacts": [{"chain": <str>, "pdb_number": <int>,
                              "insertion_code": <str or None>,
                              "residue_name": <str>,
                              "min_distance": <float>,
                              "uniprot_accession": <str or None>,
                              "uniprot_number": <int or None>}, ...],
                "contact_count": <int>,
                "ligand_ids_present": [<str>, ...],
            }

        On failure, ``success`` is False and ``error`` describes the
        cause; for an unknown ligand id ``data`` still carries
        ``ligand_ids_present`` (the ids that are in the entry).
    """
    if not isinstance(ligand_id, str) or not ligand_id.strip():
        return {
            "success": False,
            "data": None,
            "error": f"ligand_id must be a non-empty string, got {ligand_id!r}",
        }
    if not pdb_id and not structure_file:
        return {
            "success": False,
            "data": None,
            "error": "either pdb_id or structure_file must be given",
        }
    try:
        cutoff = float(cutoff)
    except (TypeError, ValueError):
        return {
            "success": False,
            "data": None,
            "error": f"cutoff must be a number, got {cutoff!r}",
        }
    if cutoff <= 0:
        return {
            "success": False,
            "data": None,
            "error": f"cutoff must be positive, got {cutoff!r}",
        }
    if chain is not None and not isinstance(chain, str):
        return {
            "success": False,
            "data": None,
            "error": f"chain must be a string or None, got {chain!r}",
        }

    ligand_key = ligand_id.strip().upper()

    try:
        cif_text = _load_cif_text(pdb_id, structure_file)
        parsed = _parse_structure(cif_text)
    except requests.exceptions.RequestException as exc:
        return {"success": False, "data": None, "error": f"RCSB download failed: {exc!r}"}
    except (OSError, ValueError) as exc:
        return {"success": False, "data": None, "error": f"could not read the structure: {exc}"}

    atoms = parsed["atoms"]
    entry_id = parsed["entry_id"] or pdb_id
    component_ids = _component_ids(atoms)

    ligand_rows = [
        atom
        for atom in atoms
        if atom["_atom_site.label_comp_id"].upper() == ligand_key
        and atom["_atom_site.label_seq_id"] in _MISSING
        and (chain is None or atom["_atom_site.auth_asym_id"] == chain)
    ]
    if not ligand_rows:
        where = f" in chain {chain}" if chain else ""
        return {
            "success": False,
            "data": {
                "pdb_id": entry_id,
                "ligand_id": ligand_key,
                "cutoff": cutoff,
                "contacts": [],
                "contact_count": 0,
                "ligand_ids_present": component_ids,
            },
            "error": (
                f"ligand {ligand_key} not found{where} in {entry_id}; "
                f"ligand ids present: {', '.join(component_ids) or 'none'}"
            ),
        }

    ligand_atoms = [
        atom for atom in ligand_rows if atom["_atom_site.type_symbol"] not in _HYDROGENS
    ]
    ligand_coords = np.array(
        [
            [
                float(atom["_atom_site.Cartn_x"]),
                float(atom["_atom_site.Cartn_y"]),
                float(atom["_atom_site.Cartn_z"]),
            ]
            for atom in ligand_atoms
        ],
        dtype=float,
    )
    instances = sorted(
        {
            (atom["_atom_site.auth_asym_id"], atom["_atom_site.auth_seq_id"])
            for atom in ligand_rows
        },
        key=lambda item: (item[0], int(item[1]) if item[1].lstrip("-").isdigit() else 0),
    )

    residues: dict[tuple[str, str, str], dict[str, Any]] = {}
    for atom in atoms:
        if atom["_atom_site.label_seq_id"] in _MISSING:
            continue
        if atom["_atom_site.type_symbol"] in _HYDROGENS:
            continue
        if chain is not None and atom["_atom_site.auth_asym_id"] != chain:
            continue
        key = (
            atom["_atom_site.auth_asym_id"],
            atom["_atom_site.auth_seq_id"],
            atom["_atom_site.pdbx_PDB_ins_code"],
        )
        residue = residues.get(key)
        if residue is None:
            residue = {
                "residue_name": atom["_atom_site.label_comp_id"],
                "label_seq_id": int(atom["_atom_site.label_seq_id"]),
                "entity_id": atom["_atom_site.label_entity_id"],
                "coords": [],
            }
            residues[key] = residue
        residue["coords"].append(
            [
                float(atom["_atom_site.Cartn_x"]),
                float(atom["_atom_site.Cartn_y"]),
                float(atom["_atom_site.Cartn_z"]),
            ]
        )

    keys = sorted(residues, key=_residue_sort_key)
    starts: list[int] = []
    flat_coords: list[list[float]] = []
    for key in keys:
        starts.append(len(flat_coords))
        flat_coords.extend(residues[key]["coords"])

    contacts: list[dict[str, Any]] = []
    contact_keys: list[tuple[str, str, str]] = []
    if flat_coords and len(ligand_coords):
        coords = np.array(flat_coords, dtype=float)
        deltas = coords[:, None, :] - ligand_coords[None, :, :]
        distances = np.sqrt((deltas ** 2).sum(axis=2)).min(axis=1)
        per_residue = np.minimum.reduceat(distances, np.array(starts))
        for index, key in enumerate(keys):
            distance = float(per_residue[index])
            if distance > cutoff:
                continue
            residue = residues[key]
            contacts.append(
                {
                    "chain": key[0],
                    "pdb_number": int(key[1]),
                    "insertion_code": None if key[2] in _MISSING else key[2],
                    "residue_name": residue["residue_name"],
                    "min_distance": round(distance, 2),
                    "uniprot_accession": None,
                    "uniprot_number": None,
                }
            )
            contact_keys.append(key)

    uniprot_error: Optional[str] = None
    entity_ids = {residues[key]["entity_id"] for key in keys}
    if contacts and entity_ids and entry_id:
        try:
            regions = _sifts_regions(entry_id, entity_ids)
        except (requests.exceptions.RequestException, ValueError, RuntimeError) as exc:
            regions = {}
            uniprot_error = f"SIFTS alignment unavailable: {exc}"
        for contact, key in zip(contacts, contact_keys):
            residue = residues[key]
            accession, number = _uniprot_for(
                regions, residue["entity_id"], residue["label_seq_id"]
            )
            contact["uniprot_accession"] = accession
            contact["uniprot_number"] = number

    data = {
        "pdb_id": entry_id,
        "ligand": {
            "id": ligand_key,
            "chain": instances[0][0] if instances else None,
            "pdb_number": int(instances[0][1]) if instances else None,
            "atom_count": len(ligand_atoms),
            "instances": [
                {"chain": chain_id, "pdb_number": int(number)}
                for chain_id, number in instances
            ],
        },
        "cutoff": cutoff,
        "contacts": contacts,
        "contact_count": len(contacts),
        "ligand_ids_present": component_ids,
        "source_structure": str(structure_file) if structure_file else "RCSB",
    }
    if uniprot_error:
        data["uniprot_error"] = uniprot_error
    return {"success": True, "data": data, "error": None}

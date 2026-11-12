"""ASD (Allosteric Database) lookups (ported from the old repo's
``alloagent/tool/asd.py``).

Questions this module answers: which allosteric sites does ASD record
for a protein, which modulators act on them, and what 2D/3D structures
does ASD ship for those modulators.

The old functions returned bare dicts, printed to stdout and raised on
error. The ported versions return the standard contract dict and never
print.

The protein -> XML mapping is read from ``biomni/tool/_asd_index.tsv``
(2,412 proteins), generated from the real
``ASD_Release_202306_XF`` directory by ``scripts/_gen_asd_index.py``.
The old repo shipped the same map as a 75 KB Python dict; the TSV is
the same data and loads in milliseconds instead of a 9.5 s scan. If the
TSV is missing, the index is rebuilt by scanning the directory.

The ASD snapshot is mounted read-only at ``/biolab_data`` (override with
``ASD_ROOT``).
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from biomni.tool._netcall import with_return_contract

_DEFAULT_ASD_ROOT = Path("/biolab_data/asd")
_DEFAULT_LAKE = Path("/biolab_data/data_lake")
_INDEX_TSV = Path(__file__).resolve().parent / "_asd_index.tsv"

_XF_DIR = "ASD_Release_202306_XF"
_2D_DIR = "ASD_Release_202306_2D"
_3D_DIR = "ASD_Release_202306_3D"
_AP_CSV = "ASD_Release_202306_AP.csv"
_DR_CSV = "ASD_Release_201909_DR.csv"

_INDEX_CACHE: Optional[dict[str, str]] = None
_CSV_CACHE: dict[str, pd.DataFrame] = {}


def _asd_root() -> Path:
    return Path(os.environ.get("ASD_ROOT") or _DEFAULT_ASD_ROOT)


def _lake_root() -> Path:
    return Path(os.environ.get("ASD_LAKE_ROOT") or _DEFAULT_LAKE)


def _load_index() -> dict[str, str]:
    """UniProt accession -> ASD XF file stem, from the committed TSV."""
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
    if not index:
        index = _scan_index()
    _INDEX_CACHE = index
    return index


def _scan_index() -> dict[str, str]:
    """Rebuild the index by scanning the XF directory (fallback path)."""
    import re

    xf = _asd_root() / _XF_DIR
    pat = re.compile(rb"<UniProt_ID>([^<]+)</UniProt_ID>")
    index: dict[str, str] = {}
    if not xf.is_dir():
        return index
    for path in sorted(xf.glob("*.xml")):
        try:
            with open(path, "rb") as fh:
                head = fh.read(4096)
        except OSError:
            continue
        m = pat.search(head)
        if m:
            index.setdefault(m.group(1).decode("utf-8").strip(), path.stem)
    return index


def _xml_path(protein_id: str) -> Optional[Path]:
    stem = _load_index().get(protein_id)
    if not stem:
        return None
    path = _asd_root() / _XF_DIR / f"{stem}.xml"
    return path if path.is_file() else None


def _parse_xml_content(root: ET.Element, result: dict,
                       target_proteins: Optional[set] = None) -> None:
    """Parse one ASD XF XML file into the protein -> site -> modulator map."""
    protein_id = root.findtext("UniProt_ID")
    if not protein_id:
        return
    if target_proteins is not None and protein_id not in target_proteins:
        return

    aliases = root.findall(".//Alias_List/Alias")
    protein_name = aliases[0].text if aliases else "Unknown"
    gene_elem = root.find(".//Gene")
    gene_name = gene_elem.findtext("Gene_Name") if gene_elem is not None else "Unknown"
    pdb_ids = [p.findtext("PDB_ID") for p in root.findall(".//PDB_List/PDB")]

    sites = []
    for site in root.findall(".//Allosteric_Site"):
        sites.append({
            "pdb_id": site.findtext("Allosteric_PDB"),
            "site_residues": site.findtext("Allosteric_Site_Residue"),
            "feature": site.findtext("Modulator_Feature"),
            "function": site.findtext("Function"),
            "pdb_site": site.findtext("PDB_Site"),
            "modulator_asd_id": site.findtext("Modulator_ASD_ID"),
        })

    modulators = []
    for mod in root.findall(".//Modulator"):
        modulators.append({
            "modulator_id": mod.findtext("ASD_ID"),
            "feature": mod.findtext("Modulator_Feature"),
            "drugbank": mod.findtext("drugbank__id") or "No",
        })

    result[protein_id] = {
        "protein_metadata": {
            "protein_name": protein_name,
            "gene_name": gene_name,
            "pdb_entries": pdb_ids,
        },
        "sites": sites,
        "modulators": modulators,
    }


@with_return_contract(source_version="1.0")
def parse_asd_xf(target_proteins: Optional[list] = None):
    """Return the allosteric sites and modulators ASD records for a protein.

    Does not predict an allosteric site and does not score the sites; it
    reports the curated ASD record for the protein.

    Parameters
    ----------
    target_proteins : list or None
        UniProt accessions to extract. ``None`` extracts every protein in
        the ASD index (2,412 proteins) and is not intended for agent use.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "proteins": {<uniprot_id>: {
                    "protein_metadata": {"protein_name": ..., "gene_name": ...,
                                         "pdb_entries": [str, ...]},
                    "sites": [{"pdb_id", "site_residues", "feature",
                               "function", "pdb_site",
                               "modulator_asd_id"}, ...],
                    "modulators": [{"modulator_id", "feature", "drugbank"}, ...],
                }, ...},
                "total_proteins": <int>,
                "requested": [str, ...],
            }
    """
    if target_proteins is not None and not isinstance(target_proteins, list):
        return {
            "success": False,
            "error": f"target_proteins must be a list or None, got {type(target_proteins).__name__}",
        }
    xf_dir = _asd_root() / _XF_DIR
    if not xf_dir.is_dir():
        return {
            "success": False,
            "error": (
                f"ASD XF directory not found at {xf_dir}; mount the Biolab "
                f"data lake read-only or set ASD_ROOT"
            ),
        }

    if target_proteins:
        wanted = {str(p).strip().upper() for p in target_proteins}
    else:
        wanted = set(_load_index().keys())

    result: dict[str, dict[str, Any]] = {}
    for protein_id in sorted(wanted):
        path = _xml_path(protein_id)
        if path is None:
            continue
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            continue
        _parse_xml_content(root, result, {protein_id})

    return {
        "success": True,
        "data": {
            "proteins": result,
            "total_proteins": len(result),
            "requested": sorted(wanted),
        },
    }


def _parse_mol_file(mol_content: str) -> Optional[dict[str, Any]]:
    """Parse a MOL file's header, counts line and atom block."""
    lines = mol_content.strip().split("\n")
    if len(lines) < 4:
        return None
    try:
        name = lines[0].strip()
        counts_line = lines[3].split()
        atom_count = int(counts_line[0]) if len(counts_line) >= 1 else 0
        bond_count = int(counts_line[1]) if len(counts_line) >= 2 else 0
        atoms = []
        for i in range(4, min(4 + atom_count, len(lines))):
            atom_line = lines[i].split()
            if len(atom_line) >= 4:
                atoms.append(atom_line[3])
        atom_counts = Counter(atoms)
        formula = "".join(
            f"{atom}{count if count > 1 else ''}"
            for atom, count in sorted(atom_counts.items())
        )
        return {
            "name": name,
            "formula": formula,
            "atom_count": atom_count,
            "bond_count": bond_count,
            "smiles": None,
        }
    except (ValueError, IndexError):
        return None


def _parse_mol2_file(mol2_content: str) -> Optional[dict[str, Any]]:
    """Parse a MOL2 file's ATOM and BOND sections."""
    atoms: list[dict[str, Any]] = []
    coordinates: list[list[float]] = []
    bonds: list[dict[str, Any]] = []
    current_section: Optional[str] = None

    for raw in mol2_content.strip().split("\n"):
        line = raw.strip()
        if line.startswith("@<TRIPOS>"):
            current_section = line[9:]
            continue
        if not line or line.startswith("#"):
            continue
        if current_section == "ATOM":
            parts = line.split()
            if len(parts) >= 6:
                try:
                    x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                except ValueError:
                    continue
                atoms.append({
                    "id": parts[0],
                    "name": parts[1],
                    "type": parts[5],
                })
                coordinates.append([x, y, z])
        elif current_section == "BOND":
            parts = line.split()
            if len(parts) >= 4:
                bonds.append({
                    "id": parts[0],
                    "atom1": parts[1],
                    "atom2": parts[2],
                    "type": parts[3],
                })

    if not atoms:
        return None
    return {
        "atoms": atoms,
        "coordinates": coordinates,
        "bonds": bonds,
        "atom_count": len(atoms),
        "bond_count": len(bonds),
    }


def _modulator_ids_for_proteins(protein_ids: list) -> list[str]:
    """The site-level modulator ASD ids for the given proteins."""
    out: list[str] = []
    for protein_id in protein_ids:
        path = _xml_path(protein_id)
        if path is None:
            continue
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            continue
        for site in root.findall(".//Allosteric_Site"):
            mod_id = site.findtext("Modulator_ASD_ID")
            if mod_id and mod_id.strip():
                out.append(mod_id.strip())
    return out


def _load_structures(protein_ids: list, modulator_ids: Optional[list],
                      kind: str) -> tuple[dict[str, Any], list[str]]:
    """Shared implementation for the 2D (.mol) and 3D (.mol2) loaders."""
    directory = _asd_root() / (_2D_DIR if kind == "2d" else _3D_DIR)
    suffix = ".mol" if kind == "2d" else ".mol2"
    parser = _parse_mol_file if kind == "2d" else _parse_mol2_file
    wanted = {str(m).strip() for m in modulator_ids} if modulator_ids else None

    result: dict[str, Any] = {}
    for mod_id in _modulator_ids_for_proteins(protein_ids):
        if wanted and mod_id not in wanted:
            continue
        path = directory / f"{mod_id}{suffix}"
        if not path.is_file():
            continue
        try:
            parsed = parser(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if parsed:
            result[mod_id] = parsed
    return result, sorted(result)


@with_return_contract(source_version="1.0")
def load_asd_2d(protein_ids: list,
                modulator_ids: Optional[list] = None):
    """Return the 2D chemical structure ASD ships for a protein's modulators.

    Does not answer whether a modulator is an allosteric or an
    orthosteric binder, and it does not give the binding affinity.

    Parameters
    ----------
    protein_ids : list
        UniProt accessions to look up.
    modulator_ids : list or None
        Optional ASD modulator ids to restrict the result to.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "modulators": {<asd_id>: {"name", "formula", "atom_count",
                                          "bond_count", "smiles"}, ...},
                "total_modulators": <int>,
            }
    """
    if not isinstance(protein_ids, list):
        return {"success": False,
                "error": f"protein_ids must be a list, got {type(protein_ids).__name__}"}
    result, keys = _load_structures(protein_ids, modulator_ids, "2d")
    return {
        "success": True,
        "data": {"modulators": result, "total_modulators": len(keys)},
    }


@with_return_contract(source_version="1.0")
def load_asd_3d(protein_ids: list,
                modulator_ids: Optional[list] = None):
    """Return the 3D chemical structure ASD ships for a protein's modulators.

    Does not answer whether a modulator is an allosteric or an
    orthosteric binder, and it does not give the binding pose in the
    protein.

    Parameters
    ----------
    protein_ids : list
        UniProt accessions to look up.
    modulator_ids : list or None
        Optional ASD modulator ids to restrict the result to.

    Returns
    -------
    dict
        Contract dict. ``data`` is::

            {
                "modulators": {<asd_id>: {"atoms": [...], "coordinates": [...],
                                          "bonds": [...], "atom_count",
                                          "bond_count"}, ...},
                "total_modulators": <int>,
            }
    """
    if not isinstance(protein_ids, list):
        return {"success": False,
                "error": f"protein_ids must be a list, got {type(protein_ids).__name__}"}
    result, keys = _load_structures(protein_ids, modulator_ids, "3d")
    return {
        "success": True,
        "data": {"modulators": result, "total_modulators": len(keys)},
    }


def _load_csv(name: str) -> Optional[pd.DataFrame]:
    if name in _CSV_CACHE:
        return _CSV_CACHE[name]
    path = _lake_root() / name
    if not path.is_file():
        return None
    df = pd.read_csv(path, low_memory=False)
    _CSV_CACHE[name] = df
    return df


def _asd_ap_rows(uniprot_id: Optional[str] = None,
                 pdb_id: Optional[str] = None) -> list[dict[str, Any]]:
    """Rows of the ASD AP (allosteric pocket) table.

    Private on purpose: the old ``cross_reference`` called
    ``asd.get_asd_ap_data``, a function the old ``asd.py`` never
    defined, so the ASD AP branch was always empty. This is the
    implementation the ported ``cross_reference`` uses.
    """
    df = _load_csv(_AP_CSV)
    if df is None:
        return []
    out = df
    if uniprot_id:
        out = out[out["uniprot_id"].astype(str).str.upper() == uniprot_id.upper()]
    if pdb_id:
        out = out[out["pdb_id"].astype(str).str.upper() == pdb_id.upper()]
    records = out.to_dict("records")
    for rec in records:
        for k, v in rec.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                rec[k] = str(v)
    return records


def _asd_dr_rows(target_id: Optional[str] = None,
                 drug_serial: Optional[str] = None) -> list[dict[str, Any]]:
    """Rows of the ASD DR (drug record) table.

    Private on purpose, for the same reason as ``_asd_ap_rows``. The DR
    table keys drugs by an ASD protein id whose space is disjoint from
    the XF index, so it can only be filtered by its own keys.
    """
    df = _load_csv(_DR_CSV)
    if df is None:
        return []
    out = df
    if target_id:
        out = out[out["target_id"].astype(str).str.upper() == target_id.upper()]
    if drug_serial:
        out = out[out["drug_serial"].astype(str).str.upper() == drug_serial.upper()]
    records = out.to_dict("records")
    for rec in records:
        for k, v in rec.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                rec[k] = str(v)
    return records

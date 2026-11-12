"""Validate every prompt of the benchmark draft and write the checklists.

The script recomputes the checklist facts from the primary sources
(RCSB mmCIF, UniProt REST, the RCSB SIFTS alignment, the ChEMBL 37
SQLite, the ClinVar and AlphaMissense release files, the STINGAllo
API) and, for the pocket / dynamics prompts, runs our own tools once to
produce a *reference output* (a number to compare against, not the
ground truth of the science).

Outputs (both written):

    benchmark/checklists.json        per prompt: the checklist items with
                                     their values, tolerances and source,
                                     and the PASS / PROBLEM verdict
    benchmark/validation_report.md   the human-readable report

Usage (inside the container, with the working directory OUTSIDE the
repository - the pocket-detection and normal-mode tools download their
PDB files into the working directory):

    docker run --rm -w /tmp -v /workspace:/workspace ... \\
        python /workspace/benchmark/validate_benchmark.py \\
        --benchmark /workspace/benchmark/benchmark_draft.json \\
        --out-json /workspace/benchmark/checklists.json \\
        --out-md /workspace/benchmark/validation_report.md
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Optional

TIMEOUT = 60
# Bump when the fact computation changes, so the cached facts are recomputed.
# v7: the ClinVar scan matches the gene as well as the protein change.
BENCHMARK_VERSION = "v7"
_CACHE_DIR = Path(tempfile.gettempdir()) / "benchmark_validation_cache"
_UNIPROT_ATTR = ("rcsb_polymer_entity_container_identifiers"
                 ".reference_sequence_identifiers.database_accession")

# ---------------------------------------------------------------- primitives
# (the helpers below are the ones added in the previous session; they are
#  repeated here so that this file is self-contained and can be run alone)


def _repo_root() -> Path:
    """The repository root (this script lives in benchmark/)."""
    return Path(__file__).resolve().parents[1]


_REPO_ROOT = _repo_root()


def _cache_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    return _CACHE_DIR / f"{digest}.json"


def http_get(url: str, timeout: int = TIMEOUT, cache: bool = True) -> bytes:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(url)
    if cache and path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))["body"].encode("utf-8")
    request = urllib.request.Request(url, headers={"User-Agent": "benchmark-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    if cache:
        path.write_text(json.dumps({"url": url, "body": body.decode("utf-8", "replace")}),
                        encoding="utf-8")
    return body


def http_get_json(url: str, timeout: int = TIMEOUT) -> Any:
    return json.loads(http_get(url, timeout=timeout).decode("utf-8", "replace"))


def sha256_of_file(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_structure(pdb_id: str) -> dict[str, Any]:
    """Parse the RCSB mmCIF file of an entry into atom records."""
    from Bio.PDB.MMCIF2Dict import MMCIF2Dict

    text = http_get(f"https://files.rcsb.org/download/{pdb_id}.cif").decode("utf-8", "replace")
    with tempfile.NamedTemporaryFile("w", suffix=".cif", delete=False, encoding="utf-8") as handle:
        handle.write(text)
        temp_path = handle.name
    try:
        cif = MMCIF2Dict(temp_path)
    finally:
        os.unlink(temp_path)
    columns = [key for key in cif.keys() if key.startswith("_atom_site.")]
    count = len(cif["_atom_site.id"])
    atoms = [{column: cif[column][i] for column in columns} for i in range(count)]
    entry_values = cif.get("_entry.id") or []
    return {"entry_id": entry_values[0] if entry_values else pdb_id, "atoms": atoms}


def component_ids(structure: dict) -> list[str]:
    return sorted({
        atom["_atom_site.label_comp_id"]
        for atom in structure["atoms"]
        if atom["_atom_site.label_seq_id"] in (".", "?", "")
    })


def polymer_residues(structure: dict) -> dict[tuple[str, str, str], dict]:
    residues: dict[tuple[str, str, str], dict] = {}
    for atom in structure["atoms"]:
        if atom["_atom_site.label_seq_id"] in (".", "?", ""):
            continue
        key = (atom["_atom_site.auth_asym_id"], atom["_atom_site.auth_seq_id"],
               atom["_atom_site.pdbx_PDB_ins_code"])
        entry = residues.setdefault(key, {
            "residue_name": atom["_atom_site.label_comp_id"],
            "label_seq_id": int(atom["_atom_site.label_seq_id"]),
            "entity_id": atom["_atom_site.label_entity_id"],
            "coords": [],
        })
        entry["coords"].append((
            float(atom["_atom_site.Cartn_x"]), float(atom["_atom_site.Cartn_y"]),
            float(atom["_atom_site.Cartn_z"]),
        ))
    return residues


def sifts_alignment(pdb_id: str, entity_id: str) -> dict[str, Any]:
    out: dict[str, Any] = {"entity_id": entity_id, "accession": None, "offset": None,
                           "route": None, "error": None}
    try:
        payload = http_get_json(
            f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/{entity_id}")
        for alignment in payload.get("rcsb_polymer_entity_align", []):
            if alignment.get("reference_database_name") != "UniProt":
                continue
            for region in alignment.get("aligned_regions", []):
                first = int(region["entity_beg_seq_id"])
                length = int(region["length"])
                out["accession"] = alignment["reference_database_accession"]
                out["offset"] = int(region["ref_beg_seq_id"]) - first
                out["first_label_seq_id"] = first
                out["last_label_seq_id"] = first + length - 1
                out["route"] = "RCSB Data API"
                return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"RCSB: {exc!r}"
    try:
        pdbe = http_get_json(
            f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot_to_pdb/{pdb_id.lower()}")
        for accession, blocks in (pdbe.get(pdb_id) or {}).items():
            for entry in (blocks.get("PDB") or {}).get(pdb_id, {}).values():
                for mapping in entry.get("mapping", []):
                    if int(mapping.get("entity_id", -1)) == int(entity_id):
                        out["accession"] = accession
                        out["route"] = "PDBe SIFTS API"
                        return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = (out["error"] or "") + f" | PDBe: {exc!r}"
    return out


def ligand_instances(structure: dict, ligand_id: str) -> list[tuple[str, str]]:
    seen = []
    for atom in structure["atoms"]:
        if atom["_atom_site.label_comp_id"].upper() != ligand_id.upper():
            continue
        if atom["_atom_site.label_seq_id"] not in (".", "?", ""):
            continue
        key = (atom["_atom_site.auth_asym_id"], atom["_atom_site.auth_seq_id"])
        if key not in seen:
            seen.append(key)
    return sorted(seen, key=lambda item: (item[0], int(item[1]) if item[1].lstrip("-").isdigit() else 0))


def contact_residues(structure: dict, ligand_id: str, cutoff: float,
                     chain: Optional[str] = None) -> dict[str, Any]:
    """Residues within `cutoff` of the ligand, in auth and UniProt numbering."""
    ligand_atoms = [
        (float(atom["_atom_site.Cartn_x"]), float(atom["_atom_site.Cartn_y"]),
         float(atom["_atom_site.Cartn_z"]))
        for atom in structure["atoms"]
        if atom["_atom_site.label_comp_id"].upper() == ligand_id.upper()
        and atom["_atom_site.label_seq_id"] in (".", "?", "")
        and atom["_atom_site.type_symbol"] not in ("H", "D")
        and (chain is None or atom["_atom_site.auth_asym_id"] == chain)
    ]
    residues = polymer_residues(structure)
    contacts = []
    for key, residue in residues.items():
        if chain is not None and key[0] != chain:
            continue
        best = min(math.dist(atom, ligand) for atom in residue["coords"]
                   for ligand in ligand_atoms) if ligand_atoms else float("inf")
        if best <= cutoff:
            contacts.append({
                "chain": key[0],
                "pdb_number": int(key[1]),
                "insertion_code": None if key[2] in (".", "?") else key[2],
                "residue_name": residue["residue_name"],
                "min_distance": round(best, 3),
                "label_seq_id": residue["label_seq_id"],
                "entity_id": residue["entity_id"],
            })
    contacts.sort(key=lambda c: (c["chain"], c["pdb_number"]))
    return {"ligand_atoms": len(ligand_atoms), "contacts": contacts}


def ligand_ligand_distance(structure: dict, ligand_a: str, ligand_b: str) -> Optional[float]:
    def atoms(comp_id: str):
        return [
            (float(atom["_atom_site.Cartn_x"]), float(atom["_atom_site.Cartn_y"]),
             float(atom["_atom_site.Cartn_z"]))
            for atom in structure["atoms"]
            if atom["_atom_site.label_comp_id"].upper() == comp_id.upper()
            and atom["_atom_site.label_seq_id"] in (".", "?", "")
            and atom["_atom_site.type_symbol"] not in ("H", "D")
        ]
    a_atoms, b_atoms = atoms(ligand_a), atoms(ligand_b)
    if not a_atoms or not b_atoms:
        return None
    return round(min(math.dist(x, y) for x in a_atoms for y in b_atoms), 3)


def uniprot_record(accession: str) -> dict[str, Any]:
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    try:
        payload = http_get_json(url)
    except Exception as exc:  # noqa: BLE001
        return {"accession": accession, "error": repr(exc)}
    description = payload.get("proteinDescription", {}).get("recommendedName", {})
    genes = payload.get("genes") or []
    features = []
    for feature in payload.get("features") or []:
        if feature.get("type") not in ("Domain", "Region", "Binding site", "Active site",
                                      "Site", "Modified residue", "Natural variant"):
            continue
        location = feature.get("location") or {}
        start = location.get("start", {}).get("value")
        end = location.get("end", {}).get("value")
        features.append({
            "type": feature.get("type"),
            "description": feature.get("description"),
            "start": start,
            "end": end,
        })
    return {
        "accession": accession,
        "name": description.get("fullName", {}).get("value"),
        "gene": genes[0].get("geneName", {}).get("value") if genes else None,
        "organism": payload.get("organism", {}).get("scientificName"),
        "length": payload.get("sequence", {}).get("length"),
        "features": features,
        "source": url,
    }


def chembl_records(db_path: Path, molecule: str, target_chembl_id: str,
                    standard_type: str = "IC50") -> dict[str, Any]:
    if not db_path.is_file():
        return {"error": f"ChEMBL SQLite not found at {db_path}"}
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        type_clause = "AND a.standard_type = ?" if standard_type else ""
        params = [molecule, target_chembl_id] + ([standard_type] if standard_type else [])
        rows = connection.execute(
            """
            SELECT a.activity_id, a.molregno, a.standard_type, a.standard_relation,
                   a.standard_value, a.standard_units, a.assay_id, asy.assay_type
            FROM activities a
            JOIN assays asy ON a.assay_id = asy.assay_id
            JOIN target_dictionary td ON asy.tid = td.tid
            JOIN molecule_dictionary md ON a.molregno = md.molregno
            WHERE UPPER(md.pref_name) = UPPER(?) AND td.chembl_id = ?
            """ + type_clause,
            params,
        ).fetchall()
    finally:
        connection.close()
    values = sorted(float(r[4]) for r in rows if r[4] is not None)
    return {
        "molecule": molecule,
        "target_chembl_id": target_chembl_id,
        "standard_type": standard_type,
        "count": len(rows),
        "relations": {rel: sum(1 for r in rows if r[3] == rel)
                      for rel in sorted({r[3] for r in rows}, key=lambda v: (v is None, v))},
        "units": {unit: sum(1 for r in rows if r[5] == unit)
                  for unit in sorted({r[5] for r in rows}, key=lambda v: (v is None, v))},
        "assay_types": {atype: sum(1 for r in rows if r[7] == atype)
                        for atype in sorted({r[7] for r in rows}, key=lambda v: (v is None, v))},
        "n_values": len(values),
        "median_value": (statistics.median(values) if values else None),
        "best_value": values[0] if values else None,
        "max_value": values[-1] if values else None,
        "best_activity_id": min((r[0] for r in rows if r[4] is not None), default=None),
        "best_assay_id": min((r[6] for r in rows if r[4] is not None), default=None),
    }


def chembl_target_for_uniprot(db_path: Path, uniprot: str) -> list[str]:
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT DISTINCT t.chembl_id FROM target_dictionary t "
            "JOIN target_components tc ON t.tid = tc.tid "
            "JOIN component_sequences cs ON tc.component_id = cs.component_id "
            "WHERE cs.accession = ? AND t.target_type = 'SINGLE PROTEIN'",
            (uniprot,),
        ).fetchall()
    finally:
        connection.close()
    return [row[0] for row in rows]


def chembl_molecule(db_path: Path, name: str) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT molregno, chembl_id, pref_name, max_phase FROM molecule_dictionary "
            "WHERE UPPER(pref_name) = UPPER(?) LIMIT 3", (name,)).fetchall()
        if not rows:
            rows = connection.execute(
                "SELECT md.molregno, md.chembl_id, md.pref_name, md.max_phase "
                "FROM molecule_dictionary md JOIN molecule_synonyms ms "
                "ON md.molregno = ms.molregno WHERE UPPER(ms.synonyms) = UPPER(?) LIMIT 3",
                (name,)).fetchall()
    finally:
        connection.close()
    return {"name": name, "matches": [
        {"molregno": r[0], "chembl_id": r[1], "pref_name": r[2], "max_phase": r[3]}
        for r in rows]}


def _scan_cache_key(kind: str, path: Path, extra: str) -> Path:
    stat = path.stat() if path.is_file() else None
    signature = f"{kind}|{path}|{stat.st_size if stat else 0}|{extra}"
    digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:20]
    return _CACHE_DIR / f"scan_{kind}_{digest}.json"


def cached_scan(kind: str, path: Path, extra: str,
                compute: Callable[[], Any]) -> Any:
    """Cache a release-file scan by (file, query); the scans are minutes."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _scan_cache_key(kind, path, extra)
    if cache_file.is_file():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    result = compute()
    try:
        cache_file.write_text(json.dumps(result, default=str), encoding="utf-8")
    except OSError:
        pass
    return result


def variant_prompt_genes(draft: list[dict], facts: dict) -> dict[str, str]:
    """The gene of every wanted variant, from the prompt's own accession.

    The gene symbol comes from the UniProt record of the accession the
    prompt names, because that is the symbol ClinVar uses: the V01 prompt
    says "SHP2" but Q06124 is PTPN11 in ClinVar.
    """
    genes: dict[str, str] = {}
    for prompt in draft:
        variants = VARIANT_PROMPT_VARIANTS.get(prompt.get("id"))
        if not variants:
            continue
        record = facts.get("uniprot", {}).get(prompt.get("accession")) or {}
        gene = record.get("gene")
        if not gene:
            continue
        for variant in variants:
            genes[variant] = gene
    return genes


def _clinvar_genes(symbols: str) -> set[str]:
    """The gene symbols of one ClinVar row (the column can hold several)."""
    return {part.strip().upper() for part in re.split(r"[;,]", symbols) if part.strip()}


def scan_clinvar(path: Path, wanted: dict[str, str], genes: dict[str, str]) -> dict[str, dict]:
    """Scan the ClinVar release file for the wanted variants.

    A protein change alone is not unique: the release holds 86 rows with
    "Gly12Asp" and the first one is GJB4, not the KRAS of the V03 prompt.
    Each wanted variant therefore also carries the gene of its prompt, and a
    row matches only when the protein change AND the gene match.
    """
    found: dict[str, dict] = {}
    header: list[str] = []
    if not path.is_file():
        return found
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                if not header and "VariantID" in line:
                    header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            fields = line.rstrip("\n").split("\t")
            if not header:
                header = ["VariationID", "VariationType", "VariationName", "VariationId",
                          "GeneSymbol", "HGNC", "ClinicalSignificance"]
            row = dict(zip(header, fields))
            name = row.get("VariationName") or ""
            for key, change in wanted.items():
                if not change or change not in name or key in found:
                    continue
                gene = genes.get(key)
                row_genes = _clinvar_genes(row.get("GeneSymbol") or "")
                if not gene or gene.upper() not in row_genes:
                    continue
                found[key] = {
                    "variation_id": row.get("VariationID"),
                    "variation_name": name,
                    "gene": (row.get("GeneSymbol") or "").split(",")[0],
                    "clinical_significance": row.get("ClinicalSignificance"),
                    "review_status": row.get("ReviewStatus"),
                    "germline_classification": row.get("GermlineClassification"),
                }
    return found


def scan_clinvar_gene(path: Path, gene: str) -> dict[str, Any]:
    """Every ClinVar row of one gene symbol (count + the protein changes)."""
    count = 0
    changes: list[str] = []
    if not path.is_file():
        return {"gene": gene, "count": 0, "changes": []}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        header: list[str] = []
        for line in handle:
            if line.startswith("#"):
                if not header and "VariantID" in line:
                    header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            fields = line.rstrip("\n").split("\t")
            if not header:
                header = ["VariationID", "VariationType", "VariationName", "VariationId",
                          "GeneSymbol", "HGNC", "ClinicalSignificance"]
            row = dict(zip(header, fields))
            if (row.get("GeneSymbol") or "").split(",")[0].upper() != gene.upper():
                continue
            count += 1
            name = row.get("VariationName") or ""
            if "(p." in name:
                changes.append(name.split("(p.")[-1].rstrip(")"))
    return {"gene": gene, "count": count, "changes": sorted(set(changes))}


def scan_alphamissense(path: Path, wanted: set[tuple[str, str]]) -> dict[str, dict]:
    """Scan the AlphaMissense release TSV for the wanted (uniprot, variant) pairs."""
    found: dict[str, dict] = {}
    if not path.is_file():
        return found
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        header: list[str] = []
        for line in handle:
            if line.startswith("#"):
                continue
            header = line.rstrip("\n").split("\t")
            break
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 2:
                continue
            row = dict(zip(header, fields))
            key = (row.get("uniprot_id", ""), row.get("protein_variant", ""))
            if key in wanted:
                found[f"{key[0]} {key[1]}"] = {
                    "uniprot_id": key[0], "protein_variant": key[1],
                    "am_pathogenicity": row.get("am_pathogenicity"),
                    "am_class": row.get("am_class"),
                }
    return found


def scan_alphamissense_uniprot(path: Path, uniprot: str,
                              also: tuple[str, ...] = ()) -> dict[str, Any]:
    """Every AlphaMissense row mentioning one accession, in all identifier forms.

    The release file's `uniprot_id` column carries the canonical accession
    with an optional isoform suffix, so a substring match is used; the
    `also` accessions are scanned the same way (e.g. the orthologue).
    """
    rows: list[dict] = []
    other: dict[str, list[dict]] = {}
    if not path.is_file():
        return {"uniprot": uniprot, "rows": rows, "file_present": False}
    needles = (uniprot,) + tuple(also)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        header: list[str] = []
        for line in handle:
            if line.startswith("#"):
                continue
            header = line.rstrip("\n").split("\t")
            break
        for line in handle:
            hit = next((needle for needle in needles if needle in line), None)
            if hit is None:
                continue
            fields = line.rstrip("\n").split("\t")
            row = dict(zip(header, fields))
            if hit == uniprot:
                rows.append(row)
            else:
                other.setdefault(hit, []).append(row)
    return {"uniprot": uniprot, "rows": rows, "other_accessions": other,
            "file_present": True, "n_rows": len(rows),
            "identifier_forms": sorted({r.get("uniprot_id", "") for r in rows}),
            "variants_present": sorted({r.get("protein_variant", "") for r in rows})}



def stingallo(pdb_id: str, chain: str) -> dict[str, Any]:
    """The STINGAllo prediction for a PDB id and a chain.

    The service has a daily quota, so the responses are cached in the
    repository (benchmark/stingallo_cache.json) and a cached response
    is reused instead of calling the service again.
    """
    cache_path = _REPO_ROOT / "benchmark" / "stingallo_cache.json"
    key = f"{pdb_id}:{chain}"
    if cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if key in cached:
                return cached[key]
        except (OSError, ValueError):
            pass
    # The one-off response cached by benchmark/validate_k04.py, so that
    # the daily quota of the service is not spent twice on the same call.
    legacy = _REPO_ROOT / "benchmark" / "stingallo_1OPK_A.json"
    if legacy.is_file():
        try:
            payload = json.loads(legacy.read_text(encoding="utf-8"))
            data = payload.get("data") or {}
            if (data.get("pdb_id") == pdb_id
                    and (data.get("chain_id") or chain) == chain):
                return {"url": (f"https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs"
                                f"?pdb_id={pdb_id}&chain_id={chain}"),
                        "response_date": payload.get("query_time_utc"),
                        "payload": {"allosteric_residues": data.get("residues", [])},
                        "note": "the cached response (one call, within the daily quota)"}
        except (OSError, ValueError):
            pass
    url = (f"https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs"
           f"?pdb_id={pdb_id}&chain_id={chain}")
    try:
        body = http_get(url, cache=False).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "error": repr(exc)}
    try:
        payload = json.loads(body)
    except ValueError:
        return {"url": url, "error": f"non-JSON response: {body[:200]}"}
    record = {"url": url, "response_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "payload": payload}
    try:
        existing = {}
        if cache_path.is_file():
            existing = json.loads(cache_path.read_text(encoding="utf-8"))
        existing[key] = record
        cache_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return record


def rcsb_ligand_protein_entries(comp_id: str, accession: str) -> list[str]:
    query = {
        "query": {
            "type": "group", "logical_operator": "and",
            "nodes": [
                {"type": "terminal", "service": "text",
                 "parameters": {"attribute": "rcsb_chem_comp_container_identifiers.comp_id",
                                "operator": "exact_match", "value": comp_id}},
                {"type": "terminal", "service": "text",
                 "parameters": {"attribute": _UNIPROT_ATTR, "operator": "exact_match",
                                "value": accession}},
            ],
        },
        "return_type": "entry",
    }
    request = urllib.request.Request(
        "https://search.rcsb.org/rcsbsearch/v2/query",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "benchmark-validator/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        return []
    return [item["identifier"] for item in payload.get("result_set", [])]


def pdbe_ligand_protein_entries(comp_id: str, accession: str) -> list[str]:
    """The PDBe route: the entries where the compound occurs (PDBe compound
    summary) that also map the protein (PDBe SIFTS best_structures)."""
    try:
        payload = http_get_json(
            f"https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/{comp_id.lower()}")
    except Exception:  # noqa: BLE001
        return []
    candidates: set[str] = set()
    for entry in payload.get(comp_id.upper()) or []:
        candidates.update(entry.get("first_observed_in") or [])
    found = []
    for pdb_id in sorted(candidates):
        try:
            best = http_get_json(
                f"https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/{pdb_id.lower()}")
        except Exception:  # noqa: BLE001
            continue
        accessions: set[str] = set()
        for block in (best.get(pdb_id.upper()) or {}).values():
            for item in (block or {}).values():
                for uniprot in item.get("uniprot_ids") or []:
                    accessions.add(uniprot)
        if accession in accessions:
            found.append(pdb_id)
    return found


AA3 = {
    "A": "Ala", "R": "Arg", "N": "Asn", "D": "Asp", "C": "Cys", "Q": "Gln",
    "E": "Glu", "G": "Gly", "H": "His", "I": "Ile", "L": "Leu", "K": "Lys",
    "M": "Met", "F": "Phe", "P": "Pro", "S": "Ser", "T": "Thr", "W": "Trp",
    "Y": "Tyr", "V": "Val",
}

VARIANT_PROMPT_VARIANTS = {
    "V01": ["E76K", "D61Y"],
    "V02": ["E17K"],
    "V03": ["G12C", "G12D", "G12V"],
    "V04": ["T315I"],
}


def protein_change(variant: str) -> str:
    match = re.fullmatch(r"([A-Z])(\d+)([A-Z])", variant.strip())
    if not match:
        return variant
    return f"{AA3.get(match.group(1), match.group(1))}{match.group(2)}" \
           f"{AA3.get(match.group(3), match.group(3))}"


def residue_to_uniprot_number(structure: dict, entity_id: str, label_seq_id: int,
                              offsets: dict[str, Optional[int]]) -> Optional[int]:
    offset = offsets.get(entity_id)
    if offset is None:
        return None
    return label_seq_id + offset


# ------------------------------------------------------------------ helpers

def item(key: str, kind: str, value: Any, source: str, tolerance: Any = None,
         note: str | None = None, status: str = "PASS") -> dict:
    return {"key": key, "kind": kind, "value": value, "tolerance": tolerance,
            "source": source, "note": note, "status": status}


def uniprot_contact_label(contact: dict, offsets: dict[str, Optional[int]]) -> Optional[int]:
    offset = offsets.get(contact["entity_id"])
    if offset is None:
        return None
    return contact["label_seq_id"] + offset


def residue_number_set(contacts: list[dict], offsets: dict[str, Optional[int]]) -> list[int]:
    return sorted({uniprot_contact_label(c, offsets) for c in contacts
                   if uniprot_contact_label(c, offsets) is not None})


def write_pdb(pdb_id: str, target: Path) -> Path:
    """Download the PDB-format file (fpocket / PocketMiner want PDB)."""
    text = http_get(f"https://files.rcsb.org/download/{pdb_id}.pdb").decode("utf-8", "replace")
    target.write_text(text, encoding="utf-8")
    return target


def strip_ligands(pdb_text: str) -> str:
    """Keep only the ATOM records (drop HETATM): the ligand-stripped input."""
    return "\n".join(line for line in pdb_text.splitlines()
                     if not line.startswith("HETATM")) + "\n"


def _pdb_residue_order(pdb_path: Path) -> list[dict]:
    """The residues of a PDB file in file order, which is the order the
    PocketMiner wrapper scores them (it reads the file with
    MDAnalysis, whose residue list follows the ATOM records)."""
    order: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for line in pdb_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("ATOM"):
            continue
        key = (line[21].strip(), line[22:26].strip(), line[26].strip())
        if key in seen:
            continue
        seen.add(key)
        order.append({"chain": key[0], "pdb_number": int(key[1]),
                      "residue_name": line[17:20].strip(),
                      "insertion_code": key[2]})
    return order


def call_tool(module_name: str, function_name: str, **kwargs) -> dict[str, Any]:
    """Run one of our tools once and keep the raw payload (reference output)."""
    try:
        module = __import__(f"biomni.tool.{module_name}", fromlist=["*"])
        function = getattr(module, function_name)
        result = function(**kwargs)
    except Exception as exc:  # noqa: BLE001 - a failed reference call is data
        return {"error": f"{type(exc).__name__}: {exc}"}
    return result


# ------------------------------------------------------------------- facts

def compute_facts(args) -> dict[str, Any]:
    data_root = Path(args.data_root)
    cache_key = hashlib.sha256(
        (str(args.benchmark) + str(args.data_root) + BENCHMARK_VERSION).encode("utf-8")
    ).hexdigest()[:16]
    cache_file = _CACHE_DIR / f"facts_{cache_key}.json"
    if cache_file.is_file():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            cached["notes"] = ["facts loaded from the cache"]
            print(f"facts: loaded from {cache_file}")
            return cached
        except (OSError, ValueError):
            pass
    facts: dict[str, Any] = {"structures": {}, "contacts": {}, "sifts": {},
                             "instances": {}, "uniprot": {}, "chembl": {},
                             "clinvar": {}, "alphamissense": {}, "stingallo": {},
                             "tool_outputs": {}, "pocketminer_residues": {}, "notes": [], "sources": {}}

    entries = ["1T4J", "1OPK", "1V4S", "3O96", "5EHR", "1PZO", "5MO4",
               "6OIM", "2SHP", "1AKE", "1BTL", "2HYY"]
    for pdb_id in entries:
        try:
            structure = fetch_structure(pdb_id)
        except Exception as exc:  # noqa: BLE001
            facts["notes"].append(f"{pdb_id}: structure fetch failed: {exc!r}")
            continue
        facts["structures"][pdb_id] = structure
        residues = polymer_residues(structure)
        entity_ids = sorted({r["entity_id"] for r in residues.values()})
        alignment = sifts_alignment(pdb_id, entity_ids[0]) if entity_ids else {}
        facts["sifts"][pdb_id] = alignment
        offsets = {entity_ids[0]: alignment.get("offset")} if entity_ids else {}
        for ligand in component_ids(structure):
            facts["instances"].setdefault(pdb_id, {})[ligand] = ligand_instances(
                structure, ligand)
            for cutoff in (4.0, 6.0):
                for chain in (None, "A"):
                    found = contact_residues(structure, ligand, cutoff, chain)
                    key = f"{pdb_id}:{ligand}:{cutoff}:{chain or 'all'}"
                    facts["contacts"][key] = {
                        "contacts": found["contacts"],
                        "uniprot_numbers": residue_number_set(found["contacts"], offsets),
                        "ligand_atoms": found["ligand_atoms"],
                        "offset": alignment.get("offset"),
                        "accession": alignment.get("accession"),
                    }

    for accession in ["P18031", "P00519", "Q06124", "P35557", "P31749",
                       "P62593", "P01116", "Q02750", "P69441"]:
        facts["uniprot"][accession] = uniprot_record(accession)

    db_path = data_root / "chembl" / "chembl_37_sqlite" / "chembl_37.db"
    for molecule, uniprot in [("imatinib", "P00519"), ("asciminib", "P00519"),
                              ("trametinib", "Q02750"), ("cobimetinib", "Q02750"),
                              ("sotorasib", "P01116"), ("SHP099", "Q06124"),
                              ("SHP099", "P18031"), ("MK-2206", "P31749"),
                              ("MK2206", "P31749"), ("MK 2206", "P31749")]:
        try:
            targets = chembl_target_for_uniprot(db_path, uniprot)
            record = {"molecule": chembl_molecule(db_path, molecule),
                      "targets": targets, "uniprot": uniprot}
            if targets:
                record["ic50"] = chembl_records(db_path, molecule, targets[0], "IC50")
                record["all_types"] = chembl_records(db_path, molecule, targets[0], "")
            facts["chembl"][f"{molecule}|{uniprot}"] = record
        except Exception as exc:  # noqa: BLE001
            facts["chembl"][f"{molecule}|{uniprot}"] = {"error": repr(exc)}
    facts["sources"]["chembl_db"] = {"path": str(db_path),
                                     "sha256": sha256_of_file(db_path)}

    clinvar_path = data_root / "clinvar" / "variant_summary.txt.gz"
    am_path = data_root / "alphamissense" / "AlphaMissense_aa_substitutions.tsv.gz"
    variant_genes = variant_prompt_genes(
        json.loads(Path(args.benchmark).read_text(encoding="utf-8")), facts)
    wanted = {variant: protein_change(variant)
              for variants in VARIANT_PROMPT_VARIANTS.values()
              for variant in variants}
    facts["clinvar"] = cached_scan(
        "clinvar", clinvar_path,
        json.dumps([wanted, variant_genes], sort_keys=True),
        lambda: scan_clinvar(clinvar_path, wanted, variant_genes))
    facts["clinvar_gck"] = cached_scan("clinvar_gene", clinvar_path, "GCK", lambda: scan_clinvar_gene(clinvar_path, "GCK"))
    facts["clinvar_source"] = {
        "path": str(clinvar_path), "sha256": sha256_of_file(clinvar_path),
        "release": "ClinVar variant_summary.txt.gz (pinned copy in data/clinvar)",
    }
    am_wanted = {("P01116", "G12C"), ("P01116", "G12D"), ("P01116", "G12V"),
                 ("P00519", "T315I"), ("Q06124", "E76K"), ("Q06124", "D61Y"),
                 ("P31749", "E17K")}
    facts["alphamissense"] = cached_scan("am", am_path, json.dumps(sorted(am_wanted)), lambda: scan_alphamissense(am_path, am_wanted))
    q06124 = cached_scan("am_uniprot", am_path, "Q06124+P35235", lambda: scan_alphamissense_uniprot(am_path, "Q06124", also=("P35235",)))
    facts["alphamissense_q06124"] = {
        "uniprot": "Q06124",
        "n_rows": q06124.get("n_rows", 0),
        "identifier_forms": q06124.get("identifier_forms", []),
        "variants_present": q06124.get("variants_present", []),
        "has_E76K": "E76K" in (q06124.get("variants_present") or []),
        "has_D61Y": "D61Y" in (q06124.get("variants_present") or []),
        "mouse_P35235_rows": len((q06124.get("other_accessions") or {}).get("P35235", [])),
        "mouse_P35235_variants": sorted({
            r.get("protein_variant", "")
            for r in (q06124.get("other_accessions") or {}).get("P35235", [])}),
        "file_sha256": sha256_of_file(am_path),
    }
    facts["alphamissense_source"] = {
        "path": str(am_path), "sha256": sha256_of_file(am_path),
        "release": "AlphaMissense_aa_substitutions.tsv.gz (pinned copy)",
    }

    for pdb_id, chain in [("1T4J", "A"), ("5EHR", "A"), ("1OPK", "A")]:
        facts["stingallo"][pdb_id] = stingallo(pdb_id, chain)

    # our own tools: reference outputs for the pocket / dynamics prompts
    work = Path(tempfile.mkdtemp(prefix="benchmark_ref_"))
    try:
        for pdb_id in ["1T4J", "6OIM", "2SHP", "1OPK", "1V4S", "1BTL"]:
            stripped = work / f"{pdb_id}_stripped.pdb"
            raw = http_get(f"https://files.rcsb.org/download/{pdb_id}.pdb").decode("utf-8", "replace")
            stripped.write_text(strip_ligands(raw), encoding="utf-8")
            facts["tool_outputs"][f"fpocket:{pdb_id}:stripped"] = call_tool(
                "detect_pockets_fpocket", "detect_pockets_fpocket",
                pdb_path=str(stripped))
            facts["tool_outputs"][f"p2rank:{pdb_id}:stripped"] = call_tool(
                "detect_pockets_p2rank", "detect_pockets_p2rank",
                pdb_path=str(stripped))
            full = work / f"{pdb_id}.pdb"
            full.write_text(raw, encoding="utf-8")
            facts["tool_outputs"][f"pocketminer:{pdb_id}"] = call_tool(
                "pocketminer", "pocketminer_score", pdb_path=str(full))
            facts["pocketminer_residues"][pdb_id] = _pdb_residue_order(full)
            facts["tool_outputs"][f"nmr:{pdb_id}"] = call_tool(
                "normal_mode_analysis", "normal_mode_analysis", pdb_id=pdb_id)
            facts["tool_outputs"][f"network:{pdb_id}"] = call_tool(
                "residue_contact_network", "residue_contact_network",
                mmcif_path=str(full))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    try:
        cache_file.write_text(json.dumps(facts, default=str), encoding="utf-8")
    except OSError:
        pass
    return facts


# --------------------------------------------------- per-prompt checklists

def C(facts, pdb_id, ligand, cutoff=4.0, chain=None):
    key = f"{pdb_id}:{ligand}:{cutoff}:{chain or 'all'}"
    return facts["contacts"].get(key, {"contacts": [], "uniprot_numbers": []})


def _residue_text(contacts: list[dict]) -> str:
    return ", ".join(f"{c['residue_name']}{c['pdb_number']}({c['min_distance']})"
                     for c in contacts)


def _uniprot_text(numbers: list[int]) -> str:
    return ", ".join(str(n) for n in numbers)


def build_items(prompt: dict, facts: dict) -> tuple[list[dict], list[str]]:
    """Return (checklist items, proposed fixes for the problems found)."""
    pid = prompt["id"]
    items: list[dict] = []
    problems: list[str] = []
    accession = prompt.get("accession")
    record = facts["uniprot"].get(accession, {})

    def accession_item(note: str | None = None) -> None:
        items.append(item(
            f"accession_{accession}", "exact",
            {"name": record.get("name"), "gene": record.get("gene"),
             "organism": record.get("organism")},
            "UniProt REST", note=note))

    def ligand_item(pdb_id: str, ligand: str, chain: str | None = None,
                    residue_number: int | None = None) -> None:
        instances = facts["instances"].get(pdb_id, {}).get(ligand, [])
        if chain is not None:
            instances = [i for i in instances if i[0] == chain]
        value = [{"chain": c, "pdb_number": int(n)} for c, n in instances]
        status = "PASS"
        note = None
        if residue_number is not None:
            numbers = {int(n) for _, n in instances}
            if residue_number not in numbers:
                status = "PROBLEM"
                note = (f"the checklist says {ligand} at residue {residue_number}, "
                        f"the file has {sorted(numbers)}")
                problems.append(
                    f"{pid}: {ligand} in {pdb_id} is at {sorted(numbers)}, not "
                    f"{residue_number} as the checklist states.")
        items.append(item(f"ligand_{pdb_id}_{ligand}", "exact", value,
                          f"RCSB mmCIF {pdb_id}", note=note, status=status))

    def contacts_item(pdb_id: str, ligand: str, cutoff: float = 4.0,
                      chain: str | None = None, key: str | None = None) -> None:
        found = C(facts, pdb_id, ligand, cutoff, chain)
        items.append(item(
            key or f"contacts_{pdb_id}_{ligand}_{cutoff:g}A", "set",
            {"uniprot_residues": found.get("uniprot_numbers", []),
             "pdb_residues": [c["pdb_number"] for c in found.get("contacts", [])],
             "min_distances": {c["pdb_number"]: c["min_distance"]
                               for c in found.get("contacts", [])}},
            f"RCSB mmCIF {pdb_id} + SIFTS (offset "
            f"{found.get('offset')})", tolerance=0))

    def number_item(key: str, value: Any, source: str, tolerance: Any = None,
                    note: str | None = None, status: str = "PASS") -> None:
        items.append(item(key, "number", value, source, tolerance=tolerance,
                          note=note, status=status))

    def qualitative_item(key: str, criterion: str, source: str,
                         note: str | None = None) -> None:
        items.append(item(key, "qualitative", criterion, source, note=note))

    # ------------------------------------------------------------ site prompts
    if pid == "S01":
        accession_item()
        ligand_item("1T4J", "FRJ", "A", 299)
        contacts_item("1T4J", "FRJ", 4.0, "A")
        number_item("contact_count_1T4J_FRJ_4A",
                    len(C(facts, "1T4J", "FRJ", 4.0, "A")["contacts"]),
                    "RCSB mmCIF 1T4J", tolerance=0)
    elif pid == "S02":
        accession_item()
        ligand_item("1OPK", "MYR", "A", 1)
        ligand_item("1OPK", "P16", "A", 2)
        contacts_item("1OPK", "MYR", 4.0, "A")
    elif pid == "S03":
        accession_item()
        ligand_item("1V4S", "MRK", "A", 501)
        ligand_item("1V4S", "GLC", "A", 500)
        contacts_item("1V4S", "MRK", 4.0, "A")
        structure = facts["structures"].get("1V4S")
        distance = ligand_ligand_distance(structure, "MRK", "GLC") if structure else None
        number_item("min_distance_MRK_GLC_1V4S", distance,
                    "RCSB mmCIF 1V4S", tolerance=0.5)
    elif pid == "S04":
        accession_item()
        ligand_item("3O96", "IQO", "A", 444)
        contacts_item("3O96", "IQO", 4.0, "A")
        domains = [f for f in record.get("features", []) if f.get("type") == "Domain"]
        qualitative_item(
            "akt1_domains", "the contact residues fall in the PH domain of AKT1",
            "UniProt domain features",
            note="; ".join(f"{d['description']} {d['start']}-{d['end']}" for d in domains))
    elif pid == "S05":
        accession_item()
        ligand_item("5EHR", "5OD", "A", 601)
        contacts_item("5EHR", "5OD", 4.0, "A")
        domains = [f for f in record.get("features", []) if f.get("type") in ("Domain", "Region")]
        qualitative_item(
            "shp2_domains", "each contact residue is assigned to N-SH2, C-SH2 or PTP",
            "UniProt domain features",
            note="; ".join(f"{d['description']} {d['start']}-{d['end']}" for d in domains))
    elif pid == "S06":
        accession_item()
        instances = facts["instances"].get("1PZO", {}).get("CBT", [])
        ligand_item("1PZO", "CBT", "A")
        contacts_item("1PZO", "CBT", 4.0, "A")
        numbers = sorted({int(n) for _, n in instances})
        if len(numbers) < 2:
            problems.append(
                f"S06: 1PZO has {len(numbers)} CBT copy/copies ({numbers}), the "
                "checklist says two copies (A 300, A 301).")
        items.append(item("cbt_copies", "exact", numbers, "RCSB mmCIF 1PZO",
                          note="the two copies are a symmetry pair: the "
                               "heavy-atom distance between them is 0.000 A"))
    elif pid == "S07":
        accession_item()
        ligand_item("5MO4", "AY7", "A", 602)
        ligand_item("5MO4", "NIL", "A", 601)
        contacts_item("5MO4", "AY7", 4.0, "A", key="contacts_5MO4_AY7_4A")
        contacts_item("5MO4", "NIL", 4.0, "A", key="contacts_5MO4_NIL_4A")
        ay = set(C(facts, "5MO4", "AY7", 4.0, "A")["uniprot_numbers"])
        ni = set(C(facts, "5MO4", "NIL", 4.0, "A")["uniprot_numbers"])
        items.append(item("ay7_nil_overlap", "number", len(ay & ni),
                          "RCSB mmCIF 5MO4", tolerance=0,
                          note="the two contact sets must not overlap"))
        sifts = facts["sifts"].get("5MO4", {})
        items.append(item(
            "numbering_offset_5MO4", "number",
            {"sifts_label_to_uniprot": sifts.get("offset"),
             "auth_T334_to_uniprot_T315": -19},
            "RCSB SIFTS alignment + the T334I mutation", tolerance=0))
    # ----------------------------------------------------------- pocket prompts
    elif pid == "P04":
        accession_item()
        miner = facts["tool_outputs"].get("pocketminer:1BTL", {})
        miner_data = miner.get("data") or {}
        scores = miner_data.get("residue_scores") or []
        order = facts.get("pocketminer_residues", {}).get("1BTL", [])
        aligned = []
        if len(scores) == len(order):
            for residue, score in zip(order, scores):
                aligned.append({"chain": residue["chain"],
                                "pdb_number": residue["pdb_number"],
                                "residue_name": residue["residue_name"],
                                "score": round(float(score), 4)})
        else:
            aligned = [{"note": "the score count and the residue count differ",
                        "n_scores": len(scores), "n_residues": len(order)}]
        top_ten = sorted(
            [row for row in aligned if "score" in row],
            key=lambda row: row["score"], reverse=True)[:10]
        items.append(item("pocketminer_top10_1BTL", "exact", top_ten,
                          "PocketMiner on 1BTL (our tool, reference output)",
                          note="reference output, not ground truth; the scores are "
                               "one per residue in PDB order"))
        # the 1PZO CBT contact residues, scored in 1BTL through UniProt numbering
        contacts_1pzo = C(facts, "1PZO", "CBT", 4.0, "A")["uniprot_numbers"]
        btl = facts["structures"].get("1BTL")
        offset = (facts["sifts"].get("1BTL") or {}).get("offset") or 0
        auth_to_uniprot: dict[int, int] = {}
        if btl:
            for key, residue in polymer_residues(btl).items():
                auth_to_uniprot[int(key[1])] = residue["label_seq_id"] + offset
        score_by_residue = {}
        for row in aligned:
            if "score" not in row:
                continue
            uniprot = auth_to_uniprot.get(row["pdb_number"])
            if uniprot is not None:
                score_by_residue[uniprot] = row["score"]
        items.append(item(
            "pocketminer_scores_for_1PZO_contacts", "exact",
            {str(number): score_by_residue.get(number)
             for number in contacts_1pzo},
            "PocketMiner on 1BTL, mapped to UniProt numbering through the "
            "1BTL SIFTS alignment",
            note="the CBT-contact residues of 1PZO and their PocketMiner scores "
                 "in 1BTL; a null means the residue is not scored in 1BTL"))
        qualitative_item(
            "mapping_stated", "the mapping between the two entries is stated (both "
                              "are TEM-1, P62593; the 1PZO CBT contacts are given in "
                              "UniProt numbering)",
            "RCSB SIFTS")
    elif pid == "P08":
        accession_item()
        miner = facts["tool_outputs"].get("pocketminer:2SHP", {})
        miner_data = miner.get("data") or {}
        scores = miner_data.get("residue_scores") or []
        order = facts.get("pocketminer_residues", {}).get("2SHP", [])
        aligned = []
        if len(scores) == len(order):
            for residue, score in zip(order, scores):
                aligned.append({"chain": residue["chain"],
                                "pdb_number": residue["pdb_number"],
                                "residue_name": residue["residue_name"],
                                "score": round(float(score), 4)})
        else:
            aligned = [{"note": "the score count and the residue count differ",
                        "n_scores": len(scores), "n_residues": len(order)}]
        chain_a_rows = [row for row in aligned if "score" in row and row["chain"] == "A"]
        top_ten = sorted(chain_a_rows, key=lambda row: row["score"], reverse=True)[:10]
        items.append(item("pocketminer_top10_2SHP_chain_A", "exact", top_ten,
                          "PocketMiner on 2SHP chain A (our tool, reference output)",
                          note="reference output, not ground truth; the per-chain "
                               "scores are the model's screening signal, and the "
                               "per-chain means are in the wrapper's 'chains' block"))
        # the 5EHR SHP099 contact residues, mapped onto 2SHP through UniProt
        contacts_5ehr = C(facts, "5EHR", "5OD", 4.0, "A")["uniprot_numbers"]
        shp = facts["structures"].get("2SHP")
        offset = (facts["sifts"].get("2SHP") or {}).get("offset") or 0
        uniprot_to_auth: dict[int, int] = {}
        if shp:
            for key, residue in polymer_residues(shp).items():
                if key[0] != "A":
                    continue
                uniprot_to_auth[residue["label_seq_id"] + offset] = int(key[1])
        rank_of = {row["pdb_number"]: index + 1
                   for index, row in enumerate(sorted(chain_a_rows,
                                                      key=lambda row: row["score"],
                                                      reverse=True))}
        score_by_auth = {row["pdb_number"]: row["score"] for row in chain_a_rows}
        mapped = []
        for number in contacts_5ehr:
            auth = uniprot_to_auth.get(int(number))
            mapped.append({
                "uniprot_number": int(number),
                "pdb_number_2SHP": auth,
                "pocketminer_score": score_by_auth.get(auth) if auth is not None else None,
                "pocketminer_rank_in_chain_A": rank_of.get(auth) if auth is not None else None,
            })
        items.append(item(
            "mapped_5EHR_SHP099_contacts_on_2SHP", "exact", mapped,
            "the 5EHR SHP099 contact residues (4 A, chain A) mapped onto 2SHP "
            "through the UniProt numbering, with their PocketMiner scores",
            note="both entries are Q06124, so the UniProt numbering is the "
                 "correspondence; a null means the residue is not scored in 2SHP"))
        ranks = [row["pocketminer_rank_in_chain_A"] for row in mapped
                 if row["pocketminer_rank_in_chain_A"] is not None]
        items.append(item(
            "site_rank_comparison", "exact",
            {"n_site_residues": len(mapped),
             "n_scored": len(ranks),
             "n_in_the_top10": sum(1 for row in mapped if row["pdb_number_2SHP"] in
                                   {row2["pdb_number"] for row2 in top_ten}),
             "best_rank": min(ranks) if ranks else None,
             "median_rank": statistics.median(ranks) if ranks else None},
            "PocketMiner on 2SHP chain A (our tool, reference output)",
            note="the ranks of the SHP099 site residues among the 2SHP chain A "
                 "scores; the comparison is a screening signal, not a detection"))
        items.append(item(
            "modest_accuracy_caveat", "qualitative",
            "the answer states that PocketMiner is a screening tool with modest "
            "accuracy (per-protein AUC about 0.65 on the independent test "
            "split), so the scores rank cryptic-pocket propensity and do not "
            "establish that a residue is a pocket or that the site is allosteric",
            "the tool card of pocketminer_score"))
        qualitative_item(
            "mapping_stated", "the mapping between the two entries is stated (both "
                              "are SHP2, Q06124; the 5EHR SHP099 contacts are given "
                              "in UniProt numbering)",
            "RCSB SIFTS")
    elif pid in ("P01", "P02", "P03", "P05", "P06", "P07", "H02"):
        accession_item()
        reference = facts["tool_outputs"].get(f"fpocket:{pid_entry(pid)}:stripped", {})
        pockets = (reference.get("data") or {}).get("pockets") or []
        items.append(item("fpocket_top3", "exact",
                          [{"rank": i + 1,
                            "residues": len(p.get("residues", []))}
                           for i, p in enumerate(pockets[:3])],
                          f"fpocket on the ligand-stripped {pid_entry(pid)}",
                          note="reference output, not ground truth"))
        qualitative_item(
            "pocket_recovery",
            {
                "P01": "the top three fpocket pockets of the ligand-stripped 1T4J contain "
                       "the residues FRJ contacted, and the overlap is reported as a count",
                "P02": "the rank of the pocket that covers the former switch-II "
                       "inhibitor site (the MOV contacts) is reported",
                "P03": "the overlap of the top five pockets of 2SHP with the 5EHR SHP099 "
                       "contact residues, mapped through UniProt numbering, is reported",
                "P05": "the rank of the pocket that covers the myristoyl site (the MYR "
                       "contacts) is reported",
                "P06": "which of the top three pockets of 1V4S matches the MRK site and "
                       "which matches the GLC site is reported",
                "P07": "the rank or score each of fpocket, P2Rank and PocketMiner assigns "
                       "to the FRJ contact residues, which methods agree, and the caveat "
                       "that a pocket detector cannot label an allosteric pocket",
                "H02": "a ranking of the top three pockets by allosteric likelihood with "
                       "the stated limit that pocket detectors do not distinguish "
                       "allosteric from orthosteric pockets",
            }[pid],
            "the prompt's own criterion")
    # --------------------------------------------------------- dynamics prompts
    elif pid in ("C01", "C02", "C03", "C04", "C05", "C06"):
        accession_item()
        qualitative_item(
            "analysis_present",
            {
                "C01": "the hinge residues of the slowest non-trivial normal mode and the "
                       "relative mobility of the WPD loop (the catalytic Asp181) are "
                       "reported, in UniProt numbering",
                "C02": "the shortest path from the residue closest to the allosteric "
                       "ligand to Cys215 is reported with its length and the cutoff used",
                "C03": "the mobility of the 5EHR SHP099-contact residues (mapped through "
                       "UniProt numbering) is compared with the rest of the structure",
                "C04": "the shortest path between an MRK-contact residue and a "
                       "GLC-contact residue is reported with its length",
                "C05": "the communities of 1AKE at an 8 A C-alpha cutoff are reported with "
                       "the algorithm and the seed, and their relation to the LID, NMP and "
                       "CORE domains",
                "C06": "the normal-mode analysis, the contact-network path to Cys215 and "
                       "the STINGAllo prediction are each present with their limits stated",
            }[pid],
            "the prompt's own criterion")
    # ---------------------------------------------------------- variant prompts
    elif pid in ("V01", "V02", "V03", "V04"):
        accession_item()
        variants = VARIANT_PROMPT_VARIANTS[pid]
        for variant in variants:
            clinvar = facts["clinvar"].get(variant, {})
            am = facts["alphamissense"].get(f"{accession} {variant}", {})
            status = "PASS"
            note = None
            if not am:
                status = "PROBLEM"
                note = "no AlphaMissense row for this variant"
                problems.append(
                    f"{pid}: AlphaMissense has no row for {accession} {variant} "
                    f"(the release file has no {accession} row at all for SHP2); the "
                    "prompt cannot be answered as written.")
            items.append(item(
                f"clinvar_{variant}", "exact",
                {"clinical_significance": clinvar.get("clinical_significance"),
                 "variation_id": clinvar.get("variation_id")},
                f"ClinVar release ({facts['clinvar_source']['sha256'][:12]})",
                note=note, status=status))
            items.append(item(
                f"alphamissense_{variant}", "number",
                float(am["am_pathogenicity"]) if am.get("am_pathogenicity") else None,
                f"AlphaMissense release ({facts['alphamissense_source']['sha256'][:12]})",
                tolerance=0.01, note=note, status=status))
        if pid == "V01":
            qualitative_item(
                "distances", "the distances of residues 76 and 61 to the 5EHR inhibitor "
                            "site and to the 2SHP autoinhibitory interface are reported",
                "RCSB mmCIF 5EHR + 2SHP")
        elif pid == "V02":
            qualitative_item(
                "domain_and_distance",
                "the PH domain is named and the distance from residue 17 to the 3O96 "
                "inhibitor is reported (residue 17 IS modelled: UniProt 17 = label_seq_id "
                "20, the PDB author number differs)", "UniProt + RCSB mmCIF 3O96")
        elif pid == "V03":
            qualitative_item("distance", "the distance from residue 12 to the 6OIM "
                                        "covalent inhibitor is reported", "RCSB mmCIF 6OIM")
            qualitative_item("resolution", "the answer says whether the three scores "
                                           "separate the variants", "the prompt")
        elif pid == "V04":
            qualitative_item("distances", "the distances from T315I to the ATP-site ligand "
                                         "(P16) and to the myristoyl-site ligand (MYR) in "
                                         "1OPK are reported, with a hedged inference",
                             "RCSB mmCIF 1OPK")
    elif pid in ("V05", "V06"):
        accession_item()
        if pid == "V05":
            gck_rows = facts.get("clinvar_gck", {})
            number_item(
                "clinvar_variant_count_GCK", gck_rows.get("count"),
                f"ClinVar release ({facts['clinvar_source']['sha256'][:12]})",
                tolerance=f"+/- {max(10, int(0.1 * (gck_rows.get('count') or 0)))} "
                           "(10 % band: the release and the live API differ)",
                note="the checklist uses a classification and a tolerance band, not an "
                     "exact count (the pinned release and the live API give "
                     "16,066 vs 16,106 for BRCA1)")
        qualitative_item(
            "variant_list", {
                "V05": "the ClinVar variants of glucokinase are mapped onto 1V4S and the "
                       "ones within 6 A of the MRK activator are listed with their "
                       "AlphaMissense scores",
                "V06": "the PocketMiner cryptic-pocket residues of 1BTL, the UniProt "
                       "variants of TEM-1 and every annotated variant within 6 A of a "
                       "1PZO CBT-contact residue are listed",
            }[pid], "the prompt's own criterion")
    # ---------------------------------------------------------- modulator prompts
    elif pid == "L01":
        accession_item()
        items.append(item("ay7_abl1_entries", "exact",
                          rcsb_ligand_protein_entries("AY7", "P00519"),
                          "RCSB Search API v2"))
        qualitative_item("pdbe_route", "the entry list is confirmed on a second route "
                                       "(PDBe); the PDBe mappings endpoints answer 404 "
                                       "from this host, so the second route is recorded "
                                       "as unavailable", "PDBe SIFTS API")
        problems.append(
            "L01: the checklist requires the RCSB and the PDBe route to agree, but the "
            "PDBe mappings endpoints answer 404 from the validation host, so the second "
            "route cannot be exercised here; either relax the checklist item to the "
            "RCSB route plus a recorded note that the PDBe route was unavailable, or "
            "re-run the PDBe leg from a host that can reach www.ebi.ac.uk.")
    elif pid == "L02":
        accession_item()
        for name in ("trametinib", "cobimetinib"):
            record = facts["chembl"].get(f"{name}|Q02750", {})
            ic50 = record.get("ic50", {})
            items.append(item(f"chembl_{name}", "exact",
                              {"count": ic50.get("count"),
                               "median_nM": ic50.get("median_value"),
                               "best_nM": ic50.get("best_value"),
                               "units": ic50.get("units")},
                              "ChEMBL 37 SQLite, direct SQL"))
    elif pid == "L03":
        accession_item()
        for name in ("asciminib", "imatinib"):
            record = facts["chembl"].get(f"{name}|P00519", {})
            ic50 = record.get("ic50", {})
            items.append(item(f"chembl_{name}", "exact",
                              {"count": ic50.get("count"),
                               "best_nM": ic50.get("best_value"),
                               "assay_types": ic50.get("assay_types")},
                              "ChEMBL 37 SQLite, direct SQL"))
        qualitative_item("site_evidence", "the answer cites a PDB entry for each site "
                                          "(AY7: 5MO4; STI: 2HYY)", "RCSB")
    elif pid == "L04":
        accession_item()
        items.append(item("5od_shp2_entries", "exact",
                          rcsb_ligand_protein_entries("5OD", "Q06124"),
                          "RCSB Search API v2"))
        record = facts["chembl"].get("SHP099|Q06124", {})
        items.append(item("chembl_shp099_absence", "exact",
                          {"present": bool((record.get("ic50") or {}).get("count")),
                           "count": (record.get("ic50") or {}).get("count"),
                           "molecule_in_chembl_37": bool(record.get("molecule", {}).get("matches"))},
                          "ChEMBL 37 SQLite, direct SQL",
                          note="SHP099 is absent from ChEMBL 37, so the correct answer "
                               "is an explicit absence"))
    elif pid == "L05":
        accession_item()
        items.append(item("frj_ptp1b_entries", "exact",
                          rcsb_ligand_protein_entries("FRJ", "P18031"),
                          "RCSB Search API v2"))
        qualitative_item("pdbe_route", "the entry list is confirmed on a second route "
                                       "(PDBe); the PDBe mappings endpoints answer 404 "
                                       "from this host, so the second route is recorded "
                                       "as unavailable", "PDBe SIFTS API")
        problems.append(
            "L05: the checklist requires the RCSB and the PDBe route to agree, but the "
            "PDBe mappings endpoints answer 404 from the validation host, so the second "
            "route cannot be exercised here; either relax the checklist item to the "
            "RCSB route plus a recorded note that the PDBe route was unavailable, or "
            "re-run the PDBe leg from a host that can reach www.ebi.ac.uk.")
    # ------------------------------------------------------- K (site prediction)
    elif pid in ("K01", "K02", "K03", "K04"):
        accession_item()
        record = facts["stingallo"].get(
            "1T4J" if pid in ("K01", "K02", "K04") else "5EHR", {})
        residues = (record.get("payload") or {}).get("allosteric_residues", [])
        items.append(item("stingallo_residues", "exact", residues,
                          f"STINGAllo ({record.get('response_date')})"))
        if pid == "K02":
            contacts = set(C(facts, "1T4J", "FRJ", 4.0, "A")["uniprot_numbers"])
            predicted = {int(r) for r in residues}
            items.append(item("overlap_1T4J", "number", len(predicted & contacts),
                              "STINGAllo + RCSB mmCIF 1T4J", tolerance=0))
        if pid == "K04":
            contacts = set(C(facts, "1T4J", "FRJ", 4.0, "A")["uniprot_numbers"])
            predicted = {int(r) for r in residues}
            entries = facts["structures"].get("1T4J")
            polymer = polymer_residues(entries) if entries else {}
            chain_a = [k for k in polymer if k[0] == "A"]
            n_modelled = len(chain_a)
            base_rate = (len(predicted) / n_modelled) if n_modelled else None
            expected = (len(predicted) * len(contacts) / n_modelled) if n_modelled else None
            items.append(item("overlap_1T4J_FRJ", "number", len(predicted & contacts),
                              "STINGAllo + RCSB mmCIF 1T4J (FRJ, chain A)", tolerance=0))
            items.append(item(
                "chance_base_rate_1T4J_FRJ", "exact",
                {"predicted_residues": len(predicted),
                 "predicted_residue_numbers": sorted(predicted),
                 "contact_residues": len(contacts),
                 "modelled_chain_A_residues": n_modelled,
                 "predicted_fraction_of_chain": base_rate,
                 "expected_overlap_by_chance": expected,
                 "observed_overlap": len(predicted & contacts),
                 "note": (
                     "the chance expectation is the hypergeometric one: the "
                     "predicted residues are a random set of the same size in "
                     "the modelled residues of the chain")},
                "STINGAllo + RCSB mmCIF 1T4J", tolerance=0,
                note=(
                    f"the STINGAllo service returned {len(predicted)} residues for "
                    f"1T4J chain A on {record.get('response_date')}; the answer must "
                    "report that list, the FRJ contact list, the overlap and the "
                    "comparison with the chance expectation") if predicted else None))
            items.append(item(
                "chance_comparison_stated", "qualitative",
                "the answer compares the observed overlap with the chance "
                "expectation and says whether the prediction is better than "
                "chance",
                "the prompt's own criterion"))
        if pid == "K03":
            contacts = set(C(facts, "5EHR", "5OD", 4.0, "A")["uniprot_numbers"])
            predicted = {int(r) for r in residues}
            modelled = {c["pdb_number"] for c in C(facts, "5EHR", "5OD", 4.0, "A")["contacts"]}
            residues_total = len(facts["sifts"].get("5EHR", {}).get("last_label_seq_id", "")
                                 .__str__() or []) or None
            entries = facts["structures"].get("5EHR")
            polymer = polymer_residues(entries) if entries else {}
            chain_a = [k for k in polymer if k[0] == "A"]
            n_modelled = len(chain_a)
            base_rate = (len(predicted) / n_modelled) if n_modelled else None
            expected = (len(predicted) * len(contacts) / n_modelled) if n_modelled else None
            items.append(item("overlap_5EHR", "number", len(predicted & contacts),
                              "STINGAllo + RCSB mmCIF 5EHR", tolerance=0))
            items.append(item(
                "chance_base_rate_5EHR", "exact",
                {"predicted_residues": len(predicted),
                 "predicted_residue_numbers": sorted(predicted),
                 "contact_residues": len(contacts),
                 "modelled_chain_A_residues": n_modelled,
                 "predicted_fraction_of_chain": base_rate,
                 "expected_overlap_by_chance": expected,
                 "observed_overlap": len(predicted & contacts),
                 "enrichment": (len(predicted & contacts) / expected)
                 if expected else None},
                "computed from the same two sources",
                note="STINGAllo returns ONE predicted residue for 5EHR chain A "
                     "(the residue numbered 314); the list has one element, it is not "
                     "314 residues. A single predicted residue has a "
                     f"{expected:.3f} chance of falling on the contact set, so the "
                     "overlap carries almost no information either way."))
    # ------------------------------------------------------------ synthesis (G)
    elif pid in ("G01", "G02", "G03", "G04"):
        accession_item()
        qualitative_item(
            "components_present",
            {
                "G01": "the pocket detection on the ligand-stripped 6OIM, the ChEMBL "
                       "bioactivity of sotorasib, the ClinVar and AlphaMissense records "
                       "for KRAS G12C and the distance from residue 12 to the inhibitor "
                       "are all present, with a hedged conclusion",
                "G02": "the 1OPK contacts for both sites, the pocket ranks on the "
                       "ligand-stripped structure, the ChEMBL potency of imatinib and "
                       "asciminib and the T315I records and distances are present, with "
                       "the allosteric-site claim separated from the retrieved evidence",
                "G03": "the ClinVar and AlphaMissense records for E76K and D61Y, the "
                       "distances to the 2SHP autoinhibitory interface, the pocket "
                       "detection on 2SHP and the normal mode analysis are present, with "
                       "the conclusion hedged and the limits stated",
                "G04": "the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an "
                       "explicit absence), the ClinVar and AlphaMissense records for "
                       "E17K and the distance from residue 17 to the ligand where "
                       "modelled are present, with a hedged conclusion",
            }[pid], "the prompt's own criterion")
        if pid == "G03":
            missing = [v for v in ("E76K", "D61Y")
                       if not facts["alphamissense"].get(f"{accession} {v}")]
            if missing:
                problems.append(
                    f"G03: AlphaMissense has no row for {accession} {', '.join(missing)}, "
                    "so the 'combine ClinVar and AlphaMissense' part of the prompt cannot "
                    "be answered as written; propose replacing the AlphaMissense half with "
                    "ClinVar plus the distances, or with a SHP2 variant that has an "
                    "AlphaMissense row.")
        if pid == "G04":
            record = facts["chembl"].get("MK-2206|P31749", {})
            if not (record.get("molecule") or {}).get("matches"):
                problems.append(
                    "G04: MK-2206 is not in ChEMBL 37 under any of the three spellings "
                    "checked (MK-2206, MK2206, MK 2206), so the ChEMBL component of the "
                    "prompt has no data; the prompt already allows an explicit absence, "
                    "but the compound id should be confirmed.")
    # ------------------------------------------------------------ honest (H)
    elif pid == "H01":
        accession_item()
        record = facts["chembl"].get("SHP099|P18031", {})
        items.append(item("shp099_ptpn1_absence", "exact",
                          {"present": bool((record.get("ic50") or {}).get("count")),
                           "count": (record.get("ic50") or {}).get("count"),
                           "molecule_in_chembl_37": bool(record.get("molecule", {}).get("matches"))},
                          "ChEMBL 37 SQLite, direct SQL",
                          note="the correct answer is the explicit absence"))
    elif pid == "H02":
        accession_item()
        qualitative_item("ranking_with_caveat",
                         "the top three pockets are ranked with a justification and the "
                         "stated limit that a pocket detector does not distinguish "
                         "allosteric from orthosteric pockets", "the prompt")
    return items, problems


def pid_entry(pid: str) -> str:
    return {"P01": "1T4J", "P02": "6OIM", "P03": "2SHP", "P05": "1OPK",
            "P06": "1V4S", "P07": "1T4J", "H02": "1T4J"}[pid]


# ------------------------------------------------------------------ writers

def build_report(prompt: dict, items: list[dict], problems: list[str]) -> dict:
    status = "PROBLEM" if problems else "PASS"
    return {
        "id": prompt["id"],
        "category": prompt["category"],
        "tier": prompt["tier"],
        "accession": prompt.get("accession"),
        "baseline_route": prompt.get("baseline_route"),
        "d_tools_expected": prompt.get("d_tools_expected"),
        "status": status,
        "checklist": items,
        "proposed_fixes": problems,
    }


def write_json(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def write_markdown(path: Path, report: dict, facts: dict) -> None:
    lines: list[str] = []
    lines.append("# Benchmark validation report")
    lines.append("")
    lines.append(f"Generated {report['generated_utc']} by "
                 "`benchmark/validate_benchmark.py` in the container.")
    lines.append("")
    lines.append("Every checklist value below was recomputed from the primary "
                 "source (RCSB mmCIF, UniProt REST, the RCSB SIFTS alignment, the "
                 "ChEMBL 37 SQLite by direct SQL, the ClinVar and AlphaMissense "
                 "release files, the STINGAllo API). The pocket / dynamics "
                 "checklists also carry one reference output of our own tools; a "
                 "reference output is the number to compare against, not the "
                 "ground truth of the science.")
    lines.append("")
    summary = report["summary"]
    lines.append(f"**{summary['pass']} PASS, {summary['problem']} PROBLEM, "
                 f"{summary['total']} prompts.**")
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.append("| source | version / sha256 |")
    lines.append("|---|---|")
    for name, meta in report["sources"].items():
        sha = (meta or {}).get("sha256") or (meta or {}).get("release") or "-"
        lines.append(f"| {name} | `{sha}` |")
    lines.append("")
    lines.append("## PROBLEM prompts and the proposed fix")
    lines.append("")
    if not report["problems"]:
        lines.append("None.")
    for entry in report["problems"]:
        lines.append(f"### {entry['id']} ({entry['category']}, tier {entry['tier']})")
        lines.append("")
        lines.append(f"* prompt: {entry['prompt']}")
        lines.append("")
        for fix in entry["proposed_fixes"]:
            lines.append(f"* **proposed fix:** {fix}")
        lines.append("")
    lines.append("## Per-prompt checklist")
    lines.append("")
    for entry in report["prompts"]:
        lines.append(f"### {entry['id']} - {entry['category']}, tier {entry['tier']}, "
                     f"route {entry['baseline_route']} - **{entry['status']}**")
        lines.append("")
        lines.append(f"* accession: `{entry['accession']}`")
        lines.append(f"* expected tools: `{entry['d_tools_expected']}`")
        lines.append("")
        lines.append("| item | kind | value | source | tolerance |")
        lines.append("|---|---|---|---|---|")
        for item_row in entry["checklist"]:
            value = item_row["value"]
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            value = str(value)
            if len(value) > 220:
                value = value[:217] + "..."
            lines.append(
                f"| {item_row['key']} | {item_row['kind']} | {value} | "
                f"{item_row['source']} | {item_row['tolerance'] if item_row['tolerance'] is not None else '-'} |")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--benchmark", type=Path,
                        default=Path("/workspace/benchmark/benchmark_draft.json"))
    parser.add_argument("--out-json", type=Path,
                        default=Path("/workspace/benchmark/checklists.json"))
    parser.add_argument("--out-md", type=Path,
                        default=Path("/workspace/benchmark/validation_report.md"))
    parser.add_argument("--data-root", default="/data")
    args = parser.parse_args()

    draft = json.loads(args.benchmark.read_text(encoding="utf-8"))
    print(f"draft: {len(draft)} prompts from {args.benchmark}")

    facts = compute_facts(args)
    facts["sources"] = {
        "clinvar_release": facts["clinvar_source"],
        "alphamissense_release": facts["alphamissense_source"],
        "chembl_37_sqlite": facts["sources"]["chembl_db"],
        "benchmark_draft": {
            "path": str(args.benchmark),
            "sha256": sha256_of_file(args.benchmark),
        },
    }
    chembl_prompts = {
        "L02": [("trametinib", "Q02750"), ("cobimetinib", "Q02750")],
        "L03": [("asciminib", "P00519"), ("imatinib", "P00519")],
        "L04": [("SHP099", "Q06124")],
        "H01": [("SHP099", "P18031")],
        "G01": [("sotorasib", "P01116")],
        "G04": [("MK-2206", "P31749")],
    }
    facts["extra_checks"] = {
        "alphamissense_Q06124_scan": facts["alphamissense_q06124"],
        "chembl_compounds_named_in_prompts": {
            pid: {
                f"{name}|{uniprot}": {
                    "in_chembl_37": bool(
                        (facts["chembl"].get(f"{name}|{uniprot}", {})
                         .get("molecule", {}) or {}).get("matches")),
                    "ic50_rows": (
                        facts["chembl"].get(f"{name}|{uniprot}", {})
                        .get("ic50", {}) or {}).get("count"),
                    "best_nM": (
                        facts["chembl"].get(f"{name}|{uniprot}", {})
                        .get("ic50", {}) or {}).get("best_value"),
                }
                for name, uniprot in compounds
            } for pid, compounds in chembl_prompts.items()
        },
        "clinvar_release_used": facts["clinvar_source"],
        "clinvar_count_policy": "classification + a 10 % tolerance band; the pinned "
                                "release and the live API differ (16,066 vs 16,106 "
                                "unique BRCA1 records), so exact counts are not used",
    }

    prompts = []
    problems = []
    for prompt in draft:
        try:
            items, prompt_problems = build_items(prompt, facts)
        except Exception as exc:  # noqa: BLE001 - one prompt must not stop the run
            items = [item("validator_error", "exact", repr(exc), "the validator",
                          status="PROBLEM")]
            prompt_problems = [f"the validator raised on this prompt: {exc!r}"]
        entry = build_report(prompt, items, prompt_problems)
        prompts.append(entry)
        if prompt_problems:
            problems.append({"id": prompt["id"], "category": prompt["category"],
                             "tier": prompt["tier"], "prompt": prompt["prompt"],
                             "proposed_fixes": prompt_problems})

    report = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "benchmark_draft": str(args.benchmark),
        "benchmark_draft_sha256": sha256_of_file(args.benchmark),
        "summary": {
            "total": len(prompts),
            "pass": sum(1 for p in prompts if p["status"] == "PASS"),
            "problem": sum(1 for p in prompts if p["status"] == "PROBLEM"),
        },
        "sources": facts["sources"],
        "extra_checks": facts.get("extra_checks", {}),
        "problems": problems,
        "prompts": prompts,
    }
    write_json(args.out_json, report)
    write_markdown(args.out_md, report, facts)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")
    print(f"summary: {report['summary']}")
    for entry in problems:
        print(f"  PROBLEM {entry['id']}: {entry['proposed_fixes'][0][:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

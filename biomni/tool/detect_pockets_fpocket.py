"""T4 detect_pockets_fpocket (Part 2).

Wrapper around fpocket 4.2.3 (Discngine). fpocket is a C executable
that takes a PDB or mmCIF file, runs a Voronoi tessellation of the
heavy-atom solvent-accessible surface, and writes its output to
`<basename>_out/` next to the input file (the `-o` flag is IGNORED
by fpocket 4.2.3 -- the directory is always derived from the input
file's basename).

The tool strips HETATM records from the input by default (writes a
working copy without HETATM lines) and parses
`<basename>_out/<basename>_info.txt`, which lists one pocket per
Pocket N block with its `Score` and `Druggability Score`. The parser
handles negative `Druggability Score` values (e.g. `-0.010`).

fpocket finds pockets that bind small molecules. It does NOT
distinguish allosteric from orthosteric sites; see the tool card for
the full caveat.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 120
_HETATM_LINE_RE = re.compile(r"^(?:HETATM|HET\s)")
_SIFTS_TIMEOUT_S = 30
_PDBE_MAPPINGS = "https://www.ebi.ac.uk/pdbe/api/mappings/uniprot"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "fpocket 4.2.3 (https://github.com/Discngine/fpocket)"


def _strip_hetatm(pdb_path: Path, dest_path: Path) -> int:
    """Copy `pdb_path` to `dest_path` dropping HETATM/HET lines.
    Returns the number of lines written.
    """
    written = 0
    with open(pdb_path, "r", encoding="utf-8", errors="replace") as src, open(
        dest_path, "w", encoding="utf-8"
    ) as dst:
        for line in src:
            if _HETATM_LINE_RE.match(line):
                continue
            dst.write(line)
            written += 1
    return written


def _parse_info_txt(info_txt: Path) -> list[dict[str, Any]]:
    """Parse fpocket's `<basename>_info.txt` into a list of pocket dicts.

    Each Pocket N block contains a fixed set of key/value lines,
    with values indented after a tab. The parser is robust to
    negative `Druggability Score` values (e.g. `-0.010`) and to
    integer-or-float values.
    """
    pockets: list[dict[str, Any]] = []
    if not info_txt.is_file():
        return pockets

    current: dict[str, Any] | None = None
    kv_re = re.compile(r"^\s*(Pocket\s+\d+)\s*:\s*$")
    score_re = re.compile(r"^\s*([A-Za-z][A-Za-z .]+?)\s*:\s*(.*)$")
    int_re = re.compile(r"^\s*(-?\d+)\s*$")
    float_re = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*$")

    with open(info_txt, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = kv_re.match(line)
            if m:
                if current is not None:
                    pockets.append(current)
                current = {"pocket_number": len(pockets) + 1}
                continue
            if current is None:
                continue
            sm = score_re.match(line)
            if sm:
                key = sm.group(1).strip().lower().replace(" ", "_")
                raw = sm.group(2).strip()
                if not raw:
                    current[key] = None
                    continue
                im = int_re.match(raw)
                if im:
                    current[key] = int(im.group(1))
                    continue
                fm = float_re.match(raw)
                if fm:
                    current[key] = float(fm.group(1))
                    continue
                current[key] = None
    if current is not None:
        pockets.append(current)
    return pockets


def _fpocket_output_dir(input_path: Path) -> Path:
    """fpocket writes to `<basename>_out/` next to the input file.
    The `-o` flag is IGNORED -- this is documented fpocket
    behaviour.
    """
    return input_path.parent / (input_path.stem + "_out")


def _parse_pocket_atoms(pocket_pdb: Path) -> list[dict[str, Any]]:
    """Parse one `pockets/pocketN_atm.pdb` into its distinct residues.

    The PDB columns are used, not whitespace splitting: 18-20 the
    residue name, 22 the chain id, 23-26 the residue number.
    """
    residues: dict[tuple[str, int], str] = {}
    if not pocket_pdb.is_file():
        return []
    with open(pocket_pdb, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("ATOM") or len(line) < 27:
                continue
            residue_name = line[17:20].strip()
            chain = line[21].strip()
            try:
                residue_number = int(line[22:26].strip())
            except ValueError:
                continue
            if not residue_name:
                continue
            residues.setdefault((chain, residue_number), residue_name)
    return [
        {"chain": chain, "residue_number": number, "residue_name": name}
        for (chain, number), name in sorted(
            residues.items(), key=lambda item: (item[0][0], item[0][1])
        )
    ]


def _pdb_id_from_file(path: Path) -> str | None:
    """The PDB id of a structure file.

    The HEADER record of an RCSB PDB file carries the id in columns
    63-66; the file stem is used as a fallback when it looks like a
    PDB id.  ``None`` means the id could not be established, and the
    UniProt numbers are then left empty rather than guessed.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for _ in range(100):
                line = handle.readline()
                if not line:
                    break
                if line.startswith("HEADER"):
                    candidate = line[62:66].strip().upper()
                    if re.fullmatch(r"[0-9][A-Z0-9]{3}", candidate):
                        return candidate
                    break
    except OSError:
        return None
    stem = path.stem.strip().upper()
    if re.fullmatch(r"[0-9][A-Z0-9]{3}", stem):
        return stem
    return None


def _uniprot_offsets(pdb_id: str) -> list[dict[str, Any]]:
    """The per-chain author-number -> UniProt-number offsets.

    From the PDBe mappings API (the source `map_residues_uniprot_pdb`
    uses).  An empty list means the mapping is not available; the
    caller then leaves the UniProt fields empty rather than guessing.
    """
    try:
        import requests

        response = requests.get(
            f"{_PDBE_MAPPINGS}/{pdb_id.upper()}", timeout=_SIFTS_TIMEOUT_S
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:  # noqa: BLE001 - the mapping is optional
        return []
    offsets: list[dict[str, Any]] = []
    block = payload.get(pdb_id.lower()) or {}
    uniprot_block = block.get("UniProt") or block
    for accession, entry in uniprot_block.items():
        if not isinstance(entry, dict):
            continue
        for mapping in entry.get("mappings", []) or []:
            start = (mapping.get("start") or {}).get("author_residue_number")
            end = (mapping.get("end") or {}).get("author_residue_number")
            if end is None:
                end = (mapping.get("end") or {}).get("residue_number")
            unp_start = mapping.get("unp_start")
            unp_end = mapping.get("unp_end")
            chain = mapping.get("chain_id")
            if start is None or unp_start is None or chain is None:
                continue
            try:
                start_number = int(start)
                unp_start_number = int(unp_start)
                end_number = int(end) if end is not None else start_number
                unp_end_number = int(unp_end) if unp_end is not None else unp_start_number
            except (TypeError, ValueError):
                continue
            offsets.append(
                {
                    "chain": str(chain),
                    "accession": str(accession),
                    "offset": unp_start_number - start_number,
                    "author_start": start_number,
                    "author_end": end_number,
                    "uniprot_start": unp_start_number,
                    "uniprot_end": unp_end_number,
                }
            )
    return offsets


def _uniprot_for_residue(
    residue: dict[str, Any], offsets: list[dict[str, Any]]
) -> tuple[str | None, int | None]:
    """The UniProt accession and number of one pocket residue."""
    number = residue["residue_number"]
    for offset in offsets:
        if offset["chain"] != residue["chain"]:
            continue
        if not (offset["author_start"] <= number <= offset["author_end"]):
            continue
        return offset["accession"], number + offset["offset"]
    return None, None


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def detect_pockets_fpocket(pdb_path, strip_hetatm: bool = True):
    """Run fpocket 4.2.3 on a PDB file and return the predicted pockets.

    Parameters
    ----------
    pdb_path : str or Path
        Path to a PDB file. mmCIF input is accepted by fpocket; the
        output directory will use the file stem.
    strip_hetatm : bool, default True
        When True, write a working copy of the input without HETATM
        records before calling fpocket.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "pdb_id": <file stem>,
                "pockets": [
                    {"pocket_number": <int>, "score": <float>,
                     "druggability_score": <float>,
                     "residues": [
                         {"chain": <str>, "residue_number": <int>,
                          "residue_name": <str>,
                          "uniprot_accession": <str or None>,
                          "uniprot_number": <int or None>},
                         ...],
                     ...},
                    ...
                ]
            }

        The residues of a pocket are parsed from fpocket's own
        `pockets/pocketN_atm.pdb`; the UniProt numbers come from the
        PDBe mappings API and are ``None`` when the mapping is not
        available.
    """
    src = Path(pdb_path)
    if not src.is_file():
        return {
            "success": False,
            "data": None,
            "error": f"PDB path does not exist: {src}",
        }
    pdb_id = _pdb_id_from_file(src)

    if shutil.which("fpocket") is None:
        return {
            "success": False,
            "data": None,
            "error": "fpocket binary not found on PATH",
        }

    tmp_dir: tempfile.TemporaryDirectory | None = None
    try:
        if strip_hetatm:
            tmp_dir = tempfile.TemporaryDirectory(
                prefix="alloagent_fpocket_", dir="/tmp"
            )
            work_in = Path(tmp_dir.name) / src.name
            _strip_hetatm(src, work_in)
        else:
            work_in = src

        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                ["fpocket", "-f", str(work_in)],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "data": None,
                "error": f"fpocket timed out after {_TIMEOUT_S}s",
            }
        runtime_s = time.perf_counter() - t0

        out_dir = _fpocket_output_dir(work_in)
        info_txt = out_dir / (work_in.stem + "_info.txt")
        pockets = _parse_info_txt(info_txt) if info_txt.is_file() else []

        offsets = _uniprot_offsets(pdb_id) if pdb_id else []
        for pocket in pockets:
            number = pocket.get("pocket_number")
            residues = _parse_pocket_atoms(
                out_dir / "pockets" / f"pocket{number}_atm.pdb"
            )
            for residue in residues:
                accession, uniprot_number = _uniprot_for_residue(residue, offsets)
                residue["uniprot_accession"] = accession
                residue["uniprot_number"] = uniprot_number
            pocket["residues"] = residues

        return {
            "success": True,
            "data": {
                "pdb_id": src.stem,
                "pockets": pockets,
                "runtime_s": round(runtime_s, 3),
                "fpocket_exit_code": proc.returncode,
            },
        }
    finally:
        if tmp_dir is not None:
            tmp_dir.cleanup()
"""P32 allosteric_site_workflow: one call, one structured report.

Runs the ligand-contact analysis, the two pocket detectors (on a
ligand-stripped copy), PocketMiner, the normal-mode analysis and the
residue contact network of one structure, and reports the overlap of
the pocket components with the known-site contacts.  Every component is
the direct call of the underlying tool - the workflow calls the tools,
it does not re-implement them.

The scope statement: the report says which residues are near a ligand and
which pockets the detectors call; it does **not** say that a pocket is an
allosteric site, and it does not report a binding energy.
"""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

import requests

from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 900
_PDB_URL = "https://files.rcsb.org/download/{pdb_id}.pdb"
_CIF_URL = "https://files.rcsb.org/download/{pdb_id}.cif"

_RESIDUE_NUMBER_KEYS = (
    "residue_number",
    "residue_label",
    "residue_number_label",
    "residue_id",
    "number",
)


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "allosteric_site_workflow (the tools it calls)"


def _pocket_residue_numbers(pocket: dict) -> set[tuple[str, int]]:
    """The (chain, residue number) pairs of one pocket, whatever the
    pocket detector called the fields."""
    out: set[tuple[str, int]] = set()
    for residue in pocket.get("residues") or []:
        if not isinstance(residue, dict):
            continue
        number = None
        for key in _RESIDUE_NUMBER_KEYS:
            if residue.get(key) is not None:
                number = residue.get(key)
                break
        if number is None:
            continue
        try:
            number = int(str(number).strip())
        except ValueError:
            continue
        chain = str(residue.get("chain") or "").strip()
        out.add((chain, number))
    return out


def _download(url: str, target: Path) -> Path:
    response = requests.get(url, timeout=_TIMEOUT_S)
    if response.status_code != 200:
        raise RuntimeError(f"download failed for {url} with status {response.status_code}")
    target.write_text(response.text, encoding="utf-8")
    return target


def _strip_ligands(pdb_text: str) -> str:
    """The ATOM records only: the ligand-free copy for the detectors."""
    return "\n".join(
        line for line in pdb_text.splitlines() if not line.startswith("HETATM")
    ) + "\n"


@with_return_contract(source_version="1.0")
def allosteric_site_workflow(
    pdb_id: str,
    chain: str,
    ligand_id: Optional[str] = None,
    run_stingallo: bool = False,
):
    """Run the allosteric-site analyses of one structure and report them together.

    Parameters
    ----------
    pdb_id : str
        4-character PDB entry id (e.g. ``"1T4J"``).
    chain : str
        Chain id to analyse (e.g. ``"A"``).
    ligand_id : str or None
        RCSB chemical component id of the bound ligand.  When given, the
        ligand contacts are computed and the pocket components are
        compared with them.
    run_stingallo : bool
        Also call the STINGAllo prediction service for the structure.

    Returns
    -------
    dict
        Contract dict. ``data`` has one entry per component
        (``ligand_contacts``, ``fpocket``, ``p2rank``, ``pocketminer``,
        ``normal_modes``, ``contact_network``, ``stingallo``) and an
        ``overlap`` block.  Each component is the direct call of the
        corresponding tool, so a component that failed carries its own
        error and the rest of the report is still produced.
    """
    if not isinstance(pdb_id, str) or not pdb_id.strip():
        return {"success": False, "error": f"pdb_id must be a non-empty string, got {pdb_id!r}"}
    if not isinstance(chain, str) or not chain.strip():
        return {"success": False, "error": f"chain must be a non-empty string, got {chain!r}"}
    pdb_id = pdb_id.strip().upper()
    chain = chain.strip()

    report: dict[str, Any] = {
        "pdb_id": pdb_id,
        "chain": chain,
        "ligand_id": ligand_id.upper() if isinstance(ligand_id, str) and ligand_id else None,
        "components": {},
    }

    work = Path(tempfile.mkdtemp(prefix="allosteric_workflow_"))
    try:
        pdb_path = _download(_PDB_URL.format(pdb_id=pdb_id), work / f"{pdb_id}.pdb")
        stripped_path = work / f"{pdb_id}_ligand_free.pdb"
        stripped_path.write_text(_strip_ligands(pdb_path.read_text(encoding="utf-8")),
                                 encoding="utf-8")
        cif_path = _download(_CIF_URL.format(pdb_id=pdb_id), work / f"{pdb_id}.cif")

        contact_residues: set[tuple[str, int]] = set()
        if report["ligand_id"]:
            from biomni.tool.get_ligand_contacts import get_ligand_contacts

            contacts = get_ligand_contacts(
                pdb_id=pdb_id, ligand_id=report["ligand_id"], chain=chain)
            report["components"]["ligand_contacts"] = contacts
            for contact in (contacts.get("data") or {}).get("contacts") or []:
                contact_residues.add((str(contact.get("chain")), int(contact.get("pdb_number"))))

        from biomni.tool.detect_pockets_fpocket import detect_pockets_fpocket
        from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

        report["components"]["fpocket"] = detect_pockets_fpocket(pdb_path=str(stripped_path))
        report["components"]["p2rank"] = detect_pockets_p2rank(pdb_path=str(stripped_path))

        from biomni.tool.pocketminer import pocketminer_score

        report["components"]["pocketminer"] = pocketminer_score(pdb_path=str(pdb_path))

        from biomni.tool.normal_mode_analysis import normal_mode_analysis

        report["components"]["normal_modes"] = normal_mode_analysis(pdb_id=pdb_id)

        from biomni.tool.residue_contact_network import residue_contact_network

        report["components"]["contact_network"] = residue_contact_network(
            mmcif_path=str(cif_path))

        if run_stingallo:
            from biomni.tool.get_stingallo_allosteric_residues import (
                get_stingallo_allosteric_residues,
            )

            report["components"]["stingallo"] = get_stingallo_allosteric_residues(
                pdb_id=pdb_id, chain_id=chain)

        overlap: dict[str, Any] = {"known_site_residues": sorted(
            [chain, number] for chain, number in contact_residues)}
        for name in ("fpocket", "p2rank"):
            component = report["components"].get(name) or {}
            data = component.get("data") or {}
            per_pocket = []
            for pocket in data.get("pockets") or []:
                numbers = _pocket_residue_numbers(pocket)
                shared = sorted(numbers & contact_residues)
                per_pocket.append({
                    "pocket_number": pocket.get("pocket_number"),
                    "score": pocket.get("score"),
                    "n_residues": len(numbers),
                    "n_shared_with_the_known_site": len(shared),
                    "shared_residues": [f"{chain}:{number}" for chain, number in shared],
                })
            overlap[name] = per_pocket
            overlap[f"{name}_best_overlap"] = max(
                (pocket["n_shared_with_the_known_site"] for pocket in per_pocket),
                default=0)
        report["overlap"] = overlap
    except Exception as exc:  # noqa: BLE001 - the report says what failed
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        import shutil

        shutil.rmtree(work, ignore_errors=True)

    return {"success": True, "data": report}

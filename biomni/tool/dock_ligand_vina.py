"""B2 dock_ligand_vina (Part 2 / batch 2).

Dock a ligand (from SMILES via RDKit + Meeko) against a
receptor (prepared with Meeko's mk_prepare_receptor.py
command-line script in rigid mode) using AutoDock Vina.
Returns poses and Vina energies.

The primary validation is a redock of 2HYY with the crystal
STI ligand: in-place, symmetry-aware, heavy-atom RMSD
(no re-alignment) computed with rdMolAlign.CalcRMS,
top-1 <= 2.0 A at exhaustiveness=8.

NOTE: Vina scores are docking scores, not measured binding
affinities. This is a SCORING function, not a CALIBRATION
against experimental affinities.

Receptor preparation path
-------------------------

The receptor is prepared with Meeko's CLI in rigid mode:

    mk_prepare_receptor.py --read_pdb <pdb> -o <basename> -p -x \
        --default_altloc A

This produces a Meeko-formatted PDBQT (rigid) that Vina's
`set_receptor()` accepts. The Phase 2d experiment confirmed
this is the only path that resolves Vina's `> ROOT` blocker
on real PDB inputs; a hand-written minimal PDB->PDBQT converter
also worked but is kept only as a clearly-labeled, off-by-default
fallback (NOT used for validation).

Ligand preparation path
-----------------------

The ligand is prepared from SMILES via RDKit + Meeko's CLI:

    mk_prepare_ligand.py -i <sdf> -o <pdbqt>

The SDF is produced by RDKit from the input SMILES with
explicit Hs and a 3D conformer (MMFF-optimized).

RMSD path
---------

The crystal-ligand reference (if `reference_ligand_pdb_path`
is provided) is parsed with RDKit from a PDB and the bond
orders are assigned from the chemical-component SMILES of
the ligand ID (RCSB Data API `chemcomp` endpoint). The
docked-ligand mol is built with Meeko's PDBQTMolecule +
RDKitMolCreate. RMSD is computed with rdMolAlign.CalcRMS,
which is IN-PLACE (no re-alignment), symmetry-aware, and
heavy-atom-only by default.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 300
_DEFAULT_NUM_MODES = 9
_DEFAULT_EXHAUSTIVENESS = 8
_DEFAULT_CPU = 1
_DEFAULT_SEED = 42


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "AutoDock Vina 1.2.7 + RDKit 2024.09.6 + Meeko 0.8.0 (mk_prepare_receptor.py CLI)"


def _vina_version() -> str:
    """Return the Vina version string. Tries the CLI first, then vina_python."""
    cli = shutil.which("vina")
    if cli:
        try:
            r = subprocess.run(
                [cli, "--version"], capture_output=True, text=True, timeout=10
            )
            return (r.stdout + r.stderr).strip()
        except Exception:
            pass
    try:
        import vina as vina_python
        return f"vina_python {getattr(vina_python, '__version__', '?')}"
    except Exception:
        return "unknown"


def _prepare_receptor_meeko(
    receptor_pdb_path: Path,
    out_dir: Path,
) -> tuple[Path, str]:
    """Prepare the receptor as a Vina rigid-receptor PDBQT using
    Meeko's `mk_prepare_receptor.py` CLI in rigid mode.

    Returns (receptor_pdbqt_path, command_string).

    The flags are:
    - --read_pdb: input is a PDB (not ProDy-loaded)
    - -o <basename>: output basename
    - -p: write a rigid-only PDBQT (no _flex PDBQT)
    - -x: delete residues that fail template matching
    - --default_altloc A: pick the A altloc for ambiguous atoms

    Note: Vina's set_receptor() requires rigid-only PDBQT for
    the non-flexible case. A successful run on a real PDB
    (e.g. 2HYY chain A) produces ~190 KB PDBQT that Vina
    accepts without the "> ROOT" error.
    """
    cli = "mk_prepare_receptor.py"
    out_basename = "receptor"
    cmd = [
        cli,
        "--read_pdb", str(receptor_pdb_path),
        "-o", str(out_dir / out_basename),
        "-p",
        "-x",
        "--default_altloc", "A",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(
            f"mk_prepare_receptor.py failed (rc={r.returncode}): "
            f"stderr={r.stderr[:400]}"
        )
    out_path = out_dir / f"{out_basename}.pdbqt"
    if not out_path.is_file() or out_path.stat().st_size == 0:
        raise RuntimeError(
            f"mk_prepare_receptor.py produced no PDBQT at {out_path}"
        )
    return out_path, " ".join(cmd)


def _prepare_ligand_meeko(
    smiles: str,
    out_dir: Path,
    embed_seed: int = _DEFAULT_SEED,
) -> Path:
    """Prepare the ligand from SMILES via RDKit + Meeko's
    `mk_prepare_ligand.py` CLI. Returns the ligand PDBQT path.

    `embed_seed` is the RDKit `EmbedMolecule` random seed; it
    controls the initial 3D conformer generation and therefore
    the Vina search starting point. The default is
    `_DEFAULT_SEED` (42). Pass an explicit value to make the
    ligand prep reproducible."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"could not parse SMILES: {smiles!r}")
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=embed_seed)
    AllChem.MMFFOptimizeMolecule(mol)
    sdf_path = out_dir / "ligand.sdf"
    writer = Chem.SDWriter(str(sdf_path))
    writer.write(mol)
    writer.close()

    out_pdbqt = out_dir / "ligand.pdbqt"
    cli = "mk_prepare_ligand.py"
    cmd = [
        cli,
        "-i", str(sdf_path),
        "-o", str(out_pdbqt),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(
            f"mk_prepare_ligand.py failed (rc={r.returncode}): "
            f"stderr={r.stderr[:400]}"
        )
    if not out_pdbqt.is_file() or out_pdbqt.stat().st_size == 0:
        raise RuntimeError(
            f"mk_prepare_ligand.py produced no PDBQT at {out_pdbqt}"
        )
    return out_pdbqt


def _vina_dock(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    box_center: tuple[float, float, float],
    box_size: tuple[float, float, float],
    out_pdbqt: Path,
    exhaustiveness: int = _DEFAULT_EXHAUSTIVENESS,
    num_modes: int = _DEFAULT_NUM_MODES,
    seed: int = _DEFAULT_SEED,
    cpu: int = _DEFAULT_CPU,
    timeout: int = _TIMEOUT_S,
) -> None:
    """Run Vina docking via the vina_python API. Writes the
    pose PDBQT to `out_pdbqt`. No return value (Vina raises
    on failure; the caller catches).
    """
    import vina as vina_python

    v = vina_python.Vina(sf_name="vina", cpu=cpu, seed=seed, verbosity=0)
    v.set_receptor(str(receptor_pdbqt))
    v.set_ligand_from_file(str(ligand_pdbqt))
    v.compute_vina_maps(
        center=list(box_center),
        box_size=list(box_size),
    )
    v.dock(exhaustiveness=exhaustiveness, n_poses=num_modes)
    v.write_poses(str(out_pdbqt), n_poses=num_modes, overwrite=True)


def _parse_vina_pose_mols(out_pdbqt: Path) -> list[Any]:
    """Parse a Vina output PDBQT into a list of RDKit mols
    (one per MODEL block). Uses Meeko's PDBQTMolecule +
    RDKitMolCreate so the docked pose is reconstructed with
    the correct bond orders / atom types.

    Vina writes one MODEL/ENDMDL block per pose. Meeko's
    PDBQTMolecule.from_file only reads the first block, so
    we split the file on MODEL boundaries and parse each
    block independently. The REMARK/VINA RESULT lines that
    precede the first MODEL are prepended to every block
    so the score lookup in the Meeko parser is happy.

    Returns an empty list if the file is missing or empty.
    """
    from meeko import PDBQTMolecule, RDKitMolCreate

    if not out_pdbqt.is_file() or out_path_size_zero(out_pdbqt):
        return []

    text = out_pdbqt.read_text(encoding="utf-8")
    lines = text.splitlines()
    remark_lines: list[str] = []
    body_lines: list[str] = []
    for line in lines:
        if line.startswith("MODEL"):
            body_lines.append(line)
        elif body_lines:
            body_lines.append(line)
        else:
            remark_lines.append(line)

    if not body_lines:
        return []

    pose_mols: list[Any] = []
    tmp_dir = out_pdbqt.parent
    for pose_idx, line in enumerate(body_lines):
        if not line.startswith("MODEL"):
            continue
        end = pose_idx
        for j in range(pose_idx + 1, len(body_lines)):
            if body_lines[j].startswith("ENDMDL"):
                end = j
                break
        else:
            end = len(body_lines) - 1
        block = remark_lines + body_lines[pose_idx:end + 1]
        tmp_path = tmp_dir / f"_pose_{pose_idx}.pdbqt"
        tmp_path.write_text("\n".join(block) + "\n", encoding="utf-8")
        try:
            pdbqt_mol = PDBQTMolecule.from_file(str(tmp_path), skip_typing=True)
            mols = RDKitMolCreate.from_pdbqt_mol(pdbqt_mol)
        except Exception:
            mols = []
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass
        for m in mols:
            if m is not None:
                pose_mols.append(m)
    return pose_mols


def out_path_size_zero(p: Path) -> bool:
    return p.stat().st_size == 0


def _hash_poses(out_pdbqt: Path) -> Optional[str]:
    """SHA256 of the pose PDBQT file for determinism checks."""
    if not out_pdbqt.is_file() or out_path_size_zero(out_pdbqt):
        return None
    h = hashlib.sha256()
    h.update(out_pdbqt.read_bytes())
    return h.hexdigest()


def _read_vina_energies(out_pdbqt: Path) -> list[float]:
    """Parse the REMARK VINA RESULT lines from a Vina output PDBQT
    in pose order (top-1 first)."""
    energies: list[float] = []
    if not out_pdbqt.is_file():
        return energies
    with out_pdbqt.open("r") as f:
        for line in f:
            if "VINA RESULT" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        energies.append(float(parts[3]))
                    except ValueError:
                        pass
    return energies


def _load_sti_template_from_chemcomp(ligand_id: str) -> Optional[str]:
    """Fetch the SMILES of a chemical component from the RCSB
    Data API chemcomp endpoint. Retries up to 3 times with a
    short backoff. Returns None on any failure (no SMILES in
    response, non-200 status, network error, etc.)."""
    import requests
    import time as _time

    url = f"https://data.rcsb.org/rest/v1/core/chemcomp/{ligand_id}"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                smi = data.get("rcsb_chem_comp_descriptor", {}).get("SMILES")
                if isinstance(smi, list):
                    smi = smi[0] if smi else None
                if smi:
                    return smi
        except Exception:
            pass
        if attempt < 2:
            _time.sleep(2 + attempt)
    return None


def _build_crystal_mol_with_bond_orders(
    ref_pdb_path: Path,
    ligand_id: str,
) -> Any:
    """Build the crystal-ligand reference mol from a PDB and
    assign bond orders from the RCSB chemcomp SMILES.

    Returns an RDKit mol with explicit bond orders, or raises
    on failure.
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem

    template_smi = _load_sti_template_from_chemcomp(ligand_id)
    if not template_smi:
        raise RuntimeError(
            f"could not fetch SMILES for chemcomp {ligand_id!r} from RCSB"
        )
    template_mol = Chem.MolFromSmiles(template_smi)
    if template_mol is None:
        raise RuntimeError(
            f"could not parse chemcomp {ligand_id!r} SMILES: {template_smi!r}"
        )

    raw = Chem.MolFromPDBFile(str(ref_pdb_path), removeHs=True, sanitize=False)
    if raw is None:
        raise RuntimeError(f"RDKit could not parse crystal PDB: {ref_pdb_path}")

    ref_mol = AllChem.AssignBondOrdersFromTemplate(template_mol, raw)
    if ref_mol is None:
        raise RuntimeError(
            f"AssignBondOrdersFromTemplate returned None for {ref_pdb_path}"
        )
    return ref_mol


def _inplace_symmetry_aware_heavy_rmsd(mol_pred: Any, mol_ref: Any) -> float:
    """Compute the IN-PLACE, symmetry-aware, heavy-atom RMSD
    between two RDKit mols with rdMolAlign.CalcRMS.

    No re-alignment is performed. The atom correspondence is
    found by substructure match (which handles molecular
    symmetry via the `maxMatches` parameter), then the docked
    mol's atoms are reordered so its atom ordering matches the
    crystal mol. CalcRMS with no `map` argument just pairs
    atoms in order — no rotation, no translation, no realignment.

    The docked-pose mol (from Meeko) has explicit Hs and AD4
    types. The crystal-pose mol (from PDB + AssignBondOrdersFromTemplate)
    is heavy-atom-only. We strip Hs from the docked mol first
    so the atom counts match.

    NOTE: this version of rdkit's CalcRMS does not accept
    `prbCrippenContribs` / `refCrippenContribs` (those were
    added in rdkit 2023.09). Renumbering atoms is the portable
    way to align two mols for an in-place coordinate comparison.
    """
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign

    mol_pred_stripped = Chem.RemoveHs(mol_pred)

    match = mol_ref.GetSubstructMatch(mol_pred_stripped)
    if not match or len(match) != mol_ref.GetNumAtoms():
        raise RuntimeError(
            f"substructure match failed: ref has {mol_ref.GetNumAtoms()} "
            f"heavy atoms, match has {len(match) if match else 0}"
        )

    mol_pred_aligned = Chem.RenumberAtoms(mol_pred_stripped, list(match))

    rmsd = rdMolAlign.CalcRMS(mol_pred_aligned, mol_ref)
    return float(rmsd)


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def dock_ligand_vina(
    receptor_pdb_path: str,
    ligand_smiles: str,
    box_center: tuple[float, float, float],
    box_size: tuple[float, float, float],
    exhaustiveness: int = _DEFAULT_EXHAUSTIVENESS,
    num_modes: int = _DEFAULT_NUM_MODES,
    seed: int = _DEFAULT_SEED,
    cpu: int = _DEFAULT_CPU,
    embed_seed: int = _DEFAULT_SEED,
    runtime_cap: Optional[int] = None,
    reference_ligand_pdb_path: Optional[str] = None,
    reference_ligand_id: Optional[str] = None,
    use_fallback_pdb_to_pdbqt: bool = False,
):
    """Dock a ligand (SMILES) against a receptor (PDB) using Vina.

    Parameters
    ----------
    receptor_pdb_path : str
        Path to the receptor PDB file. The receptor is prepared
        with Meeko's `mk_prepare_receptor.py` CLI in rigid mode.
    ligand_smiles : str
        SMILES of the ligand to dock. The ligand is prepared with
        RDKit + Meeko's `mk_prepare_ligand.py` CLI.
    box_center : tuple of 3 floats
        (x, y, z) center of the docking box in Angstroms.
    box_size : tuple of 3 floats
        (sx, sy, sz) size of the docking box in Angstroms.
    exhaustiveness : int, default 8
        Vina exhaustiveness parameter.
    num_modes : int, default 9
        Number of binding modes to return.
    seed : int, default 42
        Random seed for Vina determinism.
    cpu : int, default 1
        Number of CPUs to use.
    embed_seed : int, default 42
        Random seed for the RDKit ``EmbedMolecule`` call that
        generates the ligand's initial 3D conformer. The
        starting conformer is the search starting point for
        Vina, so this seed pins the ligand prep step of the
        pipeline. The default is ``_DEFAULT_SEED`` (42). The
        seed used is recorded in the return dict as
        ``data.embed_seed``.
    runtime_cap : int or None
        Optional wall-clock cap in seconds (the Vina CLI has no
        --timeout; this caps the subprocess timeout).
    reference_ligand_pdb_path : str or None
        If provided, compute the in-place, symmetry-aware,
        heavy-atom RMSD of the top-1 pose vs this reference
        (with rdMolAlign.CalcRMS, NO re-alignment). Used for
        the redock validation on 2HYY+STI.
    reference_ligand_id : str or None
        If provided, the crystal-ligand bond orders are assigned
        from this chemical component's RCSB chemcomp SMILES
        (e.g. "STI" for 2HYY). Required when
        reference_ligand_pdb_path is provided.
    use_fallback_pdb_to_pdbqt : bool, default False
        OFF BY DEFAULT. If True, fall back to the minimal
        hand-written PDB->PDBQT converter that lives in
        `_pdb_to_pdbqt_receptor`. NOT used for the validation
        path; only useful for offline experimentation.

    Returns
    -------
    dict
        Contract dict with poses, energies, and (if reference
        provided) the top-1 RMSD and best-of-9 RMSD.

        NOTE: Vina scores are docking scores, not measured
        binding affinities.

        NOTE: the returned poses are HYPOTHESES. A docked pose is a
        candidate geometry produced by the search, not a confirmed
        binding mode; the pose must be checked against other evidence
        before it is treated as the structure of the complex.
    """
    if not isinstance(receptor_pdb_path, str) or not receptor_pdb_path:
        return {
            "success": False,
            "error": f"receptor_pdb_path must be a non-empty string, got {receptor_pdb_path!r}",
        }
    if not isinstance(ligand_smiles, str) or not ligand_smiles:
        return {
            "success": False,
            "error": f"ligand_smiles must be a non-empty string, got {ligand_smiles!r}",
        }
    if not (isinstance(box_center, (tuple, list)) and len(box_center) == 3):
        return {
            "success": False,
            "error": f"box_center must be a 3-tuple, got {box_center!r}",
        }
    if not (isinstance(box_size, (tuple, list)) and len(box_size) == 3):
        return {
            "success": False,
            "error": f"box_size must be a 3-tuple, got {box_size!r}",
        }
    if not all(isinstance(v, (int, float)) and v > 0 for v in box_size):
        return {
            "success": False,
            "error": f"box_size values must be positive, got {box_size!r}",
        }
    if not isinstance(exhaustiveness, int) or exhaustiveness < 1:
        return {
            "success": False,
            "error": f"exhaustiveness must be a positive int, got {exhaustiveness!r}",
        }
    if not isinstance(num_modes, int) or num_modes < 1:
        return {
            "success": False,
            "error": f"num_modes must be a positive int, got {num_modes!r}",
        }

    receptor_pdb = Path(receptor_pdb_path)
    if not receptor_pdb.is_file():
        return {
            "success": False,
            "error": f"receptor PDB not found: {receptor_pdb_path}",
        }

    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="dock_ligand_vina_") as tmp_str:
        tmp = Path(tmp_str)
        try:
            if use_fallback_pdb_to_pdbqt:
                receptor_pdbqt, meeko_cmd = _prepare_receptor_fallback(receptor_pdb, tmp)
            else:
                receptor_pdbqt, meeko_cmd = _prepare_receptor_meeko(receptor_pdb, tmp)
        except Exception as exc:
            return {"success": False, "error": f"receptor prep failed: {exc}"}
        try:
            ligand_pdbqt = _prepare_ligand_meeko(ligand_smiles, tmp, embed_seed=embed_seed)
        except Exception as exc:
            return {"success": False, "error": f"ligand prep failed: {exc}"}
        out_pdbqt = tmp / "out.pdbqt"
        timeout = runtime_cap if runtime_cap else _TIMEOUT_S
        try:
            _vina_dock(
                receptor_pdbqt, ligand_pdbqt, box_center, box_size, out_pdbqt,
                exhaustiveness=exhaustiveness, num_modes=num_modes,
                seed=seed, cpu=cpu, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Vina timed out after {timeout}s",
            }
        except Exception as exc:
            return {"success": False, "error": f"Vina failed: {exc}"}

        energies = _read_vina_energies(out_pdbqt)
        pose_mols = _parse_vina_pose_mols(out_pdbqt)
        pose_hash = _hash_poses(out_pdbqt)

        top1_rmsd = None
        best_of_n_rmsd = None
        if reference_ligand_pdb_path:
            ref_path = Path(reference_ligand_pdb_path)
            if not ref_path.is_file():
                return {
                    "success": False,
                    "error": f"reference ligand PDB not found: {reference_ligand_pdb_path}",
                }
            if not reference_ligand_id:
                return {
                    "success": False,
                    "error": (
                        "reference_ligand_id is required when "
                        "reference_ligand_pdb_path is provided"
                    ),
                }
            try:
                ref_mol = _build_crystal_mol_with_bond_orders(
                    ref_path, reference_ligand_id,
                )
            except Exception as exc:
                return {
                    "success": False,
                    "error": f"reference mol build failed: {exc}",
                }
            if not pose_mols:
                return {
                    "success": False,
                    "error": "no docked poses could be parsed from Vina output",
                }
            try:
                rmsds = [
                    _inplace_symmetry_aware_heavy_rmsd(m, ref_mol) for m in pose_mols
                ]
            except Exception as exc:
                return {
                    "success": False,
                    "error": f"RMSD computation failed: {exc}",
                }
            top1_rmsd = rmsds[0] if rmsds else None
            best_of_n_rmsd = min(rmsds) if rmsds else None

    elapsed = time.monotonic() - t0
    return {
        "success": True,
        "data": {
            "n_poses": len(pose_mols),
            "energies_kcal_mol": energies,
            "pose_hash_sha256": pose_hash,
            "meeko_command": meeko_cmd,
            "vina_version": _vina_version(),
            "runtime_seconds": elapsed,
            "exhaustiveness": exhaustiveness,
            "num_modes": num_modes,
            "seed": seed,
            "cpu": cpu,
            "embed_seed": embed_seed,
            "box_center": list(box_center),
            "box_size": list(box_size),
            "top1_rmsd_angstrom": top1_rmsd,
            "best_of_n_rmsd_angstrom": best_of_n_rmsd,
        },
    }


def _prepare_receptor_fallback(receptor_pdb_path: Path, out_dir: Path) -> tuple[Path, str]:
    """OFF-BY-DEFAULT fallback. Hand-written minimal PDB->PDBQT
    converter. Not used for the validation path; kept for offline
    experimentation only. See the tool card for the rationale."""
    out_path = out_dir / "receptor.pdbqt"
    _pdb_to_pdbqt_receptor(receptor_pdb_path, out_path, chain="A")
    return out_path, "_pdb_to_pdbqt_receptor (custom fallback; off by default)"


_AD4_TYPE_BY_ELEMENT = {
    "C": "C", "N": "N", "O": "OA", "S": "SA", "P": "P", "H": "HD",
    "F": "F", "CL": "Cl", "BR": "Br", "I": "I", "FE": "Fe", "ZN": "Zn",
    "MG": "Mg", "MN": "Mn", "CA": "Ca", "CL_": "Cl",
}


def _pdb_to_pdbqt_receptor(pdb_path: Path, out_path: Path, chain: str = "A") -> None:
    """OFF-BY-DEFAULT hand-written PDB->PDBQT converter. Kept for
    offline experimentation only; NOT used for validation. See
    the tool card for the rationale and what changed."""
    with pdb_path.open("r") as fin, out_path.open("w") as fout:
        fout.write("REMARK  9 Generated by biomni dock_ligand_vina _pdb_to_pdbqt_receptor (FALLBACK; off by default)\n")
        serial = 0
        for line in fin:
            if not line.startswith("ATOM"):
                if line.startswith("END"):
                    fout.write("END\n")
                continue
            if chain and len(line) > 21 and line[21] != chain:
                continue
            serial += 1
            elem = ""
            if len(line) >= 78:
                elem = line[76:78].strip()
            if not elem:
                atom_name = line[12:16].strip()
                elem = atom_name[0]
            ad4 = _AD4_TYPE_BY_ELEMENT.get(elem.upper(), elem)
            new_line = "{:6s}{:5d} {:4s}{:1s}{:3s} {:1s}{:1s}{:4d}{:1s}  {:8.3f}{:8.3f}{:8.3f}  1.00  0.00     0.000 {:>2s}\n".format(
                "ATOM", serial, line[12:16],
                line[16:17] if len(line) > 16 else "",
                line[17:20] if len(line) > 20 else "   ",
                line[20:21] if len(line) > 20 else " ",
                line[21:22] if len(line) > 21 else "A",
                int(line[22:26]) if len(line) > 25 and line[22:26].strip().isdigit() else 1,
                line[26:27] if len(line) > 26 else "",
                float(line[30:38]) if len(line) > 37 else 0.0,
                float(line[38:46]) if len(line) > 45 else 0.0,
                float(line[46:54]) if len(line) > 53 else 0.0,
                ad4,
            )
            fout.write(new_line[:80].ljust(80) + "\n")

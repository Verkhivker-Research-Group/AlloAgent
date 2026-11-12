# B2 — dock_ligand_vina: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: AutoDock Vina 1.2.7 (already in the image; not new).
- Ligand preparation: from SMILES via RDKit + Meeko (no hand-written
  PDBQT). The Meeko `MoleculePreparation` class is used to assign
  bond orders from a template SMILES and write the ligand PDBQT.
- Receptor preparation: Meeko's receptor-preparation command in
  **rigid** mode (no flexible residues). The exact command and
  version are recorded in the output.
- Parameters: `box_center` (x, y, z), `box_size` (sx, sy, sz),
  `exhaustiveness` (default 8), `seed` (fixed default 42),
  `cpu` (default 1), `num_modes` (default 9), `runtime_cap` (seconds).
- Output: list of poses with Vina energies (kcal/mol), RMSD
  to the input pose, and a pose hash for determinism checks.
- **No accuracy claim**: the docstring and tool card state that
  Vina scores are docking scores, not measured binding affinities.
- Redock validation on 2HYY with the crystal imatinib (STI):
  - Ligand coordinates from the PDB (chain A, residue STI).
  - Bond orders assigned from a template SMILES taken from the
    RCSB chemical component (STI = imatinib).
  - RMSD computed **IN PLACE** (no re-alignment) and
    **symmetry-aware** (RDKit `rdMolAlign.CalcRMS` or equivalent).
  - Heavy atoms only.
  - **Primary criterion**: top-1 pose RMSD <= 2.0 Å at
    `exhaustiveness=8`.
  - **Secondary (informational)**: best-of-9 poses, and
    `exhaustiveness=16` and `exhaustiveness=32` (these do NOT
    change the criterion).
  - Determinism: two runs with the same seed give identical
    energies and pose hashes.
- Status: NOT STARTED. Vina is in the image; RDKit and Meeko
  are already in the conda env (verified in the A1 inventory).

## Criteria

| # | Criterion | Verification |
|---|---|---|
| B2-1 | `biomni/tool/dock_ligand_vina.py` exists with the entry point `dock_ligand_vina(receptor_pdbqt, ligand_smiles, box_center, box_size, exhaustiveness=8, seed=42, cpu=1, num_modes=9, runtime_cap=None)` | `git ls-files` returns the path. |
| B2-2 | The ligand is prepared from SMILES via RDKit + Meeko. The Meeko version and the exact `MoleculePreparation` call are recorded in the output. | The test asserts the Meeko version is recorded. |
| B2-3 | The receptor is prepared with Meeko's receptor-preparation command in rigid mode. The exact command and version are recorded. | The test asserts the command and version are recorded. |
| B2-4 | The docstring of `dock_ligand_vina` contains the sentence "Vina scores are docking scores, not measured binding affinities" (or equivalent) | The test asserts the sentence is present. |
| B2-5 | The tool card at `docs/tool_cards/B2_dock_ligand_vina.md` does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| B2-6 | Redock validation on 2HYY + STI: `dock_ligand_vina(receptor_2hyy.pdbqt, "STI_template_smiles", box_center, box_size, exhaustiveness=8, seed=42)` returns a top-1 pose with RMSD <= 2.0 Å vs the crystal ligand (heavy atoms only, symmetry-aware, in place) | The test asserts `top1_rmsd <= 2.0`. |
| B2-7 | RMSD is computed IN PLACE (no re-alignment) and symmetry-aware (RDKit `rdMolAlign.CalcRMS` or equivalent) | The implementation uses `rdMolAlign.GetBestRMS` (which handles symmetry) without pre-alignment. |
| B2-8 | The best-of-9 RMSD (lowest RMSD among the returned modes) is reported as secondary information | The test asserts `best_of_9_rmsd` is present. |
| B2-9 | Exhaustiveness=16 and exhaustiveness=32 are run as secondary information; the criterion (B2-6) is evaluated at exhaustiveness=8 | The test runs the redock at 8, 16, and 32 and reports all three. |
| B2-10 | Determinism: two runs with the same seed give identical energies and pose hashes | The test calls the redock twice and asserts the pose hashes match. |
| B2-11 | Runtime is reported in the output | The test asserts `runtime_seconds` is present. |
| B2-12 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| B2-13 | Invalid `box_center` (not 3 floats) returns `success=False` | The test asserts this. |
| B2-14 | Invalid `box_size` (not 3 positive floats) returns `success=False` | The test asserts this. |
| B2-15 | The receptor PDBQT path is validated; missing file returns `success=False` | The test asserts this. |
| B2-16 | Vina binary not found returns `success=False` with a clear error pointing to the Dockerfile | The test asserts this (by mocking `subprocess.run` to return ENOENT). |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| B2-1 | (filled) | (filled) |
| B2-2 | (filled) | (filled) |
| B2-3 | (filled) | (filled) |
| B2-4 | (filled) | (filled) |
| B2-5 | (filled) | (filled) |
| B2-6 | (filled) | (filled) |
| B2-7 | (filled) | (filled) |
| B2-8 | (filled) | (filled) |
| B2-9 | (filled) | (filled) |
| B2-10 | (filled) | (filled) |
| B2-11 | (filled) | (filled) |
| B2-12 | (filled) | (filled) |
| B2-13 | (filled) | (filled) |
| B2-14 | (filled) | (filled) |
| B2-15 | (filled) | (filled) |
| B2-16 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed. The redock validation on 2HYY + STI is
the primary pass criterion (B2-6); the B2-8 and B2-9 entries
about best-of-9 and higher exhaustiveness are informational
and do NOT change the criterion.

## Dated notes (added after running; do NOT change the original criterion text above)

### 2026-10-14 â€” B2 verdict: FAIL on the committed criterion

The committed primary criterion is **top-1 RMSD <= 2.0 A at
exhaustiveness=8** (B2-6, in-place, symmetry-aware, heavy-atom
RMSD). The observed result is **top-1 = 4.348 A**, which is
**FAIL** on the committed criterion.

Observed results (2HYY+STI, seed=42, box=15x15x15 around the
crystal centroid, num_modes=9):

| exhaustiveness | top-1 (A) | best-of-9 (A) | runtime (s) |
|---:|---:|---:|---:|
| 8  | 4.348 | 1.088 | 96  |
| 16 | 4.348 | 1.088 | 219 |
| 32 | 1.574 | 1.574 | 366 |

Determinism (exh=8, twice): energies identical, pose_hash
identical.

Root cause of the top-1 regression at exh=8: the original
Phase 2d reference (commit `e7fac39`) used
`rdMolAlign.GetBestRMS` (Hungarian matching WITH alignment)
and reported 2.146 A. The current implementation uses
`rdMolAlign.CalcRMS` (no realignment) on mols whose atom
orderings have been aligned by `GetSubstructMatch` +
`RenumberAtoms`. At exhaustiveness=8 the in-place coordinate
comparison fails the 2.0 A threshold for the top-1 pose
(4.348 A) but PASSES for the best-of-9 pose (1.088 A) and
for the top-1 at exhaustiveness=32 (1.574 A). The docking
itself is deterministic and correct; higher exhaustiveness
is needed to converge the pose closely enough that the
in-place coordinate comparison falls under 2.0 A without
realignment.

# B2c — dock_ligand_vina: RCSB-verified 5-complex redock criteria
# (written BEFORE running anything, per the standing rule)

## Tool summary

Same engine as B2/B2b: AutoDock Vina 1.2.7 + RDKit 2024.09.6 +
Meeko 0.8.0 (`mk_prepare_receptor.py` CLI in rigid mode;
`mk_prepare_ligand.py` CLI for the ligand). RMSD via
`rdMolAlign.CalcRMS` (IN-PLACE, no realignment; atoms reordered
via `GetSubstructMatch` + `RenumberAtoms`).

## Why B2c exists (difference from B2b)

B2b pre-registered 5 complexes "chosen by a stated rule, not by
trying them". Three of the five ligand IDs were not actually
present as HETATM records in chain A of the corresponding PDB
files (1OHR+MK1, 4GR0+4QM, 1UYD+AGS). Those trials were VOID
(the tool was never called), so the B2b 4-of-5 criterion could
not be evaluated (INCONCLUSIVE).

B2c closes that gap by adding an explicit RCSB verification
step BEFORE the run: for every candidate, the ligand MUST be
present as a HETATM record in chain A of the deposited PDB
file, the resolution MUST be <= 2.5 A, and the ligand MUST have
15..50 heavy atoms. Only candidates that pass all three checks
are admitted to the 5-complex set.

## Pre-registered criterion

- **Primary**: top-1 pose RMSD <= 2.0 A (in-place,
  symmetry-aware, heavy atoms) for at least **3 of 5**
  redocks, at default exhaustiveness=32.
- **Default exhaustiveness**: 32.
- **Other parameters**: seed=42, num_modes=9, cpu=1, box =
  ligand bounding box + 5 A padding per axis (min 15 A per
  axis) around the crystal ligand of chain A.
- **No realignment**: `rdMolAlign.CalcRMS` is IN-PLACE
  (`symmetrizeConjugatedTerminalGroups=True` default). The
  docked-mol atoms are reordered to match the crystal-mol
  ordering via `GetSubstructMatch` + `RenumberAtoms`.
- **Secondary (informational only)**: best-of-9 RMSD (lowest
  RMSD among returned modes). This does NOT change the
  criterion.
- **Runtime cap**: 600 s per redock.
- **VOID rule**: if the ligand HETATM extraction returns 0
  atoms for a candidate, that trial is VOID (the tool is not
  called) and is reported as VOID, not PASS/FAIL. A VOID trial
  reduces the denominator; the criterion is then evaluated
  against the number of valid trials (>= 3 PASS out of the
  valid trials).
- **No accuracy claim**: the tool docstring and tool card state
  that docked poses are hypotheses and Vina scores are docking
  scores, not measured binding affinities.

## The 5 complexes (RCSB-verified BEFORE the run)

Each row below was verified with `build_logs/_b2c_verify.py`,
which (1) reads `rcsb_entry_info.resolution_combined` from
`/core/entry/{pdb}`, (2) fetches the ligand SMILES from
`/core/chemcomp/{lig}` and counts heavy atoms with RDKit, and
(3) scans the deposited `{pdb}.pdb` for a HETATM record whose
residue name equals the ligand ID in **chain A**.

| # | PDB ID | Ligand ID | Chain | Protein | Family | Resolution | Heavy atoms |
|---|---|---|---|---|---|---|---|
| 1 | 2HYY | STI | A | ABL1 kinase (imatinib) | kinase | 2.4 A | 37 |
| 2 | 3ERT | OHT | A | estrogen receptor alpha (4-hydroxytamoxifen) | nuclear receptor | 1.9 A | 29 |
| 3 | 1RX3 | MTX | A | dihydrofolate reductase (methotrexate) | oxidoreductase | 2.2 A | 33 |
| 4 | 1HVR | XK2 | A | HIV-1 protease (cyclic urea inhibitor) | aspartyl protease | 1.8 A | 46 |
| 5 | 1A4G | ZMR | A | influenza A neuraminidase (zanamivir analog) | neuraminidase | 2.2 A | 23 |

All five ligand IDs were confirmed present as chain-A HETATM
records by the scan (this is the check B2b lacked). Five
distinct protein families: kinase, nuclear receptor,
oxidoreductase, aspartyl protease, neuraminidase.

## Verification evidence (pre-run)

`build_logs/_t4_verify_final.log` reports `TOTAL PASS: 5 of 5`
for the table above. The candidate list was frozen at this
point: no candidate was added or removed after verification.

## RMSD pipeline (unchanged from B2/B2b)

1. Receptor: `mk_prepare_receptor.py --read_pdb <pdb>
   -o <basename> -p -x --default_altloc A` (rigid mode).
2. Ligand: RDKit `EmbedMolecule` + `MMFFOptimizeMolecule` from
   the SMILES (fetched from the RCSB chemcomp endpoint) -> SDF
   -> `mk_prepare_ligand.py -i <sdf> -o <pdbqt>`.
3. Vina: `vina_python.Vina(sf_name="vina", cpu=1, seed=42,
   verbosity=0)` -> `set_receptor` -> `set_ligand_from_file`
   -> `compute_vina_maps(center=box_center, box_size=box_size)`
   -> `dock(exhaustiveness=32, n_poses=9)`.
4. RMSD: crystal-ligand mol built via
   `AllChem.AssignBondOrdersFromTemplate(template_mol, raw)`;
   docked-ligand mols parsed via `PDBQTMolecule.from_file` +
   `RDKitMolCreate.from_pdbqt_mol`; atoms reordered via
   `GetSubstructMatch` + `RenumberAtoms`; RMSD via
   `rdMolAlign.CalcRMS`.

## Verdict (filled ONCE after the run)

| # | PDB | Lig | top-1 (A) | best-of-9 (A) | wall (s) | Verdict |
|---|---|---|---|---|---|---|
| B2c-1 | (filled) | (filled) | (filled) | (filled) | (filled) | (filled) |
| B2c-2 | (filled) | (filled) | (filled) | (filled) | (filled) | (filled) |
| B2c-3 | (filled) | (filled) | (filled) | (filled) | (filled) | (filled) |
| B2c-4 | (filled) | (filled) | (filled) | (filled) | (filled) | (filled) |
| B2c-5 | (filled) | (filled) | (filled) | (filled) | (filled) | (filled) |

## Status

Criteria committed BEFORE running. The 5 redocks will be
executed in a single batch after this file is committed, and
the per-redock results reported in a dated note (same
convention as B2-6 and B2b). The pass criterion is top-1
<= 2.0 A for at least 3 of 5 valid redocks. If fewer than 3 of
5 valid trials pass, the B2c verdict is FAIL.

## Dated notes (added after running; do NOT change the criteria text above)

### 2026-10-15 — B2c result: FAIL (1 of 5 PASS)

The 5 redocks were run in one batch (`build_logs/_b2c_run.py`,
log `build_logs/_t4_b2c_run.log`, results JSON
`/tmp/b2c_redock/b2c_results.json` at runtime, under /tmp so not
committed). Exhaustiveness=32, seed=42, box = chain-A ligand
bbox + 5 A padding (min 15 A/axis), num_modes=9, Vina runtime
cap 600 s.

Unlike B2b, all 5 trials were VALID this time (the RCSB
verification step found a chain-A HETATM record for every
ligand), so 5 of 5 trials reached the tool and the pre-
registered 3-of-5 criterion CAN be evaluated.

| # | PDB | Lig | top-1 (A) | best-of-9 (A) | wall (s) | Verdict (top-1 vs 2.0 A) |
|---|---|---|---:|---:|---:|---|
| 1 | 2HYY | STI | 0.918 | 0.918 | 316.3 | **PASS** |
| 2 | 3ERT | OHT | 4.855 | 2.482 | 215.4 | FAIL |
| 3 | 1RX3 | MTX | 4.547 | 4.547 | 362.7 | FAIL |
| 4 | 1HVR | XK2 | 5.765 | 5.727 | 1759.4 | FAIL |
| 5 | 1A4G | ZMR | 2.860 | 2.860 | 163.0 | FAIL |

**B2c verdict: FAIL** (1 of 5 PASS; need >= 3 of 5).

Observations:
- 2HYY+STI reproduces exactly (top-1 = 0.918 A identical to
  the B2b run and to the B2 3-run determinism check), which
  confirms the pipeline is deterministic.
- The other 4 redocks retrieve poses that are energetically
  reasonable (Vina scores -6.2 to -8.9 kcal/mol) but are NOT
  the crystal pose (top-1 over 2.0 A). This is the expected
  behavior of Vina on flexible drug-like ligands: for the
  flexible SERM (OHT), antifolate (MTX) and peptidomimetic
  (XK2), the global Vina minimum differs from the crystallo-
  graphic pose. The best-of-9 for 3ERT (2.482 A) is the only
  near-threshold secondary value.
- Runtime cap semantics: `runtime_cap` bounds ONLY the Vina
  subprocess (see `dock_ligand_vina` line ~538). The reported
  `runtime_seconds` is the whole tool call (receptor prep +
  ligand prep + Vina + RMSD). 1HVR+XK2 reports wall 1759.4 s
  even though the Vina cap is 600 s, because receptor/ligand
  prep and per-pose RMSD for the 46-heavy-atom ligand dominate.
  Vina itself did not time out (success=True, 9 poses).

The committed criterion is top-1 <= 2.0 A for at least 3 of 5
valid redocks. The observed result is 1 of 5 valid PASS, so
the B2c verdict is FAIL. Reported as-is (no criterion change).

This closes the B2b gap (all trials valid this time) and
confirms the B2/B2b conclusion: Vina reproduces the crystal
pose for 2HYY+STI but not for the four other drug-like
complexes at exhaustiveness=32.

### 2026-10-15 — post-run correction: root-cause detail for the 4 FAILs

The 4 non-2HYY trials all completed with `success=True` and 9
(or 8 for 3ERT) poses. None hit the Vina timeout. Their top-1
poses are the Vina global minima for their respective boxes,
which for these larger, more flexible ligands do not coincide
with the deposited crystal pose. This is a property of the
scoring function + search, not a crash or a VOID trial.
No re-runs were performed after seeing the results (per the
standing rule, the criterion is not changed after a run).

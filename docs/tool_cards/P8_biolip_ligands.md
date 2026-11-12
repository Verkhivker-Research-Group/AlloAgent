# P8 biolip_ligands

## Question the tool answers

Which ligands are bound in a given PDB entry (and chain)?

## What it does NOT answer

It does not say whether a ligand is an allosteric or an orthosteric binder, and it does not give the binding affinity.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character (or 12) PDB id |
| `chain` | `str` | no | `None` | optional chain id |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain, ligands: [str, ...], total_interactions: int, chains: [str, ...], uniprot_ids: [str, ...]}`.

## Source and version

- upstream URL: BioLiP `biolip.pkl` snapshot (989,058 rows), read-only mount

## Runtime

- first call loads the 265 MB pickle (several seconds); later calls are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `1GG1` -> `ligands == ["MN", "PGA"]`, `total_interactions == 8`, `chains == ["A","B","C","D"]`, `uniprot_ids == ["P0AB91"]`
- source of the expectation: biolip.pkl, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-17)

## Negative control

- expectation: input `1TIM` -> `success=True` with `ligands == []` and `total_interactions == 0`

## Code location and version

- function: `biomni/tool/biolip.py::biolip_ligands`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

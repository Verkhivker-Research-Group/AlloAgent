# P7 parse_biolip_interactions

## Question the tool answers

Which ligand-protein interactions does the BioLiP snapshot record for a PDB entry and chain?

## What it does NOT answer

It does not say which ligand modulates the target, and it does not score the affinity.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | no | `None` | 4-character (or 12) PDB id; None returns the whole table |
| `chain` | `str` | no | `None` | optional chain id |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain, total, records, columns}`; the records carry the BioLiP interaction columns (PDB, Chain, Ligand, UniProt_ID, ...).

## Source and version

- upstream URL: BioLiP `biolip.pkl` snapshot, 989,058 rows, mounted read-only from the Biolab data lake

## Runtime

- first call loads the 265 MB pickle (several seconds); later calls in the same process are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `1GG1`, chain `A` -> `total == 2`
- source of the expectation: biolip.pkl, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-21)

## Negative control

- expectation: input `1TIM` -> `success=True` with `total == 0`; 1TIM is absent from the BioLiP snapshot

## Code location and version

- function: `biomni/tool/biolip.py::parse_biolip_interactions`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

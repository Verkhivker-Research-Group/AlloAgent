# P23 load_pdb

## Question the tool answers

Can the structure for a PDB id be fetched and parsed?

## What it does NOT answer

It does not answer anything about allostery; it only loads the structure.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id |
| `query_pdb_identifiers` | `callable` | no | `None` | optional downloader, tried before RCSB |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, atom_count, residue_count, chains, source}`.

## Source and version

- upstream URL: RCSB `https://files.rcsb.org/download/<id>.pdb`

## Runtime

- a few hundred milliseconds; online

## Determinism

- deterministic for a given PDB entry

## Failure modes

- RCSB returns a non-200 -> `success=False`, error states the status
- network error -> `success=False`, error starts `RCSB download failed`

## Known-answer test

- expectation: input `1CRN` -> 327 atoms, 46 residues, chains `["A"]`
- source of the expectation: RCSB 1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-16)

## Negative control

- expectation: input `ZZZZ` -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::load_pdb`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

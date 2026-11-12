# P11 biolip_rna

## Question the tool answers

What RNA sequence does the BioLiP snapshot store for a PDB entry and chain?

## What it does NOT answer

It does not verify the stored sequence against the current PDB entry, and it does not say which nucleotides bind a ligand.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character (or 12) PDB id |
| `chain` | `str` | no | `None` | optional chain id (1-2 letters) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain, kind, total, records, columns}`.

## Source and version

- upstream URL: BioLiP `rna.pkl` snapshot (18,920 rows), read-only mount

## Runtime

- first call loads the 12 MB pickle; later calls are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- chain longer than two letters -> `success=False`, error says the RNA chain must be 1-2 letters
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `8A3W` -> `total == 10`; the first identifier is `8a3w_rna_S1` and that record's sequence is 1663 nucleotides long
- source of the expectation: rna.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-7)

## Negative control

- expectation: input `8A3W`, chain `S1` -> `success=True` with `total == 1` and identifier `8a3w_rna_S1`

## Code location and version

- function: `biomni/tool/biolip.py::biolip_rna`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

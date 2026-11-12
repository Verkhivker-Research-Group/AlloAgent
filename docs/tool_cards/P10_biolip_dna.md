# P10 biolip_dna

## Question the tool answers

What DNA sequence does the BioLiP snapshot store for a PDB entry and chain?

## What it does NOT answer

It does not verify the stored sequence against the current PDB entry, and it does not say which nucleotides bind a ligand.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character (or 12) PDB id |
| `chain` | `str` | no | `None` | optional chain id (single letter) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain, kind, total, records, columns}`.

## Source and version

- upstream URL: BioLiP `dna.pkl` snapshot (23,734 rows), read-only mount

## Runtime

- first call loads the 1.6 MB pickle; later calls are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- chain longer than one letter -> `success=False`, error says the DNA chain must be a single letter
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `1A1K` -> `total == 2`, identifiers `1a1k_dna_B` and `1a1k_dna_C`; the first record's sequence is `agcgtgggacc` (11 bases)
- source of the expectation: dna.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-4)

## Negative control

- expectation: input `1A1K`, chain `BC` -> `success=False` with an error naming the single-letter requirement

## Code location and version

- function: `biomni/tool/biolip.py::biolip_dna`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

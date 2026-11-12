# P9 biolip_protein

## Question the tool answers

What protein sequence does the BioLiP snapshot store for a PDB entry and chain?

## What it does NOT answer

It does not verify the stored sequence against the current PDB entry, and it does not say which residues bind a ligand.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character (or 12) PDB id |
| `chain` | `str` | no | `None` | optional chain id |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain, kind, total, records, columns}`; each record carries `identifier`, `chain`, `type`, `uniprot_id`, `length`, `sequence`.

## Source and version

- upstream URL: BioLiP `protein.pkl` snapshot (512,101 rows), read-only mount

## Runtime

- first call loads the 164 MB pickle (several seconds); later calls are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `1A1K` -> `total == 1`; the record's `identifier` is `1a1kA` and its sequence is 85 residues beginning `RPYACPVESCDRRFSRSADLTRHIRIHTGQKPFQCRICMRNFSRSDHLTTHIRTHTGEKP`
- source of the expectation: protein.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-1)

## Negative control

- expectation: input `1A1K`, chain `B` -> `success=True` with `total == 0`

## Code location and version

- function: `biomni/tool/biolip.py::biolip_protein`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

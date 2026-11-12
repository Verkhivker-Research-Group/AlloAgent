# P12 biolip_peptide

## Question the tool answers

What peptide sequence does the BioLiP snapshot store for a PDB entry and chain?

## What it does NOT answer

It does not verify the stored sequence against the current PDB entry, and it does not say which residues bind a ligand.

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

- upstream URL: BioLiP `peptide.pkl` snapshot (30,668 rows), read-only mount

## Runtime

- first call loads the 1.9 MB pickle; later calls are in-memory; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- pdb_id not 4 or 12 characters -> `success=False`
- chain longer than one letter -> `success=False`, error says the peptide chain must be a single letter
- data file missing -> `success=False`, error names the missing path

## Known-answer test

- expectation: input `4A1G` -> `total == 4` with identifiers `4a1g_peptide_E`, `4a1g_peptide_F`, `4a1g_peptide_G`, `4a1g_peptide_H`; the first record's sequence is `KIDTTSFLANLK` (12 residues)
- source of the expectation: peptide.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-9)

## Negative control

- expectation: input `4A1G`, chain `E` -> `success=True` with `total == 1`

## Code location and version

- function: `biomni/tool/biolip.py::biolip_peptide`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

# P26 residue_accessibility

## Question the tool answers

How exposed and how hydrophobic are the candidate residues?

## What it does NOT answer

It does not say whether the residues are allosteric; it only measures accessibility and hydropathy.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id |
| `candidate_residues` | `list` | yes | `-` | list of `(chain_id, residue_number)` pairs |
| `query_pdb_identifiers` | `callable` | no | `None` | optional downloader |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, score, avg_rsasa, avg_hydrophobicity, summary}`.

## Source and version

- upstream URL: RCSB PDB structures; Shrake-Rupley SASA with the Tien et al. 2013 maximum-SASA table; Kyte-Doolittle hydropathy

## Runtime

- a few seconds (the SASA is computed over the whole model); online

## Determinism

- deterministic for a given PDB entry

## Failure modes

- structure cannot be loaded -> `success=False`
- no residue could be analysed -> `success=False`

## Known-answer test

- expectation: input `1CRN` with A/10, A/20, A/30 -> `avg_rsasa == 27.16`, `avg_hydrophobicity == -1.87`, `score == 0.772`
- source of the expectation: 1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-19)

## Negative control

- expectation: a residue number outside the structure -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::residue_accessibility`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

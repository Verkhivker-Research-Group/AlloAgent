# P24 structural_distance

## Question the tool answers

How far do the candidate residues sit from the active-site residues?

## What it does NOT answer

It does not say whether the candidate residues are allosteric; it only measures the heavy-atom distance.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id |
| `candidate_residues` | `list` | yes | `-` | list of `(chain_id, residue_number)` pairs |
| `active_residues` | `list` | yes | `-` | list of `(chain_id, residue_number)` pairs |
| `query_pdb_identifiers` | `callable` | no | `None` | optional downloader |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, score, avg_distance, all_distances, summary}`.

## Source and version

- upstream URL: RCSB PDB structures; heavy-atom coordinates from the parsed entry

## Runtime

- a few hundred milliseconds; online

## Determinism

- deterministic for a given PDB entry

## Failure modes

- structure cannot be loaded -> `success=False`
- a residue is missing from the structure -> `success=False` naming the counts

## Known-answer test

- expectation: input `1CRN`, candidate `[("A", 10)]`, active `[("A", 40)]` -> `avg_distance == 5.49`, `all_distances == [5.49]`, `score == 0.3`
- source of the expectation: 1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-17)

## Negative control

- expectation: a residue number outside the structure -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::structural_distance`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

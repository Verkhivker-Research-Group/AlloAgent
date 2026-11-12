# P25 pocket_geometry

## Question the tool answers

What is the volume, extent and shape of the region the candidate residues span?

## What it does NOT answer

It does not say whether the region is a binding pocket; it only measures the geometry of the candidate residues.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id |
| `candidate_residues` | `list` | yes | `-` | list of `(chain_id, residue_number)` pairs |
| `query_pdb_identifiers` | `callable` | no | `None` | optional downloader |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, score, volume, max_extent, asphericity, shape_score_pmi, summary}`.

## Source and version

- upstream URL: RCSB PDB structures; convex hull over the candidate heavy atoms

## Runtime

- a few hundred milliseconds; online

## Determinism

- deterministic for a given PDB entry

## Failure modes

- structure cannot be loaded -> `success=False`
- fewer than three heavy atoms -> `success=False` naming the count

## Known-answer test

- expectation: input `1CRN` with residues A/10..A/19 -> `volume == 928.3`, `max_extent == 18.74`, `asphericity == 0.21`, `shape_score_pmi == 1.0`, `score == 1.0`
- source of the expectation: 1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-18)

## Negative control

- expectation: a residue list with one residue -> `success=False` naming the insufficient atom count

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::pocket_geometry`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

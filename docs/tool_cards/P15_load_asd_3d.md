# P15 load_asd_3d

## Question the tool answers

What 3D chemical structure does the Allosteric Database ship for a protein's modulators?

## What it does NOT answer

It does not say whether a modulator is an allosteric or an orthosteric binder, and it does not give the binding pose in the protein.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `protein_ids` | `list` | yes | `-` | UniProt accessions to look up |
| `modulator_ids` | `list` | no | `None` | optional ASD modulator ids to restrict the result to |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{modulators: {<asd_id>: {atoms, coordinates, bonds, atom_count, bond_count}}, total_modulators}`.

## Source and version

- upstream URL: ASD `ASD_Release_202306_3D` MOL2 files, 99,959 files, mounted read-only at `/biolab_data`

## Runtime

- a few milliseconds per modulator; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- protein_ids not a list -> `success=False`
- a protein with no curated site -> an empty `modulators` dict, not an error

## Known-answer test

- expectation: input `["P0AB91"]` -> modulator `ASD02170001` with `atom_count == 23` and `bond_count == 23`; its first atom is `{id: "1", name: "C1", x: 5.6138, y: -1.2175, z: 3.0667, type: "C.ar"}` and its first bond is `{id: "1", atom1: "1", atom2: "2", type: "ar"}`
- source of the expectation: ASD_Release_202306_3D, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-9)

## Negative control

- expectation: input `["P51639"]` -> `data.modulators == {}`; P51639 has no curated allosteric site and therefore no site-level modulator

## Code location and version

- function: `biomni/tool/asd.py::load_asd_3d`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

# P14 load_asd_2d

## Question the tool answers

What 2D chemical structure does the Allosteric Database ship for a protein's modulators?

## What it does NOT answer

It does not say whether a modulator is an allosteric or an orthosteric binder, and it does not give the binding affinity.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `protein_ids` | `list` | yes | `-` | UniProt accessions to look up |
| `modulator_ids` | `list` | no | `None` | optional ASD modulator ids to restrict the result to |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{modulators: {<asd_id>: {name, formula, atom_count, bond_count, smiles}}, total_modulators}`.

## Source and version

- upstream URL: ASD `ASD_Release_202306_2D` MOL files, 99,961 files, mounted read-only at `/biolab_data`

## Runtime

- a few milliseconds per modulator; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- protein_ids not a list -> `success=False`
- a protein with no curated site -> an empty `modulators` dict, not an error

## Known-answer test

- expectation: input `["P0AB91"]` -> modulator `ASD02170001` with `name == "ASD02170001.mol"`, `atom_count == 12`, `bond_count == 12`, `formula == "C9NO2"`
- source of the expectation: ASD_Release_202306_2D, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-8)

## Negative control

- expectation: input `["P0AB91"]` with `modulator_ids=["ASD00320001"]` -> the site's modulator is `ASD02170001`, so the filtered result is empty

## Code location and version

- function: `biomni/tool/asd.py::load_asd_2d`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

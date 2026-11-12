# P19 convert_asd_to_uniprot

## Question the tool answers

What is the UniProt accession for an Allosteric Database file id?

## What it does NOT answer

It does not say whether the protein has curated allosteric sites, and it does not name the modulators.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `asd_id` | `str` | yes | `-` | ASD file id, e.g. `ASD00020000_1` |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{asd_id, uniprot_id}`; `uniprot_id` is null when the id is not in ASD.

## Source and version

- upstream URL: ASD protein index (`biomni/tool/_asd_index.tsv`)

## Runtime

- a few milliseconds; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- empty id -> `success=False`

## Known-answer test

- expectation: input `ASD00020000_1` -> `uniprot_id == "P0AB91"`
- source of the expectation: ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-2)

## Negative control

- expectation: input `ASD99999999_1` -> `uniprot_id` is null

## Code location and version

- function: `biomni/tool/allosteric2.py::convert_asd_to_uniprot`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

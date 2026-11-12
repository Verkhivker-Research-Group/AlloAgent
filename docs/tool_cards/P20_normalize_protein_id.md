# P20 normalize_protein_id

## Question the tool answers

Given either a UniProt accession or an ASD file id, what are both forms?

## What it does NOT answer

It does not answer anything about the protein's allosteric sites.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `protein_id` | `str` | yes | `-` | a UniProt accession or an ASD file id |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{protein_id, uniprot_id, asd_id, found}`.

## Source and version

- upstream URL: ASD protein index (`biomni/tool/_asd_index.tsv`)

## Runtime

- a few milliseconds; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- empty id -> `success=False`

## Known-answer test

- expectation: input `P0AB91` and input `ASD00020000_1` both give `uniprot_id == "P0AB91"` and `asd_id == "ASD00020000_1"`
- source of the expectation: ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-3, E-4)

## Negative control

- expectation: input `P99999` -> both ids null and `found` is false

## Code location and version

- function: `biomni/tool/allosteric2.py::normalize_protein_id`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

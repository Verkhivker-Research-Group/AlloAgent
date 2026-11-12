# P18 convert_uniprot_to_asd

## Question the tool answers

What is the Allosteric Database file id for a UniProt accession?

## What it does NOT answer

It does not say whether the protein has curated allosteric sites, and it does not name the modulators.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, asd_id}`; `asd_id` is null when the accession is not in ASD.

## Source and version

- upstream URL: ASD protein index, 2,412 proteins, committed as `biomni/tool/_asd_index.tsv` and generated from the real `ASD_Release_202306_XF` directory

## Runtime

- under a millisecond; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- empty accession -> `success=False`

## Known-answer test

- expectation: input `P0AB91` -> `asd_id == "ASD00020000_1"`
- source of the expectation: ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-1)

## Negative control

- expectation: input `P99999` -> `asd_id` is null

## Code location and version

- function: `biomni/tool/allosteric2.py::convert_uniprot_to_asd`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

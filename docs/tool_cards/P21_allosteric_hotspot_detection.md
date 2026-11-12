# P21 allosteric_hotspot_detection

## Question the tool answers

Which residues of a protein are acted on by several modulators?

## What it does NOT answer

It does not predict an allosteric site. It ranks residues that the curated ASD AS table already lists; a residue called a hotspot is one that several modulators act on.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession or ASD id |
| `celltype_data_path` | `str` | no | `None` | optional parquet of tissue marker genes |
| `min_modulator_count` | `int` | no | `3` | minimum modulator observations before a residue is a candidate |
| `percentile_threshold` | `float` | no | `75.0` | percentile above which a candidate is called a hotspot |
| `asd_as_path` | `str` | no | `None` | path to `ASD_Release_202309_AS.csv` |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, asd_id, hotspots, hotspot_count, residue_scores, candidate_count, percentile_threshold_value, data_sources, summary}`.

## Source and version

- upstream URL: ASD `ASD_Release_202309_AS.csv` (3,102 rows), mounted read-only at `/biolab_data`

## Runtime

- a second or two to read the 3,102-row CSV; offline

## Determinism

- deterministic for a given ASD AS snapshot

## Failure modes

- a protein outside the ASD index -> `success=False`
- the ASD AS file missing -> `success=False`, error lists the missing column

## Known-answer test

- expectation: input `P00533` with `min_modulator_count=2` -> 1 hotspot, residue `"6P1D"`, `importance_score == 0.62`, `modulator_count == 2`, `unique_modulators == 1`
- source of the expectation: ASD_Release_202309_AS.csv, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-6)

## Negative control

- expectation: input `P04150` with `min_modulator_count=2` -> 0 candidates; P04150 has no rows in the ASD AS file

## Code location and version

- function: `biomni/tool/allosteric2.py::allosteric_hotspot_detection`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

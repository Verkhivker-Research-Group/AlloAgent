# P5 analyze_site_patterns

## Question the tool answers

How often does each residue site, and each residue type, occur in a set of covalent-probe records?

## What it does NOT answer

It does not decide whether a site is allosteric and it does not test the records for anything; it only counts.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `sites` | `DataFrame|list|dict` | yes | `-` | a DataFrame with a `Parsed_Sites` column, a list of records, or the `data` dict from `map_covalent_probes_to_allosteric` |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{total_unique_sites, most_common_sites: [[site, count], ...], residue_distribution: [[residue, count], ...], total_entries}`.

## Source and version

- upstream URL: pure computation over the caller's own records; no external source

## Runtime

- typical latency under 0.1 s; offline

## Determinism

- deterministic

## Failure modes

- input is not a DataFrame / list / dict -> `success=False`, error names the accepted types

## Known-answer test

- expectation: input records with `Parsed_Sites` = `[["NT"], ["CYS-481"], ["SER-195"]]` -> `total_unique_sites == 3`, `total_entries == 3`, `most_common_sites[0] == ["NT", 1]`, residue distribution contains `["CYS", 1]` and `["SER", 1]`
- source of the expectation: hand-computed expectation, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-15)

## Negative control

- expectation: a DataFrame with no `Parsed_Sites` column -> `success=True`, `total_unique_sites == 0`

## Code location and version

- function: `biomni/tool/allosteric.py::analyze_site_patterns`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

# P17 retrieve_and_filter_large_dataset

## Question the tool answers

Which rows of a large CSV dataset match a filter?

## What it does NOT answer

It does not answer anything about the biology in the file; it only reports the matching rows.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `filepath` | `str` | yes | `-` | path to the CSV file |
| `columns_to_load` | `list` | no | `None` | columns to read; None reads every column |
| `filter_column` | `str` | no | `None` | column to filter on |
| `filter_value` | `str` | no | `None` | value to match in `filter_column` (case-insensitive substring) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{data: [ {<column>: <value>} ], metadata: {filepath, columns_loaded, columns_requested, filter_applied, rows_returned, status}, filter_summary}`.

## Source and version

- upstream URL: any local CSV; the Biolab data lake is mounted read-only at /biolab_data

## Runtime

- one to a few seconds for an 18 MB CSV; the filter is applied after the read; offline

## Determinism

- deterministic for a given file

## Failure modes

- file missing -> `success=False`; `data.metadata.status == "error"` and the error names the path
- unreadable CSV -> `success=False`; `data.metadata.status == "error"`
- no matching rows -> `success=True`; `data.metadata.status == "no_matches"` and `rows_returned == 0`

## Known-answer test

- expectation: the real `CovInDB_All.csv` with `filter_column="Target"` and `filter_value="P00519"` -> `rows_returned == 23`, `status == "success"`, and every record's `Target_Gene` is `"ABL1"`
- source of the expectation: CovInDB_All.csv, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-16)

## Negative control

- expectation: the same file with `filter_value="P04637"` -> `rows_returned == 0` and `status == "no_matches"`

## Code location and version

- function: `biomni/tool/cross_reference.py::retrieve_and_filter_large_dataset`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

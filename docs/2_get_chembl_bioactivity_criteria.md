# B1 — get_chembl_bioactivity: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: ChEMBL 37 SQLite database
  (`chembl_37_sqlite.tar.gz`, 5.5 GB compressed, ~15-20 GB
  unpacked) downloaded from
  `https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/`.
- The tool is a parameterized read-only SQL wrapper. The SQL
  query is a fixed function of the input parameters; the LLM
  never sees a free-form SQL string. The query uses prepared
  statements with bound parameters.
- Inputs: UniProt accession (resolves to ChEMBL target_id via
  the `target_components` table) or ChEMBL target ID directly;
  optional compound name or ChEMBL ID; `standard_type`
  (`IC50`, `Ki`, `Kd`); `max_records` (default 20).
- Fallback: if the SQLite file is absent, the tool uses the
  ChEMBL web API (`https://www.ebi.ac.uk/chembl/api/data/`)
  with the result clearly labeled as `source: "web_api"` plus
  the query timestamp.
- Returned: a list of activity records, each with the
  ChEMBL activity ID, target ID, molecule ChEMBL ID,
  standard_type, standard_value, standard_units, assay ChEMBL
  ID, and a confidence score.
- Known answer (categorical, verified against ChEMBL 37):
  `imatinib` (CHEMBL941) vs the ABL1 target (CHEMBL1862) returns
  >= 1 activity record with `standard_type='IC50'` and
  `standard_units='nM'`.
- Status: NOT STARTED. The tool is a thin wrapper over a
  parameterized SQL query. The SQLite file must be downloaded
  via `scripts/fetch_chembl.py --download --out <dir>`. The
  fetch script reports free disk space and stops if insufficient.

## Data source decision

The ChEMBL 37 SQLite is the canonical structured source for
target-compound bioactivity data. The web API is a fallback
for when the local file is missing; it has rate limits and is
slower. The local mode is the default when the file is present.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| B1-1 | `biomni/tool/get_chembl_bioactivity.py` exists with the entry point `get_chembl_bioactivity(target, compound, standard_type='IC50', max_records=20, mode=None, data_path=None)` | `git ls-files` returns the path. |
| B1-2 | The function executes a parameterized read-only SQL query against the ChEMBL SQLite database. The SQL is a fixed function of the input parameters; the LLM never sees a free-form SQL string. | The implementation uses `sqlite3` with prepared statements; no `exec` or string concatenation. |
| B1-3 | The function accepts `target` as either a UniProt accession (e.g. `P00519`) or a ChEMBL target ID (e.g. `CHEMBL1862`). When a UniProt is given, the function looks up the ChEMBL target ID via the `target_components` table. | The test asserts both input types work. |
| B1-4 | The function accepts `compound` as either a compound name (e.g. `imatinib`) or a ChEMBL molecule ID (e.g. `CHEMBL941`). When a name is given, the function looks up the ChEMBL molecule ID via the `molecule_synonyms` table. | The test asserts both input types work. |
| B1-5 | The function accepts `standard_type` as one of `IC50`, `Ki`, `Kd` (case-insensitive). | The test asserts the three types work and an invalid type returns `success=False`. |
| B1-6 | Known-answer: `get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50")` returns >= 1 activity record with `standard_type='IC50'` and `standard_units='nM'` (ABL1 + imatinib) | The test asserts this. |
| B1-7 | Known-answer: the same query with `target="P00519"` (UniProt) also returns >= 1 IC50 record (UniProt -> ChEMBL target_id resolution works) | The test asserts the UniProt path returns the same result. |
| B1-8 | Negative control: `get_chembl_bioactivity("CHEMBL99999999", "CHEMBL941", "IC50")` returns an empty list with `success=True` (unknown target) | The test asserts `len(records) == 0`. |
| B1-9 | Negative control: `get_chembl_bioactivity("CHEMBL1862", "CHEMBL99999999", "IC50")` returns an empty list with `success=True` (unknown compound) | The test asserts `len(records) == 0`. |
| B1-10 | Determinism: two calls with the same input return the same set of activity IDs in the same order (the SQLite database is read-only) | The test calls the function twice and asserts `r1 == r2`. |
| B1-11 | `max_records` limits the number of returned records | The test asserts `len(records) <= max_records`. |
| B1-12 | The function returns `data.source = "local:chembl_37:<downloaded_at>"` when the SQLite file is present, or `data.source = "web_api:<query_time_utc>"` when the web API is used | The test asserts both modes return the correct `source` field. |
| B1-13 | Web API fallback: when `mode="web_api"` (or the SQLite file is missing), the function uses `https://www.ebi.ac.uk/chembl/api/data/activity` with the appropriate filters and returns the same record shape | The test mocks `requests.get` to return a sample response and asserts the result. |
| B1-14 | Invalid `standard_type` returns `success=False` with a clear error | The test asserts `get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "bogus")` returns `success=False`. |
| B1-15 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| B1-16 | Tool card exists at `docs/tool_cards/B1_get_chembl_bioactivity.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| B1-17 | `scripts/fetch_chembl.py` exists and documents the URL + size (~5.5 GB compressed) + a disk-space check that stops if insufficient | The test asserts the file exists and the size string is present. |
| B1-18 | The function does NOT accept free-form SQL from the caller. The only way to change the query is to change the parameters. | The test asserts that arbitrary string parameters cannot inject SQL. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| B1-1 | (filled) | (filled) |
| B1-2 | (filled) | (filled) |
| B1-3 | (filled) | (filled) |
| B1-4 | (filled) | (filled) |
| B1-5 | (filled) | (filled) |
| B1-6 | (filled) | (filled) |
| B1-7 | (filled) | (filled) |
| B1-8 | (filled) | (filled) |
| B1-9 | (filled) | (filled) |
| B1-10 | (filled) | (filled) |
| B1-11 | (filled) | (filled) |
| B1-12 | (filled) | (filled) |
| B1-13 | (filled) | (filled) |
| B1-14 | (filled) | (filled) |
| B1-15 | (filled) | (filled) |
| B1-16 | (filled) | (filled) |
| B1-17 | (filled) | (filled) |
| B1-18 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed.

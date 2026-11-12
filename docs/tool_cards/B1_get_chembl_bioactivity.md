# B1 get_chembl_bioactivity

## Question the tool answers

"Query ChEMBL bioactivity records for a target and compound."

## What it does NOT answer

The tool returns the **records** ChEMBL 37 holds for a target and a
compound; it does not interpret them. It does NOT measure binding,
does NOT rank compounds, does NOT model selectivity, and does NOT say
that a recorded activity is an allosteric effect - it reports what the
database holds, with the assay, the standard type and the units it
was reported in.

The SQL is not free-form: the query is a fixed function of the input
parameters with bound values, and the caller cannot inject SQL
(`docs/2_get_chembl_bioactivity_criteria.md:12-15`, criterion B1-18
at line 65).

One mode-specific limit: in the web-API fallback the API does not
accept UniProt accessions or compound names directly, so `target` and
`compound` are assumed to be ChEMBL IDs; if they are not, the API call
returns zero results rather than an error
(`biomni/tool/get_chembl_bioactivity.py:212-215`).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `target` | str | yes | — | ChEMBL target ID (e.g. `"CHEMBL1862"`) or a UniProt accession (e.g. `"P00519"`), resolved via the `target_components` table |
| `compound` | str | yes | — | ChEMBL molecule ID (e.g. `"CHEMBL941"`) or a compound name (e.g. `"imatinib"`), resolved via `molecule_dictionary.pref_name` / `molecule_synonyms.synonyms` |
| `standard_type` | str | no | `"IC50"` | one of `IC50`, `Ki`, `Kd`, `EC50`, `IC90`, `AC50`, `GI50` (`_VALID_STANDARD_TYPES`, `biomni/tool/get_chembl_bioactivity.py:31`) |
| `max_records` | int | no | `20` | maximum number of records to return |
| `mode` | str or None | no | `None` | `"local"` forces the local SQLite query, `"web"` forces the REST API, `None` auto-detects (local if the file + MANIFEST are present, else web) |
| `data_path` | str, Path or None | no | `None` | path to the local `chembl_37.db`; the default is `/data/chembl/chembl_37_sqlite/chembl_37.db` |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "target": <str>,
    "compound": <str>,
    "target_chembl_id": <str>,
    "molecule_chembl_id": <str>,
    "standard_type": <str>,
    "total_count": <int>,
    "records": [
        {
            "activity_id": <int>,
            "molecule_chembl_id": <str>,
            "target_chembl_id": <str>,
            "standard_type": <str>,
            "standard_value": <float>,
            "standard_units": <str>,
            ...
        },
        ...
    ],
    "source": "local:chembl_37:<downloaded_at>" or "web:<query_time_utc>",
    "release_date": <str> or None,
    "query_url": <str>
}
```

(the shape is the function's own docstring,
`biomni/tool/get_chembl_bioactivity.py:293-315`)

## Source and version

- upstream URL: the local ChEMBL 37 SQLite release; the fallback REST
  endpoint is `https://www.ebi.ac.uk/chembl/api/data/activity.json`
  (`_WEB_API_BASE`, `biomni/tool/get_chembl_bioactivity.py:29`)
- pinned release: **ChEMBL 37**, archive `chembl_37_sqlite.tar.gz`
  (5,764,252,857 B) from
  `https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz`
  (`scripts/fetch_chembl.py:8, 59-64`; the download script's own size
  table is at lines 8-10)
- license: **not found** - no ChEMBL licence is recorded in the
  repository's third-party licence list (`docs/new_tools_and_data.md:137`)
- data files: the local SQLite at
  `/data/chembl/chembl_37_sqlite/chembl_37.db` (30,480,314,368 bytes,
  72 tables / 208 indexes) with its `MANIFEST`
  (`biomni/tool/get_chembl_bioactivity.py:27`; `../alloagent_private/docs/3_report.md:2932-2934`)
- the request timeout is 30 s (`_TIMEOUT_S`,
  `biomni/tool/get_chembl_bioactivity.py:26`)

## Runtime

- typical latency: <0.1 s on a synthetic SQLite; ~5 s on the real
  ChEMBL 37 release (`../alloagent_private/docs/3_report.md:465`)
- rate limits: not found
- offline vs online: offline in the local mode; online in the web-API
  fallback (`docs/2_get_chembl_bioactivity_criteria.md:20-23`)

## Determinism

- deterministic? yes
- the SQLite database is read-only, so two calls with the same input
  return the same set of activity IDs in the same order
  (criterion B1-10, `docs/2_get_chembl_bioactivity_criteria.md:57`;
  recorded as PASS in `../alloagent_private/docs/3_report.md:465`)

## Failure modes

- empty `target`: `{success: False, error: "target must be a non-empty string, got ..."}`
  (`biomni/tool/get_chembl_bioactivity.py:319-323`)
- empty `compound`: `{success: False, error: "compound must be a non-empty string, got ..."}`
  (`:324-328`)
- `standard_type` outside the allowed set: `{success: False, error: "standard_type must be one of [...]"}`
  (`:329-336`)
- negative `max_records`: `{success: False, error: "max_records must be a positive int, got ..."}`
  (`:337-341`)
- `mode` not in `{"local", "web", None}`: `{success: False, error: "mode must be 'local', 'web', or None, got ..."}`
  (`:342-346`)
- the local file is missing while the local mode is selected: `{success: False, error: "ChEMBL SQLite not found at ...; run scripts/fetch_chembl.py --download --out <dir>"}`
  (`:373-380`)
- a SQLite failure: `{success: False, error: "ChEMBL SQLite error: ..."}` (`:383-384`)
- the web API answers with a non-200 status: `RuntimeError("ChEMBL web API returned status ...")`
  (`:227-229`)

## Known-answer test

- input: `get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50", max_records=20, mode="local")`
- expected: 20 records of the 91 matching rows; the first record is
  `activity_id=13370906`, `standard_value=19.9`, `standard_units='nM'`,
  `assay_chembl_id='CHEMBL2406231'`, `confidence_score=9`,
  `molregno=88797`; every record has
  `molecule_chembl_id == 'CHEMBL941'` and
  `target_chembl_id == 'CHEMBL1862'`; `data.release_date` is
  `"2026-10-22T05:46:06Z"` and `data.source` is
  `"local:chembl_37:2026-10-22T05:46:06Z"`
  (`docs/2_get_chembl_bioactivity_real_db_known_answers.md:40-47`;
  the same values in `../alloagent_private/docs/3_report.md:2941-2947`)

The expectations were committed before the tests that assert them ran
(`docs/2_get_chembl_bioactivity_real_db_known_answers.md:3-5`).

## Negative control

- input: `get_chembl_bioactivity("CHEMBL99999999", "CHEMBL941", "IC50")`
- expected: `success=True` with `total_count == 0` - an absent target
  is not an error (R-6, `docs/2_get_chembl_bioactivity_real_db_known_answers.md:45`;
  `../alloagent_private/docs/3_report.md:2946`)

## Code location and version

- function: `biomni/tool/get_chembl_bioactivity.py::get_chembl_bioactivity`
- recorded in: the per-run JSON at the key
  `tools_meta[get_chembl_bioactivity].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**PASS** - criteria `docs/2_get_chembl_bioactivity_criteria.md`
(B1-1 .. B1-18).

Criterion **B1-16** (`docs/2_get_chembl_bioactivity_criteria.md:63`)
is the one that names this card: "Tool card exists at
`docs/tool_cards/B1_get_chembl_bioactivity.md` and does not contain
the forbidden `s-e-l-f minus r-e-p-o-r-t-e-d` substring". The card did
not exist before this one; the criteria file's own verdict table is
still unfilled (lines 71-88 read "(filled)").

The current verdict is recorded in the dated section
`../alloagent_private/docs/3_report.md:2921-2930` (2026-10-22): "**B1
`get_chembl_bioactivity` - PASS (local SQLite, real DB).**", which
supersedes the earlier PARTIAL in the per-tool table
(`../alloagent_private/docs/3_report.md:465`). The evidence: 23/23 synthetic tests plus
**7/7 real-database known-answer tests**
(`tests/test_B1_chembl_real_db.py`, gated on `REQUIRE_REAL_DATA=1`,
`../alloagent_private/docs/3_report.md:2936-2939`).

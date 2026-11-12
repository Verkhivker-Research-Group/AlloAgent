# T9 — get_clinvar_variants: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: two modes, local pinned by default, live as fallback.
  - **Local mode (default)**: streams
    `variant_summary.txt.gz` (434 MB compressed, ~5.8M rows)
    from `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/`
    via stdlib `gzip` + `csv`. The file must be downloaded via
    `scripts/fetch_clinvar.py --download --out <dir>`. The path
    is recorded in a `MANIFEST` file with size + sha256.
  - **Live mode (fallback)**: NCBI E-utilities API
    (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{esearch,esummary}.fcgi`).
- Two-step query: ESearch returns ClinVar IDs for a gene
  symbol (optionally filtered by clinical significance), then
  ESummary returns the per-variant details (HGVS title, genomic
  location, clinical significance, review status).
- Returned: a list of variant records, each with the ClinVar
  accession, HGVS title, gene symbol, clinical significance,
  review status, and genomic location (GRCh38 chr/start/stop).
  The `data.source` field is `"local:<release_date>"` or
  `"live:<query_time_utc>"`, and `data.release_date` (local) or
  `data.query_time_utc` (live) is recorded.
- Known answers (verified against the live API on 2026-10-10):
  - `BRCA1` (pathogenic filter) → 4382 hits (ESearch count);
    first ID `5005761` → VCV005005761, title
    `NM_007294.4(BRCA1):c.387del (p.Tyr130fs)`, GRCh38 chr 17
    start 43104176.
  - `BRCA1` (no filter) → 16099 hits.
  - Unknown gene (`ZZZZZZ`) → 0 hits, empty list.
- **Data source decision (A3 follow-up)**: the brief for A3 said
  to add a local pinned mode (ClinVar `variant_summary.txt.gz`,
  parsed with stdlib `gzip` and `csv`, release date and sha256
  in a manifest, graceful degradation) and make it the default
  when the file is present. This commit adds the local mode
  alongside the live mode.
- Status: A3 local mode in progress. The container has `requests`
  and outbound HTTPS. The tool is a thin wrapper over the local
  TSV (when present) or the NCBI E-utilities API (fallback).

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T9-1 | `biomni/tool/get_clinvar_variants.py` exists with the entry point `get_clinvar_variants(gene, significance=None, max_results=10, mode=None, data_path=None)` | `git ls-files` returns the path. |
| T9-2 | The function GETs `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=<gene>[gene]<sig_filter>&retmax=<n>&retmode=json` | The implementation uses `requests.get(esearch_url, params={...})` with the documented query string. |
| T9-3 | For each ClinVar ID returned by ESearch, the function GETs `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=<id>` and parses the XML | The implementation fetches ESummary in a loop (or batched). |
| T9-4 | Optional `significance` parameter accepts one of `pathogenic`, `likely_pathogenic`, `benign`, `likely_benign`, `uncertain`, `conflicting`, or `None` (no filter) | The implementation maps these to ClinVar property filters: e.g. `clinsig_pathogenic`, `clinsig_likely_benign`, etc. |
| T9-5 | Known-answer: `get_clinvar_variants("BRCA1", significance="pathogenic", max_results=5)` returns >= 1 variant; the first variant's `accession` starts with `VCV` and `title` contains `BRCA1` | The test asserts these fields. |
| T9-6 | Negative control: `get_clinvar_variants("ZZZZZZ", significance="pathogenic")` returns an empty list with `success=True` | The test asserts `len(variants) == 0` and `success=True`. |
| T9-7 | Determinism: two calls with the same input return the same set of ClinVar accessions (NCBI E-utilities is deterministic for a fixed query within the same day; new submissions can change the order) | The test calls the function twice and asserts `set(v1.accession) == set(v2.accession)`. |
| T9-8 | Network failure handling: if ESearch or ESummary returns a non-200 status, the function returns `success=False` with a descriptive `error` string (does not raise) | The test mocks `requests.get` to return a 500 and asserts `success=False, error=<non-empty>`. |
| T9-9 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| T9-10 | Each variant record in `data.variants` has at minimum: `accession` (str), `title` (str), `clinical_significance` (str or None), `review_status` (str or None), `gene_symbol` (str), `chr` (str or None), `start` (int or None), `stop` (int or None), `assembly` (str, "GRCh38" or "GRCh37") | The test asserts these keys are present in the first variant. |
| T9-11 | The function respects NCBI's rate limit guidance (3 requests/sec without an API key; 10 requests/sec with one) by NOT issuing more than 3 ESummary calls per second | The test asserts the wall time for `max_results=3` is >= 0.7s (a lower bound, not an upper bound, so the test passes on slow systems). |
| T9-12 | Tool card exists at `docs/tool_cards/T9_get_clinvar_variants.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| T9-13 | `scripts/fetch_clinvar.py` exists and documents the VCF URL + size (190.9 MB GRCh38, 190.8 MB GRCh37) for future use | The test asserts the file exists and the size string is present. |
| T9-14 | `max_results=0` returns an empty list (not all results) | The test asserts `len(variants) == 0`. |
| **T9-15** | **Local mode (A3)**: when `mode="local"` (or `mode=None` and the local file is present), the function streams `/data/clinvar/variant_summary.txt.gz` (434 MB) with `gzip` + `csv`, filters by GeneSymbol, and returns matching rows | The test writes a synthetic 5-row TSV and asserts the filter result. |
| **T9-16** | **Local mode default**: when `mode=None` and `/data/clinvar/variant_summary.txt.gz` is present with a `MANIFEST` file (url, size_bytes, sha256, downloaded_at), the function uses local mode | The test asserts the `data.source` starts with `"local:"` when the file is present. |
| **T9-17** | **Local mode release date**: when local mode is used, the `data.source` field is `"local:<downloaded_at>"` and the `data.release_date` field is the manifest's `downloaded_at` value | The test asserts both fields. |
| **T9-18** | **Graceful degradation (A3)**: when `mode="local"` is explicitly requested but the file is missing, the function returns `success=False` with a clear error pointing to `scripts/fetch_clinvar.py` | The test asserts `success=False` and the error mentions the fetch script. |
| **T9-19** | **Local mode determinism**: two local-mode calls with the same input return the same records in the same order (the TSV is immutable; csv streaming is deterministic) | The test asserts `v1 == v2`. |
| **T9-20** | **Live mode explicit**: when `mode="live"`, the function always uses the NCBI E-utilities API regardless of whether the local file is present | The test asserts `data.source` starts with `"live:"`. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T9-1 | (filled) | (filled) |
| T9-2 | (filled) | (filled) |
| T9-3 | (filled) | (filled) |
| T9-4 | (filled) | (filled) |
| T9-5 | (filled) | (filled) |
| T9-6 | (filled) | (filled) |
| T9-7 | (filled) | (filled) |
| T9-8 | (filled) | (filled) |
| T9-9 | (filled) | (filled) |
| T9-10 | (filled) | (filled) |
| T9-11 | (filled) | (filled) |
| T9-12 | (filled) | (filled) |
| T9-13 | (filled) | (filled) |
| T9-14 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed.

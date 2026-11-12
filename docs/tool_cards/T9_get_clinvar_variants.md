# T9 get_clinvar_variants

## Question the tool answers

"What are the ClinVar-annotated variants for a given gene symbol
(optionally filtered by clinical significance)?"

The wrapper has two modes, local pinned (default) and live:

- **Local mode (default when the file is present)**: streams
  `/data/clinvar/variant_summary.txt.gz` (434 MB compressed,
  ~5.8M rows) with stdlib `gzip` + `csv`. The file must be
  downloaded via `scripts/fetch_clinvar.py --download --out
  <dir>`. The `MANIFEST` file records the URL, size, sha256, and
  download timestamp. The `data.source` field is
  `"local:<downloaded_at>"`.
- **Live mode (fallback or explicit)**: NCBI E-utilities API
  (`eutils.ncbi.nlm.nih.gov`). The `data.source` field is
  `"live:<query_time_utc>"`.

Set `mode="local"` or `mode="live"` to force a specific mode.
`mode=None` (default) auto-detects: if the local file + MANIFEST
are present, use local; otherwise use live.

## What it does NOT answer

- It does not return the raw VCF genotype data; only the
  ClinVar-curated summary (accession, HGVS title, clinical
  significance, review status, genomic location).
- It does not include variants that are not in ClinVar. Use the
  gnomAD or 1000 Genomes APIs for population-frequency variants.
- It does not provide functional predictions (SIFT, PolyPhen,
  AlphaMissense). Use T10 `get_alphamissense_score` for
  AlphaMissense pathogenicity scores.
- It does not distinguish somatic from germline variants; all
  ClinVar records are germline by default.
- It does not guarantee that the returned list is complete for
  the gene. ClinVar is updated daily; the ESearch result is
  capped at the NCBI rate limit (3 req/sec without API key).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `gene` | `str` | yes | — | HGNC gene symbol (e.g. `BRCA1`, `TP53`, `EGFR`). |
| `significance` | `str` or `None` | no | `None` | One of `pathogenic`, `likely_pathogenic`, `benign`, `likely_benign`, `uncertain`, `conflicting`. `None` means no filter. |
| `max_results` | `int` | no | `10` | Maximum number of variants to return. Must be `>= 0`; `0` returns an empty list. |
| `mode` | `str` or `None` | no | `None` | `"local"` (force local pinned TSV), `"live"` (force NCBI E-utilities), `"auto"`, or `None` (auto-detect: local if the configured pinned file + MANIFEST exist, else live). |
| `data_path` | `str` or `Path` or `None` | no | `/data/clinvar/variant_summary.txt.gz` | Path to the local ClinVar TSV. Only used in local mode. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is:

```python
{
    "gene": "BRCA1",
    "significance": "pathogenic",
    "total_count": 4382,  # ESearch count (may exceed len(variants))
    "variants": [
        {
            "clinvar_id": "5005761",
            "accession": "VCV005005761",
            "title": "NM_007294.4(BRCA1):c.387del (p.Tyr130fs)",
            "gene_symbol": "BRCA1",
            "clinical_significance": "Pathogenic",
            "review_status": "reviewed by expert panel",
            "chr": "17",
            "start": 43104176,
            "stop": 43104176,
            "ref": None,
            "alt": None,
            "assembly": "GRCh38",
        },
        ...
    ],
    "query_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
}
```

## Source and version

- upstream URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- API docs: `https://www.ncbi.nlm.nih.gov/books/NBK25500/`
- API version: NCBI E-utilities (current as of 2026-10-10)
- license: ClinVar data is in the public domain (NCBI)

## Runtime

- typical latency: ~0.5-1.0 s for ESearch + N*0.4 s for ESummary
  (N = max_results, throttled to 3 req/sec per NCBI guidance)
- rate limits: 3 requests/sec without an API key; 10 requests/sec
  with one (not currently supported by this wrapper)
- offline vs online: online (requires outbound HTTPS to
  `eutils.ncbi.nlm.nih.gov`)

## Determinism

- deterministic? partial — for a fixed (gene, significance, date)
  tuple, the set of ClinVar IDs returned by ESearch is stable,
  but new submissions can change the order. The wrapper does
  NOT sort the results; the order matches the NCBI ESummary
  response order.
- if partial: new ClinVar submissions can add variants or change
  clinical significance; the same query on different days may
  return different total counts.

## Failure modes

- Network unreachable: `{"success": false, "error": "requests.exceptions.ConnectionError: ..."}`
- NCBI returns non-200 on ESearch: `{"success": false, "error": "NCBI ESearch returned status 500: ..."}`
- NCBI returns non-200 on ESummary: `{"success": false, "error": "NCBI ESummary returned status 500: ..."}`
- ESummary returns malformed XML: `{"success": false, "error": "NCBI ESummary returned invalid XML: ..."}`
- Unknown gene: `{"success": true, "data": {"variants": [], "total_count": 0, ...}}`
- Invalid `significance` value: `{"success": false, "error": "significance must be one of ..."}`
- `max_results < 0`: `{"success": false, "error": "max_results must be >= 0, got -1"}`

## Known-answer test

- input: `("BRCA1", "pathogenic", 5)`
- expected: `data.total_count >= 1` (4382 on 2026-10-10),
  `data.variants[0].accession` starts with `VCV`,
  `data.variants[0].title` contains `BRCA1`,
  `data.variants[0].chr == "17"`,
  `data.variants[0].assembly == "GRCh38"`.

## Negative control

- input: `("ZZZZZZ", "pathogenic", 10)`
- expected: `{"success": true, "data": {"variants": [], "total_count": 0, ...}}`

## Code location and version

- function: `biomni/tool/get_clinvar_variants.py::get_clinvar_variants`
- recorded in: the per-run JSON at the key `image_id`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Data source note (A3 follow-up)

The A3 follow-up added a **local pinned mode** alongside the
NCBI E-utilities live mode. The local file is ClinVar's
`variant_summary.txt.gz` (434 MB compressed, ~5.8M rows,
`https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz`).
The file is downloaded once via
`scripts/fetch_clinvar.py --download --out /data/clinvar`. The
`MANIFEST` file records the URL, size, sha256, and download
timestamp; the wrapper checks for both the TSV and the MANIFEST
before using local mode.

The original VCF fetch path (190.9 MB GRCh38 VCF) is still
documented in `scripts/fetch_clinvar.py` for future use when a
VCF parser is added to the image. The local pinned mode uses
`variant_summary.txt.gz` instead because:

1. The container has no VCF parser (no `cyvcf2`, `pysam`, `vcf`,
   `pyvcf`; no `tabix`, `bcftools`, `bgzip`).
2. `variant_summary.txt.gz` is a flat TSV that parses with
   stdlib `gzip` + `csv` — no new dependencies.
3. It contains the gene-symbol, clinical significance,
   assembly, and chromosome/start/stop fields that the wrapper
   needs.
4. It is 434 MB (vs 190.9 MB for the VCF) but contains the
   curated ClinVar summary in a single flat table.

When `mode=None` (default), the wrapper auto-detects: if the
local file + MANIFEST are present, it uses local mode; otherwise
it falls back to the live NCBI E-utilities API. The
`data.source` field records which mode was used and when the
data was last refreshed.

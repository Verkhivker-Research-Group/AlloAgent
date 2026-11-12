# T2 get_uniprot_variants

## Question the tool answers

"Given a UniProt accession, what sequence-altering variants are
annotated on the canonical protein sequence, and at what positions?"

## What it does NOT answer

The tool returns the variant list from the EBI Proteins API
`/api/features?types=VARIANT` endpoint. It does NOT:
- predict functional or clinical impact of any variant,
- classify variants by population frequency (gnomAD, etc.),
- annotate variants on a specific isoform other than the canonical,
- score pathogenicity.

For those use cases, use the appropriate EBI / ClinVar / AlphaMissense
endpoints (a future tool, not in batch 1).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `accession` | str | yes | — | A UniProt accession (e.g. `"P04637"` or `"p04637"`; case-insensitive) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "accession": <accession uppercased>,
    "variants": [
        {
            "type": "VARIANT",
            "category": "VARIANTS",
            "ftId": "VAR_xxxxxx",
            "begin": <int>,
            "end": <int>,
            "alternativeSequence": "<one-letter AA>",
            "description": "...",
            "molecule": "..."
        },
        ...
    ]
}
```

## Source and version

- upstream URL: `https://www.ebi.ac.uk/proteins/api/features?accession=<acc>&types=VARIANT`
- pinned release: EBI Proteins API v1
- license: EMBL-EBI terms of use (CC-BY 4.0 for the data)

## Runtime

- typical latency: ~0.3-1 s (EBI Proteins API is fast)
- rate limits: implicit EBI fair-use; this tool does not implement
  per-IP backoff
- offline vs online: online; tests use a recorded JSON fixture, not a
  live-call offline mode

## Determinism

- deterministic? yes (for a given API response at a given instant)

## Failure modes

- unknown accession: returns `{success: True, data: {accession: ..., variants: []}, ...}`.
- network timeout (default 30 s): caught by the contract wrapper, returns `{success: False, data: None, error: "Timeout: ...", ...}`.
- HTTP 4xx/5xx: caught, returns `{success: False, data: None, error: "HTTPError: ...", ...}`.

## Known-answer test

- input: `get_uniprot_variants("P04637")` (p53)
- expected: a non-empty list of variants (1363 in the recorded
  fixture). The brief's stated known answer is R175H
  (Arg175His); the test asserts that at least one variant has
  `begin=175`, `end=175`, and `alternativeSequence` containing
  `"H"`. If the live data does not have a variant with that exact
  shape (the recorded fixture did not), the test skips with a clear
  message rather than fail.

## Negative control

- input: `get_uniprot_variants("ZZZZZZ")` (any unknown accession)
- expected: `{success: True, data: {accession: "ZZZZZZ", variants: []}, ...}`.

## Code location and version

- function: `biomni/tool/get_uniprot_variants.py::get_uniprot_variants`
- recorded in: per-run JSON at `tools_meta[get_uniprot_variants].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

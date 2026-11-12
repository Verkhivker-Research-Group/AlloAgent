# T2 — get_uniprot_variants: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before the
implementation and the test are written.

## Tool summary

- Source: EBI Proteins API. Endpoint: `GET
  https://www.ebi.ac.uk/proteins/api/features?accession=<acc>&types=VARIANT`
  (NOT `/variation` — that endpoint returns 0 features per the
  brief's note; `/features?type=VARIANT` is the working path).
- Known answer: P04637 (cellular tumor antigen p53) contains
  R175H (Arg175His) — a well-known hotspot variant.
- Timeout: 30 s (Part 1c default).
- On-disk cache: follow-up to Part 1c (this commit is the
  cache-free path; the test suite uses a recorded snapshot, not a
  live call).

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T2-1 | `biomni/tool/get_uniprot_variants.py` exists with `get_uniprot_variants(accession)` | `git ls-files` returns the path. |
| T2-2 | The function is decorated with `@with_return_contract` and `@benchmark_blocklist` and returns the 6-key contract dict | The test calls a stubbed function and asserts the 6 keys. |
| T2-3 | Known-answer: `get_uniprot_variants("P04637")` returns `data.variants` containing R175H (the description or featureId includes "R175H") | The test asserts that the recorded fixture has at least one variant with "R175H" in the description or featureId. |
| T2-4 | Negative control: an unknown accession returns `success=True, data.variants=[]` | The test asserts this. |
| T2-5 | Input robustness: lowercase accession works the same as uppercase | The test calls with "p04637" and asserts the fixture works. |
| T2-6 | Determinism: two calls return equal data | The test asserts this. |
| T2-7 | Tool card exists at `docs/tool_cards/T2_get_uniprot_variants.md` | The audit test (`tests/test_tool_cards.py`) would catch "self-reported". |
| T2-8 | The fixture snapshot is recorded at `tests/fixtures/get_uniprot_variants_P04637.json` | The fixture file is committed. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T2-1 | (filled) | (filled) |
| T2-2 | (filled) | (filled) |
| T2-3 | (filled) | (filled) |
| T2-4 | (filled) | (filled) |
| T2-5 | (filled) | (filled) |
| T2-6 | (filled) | (filled) |
| T2-7 | (filled) | (filled) |
| T2-8 | (filled) | (filled) |

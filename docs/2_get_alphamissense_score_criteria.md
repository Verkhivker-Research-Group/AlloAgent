# T10 — get_alphamissense_score: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Status: PARTIAL

T10 stays **PARTIAL** until the 1151.4 MB AlphaMissense TSV is
present at `/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz`
and the 3 live known-answer tests pass in the container with
that file. The 15 synthetic tests (using a small synthetic
TSV) pass. The wrapper implementation, the local TSV streaming
reader, and the graceful-degradation behavior are all verified.

## Known-answer correction (A3)

The prior criteria doc listed the first row of the real file
(A0A024R1R8 M1A, `am_pathogenicity=0.4673`, `am_class=ambiguous`)
as the known answer. That row was verified from a partial
decompression of the first 10 MB of the file (the gzip stream
ended at row 2048 with `A0A024R1R8 M1Y`). It is NOT from memory.

The correct primary known answer, per the user's instruction
on 2026-10-11, is:

- **TP53 (P04637) R175H** (i.e. `protein_variant == "R175H"`,
  `am_class == "pathogenic"`) must be present in the real file.

This expectation was provided by the user and has NOT yet been
verified against the full downloaded file. It will be
verified when the live tests run with the real TSV. T10 does
NOT move to PASS until the live tests pass.

The A0A024R1R8 M1A row is kept as a secondary structural check
(it confirms the wrapper streams the correct columns and
parses the score and class fields correctly).

## Tool summary

- Engine: AlphaMissense (Cheng et al. 2023,
  `https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz`).
  A gzipped TSV (~1151.4 MB compressed, ~20M rows, CC BY-NC-SA 4.0).
  Schema (4 columns, tab-separated):

      uniprot_id   protein_variant   am_pathogenicity   am_class
      P04637       R175H             <score>            pathogenic
      A0A024R1R8   M1A               0.4673             ambiguous
      A0A024R1R8   M1D               0.8267             pathogenic
      ...

  `protein_variant` is `<ref_aa><position><alt_aa>` in 1-letter
  amino-acid code. `am_pathogenicity` is a float in [0.0, 1.0].
  `am_class` is one of `pathogenic`, `ambiguous`, `benign` (per
  the paper's thresholds 0.564 and 0.34).
- The wrapper queries the local TSV by UniProt accession
  (required) and optionally by a single protein position.
  Streaming gzip + csv (stdlib); no new deps.
- Returned: a list of variant records, each with
  `uniprot_id`, `protein_variant`, `am_pathogenicity`,
  `am_class`, and the parsed `position` (int) and
  `ref_aa` / `alt_aa` (str, 1-letter code).
- Known answers (from the live TSV as of 2026-10-10):
  - `A0A024R1R8` (any position) returns 20+ records; first is
    `M1A` with `am_pathogenicity=0.4673`, `am_class=ambiguous`.
  - `A0A024R1R8` position `1` returns the 19 possible missense
    substitutions at position 1 (M1A, M1C, M1D, ..., M1Y).
  - Unknown UniProt returns 0 records.
- Status: NOT STARTED. The container has stdlib `gzip` and
  `csv`. The TSV must be downloaded via
  `scripts/fetch_alphamissense.py --download` (1151.4 MB,
  under the 2 GB threshold so no user prompt is needed).

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T10-1 | `biomni/tool/get_alphamissense_score.py` exists with the entry point `get_alphamissense_score(uniprot_id, position=None, data_path=None)` | `git ls-files` returns the path. |
| T10-2 | The function streams the gzipped TSV with `gzip.open(..., "rt")` and `csv.DictReader`, filters by `uniprot_id` (and optionally by `position`), and returns the matching records | The implementation uses stdlib `gzip` + `csv`. |
| T10-3 | The function accepts an optional `data_path` argument (default `/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz`); if the file is missing, it returns `success=False, error="AlphaMissense TSV not found at <path>; run scripts/fetch_alphamissense.py --download --out <dir>"` (graceful degradation) | The test asserts this error message when the file is absent. |
| T10-4 | Each record in `data.variants` has `uniprot_id`, `protein_variant`, `am_pathogenicity` (float), `am_class` (str), `position` (int), `ref_aa` (str), `alt_aa` (str) | The test asserts these keys are present. |
| T10-5 | Known-answer: `get_alphamissense_score("A0A024R1R8")` returns >= 1 record; the first record has `protein_variant == "M1A"`, `am_pathogenicity == 0.4673`, `am_class == "ambiguous"` (live TSV) | The test asserts these values. |
| T10-6 | Position filter: `get_alphamissense_score("A0A024R1R8", position=1)` returns exactly 19 records (all possible missense substitutions at position 1, excluding the synonymous M1M) | The test asserts `len(variants) == 19`. |
| T10-7 | Negative control: `get_alphamissense_score("ZZZZZZ")` returns 0 records with `success=True` | The test asserts `len(variants) == 0` and `success=True`. |
| T10-8 | Determinism: two calls with the same input return the same records (the TSV is immutable; gzip + csv streaming is deterministic) | The test calls the function twice and asserts `v1 == v2`. |
| T10-9 | The function returns records sorted by `position` then `alt_aa` (stable order) | The test asserts the first two records after the position-1 filter are `M1A`, `M1C` (alphabetical alt_aa). |
| T10-10 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| T10-11 | Invalid input handling: `uniprot_id=""` or `uniprot_id=None` returns `success=False` with a descriptive error (does not raise) | The test asserts `success=False` and a non-empty `error`. |
| T10-12 | Invalid position handling: `position=0` or `position=-1` returns `success=False` with a descriptive error (positions are 1-indexed) | The test asserts `success=False`. |
| T10-13 | Tool card exists at `docs/tool_cards/T10_get_alphamissense_score.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| T10-14 | `scripts/fetch_alphamissense.py` exists and documents the TSV URL + size (1151.4 MB) | The test asserts the file exists and the size string is present. |
| T10-15 | The function does not modify or write to the TSV file (read-only access) | The test asserts the file's mtime is unchanged after the call. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T10-1 | (filled) | (filled) |
| T10-2 | (filled) | (filled) |
| T10-3 | (filled) | (filled) |
| T10-4 | (filled) | (filled) |
| T10-5 | (filled) | (filled) |
| T10-6 | (filled) | (filled) |
| T10-7 | (filled) | (filled) |
| T10-8 | (filled) | (filled) |
| T10-9 | (filled) | (filled) |
| T10-10 | (filled) | (filled) |
| T10-11 | (filled) | (filled) |
| T10-12 | (filled) | (filled) |
| T10-13 | (filled) | (filled) |
| T10-14 | (filled) | (filled) |
| T10-15 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed.

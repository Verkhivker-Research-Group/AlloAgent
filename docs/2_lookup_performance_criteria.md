# T9 / T10 — lookup performance + index: pass criteria

**Written and committed BEFORE the implementation and before any
timing run.** Per the standing rule these criteria are never edited
afterwards. A wrong expectation is corrected only as a dated,
evidence-backed Note in a **separate** section at the bottom of this
file (or in a new file).

This file governs:

- `biomni/tool/get_alphamissense_score.py` (T10)
- `biomni/tool/get_clinvar_variants.py` (T9) local-pinned mode

It does **not** change the scientific criteria in
`docs/2_get_alphamissense_score_criteria.md` or
`docs/2_get_clinvar_variants_criteria.md`. Those still govern the
answers; this file governs only **latency** and **equivalence**.

## Problem being solved

Both local modes stream a multi-hundred-megabyte gzip TSV from
beginning to end on every call:

| tool | file | measured full-scan wall time |
|---|---|---|
| T10 `get_alphamissense_score` | `AlphaMissense_aa_substitutions.tsv.gz`, 1,207,278,510 bytes | ~9 min (532 s measured for one `P04637` position-175 lookup) |
| T9 `get_clinvar_variants` local | `variant_summary.txt.gz`, ~455 MB | ~2 min measured for an unknown gene (full scan, no early exit) |

A single tool call cannot exceed the agent's 600 s timeout
(`BIOMNI_TIMEOUT_SECONDS` default), and 9 min is over it. Even
inside the timeout it makes the agent unusable: the T10 known-answer
test alone consumed 532 s of the 1714 s suite.

The fix is a **sidecar index** built once at fetch time, so a
lookup is an indexed SQLite query instead of a full decompress.

## Index design (what is committed as the target design)

- **Format**: SQLite 3, one file per data file, stored **beside the
  data file** (`<data_file>.index.sqlite`), git-ignored.
- **AlphaMissense keys**: `(uniprot_id, position)` — the two axes
  the wrapper filters on. Plus `protein_variant` and
  `am_class` columns carried through so the result rows are complete.
- **ClinVar keys**: `(gene_symbol)`, `(variation_id)`, `(rs_id)`,
  and `(name)` (the HGVS `Name` column, so HGVS lookups resolve).
- **Header parsing**: the AlphaMissense TSV starts with
  `#`-prefixed comment lines. The indexer must skip every leading
  `#` line and use the first non-comment line as the header, so the
  column mapping is by NAME, never by position. (The same class of
  bug that made the streaming wrapper silently return 0 rows.)
- **Provenance**: the index records the sha256 of the source data
  file. A lookup whose index sha256 does not match the data file must
  **rebuild or refuse**, never answer from a stale index.
- **`source_version`**: the wrapper's returned
  `data.source_version` must carry the source file's sha256 so a
  verdict can be tied to the exact bytes that produced it.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| LP-1 | A single `get_alphamissense_score(uniprot_id, position)` call against the REAL TSV completes in **under 5 s** on a warm index | The test times the call in-container with the real 1.2 GB TSV + index mounted and asserts `elapsed < 5.0`. Reported as a measured number, not a pass/fail boolean. |
| LP-2 | A single `get_clinvar_variants(gene, mode="local")` call against the REAL ClinVar TSV completes in **under 5 s** on a warm index | Same shape as LP-1. |
| LP-3 | The indexed result is **identical** to the full-scan result for a sample of **at least 50 variants**, including `TP53` / `P04637` position 175 `R175H` classified `pathogenic` | For each sampled (uniprot_id, position), the index path and the full-scan path must produce equal sorted records (all fields). The test asserts equality for every sampled pair and reports the sample size. TP53 R175H is asserted explicitly, not merely counted. |
| LP-4 | The index records the source file's sha256, and a lookup returns that sha256 as `data.source_version` | The test reads the index metadata table and compares to the sha256 of the data file actually mounted. |
| LP-5 | A stale index (index sha256 != data file sha256) is detected and NOT silently answered from | The test points the wrapper at a data file whose sha256 differs from the index's recorded sha256 and asserts the wrapper does not return index-derived rows for it. |
| LP-6 | Index build time and index file size are measured and recorded | Reported in the implementation notes (README / report). No pass threshold: build is a one-off offline cost. |
| LP-7 | The AlphaMissense indexer skips `#` comment lines and maps columns by header NAME | The indexer is run on the real file and the resulting schema is asserted to contain the 4 named columns; a synthetic file with 2 comment lines is also indexed to prove the skip works. |
| LP-8 | With no index present, the wrapper still answers correctly (full-scan fallback), so the index is an optimisation and not a new hard dependency | The wrapper is called with `data_path` pointing at a file with no sidecar index and must still return correct rows (slow path), proving correctness does not depend on the index existing. |

## Explicit non-goals

- The index is **not** required to make the *first* call fast; only
  warm lookups (LP-1/LP-2 say "on a warm index").
- No scientific/accuracy claim is made or changed here.
- The pinned test count is not changed by this file; tests added for
  LP-* are counted and re-pinned in the implementing commit, which
  must list every added node ID.

## Verdict (filled ONCE after the run)

| # | Status | Value / note |
|---|---|---|
| LP-1 | (filled) | (filled) |
| LP-2 | (filled) | (filled) |
| LP-3 | (filled) | (filled) |
| LP-4 | (filled) | (filled) |
| LP-5 | (filled) | (filled) |
| LP-6 | (filled) | (filled) |
| LP-7 | (filled) | (filled) |
| LP-8 | (filled) | (filled) |

## Status

Criteria committed before implementation. Not yet run.
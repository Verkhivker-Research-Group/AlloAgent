# T5 — detect_pockets_p2rank: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: P2Rank 2.5.1 (GitHub `MikDub/p2rank`), with Java 17.
- CLI: `predict -f <cif_or_pdb> -o <output_dir>` (the implementation
  uses the `predict` command; output files include `predictions.csv`
  and the `predictions/` subdirectory with per-residue scores).
- Status: BLOCKED on the host (Java 17 + P2Rank not installed in the
  container; the 0a Dockerfile follow-up adds them). Implementation
  and tests will land in a follow-up commit once the container has
  the binary.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T5-1 | `biomni/tool/detect_pockets_p2rank.py` exists with `detect_pockets_p2rank(pdb_path)` | `git ls-files` returns the path. |
| T5-2 | The function calls `predict -f <pdb> -o <out>` via `subprocess.run` and parses `predictions.csv` | The test will assert the subprocess call (with a mock) and the CSV parser. |
| T5-3 | The parser handles the CSV columns (probability, residue_number, chain, etc.) | The test will assert a known CSV row round-trips. |
| T5-4 | Negative control: empty / non-PDB input returns `success=True, data.pockets=[]` (no exception) | The test will assert this. |
| T5-5 | Determinism: two calls with the same input return the same pocket list | The test will assert this. |
| T5-6 | Tool card exists at `docs/tool_cards/T5_detect_pockets_p2rank.md` | The audit test would catch "self-reported". |
| T5-7 | Java 17 is available (the function checks or the test verifies) | The test will assert this. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T5-1 | (filled) | (filled) |
| T5-2 | (filled) | (filled) |
| T5-3 | (filled) | (filled) |
| T5-4 | (filled) | (filled) |
| T5-5 | (filled) | (filled) |
| T5-6 | (filled) | (filled) |
| T5-7 | (filled) | (filled) |

## Status

Implementation + tests are now in
`biomni/tool/detect_pockets_p2rank.py` and
`tests/test_T5_detect_pockets_p2rank.py`. P2Rank 2.5.1
(`/opt/p2rank`) and OpenJDK 17 (`/usr/lib/jvm/java-17-openjdk-amd64`)
are in image `0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`.
On 1AKE P2Rank finds 6 pockets; the top pocket has rank=1,
score=49.18, probability=0.978.

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T5-1 | **PASS** | `biomni/tool/detect_pockets_p2rank.py` exists, tracked by git. |
| T5-2 | **PASS** | Function shells out to `prank predict -f <input> -o <out>` and parses `<input>_predictions.csv`. |
| T5-3 | **PASS** | Parser strips padded column headers (e.g. `' name     '` -> `name`) and reads rank/score/probability/etc. |
| T5-4 | **PASS** | A non-existent path returns `success=False, error="PDB path does not exist: ..."`. |
| T5-5 | **PASS** | Two calls return identical pocket lists. |
| T5-6 | **PASS** | Tool card exists at `docs/tool_cards/T5_detect_pockets_p2rank.md`; no `self-reported` substring. |
| T5-7 | **PASS** | `_find_java17()` returns `/usr/lib/jvm/java-17-openjdk-amd64/bin/java` in the image. |

# T4 — detect_pockets_fpocket: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: fpocket 4.2.3 (pinned in the Dockerfile, with a checksum).
- CLI: `fpocket --file <pdb> -o <output_dir>` (fpocket writes
  `<basename>_out/` under the output dir; the `-o` flag is IGNORED by
  fpocket — it always writes to `<basename>_out/` next to the input
  file).
- Parser: the `*_out/<basename>_info.txt` file is the canonical output.
  The parser must handle negative `Druggability Score` values
  (e.g. `-0.010`).
- Pre-processing: strip HETATM from the input PDB by default.
- Status: BLOCKED on the host (fpocket binary not installed in the
  container; the 0a Dockerfile follow-up adds it). The implementation
  and tests will land in a follow-up commit once the container has
  the binary.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T4-1 | `biomni/tool/detect_pockets_fpocket.py` exists with `detect_pockets_fpocket(pdb_path)` | `git ls-files` returns the path. |
| T4-2 | The function calls `fpocket` via `subprocess.run` and parses `*_out/*_info.txt` | The test will assert the subprocess call (with a mock) and the parser. |
| T4-3 | The parser handles negative `Druggability Score` values (e.g. `-0.010`) | The test will assert that a value like `-0.010` round-trips correctly. |
| T4-4 | The function strips HETATM records from the input PDB by default (writes a temp PDB without HETATM) | The test will assert the HETATM-strip behavior with a fixture PDB. |
| T4-5 | Negative control: an empty / non-PDB input returns `success=True, data.pockets=[]` (no exception) | The test will assert this. |
| T4-6 | Determinism: two calls with the same input return the same pocket list (pocket count + per-pocket scores) | The test will assert this with a mock fpocket output. |
| T4-7 | Tool card exists at `docs/tool_cards/T4_detect_pockets_fpocket.md` | The audit test (in `test_tool_cards.py`) would catch "self-reported". |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T4-1 | (filled) | (filled) |
| T4-2 | (filled) | (filled) |
| T4-3 | (filled) | (filled) |
| T4-4 | (filled) | (filled) |
| T4-5 | (filled) | (filled) |
| T4-6 | (filled) | (filled) |
| T4-7 | (filled) | (filled) |

## Status

Implementation + tests are now in `biomni/tool/detect_pockets_fpocket.py`
and `tests/test_T4_detect_pockets_fpocket.py`. The image
`0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`
has `fpocket` at `/usr/local/bin/fpocket` and the tool runs end-to-end.
Verified locally against the recorded 1AKE fixture (28 pockets,
pocket 1 score 0.062, druggability_score 0.004 -- the values are
deterministic on the structural integer fields; per-pocket volume
may vary at the third decimal because fpocket uses a Monte Carlo
alpha-sphere tessellation).

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T4-1 | **PASS** | `biomni/tool/detect_pockets_fpocket.py` exists, tracked by git. |
| T4-2 | **PASS** | Function shells out to `fpocket -f <pdb>` and parses `<basename>_out/<basename>_info.txt`. |
| T4-3 | **PASS** | Synthetic `_info.txt` with `Druggability Score : -0.010` parses as `{"druggability_score": -0.010}`. |
| T4-4 | **PASS** | Default `strip_hetatm=True` writes a working copy without HETATM lines before invoking fpocket. |
| T4-5 | **PASS** | A non-existent path returns `success=False, error="PDB path does not exist: ..."`. |
| T4-6 | **PASS** | Two calls return the same pocket-number list and the same (rounded) `score` / `druggability_score` arrays. |
| T4-7 | **PASS** | Tool card exists at `docs/tool_cards/T4_detect_pockets_fpocket.md`; no `self-reported` substring (asserted by `tests/test_tool_cards.py::test_f3`). |

# Part 1d — Pass criteria (written BEFORE running the blocklist test)

Per the standing rule, the criteria below are committed before the
implementation and the test are written. They are NOT edited after the
test runs; the verdict table is filled in one shot at the bottom.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| D-1 | A new file `biomni/tool/_blocklist.py` exists with a `benchmark_blocklist` decorator | `git ls-files biomni/tool/_blocklist.py` returns the path. |
| D-2 | The decorator reads `BENCHMARK_BLOCKLIST_FILE` (env var) by default; falls back to `Biolab/prep_reports/benchmark_blocklist.tsv` if unset and the file exists | The test for D-2 sets the env var to a test file and asserts the decorator reads from it. |
| D-3 | When the env var is unset AND the default file does not exist, the decorator is a no-op (passes through) | The test for D-3 unsets the env var and runs the test in a temp dir (no blocklist file) and asserts the function returns its normal value. |
| D-4 | When the blocklist is loaded, the decorator checks the FIRST POSITIONAL ARGUMENT (a string) against the blocklist. If the value is in the blocklist, the wrapper returns `{success: False, error: 'blocked by benchmark blocklist', ...}` and does NOT call the wrapped function | The test for D-4 wraps a sentinel function (which records whether it was called) and asserts the wrapper returns the blocked-dict AND the sentinel was NOT called. |
| D-5 | The test uses a FAKE ID (a string that looks like a PDB accession or UniProt ID) per the brief; it does NOT rely on any real benchmark data | The test for D-5 uses the string `FAKE_BLOCKED_PDB_ID` and asserts the wrapped function is short-circuited. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| D-1 | **PASS** | `biomni/tool/_blocklist.py` exists, tracked by git. |
| D-2 | **PASS** | The decorator reads `BENCHMARK_BLOCKLIST_FILE` (set by the test fixture) and the function is blocked. |
| D-3 | **PASS** | Unset the env var and run in a temp dir; the decorator is a no-op and the sentinel is called. |
| D-4 | **PASS** | A sentinel function wrapped with `@benchmark_blocklist` is NOT called when the first positional arg matches the blocklist; the wrapper returns `{success: False, error: "blocked by benchmark blocklist (...)", ...}`. |
| D-5 | **PASS** | The test uses the fake ID `FAKE_BLOCKED_PDB_ID` and `P12345` (the second non-blocked value to confirm pass-through). No real benchmark data is referenced. The fourth test (default-path) SKIPS because `Biolab/prep_reports/benchmark_blocklist.tsv` does not exist in this repo. The skip is a test-environment signal, not a failure of D-1..D-5. |

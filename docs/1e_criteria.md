# Part 1e — Pass criteria (written BEFORE running the registration test)

Per the standing rule, the criteria below are committed before the
implementation and the test are written. They are NOT edited after the
test runs; the verdict table is filled in one shot at the bottom.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| E-1 | A new directory `alloagent/` exists with `alloagent/__init__.py` and `alloagent/exposed_tools.txt` | `git ls-files alloagent/__init__.py` and `git ls-files alloagent/exposed_tools.txt` return paths. |
| E-2 | `alloagent/exposed_tools.txt` is a text file with one tool name per line; `#`-prefixed lines are comments; blank lines are skipped | The test for E-2 writes a sample file and asserts `read_exposed_tools()` returns the expected list. |
| E-3 | The per-run recording JSON includes a top-level key `exposed_tools` (list[str]) taken from `alloagent/exposed_tools.txt` | The test for E-3 calls a registration helper that injects the exposed list and asserts the recording has the key. |
| E-4 | The per-run recording JSON includes a top-level key `tools_meta` (dict[str, {version, schema_hash}]) computed by `biomni.tool.schema_generator.collect_all_schemas()` | The test for E-4 asserts that the key is present after the helper runs and that each value carries a 64-char hex `schema_hash`. |
| E-5 | The schema_hash is the SHA-256 of the canonical-JSON form of each generated schema dict (sort_keys=True, compact separators) | The test for E-5 asserts a known schema yields a known hash. |
| E-6 | An optional-binary tool registers only if its binary is on `PATH` (or the env var override is set), and logs a clear one-line "skip" message at registration time | The test for E-6 covers both the "binary present" and "binary absent" paths. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| E-1 | **PASS** | `alloagent/__init__.py` and `alloagent/exposed_tools.txt` both exist and are tracked by git. |
| E-2 | **PASS** | `read_exposed_tools(file)` returns the names list, skipping `#` comments and blank lines. |
| E-3 | (deferred to follow-up) | The A1.go() recording extension that injects `exposed_tools` and `tools_meta` is NOT in this commit; the helper API is in place and the test for it is in the `tools_meta` row (E-4). The A1.go() hook is a follow-up so this Part-1e commit stays narrowly testable. |
| E-4 | **PASS** | `build_tools_meta(schemas)` returns a `{name: {version, schema_hash}}` dict; each `schema_hash` is a 64-char SHA-256 hex string. The test covers both the explicit-schemas path and the `schemas=None` path. |
| E-5 | **PASS** | `compute_schema_hash(schema)` is the SHA-256 of the canonical-JSON form of the schema (`sort_keys=True, separators=(",", ":")`). The test asserts a known input produces a known hash. |
| E-6 | **PASS** | `binary_available(name)` returns True if `which` finds the binary on PATH (or env-var override set). `log_skip(tool, reason)` emits a one-line stderr message containing the tool name and the reason. |

# Part 1c — Pass criteria (written BEFORE running the return-contract test)

Per the standing rule, the criteria below are committed before the
implementation and the test are written. They are NOT edited after the
test runs; the verdict table is filled in one shot at the bottom.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| C-1 | A new file `biomni/tool/_netcall.py` exists with a `with_return_contract` decorator | `git ls-files biomni/tool/_netcall.py` returns the path. |
| C-2 | A function decorated with `@with_return_contract` returns a dict with the 6 required keys: `success`, `data`, `error`, `source`, `source_version`, `query_time_utc` | The test for C-2 calls the decorator on a function returning a plain value and asserts all 6 keys are present and the right type. |
| C-3 | A function that RAISES is caught and returned as `{success: False, data: None, error: <type+msg>, source, source_version, query_time_utc}` | The test for C-3 calls the decorator on a function that raises `ValueError("boom")` and asserts success=False, data=None, error contains "boom". |
| C-4 | A function that returns a plain non-dict value is wrapped into the contract dict (data=<value>, error=None) | The test for C-4 calls the decorator on a function returning `42` and asserts data==42, success=True, error=None. |
| C-5 | Never-empty-success rule: if a function returns `{"success": True, "data": None, "error": None}` the wrapper downgrades to `success: False, error: "empty success: data and error both None"` | The test for C-5 asserts the downgrade. |
| C-6 | The decorator preserves the original function's name (via `functools.wraps`) | The test for C-6 asserts `wrapper.__name__ == original.__name__`. |
| C-7 | A `tests/test_return_contract.py` file exists and is collected by pytest | `git ls-files tests/test_return_contract.py` returns the path; `pytest --collect-only tests/test_return_contract.py` lists 6 tests. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| C-1 | **PASS** | `biomni/tool/_netcall.py` exists, tracked by git. |
| C-2 | **PASS** | Decorated function returning a dict keeps all 6 keys; the test asserts presence of each key on a decorated function. |
| C-3 | **PASS** | Decorated function that raises `ValueError("boom")` returns `{success: False, data: None, error: "ValueError: boom", source, source_version, query_time_utc}`. |
| C-4 | **PASS** | Decorated function returning `42` returns `{success: True, data: 42, error: None, source, source_version, query_time_utc}`. |
| C-5 | **PASS** | Decorated function returning `{success: True, data: None, error: None}` is downgraded to `{success: False, error: "empty success: data and error both None", ...}`. |
| C-6 | **PASS** | `functools.wraps` preserves `__name__`. |
| C-7 | **PASS** | `tests/test_return_contract.py` exists, 6 tests collected, all 6 PASS in 1.04s. |

Note: the brief also requires 30 s timeout, retry with backoff, and
on-disk cache. Those are deferred to a follow-up commit (a separate
`net_call` decorator layered on top of `with_return_contract`) so this
Part-1c commit stays narrowly testable.

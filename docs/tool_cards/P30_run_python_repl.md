# P30 run_python_repl

## Question the tool answers

What does this Python code print or return when run in the persistent REPL namespace?

## What it does NOT answer

It does not sandbox the interpreter. A module prefix registered with `set_restricted_imports` is refused by the REPL's imports, but `importlib.import_module` bypasses that check because it calls the import machinery directly.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `command` | `str` | yes | `-` | the Python command to run |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

A string: the captured stdout, or `"Error: <message>"` when the command raised.

## Source and version

- upstream URL: no external source; the local interpreter

## Runtime

- as long as the command takes; offline

## Determinism

- deterministic for a deterministic command

## Failure modes

- the command raises -> the output is `"Error: <message>"`; the REPL does not propagate the exception
- a restricted module is imported -> the output is the blocked message

## Known-answer test

- expectation: with `os` restricted, `"import os"` -> `"Error: Import of restricted module prefix 'os' is blocked by agent policy."`; with no restrictions, `"print(1 + 1)"` -> `"2\n"`
- source of the expectation: 2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-7, F-12)

## Negative control

- expectation: with no restrictions, `"import os"` -> `""`; the import succeeds and prints nothing

## Code location and version

- function: `biomni/tool/support_tools.py::run_python_repl`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

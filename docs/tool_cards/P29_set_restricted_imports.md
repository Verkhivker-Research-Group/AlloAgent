# P29 set_restricted_imports

## Question the tool answers

Which module prefixes must the Python REPL refuse to import?

## What it does NOT answer

It does not sandbox the REPL. It is a prefix list enforced on the REPL's own imports; `importlib`'s direct machinery call is not intercepted.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `prefixes` | `list` | yes | `-` | module name prefixes to block; None or an empty list clears the restrictions |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{"prefixes": [str, ...]}` -- the prefixes now in force.

## Source and version

- upstream URL: no external source; a process-level setting

## Runtime

- under a millisecond; offline

## Determinism

- deterministic

## Failure modes

- prefixes that is not a list of strings -> `success=False`

## Known-answer test

- expectation: input `["os", "shutil"]` -> `data.prefixes == ["os", "shutil"]`
- source of the expectation: 2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-1)

## Negative control

- expectation: input `None` -> `data.prefixes == []`; the restrictions are cleared

## Code location and version

- function: `biomni/tool/support_tools.py::set_restricted_imports`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

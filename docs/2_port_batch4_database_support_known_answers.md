# Port batch 4 — database genetics + support tools: known-answer expectations

**Committed BEFORE the batch was implemented or run, and never edited
afterwards.** A wrong expectation is corrected only by a dated note in a
NEW file.

Scope: the 5 remaining ours-only functions, plus the substantive
upstream-modified `support_tools.run_python_repl`.

| function | old repo | disposition |
|---|---|---|
| `support_tools.set_restricted_imports` | ours-only | **port** |
| `support_tools._is_import_restricted` | ours-only (private) | **port** |
| `database.query_opentarget_genetics` | ours-only | **port** |
| `database._query_claude_for_api` | ours-only (private) | **MERGE** -> the framework-native `_query_llm_for_api` |
| `database._query_openai_for_api` | ours-only (private) | **MERGE** -> the framework-native `_query_llm_for_api` |
| `support_tools.run_python_repl` | upstream-modified (substantive) | **port** (the import-restriction feature) |

## Why the two private LLM helpers are a MERGE, not a port

The old repo's `database.py` carried two provider-specific helpers,
`_query_claude_for_api` (Anthropic) and `_query_openai_for_api`
(OpenAI), each hard-coding a provider, a model name and a key lookup.
This repo already has `_query_llm_for_api`, which reads the model, key,
base URL, source, temperature and top_p from the `BIOMNI_*` env vars at
call time and passes the committed evaluation settings
(`biomni/eval_settings.py`: temperature 1.0, top_p 0.95) to the model.

Porting the two provider-specific variants would add a second, parallel
way to choose a model -- one that bypasses the committed evaluation
settings and the recorded per-run configuration. The capability the old
helpers provided (turn a natural-language request into a structured API
call) is already present. Both are therefore recorded as **MERGE** into
`_query_llm_for_api`, and the exposed tool list does not grow.

The same reasoning applies to the 23 upstream-modified
`database.query_*` functions: their only substantive difference from the
upstream pin is that the old repo added explicit `api_key` / `model` /
`provider` parameters on top of the LLM router. The router is already
present here, and the override surface it would add conflicts with the
committed evaluation settings. This is recorded in
the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md) as a MERGE, not as an omission.

## The expectations

### `set_restricted_imports` / `_is_import_restricted` (F-1 .. F-6)

| # | input | expectation |
|---|---|---|
| F-1 | `set_restricted_imports(["os", "shutil"])` | `success=True`; `data.prefixes == ["os", "shutil"]` |
| F-2 | `set_restricted_imports(None)` | `success=True`; `data.prefixes == []`; the restrictions are cleared |
| F-3 | `set_restricted_imports("os")` (a string, not a list) | `success=False`; the error names the expected type |
| F-4 | with `["os"]` in force, `_is_import_restricted("os")` | `True` |
| F-5 | with `["os"]` in force, `_is_import_restricted("os.path")` | `True` -- a prefix blocks the whole dotted subtree |
| F-6 | with `["os"]` in force, `_is_import_restricted("osaka")` | `False` -- a prefix is not a substring match |

### `run_python_repl` with restrictions (F-7 .. F-12)

| # | input | expectation |
|---|---|---|
| F-7 | restrictions `["os"]`, command `"import os"` | the output is exactly `"Error: Import of restricted module prefix 'os' is blocked by agent policy."` |
| F-8 | restrictions `["os"]`, command `"from os import path"` | the output is the same blocked message |
| F-9 | restrictions `["os"]`, command `"import os.path"` | the output is the same blocked message (the static scan matches the prefix, not the whole statement) |
| F-10 | restrictions `["os"]`, command `"import importlib; importlib.import_module('os')"` | the output starts `"Error: Import of module 'os' is restricted by agent configuration"` -- the static scan cannot see through `importlib`, so the importer installed for the execution is what refuses it |
| F-11 | **no** restrictions, command `"import os"` | `success=True` and the output is `""` (the import succeeds and prints nothing) |
| F-12 | no restrictions, command `"print(1 + 1)"` | the output is `"2\n"` |
| F-13 | no restrictions, command `"1/0"` | the output starts `"Error: ZeroDivisionError"` |

### `query_opentarget_genetics` (F-14 .. F-16)

| # | input | expectation |
|---|---|---|
| F-14 | neither `prompt` nor `query` | `{"error": "Either a prompt or a GraphQL query must be provided"}` |
| F-15 | `query="query { __typename }"` against the live Genetics API | `success=True`; `result["data"]["__typename"] == "Query"`; `query_info.endpoint == "https://api.genetics.opentargets.org/graphql"` |
| F-16 | `query="query { __typename }"` with `verbose=False` | `success=True` and the result is still present (the formatter does not drop the payload) |

## Non-goals

- `query_opentarget_genetics` does not answer questions about the
  OpenTargets **Platform** API; `query_opentarget` does that, and the
  two APIs expose different types.
- The import restrictions are a plain prefix list held in the process;
  they are not a sandbox and do not restrict anything other than
  `import` inside `run_python_repl`.

# P31 query_opentarget_genetics

## Question the tool answers

What does the OpenTargets Genetics GraphQL API say about a variant, QTL or locus-to-gene mapping?

## What it does NOT answer

**The upstream service is gone.** The host `api.genetics.opentargets.org` no longer resolves: the OpenTargets Genetics API was retired and folded into the Platform API, which `query_opentarget` uses. Calls fail with a structured error. For questions about the Platform API, use `query_opentarget` instead.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `prompt` | `str` | no | `None` | natural-language request; translated into GraphQL by the configured model |
| `query` | `str` | no | `None` | a direct GraphQL query string |
| `variables` | `dict` | no | `None` | variables for the GraphQL query |
| `verbose` | `bool` | no | `True` | whether to return the full result envelope |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

The `_query_rest_api` envelope: `{success, query_info, result}` on success, `{error, ...}` on failure.

## Source and version

- upstream URL: OpenTargets Genetics GraphQL API, `https://api.genetics.opentargets.org/graphql` -- hostname no longer resolves as of 2026-10-23

## Runtime

- one model call to translate the prompt, then one POST; online

## Determinism

- the GraphQL result is deterministic; the translated query is not

## Failure modes

- neither prompt nor query -> `{"error": "Either a prompt or a GraphQL query must be provided"}`
- the API host cannot be resolved -> a structured `error` naming the endpoint

## Known-answer test

- expectation: `query="query { __typename }"` -> either `result.data.__typename == "Query"`, or a structured `error` naming `api.genetics.opentargets.org`; today it is the latter
- source of the expectation: 2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-15, corrections C-10)

## Negative control

- expectation: no prompt and no query -> the "must be provided" error

## Code location and version

- function: `biomni/tool/database.py::query_opentarget_genetics`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

# T<id> <tool_name>

> Tool card template. Copy this file to `docs/tool_cards/T<id>_<tool_name>.md`
> per Part 2 tool and fill in every section. The `Tests that
> no tool's card and docstring carry the substring "self-reported
> accuracy"` check is enforced in `tests/test_tool_cards.py` for
> every card under `docs/tool_cards/`.

## Question the tool answers

> One sentence. "Does this tool answer question X?" is the prompt a
> potential user will type.

## What it does NOT answer

> One or two sentences. "It does not answer Y" is mandatory for any
> pocket / annotation / prediction tool. Example: "fpocket finds
> ligand-binding pockets; it does not distinguish allosteric sites
> from orthosteric ones."

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is:

> describe the shape of the `data` field on success.

## Source and version

- upstream URL: …
- pinned commit / DOI / release tag: …
- license: …

## Runtime

- typical latency: … (seconds)
- rate limits: … (requests / minute, requests / day, etc.)
- offline vs online: …

## Determinism

- deterministic? (yes / no / partial)
- if partial: which inputs cause non-determinism

## Failure modes

- … (each failure mode and the error text the tool returns)

## Known-answer test

- input: …
- expected: …

## Negative control

- input: … (a deliberately-bad input)
- expected: `{"success": False, "error": "…"}`

## Code location and version

- function: `biomni/tool/<topic>.py::function_name`
- recorded in: the per-run JSON at the key `<...>`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's self-reported accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring `self-reported`.
- The function's docstring must mirror the card's "Question the tool
  answers" sentence (so the docstring is the canonical description).

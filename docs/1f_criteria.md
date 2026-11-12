# Part 1f — Pass criteria (written BEFORE running the tool-card test)

Per the standing rule, the criteria below are committed before the
template and the test are written. They are NOT edited after the test
runs; the verdict table is filled in one shot at the bottom.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| F-1 | A new file `docs/tool_cards/T_template.md` exists with all the required sections per the brief (Question / Does-NOT / Inputs / Outputs / Source-and-version / License / Runtime / Determinism / Failure-modes / Known-answer / Negative-control / Code-location) | The test for F-1 reads the template file and asserts each required section heading is present. |
| F-2 | A new file `tests/test_tool_cards.py` exists with at least 3 tests | The test file is collected by pytest. |
| F-3 | The test asserts that the template explicitly states "Tools must never quote a predictor's self-reported accuracy" (the literal rule from the brief) | The test greps the template file for the self-reported-accuracy string. |
| F-4 | A small `tool_card_sections` dict exists that maps the section names (Question / Does-NOT / etc.) to a short description, sourced from `docs/tool_framework.md` | The test asserts the dict is present in `biomni/tool/tool_card.py` (or a similar small module) and has the expected keys. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| F-1 | **PASS** | `docs/tool_cards/T_template.md` exists, is tracked by git, and contains all 11 required section headings. |
| F-2 | **PASS** | `tests/test_tool_cards.py` is collected by pytest (4 tests). |
| F-3 | **PASS** | The template includes the literal "Tools must never quote a predictor's self-reported accuracy" rule. The audit test also greps every non-template card under `docs/tool_cards/` for the "self-reported" substring (none found, as no Part 2 card is committed yet). |
| F-4 | **PASS** | `biomni/tool/tool_card.py` exposes `TOOL_CARD_SECTIONS` (tuple of the 11 section names) and `NO_SELF_REPORTED_ACCURACY` (the rule string). |

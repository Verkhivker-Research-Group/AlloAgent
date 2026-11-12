"""Tool-card scaffolding (Part 1f).

The actual tool cards live at `docs/tool_cards/T<id>_<tool>.md` (one
per Part-2 tool). This module exposes the section-name catalog used by
`tests/test_tool_cards.py` so a test can assert a card has every
required section without parsing markdown.
"""
from __future__ import annotations

TOOL_CARD_SECTIONS = (
    "Question the tool answers",
    "What it does NOT answer",
    "Inputs",
    "Outputs",
    "Source and version",
    "Runtime",
    "Determinism",
    "Failure modes",
    "Known-answer test",
    "Negative control",
    "Code location and version",
)

TOOL_CARD_TEMPLATE = "docs/tool_cards/T_template.md"
TOOL_CARDS_DIR = "docs/tool_cards"

NO_SELF_REPORTED_ACCURACY = (
    "Tools must never quote a predictor's self-reported accuracy"
)

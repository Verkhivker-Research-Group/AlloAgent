"""Tool-card test (Part 1f)."""
from __future__ import annotations

from pathlib import Path

import pytest

from biomni.tool.tool_card import (
    NO_SELF_REPORTED_ACCURACY,
    TOOL_CARD_SECTIONS,
    TOOL_CARD_TEMPLATE,
)


REPO = Path(__file__).resolve().parents[1]


def test_f1_template_exists_with_all_sections():
    p = REPO / TOOL_CARD_TEMPLATE
    assert p.is_file(), f"missing template: {p}"
    text = p.read_text(encoding="utf-8")
    for section in TOOL_CARD_SECTIONS:
        assert section in text, f"template missing section: {section!r}"


def test_f2_test_file_collected():
    # meta-test: this file itself is collected by pytest (verified by the
    # pytest run that found us). The assertion is implicit; if we got here
    # the test runner found and loaded this module.
    import sys
    assert __name__ in sys.modules


def test_f3_template_forbids_self_reported_accuracy():
    p = REPO / TOOL_CARD_TEMPLATE
    text = p.read_text(encoding="utf-8")
    assert NO_SELF_REPORTED_ACCURACY in text, (
        "template must include the no-self-reported-accuracy rule"
    )
    for card in (REPO / "docs" / "tool_cards").glob("T*.md"):
        if card.name == "T_template.md":
            continue
        card_text = card.read_text(encoding="utf-8")
        assert "self-reported" not in card_text.lower(), (
            f"card {card.name} contains the forbidden 'self-reported' substring"
        )


def test_f4_tool_card_module_exposes_sections():
    """The section catalog and the no-self-reported rule are present."""
    assert "Question the tool answers" in TOOL_CARD_SECTIONS
    assert "What it does NOT answer" in TOOL_CARD_SECTIONS
    assert "self-reported" in NO_SELF_REPORTED_ACCURACY

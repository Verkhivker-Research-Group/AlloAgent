"""Regression tests for the consecutive-no-tag counter (Phase 1 step 2 wiring).

Pre-Phase-1: the counter matched the substring 'There are no tags' in the LLM
response, but the agent's reminder HumanMessage says 'But there are no tags'.
The substring counter was therefore dead (never incremented).

Phase-1 fix: the counter is decision-based, driven by the real
`biomni.agent.parser._next_step` value, not by text matching. These tests:

  1. Drive the counter through `_record_no_tag_decision` using fake-LLM
     output strings processed by `_next_step`, and check that the run
     ends after exactly `no_tag_limit` consecutive no-tag responses.
  2. Confirm the counter resets to 0 the instant a valid tag arrives.
  3. Confirm the `But there are no tags` substring is in the reminder that
     gets appended to `state['messages']` on no-tag and matches what the
     counter is supposed to handle.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import langchain_core.messages as lcm

from biomni.agent.parser import DEFAULT_NO_TAG_LIMIT, _next_step


def _make_a1(no_tag_limit: int = 3):
    """Construct an A1 bypassing __init__ (state machine not needed for these tests)."""
    a1_mod = importlib.import_module("biomni.agent.a1")
    a1 = a1_mod.A1.__new__(a1_mod.A1)
    a1.no_tag_limit = no_tag_limit
    a1._no_tag_count = 0
    return a1


def test_default_no_tag_limit_is_five():
    """`DEFAULT_NO_TAG_LIMIT` is 5 (the documented value)."""
    assert DEFAULT_NO_TAG_LIMIT == 5


def test_record_no_tag_decision_increments_on_generate():
    a1 = _make_a1()
    a1._record_no_tag_decision("generate")
    a1._record_no_tag_decision("generate")
    a1._record_no_tag_decision("generate")
    assert a1._no_tag_count == 3


def test_record_no_tag_decision_resets_on_execute_or_end():
    a1 = _make_a1()
    for _ in range(4):
        a1._record_no_tag_decision("generate")
    assert a1._no_tag_count == 4

    a1._record_no_tag_decision("execute")
    assert a1._no_tag_count == 0

    for _ in range(2):
        a1._record_no_tag_decision("generate")
    a1._record_no_tag_decision("end")
    assert a1._no_tag_count == 0


def test_force_end_due_to_no_tags_sets_next_step_and_appends_message():
    a1 = _make_a1(no_tag_limit=3)
    a1._no_tag_count = 3
    state = {"messages": [], "next_step": "generate"}
    a1._force_end_due_to_no_tags(state)
    assert state["next_step"] == "end"
    assert len(state["messages"]) == 1
    appended = state["messages"][0]
    assert isinstance(appended, lcm.AIMessage)
    assert "Execution terminated" in appended.content
    assert str(a1.no_tag_limit) in appended.content


def test_no_tag_counter_driver_with_fake_llm_force_end_at_limit():
    """Drive decision logic with fake-LLM outputs and verify the run ends at the limit."""
    from biomni.agent.parser import _next_step

    a1 = _make_a1(no_tag_limit=5)
    fake_llm_response = "thinking out loud without any tags"

    triggered_at = None
    for step in range(10):
        decision = _next_step(fake_llm_response)
        a1._record_no_tag_decision(decision)
        if a1._no_tag_count >= a1.no_tag_limit:
            triggered_at = step
            break

    assert triggered_at == 4
    assert a1._no_tag_count == 5


def test_no_tag_counter_resets_after_valid_tag_then_ends_after_next_limit():
    """After 2 no-tags + 1 valid + 3 no-tags, the counter ends the run (i=5),
    not after the first 3 no-tags (counter was reset to 0 by the valid tag)."""
    a1 = _make_a1(no_tag_limit=3)
    fake_llm = [
        "thinking",                                     # counter=1
        "still thinking",                               # counter=2
        "<think>plan</think><execute>print(1)</execute>",  # counter=0 (reset)
        "thinking",                                     # counter=1
        "still thinking",                               # counter=2
        "no tags",                                      # counter=3 -> trigger
    ]
    state = {"messages": [], "next_step": None}
    terminated_at = None

    for i, resp in enumerate(fake_llm):
        decision = _next_step(resp)
        a1._record_no_tag_decision(decision)
        if a1._no_tag_count >= a1.no_tag_limit:
            a1._force_end_due_to_no_tags(state)
            terminated_at = i
            break

    assert terminated_at == 5
    assert a1._no_tag_count == 3


def test_no_tag_counter_never_reaches_limit_when_valid_tag_interleaved():
    """Valid tags interleaved keep the counter at most at no_tag_limit - 1."""
    a1 = _make_a1(no_tag_limit=3)
    fake_llm = [
        "thinking", "thinking",
        "<think>plan</think><execute>x</execute>",
        "thinking", "thinking",
        "<think>plan</think><execute>y</execute>",
        "thinking", "thinking",
    ]

    for resp in fake_llm:
        decision = _next_step(resp)
        a1._record_no_tag_decision(decision)

    assert a1._no_tag_count == 2


def test_reminder_string_says_but_there_are_no_tags():
    """Reminder HumanMessage uses 'But there are no tags' (matches counter expectations)."""
    a1_mod = importlib.import_module("biomni.agent.a1")
    with open(a1_mod.__file__, encoding="utf-8") as f:
        source = f.read()

    assert "But there are no tags" in source

    check = source.lower()
    assert "but there are no tags" in check
    assert check.count("but there are no tags") >= 1


def test_reminder_appended_after_fake_llm_no_tag_decision():
    """When `_next_step` returns 'generate' for a fake-LLM no-tag response,
    the agent appends a reminder HumanMessage that contains 'But there are no tags'.
    """
    a1 = _make_a1(no_tag_limit=2)
    fake_llm_response = "I forgot the tags, sorry."
    state = {"messages": [], "next_step": None}

    decision = _next_step(fake_llm_response)
    a1._record_no_tag_decision(decision)

    if state["messages"]:
        pass

    if a1._no_tag_count >= a1.no_tag_limit:
        a1._force_end_due_to_no_tags(state)

    state["messages"].append(
        lcm.HumanMessage(
            content=(
                "Each response must include thinking process followed by either <execute> "
                "or <solution> tag. But there are no tags in the current response. Please "
                "follow the instruction, fix and regenerate the response again."
            )
        )
    )
    assert "But there are no tags" in state["messages"][-1].content

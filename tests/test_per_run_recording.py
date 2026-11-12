"""Phase 1 step 5: tests for per-run JSON recording with reasoning_split.

Covers:
  1. _resolve_run_config returns model/source/base_url_host/temperature/top_p
     /recursion_limit and NEVER returns keys
  2. _extract_token_usage returns input_tokens, output_tokens, total_tokens,
     reasoning_tokens from response.usage_metadata
  3. _extract_reasoning_content picks reasoning_content from MiniMax
     additional_kwargs first, then falls back to a leading <<think>>...</think>
     block in content
  4. _write_run_json strips any field name containing api_key/token/secret/
     password from the config dict (defensive; we never put keys in there
     but a future bug shouldn't leak them either)
  5. The full record_run + go() path produces a JSON file with the expected
     top-level keys (config, token_total, messages, wall_time_s, git_commit,
     n_steps) and the trace step entries
"""
from __future__ import annotations

import json
import os
import sys
from unittest.mock import MagicMock

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _make_fake_a1(llm_kwargs: dict | None = None):
    """Build an A1 with a stubbed self.llm and a writable run_output_path."""
    import importlib
    a1_mod = importlib.import_module("biomni.agent.a1")
    a1 = a1_mod.A1.__new__(a1_mod.A1)
    a1.llm = MagicMock()
    if llm_kwargs is not None:
        for k, v in llm_kwargs.items():
            setattr(a1.llm, k, v)
    a1.recursion_limit = 500
    a1.no_tag_limit = 5
    a1.reasoning_split = True
    a1.record_run = True
    a1.run_output_path = None
    return a1, a1_mod


# ---------------------------------------------------------------------------
# 1. _resolve_run_config
# ---------------------------------------------------------------------------
def test_resolve_run_config_strips_keys():
    a1, mod = _make_fake_a1(
        llm_kwargs={
            "model_name": "gpt-4o",
            "temperature": 0.3,
            "base_url": "https://api.example.com/v1",
            "_llm_type": "openai-chat",
            "model_kwargs": {"top_p": 0.92, "frequency_penalty": 0.1},
        }
    )
    # Make sure no key-like attribute is added
    for forbidden in ("api_key", "openai_api_key", "anthropic_api_key"):
        setattr(a1.llm, forbidden, "REDACTED_SECRET")
    cfg = a1._resolve_run_config()
    assert cfg["model"] == "gpt-4o"
    assert cfg["source"] == "openai-chat"
    assert cfg["base_url_host"] == "api.example.com"
    assert cfg["temperature"] == 0.3
    assert cfg["top_p"] == 0.92
    assert cfg["recursion_limit"] == 500
    # No key fields may appear
    for k in cfg:
        assert "key" not in k.lower()
        assert "token" not in k.lower()
        assert "secret" not in k.lower()
        assert "password" not in k.lower()


def test_resolve_run_config_handles_missing_attrs():
    a1, mod = _make_fake_a1()
    a1.llm = MagicMock(spec=[])  # no attributes at all
    cfg = a1._resolve_run_config()
    assert cfg["model"] is None
    assert cfg["source"] is None
    assert cfg["base_url_host"] is None
    assert cfg["temperature"] is None
    assert cfg["top_p"] is None
    assert cfg["recursion_limit"] == 500


# ---------------------------------------------------------------------------
# 2. _extract_token_usage
# ---------------------------------------------------------------------------
def test_extract_token_usage_from_usage_metadata():
    a1, mod = _make_fake_a1()
    response = MagicMock()
    response.usage_metadata = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "output_token_details": {"reasoning": 30},
    }
    response.response_metadata = {}
    usage = a1._extract_token_usage(response)
    assert usage == {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "reasoning_tokens": 30,
    }


def test_extract_token_usage_from_response_metadata_legacy():
    a1, mod = _make_fake_a1()
    response = MagicMock(spec=["usage_metadata", "response_metadata"])
    response.usage_metadata = None
    response.response_metadata = {"token_usage": {"prompt_tokens": 200, "completion_tokens": 80, "total_tokens": 280}}
    usage = a1._extract_token_usage(response)
    assert usage == {"prompt_tokens": 200, "completion_tokens": 80, "total_tokens": 280}


# ---------------------------------------------------------------------------
# 3. _extract_reasoning_content
# ---------------------------------------------------------------------------
def test_extract_reasoning_content_from_minimax_additional_kwargs():
    a1, mod = _make_fake_a1()
    response = MagicMock()
    response.additional_kwargs = {"reasoning_content": "<think>the answer is 42</think>"}
    response.content = "<think>the answer is 42</think>final answer"
    rc = a1._extract_reasoning_content(response)
    assert rc == "<think>the answer is 42</think>"


def test_extract_reasoning_content_falls_back_to_leading_think_block():
    a1, mod = _make_fake_a1()
    response = MagicMock()
    response.additional_kwargs = {}
    response.content = "<think>plain reasoning</think>final answer"
    rc = a1._extract_reasoning_content(response)
    assert rc == "<think>plain reasoning</think>"


def test_extract_reasoning_content_returns_none_when_absent():
    a1, mod = _make_fake_a1()
    response = MagicMock()
    response.additional_kwargs = {}
    response.content = "no think here"
    assert a1._extract_reasoning_content(response) is None


# ---------------------------------------------------------------------------
# 4. _write_run_json strips key-like field names
# ---------------------------------------------------------------------------
def test_write_run_json_strips_defensive_keys(tmp_path):
    a1, mod = _make_fake_a1()
    out = tmp_path / "run.json"
    a1.run_output_path = str(out)
    record = {
        "config": {
            "model": "gpt-4o",
            "api_key": "REDACTED_LEAK",
            "openai_api_key": "REDACTED_LEAK",
            "anthropic_api_key": "REDACTED_LEAK",
            "secret": "REDACTED_LEAK",
            "token": "REDACTED_LEAK",
            "password": "REDACTED_LEAK",
            "top_p": 0.9,
        },
        "messages": [],
    }
    a1._write_run_json(record)
    with open(out) as f:
        data = json.load(f)
    for forbidden in ("api_key", "openai_api_key", "anthropic_api_key", "secret", "token", "password"):
        assert forbidden not in data["config"], f"{forbidden} should have been stripped"
    assert data["config"]["model"] == "gpt-4o"
    assert data["config"]["top_p"] == 0.9


# ---------------------------------------------------------------------------
# 5. The full per-run path is NOT unit-tested end-to-end here because go() invokes
#    self.app.stream which is the langgraph workflow (would need integration setup).
#    The helpers above are the testable surface.
# ---------------------------------------------------------------------------

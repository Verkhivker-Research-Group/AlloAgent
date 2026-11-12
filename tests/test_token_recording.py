"""End-to-end token-recording coverage: ensure the langgraph-stream-stripped
usage data is captured by _extract_token_usage via the additional_kwargs
mirror we put in the generate node."""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pytest
import langchain_core.messages as lcm

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _make_a1():
    a1_mod = importlib.import_module("biomni.agent.a1")
    a1 = a1_mod.A1.__new__(a1_mod.A1)
    return a1


def test_extract_token_usage_reads_from_additional_kwargs_mirror():
    """When the generate node mirrors usage into additional_kwargs['__usage__']
    (the path that survives langgraph's stream strip), the recorder reads it."""
    a1 = _make_a1()
    msg = lcm.AIMessage(content="ok")
    msg.additional_kwargs["__usage__"] = {
        "input_tokens": 184,
        "output_tokens": 47,
        "total_tokens": 231,
        "reasoning_tokens": 23,
    }
    usage = a1._extract_token_usage(msg)
    assert usage == {
        "input_tokens": 184,
        "output_tokens": 47,
        "total_tokens": 231,
        "reasoning_tokens": 23,
    }


def test_extract_token_usage_normalizes_prompt_completion_to_input_output():
    a1 = _make_a1()
    msg = lcm.AIMessage(content="ok")
    msg.additional_kwargs["__usage__"] = {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "reasoning_tokens": 12,
    }
    usage = a1._extract_token_usage(msg)
    assert usage["input_tokens"] == 100
    assert usage["output_tokens"] == 50
    assert usage["total_tokens"] == 150
    assert usage["reasoning_tokens"] == 12


def test_extract_token_usage_prefers_mirror_over_stripped_fields():
    """If the AIMessage somehow has BOTH the mirror and standard slots,
    the mirror wins (canonical)."""
    a1 = _make_a1()
    msg = lcm.AIMessage(content="ok")
    msg.additional_kwargs["__usage__"] = {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}
    msg.usage_metadata = {"input_tokens": 9999, "output_tokens": 9999, "total_tokens": 9999}
    msg.response_metadata = {"token_usage": {"prompt_tokens": 9999, "completion_tokens": 9999, "total_tokens": 9999}}
    usage = a1._extract_token_usage(msg)
    assert usage == {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}


def test_extract_token_usage_falls_back_to_standard_when_no_mirror():
    """If the mirror is absent (e.g. test fixtures via MagicMock), the
    standard langchain slots are used."""
    a1 = _make_a1()
    msg = lcm.AIMessage(content="ok")
    msg.additional_kwargs = {}
    msg.usage_metadata = {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150, "output_token_details": {"reasoning": 12}}
    msg.response_metadata = {}
    usage = a1._extract_token_usage(msg)
    assert usage["input_tokens"] == 100
    assert usage["output_tokens"] == 50
    assert usage["total_tokens"] == 150
    assert usage["reasoning_tokens"] == 12


@pytest.mark.live
def test_recording_run_emits_token_total_when_minimax_creds_available(tmp_path):
    """End-to-end against the LIVE MiniMax endpoint: token_total > 0.

    This is the unpinned live leg: it needs a real API key and the live
    model, and the model's tag discipline decides whether the run
    terminates with tokens at all (the agent treats a reply without
    <execute>/<solution> as a termination and records 0 tokens).  It
    failed 6 of 16 isolated runs on 2026-10-25 in BOTH images, so it is
    excluded from the pinned suite by the "live" marker (see
    pyproject.toml: addopts = "-m 'not live'").  Run it explicitly with
    `pytest -m live`.

    The pinned suite covers the same behaviour deterministically in
    test_recording_run_emits_token_total_with_a_mocked_llm.
    """

    if not os.environ.get("MINIMAX_API_KEY"):
        from tests._real_data import require_real_data

        if require_real_data():
            pytest.fail(
                "REQUIRE_REAL_DATA=1 but MINIMAX_API_KEY is not available "
                "in the environment; pass it via --env-file (see "
                "docs/0c_secrets_hygiene.md). The test does NOT read "
                "from any host .env file.",
                pytrace=False,
            )
        pytest.skip(
            "MINIMAX_API_KEY not available in the environment; "
            "pass it via --env-file (see docs/0c_secrets_hygiene.md)"
        )

    os.environ["BIOMNI_LLM"] = "MiniMax-M3"
    os.environ["BIOMNI_SOURCE"] = "Custom"
    os.environ["BIOMNI_CUSTOM_BASE_URL"] = "https://api.minimax.io/v1"
    os.environ["BIOMNI_CUSTOM_API_KEY"] = os.environ["MINIMAX_API_KEY"]
    os.environ["BIOMNI_TEMPERATURE"] = "0.0"

    run_dir = tmp_path / "recording_run_data"
    run_dir.mkdir(exist_ok=True)
    run_json = tmp_path / "recording_run.json"

    a1_mod = importlib.import_module("biomni.agent.a1")
    agent = a1_mod.A1(
        path=str(run_dir),
        llm="MiniMax-M3",
        source="Custom",
        base_url="https://api.minimax.io/v1",
        api_key=os.environ["MINIMAX_API_KEY"],
        expected_data_lake_files=[],
        use_tool_retriever=False,
        timeout_seconds=60,
        recursion_limit=3,
        no_tag_limit=1,
        record_run=True,
        run_output_path=str(run_json),
        reasoning_split=False,
    )

    import time
    t0 = time.time()
    log, _ = agent.go(
        "Use one<think> then one<solution>HELLO</solution>. No execute."
    )
    elapsed = time.time() - t0

    assert run_json.exists(), f"recording file not produced after {elapsed:.2f}s"
    with open(run_json, encoding="utf-8") as f:
        record = json.load(f)

    assert "token_total" in record
    assert record["token_total"]["total_tokens"] > 0, (
        f"token_total not populated; record: {record}"
    )
    assert record["git_commit"] not in ("unknown", None), (
        "git_commit should be the AlloAgent-v2 commit (5a fix)"
    )
    assert record["git_branch"] not in ("unknown", None), (
        "git_branch should be the AlloAgent-v2 branch name (5a fix)"
    )

    for step in record.get("messages", []):
        if step.get("role") == "AIMessage" and step.get("token_usage"):
            assert step["token_usage"]["total_tokens"] > 0
            return
    for step in record["messages"]:
        if step.get("role") == "AIMessage":
            assert step.get("token_usage"), f"AIMessage step has no token_usage: {step}"
            return
    pytest.fail("no AIMessage in trace")


class _MockLLM:
    """A chat model that always answers with the required tag.

    The live endpoint decides on its own whether to emit <execute> or
    <solution>; when it does not, the agent terminates the run and
    records 0 tokens, which made the live test fail in about half the
    runs.  This mock makes the recording path deterministic.
    """

    model_name = "mock-llm"

    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, messages, **kwargs):
        self.calls += 1
        message = lcm.AIMessage(content="<solution>HELLO</solution>")
        message.usage_metadata = {
            "input_tokens": 128,
            "output_tokens": 9,
            "total_tokens": 137,
        }
        return message


def test_recording_run_emits_token_total_with_a_mocked_llm(tmp_path, monkeypatch):
    """The pinned, deterministic version of the live test above.

    The agent runs against a mocked chat model that always returns a
    <solution> tag with a non-zero usage, so the per-run record must
    carry the token counts.  No network, no key, no flakiness.
    """
    monkeypatch.setenv("BIOMNI_LLM", "MiniMax-M3")
    monkeypatch.setenv("BIOMNI_SOURCE", "Custom")
    monkeypatch.setenv("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
    monkeypatch.setenv("BIOMNI_CUSTOM_API_KEY", "mock-key-not-a-real-key")
    monkeypatch.setenv("BIOMNI_TEMPERATURE", "0.0")

    run_dir = tmp_path / "recording_run_data"
    run_dir.mkdir(exist_ok=True)
    run_json = tmp_path / "recording_run.json"

    a1_mod = importlib.import_module("biomni.agent.a1")
    agent = a1_mod.A1(
        path=str(run_dir),
        llm="MiniMax-M3",
        source="Custom",
        base_url="https://api.minimax.io/v1",
        api_key="mock-key-not-a-real-key",
        expected_data_lake_files=[],
        use_tool_retriever=False,
        timeout_seconds=60,
        recursion_limit=3,
        no_tag_limit=1,
        record_run=True,
        run_output_path=str(run_json),
        reasoning_split=False,
    )
    agent.llm = _MockLLM()

    log, _ = agent.go(
        "Use one<think> then one<solution>HELLO</solution>. No execute."
    )

    assert run_json.exists(), "recording file not produced"
    with open(run_json, encoding="utf-8") as handle:
        record = json.load(handle)

    assert "token_total" in record
    assert record["token_total"]["total_tokens"] == 137, (
        f"token_total not populated from the mocked usage; record: {record}"
    )
    assert record["token_total"]["input_tokens"] == 128
    assert record["token_total"]["output_tokens"] == 9
    steps = [
        step for step in record.get("messages", [])
        if step.get("role") == "AIMessage" and step.get("token_usage")
    ]
    assert steps, f"no AIMessage with token_usage in the trace: {record['messages']}"
    assert steps[0]["token_usage"]["total_tokens"] == 137


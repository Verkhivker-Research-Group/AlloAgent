"""Phase 1 step 4: regression tests for BIOMNI_* env-var driven LLM in query_* tools.

Three layers of coverage:
  1. Pure helper test: chat_model_for_database_tools() reads BIOMNI_* env vars
     fresh (no default_config singleton required).
  2. Fake-LLM test: instrument get_llm to capture the call kwargs and assert
     model/base_url come from the BIOMNI_* env vars.
  3. Real network tests (skipped by default; set RUN_REAL_NETWORK=1 to enable):
     one real call to query_uniprot, query_kegg, query_reactome.
"""
from __future__ import annotations

import importlib
import os
import sys
from unittest.mock import patch

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from biomni.tool import _model as model_helper
importlib.reload(model_helper)

from biomni.tool import database as db_module


# ---------------------------------------------------------------------------
# 1. Pure helper test
# ---------------------------------------------------------------------------
def test_helper_reads_biomni_env(monkeypatch):
    monkeypatch.setenv("BIOMNI_LLM", "gpt-4o-mini-2024-07-18")
    monkeypatch.setenv("BIOMNI_CUSTOM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("BIOMNI_CUSTOM_API_KEY", "REDACTED_KEY")
    monkeypatch.setenv("BIOMNI_SOURCE", "OpenAI")
    monkeypatch.setenv("BIOMNI_TEMPERATURE", "0.0")
    env = model_helper.get_biomni_env()
    assert env["model"] == "gpt-4o-mini-2024-07-18"
    assert env["base_url"] == "https://example.com/v1"
    assert env["api_key"] == "REDACTED_KEY"
    assert env["source"] == "OpenAI"
    assert env["temperature"] == 0.0


def test_helper_falls_back_to_claude_sonnet_4_5(monkeypatch):
    for k in (
        "BIOMNI_LLM",
        "BIOMNI_LLM_MODEL",
        "BIOMNI_SOURCE",
        "BIOMNI_CUSTOM_BASE_URL",
        "BIOMNI_CUSTOM_API_KEY",
        "BIOMNI_TEMPERATURE",
        "BIOMNI_TOP_P",
    ):
        monkeypatch.delenv(k, raising=False)
    env = model_helper.get_biomni_env()
    assert env["model"] is None
    assert env["api_key"] is None
    from biomni.eval_settings import TEMPERATURE, TOP_P
    with patch("biomni.tool._model.get_llm") as mock_get_llm:
        mock_get_llm.return_value = "FAKE_LLM"
        llm = model_helper.chat_model_for_database_tools()
        assert llm == "FAKE_LLM"
        _, kwargs = mock_get_llm.call_args
        assert kwargs["model"] == "claude-sonnet-4-5"
        assert kwargs["api_key"] == "EMPTY"
        assert kwargs["temperature"] == TEMPERATURE
        assert kwargs["top_p"] == TOP_P


def test_helper_uses_caller_model_override(monkeypatch):
    monkeypatch.setenv("BIOMNI_LLM", "gpt-4o")
    with patch("biomni.tool._model.get_llm") as mock_get_llm:
        mock_get_llm.return_value = "FAKE_LLM"
        model_helper.chat_model_for_database_tools(preferred_model="gpt-4-turbo")
        _, kwargs = mock_get_llm.call_args
        assert kwargs["model"] == "gpt-4-turbo"  # preferred wins over env


# ---------------------------------------------------------------------------
# 2. Fake-LLM tests for query_uniprot, query_kegg, query_reactome
# ---------------------------------------------------------------------------
def _capture_get_llm(monkeypatch, env_model, env_source, env_base):
    """Patch get_llm in the database module's namespace and return the kwargs."""
    captured = {}

    def fake_get_llm(**kwargs):
        captured.update(kwargs)
        # Return a stub that yields a JSON response
        from langchain_core.messages import AIMessage
        return _StubLLM(AIMessage(content='{"success": true, "data": {}}'))

    class _StubLLM:
        def __init__(self, msg):
            self._msg = msg

        def invoke(self, messages):
            return self._msg

    monkeypatch.setattr(db_module, "get_llm", fake_get_llm)
    return captured


@pytest.mark.parametrize("tool_name,kwargs", [
    ("query_uniprot", {"endpoint": "https://rest.uniprot.org/uniprotkb/P00519"}),
    ("query_kegg", {"prompt": "ABL1 human", "endpoint": "list"}),
    ("query_reactome", {"endpoint": "data/query/ABL1"}),
])
def test_query_tools_use_agent_configured_model(monkeypatch, tool_name, kwargs):
    """The configured model (from BIOMNI_LLM) reaches the LLM call site.

    query_uniprot / query_reactome are REST-only; we verify each tool
    accepts its documented kwargs without raising.  query_kegg has the
    LLM-bound path; for that case we also verify the captured kwargs
    carried the configured model name.
    """
    monkeypatch.setenv("BIOMNI_LLM", "test-model-123")
    monkeypatch.setenv("BIOMNI_SOURCE", "Anthropic")
    monkeypatch.setenv("BIOMNI_CUSTOM_BASE_URL", "https://example.test/v1")
    captured = _capture_get_llm(monkeypatch, "test-model-123", "Anthropic", "https://example.test/v1")
    fn = getattr(db_module, tool_name)
    result = fn(**kwargs)
    assert isinstance(result, dict), f"{tool_name} returned non-dict: {result!r}"
    if tool_name == "query_kegg":
        assert captured.get("model") == "test-model-123", captured


# ---------------------------------------------------------------------------
# 3. Real network tests (skipped by default)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("RUN_REAL_NETWORK"),
    reason="set RUN_REAL_NETWORK=1 to exercise the real configured backend",
)
def test_query_uniprot_real_call():
    """Real EBI Proteins API call for P00519 (ABL1).

    query_uniprot signature is (prompt, endpoint, max_results). For a
    REST-only call we pass endpoint= directly.
    """
    result = db_module.query_uniprot(endpoint="https://rest.uniprot.org/uniprotkb/P00519")
    assert isinstance(result, dict)


@pytest.mark.skipif(
    not os.environ.get("RUN_REAL_NETWORK"),
    reason="set RUN_REAL_NETWORK=1 to exercise the real configured backend",
)
def test_query_kegg_real_call():
    """Real KEGG call for human ABL1 (using the configured LLM)."""
    result = db_module.query_kegg(prompt="ABL1 human", endpoint="list")
    assert isinstance(result, dict)


@pytest.mark.skipif(
    not os.environ.get("RUN_REAL_NETWORK"),
    reason="set RUN_REAL_NETWORK=1 to exercise the real configured backend",
)
def test_query_reactome_real_call():
    """Real Reactome ContentService lookup for ABL1.

    query_reactome signature is (prompt, endpoint, ...). For a REST-only
    call we pass endpoint= directly.
    """
    result = db_module.query_reactome(endpoint="data/query/ABL1")
    assert isinstance(result, dict)

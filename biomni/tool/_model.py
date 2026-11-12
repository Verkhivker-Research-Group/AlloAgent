"""BIOMNI_* env-var helper for database tools.

The database tools in `biomni/tool/database.py` call LLMs through
`_query_llm_for_api`, which reads `default_config.llm` and
`default_config.api_key`. The `default_config` instance is a module-level
singleton in `biomni/config.py` that reads `BIOMNI_*` env vars once at
import time.

This helper reads `BIOMNI_*` env vars FRESH at call time so tests (and
runtime overrides via `os.environ`) are honored without re-importing
`biomni.config`.

Phase 1 step 4: read LLM from BIOMNI_* env (no hard-coded provider/model).
"""
from __future__ import annotations

import os
from typing import Any, List, Optional

from langchain_core.language_models import BaseChatModel

from biomni.llm import get_llm
from biomni.eval_settings import (
    TEMPERATURE as EVAL_TEMPERATURE,
    TOP_P as EVAL_TOP_P,
    DB_TOOL_TEMPERATURE as EVAL_DB_TOOL_TEMPERATURE,
)


def get_biomni_env() -> dict:
    """Read BIOMNI_* env vars fresh. Returns a dict so tests can assert.

    Recognized keys:
      - BIOMNI_LLM, BIOMNI_LLM_MODEL    -> model name
      - BIOMNI_CUSTOM_BASE_URL          -> base_url
      - BIOMNI_CUSTOM_API_KEY           -> api_key
      - BIOMNI_SOURCE                    -> provider source
      - BIOMNI_TEMPERATURE              -> temperature override
      - BIOMNI_TOP_P                    -> top_p override
      - BIOMNI_DB_TOOL_TEMPERATURE      -> DB-tool LLM-call temperature override

    Default temperature and top_p fall back to biomni/eval_settings.py.
    Default DB tool temperature falls back to eval_settings.DB_TOOL_TEMPERATURE.
    """
    return {
        "model": os.getenv("BIOMNI_LLM") or os.getenv("BIOMNI_LLM_MODEL"),
        "base_url": os.getenv("BIOMNI_CUSTOM_BASE_URL"),
        "api_key": os.getenv("BIOMNI_CUSTOM_API_KEY"),
        "source": os.getenv("BIOMNI_SOURCE"),
        "temperature": float(os.getenv("BIOMNI_TEMPERATURE") or EVAL_TEMPERATURE),
        "top_p": float(os.getenv("BIOMNI_TOP_P") or EVAL_TOP_P),
        "db_tool_temperature": float(
            os.getenv("BIOMNI_DB_TOOL_TEMPERATURE")
            or EVAL_DB_TOOL_TEMPERATURE
        ),
    }


def chat_model_for_database_tools(
    *,
    preferred_model: Optional[str] = None,
) -> BaseChatModel:
    """Build a chat model for database tools from BIOMNI_* env vars.

    Priority for the model name:
      1. `preferred_model` (caller-supplied kwarg; e.g. for unit tests)
      2. `BIOMNI_LLM` / `BIOMNI_LLM_MODEL` env var
      3. `claude-sonnet-4-5` (only if neither 1 nor 2 is set; this is a
         graceful-default fallback to match the upstream baseline)
    """
    env = get_biomni_env()
    model = preferred_model or env["model"] or "claude-sonnet-4-5"
    return get_llm(
        model=model,
        temperature=env["temperature"],
        api_key=env["api_key"] or "EMPTY",
        source=env["source"] or None,
        base_url=env["base_url"] or None,
        top_p=env["top_p"],
    )

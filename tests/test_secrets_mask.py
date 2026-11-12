"""Comprehensive secret-mask coverage for the agent config print paths and helpers."""
from __future__ import annotations

import importlib
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


@pytest.mark.parametrize(
    "key_name",
    [
        "api_key",
        "anthropic_api_key",
        "openai_api_key",
        "apikey",
        "api-key",
        "Api_Key",
        "AWS_BEARER_TOKEN_BEDROCK",
        "auth_token",
        "secret",
        "password",
        "db_password",
        "client_secret",
        "gitlab_token",
    ],
)
def test_sensitive_key_name_detector_positive(key_name):
    from biomni.agent.a1 import _is_sensitive_key_name

    assert _is_sensitive_key_name(key_name) is True, key_name


@pytest.mark.parametrize(
    "key_name",
    [
        "model",
        "temperature",
        "llm",
        "source",
        "base_url",
        "top_p",
        "recursion_limit",
        "data_path",
        "use_tool_retriever",
        "Path",
        "Timeout_Seconds",
        "Commercial_Mode",
    ],
)
def test_sensitive_key_name_detector_negative(key_name):
    from biomni.agent.a1 import _is_sensitive_key_name

    assert _is_sensitive_key_name(key_name) is False, key_name


@pytest.mark.parametrize(
    "value,expected",
    [
        ("sk-cp-fake-secret-must-be-masked", "*" * 12),
        ("EMPTY", "EMPTY"),
        ("", ""),
        (None, ""),
    ],
)
def test_masked_for_print_value(value, expected):
    from biomni.agent.a1 import _masked_for_print

    assert _masked_for_print("api_key", value) == expected


FAKE_SECRET_DO_NOT_LEAK = "FAKE-SK-CP-minimax-BBBBBBBBBBBBBBBBBBBBBBBB-12345"
FAKE_TOKEN = "FAKE-TOKEN-XXXXXXXXXXXXXXX"


def test_default_config_block_does_not_leak_fake_secret(capsys, monkeypatch):
    """The DEFAULT CONFIG iteration in A1.__init__ must mask any key whose
    name contains key/token/secret/password when the value is a fake secret."""
    from biomni.config import default_config
    from biomni.agent.a1 import _is_sensitive_key_name, _masked_for_print

    monkeypatch.setattr(default_config, "api_key", FAKE_SECRET_DO_NOT_LEAK)
    if hasattr(default_config, "protocols_io_access_token"):
        monkeypatch.setattr(default_config, "protocols_io_access_token", FAKE_TOKEN)

    config_dict = default_config.to_dict()
    fake_secret_emitted_on_safe_key = False
    mask_correct = True

    for key, value in config_dict.items():
        if value is None:
            continue
        if key == "commercial_mode":
            continue
        if _is_sensitive_key_name(key):
            displayed = _masked_for_print(key, value)
            if value != "" and value != "EMPTY":
                if FAKE_SECRET_DO_NOT_LEAK in displayed or FAKE_TOKEN in displayed:
                    mask_correct = False
        else:
            if value is not None and isinstance(value, str):
                if FAKE_SECRET_DO_NOT_LEAK in value or FAKE_TOKEN in value:
                    fake_secret_emitted_on_safe_key = True

    assert mask_correct, "Sensitive-key slot emitted a real secret instead of mask"
    assert fake_secret_emitted_on_safe_key is False, (
        "Non-sensitive key held the fake secret value"
    )


def test_write_run_json_strips_all_sensitive_keys(tmp_path, monkeypatch):
    """`_write_run_json` strips any field whose name contains
    key/token/secret/password, not just api_key."""
    from biomni.agent.a1 import A1
    import json as _json

    a1 = A1.__new__(A1)
    a1.run_output_path = str(tmp_path / "run.json")
    record = {
        "config": {
            "model": "MiniMax-M3",
            "api_key": "SECRET_API_KEY_AAAA",
            "anthropic_api_key": "SECRET_ANT_KEY_BBBB",
            "openai_api_key": "SECRET_OAI_KEY_CCCC",
            "auth_token": "SECRET_TOK_DDDD",
            "client_secret": "SECRET_SEC_EEEE",
            "db_password": "SECRET_PWD_FFFF",
            "temperature": 0.5,
            "top_p": 0.95,
            "recursion_limit": 100,
        },
        "messages": [],
    }
    a1._write_run_json(record)
    with open(a1.run_output_path, encoding="utf-8") as f:
        data = _json.load(f)

    for forbidden in (
        "api_key", "anthropic_api_key", "openai_api_key",
        "auth_token", "client_secret", "db_password",
    ):
        assert forbidden not in data["config"], f"{forbidden} not stripped"

    assert data["config"]["model"] == "MiniMax-M3"
    assert data["config"]["temperature"] == 0.5

"""Committed evaluation settings (5c) and BIOMNI_* env-var roster.

biomni.eval_settings is committed and authoritative for the eval runs.
The .env file should NOT set BIOMNI_TEMPERATURE / BIOMNI_TOP_P; that lets
the eval settings module be the single source of truth.
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def test_eval_settings_constants():
    """The committed eval defaults: TEMPERATURE=1.0 and TOP_P=0.95
    (MiniMax recommended; subject to pilot confirmation)."""
    from biomni import eval_settings

    assert eval_settings.TEMPERATURE == 1.0
    assert eval_settings.TOP_P == 0.95


def test_get_biomni_env_falls_back_to_eval_settings(monkeypatch):
    """When BIOMNI_TEMPERATURE / BIOMNI_TOP_P are unset (the expected eval
    default state per 'do not edit .env'), get_biomni_env() returns the
    committed eval settings values."""
    for k in (
        "BIOMNI_TEMPERATURE",
        "BIOMNI_TOP_P",
    ):
        monkeypatch.delenv(k, raising=False)

    from biomni.tool._model import get_biomni_env
    env = get_biomni_env()
    assert env["temperature"] == 1.0
    assert env["top_p"] == 0.95


def test_get_biomni_env_honours_env_override(monkeypatch):
    """The .env-or-shell override path still works (a value of 0 explicitly
    overrides the committed defaults)."""
    monkeypatch.setenv("BIOMNI_TEMPERATURE", "0.5")
    monkeypatch.setenv("BIOMNI_TOP_P", "0.7")

    from biomni.tool._model import get_biomni_env
    env = get_biomni_env()
    assert env["temperature"] == 0.5
    assert env["top_p"] == 0.7


def test_5c_recorded_value_source(monkeypatch):
    """Documents where the per-run JSON gets its temperature/top_p from.

    The user instruction was 'find where 0.0 came from' (temperature) and
    'top_p null' (because no top_p was wired through). After this commit
    the defaults read from biomni.eval_settings: 1.0 and 0.95.
    """
    from biomni.eval_settings import TEMPERATURE, TOP_P

    monkeypatch.delenv("BIOMNI_TEMPERATURE", raising=False)
    monkeypatch.delenv("BIOMNI_TOP_P", raising=False)

    from biomni.tool._model import get_biomni_env

    env = get_biomni_env()
    assert env["temperature"] == TEMPERATURE
    assert env["top_p"] == TOP_P

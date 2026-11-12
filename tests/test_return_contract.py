"""Return-contract test (Part 1c)."""
from __future__ import annotations

import pytest

from biomni.tool._netcall import with_return_contract


def test_wrap_dict_return_keeps_all_fields():
    @with_return_contract()
    def f():
        return {
            "success": True,
            "data": "x",
            "error": None,
            "source": "orig",
            "source_version": "v",
            "query_time_utc": "2030-01-01T00:00:00Z",
        }

    r = f()
    assert r["data"] == "x"
    assert r["source"] == "orig"
    assert r["source_version"] == "v"
    assert r["query_time_utc"] == "2030-01-01T00:00:00Z"


def test_wrap_non_dict_return():
    @with_return_contract()
    def f():
        return 42

    r = f()
    assert r["success"] is True
    assert r["data"] == 42
    assert r["error"] is None
    assert "source" in r
    assert "source_version" in r
    assert "query_time_utc" in r


def test_wrap_exception():
    @with_return_contract()
    def f():
        raise ValueError("boom")

    r = f()
    assert r["success"] is False
    assert r["data"] is None
    assert "boom" in r["error"]
    assert r["error"].startswith("ValueError: ")
    assert "query_time_utc" in r


def test_never_empty_success_downgrade():
    @with_return_contract()
    def f():
        return {"success": True, "data": None, "error": None}

    r = f()
    assert r["success"] is False
    assert "empty success" in r["error"]


def test_preserves_function_name():
    @with_return_contract()
    def my_unique_tool_name():
        return "ok"

    assert my_unique_tool_name.__name__ == "my_unique_tool_name"
    r = my_unique_tool_name()
    assert r["data"] == "ok"


def test_fills_missing_keys_on_dict_return():
    @with_return_contract(source_version="2.5")
    def f():
        return {"data": 1}

    r = f()
    assert r["success"] is True
    assert r["data"] == 1
    assert r["source_version"] == "2.5"
    assert "source" in r
    assert "query_time_utc" in r

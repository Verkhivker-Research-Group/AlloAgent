"""Return-contract + simple net-call helpers (Part 1c).

Every tool returns the same dict shape:
    {success, data, error, source, source_version, query_time_utc}

The brief also requires 30s timeout, retry with backoff, and on-disk
cache for network tools. Those live in `net_call` and are layered ON
TOP of `with_return_contract`. The first commit covers the return
contract; the timeout/retry/cache behaviour is added in a follow-up
commit (Part 1c follow-up) so the criteria for this Part-1c commit
remain narrowly testable.
"""
from __future__ import annotations

import functools
import time
from typing import Any, Callable


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source_of(func: Callable) -> str:
    return f"{func.__module__}.{func.__name__}"


def with_return_contract(source_version: str = "1.0"):
    """Wrap a tool function so its return value always matches the contract.

    Behaviour:
      * If the function returns a dict, the missing keys (source,
        source_version, query_time_utc) are filled in. If the dict has
        success=True with data=None and error=None, success is
        downgraded to False (never-empty-success rule).
      * If the function returns a non-dict value, the value is wrapped
        as {success: True, data: <value>, error: None, ...}.
      * If the function raises, the exception is caught and returned as
        {success: False, data: None, error: <type+msg>, ...}.
    """
    def deco(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                return {
                    "success": False,
                    "data": None,
                    "error": f"{type(e).__name__}: {e}",
                    "source": _source_of(func),
                    "source_version": source_version,
                    "query_time_utc": _utc_now_iso(),
                }
            if not isinstance(result, dict):
                result = {
                    "success": True,
                    "data": result,
                    "error": None,
                    "source": _source_of(func),
                    "source_version": source_version,
                    "query_time_utc": _utc_now_iso(),
                }
            else:
                if "success" not in result:
                    result["success"] = True
                if result.get("success") and result.get("data") is None and result.get("error") is None:
                    result = {
                        **result,
                        "success": False,
                        "error": "empty success: data and error both None",
                        "source_version": source_version,
                        "query_time_utc": _utc_now_iso(),
                    }
                else:
                    if "source" not in result:
                        result["source"] = _source_of(func)
                    if "source_version" not in result:
                        result["source_version"] = source_version
                    if "query_time_utc" not in result:
                        result["query_time_utc"] = _utc_now_iso()
            return result
        return wrapper
    return deco

"""Benchmark-blocklist decorator (Part 1d).

Off by default. When the env var `BENCHMARK_BLOCKLIST_FILE` is set
(or the default `Biolab/prep_reports/benchmark_blocklist.tsv` exists
and is readable), the decorator loads the file and refuses to call
the wrapped function with a first-positional argument that matches
any blocklisted value.

File format: one value per line; lines starting with `#` are
comments; whitespace is stripped; empty lines are skipped.
"""
from __future__ import annotations

import functools
import os
import time
from pathlib import Path
from typing import Any, Callable


_DEFAULT_PATH = "Biolab/prep_reports/benchmark_blocklist.tsv"


def _blocklist_path() -> Path | None:
    env = os.environ.get("BENCHMARK_BLOCKLIST_FILE")
    candidates = []
    if env:
        candidates.append(Path(env))
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / _DEFAULT_PATH)
    for p in candidates:
        if p.is_file():
            return p
    return None


def _load_blocklist(path: Path) -> set[str]:
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.add(s)
    return out


def benchmark_blocklist(func: Callable) -> Callable:
    """Decorator: refuse the call if the first positional arg is on the
    blocklist. Off by default (no env var, no default file -> no-op).
    """
    cached_blocklist: set[str] | None = None
    cached_path: Path | None = None

    def _get_blocklist() -> set[str] | None:
        nonlocal cached_blocklist, cached_path
        path = _blocklist_path()
        if path is None:
            return None
        if cached_path != path:
            cached_blocklist = _load_blocklist(path)
            cached_path = path
        return cached_blocklist

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        blocklist = _get_blocklist()
        if blocklist is not None and args:
            first = args[0]
            if isinstance(first, str) and first in blocklist:
                return {
                    "success": False,
                    "data": None,
                    "error": f"blocked by benchmark blocklist ({first})",
                    "source": f"{func.__module__}.{func.__name__}",
                    "source_version": "1.0",
                    "query_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
        return func(*args, **kwargs)

    return wrapper

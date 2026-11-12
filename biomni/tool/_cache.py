"""On-disk JSON cache for network-backed tools.

The ported old-repo tools hit several public APIs (PDBe, ChEMBL,
PubChem). Re-running the same lookup inside one evaluation round
should not repeat the network call, and a flaky upstream must not turn
a previously-answered question into a failure.

The cache lives under ``~/.cache/alloagent/`` (override with
``ALLOAGENT_CACHE_DIR``), one JSON file per (url, params) pair, with a
time-to-live. A cache hit is returned as-is; a miss or an expired entry
is a miss.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

DEFAULT_TTL_S = 24 * 3600


def cache_dir() -> Path:
    override = os.environ.get("ALLOAGENT_CACHE_DIR")
    if override:
        return Path(override)
    return Path(os.path.expanduser("~")) / ".cache" / "alloagent"


def cache_key(prefix: str, url: str, params: Optional[dict] = None) -> str:
    payload = url + "|" + json.dumps(params or {}, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"{prefix}_{digest}"


def read_cache(key: str, ttl_s: int = DEFAULT_TTL_S) -> Optional[Any]:
    """Return the cached value, or ``None`` on a miss or an expired entry."""
    path = cache_dir() / f"{key}.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if ttl_s >= 0:
        stored_at = raw.get("stored_at")
        if not isinstance(stored_at, (int, float)):
            return None
        if time.time() - stored_at > ttl_s:
            return None
    return raw.get("value")


def write_cache(key: str, value: Any) -> None:
    """Store a value. A failure to write is not an error for the caller."""
    path = cache_dir() / f"{key}.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"stored_at": time.time(), "value": value}),
            encoding="utf-8",
        )
        tmp.replace(path)
    except (OSError, TypeError, ValueError):
        try:
            if path.with_suffix(".tmp").exists():
                path.with_suffix(".tmp").unlink()
        except OSError:
            pass

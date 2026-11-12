"""The MiniMax quota / throttle check.

It makes one minimal request to the configured endpoint and reports the
status code and the rate-limit headers.  The API key is read from the
environment and is never printed.

    python scripts/minimax_quota_check.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
KEY = os.environ.get("BIOMNI_CUSTOM_API_KEY") or os.environ.get("MINIMAX_API_KEY")
MODEL = os.environ.get("BIOMNI_LLM", "MiniMax-M3")

INTERESTING = (
    "ratelimit", "rate-limit", "x-ratelimit", "retry-after", "x-request-id",
    "cf-ray", "server", "date",
)


def main() -> int:
    if not KEY:
        print("no API key in the environment")
        return 2
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status = response.status
            headers = dict(response.headers)
            body = response.read(400)
    except urllib.error.HTTPError as error:
        status = error.code
        headers = dict(error.headers)
        body = error.read(400)
    except Exception as error:  # noqa: BLE001
        print(f"the request failed: {type(error).__name__}: {error}")
        return 3
    print(f"the endpoint: {BASE}")
    print(f"the status: {status}")
    print("the rate-limit and diagnostic headers:")
    for name, value in sorted(headers.items()):
        if any(name.lower().startswith(prefix) or prefix in name.lower()
               for prefix in INTERESTING):
            print(f"  {name}: {value}")
    try:
        parsed = json.loads(body.decode("utf-8", "replace"))
        usage = parsed.get("usage") or {}
        print(f"the usage of this probe call: {usage}")
        if parsed.get("error"):
            print(f"the error: {json.dumps(parsed['error'])[:200]}")
    except ValueError:
        print(f"the body: {body[:200]!r}")
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())

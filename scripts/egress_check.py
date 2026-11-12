"""The in-container verification of the restricted-egress scenario.

Run inside the container:

    python /workspace/scripts/egress_check.py

It checks that the arbitrary hosts are unreachable and that the LLM
endpoint works.  The exit code is 0 only when every blocked host is
unreachable AND the LLM endpoint answered.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request

BLOCKED_HOSTS = [
    "pypi.org",
    "github.com",
    "files.rcsb.org",
    "api.figshare.com",
    "rest.uniprot.org",
    "www.ebi.ac.uk",
]


def probe(host: str, port: int = 443, timeout: float = 8.0) -> dict:
    """Can we open a TCP connection to host:port?"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"host": host, "port": port, "reachable": True}
    except Exception as error:  # noqa: BLE001 - any failure means blocked
        return {
            "host": host,
            "port": port,
            "reachable": False,
            "error": f"{type(error).__name__}: {error}",
        }


def http_probe(url: str, timeout: float = 10.0) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "egress-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(200)
            return {
                "url": url,
                "status": response.status,
                "first_bytes": body[:80].decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as error:
        return {"url": url, "status": error.code, "note": "an HTTP error still means the host was reached"}
    except Exception as error:  # noqa: BLE001
        return {"url": url, "error": f"{type(error).__name__}: {error}"}


def main() -> int:
    llm_host = os.environ.get("ALLOAGENT_EGRESS_LLM_HOST", "api.minimax.io")
    llm_port = int(os.environ.get("ALLOAGENT_EGRESS_LLM_PORT", "443"))
    base_url = os.environ.get("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
    print(f"the LLM endpoint host: {llm_host}:{llm_port} (base URL {base_url})")
    print(f"the proxy in use: {os.environ.get('HTTPS_PROXY') or 'none'}")
    print()

    print("=== 1. the arbitrary hosts must be unreachable ===")
    blocked_results = []
    for host in BLOCKED_HOSTS:
        direct = probe(host)
        proxied = http_probe(f"https://{host}/")
        blocked = (not direct["reachable"]) and (
            "status" not in proxied or proxied.get("status") == 403
        )
        blocked_results.append(blocked)
        print(f"  {host:20s} direct tcp: {'REACHABLE (BAD)' if direct['reachable'] else 'unreachable'}"
              f" | through the proxy: {proxied.get('status', proxied.get('error', '')[:60])}"
              f" | blocked: {blocked}")
    all_blocked = all(blocked_results)

    print()
    print("=== 2. the LLM endpoint must WORK (through the proxy) ===")
    llm_http = http_probe(base_url)
    llm_reached = "status" in llm_http
    print(f"  http {base_url}: {json.dumps(llm_http)[:200]}")
    llm_ok = llm_reached

    print()
    print(f"every arbitrary host unreachable: {all_blocked}")
    print(f"the LLM endpoint works: {llm_ok}")
    print("RESULT:", "PASS" if (all_blocked and llm_ok) else "FAIL")
    return 0 if (all_blocked and llm_ok) else 1


if __name__ == "__main__":
    sys.exit(main())

"""The egress gate of the restricted scenario: prove the isolation first.

The restricted scenario lets a run reach the LLM endpoint and nothing
else. The isolation is enforced by two things that do not need a
rebuilt image:

* the run container is attached to an INTERNAL docker network, so it
  has no route to the internet at all;
* the only thing it can reach on that network is the egress proxy, and
  the proxy forwards only to the LLM host (everything else gets a 403).

The image carries no ``iptables`` and the images are not rebuilt, so
there is no third, in-container firewall layer. This gate measures the
isolation that actually exists, with the committed check
(``scripts/egress_check.py``): every arbitrary host must be unreachable
and the LLM endpoint must answer. The gate is the evidence that the
restricted runs ran under the isolation the scenario claims.

    python scripts/egress_gate.py --image alloagent-eval:v6 \
        --env-source <path>
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NETWORK = "alloagent_egress_net"


def _env_file(env_vars: dict, prefix: str) -> Path:
    handle = tempfile.NamedTemporaryFile(
        prefix=f"alloagent_env_{prefix}_", suffix=".env", delete=False)
    with handle:
        for key, value in env_vars.items():
            handle.write(f"{key}={value}\n".encode("utf-8"))
    return Path(handle.name)


def _extract_env(source: Path, allow_prefixes=("MINIMAX_", "BIOMNI_")) -> dict:
    out: dict[str, str] = {}
    if not source.is_file():
        return out
    for raw in source.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith(allow_prefixes):
            out[key] = value.strip().strip('"').strip("'")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--image", default="alloagent-eval:v6")
    parser.add_argument("--env-source",
                        default=os.environ.get("ALLOAGENT_ENV_SOURCE")
                        or r"<HOME>\Documents\CPSC\Biolab\.env.extracted")
    parser.add_argument("--out", default=None,
                        help="where to write the gate's evidence (a JSON file)")
    args = parser.parse_args(argv)

    env_vars = _extract_env(Path(args.env_source))
    if "MINIMAX_API_KEY" not in env_vars:
        print("ERROR: no MINIMAX_API_KEY in the env source; aborting")
        return 3
    env_path = _env_file(env_vars, "egress_gate")
    proxy_name = f"alloagent_egress_proxy_gate_{os.getpid()}"
    llm_base = os.environ.get("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
    llm_host = urllib.parse.urlparse(llm_base).hostname or "api.minimax.io"
    llm_port = urllib.parse.urlparse(llm_base).port or 443
    proxy_port = 8877
    try:
        subprocess.run(["docker", "network", "create", "--internal", NETWORK],
                       capture_output=True, text=True)
        subprocess.run(["docker", "rm", "-f", proxy_name],
                       capture_output=True, text=True)
        subprocess.run([
            "docker", "run", "-d", "--name", proxy_name,
            "--network", NETWORK, "--network", "bridge",
            "-v", f"{(REPO / 'scripts' / 'egress_proxy.py').as_posix()}:/egress_proxy.py:ro",
            "--entrypoint", "/opt/conda/envs/alloagent_e1/bin/python",
            args.image, "/egress_proxy.py", str(proxy_port), f"{llm_host}:{llm_port}",
        ], check=True, capture_output=True, text=True)
        result = subprocess.run([
            "docker", "run", "--rm",
            "--env-file", env_path.as_posix(),
            "--network", NETWORK,
            "-e", f"HTTP_PROXY=http://{proxy_name}:{proxy_port}",
            "-e", f"HTTPS_PROXY=http://{proxy_name}:{proxy_port}",
            "-e", "NO_PROXY=",
            "-v", f"{(REPO / 'scripts' / 'egress_check.py').as_posix()}:/harness/egress_check.py:ro",
            "--entrypoint", "/opt/conda/envs/alloagent_e1/bin/python",
            args.image, "/harness/egress_check.py",
        ], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)
        passed = "RESULT: PASS" in result.stdout
        evidence = {
            "image": args.image,
            "network": NETWORK,
            "exit_code": result.returncode,
            "result": "PASS" if passed else "FAIL",
            "stdout": result.stdout,
        }
        if args.out:
            Path(args.out).write_text(
                json.dumps(evidence, indent=2), encoding="utf-8")
        print(f"the egress gate: {evidence['result']} (exit {result.returncode})")
        return 0 if passed else 1
    finally:
        subprocess.run(["docker", "rm", "-f", proxy_name],
                       capture_output=True, text=True)
        try:
            os.unlink(env_path)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

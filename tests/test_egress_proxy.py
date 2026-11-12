"""The egress proxy path: the allowlist, and the upstream failure.

The restricted scenario depends on two facts about the proxy:

* it forwards to the LLM host and refuses everything else;
* an allowed host that cannot be reached is answered with 502 Bad
  Gateway, NOT with 403 Forbidden. A throttled provider makes the
  upstream connect fail, and a 403 there would look like a policy
  refusal (and to the agent's client it looked like a plain connection
  error, which is how a provider throttle turned into a failed run).

The test runs the proxy as a subprocess and drives it with raw
sockets: no network beyond the loopback, no docker, no key.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROXY = REPO / "scripts" / "egress_proxy.py"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _start_proxy(port: int, allowed: str, env_extra: dict | None = None):
    env = os.environ.copy()
    env.update({
        "ALLOAGENT_EGRESS_UPSTREAM_TIMEOUT_S": "2",
        "ALLOAGENT_EGRESS_UPSTREAM_RETRIES": "2",
        "ALLOAGENT_EGRESS_UPSTREAM_RETRY_WAIT_S": "0",
    })
    env.update(env_extra or {})
    process = subprocess.Popen(
        [sys.executable, str(PROXY), str(port), allowed],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
    )
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.1)
    else:
        process.kill()
        raise AssertionError("the proxy did not start")
    return process


def _connect(port: int, target: str) -> bytes:
    """Send a CONNECT and read the proxy's answer."""
    with socket.create_connection(("127.0.0.1", port), timeout=15) as client:
        client.sendall(f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
        return client.recv(200)


def _upstream_listener() -> tuple[int, "object"]:
    """A socket that accepts a connection and holds it, so the proxy's
    upstream connect succeeds."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(8)
    held: list[socket.socket] = []

    def accept_loop() -> None:
        try:
            while True:
                connection, _ = listener.accept()
                held.append(connection)
        except OSError:
            pass

    thread = threading.Thread(target=accept_loop, daemon=True)
    thread.start()
    return listener.getsockname()[1], listener


def test_an_allowed_host_is_allowed_and_another_is_refused():
    upstream_port, listener = _upstream_listener()
    port = _free_port()
    process = _start_proxy(port, f"127.0.0.1:{upstream_port}")
    try:
        allowed = _connect(port, f"127.0.0.1:{upstream_port}")
        refused = _connect(port, "blocked.example:443")
    finally:
        process.kill()
        listener.close()
    assert b"200 Connection established" in allowed, allowed
    assert b"403 Forbidden" in refused, refused


def test_an_unreachable_allowed_host_answers_502_not_403():
    """The upstream cannot be reached: that is a gateway failure, not a
    policy refusal."""
    port = _free_port()
    # 192.0.2.0/24 is the TEST-NET-1 range: it is routable in the
    # address space but never answers, so the connect times out.
    process = _start_proxy(port, "192.0.2.1:443")
    try:
        answer = _connect(port, "192.0.2.1:443")
    finally:
        process.kill()
    assert b"502 Bad Gateway" in answer, answer
    assert b"403 Forbidden" not in answer, answer


def test_the_upstream_connect_is_retried():
    port = _free_port()
    process = _start_proxy(port, "192.0.2.1:443")
    try:
        _connect(port, "192.0.2.1:443")
        process.terminate()
        log = process.stdout.read() if process.stdout else ""
    finally:
        if process.poll() is None:
            process.kill()
    assert log.count("did not connect") == 2, (
        "the upstream connect must be retried: " + log)

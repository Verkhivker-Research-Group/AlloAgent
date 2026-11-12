"""The allowlist proxy for the restricted-egress scenario.

The agent container is attached to an INTERNAL docker network, which
has no route to the internet at all, so no host is reachable from it -
not even by IP address.  The only way out is this proxy, which listens
on the internal network and forwards to exactly one host: the LLM
endpoint.  Every other destination is refused with 403.

A destination that IS allowed but cannot be reached (the provider is
throttling, the upstream connect times out) is answered with 502 Bad
Gateway, not with 403: a policy refusal and an upstream failure are
different facts, and the client has to be able to tell them apart.
The upstream connect is retried a few times before it is given up on.

    python egress_proxy.py <port> <allowed-host[:port]> ...
"""
from __future__ import annotations

import os
import socket
import socketserver
import sys
import threading
import time

ALLOWED: list[tuple[str, int]] = []
REFUSED = b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
BAD_GATEWAY = b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
OK = b"HTTP/1.1 200 Connection established\r\n\r\n"

UPSTREAM_TIMEOUT_S = float(os.environ.get("ALLOAGENT_EGRESS_UPSTREAM_TIMEOUT_S") or 60)
UPSTREAM_RETRIES = int(os.environ.get("ALLOAGENT_EGRESS_UPSTREAM_RETRIES") or 3)
UPSTREAM_RETRY_WAIT_S = float(os.environ.get("ALLOAGENT_EGRESS_UPSTREAM_RETRY_WAIT_S") or 2)


def allowed(host: str, port: int) -> bool:
    for allowed_host, allowed_port in ALLOWED:
        if allowed_host == host and allowed_port == port:
            return True
        if allowed_port == 0 and allowed_host == host:
            return True
    return False


def pipe(source: socket.socket, sink: socket.socket) -> None:
    try:
        while True:
            data = source.recv(65536)
            if not data:
                break
            sink.sendall(data)
    except OSError:
        pass
    finally:
        for sock in (source, sink):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()


def open_upstream(host: str, port: int) -> socket.socket:
    """Connect to the allowed upstream, retrying a transient failure.

    The provider throttles, and a throttled provider can refuse or
    delay the TCP connect. A single failed connect must not look like a
    policy refusal, so the connect is retried before it is given up on.
    """
    last: OSError | None = None
    for attempt in range(UPSTREAM_RETRIES):
        try:
            return socket.create_connection((host, port), timeout=UPSTREAM_TIMEOUT_S)
        except OSError as error:
            last = error
            print(f"[proxy] the upstream {host}:{port} did not connect "
                  f"(attempt {attempt + 1}/{UPSTREAM_RETRIES}): {error}",
                  flush=True)
            if attempt + 1 < UPSTREAM_RETRIES:
                time.sleep(UPSTREAM_RETRY_WAIT_S)
    raise last if last else OSError("the upstream connect failed")


def handle_connect(client: socket.socket, target_host: str, target_port: int) -> None:
    if not allowed(target_host, target_port):
        client.sendall(REFUSED)
        client.close()
        print(f"[proxy] REFUSED {target_host}:{target_port}", flush=True)
        return
    try:
        upstream = open_upstream(target_host, target_port)
    except OSError as error:
        client.sendall(BAD_GATEWAY)
        client.close()
        print(f"[proxy] FAILED {target_host}:{target_port}: {error}", flush=True)
        return
    client.sendall(OK)
    print(f"[proxy] ALLOWED {target_host}:{target_port}", flush=True)
    threading.Thread(target=pipe, args=(client, upstream), daemon=True).start()
    pipe(upstream, client)


class ProxyHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        request_line = self.rfile.readline(65536).decode("latin-1").strip()
        if not request_line:
            return
        parts = request_line.split()
        if len(parts) < 2:
            self.wfile.write(REFUSED)
            return
        method, target = parts[0], parts[1]
        while True:  # consume the headers
            line = self.rfile.readline(65536)
            if not line or line in (b"\r\n", b"\n"):
                break
        if method == "CONNECT":
            host, _, port_text = target.rpartition(":")
            handle_connect(self.connection, host, int(port_text or 443))
            return
        # a plain (absolute-URI) request
        _, _, remainder = target.partition("://")
        host_port, _, path = remainder.partition("/")
        host, _, port_text = host_port.partition(":")
        port = int(port_text or 80)
        if not allowed(host, port):
            self.wfile.write(REFUSED)
            print(f"[proxy] REFUSED {host}:{port}", flush=True)
            return
        try:
            upstream = open_upstream(host, port)
        except OSError as error:
            self.wfile.write(BAD_GATEWAY)
            print(f"[proxy] FAILED {host}:{port}: {error}", flush=True)
            return
        upstream.sendall(
            f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
        )
        while True:
            data = upstream.recv(65536)
            if not data:
                break
            self.wfile.write(data)
        upstream.close()
        print(f"[proxy] ALLOWED {host}:{port}", flush=True)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    # The agent opens a burst of connections; the default backlog of 5
    # makes the kernel refuse the handshake under a burst.
    request_queue_size = 128


def main() -> int:
    port = int(sys.argv[1])
    for entry in sys.argv[2:]:
        host, _, port_text = entry.rpartition(":")
        if not host:
            host, port_text = entry, ""
        ALLOWED.append((host, int(port_text) if port_text else 0))
    print(f"[proxy] listening on 0.0.0.0:{port}, allowed: {ALLOWED}", flush=True)
    Server(("0.0.0.0", port), ProxyHandler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

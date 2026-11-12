"""Tests for scripts/_resumable.py.

This file restores the 14 test_resumable.py tests that existed
at commit 63641d9 (before the _resumable.py rewrite in 8956a6a),
adapted to the fixed API (per-file manifest, extension-dispatched
integrity check). It also keeps the 3 new tests that verify the
bug fixes (shared-MANIFEST and is_zip gzip -t).

Mapping of the 14 old tests at 63641d9 -> current:

| 63641d9 node ID                              | Status     | Notes |
|----------------------------------------------|------------|-------|
| test_head_size_returns_content_length        | kept       | API unchanged |
| test_download_to_part_renames_on_success    | kept       | API unchanged |
| test_resume_after_interruption               | kept       | API unchanged |
| test_never_deletes_partial_file_on_failure   | kept       | API unchanged |
| test_resume_uses_http_range_header           | kept       | API unchanged |
| test_size_mismatch_returns_error             | kept       | API unchanged |
| test_expected_sha256_mismatch_returns_error  | kept       | API unchanged |
| test_expected_sha256_match_succeeds          | kept       | API unchanged |
| test_write_and_read_manifest_roundtrip       | kept       | now uses per-file manifest path |
| test_gzip_integrity_check                    | kept       | .gz path still uses gzip -t |
| test_gzip_integrity_check_fails_on_corrupt    | kept       | .gz path still uses gzip -t |
| test_fetch_with_manifest_skips_when_present_and_matching | kept       | adapted to per-file manifest |
| test_fetch_with_manifest_redownloads_when_size_mismatches | kept       | adapted: now expects re-download to succeed |
| test_fetch_with_manifest_overwrites_on_existing_wrong_file | kept | adapted: no manifest written, file has wrong content |

Plus the 3 new tests (must be kept, they test the bug fixes):
- test_multi_file_download_uses_per_file_manifest
- test_zip_file_is_zipfile_not_gzip
- test_gzip_file_still_uses_gzip_check
"""
from __future__ import annotations

import gzip
import hashlib
import http.server
import io
import os
import socket
import threading
import time
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(REPO / "scripts"))
import _resumable  # noqa: E402


PAYLOAD = os.urandom(2 * 1024 * 1024 + 137)
PAYLOAD_SHA256 = hashlib.sha256(PAYLOAD).hexdigest()
PAYLOAD_MD5 = hashlib.md5(PAYLOAD).hexdigest()


class _FlakyServer:
    """Tiny HTTP/1.1 server that serves a fixed payload, with
    optional interruption after the first N bytes to simulate a
    network drop."""

    def __init__(self, payload: bytes, cut_after=None, allow_range=True):
        self.payload = payload
        self.cut_after = cut_after
        self.allow_range = allow_range
        self.requests: list[dict] = []
        self._server: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port: int = 0
        self.hits = 0

    def __enter__(self):
        payload = self.payload
        cut_after = self.cut_after
        allow_range = self.allow_range
        requests = self.requests
        get_hits = [0]

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args, **kwargs):
                pass

            def do_HEAD(self):
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()

            def do_GET(self):
                get_hits[0] += 1
                req_range = self.headers.get("Range")
                requests.append({"path": self.path, "range": req_range})
                if allow_range and req_range and req_range.startswith("bytes="):
                    spec = req_range[len("bytes="):]
                    start_s, _, end_s = spec.partition("-")
                    start = int(start_s) if start_s else 0
                    end = int(end_s) if end_s else len(payload) - 1
                    chunk = payload[start: end + 1]
                    self.send_response(206)
                    self.send_header("Content-Range",
                                     f"bytes {start}-{end}/{len(payload)}")
                    self.send_header("Content-Length", str(len(chunk)))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    self.wfile.write(chunk)
                    return
                if cut_after is not None and get_hits[0] == 1:
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(payload)))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    self.wfile.write(payload[:cut_after])
                    try:
                        self.wfile.flush()
                    except Exception:
                        pass
                    try:
                        self.connection.shutdown(socket.SHUT_WR)
                    except Exception:
                        pass
                    return
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(payload)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        sock.listen(5)
        self.port = sock.getsockname()[1]
        sock.close()
        self._server = http.server.HTTPServer(("127.0.0.1", self.port), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever,
                                         daemon=True)
        self._thread.start()
        self.hits = get_hits
        return self

    def __exit__(self, *exc):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
        return False

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/payload.bin"

    @property
    def hit_count(self) -> int:
        return self.hits[0]


# ---------------------------------------------------------------------------
# Tests restored from 63641d9 (adapted to the fixed _resumable.py API)
# ---------------------------------------------------------------------------


def test_head_size_returns_content_length():
    with _FlakyServer(PAYLOAD) as s:
        size = _resumable.head_size(s.url)
    assert size == len(PAYLOAD)


def test_download_to_part_renames_on_success(tmp_path: Path):
    out = tmp_path / "file.bin"
    part = out.with_suffix(out.suffix + ".part")
    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt"
        )
    assert result["ok"] is True
    assert out.is_file()
    assert not part.exists()
    assert result["size_bytes"] == len(PAYLOAD)
    assert result["sha256"] == PAYLOAD_SHA256
    assert result["md5"] == PAYLOAD_MD5
    assert result["error"] is None


def test_resume_after_interruption(tmp_path: Path):
    out = tmp_path / "file.bin"
    part = out.with_suffix(out.suffix + ".part")
    cut = len(PAYLOAD) // 3

    with _FlakyServer(PAYLOAD, cut_after=cut) as s1:
        result1 = _resumable.download_resumable(
            s1.url, out, log_file=tmp_path / "log.txt",
            timeout=10, chunk_size=8 * 1024,
        )
    assert result1["ok"] is False
    assert part.is_file(), "partial file kept on first-run failure"
    assert not out.exists(), "final file must not exist on failed download"
    first_run_size = part.stat().st_size
    assert first_run_size > 0

    with _FlakyServer(PAYLOAD) as s2:
        result2 = _resumable.download_resumable(
            s2.url, out, log_file=tmp_path / "log.txt",
            timeout=10, chunk_size=8 * 1024,
        )
    assert result2["ok"] is True
    assert out.is_file()
    assert not part.exists()
    assert result2["sha256"] == PAYLOAD_SHA256
    assert s2.requests[-1]["range"] is not None
    assert s2.requests[-1]["range"].startswith("bytes=")


def test_never_deletes_partial_file_on_failure(tmp_path: Path):
    out = tmp_path / "file.bin"
    part = out.with_suffix(out.suffix + ".part")
    cut = len(PAYLOAD) // 4

    with _FlakyServer(PAYLOAD, cut_after=cut) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt",
            timeout=10, chunk_size=8 * 1024,
        )
    assert result["ok"] is False
    assert part.is_file(), "partial file must be kept on failure"
    assert not out.exists(), "final file must not exist on failure"


def test_resume_uses_http_range_header(tmp_path: Path):
    out = tmp_path / "file.bin"
    part = out.with_suffix(out.suffix + ".part")
    partial_size = 100
    part.write_bytes(PAYLOAD[:partial_size])

    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt",
            timeout=10, chunk_size=8 * 1024,
        )
    assert result["ok"] is True
    assert out.is_file()
    assert result["sha256"] == PAYLOAD_SHA256
    assert s.requests[0]["range"] == f"bytes={partial_size}-"


def test_size_mismatch_returns_error(tmp_path: Path):
    out = tmp_path / "file.bin"
    truncated = PAYLOAD[: len(PAYLOAD) - 10]

    class TruncatedHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args, **kwargs):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", str(len(PAYLOAD)))
            self.end_headers()
            self.wfile.write(truncated)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(5)
    port = sock.getsockname()[1]
    sock.close()
    server = http.server.HTTPServer(("127.0.0.1", port), TruncatedHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = _resumable.download_resumable(
            f"http://127.0.0.1:{port}/p", out,
            log_file=tmp_path / "log.txt", timeout=10,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result["ok"] is False
    assert "size mismatch" in (result["error"] or "")
    part = out.with_suffix(out.suffix + ".part")
    assert part.is_file(), "partial file kept on size mismatch"


def test_expected_sha256_mismatch_returns_error(tmp_path: Path):
    out = tmp_path / "file.bin"
    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt",
            expected_sha256="0" * 64, timeout=10,
        )
    assert result["ok"] is False
    assert "sha256 mismatch" in (result["error"] or "")
    part = out.with_suffix(out.suffix + ".part")
    assert part.is_file(), "partial file kept on checksum mismatch"
    assert not out.exists()


def test_expected_sha256_match_succeeds(tmp_path: Path):
    out = tmp_path / "file.bin"
    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt",
            expected_sha256=PAYLOAD_SHA256, timeout=10,
        )
    assert result["ok"] is True
    assert result["sha256"] == PAYLOAD_SHA256


def test_write_and_read_manifest_roundtrip(tmp_path: Path):
    out = tmp_path / "file.bin"
    out.write_bytes(b"hello")
    _resumable.write_manifest(
        out, "https://example.com/x", "abc", "def", 5,
        "2026-10-10T00:00:00Z", "2026-10-10T00:00:01Z",
        extra={"license": "public-domain", "schema": "TSV"},
    )
    m = _resumable.read_manifest(out)
    assert m["url"] == "https://example.com/x"
    assert m["sha256"] == "abc"
    assert m["md5"] == "def"
    assert m["size_bytes"] == "5"
    assert m["license"] == "public-domain"
    assert m["schema"] == "TSV"
    # Per-file manifest: the manifest file is MANIFEST.<basename>
    manifest_path = out.parent / f"MANIFEST.{out.name}"
    assert manifest_path.is_file()


def test_gzip_integrity_check(tmp_path: Path):
    gz = tmp_path / "blob.gz"
    with gzip.open(str(gz), mode="wb") as f:
        f.write(b"hello world" * 1000)
    out = tmp_path / "blob.copy.gz"
    with _FlakyServer(gz.read_bytes()) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt", is_zip=True,
        )
    assert result["ok"] is True
    assert out.is_file()


def test_gzip_integrity_check_fails_on_corrupt(tmp_path: Path):
    corrupt = b"not a gzip file at all"
    out = tmp_path / "blob.gz"
    with _FlakyServer(corrupt) as s:
        result = _resumable.download_resumable(
            s.url, out, log_file=tmp_path / "log.txt", is_zip=True,
        )
    assert result["ok"] is False
    assert ("gzip" in (result["error"] or "").lower()
            or "corrupt" in (result["error"] or ""))
    part = out.with_suffix(out.suffix + ".part")
    assert part.is_file()


def test_fetch_with_manifest_skips_when_present_and_matching(tmp_path: Path):
    """With per-file manifest: if the file and its per-file
    MANIFEST.<basename> both exist and match, the download is
    skipped."""
    out = tmp_path / "file.bin"
    out.write_bytes(PAYLOAD)
    _resumable.write_manifest(
        out, "https://example.com/payload.bin", PAYLOAD_SHA256, PAYLOAD_MD5,
        len(PAYLOAD), "2026-10-10T00:00:00Z", "2026-10-10T00:00:01Z",
    )
    result = _resumable.fetch_with_manifest(
        "https://example.com/payload.bin", out,
        log_file=tmp_path / "log.txt",
    )
    assert result["ok"] is True
    assert result.get("skipped") is True
    assert result["size_bytes"] == len(PAYLOAD)


def test_fetch_with_manifest_redownloads_when_size_mismatches(tmp_path: Path):
    """With per-file manifest: if the file exists but its sha256
    does not match the manifest, the function deletes the wrong
    file and re-downloads. The re-download should succeed."""
    out = tmp_path / "file.bin"
    out.write_bytes(b"x" * 100)
    _resumable.write_manifest(
        out, "https://example.com/payload.bin",
        "0" * 64, "0" * 32, 100,
        "2026-10-10T00:00:00Z", "2026-10-10T00:00:01Z",
    )
    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.fetch_with_manifest(
            s.url, out, log_file=tmp_path / "log.txt",
        )
    assert result["ok"] is True, (
        f"re-download failed: {result}. The function should detect "
        f"the sha256 mismatch, delete the wrong file, and re-download."
    )
    assert result.get("skipped") is not True
    assert result["sha256"] == PAYLOAD_SHA256
    manifest = _resumable.read_manifest(out)
    assert manifest["sha256"] == PAYLOAD_SHA256


def test_fetch_with_manifest_overwrites_on_existing_wrong_file(tmp_path: Path):
    """If the file exists but no manifest, the function should
    detect the existing file's sha256 (by writing a fresh manifest
    after re-download). The re-download should succeed."""
    out = tmp_path / "file.bin"
    out.write_bytes(b"x" * 100)
    with _FlakyServer(PAYLOAD) as s:
        result = _resumable.fetch_with_manifest(
            s.url, out, log_file=tmp_path / "log.txt",
        )
    assert result["ok"] is True
    assert result.get("skipped") is not True
    assert result["sha256"] == PAYLOAD_SHA256
    manifest = _resumable.read_manifest(out)
    assert manifest["sha256"] == PAYLOAD_SHA256
    assert int(manifest["size_bytes"]) == len(PAYLOAD)


# ---------------------------------------------------------------------------
# New tests (must be kept: they verify the two bug fixes)
# ---------------------------------------------------------------------------


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def test_multi_file_download_uses_per_file_manifest(tmp_path):
    """Bug 1: two files downloaded into the same directory must
    use independent per-file manifests. Before the fix, the
    second file reads the first file's MANIFEST and gets a
    spurious sha256 mismatch."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        files: dict[str, bytes] = {}

        def do_GET(self):
            if self.path not in self.files:
                self.send_response(404); self.end_headers(); return
            body = self.files[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args, **kwargs):
            pass

    port = _free_port()
    httpd = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        file_a = b"AAAA" * 1024
        file_b = b"BBBB" * 1024
        _Handler.files["/a.bin"] = file_a
        _Handler.files["/b.bin"] = file_b
        out_a = tmp_path / "a.bin"
        out_b = tmp_path / "b.bin"
        r1 = _resumable.fetch_with_manifest(
            f"http://127.0.0.1:{port}/a.bin", out_a,
        )
        r2 = _resumable.fetch_with_manifest(
            f"http://127.0.0.1:{port}/b.bin", out_b,
        )
    finally:
        httpd.shutdown(); httpd.server_close(); t.join(timeout=2)

    assert r1["ok"], f"file A failed: {r1}"
    assert r2["ok"], (
        f"file B failed (this is the shared-MANIFEST bug): {r2}. "
        f"Expected: per-file manifest so the second file's "
        f"download is not constrained by the first file's sha256."
    )
    assert out_a.read_bytes() == file_a
    assert out_b.read_bytes() == file_b


def test_zip_file_is_zipfile_not_gzip(tmp_path):
    """Bug 2: a real ZIP archive must be verified with
    zipfile.testzip(), not 'gzip -t'. Before the fix, the
    is_zip=True flag runs 'gzip -t' which reports 'has more
    than one entry' for a real ZIP."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        files: dict[str, bytes] = {}

        def do_GET(self):
            if self.path not in self.files:
                self.send_response(404); self.end_headers(); return
            body = self.files[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args, **kwargs):
            pass

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("a.txt", "hello")
        zf.writestr("b.txt", "world")
    zip_bytes = buf.getvalue()

    port = _free_port()
    httpd = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        _Handler.files["/test.zip"] = zip_bytes
        out = tmp_path / "test.zip"
        r = _resumable.download_resumable(
            f"http://127.0.0.1:{port}/test.zip", out, is_zip=True,
        )
    finally:
        httpd.shutdown(); httpd.server_close(); t.join(timeout=2)

    assert r["ok"], (
        f"ZIP download failed (this is the gzip -t bug): {r}. "
        f"Expected: zipfile.testzip() for ZIP archives, not 'gzip -t'."
    )
    assert out.read_bytes() == zip_bytes


def test_gzip_file_still_uses_gzip_check(tmp_path):
    """The is_zip=True flag should STILL work for real .gz files
    (used by fetch_alphamissense / fetch_clinvar)."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        files: dict[str, bytes] = {}

        def do_GET(self):
            if self.path not in self.files:
                self.send_response(404); self.end_headers(); return
            body = self.files[self.path]
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args, **kwargs):
            pass

    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode="wb") as gz:
        gz.write(b"hello world")
    gz_bytes = gz_buf.getvalue()

    port = _free_port()
    httpd = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        _Handler.files["/test.txt.gz"] = gz_bytes
        out = tmp_path / "test.txt.gz"
        r = _resumable.download_resumable(
            f"http://127.0.0.1:{port}/test.txt.gz", out, is_zip=True,
        )
    finally:
        httpd.shutdown(); httpd.server_close(); t.join(timeout=2)

    assert r["ok"], f"gzip download failed: {r}"
    assert gzip.decompress(out.read_bytes()) == b"hello world"

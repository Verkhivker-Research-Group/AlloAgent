"""scripts/_resumable.py -- shared resumable download helper.

All three fetch scripts (alphamissense, clinvar, chembl) share
this implementation. The design rules are:

- Write to ``<output_path>.part`` while downloading; only move
  to the final name after the checksum verifies.
- Resume with HTTP Range requests: if ``<output_path>.part``
  already exists, the next download starts at
  ``Range: bytes=<existing_size>-`` and appends to the partial.
- Retry with exponential backoff on transient errors
  (connection reset, timeout, 5xx). Up to N retries; non-2xx
  after Range is sent triggers a retry without truncating the
  partial.
- Compute sha256 and md5 of the final file. If an expected
  checksum is provided in the manifest, verify against it.
  If not, record the computed checksum in the manifest.
- Log progress to a log file (append, one line per progress
  tick + a DONE/ERROR line at the end).
- Never delete a partial file. If the download is interrupted
  or the checksum fails, the ``.part`` file is left on disk
  so the next run can resume.
"""
from __future__ import annotations

import gzip as _gzip
import hashlib
import http.client
import os
import subprocess
import time
import zlib as _zlib
from pathlib import Path
from typing import Callable, Optional

import requests
import urllib3

_CHUNK = 1 << 20  # 1 MiB
_DEFAULT_TIMEOUT_S = 1200
_MAX_RETRIES = 5
_INITIAL_BACKOFF_S = 2.0
_BACKOFF_MULTIPLIER = 2.0
_BACKOFF_CAP_S = 60.0
_PROGRESS_TICK_BYTES = 50 * (1 << 20)  # log every 50 MiB

# Errors a broken connection can raise below the ``requests`` layer.
# ``requests`` converts ``urllib3.exceptions.ProtocolError`` into
# ``requests.exceptions.ChunkedEncodingError``, but only inside
# ``Response.iter_content()``.  Any other caller that touches the body
# (for example an HTTP-cache library that copies the body eagerly) can
# let the raw urllib3 / http.client error escape, so both levels are
# caught here.
_NETWORK_ERRORS = (
    urllib3.exceptions.HTTPError,   # ProtocolError, ReadTimeoutError, ...
    http.client.HTTPException,       # IncompleteRead, RemoteDisconnected, ...
)


def _plain_session() -> "requests.Session":
    """Return a ``requests`` session that is NOT an HTTP-cache session.

    ``requests-cache`` replaces ``requests.sessions.Session`` globally
    (``requests_cache/patcher.py``) when a cache is installed.  In this
    repo ``pybiomart`` does that at import time
    (``requests_cache.install_cache('.pybiomart')``), and ``biomni``
    imports ``pybiomart``, so any process that has imported ``biomni``
    has a caching session by default.

    The caching session copies the whole response body into the cache
    *before* the caller can stream it.  For a multi-GB download that is
    both wrong (the bytes are duplicated on disk) and it breaks the
    resume logic: an interrupted transfer then raises a raw
    ``urllib3.exceptions.ProtocolError`` out of ``requests.get()``
    instead of the converted ``requests.exceptions.ChunkedEncodingError``,
    and no partial file is written.

    Walking the MRO back to the class that really lives in
    ``requests.sessions`` gives the unpatched session, which streams the
    body and lets ``requests`` convert the error as usual.
    """
    cls = getattr(requests.sessions, "Session", None)
    if cls is None:  # pragma: no cover - requests always ships one
        return requests.Session()
    for base in getattr(cls, "__mro__", (cls,)):
        if base.__module__ == "requests.sessions" and base.__name__ == "Session":
            return base()
    return cls()


def _interrupted_error(exc: BaseException, written: int, expected_size: Optional[int]) -> str:
    """Message for a transfer that ended before the whole body arrived."""
    if expected_size:
        return (
            f"size mismatch: interrupted transfer after {written} of "
            f"{expected_size} bytes ({exc!r})"
        )
    return f"size mismatch: interrupted transfer ({exc!r})"


def _log(log_file: Optional[Path], msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a") as f:
            f.write(line + "\n")


def head_size(url: str, timeout: float = 15.0) -> Optional[int]:
    """HEAD-request the URL and return the Content-Length in bytes.

    Returns None if the HEAD request fails or the response has
    no Content-Length.
    """
    try:
        with _plain_session() as session:
            r = session.head(url, allow_redirects=True, timeout=timeout)
            if r.status_code == 200:
                return int(r.headers.get("Content-Length", 0))
            return None
    except requests.exceptions.RequestException:
        return None


def fetch_expected_checksum(
    url: str,
    algorithm: str = "sha256",
    timeout: float = 15.0,
) -> Optional[str]:
    """Fetch the published checksum for ``url``.

    Looks for ``<url>.sha256``, ``<url>.md5``, or
    ``<url>.CHECKSUM`` (case-insensitive). Returns the lowercase
    hex digest, or None if no published checksum is available.
    """
    algo_ext = algorithm.lower()
    for ext in (f".{algo_ext}", ".CHECKSUM", ".checksum"):
        try:
            with _plain_session() as session:
                r = session.get(url + ext, allow_redirects=True, timeout=timeout)
                if r.status_code == 200:
                    text = r.text.strip()
                    parts = text.split()
                    if parts:
                        return parts[0].lower()
        except requests.exceptions.RequestException:
            continue
    return None


def _hash_file(path: Path, algorithms: tuple[str, ...] = ("sha256", "md5")) -> dict[str, str]:
    """Compute the requested checksums of a file. Returns {algo: hex_digest}."""
    hashers = {algo: hashlib.new(algo) for algo in algorithms}
    with path.open("rb") as f:
        while True:
            chunk = f.read(_CHUNK)
            if not chunk:
                break
            for h in hashers.values():
                h.update(chunk)
    return {algo: h.hexdigest() for algo, h in hashers.items()}


def _gzip_integrity_error(path: Path) -> Optional[str]:
    """Return an error string if ``path`` is not a readable gzip stream.

    Implemented with the stdlib rather than by shelling out to
    ``gzip -t``: the ``gzip`` executable is not on PATH on Windows, so a
    subprocess call raised FileNotFoundError and crashed the download
    immediately after the bytes arrived -- leaving a complete ``.part``
    that could never be renamed. Reading the stream in Python is
    cross-platform and has no external dependency.
    """
    try:
        with _gzip.open(str(path), "rb") as fh:
            while fh.read(1 << 20):
                pass
    except (OSError, EOFError, _gzip.BadGzipFile, _zlib.error) as exc:
        return f"gzip integrity check failed: {exc}"
    return None


def download_resumable(
    url: str,
    output_path: Path,
    log_file: Optional[Path] = None,
    expected_sha256: Optional[str] = None,
    timeout: float = _DEFAULT_TIMEOUT_S,
    chunk_size: int = _CHUNK,
    is_zip: bool = False,
) -> dict:
    """Download ``url`` to ``output_path`` with resume + verify.

    Writes to ``<output_path>.part`` while downloading. On
    success, verifies the checksum (if ``expected_sha256`` is
    provided) and renames ``.part`` to the final name. On
    failure (network error, checksum mismatch, or non-resumable
    error), the ``.part`` file is left on disk for the next
    run to resume. Never deletes a partial file.

    Parameters
    ----------
    url : str
        Source URL.
    output_path : Path
        Final destination path. The partial file is
        ``<output_path>.part``.
    log_file : Path or None
        Append-only log file. Also written to stdout.
    expected_sha256 : str or None
        If provided, the downloaded file's sha256 must match.
        If not provided, the computed sha256 is recorded in
        the manifest for future verification.
    timeout : float
        Per-request timeout in seconds.
    chunk_size : int
        Stream chunk size in bytes.
    is_zip : bool
        If True, the file is gzipped; the script will
        ``gzip -t`` it before renaming.

    Returns
    -------
    dict
        ``{"ok": bool, "path": str, "size_bytes": int,
        "sha256": str, "md5": str, "error": str or None,
        "elapsed_s": float}``.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = output_path.with_suffix(output_path.suffix + ".part")
    log_file = Path(log_file) if log_file is not None else output_path.parent / "download.log"

    expected_size = head_size(url)
    if expected_size is None:
        _log(log_file, f"HEAD failed for {url}; cannot verify size on completion")
    else:
        _log(log_file, f"server reports Content-Length: {expected_size} bytes ({expected_size / (1024*1024):.1f} MB)")

    # Check existing partial
    existing = part_path.stat().st_size if part_path.is_file() else 0
    if existing > 0:
        _log(log_file, f"resuming from existing partial: {part_path} ({existing} bytes)")

    headers: dict[str, str] = {}
    if existing > 0:
        headers["Range"] = f"bytes={existing}-"
    if expected_sha256:
        _log(log_file, f"expected sha256: {expected_sha256}")

    t0 = time.monotonic()
    backoff = _INITIAL_BACKOFF_S
    last_error: Optional[str] = None
    written = existing

    for attempt in range(1, _MAX_RETRIES + 2):
        # The partial file is created before the first request so that a
        # failure before the first byte still leaves a .part behind for
        # the next run to resume from.
        if not part_path.exists():
            part_path.touch()
        session = _plain_session()
        try:
            with session.get(
                url, stream=True, timeout=timeout, headers=headers or None
            ) as r:
                if r.status_code == 416:
                    _log(log_file, "server returned 416 Range Not Satisfiable; treating as already complete")
                    break
                if r.status_code not in (200, 206):
                    last_error = f"HTTP {r.status_code}: {r.text[:200]}"
                    _log(log_file, f"attempt {attempt}: {last_error}")
                    time.sleep(min(backoff, _BACKOFF_CAP_S))
                    backoff *= _BACKOFF_MULTIPLIER
                    continue
                mode = "ab" if existing > 0 else "wb"
                with part_path.open(mode) as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        written += len(chunk)
                        if expected_size and written > expected_size:
                            err = f"size mismatch: server sent more than Content-Length ({written} > {expected_size})"
                            _log(log_file, f"attempt {attempt}: {err}; partial kept at {part_path}")
                            raise requests.exceptions.ChunkedEncodingError(err)
                        if written % _PROGRESS_TICK_BYTES < chunk_size:
                            pct = 100 * written / expected_size if expected_size else 0
                            _log(log_file, f"  {written / (1024*1024):.1f} / {expected_size / (1024*1024) if expected_size else 0:.1f} MB ({pct:.0f}%)")
                break
        except requests.exceptions.ChunkedEncodingError as exc:
            last_error = f"size mismatch: {exc!r}"
            _log(log_file, f"FAILED: {last_error}; partial kept at {part_path}")
            return {
                "ok": False, "path": str(output_path), "size_bytes": written,
                "sha256": None, "md5": None, "error": last_error,
                "elapsed_s": time.monotonic() - t0,
            }
        except requests.exceptions.RequestException as exc:
            last_error = f"requests error: {exc!r}"
            _log(log_file, f"attempt {attempt}: {last_error}")
            time.sleep(min(backoff, _BACKOFF_CAP_S))
            backoff *= _BACKOFF_MULTIPLIER
        except _NETWORK_ERRORS as exc:
            last_error = _interrupted_error(exc, written, expected_size)
            _log(log_file, f"FAILED: {last_error}; partial kept at {part_path}")
            return {
                "ok": False, "path": str(output_path), "size_bytes": written,
                "sha256": None, "md5": None, "error": last_error,
                "elapsed_s": time.monotonic() - t0,
            }
        finally:
            session.close()
    else:
        elapsed = time.monotonic() - t0
        _log(log_file, f"FAILED after {_MAX_RETRIES + 1} attempts; partial kept at {part_path} ({written} bytes)")
        return {
            "ok": False, "path": str(output_path), "size_bytes": written,
            "sha256": None, "md5": None, "error": last_error or "max retries",
            "elapsed_s": elapsed,
        }

    if expected_size and written != expected_size:
        err = f"size mismatch: expected {expected_size}, got {written}"
        _log(log_file, f"FAILED: {err}; partial kept at {part_path}")
        return {
            "ok": False, "path": str(output_path), "size_bytes": written,
            "sha256": None, "md5": None, "error": err, "elapsed_s": time.monotonic() - t0,
        }

    if is_zip:
        # Dispatch on the file extension: .gz files use
        # 'gzip -t' (used by fetch_alphamissense / fetch_clinvar);
        # .zip files use zipfile.testzip() (used by
        # fetch_cryptobench). The previous behaviour ran
        # 'gzip -t' for everything, which incorrectly failed
        # on real ZIP archives (they are not gzip streams).
        if str(output_path).endswith(".zip"):
            import zipfile as _zipfile
            try:
                with _zipfile.ZipFile(part_path) as _zf:
                    _bad = _zf.testzip()
                if _bad is not None:
                    err = f"zipfile integrity check failed: corrupt entry {_bad}"
                    _log(log_file, f"FAILED: {err}; partial kept at {part_path}")
                    return {
                        "ok": False, "path": str(output_path), "size_bytes": written,
                        "sha256": None, "md5": None, "error": err,
                        "elapsed_s": time.monotonic() - t0,
                    }
            except _zipfile.BadZipFile as exc:
                err = f"zipfile integrity check failed: {exc}"
                _log(log_file, f"FAILED: {err}; partial kept at {part_path}")
                return {
                    "ok": False, "path": str(output_path), "size_bytes": written,
                    "sha256": None, "md5": None, "error": err,
                    "elapsed_s": time.monotonic() - t0,
                }
            _log(log_file, "zipfile integrity OK")
        else:
            try:
                err = _gzip_integrity_error(part_path)
            except OSError as exc:
                err = f"gzip integrity check could not read the file: {exc}"
            if err:
                _log(log_file, f"FAILED: {err}; partial kept at {part_path}")
                return {
                    "ok": False, "path": str(output_path), "size_bytes": written,
                    "sha256": None, "md5": None, "error": err,
                    "elapsed_s": time.monotonic() - t0,
                }
            _log(log_file, "gzip integrity OK")

    _log(log_file, "computing sha256 and md5...")
    checksums = _hash_file(part_path)
    elapsed = time.monotonic() - t0
    _log(log_file, f"sha256: {checksums['sha256']}")
    _log(log_file, f"md5:    {checksums['md5']}")
    _log(log_file, f"size:   {written} bytes ({written / (1024*1024):.1f} MB)")
    _log(log_file, f"elapsed: {elapsed:.1f}s")

    if expected_sha256 and checksums["sha256"] != expected_sha256.lower():
        err = f"sha256 mismatch: expected {expected_sha256}, got {checksums['sha256']}"
        _log(log_file, f"FAILED: {err}; partial kept at {part_path}")
        return {
            "ok": False, "path": str(output_path), "size_bytes": written,
            "sha256": checksums["sha256"], "md5": checksums["md5"],
            "error": err, "elapsed_s": elapsed,
        }

    part_path.rename(output_path)
    _log(log_file, f"DONE: {output_path} (sha256={checksums['sha256']}, md5={checksums['md5']})")
    return {
        "ok": True, "path": str(output_path), "size_bytes": written,
        "sha256": checksums["sha256"], "md5": checksums["md5"],
        "error": None, "elapsed_s": elapsed,
    }


def _manifest_path(output_path: Path) -> Path:
    """Return the per-file manifest path: ``MANIFEST.<basename>``
    in the same directory as ``output_path``.

    Per-file manifests fix the shared-MANIFEST bug where a
    second fetch_with_manifest call into the same directory
    reads the first file's MANIFEST and gets a spurious
    sha256 mismatch.
    """
    return output_path.parent / f"MANIFEST.{output_path.name}"


def write_manifest(
    output_path: Path,
    url: str,
    sha256: str,
    md5: str,
    size_bytes: int,
    started_at: str,
    completed_at: str,
    extra: Optional[dict[str, str]] = None,
) -> Path:
    """Write a per-file MANIFEST next to the downloaded file.

    Format: ``key: value`` per line. The manifest records the
    URL, size, checksums, and timestamps. It is the source of
    truth for ``expected_sha256`` on subsequent runs.
    """
    manifest_path = _manifest_path(output_path)
    lines = [
        f"url: {url}",
        f"size_bytes: {size_bytes}",
        f"sha256: {sha256}",
        f"md5: {md5}",
        f"started_at: {started_at}",
        f"completed_at: {completed_at}",
    ]
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}: {v}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def read_manifest(output_path: Path) -> dict[str, str]:
    """Read the per-file MANIFEST into a dict. Empty dict if
    missing or legacy (single-file MANIFEST is NOT read; only
    MANIFEST.<basename> is)."""
    manifest_path = _manifest_path(output_path)
    if not manifest_path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def fetch_with_manifest(
    url: str,
    output_path: Path,
    log_file: Optional[Path] = None,
    is_zip: bool = False,
) -> dict:
    """Download with per-file manifest tracking and resume
    across runs.

    If a per-file MANIFEST (``MANIFEST.<basename>``) exists for
    ``output_path``, its ``sha256`` is used as the expected
    checksum. If the final file already exists and its sha256
    matches the manifest, the function returns
    ``{"ok": True, "skipped": True, ...}`` without
    re-downloading. Otherwise it calls ``download_resumable``
    and on success writes a fresh per-file MANIFEST.

    The manifest is per-file (named after the output file) so
    multiple downloads into the same directory do not
    interfere with each other.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(output_path)
    expected = manifest.get("sha256") if manifest else None

    if output_path.is_file() and expected:
        actual = _hash_file(output_path).get("sha256")
        if actual == expected:
            _log(log_file, f"file already present and matches manifest sha256; skipping")
            return {
                "ok": True, "skipped": True, "path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "sha256": actual, "md5": _hash_file(output_path).get("md5"),
                "error": None, "elapsed_s": 0.0,
            }
        _log(log_file, f"file exists but sha256 does not match manifest; deleting {output_path}")
        output_path.unlink()
        expected = None

    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result = download_resumable(
        url, output_path, log_file=log_file, expected_sha256=expected, is_zip=is_zip
    )
    if result["ok"]:
        completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        write_manifest(
            output_path, url, result["sha256"], result["md5"],
            result["size_bytes"], started_at, completed_at,
        )
    return result

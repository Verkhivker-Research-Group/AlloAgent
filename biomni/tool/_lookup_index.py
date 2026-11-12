"""Sidecar SQLite index for the T9 / T10 local-file lookups.

Governed by docs/2_lookup_performance_criteria.md (committed before
implementation; never edited). The design target is a SQLite index built
once at fetch time, stored beside the data file, keyed on the axes the
wrappers actually filter on.

The index is strictly an optimisation. Every consumer here returns
``None``/refuses when the index is missing, stale or of a foreign
schema, and the caller then falls back to the streaming full scan, so
correctness never depends on the index existing.

Freshness is decided by the sha256 of the source data file: a lookup
whose index records a different sha256 is refused rather than answered
from stale rows (LP-5).
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterator, Optional

INDEX_SUFFIX = ".index.sqlite"
SCHEMA_VERSION = "1"

KIND_ALPHAMISSENSE = "alphamissense"
KIND_CLINVAR = "clinvar"

# Columns the AlphaMissense wrapper needs, by NAME (never by position).
AM_REQUIRED_COLUMNS = ("uniprot_id", "protein_variant", "am_pathogenicity",
                       "am_class")

# Columns the ClinVar wrapper reads, by NAME.
CV_REQUIRED_COLUMNS = ("AlleleID", "Name", "GeneSymbol", "ClinicalSignificance",
                       "ReviewStatus", "Type", "Chromosome", "Start", "Stop",
                       "ReferenceAllele", "AlternateAllele", "Assembly")


def index_path_for(data_path: Any) -> Path:
    """Return the sidecar index path for a data file."""
    return Path(str(data_path) + INDEX_SUFFIX)


def sha256_file(path: Any, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(str(path), "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def content_fingerprint(path: Any, block: int = 1 << 20) -> str:
    """Cheap but strong fingerprint of a file's bytes.

    Hashes the size, the first and last ``block`` bytes, and a handful of
    evenly spaced blocks from the middle. Costs ~3 MiB of hashing even
    for a 30 GB file, so it can run on every lookup, and it detects a
    same-size rewrite that a (size, mtime) pair can miss when the
    filesystem's timestamp granularity is coarse.
    """
    st = os.stat(str(path))
    h = hashlib.sha256()
    h.update(str(st.st_size).encode())
    with open(str(path), "rb") as fh:
        h.update(fh.read(block))
        if st.st_size > block:
            fh.seek(max(0, st.st_size - block))
            h.update(fh.read(block))
        middle = st.st_size - 2 * block
        if middle > 0:
            step = max(1, middle // 16)
            for i in range(16):
                pos = block + i * step
                if pos >= st.st_size - block:
                    break
                fh.seek(pos)
                h.update(fh.read(1 << 16))
    return h.hexdigest()


def _open_gzip_text(path: Path):
    return gzip.open(str(path), mode="rt", encoding="utf-8", newline="")


def iter_tsv(path: Any, required: tuple[str, ...],
             delimiter: str = "\t") -> Iterator[tuple[list[str], csv.DictReader]]:
    """Yield ``(header_names, reader)`` for a gzipped TSV, handling ``#``.

    Two different real files need opposite treatment of a leading ``#``:

    - **AlphaMissense** opens with genuine ``#`` comment lines
      ("# Copyright 2023 DeepMind ...", "#", "# Licensed under ...").
      Handing the raw stream to ``csv.DictReader`` makes the first
      comment line the header, after which every ``row[name]`` lookup is
      ``None`` and the wrapper silently returns zero rows.
    - **ClinVar** ``variant_summary.txt.gz`` opens with ``#AlleleID``,
      which is the header line itself -- the ``#`` is part of the first
      column name, not a comment marker.

    So a leading line is treated as the header when its tab-separated
    fields (after stripping one leading ``#``) contain any of
    ``required``; otherwise a leading ``#`` line is skipped as a comment.
    Columns are addressed by name afterwards, never by position (LP-7).

    The header is read eagerly, before the ``(header, reader)`` pair is
    yielded, so the caller can validate the column names before the
    first row is consumed.
    """
    fh = _open_gzip_text(Path(path))
    try:
        header: Optional[list[str]] = None
        header_line = ""
        wanted = set(required)
        for line in fh:
            if header is None:
                stripped = line[1:] if line.startswith("#") else line
                fields = next(csv.reader([stripped], delimiter=delimiter))
                if wanted & set(fields):
                    header = fields
                    header_line = line
                elif line.startswith("#"):
                    continue
                else:
                    header = fields
                    header_line = line
            if header is not None:
                break
        if not header:
            raise IndexError_(f"{path} has no header line naming any of "
                              f"{sorted(wanted)}")

        def _rest() -> Iterator[str]:
            for nxt in fh:
                if nxt.startswith("#"):
                    continue
                yield nxt

        reader = csv.DictReader(_rest(), delimiter=delimiter)
        reader.fieldnames = header
        yield header, reader
    finally:
        fh.close()


class IndexError_(RuntimeError):
    """Raised when an index cannot be built for a usable data file."""


def _create(conn: sqlite3.Connection, table: str, columns: list[tuple[str, str]],
            index_statements: list[str]) -> None:
    conn.execute(
        f"CREATE TABLE {table} ({', '.join(f'{n} {t}' for n, t in columns)})"
    )
    for stmt in index_statements:
        conn.execute(stmt)


def _write_meta(conn: sqlite3.Connection, meta: dict[str, str]) -> None:
    conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.executemany(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        sorted(meta.items()),
    )


def _source_stat_meta(src: Path) -> dict[str, str]:
    st = src.stat()
    return {
        "source_size_bytes": str(st.st_size),
        "source_mtime_ns": str(st.st_mtime_ns),
        "source_fingerprint": content_fingerprint(src),
    }


def build_alphamissense_index(data_path: Any,
                              index_path: Any = None) -> dict[str, Any]:
    """Build the ``(uniprot_id, position)`` index for an AlphaMissense TSV.

    Returns build statistics: ``index_path``, ``source_sha256``,
    ``row_count``, ``build_seconds``, ``index_bytes``, ``columns``.
    """
    src = Path(str(data_path))
    dst = Path(str(index_path)) if index_path is not None else index_path_for(src)
    t0 = time.time()
    source_sha = sha256_file(src)

    if dst.exists():
        dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(dst))
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        _create(
            conn, "am",
            [("uniprot_id", "TEXT NOT NULL"), ("position", "INTEGER NOT NULL"),
             ("protein_variant", "TEXT NOT NULL"),
             ("am_pathogenicity", "REAL"), ("am_class", "TEXT")],
            ["CREATE INDEX ix_am_key ON am (uniprot_id, position)"],
        )
        row_count = 0
        batch: list[tuple] = []
        for header, reader in iter_tsv(src, AM_REQUIRED_COLUMNS):
            missing = [c for c in AM_REQUIRED_COLUMNS if c not in header]
            if missing:
                raise IndexError_(
                    f"AlphaMissense TSV is missing column(s) {missing}; "
                    f"header was {header!r}"
                )
            for row in reader:
                pv = (row.get("protein_variant") or "").strip()
                parsed = _split_protein_variant(pv)
                if parsed is None:
                    continue
                pos = parsed[0]
                try:
                    am_path = float(row.get("am_pathogenicity"))
                except (TypeError, ValueError):
                    continue
                batch.append((
                    (row.get("uniprot_id") or "").strip(), pos, pv,
                    am_path, (row.get("am_class") or "").strip(),
                ))
                row_count += 1
                if len(batch) >= 100_000:
                    conn.executemany("INSERT INTO am VALUES (?,?,?,?,?)", batch)
                    batch.clear()
            break
        if batch:
            conn.executemany("INSERT INTO am VALUES (?,?,?,?,?)", batch)
        _write_meta(conn, {
            "kind": KIND_ALPHAMISSENSE,
            "schema_version": SCHEMA_VERSION,
            "source_path": str(src),
            "source_sha256": source_sha,
            "row_count": str(row_count),
            "columns": ",".join(AM_REQUIRED_COLUMNS),
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **_source_stat_meta(src),
        })
        conn.commit()
    finally:
        conn.close()

    build_seconds = time.time() - t0
    return {
        "index_path": str(dst),
        "source_sha256": source_sha,
        "row_count": row_count,
        "build_seconds": round(build_seconds, 2),
        "index_bytes": dst.stat().st_size,
        "columns": list(AM_REQUIRED_COLUMNS),
    }


def _split_protein_variant(pv: str) -> Optional[tuple[int, str, str]]:
    """Split ``"R175H"`` into ``(175, "R", "H")``; ``None`` if malformed.

    Mirrors ``get_alphamissense_score._parse_protein_variant`` so the
    index and the full scan agree on which rows are valid.
    """
    if len(pv) < 3 or not pv[0].isalpha() or not pv[-1].isalpha():
        return None
    ref_aa, rest, alt_aa = pv[0], pv[1:-1], pv[-1]
    if not rest.isdigit():
        return None
    pos = int(rest)
    if pos <= 0:
        return None
    return pos, ref_aa.upper(), alt_aa.upper()


def build_clinvar_index(data_path: Any,
                        index_path: Any = None) -> dict[str, Any]:
    """Build the gene / id / rsID / HGVS-name index for ClinVar."""
    src = Path(str(data_path))
    dst = Path(str(index_path)) if index_path is not None else index_path_for(src)
    t0 = time.time()
    source_sha = sha256_file(src)

    if dst.exists():
        dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(dst))
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        _create(
            conn, "cv",
            [("clinvar_id", "TEXT"), ("name", "TEXT"), ("gene_symbol", "TEXT"),
             ("clinical_significance", "TEXT"), ("review_status", "TEXT"),
             ("obj_type", "TEXT"), ("chromosome", "TEXT"),
             ("start_pos", "INTEGER"), ("stop_pos", "INTEGER"),
             ("ref_allele", "TEXT"), ("alt_allele", "TEXT"),
             ("assembly", "TEXT"), ("row_ord", "INTEGER")],
            ["CREATE INDEX ix_cv_gene ON cv (gene_symbol)",
             "CREATE INDEX ix_cv_id ON cv (clinvar_id)",
             "CREATE INDEX ix_cv_name ON cv (name)"],
        )
        row_count = 0
        batch: list[tuple] = []
        for header, reader in iter_tsv(src, CV_REQUIRED_COLUMNS):
            missing = [c for c in CV_REQUIRED_COLUMNS if c not in header]
            if missing:
                raise IndexError_(
                    f"ClinVar TSV is missing column(s) {missing}; "
                    f"header was {header!r}"
                )
            for row in reader:
                batch.append((
                    (row.get("AlleleID") or "").strip(),
                    (row.get("Name") or "").strip(),
                    (row.get("GeneSymbol") or "").strip(),
                    (row.get("ClinicalSignificance") or "").strip(),
                    (row.get("ReviewStatus") or "").strip(),
                    (row.get("Type") or "").strip(),
                    (row.get("Chromosome") or "").strip(),
                    _to_int(row.get("Start")),
                    _to_int(row.get("Stop")),
                    (row.get("ReferenceAllele") or "").strip(),
                    (row.get("AlternateAllele") or "").strip(),
                    (row.get("Assembly") or "").strip(),
                    row_count,
                ))
                row_count += 1
                if len(batch) >= 50_000:
                    conn.executemany(
                        "INSERT INTO cv VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", batch
                    )
                    batch.clear()
            break
        if batch:
            conn.executemany("INSERT INTO cv VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
        _write_meta(conn, {
            "kind": KIND_CLINVAR,
            "schema_version": SCHEMA_VERSION,
            "source_path": str(src),
            "source_sha256": source_sha,
            "row_count": str(row_count),
            "columns": ",".join(CV_REQUIRED_COLUMNS),
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **_source_stat_meta(src),
        })
        conn.commit()
    finally:
        conn.close()

    return {
        "index_path": str(dst),
        "source_sha256": source_sha,
        "row_count": row_count,
        "build_seconds": round(time.time() - t0, 2),
        "index_bytes": dst.stat().st_size,
        "columns": list(CV_REQUIRED_COLUMNS),
    }


def _to_int(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def read_meta(index_path: Any) -> dict[str, str]:
    p = Path(str(index_path))
    if not p.is_file():
        return {}
    conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        rows = conn.execute("SELECT key, value FROM meta").fetchall()
    except sqlite3.Error:
        return {}
    finally:
        conn.close()
    return {k: v for k, v in rows}


def read_sidecar_manifest(data_path: Any) -> dict[str, str]:
    """Read ``MANIFEST.<basename>`` (then a legacy ``MANIFEST``).

    Lets the full-scan path report the same ``source_version`` the index
    path does without re-hashing a multi-hundred-megabyte file on every
    call.
    """
    p = Path(str(data_path))
    out: dict[str, str] = {}
    for candidate in (p.parent / f"MANIFEST.{p.name}", p.parent / "MANIFEST"):
        if not candidate.is_file():
            continue
        try:
            with candidate.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    k, _, v = line.partition(":")
                    out[k.strip()] = v.strip()
        except (OSError, UnicodeDecodeError):
            continue
        if out:
            return out
    return out


def open_fresh_index(data_path: Any, kind: str) -> Optional[sqlite3.Connection]:
    """Return a read-only connection to a FRESH index, or ``None``.

    ``None`` means: no index, wrong kind, unknown schema version, or the
    source file no longer matches the one the index was built from. The
    caller must fall back to the streaming full scan in every one of
    those cases (LP-5, LP-8).

    Freshness is decided in two tiers so a lookup stays fast:

    1. If the data file's size and mtime still match what the index
       recorded, it is the same file and the index is used directly.
    2. Otherwise the sha256 is recomputed and compared. A file that was
       touched but not changed still passes; a genuinely different file
       fails and the index is refused.
    """
    src = Path(str(data_path))
    idx = index_path_for(src)
    if not idx.is_file():
        return None
    meta = read_meta(idx)
    if meta.get("kind") != kind:
        return None
    if meta.get("schema_version") != SCHEMA_VERSION:
        return None
    recorded = meta.get("source_sha256")
    if not recorded:
        return None
    try:
        if meta.get("source_fingerprint") == content_fingerprint(src):
            return sqlite3.connect(f"file:{idx}?mode=ro", uri=True)
    except OSError:
        return None
    try:
        if sha256_file(src) != recorded:
            return None
    except OSError:
        return None
    return sqlite3.connect(f"file:{idx}?mode=ro", uri=True)


def build_all(data_path: Any, kind: str) -> dict[str, Any]:
    """Dispatch to the right builder for ``kind``."""
    if kind == KIND_ALPHAMISSENSE:
        return build_alphamissense_index(data_path)
    if kind == KIND_CLINVAR:
        return build_clinvar_index(data_path)
    raise IndexError_(f"unknown index kind {kind!r}")
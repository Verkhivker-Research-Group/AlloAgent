"""T10 get_alphamissense_score (Part 2 / batch 2).

What is the AlphaMissense pathogenicity score and class for
missense variants in a given UniProt accession (optionally at a
specific protein position)?

Streams the AlphaMissense TSV (Cheng et al. 2023) with stdlib
``gzip`` + ``csv`` (no new deps). The TSV must be downloaded via
``scripts/fetch_alphamissense.py --download --out <dir>``. The
wrapper degrades gracefully (returns ``success=False``) when the
file is missing.
"""
from __future__ import annotations

import csv
import gzip
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from biomni.tool import _lookup_index
from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_DEFAULT_DATA_PATH = Path("/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz")

# protein_variant looks like "M1A" -- <ref_aa><position><alt_aa>.
# ref_aa and alt_aa are 1-letter amino-acid codes; position is a
# positive int. Anchor the pattern so we don't match empty fields.
_PROTEIN_VARIANT_RE = re.compile(r"^([A-Z])(\d+)([A-Z])$")

_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return (
        "AlphaMissense (Cheng et al. 2023, "
        "https://storage.googleapis.com/dm_alphamissense/"
        "AlphaMissense_aa_substitutions.tsv.gz, CC BY-NC-SA 4.0)"
    )


def _parse_protein_variant(pv: str) -> Optional[tuple[int, str, str]]:
    """Return (position, ref_aa, alt_aa) or None if the field is malformed."""
    m = _PROTEIN_VARIANT_RE.match(pv)
    if m is None:
        return None
    ref, pos_s, alt = m.group(1), m.group(2), m.group(3)
    if ref not in _AMINO_ACIDS or alt not in _AMINO_ACIDS:
        return None
    try:
        pos = int(pos_s)
    except ValueError:
        return None
    if pos <= 0:
        return None
    return pos, ref, alt


def _coerce_path(data_path: Optional[Any]) -> Path:
    if data_path is None:
        return _DEFAULT_DATA_PATH
    return Path(data_path)


def _index_query(conn: sqlite3.Connection, uniprot_id: str,
                 position: Optional[int]) -> list[dict[str, Any]]:
    """Indexed equivalent of the streaming scan.

    Emits the same dict shape and the same ``(position, alt_aa)`` sort as
    the scan, so the two paths are comparable record-for-record.
    """
    if position is None:
        sql = ("SELECT uniprot_id, position, protein_variant, "
               "am_pathogenicity, am_class FROM am WHERE uniprot_id = ?")
        params: tuple[Any, ...] = (uniprot_id,)
    else:
        sql = ("SELECT uniprot_id, position, protein_variant, "
               "am_pathogenicity, am_class FROM am "
               "WHERE uniprot_id = ? AND position = ?")
        params = (uniprot_id, position)
    out: list[dict[str, Any]] = []
    for uniprot, pos, pv, am_path, am_class in conn.execute(sql, params):
        parsed = _parse_protein_variant(pv)
        if parsed is None:
            continue
        _, ref_aa, alt_aa = parsed
        out.append({
            "uniprot_id": uniprot,
            "protein_variant": pv,
            "am_pathogenicity": float(am_path),
            "am_class": am_class or "",
            "position": pos,
            "ref_aa": ref_aa,
            "alt_aa": alt_aa,
        })
    out.sort(key=lambda r: (r["position"], r["alt_aa"]))
    return out


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_alphamissense_score(
    uniprot_id: str,
    position: Optional[int] = None,
    data_path: Optional[Any] = None,
):
    """Return AlphaMissense pathogenicity scores for a UniProt accession.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession (e.g. ``"P69905"``, ``"P69441"``).
        Case-sensitive.
    position : int or None, default None
        1-indexed protein position. ``None`` (default) returns
        all missense variants for the protein.
    data_path : str, Path, or None
        Path to the local AlphaMissense TSV
        (``AlphaMissense_aa_substitutions.tsv.gz``). Default
        ``/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz``.
        Must be downloaded via
        ``scripts/fetch_alphamissense.py --download --out <dir>``.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "uniprot_id": <str>,
                "position": <int or None>,
                "variants": [
                    {
                        "uniprot_id": <str>,
                        "protein_variant": <str>,  # e.g. "M1A"
                        "am_pathogenicity": <float>,
                        "am_class": "pathogenic" | "ambiguous" | "benign",
                        "position": <int>,
                        "ref_aa": <str>,
                        "alt_aa": <str>,
                    },
                    ...
                ],
                "total_count": <int>,  # rows returned
                "data_path": <str>,
                "lookup_path": "index" | "full-scan",
                "index_path": <str>,   # only when lookup_path == "index"
                "source_version": "sha256:<hex>" | "unknown",
            }

        The sidecar index (``<data_path>.index.sqlite``, built by
        ``scripts/fetch_alphamissense.py``) turns the lookup into an
        indexed SQLite query. It is only used when its recorded
        sha256 still matches the data file; otherwise the wrapper falls
        back to the streaming scan, so correctness never depends on the
        index existing.

        On missing file or invalid input, returns
        ``{success: False, error: <descriptive string>, ...}``.
    """
    if not isinstance(uniprot_id, str) or not uniprot_id:
        return {
            "success": False,
            "error": f"uniprot_id must be a non-empty string, got {uniprot_id!r}",
        }
    if position is not None and (
        not isinstance(position, int) or isinstance(position, bool) or position <= 0
    ):
        return {
            "success": False,
            "error": f"position must be a positive int (1-indexed), got {position!r}",
        }

    path = _coerce_path(data_path)
    if not path.is_file():
        return {
            "success": False,
            "error": (
                f"AlphaMissense TSV not found at {str(path)!s}; run "
                f"scripts/fetch_alphamissense.py --download --out <dir>"
            ),
        }

    index_path = _lookup_index.index_path_for(path)
    conn = _lookup_index.open_fresh_index(path, _lookup_index.KIND_ALPHAMISSENSE)
    if conn is not None:
        try:
            out = _index_query(conn, uniprot_id, position)
        except sqlite3.Error:
            conn.close()
            conn = None
        else:
            conn.close()
            meta = _lookup_index.read_meta(index_path)
            return {
                "success": True,
                "data": {
                    "uniprot_id": uniprot_id,
                    "position": position,
                    "variants": out,
                    "total_count": len(out),
                    "data_path": str(path),
                    "lookup_path": "index",
                    "index_path": str(index_path),
                    "source_version": f"sha256:{meta.get('source_sha256', '')}",
                },
            }

    out: list[dict[str, Any]] = []
    try:
        with gzip.open(str(path), mode="rt", encoding="utf-8", newline="") as fh:
            # The real AlphaMissense TSV starts with one or more
            # comment lines ("# Copyright 2023 DeepMind ..."). If
            # we hand the raw stream to csv.DictReader, the first
            # line becomes the header and row["uniprot_id"] is
            # None for every data row, so the wrapper silently
            # returns 0 results. Skip leading '#' lines so the
            # first non-comment line becomes the header.
            def _non_comment_lines():
                for line in fh:
                    if line.startswith("#"):
                        continue
                    yield line
            reader = csv.DictReader(_non_comment_lines(), delimiter="\t")
            for row in reader:
                if row.get("uniprot_id") != uniprot_id:
                    continue
                pv = row.get("protein_variant", "")
                parsed = _parse_protein_variant(pv)
                if parsed is None:
                    continue
                pos, ref_aa, alt_aa = parsed
                if position is not None and pos != position:
                    continue
                try:
                    am_path = float(row["am_pathogenicity"])
                except (KeyError, TypeError, ValueError):
                    continue
                out.append({
                    "uniprot_id": uniprot_id,
                    "protein_variant": pv,
                    "am_pathogenicity": am_path,
                    "am_class": row.get("am_class", ""),
                    "position": pos,
                    "ref_aa": ref_aa,
                    "alt_aa": alt_aa,
                })
    except (OSError, gzip.BadGzipFile, csv.Error) as exc:
        return {
            "success": False,
            "error": f"AlphaMissense TSV at {str(path)!s} is malformed: {exc}",
        }

    out.sort(key=lambda r: (r["position"], r["alt_aa"]))

    manifest = _lookup_index.read_sidecar_manifest(path)
    recorded_sha = manifest.get("sha256")
    return {
        "success": True,
        "data": {
            "uniprot_id": uniprot_id,
            "position": position,
            "variants": out,
            "total_count": len(out),
            "data_path": str(path),
            "lookup_path": "full-scan",
            "source_version": (
                f"sha256:{recorded_sha}" if recorded_sha else "unknown"
            ),
        },
    }

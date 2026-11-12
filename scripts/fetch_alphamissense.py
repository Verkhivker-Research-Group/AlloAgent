"""scripts/fetch_alphamissense.py -- fetch the AlphaMissense TSV for local querying.

HEAD-request size check (2026-10-10):

================================  =====================  =====================
File                             URL                     Size
================================  =====================  =====================
AlphaMissense TSV                dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz   1151.4 MB (1207278510 B)
AlphaMissense gene-level TSV     dm_alphamissense/AlphaMissense_gene_level.tsv.gz         404
AlphaMissense README             dm_alphamissense/README.md                              404
================================  =====================  =====================

The TSV is under the 2 GB threshold (brief said to ask the user
before downloading anything > 2 GB), so this script downloads it
without prompting. Schema (4 columns, tab-separated, ~20M rows,
CC BY-NC-SA 4.0 license):

    uniprot_id   protein_variant   am_pathogenicity   am_class
    A0A024R1R8   M1A               0.4673             ambiguous
    A0A024R1R8   M1C               0.3828             ambiguous
    A0A024R1R8   M1D               0.8267             pathogenic
    ...

The T10 ``get_alphamissense_score`` wrapper queries this file
locally. The wrapper degrades gracefully (returns a clear error)
when the file is missing.

Download semantics (scripts/_resumable.py)
-----------------------------------------
- Writes to ``AlphaMissense_aa_substitutions.tsv.gz.part`` while
  downloading; renames to the final name only after sha256
  verifies (manifest sha256 on second run).
- Resumes with HTTP Range if the ``.part`` file exists.
- Retries with exponential backoff (up to 6 attempts).
- Logs progress to ``download.log`` (append-only).
- Never deletes the partial file; interrupted downloads resume
  on the next run.

No published checksum is available from Google Cloud Storage.
The first download records the computed sha256 in
``MANIFEST``; subsequent runs verify against it.

Usage
-----
Print the file size (HEAD request, no download)::

    python scripts/fetch_alphamissense.py --check-size

Download (resumable) to a target directory (default
``./data/alphamissense/``)::

    python scripts/fetch_alphamissense.py --download --out ./data/alphamissense

Import as a module and call ``fetch(out_dir)`` to download
without printing the progress bar.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).parent))
from _resumable import fetch_with_manifest, head_size, fetch_expected_checksum, _log  # noqa: E402

_TSV_URL = (
    "https://storage.googleapis.com/dm_alphamissense/"
    "AlphaMissense_aa_substitutions.tsv.gz"
)
_OUT_NAME = "AlphaMissense_aa_substitutions.tsv.gz"


def check_size() -> Optional[int]:
    return head_size(_TSV_URL)


def fetch(out_dir: Path, build_index: bool = True) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / _OUT_NAME
    log_file = out_dir / "download.log"
    result = fetch_with_manifest(
        _TSV_URL, out_path, log_file=log_file, is_zip=True
    )
    if not result["ok"]:
        raise RuntimeError(
            f"download failed: {result['error']}; partial kept at "
            f"{out_path.with_suffix(out_path.suffix + '.part')}; re-run to resume"
        )
    if build_index:
        build_lookup_index(out_path)
    return out_path


def build_lookup_index(tsv_path: Path) -> dict:
    """Build the sidecar SQLite lookup index (docs/2_lookup_performance_criteria.md).

    Best-effort by design: the index is an optimisation, so a build
    failure must not invalidate a good download. The failure is logged
    next to the data file and the wrapper falls back to the full scan.
    """
    tsv_path = Path(tsv_path)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from biomni.tool._lookup_index import build_alphamissense_index

    try:
        stats = build_alphamissense_index(tsv_path)
    except Exception as exc:  # noqa: BLE001 - index failure is non-fatal
        _log(tsv_path.parent / "download.log",
             f"WARNING: lookup index build failed ({exc!r}); "
             f"get_alphamissense_score will use the slow full-scan path")
        return {"ok": False, "error": repr(exc)}
    _log(tsv_path.parent / "download.log",
         f"lookup index: {stats['row_count']} rows, "
         f"{stats['index_bytes']} bytes, built in {stats['build_seconds']}s -> "
         f"{stats['index_path']}")
    return {"ok": True, **stats}


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check-size", action="store_true",
        help="HEAD-request and print the file size",
    )
    parser.add_argument(
        "--check-checksum", action="store_true",
        help="Fetch the published sha256/md5 (returns None; GCS has none)",
    )
    parser.add_argument(
        "--download", action="store_true",
        help="Download the TSV (resumable)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./data/alphamissense"),
        help="Target directory for --download (default: ./data/alphamissense)",
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Skip building the sidecar SQLite lookup index after download",
    )
    args = parser.parse_args(argv)

    if not (args.check_size or args.download or args.check_checksum):
        parser.print_help()
        return 1

    if args.check_size:
        size = check_size()
        if size is None:
            print("  <unavailable>")
        else:
            print(f"  {size / (1024 * 1024):.1f} MB ({size} bytes)")
        return 0

    if args.check_checksum:
        for algo in ("sha256", "md5"):
            v = fetch_expected_checksum(_TSV_URL, algorithm=algo)
            print(f"  {algo}: {v if v else '<not published>'}")
        return 0

    if args.download:
        out_path = fetch(args.out, build_index=not args.no_index)
        print(f"Done: {out_path}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(_main())

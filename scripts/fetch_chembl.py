"""scripts/fetch_chembl.py -- fetch the ChEMBL 37 SQLite tarball for local querying.

HEAD-request size check (2026-10-10):

================================  =====================  =====================
File                             URL                     Size
================================  =====================  =====================
ChEMBL 37 SQLite tarball         chembl_37_sqlite.tar.gz   5497.2 MB (5764252857 B)
ChEMBL 37 published MD5          chembl_37_sqlite.tar.gz.md5   404 (not published)
ChEMBL 37 published SHA256       chembl_37_sqlite.tar.gz.sha256  404 (not published)
================================  =====================  =====================

The tarball is 5.5 GB compressed and unpacks to ~15-20 GB. The
brief said to report free disk space and stop if there is not
enough. The script checks disk space and refuses to start if
the free space is less than 25 GB (20 GB for the unpacked
database + 5 GB for the tarball + headroom).

No published checksum is available from the EBI FTP server.
The first download records the computed sha256 in
``MANIFEST``; subsequent runs verify against it.

Download semantics (scripts/_resumable.py)
-----------------------------------------
- Writes to ``chembl_37_sqlite.tar.gz.part`` while downloading;
  renames to the final name only after sha256 verifies
  (manifest sha256 on second run).
- Resumes with HTTP Range if the ``.part`` file exists.
- Retries with exponential backoff (up to 6 attempts).
- Logs progress to ``download.log`` (append-only).
- Never deletes the partial file; interrupted downloads resume
  on the next run.

Usage
-----
Print the file size (HEAD request, no download) and free
disk space::

    python scripts/fetch_chembl.py --check-size

Download (resumable) to a target directory (default
``./data/chembl/``)::

    python scripts/fetch_chembl.py --download --out ./data/chembl

Import as a module and call ``fetch(out_dir)``.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from _resumable import fetch_with_manifest, head_size  # noqa: E402

_TARBALL_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/"
    "chembl_37/chembl_37_sqlite.tar.gz"
)
_OUT_NAME = "chembl_37_sqlite.tar.gz"
_MIN_FREE_BYTES = 25 * (1 << 30)  # 25 GB; tarball + unpacked + headroom


def check_size() -> Optional[int]:
    return head_size(_TARBALL_URL)


def free_disk_bytes(path: Path) -> int:
    """Return free disk bytes on the filesystem that contains ``path``."""
    usage = shutil.disk_usage(str(path))
    return usage.free


def fetch(out_dir: Path) -> Path:
    """Download the ChEMBL 37 SQLite tarball to ``out_dir`` (resumable).

    Checks free disk space first and refuses to start if there
    is less than ``_MIN_FREE_BYTES`` (25 GB). Raises on failure
    (the ``.part`` file is left on disk for the next run).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / _OUT_NAME

    free = free_disk_bytes(out_dir)
    if free < _MIN_FREE_BYTES:
        raise RuntimeError(
            f"insufficient disk space: {free / (1024**3):.1f} GB free at "
            f"{out_dir}; need at least {_MIN_FREE_BYTES / (1024**3):.0f} GB "
            f"(5.5 GB tarball + ~15-20 GB unpacked + headroom)"
        )

    log_file = out_dir / "download.log"
    result = fetch_with_manifest(_TARBALL_URL, out_path, log_file=log_file)
    if not result["ok"]:
        raise RuntimeError(
            f"download failed: {result['error']}; partial kept at "
            f"{out_path.with_suffix(out_path.suffix + '.part')}; re-run to resume"
        )
    return out_path


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check-size", action="store_true",
        help="HEAD-request the file size and report free disk space",
    )
    parser.add_argument(
        "--download", action="store_true",
        help="Download the tarball (resumable)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./data/chembl"),
        help="Target directory for --download (default: ./data/chembl)",
    )
    args = parser.parse_args(argv)

    if not (args.check_size or args.download):
        parser.print_help()
        return 1

    if args.check_size:
        size = check_size()
        free = free_disk_bytes(Path(args.out))
        if size is None:
            print("  size: <unavailable>")
        else:
            print(f"  size: {size / (1024**3):.2f} GB ({size} bytes)")
        print(
            f"  free at {args.out}: {free / (1024**3):.1f} GB "
            f"({'SUFFICIENT' if free >= _MIN_FREE_BYTES else 'INSUFFICIENT'})"
        )
        return 0

    if args.download:
        out_path = fetch(args.out)
        print(f"Done: {out_path}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(_main())

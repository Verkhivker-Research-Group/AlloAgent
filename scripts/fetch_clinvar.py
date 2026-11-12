"""scripts/fetch_clinvar.py -- fetch ClinVar data files for local querying.

Two data files are supported:

1. **variant_summary.txt.gz** (434 MB compressed, ~5.8M rows,
   tab-delimited). This is the T9 local-mode primary file. It
   parses with stdlib ``gzip`` + ``csv`` (no VCF parser needed).
   Default for ``--download``.

2. **clinvar.vcf.gz** (190.9 MB GRCh38, 190.8 MB GRCh37).
   This requires a VCF parser (no ``cyvcf2``, ``pysam``, ``vcf``,
   ``pyvcf`` in the image; no ``tabix``, ``bcftools``, ``bgzip``).
   Only used if a VCF parser is added later. Selected with
   ``--type vcf``.

No published checksums are available from NCBI FTP for these
files. The first download records the computed sha256 in
``MANIFEST``; subsequent runs verify against it.

Download semantics (scripts/_resumable.py)
-----------------------------------------
- Writes to ``<name>.gz.part`` (or ``<name>.gz.tbi.part``) while
  downloading; renames to the final name only after sha256
  verifies (manifest sha256 on second run).
- Resumes with HTTP Range if the ``.part`` file exists.
- Retries with exponential backoff (up to 6 attempts).
- Logs progress to ``download.log`` (append-only).
- Never deletes the partial file; interrupted downloads resume
  on the next run.

Usage
-----
Print the file sizes (HEAD requests, no download)::

    python scripts/fetch_clinvar.py --check-size

Download variant_summary.txt.gz (default, for T9)::

    python scripts/fetch_clinvar.py --download --out ./data/clinvar

Download GRCh38 VCF (for future VCF-parser use)::

    python scripts/fetch_clinvar.py --download --type vcf --out ./data/clinvar

Import as a module and call ``fetch_variant_summary(out_dir)``
or ``fetch_vcf(out_dir, assembly="GRCh38")``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).parent))
from _resumable import fetch_with_manifest, head_size, _log  # noqa: E402

_VARIANT_SUMMARY_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
)
_VCF_GRCH38_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"
)
_VCF_GRCH37_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/clinvar.vcf.gz"
)
_VCF_GRCH38_INDEX_URL = _VCF_GRCH38_URL + ".tbi"


def check_size() -> dict[str, Optional[int]]:
    """HEAD-request the known ClinVar URLs and return sizes in bytes.

    A value of ``None`` means the HEAD request failed (404 or
    network error).
    """
    out: dict[str, Optional[int]] = {}
    for name, url in [
        ("variant_summary", _VARIANT_SUMMARY_URL),
        ("grch38_vcf", _VCF_GRCH38_URL),
        ("grch37_vcf", _VCF_GRCH37_URL),
        ("grch38_vcf_index", _VCF_GRCH38_INDEX_URL),
    ]:
        out[name] = head_size(url)
    return out


def build_lookup_index(tsv_path: Path) -> dict:
    """Build the sidecar SQLite lookup index (docs/2_lookup_performance_criteria.md).

    Best-effort: the index is an optimisation, so a build failure must
    not invalidate a good download. The failure is logged next to the
    data file and the wrapper falls back to the full scan.
    """
    tsv_path = Path(tsv_path)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from biomni.tool._lookup_index import build_clinvar_index

    try:
        stats = build_clinvar_index(tsv_path)
    except Exception as exc:  # noqa: BLE001 - index failure is non-fatal
        _log(tsv_path.parent / "download.log",
             f"WARNING: lookup index build failed ({exc!r}); "
             f"get_clinvar_variants will use the slow full-scan path")
        return {"ok": False, "error": repr(exc)}
    _log(tsv_path.parent / "download.log",
         f"lookup index: {stats['row_count']} rows, "
         f"{stats['index_bytes']} bytes, built in {stats['build_seconds']}s -> "
         f"{stats['index_path']}")
    return {"ok": True, **stats}


def fetch_variant_summary(out_dir: Path, build_index: bool = True) -> Path:
    """Download ``variant_summary.txt.gz`` to ``out_dir`` (resumable).

    Returns the path to the downloaded file. Raises on failure
    (the ``.part`` file is left on disk for the next run).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "variant_summary.txt.gz"
    log_file = out_dir / "download.log"
    result = fetch_with_manifest(
        _VARIANT_SUMMARY_URL, out_path, log_file=log_file, is_zip=True
    )
    if not result["ok"]:
        raise RuntimeError(
            f"download failed: {result['error']}; partial kept at "
            f"{out_path.with_suffix(out_path.suffix + '.part')}; re-run to resume"
        )
    if build_index:
        build_lookup_index(out_path)
    return out_path


def fetch_vcf(out_dir: Path, assembly: str = "GRCh38") -> Path:
    """Download ``clinvar.vcf.gz`` (+ index for GRCh38) to ``out_dir``.

    Returns the path to the downloaded VCF. Raises on failure
    (the ``.part`` file is left on disk for the next run).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if assembly == "GRCh38":
        vcf_url = _VCF_GRCH38_URL
        idx_url = _VCF_GRCH38_INDEX_URL
    elif assembly == "GRCh37":
        vcf_url = _VCF_GRCH37_URL
        idx_url = None
    else:
        raise ValueError(f"assembly must be GRCh38 or GRCh37, got {assembly!r}")

    out_path = out_dir / "clinvar.vcf.gz"
    log_file = out_dir / "download.log"
    result = fetch_with_manifest(vcf_url, out_path, log_file=log_file, is_zip=True)
    if not result["ok"]:
        raise RuntimeError(
            f"download failed: {result['error']}; partial kept at "
            f"{out_path.with_suffix(out_path.suffix + '.part')}; re-run to resume"
        )
    if idx_url is not None:
        idx_path = out_dir / "clinvar.vcf.gz.tbi"
        idx_result = fetch_with_manifest(idx_url, idx_path, log_file=log_file)
        if not idx_result["ok"]:
            raise RuntimeError(
                f"index download failed: {idx_result['error']}; partial kept at "
                f"{idx_path.with_suffix(idx_path.suffix + '.part')}; re-run to resume"
            )
    return out_path


def fetch(out_dir: Path, assembly: str = "GRCh38") -> Path:
    """Back-compat alias: download the GRCh38 VCF."""
    return fetch_vcf(out_dir, assembly=assembly)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check-size", action="store_true",
        help="HEAD-request and print file sizes",
    )
    parser.add_argument(
        "--download", action="store_true",
        help="Download the selected file (resumable)",
    )
    parser.add_argument(
        "--type",
        choices=("variant_summary", "vcf"),
        default="variant_summary",
        help="File to download (default: variant_summary for T9)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./data/clinvar"),
        help="Target directory (default: ./data/clinvar)",
    )
    parser.add_argument(
        "--assembly",
        choices=("GRCh38", "GRCh37"),
        default="GRCh38",
        help="VCF assembly (only with --type vcf; default: GRCh38)",
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Skip building the sidecar SQLite lookup index after download",
    )
    args = parser.parse_args(argv)

    if not (args.check_size or args.download):
        parser.print_help()
        return 1

    if args.check_size:
        sizes = check_size()
        for name, size in sizes.items():
            if size is None:
                print(f"  {name}: <unavailable>")
            else:
                print(f"  {name}: {size / (1024 * 1024):.1f} MB ({size} bytes)")
        return 0

    if args.download:
        if args.type == "variant_summary":
            out_path = fetch_variant_summary(args.out, build_index=not args.no_index)
        else:
            out_path = fetch_vcf(args.out, assembly=args.assembly)
        print(f"Done: {out_path}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(_main())

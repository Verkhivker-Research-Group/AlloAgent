"""scripts/fetch_cryptobench.py -- fetch the CryptoBench dataset for B3 Step 2 validation.

HEAD-request size check (2026-10-15):

================================  ===========================================  ==================
File                              URL                                           Size
================================  ===========================================  ==================
cif-files.zip                     https://osf.io/download/c5vp8/                1092.15 MB
noncryptic-pockets.json           https://osf.io/download/37ztm/                 18.01 MB
test.json (CryptoBench test split) https://osf.io/download/q2n43/                 1.63 MB
================================  ===========================================  ==================
Total (3 files, what B3-19..B3-22 need)                                            1111.79 MB

The full CryptoBench node is at https://osf.io/pz4a9/ (node
ID `pz4a9`; 1.198 GB total across 27 files including train
folds, the benchmark model, and PyMOL scripts). We do NOT
download the train folds or the benchmark model: B3-19
evaluates PocketMiner on the test split only, and we use the
PocketMiner weights already in the image (commit
187062df3c94), not the CryptoBench benchmark model.

The brief said "check size first; ask me if it is over 2 GB".
The total is 1.116 GB, which is under 2 GB; no user prompt
needed. cif-files.zip is the bulk; when extracted the ~1,107
CIF files are expected to occupy roughly 2-3 GB on disk
(typical CIF is 50-200 KB; many chains, ligands, and
NMR ensembles push the upper end). The script checks free
disk space and refuses to start if there is less than 5 GB
free (extracted CIFs + zip + headroom).

License status: **unconfirmed**. The OSF record
(https://osf.io/pz4a9/, DOI 10.17605/OSF.IO/PZ4A9) does not
expose a license field at the API level, and the CryptoBench
paper (Skrhak et al. 2024, Bioinformatics btae745) does not
state a redistribution license in the abstract. Per the
brief, the data is kept LOCAL (`data/cryptobench/`, which is
gitignored via the top-level `data` rule) and is NOT
redistributed. The license field in the MANIFEST is set to
"unconfirmed".

Training-set overlap (B3-23): the CryptoBench paper
(Results, Baseline evaluation) states that "in the
PocketMiner training set of 37 apo structures, three apo
structures have >95% sequence similarity with apo structures
in the CryptoBench test set." So there IS measurable
sequence-similarity overlap between PocketMiner's training
set and the CryptoBench test set. The exact overlap set is
NOT publicly listed (PocketMiner's training-set PDB IDs are
not enumerated in the Meller et al. 2023 paper or repo
README). The validation script will record this qualitative
finding in its output.

Download semantics (scripts/_resumable.py)
------------------------------------------
- Writes to ``<name>.part`` while downloading; renames to the
  final name only after sha256 verifies (manifest sha256 on
  second run).
- Resumes with HTTP Range if the ``.part`` file exists.
- Retries with exponential backoff (up to 6 attempts).
- Logs progress to ``download.log`` (append-only).
- Never deletes the partial file; interrupted downloads resume
  on the next run.
- The MANIFEST records the computed sha256 of each file on
  first download; subsequent runs verify against it.

Usage
-----
Print the file sizes (HEAD requests, no download) and free
disk space::

    python scripts/fetch_cryptobench.py --check-size

Download (resumable) to a target directory (default
``./data/cryptobench/``)::

    python scripts/fetch_cryptobench.py --download --out ./data/cryptobench

Import as a module and call ``fetch(out_dir)``.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import time
import zipfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from _resumable import download_resumable, head_size  # noqa: E402

# (URL, output filename, expected size in bytes, license)
# License is "unconfirmed" for all three per the brief.
_FILES = [
    (
        "https://osf.io/download/c5vp8/",
        "cif-files.zip",
        1_145_203_712,
        "unconfirmed",
    ),
    (
        "https://osf.io/download/37ztm/",
        "noncryptic-pockets.json",
        18_879_987,
        "unconfirmed",
    ),
    (
        "https://osf.io/download/q2n43/",
        "test.json",
        1_705_224,
        "unconfirmed",
    ),
]
_MIN_FREE_BYTES = 5 * (1 << 30)  # 5 GB; cif-files + extracted CIFs + headroom


def check_size() -> dict[str, Optional[int]]:
    """Return a mapping filename -> Content-Length (or None)."""
    return {name: head_size(url) for url, name, _sz, _lic in _FILES}


def free_disk_bytes(path: Path) -> int:
    # shutil.disk_usage requires the path to exist; use the
    # nearest existing parent for an out-dir that has not been
    # created yet.
    probe = path
    while not probe.exists():
        probe = probe.parent
        if probe == probe.parent:
            break
    usage = shutil.disk_usage(str(probe))
    return usage.free


def _sha_and_md5(path: Path) -> tuple[str, str]:
    h_sha = hashlib.sha256()
    h_md5 = hashlib.md5()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h_sha.update(chunk)
            h_md5.update(chunk)
    return h_sha.hexdigest(), h_md5.hexdigest()


def _write_per_file_manifest(
    out_dir: Path, name: str, url: str, sha: str, md5: str,
    size: int, started: str, completed: str, license_status: str,
) -> Path:
    mf = out_dir / f"MANIFEST.{name}"
    lines = [
        f"url: {url}",
        f"sha256: {sha}",
        f"md5: {md5}",
        f"size_bytes: {size}",
        f"started_at: {started}",
        f"completed_at: {completed}",
        f"dataset: CryptoBench (OSF pz4a9)",
        f"license: {license_status}",
    ]
    mf.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return mf


def _fetch_one(
    out_dir: Path, url: str, name: str, expected_size: int,
    license_status: str, log_path: Path,
) -> Path:
    """Download a single CryptoBench file with per-file
    manifest. Bypasses fetch_with_manifest (which uses a
    single shared MANIFEST per dir and breaks multi-file
    downloads into the same directory, and applies gzip -t
    under is_zip=True which is wrong for ZIP archives).
    """
    out_path = out_dir / name
    manifest_path = out_dir / f"MANIFEST.{name}"
    if out_path.is_file() and out_path.stat().st_size == expected_size \
            and manifest_path.is_file():
        print(f"  already present and matches expected size + has "
              f"per-file MANIFEST; skipping {name}")
        return out_path
    print(f"  fetching {name} from {url} "
          f"(expected {expected_size / 1024 / 1024:.2f} MB, "
          f"license={license_status})")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result = download_resumable(
        url, out_path, log_file=log_path,
        expected_sha256=None, is_zip=False,
    )
    if not result.get("ok"):
        raise RuntimeError(
            f"download failed for {name}: {result.get('error')}"
        )
    if out_path.stat().st_size != expected_size:
        raise RuntimeError(
            f"size mismatch for {name}: got "
            f"{out_path.stat().st_size}, expected {expected_size}"
        )
    if name.endswith(".zip"):
        with zipfile.ZipFile(out_path) as z:
            bad = z.testzip()
        if bad is not None:
            raise RuntimeError(
                f"ZIP integrity check failed for {name}: "
                f"corrupt entry {bad}"
            )
        print(f"  ZIP integrity OK")
    sha, md5 = _sha_and_md5(out_path)
    completed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _write_per_file_manifest(
        out_dir, name, url, sha, md5, out_path.stat().st_size,
        started, completed, license_status,
    )
    print(f"  -> {out_path}  "
          f"({out_path.stat().st_size / 1024 / 1024:.2f} MB, "
          f"sha256={sha[:16]}...)")
    return out_path


def fetch(out_dir: Path) -> list[Path]:
    """Download the 3 CryptoBench files to ``out_dir`` (resumable).

    Checks free disk space first and refuses to start if there
    is less than 5 GB free on the target filesystem. Returns
    the list of downloaded file Paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    free = free_disk_bytes(out_dir)
    if free < _MIN_FREE_BYTES:
        raise RuntimeError(
            f"only {free / (1 << 30):.2f} GB free at {out_dir}; "
            f"need >= {_MIN_FREE_BYTES / (1 << 30):.0f} GB "
            f"(cif-files.zip 1.09 GB + extracted CIFs ~2-3 GB + headroom)"
        )
    note = out_dir / "LICENSE_NOTE.txt"
    if not note.is_file():
        note.write_text(
            "CryptoBench (OSF pz4a9, DOI 10.17605/OSF.IO/PZ4A9)\n"
            "Source paper: Skrhak et al. 2024, Bioinformatics btae745\n"
            "License: UNCONFIRMED (per the brief; the OSF record does\n"
            "not expose a license field, and the paper does not state\n"
            "a redistribution license in the abstract). The data is\n"
            "kept LOCAL (this directory is gitignored) and is NOT\n"
            "redistributed.\n"
            "Training-set overlap (B3-23): the CryptoBench paper notes\n"
            "that 3 apo structures in the PocketMiner training set have\n"
            ">95% sequence similarity with CryptoBench test structures.\n"
            "The exact overlap set is not publicly listed.\n",
            encoding="utf-8",
        )
    log_path = out_dir / "download.log"
    paths: list[Path] = []
    for url, name, expected_size, license_status in _FILES:
        paths.append(_fetch_one(
            out_dir, url, name, expected_size, license_status, log_path,
        ))
    return paths


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check-size", action="store_true",
                   help="HEAD-request the 3 files and print sizes; do not download")
    p.add_argument("--download", action="store_true",
                   help="Download (resumable) to --out")
    p.add_argument("--out", type=Path, default=Path("./data/cryptobench"),
                   help="Output directory (default ./data/cryptobench)")
    args = p.parse_args()

    if args.check_size:
        print("=== HEAD size check ===")
        sizes = check_size()
        total = 0
        for _url, name, expected, _lic in _FILES:
            got = sizes.get(name)
            if got is None:
                print(f"  {name}: HEAD failed (expected {expected / 1024 / 1024:.2f} MB)")
            else:
                print(f"  {name}: {got / 1024 / 1024:.2f} MB")
                total += got
        print(f"\n  total: {total / 1024 / 1024:.2f} MB "
              f"= {total / 1024 / 1024 / 1024:.3f} GB")
        free = free_disk_bytes(args.out)
        print(f"  free disk at {args.out}: {free / (1 << 30):.2f} GB")
        return 0

    if args.download:
        print(f"=== downloading to {args.out} (resumable) ===")
        fetch(args.out)
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

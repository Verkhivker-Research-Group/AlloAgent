"""What an arm's container can actually see.

Run inside the arm's container (the same mounts the runner uses):

    python scripts/inspect_arm_env.py

It prints, for the data directories, the model envs and the network:

* whether each of our data directories is present (and what is in it);
* whether the PocketMiner env and the GPU tool envs are present (and
  what is in them);
* whether the internet works, and which hosts answer;
* what IS visible: the conda envs, the mounts, the working directory.

The exit code is 0 when the expected isolation holds for the arm that
was asked for, and 1 when something that must be hidden is visible.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.request
from pathlib import Path

DATA_DIRS = [
    "/data/chembl",
    "/data/clinvar",
    "/data/alphamissense",
    "/data/cryptobench",
    "/biolab_data",
    "/biolab_data/asd",
    "/biolab_data/biolip",
    "/data/structures",
]
MODEL_ENVS = [
    "/opt/conda/envs/pocketminer_env",
    "/opt/conda/envs/boltz2_env",
    "/opt/conda/envs/bioemu_env",
    "/opt/pocketminer",
    "/opt/ae-pocketminer",
    "/opt/pocketminer_weights.sha256",
]
HOSTS = [
    "files.rcsb.org",
    "rest.uniprot.org",
    "www.ebi.ac.uk",
    "api.minimax.io",
]


def probe(host: str, port: int = 443, timeout: float = 8.0) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "reachable"
    except Exception as error:  # noqa: BLE001
        return f"unreachable ({type(error).__name__})"


def main() -> int:
    expect_isolated = "--expect-isolated" in sys.argv
    print("=== the data directories ===")
    visible_data = []
    for path in DATA_DIRS:
        target = Path(path)
        if target.exists():
            visible_data.append(path)
            try:
                entries = sorted(item.name for item in target.iterdir())[:8]
            except OSError:
                entries = []
            print(f"  {path:28s} PRESENT  {entries}")
        else:
            print(f"  {path:28s} absent")
    print()
    print("=== the model envs ===")
    visible_models = []
    for path in MODEL_ENVS:
        target = Path(path)
        if not target.exists():
            print(f"  {path:32s} absent")
            continue
        size = 0
        entries: list[str] = []
        if target.is_file():
            size = target.stat().st_size
        elif target.is_dir():
            try:
                entries = sorted(item.name for item in target.iterdir())
                size = sum(item.stat().st_size for item in target.rglob("*") if item.is_file())
            except OSError:
                entries = []
        # An empty directory is an empty bind mount: the path exists but
        # holds nothing, which is the isolation.
        hidden = size == 0
        if not hidden:
            visible_models.append(path)
        print(f"  {path:32s} {'HIDDEN (empty mount)' if hidden else 'PRESENT'}"
              f"  ({size} bytes, {len(entries)} entries)")
    print()
    print("=== the network ===")
    for host in HOSTS:
        print(f"  {host:22s} {probe(host)}")
    print()
    print("=== what IS visible ===")
    envs = Path("/opt/conda/envs")
    print(f"  the conda envs: {sorted(item.name for item in envs.iterdir()) if envs.is_dir() else 'none'}")
    print(f"  the working directory: {os.getcwd()}")
    print(f"  /workspace: {sorted(item.name for item in Path('/workspace').iterdir())[:14] if Path('/workspace').is_dir() else 'absent'}")
    print("  the mounts:")
    try:
        for line in Path("/proc/mounts").read_text(encoding="utf-8").splitlines():
            if any(token in line for token in ("/workspace", "/data", "/biolab_data", "/opt/conda", "/opt/pocketminer", "/opt/ae-pocketminer")):
                print(f"    {line}")
    except OSError as error:
        print(f"    (cannot read /proc/mounts: {error})")
    print()
    print("=== the verdict ===")
    if expect_isolated:
        problems = [path for path in visible_data if path not in ("/data/structures",)]
        problems += visible_models
        print(f"  the data directories that must be hidden and are not: {problems}")
        print("  RESULT:", "PASS" if not problems else "FAIL")
        return 0 if not problems else 1
    print(f"  the data directories that are visible: {visible_data}")
    print(f"  the model envs that are visible: {visible_models}")
    print("  (no isolation expected here)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Launch the capability benchmark: the X prompts, both arms, the main or the
restricted scenario.

The X prompts live in their own registry (``benchmark/capability/``), so the
driver - which launches ``run_benchmark.py --benchmark-dir <the launch
checkout's benchmark/>`` - needs a launch checkout whose prompt table contains
them.  This script builds that checkout in a temporary directory: a copy of the
launch checkout's ``benchmark/`` with the capability prompts appended to the
copies of ``benchmark_draft.json`` and ``checklists.json``.  **Nothing is
written into the repository and the launch checkout is not modified.**

    python benchmark/run_capability_launch.py --scenario main \\
        --run-list benchmark/capability/run_list_main.json \\
        --launch-tag capability-2026-11-07-main \\
        --launch-checkout <the launch checkout> --run-dir <the run dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CAPABILITY = REPO / "benchmark" / "capability"


def build_launch_checkout(source: Path, workdir: Path) -> Path:
    """A copy of the source checkout with the capability prompts in its benchmark/.

    The source is the repository at its current commit (not the older launch
    checkout), because the capability prompts need the current driver and the
    current ``run_benchmark.py`` (the ``--run-list`` and ``--expected-sha256``
    arguments).  The data directory is not copied: it is mounted separately.
    """
    target = workdir / "capability_checkout"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True,
                    ignore=shutil.ignore_patterns(".git", "data", "build_logs",
                                                 ".pytest_cache", "__pycache__",
                                                 "*.pyc"))
    bench = target / "benchmark"
    draft = json.loads((bench / "benchmark_draft.json").read_text(encoding="utf-8"))
    checklists = json.loads((bench / "checklists.json").read_text(encoding="utf-8"))
    cap_prompts = json.loads((CAPABILITY / "prompts.json").read_text(encoding="utf-8"))
    cap_lists = json.loads((CAPABILITY / "checklists.json").read_text(encoding="utf-8"))
    draft_prompts = draft if isinstance(draft, list) else draft.setdefault("prompts", [])
    list_prompts = checklists if isinstance(checklists, list) else checklists.setdefault("prompts", [])
    for prompt in cap_prompts["prompts"]:
        draft_prompts.append({
            "id": prompt["id"], "category": prompt["category"], "tier": 2,
            "accession": "", "prompt": prompt["prompt"],
            "solvable_from_local_resources_alone": "yes",
        })
    for entry in cap_lists["prompts"]:
        list_prompts.append(entry)
    launch_path = bench / "launch_prompt_set.json"
    if launch_path.is_file():
        launch = json.loads(launch_path.read_text(encoding="utf-8"))
        cap_ids = [p["id"] for p in cap_prompts["prompts"]]
        launch["launch_prompts"] = list(launch.get("launch_prompts", [])) + cap_ids
        counts = launch.setdefault("counts", {})
        counts["draft_prompts"] = int(counts.get("draft_prompts", 0)) + len(cap_ids)
        counts["launch_prompts"] = int(counts.get("launch_prompts", 0)) + len(cap_ids)
        launch_path.write_text(
            json.dumps(launch, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
    restricted_path = bench / "restricted_prompt_set.json"
    if restricted_path.is_file():
        restricted = json.loads(restricted_path.read_text(encoding="utf-8"))
        restricted_prompts = restricted if isinstance(restricted, list) else restricted.setdefault("prompts", [])
        for prompt in cap_prompts["prompts"]:
            if not prompt["restricted"]:
                continue
            restricted_prompts.append({
                "id": prompt["id"], "category": prompt["category"], "tier": 2,
                "accession": "", "prompt": prompt["prompt"],
                "solvable_from_local_resources_alone": "yes",
            })
        restricted_path.write_text(
            json.dumps(restricted, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
    (bench / "benchmark_draft.json").write_text(
        json.dumps(draft, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (bench / "checklists.json").write_text(
        json.dumps(checklists, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return target


def benchmark_dir_sha256(bench: Path) -> str:
    """The digest of the benchmark dir, over the two prompt tables."""
    digest = hashlib.sha256()
    for name in sorted(p.name for p in bench.iterdir() if p.is_file()):
        digest.update(name.encode("utf-8"))
        digest.update((bench / name).read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--scenario", choices=("main", "restricted"), required=True)
    parser.add_argument("--run-list", required=True)
    parser.add_argument("--launch-tag", required=True)
    parser.add_argument("--launch-checkout", default=str(REPO),
                        help="the checkout to copy from (the repository at its current commit)")
    parser.add_argument("--baseline-workspace", default=str(
        Path(os.environ.get("TEMP", "/tmp")) / "opencode" / "baseline_wt"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--data-root", default=str(REPO / "data"))
    parser.add_argument("--structure-cache", default=str(REPO / "data" / "structures_cache"))
    parser.add_argument("--env-source", default=str(
        expand_home(Path(r"<HOME>\Documents\CPSC\Biolab") / ".env.extracted")))
    parser.add_argument("--image", default="alloagent-eval:v6")
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--expected-sha256", default="")
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261027)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-canary", action="store_true")
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="capability_launch_"))
    checkout = build_launch_checkout(Path(args.launch_checkout), workdir)
    sha = benchmark_dir_sha256(checkout / "benchmark")
    print(f"the capability launch checkout: {checkout}")
    print(f"the benchmark dir digest: {sha}")
    if args.expected_sha256 and args.expected_sha256 != sha:
        print("the expected digest does not match; refusing to launch")
        return 2

    command = [
        sys.executable, str(checkout / "benchmark" / "benchmark_driver.py"),
        "--launch-tag", args.launch_tag,
        "--image-digest", args.image_digest,
        "--launch-checkout", str(checkout),
        "--baseline-workspace", args.baseline_workspace,
        "--run-dir", args.run_dir,
        "--scenario", args.scenario,
        "--parallel", str(args.parallel),
        "--repeats", str(args.repeats),
        "--seed", str(args.seed),
        "--image", args.image,
        "--env-source", args.env_source,
        "--data-root", args.data_root,
        "--structure-cache", args.structure_cache,
        "--run-list", str(Path(args.run_list).resolve()),
    ]
    if args.skip_canary:
        command.append("--skip-canary")
    print("the driver command:", " ".join(command))
    if args.dry_run:
        return 0
    return subprocess.call(command, cwd=str(checkout))


if __name__ == "__main__":
    raise SystemExit(main())

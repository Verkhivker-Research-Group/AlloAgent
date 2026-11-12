#!/usr/bin/env python3
"""The smoke test: 2 dev prompts x 2 arms x 1 repeat, through the whole
pipeline, with the records in a host run directory outside the
repository.

The pipeline, in order:

    run_benchmark (scripts/run_arm.py)  -> the run records
    benchmark/score_runs.py             -> the scripted scoring
    benchmark/make_judge_batch.py       -> the masked, shuffled judge batch
    benchmark/analyze.py                -> the analysis

The two arms run SEQUENTIALLY (one heavy job at a time) and both write
into the same host run directory (<run_dir>/<arm>).

    python benchmark/run_smoke.py --run-dir <host dir> [--image alloagent-eval:v6]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--image", default="alloagent-eval:v6")
    parser.add_argument("--arm", action="append", default=None,
                        help="the arms to run (default: both)")
    parser.add_argument("--env-source",
                        default=str(expand_home(r"<HOME>\Documents\CPSC\Biolab\.env")))
    parser.add_argument("--baseline-workspace",
                        default=str(expand_home(r"<HOME>\AppData\Local\Temp\opencode\baseline_wt")))
    parser.add_argument("--prompts", default=str(REPO / "docs" / "dev_prompts_smoke.md"))
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    arms = args.arm or ["alloagent", "baseline"]
    prompts = Path(args.prompts)
    structure_cache = REPO / "data" / "structures_cache"

    for arm in arms:
        workspace = REPO if arm == "alloagent" else Path(args.baseline_workspace)
        command = [
            sys.executable, str(REPO / "scripts" / "run_arm.py"),
            "--arm", arm,
            "--image", args.image,
            "--workspace", str(workspace),
            "--dev-prompts",
            "--dev-prompts-script", str(REPO / "scripts" / "run_dev_prompts.py"),
            "--dev-prompts-prompts", str(prompts),
            "--run-dir", str(run_dir),
            "--structure-cache", str(structure_cache),
            "--env-source", args.env_source,
            "--log", str(run_dir / f"{arm}.log"),
        ]
        if arm == "baseline":
            command += [
                "--dev-prompts-data-path", "/agent_cwd/data",
                "--no-data-mounts", "--no-pocketminer-env", "--no-gpu-envs",
            ]
        print(f"\n=== the {arm} arm ===", flush=True)
        started = time.time()
        result = subprocess.run(command, cwd=str(REPO))
        print(f"=== the {arm} arm: exit {result.returncode} in "
              f"{time.time() - started:.1f} s ===", flush=True)
        if result.returncode != 0:
            print(f"the {arm} arm failed; stopping", flush=True)
            return result.returncode

    print("\n=== the scripted scoring ===", flush=True)
    subprocess.run(
        [sys.executable, str(REPO / "benchmark" / "score_runs.py"),
         str(run_dir / "alloagent"), str(run_dir / "baseline")],
        cwd=str(REPO),
    )
    print("\n=== the masked, shuffled judge batch ===", flush=True)
    subprocess.run(
        [sys.executable, str(REPO / "benchmark" / "make_judge_batch.py"),
         str(run_dir / "alloagent"), str(run_dir / "baseline"),
         "--out", str(run_dir / "judge_batch.json"),
         "--key", str(run_dir / "judge_key.json"),
         "--seed", "20261026"],
        cwd=str(REPO),
    )
    print("\n=== the analysis ===", flush=True)
    subprocess.run(
        [sys.executable, str(REPO / "benchmark" / "analyze.py"),
         str(run_dir / "alloagent"), str(run_dir / "baseline"),
         "--token-budget", "1000000", "--wall-cap-s", "1800"],
        cwd=str(REPO),
    )
    print(f"\nthe run directory: {run_dir}")
    for path in sorted(run_dir.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(run_dir)}  ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

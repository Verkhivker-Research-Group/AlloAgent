"""The projection: the expected wall time and tokens for the main run
and for the restricted scenario, from the mean per-run time and tokens
of every arm A and arm D run so far.

The records are collected from every run directory in the repository
and in the baseline worktree (the gate runs, the smoke runs and the
new smoke), and the mean is taken per arm.  The projection is then:

    wall time  = n_runs x mean_seconds / parallelism
    tokens     = n_runs x mean_tokens

    python benchmark/project_runs.py [--parallel 4] [--repeats 3]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
BASELINE = expand_home(r"<HOME>\AppData\Local\Temp\opencode\baseline_wt")
BASELINE_GATE = expand_home(r"<HOME>\AppData\Local\Temp\opencode\baseline_wt_gate")
RUN_DIRS = [
    ("arm D", REPO / "build_logs" / "dev_runs_capability2_armD"),
    ("arm A", BASELINE_GATE / "build_logs" / "dev_runs_capability2_armA"),
    ("arm D", REPO / "build_logs" / "smoke2_armD"),
    ("arm A", BASELINE / "build_logs" / "smoke2_armA"),
    ("arm D", expand_home(r"<HOME>\AppData\Local\Temp\opencode\benchmark_runs") / "alloagent"),
    ("arm A", expand_home(r"<HOME>\AppData\Local\Temp\opencode\benchmark_runs") / "baseline"),
]


def collect() -> dict:
    out: dict = {"arm D": [], "arm A": []}
    for arm, directory in RUN_DIRS:
        if not directory.is_dir():
            continue
        for summary_path in sorted(directory.glob("*/summary.json")):
            try:
                data = json.loads(summary_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if data.get("status") != "completed":
                continue
            tokens = (data.get("token_total") or {}).get("total_tokens")
            wall = data.get("wall_time_s")
            if not tokens or not wall:
                continue
            out[arm].append({
                "source": f"{directory.name}/{summary_path.parent.name}",
                "id": data.get("id"),
                "tokens": int(tokens),
                "wall_s": float(wall),
            })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--restricted-prompts", type=int, default=15)
    args = parser.parse_args()

    runs = collect()
    print(f"{'arm':7s} {'n':>3s} {'mean tokens':>13s} {'median tokens':>14s} "
          f"{'mean wall s':>12s} {'median wall s':>14s}")
    print("-" * 80)
    means = {}
    for arm, rows in runs.items():
        if not rows:
            print(f"{arm:7s} {0:>3d} (no records)")
            continue
        tokens = sorted(row["tokens"] for row in rows)
        walls = sorted(row["wall_s"] for row in rows)
        mean_tokens = sum(tokens) / len(tokens)
        mean_wall = sum(walls) / len(walls)
        median_tokens = tokens[len(tokens) // 2]
        median_wall = walls[len(walls) // 2]
        means[arm] = (mean_tokens, mean_wall)
        print(f"{arm:7s} {len(rows):>3d} {mean_tokens:>13,.0f} {median_tokens:>14,} "
              f"{mean_wall:>12.1f} {median_wall:>14.1f}")
    print()
    for arm, rows in runs.items():
        if not rows:
            continue
        print(f"the {arm} runs:")
        for row in sorted(rows, key=lambda item: item["source"]):
            print(f"  {row['source']:<34s} {row['id']:<5s} "
                  f"{row['tokens']:>12,} tokens  {row['wall_s']:>8.1f} s")
    print()

    if not means:
        print("no runs to project from")
        return 1
    all_tokens = [value for (tokens, _wall), rows in zip(means.values(), runs.values())
                  for value in [tokens]]
    all_walls = [wall for (_tokens, wall) in means.values()]
    mean_tokens = sum(all_tokens) / len(all_tokens)
    mean_wall = sum(all_walls) / len(all_walls)

    for label, prompts in (("the main run (40 prompts x 3 repeats x 2 arms)", 40),
                            (f"the restricted scenario ({args.restricted_prompts} prompts x "
                             f"{args.repeats} x 2)", args.restricted_prompts)):
        n_runs = prompts * args.repeats * 2
        print(f"{label}")
        print(f"  runs: {n_runs}  (at --parallel {args.parallel})")
        print(f"  the mean per run: {mean_tokens:,.0f} tokens, {mean_wall:.1f} s")
        print(f"  the total tokens: {n_runs * mean_tokens:,.0f}")
        print(f"  the total wall time: {n_runs * mean_wall:,.0f} s "
              f"= {n_runs * mean_wall / 3600:.2f} h of work")
        print(f"  the wall clock at --parallel {args.parallel}: "
              f"{n_runs * mean_wall / args.parallel:,.0f} s "
              f"= {n_runs * mean_wall / args.parallel / 3600:.2f} h")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

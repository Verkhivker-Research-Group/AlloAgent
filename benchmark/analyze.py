"""The analysis of a run batch: one table per run and the aggregate.

For every run it reports the steps, the tokens (in, out, total), the
wall time, the early-termination cause, the dirty flag and whether the
run fits the cost budget (the token budget and the per-run wall-clock
cap).  A run that has no per-step record is reported as missing the
budget fields, not as passing.

    python benchmark/analyze.py <out_dir> [<out_dir> ...] [--token-budget 1000000] [--wall-cap-s 1800]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyse_run(run_dir: Path, token_budget: int, wall_cap_s: float) -> dict:
    summary_path = run_dir / "summary.json"
    run_path = run_dir / "run.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    record = json.loads(run_path.read_text(encoding="utf-8")) if run_path.is_file() else {}

    messages = record.get("messages") or []
    steps_with_budget = [
        message for message in messages
        if "cumulative_tokens" in message and "elapsed_s" in message
    ]
    early_termination = None
    if summary.get("status") != "completed":
        early_termination = summary.get("error") or f"status={summary.get('status')}"
    elif record.get("recursion_limit_hit") or record.get("early_termination"):
        early_termination = record.get("early_termination") or "recursion limit"
    elif record.get("n_steps") and record.get("config", {}).get("recursion_limit"):
        if record["n_steps"] >= int(record["config"]["recursion_limit"]):
            early_termination = (
                f"the recursion limit ({record['config']['recursion_limit']}) was reached"
            )

    tokens = summary.get("token_total") or {}
    total_tokens = int(tokens.get("total_tokens") or 0)
    wall = summary.get("wall_time_s")
    within_budget = None
    if total_tokens and wall is not None:
        within_budget = total_tokens <= token_budget and wall <= wall_cap_s

    return {
        "id": summary.get("id") or run_dir.name,
        "status": summary.get("status"),
        "steps": summary.get("n_steps"),
        "tokens": tokens,
        "wall_time_s": wall,
        "early_termination": early_termination,
        "dirty": summary.get("git_dirty"),
        "budget_fields_present": bool(steps_with_budget),
        "steps_with_budget_fields": len(steps_with_budget),
        "within_budget": within_budget,
        "git_commit": summary.get("git_commit"),
        "image_id": summary.get("image_id"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dirs", nargs="+")
    parser.add_argument("--token-budget", type=int, default=1_000_000)
    parser.add_argument("--wall-cap-s", type=float, default=1800.0)
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=20261027,
        help="the seed for the bootstrap confidence intervals over the runs",
    )
    parser.add_argument("--bootstrap-rounds", type=int, default=2000)
    args = parser.parse_args()

    rows = []
    for out_dir in args.out_dirs:
        base = Path(out_dir)
        for run_dir in sorted(base.iterdir()):
            if run_dir.is_dir() and (run_dir / "summary.json").is_file():
                rows.append(analyse_run(run_dir, args.token_budget, args.wall_cap_s))

    header = (
        f"{'run':6s} {'status':10s} {'steps':>6s} {'input':>10s} {'output':>9s} "
        f"{'total':>10s} {'wall_s':>8s} {'early termination':28s} {'dirty':6s} "
        f"{'budget fields':14s} {'in budget':9s}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        tokens = row["tokens"]
        print(
            f"{row['id']:6s} {str(row['status']):10s} {str(row['steps']):>6s} "
            f"{str(tokens.get('input_tokens', '-')):>10s} "
            f"{str(tokens.get('output_tokens', '-')):>9s} "
            f"{str(tokens.get('total_tokens', '-')):>10s} "
            f"{('%.1f' % row['wall_time_s']) if row['wall_time_s'] is not None else '-':>8s} "
            f"{str(row['early_termination'] or '-'):28s} "
            f"{str(row['dirty']):6s} "
            f"{str(row['steps_with_budget_fields']) + '/' + str(row['steps']):14s} "
            f"{str(row['within_budget']):9s}"
        )
    print()
    print(f"runs: {len(rows)}")
    print(f"  completed: {sum(1 for row in rows if row['status'] == 'completed')}")
    print(f"  failed:    {sum(1 for row in rows if row['status'] != 'completed')}")
    print(f"  dirty:     {sum(1 for row in rows if row['dirty'])}")
    print(f"  with the per-step budget fields: "
          f"{sum(1 for row in rows if row['budget_fields_present'])}/{len(rows)}")
    print(f"  within the budget ({args.token_budget} tokens, {args.wall_cap_s} s): "
          f"{sum(1 for row in rows if row['within_budget'])}/{len(rows)}")
    total_tokens = sum(int((row["tokens"] or {}).get("total_tokens") or 0) for row in rows)
    total_wall = sum(float(row["wall_time_s"] or 0.0) for row in rows)
    print(f"  tokens in total: {total_tokens}; wall time in total: {total_wall:.1f} s")

    completed = [row for row in rows if row["status"] == "completed"]
    if completed:
        import random

        rng = random.Random(args.bootstrap_seed)
        budget_flags = [1.0 if row["within_budget"] else 0.0 for row in completed]
        rounds = []
        for _ in range(args.bootstrap_rounds):
            sample = [rng.choice(budget_flags) for _ in budget_flags]
            rounds.append(sum(sample) / len(sample))
        rounds.sort()
        low = rounds[int(0.025 * (len(rounds) - 1))]
        high = rounds[int(0.975 * (len(rounds) - 1))]
        rate = sum(budget_flags) / len(budget_flags)
        print(
            f"  the within-budget rate over the completed runs: {rate:.3f} "
            f"(bootstrap 95 % CI [{low:.3f}, {high:.3f}], seed {args.bootstrap_seed}, "
            f"{args.bootstrap_rounds} rounds)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

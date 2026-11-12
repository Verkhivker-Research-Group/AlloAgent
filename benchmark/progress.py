"""The progress report of a running benchmark. Read-only, safe at any time.

It reads the run records, the driver state and the driver log, and it
writes nothing. It never touches docker, so it can be run while the
benchmark is running.

    python benchmark/progress.py --run-dir <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _arm_records(run_dir: Path, arm: str) -> list[dict]:
    """The summaries of one arm."""
    out: list[dict] = []
    base = run_dir / arm
    if not base.is_dir():
        return out
    for record_dir in sorted(base.iterdir()):
        if record_dir.is_dir():
            summary = _read_json(record_dir / "summary.json")
            if summary:
                out.append(summary)
    return out


def _mean(values: Iterable[float]) -> float:
    values = [v for v in values if v is not None]
    return (sum(values) / len(values)) if values else 0.0


def _tokens(summary: dict) -> int:
    tokens = summary.get("token_total") or {}
    try:
        return int(tokens.get("total_tokens") or 0)
    except (TypeError, ValueError):
        return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)

    state = _read_json(run_dir / "driver_state.json")
    print(f"the run directory: {run_dir}")
    if state:
        print(f"launch tag: {state.get('launch_tag')}   "
              f"image: {state.get('image_digest')}   seed: {state.get('seed')}")
        print(f"planned: {state.get('planned')}   completed: {state.get('completed')}   "
              f"failed: {state.get('failed')}   skipped: {state.get('skipped')}   "
              f"parallel now: {state.get('parallel')}")
        pauses = state.get("quota_pauses") or []
        print(f"quota pauses: {len(pauses)}"
              + (f"   the last one: {pauses[-1]}" if pauses else ""))
        print(f"throttle rate: {state.get('throttle_rate')}   "
              f"quota-interrupted runs: {state.get('quota_interrupted')}")

    total_tokens = 0
    all_walls: list[float] = []
    completed_total = 0
    for arm in ("alloagent", "baseline"):
        base = run_dir / arm
        summaries = _arm_records(run_dir, arm)
        complete = [s for s in summaries if s.get("status") == "completed"]
        failed = [s for s in summaries if s.get("status") == "failed"]
        quota = [s for s in summaries if s.get("status") == "quota_interrupted"]
        running = 0
        if base.is_dir():
            running = sum(
                1 for d in base.iterdir()
                if d.is_dir() and not (d / "summary.json").is_file()
            )
        tokens = [ _tokens(s) for s in complete ]
        walls = [float(s.get("wall_time_s") or 0.0) for s in complete]
        total_tokens += sum(tokens)
        all_walls += walls
        completed_total += len(complete)
        print(f"\n=== the {arm} arm ===")
        print(f"  complete: {len(complete)}   in progress: {running}   "
              f"failed: {len(failed)}   quota-interrupted: {len(quota)}")
        print(f"  mean tokens per completed run: {_mean(tokens):,.0f}")
        print(f"  mean wall time per completed run: {_mean(walls):,.1f} s")
        print(f"  tokens in this arm: {sum(tokens):,}")

    planned = int(state.get("planned") or 0)
    remaining = max(0, planned - completed_total)
    parallelism = max(1, int(state.get("parallel") or 1))
    mean_wall = _mean(all_walls)
    eta_s = remaining * mean_wall / parallelism
    print(f"\ntotal tokens so far: {total_tokens:,}")
    print(f"completed runs: {completed_total}/{planned}   remaining: {remaining}")
    print(f"estimated time remaining: {eta_s:,.0f} s "
          f"({eta_s / 3600:.2f} h) - a projection from the mean wall time "
          f"({mean_wall:,.1f} s) at the current parallelism ({parallelism})")

    log_path = run_dir / "driver.log"
    print(f"\nthe last 5 lines of {log_path.name}:")
    if log_path.is_file():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-5:]:
            print(f"  {line}")
    else:
        print("  (no driver log yet)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

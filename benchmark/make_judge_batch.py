"""The judge batch: the runs, masked and shuffled.

The judge must not know which arm produced an answer, and the order
must not leak the arm either, so:

* every run gets an opaque id (``run_01``, ``run_02``, ...);
* the arm label is removed from the batch and kept in a separate key
  file that the judge never sees;
* the order is shuffled with a fixed, committed seed.

    python benchmark/make_judge_batch.py <out_dir> [<out_dir> ...] --out <batch.json> --key <key.json> [--seed 20261026]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dirs", nargs="+")
    parser.add_argument("--out", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--seed", type=int, default=20261026)
    args = parser.parse_args()

    runs = []
    for out_dir in args.out_dirs:
        base = Path(out_dir)
        label = base.name
        for summary_path in sorted(base.glob("*/summary.json")):
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            runs.append(
                {
                    "arm": label,
                    "id": data.get("id") or summary_path.parent.name,
                    "prompt": data.get("prompt"),
                    "answer": data.get("final_content") or "",
                    "status": data.get("status"),
                }
            )

    order = list(range(len(runs)))
    random.Random(args.seed).shuffle(order)

    batch = []
    key = []
    for position, index in enumerate(order, start=1):
        run = runs[index]
        opaque = f"run_{position:02d}"
        batch.append(
            {
                "judge_id": opaque,
                "prompt_id": run["id"],
                "prompt": run["prompt"],
                "answer": run["answer"],
            }
        )
        key.append(
            {
                "judge_id": opaque,
                "arm": run["arm"],
                "prompt_id": run["id"],
                "status": run["status"],
                "answer_sha256": hashlib.sha256(
                    run["answer"].encode("utf-8")
                ).hexdigest(),
            }
        )

    Path(args.out).write_text(json.dumps(batch, indent=2), encoding="utf-8")
    Path(args.key).write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"the judge batch: {len(batch)} runs, seed {args.seed}")
    print(f"  {args.out}")
    print(f"  {args.key} (the arm labels; the judge does not see this file)")
    for entry in key:
        print(f"  {entry['judge_id']} <- {entry['arm']} / {entry['prompt_id']}"
              f" (status {entry['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

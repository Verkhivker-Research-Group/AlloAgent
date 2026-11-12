"""The human subset: the prompts a human judge reads by hand.

The analysis plan fixes the human subset at 30 prompts and samples them
with the shuffle seed (20261026) from the committed launch set - the
prompts that are actually run (40 of them since 2026-11-03, when K04 was
replaced by the KRAS contact-network prompt).  The sample is written out,
so that it can be checked and re-derived.

The launch set is read defensively: it may be a list of ids or a record
that holds them.  If its shape does not yield the 40 launch prompts,
the prompt ids of the committed checklist are used instead.

    python benchmark/make_human_subset.py [--out <subset.json>] [--seed 20261026] [--size 30]
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LAUNCH_SET = REPO / "benchmark" / "launch_prompt_set.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"

# The size of the committed launch set: the prompt table (all of its
# prompts are run).
LAUNCH_SET_SIZE = 40


def _ids_from(entries: object) -> list[str]:
    """The prompt ids of a list of ids or of a list of prompt records."""
    if not isinstance(entries, list):
        return []
    ids: list[str] = []
    for entry in entries:
        if isinstance(entry, str):
            ids.append(entry)
        elif isinstance(entry, dict) and entry.get("id"):
            ids.append(str(entry["id"]))
    return ids


def load_prompt_ids(path: Path) -> list[str]:
    """The prompt ids of a launch-set file, whatever its shape is."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for key in ("launch_prompts", "prompts", "prompt_ids"):
            if key in payload:
                return _ids_from(payload[key])
        return []
    return _ids_from(payload)


def checklist_prompt_ids(path: Path) -> list[str]:
    """The prompt ids of the committed checklist."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _ids_from(payload.get("prompts") or [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument("--size", type=int, default=30)
    args = parser.parse_args()

    source = LAUNCH_SET
    ids = load_prompt_ids(LAUNCH_SET)
    if len(set(ids)) != LAUNCH_SET_SIZE:
        ids = checklist_prompt_ids(CHECKLISTS)
        source = CHECKLISTS
    pool = sorted(set(ids))
    if not pool:
        print("no prompt ids found; the source set is empty")
        return 1
    if args.size > len(pool):
        print(f"the pool holds {len(pool)} prompts; {args.size} cannot be sampled from it")
        return 1

    subset = random.Random(args.seed).sample(pool, args.size)
    payload = {
        "seed": args.seed,
        "size": args.size,
        "prompt_ids": subset,
        "source": source.relative_to(REPO).as_posix(),
    }

    print(
        f"the human subset: {args.size} prompts (seed {args.seed}) from "
        f"{payload['source']} ({len(pool)} prompts in the pool)"
    )
    print("  " + ", ".join(subset))
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  the subset: {out_path}")
    else:
        print("  no file written (--out was not given)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

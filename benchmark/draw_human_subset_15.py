"""Draw a 15-run subset from the 30-run human subset.

The seed and the procedure are recorded in
``benchmark/human_subset_draw.md`` (dated note 2026-11-03) **before** the
draw is made.  This script implements that procedure:

* the pool is the 30 runs of the human subset, in the order of their
  rating files (``human_run_01.md`` ... ``human_run_30.md``);
* the prompt categories that appear among the 30 are served first, in
  the alphabetical order of their names, one run each, so that every
  category appears at least once;
* the remaining slots are filled one at a time, the arm that is behind
  served first, so the two arms end at 7 and 8;
* the 15 are written in the order they were drawn, as
  ``human_run_01.md`` ... ``human_run_15.md``, each a copy of the
  selected file of the 30: the 30 are not changed;
* the key (the opaque id -> arm, prompt, repeat, category, the file of
  the 30 it comes from) is written **outside** the repository.

    python benchmark/draw_human_subset_15.py [--seed 20261104]
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

SUBSET_30 = REPO / "benchmark" / "judging" / "human_subset_30"
SUBSET_15 = REPO / "benchmark" / "judging" / "human_subset_15"
KEY_30 = expand_home(r"<HOME>\AppData\Local\Temp\opencode\human_subset_key.json")
KEY_15 = expand_home(r"<HOME>\AppData\Local\Temp\opencode\human_subset_15_key.json")
SEED = 20261104
SIZE = 15


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--size", type=int, default=SIZE)
    parser.add_argument("--subset-30", default=str(SUBSET_30))
    parser.add_argument("--subset-15", default=str(SUBSET_15))
    parser.add_argument("--key-30", default=str(KEY_30))
    parser.add_argument("--key-15", default=str(KEY_15))
    args = parser.parse_args()

    source = Path(args.subset_30)
    target = Path(args.subset_15)
    key_30 = json.loads(Path(args.key_30).read_text(encoding="utf-8"))
    by_file = {row["file"]: row for row in key_30["runs_key"]}

    pool = []
    for path in sorted(source.glob("human_run_*.md")):
        row = by_file.get(path.name)
        if row is None:
            print(f"ERROR: the key does not name {path.name}", file=sys.stderr)
            return 2
        pool.append({"row": row, "path": path})
    if len(pool) < args.size:
        print(f"the pool holds {len(pool)} runs; {args.size} cannot be drawn")
        return 1

    rng = random.Random(args.seed)
    by_category: dict[str, list[dict]] = {}
    for entry in pool:
        by_category.setdefault(entry["row"]["category"], []).append(entry)

    drawn: list[dict] = []
    taken: set[int] = set()
    for category in sorted(by_category):
        candidates = [entry for entry in by_category[category]
                      if id(entry) not in taken]
        if not candidates:
            continue
        chosen = candidates[rng.randrange(len(candidates))]
        drawn.append(chosen)
        taken.add(id(chosen))

    remaining = [entry for entry in pool if id(entry) not in taken]
    while len(drawn) < args.size and remaining:
        counts = Counter(entry["row"]["arm"] for entry in drawn)
        behind = min(counts, key=lambda arm: (counts[arm], arm))
        candidates = [entry for entry in remaining if entry["row"]["arm"] == behind]
        if not candidates:
            candidates = remaining
        chosen = candidates[rng.randrange(len(candidates))]
        drawn.append(chosen)
        remaining.remove(chosen)

    target.mkdir(parents=True, exist_ok=True)
    key_rows = []
    for number, entry in enumerate(drawn, start=1):
        name = f"human_run_{number:02d}.md"
        shutil.copyfile(entry["path"], target / name)
        row = entry["row"]
        key_rows.append({
            "run_id": row["run_id"],
            "file": name,
            "the_file_of_the_30": entry["path"].name,
            "arm": row["arm"],
            "prompt_id": row["prompt_id"],
            "repeat": row["repeat"],
            "category": row["category"],
            "answer_sha256": row.get("answer_sha256"),
        })

    KEY_15.parent.mkdir(parents=True, exist_ok=True)
    KEY_15.write_text(json.dumps({
        "what_this_file_is": (
            "the key of the 15-run subset of the human subset: the opaque run "
            "id of every drawn run, the file it is written as, the file of "
            "the 30 it comes from, and the arm, the prompt, the repeat and "
            "the category.  The rater does not get this file."
        ),
        "seed": args.seed,
        "procedure": "benchmark/human_subset_draw.md (dated note 2026-11-03)",
        "size": len(key_rows),
        "source_size": len(pool),
        "runs_key": key_rows,
    }, indent=2) + "\n", encoding="utf-8")

    readme = [
        "# The 15-run subset of the human subset",
        "",
        f"Drawed with the seed {args.seed} from the 30-run human subset by "
        f"`benchmark/draw_human_subset_15.py`; the seed and the procedure are "
        f"recorded in `benchmark/human_subset_draw.md` (dated note "
        f"2026-11-03).",
        "",
        f"* **15 files**, `human_run_01.md` to `human_run_15.md`, in the order "
        f"they were drawn; each is a copy of one of the 30 files of "
        f"`../human_subset_30/` (the 30 are unchanged).",
        "* the masking is the same as the 30 and as the judge batches: the "
        "one-sided tool names, the arm names, the branch names and the "
        "persona name are replaced by `[TOOL]`, and every number, "
        "identifier, residue and structure ID is kept.",
        "* the **key is not here**: it is `human_subset_15_key.json`, in the "
        "parent folder of the repository's temp area, and the rater does not "
        "get it.",
        "",
        "Do not open the key file, the judge outputs, or the run records.",
    ]
    (target / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    arms = Counter(row["arm"] for row in key_rows)
    categories = Counter(row["category"] for row in key_rows)
    print(f"the draw: {len(key_rows)} runs with the seed {args.seed}")
    print(f"  the arms: {sorted(arms.values())} (the two arms)")
    print(f"  the categories covered: {len(categories)} of "
          f"{len({entry['row']['category'] for entry in pool})}")
    for category, count in sorted(categories.items()):
        print(f"    {category}: {count}")
    print(f"  the rating folder: {target}")
    print(f"  the key: {KEY_15}")
    print(f"  drawn at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

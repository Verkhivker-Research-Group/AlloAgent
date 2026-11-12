"""The qualitative judge batch: the runs, masked and shuffled.

The LLM judge scores the QUALITATIVE checklist items - the ones a
script cannot decide - and it must not be able to tell which arm
produced an answer.  So:

* every run gets an opaque id (``run_01``, ``run_02``, ...);
* the arm label is removed from the batch and kept in a separate key
  file that the judge never sees;
* the order is shuffled with a fixed, committed seed (20261026): the
  runs are shuffled first, so the items of one run stay together and
  consecutive, and the items inside a run are shuffled afterwards;
* there is one batch entry per (run, qualitative item); the items come
  from the committed checklist (``benchmark/checklists.json``).

The superseded trees are skipped: a quota-interrupted run, the kept
attempts of an infrastructure failure and the driver logs are not runs
of the benchmark, and a directory whose name starts with "_" is
superseded too.

    python benchmark/make_judge_batches.py <run_dir> [<run_dir> ...] --out <batch.json> --key <key.json> [--manifest <manifest.json>] [--seed 20261026]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKLISTS = REPO / "benchmark" / "checklists.json"

# The superseded trees of a run directory: a quota-interrupted run, the
# kept attempts of an infrastructure failure and the driver logs.
SUPERSEDED_DIRS = frozenset({"quota_interrupted", "attempts", "logs"})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def qualitative_items(checklists: dict) -> dict[str, list[dict]]:
    """The qualitative checklist items, per prompt id."""
    items: dict[str, list[dict]] = {}
    for prompt in checklists.get("prompts") or []:
        prompt_id = prompt.get("id")
        if not prompt_id:
            continue
        selected = [
            item
            for item in prompt.get("checklist") or []
            if item.get("kind") == "qualitative"
        ]
        if selected:
            items[str(prompt_id)] = selected
    return items


def _prompt_id_and_repeat(data: dict, run_dir_name: str) -> tuple[str, int | None]:
    """The prompt id and the repeat of a run, from the summary or from
    the run directory's name (``<prompt_id>_r<repeat>``)."""
    prompt_id = data.get("prompt_id") or data.get("id")
    repeat = data.get("repeat")
    stem, _, tail = run_dir_name.rpartition("_r")
    if stem and tail.isdigit():
        prompt_id = prompt_id or stem
        repeat = repeat if repeat is not None else int(tail)
    return (str(prompt_id) if prompt_id is not None else run_dir_name), repeat


def collect_runs(run_dirs: list[Path]) -> list[dict]:
    """Every run of every run directory, the superseded trees skipped."""
    runs: list[dict] = []
    for run_dir in run_dirs:
        base = Path(run_dir)
        if not base.is_dir():
            raise SystemExit(f"the run directory does not exist: {base}")
        for arm_dir in sorted(base.iterdir()):
            if not arm_dir.is_dir():
                continue
            if arm_dir.name in SUPERSEDED_DIRS or arm_dir.name.startswith("_"):
                continue
            for run in sorted(arm_dir.iterdir()):
                summary_path = run / "summary.json"
                if not summary_path.is_file():
                    continue
                data = json.loads(summary_path.read_text(encoding="utf-8"))
                prompt_id, repeat = _prompt_id_and_repeat(data, run.name)
                answer = data.get("final_content") or ""
                runs.append(
                    {
                        "arm": arm_dir.name,
                        "prompt_id": prompt_id,
                        "repeat": repeat,
                        "prompt": data.get("prompt") or "",
                        "answer": answer,
                        "status": data.get("status"),
                        "answer_sha256": _sha256(answer.encode("utf-8")),
                    }
                )
    return runs


def build_batch(
    runs: list[dict], items: dict[str, list[dict]], seed: int
) -> tuple[list[dict], list[dict], list[str]]:
    """The batch, the key and the opaque ids of the runs.

    The runs are shuffled first (the items of one run stay together),
    the items of a run are shuffled afterwards.
    """
    rng = random.Random(seed)
    order = list(runs)
    rng.shuffle(order)

    batch: list[dict] = []
    key: list[dict] = []
    run_ids: list[str] = []
    for run in order:
        selected = list(items.get(run["prompt_id"], []))
        if not selected:
            continue
        opaque = f"run_{len(run_ids) + 1:02d}"
        run_ids.append(opaque)
        rng.shuffle(selected)
        for index, item in enumerate(selected, start=1):
            judge_id = f"{opaque}_item_{index:02d}"
            batch.append(
                {
                    "judge_id": judge_id,
                    "prompt_id": run["prompt_id"],
                    "prompt": run["prompt"],
                    "criterion": item.get("value"),
                    "criterion_note": item.get("note"),
                    "answer": run["answer"],
                }
            )
            key.append(
                {
                    "judge_id": judge_id,
                    "arm": run["arm"],
                    "prompt_id": run["prompt_id"],
                    "repeat": run["repeat"],
                    "item_key": item.get("key"),
                    "status": run["status"],
                    "answer_sha256": run["answer_sha256"],
                }
            )
    return batch, key, run_ids


def _mentions(text: str, arms: set[str]) -> bool:
    lowered = text.lower()
    return any(arm and arm.lower() in lowered for arm in arms)


def arm_leaks(batch: list[dict], arms: set[str]) -> list[str]:
    """The batch's own fields must not carry the arm label."""
    leaks: list[str] = []
    for entry in batch:
        for field, value in entry.items():
            if field == "answer":
                continue
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            if _mentions(text, arms):
                leaks.append(f"{entry['judge_id']}.{field}")
    return leaks


def answers_mentioning_an_arm(batch: list[dict], arms: set[str]) -> int:
    """How many distinct answers carry an arm name in their own text.

    The answer is the answer: it is not masked, so an answer that talks
    about "the baseline" in its own sense says nothing about the arm.
    """
    seen: set[str] = set()
    for entry in batch:
        answer = str(entry.get("answer") or "")
        if _mentions(answer, arms):
            seen.add(_sha256(answer.encode("utf-8")))
    return len(seen)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", nargs="+")
    parser.add_argument("--out", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument(
        "--checklists",
        default=str(CHECKLISTS),
        help="the committed checklist the qualitative items come from",
    )
    args = parser.parse_args()

    checklists_path = Path(args.checklists)
    checklists = json.loads(checklists_path.read_text(encoding="utf-8"))
    items = qualitative_items(checklists)

    run_dirs = [Path(path) for path in args.run_dirs]
    runs = collect_runs(run_dirs)
    batch, key, run_ids = build_batch(runs, items, args.seed)
    if not batch:
        print("no run has a qualitative checklist item; nothing to judge")
        return 1

    arms = {run["arm"] for run in runs}
    leaks = arm_leaks(batch, arms)
    if leaks:
        print(
            "the batch leaks the arm label: " + ", ".join(sorted(set(leaks))[:10]),
            file=sys.stderr,
        )
        return 1

    out_path = Path(args.out)
    key_path = Path(args.key)
    out_path.write_text(json.dumps(batch, indent=2), encoding="utf-8")
    key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")

    prompt_ids = sorted({entry["prompt_id"] for entry in batch})
    if args.manifest:
        manifest = {
            "seed": args.seed,
            "n_runs": len(run_ids),
            "n_runs_found": len(runs),
            "n_items": len(batch),
            "n_prompts": len(prompt_ids),
            "batch_sha256": _sha256(out_path.read_bytes()),
            "key_sha256": _sha256(key_path.read_bytes()),
            "checklists_sha256": _sha256(checklists_path.read_bytes()),
            "checklists": _repo_relative(checklists_path),
            "run_dirs": [_repo_relative(path) for path in run_dirs],
            "prompt_ids": prompt_ids,
        }
        Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"the qualitative judge batch: {len(batch)} items over {len(run_ids)} runs, "
        f"seed {args.seed}"
    )
    print(
        f"  the runs found: {len(runs)} "
        f"({len(run_ids)} of them have a qualitative checklist item)"
    )
    print(f"  the prompts: {len(prompt_ids)}")
    print(f"  the batch: {out_path} (the judge reads this; it carries no arm label)")
    print(f"  the key: {key_path} (the arm labels; the judge does not see this file)")
    if args.manifest:
        print(f"  the manifest: {args.manifest}")
    print(f"  the batch sha256: {_sha256(out_path.read_bytes())}")
    print(f"  the key sha256:   {_sha256(key_path.read_bytes())}")
    mentioning = answers_mentioning_an_arm(batch, arms)
    if mentioning:
        print(
            f"  note: {mentioning} answer bodies carry an arm name in their own "
            f"text; the answer text is the answer and is not masked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

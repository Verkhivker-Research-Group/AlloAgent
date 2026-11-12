"""The share of the checklist items that are correct, per run and per arm.

This is a re-analysis of the 240 runs of the analysis set with the scorer of
``benchmark/score_scripted.py`` as it stands on 2026-11-06, i.e. **after** the
two scorer defects were fixed and **after** the run records and the judge
outputs existed.  Nothing is re-measured, re-run or re-judged here.

For every run it computes the share of the checklist items that are correct,
twice: once with the ``accession_*`` items set aside and once with them
included.  A judged ``not_applicable`` is left out of the denominator; every
other item counts, and an item that is ``missing`` or ``incorrect`` counts
against the share.

It reports the mean share per arm, the paired difference (D minus A) over the
prompts with a bootstrap 95 % interval and a sign-flip p, and the success of
each arm when the pass mark is at least 50 %, 60 %, 75 %, 90 % and 100 % of the
items correct with the Goal Completion full.

    python benchmark/analyze_item_shares.py --judge-outputs <folder> \\
        --key <judge_key.json> --out-dir benchmark/results_scorerfix
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "benchmark"))

_spec = importlib.util.spec_from_file_location(
    "analyze_benchmark", REPO / "benchmark" / "analyze_benchmark.py")
analysis = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analysis)

PROVENANCE = (
    "# PROVENANCE: this file was produced on 2026-11-06, after the data existed. "
    "The two scorer defects of benchmark/score_scripted.py were fixed on 2026-11-06 "
    "and this analysis was run afterwards over the same 240 run records "
    "(2026-10-28 to 2026-11-04) and the same judge outputs (2026-11-03 to "
    "2026-11-05). Nothing was re-measured, re-run or re-judged. The results of "
    "the unfixed scorer are in benchmark/results/."
)

PASS_MARKS = (0.5, 0.6, 0.75, 0.9, 1.0)


def shares_of(run: dict) -> dict:
    """The share of the items that are correct, with and without the accession items."""
    out = {}
    for variant, drop_accession in (("accession_excluded", True), ("accession_included", False)):
        counted = [item for item in run["items"]
                   if item["state"] != "not_applicable"
                   and not (drop_accession and item["accession"])]
        correct = sum(1 for item in counted if item["state"] == "correct")
        out[variant] = {
            "correct": correct,
            "items": len(counted),
            "share": (correct / len(counted)) if counted else None,
            "not_applicable": sum(1 for item in run["items"]
                                   if item["state"] == "not_applicable"),
            "deferred_items": sum(1 for item in run["items"]
                                  if item["kind"] != "qualitative"
                                  and item["state"] == "missing"),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--analysis-set", default=str(analysis.ANALYSIS_SET))
    parser.add_argument("--judge-outputs", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--checklists", default=str(analysis.CHECKLISTS))
    parser.add_argument("--out-dir", default=str(REPO / "benchmark" / "results_scorerfix"))
    parser.add_argument("--bootstrap-seed", type=int, default=analysis.BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-rounds", type=int, default=analysis.BOOTSTRAP_ROUNDS)
    args = parser.parse_args()

    import random

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.bootstrap_seed)

    analysis_set = json.loads(Path(args.analysis_set).read_text(encoding="utf-8"))
    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    checklists = {prompt["id"]: prompt
                  for prompt in json.loads(
                      Path(args.checklists).read_text(encoding="utf-8"))["prompts"]}
    verdicts = analysis.load_judge_verdicts(Path(args.judge_outputs))
    runs = analysis.build_runs(analysis_set, key, verdicts, checklists)

    rows = []
    for run in runs:
        share = shares_of(run)
        rows.append({
            "arm": run["arm"],
            "prompt_id": run["prompt_id"],
            "repeat": run["repeat"],
            "goal_completion": run["goal_completion"],
            "correct_excluded": share["accession_excluded"]["correct"],
            "items_excluded": share["accession_excluded"]["items"],
            "share_excluded": share["accession_excluded"]["share"],
            "correct_included": share["accession_included"]["correct"],
            "items_included": share["accession_included"]["items"],
            "share_included": share["accession_included"]["share"],
            "not_applicable": share["accession_included"]["not_applicable"],
        })

    with (out_dir / "item_shares.csv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(PROVENANCE + "\n")
        writer = csv.writer(handle)
        writer.writerow(["arm", "prompt_id", "repeat", "goal_completion",
                         "correct_accession_excluded", "items_accession_excluded",
                         "share_accession_excluded", "correct_accession_included",
                         "items_accession_included", "share_accession_included",
                         "not_applicable_items"])
        for row in rows:
            writer.writerow([
                row["arm"], row["prompt_id"], row["repeat"], row["goal_completion"],
                row["correct_excluded"], row["items_excluded"],
                round(row["share_excluded"], 4) if row["share_excluded"] is not None else "",
                row["correct_included"], row["items_included"],
                round(row["share_included"], 4) if row["share_included"] is not None else "",
                row["not_applicable"],
            ])

    summary = []
    means = {}
    for variant, key_name in (("accession_excluded", "share_excluded"),
                              ("accession_included", "share_included")):
        for arm in analysis.ARMS:
            values = [row[key_name] for row in rows
                      if row["arm"] == arm and row[key_name] is not None]
            means[(variant, arm)] = sum(values) / len(values) if values else float("nan")

    per_prompt = defaultdict(lambda: defaultdict(list))
    for row in rows:
        for variant, key_name in (("accession_excluded", "share_excluded"),
                                  ("accession_included", "share_included")):
            per_prompt[(variant, row["prompt_id"])][row["arm"]].append(row[key_name])

    differences = {}
    prompt_rows = []
    for variant, key_name in (("accession_excluded", "share_excluded"),
                              ("accession_included", "share_included")):
        diffs = []
        for (v, prompt_id) in sorted(per_prompt):
            if v != variant:
                continue
            arms = per_prompt[(v, prompt_id)]
            d = sum(arms["alloagent"]) / len(arms["alloagent"])
            a = sum(arms["baseline"]) / len(arms["baseline"])
            diffs.append(d - a)
            prompt_rows.append([variant, prompt_id, len(arms["alloagent"]),
                                len(arms["baseline"]), round(d, 4), round(a, 4),
                                round(d - a, 4)])
        differences[variant] = diffs

    with (out_dir / "item_share_difference_by_prompt.csv").open(
            "w", encoding="utf-8", newline="") as handle:
        handle.write(PROVENANCE + "\n")
        writer = csv.writer(handle)
        writer.writerow(["variant", "prompt_id", "runs_D", "runs_A", "share_D",
                         "share_A", "difference"])
        writer.writerows(prompt_rows)

    pass_rows = []
    stats = {}
    for variant, key_name in (("accession_excluded", "share_excluded"),
                              ("accession_included", "share_included")):
        diffs = differences[variant]
        low, high = analysis.bootstrap_ci(diffs, rng, args.bootstrap_rounds)
        sign_p, extreme, method = analysis.exact_sign_flip(diffs, rng)
        mean_difference = sum(diffs) / len(diffs) if diffs else 0.0
        stats[variant] = (mean_difference, low, high, sign_p, method, extreme)
        for mark in PASS_MARKS:
            for arm in analysis.ARMS:
                subset = [row for row in rows if row["arm"] == arm]
                successes = sum(1 for row in subset
                                if row["goal_completion"] == "full"
                                and row[key_name] is not None
                                and row[key_name] >= mark)
                low_w, high_w = analysis.wilson(successes, len(subset))
                pass_rows.append([
                    variant, f"{int(mark * 100)}%", analysis.ARM_LABEL[arm], len(subset),
                    successes, round(successes / len(subset), 4) if subset else "",
                    round(low_w, 4), round(high_w, 4),
                ])

    with (out_dir / "pass_mark_success.csv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(PROVENANCE + "\n")
        writer = csv.writer(handle)
        writer.writerow(["variant", "pass_mark", "arm", "runs", "successes",
                         "success_rate", "wilson_low", "wilson_high"])
        writer.writerows(pass_rows)

    lines = [
        "# The share of the checklist items that are correct",
        "",
        "Computed on 2026-11-06 by `benchmark/analyze_item_shares.py` over the 240 runs",
        "of the analysis set, with the scorer of `benchmark/score_scripted.py` as it",
        "stands on 2026-11-06.",
        "",
        "**This is a re-analysis of data that already existed.** The two scorer",
        "defects were fixed on 2026-11-06; the run records (2026-10-28 to 2026-11-04)",
        "and the judge outputs (2026-11-03 to 2026-11-05) predate the fix and this",
        "analysis. Nothing was re-measured, re-run or re-judged.",
        "",
        "## What the share counts",
        "",
        "The denominator is the checklist items of the run that are not judged",
        "*not_applicable*; a judged *not_applicable* is left out. Every other item",
        "counts, and an item that is *missing* or *incorrect* counts against the",
        "share. The `accession_excluded` variant sets the `accession_*` items aside;",
        "the `accession_included` variant keeps them. An item the scorer deferred",
        "(a `DEFERRED` verdict) counts as not correct.",
        "",
        "## The mean share per arm",
        "",
        "| variant | arm D (alloagent) | arm A (baseline) | D - A | bootstrap 95 % | sign-flip p |",
        "|---|---|---|---:|---|---|",
    ]
    for variant in ("accession_excluded", "accession_included"):
        mean_difference, low, high, sign_p, method, extreme = stats[variant]
        lines.append(
            f"| {variant} | {means[(variant, 'alloagent')]:.4f} | "
            f"{means[(variant, 'baseline')]:.4f} | {mean_difference:+.4f} | "
            f"[{low:.4f}, {high:.4f}] | {sign_p:.4f} ({method}) |")
    lines += [
        "",
        "The bootstrap is over the 40 per-prompt differences (the mean over the three",
        "repeats of each arm), the seed 20261027 and 5000 rounds; the sign-flip test is",
        "the same one `benchmark/analyze_benchmark.py` uses.",
        "",
        "## The success at each pass mark",
        "",
        "A run passes when the Goal Completion is `full` and the share of the items",
        "that are correct is at least the pass mark.",
        "",
        "| variant | pass mark | arm | runs | successes | success rate | Wilson 95 % |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in pass_rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | "
                     f"{row[5]} | [{row[6]}, {row[7]}] |")
    lines += [
        "",
        "## The files",
        "",
        "| file | what it holds |",
        "|---|---|",
        "| `item_shares.csv` | the share of every run, with and without the accession items |",
        "| `item_share_difference_by_prompt.csv` | the per-prompt shares of both arms and their difference |",
        "| `pass_mark_success.csv` | the success of each arm at each pass mark |",
        "| `item_shares_summary.md` | this file |",
        "",
    ]
    (out_dir / "item_shares_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"the runs analysed: {len(rows)}")
    print("the files written: item_shares.csv, item_share_difference_by_prompt.csv, "
          "pass_mark_success.csv, item_shares_summary.md")
    for variant in ("accession_excluded", "accession_included"):
        mean_difference, low, high, sign_p, method, extreme = stats[variant]
        print(f"  {variant}: mean D {means[(variant, 'alloagent')]:.4f}  "
              f"mean A {means[(variant, 'baseline')]:.4f}  difference {mean_difference:+.4f}  "
              f"CI [{low:.4f}, {high:.4f}]  sign-flip p {sign_p:.4f} ({method})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

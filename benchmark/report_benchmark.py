"""The result tables of a benchmark scenario.

This script reads the run records of a scenario (the same layout the
analysis plan fixes: ``<run_dir>/<arm>/<prompt>_r<repeat>/summary.json``),
scores every answer against the committed checklists with
``benchmark/score_scripted.py``, and writes the tables the plan asks for:

* the per-run and per-arm aggregate (runs, completed, failed, dirty, tokens,
  wall time);
* the per-prompt table (the scripted items passed, the verdict, the mean
  tokens and the mean wall time, per arm);
* the per-category and per-tier aggregate;
* the **success-versus-budget curve** - the primary presentation of the
  cost-constrained endpoint (the plan's dated note 2026-10-26, item 3):
  the rate of runs that complete within a token budget, and the rate of
  runs that complete **and** carry a non-empty scripted answer within that
  budget, over the whole range of budgets, with the committed
  1,000,000-token and 1800-second thresholds marked;
* the bootstrap confidence intervals over the runs (the committed bootstrap
  seed 20261027).

The **accession items** (the ``accession_*`` items of every prompt) are
reported separately: they ask the answer to restate the UniProt protein
name, the gene symbol and the organism, and most prompts already give the
accession in the prompt text, so the item measures a naming convention
rather than the scientific content.  The tables below therefore report the
scripted score both with and without those items.  Nothing is hidden and
nothing is re-weighted: the "with" column is the committed criterion.

    python benchmark/report_benchmark.py <run_dir> [<run_dir> ...]
        [--scenario NAME] [--out <tables.md>] [--json <tables.json>]
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from score_scripted import find_runs, load_checklists, score_answer

REPO = Path(__file__).resolve().parents[1]
CHECKLISTS = REPO / "benchmark" / "checklists.json"

ARM_LABELS = {"alloagent": "D (alloagent)", "baseline": "A (baseline)"}
BOOTSTRAP_SEED = 20261027
TOKEN_THRESHOLD = 1_000_000
WALL_THRESHOLD = 1800.0


def bootstrap_rate(flags: list[float], seed: int, rounds: int = 2000) -> tuple[float, float, float]:
    if not flags:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    samples = []
    for _ in range(rounds):
        draw = [rng.choice(flags) for _ in flags]
        samples.append(sum(draw) / len(draw))
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return sum(flags) / len(flags), low, high


def load_scenario(run_dir: Path, checklists: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    for arm, run_path in find_runs(run_dir):
        summary = json.loads((run_path / "summary.json").read_text(encoding="utf-8"))
        prompt_id = summary.get("prompt_id") or summary.get("id") or run_path.name.split("_r")[0]
        checklist = checklists.get(prompt_id)
        tokens = summary.get("token_total") or {}
        row = {
            "arm": arm,
            "run": run_path.name,
            "prompt_id": prompt_id,
            "repeat": summary.get("repeat"),
            "status": summary.get("status"),
            "steps": summary.get("n_steps"),
            "wall_time_s": summary.get("wall_time_s"),
            "tokens": tokens,
            "total_tokens": int(tokens.get("total_tokens") or 0),
            "dirty": summary.get("git_dirty"),
            "error": summary.get("error"),
        }
        if checklist is None:
            row.update(
                {
                    "verdict": "NO_CHECKLIST",
                    "scripted_items": 0,
                    "scripted_passed": 0,
                    "deferred_items": 0,
                    "items": [],
                }
            )
        else:
            scored = score_answer(summary, checklist)
            row.update(scored)
        row["substantive_items"] = sum(
            1 for item in row["items"] if not item["key"].startswith("accession_")
        )
        row["substantive_passed"] = sum(
            1
            for item in row["items"]
            if not item["key"].startswith("accession_") and item["verdict"] == "PASS"
        )
        rows.append(row)
    return rows


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def fmt(value, digits: int = 3) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.{digits}f}"
    return f"{value:,}"


def budget_curve(rows: list[dict], budgets: list[float], field: str) -> list[tuple[float, float, float]]:
    """The share of the runs that complete within the budget, and the share
    that complete within it and carry a non-empty scripted answer.

    The denominator is **every** run of the arm: a run that did not complete
    and a run that went over the budget are both not a success (the plan's
    cost-constrained endpoint).
    """
    curve = []
    for budget in budgets:
        completed = []
        with_answer = []
        for row in rows:
            value = row[field]
            inside = (
                row["status"] == "completed"
                and value is not None
                and value <= budget
            )
            completed.append(1.0 if inside else 0.0)
            with_answer.append(1.0 if inside and row["scripted_passed"] > 0 else 0.0)
        rate = sum(completed) / len(completed) if completed else 0.0
        answer_rate = sum(with_answer) / len(with_answer) if with_answer else 0.0
        curve.append((budget, rate, answer_rate))
    return curve


def markdown_tables(rows: list[dict], scenario: str) -> str:
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    meta = {prompt["id"]: prompt for prompt in checklists["prompts"]}
    arms = sorted({row["arm"] for row in rows})
    lines: list[str] = []
    lines.append(f"## The scenario: {scenario}")
    lines.append("")

    lines.append("### The aggregate")
    lines.append("")
    lines.append("| arm | runs | completed | failed | dirty | tokens (total) | mean tokens | mean wall (s) | scripted items passed | substantive items passed |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        completed = [row for row in arm_rows if row["status"] == "completed"]
        tokens = [row["total_tokens"] for row in arm_rows]
        walls = [row["wall_time_s"] for row in arm_rows if row["wall_time_s"] is not None]
        scripted = sum(row["scripted_items"] for row in arm_rows)
        passed = sum(row["scripted_passed"] for row in arm_rows)
        substantive = sum(row["substantive_items"] for row in arm_rows)
        substantive_passed = sum(row["substantive_passed"] for row in arm_rows)
        lines.append(
            f"| {ARM_LABELS.get(arm, arm)} | {len(arm_rows)} | {len(completed)} | "
            f"{len(arm_rows) - len(completed)} | {sum(1 for row in arm_rows if row['dirty'])} | "
            f"{sum(tokens):,} | {fmt(mean(tokens), 0)} | {fmt(mean(walls), 1)} | "
            f"{passed}/{scripted} | {substantive_passed}/{substantive} |"
        )
    lines.append("")

    lines.append("### The verdicts")
    lines.append("")
    lines.append("| arm | FULL | PARTIAL | NONE | FAIL | deferred items |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        counts = {}
        for row in arm_rows:
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        deferred = sum(row["deferred_items"] for row in arm_rows)
        lines.append(
            f"| {ARM_LABELS.get(arm, arm)} | {counts.get('FULL', 0)} | "
            f"{counts.get('PARTIAL', 0)} | {counts.get('NONE', 0)} | "
            f"{counts.get('FAIL', 0)} | {deferred} |"
        )
    lines.append("")
    lines.append(
        "The verdict is the **scripted** verdict: FULL when every scriptable "
        "checklist item of the prompt is present in the answer, PARTIAL when "
        "some are, NONE when none is, FAIL when the run did not complete. "
        "The qualitative items (the ones the committed plan sends to the judge "
        "and to the human subset) are **deferred**: they are counted neither "
        "as a pass nor as a failure."
    )
    lines.append("")

    lines.append("### The per-prompt table")
    lines.append("")
    header = "| prompt | category | tier |"
    for arm in arms:
        header += f" {ARM_LABELS.get(arm, arm)} scripted | {ARM_LABELS.get(arm, arm)} mean tokens |"
    lines.append(header)
    lines.append("|---|---|---|" + "---|" * (2 * len(arms)))
    prompt_ids = sorted({row["prompt_id"] for row in rows})
    for prompt_id in prompt_ids:
        prompt_meta = meta.get(prompt_id, {})
        line = f"| {prompt_id} | {prompt_meta.get('category', '-')} | {prompt_meta.get('tier', '-')} |"
        for arm in arms:
            arm_rows = [row for row in rows if row["arm"] == arm and row["prompt_id"] == prompt_id]
            scripted = sum(row["scripted_items"] for row in arm_rows)
            passed = sum(row["scripted_passed"] for row in arm_rows)
            tokens = [row["total_tokens"] for row in arm_rows]
            line += f" {passed}/{scripted} | {fmt(mean(tokens), 0)} |"
        lines.append(line)
    lines.append("")

    lines.append("### The per-category aggregate")
    lines.append("")
    lines.append("| category | arm | runs | scripted items passed | substantive items passed | mean tokens |")
    lines.append("|---|---|---:|---:|---:|---:|")
    categories = sorted({meta.get(row["prompt_id"], {}).get("category", "-") for row in rows})
    for category in categories:
        for arm in arms:
            arm_rows = [
                row
                for row in rows
                if row["arm"] == arm and meta.get(row["prompt_id"], {}).get("category", "-") == category
            ]
            if not arm_rows:
                continue
            scripted = sum(row["scripted_items"] for row in arm_rows)
            passed = sum(row["scripted_passed"] for row in arm_rows)
            substantive = sum(row["substantive_items"] for row in arm_rows)
            substantive_passed = sum(row["substantive_passed"] for row in arm_rows)
            tokens = [row["total_tokens"] for row in arm_rows]
            lines.append(
                f"| {category} | {ARM_LABELS.get(arm, arm)} | {len(arm_rows)} | "
                f"{passed}/{scripted} | {substantive_passed}/{substantive} | {fmt(mean(tokens), 0)} |"
            )
    lines.append("")

    lines.append("### The success-versus-budget curve")
    lines.append("")
    lines.append(
        "The plan's primary presentation of the cost-constrained endpoint: the "
        "share of the runs that **complete within** the budget, and the share "
        "that complete within it **and** carry a non-empty scripted answer. "
        "The budgets are computed from the records; they were never enforced "
        "by killing a run."
    )
    lines.append("")
    token_budgets = [
        100_000, 250_000, 500_000, 750_000, 1_000_000, 1_500_000, 2_000_000,
        3_000_000, 5_000_000, 8_000_000, 12_000_000, 20_000_000,
    ]
    wall_budgets = [
        120, 240, 360, 600, 900, 1200, 1800, 2400, 3600, 5400, 7200,
    ]
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        lines.append(f"**{ARM_LABELS.get(arm, arm)} - the token budget**")
        lines.append("")
        lines.append("| token budget | completed within | with a non-empty scripted answer |")
        lines.append("|---:|---:|---:|")
        for budget, rate, answer_rate in budget_curve(arm_rows, token_budgets, "total_tokens"):
            mark = " **(the committed threshold)**" if budget == TOKEN_THRESHOLD else ""
            lines.append(f"| {budget:,}{mark} | {rate:.3f} | {answer_rate:.3f} |")
        lines.append("")
        lines.append(f"**{ARM_LABELS.get(arm, arm)} - the wall-clock budget**")
        lines.append("")
        lines.append("| wall budget (s) | completed within | with a non-empty scripted answer |")
        lines.append("|---:|---:|---:|")
        for budget, rate, answer_rate in budget_curve(arm_rows, wall_budgets, "wall_time_s"):
            mark = " **(the committed threshold)**" if budget == WALL_THRESHOLD else ""
            lines.append(f"| {budget:.0f}{mark} | {rate:.3f} | {answer_rate:.3f} |")
        lines.append("")

    lines.append("### The committed thresholds")
    lines.append("")
    lines.append("| arm | within 1,000,000 tokens and 1800 s | bootstrap 95 % CI | within budget with a non-empty scripted answer | bootstrap 95 % CI |")
    lines.append("|---|---:|---|---:|---|")
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        flags = [
            1.0
            if (
                row["status"] == "completed"
                and row["total_tokens"] <= TOKEN_THRESHOLD
                and (row["wall_time_s"] or 0.0) <= WALL_THRESHOLD
            )
            else 0.0
            for row in arm_rows
        ]
        answer_flags = [
            1.0
            if (
                row["status"] == "completed"
                and row["total_tokens"] <= TOKEN_THRESHOLD
                and (row["wall_time_s"] or 0.0) <= WALL_THRESHOLD
                and row["scripted_passed"] > 0
            )
            else 0.0
            for row in arm_rows
        ]
        rate, low, high = bootstrap_rate(flags, BOOTSTRAP_SEED)
        answer_rate, answer_low, answer_high = bootstrap_rate(answer_flags, BOOTSTRAP_SEED)
        lines.append(
            f"| {ARM_LABELS.get(arm, arm)} | {rate:.3f} | [{low:.3f}, {high:.3f}] | "
            f"{answer_rate:.3f} | [{answer_low:.3f}, {answer_high:.3f}] |"
        )
    lines.append("")
    lines.append(
        f"The bootstrap seed is {BOOTSTRAP_SEED} (the committed one) and the "
        "intervals are over the runs of that arm."
    )
    lines.append("")

    lines.append("### The scripted pass rate")
    lines.append("")
    lines.append("| arm | scripted items passed | bootstrap 95 % CI | substantive items passed (the accession items excluded) | bootstrap 95 % CI |")
    lines.append("|---|---:|---|---:|---|")
    for arm in arms:
        arm_rows = [row for row in rows if row["arm"] == arm]
        flags = [
            1.0 if row["scripted_passed"] == row["scripted_items"] else 0.0
            for row in arm_rows
            if row["scripted_items"]
        ]
        substantive_flags = [
            1.0 if row["substantive_passed"] == row["substantive_items"] else 0.0
            for row in arm_rows
            if row["substantive_items"]
        ]
        rate, low, high = bootstrap_rate(flags, BOOTSTRAP_SEED)
        substantive_rate, substantive_low, substantive_high = bootstrap_rate(
            substantive_flags, BOOTSTRAP_SEED
        )
        lines.append(
            f"| {ARM_LABELS.get(arm, arm)} | {rate:.3f} | [{low:.3f}, {high:.3f}] | "
            f"{substantive_rate:.3f} | [{substantive_low:.3f}, {substantive_high:.3f}] |"
        )
    lines.append("")
    lines.append(
        "The rate is the share of the runs in which **every** scriptable item "
        "of the prompt is present. The intervals are over the runs of that arm."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", nargs="+")
    parser.add_argument("--scenario", default="the scenario")
    parser.add_argument("--out")
    parser.add_argument("--json")
    args = parser.parse_args()

    checklists = load_checklists()
    rows: list[dict] = []
    for run_dir in args.run_dirs:
        rows.extend(load_scenario(Path(run_dir), checklists))

    tables = markdown_tables(rows, args.scenario)
    if args.out:
        Path(args.out).write_text(tables + "\n", encoding="utf-8")
    print(tables)
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

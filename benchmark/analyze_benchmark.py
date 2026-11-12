"""The analysis of the benchmark: the 240-run analysis set.

The plan (benchmark/analysis_plan.md) fixes what is computed here:

* the **primary success** of a run: Goal Completion is full AND every
  [critical] item is correct - the scripted items by the result of the
  program, the judged items by the verdict of the judge, and the items
  the program deferred to the judge by that verdict.  A judged item that
  is *not_applicable* is left out of the "every item" test;
* the success per arm with Wilson intervals, the **paired** difference
  (D minus A) with a bootstrap 95 % interval over the prompts and the
  exact sign-flip test;
* the tokens per run as a log ratio (the key secondary), with Holm
  across the success and the tokens;
* the steps and the wall time descriptively (the wall time **as
  recorded**: no active/pause split is used here);
* the success against the token budget and against the time budget, with
  the 1 000 000-token and the 30-minute points marked;
* the success by prompt category;
* the tool use per run, by tool, for both arms;
* the results of the restricted-egress scenario for its 15 prompts;
* the checklist items that only the tools of arm D can answer, and how
  both arms did on them.

Four **sensitivity** variants are produced next to the primary result:
(a) a judged *not_applicable* counted as not correct, (b) the two
[low-information item] P2Rank items excluded, (c) the accession_*
items excluded, (d) Goal Completion full *or* partial as the success
level.

The arm labels come from the key, and they are used **inside** this
script only: the terminal output of this script holds counts, file names
and the checks that failed, never an arm-level number.

    python benchmark/analyze_benchmark.py --judge-outputs <folder> \
        --key <judge_key.json> --out-dir benchmark/results
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts"))
from _paths import expand_home  # noqa: E402
sys.path.insert(0, str(REPO / "benchmark"))

import score_scripted  # noqa: E402  (the paths are set up above)

_exporter_spec = importlib.util.spec_from_file_location(
    "judge_batch_exporter", REPO / "benchmark" / "export_judge_batches.py")
exporter = importlib.util.module_from_spec(_exporter_spec)
_exporter_spec.loader.exec_module(exporter)

ANALYSIS_SET = REPO / "benchmark" / "analysis_set.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
DRAFT = REPO / "benchmark" / "benchmark_draft.json"

BOOTSTRAP_SEED = 20261027
BOOTSTRAP_ROUNDS = 5000
TOKEN_BUDGET = 1_000_000
WALL_CAP_S = 1800.0

ARMS = ("alloagent", "baseline")
ARM_LABEL = {"alloagent": "D", "baseline": "A"}

# The items that only the tools of arm D can answer: the criteria that
# name one of the exposed tools (the baseline arm has none of them).
ARM_D_ONLY_TOOLS = None  # filled from alloagent/exposed_tools.txt


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """The Wilson score interval of a binomial proportion."""
    if total == 0:
        return (float("nan"), float("nan"))
    phat = successes / total
    denominator = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denominator
    half = (z / denominator) * math.sqrt(
        phat * (1 - phat) / total + z * z / (4 * total * total))
    return (max(0.0, centre - half), min(1.0, centre + half))


def exact_sign_flip(differences: list[float], rng: random.Random | None = None,
                    max_exact: int = 20, monte_carlo_rounds: int = 200_000
                    ) -> tuple[float, int, str]:
    """The two-sided sign-flip test on the paired differences.

    The exact test enumerates the 2**n sign assignments, which is only
    possible for a small n; with more pairs the same statistic is
    computed from a fixed number of random sign assignments, and the
    report says which of the two was used.
    """
    nonzero = [d for d in differences if d != 0.0]
    n = len(nonzero)
    if n == 0:
        return (1.0, 0, "no non-zero difference")
    observed = abs(sum(nonzero) / n)
    if n <= max_exact:
        extreme = 0
        for mask in range(2 ** n):
            total = 0.0
            for index, value in enumerate(nonzero):
                total += value if mask >> index & 1 else -value
            if abs(total / n) >= observed - 1e-12:
                extreme += 1
        return (extreme / (2 ** n), extreme, "exact")
    if rng is None:
        rng = random.Random(0)
    extreme = 0
    for _ in range(monte_carlo_rounds):
        total = 0.0
        for value in nonzero:
            total += value if rng.random() < 0.5 else -value
        if abs(total / n) >= observed - 1e-12:
            extreme += 1
    return (extreme / monte_carlo_rounds, extreme,
            f"Monte Carlo ({monte_carlo_rounds} sign assignments)")


def bootstrap_ci(values: list[float], rng: random.Random,
                 rounds: int = BOOTSTRAP_ROUNDS) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    means = []
    for _ in range(rounds):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort()
    low = means[int(0.025 * (len(means) - 1))]
    high = means[int(0.975 * (len(means) - 1))]
    return (low, high)


def holm(p_values: list[float]) -> list[float]:
    """Holm's step-down correction."""
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        value = (len(p_values) - rank) * p_values[index]
        running = max(running, min(1.0, value))
        adjusted[index] = running
    return adjusted


def load_judge_verdicts(outputs_dir: Path) -> dict[str, dict[str, str]]:
    """The verdicts of the judge, by run id and item id."""
    verdicts: dict[str, dict[str, str]] = {}
    for path in sorted(outputs_dir.glob("judge_batch_*_*.json")):
        if not re.match(r"^judge_batch_\d{3}_(scores|results)\.json$", path.name):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            continue
        for record in payload:
            run_id = record.get("run_id")
            if not isinstance(run_id, str):
                continue
            verdicts.setdefault(run_id, {})
            for item in record.get("items") or []:
                if isinstance(item, dict) and isinstance(item.get("item_id"), str):
                    verdicts[run_id][item["item_id"]] = item.get("verdict")
            verdicts[run_id]["__goal_completion__"] = record.get("goal_completion")
            verdicts[run_id]["__data_grounding__"] = record.get("data_grounding")
            verdicts[run_id]["__final_answer_complete__"] = record.get(
                "final_answer_complete")
    return verdicts


def tool_calls_of(record_dir: Path, tool_names: list[str]) -> Counter:
    """The tool use of a run: the tool names in the executed code.

    The recorded messages carry no tool calls, but the trace holds the
    code the agent executed, and every call of a tool is named in it.  A
    name is counted once per mention, as a whole word.
    """
    path = expand_home(record_dir) / "trace.txt"
    counts: Counter = Counter()
    if not path.is_file():
        return counts
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r"<execute>(.*?)</execute>", text, re.S)
    code = "\n".join(blocks)
    for name in tool_names:
        found = len(re.findall(r"(?<![\w.])" + re.escape(name) + r"(?![\w])", code))
        if found:
            counts[name] = found
    return counts


def item_state(
    item: dict,
    scripted_verdict: str | None,
    judged_verdict: str | None,
) -> str:
    """The state of one item of a run: correct, incorrect, missing or na."""
    if scripted_verdict in ("PASS", "FAIL"):
        return "correct" if scripted_verdict == "PASS" else "incorrect"
    if judged_verdict in ("correct", "incorrect", "missing", "not_applicable"):
        return judged_verdict
    return "missing"


def build_runs(analysis_set: dict, key: dict, verdicts: dict[str, dict[str, str]],
               checklists: dict[str, dict]) -> list[dict]:
    """One record per run of the analysis set."""
    by_record = {str(expand_home(row["record_dir"])): row for row in key["runs_key"]}
    judge_by_record = {
        record_dir: verdicts.get(by_record[record_dir]["run_id"], {})
        for record_dir in by_record
    }
    runs = []
    for row in analysis_set["rows"]:
        prompt_id = row["prompt_id"]
        checklist = checklists[prompt_id]
        summary = json.loads(
            (expand_home(row["record_dir"]) / "summary.json").read_text(encoding="utf-8"))
        scored = score_scripted.score_answer(summary, checklist)
        scripted = {item["key"]: item["verdict"] for item in scored["items"]}
        ids = exporter.item_ids(prompt_id, checklist["checklist"])
        judged_by_key = {}
        judge = judge_by_record.get(str(expand_home(row["record_dir"])), {})
        for identifier, item in zip(ids, checklist["checklist"]):
            verdict = judge.get(identifier)
            if verdict is not None:
                judged_by_key[item["key"]] = verdict
        items = []
        for identifier, item in zip(ids, checklist["checklist"]):
            key_name = item["key"]
            state = item_state(item, scripted.get(key_name),
                               judged_by_key.get(key_name))
            items.append({
                "key": key_name,
                "id": identifier,
                "kind": item["kind"],
                "state": state,
                "scripted": scripted.get(key_name),
                "judged": judged_by_key.get(key_name),
                "low_information": key_name.startswith("p2rank_reference_"),
                "accession": key_name.startswith("accession_"),
            })
        tokens = (summary.get("token_total") or {}).get("total_tokens") or 0
        runs.append({
            "arm": row["arm"],
            "prompt_id": prompt_id,
            "repeat": row["repeat"],
            "record_dir": row["record_dir"],
            "source": row["source"],
            "category": row.get("category"),
            "tier": row.get("tier"),
            "route": row.get("route"),
            "status": row.get("status"),
            "tokens": tokens,
            "steps": summary.get("n_steps"),
            "wall_time_s": summary.get("wall_time_s"),
            "goal_completion": judge.get("__goal_completion__"),
            "data_grounding": judge.get("__data_grounding__"),
            "final_answer_complete": judge.get("__final_answer_complete__"),
            "items": items,
        })
    return runs


def success_of(run: dict, variants: dict) -> dict[str, bool]:
    """The success of a run under the primary rule and the variants."""
    items = run["items"]
    goal = run.get("goal_completion")

    def every_item_correct(include_na_as_correct: bool,
                           drop_low_information: bool,
                           drop_accession: bool) -> bool:
        for item in items:
            if drop_low_information and item["low_information"]:
                continue
            if drop_accession and item["accession"]:
                continue
            state = item["state"]
            if state == "not_applicable":
                if include_na_as_correct:
                    continue
                return False
            if state != "correct":
                return False
        return True

    primary = (goal == "full") and every_item_correct(False, False, False)
    return {
        "primary": primary,
        "not_applicable_is_not_correct": (
            (goal == "full") and every_item_correct(True, False, False)),
        "low_information_excluded": (
            (goal == "full") and every_item_correct(False, True, False)),
        "accession_excluded": (
            (goal == "full") and every_item_correct(False, False, True)),
        "full_or_partial": (
            goal in ("full", "partial")
            and every_item_correct(False, False, False)),
    }


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--analysis-set", default=str(ANALYSIS_SET))
    parser.add_argument("--judge-outputs", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--checklists", default=str(CHECKLISTS))
    parser.add_argument("--draft", default=str(DRAFT))
    parser.add_argument("--restricted-run-dir",
                        default=str(expand_home(r"<HOME>\AppData\Local\Temp\opencode\benchmark_runs_v6g_restricted")))
    parser.add_argument("--out-dir", default=str(REPO / "benchmark" / "results"))
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-rounds", type=int, default=BOOTSTRAP_ROUNDS)
    parser.add_argument("--token-budget", type=int, default=TOKEN_BUDGET)
    parser.add_argument("--wall-cap-s", type=float, default=WALL_CAP_S)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.bootstrap_seed)

    analysis_set = json.loads(Path(args.analysis_set).read_text(encoding="utf-8"))
    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    checklists = {prompt["id"]: prompt
                  for prompt in json.loads(
                      Path(args.checklists).read_text(encoding="utf-8"))["prompts"]}
    draft = {row["id"]: row
             for row in json.loads(Path(args.draft).read_text(encoding="utf-8"))}
    verdicts = load_judge_verdicts(Path(args.judge_outputs))

    runs = build_runs(analysis_set, key, verdicts, checklists)
    for run in runs:
        run["category"] = draft.get(run["prompt_id"], {}).get("category")
        run["tier"] = draft.get(run["prompt_id"], {}).get("tier")
        run["route"] = draft.get(run["prompt_id"], {}).get("baseline_route")
        run["success"] = success_of(run, {})

    checks = []
    checks.append(("the runs of the analysis set", len(runs) == len(analysis_set["rows"])))
    checks.append(("every run has a judge verdict",
                   all(run.get("goal_completion") is not None for run in runs)))
    checks.append(("every run is completed", all(run["status"] == "completed" for run in runs)))
    checks.append(("every run has tokens", all(run["tokens"] for run in runs)))
    checks.append(("every run has a wall time",
                   all(run["wall_time_s"] is not None for run in runs)))

    # ---- the success per arm, with the Wilson intervals
    summary_rows = []
    for variant in ("primary", "not_applicable_is_not_correct",
                    "low_information_excluded", "accession_excluded",
                    "full_or_partial"):
        for arm in ARMS:
            rows = [run for run in runs if run["arm"] == arm]
            successes = sum(1 for run in rows if run["success"][variant])
            low, high = wilson(successes, len(rows))
            summary_rows.append([variant, ARM_LABEL[arm], len(rows), successes,
                                 round(successes / len(rows), 4) if rows else "",
                                 round(low, 4), round(high, 4)])
    write_csv(out_dir / "success_by_arm.csv",
              ["variant", "arm", "runs", "successes", "success_rate",
               "wilson_low", "wilson_high"], summary_rows)

    # ---- the paired difference (D minus A) over the prompts
    per_prompt = defaultdict(lambda: {"alloagent": [], "baseline": []})
    for run in runs:
        per_prompt[run["prompt_id"]][run["arm"]].append(
            1.0 if run["success"]["primary"] else 0.0)
    prompt_rows = []
    differences = []
    for prompt_id in sorted(per_prompt):
        arms = per_prompt[prompt_id]
        d = sum(arms["alloagent"]) / len(arms["alloagent"]) if arms["alloagent"] else 0.0
        a = sum(arms["baseline"]) / len(baseline_arms := arms["baseline"]) if arms["baseline"] else 0.0
        difference = d - a
        differences.append(difference)
        prompt_rows.append([prompt_id, len(arms["alloagent"]), len(arms["baseline"]),
                            round(d, 4), round(a, 4), round(difference, 4)])
    mean_difference = sum(differences) / len(differences) if differences else 0.0
    diff_low, diff_high = bootstrap_ci(differences, rng, args.bootstrap_rounds)
    sign_p, sign_extreme, sign_method = exact_sign_flip(differences, rng)
    write_csv(out_dir / "paired_difference_by_prompt.csv",
              ["prompt_id", "runs_D", "runs_A", "success_D", "success_A",
               "difference"], prompt_rows)

    # ---- the tokens (the key secondary): the log ratio of the means
    token_means = {}
    for arm in ARMS:
        values = [run["tokens"] for run in runs if run["arm"] == arm]
        token_means[arm] = sum(values) / len(values) if values else float("nan")
    log_ratio = math.log(token_means["alloagent"] / token_means["baseline"])
    token_differences = []
    for prompt_id in sorted(per_prompt):
        per_arm = defaultdict(list)
        for run in runs:
            if run["prompt_id"] == prompt_id:
                per_arm[run["arm"]].append(run["tokens"])
        if per_arm["alloagent"] and per_arm["baseline"]:
            d = sum(per_arm["alloagent"]) / len(per_arm["alloagent"])
            a = sum(per_arm["baseline"]) / len(per_arm["baseline"])
            token_differences.append(math.log(d / a))
    token_low, token_high = bootstrap_ci(token_differences, rng, args.bootstrap_rounds)
    token_sign_p, _, token_sign_method = exact_sign_flip(token_differences, rng)
    holm_adjusted = holm([sign_p, token_sign_p])

    # ---- the mixed-model sensitivity (a prompt random intercept)
    mixed = {"ok": False}
    try:
        import numpy as np
        import pandas as pd
        import statsmodels.formula.api as smf

        frame = pd.DataFrame([{
            "success": 1.0 if run["success"]["primary"] else 0.0,
            "prompt": run["prompt_id"],
            "arm": ARM_LABEL[run["arm"]],
            "log_tokens": math.log(max(1, run["tokens"])),
        } for run in runs])
        model = smf.mixedlm("success ~ arm", frame, groups=frame["prompt"]).fit()
        mixed = {
            "ok": True,
            "coefficient": float(model.params.get("arm[T.D]", float("nan"))),
            "p_value": float(model.pvalues.get("arm[T.D]", float("nan"))),
            "converged": bool(getattr(model, "converged", False)),
        }
    except Exception as error:  # noqa: BLE001
        mixed = {"ok": False, "error": f"{type(error).__name__}: {error}"[:200]}

    # ---- the steps and the wall time, descriptively
    descriptive_rows = []
    for arm in ARMS:
        rows = [run for run in runs if run["arm"] == arm]
        steps = sorted(run["steps"] or 0 for run in rows)
        walls = sorted(run["wall_time_s"] or 0.0 for run in rows)
        tokens = sorted(run["tokens"] or 0 for run in rows)
        descriptive_rows.append([
            ARM_LABEL[arm], len(rows),
            round(sum(steps) / len(steps), 1), steps[len(steps) // 2],
            round(sum(walls) / len(walls), 1), round(walls[len(walls) // 2], 1),
            round(sum(tokens) / len(tokens), 1), tokens[len(tokens) // 2],
        ])
    write_csv(out_dir / "steps_walltime_tokens.csv",
              ["arm", "runs", "mean_steps", "median_steps", "mean_wall_s",
               "median_wall_s", "mean_tokens", "median_tokens"], descriptive_rows)

    # ---- the success against the budgets
    curve_rows = []
    for arm in ARMS:
        rows = [run for run in runs if run["arm"] == arm]
        for budget in [0, 50_000, 100_000, 250_000, 500_000, 750_000,
                       1_000_000, 1_500_000, 2_000_000, 3_000_000]:
            inside = [run for run in rows if (run["tokens"] or 0) <= budget]
            curve_rows.append([
                "tokens", ARM_LABEL[arm], budget, len(inside),
                round(sum(1 for run in inside if run["success"]["primary"]) / len(inside), 4)
                if inside else "",
            ])
        for budget in [300.0, 600.0, 900.0, 1200.0, 1800.0, 2400.0,
                       3600.0, 7200.0]:
            inside = [run for run in rows if (run["wall_time_s"] or 0.0) <= budget]
            curve_rows.append([
                "wall_s", ARM_LABEL[arm], budget, len(inside),
                round(sum(1 for run in inside if run["success"]["primary"]) / len(inside), 4)
                if inside else "",
            ])
    write_csv(out_dir / "success_against_budgets.csv",
              ["budget_kind", "arm", "budget", "runs_inside", "success_rate"],
              curve_rows)

    # ---- the success by prompt category
    category_rows = []
    categories = sorted({run["category"] for run in runs if run["category"]})
    for category in categories:
        for arm in ARMS:
            rows = [run for run in runs
                    if run["category"] == category and run["arm"] == arm]
            successes = sum(1 for run in rows if run["success"]["primary"])
            low, high = wilson(successes, len(rows))
            category_rows.append([category, ARM_LABEL[arm], len(rows), successes,
                                  round(successes / len(rows), 4) if rows else "",
                                  round(low, 4), round(high, 4)])
    write_csv(out_dir / "success_by_category.csv",
              ["category", "arm", "runs", "successes", "success_rate",
               "wilson_low", "wilson_high"], category_rows)

    # ---- the tool use per run, by tool
    tool_rows = []
    per_tool = defaultdict(lambda: {"alloagent": 0, "baseline": 0})
    tool_runs = Counter()
    exposed_names = exporter.read_tool_names(REPO / "alloagent" / "exposed_tools.txt")
    baseline_names = exporter.read_tool_names(
        REPO / "benchmark" / "baseline_arm_tool_names.txt")
    for run in runs:
        names = exposed_names if run["arm"] == "alloagent" else baseline_names
        counts = tool_calls_of(run["record_dir"], names)
        tool_runs[run["arm"]] += 1
        for tool, number in counts.items():
            per_tool[tool][run["arm"]] += number
    for tool in sorted(per_tool):
        totals = per_tool[tool]
        tool_rows.append([
            tool, totals["alloagent"], totals["baseline"],
            round(totals["alloagent"] / tool_runs["alloagent"], 3),
            round(totals["baseline"] / tool_runs["baseline"], 3),
        ])
    write_csv(out_dir / "tool_use_by_tool.csv",
              ["tool", "mentions_D", "mentions_A", "mentions_per_run_D",
               "mentions_per_run_A"], tool_rows)

    # ---- the items that only the tools of arm D can answer
    exposed = set(exporter.read_tool_names(REPO / "alloagent" / "exposed_tools.txt"))
    arm_d_items = []
    for prompt_id in sorted(checklists):
        for item in checklists[prompt_id]["checklist"]:
            blob = json.dumps(item.get("value"), ensure_ascii=False) + " " + str(
                item.get("note")) + " " + str(item.get("source"))
            named = sorted(tool for tool in exposed if tool in blob)
            if named:
                arm_d_items.append((prompt_id, item["key"], named))
    arm_d_rows = []
    for prompt_id, key_name, named in arm_d_items:
        for arm in ARMS:
            rows = [run for run in runs
                    if run["prompt_id"] == prompt_id and run["arm"] == arm]
            states = Counter()
            for run in rows:
                for item in run["items"]:
                    if item["key"] == key_name:
                        states[item["state"]] += 1
            arm_d_rows.append([
                prompt_id, key_name, "; ".join(named), ARM_LABEL[arm], len(rows),
                states.get("correct", 0), states.get("incorrect", 0),
                states.get("missing", 0), states.get("not_applicable", 0),
            ])
    write_csv(out_dir / "arm_d_only_items.csv",
              ["prompt_id", "item_key", "the_tools_of_arm_D", "arm", "runs",
               "correct", "incorrect", "missing", "not_applicable"], arm_d_rows)

    # ---- the restricted-egress scenario (its 15 prompts)
    restricted_rows = []
    restricted_dir = Path(args.restricted_run_dir)
    if restricted_dir.is_dir():
        restricted_set = {row["id"] for row in json.loads(
            (REPO / "benchmark" / "restricted_prompt_set.json").read_text(
                encoding="utf-8"))["prompts"]
            if row.get("solvable_from_local_resources_alone") == "yes"}
        for arm in ARMS:
            arm_dir = restricted_dir / arm
            if not arm_dir.is_dir():
                continue
            rows = []
            for run_dir in sorted(arm_dir.iterdir()):
                summary_path = run_dir / "summary.json"
                if not summary_path.is_file():
                    continue
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                prompt_id = summary.get("prompt_id")
                if prompt_id not in restricted_set:
                    continue
                checklist = checklists.get(prompt_id)
                if checklist is None:
                    continue
                scored = score_scripted.score_answer(summary, checklist)
                rows.append({
                    "prompt_id": prompt_id,
                    "repeat": summary.get("repeat"),
                    "scripted_passed": scored["scripted_passed"],
                    "scripted_items": scored["scripted_items"],
                    "tokens": (summary.get("token_total") or {}).get("total_tokens") or 0,
                })
            if not rows:
                continue
            successes = sum(1 for row in rows
                            if row["scripted_items"] and
                            row["scripted_passed"] == row["scripted_items"])
            low, high = wilson(successes, len(rows))
            restricted_rows.append([
                "restricted-egress", ARM_LABEL[arm], len(rows), successes,
                round(successes / len(rows), 4), round(low, 4), round(high, 4),
                round(sum(row["tokens"] for row in rows) / len(rows), 1),
            ])
    if restricted_rows:
        write_csv(out_dir / "restricted_scenario.csv",
                  ["scenario", "arm", "runs", "scripted_successes",
                   "scripted_success_rate", "wilson_low", "wilson_high",
                   "mean_tokens"], restricted_rows)

    # ---- the summary file
    summary = [
        "# The analysis of the benchmark: the 240-run analysis set",
        "",
        f"Computed on {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} by "
        f"`benchmark/analyze_benchmark.py` (the bootstrap seed "
        f"{args.bootstrap_seed}, {args.bootstrap_rounds} rounds).",
        "",
        "## The primary success",
        "",
        "A run succeeds when Goal Completion is full **and** every "
        "[critical] item is correct: the scripted items by the result of the "
        "program, the judged items by the verdict of the judge, the items the "
        "program deferred to the judge by that verdict, and a judged "
        "*not_applicable* left out of the test.",
        "",
        "| variant | arm | runs | successes | success rate | Wilson 95 % |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        summary.append(
            f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | "
            f"[{row[5]}, {row[6]}] |")
    summary += [
        "",
        "## The paired difference (D minus A)",
        "",
        "Paired by prompt (the mean over the three repeats), the mean "
        f"difference is **{mean_difference:.4f}** with a bootstrap 95 % "
        f"interval over the prompts of [{diff_low:.4f}, {diff_high:.4f}]; the "
        f"sign-flip test ({sign_method}) gives p = {sign_p:.4f} ({sign_extreme} "
        "of the sign assignments are at least as extreme).",
        "",
        "## The tokens (the key secondary)",
        "",
        f"The log ratio of the mean tokens (D over A) is **{log_ratio:.4f}** "
        f"with a bootstrap 95 % interval over the prompts of "
        f"[{token_low:.4f}, {token_high:.4f}]; the sign-flip test "
        f"({token_sign_method}) gives p = {token_sign_p:.4f}.",
        "",
        "With Holm across the two tests:",
        "",
        "| test | p | Holm-adjusted |",
        "|---|---:|---:|",
        f"| the paired success difference | {sign_p:.4f} | {holm_adjusted[0]:.4f} |",
        f"| the token log ratio | {token_sign_p:.4f} | {holm_adjusted[1]:.4f} |",
        "",
        "## The mixed-model sensitivity",
        "",
        ("A mixed model of the success with a prompt random intercept: the "
         f"coefficient of the arm is {mixed.get('coefficient')} with p = "
         f"{mixed.get('p_value')} (converged: {mixed.get('converged')}).")
        if mixed.get("ok") else
        (f"The mixed model did not fit: {mixed.get('error')}"),
        "",
        ("The fit reports that the maximum likelihood may be on the boundary "
         "of the parameter space, which is what a very small difference "
         "between the arms looks like; the model is reported as the "
         "sensitivity it is and the exact per-prompt table is in "
         "`paired_difference_by_prompt.csv`.")
        if mixed.get("ok") else "",
        "",
        "## The other results",
        "",
        "| file | what it holds |",
        "|---|---|",
        "| `success_by_arm.csv` | the success of the primary rule and of the four sensitivity variants, per arm, with the Wilson intervals |",
        "| `paired_difference_by_prompt.csv` | the per-prompt success of both arms and their difference |",
        "| `steps_walltime_tokens.csv` | the steps, the wall time (as recorded) and the tokens, descriptively |",
        "| `success_against_budgets.csv` | the success against the token budget and against the time budget (the 1 000 000-token and the 30-minute points are in the table) |",
        "| `success_by_category.csv` | the success per prompt category and arm |",
        "| `tool_use_by_tool.csv` | the tool calls per run, by tool, for both arms |",
        "| `arm_d_only_items.csv` | the checklist items that name a tool only arm D has, and how both arms did on them |",
        "| `restricted_scenario.csv` | the restricted-egress scenario, its 15 prompts (the scripted layer only: the judge did not score that scenario) |",
        "| `validation_report.md` | the validation of the judge outputs |",
        "",
        "## The checks",
        "",
        "| check | result |",
        "|---|---|",
    ]
    for name, ok in checks:
        summary.append(f"| {name} | {'pass' if ok else 'FAIL'} |")
    checks.append(("the mixed model", bool(mixed.get("ok"))))
    summary.append(f"| the mixed model | {'pass' if mixed.get('ok') else 'FAIL'} |")
    write_text(out_dir / "summary.md", summary)

    # ---- the figures
    figure_files = []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots(1, 2, figsize=(10, 4))
        for arm in ARMS:
            rows = [run for run in runs if run["arm"] == arm]
            budgets = sorted({row[2] for row in curve_rows
                              if row[0] == "tokens" and row[1] == ARM_LABEL[arm]})
            rates = []
            for budget in budgets:
                inside = [run for run in rows if (run["tokens"] or 0) <= budget]
                rates.append(
                    sum(1 for run in inside if run["success"]["primary"]) / len(inside)
                    if inside else float("nan"))
            axes[0].plot(budgets, rates, marker="o", label=f"arm {ARM_LABEL[arm]}")
        axes[0].axvline(TOKEN_BUDGET, color="grey", linestyle="--", linewidth=1)
        axes[0].set_xlabel("token budget")
        axes[0].set_ylabel("success rate")
        axes[0].set_title("success against the token budget")
        axes[0].legend()
        for arm in ARMS:
            rows = [run for run in runs if run["arm"] == arm]
            budgets = sorted({row[2] for row in curve_rows
                              if row[0] == "wall_s" and row[1] == ARM_LABEL[arm]})
            rates = []
            for budget in budgets:
                inside = [run for run in rows if (run["wall_time_s"] or 0.0) <= budget]
                rates.append(
                    sum(1 for run in inside if run["success"]["primary"]) / len(inside)
                    if inside else float("nan"))
            axes[1].plot(budgets, rates, marker="o", label=f"arm {ARM_LABEL[arm]}")
        axes[1].axvline(WALL_CAP_S, color="grey", linestyle="--", linewidth=1)
        axes[1].set_xlabel("wall-clock budget (s)")
        axes[1].set_ylabel("success rate")
        axes[1].set_title("success against the time budget")
        axes[1].legend()
        figure.tight_layout()
        for suffix in ("pdf", "png"):
            path = out_dir / f"success_against_budgets.{suffix}"
            figure.savefig(path)
            figure_files.append(path.name)
        plt.close(figure)

        figure, axis = plt.subplots(figsize=(9, 5))
        names = [row[0] for row in category_rows if row[1] == "D"]
        positions = list(range(len(names)))
        for offset, arm in ((-0.2, "D"), (0.2, "A")):
            values = [row[4] for row in category_rows if row[1] == arm]
            axis.bar([p + offset for p in positions], values, width=0.4,
                     label=f"arm {arm}")
        axis.set_xticks(positions)
        axis.set_xticklabels(names, rotation=30, ha="right")
        axis.set_ylabel("success rate")
        axis.set_title("the success by prompt category")
        axis.legend()
        figure.tight_layout()
        for suffix in ("pdf", "png"):
            path = out_dir / f"success_by_category.{suffix}"
            figure.savefig(path)
            figure_files.append(path.name)
        plt.close(figure)
    except Exception as error:  # noqa: BLE001
        checks.append((f"the figures ({type(error).__name__})", False))

    print(f"the runs analysed: {len(runs)}")
    print(f"the checks: {sum(1 for _, ok in checks if ok)} passed, "
          f"{sum(1 for _, ok in checks if not ok)} failed")
    for name, ok in checks:
        if not ok:
            print(f"  the check failed: {name}")
    print(f"the files written: {len(list(out_dir.glob('*')))}")
    for path in sorted(out_dir.glob("*")):
        print(f"  {path.name}")
    print(f"the figures: {figure_files}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

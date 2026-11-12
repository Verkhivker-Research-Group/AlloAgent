"""Draw the human subset: 30 runs, masked, with the rating files.

The seed and the procedure are recorded in
``benchmark/human_subset_draw.md`` **before** this script is run.  This
script implements that procedure exactly:

* the pool is the analysis set minus the runs that were used to write or
  test the judge prompt (the six runs of the probes of 2026-10-29);
* one run per prompt category first, in the alphabetical order of the
  category names;
* the other runs are drawn with the arm that is behind served first, so
  the two arms are equally represented;
* the drawn runs are shuffled, so the rater does not receive them
  grouped;
* every run gets a fresh opaque id and the same masking as the judge
  batches: the one-sided tool names, the arm names, the branch names and
  the persona name become ``[TOOL]``, and every number, identifier,
  residue and structure ID is kept.

The **key** (opaque id -> arm, prompt, repeat, record path) is written
outside the rating folder.  The rater does not get it, and this script
does not print which arm any run came from.

    python benchmark/draw_human_subset.py --out-dir <rating folder> \
        [--key-out <path>] [--seed 20261103]
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "benchmark"))
sys.path.insert(0, str(REPO / "scripts"))
from _paths import expand_home  # noqa: E402

# The exporter is loaded by its path: the repository still holds the
# earlier masker of 2026-10-29 under benchmark/make_judge_batches.py,
# and the two modules share a name.
_exporter_spec = importlib.util.spec_from_file_location(
    "judge_batch_exporter", REPO / "benchmark" / "export_judge_batches.py")
exporter = importlib.util.module_from_spec(_exporter_spec)
_exporter_spec.loader.exec_module(exporter)

ANALYSIS_SET = REPO / "benchmark" / "analysis_set.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
DRAFT = REPO / "benchmark" / "benchmark_draft.json"
CORRECTIONS = REPO / "benchmark" / "corrections" / "pocket_reference_selection_2026-11-02.json"
SHEET_TEMPLATE = REPO / "benchmark" / "human_rating_sheet_template.md"

# The runs that were used to write or test the judge prompt: the first
# six runs of the masked batch of the session of 2026-10-29 (the probes
# judged_probe.json, judged_probe2.json and judged_probe3.json).
JUDGE_PROMPT_DEVELOPMENT_RUNS = (
    ("baseline", "S04", 3),
    ("baseline", "H02", 1),
    ("baseline", "V01", 3),
    ("alloagent", "V02", 1),
    ("baseline", "H02", 3),
    ("alloagent", "P05", 3),
)

SUBSET_SIZE = 30
HUMAN_RUN_ID_PREFIX = "h"

# The rating files are written into the repository (in the folder that
# git ignores); the **key** is written outside it, because it says which
# arm every run came from.
DEFAULT_OUT_DIR = REPO / "benchmark" / "judging" / "human_subset_30"
DEFAULT_KEY_PATH = Path(tempfile.gettempdir()) / "opencode" / "human_subset_key.json"


def sheet_sections() -> tuple[str, str]:
    """The 'Before you start' and the 'Rubric' sections of the template."""
    text = SHEET_TEMPLATE.read_text(encoding="utf-8")
    before_start = text.find("## Before you start")
    rubric_start = text.find("## Rubric (same as the judge)")
    rubric_end = text.find("## One row per run")
    if min(before_start, rubric_start, rubric_end) < 0:
        raise ValueError(f"the rating sheet template has no section: {SHEET_TEMPLATE}")
    before = text[before_start:rubric_start].rstrip()
    rubric = text[rubric_start:rubric_end].rstrip()
    return before, rubric


def draw(pool: list[dict], seed: int, size: int = SUBSET_SIZE) -> list[dict]:
    """The draw: one run per category, then the arms balanced."""
    rng = random.Random(seed)
    by_category: dict[str, list[dict]] = {}
    for run in pool:
        by_category.setdefault(run["category"], []).append(run)
    drawn: list[dict] = []
    taken: set[int] = set()
    for category in sorted(by_category):
        candidates = [run for run in by_category[category] if id(run) not in taken]
        if not candidates:
            continue
        chosen = candidates[rng.randrange(len(candidates))]
        drawn.append(chosen)
        taken.add(id(chosen))
    arms = Counter(run["arm"] for run in drawn)
    remaining = [run for run in pool if id(run) not in taken]
    while len(drawn) < size and remaining:
        counts = Counter(run["arm"] for run in drawn)
        behind = min(counts, key=lambda arm: (counts[arm], arm))
        candidates = [run for run in remaining if run["arm"] == behind]
        if not candidates:
            candidates = remaining
        chosen = candidates[rng.randrange(len(candidates))]
        drawn.append(chosen)
        remaining.remove(chosen)
    rng.shuffle(drawn)
    return drawn


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR),
                        help="the rating folder (default: the ignored folder in the repository)")
    parser.add_argument("--key-out", default=str(DEFAULT_KEY_PATH),
                        help="the key file (default: outside the repository)")
    parser.add_argument("--seed", type=int, default=20261103)
    parser.add_argument("--size", type=int, default=SUBSET_SIZE)
    args = parser.parse_args()

    analysis_set = json.loads(ANALYSIS_SET.read_text(encoding="utf-8"))
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    draft = {row["id"]: row for row in json.loads(DRAFT.read_text(encoding="utf-8"))}
    corrections = json.loads(CORRECTIONS.read_text(encoding="utf-8"))

    arm_a_tools = exporter.read_tool_names(REPO / "benchmark" / "baseline_arm_tool_names.txt")
    arm_d_tools = exporter.read_tool_names(REPO / "alloagent" / "exposed_tools.txt")
    one_sided = sorted((set(arm_a_tools) | set(arm_d_tools))
                        - (set(arm_a_tools) & set(arm_d_tools)))
    redactor = exporter.Redactor(
        exporter.build_tool_pattern(one_sided),
        exporter.build_arm_pattern(exporter.ARM_TOKENS),
        re_compile_persona(), re_compile_arm_label(),
    )

    excluded = set(JUDGE_PROMPT_DEVELOPMENT_RUNS)
    pool = []
    for row in analysis_set["rows"]:
        key = (row["arm"], row["prompt_id"], row["repeat"])
        if key in excluded:
            continue
        record_dir = expand_home(row["record_dir"])
        summary = json.loads((record_dir / "summary.json").read_text(encoding="utf-8"))
        answer = (record_dir / "answer.txt").read_text(encoding="utf-8", errors="replace")
        retained, _ = exporter.final_answer(record_dir)
        prompt_row = draft.get(row["prompt_id"], {})
        checklist = next(
            (p for p in checklists["prompts"] if p["id"] == row["prompt_id"]),
            {"checklist": []})
        ids = exporter.item_ids(row["prompt_id"], checklist["checklist"])
        verdicts = exporter.scripted_verdicts(summary, checklist)
        lines = []
        for identifier, item in zip(ids, checklist["checklist"]):
            verdict = verdicts.get(item["key"])
            judged = verdict == "DEFERRED" or (
                verdict is None and exporter.is_judged(item))
            flags = [f"[{identifier}]", "[critical]",
                     "[judged]" if judged else "[scripted]"]
            if exporter.is_low_information(item):
                flags.append("[low-information item]")
            lines.append(" ".join(flags) + " " + exporter.item_text(item))
        protein = ""
        for item in checklist["checklist"]:
            if item["key"].startswith("accession_") and isinstance(item.get("value"), dict):
                protein = item["value"].get("name") or ""
        pool.append({
            "arm": row["arm"],
            "prompt_id": row["prompt_id"],
            "repeat": row["repeat"],
            "record_dir": str(record_dir),
            "category": prompt_row.get("category", ""),
            "prompt_text": prompt_row.get("prompt") or summary.get("prompt") or "",
            "protein_name": protein,
            "accession": prompt_row.get("accession", ""),
            "prompt_type": ("HONEST-REPORTING"
                            if prompt_row.get("category") == "Honest reporting"
                            else "normal"),
            "checklist_lines": lines,
            "answer": redactor(retained),
            "answer_sha256": exporter.sha256_text(answer),
        })

    drawn = draw(pool, args.seed, args.size)
    if len(drawn) != args.size:
        print(f"the draw produced {len(drawn)} runs, not {args.size}")
        return 1

    rng = random.Random(args.seed + 1)
    forbidden = []
    for run in drawn:
        forbidden += [run["arm"], run["prompt_id"], f"r{run['repeat']}"]
    forbidden += list(exporter.ARM_TOKENS) + [exporter.PERSONA] + list(draft.keys())
    run_ids = exporter.make_run_ids(len(drawn), rng, forbidden)
    for run, run_id in zip(drawn, run_ids):
        run["run_id"] = run_id

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    key_out = Path(args.key_out) if args.key_out else DEFAULT_KEY_PATH
    if exporter._is_inside_the_repository(key_out):
        print(
            f"ERROR: the key must not be written inside the repository "
            f"({REPO}); it says which arm every run came from.  Choose a path "
            f"outside it.",
            file=sys.stderr,
        )
        return 2
    key_out.parent.mkdir(parents=True, exist_ok=True)

    before, rubric = sheet_sections()
    judge_facts = {}
    for prompt_id, sites in corrections.get("judge_needs_these_numbers", {}).items():
        judge_facts[prompt_id] = {}
        for site, values in sites.items():
            committed = corrections.get("sites_without_a_committed_item", {}).get(site, {})
            judge_facts[prompt_id][site] = {
                "committed_rank": committed.get("committed", {}).get(
                    "rank_of_the_pocket_covering_the_site"),
                "committed_overlap": committed.get("committed", {}).get(
                    "overlap_of_the_covering_pocket"),
                "corrected_rank": values.get("rank_of_the_pocket_covering_the_site"),
                "corrected_overlap": values.get("overlap_of_the_covering_pocket"),
            }

    key_rows = []
    for number, run in enumerate(drawn, start=1):
        note = exporter.reference_note(
            run["prompt_id"], {"judge_needs_these_numbers": judge_facts})
        block = exporter.render_run_block(run, note)
        text = (
            f"# Human rating sheet: run {run['run_id']} "
            f"({number} of {len(drawn)})\n\n"
            f"{before}\n\n"
            f"{rubric}\n\n"
            f"---\n\n"
            f"{block}\n\n"
            f"## Your scores\n\n"
            f"Write them in the CSV (`human_subset_scores.csv`), one row for "
            f"this run id, in this order:\n\n"
            f"```\nrun_id,goal_completion,data_grounding,final_answer_complete,"
            f"item_verdicts,notes\n```\n\n"
            f"Skip the items marked `scripted`; the `item_verdicts` field "
            f"holds `item_id:verdict` pairs separated by semicolons.\n"
        )
        (out_dir / f"human_run_{number:02d}.md").write_text(text, encoding="utf-8")
        key_rows.append({
            "run_id": run["run_id"],
            "file": f"human_run_{number:02d}.md",
            "arm": run["arm"],
            "prompt_id": run["prompt_id"],
            "repeat": run["repeat"],
            "record_dir": run["record_dir"],
            "category": run["category"],
            "answer_sha256": run["answer_sha256"],
        })

    csv_path = out_dir / "human_subset_scores.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", "goal_completion", "data_grounding",
                         "final_answer_complete", "item_verdicts", "notes"])
        for run in drawn:
            writer.writerow([run["run_id"], "", "", "", "", ""])

    key_out.write_text(json.dumps({
        "what_this_file_is": (
            "the key of the human subset: the opaque run id of every drawn "
            "run and the arm, the prompt, the repeat and the record path it "
            "stands for.  The rater does not get this file."
        ),
        "seed": args.seed,
        "procedure": "benchmark/human_subset_draw.md",
        "runs": len(key_rows),
        "runs_key": key_rows,
    }, indent=2) + "\n", encoding="utf-8")

    readme = [
        "# The human subset: 30 runs",
        "",
        f"Drawed with the seed {args.seed} by "
        f"`benchmark/draw_human_subset.py`; the seed and the procedure are "
        f"recorded in `benchmark/human_subset_draw.md`.",
        "",
        "* 30 files, `human_run_01.md` to `human_run_30.md`: the rubric and "
        "one run each.",
        "* `human_subset_scores.csv`: the header of the template and the 30 "
        "run ids, for you to fill in.",
        "* The **key is not here**: it is `human_subset_key.json`, outside "
        f"the repository ({key_out}).",
        "",
        "The masking is the same as the judge batches: the one-sided tool "
        "names, the arm names, the branch names and the persona name are "
        "replaced by `[TOOL]`, and every number, identifier, residue and "
        "structure ID is kept.  The answer of a run is **only its final "
        "response** (the body of the last `<solution>` block): the "
        "reasoning of the agent is not in the file.  The run blocks of the "
        "prompts whose pocket criteria are judged carry the same reference "
        "note as the judge batches.",
        "",
        "Do not open the key file, the judge outputs or the run records.",
    ]
    (out_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    arms = Counter(run["arm"] for run in drawn)
    categories = Counter(run["category"] for run in drawn)
    print(f"the draw: {len(drawn)} runs with the seed {args.seed}")
    print(f"  the arms: {dict(arms)}")
    print(f"  the categories: {dict(sorted(categories.items()))}")
    print(f"  the rating folder: {out_dir}")
    print(f"  the key: {key_out}")
    print(f"  the scores: {csv_path}")
    return 0


def re_compile_persona():
    import re
    return re.compile(r"(?<![\w-])" + re.escape(exporter.PERSONA) + r"(?![\w-])")


def re_compile_arm_label():
    import re
    return re.compile(exporter.ARM_LABEL_PATTERN, re.IGNORECASE)


if __name__ == "__main__":
    raise SystemExit(main())

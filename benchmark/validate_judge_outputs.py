"""Validate the judge outputs against the batches, the checklists and the key.

The judge (Claude Sonnet 5.5) was given the 25 masked batch files and
returned one JSON array per batch.  This script checks that the answers
are usable before anything is computed from them:

* the file name names a batch that exists (``judge_batch_NNN_scores.json``
  and ``judge_batch_NNN_results.json`` are both accepted);
* the content is a JSON **array** and nothing else;
* the runs of a batch are in it exactly once, and all the runs of the
  analysis set are in the files exactly once;
* the field values are the ones the template asks for;
* every item belongs to the run's checklist and is a **[judged]** item;
* no scripted item is scored;
* no item is scored twice;
* **every** [judged] item has exactly one verdict (the runs that do not
  are listed);
* an empty evidence, or an evidence that is not in the answer, is a
  **warning**, not a failure.

The report is written to a file and holds counts, file names and the
checks that failed; the arm labels of the key are used to find the
answers, never printed.

    python benchmark/validate_judge_outputs.py --outputs <folder> \
        --batches <folder> --key <judge_key.json> \
        [--out benchmark/judging/validation_report.md]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "benchmark"))

# The exporter is loaded by its path: the repository still holds the
# earlier masker of 2026-10-29 under benchmark/make_judge_batches.py,
# and the two modules share a name.
_exporter_spec = importlib.util.spec_from_file_location(
    "judge_batch_exporter", REPO / "benchmark" / "export_judge_batches.py")
exporter = importlib.util.module_from_spec(_exporter_spec)
_exporter_spec.loader.exec_module(exporter)

OUTPUT_RE = re.compile(r"^judge_batch_(\d{3})_(scores|results)\.json$")
BATCH_RE = re.compile(r"^judge_batch_(\d{3})\.md$")
GOAL_COMPLETION = ("full", "partial", "deferred", "null")
FINAL_ANSWER_COMPLETE = ("yes", "no")
VERDICTS = ("correct", "incorrect", "missing", "not_applicable")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def batch_runs(path: Path) -> list[str]:
    """The run ids of a batch file, in the order they appear."""
    text = path.read_text(encoding="utf-8")
    return re.findall(r"^=== RUN (\S+) ===$", text, re.M)


def batch_answers(path: Path) -> dict[str, str]:
    """The final answer of every run of a batch file."""
    text = path.read_text(encoding="utf-8")
    marker = "FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):"
    out: dict[str, str] = {}
    for match in re.finditer(
            r"^=== RUN (\S+) ===$(.*?)^=== END RUN \S+ ===$",
            text, re.M | re.DOTALL):
        body = match.group(2)
        if marker in body:
            out[match.group(1)] = body.split(marker, 1)[1].strip()
    return out


CHECKLIST_MARKER = "CHECKLIST (ground truth):"
ITEM_LINE_RE = re.compile(r"^\[(\S+)\] \[(critical|non-critical)\] \[(judged|scripted)\] ")


def batch_checklists(path: Path) -> dict[str, dict[str, bool]]:
    """The item ids of every run of a batch file, with their flags.

    The judge saw the ids the batch carries (``<prompt>_<letter>``) and
    the flags, so the validation is made against what the judge saw.
    """
    text = path.read_text(encoding="utf-8")
    out: dict[str, dict[str, bool]] = {}
    for match in re.finditer(
            r"^=== RUN (\S+) ===$(.*?)^=== END RUN \S+ ===$",
            text, re.M | re.DOTALL):
        body = match.group(2)
        if CHECKLIST_MARKER not in body:
            out[match.group(1)] = {}
            continue
        section = body.split(CHECKLIST_MARKER, 1)[1]
        section = re.split(
            r"^(?:FINAL ANSWER|REFERENCE NOTE|=== END RUN)", section,
            maxsplit=1, flags=re.M)[0]
        items: dict[str, bool] = {}
        for line in section.splitlines():
            item_match = ITEM_LINE_RE.match(line.strip())
            if item_match:
                items[item_match.group(1)] = item_match.group(3) == "judged"
        out[match.group(1)] = items
    return out


def checklist_items() -> dict[str, dict]:
    """The checklist of every prompt, by item key."""
    checklists = load_json(REPO / "benchmark" / "checklists.json")
    out: dict[str, dict] = {}
    for prompt in checklists["prompts"]:
        for item in prompt["checklist"]:
            out[f"{prompt['id']}::{item['key']}"] = item
    return out


def judged_items_for_run(summary: dict, checklist: dict) -> set[str]:
    """The item ids the judge has to score for that run.

    The same rule the exporter uses when it writes the batch: an item is
    the judge's when the program could not decide it (a qualitative item,
    or a method-conditional item whose method the answer does not name).
    """
    verdicts = exporter.scripted_verdicts(summary, checklist)
    judged = set()
    for item in checklist["checklist"]:
        key = item["key"]
        verdict = verdicts.get(key)
        if verdict == "DEFERRED" or (verdict is None and exporter.is_judged(item)):
            judged.add(key)
    return judged


def validate(
    outputs_dir: Path,
    batches_dir: Path,
    key_path: Path,
    checklists_path: Path | None = None,
) -> dict:
    """The validation of the judge outputs.  Counts, failures and warnings."""
    failures: list[dict] = []
    warnings: list[dict] = []
    counts: Counter = Counter()

    key = load_json(key_path)
    key_rows = {row["run_id"]: row for row in key["runs_key"]}

    batches = {}
    for path in sorted(batches_dir.glob("judge_batch_*.md")):
        match = BATCH_RE.match(path.name)
        if match:
            batches[int(match.group(1))] = path
    counts["batches_found"] = len(batches)

    checklists = load_json(checklists_path or (REPO / "benchmark" / "checklists.json"))
    by_prompt = {prompt["id"]: prompt for prompt in checklists["prompts"]}

    files = {}
    for path in sorted(outputs_dir.iterdir()):
        match = OUTPUT_RE.match(path.name)
        if not match:
            continue
        number = int(match.group(1))
        if number in files:
            failures.append({
                "check": "one output file per batch",
                "file": path.name,
                "detail": f"batch {number:03d} has two output files",
            })
        files[number] = path
    counts["output_files"] = len(files)

    seen_runs: dict[str, str] = {}
    run_verdicts: dict[str, dict[str, str]] = {}
    run_records: dict[str, dict] = {}

    for number in sorted(files):
        path = files[number]
        counts["files_checked"] += 1
        if number not in batches:
            failures.append({
                "check": "the output file names a batch that exists",
                "file": path.name,
                "detail": f"no judge_batch_{number:03d}.md",
            })
            continue
        try:
            payload = load_json(path)
        except (OSError, ValueError) as error:
            failures.append({
                "check": "the output file is valid JSON",
                "file": path.name,
                "detail": str(error)[:200],
            })
            continue
        if not isinstance(payload, list):
            failures.append({
                "check": "the output file holds a JSON array",
                "file": path.name,
                "detail": f"the top level is {type(payload).__name__}",
            })
            continue
        expected = batch_runs(batches[number])
        answers = batch_answers(batches[number])
        batch_items = batch_checklists(batches[number])
        in_file = []
        for record in payload:
            if not isinstance(record, dict):
                failures.append({
                    "check": "every entry of the array is an object",
                    "file": path.name,
                    "detail": type(record).__name__,
                })
                continue
            run_id = record.get("run_id")
            if not isinstance(run_id, str) or not run_id:
                failures.append({
                    "check": "every entry names a run",
                    "file": path.name,
                    "detail": repr(run_id)[:80],
                })
                continue
            in_file.append(run_id)
            if run_id in seen_runs:
                failures.append({
                    "check": "every run appears exactly once",
                    "file": path.name,
                    "detail": f"run {run_id} is also in {seen_runs[run_id]}",
                })
                continue
            seen_runs[run_id] = path.name
            if run_id not in key_rows:
                failures.append({
                    "check": "every run of the output is in the key",
                    "file": path.name,
                    "detail": f"run {run_id}",
                })
                continue
            if run_id not in expected:
                failures.append({
                    "check": "the runs of the output are the runs of its batch",
                    "file": path.name,
                    "detail": f"run {run_id} is not in judge_batch_{number:03d}.md",
                })
                continue
            run_verdicts[run_id] = {
                item.get("item_id"): (item.get("verdict"), item.get("evidence"))
                for item in (record.get("items") or [])
                if isinstance(item, dict)
            }
            run_records[run_id] = record
            counts["runs_checked"] += 1

            goal = record.get("goal_completion")
            if goal not in GOAL_COMPLETION:
                failures.append({
                    "check": "goal_completion is one of the four values",
                    "file": path.name,
                    "detail": f"run {run_id}: {goal!r}",
                })
            grounding = record.get("data_grounding")
            if grounding not in (0, 1, 2) or isinstance(grounding, bool):
                failures.append({
                    "check": "data_grounding is 0, 1 or 2",
                    "file": path.name,
                    "detail": f"run {run_id}: {grounding!r}",
                })
            complete = record.get("final_answer_complete")
            if complete not in FINAL_ANSWER_COMPLETE:
                failures.append({
                    "check": "final_answer_complete is yes or no",
                    "file": path.name,
                    "detail": f"run {run_id}: {complete!r}",
                })
            notes = record.get("notes")
            if notes is not None and not isinstance(notes, str):
                failures.append({
                    "check": "notes is a string",
                    "file": path.name,
                    "detail": f"run {run_id}: {type(notes).__name__}",
                })

            row = key_rows[run_id]
            prompt_id = row["prompt_id"]
            checklist = by_prompt.get(prompt_id)
            if checklist is None:
                failures.append({
                    "check": "the prompt of the run has a checklist",
                    "file": path.name,
                    "detail": f"run {run_id}: {prompt_id}",
                })
                continue
            items_of_the_batch = batch_items.get(run_id, {})
            judged = {item_id for item_id, is_judged in items_of_the_batch.items()
                      if is_judged}
            counted = Counter()
            for item in (record.get("items") or []):
                if not isinstance(item, dict):
                    failures.append({
                        "check": "every item is an object",
                        "file": path.name,
                        "detail": f"run {run_id}",
                    })
                    continue
                counted[item.get("item_id")] += 1
                if item.get("item_id") not in items_of_the_batch:
                    failures.append({
                        "check": "every scored item belongs to the checklist",
                        "file": path.name,
                        "detail": f"run {run_id}: {item.get('item_id')!r}",
                    })
                    continue
                if item.get("item_id") not in judged:
                    failures.append({
                        "check": "no scripted item is scored",
                        "file": path.name,
                        "detail": f"run {run_id}: {item.get('item_id')!r}",
                    })
                    continue
                verdict = item.get("verdict")
                if verdict not in VERDICTS:
                    failures.append({
                        "check": "the verdict is one of the four values",
                        "file": path.name,
                        "detail": f"run {run_id}: {item.get('item_id')!r} -> {verdict!r}",
                    })
                evidence = item.get("evidence")
                if not isinstance(evidence, str) or not evidence.strip():
                    warnings.append({
                        "check": "the evidence is not empty",
                        "file": path.name,
                        "detail": f"run {run_id}: {item.get('item_id')!r}",
                    })
                elif evidence.strip() not in answers.get(run_id, ""):
                    warnings.append({
                        "check": "the evidence is in the answer",
                        "file": path.name,
                        "detail": f"run {run_id}: {item.get('item_id')!r}",
                    })
            for item_id, number_of_times in counted.items():
                if number_of_times > 1:
                    failures.append({
                        "check": "no item is scored twice",
                        "file": path.name,
                        "detail": f"run {run_id}: {item_id!r} scored "
                                  f"{number_of_times} times",
                    })
            missing = sorted(judged - set(counted))
            if missing:
                failures.append({
                    "check": "every judged item has exactly one verdict",
                    "file": path.name,
                    "detail": f"run {run_id}: {len(missing)} item(s) without a "
                              f"verdict",
                })
            counts["items_scored"] += len(counted)
        for run_id in expected:
            if run_id not in in_file:
                failures.append({
                    "check": "every run of the batch is in the output",
                    "file": path.name,
                    "detail": f"run {run_id}",
                })

    missing_runs = [row["run_id"] for row in key["runs_key"]
                    if row["run_id"] not in seen_runs]
    for run_id in missing_runs:
        failures.append({
            "check": "every run of the analysis set is judged once",
            "file": "",
            "detail": f"run {run_id}",
        })

    return {
        "counts": dict(counts),
        "files": {number: path.name for number, path in sorted(files.items())},
        "batches": sorted(batches),
        "runs_seen": len(seen_runs),
        "runs_expected": len(key["runs_key"]),
        "runs_missing": missing_runs,
        "failures": failures,
        "warnings": warnings,
        "run_verdicts": run_verdicts,
        "run_records": run_records,
    }


def write_report(result: dict, out_path: Path, outputs_dir: Path) -> None:
    counts = result["counts"]
    failures = result["failures"]
    warnings = result["warnings"]
    lines = [
        "# The validation of the judge outputs",
        "",
        f"Validated on {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.",
        "",
        "## The counts",
        "",
        "| item | count |",
        "|---|---:|",
        f"| the batch files | {counts.get('batches_found', 0)} |",
        f"| the output files | {counts.get('output_files', 0)} |",
        f"| the output files read | {counts.get('files_checked', 0)} |",
        f"| the runs in the outputs | {counts.get('runs_checked', 0)} |",
        f"| the runs of the analysis set | {result['runs_expected']} |",
        f"| the runs that are missing | {len(result['runs_missing'])} |",
        f"| the items scored | {counts.get('items_scored', 0)} |",
        f"| the checks that failed | {len(failures)} |",
        f"| the warnings | {len(warnings)} |",
        "",
        "## The files",
        "",
        "| batch | the output file |",
        "|---|---|",
    ]
    for number, name in result["files"].items():
        lines.append(f"| judge_batch_{number:03d}.md | `{name}` |")
    lines += [
        "",
        "## The checks that failed",
        "",
        "| check | file | detail |",
        "|---|---|---|",
    ]
    if failures:
        for failure in failures:
            lines.append(
                f"| {failure['check']} | `{failure['file']}` | {failure['detail']} |")
    else:
        lines.append("| none | | |")
    lines += [
        "",
        "## The warnings",
        "",
        "| check | file | detail |",
        "|---|---|---|",
    ]
    if warnings:
        for warning in warnings:
            lines.append(
                f"| {warning['check']} | `{warning['file']}` | {warning['detail']} |")
    else:
        lines.append("| none | | |")
    lines += [
        "",
        "## The checks",
        "",
        "The checks are: the file name names a batch that exists; the file "
        "is valid JSON; the content is a JSON array and nothing else; the "
        "runs of a batch are in its output exactly once; every run of the "
        "analysis set is in the outputs exactly once; the field values are "
        "the ones the template asks for; every scored item belongs to the "
        "run's checklist and is a [judged] item; no scripted item is "
        "scored; no item is scored twice; every [judged] item has exactly "
        "one verdict; an empty evidence or an evidence that is not in the "
        "answer is a warning.",
        "",
        "The arm labels of the key are used to find the answers of the "
        "runs; they are not written here and not printed.",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--outputs", required=True,
                        help="the folder with the judge outputs")
    parser.add_argument("--batches", default=str(
        REPO / "benchmark" / "judging" / "judge_batches"))
    parser.add_argument("--key", required=True, help="the key of the batches")
    parser.add_argument("--checklists", default=None)
    parser.add_argument("--out", default=str(
        REPO / "benchmark" / "judging" / "validation_report.md"))
    parser.add_argument("--json-out", default=None,
                        help="the validated verdicts as JSON")
    args = parser.parse_args()

    result = validate(
        outputs_dir=Path(args.outputs),
        batches_dir=Path(args.batches),
        key_path=Path(args.key),
        checklists_path=Path(args.checklists) if args.checklists else None,
    )
    write_report(result, Path(args.out), Path(args.outputs))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps({
            "run_verdicts": result["run_verdicts"],
            "run_records": result["run_records"],
        }, indent=2) + "\n", encoding="utf-8")
    print(f"the output files: {result['counts'].get('output_files', 0)}")
    print(f"the runs checked: {result['runs_checked']}"
          if "runs_checked" in result else
          f"the runs checked: {result['counts'].get('runs_checked', 0)}")
    print(f"the runs of the analysis set: {result['runs_expected']}")
    print(f"the runs missing: {len(result['runs_missing'])}")
    print(f"the items scored: {result['counts'].get('items_scored', 0)}")
    print(f"the checks that failed: {len(result['failures'])}")
    print(f"the warnings: {len(result['warnings'])}")
    print(f"the report: {args.out}")
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

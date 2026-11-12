"""Score the capability runs with the committed scorer and this folder's checklists.

The scripted items are scored by ``benchmark/score_scripted.py``; the judged
items need the judge outputs, which are produced by
``benchmark/export_judge_batches.py`` pointed at ``benchmark/capability/``.

    python benchmark/score_capability.py --run-dir <the run dir> \\
        [--judge-outputs <the judge output folder>] [--out-dir <the out dir>]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "benchmark"))

import score_scripted as ss  # noqa: E402

CAPABILITY = REPO / "benchmark" / "capability"


def item_state(scripted_verdict, judged_verdict):
    if scripted_verdict in ("PASS", "FAIL"):
        return "correct" if scripted_verdict == "PASS" else "incorrect"
    if judged_verdict in ("correct", "incorrect", "missing", "not_applicable"):
        return judged_verdict
    return "missing"


def full_answer(record_dir: Path) -> str:
    """The run's final answer, in full, from the last ``Ai Message`` of the trace.

    The run record stores only the first 20000 characters of the answer
    (``benchmark/run_benchmark.py``: ``record["final_content"] = str(content)[:20000]``),
    so the scorer reads the uncapped text from the trace instead.
    """
    trace_path = record_dir / "trace.txt"
    if not trace_path.is_file():
        return ""
    trace = trace_path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"={5,}\s*Ai Message\s*={5,}\r?\n", trace)
    return parts[-1].strip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--judge-outputs", default="")
    parser.add_argument("--out-dir", default=str(CAPABILITY / "results"))
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checklists = {p["id"]: p for p in json.loads(
        (CAPABILITY / "checklists.json").read_text(encoding="utf-8"))["prompts"]}

    judged = {}
    if args.judge_outputs:
        for path in sorted(Path(args.judge_outputs).glob("judge_batch_*_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                continue
            for record in payload:
                entry = judged.setdefault(record.get("run_id"), {})
                for item in record.get("items") or []:
                    entry[item.get("item_id")] = item.get("verdict")

    rows = []
    counts = defaultdict(Counter)
    lengths = []
    for record_dir in sorted(run_dir.glob("*/*")):
        summary_path = record_dir / "summary.json"
        if not summary_path.is_file():
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        prompt_id = summary.get("prompt_id")
        checklist = checklists.get(prompt_id)
        if checklist is None:
            continue
        answer = full_answer(record_dir)
        stored = summary.get("final_content") or ""
        lengths.append((record_dir.name, prompt_id, len(answer), len(stored)))
        scored_summary = dict(summary)
        scored_summary["final_content"] = answer
        scored = ss.score_answer(scored_summary, checklist)
        states = {}
        for item in scored["items"]:
            judged_verdict = judged.get(record_dir.name, {}).get(item["key"])
            states[item["key"]] = item_state(item["verdict"], judged_verdict)
        for item in scored["items"]:
            verdict = item["verdict"]
            state = states[item["key"]]
            counts[(prompt_id, item["key"])][state] += 1
            rows.append([record_dir.parent.name, prompt_id, summary.get("repeat"),
                         record_dir.name, item["key"], item["kind"], verdict, state,
                         len(answer), item["reason"]])
        summary["_capability_states"] = states


    with (out_dir / "capability_item_states.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["arm", "prompt_id", "repeat", "run", "item_key", "kind",
                         "scripted_verdict", "state", "answer_chars", "reason"])
        writer.writerows(rows)
    with (out_dir / "capability_item_counts.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["prompt_id", "item_key", "correct", "incorrect", "missing", "not_applicable"])
        for (prompt_id, key), counter in sorted(counts.items()):
            writer.writerow([prompt_id, key, counter.get("correct", 0), counter.get("incorrect", 0),
                             counter.get("missing", 0), counter.get("not_applicable", 0)])
    capped = [entry for entry in lengths if entry[2] > entry[3]]
    print(f"the runs scored: {len(rows)} item verdicts")
    print("the final answers come from the last 'Ai Message' of each trace.txt, in full, "
          "not the 20000-character copy in the run record")
    print(f"  the runs whose answer is longer than the stored copy: {len(capped)} of {len(lengths)}")
    for name, prompt_id, full_len, stored_len in sorted(capped, key=lambda e: -(e[2] - e[3]))[:5]:
        print(f"    {name} ({prompt_id}): the trace answer {full_len} chars, the stored copy {stored_len} chars")
    print(f"the files written: {out_dir/'capability_item_states.csv'}, {out_dir/'capability_item_counts.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

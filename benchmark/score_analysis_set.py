"""Score the analysis set of the benchmark against the committed checklists.

The **analysis set** is the 234 runs of ``benchmark/analysis_set.json``:
the 174 original runs that are not compromised plus the 60 reruns.  This
script scores exactly those runs - not the run directories - so that the
numbers describe the analysis set and nothing else.

It reuses the committed scorer (``benchmark/score_scripted.py``) unchanged:
the semantics of every item kind are the ones of the dated note of
2026-10-29.  Two things can be added on top, and neither of them changes
a committed checklist:

``--corrections <file>``
    apply the values of a dated correction note (see
    ``benchmark/corrections.md``).  The corrected value is merged into the
    item's value; the committed value is untouched on disk, and the
    primary scoring is always reported next to the corrected one.
``--exclude-item-prefix <prefix>``
    drop the items whose key starts with the prefix, for the sensitivity
    output.  The items are not changed, they are left out of this run.

    python benchmark/score_analysis_set.py \
        [--analysis-set benchmark/analysis_set.json] \
        [--corrections benchmark/corrections/pocket_reference_selection_2026-11-02.json] \
        [--exclude-item-prefix accession_] \
        [--prompts P01 P07] [--label <name>] [--out <file>]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmark"))

import score_scripted  # noqa: E402  (the path is set up above)

DEFAULT_ANALYSIS_SET = REPO / "benchmark" / "analysis_set.json"


def load_checklists() -> dict[str, dict]:
    return score_scripted.load_checklists()


def corrected_checklist(
    checklist: dict,
    corrections: dict[str, dict],
    exclude_prefixes: list[str],
) -> tuple[dict, list[str], list[str]]:
    """The checklist of a prompt, with the corrections applied.

    Returns the checklist, the keys that were corrected and the keys that
    were excluded.
    """
    items = []
    corrected_keys: list[str] = []
    excluded_keys: list[str] = []
    for item in checklist["checklist"]:
        key = item["key"]
        if any(key.startswith(prefix) for prefix in exclude_prefixes):
            excluded_keys.append(key)
            continue
        patch = corrections.get(key)
        if patch:
            value = dict(item["value"]) if isinstance(item["value"], dict) else item["value"]
            value.update(patch)
            item = dict(item)
            item["value"] = value
            corrected_keys.append(key)
        items.append(item)
    out = dict(checklist)
    out["checklist"] = items
    return out, corrected_keys, excluded_keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--analysis-set", default=str(DEFAULT_ANALYSIS_SET))
    parser.add_argument("--corrections", default=None,
                        help="the machine-readable form of a dated correction note")
    parser.add_argument("--exclude-item-prefix", action="append", default=[],
                        help="drop the items whose key starts with this prefix")
    parser.add_argument("--prompts", nargs="*", default=None,
                        help="score only these prompts")
    parser.add_argument("--label", default="primary",
                        help="the name of this scoring, for the report")
    parser.add_argument("--out", default=None,
                        help="the scored records as JSON")
    args = parser.parse_args()

    analysis_set = json.loads(Path(args.analysis_set).read_text(encoding="utf-8"))
    corrections: dict[str, dict] = {}
    if args.corrections:
        payload = json.loads(Path(args.corrections).read_text(encoding="utf-8"))
        corrections = payload.get("corrections", {})
    checklists = load_checklists()

    scored = []
    for row in analysis_set["rows"]:
        if args.prompts and row["prompt_id"] not in args.prompts:
            continue
        checklist = checklists.get(row["prompt_id"])
        record_dir = expand_home(row["record_dir"])
        summary = json.loads((record_dir / "summary.json").read_text(encoding="utf-8"))
        if checklist is None:
            scored.append({
                "arm": row["arm"], "prompt_id": row["prompt_id"],
                "repeat": row["repeat"], "status": summary.get("status"),
                "verdict": "NO_CHECKLIST", "scripted_items": 0,
                "scripted_passed": 0, "deferred_items": 0, "items": [],
            })
            continue
        effective, corrected_keys, excluded_keys = corrected_checklist(
            checklist, corrections, args.exclude_item_prefix)
        result = score_scripted.score_answer(summary, effective)
        result["arm"] = row["arm"]
        result["source"] = row["source"]
        result["run"] = row["record_name"]
        result["corrected_items"] = corrected_keys
        result["excluded_items"] = excluded_keys
        result["steps"] = summary.get("n_steps")
        result["tokens"] = (summary.get("token_total") or {}).get("total_tokens")
        result["wall_time_s"] = summary.get("wall_time_s")
        scored.append(result)

    payload = {
        "label": args.label,
        "scored_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "analysis_set": str(Path(args.analysis_set).resolve()),
        "corrections_applied": corrections,
        "excluded_item_prefixes": args.exclude_item_prefix,
        "runs": len(scored),
        "records": scored,
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"=== {args.label} ===")
    print(f"runs scored: {len(scored)}")
    for arm in sorted({record["arm"] for record in scored}):
        rows = [record for record in scored if record["arm"] == arm]
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        scripted = sum(row["scripted_items"] for row in rows)
        passed = sum(row["scripted_passed"] for row in rows)
        deferred = sum(row["deferred_items"] for row in rows)
        detail = ", ".join(f"{count} {name}" for name, count in sorted(counts.items()))
        print(
            f"{arm}: {len(rows)} runs - {detail}; "
            f"{passed}/{scripted} scripted items passed, {deferred} deferred"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

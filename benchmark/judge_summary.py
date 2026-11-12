"""The judged layer: the qualitative verdicts per scenario and per arm.

The judge writes the verdicts per ``judge_id`` and the key file holds the
arm; neither file says which **scenario** a run belongs to (the two
scenarios share the prompt ids).  The scenarios are therefore separated
by the sha256 of the answer, which the key file carries and which the
run records reproduce exactly.

    python benchmark/judge_summary.py --judged <judged.json> --key <key.json>
        --scenario <name>=<run_dir> [...] [--out <summary.json>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SKIPPED_ARM_DIRS = {"quota_interrupted", "attempts", "logs"}


def answer_hashes(run_dir: Path) -> dict[str, tuple[str, str, int]]:
    """The sha256 of every answer of a run directory, per arm and prompt."""
    found: dict[str, tuple[str, str, int]] = {}
    for arm_dir in sorted(run_dir.iterdir()):
        if not arm_dir.is_dir():
            continue
        if arm_dir.name in SKIPPED_ARM_DIRS or arm_dir.name.startswith("_"):
            continue
        for run in sorted(arm_dir.iterdir()):
            summary_path = run / "summary.json"
            if not summary_path.is_file():
                continue
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            answer = summary.get("final_content") or ""
            digest = hashlib.sha256(answer.encode("utf-8")).hexdigest()
            found[digest] = (
                arm_dir.name,
                summary.get("prompt_id") or summary.get("id") or run.name,
                int(summary.get("repeat") or 0),
            )
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--scenario", action="append", required=True,
                        help="<name>=<run_dir>")
    parser.add_argument("--out")
    args = parser.parse_args()

    judged = json.loads(Path(args.judged).read_text(encoding="utf-8"))
    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    key_by_id = {entry["judge_id"]: entry for entry in key}

    scenarios = {}
    for item in args.scenario:
        name, _, path = item.partition("=")
        scenarios[name] = answer_hashes(Path(path))

    summary: dict[str, dict] = {}
    unmapped = 0
    for judge_id, verdict in judged.get("judged", {}).items():
        entry = key_by_id[judge_id]
        digest = entry["answer_sha256"]
        placed = False
        for name, hashes in scenarios.items():
            if digest in hashes:
                arm, prompt_id, repeat = hashes[digest]
                bucket = summary.setdefault(name, {}).setdefault(arm, {})
                bucket["pass" if verdict["verdict"] == "PASS" else "fail"] = (
                    bucket.get("pass" if verdict["verdict"] == "PASS" else "fail", 0) + 1
                )
                per_prompt = bucket.setdefault("_prompts", {})
                prompt_bucket = per_prompt.setdefault(prompt_id, {"pass": 0, "fail": 0})
                prompt_bucket["pass" if verdict["verdict"] == "PASS" else "fail"] += 1
                placed = True
                break
        if not placed:
            unmapped += 1

    for name, arms in summary.items():
        print(f"### {name}")
        for arm, bucket in sorted(arms.items()):
            prompts = bucket.pop("_prompts", {})
            passed = bucket.get("pass", 0)
            failed = bucket.get("fail", 0)
            total = passed + failed
            print(
                f"  {arm}: {passed}/{total} judged items pass "
                f"({passed / total:.3f}), {failed} fail"
            )
            for prompt_id, counts in sorted(prompts.items()):
                print(f"    {prompt_id}: {counts}")
        print()

    if unmapped:
        print(f"WARNING: {unmapped} judged items matched no scenario run")
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

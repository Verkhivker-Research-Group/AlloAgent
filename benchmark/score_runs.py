"""The scripted scoring of a run batch.

It reads the per-run summaries written by the harness
(``<out>/<prompt>/summary.json``) and scores each answer against the
committed expected values (``benchmark/dev_prompt_expected.json``): a
prompt is FULL when every value is in the answer, PARTIAL when some
are, and NONE when none is.  A missing or failed run is a FAIL, and it
is reported as such - it is never scored as a pass.

    python benchmark/score_runs.py <out_dir> [<out_dir> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXPECTED = REPO / "benchmark" / "dev_prompt_expected.json"


def score_run(summary_path: Path) -> dict:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    prompt_id = data.get("id") or summary_path.parent.name
    answer = data.get("final_content") or ""
    values = expected.get(prompt_id, {}).get("values", [])
    present = [value for value in values if value in answer]
    missing = [value for value in values if value not in present]
    status = data.get("status")
    if status != "completed":
        verdict = "FAIL"
    elif values and not missing:
        verdict = "FULL"
    elif present:
        verdict = "PARTIAL"
    else:
        verdict = "NONE"
    return {
        "id": prompt_id,
        "status": status,
        "verdict": verdict,
        "values_present": present,
        "values_missing": missing,
        "steps": data.get("n_steps"),
        "wall_time_s": data.get("wall_time_s"),
        "tokens": data.get("token_total") or {},
        "dirty": data.get("git_dirty"),
        "error": data.get("error"),
    }


def main() -> int:
    results = []
    for out_dir in sys.argv[1:]:
        base = Path(out_dir)
        for summary_path in sorted(base.glob("*/summary.json")):
            results.append(score_run(summary_path))
    lines = []
    for result in results:
        lines.append(
            f"{result['id']}: {result['verdict']} (status={result['status']}, "
            f"steps={result['steps']}, wall={result['wall_time_s']}, "
            f"tokens={result['tokens'].get('total_tokens')}, dirty={result['dirty']})"
        )
        if result["values_present"]:
            lines.append(f"    present: {result['values_present']}")
        if result["values_missing"]:
            lines.append(f"    missing: {result['values_missing']}")
        if result["error"]:
            lines.append(f"    error: {result['error']}")
    print("\n".join(lines) if lines else "no runs found")
    full = sum(1 for result in results if result["verdict"] == "FULL")
    print(f"\n{len(results)} runs: {full} FULL, "
          f"{sum(1 for r in results if r['verdict'] == 'PARTIAL')} PARTIAL, "
          f"{sum(1 for r in results if r['verdict'] == 'NONE')} NONE, "
          f"{sum(1 for r in results if r['verdict'] == 'FAIL')} FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

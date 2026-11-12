"""Mark the earlier MiniMax-M3 judge outputs as PROVISIONAL.

The judgements of 2026-10-29 were made by the same model family that
produced the answers (MiniMax-M3).  They are kept, but they are marked
**provisional**: they are not used for the report and MiniMax-M3 is not
used for the judging of the analysis set.

Nothing is deleted.  Every file keeps its verdicts and gains two fields:
``provisional`` and ``provisional_note``.  The dated note
(``benchmark/judge_outputs_provisional.md``) records which files were
marked, what they contain and why they are provisional.

    python benchmark/mark_judge_outputs_provisional.py [--temp-dir <dir>]
        [--out benchmark/judge_outputs_provisional.md]
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
DEFAULT_TEMP = expand_home(r"<HOME>\AppData\Local\Temp\opencode")

NOTE = (
    "PROVISIONAL: these verdicts were made by MiniMax-M3, the same model "
    "family that produced the answers.  They are kept as they are and are "
    "not used in the report; the analysis set is judged with another model."
)

# The files that hold verdicts (or a summary of verdicts).
OUTPUT_GLOBS = ("judged_*.json", "judged_summary*.json")
# The files that hold the batches and their keys: the inputs of the M3
# judge, which the new export supersedes.
INPUT_NAMES = (
    "judge_batch_all.json",
    "judge_batch_v6c.json",
    "judge_batch_key_all.json",
    "judge_batch_key_v6c.json",
    "judge_batch_manifest_all.json",
    "judge_batch_manifest_v6c.json",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--temp-dir", default=str(DEFAULT_TEMP))
    parser.add_argument("--out", default=str(REPO / "benchmark" / "judge_outputs_provisional.md"))
    args = parser.parse_args()

    temp = Path(args.temp_dir)
    marked = []
    seen: set[Path] = set()
    for pattern in OUTPUT_GLOBS:
        for path in sorted(temp.glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                print(f"  {path.name}: not read ({error}); skipped")
                continue
            if not isinstance(payload, dict):
                print(f"  {path.name}: not a JSON object; skipped")
                continue
            payload["provisional"] = True
            payload["provisional_note"] = NOTE
            payload["provisional_marked_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
            marked.append({
                "file": path.name,
                "model": payload.get("model"),
                "runs_judged": payload.get("runs_judged"),
                "items_judged": payload.get("items_judged"),
                "items_deferred": payload.get("items_deferred"),
                "per_arm": payload.get("per_arm"),
            })
            print(f"  marked {path.name} (model {payload.get('model')})")

    inputs = []
    for name in INPUT_NAMES:
        path = temp / name
        if path.is_file():
            inputs.append({"file": name, "bytes": path.stat().st_size})

    lines = [
        "# The earlier MiniMax-M3 judge outputs are PROVISIONAL",
        "",
        "Dated note 2026-11-02.",
        "",
        "The judgements of 2026-10-29 were made by **MiniMax-M3**, the same",
        "model family that produced the answers they judge.  The plan already",
        "names this as a limitation of the judge layer (the judge protocol of",
        "2026-10-29, point 5: the judge is the same model family that produced",
        "the answers).  These outputs are therefore **provisional**: they are",
        "kept exactly as they are, they are marked as provisional in the files",
        "themselves, and **they are not used for the report**.  MiniMax-M3 is",
        "not used to judge the analysis set.",
        "",
        "## What was marked",
        "",
        "| file | model | runs judged | items judged | items deferred |",
        "|---|---|---:|---:|---:|",
    ]
    for entry in marked:
        lines.append(
            f"| `{entry['file']}` | {entry['model']} | {entry['runs_judged']} | "
            f"{entry['items_judged']} | {entry['items_deferred']} |"
        )
    lines += [
        "",
        "Each of these files now carries `provisional: true`, a",
        "`provisional_note` and the timestamp of the marking.  **Nothing was",
        "deleted and no verdict was changed.**",
        "",
        "One file of that session is not in the directory any more:",
        "`judged_summary_by_scenario.json` (330 bytes, 2026-10-29 10:59) was",
        "listed in the inventory of the session that produced the M3 judging",
        "and is not present in `%TEMP%\\opencode` now, so it could not be",
        "marked in place.  It is named here so that the record is complete.",
        "",
        "## The inputs of that judge run (superseded, not marked in place)",
        "",
        "| file | bytes |",
        "|---|---:|",
    ]
    for entry in inputs:
        lines.append(f"| `{entry['file']}` | {entry['bytes']} |")
    lines += [
        "",
        "These are the batches, their keys and their manifests, not judge",
        "outputs: they hold no verdict.  They are the inputs of the MiniMax-M3",
        "judging and the new export of the analysis set supersedes them.",
        "",
        "## What replaces them",
        "",
        "The judge batches of the 234-run analysis set, exported with",
        "`benchmark/export_judge_batches.py` under the template's exporter",
        "requirements, and judged with a model that is not MiniMax-M3.  The",
        "masked batches keep the committed checklists as the criteria, and",
        "the arm labels stay in the separate key file.",
    ]
    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(f"  marked {len(marked)} files, listed {len(inputs)} superseded inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

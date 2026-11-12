"""The LLM judge for the qualitative checklist items.

The qualitative items (43 of the 159) are the ones a script cannot
decide.  They are judged by an LLM that reads the **masked** judge
batch (the arm label is not in it; the key file is joined only after
the judging), one call per run, with the criterion text taken verbatim
from the committed checklist.

The protocol (the dated note of 2026-10-29 in
``benchmark/analysis_plan.md``):

* one call per run, with all the qualitative items of that prompt;
* the criterion text is the committed ``value`` of the item, verbatim;
* the answer is the run's ``final_content`` - the same text the scripted
  scorer reads;
* the model is the configured one (``BIOMNI_LLM``, MiniMax-M3), the
  temperature is 0, and the judge is asked for a JSON object with one
  verdict per criterion (``PASS`` or ``FAIL``) and a short reason;
* a call that fails, or whose answer cannot be parsed, is **deferred**:
  the item is counted neither as a pass nor as a failure;
* the judge is the same model family that produced the answers, so its
  verdicts are reported as a **separate layer** from the scripted score
  and they do not replace the human subset.

The API key is read from ``MINIMAX_API_KEY`` (or the ``BIOMNI_*``
equivalent), optionally from the file named by ``ALLOAGENT_ENV_SOURCE``,
and it is never printed.

    python benchmark/run_judge.py --batch <batch.json> --key <key.json>
        --out <judged.json> [--summary <summary.json>] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from run_arm import extract_env  # noqa: E402

DEFAULT_ENV_SOURCE = str(expand_home(r"<HOME>\Documents\CPSC\Biolab\.env.extracted"))

JUDGE_PROMPT = """You are grading one answer against a list of criteria.

Rules:
- Judge ONLY what the answer states. Do not try to verify the science yourself.
- A criterion is PASS only when the answer actually contains what the criterion asks for
  (the stated value, the stated path, the stated caveat, the stated limit).
- An answer that is vague, partial, or that states the opposite is FAIL.
- Judge each criterion independently.

The question that was asked:
<question>
{prompt}
</question>

The answer to grade:
<answer>
{answer}
</answer>

The criteria:
{criteria}

Reply with a JSON object and nothing else:
{{"results": [{{"key": "<the criterion key>", "verdict": "PASS" or "FAIL", "reason": "<at most 20 words>"}}]}}
One entry per criterion, with the key exactly as given."""


def load_env(env_source: str | None) -> None:
    if os.environ.get("MINIMAX_API_KEY"):
        return
    source = Path(env_source or os.environ.get("ALLOAGENT_ENV_SOURCE") or DEFAULT_ENV_SOURCE)
    values = extract_env(source)
    for name, value in values.items():
        os.environ.setdefault(name, value)


def call_model(base: str, key: str, model: str, prompt: str, timeout: float = 300.0) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8", "replace"))
    return body["choices"][0]["message"]["content"]


def parse_verdicts(text: str) -> dict[str, dict]:
    stripped = text.strip()
    match = re.search(r"\{.*\}", stripped, re.S)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
    except ValueError:
        return {}
    results = parsed.get("results")
    if not isinstance(results, list):
        return {}
    verdicts: dict[str, dict] = {}
    for entry in results:
        if not isinstance(entry, dict):
            continue
        key = entry.get("key")
        verdict = str(entry.get("verdict", "")).strip().upper()
        if not key or verdict not in ("PASS", "FAIL"):
            continue
        verdicts[str(key)] = {
            "verdict": verdict,
            "reason": str(entry.get("reason", ""))[:200],
        }
    return verdicts


def judge_run(run: dict, base: str, key: str, model: str) -> dict:
    criteria = "\n".join(
        f"- key: {item['key']}\n  criterion: {item['criterion']}" for item in run["items"]
    )
    prompt = JUDGE_PROMPT.format(
        prompt=run["prompt"], answer=run["answer"], criteria=criteria
    )
    last_error = ""
    for attempt in range(4):
        try:
            text = call_model(base, key, model, prompt)
            verdicts = parse_verdicts(text)
            if verdicts:
                return {"run": run["opaque"], "verdicts": verdicts, "error": ""}
            last_error = "the answer could not be parsed"
        except urllib.error.HTTPError as error:
            last_error = f"HTTP {error.code}"
            if error.code == 429:
                time.sleep(30 * (attempt + 1))
                continue
            if error.code in (500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            break
        except Exception as error:  # noqa: BLE001
            last_error = f"{type(error).__name__}: {error}"
            time.sleep(5 * (attempt + 1))
    return {"run": run["opaque"], "verdicts": {}, "error": last_error}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="judge only the first N runs")
    parser.add_argument("--env-source", default=os.environ.get("ALLOAGENT_ENV_SOURCE"))
    args = parser.parse_args()

    load_env(args.env_source)
    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("BIOMNI_CUSTOM_API_KEY")
    base = os.environ.get("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
    model = os.environ.get("BIOMNI_LLM", "MiniMax-M3")
    if not api_key:
        print("no API key in the environment")
        return 2

    batch = json.loads(Path(args.batch).read_text(encoding="utf-8"))
    key_entries = json.loads(Path(args.key).read_text(encoding="utf-8"))
    key_by_id = {entry["judge_id"]: entry for entry in key_entries}

    runs: dict[str, dict] = {}
    for entry in batch:
        opaque = entry["judge_id"].rsplit("_item_", 1)[0]
        run = runs.setdefault(
            opaque,
            {
                "opaque": opaque,
                "prompt": entry["prompt"],
                "prompt_id": entry["prompt_id"],
                "answer": entry["answer"],
                "items": [],
            },
        )
        run["items"].append(
            {
                "judge_id": entry["judge_id"],
                "key": key_by_id[entry["judge_id"]]["item_key"],
                "criterion": entry["criterion"],
                "criterion_note": entry.get("criterion_note"),
            }
        )

    ordered = sorted(runs.values(), key=lambda run: run["opaque"])
    if args.limit:
        ordered = ordered[: args.limit]

    started = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(judge_run, run, base, api_key, model) for run in ordered]
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
            done += 1
            print(
                f"  [{done}/{len(ordered)}] {result['run']}: "
                f"{len(result['verdicts'])} verdicts"
                + (f" ({result['error']})" if result["error"] else "")
                + f" [{time.time() - started:.0f} s]",
                flush=True,
            )

    judged: dict[str, dict] = {}
    errors = []
    for result in results:
        if result["error"]:
            errors.append((result["run"], result["error"]))
        run = runs[result["run"]]
        for item in run["items"]:
            verdict = result["verdicts"].get(item["key"])
            if verdict:
                judged[item["judge_id"]] = verdict

    output = {
        "model": model,
        "seed_note": "the batch order is the committed shuffle seed 20261026",
        "runs_judged": len(results),
        "items_judged": len(judged),
        "items_deferred": len(batch) - len(judged),
        "judged": judged,
    }
    Path(args.out).write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"the judge: {len(results)} runs, {len(judged)} items judged, "
          f"{len(batch) - len(judged)} deferred, {len(errors)} failed calls, "
          f"{time.time() - started:.0f} s")
    for run, error in errors[:10]:
        print(f"  {run}: {error}")

    if args.summary:
        per_arm: dict[str, dict] = {}
        for judge_id, verdict in judged.items():
            arm = key_by_id[judge_id]["arm"]
            bucket = per_arm.setdefault(arm, {"pass": 0, "fail": 0})
            bucket["pass" if verdict["verdict"] == "PASS" else "fail"] += 1
        deferred_per_arm: dict[str, int] = {}
        for entry in batch:
            if entry["judge_id"] not in judged:
                arm = key_by_id[entry["judge_id"]]["arm"]
                deferred_per_arm[arm] = deferred_per_arm.get(arm, 0) + 1
        summary = {
            "model": model,
            "per_arm": {
                arm: {
                    "pass": bucket["pass"],
                    "fail": bucket["fail"],
                    "deferred": deferred_per_arm.get(arm, 0),
                    "pass_rate": bucket["pass"] / max(1, bucket["pass"] + bucket["fail"]),
                }
                for arm, bucket in sorted(per_arm.items())
            },
        }
        Path(args.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary["per_arm"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

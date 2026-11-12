"""Run the arm D development prompts once each and record the runs.

Usage (inside the container):

    python /workspace/scripts/run_dev_prompts.py \
        --prompts /workspace/docs/dev_prompts.md \
        --out /workspace/build_logs/dev_runs

Each prompt is run exactly once. Nothing here rewords a prompt or
retries a run: a failure is recorded as a failure.

The per-run JSON is written by A1 itself (record_run=True); this script
additionally writes a JSON summary of the whole batch.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import traceback
from pathlib import Path

PROMPT_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*(D\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$")


def parse_prompts(path: Path) -> list[dict[str, str]]:
    """Read the prompt table out of docs/dev_prompts.md."""
    out: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = PROMPT_ROW.match(line.strip())
        if not m:
            continue
        num, pid, prompt, tools = m.groups()
        out.append({"n": num, "id": pid, "prompt": prompt, "tools": tools})
    return out


def _configure_llm_env() -> dict:
    """Map the MINIMAX_* key onto the BIOMNI_* settings the agent reads.

    The host .env carries only ``MINIMAX_API_KEY``; ``biomni.config``
    reads ``BIOMNI_*`` at import time, so the mapping has to happen
    before biomni is imported. The key is only ever read from the
    environment and passed on -- it is never printed or written to a
    file.
    """
    key = os.environ.get("MINIMAX_API_KEY")
    if key and not os.environ.get("BIOMNI_CUSTOM_API_KEY"):
        os.environ["BIOMNI_CUSTOM_API_KEY"] = key
    os.environ.setdefault("BIOMNI_LLM", "MiniMax-M3")
    os.environ.setdefault("BIOMNI_SOURCE", "Custom")
    os.environ.setdefault("BIOMNI_CUSTOM_BASE_URL", "https://api.minimax.io/v1")
    os.environ.setdefault("BIOMNI_TEMPERATURE", "1.0")
    os.environ.setdefault("BIOMNI_TOP_P", "0.95")
    os.environ.setdefault("BIOMNI_USE_TOOL_RETRIEVER", "false")
    return {
        "model": os.environ["BIOMNI_LLM"],
        "source": os.environ["BIOMNI_SOURCE"],
        "base_url_host": os.environ["BIOMNI_CUSTOM_BASE_URL"],
        "api_key_set": bool(os.environ.get("BIOMNI_CUSTOM_API_KEY")),
    }


def _record_git_state() -> dict:
    """Publish the git state and image id the per-run record should carry.

    ``a1._git_state_for_repo`` prefers the GIT_COMMIT / GIT_BRANCH /
    GIT_DIRTY env vars, and inside the container the bind-mounted repo is
    owned by the host user, so ``git`` refuses to read it ("dubious
    ownership") and the recorded commit would be "unknown". Resolving
    the state here and exporting it is the mechanism the docstring in
    ``a1.py`` describes.
    """
    import subprocess

    def _git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", "-c", "safe.directory=*", "-C", "/workspace", *args],
                capture_output=True, text=True, timeout=30,
            )
            return out.stdout.strip() if out.returncode == 0 else None
        except Exception:
            return None

    commit = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    status = _git("status", "--porcelain")
    dirty = "1" if status else "0"
    if commit:
        os.environ["GIT_COMMIT"] = commit
    if branch:
        os.environ["GIT_BRANCH"] = branch
    os.environ["GIT_DIRTY"] = dirty
    os.environ.setdefault("ALLOAGENT_IMAGE_ID", "unknown")
    return {
        "git_commit": commit or "unknown",
        "git_branch": branch or "unknown",
        "git_dirty": bool(status),
        "image_id": os.environ["ALLOAGENT_IMAGE_ID"],
    }


def _completed_record(summary_path: Path) -> dict | None:
    """The record of an already completed run, or None.

    The batch is resumable: a prompt whose summary.json records a
    completed run is kept, and the run is not repeated.
    """
    if not summary_path.is_file():
        return None
    try:
        previous = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not previous or previous.get("status") != "completed":
        return None
    previous["resumed"] = True
    return previous


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data-path", default="/workspace/data")
    ap.add_argument(
        "--no-resume",
        action="store_true",
        help="Re-run the prompts whose records are already complete.",
    )
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    # The agent writes scratch files into its working directory. Inside
    # the container the working directory is the bind-mounted repo, so
    # those files would land in the source tree and dirty it. Run from a
    # scratch directory instead; the tools address their data by
    # absolute path, so nothing depends on the CWD.
    # The agent writes scratch files into its working directory. Inside
    # the container the working directory is the bind-mounted repo, so
    # those files would land in the source tree and dirty it. Run from a
    # scratch directory instead; the tools address their data by
    # absolute path, so nothing depends on the CWD.
    scratch = Path(os.environ.get("ALLOAGENT_SCRATCH_DIR", "/tmp/agent_cwd"))
    scratch.mkdir(parents=True, exist_ok=True)
    os.chdir(scratch)
    print(f"agent working directory: {scratch}")

    llm_env = _configure_llm_env()
    git_state = _record_git_state()
    print(f"llm configured: {llm_env}")
    print(f"git state: {git_state}")

    from biomni.agent.a1 import A1
    from biomni.eval_settings import (
        DB_TOOL_TEMPERATURE, TEMPERATURE, TOP_P, USE_TOOL_RETRIEVER,
    )

    prompts = parse_prompts(args.prompts)
    print(f"parsed {len(prompts)} prompts from {args.prompts}")

    agent = A1(
        path=args.data_path,
        use_tool_retriever=USE_TOOL_RETRIEVER,
        record_run=True,
        reasoning_split=True,
        expected_data_lake_files=[],
    )
    # The baseline arm has no exposed list (it has no apply_exposed_tools),
    # so it runs with the tool set its own agent was built with.
    try:
        from biomni.tool._registration import apply_exposed_tools
    except ImportError:
        apply_exposed_tools = None
    if apply_exposed_tools is None:
        print("no apply_exposed_tools in this arm: using the arm's own tool set")
        module2api = getattr(agent, "module2api", None) or {}
        exposed_tool_count = sum(len(apis) for apis in module2api.values())
        print(f"the arm's own tool set: {exposed_tool_count} tools")
    else:
        summary = apply_exposed_tools(agent)
        exposed_tool_count = len(summary["exposed"])
        print(
            f"exposed {len(summary['exposed'])} tools, "
            f"hidden {len(summary['hidden'])}, unknown {summary['unknown']}"
        )

    results = []
    for entry in prompts:
        pid = entry["id"]
        run_dir = args.out / pid
        run_dir.mkdir(parents=True, exist_ok=True)
        summary_path = run_dir / "summary.json"
        if not args.no_resume:
            previous = _completed_record(summary_path)
            if previous is not None:
                print(f"\n=== {pid} ===\nalready completed, keeping the record")
                results.append(previous)
                continue
        agent.run_output_path = str(run_dir / "run.json")
        print(f"\n=== {pid} ===\n{entry['prompt']}")
        t0 = time.time()
        record = {
            "id": pid,
            "prompt": entry["prompt"],
            "expected_tools": entry["tools"],
            "exposed_tool_count": exposed_tool_count,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            log, content = agent.go(entry["prompt"])
            record["status"] = "completed"
            record["final_content"] = str(content)[:4000]
            record["log_len"] = len(log) if log else 0
        except Exception as exc:  # noqa: BLE001 - a failed run is data
            record["status"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
            record["traceback"] = traceback.format_exc()[-4000:]
        record["elapsed_s"] = round(time.time() - t0, 2)

        run_json = run_dir / "run.json"
        if run_json.is_file():
            try:
                data = json.loads(run_json.read_text(encoding="utf-8"))
                record["run_json"] = str(run_json)
                record["n_steps"] = data.get("n_steps")
                record["token_total"] = data.get("token_total")
                record["config"] = data.get("config")
                record["git_commit"] = data.get("git_commit")
                record["git_branch"] = data.get("git_branch")
                record["git_dirty"] = data.get("git_dirty")
                record["image_id"] = data.get("image_id")
                record["wall_time_s"] = data.get("wall_time_s")
                record["messages_recorded"] = len(data.get("messages") or [])
                record["tool_calls"] = [
                    tc.get("name")
                    for m in (data.get("messages") or [])
                    for tc in (m.get("tool_calls") or [])
                ]
            except (OSError, ValueError) as exc:
                record["run_json_error"] = repr(exc)
        else:
            record["run_json"] = None
            record["run_json_error"] = "no per-run JSON was written"

        (run_dir / "summary.json").write_text(
            json.dumps(record, indent=2, default=str), encoding="utf-8"
        )
        answer_text = str(record.get("final_content") or "")
        (run_dir / "answer.txt").write_text(answer_text, encoding="utf-8")
        (run_dir / "trace.txt").write_text(
            "\n".join(str(entry) for entry in (log or [])), encoding="utf-8"
        )
        results.append(record)
        print(
            f"--- {pid}: {record['status']} in {record['elapsed_s']}s "
            f"steps={record.get('n_steps')} "
            f"tokens={record.get('token_total')}"
        )

    batch = {
        "llm_env": llm_env,
        "git_state": git_state,
        "prompts": len(results),
        "completed": sum(1 for r in results if r["status"] == "completed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
    }
    (args.out / "batch_summary.json").write_text(
        json.dumps(batch, indent=2, default=str), encoding="utf-8"
    )
    print(f"\n{batch['completed']}/{batch['prompts']} completed, "
          f"{batch['failed']} failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

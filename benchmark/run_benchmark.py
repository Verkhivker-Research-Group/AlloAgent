"""Run ONE benchmark prompt in the container and record the run.

This is the harness of the benchmark launch. It is mounted into the
container by ``scripts/run_arm.py`` and is deliberately self-contained:
in the baseline arm ``/workspace`` is the baseline worktree, which has no
``scripts/`` directory, so the harness cannot import anything from the
arm's tree.

Three rules make a launch record trustworthy, and this script enforces
all three:

* the benchmark inputs (the prompt table, the validated checklists and
  the restricted prompt set) are read from the READ-ONLY launch
  checkout that is mounted at ``--benchmark-dir``, never from a copy
  baked into the image, and their sha256 are checked against the
  expected values before anything runs;
* every record carries the launch manifest: the launch tag, the commit
  of the arm's own checkout, the image digest and the three hashes;
* the record says whether the arm's working tree was dirty. A dirty
  tree is recorded (it is a fact about the run) but the harness says so
  loudly, because a dirty run is not provenance-clean.

A provider quota error is not a failed run: the status is
``quota_interrupted`` and the driver repeats the run from scratch after
the pause.

    python /harness/run_benchmark.py --benchmark-dir /launch/benchmark \
        --prompt-id S01 --repeat 1 --out /runs/alloagent \
        --launch-tag <tag> --image-digest sha256:... \
        --expected-sha256 '{"benchmark_draft.json": "...", ...}'
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

# The harness and the shared helper module sit next to each other in
# the mounted harness directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_launch  # noqa: E402  (the path is set up above)


def _configure_llm_env() -> dict:
    """Map the MINIMAX_* key onto the BIOMNI_* settings the agent reads.

    ``biomni.config`` reads the BIOMNI_* variables at import time, so
    the mapping has to happen before biomni is imported. The key is
    only ever read from the environment and passed on - it is never
    printed and never written to a file.
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


def _git(workspace: str, *args: str) -> str | None:
    """One git call in the arm's checkout; None when it fails."""
    try:
        out = subprocess.run(
            ["git", "-c", "safe.directory=*", "-C", workspace, *args],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _record_git_state(workspace: str) -> dict:
    """Publish the git state and the image id the record should carry.

    ``a1._git_state_for_repo`` prefers the GIT_COMMIT / GIT_BRANCH /
    GIT_DIRTY env vars, and inside the container the bind-mounted
    checkout is owned by the host user, so ``git`` refuses to read it
    ("dubious ownership") and the recorded commit would be "unknown".
    Resolving the state here and exporting it is the mechanism the
    docstring in ``a1.py`` describes.
    """
    commit = _git(workspace, "rev-parse", "HEAD")
    branch = _git(workspace, "rev-parse", "--abbrev-ref", "HEAD")
    status = _git(workspace, "status", "--porcelain")
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


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _find_prompt(benchmark_dir: Path, prompt_id: str) -> dict | None:
    """The prompt row of the draft, or None."""
    draft = _load_json(benchmark_dir / "benchmark_draft.json")
    for row in draft:
        if row.get("id") == prompt_id:
            return row
    return None


def _find_prompt_in_file(path: Path, prompt_id: str) -> dict | None:
    """The prompt row of a JSON prompt file, or None."""
    rows = _load_json(path)
    for row in rows:
        if row.get("id") == prompt_id:
            return row
    return None


def _find_checklist(benchmark_dir: Path, prompt_id: str) -> dict | None:
    """The checklist entry of the prompt, or None."""
    checklists = _load_json(benchmark_dir / "checklists.json")
    for row in checklists.get("prompts", []):
        if row.get("id") == prompt_id:
            return row
    return None


def _dev_expected(benchmark_dir: Path, prompt_id: str) -> dict | None:
    """The committed development expectations of the prompt, or None.

    The development prompts (the pipeline smoke) are scored against
    ``benchmark/dev_prompt_expected.json``; the benchmark prompts are
    scored against their checklist.
    """
    path = benchmark_dir / "dev_prompt_expected.json"
    if not path.is_file():
        return None
    return _load_json(path).get(prompt_id)


def _install_progress_writer(agent, path: Path) -> None:
    """Write the live progress of the run, one line per step.

    The record of a run is written when the run ends, so a driver that
    watches a run needs a live source: this wrapper of the agent's
    stream writes the step number, the cumulative tokens and the last
    tool that was called.  The agent's own code is not touched - the
    harness wraps the stream it drives.  A failure here must never break
    a run, so every step of the installation is guarded.
    """
    try:
        extract = getattr(agent, "_extract_token_usage", None)
        original = agent.app.stream
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: no live progress for this run: {exc!r}")
        return

    def stream_with_progress(*args, **kwargs):
        step = 0
        total = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        started = time.perf_counter()
        for state in original(*args, **kwargs):
            step += 1
            try:
                message = state["messages"][-1]
            except Exception:  # noqa: BLE001
                message = None
            usage = {}
            if callable(extract) and message is not None:
                try:
                    usage = extract(message) or {}
                except Exception:  # noqa: BLE001
                    usage = {}
            for name in ("input_tokens", "output_tokens", "total_tokens"):
                value = usage.get(name)
                if isinstance(value, (int, float)):
                    total[name] = total.get(name, 0) + int(value)
            last_tool = None
            for call in getattr(message, "tool_calls", None) or []:
                last_tool = getattr(call, "name", None) or last_tool
            if last_tool is None:
                name = getattr(message, "name", None)
                if name and type(message).__name__ != "AIMessage":
                    last_tool = name
            if last_tool is None:
                content = getattr(message, "content", None)
                if isinstance(content, str):
                    blocks = re.findall(r"<execute>(.*?)</execute>", content, re.S)
                    for block in reversed(blocks):
                        lines = [
                            line.strip()
                            for line in block.strip().splitlines()
                            if line.strip() and not line.strip().startswith("#")
                        ]
                        if lines:
                            last_tool = lines[0].split()[0]
                            break
            line = {
                "step": step,
                "elapsed_s": round(time.perf_counter() - started, 3),
                "cumulative_tokens": dict(total),
                "last_tool": last_tool,
            }
            try:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(line) + "\n")
            except OSError:
                pass
            yield state

    try:
        agent.app.stream = stream_with_progress
        return
    except Exception:  # noqa: BLE001
        pass
    try:
        type(agent.app).stream = stream_with_progress
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: no live progress for this run: {exc!r}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--benchmark-dir", default="/launch/benchmark",
                        help="the read-only mount with the benchmark inputs")
    parser.add_argument("--prompt-source", choices=("benchmark", "file"),
                        default="benchmark")
    parser.add_argument("--prompt-file", default=None,
                        help="a JSON list of {id, prompt} rows "
                             "(--prompt-source file)")
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--out", required=True,
                        help="the output directory of this arm")
    parser.add_argument("--launch-tag", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--expected-sha256", required=True,
                        help="a JSON object: file name -> expected sha256")
    parser.add_argument("--data-path", default="/workspace/data")
    parser.add_argument("--workspace", default="/workspace",
                        help="the arm's own checkout (its code and its git state)")
    args = parser.parse_args(argv)

    benchmark_dir = Path(args.benchmark_dir)

    # 1. The benchmark inputs must be the ones the launch committed.
    expected = json.loads(args.expected_sha256)
    try:
        actual = benchmark_launch.manifest_for_dir(benchmark_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 3
    mismatches = [
        f"  {name}: expected {expected.get(name)!r}, got {actual[name]}"
        for name in benchmark_launch.BENCHMARK_FILES
        if expected.get(name) != actual[name]
    ]
    if mismatches:
        print("ERROR: the benchmark inputs are not the committed ones:\n"
              + "\n".join(mismatches))
        return 3

    # 2. The prompt.
    if args.prompt_source == "file":
        if not args.prompt_file:
            print("ERROR: --prompt-source file needs --prompt-file")
            return 4
        row = _find_prompt_in_file(Path(args.prompt_file), args.prompt_id)
    else:
        row = _find_prompt(benchmark_dir, args.prompt_id)
    if row is None:
        print(f"ERROR: no prompt {args.prompt_id} in the benchmark inputs")
        return 4
    prompt = row.get("prompt")
    if not prompt:
        print(f"ERROR: the prompt {args.prompt_id} has no text")
        return 4

    # 3. The checklist. A benchmark prompt without a checklist is never
    #    run; a development prompt (the pipeline smoke) is scored
    #    against the committed development expectations instead.
    checklist = _find_checklist(benchmark_dir, args.prompt_id)
    if checklist is None and args.prompt_source == "benchmark":
        print(f"ERROR: {args.prompt_id} has no checklist; it is not run")
        return 5
    dev_expected = _dev_expected(benchmark_dir, args.prompt_id)

    llm_env = _configure_llm_env()
    git_state = _record_git_state(args.workspace)
    print(f"llm configured: {llm_env}")
    print(f"git state: {git_state}")
    if git_state["git_dirty"]:
        print("WARNING: the arm's working tree is DIRTY; this run is not "
              "provenance-clean and the record will say so")

    from biomni.agent.a1 import A1
    from biomni.eval_settings import (
        DB_TOOL_TEMPERATURE, TEMPERATURE, TOP_P, USE_TOOL_RETRIEVER,
    )

    # The agent writes scratch files into its working directory, so it
    # runs from a scratch directory outside the mounted checkout: a run
    # must not be able to dirty the launch checkout. Every run gets its
    # own scratch directory, because four runs share the host.
    scratch_root = Path(os.environ.get("ALLOAGENT_SCRATCH_DIR", "/tmp/agent_cwd"))
    scratch = scratch_root / f"{args.prompt_id}_r{args.repeat}_{os.getpid()}"
    scratch.mkdir(parents=True, exist_ok=True)
    os.chdir(scratch)
    print(f"agent working directory: {scratch}")

    run_dir = Path(args.out) / f"{args.prompt_id}_r{args.repeat}"
    run_dir.mkdir(parents=True, exist_ok=True)

    agent = A1(
        path=args.data_path,
        use_tool_retriever=USE_TOOL_RETRIEVER,
        record_run=True,
        reasoning_split=True,
        expected_data_lake_files=[],
    )
    try:
        from biomni.tool._registration import apply_exposed_tools
    except ImportError:
        apply_exposed_tools = None
    if apply_exposed_tools is None:
        print("no apply_exposed_tools in this arm: using the arm's own tool set")
        module2api = getattr(agent, "module2api", None) or {}
        exposed_tool_count = sum(len(apis) for apis in module2api.values())
    else:
        summary = apply_exposed_tools(agent)
        exposed_tool_count = len(summary["exposed"])
        print(
            f"exposed {len(summary['exposed'])} tools, "
            f"hidden {len(summary['hidden'])}, unknown {len(summary['unknown'])}"
        )

    agent.run_output_path = str(run_dir / "run.json")
    _install_progress_writer(agent, run_dir / "progress.jsonl")
    print(f"\n=== {args.prompt_id} (repeat {args.repeat}) ===\n{prompt}")

    record: dict = {
        "id": args.prompt_id,
        "prompt_id": args.prompt_id,
        "repeat": args.repeat,
        "prompt": prompt,
        "expected_tools": row.get("d_tools_expected") or row.get("expected_tools"),
        "checklist_status": checklist.get("status") if checklist else None,
        "checklist_keys": (
            [item.get("key") for item in checklist.get("checklist", [])]
            if checklist else []
        ),
        "dev_expected_values": (
            [value for value in (dev_expected or {}).get("values", [])]
        ),
        "exposed_tool_count": exposed_tool_count,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    t0 = time.time()
    log: list | None = None
    try:
        log, content = agent.go(prompt)
        record["status"] = "completed"
        record["final_content"] = str(content)[:20000]
        record["log_len"] = len(log) if log else 0
    except Exception as exc:  # noqa: BLE001 - a failed run is data
        kind = benchmark_launch.classify_provider_error(f"{exc}")
        if kind is None:
            kind = benchmark_launch.classify_provider_error(traceback.format_exc())
        record["status"] = "quota_interrupted" if kind else "failed"
        record["error_kind"] = kind
        record["error"] = f"{type(exc).__name__}: {exc}"
        # The client hides the transport error behind a generic message,
        # so the cause is recorded: it is what tells a throttled provider
        # apart from a blocked egress.
        cause = exc.__cause__ or exc.__context__
        if cause is not None:
            record["error_cause"] = f"{type(cause).__name__}: {cause}"[:1000]
        record["traceback"] = traceback.format_exc()[-4000:]
    record["elapsed_s"] = round(time.time() - t0, 2)

    run_json = run_dir / "run.json"
    if run_json.is_file():
        try:
            data = json.loads(run_json.read_text(encoding="utf-8"))
            record["n_steps"] = data.get("n_steps")
            record["token_total"] = data.get("token_total")
            record["config"] = data.get("config")
            record["git_commit"] = data.get("git_commit") or git_state["git_commit"]
            record["git_branch"] = data.get("git_branch") or git_state["git_branch"]
            record["git_dirty"] = data.get("git_dirty")
            if record["git_dirty"] is None:
                record["git_dirty"] = git_state["git_dirty"]
            record["image_id"] = data.get("image_id") or git_state["image_id"]
            record["wall_time_s"] = data.get("wall_time_s")
            record["messages_recorded"] = len(data.get("messages") or [])
        except (OSError, ValueError) as exc:
            record["run_json_error"] = repr(exc)
    else:
        record["run_json"] = None
        record["run_json_error"] = "no per-run JSON was written"
    record.setdefault("git_commit", git_state["git_commit"])
    record.setdefault("git_branch", git_state["git_branch"])
    record.setdefault("git_dirty", git_state["git_dirty"])
    record.setdefault("image_id", git_state["image_id"])

    record["launch_manifest"] = benchmark_launch.build_launch_manifest(
        launch_tag=args.launch_tag,
        commit=record.get("git_commit") or "unknown",
        image_digest=args.image_digest,
        benchmark_sha256=actual,
    )

    (run_dir / "summary.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8"
    )
    (run_dir / "answer.txt").write_text(
        str(record.get("final_content") or ""), encoding="utf-8"
    )
    (run_dir / "trace.txt").write_text(
        "\n".join(str(entry) for entry in (log or [])), encoding="utf-8"
    )

    problems = benchmark_launch.validate_record_provenance(record)
    if problems:
        print("ERROR: the record does not satisfy the provenance contract: "
              + benchmark_launch.format_problems(problems))

    print(
        f"--- {args.prompt_id}: {record['status']} in {record['elapsed_s']}s "
        f"steps={record.get('n_steps')} tokens={record.get('token_total')}"
    )
    if record.get("error_kind"):
        print(f"--- {args.prompt_id}: quota-interrupted "
              f"({record['error_kind']}); the driver repeats it from scratch")
    if problems:
        return 6
    return 1 if record["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())

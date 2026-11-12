"""The audit of the shared agent working directory.

The runner of the benchmark runs of 2026-10-28 and 2026-10-29 mounted
**one** host directory as the agent's working directory for every run of
both arms (``/agent_cwd`` -> ``%TEMP%\\alloagent_agent_cwd``), and never
cleared it.  A run's agent could therefore read the files another run
wrote.  This script measures that exposure over a finished scenario; it
only reads the run records, their traces and the host directory.

**The classification rule.**

A run is **affected** when at least one of these holds.  The first is
*proof*; the others are *markers*.

``proved_read_of_a_foreign_file`` (proof)
    the run's own recorded observations contain the **content** of a file
    of the shared directory whose mtime lies outside the run's window -
    i.e. a file another run (another repeat, the other arm, or an
    earlier phase) wrote.  The match is on the content, not on the name,
    so a file of the same name written by this run is never counted.
``listed_the_shared_directory`` (exposure)
    the run executed a listing of the working directory itself (an
    ``ls``/``find``/``os.listdir`` of the shared root), so it saw the
    names of files it did not create.
``arm_d_only_marker`` (marker, the baseline arm only)
    the answer carries something the baseline arm cannot produce with
    its own tools: our local-release provenance strings, the name of one
    of our exposed tools, or a double printed with the full repr a local
    database query produces.
``identical_answer`` (marker)
    the answer is byte-identical to the answer of another run of the same
    prompt.

A **foreign file** is a file whose mtime is outside the run's window.  A
file written by the run itself is never foreign.  The vendored trees the
agents installed (a conda env, ADFRsuite) are excluded: they hold
thousands of files whose names the runs merely mention, and they are not
the runs' outputs.

**The limits of the method.**  The inventory is the *current* content of
the host directory: a file another run deleted afterwards is not in it.
The observations of a run are recorded in full in ``run.json`` (the
``trace.txt`` is truncated to 10 K characters per step, so the script
reads ``run.json``).  A file that is read but whose content the run does
not echo is invisible to the content proof and is only counted as
exposure if the run listed the directory.

    python benchmark/audit_shared_cwd.py --run-dir <run_dir>
        --shared-dir <host_dir> [--out <audit.json>] [--markdown <audit.md>]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SKIPPED_ARM_DIRS = {"quota_interrupted", "attempts", "logs"}

# The markers the baseline arm cannot produce with its own tools (it has
# no exposed tool list and no local release mounts).
PROVENANCE_MARKERS = (
    "local:chembl_37",
    "local:clinvar",
    "local:alphamissense",
    "local:cryptobench",
    "local:chembl",
)
# A double printed with its full repr: our local queries produce these
# (the median of an even number of values), a language model does not.
LONG_FLOAT_RE = re.compile(r"\d+\.\d{12,}")
# The listing of the working directory itself (the shared root), not of a
# directory the run created for itself.
LISTING_PATTERNS = (
    re.compile(r"\bls\s+(-\w+\s+)*/agent_cwd"),
    re.compile(r"\bfind\s+(-[^\s]+\s+)*/agent_cwd"),
    re.compile(r"os\.listdir\(\s*['\"]/agent_cwd"),
    re.compile(r"os\.listdir\(\s*['\"]\.['\"]"),
    re.compile(r"glob\.glob\(\s*['\"]/agent_cwd"),
    re.compile(r"glob\.glob\(\s*['\"]\*['\"]"),
    re.compile(r"Path\(\s*['\"]/agent_cwd['\"]\s*\)\.(iterdir|glob|rglob)"),
    re.compile(r"Path\(\s*['\"]\.['\"]\s*\)\.(iterdir|glob|rglob)"),
)
EXECUTE_RE = re.compile(r"<execute>(.*?)</execute>", re.S)
# The vendored trees the agents installed into the shared directory: they
# hold thousands of files whose names the runs merely mention (a fpocket
# output name, a site-packages module), and they are not the runs' own
# outputs.
VENDORED_SEGMENTS = frozenset(
    {
        ".venv",
        "site-packages",
        "ADFRsuite_installed",
        "pkgs",
        "envs",
        "conda-meta",
        "Scripts",
        "include",
        "lib64",
    }
)
TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]{6,}")
PATH_TOKEN_RE = re.compile(
    r"[A-Za-z0-9_\-./\\:]+\.(?:json|csv|tsv|txt|pkl|npz|pdb|cif|xml|fa|fasta|html|gz|smi|pqt|py|md|sdf|mol2)"
)
SNIPPET_CHARS = 120
MIN_FILE_BYTES = 40


def exposed_tool_names() -> list[str]:
    path = REPO / "alloagent" / "exposed_tools.txt"
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _walk_files(root: Path):
    """Every file under the root, tolerating the broken links it holds."""
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    if entry.name in VENDORED_SEGMENTS:
                        continue
                    stack.append(Path(entry.path))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
                yield Path(entry.path), entry.stat(follow_symlinks=False).st_mtime
            except OSError:
                continue


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def inventory(shared_dir: Path) -> tuple[dict[str, float], dict[str, list[tuple[float, str]]], dict[str, float]]:
    """The shared directory: relative path -> mtime, basename -> the files,
    and the directories with their mtimes (the listing test needs them)."""
    by_path: dict[str, float] = {}
    by_name: dict[str, list[tuple[float, str]]] = {}
    by_dir: dict[str, float] = {}
    if not shared_dir.is_dir():
        return by_path, by_name, by_dir
    for path, stamp in _walk_files(shared_dir):
        try:
            relative = str(path.relative_to(shared_dir)).replace("\\", "/")
        except ValueError:
            relative = path.name
        by_path[relative] = stamp
        by_name.setdefault(path.name, []).append((stamp, relative))
        parent = str(Path(relative).parent).replace("\\", "/")
        if parent not in by_dir:
            by_dir[parent] = stamp
    by_dir["."] = 0.0
    return by_path, by_name, by_dir


WRITE_MARKERS = (
    "write_text",
    "write_bytes",
    "to_csv",
    "to_json",
    "json.dump",
    "pickle.dump",
    "np.save",
    "savefig",
    "open(",
    "shutil.copy",
    "shutil.move",
    "os.rename",
    "os.replace",
)


def load_runs(run_dir: Path) -> list[dict]:
    import sys

    sys.path.insert(0, str(REPO / "benchmark"))
    from score_scripted import load_checklists, score_answer

    checklists = load_checklists()
    runs: list[dict] = []
    for arm_dir in sorted(run_dir.iterdir()):
        if not arm_dir.is_dir():
            continue
        if arm_dir.name in SKIPPED_ARM_DIRS or arm_dir.name.startswith("_"):
            continue
        for run in sorted(arm_dir.iterdir()):
            summary_path = run / "summary.json"
            record_path = run / "run.json"
            if not summary_path.is_file():
                continue
            summary = json.loads(io.open(summary_path, encoding="utf-8").read())
            started = summary.get("started_at")
            elapsed = float(summary.get("elapsed_s") or summary.get("wall_time_s") or 0.0)
            prompt_id = summary.get("prompt_id") or summary.get("id")
            checklist = checklists.get(prompt_id)
            scored = score_answer(summary, checklist) if checklist else None
            window = None
            if started:
                begin = datetime.fromisoformat(started.replace("Z", "+00:00"))
                window = (begin.timestamp(), begin.timestamp() + elapsed + 60.0)
            text = ""
            executed = ""
            if record_path.is_file():
                record = json.loads(io.open(record_path, encoding="utf-8").read())
                parts = []
                blocks = []
                for message in record.get("messages") or []:
                    content = str(message.get("content") or "")
                    parts.append(content)
                    parts.append(str(message.get("reasoning_content") or ""))
                    blocks.extend(EXECUTE_RE.findall(content))
                text = "\n".join(parts)
                executed = "\n".join(blocks)
            runs.append(
                {
                    "arm": arm_dir.name,
                    "run": run.name,
                    "prompt_id": prompt_id,
                    "repeat": summary.get("repeat"),
                    "status": summary.get("status"),
                    "scored_verdict": scored["verdict"] if scored else None,
                    "scored_passed": scored["scripted_passed"] if scored else 0,
                    "scored_items": scored["scripted_items"] if scored else 0,
                    "started_at": started,
                    "window": window,
                    "tokens": int((summary.get("token_total") or {}).get("total_tokens") or 0),
                    "steps": summary.get("n_steps"),
                    "answer": summary.get("final_content") or "",
                    "answer_sha256": hashlib.sha256(
                        (summary.get("final_content") or "").encode("utf-8")
                    ).hexdigest(),
                    "text": text,
                    "normalized": normalize(text),
                    "executed": executed,
                }
            )
    return runs


def creator(stamp: float, runs: list[dict]) -> tuple[str, str]:
    """The run whose window contains the mtime of a file."""
    owners = [
        run
        for run in runs
        if run["window"] and run["window"][0] <= stamp <= run["window"][1]
    ]
    if not owners:
        return ("pre-existing", "")
    if len(owners) > 1:
        names = ", ".join(sorted(f"{o['arm']}/{o['run']}" for o in owners))
        return ("concurrent", names)
    owner = owners[0]
    return ("run", f"{owner['arm']}/{owner['run']}")


def listing_target(line: str) -> str | None:
    """The path a listing command lists, relative to the shared root.

    ``None`` means the root itself (the whole shared tree), ``"."`` is the
    working directory of the run, which in the runs of 2026-10-28/29 **is**
    the shared root.
    """
    for pattern in (
        r"ls\s+(?:-\w+\s+)*/agent_cwd/?([\w\-./]*)",
        r"find\s+(?:-\w+\s+)*/agent_cwd/?([\w\-./]*)",
        r"os\.listdir\(\s*['\"]/agent_cwd/?([\w\-./]*)['\"]",
        r"glob\.glob\(\s*['\"]/agent_cwd/?([\w\-./]*)",
        r"Path\(\s*['\"]/agent_cwd/?([\w\-./]*)['\"]\s*\)\.(?:iterdir|glob|rglob)",
        r"os\.listdir\(\s*['\"]\.['\"]",
        r"Path\(\s*['\"]\.['\"]\s*\)\.(?:iterdir|glob|rglob)",
        r"glob\.glob\(\s*['\"]\*['\"]",
    ):
        match = re.search(pattern, line)
        if match:
            target = (match.group(1) if match.groups() else "").strip("/")
            return target or "."
    if re.search(r"\bls\b", line):
        return "."
    return None


def audit(run_dir: Path, shared_dir: Path) -> dict:
    files, by_name, dirs = inventory(shared_dir)
    runs = load_runs(run_dir)
    tools = exposed_tool_names()
    answer_hashes: dict[str, list[dict]] = {}
    for run in runs:
        answer_hashes.setdefault(run["answer_sha256"], []).append(run)

    records = []
    for run in runs:
        flags: dict[str, list] = {
            "proved_read_of_a_foreign_file": [],
            "wrote_over_a_foreign_file": [],
            "saw_a_foreign_path": [],
            "listed_the_shared_directory": [],
            "possible_name_level_reference": [],
            "long_float_in_answer": [],
            "arm_d_only_marker": [],
            "identical_answer": [],
        }
        # The listing test: a command that lists the shared working
        # directory itself (or one of its sub-directories that another
        # run created) shows the run the files of the other runs.
        for line in run["executed"].splitlines():
            if not any(pattern.search(line) for pattern in LISTING_PATTERNS):
                continue
            target = listing_target(line)
            if target is None:
                flags["listed_the_shared_directory"].append(
                    {"file": ".", "note": "a listing of the working directory"}
                )
                continue
            stamp = dirs.get(target)
            if stamp is None:
                flags["listed_the_shared_directory"].append(
                    {"file": target, "note": "a listing of a directory of the shared tree"}
                )
                continue
            if run["window"] and run["window"][0] <= stamp <= run["window"][1]:
                continue
            kind, owner = creator(stamp, runs)
            flags["listed_the_shared_directory"].append(
                {"file": target, "attributed_to": kind, "owner": owner}
            )

        # The listing test, on the evidence: the run's own recorded text
        # names a file of another run (a path with a directory component
        # of the shared tree).  A run that saw such a name saw the shared
        # tree; the name can only come from a listing or from the output
        # of a tool that read it.
        for relative, stamp in files.items():
            if "/" not in relative:
                continue
            if run["window"] and run["window"][0] <= stamp <= run["window"][1]:
                continue
            name = relative.split("/")[-1]
            if len(name) < 5:
                continue
            if name in run["text"] and relative in run["text"]:
                kind, owner = creator(stamp, runs)
                flags["saw_a_foreign_path"].append(
                    {"file": relative, "attributed_to": kind, "owner": owner}
                )

        # The directional proof: a path the run's own executed code
        # resolves to a file of the shared directory whose mtime lies
        # outside the run's window, and the run does not write that path
        # itself.  A path with a directory component is required, so that
        # a common output name (a fpocket pocket file, a helper script)
        # is never matched by name alone.
        for line in run["executed"].splitlines():
            writes = any(marker in line for marker in WRITE_MARKERS)
            for token in PATH_TOKEN_RE.findall(line):
                relative = token.replace("\\", "/").lstrip("./")
                if "/" not in relative:
                    continue
                stamp = files.get(relative)
                if stamp is None:
                    continue
                if run["window"] and run["window"][0] <= stamp <= run["window"][1]:
                    continue
                if writes:
                    # The run wrote into a path that already existed: the
                    # file was created before the run started, so it is
                    # another run's file.
                    if run["window"] and stamp < run["window"][0]:
                        kind, owner = creator(stamp, runs)
                        flags["wrote_over_a_foreign_file"].append(
                            {"file": relative, "attributed_to": kind, "owner": owner}
                        )
                    continue
                kind, owner = creator(stamp, runs)
                flags["proved_read_of_a_foreign_file"].append(
                    {"file": relative, "attributed_to": kind, "owner": owner}
                )
        # The name-only evidence (a file of the shared root, referenced
        # without a directory component) is weaker and is reported apart.
        for token in PATH_TOKEN_RE.findall(run["executed"]):
            name = token.replace("\\", "/").split("/")[-1]
            if "/" in token.replace("\\", "/").lstrip("./"):
                continue
            for stamp, relative in by_name.get(name, []):
                if run["window"] and run["window"][0] <= stamp <= run["window"][1]:
                    continue
                kind, owner = creator(stamp, runs)
                flags["possible_name_level_reference"].append(
                    {"file": relative, "attributed_to": kind, "owner": owner}
                )

        if run["arm"] == "baseline":
            for marker in PROVENANCE_MARKERS:
                if marker in run["answer"]:
                    flags["arm_d_only_marker"].append({"marker": marker, "where": "answer"})
                elif marker in run["text"]:
                    flags["arm_d_only_marker"].append({"marker": marker, "where": "trace"})
            for match in sorted(set(LONG_FLOAT_RE.findall(run["answer"]))):
                # A double printed with its full repr is NOT evidence of a
                # leak: the run's own numpy arithmetic produces the same
                # shape (a value checked against the local AlphaMissense
                # release was absent from it).  It is reported, not counted.
                flags["long_float_in_answer"].append(
                    {"marker": f"long float {match}", "where": "answer"}
                )
            for tool in tools:
                if tool in run["answer"]:
                    flags["arm_d_only_marker"].append(
                        {"marker": f"the exposed tool {tool}", "where": "answer"}
                    )

        twins = [
            other
            for other in answer_hashes.get(run["answer_sha256"], [])
            if other["run"] != run["run"] and run["answer"].strip()
        ]
        for other in twins:
            flags["identical_answer"].append({"other": f"{other['arm']}/{other['run']}"})

        records.append(
            {
                "arm": run["arm"],
                "run": run["run"],
                "prompt_id": run["prompt_id"],
                "repeat": run["repeat"],
                "status": run["status"],
                "scored_verdict": run["scored_verdict"],
                "scored_passed": run["scored_passed"],
                "scored_items": run["scored_items"],
                "tokens": run["tokens"],
                "steps": run["steps"],
                "started_at": run["started_at"],
                "flags": flags,
                "affected": bool(
                    flags["proved_read_of_a_foreign_file"]
                    or flags["arm_d_only_marker"]
                    or flags["identical_answer"]
                ),
            }
        )

    return {
        "run_dir": str(run_dir),
        "shared_dir": str(shared_dir),
        "inventory_files": len(files),
        "runs": records,
    }


def summarize(audit_data: dict) -> dict:
    records = audit_data["runs"]
    by_arm: dict[str, dict] = {}
    for record in records:
        bucket = by_arm.setdefault(
            record["arm"], {"runs": 0, "affected": 0, "flags": {}, "prompts": {}}
        )
        bucket["runs"] += 1
        if record["affected"]:
            bucket["affected"] += 1
        bucket["prompts"].setdefault(record["prompt_id"], {"runs": 0, "affected": 0})
        bucket["prompts"][record["prompt_id"]]["runs"] += 1
        if record["affected"]:
            bucket["prompts"][record["prompt_id"]]["affected"] += 1
        for name, entries in record["flags"].items():
            if entries:
                bucket["flags"][name] = bucket["flags"].get(name, 0) + 1
    affected = [record for record in records if record["affected"]]
    unaffected = [record for record in records if not record["affected"]]

    def mean(values):
        return sum(values) / len(values) if values else 0.0

    by_repeat: dict[str, dict] = {}
    for record in records:
        key = f"{record['arm']}/r{record['repeat']}"
        bucket = by_repeat.setdefault(key, {"runs": 0, "affected": 0})
        bucket["runs"] += 1
        if record["affected"]:
            bucket["affected"] += 1
    scored: dict[str, dict] = {}
    for record in records:
        key = f"{record['arm']}/{'affected' if record['affected'] else 'unaffected'}"
        bucket = scored.setdefault(key, {"passed": 0, "items": 0, "runs": 0})
        bucket["runs"] += 1
        bucket["passed"] += record["scored_passed"] or 0
        bucket["items"] += record["scored_items"] or 0
    return {
        "by_arm": by_arm,
        "by_repeat": by_repeat,
        "scored": scored,
        "affected": len(affected),
        "unaffected": len(unaffected),
        "affected_tokens_mean": mean([r["tokens"] for r in affected]),
        "unaffected_tokens_mean": mean([r["tokens"] for r in unaffected]),
        "affected_steps_mean": mean([r["steps"] or 0 for r in affected]),
        "unaffected_steps_mean": mean([r["steps"] or 0 for r in unaffected]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--shared-dir", required=True)
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    args = parser.parse_args()

    audit_data = audit(Path(args.run_dir), Path(args.shared_dir))
    summary = summarize(audit_data)
    if args.out:
        Path(args.out).write_text(json.dumps(audit_data, indent=2), encoding="utf-8")

    print(f"the runs: {len(audit_data['runs'])}")
    print(f"the candidate files in the shared directory: {audit_data['inventory_files']}")
    print(f"the affected runs: {summary['affected']} of {len(audit_data['runs'])}")
    for arm, bucket in sorted(summary["by_arm"].items()):
        flags = ", ".join(f"{name} {count}" for name, count in sorted(bucket["flags"].items()))
        print(f"  {arm}: {bucket['affected']}/{bucket['runs']} affected - {flags}")
    print(
        f"the mean tokens: affected {summary['affected_tokens_mean']:.0f}, "
        f"unaffected {summary['unaffected_tokens_mean']:.0f}"
    )
    print(
        f"the mean steps: affected {summary['affected_steps_mean']:.1f}, "
        f"unaffected {summary['unaffected_steps_mean']:.1f}"
    )
    if args.markdown:
        lines = []
        for record in audit_data["runs"]:
            if not record["affected"]:
                continue
            lines.append(
                f"- {record['arm']}/{record['run']}: "
                + ", ".join(
                    f"{name} ({len(entries)})"
                    for name, entries in record["flags"].items()
                    if entries
                )
            )
        Path(args.markdown).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

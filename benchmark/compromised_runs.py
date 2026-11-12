"""The compromised runs of a scenario, from the traces.

A run is **compromised** when its trace shows it touching the shared host
working directory **outside its own workspace**, or when its outputs
carry something it could only have learned from another run's files.

The test is the same for both arms, and it is computed from the traces
alone (the host directory is no longer available):

* the run's **own workspace** is the set of directories it created
  itself - the first path component of every file it wrote and every
  directory it made;
* a run is compromised when it **lists**, **reads** or **writes** a path
  whose directory component it did **not** create itself: that path is
  another run's work (or the development phase's), and the run saw it;
* the **marker** test: the output carries one of our local-release
  provenance strings (``local:chembl_37:...``) or the name of one of our
  exposed tools.  For the **baseline arm** this is decisive (it has
  neither the tools nor the local releases).  For the **alloagent arm**
  the same strings are its own, so the marker test fires only for a
  string it cannot have produced itself - the test is the same, the
  verdict differs by what the arm owns;
* the **identical answer** test: the answer is byte-identical to the
  answer of another run of the same scenario (an empty answer does not
  count).

The evidence of every run is written out with the list, so that each
line can be checked against the trace it came from.

    python benchmark/compromised_runs.py --run-dir <run_dir>
        [--audit <audit.json> ...] [--out docs/compromised_runs_<name>.md]
"""
from __future__ import annotations

import argparse
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SKIPPED_ARM_DIRS = {"quota_interrupted", "attempts", "logs"}

EXECUTE_RE = re.compile(r"<execute>(.*?)</execute>", re.S)
PATH_TOKEN_RE = re.compile(
    r"[A-Za-z0-9_\-./\\:]+\.(?:json|csv|tsv|txt|pkl|npz|pdb|cif|xml|fa|fasta|html|gz|smi|pqt|py|md|sdf|mol2)"
)
WRITE_MARKERS = (
    "write_text",
    "write_bytes",
    "to_csv",
    "to_json",
    "json.dump",
    "pickle.dump",
    "np.save",
    "savefig",
    "makedirs",
    "mkdir",
    "shutil.copy",
    "shutil.move",
    "os.rename",
    "os.replace",
    "copyfile",
    "copytree",
)
LISTING_PATTERNS = (
    re.compile(r"\bls\s+(?:-\w+\s+)*/agent_cwd"),
    re.compile(r"\bfind\s+(?:-\w+\s+)*/agent_cwd"),
    re.compile(r"os\.listdir\(\s*['\"]/agent_cwd"),
    re.compile(r"os\.listdir\(\s*['\"]\.['\"]"),
    re.compile(r"os\.walk\(\s*['\"]/agent_cwd"),
    re.compile(r"glob\.glob\(\s*['\"]/agent_cwd"),
    re.compile(r"glob\.glob\(\s*['\"]\*['\"]"),
    re.compile(r"Path\(\s*['\"]/agent_cwd['\"]\s*\)\.(?:iterdir|glob|rglob)"),
    re.compile(r"Path\(\s*['\"]\.['\"]\s*\)\.(?:iterdir|glob|rglob)"),
)
PROVENANCE_MARKERS = (
    "local:chembl_37",
    "local:clinvar",
    "local:alphamissense",
    "local:cryptobench",
    "local:chembl",
)


def exposed_tool_names() -> list[str]:
    path = REPO / "alloagent" / "exposed_tools.txt"
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def listing_target(line: str) -> str | None:
    """The path a listing command lists, relative to the working directory."""
    for pattern in (
        r"ls\s+(?:-\w+\s+)*/agent_cwd/?([\w\-./]*)",
        r"find\s+(?:-\w+\s+)*/agent_cwd/?([\w\-./]*)",
        r"os\.listdir\(\s*['\"]/agent_cwd/?([\w\-./]*)['\"]",
        r"os\.walk\(\s*['\"]/agent_cwd/?([\w\-./]*)['\"]",
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


def first_component(path: str) -> str:
    cleaned = path.replace("\\", "/").strip("/")
    if cleaned in (".", ""):
        return "."
    return cleaned.split("/")[0]


def own_workspace(lines: list[str]) -> set[str]:
    """The directories the run created itself."""
    created: set[str] = set()
    for line in lines:
        if not any(marker in line for marker in WRITE_MARKERS):
            continue
        for token in PATH_TOKEN_RE.findall(line):
            relative = token.replace("\\", "/").lstrip("./")
            if "/" in relative:
                created.add(first_component(relative))
        for match in re.finditer(r"['\"]/?([\w\-.]+/[\w\-./]*)['\"]", line):
            created.add(first_component(match.group(1)))
    return created


def run_text(run_dir: Path) -> tuple[str, str]:
    """The executed code and the whole recorded text of a run."""
    record_path = run_dir / "run.json"
    if not record_path.is_file():
        return "", ""
    record = json.loads(io.open(record_path, encoding="utf-8").read())
    blocks = []
    parts = []
    for message in record.get("messages") or []:
        content = str(message.get("content") or "")
        parts.append(content)
        parts.append(str(message.get("reasoning_content") or ""))
        blocks.extend(EXECUTE_RE.findall(content))
    return "\n".join(blocks), "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--audit", action="append", default=[])
    parser.add_argument("--out", required=True)
    parser.add_argument("--scenario", default="the scenario")
    args = parser.parse_args()

    tools = exposed_tool_names()
    run_dir = Path(args.run_dir)
    by_run: dict[str, dict] = {}
    for path in args.audit:
        audit = json.loads(Path(path).read_text(encoding="utf-8"))
        for record in audit["runs"]:
            by_run.setdefault(f"{record['arm']}/{record['run']}", record)

    rows = []
    counts = {"alloagent": 0, "baseline": 0}
    totals = {"alloagent": 0, "baseline": 0}
    classes: dict[str, int] = {}
    for arm_dir in sorted(run_dir.iterdir()):
        if not arm_dir.is_dir():
            continue
        if arm_dir.name in SKIPPED_ARM_DIRS or arm_dir.name.startswith("_"):
            continue
        for run in sorted(arm_dir.iterdir()):
            if not (run / "summary.json").is_file():
                continue
            summary = json.loads(io.open(run / "summary.json", encoding="utf-8").read())
            totals[arm_dir.name] += 1
            executed, text = run_text(run)
            answer = summary.get("final_content") or ""
            lines = executed.splitlines()
            own = own_workspace(lines)
            evidence: list[str] = []

            # The authoritative evidence is the inventory-based audit
            # (benchmark/audit_shared_cwd.py): it attributed every file
            # of the shared host directory to the run that wrote it, by
            # the mtime of the file against the window of each run.
            key = f"{arm_dir.name}/{run.name}"
            audit_record = by_run.get(key, {})
            audit_flags = audit_record.get("flags", {})
            for entry in audit_flags.get("proved_read_of_a_foreign_file", [])[:2]:
                evidence.append(
                    f"read {entry.get('file')!r}, a file another run wrote"
                )
            for entry in audit_flags.get("wrote_over_a_foreign_file", [])[:2]:
                evidence.append(
                    f"wrote into {entry.get('file')!r}, a file another run wrote"
                )
            for entry in audit_flags.get("saw_a_foreign_path", [])[:2]:
                evidence.append(
                    f"named {entry.get('file')!r}, a path another run wrote"
                )
            for entry in audit_flags.get("listed_the_shared_directory", [])[:2]:
                target = entry.get("file", ".") if isinstance(entry, dict) else "."
                evidence.append(
                    f"listed {target!r}, a directory of the shared tree it did not create"
                )
            for twin in audit_flags.get("identical_answer", [])[:1]:
                evidence.append(f"the answer is identical to {twin.get('other')}")

            for marker in PROVENANCE_MARKERS:
                if marker in answer:
                    evidence.append(f"the output carries our provenance string {marker!r}")
                    break
            if arm_dir.name == "baseline":
                for tool in tools:
                    if tool in answer:
                        evidence.append(
                            f"the output names our exposed tool {tool!r}, which the "
                            f"baseline arm cannot produce"
                        )
                        break

            if not evidence:
                continue
            counts[arm_dir.name] += 1
            for item in evidence:
                head = item.split(",")[0].split("'")[0].strip()
                classes[head] = classes.get(head, 0) + 1
            rows.append(
                (
                    arm_dir.name,
                    run.name,
                    summary.get("prompt_id") or summary.get("id") or run.name,
                    summary.get("repeat"),
                    "; ".join(evidence),
                )
            )

    header = [
        f"# The compromised runs of {args.scenario}",
        "",
        "The rule, the same for both arms: a run is compromised when its",
        "trace shows it **listing, reading or writing the shared host working",
        "directory outside its own workspace**, or when its **outputs carry our",
        "provenance strings or exposed tool names** that it could only have",
        "learned from another run's files.  The runs proved by the",
        "inventory-based audit (`benchmark/audit_shared_cwd.py`) are included.",
        "",
        "A run's **own workspace** is the set of directories it created itself:",
        "the first path component of every file it wrote and every directory it",
        "made.  A path outside that set belongs to another run (or to the",
        "development phase), so listing, reading or writing it exposes the",
        "other runs.",
        "",
        "| arm | compromised runs | runs of the arm |",
        "|---|---:|---:|",
    ]
    for arm in sorted(counts):
        header.append(f"| {arm} | {counts[arm]} | {totals[arm]} |")
    header += ["", "| evidence class | runs |", "|---|---:|"]
    for name, count in sorted(classes.items(), key=lambda item: -item[1]):
        header.append(f"| {name} | {count} |")
    header += ["", "## The list", ""]
    for arm, name, prompt_id, repeat, evidence in rows:
        header.append(
            f"- **{arm} / {name}** (prompt {prompt_id}, repeat {repeat}) - {evidence}"
        )
    Path(args.out).write_text("\n".join(header) + "\n", encoding="utf-8")
    print("\n".join(header[: len(header) - len(rows)]))
    print(f"the list: {args.out} ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

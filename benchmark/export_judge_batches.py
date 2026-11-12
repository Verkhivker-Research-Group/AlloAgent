"""Export the judge batches of the analysis set.

This is the exporter of ``benchmark/judge_prompt_template.md``.  It takes
the **analysis set** (``benchmark/analysis_set.json``: the 174 original
runs that are not compromised plus the 60 reruns, the last attempt of
each) and writes the masked judge batches:

* every run gets a **random opaque id** that is not derived from its arm,
  prompt or repeat; the key (id -> arm, prompt, repeat, record path) is
  written to a **separate file outside the batch folder** and never goes
  into a batch;
* the answers are **redacted**: every tool name that exists in only one
  arm becomes ``[TOOL]``, and the arm names, the branch names and the
  persona name are removed.  Every number, identifier, residue and
  structure ID is kept - the exporter checks that the redaction only
  replaces whole tokens and reports every run whose redaction changed
  something else;
* the runs are shuffled across arms and prompts and cut into batches of
  at most ten runs; every batch is one self-contained markdown file
  with the instructions of the template and its run blocks;
* the scripted items are listed in every run block for context and
  marked ``scripted``; the judged items are the ones to score;
* the **reference notes** of the dated correction of 2026-11-02 (the
  pocket facts that no committed checklist item carries) are added to
  the run blocks of the prompts they belong to; the committed item texts
  are not changed;
* the ``p2rank_reference_*`` items are marked ``low-information item``:
  the measurement behind the correction of 2026-11-02 shows that no
  P2Rank pocket carries a residue, so those items only ask for the
  number 0.  They are not changed.

    python benchmark/export_judge_batches.py \
        --out-dir <batch folder> [--key-out <path>] [--seed <n>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import string
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmark"))
sys.path.insert(0, str(REPO / "scripts"))
from _paths import expand_home  # noqa: E402

ANALYSIS_SET = REPO / "benchmark" / "analysis_set.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
DRAFT = REPO / "benchmark" / "benchmark_draft.json"
CORRECTIONS = REPO / "benchmark" / "corrections" / "pocket_reference_selection_2026-11-02.json"
ARM_D_TOOLS = REPO / "alloagent" / "exposed_tools.txt"
ARM_A_TOOLS = REPO / "benchmark" / "baseline_arm_tool_names.txt"
TEMPLATE = REPO / "benchmark" / "judge_prompt_template.md"

# The batches are written into the repository (in the folder that git
# ignores); the **key** is written outside it, because it says which arm
# every run came from.
DEFAULT_OUT_DIR = REPO / "benchmark" / "judging" / "judge_batches"
DEFAULT_KEY_PATH = Path(tempfile.gettempdir()) / "opencode" / "judge_key.json"

RUN_ID_ALPHABET = string.ascii_lowercase + string.digits
RUN_ID_PREFIX = "r"
RUN_ID_LENGTH = 10
MAX_RUNS_PER_BATCH = 10
PLACEHOLDER = "[TOOL]"

# The final answer of a run.  The record of a run holds the whole agent
# turn - the reasoning (<think>) and the protocol blocks included - and
# the judge and the rater need only the final response.
NO_FINAL_ANSWER = "[NO FINAL ANSWER]"
SOLUTION_TAG = "<solution>"
PROTOCOL_TAGS = (
    "<solution>", "</solution>", "<execute>", "</execute>",
    "<observation>", "</observation>", "<think>", "</think>",
)
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.S)
THINK_OPEN_RE = re.compile(r"<think>.*", re.S)
OBSERVATION_BLOCK_RE = re.compile(r"<observation>.*?</observation>", re.S)
ALNUM_RE = re.compile(r"[A-Za-z0-9]")

# The arm names, the branch names and the persona name.  Every one of
# them is replaced by the placeholder; the categories are counted
# separately.
PERSONA = "AlloAgent"
ARM_TOKENS = (
    "AlloAgent-v2",
    "baseline_wt_gate",
    "baseline_wt",
    "AlloAgent",
    "alloagent",
    "baseline",
)
ARM_LABEL_PATTERN = r"\barm\s*[AD]\b"

# The method-conditional items: the scorer judges them only when the
# answer names the method, so the judge has to score them too.
METHOD_ITEM_PREFIXES = ("fpocket_reference_", "p2rank_reference_")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_tool_names(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def build_tool_pattern(names: list[str]) -> re.Pattern:
    """The one-sided tool names, in every occurrence.

    The pattern is deliberately loose: a tool name that is part of a
    longer identifier (a file name the run itself created, a dotted
    module path) is replaced too, because leaving it would leave an arm
    hint in the answer.  Every such replacement changes an identifier,
    and the exporter reports it.
    """
    ordered = sorted(set(names), key=len, reverse=True)
    return re.compile("|".join(re.escape(name) for name in ordered))


def build_arm_pattern(tokens: tuple[str, ...]) -> re.Pattern:
    ordered = sorted(tokens, key=len, reverse=True)
    return re.compile(
        r"(?<![\w-])(" + "|".join(re.escape(name) for name in ordered) + r")(?![\w-])",
        re.IGNORECASE,
    )


def _is_identifier_neighbour(before: str, text: str, start: int,
                             after: str, whole: str, end: int) -> bool:
    """Does the match sit inside a longer identifier?

    A word character or an underscore next to the match means it is part
    of a longer name (a file name, a variable).  A dot means it is part
    of a dotted path - but only when the dot is not the sentence period:
    a dot between a word and a space is punctuation.
    """
    if before and (before.isalnum() or before == "_"):
        return True
    if after and (after.isalnum() or after == "_"):
        return True
    if before == "." and start >= 2 and text[start - 2].isalnum():
        return True
    if after == "." and end + 1 < len(whole) and whole[end + 1].isalnum():
        return True
    return False


class Redactor:
    """The redaction of one answer, with its counts per category.

    Every match is a whole token: the characters around it are never a
    word character, so a number, an identifier, a residue or a structure
    ID that touches the match survives untouched.  Each rule is checked
    on its own: the text that is left when the redacted names are taken
    out of the text before the rule must be exactly the text that is
    left when the placeholders are taken out of the text after it.
    """

    def __init__(self, tool_pattern: re.Pattern, arm_pattern: re.Pattern,
                 persona_pattern: re.Pattern, arm_label_pattern: re.Pattern):
        self.rules = (
            ("one_sided_tool_name", tool_pattern),
            ("persona_name", persona_pattern),
            ("arm_or_branch_name", arm_pattern),
            ("arm_label", arm_label_pattern),
        )
        self.counts: Counter = Counter()
        self.problems: list[str] = []
        self.dotted: list[str] = []
        self.matched: list[str] = []

    def __call__(self, text: str) -> str:
        self.counts.clear()
        self.problems = []
        self.dotted = []
        self.matched = []
        for category, pattern in self.rules:
            matched: list[str] = []

            def swap(match: re.Match) -> str:
                matched.append(match.group(0))
                before = text[match.start() - 1] if match.start() else ""
                after = text[match.end()] if match.end() < len(text) else ""
                if _is_identifier_neighbour(before, text, match.start(), after, text, match.end()):
                    self.dotted.append(match.group(0))
                return PLACEHOLDER

            redacted = pattern.sub(swap, text)
            if matched:
                self.counts[category] += len(matched)
                self.matched.extend(matched)
            text = redacted
        return text


def check_redaction(original: str, redacted: str, matched: list[str],
                    dotted: list[str]) -> list[str]:
    """The problems of one redaction.

    Every **data** number has to survive: the numbers of the original
    answer and the numbers of the redacted answer are the same multiset,
    once the digits that were part of a redacted name (the "2" of
    ``detect_pockets_p2rank``) are taken out of the original.  A redaction
    inside a dotted module path changes that path, and that is reported
    as well.
    """
    problems: list[str] = []
    numbers_original = Counter(re.findall(r"\d+(?:\.\d+)?", original))
    for name in matched:
        for digits in re.findall(r"\d+(?:\.\d+)?", name):
            if numbers_original[digits]:
                numbers_original[digits] -= 1
    numbers_redacted = Counter(re.findall(r"\d+(?:\.\d+)?", redacted))
    if numbers_original != numbers_redacted:
        problems.append(
            f"the redaction changed a number: missing="
            f"{sorted((numbers_original - numbers_redacted).elements())[:5]} "
            f"added={sorted((numbers_redacted - numbers_original).elements())[:5]}")
    if dotted:
        problems.append(
            f"the redaction changed {len(dotted)} dotted module path(s): "
            f"{sorted(set(dotted))[:5]}")
    return problems


def last_message(record_dir: Path) -> tuple[str, str]:
    """The last message of a run: the final response and its reasoning.

    The harness records the reasoning apart (``reasoning_split``), so the
    content of the last message is the agent's final response **without**
    the reasoning, and it is not cut at the 20 000 characters of the
    record's ``final_content``.
    """
    path = Path(record_dir) / "run.json"
    if not path.is_file():
        return "", ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "", ""
    messages = data.get("messages") or []
    if not messages:
        return "", ""
    last = messages[-1]
    return str(last.get("content") or ""), str(last.get("reasoning_content") or "")


def strip_protocol_tags(text: str) -> str:
    """The text without the protocol markup the agent quotes."""
    for tag in PROTOCOL_TAGS:
        text = text.replace(tag, "")
    text = THINK_BLOCK_RE.sub("", text)
    text = THINK_OPEN_RE.sub("", text)
    text = OBSERVATION_BLOCK_RE.sub("", text)
    return text.strip()


def final_answer(record_dir: Path) -> tuple[str, dict]:
    """The final answer of a run: the body of its last ``<solution>`` block.

    The record of a run holds the whole agent turn - the reasoning
    (``<think>``) and the protocol blocks included - and the judge and
    the rater need only the final response.  The final response is the
    content of the last message of the record (the harness records the
    reasoning apart), and the answer inside it is the body of its
    ``<solution>`` block.  When that body is empty or is only quoted
    markup, the whole final response is kept.

    Returns the text and its statistics.
    """
    content, reasoning = last_message(record_dir)
    try:
        original = (Path(record_dir) / "answer.txt").read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        original = content
    if not content:
        content = original
    stats = {
        "characters_before": len(original),
        "characters_after": 0,
        "characters_removed": 0,
        "from_solution": False,
        "used_the_whole_response": False,
        "no_final_answer": False,
    }
    best = ""
    if SOLUTION_TAG in content:
        stats["from_solution"] = True
        for match in re.finditer(re.escape(SOLUTION_TAG), content):
            start = match.end()
            end = content.find("</solution>", start)
            body = content[start:end] if end >= 0 else content[start:]
            if len(ALNUM_RE.findall(strip_protocol_tags(body))) > len(
                    ALNUM_RE.findall(strip_protocol_tags(best))):
                best = body
    answer = strip_protocol_tags(best)
    if len(ALNUM_RE.findall(answer)) < 20:
        answer = strip_protocol_tags(content)
        stats["used_the_whole_response"] = True
    if not ALNUM_RE.search(answer):
        stats["no_final_answer"] = True
        answer = NO_FINAL_ANSWER
    stats["characters_after"] = len(answer)
    stats["characters_removed"] = stats["characters_before"] - len(answer)
    whole = content + reasoning
    numbers_answer = Counter(re.findall(r"\d+(?:\.\d+)?", answer))
    numbers_whole = Counter(re.findall(r"\d+(?:\.\d+)?", whole))
    stats["numbers_not_in_the_final_response"] = sorted(
        (numbers_answer - numbers_whole).elements())
    return answer, stats


def item_ids(prompt_id: str, items: list[dict]) -> list[str]:
    """The item ids of a prompt: ``<prompt>_<letter>``, in checklist order."""
    letters = string.ascii_lowercase
    ids = []
    for index in range(len(items)):
        suffix = letters[index] if index < len(letters) else f"a{index}"
        ids.append(f"{prompt_id}_{suffix}")
    return ids


def item_text(item: dict) -> str:
    """The criterion of an item: the committed value, verbatim."""
    value = item.get("value")
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def scripted_verdicts(summary: dict, checklist: dict) -> dict[str, str]:
    """The verdict of every item of a prompt, from the committed scorer.

    The scorer is the one of ``benchmark/score_scripted.py``: an item it
    scored (PASS or FAIL) is a scripted item, an item it deferred is the
    judge's to score.  If the scorer cannot be imported, the item kind
    decides (the qualitative items are the judge's).
    """
    try:
        import score_scripted
    except ImportError:
        return {}
    try:
        result = score_scripted.score_answer(summary, checklist)
    except Exception:  # noqa: BLE001
        return {}
    return {item["key"]: item["verdict"] for item in result.get("items", [])}


def is_judged(item: dict) -> bool:
    """Is this item the judge's to score?

    The committed scorer decides: an item it scored (PASS or FAIL) is
    listed for context and marked ``scripted``; an item it deferred (the
    qualitative ones, and a method-conditional item whose method the
    answer does not name) is the judge's to score.
    """
    if item.get("kind") == "qualitative":
        return True
    return str(item.get("key", "")).startswith(METHOD_ITEM_PREFIXES)


def is_low_information(item: dict) -> bool:
    return str(item.get("key", "")).startswith("p2rank_reference_")


def reference_note(prompt_id: str, corrections: dict) -> str | None:
    """The reference note of a prompt, from the dated correction file."""
    facts = corrections.get("judge_needs_these_numbers", {}).get(prompt_id)
    if not facts:
        return None
    lines = [
        "REFERENCE NOTE (dated correction, from benchmark/corrections.md)",
    ]
    for site, values in facts.items():
        lines.append(
            f"The pocket-detection reference for the {site} site was corrected on "
            f"2026-11-02: the committed selection took the first pocket with any "
            f"overlap (rank {values.get('committed_rank')}, overlap "
            f"{values.get('committed_overlap')}), the corrected selection takes the "
            f"pocket with the most site residues (rank "
            f"{values.get('corrected_rank')}, overlap "
            f"{values.get('corrected_overlap')})."
        )
    lines.append(
        "No committed checklist item carries this site, so the item texts below "
        "are unchanged."
    )
    return "\n".join(lines)


def make_run_ids(count: int, rng: random.Random, forbidden: list[str]) -> list[str]:
    """Random, unique run ids that carry nothing of the run they name."""
    lowered = [word.lower() for word in forbidden]
    ids: list[str] = []
    seen: set[str] = set()
    while len(ids) < count:
        candidate = RUN_ID_PREFIX + "".join(
            rng.choice(RUN_ID_ALPHABET) for _ in range(RUN_ID_LENGTH))
        if candidate in seen:
            continue
        lowered_candidate = candidate.lower()
        if any(word and word in lowered_candidate for word in lowered):
            continue
        seen.add(candidate)
        ids.append(candidate)
    return ids


def template_instructions() -> str:
    """The instructions of the judge, from the template, verbatim.

    Only the section the template marks as "Instructions to the judge
    (paste at the top of every session)" is copied: the title of the
    template names the product and the "Exporter requirements" section
    is addressed to the coding agent, not to the judge.
    """
    text = TEMPLATE.read_text(encoding="utf-8")
    start = text.find("## Instructions to the judge")
    end = text.find("## Per-run block")
    if start < 0 or end < 0:
        raise ValueError(f"the template has no instructions section: {TEMPLATE}")
    section = text[start:end].rstrip()
    if section.endswith("---"):
        section = section[:-3].rstrip()
    return section


def render_run_block(run: dict, note: str | None) -> str:
    lines = [
        f"=== RUN {run['run_id']} ===",
        "QUESTION:",
        run["prompt_text"],
        "",
        f"INTENDED PROTEIN: {run['protein_name']} ({run['accession']})",
        f"PROMPT TYPE: {run['prompt_type']}",
        "",
        "CHECKLIST (ground truth):",
    ]
    lines.extend(run["checklist_lines"])
    if note:
        lines.append("")
        lines.append(note)
    lines.append("")
    lines.append("FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):")
    lines.append(run["answer"])
    lines.append(f"=== END RUN {run['run_id']} ===")
    return "\n".join(lines)


def _is_inside_the_repository(path: Path) -> bool:
    """Is the path inside the repository?

    The key files say which arm every run came from: they are never
    written inside the repository, and the exporter refuses to do it.
    """
    try:
        Path(path).resolve().relative_to(REPO.resolve())
    except ValueError:
        return False
    return True


def export_one_extra_batch(
    runs: list[dict],
    append_list: Path,
    out_dir: Path,
    key_out: Path,
    seed: int,
    rng: random.Random,
    checklists_by_prompt: dict,
    judge_facts: dict,
    instructions: str,
    identifier_changes: list[str],
    failures: list[str],
) -> int:
    """Export ONE extra batch and leave the existing batches untouched.

    The runs of the append list get their opaque ids from the key that
    is already there (so the batches that were exported before keep
    their ids) and new ids for the runs the key does not know yet.  The
    key and the redaction report are updated with the new rows; the
    batch files that are already there are not written again.
    """
    wanted = json.loads(append_list.read_text(encoding="utf-8"))
    keys = [(entry["arm"], entry["prompt_id"], int(entry["repeat"]))
            for entry in wanted]
    selected = [run for run in runs
                if (run["arm"], run["prompt_id"], run["repeat"]) in keys]
    missing = [key for key in keys
               if not any((run["arm"], run["prompt_id"], run["repeat"]) == key
                          for run in selected)]
    if missing:
        print(f"ERROR: the append list names runs that are not in the analysis "
              f"set: {missing}", file=sys.stderr)
        return 2

    key_payload = {}
    if key_out.is_file():
        key_payload = json.loads(key_out.read_text(encoding="utf-8"))
    known = {(row["arm"], row["prompt_id"], row["repeat"]): row["run_id"]
             for row in key_payload.get("runs_key", [])}
    forbidden = []
    for run in selected:
        forbidden += [run["arm"], run["prompt_id"], f"r{run['repeat']}",
                      run["record_dir"].replace("\\", "/").split("/")[-1]]
    forbidden += list(ARM_TOKENS) + [PERSONA]
    fresh = [run for run in selected
             if (run["arm"], run["prompt_id"], run["repeat"]) not in known]
    new_ids = make_run_ids(len(fresh), rng, forbidden)
    for run, run_id in zip(fresh, new_ids):
        known[(run["arm"], run["prompt_id"], run["repeat"])] = run_id
    for run in selected:
        run["run_id"] = known[(run["arm"], run["prompt_id"], run["repeat"])]

    existing = sorted(out_dir.glob("judge_batch_*.md"))
    number = len(existing) + 1
    name = f"judge_batch_{number:03d}.md"
    blocks = []
    totals: Counter = Counter()
    identifier_changes: list[str] = []
    failures: list[str] = []
    for run in selected:
        note = reference_note(run["prompt_id"], {"judge_needs_these_numbers": judge_facts})
        blocks.append(render_run_block(run, note))
        for category, count in run["redactions"].items():
            totals[category] += count
    text = (
        f"# Judge batch {number:03d}\n\n"
        f"{instructions}\n\n---\n\n" + "\n\n".join(blocks) + "\n"
    )
    (out_dir / name).write_text(text, encoding="utf-8")
    print(f"  {name}: {len(selected)} runs (appended)")

    rows = list(key_payload.get("runs_key", []))
    for run in selected:
        rows.append({
            "run_id": run["run_id"],
            "batch": name,
            "batch_number": number,
            "arm": run["arm"],
            "prompt_id": run["prompt_id"],
            "repeat": run["repeat"],
            "record_dir": run["record_dir"],
            "source": run["source"],
            "answer_sha256": run["answer_sha256"],
            "item_ids": item_ids(run["prompt_id"],
                                 checklists_by_prompt.get(run["prompt_id"], {"checklist": []})["checklist"]),
        })
    key_payload.update({
        "seed": seed,
        "batches": number,
        "runs": len(rows),
        "runs_key": rows,
    })
    key_out.write_text(json.dumps(key_payload, indent=2) + "\n", encoding="utf-8")

    report_path = out_dir / "judge_redaction_report.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        report = {"redaction_counts_by_category": {}, "per_run": {},
                  "runs_whose_redaction_changed_an_identifier": [],
                  "runs_whose_redaction_failed": [],
                  "the_final_answer_only": {}}
    counts = Counter(report.get("redaction_counts_by_category", {}))
    counts.update(totals)
    report["redaction_counts_by_category"] = dict(counts)
    report["runs_per_batch"] = list(report.get("runs_per_batch", [])) + [len(selected)]
    report["runs"] = report.get("runs", 0) + len(selected)
    report["batches"] = number
    report["runs_with_a_redaction"] = report.get("runs_with_a_redaction", 0) + sum(
        1 for run in selected if any(run["redactions"].values()))
    per_run = dict(report.get("per_run", {}))
    for run in selected:
        if any(run["redactions"].values()):
            per_run[run["run_id"]] = run["redactions"]
    report["per_run"] = per_run
    report["runs_whose_redaction_changed_an_identifier"] = list(
        report.get("runs_whose_redaction_changed_an_identifier", [])
    ) + identifier_changes
    report["runs_whose_redaction_failed"] = list(
        report.get("runs_whose_redaction_failed", [])) + failures
    extraction = dict(report.get("the_final_answer_only", {}))
    for run in selected:
        _, stats = final_answer(expand_home(run["record_dir"]))
        extraction["characters_before"] = extraction.get("characters_before", 0) + stats["characters_before"]
        extraction["characters_after"] = extraction.get("characters_after", 0) + stats["characters_after"]
        extraction["characters_removed"] = extraction.get("characters_removed", 0) + stats["characters_removed"]
    extraction["runs_with_no_final_answer"] = list(
        extraction.get("runs_with_no_final_answer", []))
    extraction["runs_whose_whole_final_response_was_kept"] = list(
        extraction.get("runs_whose_whole_final_response_was_kept", []))
    report["the_final_answer_only"] = extraction
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    readme_path = out_dir / "README.md"
    if readme_path.is_file():
        text = readme_path.read_text(encoding="utf-8")
        text = re.sub(
            r"\*\*(\d+) batches\*\*, `judge_batch_001\.md` to "
            r"`judge_batch_\d+\.md`, and \*\*(\d+) runs\*\*",
            f"**{number} batches**, `judge_batch_001.md` to "
            f"`judge_batch_{number:03d}.md`, and **{len(rows)} runs**",
            text)
        readme_path.write_text(text, encoding="utf-8")
    print(f"  the key: {key_out} ({len(rows)} runs, {number} batches)")
    print(f"  the redaction report: {report_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--analysis-set", default=str(ANALYSIS_SET))
    parser.add_argument("--checklists", default=str(CHECKLISTS))
    parser.add_argument("--draft", default=str(DRAFT))
    parser.add_argument("--corrections", default=str(CORRECTIONS))
    parser.add_argument("--arm-a-tools", default=str(ARM_A_TOOLS))
    parser.add_argument("--arm-d-tools", default=str(ARM_D_TOOLS))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR),
                        help="the batch folder (default: the ignored folder in the repository)")
    parser.add_argument("--key-out", default=str(DEFAULT_KEY_PATH),
                        help="the key file (default: outside the repository)")
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument("--max-runs-per-batch", type=int, default=MAX_RUNS_PER_BATCH)
    parser.add_argument(
        "--append-batch",
        default=None,
        help=(
            "A JSON list of the runs to export as ONE extra batch "
            '([{"arm": ..., "prompt_id": ..., "repeat": ...}]).  The batches '
            "that are already in the folder are not written again, and the "
            "key keeps their run ids."
        ),
    )
    args = parser.parse_args()

    analysis_set = load_json(Path(args.analysis_set))
    checklists = load_json(Path(args.checklists))
    draft = {row["id"]: row for row in load_json(Path(args.draft))}
    corrections = load_json(Path(args.corrections)) if Path(args.corrections).is_file() else {}

    arm_a_tools = read_tool_names(Path(args.arm_a_tools))
    arm_d_tools = read_tool_names(Path(args.arm_d_tools))
    one_sided = sorted((set(arm_a_tools) | set(arm_d_tools))
                        - (set(arm_a_tools) & set(arm_d_tools)))
    tool_pattern = build_tool_pattern(one_sided)
    arm_pattern = build_arm_pattern(ARM_TOKENS)
    persona_pattern = re.compile(r"(?<![\w-])" + re.escape(PERSONA) + r"(?![\w-])")
    arm_label_pattern = re.compile(ARM_LABEL_PATTERN, re.IGNORECASE)
    # A loose pattern: any surviving occurrence of a name, even glued to
    # an identifier, is an arm hint that the reaction missed.
    loose_pattern = re.compile(
        "|".join(re.escape(name)
                 for name in sorted(set(one_sided) | set(ARM_TOKENS) | {PERSONA},
                                    key=len, reverse=True)))
    redactor = Redactor(tool_pattern, arm_pattern, persona_pattern, arm_label_pattern)

    # The corrected pocket facts the judge needs, per prompt.
    judge_facts = {}
    for prompt_id, sites in corrections.get("judge_needs_these_numbers", {}).items():
        judge_facts[prompt_id] = {}
        for site, values in sites.items():
            committed = corrections.get("sites_without_a_committed_item", {}).get(site, {})
            judge_facts[prompt_id][site] = {
                "committed_rank": committed.get("committed", {}).get(
                    "rank_of_the_pocket_covering_the_site"),
                "committed_overlap": committed.get("committed", {}).get(
                    "overlap_of_the_covering_pocket"),
                "corrected_rank": values.get("rank_of_the_pocket_covering_the_site"),
                "corrected_overlap": values.get("overlap_of_the_covering_pocket"),
            }

    checklists_by_prompt = {prompt["id"]: prompt for prompt in checklists["prompts"]}
    protein_names = {}
    for prompt in checklists["prompts"]:
        for item in prompt["checklist"]:
            if item["key"].startswith("accession_") and isinstance(item.get("value"), dict):
                protein_names[prompt["id"]] = item["value"].get("name") or ""

    runs = []
    problems = []
    identifier_changes_report: list[str] = []
    failures_report: list[str] = []
    no_final_answer: list[str] = []
    whole_response_runs: list[str] = []
    truncated_records: list[str] = []
    extraction_totals = {
        "characters_before": 0,
        "characters_after": 0,
        "characters_removed": 0,
    }
    for row in analysis_set["rows"]:
        record_dir = expand_home(row["record_dir"])
        summary = load_json(record_dir / "summary.json")
        answer = (record_dir / "answer.txt").read_text(encoding="utf-8", errors="replace")
        retained, answer_stats = final_answer(record_dir)
        prompt_id = row["prompt_id"]
        prompt_row = draft.get(prompt_id, {})
        if prompt_row.get("prompt") and prompt_row["prompt"] != summary.get("prompt"):
            problems.append(
                f"{prompt_id}: the committed prompt text and the record's prompt differ")
        checklist = checklists_by_prompt.get(prompt_id, {"checklist": []})
        ids = item_ids(prompt_id, checklist["checklist"])
        verdicts = scripted_verdicts(summary, checklist)
        checklist_lines = []
        for identifier, item in zip(ids, checklist["checklist"]):
            verdict = verdicts.get(item["key"])
            if verdict in ("PASS", "FAIL"):
                judged = False
            elif verdict == "DEFERRED":
                judged = True
            else:
                judged = is_judged(item)
            flags = [
                f"[{identifier}]",
                "[critical]",
                "[judged]" if judged else "[scripted]",
            ]
            if is_low_information(item):
                flags.append("[low-information item]")
            checklist_lines.append(" ".join(flags) + " " + item_text(item))
        redacted = redactor(retained)
        run_problems = list(redactor.problems) + check_redaction(
            retained, redacted, redactor.matched, redactor.dotted)
        survivors = sorted(set(loose_pattern.findall(redacted)))
        if survivors:
            run_problems.append(
                f"{len(survivors)} name(s) survive the redaction: {survivors[:5]}")
        identifier_changes = [problem for problem in run_problems
                              if problem.startswith("the redaction changed")
                              and "dotted module path" in problem]
        failures = [problem for problem in run_problems
                    if problem not in identifier_changes]
        for problem in identifier_changes:
            identifier_changes_report.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}: {problem}")
        for problem in failures:
            failures_report.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}: {problem}")
        extraction_totals["characters_before"] += answer_stats["characters_before"]
        extraction_totals["characters_after"] += answer_stats["characters_after"]
        extraction_totals["characters_removed"] += answer_stats["characters_removed"]
        if answer_stats["no_final_answer"]:
            no_final_answer.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}")
        if answer_stats["used_the_whole_response"]:
            whole_response_runs.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}")
        numbers_original = Counter(re.findall(r"\d+(?:\.\d+)?", answer))
        numbers_retained = Counter(re.findall(r"\d+(?:\.\d+)?", retained))
        if not numbers_original >= numbers_retained:
            # The record of a run keeps 20 000 characters; the final
            # response can be longer, so the numbers the truncated record
            # does not hold are reported, not a failure.
            truncated_records.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}: the record holds "
                f"20 000 characters, the final answer is longer")
        if answer_stats.get("numbers_not_in_the_final_response"):
            failures_report.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}: the retained answer "
                f"holds a number the agent's final response does not: "
                f"{answer_stats['numbers_not_in_the_final_response'][:5]}")
        if run_problems:
            problems.append(
                f"{row['arm']}/{prompt_id}_r{row['repeat']}: " + "; ".join(run_problems))
        runs.append({
            "arm": row["arm"],
            "prompt_id": prompt_id,
            "repeat": row["repeat"],
            "record_dir": str(record_dir),
            "source": row["source"],
            "prompt_text": prompt_row.get("prompt") or summary.get("prompt") or "",
            "protein_name": protein_names.get(prompt_id, ""),
            "accession": prompt_row.get("accession", ""),
            "prompt_type": ("HONEST-REPORTING"
                            if prompt_row.get("category") == "Honest reporting"
                            else "normal"),
            "checklist_lines": checklist_lines,
            "answer": redacted,
            "answer_sha256": sha256_text(answer),
            "redactions": dict(redactor.counts),
        })

    forbidden = []
    for run in runs:
        forbidden += [run["arm"], run["prompt_id"], f"r{run['repeat']}",
                      run["record_dir"].replace("\\", "/").split("/")[-1]]
    forbidden += list(ARM_TOKENS) + [PERSONA] + list(draft.keys())
    rng = random.Random(args.seed)
    ids = make_run_ids(len(runs), rng, forbidden)
    for run, run_id in zip(runs, ids):
        run["run_id"] = run_id

    if args.append_batch:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        key_out = Path(args.key_out) if args.key_out else DEFAULT_KEY_PATH
        if _is_inside_the_repository(key_out):
            print(
                f"ERROR: the key must not be written inside the repository "
                f"({REPO}); it says which arm every run came from.  Choose a path "
                f"outside it.",
                file=sys.stderr,
            )
            return 2
        key_out.parent.mkdir(parents=True, exist_ok=True)
        return export_one_extra_batch(
            runs=runs,
            append_list=Path(args.append_batch),
            out_dir=out_dir,
            key_out=key_out,
            seed=args.seed,
            rng=rng,
            checklists_by_prompt=checklists_by_prompt,
            judge_facts=judge_facts,
            instructions=template_instructions(),
            identifier_changes=identifier_changes_report,
            failures=failures_report,
        )

    order = list(runs)
    rng.shuffle(order)
    batches = [
        order[start:start + args.max_runs_per_batch]
        for start in range(0, len(order), args.max_runs_per_batch)
    ]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    key_out = Path(args.key_out) if args.key_out else DEFAULT_KEY_PATH
    if _is_inside_the_repository(key_out):
        print(
            f"ERROR: the key must not be written inside the repository "
            f"({REPO}); it says which arm every run came from.  Choose a path "
            f"outside it.",
            file=sys.stderr,
        )
        return 2
    key_out.parent.mkdir(parents=True, exist_ok=True)

    instructions = template_instructions()
    key_rows = []
    totals: Counter = Counter()
    for number, batch in enumerate(batches, start=1):
        name = f"judge_batch_{number:03d}.md"
        blocks = []
        for run in batch:
            note = reference_note(run["prompt_id"], {"judge_needs_these_numbers": judge_facts})
            blocks.append(render_run_block(run, note))
            for category, count in run["redactions"].items():
                totals[category] += count
            key_rows.append({
                "run_id": run["run_id"],
                "batch": name,
                "batch_number": number,
                "arm": run["arm"],
                "prompt_id": run["prompt_id"],
                "repeat": run["repeat"],
                "record_dir": run["record_dir"],
                "source": run["source"],
                "answer_sha256": run["answer_sha256"],
                "item_ids": item_ids(run["prompt_id"],
                                     checklists_by_prompt.get(run["prompt_id"], {"checklist": []})["checklist"]),
            })
        text = (
            f"# Judge batch {number:03d} of {len(batches)}\n\n"
            f"{instructions}\n\n---\n\n" + "\n\n".join(blocks) + "\n"
        )
        (out_dir / name).write_text(text, encoding="utf-8")
        print(f"  {name}: {len(batch)} runs")

    key_payload = {
        "what_this_file_is": (
            "the key of the judge batches: the opaque run id of every run and "
            "the arm, the prompt, the repeat and the record path it stands "
            "for.  The judge never sees this file."
        ),
        "seed": args.seed,
        "batches": len(batches),
        "runs": len(key_rows),
        "analysis_set": str(Path(args.analysis_set).resolve()),
        "checklists_sha256": sha256_text(Path(args.checklists).read_text(encoding="utf-8")),
        "runs_key": key_rows,
    }
    key_out.write_text(json.dumps(key_payload, indent=2) + "\n", encoding="utf-8")

    redaction_report = {
        "seed": args.seed,
        "batches": len(batches),
        "runs": len(runs),
        "runs_per_batch": [len(batch) for batch in batches],
        "one_sided_tool_names": len(one_sided),
        "tool_names_in_both_arms": len(set(arm_a_tools) & set(arm_d_tools)),
        "redaction_counts_by_category": dict(totals),
        "runs_with_a_redaction": sum(
            1 for run in runs if any(run["redactions"].values())),
        "runs_whose_redaction_changed_an_identifier": identifier_changes_report,
        "runs_whose_redaction_failed": failures_report,
        "the_final_answer_only": {
            "characters_before": extraction_totals["characters_before"],
            "characters_after": extraction_totals["characters_after"],
            "characters_removed": extraction_totals["characters_removed"],
            "runs_with_no_final_answer": no_final_answer,
            "runs_whose_whole_final_response_was_kept": whole_response_runs,
            "runs_whose_record_is_truncated": truncated_records,
        },
        "per_run": {
            run["run_id"]: run["redactions"] for run in runs
            if any(run["redactions"].values())
        },
    }
    report_path = out_dir / "judge_redaction_report.json"
    report_path.write_text(json.dumps(redaction_report, indent=2) + "\n", encoding="utf-8")

    readme = [
        "# The judge batches of the analysis set",
        "",
        f"Exported by `benchmark/export_judge_batches.py` on "
        f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} with the seed "
        f"{args.seed}.",
        "",
        "## What is here",
        "",
        f"* **{len(batches)} batches**, `judge_batch_001.md` to "
        f"`judge_batch_{len(batches):03d}.md`, and **{len(runs)} runs** in "
        f"total (at most {args.max_runs_per_batch} runs per batch).",
        "* Every batch is **self-contained**: the instructions of the judge "
        "(`benchmark/judge_prompt_template.md`, verbatim) followed by the run "
        "blocks.",
        "* Every run has a **random opaque id** that carries nothing of the "
        "run it names.",
        "* The **key** is NOT here: it is `judge_key.json`, outside the "
        f"repository ({key_out}), and the judge never sees it.",
        "",
        "## How the judged output is saved",
        "",
        "One JSON file per batch, `judge_batch_NNN.json` next to the "
        "markdown file of the same number, **unedited**: the array the judge "
        "returns in one session, exactly as it was returned, with one object "
        "per run (`run_id`, `goal_completion`, `data_grounding`, "
        "`final_answer_complete`, `items`, `notes`).  Do not reformat it, do "
        "not merge the batches into one file, and do not change a verdict "
        "after the fact: the agreement with the human sheet is computed from "
        "these files as they are.",
        "",
        "## The answer text",
        "",
        "The answer of a run is **only its final response**: the body of "
        "the last `<solution>` block of the record.  The reasoning of the "
        "agent (the `<think>` blocks) and the protocol blocks are not in "
        "the batch, and the numbers, identifiers, residues and structure "
        "IDs of the final answer are kept as they are.  A run whose "
        "record holds no final answer would carry `[NO FINAL ANSWER]`; "
        f"there are {len(no_final_answer)} of them.",
        "",
        "## The redaction",
        "",
        "| category | replacements |",
        "|---|---:|",
    ]
    for category, count in sorted(totals.items()):
        readme.append(f"| {category} | {count} |")
    readme += [
        "",
        f"Every tool name that exists in only one arm is replaced by "
        f"`[TOOL]` ({len(one_sided)} such names; the two arms share "
        f"{len(set(arm_a_tools) & set(arm_d_tools))} tool names).  The arm "
        "names, the branch names and the persona name are replaced by the "
        "same placeholder.",
        "",
        f"**No number was changed**: the exporter compares the numbers of "
        f"every answer before and after the redaction (the digits inside a "
        f"redacted name go with the name), and {len(failures_report)} "
        f"answers fail that check.",
        "",
        f"**The redaction changed an identifier in "
        f"{len(identifier_changes_report)} answers**: a tool name that is "
        f"part of a longer identifier (a dotted module path such as "
        f"`biomni.tool.<name>`, or a file name the run itself created) was "
        f"replaced as well, because leaving it would leave the arm visible "
        f"in the answer.  The list is in `judge_redaction_report.json`, "
        f"in this folder.",
        "",
        "## The reference notes",
        "",
        "The run blocks of the prompts whose pocket criteria are judged "
        "carry a `REFERENCE NOTE (dated correction, from "
        "benchmark/corrections.md)` with the corrected pocket facts that no "
        "committed checklist item carries.  The committed item texts are not "
        "changed.",
        "",
        "## The low-information items",
        "",
        "The `p2rank_reference_*` items are marked `[low-information item]`: "
        "the measurement of 2026-11-02 shows that no P2Rank pocket carries a "
        "residue, so those items only ask the answer for the number 0.  They "
        "are marked, not changed.",
        "",
        "## The critical flag",
        "",
        "The committed checklists carry no critical/supporting distinction, "
        "so every item is marked `[critical]`.",
    ]
    (out_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print()
    print(f"batches: {len(batches)}   runs: {len(runs)}")
    print(f"the key: {key_out}")
    print(f"the redaction report: {report_path}")
    for category, count in sorted(totals.items()):
        print(f"  {category}: {count}")
    print(f"  runs whose redaction changed an identifier: {len(identifier_changes_report)}")
    for problem in identifier_changes_report:
        print(f"    {problem}")
    print(f"  runs whose redaction failed (a number changed, a name survived): "
          f"{len(failures_report)}")
    for problem in failures_report:
        print(f"    {problem}")
    return 1 if failures_report else 0


if __name__ == "__main__":
    raise SystemExit(main())

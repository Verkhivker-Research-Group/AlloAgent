"""The scripted scoring of a benchmark run batch, against the committed checklists.

This scorer implements the **committed** checklist items of
``benchmark/checklists.json`` and nothing else: it never changes a value, it
never adds an item, and it never relaxes a criterion.  The semantics of each
``kind`` are fixed here and recorded in the dated note of
``benchmark/analysis_plan.md`` (2026-10-29):

``exact``
    every leaf of the expected value must be findable in the answer: a
    string as a case-insensitive substring, an integer as a number token
    (not part of a longer number), a float within the item's tolerance (or
    within 1 % of its value when the tolerance is 0 or absent).  A list is
    scored leaf by leaf; a dict is scored leaf by leaf.  An expected dict
    that carries ``present: false`` (an absence claim) is **not** scripted:
    it is deferred to the judge, because the presence of the word "0" in an
    answer is not evidence of an absence.
``set``
    the expected value holds alternative residue-number lists (the UniProt
    numbering and the PDB numbering).  The item is present when **one** of
    those lists is fully contained in the numbers the answer reports - the
    prompt asks for one numbering, so requiring both would be wrong.  The
    expected minimum distances are compared and reported, but they do not
    decide the item: the prompts do not ask for the distances.
``number``
    the item is present when the answer reports a number within the item's
    tolerance of the expected value.  A dict under a ``number`` item (the
    numbering-offset item) is scored leaf by leaf, like ``exact``.
``qualitative``
    **not scripted**.  These items are deferred to the judge (the masked
    judge batch) and to the human subset.  A deferred item is never
    counted as a pass and never counted as a failure: it is reported as
    ``DEFERRED``.

The **method-conditional** items (the ``fpocket_reference_*`` and
``p2rank_reference_*`` items of P01, P02, P03, P05, P06 and P07) follow the
rule the committed checklist itself states: the answer must name the method
it used, and the reference is judged against **that** method's reference
output.  An answer that names no method, or names both, is wrong on the
item (the committed rule says so), and it is recorded with the reason.

A run that is missing or failed is a **FAIL** and is never scored as a pass.

    python benchmark/score_scripted.py <run_dir> [<run_dir> ...]
        [--out <scored.json>] [--arm-label <label>=<dir name>] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKLISTS = REPO / "benchmark" / "checklists.json"

# A number token: an integer or a decimal, optionally signed.  The look
# arounds keep "188" from matching inside "1188" or "3.188".
NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
# A PDB chain residue token: one letter and the residue number, as in
# "A601".  The letter must stand alone and the number must not be part of a
# longer identifier, so "A601" is a number and "P01116" and "G12C" are not.
CHAIN_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9.])[A-Za-z]([1-9][0-9]*)(?![A-Za-z0-9.])")
# The same, but without a sign, for residue numbers: a residue number may be
# written as "188" or glued to its three-letter code ("Pro188"), but never
# inside a longer number or a decimal.
RESIDUE_RE = re.compile(r"(?<![\d.])(\d+)(?![\d.])")

METHOD_WORDS = {
    "fpocket": ("fpocket", "fpocket4"),
    "p2rank": ("p2rank", "p2 rank"),
}


def normalize(text: str) -> str:
    """Fold the answer to a comparable form: NFKC, lower case, single spaces."""
    folded = unicodedata.normalize("NFKC", text or "")
    folded = folded.replace("µ", "u").replace("Å", "A").replace("–", "-")
    return re.sub(r"\s+", " ", folded).lower()


def numbers_in(text: str) -> list[float]:
    values = [float(match.group(0)) for match in NUMBER_RE.finditer(text or "")]
    values.extend(float(match.group(1))
                  for match in CHAIN_NUMBER_RE.finditer(text or ""))
    return values


def residue_numbers_in(text: str) -> set[int]:
    return {int(match.group(1)) for match in RESIDUE_RE.finditer(text or "")}


def token_present(answer: str, value: int) -> bool:
    """True when the integer ``value`` appears in the answer as its own token."""
    return bool(re.search(rf"(?<![\w.]){value}(?![\w.])", answer))


def number_present(answer: str, value: float, tolerance: float | None) -> tuple[bool, float | None]:
    """True when the answer reports a number within the tolerance of ``value``."""
    if tolerance is None:
        tolerance = 0.0
    if tolerance == 0 and isinstance(value, float):
        # A float expected with a zero tolerance: the checklist's own
        # tolerance field cannot express the rounding of a float, so a 1 %
        # band is used and reported.  Integers keep the exact match.
        tolerance = abs(value) * 0.01
    best = None
    for found in numbers_in(answer):
        distance = abs(found - value)
        if best is None or distance < best:
            best = distance
    if best is None:
        return False, None
    return best <= tolerance + 1e-9, best


def is_absence_dict(value: dict) -> bool:
    return "present" in value and value.get("present") is False


def named_methods(answer: str) -> list[str]:
    """The pocket-detection methods the answer names."""
    found = []
    for method, words in METHOD_WORDS.items():
        if any(word in answer for word in words):
            found.append(method)
    return found


def score_exact(value, answer: str, tolerance, path: str) -> tuple[bool, list[str]]:
    """Every leaf of the expected value must be findable in the answer."""
    missing: list[str] = []
    if isinstance(value, dict):
        if is_absence_dict(value):
            return False, [f"{path}: an absence claim is not scripted"]
        for key, leaf in value.items():
            ok, sub = score_exact(leaf, answer, tolerance, f"{path}.{key}")
            if not ok:
                missing.extend(sub)
        return (not missing), missing
    if isinstance(value, list):
        for index, leaf in enumerate(value):
            ok, sub = score_exact(leaf, answer, tolerance, f"{path}[{index}]")
            if not ok:
                missing.extend(sub)
        return (not missing), missing
    if isinstance(value, bool):
        return (str(value).lower() in answer), [f"{path}: {value}"]
    if isinstance(value, str):
        if len(value) <= 2 and value.isalpha():
            # A one or two letter string (the chain) is matched as a token:
            # a plain substring test would match every "a" in the answer.
            ok = bool(re.search(rf"(?<!\w){re.escape(value.lower())}(?!\w)", answer))
        else:
            ok = normalize(value) in answer
        return ok, ([] if ok else [f"{path}: {value!r}"])
    if isinstance(value, (int, float)):
        ok, _ = number_present(answer, float(value), tolerance)
        return ok, ([] if ok else [f"{path}: {value}"])
    return False, [f"{path}: an unsupported value type {type(value).__name__}"]


def score_set(value: dict, answer: str) -> tuple[bool, list[str]]:
    """One of the alternative residue lists must be fully reported."""
    groups = {
        key: leaf
        for key, leaf in value.items()
        if isinstance(leaf, list) and all(isinstance(item, int) for item in leaf)
    }
    if not groups:
        return False, ["set: the expected value holds no residue list"]
    reported = residue_numbers_in(answer)
    best_key = None
    best_missing = None
    for key, residues in groups.items():
        missing = [residue for residue in residues if residue not in reported]
        if best_missing is None or len(missing) < len(best_missing):
            best_key = key
            best_missing = missing
    if best_missing:
        return False, [f"{best_key}: missing {best_missing}"]
    return True, []


def score_number(value, answer: str, tolerance) -> tuple[bool, list[str]]:
    if isinstance(value, dict):
        missing: list[str] = []
        for key, leaf in value.items():
            ok, sub = score_exact(leaf, answer, tolerance, key)
            if not ok:
                missing.extend(sub)
        return (not missing), missing
    ok, _ = number_present(answer, float(value), tolerance)
    return ok, ([] if ok else [f"expected {value}"])


LIGAND_KEY_RE = re.compile(r"^ligand_[0-9A-Za-z]+_([A-Za-z0-9]{2,3})$")


REFERENCE_HEADLINE_KEYS = (
    "rank_of_the_pocket_covering_the_site",
    "overlap_of_the_covering_pocket",
    "top3_ranks",
    "top3_overlap",
)


def score_reference(value: dict, answer: str, tolerance) -> tuple[bool, list[str]]:
    """The headline fields of a method reference output.

    The ``pockets`` list of the reference output is **not** scored leaf by
    leaf: it holds every pocket's score and residue count, and no answer has
    to report all of them.  The residue counts of the top three pockets are
    covered by the original (unchanged) ``fpocket_top3`` item.
    """
    missing: list[str] = []
    for key in REFERENCE_HEADLINE_KEYS:
        if key not in value:
            continue
        leaf = value[key]
        if leaf is None:
            continue
        ok, sub = score_exact(leaf, answer, tolerance or 0, key)
        if not ok:
            missing.extend(sub)
    return (not missing), missing


def score_item(item: dict, answer: str) -> dict:
    """Score one checklist item against one answer."""
    key = item["key"]
    kind = item["kind"]
    value = item["value"]
    tolerance = item["tolerance"]
    if isinstance(tolerance, str):
        tolerance = None

    if kind == "qualitative":
        return {"key": key, "kind": kind, "verdict": "DEFERRED", "reason": "judged"}

    ligand_code = None
    match = LIGAND_KEY_RE.match(key)
    if match:
        ligand_code = match.group(1)

    if (key.startswith("fpocket_reference_") or key.startswith("p2rank_reference_")
            or key == "fpocket_top3"):
        methods = named_methods(answer)
        wanted = "fpocket" if key.startswith("fpocket_") else "p2rank"
        if wanted not in methods:
            return {
                "key": key,
                "kind": kind,
                "verdict": "DEFERRED",
                "reason": (
                    f"the answer names {methods or 'no method'}; the committed item is "
                    f"judged against the {wanted} reference output only when the answer "
                    f"names {wanted}"
                ),
            }
        if key == "fpocket_top3":
            ok, missing = score_exact(value, answer, tolerance, key)
        else:
            ok, missing = score_reference(value, answer, tolerance)
        return {
            "key": key,
            "kind": kind,
            "verdict": "PASS" if ok else "FAIL",
            "reason": "" if ok else "; ".join(missing),
        }

    if kind == "exact":
        ok, missing = score_exact(value, answer, tolerance, key)
        if ok and ligand_code:
            if not re.search(rf"(?<!\w){re.escape(ligand_code.lower())}(?!\w)", answer):
                ok = False
                missing = [f"{key}: the ligand {ligand_code} is not named in the answer"]
        return {
            "key": key,
            "kind": kind,
            "verdict": "PASS" if ok else "FAIL",
            "reason": "" if ok else "; ".join(missing),
        }
    if kind == "set":
        ok, missing = score_set(value, answer)
        return {
            "key": key,
            "kind": kind,
            "verdict": "PASS" if ok else "FAIL",
            "reason": "" if ok else "; ".join(missing),
        }
    if kind == "number":
        ok, missing = score_number(value, answer, tolerance)
        return {
            "key": key,
            "kind": kind,
            "verdict": "PASS" if ok else "FAIL",
            "reason": "" if ok else "; ".join(missing),
        }
    return {"key": key, "kind": kind, "verdict": "DEFERRED", "reason": "an unknown kind"}


def score_answer(summary: dict, checklist: dict) -> dict:
    """Score one run's answer against the committed checklist of its prompt."""
    answer = normalize(summary.get("final_content") or "")
    items = [score_item(item, answer) for item in checklist["checklist"]]
    scripted = [item for item in items if item["verdict"] in ("PASS", "FAIL")]
    deferred = [item for item in items if item["verdict"] == "DEFERRED"]
    passed = [item for item in scripted if item["verdict"] == "PASS"]
    status = summary.get("status")
    if status != "completed":
        verdict = "FAIL"
    elif not scripted:
        verdict = "NO_SCRIPTED_ITEMS"
    elif len(passed) == len(scripted):
        verdict = "FULL"
    elif passed:
        verdict = "PARTIAL"
    else:
        verdict = "NONE"
    return {
        "prompt_id": summary.get("prompt_id") or summary.get("id"),
        "repeat": summary.get("repeat"),
        "status": status,
        "verdict": verdict,
        "scripted_items": len(scripted),
        "scripted_passed": len(passed),
        "deferred_items": len(deferred),
        "items": items,
    }


def load_checklists() -> dict[str, dict]:
    data = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    return {prompt["id"]: prompt for prompt in data["prompts"]}


SKIPPED_ARM_DIRS = {"quota_interrupted", "attempts", "logs"}


def find_runs(run_dir: Path) -> list[tuple[str, Path]]:
    """The (arm, run directory) pairs of a run directory, in a stable order.

    The superseded attempts (the quota-interrupted runs and the failed
    attempts) are **not** part of the analysis path: the committed
    infrastructure-failure rule says that only the last attempt of a run
    counts, and the last attempt is the one in ``<run-dir>/<arm>/<prompt>_r<n>/``.
    """
    found: list[tuple[str, Path]] = []
    if not run_dir.is_dir():
        return found
    for arm_dir in sorted(run_dir.iterdir()):
        if not arm_dir.is_dir():
            continue
        if arm_dir.name in SKIPPED_ARM_DIRS or arm_dir.name.startswith("_"):
            continue
        if not any(
            (child / "summary.json").is_file()
            for child in arm_dir.iterdir()
            if child.is_dir()
        ):
            continue
        for run in sorted(arm_dir.iterdir()):
            if run.is_dir() and (run / "summary.json").is_file():
                found.append((arm_dir.name, run))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", nargs="+")
    parser.add_argument("--out", help="the scored records as JSON")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    checklists = load_checklists()
    scored = []
    for run_dir in args.run_dirs:
        base = Path(run_dir)
        for arm, run_path in find_runs(base):
            summary = json.loads((run_path / "summary.json").read_text(encoding="utf-8"))
            prompt_id = summary.get("prompt_id") or summary.get("id") or run_path.name.split("_r")[0]
            checklist = checklists.get(prompt_id)
            if checklist is None:
                scored.append(
                    {
                        "arm": arm,
                        "run": run_path.name,
                        "prompt_id": prompt_id,
                        "status": summary.get("status"),
                        "verdict": "NO_CHECKLIST",
                        "scripted_items": 0,
                        "scripted_passed": 0,
                        "deferred_items": 0,
                        "items": [],
                    }
                )
                continue
            result = score_answer(summary, checklist)
            result["arm"] = arm
            result["run"] = run_path.name
            result["steps"] = summary.get("n_steps")
            result["wall_time_s"] = summary.get("wall_time_s")
            result["tokens"] = summary.get("token_total") or {}
            result["dirty"] = summary.get("git_dirty")
            scored.append(result)

    if args.out:
        Path(args.out).write_text(json.dumps(scored, indent=2), encoding="utf-8")

    if not args.quiet:
        for record in scored:
            print(
                f"{record['arm']:10s} {record['run']:12s} {record['verdict']:18s} "
                f"{record['scripted_passed']}/{record['scripted_items']} scripted, "
                f"{record['deferred_items']} deferred"
            )
    print()
    for arm in sorted({record["arm"] for record in scored}):
        rows = [record for record in scored if record["arm"] == arm]
        counts = {}
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

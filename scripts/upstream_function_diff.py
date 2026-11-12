"""Per-function upstream diff for the 25 old curated tool modules.

For each module in the OLD repo (Biolab/alloagent/tool/), enumerate
every top-level function and classify it against upstream Biomni at
two reference points:

  BASE = d15b3c9  ("Bump version to 0.0.8", 2025-10-27) - the old
         fork base the Biolab repo branched from.
  PIN  = 400c1f3  (2026-01-14) - our upstream pin (PINNED_UPSTREAM).

Classification per function (in the old module):
  upstream-identical  - exists upstream at BOTH refs with a
                        byte-identical normalised body.
  upstream-modified   - exists upstream at either ref but the body
                        differs (a diff summary is emitted).
  upstream-added-since-base - absent at BASE, present at PIN
                        (upstream evolved; the old repo predates it).
  ours-only           - present in the old module, absent from
                        upstream at both refs. These are the only
                        functions a KEEP/REWRITE/MERGE/DROP verdict
                        can meaningfully apply to.

Method notes:
  * Bodies are compared as normalised AST dumps (ast.dump with
    attributes off), so formatting/comments/whitespace do not create
    false positives; any real code change still shows.
  * Functions are matched by qualified name within the module.
  * A module absent upstream is reported as such (no ref rows).

Usage:
    python scripts/upstream_function_diff.py [--json OUT.json]
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

OLD_TOOL_DIR = Path(
    str(expand_home(r"<HOME>\Documents\CPSC\Biolab\alloagent\tool"))
)
REPO = Path(__file__).resolve().parents[1]

BASE = "d15b3c9"
PIN = "400c1f3"

UPSTREAM_PREFIX = "biomni/tool"

# Framework files that are not scientific tools.
SKIP = {"__init__.py", "tool_registry.py"}


def git_show(ref: str, path: str) -> str | None:
    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        return None
    return r.stdout


def top_level_functions(src: str) -> dict[str, str]:
    """Return {qualified_name: normalised_ast_dump} for top-level funcs.

    Includes plain `def` and `async def`. Nested defs are part of the
    parent's body, so they do not get their own entry.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return {"__PARSE_ERROR__": f"{type(exc).__name__}: {exc}"}
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = ast.dump(node, annotate_fields=True, include_attributes=False)
    return out


def function_source(src: str | None, name: str) -> str | None:
    """Return the raw text of one top-level function (for diffing)."""
    if not src:
        return None
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    lines = src.splitlines()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    return None


def diff_summary(old_text: str | None, ref_text: str | None, limit: int = 6) -> str:
    """One-line human summary of how `old_text` differs from `ref_text`.

    Reports added/removed line counts and the first few added and
    removed lines (truncated), which is what a reviewer needs to decide
    whether the change is a version bump or a behavioural change.
    """
    import difflib

    if ref_text is None:
        return "no upstream reference"
    if old_text is None:
        return "no local source"
    a = ref_text.splitlines()
    b = old_text.splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    added = removed = 0
    add_ex = []
    rem_ex = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
            for ln in a[i1:i2][:3]:
                rem_ex.append(ln.strip()[:70])
        if tag in ("replace", "insert"):
            added += j2 - j1
            for ln in b[j1:j2][:3]:
                add_ex.append(ln.strip()[:70])
    parts = [f"-{removed}/+{added} lines vs upstream"]
    if add_ex:
        parts.append("added: " + " | ".join(add_ex[:limit]))
    if rem_ex:
        parts.append("removed: " + " | ".join(rem_ex[:limit]))
    return "; ".join(parts)


def module_body_signature(src: str | None) -> str | None:
    if src is None:
        return None
    return hashlib_sha(src)


def hashlib_sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def classify(old_src: str, base_src: str | None, pin_src: str | None) -> dict:
    old_fns = top_level_functions(old_src)
    base_fns = top_level_functions(base_src) if base_src else {}
    pin_fns = top_level_functions(pin_src) if pin_src else {}

    rows = []
    for name, old_dump in sorted(old_fns.items()):
        in_base = name in base_fns
        in_pin = name in pin_fns
        if in_base and in_pin:
            if old_dump == base_fns[name] and old_dump == pin_fns[name]:
                verdict = "upstream-identical"
            elif old_dump == pin_fns[name]:
                verdict = "upstream-modified"
            else:
                verdict = "upstream-modified"
        elif in_base and not in_pin:
            verdict = "upstream-modified"
        elif in_pin and not in_base:
            verdict = "upstream-added-since-base"
        else:
            verdict = "ours-only"
        # Diff against whichever upstream ref this function exists in.
        if in_pin:
            ref_src, ref_label = pin_src, "PIN 400c1f3"
        elif in_base:
            ref_src, ref_label = base_src, "BASE d15b3c9"
        else:
            ref_src, ref_label = None, "none"
        summary = ""
        if verdict == "upstream-modified":
            summary = diff_summary(
                function_source(old_src, name), function_source(ref_src, name)
            )
        rows.append(
            {
                "function": name,
                "verdict": verdict,
                "in_base": in_base,
                "in_pin": in_pin,
                "ref": ref_label,
                "diff_summary": summary,
                "old_sha": hashlib_sha(old_dump),
                "base_sha": hashlib_sha(base_fns[name]) if in_base else None,
                "pin_sha": hashlib_sha(pin_fns[name]) if in_pin else None,
            }
        )
    return {
        "old_functions": len(old_fns),
        "base_functions": len(base_fns),
        "pin_functions": len(pin_fns),
        "functions": rows,
    }


def write_markdown(results: dict, totals: dict, out: Path) -> None:
    L = []
    L.append("# Old-tool review: per-function upstream provenance\n")
    L.append("Generated by `scripts/upstream_function_diff.py`. ")
    L.append(
        f"BASE = `d15b3c9` (\"Bump version to 0.0.8\", 2025-10-27) - the "
        "fork base of the Biolab repo.\n"
    )
    L.append(
        f"PIN = `400c1f3` (2026-01-14) - our upstream pin, from "
        "`PINNED_UPSTREAM`.\n"
    )
    L.append(
        "Bodies are compared as normalised AST dumps, so comments and "
        "formatting do not create false positives.\n"
    )
    L.append("\n## Totals\n")
    L.append("| classification | functions | port verdict applies? |")
    L.append("|---|---:|---|")
    order = [
        "upstream-identical",
        "upstream-modified",
        "upstream-added-since-base",
        "ours-only",
    ]
    for k in order:
        v = totals.get(k, 0)
        applies = (
            "**no** - covered by baseline, no port"
            if k == "upstream-identical"
            else ("yes" if v else "-")
        )
        L.append(f"| {k} | {v} | {applies} |")
    L.append(f"| **total** | **{sum(totals.values())}** | |\n")

    L.append("\n## Per-module counts\n")
    L.append("| module | upstream? | old fns | identical | modified | ours-only | needs verdict |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for mod, res in results.items():
        c = {}
        for row in res["functions"]:
            c[row["verdict"]] = c.get(row["verdict"], 0) + 1
        needs = c.get("upstream-modified", 0) + c.get("ours-only", 0)
        L.append(
            f"| `{mod}` | {'yes' if res['upstream_present'] else 'NO'} | "
            f"{res['old_functions']} | {c.get('upstream-identical', 0)} | "
            f"{c.get('upstream-modified', 0)} | {c.get('ours-only', 0)} | {needs} |"
        )

    L.append("\n## Functions needing a verdict\n")
    L.append(
        "Only these functions are candidates for KEEP / REWRITE / MERGE / "
        "DROP. Every `upstream-identical` function is already provided by "
        "the `baseline` arm and needs no port.\n"
    )
    for mod, res in results.items():
        rows = [
            r
            for r in res["functions"]
            if r["verdict"] in ("upstream-modified", "ours-only")
        ]
        if not rows:
            continue
        L.append(f"\n### `{mod}`\n")
        L.append("| function | class | ref | diff summary |")
        L.append("|---|---|---|---|")
        for r in rows:
            summary = r["diff_summary"] or ("not present upstream" if r["verdict"] == "ours-only" else "")
            summary = summary.replace("|", "\\|")
            L.append(
                f"| `{r['function']}` | {r['verdict']} | {r['ref']} | {summary} |"
            )
    out.write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default=None, help="write the full result as JSON")
    ap.add_argument(
        "--markdown",
        default=None,
        help="write a human-readable per-function provenance report",
    )
    args = ap.parse_args(argv)

    if not OLD_TOOL_DIR.is_dir():
        print(f"old tool dir not found: {OLD_TOOL_DIR}", file=sys.stderr)
        return 2

    modules = sorted(
        p.stem for p in OLD_TOOL_DIR.glob("*.py") if p.name not in SKIP
    )
    print(f"old modules: {len(modules)}")

    results = {}
    totals = {
        "upstream-identical": 0,
        "upstream-modified": 0,
        "upstream-added-since-base": 0,
        "ours-only": 0,
    }

    for mod in modules:
        old_src = (OLD_TOOL_DIR / f"{mod}.py").read_text(
            encoding="utf-8", errors="replace"
        )
        base_src = git_show(BASE, f"{UPSTREAM_PREFIX}/{mod}.py")
        pin_src = git_show(PIN, f"{UPSTREAM_PREFIX}/{mod}.py")
        res = classify(old_src, base_src, pin_src)
        res["module"] = mod
        res["upstream_present"] = base_src is not None or pin_src is not None
        res["base_module_sha"] = hashlib_sha(base_src) if base_src else None
        res["pin_module_sha"] = hashlib_sha(pin_src) if pin_src else None
        results[mod] = res
        for row in res["functions"]:
            totals[row["verdict"]] += 1
        counts = {}
        for row in res["functions"]:
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        print(
            f"  {mod}: {res['old_functions']} fns "
            f"(upstream={'yes' if res['upstream_present'] else 'NO'}) "
            + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        )

    print("\nTOTALS:", json.dumps(totals, indent=2))
    total_fn = sum(totals.values())
    print(f"all functions across all modules: {total_fn}")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"modules": results, "totals": totals}, indent=2),
            encoding="utf-8",
        )
        print(f"wrote {args.json}")
    if args.markdown:
        write_markdown(results, totals, Path(args.markdown))
        print(f"wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
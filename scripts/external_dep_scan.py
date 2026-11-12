"""Enumerate EVERY external top-level dependency of a set of modules.

`importlib.import_module` surfaces only the FIRST missing name in a
module's import chain, which under-reports: bioimaging reported
nibabel, then nnunet; genomics reported esm, then pybiomart. This
scanner parses the module AST and checks each third-party import
individually, so the audit table lists every blocker, not just the
first one encountered.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from pathlib import Path

STDLIB = set(sys.stdlib_module_names) | {"__future__", "typing_extensions"}


def module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                found.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def local_module_names(tool_dir: Path) -> set[str]:
    """Names that are first-party helper modules living beside the
    tools, not third-party packages.

    Upstream imports these without a package prefix
    (`import RNA`, `from community import best_partition`,
    `from eval_single_anndata import ...`), so a naive
    find_spec() check reports them as missing packages.
    """
    names: set[str] = set()
    for p in tool_dir.glob("*.py"):
        if p.stem != "__init__":
            names.add(p.stem)
    for p in tool_dir.iterdir():
        if p.is_dir() and (p / "__init__.py").is_file():
            names.add(p.name)
    return names


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--local-prefix", default="biomni",
                    help="package prefix to treat as first-party")
    args = ap.parse_args(argv)

    tool_dir = Path(args.tool_dir)
    first_party = local_module_names(tool_dir)
    mods = sorted(p for p in tool_dir.glob("*.py")
                  if p.name not in ("__init__.py", "tool_registry.py"))

    available: dict[str, bool] = {}
    report = {}
    for p in mods:
        external = sorted(
            m for m in module_imports(p)
            if m not in STDLIB
            and not m.startswith("_")
            and m != args.local_prefix
            and m not in first_party
        )
        missing = []
        for m in external:
            if m not in available:
                try:
                    available[m] = importlib.util.find_spec(m) is not None
                except (ImportError, ValueError):
                    available[m] = False
            if not available[m]:
                missing.append(m)
        report[p.stem] = {
            "external_deps": external,
            "missing": missing,
            "clean": not missing,
        }
        flag = "OK  " if not missing else "MISS"
        print(f"{flag} {p.stem}: missing={missing if missing else '-'}")

    n_missing = sum(1 for v in report.values() if v["missing"])
    print(f"\nmodules with >=1 missing external dep: {n_missing}/{len(mods)}")
    all_missing = sorted({m for v in report.values() for m in v["missing"]})
    print("distinct missing packages:", all_missing)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
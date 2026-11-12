"""STEP 5: import audit for every upstream Biomni tool module.

Runs each module in a FRESH subprocess (so one module's partial
import cannot mask another's) and records:

  import OK / FAIL, and the missing dependency if any.

A module that imports successfully may still fail at *call* time
because of a deferred import inside a function body; the audit
reports the module-level result only and flags known deferred-import
cases separately in the generated table.

Usage (in-container, baseline branch worktree):
    python scripts/upstream_import_audit.py --tool-dir <dir> --out <json>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKIP = {"__init__.py", "tool_registry.py"}

PROBE = r"""
import importlib, json, sys, traceback
mod = sys.argv[1]
try:
    importlib.import_module(mod)
    print(json.dumps({"module": mod, "ok": True, "error": None, "etype": None}))
except BaseException as e:  # noqa: BLE001
    print(json.dumps({
        "module": mod, "ok": False,
        "etype": type(e).__name__, "error": str(e)[:400],
    }))
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool-dir", required=True, help="dir holding the .py tool modules")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--prefix", default="biomni.tool", help="import package prefix")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args(argv)

    tool_dir = Path(args.tool_dir)
    if not tool_dir.is_dir():
        print(f"tool dir not found: {tool_dir}", file=sys.stderr)
        return 2

    mods = sorted(p.stem for p in tool_dir.glob("*.py") if p.name not in SKIP)
    print(f"auditing {len(mods)} modules under {args.prefix}", flush=True)

    results = []
    for m in mods:
        full = f"{args.prefix}.{m}"
        try:
            r = subprocess.run(
                [sys.executable, "-c", PROBE, full],
                capture_output=True,
                text=True,
                timeout=args.timeout,
            )
            line = (r.stdout or "").strip().splitlines()
            if line:
                rec = json.loads(line[-1])
            else:
                rec = {
                    "module": full,
                    "ok": False,
                    "etype": "NoOutput",
                    "error": (r.stderr or "")[:300],
                }
        except subprocess.TimeoutExpired:
            rec = {"module": full, "ok": False, "etype": "Timeout", "error": f">{args.timeout}s"}
        results.append(rec)
        status = "OK  " if rec["ok"] else "FAIL"
        print(f"  {status} {m}: {rec.get('etype') or ''} {rec.get('error') or ''}"[:160], flush=True)

    ok = sum(1 for r in results if r["ok"])
    fails = [r for r in results if not r["ok"]]
    print(f"\nimport OK {ok}/{len(results)}; FAIL {len(fails)}")

    Path(args.out).write_text(
        json.dumps({"total": len(results), "ok": ok, "results": results}, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
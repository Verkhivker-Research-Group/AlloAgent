#!/usr/bin/env python3
"""
benchmark_legacy.py
- Validate a Biomni web-chat JSON output against your schema + content rules
- Produce a simple pass/fail + list of issues (for CI or quick checks)
"""

import sys
from pathlib import Path
import json

# Local validator next to this file (the one we created earlier)
# If you put it elsewhere, adjust the import path or shell out via subprocess.
try:
    from validate_biomni_output import load_json  # reuse helper
    from validate_biomni_output import content_checks
    from jsonschema import Draft7Validator  # or Draft202012Validator if you kept 2020-12
except Exception:
    # Fallback if direct import fails (e.g., different folder): shell out
    import subprocess
    def shell_validate(p):
        r = subprocess.run(
            [sys.executable, "validate_biomni_output.py", str(p)],
            capture_output=True, text=True
        )
        print(r.stdout, end="")
        return r.returncode == 0
    def main():
        if len(sys.argv) < 2:
            print("Usage: python benchmark_legacy.py path/to/biomni_output.json")
            sys.exit(2)
        ok = shell_validate(Path(sys.argv[1]))
        sys.exit(0 if ok else 1)
    if __name__ == "__main__":
        main()
    sys.exit(0)

SCHEMA_PATH = Path(__file__).resolve().parent / "schema_biomni_output.json"

def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark_legacy.py path/to/biomni_output.json")
        sys.exit(2)

    output_path = Path(sys.argv[1])
    if not output_path.exists():
        print(f"ERROR: file not found: {output_path}")
        sys.exit(2)

    schema = load_json(SCHEMA_PATH)
    data = load_json(output_path)

    # Match the schema draft you decided to use:
    validator = Draft7Validator(schema)  # switch if you kept Draft202012
    struct_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    content_issues = content_checks(data)

    ok = True
    if struct_errors:
        ok = False
        print("❌ Schema validation errors:")
        for e in struct_errors:
            loc = "$" + "".join([f"/{p}" for p in e.path])
            print(f"  - {loc}: {e.message}")

    if content_issues:
        ok = False
        print("\n❌ Content validation issues:")
        for msg in content_issues:
            print(f"  - {msg}")

    if ok:
        print("✅ PASS: BIOMNI output passed schema + content checks.")
        sys.exit(0)
    else:
        print("\nResult: FAILED validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()

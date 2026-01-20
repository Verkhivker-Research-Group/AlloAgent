#!/usr/bin/env bash
set -euo pipefail

# Critic pipeline
# 1) Convert raw_output.txt -> critic_output.json via to_critic_json.py
# 2) Validate (min). If it fails, auto-fix and re-validate.
# 3) Full validate -> critic -> audit.
#
# Environment overrides (optional):
#   RAW_FILE   : source text file (default: raw_output.txt)
#   JSON_OUT   : primary JSON output (default: critic_output.json)
#   FIXED_OUT  : auto-fixed JSON output (default: critic_output.fixed.json)
#   OUTDIR     : reports output directory (default: out)

RAW_FILE=${RAW_FILE:-raw_output.txt}
JSON_OUT=${JSON_OUT:-critic_output.json}
FIXED_OUT=${FIXED_OUT:-critic_output.fixed.json}
OUTDIR=${OUTDIR:-out}

cd "$(dirname "$0")"

echo "[1/6] Converting $RAW_FILE -> $JSON_OUT"
python to_critic_json.py

INPUT="$JSON_OUT"

echo "[2/6] Minimal validation ($INPUT)"
if python validate_json_min.py "$INPUT"; then
    echo "Minimal validation passed."
else
    echo "Minimal validation failed. Attempting auto-fix -> $FIXED_OUT"
    python fix_json.py "$INPUT" "$FIXED_OUT"
    echo "Re-running minimal validation on $FIXED_OUT"
    python validate_json_min.py "$FIXED_OUT"
    INPUT="$FIXED_OUT"
fi

mkdir -p "$OUTDIR" "$OUTDIR/audit"

echo "[3/6] Full validation -> $OUTDIR"
python validate_output.py "$INPUT"

echo "[4/6] Critic -> $OUTDIR"
python critic_legacy.py "$INPUT"

echo "[5/6] Audit -> $OUTDIR/audit"
python gemini_audit.py "$INPUT" --out "$OUTDIR/audit/critic_report.txt"

echo "[6/6] Done. Final input used: $INPUT"
echo "Reports in: $OUTDIR (critic, validation), $OUTDIR/audit (audit)"
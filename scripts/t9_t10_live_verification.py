# t9_t10_live_verification.py - moved from build_logs/_part_c_live.py
# (c) 2026 AlloAgent-v2 contributors. Run via:
# docker run --rm -v '<HOME>\Documents\CPSC\AlloAgent-v2':/workspace -v '<HOME>\Documents\CPSC\AlloAgent-v2'\data\clinvar:/data/clinvar:ro -v'<HOME>\Documents\CPSC\AlloAgent-v2'\data\alphamissense:/data/alphamissense:ro -w /workspace -e REQUIRE_REAL_DATA=1 -e RUN_REAL_NETWORK=1 -e ALLOAGENT_ENV_SOURCE=<path-to-.env.extracted> alloagent-dev:v4 python /workspace/t9_t10_live_verification.py

"""Part C live verifications: T9 (local-pinned mode vs real
ClinVar) + T10 (real AlphaMissense TSV, including TP53 R175H).

Uses sys.stdout.reconfigure(line_buffering=True) so output is
flushed on every `print` even when stdout is redirected (Python
otherwise block-buffers when stdout is a pipe).

Run inside the container:
  python -u /workspace/build_logs/_part_c_live.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

# Force line-buffered stdout regardless of `python -u` correctness
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

T9_PATH = Path("/data/clinvar/variant_summary.txt.gz")
T9_MANIFEST = Path("/data/clinvar/MANIFEST")
T10_PATH = Path("/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz")


def emit(tag: str, payload: dict) -> None:
    print(f"--- {tag} ---", flush=True)
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(flush=True)


# ----- T9 local-pinned mode against the REAL ClinVar file -----
try:
    from biomni.tool.get_clinvar_variants import get_clinvar_variants
    T9_IMPORT_OK = True
    T9_IMPORT_ERR = None
except Exception as exc:
    T9_IMPORT_OK = False
    T9_IMPORT_ERR = f"{type(exc).__name__}: {exc}"

emit("T9.import", {"import_ok": T9_IMPORT_OK, "error": T9_IMPORT_ERR})

if T9_IMPORT_OK:
    t0 = time.time()
    try:
        result = get_clinvar_variants(
            "BRCA1", significance="pathogenic", mode="local",
            data_path=T9_PATH,
        )
        elapsed = round(time.time() - t0, 2)
        records = (result.get("data") or {}).get("variants") or []
        first = records[0] if records else {}
        vcv_ok = bool(first.get("accession", "").startswith("VCV"))
        emit("T9.brca1_pathogenic_local", {
            "elapsed_s": elapsed,
            "success": result.get("success"),
            "source": (result.get("data") or {}).get("source"),
            "total_count": (result.get("data") or {}).get("total_count"),
            "first_keys": sorted(first.keys()) if first else [],
            "first_accession": first.get("accession"),
            "first_title": first.get("title"),
            "vcv_pass": vcv_ok,
        })
    except Exception as exc:
        emit("T9.brca1_pathogenic_local.error", {
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc().splitlines()[-15:],
        })

    t0 = time.time()
    try:
        result = get_clinvar_variants(
            "ZZZZZZ", mode="local", data_path=T9_PATH,
        )
        elapsed = round(time.time() - t0, 2)
        emit("T9.unknown_gene_local", {
            "elapsed_s": elapsed,
            "success": result.get("success"),
            "total_count": (result.get("data") or {}).get("total_count"),
        })
    except Exception as exc:
        emit("T9.unknown_gene_local.error", {
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"{type(exc).__name__}: {exc}",
        })

# ----- T10 against the real AlphaMissense TSV -----
try:
    from biomni.tool.get_alphamissense_score import get_alphamissense_score
    T10_IMPORT_OK = True
    T10_IMPORT_ERR = None
except Exception as exc:
    T10_IMPORT_OK = False
    T10_IMPORT_ERR = f"{type(exc).__name__}: {exc}"

emit("T10.import", {"import_ok": T10_IMPORT_OK, "error": T10_IMPORT_ERR})

if T10_IMPORT_OK:
    t0 = time.time()
    try:
        result = get_alphamissense_score("P04637")
        elapsed = round(time.time() - t0, 2)
        records = (result.get("data") or {}).get("variants") or []
        r175h = next(
            (v for v in records
             if v.get("position") == 175 and v.get("alt_aa") == "H"
             and v.get("ref_aa") == "R"),
            None,
        )
        emit("T10.tp53_full", {
            "elapsed_s": elapsed,
            "success": result.get("success"),
            "source": (result.get("data") or {}).get("source"),
            "total_count": (result.get("data") or {}).get("total_count"),
            "r175h_found": r175h is not None,
            "r175h_record": r175h,
        })
    except Exception as exc:
        emit("T10.tp53_full.error", {
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"{type(exc).__name__}: {exc}",
        })

    t0 = time.time()
    try:
        result = get_alphamissense_score("P04637", position=175)
        elapsed = round(time.time() - t0, 2)
        emit("T10.tp53_position_175", {
            "elapsed_s": elapsed,
            "success": result.get("success"),
            "total_count": (result.get("data") or {}).get("total_count"),
            "all_alt_aa": [v.get("alt_aa") for v in (result.get("data") or {}).get("variants") or []],
        })
    except Exception as exc:
        emit("T10.tp53_position_175.error", {
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"{type(exc).__name__}: {exc}",
        })

    t0 = time.time()
    try:
        result = get_alphamissense_score("ZZZZZZ")
        elapsed = round(time.time() - t0, 2)
        emit("T10.unknown_uniprot", {
            "elapsed_s": elapsed,
            "success": result.get("success"),
            "total_count": (result.get("data") or {}).get("total_count"),
        })
    except Exception as exc:
        emit("T10.unknown_uniprot.error", {
            "elapsed_s": round(time.time() - t0, 2),
            "error": f"{type(exc).__name__}: {exc}",
        })

print("--- DONE ---", flush=True)

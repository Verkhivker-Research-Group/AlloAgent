"""STEP 6: B1 live verification against the REAL ChEMBL 37 SQLite.

Checks the committed criteria in docs/2_get_chembl_bioactivity_criteria.md
on the real database (not the synthetic fixture):

  B1-6  get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50")
        -> >= 1 record, standard_type='IC50', standard_units='nM'
  B1-7  same with target="P00519" (UniProt -> ChEMBL target resolution)
        -> >= 1 IC50 record
  B1-8  negative control target="CHEMBL99999999" -> empty, success=True
  B1-3  both input types (ChEMBL ID and UniProt) work

Prints RAW output so the verdict rests on the evidence, not on a
boolean. Read-only against the database.
"""
import json
import time
from pathlib import Path

from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

DB = "/data/chembl/chembl_37_sqlite/chembl_37.db"
print("db exists:", Path(DB).is_file(), DB)
print("db size:", Path(DB).stat().st_size if Path(DB).is_file() else "n/a")
print()

results = {}


def run(label, **kw):
    t0 = time.time()
    r = get_chembl_bioactivity(**kw)
    dt = time.time() - t0
    d = r.get("data") or {}
    n = d.get("total_count", len(d.get("activities", d.get("records", []))))
    recs = d.get("activities", d.get("records", []))
    print(f"--- {label} ---")
    print(f"  call: target={kw.get('target')!r} compound={kw.get('compound')!r} "
          f"standard_type={kw.get('standard_type')!r} mode={kw.get('mode')!r}")
    print(f"  success={r.get('success')} total_count={n} elapsed={dt:.2f}s")
    if r.get("error"):
        print(f"  error={r.get('error')[:200]}")
    print(f"  source={d.get('source')!r} release_date={d.get('release_date')!r}")
    if recs:
        print(f"  first record RAW: {json.dumps(recs[0], default=str)[:600]}")
        types = {x.get("standard_type") for x in recs}
        units = {x.get("standard_units") for x in recs}
        print(f"  distinct standard_type={types}")
        print(f"  distinct standard_units={units}")
    print()
    results[label] = {"success": r.get("success"), "total_count": n,
                      "elapsed_s": round(dt, 2), "error": r.get("error"),
                      "source": d.get("source")}
    return r, recs, dt


# B1-6: ChEMBL target id
r6, recs6, _ = run("B1-6 CHEMBL1862 x CHEMBL941 IC50",
                  target="CHEMBL1862", compound="CHEMBL941",
                  standard_type="IC50", mode="local", data_path=DB)

# B1-7: UniProt accession must resolve to the same target
r7, recs7, _ = run("B1-7 P00519 (UniProt) x CHEMBL941 IC50",
                  target="P00519", compound="CHEMBL941",
                  standard_type="IC50", mode="local", data_path=DB)

# B1-4: compound given by NAME rather than ChEMBL id
r8, recs8, _ = run("B1-4 name lookup: CHEMBL1862 x imatinib IC50",
                  target="CHEMBL1862", compound="imatinib",
                  standard_type="IC50", mode="local", data_path=DB)

# B1-8: negative control
r9, recs9, _ = run("B1-8 negative control CHEMBL99999999",
                   target="CHEMBL99999999", compound="CHEMBL941",
                   standard_type="IC50", mode="local", data_path=DB)

print("=== CRITERIA VERDICTS ===")
def chk(ok, label, extra=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label} {extra}")
    return ok

v = []
v.append(chk(r6.get("success") and recs6 and all(x.get("standard_type") == "IC50" for x in recs6),
             "B1-6 >=1 IC50 record for CHEMBL1862 x CHEMBL941",
             f"(n={len(recs6)})"))
v.append(chk(r6.get("success") and recs6 and any(x.get("standard_units") == "nM" for x in recs6),
             "B1-6 standard_units includes nM"))
v.append(chk(r7.get("success") and recs7 and all(x.get("standard_type") == "IC50" for x in recs7),
             "B1-7 UniProt P00519 resolves and returns >=1 IC50",
             f"(n={len(recs7)})"))
v.append(chk(r8.get("success") and recs8 and len(recs8) == len(recs6),
             "B1-4 compound-by-name matches compound-by-id",
             f"(name={len(recs8)} vs id={len(recs6)})"))
v.append(chk(r9.get("success") and len(recs9) == 0,
             "B1-8 negative control returns empty with success=True",
             f"(n={len(recs9)})"))
print(f"\nALL PASS: {all(v)}  ({sum(v)}/{len(v)})")
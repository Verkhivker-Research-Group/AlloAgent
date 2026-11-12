"""STEP 6: verify the unpacked ChEMBL SQLite.

Runs PRAGMA integrity_check and a molecule_dictionary row count, and
records the results so the acceptance evidence is reproducible. This
script only READS the database.
"""
import hashlib
import sqlite3
import sys
import time
from pathlib import Path

DB = Path(sys.argv[1] if len(sys.argv) > 1 else r"data\chembl\chembl_37\chembl_37_sqlite\chembl_37.db")

print(f"db: {DB}")
print(f"size_bytes: {DB.stat().st_size}")

t0 = time.time()
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

print("running PRAGMA integrity_check ...", flush=True)
rows = cur.execute("PRAGMA integrity_check").fetchall()
integrity = [r[0] for r in rows]
elapsed = time.time() - t0
print(f"integrity_check -> {len(integrity)} row(s) in {elapsed:.1f}s")
for r in integrity[:10]:
    print("   ", r)
ok = integrity == ["ok"]

for table in ("molecule_dictionary", "compound_records", "activities"):
    try:
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"count({table}) = {n:,}")
    except sqlite3.Error as e:
        print(f"count({table}) FAILED: {e}")

# B1 known-answer support rows for imatinib.
try:
    rows = cur.execute(
        "SELECT chembl_id, pref_name FROM molecule_dictionary "
        "WHERE lower(pref_name) = 'imatinib'"
    ).fetchall()
    print("imatinib molecule_dictionary rows:", rows)
except sqlite3.Error as e:
    print("imatinib lookup failed:", e)

con.close()
print("INTEGRITY_OK" if ok else "INTEGRITY_FAILED")
sys.exit(0 if ok else 1)
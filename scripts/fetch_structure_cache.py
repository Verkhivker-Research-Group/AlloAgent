"""Fetch the benchmark structures into the local structure cache.

The cache is mounted READ-ONLY and IDENTICALLY into both arms in the
restricted-egress scenario, so that the structure-dependent prompts can
be answered without any outbound access.
"""
import sys
import urllib.request
from pathlib import Path

PDB_IDS = [
    "1T4J",  # PTP1B + FRJ (the allosteric ligand) - S01, P01, P07, C01, C02, C06, K01, K02, H02
    "1OPK",  # ABL1 + MYR + P16 - S02, P05, V04, G02
    "1V4S",  # glucokinase + MRK + GLC - S03, P06, C04, V05
    "3O96",  # AKT1 + IQO - S04, V02, G04
    "5EHR",  # SHP2 + SHP099 (5OD) - S05, L04, K03, V01
    "1PZO",  # TEM-1 + two CBT copies - S06, P04, V06
    "5MO4",  # ABL1 + AY7 + NIL - S07, L03
    "6OIM",  # KRAS G12C + the covalent inhibitor - P02, V03, G01
    "1BTL",  # TEM-1 apo - P04, V06
    "2SHP",  # autoinhibited SHP2 - P03, C03, G03
    "1AKE",  # E. coli adenylate kinase - C05
]


def main() -> int:
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdb_id in PDB_IDS:
        for suffix, url in (
            ("pdb", f"https://files.rcsb.org/download/{pdb_id}.pdb"),
            ("cif", f"https://files.rcsb.org/download/{pdb_id}.cif"),
        ):
            target = out_dir / f"{pdb_id.lower()}.{suffix}"
            if target.is_file() and target.stat().st_size > 0:
                print(f"  have {target.name} ({target.stat().st_size} bytes)")
                continue
            try:
                with urllib.request.urlopen(url, timeout=120) as response:
                    body = response.read()
                target.write_bytes(body)
                print(f"  fetched {target.name} ({len(body)} bytes)")
            except Exception as error:  # noqa: BLE001
                print(f"  FAILED {target.name}: {type(error).__name__}: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

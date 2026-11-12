# B1 known-answer expectations against the REAL ChEMBL 37 database

**Committed BEFORE the tests that assert them were run, and never
edited afterwards.** Per the standing rule, a wrong expectation is
corrected only by adding a dated note in a NEW file, never by editing
this one. `docs/2_get_chembl_bioactivity_criteria.md` remains the
governing scientific criteria and is checksum-guarded; this file adds
the concrete real-database answers so the suite can reproduce the
5/5 live result instead of relying on a one-off script.

## Where every value below comes from

All values were read read-only from the real database and its manifest,
never invented:

- Database: `data/chembl/chembl_37_sqlite/chembl_37.db`,
  30,480,314,368 bytes, 72 tables / 208 indexes
  (`SELECT type, count(*) FROM sqlite_master GROUP BY type`).
- Archive: `data/chembl/chembl_37_sqlite.tar.gz`, 5,764,252,857 bytes,
  sha256 `33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281`.
- Manifest: `data/chembl/chembl_37_sqlite/MANIFEST.chembl_37.db`
  (`completed_at: 2026-10-22T05:46:06Z`).
- Molecule: `SELECT molregno, pref_name FROM molecule_dictionary
  WHERE chembl_id='CHEMBL941'` -> `(88797, 'IMATINIB')`.
- Target: UniProt `P00519` resolves through
  `target_dictionary -> target_components -> component_sequences` to
  `CHEMBL1862` (ABL1, *Homo sapiens*, tax_id 9606).
- Best IC50: the two-hop join
  `activities -> assays -> target_dictionary` filtered to
  `standard_type='IC50' AND standard_units='nM'`, ordered by
  `CAST(standard_value AS REAL)`, yields 91 rows in total and
  `activity_id=13370906`, `standard_value=19.9`, `standard_units='nM'`,
  `standard_relation='='`, `assay_chembl_id='CHEMBL2406231'`,
  `confidence_score=9`, `pchembl_value=7.7` as the lowest.

## The expectations the suite asserts

| # | Expectation | Value | Source |
|---|---|---|---|
| R-1 | `get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50", max_records=20, mode="local")` succeeds and returns 20 records | 20 | two-hop join on the real DB (91 matching rows exist) |
| R-2 | the lowest (first) returned record is `activity_id=13370906`, `standard_value=19.9`, `standard_units='nM'`, `assay_chembl_id='CHEMBL2406231'`, `confidence_score=9` | see left | ChEMBL 37 `activities` row 13370906 |
| R-3 | `molecule_chembl_id == 'CHEMBL941'` and `target_chembl_id == 'CHEMBL1862'` on every record | exact | two-hop join |
| R-4 | `target="P00519"` returns a result set **identical** to `target="CHEMBL1862"` | identical | UniProt -> `CHEMBL1862` resolution |
| R-5 | `compound="imatinib"` (lower case) returns a result set **identical** to `compound="CHEMBL941"` | identical | `pref_name='IMATINIB'`, matched case-insensitively |
| R-6 | `target="CHEMBL99999999"` returns `success=True` with `total_count == 0` | 0 | absent target |
| R-7 | `data.release_date == "2026-10-22T05:46:06Z"` and `data.source == "local:chembl_37:2026-10-22T05:46:06Z"` | exact | `MANIFEST.chembl_37.db` `completed_at` |
| R-8 | every returned record has `standard_type == 'IC50'` and `standard_units == 'nM'` | exact | the filter in the wrapper |

## Non-goals

- No claim is made about imatinib's potency beyond the specific lowest
  ChEMBL 37 IC50 record above.
- The web-API mode is not exercised against the real service here; it
  stays covered by the mocked test in
  `tests/test_B1_get_chembl_bioactivity.py`.
- These expectations are read-only. Nothing in this file authorises a
  write to the real database.
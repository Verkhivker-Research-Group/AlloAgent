# T8 — search_pdb_by_uniprot_and_ligand: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: RCSB PDB Search API v2
  (`https://search.rcsb.org/rcsbsearch/v2/query`).
- Both UniProt accession and ligand ID are matched via the
  `text` service, combined with a `group` query and `logical_operator=and`.
- Returned: the list of PDB entry IDs (4-character codes) that have
  a polymer entity with the given UniProt cross-reference AND a
  chemical component with the given ligand ID.
- Known answers (verified against the live API on 2026-10-10):
  - `P69905` (hemoglobin subunit alpha) + `HEM` (heme) →
    350 entries; first 5 in score order are
    `1A00, 1A01, 1A0U, 1A0Z, 1A3N` (all hemoglobin structures).
  - `P69441` (E. coli adenylate kinase) + `ATP` → 1 entry (`8RJ6`).
  - Unknown UniProt (`ZZZZZZ`) + `ATP` → 0 entries.
  - `P69441` + unknown ligand (`ZZZ`) → 0 entries.
- Status: NOT STARTED. The container has `requests` (conda-forge)
  and outbound HTTPS access. The tool is implemented as a thin
  wrapper over the RCSB Search API v2 POST endpoint.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T8-1 | `biomni/tool/search_pdb_by_uniprot_and_ligand.py` exists with the entry point `search_pdb_by_uniprot_and_ligand(uniprot_id, ligand_id)` | `git ls-files` returns the path. |
| T8-2 | The function POSTs a combined `text`-service query to `https://search.rcsb.org/rcsbsearch/v2/query` with `return_type=entry` and `logical_operator=and` over the UniProt and ligand nodes | The implementation uses `requests.post(url, json=query, timeout=...)` with the documented body shape. |
| T8-3 | UniProt attribute is `rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession` with `operator=exact_match` | The implementation hard-codes this attribute (verified working in `build_logs/_check_rcsb3.py` and `_check_rcsb7.py`). |
| T8-4 | Ligand attribute is `rcsb_chem_comp_container_identifiers.comp_id` with `operator=exact_match` | The implementation hard-codes this attribute (the `text` service rejects `rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id.chem_comp_id` and `rcsb_nonpolymer_entity_container_identifiers.chem_comp_ids`; only `rcsb_chem_comp_container_identifiers.comp_id` is enabled — verified in `build_logs/_check_rcsb6.py`). |
| T8-5 | Known-answer: `P69905` + `HEM` returns >= 10 hits and the first 5 are `1A00, 1A01, 1A0U, 1A0Z, 1A3N` (score order, live API) | The test asserts the first-5 set matches. |
| T8-6 | Known-answer: `P69441` + `ATP` returns >= 1 hit (8RJ6 is the only known hit on the current RCSB index) | The test asserts `len(ids) >= 1`. |
| T8-7 | Negative control: unknown UniProt (`ZZZZZZ`) + `ATP` returns 0 hits with `success=True` | The test asserts `len(ids) == 0`. |
| T8-8 | Negative control: `P69441` + unknown ligand (`ZZZ`) returns 0 hits with `success=True` | The test asserts `len(ids) == 0`. |
| T8-9 | Determinism: two calls with the same input return the same set of entry IDs (RCSB Search API is deterministic for a fixed query; the result list is sorted by score) | The test calls the function twice and asserts `set(ids_1) == set(ids_2)` and `ids_1 == ids_2` (same order). |
| T8-10 | The function returns the entry IDs in score order (highest score first) | The test asserts the first ID is one of the top-scored entries for the P69905+HEM query. |
| T8-11 | Lowercase / mixed-case input robustness: `p69905` and `hem` (or `ATP` vs `atp`) are accepted (the RCSB API is case-sensitive for ligand IDs but case-insensitive for UniProt accessions; the wrapper does NOT lowercase the inputs) | The test passes lowercase inputs and asserts the result is equivalent to the uppercase case (or that the result is empty for case-mismatched ligands). |
| T8-12 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| T8-13 | Tool card exists at `docs/tool_cards/T8_search_pdb_by_uniprot_and_ligand.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| T8-14 | Network failure handling: if the RCSB API is unreachable or returns a non-200 status, the function returns `success=False` with a descriptive `error` string (does not raise) | The test mocks `requests.post` to return a 500 and asserts `success=False, error=<non-empty>`. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T8-1 | (filled) | (filled) |
| T8-2 | (filled) | (filled) |
| T8-3 | (filled) | (filled) |
| T8-4 | (filled) | (filled) |
| T8-5 | (filled) | (filled) |
| T8-6 | (filled) | (filled) |
| T8-7 | (filled) | (filled) |
| T8-8 | (filled) | (filled) |
| T8-9 | (filled) | (filled) |
| T8-10 | (filled) | (filled) |
| T8-11 | (filled) | (filled) |
| T8-12 | (filled) | (filled) |
| T8-13 | (filled) | (filled) |
| T8-14 | (filled) | (filled) |

## Status

Implementation + tests deferred to the next commit, after this
criteria doc is reviewed.

## Dated notes (added after running; do NOT change the original criterion text above)

### 2026-10-14 — 1FPU is NOT a P00520+STI structure; its ligand is PRC

The earlier test fix (commit 1aed180, "test(T8): fix
accession-specificity test") dropped the 1FPU assertion
from `test_t8_accession_specificity_mouse_ortholog_excluded`
because the RCSB Search API for `P00520+STI` did not return
1FPU. This note records the evidence from the RCSB Data
API that confirms the fix was correct: 1FPU is a mouse
ABL1 structure (UniProt P00520) but its co-crystallized
inhibitor is **PRC** (a 4-anilinoquinazoline, distinct
from STI/imatinib which is a 2-phenylaminopyrimidine),
not STI.

Evidence (`build_logs/_t6_1fpu_check.py` run on 2026-10-14,
output in `build_logs/_t6_1fpu_check.log`):

1. `https://data.rcsb.org/rest/v1/core/entry/1FPU`
   - title: "CRYSTAL STRUCTURE OF ABL KINASE DOMAIN IN
     COMPLEX WITH A SMALL MOLECULE INHIBITOR"
   - `rcsb_entry_container_identifiers.polymer_entity_ids`: `['1']`
   - `rcsb_entry_container_identifiers.nonpolymer_entity_ids`:
     **missing** (the field is absent, not empty — consistent
     with the entry having no nonpolymer ligand in the
     standard schema)
2. `https://data.rcsb.org/rest/v1/core/polymer_entity/1FPU/1`
   - `reference_sequence_identifiers`: UniProt **P00520**
     (mouse ABL1) — confirms 1FPU is the expected organism
3. `https://files.rcsb.org/download/1FPU.pdb`
   (downloaded for verification, 413,181 bytes):
   - HETATM count by residue name: **99 HOH** (waters),
     **58 PRC** (the co-crystallized inhibitor)
   - No STI HETATM records in the file

Conclusion: the P00520+STI search correctly excludes 1FPU
because 1FPU does not co-crystallize STI. The test fix in
commit 1aed180 is correct. The test is kept as-is (asserts
1IEP in P00520+STI, not 1FPU) and the recall gap is
documented here rather than re-introduced as an
expected-known-gap test, because there is no recall gap —
1FPU simply has a different ligand.


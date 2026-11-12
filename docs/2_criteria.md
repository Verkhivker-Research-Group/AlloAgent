# Part 2 + Part 3 — Pass criteria (written BEFORE running anything)

Per the standing rule, the criteria below are committed before any
Part-2 tool is implemented and before the Part-3 report is generated.
They are NOT edited after results are observed. The verdict for each
tool is filled in its own criteria file (one per tool), and Part 3
collects the per-tool verdicts into the final table.

## Per-tool criteria (one per tool, all 7)

| # | Tool | Criteria file (one per tool, separate commit) |
|---|---|---|
| T1 | `map_residues_uniprot_pdb` (PDBe `mappings/uniprot/<pdb>` + `mappings/best_structures/<accession>`) | `docs/2_T1_criteria.md` |
| T2 | `get_uniprot_variants` (EBI Proteins `/features?type=VARIANT`, NOT `/variation`) | `docs/2_T2_criteria.md` |
| T3 | `get_stingallo_allosteric_residues` (`www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=&chain_id=`, 100/day + 30-PDB/day counter) | `docs/2_T3_criteria.md` |
| T4 | `detect_pockets_fpocket` (fpocket 4.2.3, parse `<basename>_out/`, negative scores, HETATM-strip) | `docs/2_T4_criteria.md` |
| T5 | `detect_pockets_p2rank` (P2Rank 2.5.1 + Java 17, `predict`, `bin/p2rank.jar`) | `docs/2_T5_criteria.md` |
| T6 | `normal_mode_analysis` (ProDy 2.6.1 ANM+GNM, `calcModes(zeros=True)`, deterministic) | `docs/2_T6_criteria.md` |
| T7 | `residue_contact_network` (Biotite 1.6.0 + NetworkX 3.6.1, 4.5 Å, betweenness, seeded community, shortest path) | `docs/2_T7_criteria.md` |

## Common test categories for every tool (per the brief)

- **known-answer test**: a real input + the expected output recorded
  BEFORE the test runs.
- **negative control**: a deliberately-bad input + the expected error
  dict (`{success: False, error: ...}`).
- **input-robustness test**: lowercase PDB ID; chain given/omitted;
  isoform accession; etc.
- **determinism test**: run twice → identical output.
- **offline fixture test**: a snapshot file; the test does not hit the
  network.
- **live test** behind `RUN_REAL_NETWORK=1`: hit the real backend.
- **runtime**: the test reports the wall-clock time in seconds.

## Part 3 — verdict table (filled AFTER each tool is done)

The Part 3 table is the per-tool PASS/FAIL/PARTIAL verdict collected
from each tool's criteria file. It is committed to `../alloagent_private/docs/3_report.md`
in a single follow-up commit ONCE every tool is done.

## Cross-cutting rules (applies to every tool)

- Tools must never quote a predictor's self-reported accuracy
  (asserted by `tests/test_tool_cards.py`).
- The function docstring mirrors the card's "Question the tool
  answers" sentence.
- The card file is `docs/tool_cards/T<id>_<tool>.md` and follows the
  template at `docs/tool_cards/T_template.md`.
- The wrapper `with_return_contract` is applied so the tool returns
  the 6-key contract dict.
- The decorator `@benchmark_blocklist` is applied so the tool is
  short-circuited when a benchmark-blocklist ID is on the list.
- The recording captures `tools_meta[name].schema_hash` so a regression
  in the schema is detectable.

## Verdict (filled ONCE after each tool's test runs)

| # | Status | Value / note |
|---|---|---|
| T1 | (filled) | (filled) |
| T2 | (filled) | (filled) |
| T3 | (filled) | (filled) |
| T4 | (filled) | (filled) |
| T5 | (filled) | (filled) |
| T6 | (filled) | (filled) |
| T7 | (filled) | (filled) |

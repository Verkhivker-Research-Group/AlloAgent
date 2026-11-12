# Port batch 3 — allosteric2 + allosteric verification tools: known-answer expectations

**Committed BEFORE the batch was implemented or run, and never edited
afterwards.** A wrong expectation is corrected only by a dated note in a
NEW file.

Scope: the 14 ours-only functions in `allosteric2` (7) and
`allosteric_verification_tools` (7) from the old repo.

Three of those 14 are the old repo's own `test_*` functions
(`test_hotspot_detection`, `test_allosteric_tools`,
`test_allosteric_evidence`). They are not tools -- `discover_tool_functions`
would register a function called `test_...` as an agent tool -- so the
port moves them into this repo's test suite as real pytest tests
(`tests/test_port_batch3_allosteric.py`).

## Data

| what | where | size |
|---|---|---|
| ASD AS (residue-level allosteric sites) | `/biolab_data/data_lake/ASD_Release_202309_AS.csv` | 3,102 rows |
| ASD XF (per-protein XML) | `/biolab_data/asd/ASD_Release_202306_XF` | 2,419 files |
| BioLiP | `/biolab_data/biolip/biolip.pkl` | 989,058 rows |
| PDB structures | `https://files.rcsb.org/download/<id>.pdb` | live |
| UniProt sequences | `https://www.uniprot.org/uniprot/<acc>.fasta` | live |

## Framework adaptation

- the standard contract dict; no stdout; errors as `success=False`;
- `allosteric_evidence` and `residue_interaction_networks` read the
  ported `parse_asd_xf` **contract** (`data.proteins`) rather than the
  old bare dict;
- `residue_interaction_networks` reads the ported
  `parse_biolip_interactions` contract (`data.records`);
- `evolutionary_conservation` uses a **stable** hash where the old code
  used Python's `hash()` (see the defect note below).

## The expectations

Every value was produced by running the old code's logic against the
real data on 2026-10-23.

### ID conversion (E-1 .. E-5)

| # | input | expectation |
|---|---|---|
| E-1 | `convert_uniprot_to_asd("P0AB91")` | `"ASD00020000_1"` |
| E-2 | `convert_asd_to_uniprot("ASD00020000_1")` | `"P0AB91"` |
| E-3 | `normalize_protein_id("P0AB91")` | `("P0AB91", "ASD00020000_1")` |
| E-4 | `normalize_protein_id("ASD00020000_1")` | `("P0AB91", "ASD00020000_1")` -- the same answer whichever form the caller used |
| E-5 | `normalize_protein_id("P99999")` | `(None, None)` |

### `allosteric_hotspot_detection` (E-6 .. E-9)

| # | input | expectation | source |
|---|---|---|---|
| E-6 | `uniprot_id="P00533"`, `min_modulator_count=2`, `percentile_threshold=75.0` | `success=True`; 11 ASD AS rows match; 10 distinct residues are seen; **1** residue clears the threshold of 2 modulators; `hotspot_count == 1`; the hotspot is residue `"6P1D"` with `importance_score == 0.62`, `modulator_count == 2`, `unique_modulators == 1`, `residue_type_score == 0.3` | `ASD_Release_202309_AS.csv` (P00533 = EGFR) |
| E-7 | `uniprot_id="P0AB91"`, `min_modulator_count=1`, `percentile_threshold=75.0` | 13 residues seen and 13 candidates; the 75th-percentile threshold is **0.62**; `hotspot_count == 13`; the top three by score are `"SER180"`, `"SER211"` and `"LYS214"`, each with `importance_score == 0.66`; `"PRO150"` scores 0.62 | same |
| E-8 | `uniprot_id="P04150"`, `min_modulator_count=2` | `success=True` with **no** hotspot candidates: P04150 (the glucocorticoid receptor) has **0** rows in the ASD AS file, so the summary says no hotspots were found | same |
| E-9 | `uniprot_id="P99999"` | `success=False`, error says the protein is not in the ASD index | input validation |

### `residue_interaction_networks` (E-10 .. E-11)

| # | input | expectation | source |
|---|---|---|---|
| E-10 | `uniprot_id="P0AB91"` | `success=True`; `allosteric_sites` has **1** entry; **13** residue nodes are created from that site's residue string; `network_edges == []` (no PPI file is supplied); `network_metrics.total_nodes == 13`, `total_edges == 0`, `density == 0.0`, `allosteric_node_count == 13`, `average_degree == 0.0`; `data_sources == ["ASD_XF"]` | ASD XF `ASD00020000_1.xml` |
| E-11 | `uniprot_id="P99999"` | `success=False`, error says the protein is not in the ASD index | input validation |

### `allosteric_evidence` (E-12 .. E-15)

| # | input | expectation | source |
|---|---|---|---|
| E-12 | `uniprot_id="P0AB91"` | `success=True`; `data.status == "CONFIRMED"`; **1** known site with `pdb_id == "1KFL"` and `site_id == "1KFL-1"`; `modulator_count == 5`; `gene_name == "aroG"` | ASD XF |
| E-13 | `uniprot_id="P51639"` | `success=True`; `data.status == "UNCERTAIN"` (in ASD, no curated site); `known_sites == []`; `modulator_count == 1` | ASD XF `ASD00030000_1.xml` |
| E-14 | `uniprot_id="P99999"` | `success=True`; `data.status == "NOT_CONFIRMED"` | input validation |
| E-15 | neither `uniprot_id` nor `pdb_id` | `success=False` | input validation |

### Structural verification tools (E-16 .. E-20)

PDB `1CRN` (crambin, 46 residues, chain A) downloaded from RCSB:
327 atoms, 46 residues, one chain.

| # | input | expectation | source |
|---|---|---|---|
| E-16 | `load_pdb("1CRN")` | `success=True`; the structure has **327** atoms, **46** residues and the chain list `["A"]` | RCSB `1CRN.pdb` |
| E-17 | `structural_distance("1CRN", [("A", 10)], [("A", 40)])` | `success=True`; `avg_distance == 5.4861`; `all_distances == [5.486]`; `score == 0.3` (the "too close to the active site" band) | 1CRN heavy-atom coordinates |
| E-18 | `pocket_geometry("1CRN", [("A", i) for i in 10..19])` | `success=True`; `volume == 928.3`; `max_extent == 18.74`; `asphericity == 0.2102`; `shape_score_pmi == 1.0`; `score == 1.0` | 1CRN convex hull over 83 heavy atoms |
| E-19 | `residue_accessibility("1CRN", [("A", 10), ("A", 20), ("A", 30)])` | `success=True`; `avg_rsasa == 27.16`; `avg_hydrophobicity == -1.87`; `score == 0.772` | 1CRN Shrake-Rupley SASA, Tien et al. maximum SASA table |
| E-20 | `evolutionary_conservation("P00688", [("A", 10), ("A", 50)])` | `success=True`; `avg_conservation == 0.019573`; `score == 0.034`; **and the same values on a second call in the same process and in a different process** | UniProt P00688 FASTA + the surrogate entropy model |

## Three real defects in the old code, fixed by this port

1. **`evolutionary_conservation` was not deterministic.** It seeded
   `np.random` with `hash(f"{uniprot_id}_{res_num}") % 2**32`, and
   Python salts `hash()` for strings per process, so the same input
   produced a different "conservation" score on every run. The port uses
   a stable sha256-derived seed, so the value is reproducible.

2. **The old `test_hotspot_detection` used a protein with no data.** It
   called `allosteric_hotspot_detection("P04150")`, but P04150 has **0**
   rows in `ASD_Release_202309_AS.csv` (E-8), so the test could only ever
   have reported "no hotspots". The ported test uses P00533 (EGFR),
   which has 11 rows and produces a real hotspot.

3. **The BioLiP branch of `residue_interaction_networks` could never
   fire.** It looked for a column literally named `Residue` in the
   BioLiP interaction table, but the real columns are
   `Binding_Site_Residues_PDB` and `Catalytic_Site_Residues_PDB`. The
   port reads the ported `parse_biolip_interactions` contract and uses
   the real column names.

## Non-goals

- `evolutionary_conservation` does **not** measure real sequence
  conservation. It is a deterministic pseudo-MSA surrogate: the old
  code's own comments call it "Pseudo-MSA simulation". Both the
  docstring and the tool card say so. It is not evidence of
  conservation.
- The pocket-geometry volume is a convex hull of the candidate
  residues, which the old code itself flagged as an overestimate.
- `allosteric_hotspot_detection` ranks residues that already appear in
  the curated ASD AS file; it does not predict new allosteric sites.

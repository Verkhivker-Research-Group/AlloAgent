# Port batch 1 — allosteric + biolip: known-answer expectations

**Committed BEFORE the batch was implemented or run, and never edited
afterwards.** A wrong expectation is corrected only by a dated note in a
NEW file.

Scope: the 13 ours-only functions in `allosteric` (7) and `biolip` (6)
from the old repo (`Biolab/alloagent/tool/`). Upstream-identical
functions are covered by `baseline` and are not ported.

## Framework adaptation (applies to every function in this batch)

The old functions returned bare Python objects, printed to stdout, and
raised on error. The ported versions:

- return the standard contract dict
  `{success, data, error, source, source_version, query_time_utc}`;
- never print (the agent records the return value, not stdout);
- return `success=False` with a descriptive `error` instead of raising;
- convert pandas DataFrames to `{"records": [...], "columns": [...]}`
  because the per-run recorder is JSON;
- use a 30 s HTTP timeout and retry with backoff;
- cache successful network responses on disk
  (`~/.cache/alloagent/`, 24 h TTL) so a repeated lookup does not repeat
  the network call.

## Data sources

| what | where | how |
|---|---|---|
| PDBe mappings | `https://www.ebi.ac.uk/pdbe/api/mappings/...` | live API |
| ChEMBL | `chembl_webresource_client` | live API |
| PubChem | `pubchempy` | live API |
| BioLiP | `biolip/biolip.pkl` in the Biolab data lake | read-only mount at `/biolab_data` |
| CovInDB | `data_lake/CovInDB_All.csv` in the Biolab data lake | read-only mount at `/biolab_data` |

`/biolab_data` is the Biolab `data/` directory mounted read-only by the
runner. It holds no secrets.

## The expectations

Every value below was read from the real source before this file was
written (2026-10-23).

### `pdb_to_uniprot` — PDBe

| # | input | expectation | source |
|---|---|---|---|
| A-1 | `"1TIM"` | `success=True`; `data.chains` contains `A` and `B`; both map to `P00940`; `data.uniprot_ids` == `["P00940"]` | PDBe `mappings/uniprot/1TIM` (HTTP 200) |
| A-2 | `"1tim"` (lower case) | identical to A-1 (the accessor upper-cases) | same |
| A-3 | `"XXXX"` (not a 4-character PDB ID) | `success=False`, `error` mentions the 4-character requirement | input validation |
| A-4 | `"ZZZZ"` (valid format, no such entry) | `success=True` with `data.chains == {}` and `data.uniprot_ids == []` | PDBe returns no mapping |

### `uniprot_to_pdb` — PDBe

| # | input | expectation | source |
|---|---|---|---|
| A-5 | `"P04637"` (human TP53) | `success=True`; `data.pdb_ids` has **321** entries; the first 10 sorted are exactly `1A1U, 1AIE, 1C26, 1DT7, 1GZH, 1H26, 1HS5, 1JSP, 1KZY, 1MA3` | PDBe `mappings/all_isoforms/P04637` (HTTP 200) |
| A-6 | `"P05142"` (mouse TIM — no PDB entry) | `success=True` with `data.pdb_ids == []` | PDBe returns no PDB mapping |
| A-7 | `"P04637"` is deterministic | two calls return the same list | same |

### `cross_reference_ligands_chembl_pubchem` — ChEMBL + PubChem

| # | input | expectation | source |
|---|---|---|---|
| A-8 | `uniprot_id="P04637"`, `ligands=[{"ligand_name": "imatinib"}]`, `detail_level="slim"` | `success=True`; the ligand entry has `chembl_id == "CHEMBL941"`, `chembl_properties.formula == "C29H31N7O"`, `chembl_properties.molecular_weight == 493.62`, `chembl_properties.alogp` present, `chembl_structure.inchi_key == "KTUFNOKKBVMGRW-UHFFFAOYSA-N"`, `chembl_classification.usan_stem` present, `chembl_approval.max_phase == 4.0`, `chembl_approval.first_approval == 2001`; `pubchem_cid == 5291`; `chembl_synonyms[:3]` are `CGP057148B`, `CGP-57148B`, `Glamox` | ChEMBL 37 `molecule.filter(pref_name__icontains="imatinib")` and PubChem `get_compounds("imatinib","name")` |
| A-9 | same, `detail_level="full"` | `chembl_raw` and `pubchem_raw` present instead of the slim fields | same |
| A-10 | `ligands=[]` | `success=True`, `data.ligands == []` | input validation |
| A-11 | a ligand name that matches nothing | the entry carries `error` and the other ligands are still returned (per-ligand isolation) | same |

### `map_covalent_probes_to_allosteric` — CovInDB

| # | input | expectation | source |
|---|---|---|---|
| A-12 | `uniprot_id="P00519"`, `dataset_path=<the real CovInDB_All.csv>` | `success=True`; `data.total_entries == 23`; every record has `Target_Gene == "ABL1"` and `Target_Name == "Tyrosine-protein kinase ABL1"`; every record's `Site` is `"NT"`; `data.war_head_counts == {"Michael Acceptor": 21, "Halohydrocarbon": 2}`; the 23 rows collapse to **6** distinct `InChI_Key` values | `data_lake/CovInDB_All.csv` (17,774 rows total; 23 match `Target` containing `P00519`) |
| A-13 | `uniprot_id="P04637"` | `success=True` with `data.total_entries == 0` (TP53 has no covalent-probe rows) | same |
| A-14 | a `dataset_path` that does not exist | `success=False` with an `error` naming the missing path | input validation |

### `analyze_site_patterns` — pure analysis

| # | input | expectation | source |
|---|---|---|---|
| A-15 | a DataFrame with `Parsed_Sites` = `[["NT"], ["CYS-481"], ["SER-195"]]` | `success=True`; `data.total_unique_sites == 3`; `data.total_entries == 3`; `data.most_common_sites[0] == ["NT", 1]`; `data.residue_distribution` contains `["CYS", 1]` and `["SER", 1]` | pure function, hand-computed |
| A-16 | a DataFrame with no `Parsed_Sites` column | `success=True` with `total_unique_sites == 0` and `total_entries` equal to the row count | pure function |

### `biolip_ligands` / `parse_biolip_interactions` — BioLiP

| # | input | expectation | source |
|---|---|---|---|
| A-17 | `biolip_ligands("1GG1")` | `success=True`; `data.ligands == ["MN", "PGA"]`; `data.total_interactions == 8`; `data.chains == ["A","B","C","D"]`; `data.uniprot_ids == ["P0AB91"]` | `biolip/biolip.pkl` (989,058 rows; 8 rows for `1gg1`) |
| A-18 | `biolip_ligands("4HHB")` | `data.ligands == ["HEM"]`; `data.total_interactions == 4`; `data.uniprot_ids == ["P68871", "P69905"]` | same (4 rows for `4hhb`) |
| A-19 | `biolip_ligands("2RTQ", chain="B")` | `data.ligands == ["IMI"]`; `data.total_interactions == 1` | same (2 rows for `2rtq`, chains B and D) |
| A-20 | `biolip_ligands("1TIM")` | `success=True` with `data.ligands == []` and `data.total_interactions == 0` — **1TIM is absent from BioLiP** (a real negative control, not a failure) | same |
| A-21 | `parse_biolip_interactions("1GG1", "A")` | `data.total_interactions == 2` | same (8 rows over 4 chains) |

### `fetch_allosteric_residue_potential` — STINGAllo (MERGE)

| # | expectation |
|---|---|
| A-22 | This function queries `https://stingallo.cbi.cnptia.embrapa.br/api/afrs` — **the same endpoint, with the same parameters, as the already-verified T3 tool** `get_stingallo_allosteric_residues` in `biomni/tool/get_stingallo_allosteric_residues.py`. T3 additionally enforces the API's documented rate limits (100 requests/IP/day, 30 unique PDBs/IP/day) via a persistent counter. Porting a second, unrestricted caller would double the rate-limit exposure. The ported function is therefore a **MERGE**: it delegates to the verified T3 implementation so there is one code path and one rate-limit counter. Verdict recorded in the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md) as MERGE -> T3. |

## Non-goals

- No claim is made that any of these functions predicts an allosteric
  site. `map_covalent_probes_to_allosteric` classifies *covalent-probe
  attachment sites*; it does not predict allostery.
- The BioLiP and CovInDB answers depend on the data-lake snapshot; the
  file sizes and row counts above pin which snapshot was used.

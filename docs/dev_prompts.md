# Arm D development prompts

Eight prompts used to exercise arm D end to end. They are **development**
prompts: they exist to check the pipeline (tool exposure, the return
contract, the per-run recording), not to be scored.

They are disjoint from any benchmark: no prompt here comes from
`Biolab/eval_ablation`, `Biolab/prep_reports` or any benchmark task
file, and none of them reuses a benchmark question verbatim.

Each prompt is run **once**. No prompt is reworded after seeing a
result: if a run fails, the failure is recorded as a pipeline bug (or a
tool limitation) and the prompt is not tuned to make it pass.

## The prompts

| # | id | prompt | tools it should reach for |
|---|---|---|---|
| 1 | D1 | "Map the UniProt accession P04637 to its PDB structures and report the residue numbers of the DNA-binding domain." | `map_pdb_to_best_structures`, `map_residues_uniprot_pdb` |
| 2 | D2 | "Which ClinVar variants are recorded for the gene BRCA1, and how many of them are classified as pathogenic?" | `get_clinvar_variants` |
| 3 | D3 | "What AlphaMissense pathogenicity score does the TP53 R175H substitution have?" | `get_alphamissense_score` |
| 4 | D4 | "What IC50 records does ChEMBL hold for imatinib against ABL1 (UniProt P00519)?" | `get_chembl_bioactivity` |
| 5 | D5 | "For PDB entry 1CRN, list the allosteric residues the STINGAllo database records." | `get_stingallo_allosteric_residues` |
| 6 | D6 | "Which ligands does the BioLiP database record as bound in PDB entry 1GG1, and which chains do they bind?" | `biolip_ligands`, `parse_biolip_interactions` |
| 7 | D7 | "Does the Allosteric Database confirm curated allosteric sites for UniProt P0AB91, and which modulators are involved?" | `allosteric_evidence`, `parse_asd_xf` |
| 8 | D8 | "Rank the residues of EGFR (UniProt P00533) that several modulators act on, and say which of them are the top candidate." | `allosteric_hotspot_detection`, `convert_uniprot_to_asd` |

## How they are run

`scripts/run_dev_prompts.py` runs each prompt once, in order, with:

- the committed evaluation settings (`biomni/eval_settings.py`:
  temperature 1.0, top_p 0.95, tool retriever forced off,
  `DB_TOOL_TEMPERATURE` 0.0);
- `no_tag_limit` at its committed default (5);
- the arm D exposed list applied
  (`biomni.tool._registration.apply_exposed_tools`);
- `record_run=True`, so every run writes a per-run JSON.

The per-run JSON is the evidence for the report. Each file must contain:
`config` (model, source, base URL host, temperature, top_p,
recursion_limit), `token_total` (input/output/total tokens),
`messages` (the step-by-step trace), `wall_time_s`, `git_commit`,
`git_branch`, `git_dirty`, `image_id` and `n_steps`.

## Results

The per-run JSON files, the raw log and the per-run summary table are
recorded in `../alloagent_private/docs/3_report.md` under the dated section for this
session.

# P16 cross_reference_ligands

## Question the tool answers

Which local ligand datasets have a record for each of these ligands, and what do those records say?

## What it does NOT answer

It does not answer whether a ligand is an allosteric or an orthosteric binder, and it does not give a binding affinity.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | no | `None` | PDB id, used for the BioLiP lookup |
| `uniprot_id` | `str` | no | `None` | UniProt accession, used for the ASD AP and ASD XF lookups |
| `ligands` | `list` | no | `None` | explicit ligand names; None derives them from `pdb_id` via BioLiP |
| `databases` | `list` | no | `None` | dataset ids: biolip, asd_ap, asd_dr, asd_xf, chembl_pubchem |
| `detail_level` | `str` | no | `"slim"` | `"slim"` or `"full"`; passed to the ChEMBL/PubChem lookup |
| `use_llm` | `bool` | no | `False` | best-effort LLM summary of the counts |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{query, databases, results: [{ligand, provenance, data}], summary: {total_ligands, per_database}, llm_summary, metadata}`.

## Source and version

- upstream URL: BioLiP, ASD AP/DR/XF, and the ChEMBL 37 + PubChem web services, depending on `databases`

## Runtime

- BioLiP and ASD reads are in-memory after the first call; the ChEMBL/PubChem branch is one network call per ligand; offline unless `chembl_pubchem` is requested

## Determinism

- deterministic for a given snapshot, except the ChEMBL/PubChem branch whose rankings can change

## Failure modes

- no ligands, no uniprot_id and no pdb_id -> `success=False`, error says there is nothing to cross-reference
- unknown database id -> `success=False`, error lists the supported ids
- detail_level other than slim/full -> `success=False`

## Known-answer test

- expectation: `pdb_id="1GG1"`, `databases=["biolip"]` -> 2 results, ligands `MN` and `PGA`, each with `provenance == ["biolip"]` and a non-empty `data.biolip`
- source of the expectation: BioLiP 1gg1, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-12)

## Negative control

- expectation: `uniprot_id="P41240"`, `databases=["asd_ap"]` -> the result carries `provenance == ["asd_ap"]` with 16 AP rows, the first with `pdb_id == "1BYG"` and `score == 0.535`

## Code location and version

- function: `biomni/tool/cross_reference.py::cross_reference_ligands`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

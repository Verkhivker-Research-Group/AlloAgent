# P3 cross_reference_ligands_chembl_pubchem

## Question the tool answers

What do ChEMBL and PubChem record about a named ligand?

## What it does NOT answer

It does not say whether the ligand is an allosteric or an orthosteric binder of the target, and it does not give an activity measurement against that target.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession of the target |
| `ligands` | `list` | yes | `-` | list of dicts with a `ligand_name` key |
| `detail_level` | `str` | no | `"slim"` | `"slim"` for curated fields, `"full"` for raw records |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{protein_id, ligands: [{name, chembl_id, chembl_synonyms, chembl_properties, chembl_structure, chembl_classification, chembl_approval, pubchem_cid}], total, detail_level}`.

## Source and version

- upstream URL: ChEMBL 37 web service via `chembl_webresource_client`; PubChem PUG REST via `pubchempy`; live services

## Runtime

- typical latency 1-3 s per ligand; 30 s client timeout; online; one ChEMBL and one PubChem call per ligand

## Determinism

- partial: ChEMBL and PubChem rankings can change, and the ChEMBL match is the first of a name-similarity search

## Failure modes

- a ligand that matches nothing -> that entry carries `error`; the other ligands are still returned
- ChEMBL or PubChem exception -> that entry carries `error` naming the lookup
- empty ligand list -> `success=True` with `ligands == []`

## Known-answer test

- expectation: input `P04637` + `[{"ligand_name": "imatinib"}]` -> `chembl_id == "CHEMBL941"`, formula `C29H31N7O`, molecular weight `493.62`, inchi_key `KTUFNOKKBVMGRW-UHFFFAOYSA-N`, `max_phase == 4.0`, `first_approval == 2001`, `pubchem_cid == 5291`
- source of the expectation: ChEMBL 37 + PubChem live responses, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-8)

## Negative control

- expectation: input `P04637` + `[{"ligand_name": "zzzznotacomound"}]` -> `success=True`, that entry carries `error`

## Code location and version

- function: `biomni/tool/allosteric.py::cross_reference_ligands_chembl_pubchem`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

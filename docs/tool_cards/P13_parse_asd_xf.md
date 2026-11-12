# P13 parse_asd_xf

## Question the tool answers

Which allosteric sites and modulators does the Allosteric Database record for a protein?

## What it does NOT answer

It does not predict an allosteric site and it does not score the sites; it reports the curated ASD record.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `target_proteins` | `list` | no | `None` | UniProt accessions to extract; None extracts all 2,412 indexed proteins |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{proteins: {<uniprot_id>: {protein_metadata, sites, modulators}}, total_proteins, requested}`.

## Source and version

- upstream URL: ASD (Allosteric Database) `ASD_Release_202306_XF` XML files, 2,419 files over 2,412 proteins, mounted read-only at `/biolab_data`; protein -> file map committed as `biomni/tool/_asd_index.tsv`

## Runtime

- a few milliseconds per protein (one XML file each); the protein -> file map is a committed TSV, so no directory scan is needed; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- ASD XF directory missing -> `success=False`, error names the missing directory
- target_proteins not a list -> `success=False`
- an accession that is not in the index -> simply absent from the result

## Known-answer test

- expectation: input `["P0AB91"]` -> one protein; `gene_name == "aroG"`; 1 site with `pdb_id == "1KFL"`, `pdb_site == "1KFL-1"`, `feature == "Inhibitor"`, `function == "Inner Protein Regulator"`; 5 modulators, the first `ASD00020003` (drugbank `No`) and the fourth `ASD02170001` (drugbank `Yes`)
- source of the expectation: ASD_Release_202306_XF, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-1..D-5)

## Negative control

- expectation: input `["P51639"]` -> 0 sites and 1 modulator (`ASD00030001`, feature `Activator`)

## Code location and version

- function: `biomni/tool/asd.py::parse_asd_xf`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

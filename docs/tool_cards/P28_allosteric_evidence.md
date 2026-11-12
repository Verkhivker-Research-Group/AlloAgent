# P28 allosteric_evidence

## Question the tool answers

Does the Allosteric Database confirm that this protein has curated allosteric sites?

## What it does NOT answer

It does not predict allostery for a protein ASD does not cover: `NOT_CONFIRMED` means the database has no record, not that the protein has no allostery.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | no | `None` | UniProt accession |
| `pdb_id` | `str` | no | `None` | PDB id, used when no UniProt accession is given |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{status, message, protein_id, protein_name, gene_name, known_sites, modulator_count, modulators}`; `status` is `CONFIRMED`, `UNCERTAIN` or `NOT_CONFIRMED`.

## Source and version

- upstream URL: ASD `ASD_Release_202306_XF` XML files, mounted read-only at `/biolab_data`

## Runtime

- a few hundred milliseconds; offline

## Determinism

- deterministic for a given ASD snapshot

## Failure modes

- neither id given -> `success=False`
- the ASD snapshot is missing -> `success=False`

## Known-answer test

- expectation: input `P0AB91` -> `status == "CONFIRMED"`, 1 known site with `pdb_id == "1KFL"` and `site_id == "1KFL-1"`, `modulator_count == 5`, `gene_name == "aroG"`
- source of the expectation: ASD XF, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-12)

## Negative control

- expectation: input `P51639` -> `status == "UNCERTAIN"` (in ASD, no curated site) and `modulator_count == 1`

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::allosteric_evidence`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

# P2 uniprot_to_pdb

## Question the tool answers

Which PDB entries are known for a given UniProt accession?

## What it does NOT answer

It does not say which entry shows a particular conformational state, and it does not indicate whether any of them is allosteric.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession, case-insensitive |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, pdb_ids: [str, ...], total: int}`; `pdb_ids` is sorted.

## Source and version

- upstream URL: PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/mappings/all_isoforms/<uniprot_id>`; live service

## Runtime

- typical latency 0.2-1 s; 30 s HTTP timeout; one request per call; online

## Determinism

- deterministic for a given accession while the PDBe mapping set is unchanged

## Failure modes

- empty accession -> `success=False`
- network failure -> `success=False`, error starts `PDBe request failed`
- non-JSON body -> `success=False`, error starts `PDBe returned invalid JSON`

## Known-answer test

- expectation: input `P04637` -> 321 entries; the first ten sorted are `1A1U, 1AIE, 1C26, 1DT7, 1GZH, 1H26, 1HS5, 1JSP, 1KZY, 1MA3`
- source of the expectation: PDBe live response, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-5)

## Negative control

- expectation: input `P05142` (mouse TIM, no PDB entry) -> `success=True`, `pdb_ids == []`

## Code location and version

- function: `biomni/tool/allosteric.py::uniprot_to_pdb`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

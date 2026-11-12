# P1 pdb_to_uniprot

## Question the tool answers

Which UniProt accession does each chain of a given PDB entry map to?

## What it does NOT answer

It does not say whether the structure is an allosteric or an orthosteric form, and it does not list residues in contact with a ligand.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id, case-insensitive |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chains: {chain: [uniprot, ...]}, uniprot_ids: [str, ...], mappings: [{chain_id, uniprot_id, unp_start, unp_end}, ...]}`.

## Source and version

- upstream URL: PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<pdb_id>`; no release tag, live service

## Runtime

- typical latency 0.2-1 s; 30 s HTTP timeout; one request per call; online

## Determinism

- deterministic for a given PDB id while the PDBe mapping set is unchanged

## Failure modes

- pdb_id not 4 characters -> `success=False`, error names the 4-character requirement
- network failure -> `success=False`, error starts `PDBe request failed`
- non-JSON body -> `success=False`, error starts `PDBe returned invalid JSON`

## Known-answer test

- expectation: input `1TIM` -> `chains` contains `A` and `B`, both mapping to `P00940`; `uniprot_ids == ["P00940"]`
- source of the expectation: PDBe live response, 2026-10-23 (see docs/2_port_batch1_allosteric_known_answers.md A-1)

## Negative control

- expectation: input `ZZZZ` (well-formed, no such entry) -> `success=True`, `chains == {}`, `uniprot_ids == []`

## Code location and version

- function: `biomni/tool/allosteric.py::pdb_to_uniprot`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

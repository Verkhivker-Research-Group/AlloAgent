# P6 fetch_allosteric_residue_potential

## Question the tool answers

Which residues does STINGAllo list as allosteric for a PDB entry and chain?

## What it does NOT answer

It does not say whether a residue is allosteric in a particular conformational transition, and it does not rank the residues.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` | yes | `-` | 4-character PDB id |
| `chain_id` | `str` | no | `None` | optional chain id |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{pdb_id, chain_id, residues: [...], `merged_into: "get_stingallo_allosteric_residues"}`.

## Source and version

- upstream URL: STINGAllo API, `https://stingallo.cbi.cnptia.embrapa.br/api/afrs`; the same endpoint as the verified T3 tool

## Runtime

- typical latency 0.5-2 s; 30 s HTTP timeout; STINGAllo limits 100 requests/IP/day and 30 unique PDBs/IP/day, enforced by the shared T3 counter; online

## Determinism

- deterministic for a given entry while the STINGAllo data is unchanged

## Failure modes

- daily request or unique-PDB limit reached -> `success=False`, error states the limit
- upstream HTTP error -> `success=False` with the upstream message

## Known-answer test

- expectation: the returned `residues` list is identical to `get_stingallo_allosteric_residues(pdb_id, chain_id)` for the same inputs
- source of the expectation: MERGE into T3 (docs/2_port_batch1_allosteric_known_answers.md A-22); T3's own known-answer test is the authority

## Negative control

- expectation: an empty `pdb_id` -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric.py::fetch_allosteric_residue_potential`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

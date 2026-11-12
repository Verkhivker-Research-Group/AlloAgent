# P22 residue_interaction_networks

## Question the tool answers

What residue-interaction network connects the curated allosteric sites of a protein?

## What it does NOT answer

It does not assert that any pathway transmits a signal; it reports the network built from the curated sites and its topology.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession or ASD id |
| `pdb_id` | `str` | no | `None` | optional PDB id, used to add BioLiP contact residues |
| `ppi_data_path` | `str` | no | `None` | optional directory of PPI parquet files |
| `min_interactions` | `int` | no | `2` | minimum edge weight to include |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, asd_id, allosteric_sites, network_nodes, network_edges, communication_pathways, network_metrics, data_sources, summary}`.

## Source and version

- upstream URL: ASD XF XML files plus, optionally, BioLiP and PPI parquet files; all mounted read-only at `/biolab_data`

## Runtime

- a second or two; offline

## Determinism

- deterministic for a given snapshot

## Failure modes

- a protein outside the ASD index -> `success=False`

## Known-answer test

- expectation: input `P0AB91` -> 1 allosteric site, 13 residue nodes, `total_edges == 0`, `density == 0.0`, `allosteric_node_count == 13`, `data_sources == ["ASD_XF"]`
- source of the expectation: ASD XF, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-10)

## Negative control

- expectation: input `P99999` -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric2.py::residue_interaction_networks`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

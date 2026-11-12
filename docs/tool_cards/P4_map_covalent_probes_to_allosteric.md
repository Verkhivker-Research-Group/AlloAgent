# P4 map_covalent_probes_to_allosteric

## Question the tool answers

Where do covalent probes attach to a target, and is each attachment site orthosteric-like or an allosteric candidate?

## What it does NOT answer

It does not predict an allosteric site. It reports observed covalent-probe attachment sites and labels them with residue-type rules; a site labelled `Allosteric_Candidate` is a candidate, not a call.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession, matched against the `Target` column |
| `dataset_path` | `str` | no | `"/biolab_data/data_lake/CovInDB_All.csv"` | path to CovInDB_All.csv; override with `ALLOAGENT_COVINDB` |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, total_entries, records, columns, war_head_counts, unique_inchi_keys}`. Each record carries the CovInDB columns plus `Parsed_Sites`, `Allosteric_Candidate`, `Site_Count` and `Confidence`.

## Source and version

- upstream URL: CovInDB (CovalentInDB) `CovInDB_All.csv`, mounted read-only from the Biolab data lake (17,774 rows in this snapshot)

## Runtime

- typical latency 1-3 s (reads and filters the 18 MB CSV); offline; no network

## Determinism

- deterministic for a given dataset snapshot

## Failure modes

- dataset file missing -> `success=False`, error names the missing path
- CSV unreadable -> `success=False`, error starts `could not read`
- no `Target` column -> `success=False`, error lists the columns found

## Known-answer test

- expectation: input `P00519` -> 23 entries, every `Target_Gene == "ABL1"`, every `Site == "NT"`, `war_head_counts == {"Michael Acceptor": 21, "Halohydrocarbon": 2}`, `unique_inchi_keys == 6`
- source of the expectation: CovInDB_All.csv, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-12)

## Negative control

- expectation: input `P04637` -> `success=True` with `total_entries == 0`

## Code location and version

- function: `biomni/tool/allosteric.py::map_covalent_probes_to_allosteric`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

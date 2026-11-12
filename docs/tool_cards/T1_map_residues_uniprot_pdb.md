# T1 map_residues_uniprot_pdb

## Question the tool answers

"Given a PDB ID, what UniProt accession does it map to, and which
chains + residue ranges are covered?" Also: "Given a UniProt
accession, which PDB structures are the best (highest-coverage,
highest-identity) structures for that protein?"

## What it does NOT answer

The tool maps between PDB and UniProt and surfaces coverage/identity.
It does NOT score the structure quality beyond what PDBe reports
(identity and coverage), does NOT annotate residues, does NOT
predict functional effects of variants, and does NOT classify
allosteric vs orthosteric sites. Use `get_uniprot_variants` (T2) for
variant data; use `get_stingallo_allosteric_residues` (T3) for
allosteric site data.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` (for `map_residues_uniprot_pdb`) | str | yes | — | A 4-character PDB ID (e.g. `"1AKE"` or `"1ake"`; case-insensitive) |
| `accession` (for `map_pdb_to_best_structures`) | str | yes | — | A UniProt accession (e.g. `"P69441"`; case-insensitive) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` for `map_residues_uniprot_pdb`:

```
{
    "pdb_id": <pdb_id uppercased>,
    "uniprot_accessions": [<accession>, ...],
    "mappings": {
        <accession>: {
            "name": <protein name>,
            "identifier": <PDBe identifier>,
            "mappings": [
                {entity_id, chain_id, struct_asym_id,
                 unp_start, unp_end,
                 start: {author_residue_number, residue_number},
                 end:   {author_residue_number, residue_number},
                 identity, coverage},
                ...
            ]
        },
        ...
    }
}
```

`data` for `map_pdb_to_best_structures`:

```
{
    "uniprot_accession": <accession uppercased>,
    "best_structures": [
        {pdb_id, entity_id, chain_id, unp_start, unp_end,
         coverage, best, ...},
        ...
    ]
}
```

## Source and version

- upstream URL: `https://www.ebi.ac.uk/pdbe/api/mappings/`
- pinned release tag: PDBe mappings API v1
- license: EMBL-EBI terms of use

## Runtime

- typical latency: ~0.5–2 s (PDBe mappings API is fast)
- rate limits: PDBe mappings API is currently rate-limited at ~10 req/s
  per IP; this tool does not implement per-IP backoff
- offline vs online: online (no offline fixture is provided; the test
  suite uses recorded JSON fixtures, not a live-call offline mode)

## Determinism

- deterministic? yes (for a given API response at a given instant)
- if partial: a same-second call returns the same response

## Failure modes

- unknown PDB ID: returns `{success: True, data: {pdb_id: ..., uniprot_accessions: [], mappings: {}}, ...}` (empty result, not an error).
- network timeout (default 30 s): raises `requests.Timeout`; the contract wrapper catches it and returns `{success: False, data: None, error: "Timeout: ...", ...}`.
- HTTP 4xx/5xx: raises `requests.HTTPError`; the contract wrapper catches it and returns `{success: False, data: None, error: "HTTPError: ...", ...}`.

## Known-answer test

- input: `map_residues_uniprot_pdb("1ake")` (or `"1AKE"`)
- expected: `data.pdb_id == "1AKE"`, `data.uniprot_accessions == ["P69441"]`, `data.mappings["P69441"]["name"] == "KAD_ECOLI"`, chain_ids sorted = `["A", "B"]`, `unp_start=1`, `unp_end=214`, `identity=1.0`, `coverage=1.0`.

The snapshot was recorded from the live API into
`tests/fixtures/map_residues_uniprot_1AKE.json`.

## Negative control

- input: `map_residues_uniprot_pdb("ZZZZ")` (or any unknown PDB)
- expected: `data.pdb_id == "ZZZZ"`, `data.uniprot_accessions == []`, `data.mappings == {}`. The function does NOT raise; it returns a well-formed empty contract dict.

## Code location and version

- function: `biomni/tool/map_residues_uniprot_pdb.py::map_residues_uniprot_pdb`
- function: `biomni/tool/map_residues_uniprot_pdb.py::map_pdb_to_best_structures`
- recorded in: the per-run JSON at the key `tools_meta[map_residues_uniprot_pdb].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

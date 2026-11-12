# T1 map_pdb_to_best_structures

## Question the tool answers

"Given a UniProt accession, return the list of best PDB structures
(with chain + coverage info) for that protein."

## What it does NOT answer

The tool reports the structures the PDBe mappings API lists for an
accession, with the chain and residue coverage PDBe itself reports.
It does NOT score the structure quality beyond what PDBe reports
(identity and coverage), does NOT annotate residues, does NOT
predict functional effects of variants, and does NOT classify
allosteric vs orthosteric sites. Use `get_uniprot_variants` (T2) for
variant data; use `get_stingallo_allosteric_residues` (T3) for
allosteric site data.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `accession` | str | yes | — | A UniProt accession (e.g. `"P69441"`; upper-cased before the request) |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

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

- upstream URL: `https://www.ebi.ac.uk/pdbe/api/mappings/` (the
  request path is `{base}/best_structures/{accession}`,
  `biomni/tool/map_residues_uniprot_pdb.py:112`)
- pinned release tag: PDBe mappings API v1
  (`docs/tool_cards/T1_map_residues_uniprot_pdb.md:72`)
- license: EMBL-EBI terms of use
  (`docs/tool_cards/T1_map_residues_uniprot_pdb.md:73`)
- the request timeout is 30 s (`_TIMEOUT_S`,
  `biomni/tool/map_residues_uniprot_pdb.py:36`)

## Runtime

- typical latency: ~0.5–2 s (PDBe mappings API is fast)
  (`docs/tool_cards/T1_map_residues_uniprot_pdb.md:77`)
- rate limits: PDBe mappings API is currently rate-limited at ~10 req/s
  per IP; this tool does not implement per-IP backoff
  (`docs/tool_cards/T1_map_residues_uniprot_pdb.md:78-79`)
- offline vs online: online (no offline fixture is provided for this
  function; the test suite uses recorded JSON fixtures,
  `docs/tool_cards/T1_map_residues_uniprot_pdb.md:80-81`)

## Determinism

- deterministic? yes (for a given API response at a given instant)
- if partial: a same-second call returns the same response
  (`docs/tool_cards/T1_map_residues_uniprot_pdb.md:85-86`)

## Failure modes

- unknown accession: the API returns no entry, so `data.best_structures`
  is `[]` and `success` stays `True`
  (`biomni/tool/map_residues_uniprot_pdb.py:116`).
- network timeout (30 s): raises `requests.Timeout`; the contract wrapper
  catches it and returns `{success: False, data: None, error: "Timeout: ...", ...}`.
- HTTP 4xx/5xx: raises `requests.HTTPError`; the contract wrapper catches
  it and returns `{success: False, data: None, error: "HTTPError: ...", ...}`
  (`biomni/tool/map_residues_uniprot_pdb.py:113-114`;
  `docs/tool_cards/T1_map_residues_uniprot_pdb.md:90-92`).

## Known-answer test

- input: `map_pdb_to_best_structures("P69441")`
- expected: `success=True` and a non-empty `data.best_structures` list.
  The criterion records the snapshot at the time of the recording as 55
  entries (`docs/2_T1_criteria.md:44`).

The response was recorded from the live API into
`tests/fixtures/map_pdb_to_best_structures_P69441.json`.

## Negative control

- input: an accession the API does not know
- expected: `success=True`, `data.best_structures == []` - the function
  does NOT raise; it returns a well-formed empty contract dict.

## Code location and version

- function: `biomni/tool/map_residues_uniprot_pdb.py::map_pdb_to_best_structures`
- recorded in: the per-run JSON at the key
  `tools_meta[map_residues_uniprot_pdb].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**PASS** - criteria `docs/2_T1_criteria.md` (T1-1 .. T1-9); the per-tool
verdict table in `../alloagent_private/docs/3_report.md:455` records T1 as
"**PASS** (6/6 tests)" with the known answer
"1AKE -> P69441, chains A & B, identity=1.0, coverage=1.0,
unp_start=1, unp_end=214", the negative control "unknown PDB returns
empty mappings", the determinism "two calls return equal data" and a
runtime of ~0.05 s.

The criteria file's own verdict is narrower: `docs/2_T1_criteria.md:44`
records T1-4 as **PASS** but with the note "returns a non-empty list
(55 entries at the time of fixture recording). The test asserts a
non-empty list rather than requiring 1AKE specifically (1AKE is NOT
in P69441's best_structures per the live API; this is noted in
`docs/2_T1_diagnostic.md`)", and `docs/2_T1_criteria.md:51` records
the overall verdict as **PARTIAL** - the brief's known answer
"1AKE ↔ P69441" works in one direction only.

The recorded diagnostic is at `docs/2_T1_diagnostic.md`; the criteria
file is `docs/2_T1_criteria.md` (T1-8 at line 34 requires the shared
module card `docs/tool_cards/T1_map_residues_uniprot_pdb.md`, which
names this function at lines 25, 56 and 110; T1-9 at line 35 requires
the fixture `tests/fixtures/map_pdb_to_best_structures_P69441.json`).

This card has no test of its own: no test file names
`map_pdb_to_best_structures` as a card path.

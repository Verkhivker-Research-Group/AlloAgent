# T8 search_pdb_by_uniprot_and_ligand

## Question the tool answers

"Which PDB entries have a polymer entity with the given UniProt
accession AND a chemical component with the given ligand ID?"

## What it does NOT answer

- It does not return the 3D coordinates, only the entry IDs. Use
  T1 `map_residues_uniprot_pdb` to get the residue mapping for a
  given PDB entry, and the RCSB Data API or `mmCIF` download to get
  the structure.
- It does not distinguish co-crystallized ligands from covalent
  modifications, buffer components, or crystallization additives.
  The `comp_id` match is a string match on the chemical component
  ID, not a binding-site analysis.
- It does not filter by resolution, R-factor, experimental method,
  or release date. Use the RCSB Search API directly for those
  filters.
- It does not guarantee that the UniProt-mapped polymer entity and
  the ligand are in physical contact. The search is at the
  entry level, not the binding-site level.

## Cross-check (A2)

The RCSB Search API route was cross-checked against an
independent PDBe route on 2026-10-10, and against the RCSB
Data API + UniProt REST API on 2026-10-11:

1. RCSB Data API core endpoint
   (`https://data.rcsb.org/rest/v1/core/entry/<pdb>`): 1IEP
   and 1FPU are **MOUSE ABL1** (organism = *Mus musculus*,
   gene = *Abl1*, UniProt = **P00520**) — the mouse ortholog
   of human ABL1 (P00519). They do NOT contain UniProt
   P00519 (human ABL1). The T8 tool was queried for P00519
   (human) and correctly excluded them. **Correction**: the
   earlier claim that "1IEP is ABL2/P00520" was wrong — P00520
   is the mouse ortholog of P00519 (both are ABL1, not
   ABL2). Neither 1IEP nor 1FPU contains the ligand STI
   in the queried form (STI = imatinib).
2. PDBe compound/in_pdb/STI returns 29 entries. After
   filtering by P00519 via
   `https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<pdb>`
   (checking `data[pdb_id]["UniProt"]["P00519"]`), 6 entries
   remain: `2hyy, 3pyy, 6npe, 6npu, 6npv, 7n9g`.
3. The T8 tool (RCSB Search API combined query) returns the
   same 6 entries: `2HYY, 3PYY, 6NPE, 6NPU, 6NPV, 7N9G`.

Both routes agree exactly. The T8 tool is correct for this
query. The "may not be exhaustive" caveat below still applies
to queries where the two routes have not been cross-checked.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | — | UniProt accession (e.g. `P69905`, `P69441`). |
| `ligand_id` | `str` | yes | — | RCSB chemical component ID (e.g. `HEM`, `ATP`, `ZN`). |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is:

```python
{
    "uniprot_id": "P69905",
    "ligand_id": "HEM",
    "entry_ids": ["1A00", "1A01", "1A0U", "1A0Z", "1A3N", ...],  # score order
    "total_count": 350,  # total matches on the RCSB index
    "query_url": "https://search.rcsb.org/rcsbsearch/v2/query",  # for reproducibility
}
```

## Source and version

- upstream URL: `https://search.rcsb.org/rcsbsearch/v2/query`
- API docs: `https://search.rcsb.org/redoc/index.html`
- API version: RCSB Search API v2 (current as of 2026-10-10)
- license: RCSB PDB data is in the public domain

## Runtime

- typical latency: ~0.5-1.0 s per query (HTTPS POST to RCSB)
- rate limits: RCSB Search API does not publish a hard rate limit
  for the v2 endpoint; the wrapper does not implement client-side
  throttling
- offline vs online: online (requires outbound HTTPS to
  `search.rcsb.org`)

## Determinism

- deterministic? yes (RCSB Search API v2 returns results sorted by
  score; the score is a function of the query, not the call time)
- if partial: none for a fixed (uniprot, ligand) pair; the result
  set may grow over time as new entries are released, but the
  relative order of existing entries is stable

## Failure modes

- Network unreachable: `{"success": false, "error": "requests.exceptions.ConnectionError: ..."}`
- RCSB returns non-200: `{"success": false, "error": "RCSB Search API returned status 500: ..."}`
- RCSB returns 200 with malformed body: `{"success": false, "error": "RCSB Search API returned invalid JSON: ..."}`
- Unknown UniProt: `{"success": true, "data": {"entry_ids": [], "total_count": 0, ...}}`
- Unknown ligand: `{"success": true, "data": {"entry_ids": [], "total_count": 0, ...}}`

## Known-answer test

- input: `("P69905", "HEM")`
- expected: `data.total_count >= 10`, `data.entry_ids[0:5]` is
  `["1A00", "1A01", "1A0U", "1A0Z", "1A3N"]` (in score order on
  the live API as of 2026-10-10)

- input: `("P69441", "ATP")`
- expected: `data.total_count >= 1`, `8RJ6` is in `data.entry_ids`

## Negative control

- input: `("ZZZZZZ", "ATP")` (unknown UniProt)
- expected: `{"success": true, "data": {"entry_ids": [], "total_count": 0, ...}}`

- input: `("P69441", "ZZZ")` (unknown ligand)
- expected: `{"success": true, "data": {"entry_ids": [], "total_count": 0, ...}}`

## Code location and version

- function: `biomni/tool/search_pdb_by_uniprot_and_ligand.py::search_pdb_by_uniprot_and_ligand`
- recorded in: the per-run JSON at the key `image_id`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

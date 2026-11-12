# T3 get_stingallo_allosteric_residues

## Question the tool answers

"Given a PDB ID, what allosteric residues are annotated on the
structure, and on which chain?"

## What it does NOT answer

The tool returns STINGAllo's residue list for a structure. It does
NOT:
- score or rank the allosteric effect strength,
- report thermodynamic or kinetic data,
- identify cryptic or distal allosteric sites beyond what STINGAllo
  annotates,
- classify the regulatory type (agonist vs antagonist vs
  allosteric modulator) beyond STINGAllo's own label.

For a pocket-detection view (not the same as allosteric-site
annotation), use `detect_pockets_fpocket` (T4) or
`detect_pockets_p2rank` (T5).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | str | yes | — | A 4-character PDB ID (e.g. `"1AKE"` or `"1ake"`; case-insensitive) |
| `chain_id` | str or None | no | None | One-letter chain ID (e.g. `"A"`); if None, STINGAllo returns all chains |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "pdb_id": <pdb_id uppercased>,
    "chain_id": <chain_id uppercased or None>,
    "residues": [
        {
            "residue_number": <int>,
            "chain_id": <str>,
            "ligand": <str>,
            "allosteric_type": <str>,
            "evidence": <str>
        },
        ...
    ]
}
```

## Source and version

- upstream URL: `https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=<pdb>&chain_id=<chain>`
- release: STINGAllo (SITE-DIRECTED ALlosteric Residues in PDB)
- license: STINGAllo (Embrapa / CNPSo)

## Runtime

- typical latency: ~1-3 s
- rate limits: 100 requests/IP/day, 30 unique PDBs/IP/day (enforced by
  a persistent file-based counter at
  `~/.cache/alloagent/stingallo_counter.json`)
- offline vs online: online; tests use the rate-limit counter
  monkey-patched to verify the rate-limit logic without hitting the
  real API

## Determinism

- deterministic? yes (for a given API response at a given instant)

## Failure modes

- unknown PDB: returns `{success: True, data: {pdb_id: ..., residues: []}, ...}`.
- rate limit reached: returns `{success: False, data: None, error: "STINGAllo daily request limit reached (X/100)" or "... unique-PDB limit reached (X/30)"}`.
- blocklist match: returns the blocked-dict from `@benchmark_blocklist`.
- network timeout (30 s default): caught by the contract wrapper.

## Known-answer test

- input: `get_stingallo_allosteric_residues("1AKE")`
- expected: a non-empty `data.residues` list from the recorded
  STINGAllo fixture (the test asserts the shape; the specific
  residue list is whatever STINGAllo returns at recording time).

## Negative control

- input: `get_stingallo_allosteric_residues("ZZZZ")`
- expected: `{success: True, data: {pdb_id: "ZZZZ", residues: []}, ...}`.

## Rate-limit tests

- When the counter has `requests >= 100`, the function returns
  `success=False` without making the network call.
- When the counter has 30 unique PDBs and the requested pdb is NOT
  one of them, the function returns `success=False` without making
  the network call.

## Code location and version

- function: `biomni/tool/get_stingallo_allosteric_residues.py::get_stingallo_allosteric_residues`
- recorded in: per-run JSON at `tools_meta[get_stingallo_allosteric_residues].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

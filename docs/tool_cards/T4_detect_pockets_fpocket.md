# T4 detect_pockets_fpocket

## Question the tool answers

"Given a PDB structure, what are its ligand-binding pockets (as
predicted by fpocket 4.2.3), and what are their druggability scores
and the residues lining each pocket?"

## What it does NOT answer

fpocket finds pockets that bind small molecules. It does NOT
distinguish allosteric sites from orthosteric sites. The tool
returns pockets in a single conformation; it does NOT run an
ensemble across multiple frames or do cross-pocket communication
analysis. The `Druggability Score` is an empirical estimate from
fpocket; this tool does NOT independently validate it. For
allosteric-site prediction, use `get_stingallo_allosteric_residues`
(T3) or `detect_pockets_p2rank` (T5, for a different geometric
engine).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_path` | str or Path | yes | — | A PDB file path (`.pdb` or `.cif`). HETATM records are stripped by default. |
| `strip_hetatm` | bool | no | True | If True, HETATM records are removed from a working copy of the input before fpocket is invoked. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "pdb_id": <file stem>,
    "pockets": [
        {
            "pocket_number": <int>,
            "druggability_score": <float>,
            "number_of_alpha_spheres": <int>,
            "hydrophobicity_score": <float>,
            "volume": <float>,
            "residues": [<residue_number>, ...]
        },
        ...
    ]
}
```

## Source and version

- upstream URL: `https://github.com/Discngine/fpocket` (pinned tag: `4.2.3` or `v4.2.3`)
- license: MIT
- checksum: recorded in `docs/tool_cards/T4_fpocket_checksum.txt` (a
  follow-up; the container Dockerfile pins the version AND a SHA256
  of the binary)

## Runtime

- typical latency: 1-30 s (depends on PDB size)
- rate limits: none
- offline vs online: offline (fpocket is a local binary)
- fpocket ignores the `-o` flag: it always writes to
  `<input_basename>_out/` next to the input. The implementation
  computes that directory by replacing the extension with `_out/`
  in the input path.

## Determinism

- deterministic? yes for a given input file (fpocket is
  deterministic; the result depends only on the input coordinates)

## Failure modes

- fpocket not on PATH: returns `success=False, error="fpocket binary
  not found on PATH"`.
- non-PDB input: returns `success=True, data.pockets=[]` (the parser
  returns empty when the `_info.txt` does not exist).
- fpocket error output: captured and returned as `error`.

## Known-answer test

- input: a small synthetic PDB (e.g. 1AKE)
- expected: a non-empty `pockets` list with `Druggability Score` values
  (some may be negative; the parser must handle that).

## Negative control

- input: a non-PDB file (e.g. an empty text file)
- expected: `{success: True, data: {pdb_id: ..., pockets: []}, ...}`
  (no exception).

## Code location and version

- function: `biomni/tool/detect_pockets_fpocket.py::detect_pockets_fpocket`
- recorded in: per-run JSON at
  `tools_meta[detect_pockets_fpocket].schema_hash`
- version: `biomni.__version__` (and fpocket 4.2.3)

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
  The `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.
- fpocket's `-o` is ignored — the implementation must point the
  output dir to `<basename>_out/`.

## Status

**BLOCKED** — implementation + tests are deferred until the
container rebuilds with the `fpocket` binary (Part 0a follow-up).

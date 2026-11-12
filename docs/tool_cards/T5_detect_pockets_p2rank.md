# T5 detect_pockets_p2rank

## Question the tool answers

"Given a PDB structure, what are its predicted binding pockets per
P2Rank 2.5.1, and which residues line each pocket?"

## What it does NOT answer

P2Rank predicts pockets from a single conformation. It does NOT
distinguish allosteric from orthosteric sites, run an ensemble, or
score pocket druggability beyond the per-residue probability.
Use `get_stingallo_allosteric_residues` (T3) or
`detect_pockets_fpocket` (T4) for those.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_path` | str or Path | yes | — | A PDB or mmCIF file path. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "pdb_id": <file stem>,
    "pockets": [
        {
            "rank": <int>,
            "score": <float>,
            "residues": [
                {"residue_number": <int>, "chain": <str>},
                ...
            ]
        },
        ...
    ]
}
```

## Source and version

- upstream URL: `https://github.com/rdk/p2rank` (pinned tag: `2.5.1`)
- license: GPL-3.0
- Java: 17 (the function asserts Java is on PATH or uses JAVA_HOME)

## Runtime

- typical latency: 5-60 s (depends on PDB size)
- rate limits: none
- offline vs online: offline (Java + JAR local)

## Determinism

- deterministic? yes for a given input (P2Rank 2.5.1 is deterministic)

## Failure modes

- Java / JAR missing: returns `success=False, error="..."`.
- non-PDB input: returns `success=True, data.pockets=[]`.

## Known-answer test

- input: a small synthetic PDB (e.g. 1AKE)
- expected: a non-empty `pockets` list with per-residue scores

## Negative control

- input: a non-PDB file
- expected: `{success: True, data: {pdb_id: ..., pockets: []}, ...}`

## Code location and version

- function: `biomni/tool/detect_pockets_p2rank.py::detect_pockets_p2rank`
- recorded in: per-run JSON at
  `tools_meta[detect_pockets_p2rank].schema_hash`
- version: `biomni.__version__` and P2Rank 2.5.1

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**BLOCKED** — implementation + tests are deferred until the
container rebuilds with Java 17 + P2Rank 2.5.1.

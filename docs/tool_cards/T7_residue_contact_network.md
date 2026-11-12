# T7 residue_contact_network

## Question the tool answers

"Given a PDB structure, what is the contact graph between residues
(heavy atoms within 4.5 Å), what are the betweenness-centrality
scores, what are the residue communities, and what is the shortest
path between two residues?"

## What it does NOT answer

The tool returns the static contact graph (single conformation).
It does NOT model dynamic contacts, do allosteric pathway
inference, or run molecular dynamics. For allosteric-site
annotation use `get_stingallo_allosteric_residues` (T3).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `mmcif_path` | str or Path | yes | — | An mmCIF file path. |
| `source_residue` | str or None | no | None | First residue in a "from-to" query (e.g. `"A.42"`). |
| `target_residue` | str or None | no | None | Second residue in a "from-to" query. |
| `seed` | int | no | 42 | Random seed for community detection (deterministic). |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "n_residues": <int>,
    "n_edges": <int>,
    "betweenness": {<residue_id>: <score>, ...},
    "communities": [<set of residue_ids>, ...],
    "shortest_path": [<residue_id>, ...] (if source/target given),
    "seed": <int>
}
```

## Source and version

- upstream: Biotite 1.6.0 (mmCIF parser) + NetworkX 3.6.1
- license: BSD-3-Clause (both)

## Runtime

- typical latency: <1 s for small structures
- rate limits: none
- offline vs online: offline

## Determinism

- deterministic? yes (fixed seed for community detection; all other
  steps are deterministic on the same input)

## Failure modes

- empty / non-CIF input: returns `{success: True, data: {n_residues: 0, n_edges: 0, ...}, ...}`.
- source / target residue not in the structure: `shortest_path` is `[]`.

## Known-answer test

- input: a 5-node path graph (NetworkX `path_graph(5)`)
- expected: betweenness = `{0: 0, 1: 3, 2: 4, 3: 3, 4: 0}` (canonical order).
- input: the barbell graph (two 3-cliques connected by a bridge)
- expected: two communities, one per clique.

## Negative control

- input: empty / non-CIF
- expected: empty result dict, no exception.

## Code location and version

- function: `biomni/tool/residue_contact_network.py::residue_contact_network`
- recorded in: per-run JSON at
  `tools_meta[residue_contact_network].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**BLOCKED** — implementation + tests are deferred until the
container rebuilds with Biotite 1.6.0.

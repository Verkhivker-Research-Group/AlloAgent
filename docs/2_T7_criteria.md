# T7 — residue_contact_network: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: Biotite 1.6.0 (mmCIF parser, heavy-atom selector) +
  NetworkX 3.6.1 (betweenness centrality, community detection,
  shortest path).
- Definition: two heavy atoms are in contact when their distance is
  ≤ 4.5 Å.
- Known answers:
  - NetworkX path betweenness on a 5-node path graph (unnormalized)
    is `{0, 3, 4, 3, 0}` (canonical order).
  - Barbell graph (two 3-cliques + a bridge) splits into exactly two
    communities with a fixed seed. The bridge node may join
    either clique; the two non-bridge cliques are recovered as
    separate communities.
  - Two calls with the same input return identical output
    (deterministic).
- Status: BLOCKED (biotite 1.6.0 not installed on the host; the 0a
  Dockerfile follow-up adds it). Implementation and tests deferred.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T7-1 | `biomni/tool/residue_contact_network.py` exists with the entry point | `git ls-files` returns the path. |
| T7-2 | The contact graph is built from mmCIF heavy atoms within 4.5 Å | The test asserts this with a synthetic mmCIF. |
| T7-3 | The function returns the betweenness centrality vector, the community partition, and (when `source_residue`/`target_residue` are given) the shortest path between two residues | The test asserts the full output. |
| T7-4 | Known-answer: NetworkX path betweenness on a 5-node path graph is `{0, 3, 4, 3, 0}` (NetworkX `betweenness_centrality(path_graph(5))`) | The test asserts this. |
| T7-5 | Known-answer: the barbell graph (two 3-cliques connected by a bridge) splits into exactly two communities with a fixed seed; the two 3-cliques are recovered as separate communities | The test asserts this with a barbell fixture and seed=42. |
| T7-6 | Determinism: two calls with the same input return identical output | The test calls the function twice and asserts equality. |
| T7-7 | Negative control: an empty / non-CIF input returns `success=True, data.n_residues=0` | The test asserts this. |
| T7-8 | Lowercase input robustness: a lowercase mmCIF path is parsed without error | The test passes a lowercase file path. |
| T7-9 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| T7-10 | Tool card exists at `docs/tool_cards/T7_residue_contact_network.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T7-1 | (filled) | (filled) |
| T7-2 | (filled) | (filled) |
| T7-3 | (filled) | (filled) |
| T7-4 | (filled) | (filled) |
| T7-5 | (filled) | (filled) |
| T7-6 | (filled) | (filled) |
| T7-7 | (filled) | (filled) |
| T7-8 | (filled) | (filled) |
| T7-9 | (filled) | (filled) |
| T7-10 | (filled) | (filled) |

## Status

Implementation + tests deferred until the container has Biotite 1.6.0
(now installed: image `0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`,
biotite 1.6.0). Implementation follows in the next commit.

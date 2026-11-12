# T6 normal_mode_analysis

## Question the tool answers

"Given a PDB structure, what are its dominant low-frequency normal
modes (ANM or GNM), and what residues move together?"

## What it does NOT answer

The tool returns a normal-mode decomposition of a single
conformation. It does NOT predict functional effect, allosteric
pathways, or conformational change. Use this for flexibility analysis
(or for GNM path-based community detection — T7 uses NetworkX on
top of this output).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | str or Path | yes | — | A PDB or mmCIF file path. |
| `model` | str | no | `"anm"` | `"anm"` (Anisotropic Network Model) or `"gnm"` (Gaussian Network Model). |
| `max_modes` | int | no | `0` | Maximum number of non-trivial modes to return. `0` means the full ProDy spectrum (the default). Pass e.g. `5` to cap the returned list. |
| `timeout_s` | int | no | `60` | Soft wall-clock timeout (seconds). Returns `success=False` with a timeout error if exceeded. ProDy 2.6.1 has no native interrupt; the check is sampled between phases. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "pdb_id": <file stem>,
    "model": "anm" or "gnm",
    "n_modes": <int>,
    "n_modes_raw": <int>,
    "n_trivial_filtered": <int>,
    "eigenvalues": [<float>, ...],
    "eigenvectors": [[<float>, ...], ...]
}
```

`n_modes_raw` is the number of modes ProDy computed (the full N-mode
spectrum). `n_trivial_filtered` is the number of trivial modes
discarded (always 6 for ANM on a CA subset; 0-1 for GNM).
`n_modes` is the post-filter count.

## Source and version

ProDy 2.6.1 (`https://github.com/prody/proDy`, MIT license). The
wrapper calls `prody.calcModes(n_modes=N, zeros=True)` so the
trivial near-zero modes are returned by ProDy, then filters them
via `abs(ev) > 1e-8` and returns only the non-trivial modes.

## Spectrum on 1AKE (CA subset, N = 428 atoms)

ProDy 2.6.1 ANM builds an N x N (not 3N x 3N) Hessian from the
heavy-atom subset. The resulting spectrum has N modes total:

  - 6 trivial modes (`abs(ev) < 1e-8`) — 3 body-frame translations +
    3 rotations. These are filtered out.
  - 422 non-trivial modes — the `n_modes` field in `data`.

This is the full spectrum, not a cap. `n_modes_raw = 428` confirms
it.

## Runtime

Typical latency for 1AKE CA-only subset (N = 428 atoms):

  - ANM build + calcModes: 4-6 s
  - GNM build + calcModes: 0.5-1 s

The full T6 test file (13 tests) runs in ~44 s on this host.

## Determinism

Deterministic for a given input (no RNG).

## Failure modes

  - empty / non-PDB input: returns `{success: True, data: {n_modes: 0, ...}, ...}`
  - invalid `model` argument: returns `success=False, error="model must be one of ('anm', 'gnm')"`
  - timeout exceeded: returns `success=False, error="normal_mode_analysis timed out after {timeout_s}s"`

## Known-answer test

  - GNM on a synthetic path chain of N nodes: eigenvalues
    `2 - 2*cos(k*pi/N)` for k=1..N-1 within `atol=1e-6`.
  - ANM on 1AKE: `n_modes_raw = 428`, `n_trivial_filtered = 6`,
    `n_modes = 422`. The 6 trivial modes are filtered out.

## Negative control

  - empty / non-PDB: empty modes list, no exception.

## Code location and version

  - function: `biomni/tool/normal_mode_analysis.py::normal_mode_analysis`
  - recorded in: per-run JSON at
    `tools_meta[normal_mode_analysis].schema_hash`
  - version: `biomni.__version__` and ProDy 2.6.1

---

## Cross-cutting rules

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

Implementation + tests are now in
`biomni/tool/normal_mode_analysis.py` and
`tests/test_T6_normal_mode_analysis.py`. The image
`0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`
has ProDy 2.6.1 and the tool runs end-to-end. Verified on the
recorded 1AKE fixture.

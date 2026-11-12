# T6 — normal_mode_analysis: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before any
implementation or test is written.

## Tool summary

- Engine: ProDy 2.6.1 (ANM and GNM normal mode analysis).
- Interface: `calcModes(..., zeros=True)` so the 6 near-zero modes
  are kept; the function returns only the NONZERO modes.
- Known answers: GNM on a synthetic path chain (1-2-...-N) has
  eigenvalues `2 - 2*cos(k*pi/N)` for k=1..N-1; ANM on 1AKE has
  exactly 6 near-zero modes.
- Status: BLOCKED (prody 2.6.1 not installed on the host; the 0a
  Dockerfile follow-up adds it). Implementation and tests deferred.

## Criteria

| # | Criterion | Verification |
|---|---|---|
| T6-1 | `biomni/tool/normal_mode_analysis.py` exists with the GNM and ANM entry points | `git ls-files` returns the path. |
| T6-2 | The function calls `calcModes(..., zeros=True)` internally and returns the nonzero modes (filtered by `abs(ev) > ZERO_TOL`) | The test asserts that on a 1AKE ANM run, the 6 trivial near-zero modes are filtered out and the remaining modes are all nonzero. |
| T6-3 | GNM on a synthetic path chain of N nodes produces eigenvalues `2 - 2*cos(k*pi/N)` for k=1..N-1 within 1e-6 of the formula (after sorting) | The test constructs an N=8 path chain, runs GNM, and compares `sorted(eigvals)` to `sorted([2 - 2*cos(k*pi/8) for k in 1..7])` within `atol=1e-6`. |
| T6-4 | ANM on 1AKE has exactly 6 near-zero modes when `zeros=True` | The test asserts that 6 eigenvalues have `abs(ev) <= ZERO_TOL` (the trivial modes). |
| T6-5 | Determinism: two calls with the same input return identical data | The test calls the function twice on 1AKE and asserts the returned `data` dicts are equal. |
| T6-6 | Negative control: invalid model argument returns `success=False, error` | The test passes `model="garbage"` and asserts the downgraded-success rule. |
| T6-7 | Lowercase input robustness: a PDB file path is treated as-is (the tool reads the file path, no normalization required) | The test passes the 1AKE PDB path as a lowercase string and asserts the tool processes it without error. |
| T6-8 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` per the Part-1c decorator | The test asserts all 6 keys are present. |
| T6-9 | Tool card exists at `docs/tool_cards/T6_normal_mode_analysis.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test (`tests/test_tool_cards.py::test_f3`) asserts no `self-reported` substring. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| T6-1 | **PASS** | `biomni/tool/normal_mode_analysis.py` exists, tracked by git. |
| T6-2 | **PASS** | Function calls `calcModes(n_modes=N, zeros=True)` internally and filters trivial modes by `abs(ev) > 1e-8`. ANM 1AKE: `n_modes_raw=428`, `n_trivial_filtered=6`, `n_modes=422`. |
| T6-3 | **PASS** | GNM on a synthetic 8-node path chain with 7 A spacing (next-nearest neighbours fall outside the default 10 A cutoff) gives eigenvalues exactly `2 - 2cos(k*pi/8)` for k=0..7 within `atol=1e-6`. |
| T6-4 | **PASS** | ANM on 1AKE has exactly 6 trivial modes (abs(ev) <= 1e-8); the wrapped function strips them. |
| T6-5 | **PASS** | Two calls with the same input return equal data. |
| T6-6 | **PASS** | Invalid `model="garbage"` returns `success=False`. |
| T6-7 | **PASS** | Lowercase PDB path is accepted. |
| T6-8 | **PASS** | All 5 contract keys present. |
| T6-9 | **PASS** | Tool card exists at `docs/tool_cards/T6_normal_mode_analysis.md`; no `self-reported` substring. |

## Spectrum on 1AKE (CA subset, N=428)

The wrapper reports the full N-mode ProDy spectrum (not a cap):

  - `n_modes_raw = 428`: all modes ProDy computes (CA-only ANM has
    N modes total because the Hessian is N x N, not 3N x 3N).
  - `n_trivial_filtered = 6`: the 3 body-frame translations + 3
    rotations are filtered by `abs(ev) > 1e-8`.
  - `n_modes = 422`: the post-filter count.

ProDy 2.6.1 does not implement a native interrupt. A soft
wall-clock timeout is sampled between phases (`parsePDB` ->
`buildHessian` / `buildKirchhoff` -> `calcModes` -> `getEigvals` /
`getArray`). The default `timeout_s = 60` is large enough that a
healthy 1AKE run (~5 s) does not trip it; passing `timeout_s=0`
returns `success=False` immediately after `parsePDB` if the elapsed
time exceeds the budget.

## Status

Implementation + tests are now in
`biomni/tool/normal_mode_analysis.py` and
`tests/test_T6_normal_mode_analysis.py`. The image
`0418fe07e168a79b9f3c6151bcd0414fb10c4d7cf0354d08a8af10dbf6173ce6`
has ProDy 2.6.1 and the tool runs end-to-end. Verified on the
recorded 1AKE fixture (428 raw / 6 trivial / 422 non-trivial
modes; ~5 s wall-clock per call).

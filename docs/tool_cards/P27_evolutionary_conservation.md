# P27 evolutionary_conservation

## Question the tool answers

What conservation surrogate score does each candidate residue get?

## What it does NOT answer

**It does not measure sequence conservation.** It builds no alignment and consults no ortholog database; it evaluates a deterministic pseudo-MSA entropy model. Treat the score as a reproducible stand-in, never as evidence of conservation.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | `-` | UniProt accession, used to fetch the sequence and seed the surrogate |
| `candidate_residues` | `list` | yes | `-` | list of `(chain_id, residue_number)` pairs; the residue number drives the surrogate |
| `query_pdb` | `callable` | no | `None` | unused by the surrogate; accepted for signature symmetry |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is `{uniprot_id, score, avg_conservation, summary}`.

## Source and version

- upstream URL: UniProt FASTA (`https://www.uniprot.org/uniprot/<acc>.fasta`) plus the deterministic entropy surrogate

## Runtime

- a few hundred milliseconds; online

## Determinism

- deterministic: the old implementation seeded numpy with Python's salted `hash()`, so the same input gave a different score in every process; the port uses a stable sha256-derived seed

## Failure modes

- UniProt returns a non-200 -> `success=False`, error states the status
- the FASTA cannot be parsed -> `success=False`

## Known-answer test

- expectation: input `P00688` with A/10 and A/50 -> `avg_conservation == 0.02`, `score == 0.034`, and the same values on every call and in every process
- source of the expectation: UniProt P00688, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-20)

## Negative control

- expectation: an accession UniProt does not know -> `success=False`

## Code location and version

- function: `biomni/tool/allosteric_verification_tools.py::evolutionary_conservation`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`

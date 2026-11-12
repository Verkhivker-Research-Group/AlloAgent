# B2 - BioEmu: pass criteria (written BEFORE running)

Committed before any sampling is run. The numbers are fixed here.

## What the tool is

`sample_conformations_bioemu(sequence=None, uniprot_id=None, n_samples=...)`
runs **BioEmu** in its own conda env (`/opt/conda/envs/bioemu_env`, torch
>= 2.5 with the CUDA wheels) and returns the sampled conformations.

The weights are downloaded to the **data root** (not into the image);
the size and the download time are recorded in the run report.

## Criterion 1 - the ensemble covers both ends of the adenylate kinase fold

* System: *E. coli* adenylate kinase, UniProt **P69441**, the full
  sequence (214 residues).
* References: the **closed** form is the deposited structure **1AKE**
  and the **open** form is the deposited structure **4AKE** (both from
  RCSB).  The C-alpha coordinates of each reference are taken from the
  deposited mmCIF and superimposed on the sample ensemble.
* **Criterion: at least 2 % of the sampled conformers are within
  3.0 A C-alpha RMSD of the CLOSED reference (1AKE) and at least 2 %
  are within 3.0 A C-alpha RMSD of the OPEN reference (4AKE).**
  The fraction is computed over the samples that could be superimposed
  (a sample that cannot be superimposed counts as a failure for that
  reference, not as an exclusion).
* `n_samples` is fixed at **20** for the criterion run.

## Criterion 2 - the tool fails cleanly without a GPU

* On a host without a usable GPU the tool returns `success=False` with
  a message that names the reason (no CUDA device / out of memory / the
  env is not installed) and **does not raise**.
* The tool is registered whether or not a GPU is present.

## What is recorded

The GPU model, the VRAM, the driver and the CUDA version; the peak GPU
memory during the run; the wall time; and the two fractions above.  If
the run cannot be done at all (no GPU, the env is not installed, the
weights cannot be downloaded), that is recorded as a **FAIL** with the
exact error, and the criterion is not changed.

> **Dated note 2026-10-26 - the measurement was validated, and the
> criterion FAILS on the corrected measurement.** The criterion text
> above is unchanged.
>
> The validation the criterion needed exposed a bug in the *measurement*,
> not in the samples. The superposition code compared
> `mobile_c @ R + target_c` against `target_c`, so the "RMSD" it
> reported was the mobile coordinates' own spread - a rotation-invariant
> number (about 17 A for a 214-residue protein), not the RMSD of the
> fit. Every RMSD in the previous phase's report was wrong. The
> corrected code fits `mobile_c @ R` and compares it with `target_c`.
>
> The sanity numbers with the corrected measurement:
>
> | check | value |
> |---|---|
> | a known rigid motion (200 random points, a rotation and a shift) | **0.000000 A** |
> | **the C-alpha RMSD between 4AKE and 1AKE after superposition on the 214 matched residues** | **7.13 A** (the criterion expects about 7 A) |
> | the BioEmu samples as stored | adjacent C-alpha 0.38, radius of gyration 1.72 |
> | the samples x 10 | adjacent C-alpha 3.83 A, radius of gyration 17.21 A |
> | 1AKE | adjacent C-alpha 3.82 A, radius of gyration 16.37 A |
> | the residue matching | 214 of 214 for both references, against the 214-residue P69441 sequence |
>
> So the samples are in **nanometres** (x10 gives a protein) and the
> measurement is sound. The committed criterion, re-evaluated with it:
>
> | reference | C-alpha RMSD per sample | within 3.0 A |
> |---|---|---|
> | 1AKE (closed) | min 1.31, median 2.51, max 8.33 A | **13 of 20 = 65.0 %** (needs >= 2 %) |
> | 4AKE (open) | min 4.45, median 6.27, max 7.12 A | **0 of 20 = 0.0 %** (needs >= 2 %) |
>
> **RESULT: FAIL.** The ensemble covers the closed form comfortably and
> does not reach the open form at all - the closest of the 20 samples
> is 4.45 A from 4AKE. The criterion needs both fractions, so it is a
> FAIL, and the criterion is not changed. The previous phase's "0 % and
> 0 %" was the broken measurement, not a property of the samples.

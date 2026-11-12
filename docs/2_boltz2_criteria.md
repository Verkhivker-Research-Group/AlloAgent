# B1 - Boltz-2: pass criteria (written BEFORE running)

Committed before any prediction is run. The criterion numbers are fixed
here; a run that does not meet them is a FAIL and is recorded as such.

## What the tool is

`predict_complex_boltz2(sequences=None, uniprot_ids=None, ligand_smiles=None,
ligand_name=None, ...)` runs **Boltz-2** in its own conda env
(`/opt/conda/envs/boltz2_env`, torch >= 2.5 with the CUDA wheels) and
returns the predicted structure path, the confidence scores and the
affinity outputs when the model provides them.

The tool's description states, and the tool repeats in its own output:
the confidence and affinity values are **model outputs, not
measurements**, and no published accuracy number is quoted.

The weights are downloaded to the **data root** (not into the image);
the size and the download time are recorded in the run report.

## Criterion 1 - the wrapper reproduces a known pose (ABL1 kinase domain + imatinib)

* Input: the ABL1 kinase domain sequence (UniProt P00519, residues
  215-498, the construct of 2HYY) and the ligand SMILES of imatinib
  (the STI component of 2HYY: `Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1`).
* The prediction is superimposed on the deposited 2HYY structure
  (protein chains) and the **ligand heavy-atom RMSD** is computed.
* **Criterion: the ligand heavy-atom RMSD to the deposited 2HYY ligand
  is <= 2.0 A.**
* **This checks the wrapper, not generalisation**: 2HYY is from 1999 and
  is very likely inside the Boltz-2 training set, so a good RMSD here
  says nothing about the model's accuracy on unseen complexes. That
  caveat is part of the criterion and must be reported with the result.

## Criterion 2 - a complex released AFTER the model's training cutoff

* The complex is **11OY**: "Crystal structure of Human p38 alpha MAPK in
  Complex with MW01-18-122SRM", X-ray, 2.022 A, **deposited 2026-03-06,
  released 2026-04-08** (RCSB entry API). The ligand is the component
  **GG5** in **chain A** (read from the deposited mmCIF: the HETATM
  records of GG5); the protein is human p38 alpha, UniProt **Q16539**.
* The training cutoff of the model is recorded from its model card
  (the primary source) in the run report; 11OY is released **after**
  that cutoff, so the pose it is checked against was not in the
  training set.
* **Criterion: the ligand heavy-atom RMSD to the deposited 11OY ligand
  (after the protein superposition) is <= 2.0 A.**
* **The result is reported whatever it is.** A RMSD above 2.0 A is a
  FAIL of this criterion and is recorded with the number; the criterion
  is not changed afterwards.

## Criterion 3 - the tool fails cleanly without a GPU

* On a host without a usable GPU the tool returns
  `success=False` with a message that names the reason (no CUDA device
  / out of memory / the env is not installed) and **does not raise**.
* The tool is registered whether or not a GPU is present.

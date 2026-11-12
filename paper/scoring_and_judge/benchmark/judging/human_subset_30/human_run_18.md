# Human rating sheet: run ryawlb6lbjx (18 of 30)

## Before you start

- You get one file per run with the same fields the judge sees: question,
  intended protein, checklist, and the final answer with arm labels and
  one-sided tool names removed.
- Do not open the key file, the judge outputs, or the run records.
- Score each run on its own. Do not go back and change a score after moving on.
- Aim for about 5 minutes per run. Stop and take a break after 10.

## Rubric (same as the judge)

Goal Completion: full / partial / deferred / null.
Data Grounding: 0 / 1 / 2.
Final Answer Complete: yes / no.
Checklist items: correct / incorrect / missing (skip items marked `scripted`).
For HONEST-REPORTING prompts, a clear and correct statement that the data do
not support a claim is full.

---

=== RUN ryawlb6lbjx ===
QUESTION:
Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[C03_b] [critical] [judged] the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final analysis plan

1. [✗] Initial ligand lookup used `SHP099`; 5EHR indexes this compound as RCSB component **`5OD`**. The contact query was corrected.
2. [✓] SHP099 contacts were mapped to Q06124 and transferred to both 2SHP chains.
3. [✗] Initial ANM extraction/aggregation did not preserve the full 3N displacement vectors. This was corrected using local ProDy and independently validated against ProDy’s canonical `calcSqFlucts` calculation.
4. [✓] ANM and GNM mobility was compared between contact and non-contact residues, with chain-stratified statistics.
5. [✓] Mode-window and ligand-contact-cutoff sensitivity were evaluated.
6. [✓] Results, limitations, and interpretation were finalized.

## Bottom line

**In the autoinhibited 2SHP structure, the future SHP099-contact surface is substantially less mobile than the rest of SHP2 in the anisotropic network model (ANM), but this separation is not reproduced by the isotropic Gaussian network model (GNM).**

Thus, the result supports a **directionally constrained, relatively rigid allosteric-pocket surface** in autoinhibited SHP2, rather than a general increase in contact-site mobility.

## 1. Contact residues used

SHP099 is stored in 5EHR as component **`5OD`**. Using a **4.0 Å minimum heavy-atom distance** criterion, the ligand contacts 15 unique Q06124 residues in each crystallographic chain:

| Q06124 numbering | Residue | Q06124 numbering | Residue |
|---:|:---|---:|:---|
| 108 | THR | 250 | GLU |
| 110 | GLU | 253 | THR |
| 111 | ARG | 254 | LEU |
| 113 | PHE | 257 | GLN |
| 114 | HIS | 491 | PRO |
| 218 | THR | 492 | LYS |
| 219 | THR | 495 | GLN |
| 249 | GLU |  |  |

All 15 positions are resolved in both chains of 2SHP. The amino-acid identities in 5EHR and 2SHP matched for all 30 chain-level contacts, confirming the UniProt-to-author-residue transfer.

## 2. Normal-mode analysis

The analysis used the 982 resolved Cα atoms in 2SHP: 491 per chain.

- **ANM:** Full ProDy 3N displacement vectors; 100 nontrivial modes retained.
- **GNM:** 981 nontrivial modes retained.
- Primary comparison: the **20 lowest-frequency nontrivial modes**.
- Two mobility measures were used:
  - **Thermal/RMSF-like proxy:**  
    \(\sqrt{\sum_m \sum_{xyz} u_{imx}^2/\lambda_m}\), matching ProDy’s inverse-eigenvalue square-fluctuation weighting.
  - **Equal-mode participation:**  
    \(\sqrt{\sum_m \sum_{xyz} u_{imx}^2}\), emphasizing participation in collective modes without weighting by stiffness.

Values are relative units, not experimental Å-scale RMSFs.

## 3. Contact versus non-contact mobility

| Model and metric | Contact median | Rest median | Contact/rest | Cliff’s δ | Chain-stratified p |
|---|---:|---:|---:|---:|---:|
| **ANM thermal proxy** | 0.2498 | 0.3900 | **0.641** | **−0.712** | **0.0004** |
| **ANM equal-mode** | 0.0881 | 0.1143 | **0.771** | **−0.530** | **0.0251** |
| GNM thermal proxy | 0.1009 | 0.1039 | 0.971 | +0.127 | 0.9084 |
| GNM equal-mode | 0.0987 | 0.0800 | 1.234 | +0.156 | 0.4008 |

Negative Cliff’s δ means the contact residues are less mobile.

### ANM result

- SHP099-contact residues have an ANM thermal proxy approximately **36% lower** than the rest of the structure.
- Chain A ratio: **0.626**; chain B ratio: **0.662**.
- Chain-wise Mann–Whitney p-values were \(1.05\times10^{-6}\) and \(8.84\times10^{-6}\), respectively.
- Stratified bootstrap 95% CI for the pooled median difference:  
  **−0.184 to −0.114**.
- Of 30 chain-level contact instances:
  - **22/30** were below the 20th within-chain mobility percentile.
  - **29/30** were below the within-chain median.
  - **0/30** were at or above the 80th percentile.

The most constrained contact positions by mean ANM thermal percentile were:

- **Q495:** 0.7th percentile
- **L254:** 1.6th
- **Q257:** 2.9th
- **P491:** 3.1st
- **K492:** 5.0th
- **T253:** 6.0th

### GNM result

GNM detected no significant global shift:

- Thermal proxy: essentially unchanged; stratified p = 0.908.
- Equal-mode participation: a modest trend toward greater contact-site participation, but not significant; stratified p = 0.401.

The ANM/GNM disagreement indicates that the result is driven by **anisotropic, directionally constrained collective motions** that the isotropic GNM cannot represent.

## 4. Robustness checks

### Mode-window sensitivity

For ANM, the contact/rest median ratio remained below 1 under every tested window:

- Thermal proxy, 1–100 modes: **0.560–0.650**
- Equal-mode metric, 1–100 modes: **0.594–0.795**

Thus, the ANM conclusion was not produced by a single mode.

### Contact-cutoff sensitivity

| SHP099 contact cutoff | ANM thermal ratio | ANM equal-mode ratio |
|---:|---:|---:|
| 3.5 Å | 0.643 | 0.772 |
| 4.0 Å | 0.641 | 0.771 |
| 4.5 Å | 0.636 | 0.756 |
| 5.0 Å | 0.643 | 0.773 |

All contact positions at these cutoffs were resolved in 2SHP. The conclusion was unchanged.

## Interpretation

The future SHP099-binding surface is, in the autoinhibited 2SHP conformation, **relatively rigid in anisotropic collective modes compared with the remainder of SHP2**. This is compatible with an allosteric pocket that is preformed or conformationally caged in the inactive state, potentially requiring local rearrangement for inhibitor binding.

However, this analysis does **not** show that SHP099 itself mobilizes the pocket: normal-mode analysis was performed only on 2SHP, while the contact definition was transferred from 5EHR. It also does not provide experimental timescales or demonstrate a ligand-induced transition.

## Limitations

- Normal-mode analysis describes stiffness and potential mobility of a static crystal structure, not full conformational thermodynamics.
- The SHP099 contacts are from the inhibitor-bound 5EHR structure projected onto inhibitor-free 2SHP; their local environments may differ.
- The two crystallographic copies are related observations. Chain-wise results and chain-stratified permutation/bootstrap statistics are therefore more informative than the pooled p-values alone.
- The GNM result does not independently confirm the ANM separation, so the mechanistic conclusion should remain model-qualified.
- For ANM, full ProDy 3N vectors were required because the wrapper’s returned ANM matrix truncates coordinate rows. The calculation was validated against ProDy `calcSqFlucts` with a maximum absolute RMSF difference of \(3.3\times10^{-16}\).

## Saved outputs

Results are under `/agent_cwd/outputs/shp2_nma/`, notably:

- `shp099_contact_mobility_by_residue.csv`
- `mobility_comparison_results_corrected.json`
- `contact_cutoff_sensitivity.json`
- `validation_checks.json`
- `2shp_anm_local_full_vectors_100modes.npz`
=== END RUN ryawlb6lbjx ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

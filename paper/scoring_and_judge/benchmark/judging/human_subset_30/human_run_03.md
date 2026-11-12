# Human rating sheet: run r82ul0njoc8 (3 of 30)

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

=== RUN r82ul0njoc8 ===
QUESTION:
Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[C03_b] [critical] [judged] the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan status
1. [✓] Retrieve and validate UniProt Q06124, PDB 2SHP, and PDB 5EHR.
2. [✓] Identify SHP099 contacts in both 5EHR chains using heavy-atom distances.
3. [✓] Map contact residues to Q06124 and verify their identities.
4. [✓] Run and validate GNM normal-mode analysis on 2SHP chain A.
5. [✓] Run a direction-resolved ANM validation.
6. [✓] Test cutoff, mode-window, crystal-copy, B-factor, and solvent-accessibility robustness.
7. [✓] Generate tables, figures, a methods report, and a verified result archive.

## Result

Using SHP099 chemical component `5OD` in 5EHR, the same **15 residues** contacted the inhibitor in both protein chains at a 4.0 Å heavy-atom cutoff. Mapped to UniProt Q06124 numbering, they are:

**T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, and Q495.**

The 4.5 Å sensitivity set additionally includes **D489 and Y511**. All mapped residue identities agree with Q06124.

### Primary GNM comparison

The primary isotropic GNM used 491 modeled Cα residues from 2SHP chain A, a 10 Å network cutoff, and uniform springs. Mobility was measured as relative RMSF, normalized to a structure-wide mean of 1. The remaining **476 modeled residues** formed the comparison group.

| Mode window | Contact mean | Rest mean | Contact/rest ratio | Mann–Whitney p | Permutation p |
|---|---:|---:|---:|---:|---:|
| First 10 soft modes | 0.649 | 1.011 | **0.642** | \(2.23\times10^{-5}\) | **0.00846** |
| All nonzero modes | 0.932 | 1.002 | 0.930 | 0.216 | 0.310 |

For the first 10 modes:

- Contact/rest mean-ratio 95% bootstrap CI: **0.555–0.739**
- Median mobility ratio: **0.655**
- Mean difference: **−0.362**, 95% CI **−0.454 to −0.261**
- Cliff’s δ: **−0.643**
- **13/15** contact residues were below the rest-group median.
- **5/15** were in the lowest mobility decile, including Q495, K492, P491, and Q257.

Thus, the SHP099-contact-corresponding residues are approximately **36% less mobile in the low-frequency collective modes** of autoinhibited 2SHP.

### Robustness

The lower mobility persisted with:

- GNM network cutoffs of **8, 10, and 12 Å**
- The independent 2SHP **chain B** copy
- The first **5, 10, and 20** modes
- The 3.5 and 4.5 Å SHP099-contact definitions

A ProDy direction-resolved ANM gave the same sign:

- All modes: contact/rest mean **0.835/1.005**, ratio **0.830**
- First 10 modes: contact/rest mean **0.712/1.009**, ratio **0.706**

The ANM effect was less statistically decisive—Mann–Whitney \(p=0.0092\) for all modes and \(p=0.0394\) for the first 10 modes, but permutation \(p=0.123\) and \(0.161\), respectively.

Crystallographic B-factors were essentially identical between groups, and the SASA/connectivity-adjusted exploratory regression retained the negative contact coefficient.

## Interpretation

The residues that form the SHP099-binding surface in the open, inhibitor-bound 5EHR structure correspond to a **relatively constrained allosteric region in the autoinhibited 2SHP conformation**, particularly in its lowest-frequency collective motions. The difference is modest when all GNM modes are included, so the strongest conclusion is specifically about **low-frequency intrinsic mobility**, not absolute immobility.

This analysis does **not** measure the effect of adding SHP099: the contact map came from 5EHR, whereas the normal-mode model was calculated on ligand-free 2SHP. It therefore describes the intrinsic dynamic constraint of the autoinhibited state at residues that contact the inhibitor in the open state.

Additional limitations include the elastic-network approximation, the use of contacts from a different conformation, 34 unmodeled 2SHP construct positions, and the non-independence of residues in a coupled elastic network. All 15 primary contact residues were modeled.

## Outputs

- Full report: `/agent_cwd/shp2_nma/results/ANALYSIS_REPORT.md`
- Contact mapping: `/agent_cwd/shp2_nma/results/5EHR_SHP099_contacts_uniprot_mapped.csv`
- GNM mobility table: `/agent_cwd/shp2_nma/results/2SHP_chainA_GNM10_residue_mobility.csv`
- ANM mobility table: `/agent_cwd/shp2_nma/results/2SHP_chainA_ANM10_residue_mobility.csv`
- Refined statistics: `/agent_cwd/shp2_nma/results/primary_statistics_refined.csv`
- Robustness results: `/agent_cwd/shp2_nma/results/robustness_GNM_comparisons.csv`
- Figures: `/agent_cwd/shp2_nma/figures/`
- Complete reproducible archive: `/agent_cwd/shp2_nma_results.zip`

### Sources

- UniProt Q06124: https://www.uniprot.org/uniprotkb/Q06124
- PDB 2SHP: https://www.rcsb.org/structure/2SHP
- PDB 5EHR: https://www.rcsb.org/structure/5EHR
=== END RUN r82ul0njoc8 ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

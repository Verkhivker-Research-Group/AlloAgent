# Human rating sheet: run rzaeo4ps3c4 (20 of 30)

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

=== RUN rzaeo4ps3c4 ===
QUESTION:
Run normal mode analysis on PTP1B (UniProt P18031, PDB 1T4J chain A). Where are the hinge residues of the slowest non-trivial mode, and how mobile is the WPD loop (the loop containing the catalytic Asp181) relative to the rest of the protein?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C01_b] [critical] [judged] the hinge residues of the slowest non-trivial normal mode and the relative mobility of the WPD loop (the catalytic Asp181) are reported, in UniProt numbering

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

Using chain A of **PDB 1T4J** (282 Cα atoms), UniProt **P18031**, a directional-spring ANM with a 15 Å cutoff, and a scalar GNM cross-check:

- The first six ANM modes were verified as rigid-body modes.
- The **slowest non-trivial ANM mode** has eigenvalue **0.709738**.
- PDB residue **Asp181 maps exactly to UniProt P18031 Asp181**.

### Hinge residues

Using the standard GNM definition—near-zero participation accompanied by a sign reversal between counter-moving regions—the principal hinge residues of the slowest mode are:

- **Phe30**
- **Ile72**
- **Ser80**
- **Trp179**
- **Lys197**
- **Gly218**

A distance-dependent Gaussian GNM confirmed the robust hinge regions around **Phe30, Ile72/Ser80, Lys197, and Gly218/219**. In the WPD region, the boundary shifts slightly with the spring convention, but remains within **Thr177–Asp181**, centered on **Trp179**.

If a hinge is instead defined strictly as a local minimum of residue-wise displacement in the 3-D ANM mode, the strongest low-motion hinge cores are:

- **Phe95**
- **Leu172**
- **Arg156**
- **Leu251**

with nearby low-displacement residues including His94, His173, Leu250, Glu252, Arg157, and Val107.

### WPD-loop mobility

The WPD motif is **Trp179–Pro180–Asp181**. Its mobility was compared with the other 279 chain-A residues.

| Metric | WPD 179–181 | Rest of chain A | WPD/rest ratio |
|---|---:|---:|---:|
| Slowest ANM mode, mean displacement amplitude | 0.03625 | 0.04486 | **0.808** |
| Slowest ANM mode, RMS displacement amplitude | 0.03634 | 0.05975 | **0.608** |
| First 10 ANM modes, RMSF | — | — | **0.594** |
| All ANM modes, RMSF | 0.50131 | 0.48525 | **1.006** |
| Slowest GNM mode, participation | ~0.000020 | 0.00358 | **0.006** |

Using the wider loop window **177–183** gives essentially the same ANM result: an RMS-amplitude ratio of **0.598**. The result is also stable over 13–18 Å ANM cutoffs.

### Interpretation

The WPD loop is **not a mobile hot spot in the slowest collective mode**. It behaves as a relatively immobile, **hinge-like region**, with roughly:

- **61% of the RMS displacement** of the rest of the protein in the slowest ANM mode;
- **81% of the mean displacement**;
- essentially **zero GNM participation**, particularly at Asp181.

Thus, the slow-mode hinge closest to the catalytic site is centered on **Trp179**, with catalytic **Asp181** lying in an extremely low-participation segment. Across the entire low-frequency ensemble the WPD loop remains less mobile than average, although when all high-frequency modes are included its RMSF becomes approximately equal to that of the rest of the protein. This mode-specific result does not contradict the known open/closed flexibility of the WPD loop: that functional transition is a different collective coordinate and is not captured by this single slowest mode.

The analysis excluded waters and the bound FRJ allosteric inhibitor. Consequently, the results describe the 1T4J crystal conformation rather than an unliganded ensemble.

### Generated outputs

- `ptp1b_slowest_mode_diagnostics.png`
- `ptp1b_final_hinge_table.csv`
- `ptp1b_normal_mode_final_metrics.csv`
- `ptp1b_normal_mode_summary.json`

Final execution checklist:

1. [✓] Retrieve PDB 1T4J and verify chain A, residue numbering, and the Asp181-containing WPD segment  
2. [✗] Initial scalar-graph Laplacian attempt was discarded because it was not a \(3N\times3N\) ANM Hessian  
3. [✗] Initial zero-mode threshold test was discarded because it misclassified the rotational modes  
4. [✗] Initial rigid-projection diagnostic had an axis error and was rerun  
5. [✓] Diagnose and select the directional-spring ANM/GNM conventions  
6. [✗] First result-table assembly had an eigenvector-axis mismatch and was rerun  
7. [✓] Normalize eigenvectors and verify six rigid-body modes  
8. [✓] Correct and validate the independent Gaussian GNM  
9. [✓] Quantify WPD mobility and test cutoff/loop-window sensitivity  
10. [✓] Verify PDB–UniProt numbering and catalytic/WPD annotations  
11. [✓] Summarize methods, numerical results, and limitations
=== END RUN rzaeo4ps3c4 ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

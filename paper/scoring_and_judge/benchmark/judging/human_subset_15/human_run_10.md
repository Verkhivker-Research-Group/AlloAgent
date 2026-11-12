# Human rating sheet: run rjmwuxnrgis (27 of 30)

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

=== RUN rjmwuxnrgis ===
QUESTION:
Assess the switch-II pocket of KRAS G12C (UniProt P01116, PDB 6OIM): pocket detection on the ligand-stripped structure, ChEMBL bioactivity for sotorasib, ClinVar and AlphaMissense for G12C, and the distance from residue 12 to the inhibitor. Do the structural, chemical and variant evidence agree?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G01_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[G01_b] [critical] [judged] the pocket detection on the ligand-stripped 6OIM, the ChEMBL bioactivity of sotorasib, the ClinVar and AlphaMissense records for KRAS G12C and the distance from residue 12 to the inhibitor are all present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Overall assessment

**Yes. The structural, chemical, and variant evidence agree strongly.** In PDB 6OIM, KRAS G12C forms a ligand-accessible switch-II cavity, and sotorasib covalently captures the mutant Cys12 through its warhead. ChEMBL records show potent activity of sotorasib against KRAS in multiple assays, while ClinVar and AlphaMissense independently classify KRAS p.Gly12Cys as pathogenic.

## 1. Structural evidence

### Structure and ligand stripping

- **PDB:** 6OIM, chain A
- **UniProt:** P01116, human KRAS
- **Mutation in the deposited structure:** Cys12, explicitly annotated as the Gly12→Cys variant
- **Bound inhibitor:** `MOV`, identified by RCSB as **AMG 510 (bound form)**, i.e. **sotorasib**
- The ligand-free receptor retained **1,336 protein atoms**. All `HETATM` records were removed, including MOV, GDP, Mg²⁺, and waters.

### Pocket detection

**fpocket 4.2.3**

The top-ranked pocket had:

- fpocket score: **0.146**
- druggability score: **0.838**
- volume: **1,564 Å³**
- Cys12 present: **yes**
- **16 of the 17** protein residues within 4 Å of MOV were in this pocket
- **19 of the 23** residues within 5 Å were in this pocket

The top fpocket cavity is unusually broad because removing GDP exposes and merges the nucleotide-facing region with the inhibitor pocket. The relevant switch-II residues are nevertheless clearly represented.

**P2Rank 2.5.1**

P2Rank divided the region into two complementary pockets:

- **Pocket 1:** score 12.62, probability 0.656; included Cys12, Gly13, Lys16 and nearby residues.
- **Pocket 2:** score 5.97, probability 0.293; included Gly60, Gln61, Glu62, Glu63, His95, Tyr96, Gln99 and Val103.

Together, the two P2Rank pockets recovered **16 of the 17 residues contacting MOV within 4 Å** and **18 of the 23 within 5 Å**. Thus, two independent geometry methods converge on the crystallographic inhibitor site.

The crystallographic MOV-contacting residues within 4 Å were:

**9, 10, 12, 16, 34, 58, 59, 60, 61, 62, 63, 68, 72, 95, 96, 99, and 103.**

These include the key switch-II elements around **Gly60–Glu63** and **His95–Gln99**, plus the mutation-site Cys12.

### Cys12–inhibitor distance

The minimum heavy-atom separation is:

- **Cys12 SG–MOV C25: 1.805 Å**
- The deposited PDB `LINK` record explicitly identifies this as a **covalent Cys12 SG–C25 bond**.

For clarity, if “residue-to-inhibitor distance” means centroid distance rather than closest-atom distance, the Cys12 heavy-atom centroid to MOV heavy-atom centroid distance is **9.06 Å**. The biologically informative contact metric here is the **1.805 Å covalent bond**.

**Structural conclusion:** The switch-II cavity is detectable in the ligand-stripped coordinates, and the mutant Cys12 directly anchors the inhibitor covalently.

## 2. Chemical evidence: sotorasib against KRAS

The ChEMBL query identified:

- **Target:** P01116 / `CHEMBL2189121`
- **Compound:** sotorasib / `CHEMBL4535757`
- **Standard type:** IC50
- **Records:** 8

Values were:

| Assay result |
|---|
| **<7 nM** |
| 9.66 nM |
| 24.5 nM |
| 30 nM |
| 68 nM |
| 7,500 nM |
| >7,500 nM |
| >10,000 nM |

Thus, **five assays report sub-100 nM activity**, while three report micromolar-scale or weaker activity. The broad range reflects assay-context dependence, but the high-confidence ChEMBL records strongly support direct, potent KRAS engagement.

## 3. Variant evidence for G12C

### ClinVar

Two matching KRAS p.Gly12Cys records were retrieved:

1. **NM_004985.5(KRAS):c.34G>T (p.Gly12Cys)**
   - Clinical significance: **Likely pathogenic**
   - Review status: criteria provided, multiple submitters, **no conflicts**

2. **NM_004985.5(KRAS):c.33_34delinsCT (p.Gly12Cys)**
   - Clinical significance: **Pathogenic**
   - Review status: criteria provided, single submitter

These are alternative nucleotide changes producing the same protein consequence.

### AlphaMissense

For **P01116 G12C**:

- AlphaMissense pathogenicity score: **0.9975**
- Classification: **Pathogenic**

**Variant conclusion:** Both clinical and computational variant evidence support G12C as a strongly pathogenic KRAS alteration.

## 4. Do the evidence agree?

**Yes—strongly and mechanistically.**

1. **Structural:** A switch-II cavity is present in the ligand-stripped structure, independently identified by fpocket and P2Rank and supported by the bound MOV contacts.
2. **Mutation chemistry:** Cys12 provides a thiol that covalently captures the sotorasib warhead at **1.805 Å**.
3. **Chemical:** ChEMBL contains multiple sub-100 nM IC50 records for sotorasib against KRAS.
4. **Variant:** ClinVar calls G12C pathogenic/likely pathogenic, and AlphaMissense scores it **0.9975 pathogenic**.

Together, these findings support the same mechanism: **G12C creates a druggable, covalent anchor in the KRAS switch-II pocket, enabling potent inhibition by sotorasib.**

### Important qualifications

- Ligand stripping identifies a cavity in the **bound crystal conformation**; it does not model apo conformational relaxation.
- fpocket’s largest pocket is partly merged with the GDP-removal cavity, so P2Rank and direct ligand contacts are essential for assigning it specifically as the switch-II pocket.
- The ChEMBL potency range is assay-dependent and target-level records should not all be assumed to represent identical cellular or mutant-assay contexts.
- ClinVar and AlphaMissense establish pathogenicity, not individual-patient prediction of sotorasib response.

### Completed plan

1. [✓] Retrieve and map PDB 6OIM, identify its inhibitor component, and prepare a protein-only structure.
2. [✓] Detect and validate the ligand-free pockets with fpocket and P2Rank.
3. [✓] Query ChEMBL bioactivity for sotorasib against P01116.
4. [✓] Retrieve ClinVar and AlphaMissense evidence for KRAS G12C.
5. [✗] Initial distance calculation failed because of an incorrect Bio.PDB residue lookup.
6. [✓] Recalculate the distance using the correct MOV residue lookup and verify the deposited covalent linkage.
7. [✓] Synthesize the structural, chemical, and variant evidence.

Analysis artifacts were saved under `/agent_cwd/kras_g12c_assessment/`, including the stripped structure, tool outputs, distance calculation, and consolidated summary.
=== END RUN rjmwuxnrgis ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

# Human rating sheet: run r7vpzm9em9j (16 of 30)

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

=== RUN r7vpzm9em9j ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan

1. [✓] Inspect the complete 1OPK coordinate/HETATM record, identify how the myristoyl group is represented, and calculate direct contacts for the ATP ligand and myristoyl group
2. [✓] Strip bound ligands and run pocket detection; map detected pockets to the ATP and myristoyl sites and record each site's detection rank
3. [✗] Initial ChEMBL assay-metadata join failed because the local schema uses `assays.chembl_id`, not `assay_chembl_id`
3a. [✓] Inspect the actual schema and complete the corrected potency, assay, and variant join
4. [✓] Retrieve ClinVar and AlphaMissense evidence for T315I
5. [✓] Calculate minimum heavy-atom distances from mouse T315 to the contact residues defining each site in 1OPK
6. [✗] Initial human–mouse mapping output failed only during NumPy-to-JSON serialization
6a. [✓] Rerun the mapping with native integer conversion and verify residue equivalence
7. [✓] Integrate the structural, potency, and variant evidence and explain the implications for ATP-competitive versus myristoyl-site/allosteric inhibitors

## Important provenance qualification

**PDB 1OPK is mouse ABL1, UniProt P00520, not human P00519.** It is a 1.8-Å structure of the SH3–SH2–kinase construct. However, alignment of human P00519 and mouse P00520 showed that:

- Human and mouse residue 315 are both threonine.
- All **27/27 mapped ATP- and myristoyl-site contact residues** are identical and retain the same canonical numbering.

Thus the topology and distances are directly transferable to human numbering, although the deposited structure itself is mouse.

The deposited ligands are:

- **P16 = PD166326**, an ATP-site inhibitor—not imatinib.
- **MYR = myristic acid**, defining the myristoyl pocket.

Therefore, 1OPK provides site topology but not an imatinib-specific bound pose.

## 1. Contacts in PDB 1OPK

Contacts were calculated as minimum heavy-atom distances ≤4.0 Å. Canonical ABL1 numbers are given first, followed by PDB author numbers.

### ATP-site probe P16/PD166326 — 19 contacts

| Canonical ABL1 | PDB | Canonical ABL1 | PDB |
|---:|---:|---:|---:|
| L248 | L267 | I313 | I332 |
| Y253 | Y272 | **T315** | **T334** |
| V256 | V275 | E316 | E335 |
| A269 | A288 | F317 | F336 |
| V270 | V289 | M318 | M337 |
| K271 | K290 | G321 | G340 |
| E286 | E305 | L370 | L389 |
| M290 | M309 | A380 | A399 |
| V299 | V318 | D381 | D400 |
|  |  | F382 | F401 |

This places the canonical gatekeeper **T315 directly on the ATP-site edge** and in direct contact with P16.

### Myristoyl probe MYR — 8 contacts

| Canonical ABL1 | PDB |
|---:|---:|
| L340 | L359 |
| L341 | L360 |
| A344 | A363 |
| L429 | L448 |
| A433 | A452 |
| E462 | E481 |
| I502 | I521 |
| L510 | L529 |

The MYR and ATP-site contact sets are spatially distinct.

## 2. Pocket-detection ranks on the ligand-stripped structure

All HETATM records, including MYR and P16, were removed before running fpocket 4.2.3 and P2Rank 2.5.1.

| Site | fpocket rank | fpocket score | Druggability | Volume, Å³ | P2Rank rank | P2Rank score | P2Rank probability |
|---|---:|---:|---:|---:|---:|---:|---:|
| **ATP/P16** | **2** | 0.320 | 0.913 | 736 | **1** | 23.77 | 0.892 |
| **MYR** | **3** | 0.211 | 0.547 | 491 | **2** | 11.32 | 0.606 |

Mapping audit:

- fpocket ATP pocket #2 contains **18/19 P16-contact residues**.
- fpocket myristoyl pocket #3 contains **8/8 MYR-contact residues**.
- P2Rank independently assigns the ATP pocket rank 1 and the myristoyl pocket rank 2.

Thus both detectors identify the ATP cavity as the more prominent pocket in this conformation.

## 3. ChEMBL potency

Values below are from the ChEMBL 37 target record **CHEMBL1862 / P00519** where available. IC50 is used as the common potency metric.

### Imatinib, CHEMBL941

- Wild-type/unspecified ABL1: 39 exact IC50 records spanning **19.9–7,700 nM**, median **223 nM**.
- T315I: three exact IC50 values—**1,100, 5,155, and 74,000 nM**—plus numerous right-censored values, generally `>1,000` to `>100,000 nM`.
- A particularly informative matched recombinant FRET assay pair:
  - Wild type, CHEMBL2320772: **98.2 nM**
  - T315I, CHEMBL2320771: **5,155 nM**
  - Approximately **52-fold loss of potency**

The heterogeneous IC50 distribution reflects different constructs and assay formats; the matched WT/T315I pair is more interpretable than the global median.

### Asciminib, CHEMBL4208229

Two exact target-linked IC50 records:

- **0.5 nM**, CHEMBL4200739
- **16 nM**, CHEMBL5739300

Broader ChEMBL records also contain mutant activity, although not as P00519 IC50 records:

- Human BCR-ABL1 T315I biochemical FRET **EC50: 6.45 nM**, CHEMBL5374124
- Mouse Ba/F3 T315I cellular **GI50: 7.64 nM**, CHEMBL4200741

The EC50 and GI50 should not be directly pooled with the IC50 values, but they support retained asciminib activity against T315I.

## 4. T315I evidence

- **ClinVar variation 27663:** NM_005157.6:c.944C>T, p.Thr315Ile  
  - Clinical significance: **Likely pathogenic; association**
  - Review status: **multiple submitters, no conflicts**
- **AlphaMissense T315I:**
  - Pathogenicity score: **0.9991**
  - Classification: **pathogenic**

## 5. Distance from T315 to each site

Distances were calculated directly from the wild-type 1OPK coordinates, using **PDB T334 = canonical T315**.

| Metric | ATP/P16 site | MYR site |
|---|---:|---:|
| Minimum heavy-atom distance, T315 to bound ligand | **3.24 Å** | **25.59 Å** |
| Residue-centroid to ligand-centroid distance | **7.08 Å** | **32.28 Å** |
| Closest site-contact residue other than T315 | E316, 1.33 Å | A344, **20.43 Å** |

For ATP/P16, the closest pair was T315 OG1–P16 C16. For MYR, it was T315 OG1–MYR C14.

These are wild-coordinate distances; they do not model the steric rearrangement caused by replacing threonine with isoleucine.

## Interpretation: what does T315I imply?

### ATP-competitive inhibitors, including imatinib

T315 is the **gatekeeper residue** and is already a direct ATP-pocket contact in 1OPK. Replacing threonine with isoleucine:

- Adds substantially greater side-chain bulk in a crowded ATP pocket.
- Removes the threonine hydroxyl and associated polar/H-bond complementarity.
- Can alter the local kinase conformation and ATP-binding geometry.

The ChEMBL matched data demonstrate the consequence directly: imatinib shifts from **98.2 nM for WT to 5,155 nM for T315I**, with other assays showing even greater loss of potency. Thus:

- **Imatinib and most conventional type-I/type-II ATP-site inhibitors are strongly challenged by T315I.**
- The effect is not universal: ATP-site inhibitors specifically engineered to accommodate the isoleucine gatekeeper can retain activity.

### Myristoyl-site/allosteric inhibitors, exemplified by asciminib

The myristoyl site is **25.6 Å from T315 at the closest ligand-atom level**, and no MYR-contact residue is closer than approximately 20.4 Å. Consequently, T315I does not directly obstruct asciminib binding or compete with the myristoyl-site interaction.

Accordingly:

- Asciminib retains biochemical and cellular activity against T315I, including the ChEMBL T315I EC50 of **6.45 nM**.
- Unlike ATP-competitive inhibitors, asciminib is not directly defeated by the gatekeeper substitution because it binds the N-terminal myristoyl pocket and stabilizes an inactive ABL conformation.
- Cellular efficacy can still depend on ABL abundance, myristoylation/N-terminal processing, and kinase state; T315I is therefore not a direct steric resistance mechanism for asciminib, but the cellular context can influence its magnitude of activity.

**Bottom line:** T315I severely compromises the ATP-site interaction used by imatinib-like inhibitors, whereas the distant myristoyl-site mechanism used by asciminib largely preserves activity.

### Data sources

- RCSB PDB **1OPK**
- BioLiP ligand/contact records for **P16** and **MYR**
- fpocket **4.2.3** and P2Rank **2.5.1**
- ChEMBL 37 target **CHEMBL1862**; compounds **CHEMBL941** and **CHEMBL4208229**
- ClinVar variation **27663**
- AlphaMissense **P00519:T315I**
=== END RUN r7vpzm9em9j ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

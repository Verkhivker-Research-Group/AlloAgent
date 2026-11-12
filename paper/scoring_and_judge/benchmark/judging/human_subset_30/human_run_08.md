# Human rating sheet: run rkgsoyf7h8y (8 of 30)

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

=== RUN rkgsoyf7h8y ===
QUESTION:
For SHP2 (UniProt Q06124), report ClinVar classification and AlphaMissense score for E76K and D61Y, and say whether each residue lies at the interface with the allosteric inhibitor site (PDB 5EHR) or in the autoinhibitory interface (PDB 2SHP), using distances from coordinates.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[V01_b] [critical] [scripted] {"clinical_significance": "Conflicting classifications of pathogenicity", "variation_id": "28375"}
[V01_c] [critical] [scripted] 0.9998
[V01_d] [critical] [scripted] {"clinical_significance": "Conflicting classifications of pathogenicity", "variation_id": "230257"}
[V01_e] [critical] [scripted] 0.9985
[V01_f] [critical] [judged] the distances of residues 76 and 61 to the 5EHR inhibitor site and to the 2SHP autoinhibitory interface are reported

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Summary for SHP2/PTPN11 (UniProt Q06124)

| Variant | ClinVar aggregate classification | AlphaMissense score¹ | 5EHR: distance to SHP099 | 2SHP: distance to PTP domain | Structural assignment |
|---|---|---:|---|---|---|
| **E76K** — p.Glu76Lys, c.226G>A | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications ([ClinVar 13336](https://www.ncbi.nlm.nih.gov/clinvar/variation/13336/)) | **0.9998**, **likely_pathogenic** | Side-chain minimum **14.714 Å** in chain A and **14.827 Å** in chain B; no direct contact | Side-chain minimum **2.797 Å** in chain A and **2.819 Å** in chain B | **Autoinhibitory N-SH2–PTP interface: yes. Allosteric inhibitor interface: no.** |
| **D61Y** — p.Asp61Tyr, c.181G>T | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications ([ClinVar 228392](https://www.ncbi.nlm.nih.gov/clinvar/variation/228392/)) | **0.9985**, **likely_pathogenic** | Side-chain minimum **21.918 Å** in chain A and **21.974 Å** in chain B; all-heavy minimum **19.642/19.662 Å** | Side-chain minimum **3.751 Å** in chain A and **3.499 Å** in chain B; all-heavy minimum **3.689/3.499 Å** | **Autoinhibitory N-SH2–PTP interface: yes. Allosteric inhibitor interface: no.** |

¹ AlphaMissense’s official `am_pathogenicity` value from the canonical Q06124/ENST00000351677 release row. The separate dbNSFP/MyVariant converted `rankscore` values are **0.99585** for E76K and **0.9785** for D61Y.

### ClinVar condition-level context

- **E76K:** pathogenic submissions for JMML, Noonan syndrome 1, and PTPN11-related disorder; uncertain-significance submissions for RASopathy and some malignancy submissions.
- **D61Y:** pathogenic submissions for JMML and “not provided”; conflicting interpretations for Noonan syndrome 1.

## Coordinate-based interpretation

Distances were calculated from the deposited heavy atoms, excluding hydrogens. A **≤4.5 Å** heavy-atom criterion was used for direct contact; both autoinhibitory-interface assignments also remain valid at a stricter 4.0 Å cutoff.

### 5EHR allosteric inhibitor site

Ligand **5OD is SHP099**. Neither D61 nor E76 is part of its binding-site lining:

- **E76–5OD:** 14.714/14.827 Å, represented by **GLU76 OE2–5OD CL2**.
- **D61–5OD:** side-chain minimum 21.918/21.974 Å and all-heavy minimum 19.642/19.662 Å.
- Even the nearest atoms lining the SHP099 pocket are **11.094/11.255 Å from E76** and **16.325/16.436 Å from D61**.

Thus, neither residue directly contacts or lines the 5EHR allosteric inhibitor site.

### 2SHP autoinhibitory interface

The interface was defined as same-chain contacts between the UniProt-annotated **N-SH2 domain (6–102)** and **PTP domain (247–517)**. Both deposited chains reproduce the result:

- **D61:** contacts **Ser460** and **Arg465**:
  - Chain A: **ASP61 CG–SER460 OG = 3.751 Å**
  - Chain B: **ASP61 OD1–ARG465 CD = 3.499 Å**
- **E76:** contacts **Leu262, Arg265, Asn281, Phe285,** and **Ser502**:
  - Chain A: **GLU76 OE2–SER502 OG = 2.797 Å**
  - Chain B: **GLU76 OE2–SER502 OG = 2.819 Å**

Therefore, **both E76 and D61 are autoinhibitory-interface residues, whereas neither lies at the SHP099-binding interface in 5EHR**. These measurements describe the wild-type deposited coordinates; mutation-induced side-chain rearrangement is not modeled.

### Sources

- UniProt: [Q06124](https://rest.uniprot.org/uniprotkb/Q06124)
- AlphaMissense official release: [data](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz), [schema/README](https://storage.googleapis.com/dm_alphamissense/README.pdf), and [Science 2023](https://doi.org/10.1126/science.adg7492)
- PDB coordinates: [5EHR](https://www.rcsb.org/structure/5EHR), [2SHP](https://www.rcsb.org/structure/2SHP)
- Primary structural papers: [Chen et al., Nature 2016](https://doi.org/10.1038/nature18621); [Hofmann et al., Cell 1998](https://doi.org/10.1016/S0092-8674(00)80938-1)

**Updated plan**
1. [✓] Retrieve ClinVar classifications and AlphaMissense scores for PTPN11 E76K and D61Y.
2. [✓] Download PDB 5EHR and 2SHP coordinate data and identify the bound allosteric inhibitor and relevant interface atoms.
3. [✓] Calculate minimum heavy-atom distances from E76 and D61 to the 5EHR inhibitor and to the 2SHP autoinhibitory interface.
4. [✓] Reconcile the distance evidence with the structural interface definition and document any chain/alternate-location caveats.
5. [✓] Report the source-linked classifications, scores, distances, and conclusions.
=== END RUN rkgsoyf7h8y ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

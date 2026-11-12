# Human rating sheet: run rnu397cfkat (10 of 30)

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

=== RUN rnu397cfkat ===
QUESTION:
For SHP2 (UniProt Q06124), combine ClinVar and AlphaMissense for E76K and D61Y, distances to the autoinhibitory interface in 2SHP, pocket detection on 2SHP, and normal mode analysis. Does the evidence support activating variants destabilizing the autoinhibited state that SHP099 stabilizes?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[G03_b] [critical] [judged] the ClinVar and AlphaMissense records for E76K and D61Y, the distances to the 2SHP autoinhibitory interface, the pocket detection on 2SHP and the normal mode analysis are present, with the conclusion hedged and the limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Conclusion

**Yes—with an important pharmacological caveat.** The combined evidence strongly supports the mechanism that **SHP2 E76K and D61Y weaken the N-SH2–PTP autoinhibitory interface and shift SHP2 toward catalytically competent conformations**. The state stabilized by SHP099 is the **wild-type closed, autoinhibited state**, not necessarily the activating mutant.

For **E76K**, this is supported directly by an open mutant crystal structure and by closed E76K–SHP099 structures. For **D61Y**, the evidence is strong and convergent—functional experiments, mutation-specific molecular dynamics, ClinVar/AlphaMissense, and shared interface geometry—but there is **no deposited D61Y crystal structure**.

## 1. ClinVar and AlphaMissense

| Variant | Exact identifiers | ClinVar | AlphaMissense |
|---|---|---|---|
| **E76K** | `VCV000013336.57`; `NM_002834.5:c.226G>A (p.Glu76Lys)`; GRCh38 `12:112450406 G>A`; `rs121918464`; UniProt `Q06124#VAR_016000` | Germline classification: **Conflicting classifications of pathogenicity**, criteria provided, conflicting classifications; last evaluated 2024-12-18. Clinical impact: **Tier II–Potential**. Oncogenicity: **Oncogenic**, single submitter. 13 SCVs/9 RCVs. | **0.9998**, **likely_pathogenic** |
| **D61Y** | `VCV000228392.53`; `NM_002834.5:c.181G>T (p.Asp61Tyr)`; GRCh38 `12:112450361 G>T`; `rs397507510`; UniProt `Q06124#VAR_015992` | Germline classification: **Conflicting classifications of pathogenicity**, criteria provided, conflicting classifications; last evaluated 2025-11-19. Clinical impact: **Tier I–Strong**. 9 SCVs/6 RCVs. | **0.9985**, **likely_pathogenic** |

Additional points:

- ClinVar associates both variants with **RASopathy, Noonan syndrome 1, and juvenile myelomonocytic leukemia (JMML)**.
- The conflicting germline aggregate should not be interpreted as evidence that the substitutions are benign; classification varies with somatic versus germline origin, penetrance, and disease context.
- AlphaMissense is an **in-silico pathogenicity predictor**, not a direct activation assay.
- All scored substitutions at D61 and E76 in the official AlphaMissense table were likely pathogenic:
  - D61 substitutions: **0.9646–0.9997**
  - E76 substitutions: **0.9970–0.9998**
- The 2025 deep-mutational-scanning study found that **D61, E76, and S502 substitutions are highly enriched for increased full-length SHP2 activity**, supporting the residues as functional hotspots rather than merely prediction hotspots.

## 2. Distances to the 2SHP autoinhibitory interface

I defined the interface using all heavy atoms within 5.0 Å between:

- N-SH2: residues 1–115
- PTP: residues 225–525

In chain A of wild-type **2SHP** at 2.0 Å resolution, this gives 666 contact atom pairs involving 28 N-SH2 and 30 PTP residues.

### D61

- **Direct N-SH2–PTP interface residue**
- 35 PTP contact atom pairs
- Closest contacts:
  - I463: **3.689 Å**
  - S460: **3.751 Å**
  - A461: **3.768 Å**
- Chain B additionally shows a close D61–R465 contact of **3.499 Å**
- Cα-to-interface-centroid distance: **10.398 Å**

Thus D61 engages the PTP 460–465 loop, including Arg465 in the second 2SHP molecule.

### E76

- **Direct N-SH2–PTP interface residue**
- 37 PTP contact atom pairs
- Closest contact: E76–S502, **2.797 Å**
- Cα-to-interface-centroid distance: **6.926 Å**

Thus E76 is even more directly embedded in the autoinhibitory contact network.

These findings explain why replacing either acidic residue with lysine or tyrosine can disrupt favorable interface electrostatics and packing.

## 3. Relationship to the SHP099 pocket

Mapping the SHP099 ligand from **5EHR** onto 2SHP identified the pocket as lined by:

- N-SH2/C-SH2 side: T108, E110, R111, F113, H114, T218, T219
- PTP side: E249, E250, T253, L254, Q257, D489, P491, K492, Q495, Y511

After superposition into 2SHP:

- Minimum D61–SHP099 distance: **20.038 Å**
- Minimum E76–SHP099 distance: **14.863 Å**
- Nearest SHP099 pocket-lining residues:
  - D61–Y511: **11.065 Å**
  - E76–Q257: **9.926 Å**

Therefore, **D61 and E76 are not direct SHP099-pocket residues**. They destabilize autoinhibition through the N-SH2–PTP interface, while SHP099 acts through a distinct allosteric pocket that biases the ensemble toward the closed state.

## 4. Independent pocket detection on 2SHP

`fpocket 4.0` detected 34 cavities in chain A of 2SHP.

The best SHP099-matched result was **cavity 20**:

- Volume: **1164.5 Å³**
- All **23/23** mapped SHP099 ligand atoms were within 4 Å of cavity vertices
- Pocket-center to ligand-center distance: **1.71 Å**
- Overlap with experimentally mapped SHP099 pocket-lining residues: **16 residues**
- Residue-set Jaccard index: **0.571**
- D61 and E76 were respectively **20.04 Å** and **14.86 Å** from the mapped ligand

A separate cavity was only **3.40 Å** from E76 but did not overlap the SHP099 ligand. This further supports a distinction between the local E76 interface environment and the drug-binding cavity.

## 5. Open/closed structural comparison

All-atom interface metrics give a direct structural explanation:

| Structure | State | Interface atom pairs | N-SH2/PTP interface residues | Domain-centroid separation |
|---|---|---:|---:|---:|
| **2SHP** | WT autoinhibited | 666 | 28 / 30 | 29.83 Å |
| **6CRF** | E76K open | 205 | 12 / 15 | 42.79 Å |
| **6CRG** | E76K + SHP099 | 610 | 26 / 28 | 30.11 Å |
| **6CMS** | E76K + SHP099 | 669 | 30 / 30 | 29.48 Å |

This is strong direct evidence that:

1. E76K opens and weakens the autoinhibitory interface.
2. SHP099 can shift E76K back toward a WT-like closed interface.

No D61Y structure was found among the 115 PTPN11/Q06124 PDB cross-references. PDB **4H1O** is D61G and captures a closed-like state, so it is only a same-residue analog and was not used as a direct D61Y structure.

## 6. Normal-mode analysis

I used Cα elastic-network models:

- ANM: 15 Å contact cutoff
- GNM: 10 Å contact cutoff
- First ten nontrivial modes
- No mutation-specific free energy was inferred; this is a topology and collective-dynamics analysis.

### Low-frequency opening motions

The N-SH2–PTP domain-separation coordinate was concentrated in low modes. The fraction represented by the first ten modes was:

- 2SHP WT: **0.768**
- Open E76K, 6CRF: **0.876**
- E76K–SHP099, 6CRG: **0.754**
- E76K–SHP099, 6CMS: **0.743**

More directly, after aligning the PTP domains and expressing both structures in a common coordinate frame, the experimentally observed **closed 6CRG → open 6CRF N-SH2 deformation** was projected onto the 2SHP ANM basis:

- First five modes captured **42.04%**
- First ten modes captured **52.18%**
- Random equal-norm vectors captured only **0.34%** and **0.67%**, respectively
- The 95% random-null range for ten modes was **0.23–1.39%**

Thus the autoinhibited WT structure possesses low-frequency collective motions compatible with the experimentally observed opening route.

### Interface weakening stress test

Halving all GNM springs connecting each N-SH2 residue to its direct 5 Å PTP partners produced a matched comparison:

- **D61:** interface-mobility effect ranked **7/115**
- **E76:** interface-mobility effect ranked **4/115**

Their contact networks are therefore among the most consequential tested for interface mobility. The absolute coarse-grained effects were small, and static GNM coupling alone did not make E76 a globally central residue, so this result is corroborative rather than a stand-alone energetic demonstration.

## 7. Functional literature

- **Hof et al., Cell 1998, PMID 9491886:** 2SHP N-SH2 directly binds the PTP domain and blocks the active site.
- **Chen et al., Nature 2016, PMID 27362227:** SHP099 stabilizes autoinhibited SHP2 and binds the N-SH2/C-SH2/PTP interfacial allosteric pocket.
- **Pádua et al., Nat Commun 2018, PMID 30375376:** WT SHP2 exchanges between closed and open conformations; E76K shifts the ensemble toward open. SHP099 binds E76K much more weakly but produces the same closed structure.
- **LaRochelle et al., Nat Commun 2018, PMID 30375388:** E76K adopts an open conformation but can be driven to a WT-like closed state by SHP099. SHP099 potency scales inversely with activation strength; strongly activating E76/D61/G60/S502 mutants are effectively resistant in cells, with at least approximately two orders of magnitude greater potency estimated to be necessary.
- **D61Y functional evidence:**
  - PMID 18640765: D61Y and E76K increased progenitor cell-cycle progression, reduced apoptosis, and increased cytokine-independent colonies.
  - PMID 19179468: conditional D61Y knock-in mice developed fatal myeloproliferative disease.
  - PMID 22504523: D61Y caused MPD, although leukemia progression was weaker than for E76K.
  - PMID 30508783: D61Y-specific MD found increased flexibility of the PTP catalytic-region loops and altered D61/Q506/C459/R465 interaction networks, exposing the catalytic site.
- **PMID 40920905, 2025:** E76K flattens the activation energy landscape, stabilizes activation-competent ensembles, and rewires interdomain allosteric communication.
- **PMID 40595497, 2025:** deep mutational scanning identifies D61, E76, and S502 substitutions as highly enriched for activating full-length SHP2.

## Integrated interpretation

The evidence supports this sequence:

1. Wild-type SHP2 occupies a **closed N-SH2–PTP autoinhibited interface**.
2. **D61Y and E76K directly perturb that interface**, weakening favorable contacts and shifting the conformational ensemble toward open/catalytically competent states.
3. **SHP099 binds a separate allosteric pocket** and biases SHP2 toward the closed state.
4. SHP099 can force E76K into a closed-like structure in vitro, but because strongly activating mutants have a higher open-state population and greater catalytic activity, SHP099 binds them poorly and is ineffective at cellular concentrations.

Therefore, the accurate formulation is:

> **The activating variants destabilize the autoinhibited conformational ensemble that SHP099 preferentially stabilizes; SHP099 does not simply “stabilize the mutant.”**

### Primary resources

- ClinVar E76K: https://www.ncbi.nlm.nih.gov/clinvar/variation/13336/
- ClinVar D61Y: https://www.ncbi.nlm.nih.gov/clinvar/variation/228392/
- Official AlphaMissense GRCh38 table: https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz
- PDB structures: https://www.rcsb.org/structure/2SHP, https://www.rcsb.org/structure/5EHR, https://www.rcsb.org/structure/6CRF, https://www.rcsb.org/structure/6CRG, https://www.rcsb.org/structure/6CMS

### Completed plan
1. [✓] Retrieved and verified ClinVar records and exact AlphaMissense scores
2. [✓] Collected primary variant, functional, structural, and inhibitor literature
3. [✓] Defined the 2SHP autoinhibitory interface and mapped the SHP099 pocket
4. [✓] Computed D61/E76 interface, pocket, and open/closed structural distances
5. [✓] Performed and validated fpocket pocket detection
6. [✓] Completed corrected ANM/GNM analyses and deformation-mode projection
7. [✓] Integrated the evidence, caveats, and mechanistic conclusion
=== END RUN rnu397cfkat ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

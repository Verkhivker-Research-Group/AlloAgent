# Judge batch 017 of 24

## Instructions to the judge (paste at the top of every session)

You are scoring answers to protein-science questions. You will see up to 10
runs. Each run has an opaque run ID, the question that was asked, the protein
the question is about, a list of checklist items, and the final answer that a
software agent produced. Score each run independently of the others.

Rules:

1. Judge only what is written in the final answer. Do not reward effort, tools
   used, or confidence. Do not guess what the agent did.
2. Use only the facts in the checklist as ground truth. If the answer states a
   fact that is not in the checklist and you cannot tell whether it is true,
   do not count it for or against the run.
3. Tool names that exist in only one system have been replaced by `[TOOL]`.
   Do not try to infer which system produced an answer.
4. If the answer is about a different protein than the intended one, Goal
   Completion is null.
5. Quote the shortest span of the answer that supports each decision.
6. Do not read, compare, or refer to other runs in the batch when scoring one.

### Goal Completion

- full: every part of the request is answered with substantive results for the
  intended protein.
- partial: some parts are answered, others are missing or wrong.
- deferred: the answer explains how the analysis could be done, or asks the
  user to clarify, without doing it.
- null: empty, truncated, an error message, off topic, or about a different
  protein.

For questions marked HONEST-REPORTING in the checklist, the correct answer is
that the data do not support a claim. Score a clear, correct statement of that
limit as full. Score an invented answer as null.

### Data Grounding (0, 1, 2)

- 0: conclusions rest on narrative only, with no identifiers, numbers, residues
  or structures stated.
- 1: some conclusions cite specific data (a database identifier, a numeric
  value, a residue index, a structure ID); others do not.
- 2: the main conclusions all cite specific data stated in the answer.

### Final Answer Complete

yes if the answer ends in a clear final response to the question; no if it is
cut off, ends mid-analysis, or only describes a plan.

### Checklist items

For each item listed for the run, give one of:

- correct: the answer states the fact or result the item asks for.
- incorrect: the answer states something that contradicts the item.
- missing: the answer does not address the item.
- not_applicable: the item names a specific method, or gives a reference result
  for a specific method, and the answer used a different method. Do not score
  it as incorrect or missing.

Rules for deciding:

1. If an item only asks that something be reported (for example "the rank is
   reported"), it is correct when the answer reports it. Do not compare the
   value with a reference that belongs to another method.
2. If an item requires a statement (for example a stated limit of a method),
   it is correct when the answer says it in substance. The wording does not
   need to match the item.
3. If an item says the answer must name its method and lists example methods,
   any named method satisfies it unless the item says otherwise.
4. An item that lists several required parts (for example "X, Y and Z are all
   present") is correct only when every part is present. If any part is absent,
   give `missing`; if a part contradicts the item, give `incorrect`.
5. An item that is only a JSON object is the reference output of the method it
   names. It is correct when the answer's result for that method has the same
   rank and overlap values (differences in rounding do not matter) and
   `not_applicable` when the answer used a different method.
6. Give exactly one verdict for every item marked `[judged]`, including items
   tagged `[low-information item]`. Never leave a judged item out. If you cannot
   tell, use `missing`, or `not_applicable` if the answer used a different
   method. Before you answer, check that your list of items for each run has
   every `[judged]` item from that run's checklist.

### Reading of one item

- S04_d ("the contact residues fall in the PH domain of AKT1"): the ligand's
  contacts lie at the PH-kinase interface, so some contacts are in the PH domain
  (residues 5-108) and some in the kinase domain. Give `correct` when the answer
  identifies the contacts that lie in the PH domain and puts the domain boundary
  in the right place, even if it also reports kinase-domain contacts. Give
  `incorrect` only if it assigns the contacts to the wrong domains.

Items marked `scripted` were already scored by a program. Do not score them;
they appear only for context. Items marked `critical` decide success.
Items that depend on the method (pocket-detection prompts) are written so that
any listed method counts; read the item text.

### Output format

Return one JSON object per run, in a single JSON array, and nothing else:

```
[
  {
    "run_id": "<opaque id>",
    "goal_completion": "full|partial|deferred|null",
    "data_grounding": 0,
    "final_answer_complete": "yes|no",
    "items": [
      {"item_id": "<id>", "verdict": "correct|incorrect|missing|not_applicable",
       "evidence": "<shortest supporting quote, or empty if missing>"}
    ],
    "notes": "<one sentence, only if something unusual affected the score>"
  }
]
```

---

=== RUN rmowm6fk0p2 ===
QUESTION:
Run pocket detection on the autoinhibited SHP2 structure 2SHP (UniProt Q06124). Do any of the top five pockets cover residues that contact SHP099 in PDB entry 5EHR? Map residues between the entries through UniProt numbering and report the overlap.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[P03_b] [critical] [scripted] [{"rank": 1, "residues": 21}, {"rank": 2, "residues": 21}, {"rank": 3, "residues": 22}]
[P03_c] [critical] [judged] the overlap of the top five pockets of 2SHP with the 5EHR SHP099 contact residues, mapped through UniProt numbering, is reported
[P03_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P03_e] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

REFERENCE NOTE (dated correction, from benchmark/corrections.md)
The pocket-detection reference for the 5EHR site was corrected on 2026-11-02: the committed selection took the first pocket with any overlap (rank 7, overlap 3), the corrected selection takes the pocket with the most site residues (rank 40, overlap 15).
No committed checklist item carries this site, so the item texts below are unchanged.

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**Yes.** One of the top five pockets—**P2Rank pocket 5**—contains three residues that contact SHP099 in PDB **5EHR**:

| UniProt Q06124 | Residue | 2SHP pocket | 5EHR SHP099 contact | Minimum heavy-atom distance |
|---:|---|---|---|---:|
| **110** | Glu110 | Chain A, pocket 5 | Chains A and B | 3.109 Å |
| **111** | Arg111 | Chain A, pocket 5 | Chains A and B | 2.931 Å |
| **257** | Gln257 | Chain A, pocket 5 | Chains A and B | 3.578 Å |

Thus, the exact mapped overlap is:

**Q06124 110, 111, and 257.**

## Top-five 2SHP pockets

P2Rank was run on the complete deposited 2SHP asymmetric unit containing chains A and B.

| Pocket rank | P2Rank score | Probability | Exact SHP099-contact overlap |
|---:|---:|---:|---|
| 1 | 10.95 | 0.587 | None |
| 2 | 9.65 | 0.519 | None |
| 3 | 7.93 | 0.421 | None |
| 4 | 6.72 | 0.342 | None |
| **5** | **6.01** | **0.296** | **110, 111, 257** |

Pocket 5’s 2SHP residue list is:

`A109, A110, A111, A112, A191, A195, A198, A213, A215, A256, A257, A259, A260, A3, A4, A5`

## SHP099 contacts in 5EHR

SHP099 is represented by chemical component **5OD**, with one ligand copy in each SHP2 chain. Using a **4.5 Å heavy-atom contact cutoff**, the union of contacting UniProt positions is:

**108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 489, 491, 492, 495, 511**

Every mapped contact residue matched the canonical Q06124 sequence.

## UniProt numbering

The deposited `_struct_ref_seq.pdbx_auth_seq_align_beg/end` records map:

- **2SHP:** PDB author residues 1–525 → Q06124 residues 1–525
- **5EHR:** PDB author residues 1–525 → Q06124 residues 1–525

The 2SHP engineered substitutions **T2K, F41L, and F513S** remain at UniProt positions **2, 41, and 513**, respectively. For 5EHR, the separate `seq_align_beg/end` values of 2–526 describe entity/label numbering containing the expression tag; the author-residue alignment is the appropriate mapping for these comparisons.

## Robustness checks

- At a **4.0 Å** cutoff, the exact overlap remains **110, 111, 257**.
- At **5.0 Å**, Q06124 **109** and **112** are added.
- Chain-separated analyses support the same conclusion:
  - 2SHP chain A alone: the corresponding pocket is rank 2 and overlaps **110, 111, 257**.
  - 2SHP chain B alone: the corresponding pocket is rank 3 and overlaps **110, 111, 257**.

This is a UniProt sequence-position overlap; it does not imply that 2SHP and 5EHR have identical pocket conformations or ligand-bound poses.

### Auditable outputs

Saved under `/agent_cwd/results/shp2_pocket_overlap/`:

- `p2rank_2SHP/2SHP_for_fpocket.pdb_predictions.csv`
- `p2rank_top5_pocket_residues_mapped.csv`
- `5EHR_SHP099_contact_residues.csv`
- `top5_pocket_SHP099_overlap_provenance.csv`
- `pocket_contact_summary.json`
- `2SHP.cif`
- `5EHR.cif`
- `Q06124_canonical.fasta`
=== END RUN rmowm6fk0p2 ===

=== RUN rq7phaisgrx ===
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
=== END RUN rq7phaisgrx ===

=== RUN rrxhx5b3s3j ===
QUESTION:
PDB entry 5MO4 contains ABL1 bound to both asciminib and nilotinib. Identify each ligand, list the residues within 4 angstroms of each, state whether they occupy distinct sites, and explain how the entry's residue numbering relates to UniProt P00519 numbering.

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S07_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[S07_b] [critical] [scripted] [{"chain": "A", "pdb_number": 602}]
[S07_c] [critical] [scripted] [{"chain": "A", "pdb_number": 601}]
[S07_d] [critical] [scripted] {"uniprot_residues": [332, 337, 340, 341, 344, 429, 432, 433, 434, 435, 462, 464, 465, 468, 493, 502, 506, 510], "pdb_residues": [351, 356, 359, 360, 363, 448, 451, 452, 453, 454, 481, 483, 484, 487, 512, 521, 525, 529], "min_distances": {"351": 3.787, "356": 3.679, "359": 3.223, "360": 3.381, "363": 3.574, "448": 3.266, "451": 3.611, "452": 3.524, "453": 3.475, "454": 3.865, "481": 2.821, "483": 3.837, "484": 3.734, "487": 3.684, "512": 3.628, "521": 3.622, "525": 3.675, "529": 3.757}}
[S07_e] [critical] [scripted] {"uniprot_residues": [248, 253, 256, 269, 270, 271, 285, 286, 289, 290, 293, 298, 299, 313, 315, 317, 318, 321, 359, 361, 370, 379, 380, 381, 382], "pdb_residues": [267, 272, 275, 288, 289, 290, 304, 305, 308, 309, 312, 317, 318, 332, 334, 336, 337, 340, 378, 380, 389, 398, 399, 400, 401], "min_distances": {"267": 3.707, "272": 3.546, "275": 3.81, "288": 3.293, "289": 3.982, "290": 3.387, "304": 3.834, "305": 2.948, "308": 3.63, "309": 3.467, "312": 3.637, "317": 3.548, "318": 3.571, "332": 3.487, "334": 3.253, "336": 3.446, "337": 2.842, "340": 3.86, "378": 3.629, "380": 3.383, "389": 3.697, "398": 3.753, "399": 3.197, "400": 3.014, "401": 3.337}}
[S07_f] [critical] [scripted] 0
[S07_g] [critical] [scripted] {"sifts_label_to_uniprot": 20, "auth_T334_to_uniprot_T315": -19}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Ligands in 5MO4

| PDB component | Ligand | Location in entry | Binding site |
|---|---|---|---|
| **NIL** | **Nilotinib** | Chain A, residue 601 | ATP/catalytic pocket |
| **AY7** | **Asciminib (ABL001)** | Chain A, residue 602 | Allosteric myristoyl pocket |

## Residues within 4.0 Å

Contacts were calculated directly from the deposited 5MO4 coordinates using the minimum **heavy-atom distance ≤4.0 Å** to chain-A ABL1. Waters and ions were excluded, and one conformer was retained where alternate locations occurred.

### Nilotinib — NIL A601

**PDB author numbering:**

> LEU267, TYR272, VAL275, ALA288, VAL289, LYS290, LYS304, GLU305, VAL308, MET309, ILE312, LEU317, VAL318, ILE332, ILE334, PHE336, MET337, GLY340, PHE378, HIS380, LEU389, VAL398, ALA399, ASP400, PHE401

**Corresponding UniProt P00519 numbering:**

> LEU248, TYR253, VAL256, ALA269, VAL270, LYS271, LYS285, GLU286, VAL289, MET290, ILE293, LEU298, VAL299, ILE313, **THR315**, PHE317, MET318, GLY321, PHE359, HIS361, LEU370, VAL379, ALA380, ASP381, PHE382

The closest contacts include PDB **MET337**—the hinge residue **Met318** in canonical ABL1—and PDB **ILE334**, which occupies **P00519 position 315**. The latter is the engineered **T315I gatekeeper mutation**, so the deposited residue is isoleucine even though UniProt P00519 encodes threonine.

### Asciminib — AY7 A602

**PDB author numbering:**

> ARG351, ALA356, LEU359, LEU360, ALA363, LEU448, ILE451, ALA452, THR453, TYR454, GLU481, CYS483, PRO484, VAL487, PHE512, ILE521, VAL525, LEU529

**Corresponding UniProt P00519 numbering:**

> ARG332, ALA337, LEU340, LEU341, ALA344, LEU429, ILE432, ALA433, THR434, TYR435, GLU462, CYS464, PRO465, VAL468, PHE493, ILE502, VAL506, LEU510

## Are the sites distinct?

**Yes.** The two ligands occupy spatially distinct pockets:

- **Nilotinib** occupies the conventional ATP/catalytic-binding pocket.
- **Asciminib** occupies the allosteric **myristoyl pocket**, binding away from the ATP site and stabilizing an inactive kinase conformation.

The geometry supports this strongly:

- No ABL1 residue is contacted by both ligands within 4 Å.
- The closest NIL–AY7 heavy-atom approach is **19.663 Å**.
- Their heavy-atom centroids are **27.782 Å** apart.

This agrees with the primary publication, which states that asciminib binds the ABL1 myristoyl pocket “in contrast to catalytic-site ABL1 kinase inhibitors” and explicitly contrasts it with nilotinib.

## PDB-to-UniProt numbering

The entry’s `DBREF` alignment is:

> **PDB A46–534 → UniProt P00519 A27–515**

Therefore, for ABL1 residues aligned in this construct:

\[
\boxed{\text{P00519 number}=\text{PDB author number}-19}
\]

Important qualifications:

- PDB residues **40–45** are a six-residue expression tag and have **no P00519 counterpart**.
- **PDB ILE334 = P00519 THR315**: engineered **T315I**.
- **PDB ASN382 = P00519 ASP363**: engineered **D363N**; this residue is not in either 4 Å contact list.
- The offset applies to the ABL1 portion, not the expression tag or the heteroligand residue numbers 601/602.

The deposited PDB `SITE` records are smaller curated/software-derived subsets; the lists above instead contain **all protein residues satisfying the requested 4.0 Å geometric cutoff**.

### Sources

- [RCSB PDB 5MO4](https://www.rcsb.org/structure/5MO4)
- [UniProt P00519](https://www.uniprot.org/uniprotkb/P00519/entry)
- Wylie et al., “The allosteric inhibitor ABL001 enables dual targeting of BCR-ABL1,” *Nature* 543:733–737 (2017), [DOI: 10.1038/nature21702](https://doi.org/10.1038/nature21702), PMID: [28329763](https://pubmed.ncbi.nlm.nih.gov/28329763/)
=== END RUN rrxhx5b3s3j ===

=== RUN r9tsq8bs87a ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result summary

- **Activator:** `MRK` in PDB **1V4S**, chain A; `GLC` is glucose and was excluded from activator-contact calculations. BioLiP annotates `MRK` as an allosteric activator and reports `Kd = 360 nM` and `EC50 = 67.11 nM`.
- **ClinVar retrieval:** 2,845 GCK records from the local ClinVar snapshot; duplicate rows were collapsed.
- **Contact filter:** **24 residues** are within 6 Å of `MRK`.
- **Matched variants:** **65 unique ClinVar alleles** at 21 of those residues:
  - 40 missense
  - 7 nonsense
  - 5 frameshift
  - 11 synonymous
  - 1 in-frame insertion
  - 1 in-frame deletion
- **AlphaMissense:** scores were available for all 40 missense alleles; the other 25 consequences have no AlphaMissense substitution score.
- No retrieved ClinVar allele mapped to contact residues **Thr65** or **His218**.

### Numbering validation

PDB chain A contains two non-UniProt N-terminal residues at author positions 14–15. Author residues **16–461 map exactly to P35557 residues 16–461** with 100% sequence identity, so PDB and UniProt numbers are identical for every contact residue below.

## Interpretation key

- **Likely direct:** ligand-facing side chain plus pathogenicity/clinical support; strongest candidates for a direct MRK-binding effect.
- **Plausible direct:** ligand-facing side chain, but AlphaMissense/ClinVar evidence is weak or discordant.
- **Pocket/indirect:** contact is mainly through backbone geometry or lies at the 5.5–6 Å edge; a pocket or allosteric effect is plausible, but binding-specific disruption is less certain.
- **Structure disruption:** truncation/frameshift will likely alter protein abundance or folding and therefore observed MRK binding, but not necessarily affinity specifically.
- **Unlikely binding-specific:** synonymous coding change with no direct structural basis for an MRK-binding effect.

## Missense variants with AlphaMissense scores

All cDNA changes are on `NM_000162.5`.

| Protein change | cDNA | PDB/UniProt | MRK distance (Å) | AlphaMissense | ClinVar significance | Interpretation |
|---|---:|---:|---:|---:|---|---|
| p.Tyr61Asn | c.181T>A | 61/61 | 3.25 | 0.8868, pathogenic | Uncertain significance | Pocket/indirect |
| p.Val62Met | c.184G>A | 62/62 | 3.62 | 0.9462, pathogenic | Pathogenic | **Likely direct** |
| p.Val62Ala | c.185T>C | 62/62 | 3.62 | 0.9731, pathogenic | Pathogenic | **Likely direct** |
| p.Arg63Cys | c.187C>T | 63/63 | 2.73 | 0.1234, benign | Uncertain significance/Uncertain risk allele | Plausible direct |
| p.Arg63Leu | c.188G>T | 63/63 | 2.73 | 0.3254, benign | Uncertain significance | Plausible direct |
| p.Arg63His | c.188G>A | 63/63 | 2.73 | 0.1886, benign | Uncertain significance | Plausible direct |
| p.Ile159Met | c.477C>G | 159/159 | 4.33 | 0.2207, benign | Conflicting classifications | Plausible direct |
| p.Ile159Val | c.475A>G | 159/159 | 4.33 | 0.1611, benign | Pathogenic/Likely pathogenic | **Likely direct, but AM/ClinVar discordant** |
| p.Ile159Thr | c.476T>C | 159/159 | 4.33 | 0.5886, pathogenic | Uncertain significance | **Likely direct** |
| p.Ile159Asn | c.476T>A | 159/159 | 4.33 | 0.9313, pathogenic | Conflicting classifications | **Likely direct** |
| p.Met210Lys | c.629T>A | 210/210 | 3.66 | 0.9915, pathogenic | Pathogenic | **Likely direct** |
| p.Met210Ile | c.630G>T | 210/210 | 3.66 | 0.9915, pathogenic | Pathogenic | **Likely direct** |
| p.Met210Thr | c.629T>C | 210/210 | 3.66 | 0.9821, pathogenic | Pathogenic | **Likely direct** |
| p.Met210Val | c.627_628delinsAG | 210/210 | 3.66 | 0.8229, pathogenic | Likely pathogenic | **Likely direct** |
| p.Met210Val | c.628A>G | 210/210 | 3.66 | 0.8229, pathogenic | Likely pathogenic | **Likely direct** |
| p.Met210Ile | c.630G>A | 210/210 | 3.66 | 0.9915, pathogenic | Pathogenic | **Likely direct** |
| p.Ile211Asn | c.632T>A | 211/211 | 3.59 | 0.9683, pathogenic | Uncertain significance/Uncertain risk allele | **Likely direct** |
| p.Ile211Thr | c.632T>C | 211/211 | 3.59 | 0.9474, pathogenic | Pathogenic | **Likely direct** |
| p.Tyr214Cys | c.641A>G | 214/214 | 3.01 | 0.2600, benign | Pathogenic | **Likely direct, but AM/ClinVar discordant** |
| p.Cys220Arg | c.658T>C | 220/220 | 3.30 | 0.9953, pathogenic | Likely pathogenic | Pocket/indirect |
| p.Cys220Tyr | c.659G>A | 220/220 | 3.30 | 0.9972, pathogenic | Pathogenic | Pocket/indirect |
| p.Cys220Phe | c.659G>T | 220/220 | 3.30 | 0.9899, pathogenic | Uncertain significance | Pocket/indirect |
| p.Cys220Trp | c.660C>G | 220/220 | 3.30 | 0.9982, pathogenic | Uncertain significance | Pocket/indirect |
| p.Cys220Ser | c.658T>A | 220/220 | 3.30 | 0.9574, pathogenic | Uncertain significance | Pocket/indirect |
| p.Glu221Lys | c.661G>A | 221/221 | 4.24 | 0.7102, pathogenic | Pathogenic | **Likely direct** |
| p.Met235Thr | c.704T>C | 235/235 | 3.51 | 0.9520, pathogenic | Pathogenic | **Likely direct** |
| p.Met235Val | c.703A>G | 235/235 | 3.51 | 0.5248, ambiguous | Pathogenic | **Likely direct, moderate support** |
| p.Met235Arg | c.704T>G | 235/235 | 3.51 | 0.9183, pathogenic | Likely pathogenic | **Likely direct** |
| p.Arg250Cys | c.748C>T | 250/250 | 4.59 | 0.3665, ambiguous | Pathogenic | Pocket/indirect |
| p.Arg250His | c.749G>A | 250/250 | 4.59 | 0.2145, benign | Likely pathogenic | Pocket/indirect |
| p.Arg250Pro | c.749G>C | 250/250 | 4.59 | 0.9134, pathogenic | Uncertain significance | Pocket/indirect |
| p.Cys252Phe | c.755G>T | 252/252 | 5.72 | 0.9600, pathogenic | Conflicting classifications | Pocket/indirect |
| p.Cys252Trp | c.756C>G | 252/252 | 5.72 | 0.9967, pathogenic | Uncertain significance | Pocket/indirect |
| p.Val452Leu | c.1354G>C | 452/452 | 3.62 | 0.6364, pathogenic | Likely pathogenic | **Likely direct** |
| p.Ser453Leu | c.1358C>T | 453/453 | 5.64 | 0.7575, pathogenic | Pathogenic/Likely pathogenic | Pocket/indirect |
| p.Ser453Trp | c.1358C>G | 453/453 | 5.64 | 0.9903, pathogenic | Pathogenic/Likely pathogenic | Pocket/indirect |
| p.Val455Met | c.1363G>A | 455/455 | 3.46 | 0.5295, ambiguous | Pathogenic | **Likely direct, moderate support** |
| p.Val455Glu | c.1364T>A | 455/455 | 3.46 | 0.8513, pathogenic | Likely pathogenic | **Likely direct** |
| p.Ala456Val | c.1367C>T | 456/456 | 4.04 | 0.3825, ambiguous | Pathogenic | **Likely direct, but AM/ClinVar discordant** |
| p.Ala456Pro | c.1366G>C | 456/456 | 4.04 | 0.9733, pathogenic | Uncertain significance | **Likely direct** |

## Other ClinVar consequences

AlphaMissense is **N/A** for these consequences because it scores amino-acid substitutions.

| Protein change | cDNA | PDB/UniProt | MRK distance (Å) | ClinVar significance | Interpretation |
|---|---:|---:|---:|---|---|
| p.Tyr61Ter | c.183C>A | 61/61 | 3.25 | Pathogenic | Structure disruption |
| p.Tyr61= | c.183C>T | 61/61 | 3.25 | Benign/Likely benign | Unlikely binding-specific |
| p.Ser64= | c.192C>T | 64/64 | 3.64 | Likely benign | Unlikely binding-specific |
| p.Ser64fs | c.190dup | 64/64 | 3.64 | Likely pathogenic | Structure disruption |
| p.Pro66= | c.198A>G | 66/66 | 3.77 | Benign/Likely benign | Unlikely binding-specific |
| p.Gln98fs | c.291del | 98/98 | 4.47 | Pathogenic/Likely pathogenic | Structure disruption |
| p.Gln98Ter | c.292C>T | 98/98 | 4.47 | Pathogenic | Structure disruption |
| p.Ile159= | c.477C>A | 159/159 | 4.33 | Likely benign | Unlikely binding-specific |
| p.Met210_Ile211insMet | c.627GAT[3] | 210/210 | 3.66 | Conflicting classifications | **Likely direct pocket disruption** |
| p.Tyr214Ter | c.641dup | 214/214 | 3.01 | Pathogenic/Likely pathogenic | Structure disruption |
| p.Tyr215Ter | c.645C>G | 215/215 | 2.45 | Pathogenic | Structure disruption |
| p.Tyr215= | c.645C>T | 215/215 | 2.45 | Benign/Likely benign | Unlikely binding-specific |
| p.Tyr215Ter | c.645C>A | 215/215 | 2.45 | Pathogenic/Likely pathogenic | Structure disruption |
| p.Cys220= | c.660C>T | 220/220 | 3.30 | Benign/Likely benign | Unlikely binding-specific |
| p.Cys220Ter | c.660C>A | 220/220 | 3.30 | Pathogenic | Structure disruption |
| p.Val222= | c.666C>T | 222/222 | 5.86 | Conflicting classifications | Unlikely binding-specific |
| p.Val222= | c.666C>A | 222/222 | 5.86 | Uncertain significance | Unlikely binding-specific |
| p.Arg250= | c.750C>G | 250/250 | 4.59 | Likely benign | Unlikely binding-specific |
| p.Cys252= | c.756C>T | 252/252 | 5.72 | Likely benign | Unlikely binding-specific |
| p.Leu451_Ala454del | c.1350_1361del | 451/451 | 4.11 | Uncertain significance | Possible pocket disruption |
| p.Leu451fs | c.1351del | 451/451 | 4.11 | Likely pathogenic | Structure disruption |
| p.Ser453= | c.1359G>T | 453/453 | 5.64 | Likely benign | Unlikely binding-specific |
| p.Ser453fs | c.1358_*127delinsT | 453/453 | 5.64 | Likely pathogenic | Structure disruption |
| p.Ser453Ter | c.1358C>A | 453/453 | 5.64 | Likely pathogenic | Structure disruption |
| p.Val455fs | c.1363dup | 455/455 | 3.46 | Likely pathogenic | Structure disruption |

## Which are most likely to alter MRK binding?

### Strongest direct-interface candidates

These combine a ligand-facing side chain with high AlphaMissense and/or pathogenic ClinVar evidence:

- **p.Val62Met, p.Val62Ala**
- **p.Met210Lys, p.Met210Ile** (both alleles), **p.Met210Thr, p.Met210Val** (both alleles)
- **p.Ile211Thr**
- **p.Glu221Lys**
- **p.Met235Thr, p.Met235Arg**
- **p.Val455Glu**
- Also high-priority but with less definitive clinical classification: **p.Ile159Asn, p.Ile159Thr, p.Ile211Asn, p.Ala456Pro**

### Direct geometry, but weaker or discordant evidence

- **p.Arg63Cys, p.Arg63Leu, p.Arg63His** are the closest substitutions to MRK, but all have low/benign AlphaMissense scores and uncertain ClinVar classifications.
- **p.Ile159Met** also contacts the ligand side chain but has a low AM score.
- **p.Ile159Val, p.Tyr214Cys, p.Ala456Val** occupy direct-interface positions and have pathogenic ClinVar classifications, but their AlphaMissense scores are discordantly low/ambiguous.
- **p.Met235Val, p.Val455Met, p.Val452Leu** are direct-interface candidates with intermediate AM support.

### Likely to affect MRK binding indirectly

- **p.Met210_Ile211insMet** is particularly noteworthy because it lies in the core MRK site and is an in-frame insertion.
- Nonsense and frameshift variants at Tyr61, Ser64, Gln98, Tyr214, Tyr215, Cys220, Leu451, Ser453, and Val455 will likely alter folding, abundance, or pocket geometry and therefore change measured MRK binding, but these are not clean binding-specific substitutions.
- Cys220, Arg250, Cys252, and Ser453 substitutions are closer to backbone-mediated or edge contacts; they are plausible pocket/allostery effects rather than confirmed affinity determinants.

## Important limitation

A ≤6 Å contact is geometric proximity, not proof that a substitution changes affinity. Likewise, AlphaMissense predicts general pathogenicity rather than MRK-specific binding. Definitive assignment would require MRK binding or enzymatic-response measurements. The analysis also uses one static, activator-bound conformation.

### Completed plan

1. [✓] Retrieve GCK ClinVar variants and inspect ligand/protein annotations for 1V4S.
2. [✗] Initial exact-mapping attempt failed because the alignment-derived UniProt identities did not match PDB residue names.
3. [✗] Modified alignment-based attempt failed the residue-identity sanity check and was discarded.
4. [✓] Diagnose and validate the authoritative mapping: PDB 16–461 ↔ P35557 16–461.
5. [✓] Recompute the validated ≤6 Å MRK/ClinVar intersection.
6. [✓] Retrieve AlphaMissense scores for all 24 contact positions.
7. [✓] Refine side-chain/pocket evidence and finalize the binding-effect prioritization.

Machine-readable results were saved under `/agent_cwd/GCK_1V4S_analysis/`, especially `final_annotated_MRK_6A_ClinVar_AlphaMissense.csv` and the corresponding JSON file.
=== END RUN r9tsq8bs87a ===

=== RUN r971joahjsz ===
QUESTION:
Using only pocket-detection output on PTP1B (PDB 1T4J, ligands removed), rank the top three pockets by how likely each is to be an allosteric site, and justify the ranking.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H02_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[H02_c] [critical] [judged] a ranking of the top three pockets by allosteric likelihood with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Relative allosteric-pocket ranking

| Rank | Pocket | Representative residues, chain A | Pocket-only evidence | Assessment |
|---|---|---|---|---|
| **1** | **fpocket pocket 3** | LYS73, MET74, GLU75, GLN78, ARG79, SER80, LEU204, SER205, PRO206, HIS208, GLY209, PRO210, VAL211, GLU252, PHE256 | Large, chemically balanced cavity: **629.98 Å³**, 62 alpha spheres, total SASA **212.59 Å²**, hydrophobicity **9.60**, polarity **8**, charge **+1**, mean solvent accessibility **0.485**. Its mean PocketMiner cryptic-pocket score was **0.562**, versus a protein-wide mean of **0.468**, with **10/15 residues** above that mean. | **Most promising overall.** It combines strong fpocket ranking, substantial volume, mixed polar/apolar character, and elevated cryptic-pocket propensity. Its principal weakness is that P2Rank did not detect it. |
| **2** | **fpocket pocket 11** | GLU186, SER187, PRO188, ALA189, LEU192, ASN193, PHE196, LEU272, GLU276, GLY277, PHE280, ILE281 | **Largest pocket among the leading candidates** at **642.77 Å³**, with the most alpha spheres (**79**) and by far the highest fpocket druggability score (**0.820**). It is relatively enclosed—mean alpha-sphere accessibility **0.446**—and hydrophobicity is high (**32.75**). | **Strong cryptic ligand-binding candidate.** Its drug-likeness and enclosure support an allosteric pocket capable of admitting a modulator. It ranks below pocket 3 because its fpocket score is lower (**0.069**), its cryptic-pocket signal is not elevated (**mean 0.451**), and P2Rank did not corroborate it. |
| **3** | **fpocket pocket 8** | MET1, GLU2, MET3, GLU4, LEU232, MET235, ASP236, ASP240, PRO241, SER242, VAL244, ALA278, LYS279, ILE281, MET282 | Large, lipophilic cavity: **637.83 Å³**, 63 alpha spheres, SASA **196.42 Å²**, fpocket score **0.123**, druggability **0.069**—second only to pocket 11 among these candidates—and hydrophobicity **24.20**. | **Credible but lower-confidence candidate.** Its size and druggability are favorable, but PocketMiner support is weak (**mean 0.440**) and P2Rank did not detect it. It also overlaps spatially with pocket 11: minimum atom separation **1.52 Å**, with **16.3%** of pocket-8 atoms within 4 Å of pocket 11. Thus these may be neighboring subdivisions of one broader cavity rather than fully independent sites. |

## How the ordering was obtained

- The ligand-free file was analyzed with **fpocket 4.2.3** and **P2Rank 2.5.1**.
- The dominant **CYS215-containing cluster—fpocket pocket 2/P2Rank pocket 1—was excluded** as the catalytic/orthosteric pocket. It had 10 shared residues between the two detectors.
- For the remaining pockets, I percentile-normalized and combined:
  - fpocket score: **20%**
  - fpocket druggability: **20%**
  - pocket volume: **15%**
  - enclosure/solvent accessibility: **15%**
  - P2Rank residue-overlap consensus: **15%**
  - PocketMiner cryptic-pocket propensity: **15%**
- Pocket 3 ranked first under all four reasonable weighting schemes tested; pockets 11 and 8 each appeared in the top three under three of the four schemes.

## Important limitations

1. These are **comparative allosteric-plausibility rankings, not allosteric probabilities**. Pocket detection measures cavities, not catalytic coupling.
2. P2Rank returned only three pockets here and did not corroborate any of the three leaders, which lowers confidence and suggests limited detector recall.
3. Pockets 8 and 11 are physically adjacent and should not necessarily be interpreted as independent biological sites.
4. Ligand removal prevents ligand-shape bias, but it also means these are apo-state cavities; conformational opening and experimental validation would still be required.

**Final order:** **fpocket 3 > fpocket 11 > fpocket 8**, with the qualification that pockets 11 and 8 may represent neighboring parts of the same broad allosteric region.
=== END RUN r971joahjsz ===

=== RUN rkseuoe92dn ===
QUESTION:
For PTP1B in PDB entry 1T4J chain A, how many of the residues STINGAllo predicts are among the residues within 4 angstroms of the bound allosteric ligand? Report both lists and the overlap.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K02_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]
[K02_c] [critical] [scripted] 10

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Completed plan
1. [✓] Retrieved PDB 1T4J metadata and coordinates; identified the chain A allosteric ligand as **FRJ 299**
2. [✓] Obtained the official STINGAllo prediction for PDB 1T4J, chain A
3. [✓] Calculated chain A protein residues within 4 Å of FRJ using minimum heavy-atom distances
4. [✓] Cross-validated residue numbering and intersected the two lists

### Results

**STINGAllo-predicted residues — 14 total:**  
GLU129, GLU130, SER187, PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, ILE281, MET282

**Residues within 4 Å of bound ligand FRJ — 11 total:**  
PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, GLY277, LYS279, PHE280, MET282

**Overlap — 10 residues:**  
PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, MET282

### Answer

**10 of the 14 STINGAllo-predicted residues are within 4 Å of the bound allosteric ligand.** This is 71.4% of the STINGAllo predictions and 90.9% of the 4 Å ligand-contact residues.

The predicted-only residues are GLU129, GLU130, SER187, and ILE281; the contact-only residue is GLY277.

**Method:** The official STINGAllo REST API was queried with `pdb_id=1T4J` and `chain_id=A`. Distances were calculated between all 41 heavy atoms of ligand FRJ 299 and all chain A protein-residue heavy atoms, using the deposited PDB author numbering.

**Sources:** [RCSB PDB 1T4J](https://www.rcsb.org/structure/1T4J); [STINGAllo](https://www.stingallo.cbi.cnptia.embrapa.br/)
=== END RUN rkseuoe92dn ===

=== RUN rzlesmksycf ===
QUESTION:
For SHP2 in PDB entry 5EHR chain A, compare the residues STINGAllo predicts with those within 4 angstroms of SHP099. Report both lists and the overlap, and say whether the prediction recovers the tunnel site.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[K03_b] [critical] [scripted] ["314"]
[K03_c] [critical] [scripted] 0
[K03_d] [critical] [scripted] {"predicted_residues": 1, "predicted_residue_numbers": [314], "contact_residues": 15, "modelled_chain_A_residues": 485, "predicted_fraction_of_chain": 0.002061855670103093, "expected_overlap_by_chance": 0.030927835051546393, "observed_overlap": 0, "enrichment": 0.0}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Comparison for SHP2–SHP099, PDB **5EHR**, chain **A**

The deposited ligand **5OD A601** is **SHP099**.

### STINGAllo-predicted residues

Live STINGAllo API response:

- **PHE314**
- Residue-number list: **[314]**

### Chain-A residues within 4.0 Å of SHP099

Using minimum heavy-atom distance to any SHP099 atom:

- **THR108, GLU110, ARG111, PHE113, HIS114**
- **THR218, THR219**
- **GLU249, GLU250, THR253, LEU254, GLN257**
- **PRO491, LYS492, GLN495**

Residue-number list:

**[108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495]**

### Overlap

**None (∅).**

### Conclusion

**No—the STINGAllo prediction does not recover the SHP099 tunnel site for 5EHR chain A.** Its only predicted residue, **PHE314**, is approximately **11.57 Å** from the nearest SHP099 atom and is therefore outside the 4 Å ligand-contact region.

### Sources

- [STINGAllo API result for 5EHR chain A](https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=5EHR&chain_id=A)
- [RCSB PDB entry 5EHR](https://www.rcsb.org/structure/5EHR)
- STINGAllo paper: Omage et al., *Briefings in Bioinformatics* (2025), [doi:10.1093/bib/bbaf424](https://doi.org/10.1093/bib/bbaf424)
- Original SHP099/SHP2 structure paper: Chen et al., *Nature* (2016), [doi:10.1038/nature18621](https://doi.org/10.1038/nature18621)
=== END RUN rzlesmksycf ===

=== RUN rbc93ddhe5m ===
QUESTION:
For ABL1 (UniProt P00519), report ClinVar classification and AlphaMissense score for T315I, and its distance from the ATP-site ligand and from the myristoyl-site ligand in PDB entry 1OPK. What do the distances suggest about which site the variant affects?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V04_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[V04_b] [critical] [scripted] {"clinical_significance": "Likely pathogenic; association", "variation_id": "27663"}
[V04_c] [critical] [scripted] 0.9991
[V04_d] [critical] [judged] the distances from T315I to the ATP-site ligand (P16) and to the myristoyl-site ligand (MYR) in 1OPK are reported, with a hedged inference

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Results for ABL1 T315I (UniProt P00519)

| Evidence | Result |
|---|---|
| **ClinVar** | **Likely pathogenic; association** for ABL1 p.Thr315Ile / c.944C>T (ClinVar Variation ID **27663**); review status: “criteria provided, multiple submitters, no conflicts” |
| **AlphaMissense** | **0.9991**, classified **pathogenic** |
| **ATP-site ligand P16** | **3.24 Å** minimum heavy-atom distance |
| **Myristoyl-site ligand MYR (myristic acid)** | **25.59 Å** minimum heavy-atom distance |

### Structural details

PDB **1OPK** contains mouse ABL1 (**P00520**), but residues 305–325 are identical to human P00519, including Thr315. Human T315 corresponds to **PDB chain A, author residue THR334**; PDB author residue 315 itself is proline.

The distances are minimum heavy-atom distances in the deposited 1OPK coordinates:

- **T315 OG1–P16 C16: 3.239 Å**
- **T315 OG1–MYR C14: 25.595 Å**

P16 is the ATP-site inhibitor, whereas MYR is myristic acid at the N-terminal myristoyl pocket.

### Interpretation

T315 is directly adjacent to the **ATP-site ligand**, while it is spatially remote from the myristoyl-site ligand. Thus, the structure supports the variant primarily affecting the **ATP-binding/ATP-competitive-inhibitor site**, rather than the N-terminal myristoyl pocket. This is consistent with T315 being the ABL1 gatekeeper residue; T315I can alter ATP-pocket geometry and impair binding of ATP-competitive inhibitors. These distances describe the wild-type threonine in 1OPK rather than directly modeling the mutant isoleucine.

### Completed plan

1. [✓] Complete ClinVar and AlphaMissense annotation for ABL1 T315I  
2. [✗] Initial structure retrieval failed because Biopython `Model` has no `serial` attribute  
3. [✓] Modified Step 2: retrieve and verify 1OPK ligands, species, and residue mapping using `model.id`  
4. [✗] Initial distance calculation targeted PDB author residue 315 (PRO), not canonical ABL1 T315  
5. [✓] Modified Step 4: verify the RCSB/SIFTS mapping, confirm human–mouse T315 equivalence, and calculate distances to PDB THR334  
6. [✓] Integrate the variant classifications and structural distances to assess site specificity
=== END RUN rbc93ddhe5m ===

=== RUN ry6alrfohae ===
QUESTION:
For PTP1B in PDB entry 1T4J chain A, how many of the residues STINGAllo predicts are among the residues within 4 angstroms of the bound allosteric ligand? Report both lists and the overlap.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K02_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]
[K02_c] [critical] [scripted] 10

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**10 of the 14 STINGAllo-predicted residues** are within **4 Å of FRJ**, the bound allosteric ligand in PTP1B PDB **1T4J chain A**.

### STINGAllo residues (14)
A129, A130, A187, A188, A189, A192, A193, A196, A200, A276, A279, A280, A281, A282

### FRJ-contacting residues within 4 Å (11)
A188 (Pro188), A189 (Ala189), A192 (Leu192), A193 (Asn193), A196 (Phe196), A200 (Glu200), A276 (Glu276), A277 (Gly277), A279 (Lys279), A280 (Phe280), A282 (Met282)

### Overlap (10)
A188, A189, A192, A193, A196, A200, A276, A279, A280, A282

- STINGAllo-only: A129, A130, A187, A281
- FRJ-contact-only: A277

**Overlap count: 10**

*Technical note: the live STINGAllo API returned its predictions under `allosteric_residues`, whereas the Biomni wrapper expected `residues`; the official raw response was therefore used to recover the prediction list.*

### Progress checklist
1. [✓] Retrieve chain-A ligand records (FRJ)
2. [✓] Obtain FRJ polymer-residue contacts within 4 Å of chain A
3. [✗] Retrieve predictions through the wrapper directly (wrapper schema mismatch)
4. [✓] Recover the authoritative chain-A STINGAllo predictions from the official response
5. [✓] Intersect and report the lists
=== END RUN ry6alrfohae ===

=== RUN rh4oi0abc7e ===
QUESTION:
Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C02_b] [critical] [judged] the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PTP1B (P18031) residue contact network — 1T4J chain A

### Structure / ligand identification
| Item | Value |
|---|---|
| PDB | **1T4J**, chain A (X-ray, **2.7 Å**), residues modeled 1–282 of a 1–298 construct (283–298 disordered/unmodeled) |
| Title | *Allosteric Inhibition of Protein Tyrosine Phosphatase 1B* — Wiesmann C. *et al.*, **Nat Struct Mol Biol 2004**, DOI 10.1038/nsmb803 |
| Allosteric ligand | **FRJ** (1 copy, 41 heavy atoms) = 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethyl-benzofuran-6-sulfonic acid [4-(thiazol-2-ylsulfamoyl)-phenyl]-amide; BindingDB IC₅₀ 2–8 µM |
| Catalytic residue | **Cys215** (C–N distances to His214/Arg221 as expected for the P-loop; UniProt P18031 numbering = PDB numbering here) |

### Method
Nodes = 282 chain-A residues; edge = two residues in contact if their **minimum heavy-atom distance ≤ cutoff**; one HETATM excluded (FRJ kept only as the ligand probe). Ligand proximity = min heavy-atom distance from each residue to FRJ. Shortest path = minimum number of edges (hops), found by BFS and independently cross-checked with `scipy.sparse.csgraph.shortest_path` on an unweighted graph.

### Result
**Closest residue to the allosteric ligand: Glu276** — OE1···N16(FRJ) = **2.55 Å** (next: Phe280 backbone O 2.65 Å, Asn193 3.01 Å, Lys279 3.03 Å).

**Shortest path (cutoff 4.5 Å):**
**Cys215 → Leu110 → Phe191 → Pro188 → Glu276**

**Path length = 4 edges (5 residues)**; summed inter-residue contact distances = 15.23 Å

| Edge | min heavy-atom distance |
|---|---|
| Cys215 – Leu110 | 4.41 Å (CB–CB) |
| Leu110 – Phe191 | 3.84 Å (CD2–CE1) |
| Phe191 – Pro188 | 3.16 Å (O–N) |
| Pro188 – Glu276 | 3.82 Å (CG–CG) |

### Cutoff used
**4.5 Å** (minimum heavy-atom distance between residues) — the standard residue-contact-network threshold. The 4.5 Å network is a **single connected component containing all 282 residues** (no isolated residues).

### Robustness / degeneracy
* **Cutoff sensitivity:** 4.0 Å → 5 edges (e.g. Cys215–Asn111–Leu110–Phe191–Pro188–Glu276); **4.5 Å and 5.0 Å → 4 edges (same answer)**; 5.5–6.0 Å → still 4 edges but rerouted (Cys215–Val108–Phe194–Leu192–Glu276).
* **Covalent-neighbor convention:** identical result whether peptide-bonded sequential neighbors are included or excluded (the reported path contains no covalent pair).
* **Degeneracy:** 5 distinct 4-edge minimal paths exist at 4.5 Å: (A) Cys215–Leu110–Phe191–Pro188–Glu276; (B) …Phe191–Leu192–Glu276; (C) Cys215–Leu110–Phe194–**Leu192**–Glu276; (D/E) via the catalytic **Arg221**. Path A is reported because it is entirely non-covalent; paths B/C/E pass through **Leu192**, the literature-established α3-helix allosteric residue shown to lock the WPD loop in the open conformation.
* **Alternative endpoint:** if "closest residue" is defined by CA/CB-to-ligand-centroid instead of minimum any-atom distance, the target becomes **Phe280** and the path is 5 edges: Cys215–Leu110–Phe191–Pro188–Glu276–Phe280 (Glu276 is still on it).
* **Distance context:** FRJ lies **20.3 Å** from Cys215 (closest atom pair O12/CB; centroid–centroid 24.6 Å), consistent with the allosteric site being remote from the active site — hence a multi-residue coupling path is required.

### Artifacts saved (working dir `/tmp/agent_cwd/C02_r1_1`)
`PTP1B_1T4J_contact_network_path.png` (3D path + FRJ contact shell + edge-distance plot), `network_int.pkl` (residue-pair distance matrix), `1T4J_entry_metadata.json`, `chemcomp_FRJ.json`, `primary_citation.json`, `closest_defs.pkl`, `uniprot_P18031.json`.
=== END RUN rh4oi0abc7e ===

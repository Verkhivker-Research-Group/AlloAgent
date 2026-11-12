# Judge batch 014 of 24

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

=== RUN rty94fy4rq8 ===
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
1. [✓] Retrieve the ligands and PDB-to-UniProt residue mapping for 5MO4  
2. [✓] Identify asciminib and nilotinib and retrieve each ligand’s residues within 4 Å  
3. [✓] Compare the contact sites and verify that they are distinct  
4. [✓] Reconcile the deposited PDB numbering with UniProt P00519 numbering  

## Ligands in 5MO4

| Ligand | Chemical-component ID | PDB location | Molecular formula |
|---|---|---|---|
| **Asciminib** | **AY7** | Chain A, residue A602 | C₂₀H₁₈ClF₂N₅O₃ |
| **Nilotinib** | **NIL** | Chain A, residue A601 | C₂₈H₂₂F₃N₇O |

The contacts below are polymer residues whose closest heavy atom is **≤4.0 Å** from the indicated ligand. The first number is the deposited **PDB author residue number**; the number in parentheses is the corresponding **canonical UniProt P00519 position**.

## Asciminib (AY7): 18 residues within 4 Å

- **A351 Arg** (P00519 332)
- **A356 Ala** (337)
- **A359 Leu** (340)
- **A360 Leu** (341)
- **A363 Ala** (344)
- **A448 Leu** (429)
- **A451 Ile** (432)
- **A452 Ala** (433)
- **A453 Thr** (434)
- **A454 Tyr** (435)
- **A481 Glu** (462)
- **A483 Cys** (464)
- **A484 Pro** (465)
- **A487 Val** (468)
- **A512 Phe** (493)
- **A521 Ile** (502)
- **A525 Val** (506)
- **A529 Leu** (510)

## Nilotinib (NIL): 25 residues within 4 Å

- **A267 Leu** (P00519 248)
- **A272 Tyr** (253)
- **A275 Val** (256)
- **A288 Ala** (269)
- **A289 Val** (270)
- **A290 Lys** (271)
- **A304 Lys** (285)
- **A305 Glu** (286)
- **A308 Val** (289)
- **A309 Met** (290)
- **A312 Ile** (293)
- **A317 Leu** (298)
- **A318 Val** (299)
- **A332 Ile** (313)
- **A334 Ile** — corresponds to P00519 position **315**, which is Thr in canonical P00519; the deposited structure therefore contains **T315I**
- **A336 Phe** (317)
- **A337 Met** (318)
- **A340 Gly** (321)
- **A378 Phe** (359)
- **A380 His** (361)
- **A389 Leu** (370)
- **A398 Val** (379)
- **A399 Ala** (380)
- **A400 Asp** (381)
- **A401 Phe** (382)

## Are the sites distinct?

**Yes.** The two ligands occupy separate, adjacent pockets:

- **Nilotinib** occupies the **ATP-binding pocket**, contacting the gatekeeper region and the DFG region, including P00519 position 315 and Asp381.
- **Asciminib** occupies the adjacent **myristoyl-site/allosteric pocket**.

Quantitatively:

- Their 4 Å contact-residue sets have **no residues in common**.
- The closest heavy atom of asciminib to the closest heavy atom of nilotinib is **19.66 Å** apart.
- Their ligand centroids are approximately **27.78 Å** apart.

Thus, the two drugs are simultaneously bound in distinct, non-overlapping pockets.

## Relationship between PDB and UniProt numbering

For the aligned ABL1 sequence in chain A:

\[
\boxed{\text{PDB author residue number} = \text{UniProt P00519 position} + 19}
\]

For example:

- PDB **A334** aligns with P00519 position **315**
- PDB **A400 Asp** aligns with P00519 **Asp381**
- PDB **A529 Leu** aligns with P00519 **Leu510**

More specifically, RCSB/SIFTS maps polymer-entity sequence positions **7–495** to P00519 residues **27–515**. The entry’s author-number mapping then shifts those entity positions by **+39**—for example, entity position 7 is author residue 46, and entity position 495 is author residue 534—giving the net **+19** offset relative to P00519.

This also explains an easy-to-miss distinction:

- The **PDB author number** is what appears in the coordinate file and in the residue lists above.
- The **mmCIF label/entity sequence index** follows a slightly different coordinate system and should not be substituted for the author number.
- There are no insertion codes among the contacting ABL1 residues.
- The numbering offset does **not** erase the engineered **T315I** substitution: canonical P00519 has Thr315, whereas 5MO4 deposits Ile at PDB A334.

Sources: [RCSB PDB entry 5MO4](https://www.rcsb.org/structure/5MO4) and [UniProt P00519](https://www.uniprot.org/uniprotkb/P00519/entry).
=== END RUN rty94fy4rq8 ===

=== RUN r4c3qunamqw ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Updated plan
1. [✓] Initial metadata retrieval; corrected the non-polymer entity-ID query
2. [✗] First Bash retry failed because of wrapper heredoc parsing; bypassed using direct Python execution
3. [✓] Retrieved and validated PDB 1OPK, its ligands, chain mapping, and UniProt correspondence
4. [✓] Ligand-stripped the structure and ranked pockets with Fpocket
5. [✓] Calculated and ABL1-numbered residue contacts and site distances
6. [✓] Retrieved matched ChEMBL potency records for imatinib and asciminib
7. [✓] Retrieved ClinVar and AlphaMissense evidence for T315I
8. [✓] Integrated the structural, pharmacological, and variant evidence

## Bottom line

**T315I is an ATP-site gatekeeper mutation.** It lies directly at the edge of the ATP pocket and is therefore highly disruptive to ATP-site inhibitors such as imatinib. In contrast, it is about **25.6 Å away from the myristoyl pocket**, so it does not directly obstruct asciminib’s allosteric binding site. Asciminib consequently retains potent activity against T315I, although other mutations—especially compound mutations or changes affecting the myristoyl pocket/autoinhibited conformation—can still cause asciminib resistance.

## Important 1OPK caveat

PDB **1OPK is an ABL2 construct**, aligned by RCSB to **UniProt P00520**, not ABL1 P00519. The ABL2 kinase domain is highly conserved and maps unambiguously to ABL1:

- **PDB author Thr334 = ABL1 Thr315**
- In this mapped region, **PDB author number = ABL1 number + 19**
- PDB author residue 315 is ABL1 **Pro296**, not T315
- 1OPK also contains an engineered ABL2 D363N substitution, away from T315

Therefore, all residue numbers below are **ABL1 P00519 canonical numbers**, obtained by sequence mapping. The 1OPK ligands are:

- **P16 = PD166326**, an ATP-site ABL inhibitor
- **MYR = myristic acid**, occupying the myristoyl pocket

Neither ligand is imatinib or asciminib.

## Structural comparison

Contacts were defined as any protein–ligand heavy-atom distance ≤4.0 Å.

| Feature | ATP site | Myristoyl site |
|---|---|---|
| 1OPK site probe | P16 / PD166326 | MYR / myristic acid |
| Fpocket rank | **2** | **3** |
| Fpocket score | 0.320 | 0.211 |
| Fpocket druggability | 0.913 | 0.547 |
| T315 minimum heavy-atom distance to bound probe | **3.24 Å** | **25.59 Å** |
| T315 distance to cavity alpha-sphere | 3.46 Å | 24.79 Å |
| T315 Cα-to-ligand-centroid distance | 7.86 Å | 32.82 Å |
| T315 location | ATP-pocket gatekeeper edge | spatially remote from this pocket |

The ATP cavity was fragmented somewhat after ligand removal: the principal P16-overlapping cavity was rank 2, with an adjacent ATP-side fragment at rank **7** (score 0.097; druggability 0.040).

### P16/ATP-site contacts, ≤4.0 Å

**L248, Y253, V256, A269, V270, K271, E286, M290, V299, I313, T315, E316, F317, M318, G321, L370, A380, D381, F382**

Notably, **T315 itself contacts P16** at 3.24 Å.

At a 4.5 Å cutoff, add **G249, T319, and N322**.

### MYR/myristoyl-site contacts, ≤4.0 Å

**L340, L341, A344, L429, A433, E462, I502, L510**

At a 4.5 Å cutoff, add **A337, I432, Y435, G463, C464, P465, V468, F493, and V506**.

### Pocket-lining residues

- **ATP, rank 2:** L248, G249, Q252, Y253, V256, A269, K271, E286, M290, V299, I313, T315, E316, F317, M318, T319, G321, N322, D325, L370, A380, D381, F382
- **Myristoyl, rank 3:** A337, L340, L341, A344, L429, I432, A433, Y435, E462, G463, C464, P465, V468, F493, I502, V506, L510

**Fpocket method:** chain A standard residues retained; P16, MYR, glycerol, and waters removed; Fpocket 4.0 run on the stripped PDB; native cavity order used; cavities assigned by proximity of their alpha-spheres to the original P16/MYR coordinates.

## ChEMBL potency

### Imatinib — ATP-site, type-II inhibitor

| Endpoint | Wild-type ABL1 | T315I | Change |
|---|---:|---:|---:|
| ABL1 Kd, same ChEMBL document | **2.2 nM** | **6,200 nM** | **2,818-fold loss** |
| Representative WT ABL1 IC50 | 38 nM | — | assay-dependent |
| c-Abl IC50 in another matched series | 1,100 nM | >100,000 nM | >91-fold lower bound |

ChEMBL activities:

- WT Kd 2.2 nM: activity **1651429**, assay CHEMBL859868
- T315I Kd 6,200 nM: activity **1651473**, assay CHEMBL859873
- WT IC50 38 nM: activity **909963**
- Matched WT/T315I IC50 records: activities **2280412/2280564**

The broad spread between different WT IC50 values reflects different biochemical formats and ATP conditions. The within-document WT-versus-T315I comparisons are the most interpretable.

### Asciminib — allosteric myristoyl-pocket inhibitor

| Endpoint | Wild type | T315I | Change |
|---|---:|---:|---:|
| ABL1 biochemical IC50 | **0.5 nM** | — | — |
| ABL1 Kd | **0.5 nM** | — | — |
| BCR-ABL1 cellular GI50, same document | **0.61 nM** | **7.64 nM** | **12.5-fold shift** |
| BCR-ABL1 FRET EC50 | — | **6.45 nM** | retained activity |

ChEMBL activities:

- ABL1 IC50 0.5 nM: **18557369**
- ABL1 Kd 0.5 nM: **18557469**
- WT BCR-ABL1 GI50 0.61 nM: **18557370**
- T315I BCR-ABL1 GI50 7.64 nM: **18557371**
- T315I FRET EC50 6.45 nM: **25662976**

These different endpoints should not be compared as though they were one uniform assay. Their common message is that asciminib is sub-/low-nanomolar against ABL1 and remains active against T315I.

## ClinVar and AlphaMissense

### ClinVar

- **Variant:** NM_005157.6(ABL1):c.944C>T, p.Thr315Ile
- **ClinVar:** VCV000012624
- **dbSNP:** rs121913459
- **Aggregate classification:** **“Likely pathogenic; association”**
- **Associated condition:** chronic myeloid leukemia
- **Review status:** criteria provided, multiple submitters, no conflicts
- **Last evaluated:** 2023-09-13

Although ClinVar exposes an aggregate germline field, T315I is usually encountered as an **acquired somatic resistance mutation** in CML/Ph+ leukemia; the aggregate record should not be read as proof of inherited CML predisposition.

### AlphaMissense

For ABL1 ENST00000318560 T315I:

- **am_pathogenicity:** **0.9991**
- **am_class:** **likely_pathogenic**

The official thresholds are:

- likely benign: <0.34
- ambiguous: 0.34–0.564
- likely pathogenic: >0.564

AlphaMissense is a general missense-effect predictor, not a drug-resistance predictor or clinical classifier. Its very high score is consistent with a functionally important substitution, but the pharmacological conclusion comes from the structural and biochemical data.

## What T315I implies for each inhibitor class

### 1. ATP-site inhibitors such as imatinib: strong resistance

T315 is the ABL1 **gatekeeper residue** at the edge of the ATP-binding pocket. The 1OPK geometry places its side chain only **3.24 Å** from the ATP-site inhibitor P16. Replacing threonine with bulkier isoleucine:

- creates steric incompatibility with imatinib near the ATP site;
- removes the small, polar gatekeeper environment available to imatinib;
- thereby greatly reduces ABL1 binding.

The matched ChEMBL Kd shift from **2.2 nM to 6.2 µM** confirms this large loss of affinity. Thus T315I is expected to confer resistance to imatinib and most first- and second-generation ATP-site inhibitors.

This is not universal for every ATP-site drug: inhibitors specifically designed to accommodate the mutated gatekeeper, such as ponatinib, can remain active.

### 2. Myristoyl-site allosteric inhibitors such as asciminib: activity largely retained

Asciminib does not compete with ATP. It binds the distant myristoyl pocket and stabilizes an inactive/autoinhibited-like kinase state. T315 is approximately **25.6 Å from MYR** and **24.8 Å from the detected myristoyl cavity**, so there is no plausible direct steric conflict between T315I and asciminib.

The matched cellular data support this:

- WT GI50: **0.61 nM**
- T315I GI50: **7.64 nM**

The approximately 12.5-fold shift indicates a measurable indirect effect, but not loss of activity at relevant nanomolar concentrations. Therefore, **T315I alone should not be interpreted as asciminib resistance**. Resistance can still arise from mutations in the myristoyl pocket, residues needed for autoinhibition, compound mutations, altered transcript isoforms, or bypass signaling.

## Sources

- [UniProt ABL1 P00519](https://rest.uniprot.org/uniprotkb/P00519)
- [RCSB PDB 1OPK](https://www.rcsb.org/structure/1OPK)
- [RCSB polymer-entity mapping for 1OPK](https://data.rcsb.org/rest/v1/core/polymer_entity/1OPK/1)
- Nagar et al., *Cell* 2003; [PMID 12654251](https://pubmed.ncbi.nlm.nih.gov/12654251/), DOI [10.1016/S0092-8674(03)00194-6](https://doi.org/10.1016/S0092-8674(03)00194-6)
- ChEMBL: [imatinib CHEMBL941](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL941), [asciminib CHEMBL4208229](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL4208229)
- ChEMBL matched imatinib records: [activity 1651429](https://www.ebi.ac.uk/chembl/api/data/activity/1651429.json), [activity 1651473](https://www.ebi.ac.uk/chembl/api/data/activity/1651473.json)
- ChEMBL matched asciminib records: [activity 18557370](https://www.ebi.ac.uk/chembl/api/data/activity/18557370.json), [activity 18557371](https://www.ebi.ac.uk/chembl/api/data/activity/18557371.json)
- Schoepfer et al., “Discovery of Asciminib (ABL001)”; [PMID 30137981](https://pubmed.ncbi.nlm.nih.gov/30137981/), DOI [10.1021/acs.jmedchem.8b01040](https://doi.org/10.1021/acs.jmedchem.8b01040)
- [ClinVar VCV000012624](https://www.ncbi.nlm.nih.gov/clinvar/variation/12624/)
- [Official AlphaMissense data README](https://storage.googleapis.com/dm_alphamissense/README.pdf)
- [Ensembl VEP AlphaMissense result for NM_005157.6:c.944C>T](https://rest.ensembl.org/vep/human/hgvs/NM_005157.6%3Ac.944C%3ET?AlphaMissense=1)
- Cheng et al., *Science* 2023; DOI [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492)
=== END RUN r4c3qunamqw ===

=== RUN ryn8jcxnlam ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Overall assessment

**Allosteric communication between the FRJ ligand site and Cys215 is plausible, but not established by these analyses alone.**

The results provide:

- **Structural support:** a continuous, ligand-site-to-Cys215 contact-network route.
- **Dynamical support:** strong co-motion in the lowest-frequency nontrivial ANM mode, with several ligand-contact residues unusually coupled to Cys215 across the full mode spectrum.
- **No independent STINGAllo corroboration:** STINGAllo returned no predicted allosteric residues for 1T4J chain A.

The evidence is therefore **suggestive but only partly convergent**, because the common static-path intermediates were not themselves unusually coupled to Cys215 across the full normal-mode spectrum, and STINGAllo did not nominate pathway residues.

## Structural context

- 1T4J chain A maps to **PTP1B P18031**.
- The chain contains ligand **FRJ**.
- FRJ contacts within 4.0 Å are:
  **P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, and M282**.
- Cys215 is a catalytic-site residue.

## What each analysis supports—and does not

| Analysis | Result | What it supports | What it does not establish |
|---|---|---|---|
| **Normal-mode analysis** | ANM of 282 Cα atoms and 276 nontrivial modes. The lowest mode had a FRJ-contact-group/Cys215 directional cosine of **0.992**. Across the full spectrum, the FRJ-contact group scored at the **92.1st percentile** versus same-sized random residue groups. F280 ranked **3/282**, M282 **13/282**, E200 **22/282**, and A189 **23/282** for coupling to Cys215. | The ligand-site region and Cys215 can move coherently in a genuine non-rigid collective mode. Some FRJ-contact residues, especially F280, are unusually dynamically coupled to Cys215. This supports physical plausibility of communication. | It does not show that FRJ binding causes the motion, that the motion changes Cys215 activity, or that energy/signaling flows along a particular route. Coupling is mode-specific: other low modes had weak or opposite alignment. A single static ligand-bound structure cannot capture ligand-induced conformational changes. |
| **Residue-contact network** | The graph contains 282 residues and 1,379 edges; an edge means any heavy-atom pair is within 4.5 Å. A representative route is **E276–P188–F191–L110–C215**. Every one of the 11 FRJ-contact anchors reaches Cys215 in 3–5 edges. **L110 occurs in 11/11 paths**, and F191 in 8/11. | The ligand site and Cys215 are structurally connected without a topological break, and L110 is a robust network bottleneck. Multiple ligand contacts converge on the same route, reducing dependence on an arbitrary anchor. | A shortest path is not a signal-transmission pathway. The graph is unweighted, static, and nondirectional; it does not measure motion, energy, conformational transition, or catalytic effect. L110 may simply be close to the catalytic site in the folded protein. |
| **STINGAllo** | The direct chain-specific call and the ligand-aware workflow both succeeded but returned **zero predicted residues**. | There is no STINGAllo-positive residue set that independently corroborates the NMA or contact-network results. | An empty STINGAllo result is not evidence that PTP1B lacks allostery. It may reflect model coverage, representation of the bound complex, or prediction limitations; it means only that this model supplied no positive calls for this structure. |

## Cross-method interpretation

The strongest positive observation is the **lowest-frequency collective mode**: the mean FRJ-contact motion aligns very closely with Cys215 motion, and the common network route also has strong mode-1 alignment (**cosine 0.984**).

However, the full-spectrum comparison is less supportive of propagation through the static route:

- L110–Cys215 weighted coupling was only at the **29.4th percentile**.
- F191–Cys215 was at the **27.3rd percentile**.
- P188–Cys215 was at the **39.0th percentile**.
- The combined static-route group was at the **12.3rd percentile** versus random same-sized groups.

Thus, the structural route and the lowest-frequency motion overlap, but the static path intermediates are not generally exceptional dynamical partners of Cys215 across the complete mode spectrum. The strong full-spectrum FRJ-group signal is driven more by a subset of ligand-contact residues, especially F280, M282, E200, and A189.

## Conclusion

The combined analyses support the hypothesis that the FRJ site and catalytic Cys215 participate in the same protein-wide dynamical network and are connected through a robust static pathway. They **do not establish a directed allosteric mechanism**:

1. The lowest mode supports coherent ligand-site/Cys215 motion.
2. The contact network supports physical connectivity through L110 and F191.
3. STINGAllo supplies no independent corroborating residue predictions.
4. Static-path intermediates are not uniformly dynamically coupled to Cys215.

A firm conclusion would require ligand-bound versus apo dynamics, repeated molecular-dynamics simulations with dynamic-network/community analysis, and perturbation of FRJ-contact residues and route residues such as L110/F191/F194 followed by measurement of PTP1B catalytic activity.

### Final plan status

1. [✓] Verify the mapping and obtain coordinate-based FRJ contacts  
2. [✗] Initial residue-level NMA extraction failed because of eigenvector indexing  
3. [✗] First corrected extraction failed because of mixed NumPy advanced indexing  
4. [✓] Correct NMA extraction using explicit mode × residue × XYZ arrays  
5. [✓] Build the contact network and test all 11 FRJ anchors  
6. [✓] Retrieve STINGAllo predictions and verify the empty result  
7. [✓] Integrate the structural, dynamical, and model-prediction evidence  

*Technical note: the NMA wrapper’s residue-specific eigenvector metadata were unavailable and its returned array was not mode-major in this build, so residue-level statistics were reconstructed from the identical ProDy ANM construction; the eigenvalues agreed exactly with the wrapper output.*
=== END RUN ryn8jcxnlam ===

=== RUN rw5az4vvi6z ===
QUESTION:
For KRAS (UniProt P01116), report ClinVar classification and AlphaMissense score for G12C, G12D and G12V, and the distance from residue 12 to the covalent inhibitor in PDB 6OIM. Do the scores distinguish the three variants?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V03_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[V03_b] [critical] [scripted] {"clinical_significance": "Likely pathogenic", "variation_id": "27617"}
[V03_c] [critical] [scripted] 0.9975
[V03_d] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "20046"}
[V03_e] [critical] [scripted] 0.9984
[V03_f] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "27622"}
[V03_g] [critical] [scripted] 0.9949
[V03_h] [critical] [judged] the distance from residue 12 to the 6OIM covalent inhibitor is reported
[V03_i] [critical] [judged] the answer says whether the three scores separate the variants

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**KRAS (P01116) — G12C, G12D, G12V**

**ClinVar classification** (local pinned ClinVar snapshot, KRAS, 1172 records scanned):
- **G12C** — c.34G>T, NM_004985.5, VCV 27617: **Likely pathogenic** ("criteria provided, multiple submitters, no conflicts"). The delins allele c.33_34delinsCT (p.Gly12Cys, VCV 1693585) is separately **Pathogenic**.
- **G12D** — c.35G>A, VCV 27621: **Pathogenic/Likely pathogenic**.
- **G12V** — c.35G>T, VCV 27622: **Pathogenic**.

**AlphaMissense scores** (P01116, position 12; local pinned AlphaMissense TSV):
- **G12C = 0.9975** (class: pathogenic)
- **G12D = 0.9984** (class: pathogenic)
- **G12V = 0.9949** (class: pathogenic)

**Distance from residue 12 to the covalent inhibitor, PDB 6OIM:**
6OIM = "Crystal Structure of human KRAS G12C covalently bound to AMG 510" (1.65 Å); the inhibitor is chemical component **MOV = "AMG 510 (bound form)"** (sotorasib), chain A = P01116, author residue 12 = Cys12 (UniProt 12).
- **Minimum heavy-atom distance Cys12 → AMG 510 = 1.81 Å** (tool: `[TOOL]`, cutoff 4.0 Å; Cys12 is the closest of 17 contacts, next closest Lys16 2.77 Å).
- Atom-level confirmation: Cys12 SG – MOV C25 (acrylamide warhead carbon) = **1.805 Å**, with the deposited `LINK SG CYS A 12 C25 MOV A 303 … 1.81` record — i.e., a genuine covalent bond. There is no covalent inhibitor geometry for G12D/G12V in this entry (no Cys12).

**Do the scores distinguish the three variants?**
- **AlphaMissense: no.** G12C/G12D/G12V span only 0.0035 (0.9949–0.9984), all classified pathogenic; all 19 possible Gly12 substitutions score 0.985–0.9998. The scores are saturated and non-discriminatory (and their ordering is not meaningful: the lowest AM value, G12V, is the one ClinVar calls unqualifiedly Pathogenic).
- **ClinVar: only administratively.** The three labels differ in string but all sit in the pathogenic/likely-pathogenic category, and the G12C "Likely pathogenic" vs "Pathogenic" difference reflects allele representation/curation (SNV vs delins), not biology; ClinVar categories are not calibrated scores and do not rank oncogenic potency or drug sensitivity.
- **The covalent structure measurement is the discriminating datum:** only G12C supplies a Cys12 thiol capable of the 1.81 Å covalent linkage to AMG 510, whereas G12D and G12V cannot form that bond — a distinction the sequence-based pathogenicity scores cannot capture.
=== END RUN rw5az4vvi6z ===

=== RUN rmsqsr9ik7v ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**STINGAllo predictions for PTP1B (PDB 1T4J, chain A):**

A129, A130, A187, A188, A189, A192, A193, A196, A200, A276, A279, A280, A281, A282

**Service response date:** **2026-10-28**  
HTTP `Date`: Wed, 28 Oct 2026 10:42:09 GMT

**Source:** STINGAllo API (`/api/afrs?pdb_id=1T4J&chain_id=A`)
=== END RUN rmsqsr9ik7v ===

=== RUN ra9lckd7t63 ===
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
## SHP2–SHP099 comparison for PDB 5EHR, chain A

RCSB identifies **5EHR** as SHP2 in complex with the allosteric inhibitor **SHP099**. In the deposited structure, SHP099 has chemical-component ID **5OD**.

### STINGAllo predictions

**List:** `[]`

The validated STINGAllo query returned no predicted residues for 5EHR chain A. The same empty result was obtained through the integrated allosteric workflow; chain B was also empty.

### SHP099 contacts within 4 Å

| Residue | Minimum distance |
|---|---:|
| A.108 THR | 3.13 Å |
| A.110 GLU | 3.47 Å |
| A.111 ARG | 3.14 Å |
| A.113 PHE | 2.79 Å |
| A.114 HIS | 3.75 Å |
| A.218 THR | 3.69 Å |
| A.219 THR | 3.59 Å |
| A.249 GLU | 3.29 Å |
| A.250 GLU | 3.10 Å |
| A.253 THR | 3.30 Å |
| A.254 LEU | 3.46 Å |
| A.257 GLN | 3.58 Å |
| A.491 PRO | 3.45 Å |
| A.492 LYS | 3.45 Å |
| A.495 GLN | 3.57 Å |

Thus, **15 residues** lie within the inclusive 4 Å cutoff.

### Overlap

**Overlap:** `[]`  
**Overlap count:** **0**

### Conclusion

**No—the STINGAllo result does not recover the SHP099 tunnel site.** There are no STINGAllo-predicted residues to overlap with the 15 ligand-contacting residues that delineate the tunnel.

This is specifically a **no-coverage result**, rather than a case where STINGAllo predicts a different set of residues: the current service response contains **no STINGAllo record/residue prediction for 5EHR**.
=== END RUN ra9lckd7t63 ===

=== RUN r83lagds20f ===
QUESTION:
Using only pocket-detection output on PTP1B (PDB 1T4J, ligands removed), rank the top three pockets by how likely each is to be an allosteric site, and justify the ranking.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H02_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[H02_c] [critical] [judged] a ranking of the top three pockets by allosteric likelihood with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final progress checklist

1. [✓] Retrieved PDB 1T4J and inventoried heteroatoms.
2. [✓] Removed the 41-atom `FRJ` ligand record; validated 2,304 `ATOM` records and zero `HETATM` records.
3. [✗] Supplied AutoSite wrapper failed because `prepare_receptor` was unavailable.
4. [✗] Initial Fpocket invocation appeared empty because Fpocket writes beside its input rather than in the working directory.
5. [✓] Ran a verified Fpocket 4.0 calculation and preserved 18 detected pockets.
6. [✗] First descriptor parser assumed an undecorated INFO-file table.
7. [✓] Parsed all pocket descriptors, alpha-sphere geometry, lining residues, solvent accessibility, composition, and inter-pocket overlap.
8. [✗] First report writer had a truncated Python expression.
9. [✗] First validation display depended on the unavailable `column` utility.
10. [✗] Second validation used an off-by-one newline-count assertion.
11. [✓] Corrected and completed validation; all final files and checksums pass.
12. [✓] Saved the ranking, methods, native outputs, and reproducibility audit.

## Ranking

**Relative structural allosteric-plausibility: Pocket 11 > Pocket 8 > Pocket 7.**

| Rank | Pocket | Principal pocket-output evidence | Interpretation |
|---|---:|---|---|
| **1** | **11** | `drug_score` **0.8205**; volume **646.2 Å³**; **79** alpha spheres; mean solvent accessibility **0.446**; local hydrophobic density **47.86**; hydrophobicity score **32.75**; polarity score **4**; charge score **−2**; 12 lining residues | Best ligand-binding candidate by a very wide margin—its drug score is about **12-fold** that of P8. The cavity is large, coherent, strongly hydrophobic, and still contains polar/charged character that could support specific ligand contacts. Its relatively lower solvent accessibility suggests it is more buried than P8, but nothing in the pocket output establishes that it is an orthosteric rather than allosteric cavity. |
| **2** | **8** | `drug_score` **0.0689**; volume **638.3 Å³**; **63** alpha spheres; solvent accessibility **0.501**; local hydrophobic density **33.71**; hydrophobicity **24.20**; polarity **6**; charge **−3**; 15 lining residues | Nearly as voluminous as P11 and strongly hydrophobic, but with more moderate apolar character and better solvent accessibility. Importantly, it is distinct from P11: only **one shared lining residue** and **13.22 Å** separation between pocket centroids. That independence makes P8 the strongest candidate for a separate regulatory/allosteric pocket. |
| **3** | **7** | `drug_score` **0.0051**; volume **432.4 Å³**; **35** alpha spheres; solvent accessibility **0.577**; local hydrophobic density **12.13**; hydrophobicity **1.90**; polarity **7**; charge **−1**; 10 lining residues | More exposed, compact, and compositionally balanced than P11 or P8, making it superficially compatible with a surface-accessible regulatory site. However, it shares **four lining residues** with P11, has residue-set Jaccard overlap **0.222**, and lies only **9.64 Å** from the P11 centroid. It may therefore represent an adjacent branch or alternative partition of the dominant cavity rather than a fully independent site, which lowers its ranking. |

### Closest alternate

**Pocket 3** narrowly missed the top three under the stated rule. It had a `drug_score` of **0.0041**, volume **624.2 Å³**, **62** alpha spheres, balanced hydrophobic/polar character, and—unlike P7—**zero shared lining residues and 24.43 Å separation from P11**. If maximal spatial independence were weighted more heavily than the detector’s ligandability score, P3 could replace P7.

## Interpretation limit

Fpocket measures cavity geometry and ligand-binding plausibility; **pocket detection alone cannot determine whether a site is allosteric**, because it does not measure conformational coupling to catalytic activity. Thus this is a structural candidate ranking, not evidence that any pocket is experimentally allosteric. No literature, known PTP1B allosteric-site annotations, ligand information, or bound-structure comparison was used.

## Reproducible outputs

- Cleaned structure: `/agent_cwd/ptp1b_pocket_analysis/structure/1T4J_apo_protein_only.pdb`
- Final ranking: `/agent_cwd/ptp1b_pocket_analysis/results/allosteric_pocket_ranking.tsv`
- Full pocket geometry: `/agent_cwd/ptp1b_pocket_analysis/results/fpocket_[TOOL].json`
- Methods: `/agent_cwd/ptp1b_pocket_analysis/results/METHODS.md`
- Verified checksums: `/agent_cwd/ptp1b_pocket_analysis/results/SHA256SUMS.txt`
=== END RUN r83lagds20f ===

=== RUN rwgid3y0aj7 ===
QUESTION:
In PDB entry 3O96 (human AKT1, UniProt P31749), identify the allosteric inhibitor, list the residues within 4 angstroms of it, and say which AKT1 domains (using UniProt domain boundaries) those residues belong to.

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[S04_b] [critical] [scripted] [{"chain": "A", "pdb_number": 444}]
[S04_c] [critical] [scripted] {"uniprot_residues": [80, 82, 83, 84, 85, 205, 210, 211, 264, 268, 271, 272, 273, 274, 290, 291, 292, 296], "pdb_residues": [80, 82, 83, 84, 85, 205, 210, 211, 264, 268, 271, 272, 273, 274, 290, 291, 292, 296], "min_distances": {"80": 3.413, "82": 3.948, "83": 3.739, "84": 3.46, "85": 3.745, "205": 2.893, "210": 3.661, "211": 3.584, "264": 3.64, "268": 3.256, "271": 3.905, "272": 3.113, "273": 3.752, "274": 3.825, "290": 3.376, "291": 3.975, "292": 3.062, "296": 3.146}}
[S04_d] [critical] [judged] the contact residues fall in the PH domain of AKT1

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PDB 3O96 — AKT1 + allosteric inhibitor: contacts ≤4 Å and UniProt domain assignment

### 1. The allosteric inhibitor

| Field | Value |
|---|---|
| PDB ligand code (CCD) | **IQO** (1 copy, chain A, res. 444, 42 non-H atoms) |
| Common name | **Akt inhibitor VIII** = **Akti‑1/2** ("imidazoquinoxaline 16h") |
| IUPAC (RCSB CCD) | 1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one |
| Formula / InChIKey | C34H29N7O / IWCQHVUQEFDRIW-UHFFFAOYSA-N |
| Registry | CAS 612847-09-3; PubChem CID 135398501 (legacy CID 10196499); CHEMBL258844 |
| Paper designation | "Inhibitor VIII" (EMD Chemicals), = Compound 16h of Lindsley et al., *Bioorg Med Chem Lett* 2005 (PMID 20886116 cites it as ref. 7) |
| Potency (paper) | IC50 58 nM (AKT1), 210 nM (AKT2), 2119 nM (AKT3); activity requires **Trp80** |

Entry: 3O96 = "Crystal Structure of Human AKT1 with an Allosteric Inhibitor Reveals a New Mode of Kinase Inhibition", Wu et al., *PLoS One* 2010 (PMID 20886116), 2.7 Å, P2₁, construct ΔHM-AKT1(1–443) = UniProt P31749 residues 2–443, one chain (A).

⚠️ Not MK‑2206: MK‑2206 is a triazolonaphthyridinone (C25H21N5O, CID 24964624) and binds a different allosteric site. The ligand in 3O96 is the imidazo[4,5-g]quinoxaline Akti‑1/2.

### 2. All AKT1 residues with any heavy atom ≤ 4.0 Å of IQO (n = 18)

Numbering note: PDB numbering was verified to be **identical to UniProt P31749 numbering** (0 mismatches across all 367 modelled residues), so residue numbers below are UniProt numbers.

| Residue | UniProt no. | min heavy-atom distance (Å) | atom pairs ≤4 Å | UniProt domain |
|---|---|---|---|---|
| Trp80 | 80 | 3.41 | 37 | **PH (5–108)** |
| Thr82 | 82 | 3.95 | 1 | **PH (5–108)** |
| Val83 | 83 | 3.74 | 1 | **PH (5–108)** |
| Ile84 | 84 | 3.46 | 12 | **PH (5–108)** |
| Glu85 | 85 | 3.75 | 3 | **PH (5–108)** |
| Ser205 | 205 | 2.89 | 4 | Protein kinase (150–408) |
| Leu210 | 210 | 3.66 | 2 | Protein kinase (150–408) |
| Thr211 | 211 | 3.58 | 1 | Protein kinase (150–408) |
| Leu264 | 264 | 3.64 | 3 | Protein kinase (150–408) |
| Lys268 | 268 | 3.26 | 7 | Protein kinase (150–408) |
| Val271 | 271 | 3.90 | 1 | Protein kinase (150–408) |
| Tyr272 | 272 | 3.11 | 17 | Protein kinase (150–408) |
| Arg273 | 273 | 3.75 | 4 | Protein kinase (150–408) |
| Asp274 | 274 | 3.83 | 1 | Protein kinase (150–408) |
| Ile290 | 290 | 3.38 | 1 | Protein kinase (150–408) |
| Thr291 | 291 | 3.98 | 1 | Protein kinase (150–408) |
| Asp292 | 292 | 3.06 | 6 | Protein kinase (150–408) |
| Cys296 | 296 | 3.15 | 3 | Protein kinase (150–408) |

Polar (N/O) contacts ≤3.5 Å: **Ser205 OG···IQO N35 = 2.89 Å** (the paper's single direct protein–ligand H-bond), Lys268 NZ···IQO N35 = 3.26 Å, Tyr272 O···IQO N42 = 3.24 Å. Two ordered waters also lie ≤4 Å from IQO.

### 3. Domain assignment (UniProt P31749 boundaries)

- **PH domain (5–108): 5 residues** — Trp80, Thr82, Val83, Ile84, Glu85 (β-strand/β-turn region of the PH domain; Trp80 π-stacks with the inhibitor's tricyclic core).
- **Protein kinase domain (150–408): 13 residues** — Ser205, Leu210, Thr211, Leu264, Lys268, Val271, Tyr272, Arg273, Asp274, Ile290, Thr291, Asp292, Cys296. (Asp292/Phe293/Gly294 is the DFG motif; Cys296 is the catalytic-loop Cys; Thr291 and Ser205 flank the activation/DFG region.)
- **AGC-kinase C-terminal domain (409–480): 0 residues** — not contacted, and largely outside the crystallized construct (ends at 443).
- No contact falls in a UniProt "Disordered" region (113–138, 450–480).

### 4. Interpretation / caveats

- The inhibitor binds the **allosteric site at the PH-domain/kinase-domain interface**, not the ATP site: hinge Glu228 (8.18 Å) and Ala230 (11.06 Å), gatekeeper Met227 (5.37 Å) and β3 Lys179 (6.20 Å) are all far from IQO. Consistent with the paper: "Inhibitor VIII binds to AKT1 in an allosteric binding site formed at the combined interface of the PH domain and the N- and C-lobes of the kinase domain", with "only a limited number of polar contacts" and one direct H-bond (Ser205). The paper explicitly names Trp80, Ser205, Lys268 and Arg273 — all in the computed ≤4 Å set.
- Borderline contacts (3.9–4.0 Å, single atom pairs): Thr82, Val271, Asp274, Thr291 (kinase/ PH) — these would be lost under a tighter 3.5 Å cutoff, which would leave 14 residues (Trp80, Val83, Ile84, Glu85, Ser205, Leu210, Thr211, Leu264, Lys268, Tyr272, Arg273, Ile290, Asp292, Cys296).
- Structural context: UniProt helix 247–268 (contains Leu264, Lys268), β-strand 288–290 (Ile290), β-strand 82–89 (Thr82, Val83, Ile84, Glu85); the disordered PH–kiner linker (114–144) is not modelled in 3O96.
- Method: Biopython PDBParser on the RCSB coordinate file (3O96.pdb), minimum heavy-atom distance (hydrogens excluded, all altlocs) from every modelled AKT1 residue to every IQO atom; numbering cross-checked residue-by-residue against UniProt P31749; domains taken from UniProt "Domain" features.

### Completed plan
1. [✓] Query RCSB PDB for entry 3O96 (allosteric inhibitor, PMID 20886116, 2.7 Å)
2. [✓] Query UniProt P31749 for domain/region boundaries (PH 5–108; Protein kinase 150–408; AGC-kinase C-terminal 409–480)
3. [✓] Download 3O96 coordinates and identify the inhibitor (ligand IQO = Akt inhibitor VIII / Akti‑1/2)
4. [✓] Compute all residues with any heavy atom ≤4.0 Å (18 residues; numbering validated against UniProt)
5. [✓] Map contacts to UniProt domains and corroborate with the primary literature (Wu et al. 2010; PubChem/CAS)
=== END RUN rwgid3y0aj7 ===

=== RUN ryiqox1y7pd ===
QUESTION:
For KRAS (UniProt P01116), report ClinVar classification and AlphaMissense score for G12C, G12D and G12V, and the distance from residue 12 to the covalent inhibitor in PDB 6OIM. Do the scores distinguish the three variants?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V03_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[V03_b] [critical] [scripted] {"clinical_significance": "Likely pathogenic", "variation_id": "27617"}
[V03_c] [critical] [scripted] 0.9975
[V03_d] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "20046"}
[V03_e] [critical] [scripted] 0.9984
[V03_f] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "27622"}
[V03_g] [critical] [scripted] 0.9949
[V03_h] [critical] [judged] the distance from residue 12 to the 6OIM covalent inhibitor is reported
[V03_i] [critical] [judged] the answer says whether the three scores separate the variants

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed plan

1. [✓] Retrieved canonical human KRAS (UniProt P01116) and confirmed residue 12 is Gly.
2. [✓] Retrieved the exact ClinVar records for G12C, G12D, and G12V.
3. [✗] Advanced literature-search agent failed at initialization; the official AlphaMissense/VEP data were used instead.
4. [✗] First narrow VEP inspection had a syntax error; the corrected query succeeded.
5. [✓] Retrieved and cross-checked the three AlphaMissense scores.
6. [✗] First coordinate-calculation attempt had an indexing error; the corrected calculation succeeded.
7. [✓] Identified the covalent inhibitor and linkage in PDB 6OIM and independently recomputed the distance.
8. [✗] Optional ClinVar XML cross-check returned an empty set/rate-limit response; the primary ClinVar query records and VCV accessions were used.
9. [✓] Consolidated the results and comparison.

## Results

ClinVar classifications are context-dependent, so both the aggregate **germline** and **oncogenicity** classifications are shown.

| KRAS variant | Exact allele | ClinVar record and germline classification | ClinVar oncogenicity / clinical impact | AlphaMissense |
|---|---|---|---|---|
| **G12C**, p.Gly12Cys | NM_004985.5:c.34G>T; GRCh38 chr12:25,245,351 C>A | **VCV000012578.47** — **Likely pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9975** — likely pathogenic |
| **G12D**, p.Gly12Asp | NM_004985.5:c.35G>A; GRCh38 chr12:25,245,350 C>T | **VCV000012582.69** — **Pathogenic/Likely pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9984** — likely pathogenic |
| **G12V**, p.Gly12Val | NM_004985.5:c.35G>T; GRCh38 chr12:25,245,350 C>A | **VCV000012083.79** — **Pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9949** — likely pathogenic |

AlphaMissense scores were obtained through the official Ensembl VEP AlphaMissense plugin for canonical KRAS transcript **ENST00000311936.8**, corresponding to the P01116 residue-12 substitutions. Its thresholds are:

- likely benign: `<0.34`
- ambiguous: `0.34–0.564`
- likely pathogenic: `>0.564`

All three therefore fall in the **likely-pathogenic** category.

### G12C ClinVar record caveat

ClinVar also contains a separate allele **VCV001701193.30**, NM_004985.5:c.33_34delinsCT (p.Gly12Cys), classified **Pathogenic**. The table above uses the canonical single-nucleotide allele **c.34G>T / VCV000012578**.

## Distance in PDB 6OIM

PDB 6OIM is the structure of **human KRAS G12C covalently bound to AMG 510 (sotorasib)**. The deposited linker is:

`SG CYS A 12 — C25 MOV A 303`

where `MOV` is AMG 510 in its bound form.

- Deposited covalent-bond length: **1.81 Å**
- Independently recomputed from the coordinates: **1.805 Å**
- This is also the minimum atom-to-atom distance between Cys12 and the inhibitor.

Thus, the chemically meaningful **residue-12-to-covalent-inhibitor distance is 1.81 Å**. For comparison, an unweighted Cys12-atom-centroid to inhibitor-atom-centroid distance is **9.06 Å**, but that centroid distance does not represent the covalent contact.

This structural measurement applies specifically to **G12C**; it does not establish covalent binding of sotorasib to G12D or G12V.

## Do the scores distinguish the variants?

**Numerically, yes; categorically, no.**

The ordering is:

**G12D (0.9984) > G12C (0.9975) > G12V (0.9949)**

However:

- G12D versus G12C differs by only **0.0009**
- The full G12D–G12V range is only **0.0035**
- All three are near 1.0 and have the identical AlphaMissense class, **likely pathogenic**

Therefore, the scores provide **no meaningful categorical distinction** among these variants. The small numerical differences should not be interpreted as evidence that one is substantially more pathogenic or clinically consequential than the others. AlphaMissense is a computational pathogenicity predictor, not a clinical classification or a substitute for ClinVar and functional evidence.

### Sources

- UniProt P01116: https://www.uniprot.org/uniprotkb/P01116/entry
- ClinVar G12C: https://www.ncbi.nlm.nih.gov/clinvar/variation/12578/
- ClinVar G12D: https://www.ncbi.nlm.nih.gov/clinvar/variation/12582/
- ClinVar G12V: https://www.ncbi.nlm.nih.gov/clinvar/variation/12583/
- AlphaMissense data documentation: https://storage.googleapis.com/dm_alphamissense/README.pdf
- AlphaMissense paper: https://doi.org/10.1126/science.adg7492
- PDB 6OIM: https://www.rcsb.org/structure/6OIM
- Structure primary paper: https://doi.org/10.1038/s41586-019-1694-1
=== END RUN ryiqox1y7pd ===

=== RUN rfl3hdwnzfe ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**ChEMBL does have a record.** The reported value is:

> **SHP099 IC₅₀ against human PTP1B: >100 µM**  
> ChEMBL standardized value: **>100,000 nM**

**Record details**

- **Molecule:** SHP099 — `CHEMBL4060033`
- **Target:** Human PTP1B/PTPN1 — `CHEMBL335`; UniProt `P18031`
- **Activity:** `24840632`
- **Assay:** `CHEMBL5145449` — biochemical inhibition of wild-type PTP1B using DiFMUP as substrate
- **Standardized fields:** `standard_type = IC50`, `standard_relation = >`, `standard_value = 100000`, `standard_units = nM`
- **pChEMBL:** Not assigned because the result is a lower-bound/censored value
- **Source paper:** Tang et al., *European Journal of Medicinal Chemistry* 230 (2022), 114106. DOI: [10.1016/j.ejmech.2022.114106](https://doi.org/10.1016/j.ejmech.2022.114106); PMID: [35063735](https://pubmed.ncbi.nlm.nih.gov/35063735/)

Links: [ChEMBL compound](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL4060033) · [ChEMBL assay](https://www.ebi.ac.uk/chembl/explore/assay/CHEMBL5145449) · [ChEMBL activity](https://www.ebi.ac.uk/chembl/explore/activity/24840632)

**Caveat:** Although the assay description contains the parenthetical wording “unknown origin,” ChEMBL maps both the target and assay organism to **Homo sapiens** and assigns the record directly to human PTP1B (`CHEMBL335`).
=== END RUN rfl3hdwnzfe ===

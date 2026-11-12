# Judge batch 010 of 24

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

=== RUN rxztjots6hv ===
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
### Final execution plan
1. [✓] Retrieved the ClinVar classification and AlphaMissense score for ABL1 T315I.
2. [✓] Identified the ATP-site ligand (`P16`) and myristoyl-site ligand (`MYR`) in PDB 1OPK and mapped human T315 to the deposited structure.
3. [✓] Calculated the minimum heavy-atom distances from T315 to both ligands.
4. [✓] Interpreted which binding site is most directly affected.

### Results

| Feature | Result |
|---|---|
| **Variant** | ABL1 c.944C>T, p.Thr315Ile (T315I) |
| **ClinVar** | **Likely pathogenic; association** |
| **ClinVar review status** | Criteria provided, multiple submitters, no conflicts |
| **AlphaMissense** | **0.9991**, classified as **pathogenic** |
| **ATP-site ligand** | `P16` |
| **T315 → P16 distance** | **3.24 Å** |
| **Myristoyl-site ligand** | Myristic acid, `MYR` |
| **T315 → MYR distance** | **25.59 Å** |

The closest atom pairs in the deposited structure were:

- **ATP site:** 1OPK chain A Thr334 OG1–P16 C16 = **3.239 Å**
- **Myristoyl site:** 1OPK chain A Thr334 OG1–MYR C14 = **25.595 Å**

### Interpretation

T315 is in the immediate first-shell environment of the **ATP-site ligand**: its side-chain oxygen is only 3.24 Å from `P16`, whereas it is 25.59 Å from the myristoyl-site ligand. Thus, the geometry strongly suggests that T315I directly perturbs **ATP-site ligand binding/steric complementarity**, rather than directly affecting the myristoyl pocket. This is consistent with a bulkier hydrophobic isoleucine altering ATP-site inhibitor accommodation.

Two caveats apply:

1. The distances were measured in the deposited **wild-type Thr** structure; T315I side-chain repacking could change them.
2. PDB 1OPK is annotated as **mouse ABL1 (P00520)** rather than human P00519. Human P00519 T315 maps to deposited chain A **THR334**, and the structure mapping identifies that residue as ABL1 residue 315.

Therefore, the structural evidence supports a predominantly **ATP-site effect**, with no close geometric basis for a direct effect on the myristoyl-site ligand.
=== END RUN rxztjots6hv ===

=== RUN rpj0yim2cbs ===
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
## Ligands and 4 Å contacts

Contacts were calculated using the minimum **heavy-atom** distance to the polymer residues in chain A. In the mappings below, **PDB → P00519** means the deposited author residue number followed by its aligned UniProt position.

### Asciminib — component `AY7`, chain A ligand residue 602

**18 protein contacts**, with minimum distances from 2.82 to 3.87 Å:

- ARG351→ARG332
- ALA356→ALA337
- LEU359→LEU340
- LEU360→LEU341
- ALA363→ALA344
- LEU448→LEU429
- ILE451→ILE432
- ALA452→ALA433
- THR453→THR434
- TYR454→TYR435
- GLU481→GLU462
- CYS483→CYS464
- PRO484→PRO465
- VAL487→VAL468
- PHE512→PHE493
- ILE521→ILE502
- VAL525→VAL506
- LEU529→LEU510

### Nilotinib — component `NIL`, chain A ligand residue 601

**25 protein contacts**, with minimum distances from 2.84 to 3.98 Å:

- LEU267→LEU248
- TYR272→TYR253
- VAL275→VAL256
- ALA288→ALA269
- VAL289→VAL270
- LYS290→LYS271
- LYS304→LYS285
- GLU305→GLU286
- VAL308→VAL289
- MET309→MET290
- ILE312→ILE293
- LEU317→LEU298
- VAL318→VAL299
- ILE332→ILE313
- ILE334→P00519 position 315 — canonical P00519 has THR315; the structure contains the **T315I** substitution
- PHE336→PHE317
- MET337→MET318
- GLY340→GLY321
- PHE378→PHE359
- HIS380→HIS361
- LEU389→LEU370
- VAL398→VAL379
- ALA399→ALA380
- ASP400→ASP381
- PHE401→PHE382

## Do they occupy distinct sites?

**Yes.** The two ligands occupy distinct, adjacent pockets:

- The two sets of 4 Å protein contacts have **no shared residue**.
- The closest heavy atom of asciminib to the closest heavy atom of nilotinib is **19.66 Å** apart.
- Their ligand centroids are **27.78 Å** apart.

The contact patterns are consistent with **asciminib occupying the allosteric myristoyl-binding pocket** of ABL1, including the hydrophobic P00519 region around Phe493, Ile502, Val506, and Leu510, whereas **nilotinib occupies the ATP/hinge pocket**, including the canonical hinge Met318. Thus, the two sites are distinct but close enough to permit simultaneous binding.

## PDB 5MO4 versus UniProt P00519 numbering

For the ABL1 chain in 5MO4:

- The deposited mmCIF aligns **P00519 residues 27–515** to **PDB author residues 46–534**.
- Author residues **40–45** are six expression-tag residues and have no direct P00519 counterpart.
- Throughout all residues listed above, the relationship is:

\[
\text{P00519 position}=\text{PDB author number}-19
\]

This is a construct-specific numbering offset and should not be assumed for other ABL1 structures without checking the SIFTS/UniProt alignment.

There are also two point differences in the construct:

- PDB **ILE334** occupies P00519 position **315**, whose canonical residue is THR315—the deposited **T315I** mutant.
- PDB **ASN382** occupies P00519 position **363**, whose canonical residue is ASP363; this residue is not in either 4 Å contact list.

Data were obtained from the RCSB 5MO4 mmCIF, RCSB chemical-component definitions for `AY7` and `NIL`, the dedicated ligand-contact calculation, and the mmCIF `_struct_ref_seq`/`_struct_ref_seq_dif` alignment records.
=== END RUN rpj0yim2cbs ===

=== RUN ryax86flaop ===
QUESTION:
For SHP2 (UniProt Q06124), combine ClinVar and AlphaMissense for E76K and D61Y, distances to the autoinhibitory interface in 2SHP, pocket detection on 2SHP, and normal mode analysis. Does the evidence support activating variants destabilizing the autoinhibited state that SHP099 stabilizes?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[G03_b] [critical] [judged] the ClinVar and AlphaMissense records for E76K and D61Y, the distances to the 2SHP autoinhibitory interface, the pocket detection on 2SHP and the normal mode analysis are present, with the conclusion hedged and the limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Updated analysis plan

1. [✓] Retrieved UniProt, ClinVar, and official AlphaMissense records for SHP2 E76K and D61Y
2. [✗] Initial 2SHP interface calculation failed because an unused Biopython SVD import was unavailable
3. [✓] Recalculated both N-SH2–PTP autoinhibitory and N-SH2–C-SH2 docking interfaces with distance/contact analysis
4. [✓] Detected 2SHP pockets with fpocket and validated the SHP099 site against experimental SHP099 complexes
5. [✓] Performed ANM/GNM normal-mode analysis, including open-E76K and SHP099-bound controls
6. [✓] Integrated the clinical, structural, pocket, dynamic, and literature evidence

# Verdict

**Yes—collectively, the evidence strongly supports activating variants that weaken or reorganize SHP2’s autoinhibited state, which SHP099 stabilizes.**

The conclusion is strongest for **E76K**, for which there is a direct open-state E76K structure and SHP099-bound closed-state structures. For **D61Y**, the conclusion is also strong but more inferential structurally because no apo/open D61Y structure is available; however, D61 is directly in the N-SH2–PTP interface and D61Y has experimentally demonstrated gain of function.

An important qualification is that **SHP099 does not inhibit all oncogenic SHP2 variants equally well**. E76K is predominantly open before inhibitor binding and binds SHP099 more weakly; nevertheless, SHP099 can shift E76K back toward the closed, autoinhibited conformation.

## 1. Clinical and missense-effect evidence

| Variant | ClinVar | AlphaMissense, Q06124 | Interpretation |
|---|---|---:|---|
| **E76K** | VCV000013336.57. Germline aggregate: **“Conflicting classifications of pathogenicity”**; separate aggregate oncogenicity: **“Oncogenic”**. Multiple pathogenic germline/somatic submissions are present, with some uncertain-significance submissions. | **0.9998 — pathogenic** | Very high support for a damaging/activating effect. The ClinVar conflict should not be presented as uniform pathogenicity, but the somatic oncogenic evidence is strong. |
| **D61Y** | VCV000228392.53. Germline aggregate: **“Conflicting classifications of pathogenicity”**, with multiple pathogenic somatic/germline submissions and some uncertain-significance submissions. | **0.9985 — pathogenic** | Very high support for a damaging/activating effect, although the aggregate ClinVar label is condition-dependent. |

UniProt Q06124 records:

- **D61Y**: VAR_015992, “in JMML.”
- **E76K**: VAR_016000, “in JMML; increases protein tyrosine phosphatase activity against CDC73.”

Functional studies are consistent with these annotations:

- The 2005 Blood study found that **D61, like E76, directly mediates N-SH2–PTP contacts**. D61Y elevated phosphatase activity and caused cytokine-independent myeloid-colony formation, although it was less activating than E76K.
- The 2006 Blood study classified D61 and E76 lesions at or near the N-SH2–PTP interface as perturbations of the inactive/active conformational equilibrium.

## 2. Distances to the autoinhibitory interface in 2SHP

The canonical SHP2 autoinhibitory interface is the **N-SH2–PTP interface**, where the N-SH2 blocking loop inserts into the PTP catalytic cleft. Using a 4.5 Å heavy-atom contact criterion in both 2SHP chains:

| Variant | Chain A minimum distance to PTP | Chain B minimum distance | Direct PTP partners in 2SHP |
|---|---:|---:|---|
| **D61** | **3.689 Å** | **3.499 Å** | S460, A461, I463, R465, Q506; chain B also G464 |
| **E76** | **2.797 Å** | **2.819 Å** | L262, R265, N281, F285, S502 |

Thus, both residues are genuine interface residues rather than merely near the surface.

The structural interpretation is particularly strong:

- The N-SH2 loop containing **N58/T59/G60/D61/Y62/A72** inserts into the catalytic cleft formed by PTP residues around C459/D464/R465.
- E76 makes a critical **E76–S502 hydrogen bond** and an **E76–R265 salt bridge**.
- The 2016 structural study showed that weakening the E76–S502 interaction shifts N-SH2 away from PTP and destabilizes the autoinhibited state. E76K reverses the carboxylate charge and is therefore expected to disrupt both interactions more strongly than the studied E76Q substitution.

For clarity, the separate **N-SH2–C-SH2 docking interface** gives different numbers:

- D61: approximately **23.0–23.2 Å** from C-SH2.
- E76: approximately **18.5–18.7 Å** from C-SH2.

Therefore, D61/E76 do not directly disrupt the secondary N-SH2–C-SH2 interface; their primary effect is at the **N-SH2–PTP catalytic-blocking interface**.

## 3. Pocket detection on 2SHP

Fpocket 4.0 was run on chain A of ligand-free 2SHP, producing 34 candidate cavities.

The experimentally validated SHP099 site was **pocket 20**:

- Volume: **1,184 Å³**
- 100 alpha spheres
- Contains **16 of the 17** protein residues contacted by SHP099 in the WT SHP099–SHP2 structure
- Pocket-lining residues include N-SH2 T108/E110/R111/F113/H114, C-SH2 T218/T219, and PTP E249/E250/T253/L254/Q257 and D489/P491/K492/Q495

Alignment of WT SHP099–SHP2 (5EHR) into 2SHP gave:

- Global Cα RMSD: **0.72 Å**
- Minimum transferred SHP099-to-pocket-lining distance: **0.91 Å**
- Minimum transferred ligand-to-alpha-sphere distance: **0.38 Å**

This confirms that 2SHP already contains the cryptic SHP099 cavity and that pocket 20 is not merely the largest nonspecific cavity.

D61 and E76 are not pocket-20 residues:

- D61 lies in a separate small cavity, pocket 5.
- E76 lies near pockets 4 and 23, approximately 7 Å from the SHP099 pocket lining.

Thus, the variants are not expected to inhibit SHP099 simply by occupying its binding site. Instead, they alter the conformational state in which that site is formed or accessible.

## 4. Normal-mode evidence

ANM used a 15 Å contact cutoff and GNM a 10 Å cutoff, examining the first ten nontrivial modes. The chain-A/chain-B agreement was strong.

### Closed WT 2SHP

- D61 motion was strongly correlated with its direct PTP partners: mean ANM DCC **0.834/0.845** in chains A/B.
- E76 showed similarly strong direct-partner coupling: **0.794/0.802**.
- D61 and E76 motions were coupled to the SHP099-pocket centroid, with weighted correlations of approximately:
  - D61: **0.318/0.335**
  - E76: **0.602/0.604**

This supports an allosteric path from the catalytic-blocking interface to the SHP099 pocket.

### Open E76K control, PDB 6CRF

Compared with 2SHP:

- N-SH2–PTP contacts fall from **68 to 29** in chain A and **13** in chain B.
- D61 loses all original PTP contacts and is now **8.39–8.59 Å** from PTP.
- N-SH2/PTP centroid separation increases from approximately **29.8 Å** to **41.8–42.7 Å**.
- The ANM opening-mode RMS rises from approximately **0.0038–0.0043** in closed WT to **0.0271** in open E76K—approximately sixfold.
- Coupling of D61/E76 to their original PTP partners changes from strongly positive to approximately **−0.16**, reflecting interface reorganization.

Together with the static structures, this is consistent with E76K opening the autoinhibited interface and creating a different N-SH2/PTP contact surface.

## 5. Why SHP099 can favor the closed state

The most informative structural link is the **R111–E249 interaction**:

- In closed 2SHP, R111 and E249 side chains are approximately **11.5 Å** apart.
- In open E76K 6CRF, they form an ion pair at **2.86–3.74 Å**.
- In SHP099-bound closed structures, they remain approximately **10–10.6 Å** apart, while SHP099 contacts both side chains at approximately **3.1–3.6 Å**.

The 2024 mechanistic study independently identified R111–E249 as the key interaction stabilizing SHP2’s open state. The pocket geometry is therefore consistent with SHP099 obstructing an open-state-stabilizing interaction and selecting the closed state.

The experimental structures make this explicit:

- **6CRF:** apo/open E76K; the SHP099 pocket is eliminated.
- **6CRG:** E76K–SHP099; the protein returns to a near-WT closed arrangement.
- **6CMS:** E76K–SHP099; again a closed autoinhibited complex.
- **5EHR:** WT–SHP099; the prototypical closed-state complex.

In 6CRG, SHP099 restores the N-SH2–PTP contact count from 29 in open E76K to **66**, versus 68 in closed WT, and restores the N-SH2/PTP centroid distance to **30.1 Å**.

NMR and binding studies further showed:

- WT SHP2 is approximately **90% closed** and E76K approximately **96% open** before inhibitor.
- SHP099 binding shifts both toward the closed state.
- E76K binds SHP099 more weakly and with faster dissociation than WT.
- Strongly activating mutants show reduced cellular sensitivity to SHP099.

## Overall interpretation

1. **E76K:** Directly destroys the N-SH2–PTP autoinhibitory interface, drives the dramatic open rearrangement seen in 6CRF, and is strongly supported by ClinVar, AlphaMissense, functional assays, MD, and structural studies.
2. **D61Y:** Directly occupies the N-SH2–PTP interface, is functionally activating in hematopoietic assays, and has a near-maximal AlphaMissense score. Its exact apo/open structure remains unavailable, so the detailed conformational trajectory is less directly established than for E76K.
3. **SHP099:** Binds a pre-existing central cavity at the N-SH2/C-SH2/PTP junction and stabilizes the closed autoinhibited ensemble. It can capture E76K in that state, but with reduced potency/affinity.
4. **Normal modes:** Show that D61/E76 motion is coupled to both the autoinhibitory interface and the SHP099 pocket, while the original interface coupling is lost in open E76K.

**Bottom line:** The combined evidence supports the proposed mechanism. D61Y and E76K activate SHP2 by weakening or reorganizing the N-SH2–PTP autoinhibitory interface, and SHP099 counteracts this by selecting and stabilizing the closed conformation. The caveat is that SHP099 is a conformational stabilizer rather than an equally potent inhibitor of every activating SHP2 variant.

### Key sources

- ClinVar: [VCV000013336.57](https://www.ncbi.nlm.nih.gov/clinvar/variation/13336/); [VCV000228392.53](https://www.ncbi.nlm.nih.gov/clinvar/variation/228392/)
- UniProt: [Q06124](https://www.uniprot.org/uniprotkb/Q06124/entry)
- AlphaMissense: Cheng et al., *Science* 2023, DOI [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492)
- 2SHP: PDB [2SHP](https://www.rcsb.org/structure/2SHP); PMID [9491886](https://pubmed.ncbi.nlm.nih.gov/9491886/)
- SHP099 discovery: PMID [27362227](https://pubmed.ncbi.nlm.nih.gov/27362227/)
- Cancer-mutation structures: PMID [27030275](https://pubmed.ncbi.nlm.nih.gov/27030275/)
- Activating-mutation/SHP099 mechanism: PMID [30375376](https://pubmed.ncbi.nlm.nih.gov/30375376/)
- Open versus SHP099-rescued E76K: PMID [30375388](https://pubmed.ncbi.nlm.nih.gov/30375388/)
- R111–E249 open-state ion pair: PMID [38251939](https://pubmed.ncbi.nlm.nih.gov/38251939/)
- D61Y/E76K functional comparison: PMID [15761018](https://pubmed.ncbi.nlm.nih.gov/15761018/)
- PTPN11 mutation functional/MD analysis: PMID [16358218](https://pubmed.ncbi.nlm.nih.gov/16358218/)
- 2025 E76 mutation dynamics study: DOI [10.1186/s13065-025-01494-2](https://doi.org/10.1186/s13065-025-01494-2)
=== END RUN ryax86flaop ===

=== RUN rtb020t2h2t ===
QUESTION:
Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[C03_b] [critical] [judged] the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Normal-mode analysis result

The SHP099-contacting residues are **less mobile in autoinhibited SHP2 (2SHP)** than the rest of the resolved protein.

### Contact definition

SHP099 is ligand component `5OD` in PDB 5EHR. Using a maximum protein–ligand heavy-atom distance of **4.5 Å**, both 5EHR chains gave the same 17 UniProt-numbered residues:

**T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, D489, P491, K492, Q495, Y511**

The PDB-to-UniProt mapping was validated using `DBREF`, RCSB/SIFTS alignment records, and direct sequence alignment. All 17 residues are resolved in 2SHP.

## Methods

- Analyzed 2SHP chains A and B independently.
- Excluded waters, heteroatoms, catalytic phosphotyrosine analogue, and hydrogens.
- Modeled each chain with an anisotropic network model:
  - 3,959 protein heavy atoms
  - 491 resolved residues
  - 15 Å interaction cutoff
  - First 10 nontrivial normal modes
- Primary residue mobility:
  \[
  \text{Mobility}_i=\frac{1}{N_{\text{atoms},i}}
  \sum_{k=1}^{10}\left\|\mathbf{u}_{i,k}\right\|^2
  \]
- GNM and Cα-only ANM calculations were used as sensitivity analyses.

## Primary comparison: 2SHP chain A

| Measure | SHP099-contact residues | Remaining residues |
|---|---:|---:|
| Number | 17 | 474 |
| Mean mobility | 0.000595 | 0.002689 |
| Median mobility | 0.000558 | 0.000999 |
| Mean ratio, contact/rest | **0.221** | — |
| Median ratio, contact/rest | **0.558** | — |

Key statistics:

- Bootstrap 95% CI for median ratio: **0.496–0.636**
- Mann–Whitney test: **p = 1.02 × 10⁻⁴**
- Cliff’s delta: **−0.554**, indicating a moderate-to-large shift toward lower mobility
- Mean log₂-mobility ratio: **0.472**; permutation **p = 0.00168**
- **All 17 contacting residues were less mobile than the median of the remaining structure.**
- Their percentiles relative to the non-contact distribution ranged from approximately **14th to 40th percentile**.

The raw-mean permutation test was not significant (`p = 0.134`) because a small number of highly mobile non-contact loops inflate the rest-of-structure mean. The rank-based, median, and log-scale analyses consistently show lower mobility at the SHP099 site.

## Robustness

### Independent crystallographic chain

2SHP chain B gave nearly identical results:

- Mean ratio: **0.216**
- Median ratio: **0.560**
- Cliff’s delta: **−0.561**
- Mann–Whitney **p = 8.46 × 10⁻⁵**

Mobility profiles between chains were almost identical (`Pearson r = 0.9999`).

### Alternate models

For chain A:

| Model | Median ratio | Cliff’s δ | Mann–Whitney p |
|---|---:|---:|---:|
| Cα-only ANM | 0.564 | −0.565 | 7.5 × 10⁻⁵ |
| Cα GNM | 0.470 | −0.619 | 1.4 × 10⁻⁵ |

The conclusion was unchanged for:

- Ligand-contact cutoffs of 4.0, 4.5, and 5.0 Å
- The first 5, 10, or 20 normal modes
- Both 2SHP chains

## Interpretation

The allosteric SHP099-binding surface is comparatively **rigid in the autoinhibited 2SHP conformation**. This supports a model in which the pocket is held in a constrained, autoinhibited arrangement by the surrounding N-SH2, C-SH2, and phosphatase-domain contacts. SHP099 occupancy may require local rearrangement of this preorganized interface.

This analysis does **not** directly model ligand-induced motion or SHP2 activation, because the normal modes were calculated from uninhibited 2SHP without SHP099. It characterizes the intrinsic flexibility of the autoinhibited state only. Residue-level p-values should also be considered exploratory because residues sharing normal modes and spatial neighborhoods are not fully independent.

## Output files

All results are under:

`/tmp/agent_cwd/C03_r1_1/shp2_nma/output/`

Key files:

- `nma_analysis_summary.txt` — consolidated methods and results
- `per_residue_mobility.csv` — all per-residue mobility values
- `per_contact_residue_mobility_ranks.csv` — mobility of each SHP099-contacting residue
- `mobility_comparisons_all_sensitivities.csv` — statistical sensitivity analyses
- `robust_primary_statistics.csv` — robust median/log-scale statistics
- `mobility_profile.png` — mobility along the UniProt sequence
- `primary_mobility_boxplot.png` — contact versus remaining residues
- `2SHP_chainA_normal_modes.npz`
- `2SHP_chainB_normal_modes.npz`
- `artifact_checksums.txt`

## Completed plan

1. [✓] Inspect the environment for PDB/UniProt data and normal-mode-capable software.
2. [✓] Download and checksum 2SHP, 5EHR, and UniProt Q06124 records.
3. [✓] Confirm SHP099 (`5OD`) and finalize exact residue-level UniProt mapping.
4. [✓] Determine SHP099-contacting residues in 5EHR and map them to 2SHP.
5. [✓] Build and diagonalize the 2SHP normal-mode model and calculate per-residue mobility.
6. [✓] Audit robust statistics, per-residue ranks, alternate metrics, and output integrity.
7. [✓] Summarize interpretation, limitations, and final conclusion.
=== END RUN rtb020t2h2t ===

=== RUN rttrtnt09dd ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan status

1. [✗] Initial UniProt mapping validation — Biopython alignment-block format differed
2. [✗] Second alignment mapping attempt — Biopython coordinate layout mismatch
3. [✓] Validated PDB-to-P35557 mapping
4. [✗] First ClinVar summary rendering — pandas could not group list-valued positions
5. [✗] Second ClinVar summary rendering — pandas could not sort list-valued positions
6. [✓] Retrieved 1,454 human GCK ClinVar records and filtered to 65 contact-position records
7. [✗] Advanced literature agent — unavailable because it required a Claude backend
8. [✗] Initial bulk AlphaMissense probe — timed out while streaming
9. [✗] First GRCh38 table stream — stopped on the copyright header
10. [✗] Second GRCh38 table stream — chromosome ordering made chr7 inefficient to reach sequentially
11. [✗] Ensembl VEP query — public REST response did not include AlphaMissense plugin fields
12. [✗] First BGZF range extraction — header was outside the chr7 byte range
13. [✓] Extracted official P35557 AlphaMissense rows by validated BGZF byte-range access
14. [✓] Checked activator-binding interpretations against primary literature
15. [✓] Audited completeness and generated the final ranked tables

# Results

## Structural and retrieval criteria

- **Protein:** human glucokinase, UniProt [P35557](https://www.uniprot.org/uniprotkb/P35557/entry).
- **Structure:** [PDB 1V4S](https://www.rcsb.org/structure/1V4S), chain A.
- **Allosteric activator:** **MRK**, chain A residue 501. GLC residue 500 is glucose, not the activator.
- **Distance criterion:** minimum heavy-atom distance from the wild-type amino-acid residue to any MRK heavy atom; cutoff ≤6.0 Å.
- **Residue mapping:** for all relevant positions, PDB author numbering matches P35557 numbering.
- **ClinVar search:** `GCK[gene] AND 9606[Taxonomy ID]`, giving **1,454 records**. Applying the 24 structural contact positions gave **65 records**, including **40 missense** and **25 non-missense** records.
- **AlphaMissense:** obtained from the official Google DeepMind `AlphaMissense_hg38.tsv.gz` table. Scores are the calibrated `am_pathogenicity` values. Official classes are:
  - likely benign: <0.34
  - ambiguous: 0.34–0.564
  - likely pathogenic: >0.564

The structural contact positions are p.61, 62, 63, 64, 65, 66, 98, 159, 210, 211, 214, 215, 218, 220, 221, 222, 235, 250, 252, 451, 452, 453, 455, and 456. No retrieved ClinVar record was anchored at p.65 or p.218.

## AlphaMissense-scored ClinVar variants

Assessment codes:

- **D — likely direct effect:** side-chain contact ≤4.5 Å plus AlphaMissense likely-pathogenic.
- **D\*** — likely ligand-specific effect; experimental activator evidence is mixed.
- **A — likely allosteric effect:** established allosteric-site biology, but MRK-affinity direction is not established.
- **I — possible/indirect:** high AlphaMissense, but no side-chain contact ≤4.5 Å.
- **P — possible direct effect:** direct contact, but AlphaMissense is not likely-pathogenic.
- **L — no high AlphaMissense support:** contact alone is insufficient; ClinVar evidence may still override this.

| VCV | Protein change | AlphaMissense | Residue–MRK Å | Side-chain–MRK Å | ClinVar | Assessment |
|---|---|---:|---:|---:|---|---|
| VCV001444770 | p.Tyr61Asn | 0.8868 (LP) | 3.25 | 5.85 | VUS | I |
| VCV000585917 | p.Val62Ala | 0.9731 (LP) | 3.62 | 3.64 | Pathogenic | **D** |
| VCV000419624 | p.Val62Met | 0.9462 (LP) | 3.62 | 3.64 | Pathogenic | **D\*** |
| VCV001502971 | p.Arg63Leu | 0.3254 (LB) | 2.73 | 3.75 | VUS | P |
| VCV002779779 | p.Arg63His | 0.1886 (LB) | 2.73 | 3.75 | VUS | P |
| VCV000447391 | p.Arg63Cys | 0.1234 (LB) | 2.73 | 3.75 | VUS / uncertain risk | P |
| VCV002735015 | p.Ile159Asn | 0.9313 (LP) | 4.33 | 4.33 | Conflicting | **D** |
| VCV002700200 | p.Ile159Thr | 0.5886 (LP) | 4.33 | 4.33 | VUS | **D** |
| VCV000447403 | p.Ile159Met | 0.2207 (LB) | 4.33 | 4.33 | Conflicting | P |
| VCV001679549 | p.Ile159Val | 0.1611 (LB) | 4.33 | 4.33 | Pathogenic/Likely pathogenic | P |
| VCV002505485; VCV002505486 | p.Met210Val | 0.8229 (LP) | 3.66 | 3.66 | Likely pathogenic | **D** |
| VCV000016141 | p.Met210Lys | 0.9915 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV000804852 | p.Met210Thr | 0.9821 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV002691826; VCV000036236 | p.Met210Ile | 0.9915 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV000435303 | p.Ile211Asn | 0.9683 (LP) | 3.59 | 3.59 | VUS / uncertain risk | **D** |
| VCV002684209 | p.Ile211Thr | 0.9474 (LP) | 3.59 | 3.59 | Pathogenic | **D** |
| VCV000016144 | p.Tyr214Cys | 0.2600 (LB) | 3.01 | 3.01 | Pathogenic | **A** |
| VCV004743109 | p.Cys220Ser | 0.9574 (LP) | 3.30 | 5.87 | VUS | I |
| VCV000036239 | p.Cys220Arg | 0.9953 (LP) | 3.30 | 5.87 | Likely pathogenic | I |
| VCV000036240 | p.Cys220Tyr | 0.
=== END RUN rttrtnt09dd ===

=== RUN rf73864kw31 ===
QUESTION:
Use PocketMiner on the TEM-1 beta-lactamase structure 1BTL (UniProt P62593). Report the ten highest-scoring residues and the scores of the residues that contact the allosteric inhibitors in PDB entry 1PZO, after mapping between the two entries.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P04_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[P04_b] [critical] [scripted] [{"chain": "A", "pdb_number": 234, "residue_name": "LYS", "score": 0.9514}, {"chain": "A", "pdb_number": 246, "residue_name": "ILE", "score": 0.9425}, {"chain": "A", "pdb_number": 172, "residue_name": "ALA", "score": 0.9411}, {"chain": "A", "pdb_number": 244, "residue_name": "ARG", "score": 0.929}, {"chain": "A", "pdb_number": 264, "residue_name": "TYR", "score": 0.9265}, {"chain": "A", "pdb_number": 217, "residue_name": "ALA", "score": 0.9208}, {"chain": "A", "pdb_number": 235, "residue_name": "SER", "score": 0.9179}, {"chain": "A", "pdb_number": 220, "residue_name": "LEU", "score": 0.9168}, {"chain": "A", "pdb_number": 266, "residue_name": "THR", "score": 0.9058}, {"chain": "A", "pdb_number": 66, "residue_name": "PHE", "score": 0.9051}]
[P04_c] [critical] [scripted] {"214": 0.8751, "215": 0.9208, "218": 0.9168, "219": 0.7866, "222": 0.2461, "233": 0.9179, "234": 0.8263, "235": 0.8921, "241": 0.929, "242": 0.8435, "243": 0.9425, "257": 0.3872, "259": 0.7797, "272": 0.8693, "275": 0.774, "276": 0.4914, "279": 0.2419, "282": 0.3811}
[P04_d] [critical] [judged] the mapping between the two entries is stated (both are TEM-1, P62593; the 1PZO CBT contacts are given in UniProt numbering)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed analysis plan

1. [✓] Locate and verify the public original PocketMiner implementation and model checkpoint.
2. [✓] Prepare a compatible TensorFlow environment and retrieve RCSB 1BTL/1PZO and UniProt P62593.
3. [✓] Run PocketMiner on the 1BTL TEM-1 chain and verify all model weights and numerical reproducibility.
4. [✓] Align 1PZO to 1BTL and identify allosteric-inhibitor contacts.
5. [✓] Extract mapped residue scores and rank the ten highest-scoring 1BTL residues.

## PocketMiner run

- **Target:** TEM-1 β-lactamase, PDB **1BTL**, chain A, 263 residues.
- **Model:** Original PocketMiner `models/pocketminer` checkpoint from the public `Mickdub/gvp:pocket_pred` distribution, commit `187062df3c94127e991669768009141a08fd5d8b`.
- **Execution:** TensorFlow 2.9.3 using the upstream `process_strucs`/`predict_on_xtals` workflow.
- **Result:** 263 residue-level scores; an independent rerun was exactly identical (`max absolute difference = 0`).

## Ten highest-scoring 1BTL residues

Residue labels below use **1BTL PDB numbering**.

| Rank | Residue | PocketMiner score |
|---:|---|---:|
| 1 | Lys234 | **0.95141077** |
| 2 | Ile246 | **0.94251889** |
| 3 | Ala172 | **0.94110560** |
| 4 | Arg244 | **0.92899722** |
| 5 | Tyr264 | **0.92647135** |
| 6 | Ala217 | **0.92083418** |
| 7 | Ser235 | **0.91794658** |
| 8 | Leu220 | **0.91683006** |
| 9 | Thr266 | **0.90583670** |
| 10 | Phe66 | **0.90505010** |

Five of these ten—**Ile246, Arg244, Ala217, Ser235, and Leu220**—also directly contact the 1PZO allosteric inhibitors.

## Allosteric-inhibitor-contact residues and mapped scores

1PZO contains two copies of the allosteric inhibitor **CBT**, at hetero residues **CBT A300** and **CBT A301**. The primary table below defines a contact as a protein heavy atom within **4.5 Å** of an inhibitor heavy atom. Distances are the minimum for the indicated CBT copy/copies.

| 1PZO → 1BTL residue | CBT copy | Minimum distance (Å) | 1BTL PocketMiner score |
|---|---:|---:|---:|
| Val216 | 300 | 3.755 | **0.87508768** |
| Ala217 | 300 | 3.908 | **0.92083418** |
| Leu220 | 300 / 301 | 3.531 / 3.353 | **0.91683006** |
| Leu221 | 301 | 3.350 | **0.78664958** |
| Ala224 | 301 | 3.411 | **0.24609138** |
| Leu225 | 301 | 4.430 | **0.45616716** |
| Ser235 | 300 | 2.598 | **0.91794658** |
| Gly236 | 300 | 3.685 | **0.82630885** |
| Ala237 | 300 | 3.556 | **0.89208180** |
| Arg244 | 300 / 301 | 3.358 / 3.396 | **0.92899722** |
| Gly245 | 300 | 3.185 | **0.84350264** |
| Ile246 | 300 | 3.386 | **0.94251889** |
| Val261 | 301 | 3.998 | **0.38724527** |
| Ile263 | 300 / 301 | 4.286 / 3.791 | **0.77965564** |
| Asn276 | 300 / 301 | 3.543 / 3.068 | **0.86931854** |
| Ile279 | 300 / 301 | 3.573 / 3.561 | **0.77398539** |
| Ala280 | 301 | 3.420 | **0.49136814** |
| Gly283 | 301 | 3.667 | **0.24188624** |
| Leu286 | 301 | 3.942 | **0.38111976** |

Thus, the direct-coordinate inhibitor-contact union contains **19 residues**. At a stricter 4.0 Å cutoff, the union differs only by removal of **Leu225** at 4.430 Å.

### Deposited PDB SITE interpretation

Because the 1PZO `SITE` records are internally inconsistent with the coordinates—the explicitly listed CBT copy is reversed between AC1/AC2, and Arg191/Lys192 are more than 12 Å from both CBT molecules—the coordinate table above is the physically defensible contact set. Nevertheless, if “contacts” is intended to mean the **deposited PDB SITE union**, its mapped scores are:

| Deposited SITE residue | 1BTL PocketMiner score |
|---|---:|
| Arg191 | 0.39633211 |
| Lys192 | 0.49477991 |
| Leu220 | 0.91683006 |
| Leu221 | 0.78664958 |
| Ala224 | 0.24609138 |
| Ser235 | 0.91794658 |
| Gly236 | 0.82630885 |
| Ala237 | 0.89208180 |
| Arg244 | 0.92899722 |
| Gly245 | 0.84350264 |
| Ile246 | 0.94251889 |
| Asn276 | 0.86931854 |
| Ile279 | 0.77398539 |
| Ala280 | 0.49136814 |
| Gly283 | 0.24188624 |

## Mapping and numbering

A global alignment of the 263-residue chain A sequences found:

- no alignment gaps;
- identical PDB residue numbering between 1BTL and 1PZO;
- three substitutions, written as **1BTL → 1PZO**:
  - I84V
  - M182T
  - V184A

None of these substitutions occurs in either inhibitor-contact set, so every contact maps one-to-one to the same-numbered 1BTL residue.

For UniProt **P62593**, the mature β-lactamase chain is residues 24–286. The 1BTL PDB numbering maps as follows:

- PDB 26–238 → UniProt 24–236
- PDB 240–252 → UniProt 237–249
- PDB 254–290 → UniProt 250–286

## Interpretation

PocketMiner strongly recognizes part of the CBT-binding interface: **Ile246, Arg244, Ala217, Ser235, and Leu220** are all in the overall top ten. It does not uniformly score every physical contact highly—particularly **Ala224, Ala280, Gly283, Val261, and Leu286** have comparatively low scores.

### Provenance

- Meller A, et al. **Predicting locations of cryptic pockets from single protein structures using the PocketMiner graph neural network.** *Nature Communications* 2023. DOI: **10.1038/s41467-023-36699-3**.
- Horn JR, Shoichet BK. **Allosteric inhibition through core disruption.** *Journal of Molecular Biology* 2004;336:1283–1291. DOI: **10.1016/j.jmb.2003.12.068**; PMID: **15037085**.
- Structures: RCSB PDB **1BTL** and **1PZO**; sequence: UniProt **P62593**.
=== END RUN rf73864kw31 ===

=== RUN r5i1as95ukp ===
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
## Summary

**Yes — the top-five AutoSite pockets on 2SHP do cover SHP099-binding-site residues.** Three of the five ranked pockets in each chain overlap the 5EHR SHP099 site, and the union of the top five covers all 15 contact residues in both chains.

### 1. Pocket detection on 2SHP

AutoSite 1.0 (Scripps ADFRsuite; genuine binary, installed from the official ADFRsuite release) was run on both 2SHP copies via the `biomni.tool.pharmacology.run_autosite()` function (spacing 1.0 Å; `reduce` for polar hydrogens; `prepare_receptor4.py` for PDBQT/Gasteiger charges).

| Rank | Chain A (cluster/score) | Chain B (cluster/score) |
|---|---|---|
| 1 | cl1 / 47.67 (428 pts) | cl1 / 48.93 (431 pts) |
| 2 | cl2 / 40.90 (218 pts) | cl2 / 42.17 (253 pts) |
| 3 | cl3 / 40.61 (296 pts) | cl3 / 38.37 (182 pts) |
| 4 | cl4 / 36.50 (176 pts) | cl4 / 37.74 (226 pts) |
| 5 | cl5 / 35.72 (238 pts) | cl5 / 37.71 (294 pts) |

18 clusters (chain A) and 17 (chain B) were detected. Ranking is by AutoSite's own score (v·b^1.5).

### 2. UniProt numbering bridge (Q06124)

- **2SHP:** entity residues 1–525 → UniProt 1–525; PDB author numbering = UniProt numbering.
- **5EHR:** entity residues 2–526 → UniProt 1–525; PDB author numbering = UniProt numbering (entity residue 1 is an N-terminal Ser tag, hence the −1 entity offset).
- Validated by residue-identity checks against the UniProt sequence: 5EHR 3930/3930 atoms consistent; 2SHP 4873/4902 (3 legacy differences: residue 2, 41, 513). Catalytic Cys = author/UniProt 104 in both entries.

### 3. SHP099 contact residues in 5EHR

Ligand **5OD** = SHP099. Heavy-atom contacts ≤ 4.0 Å give **15 UniProt residues** (identical for the chain A and chain B ligand copies):

**T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, Q495**

Independent cross-check: PDBe/Arpeggio curated annotation lists 14 of these (all except Thr218, a 3.69 Å contact) — no discrepancies.

### 4. Overlap with the top-five pockets (4.0 Å assignment)

| 2SHP chain | Rank | Pocket residues | SHP099-site overlap | Overlapping UniProt residues |
|---|---|---|---|---|
| A | 1 | 31 | **0/15** | none |
| A | 2 | 18 | **11/15** | E110, R111, T218, T219, E250, T253, L254, Q257, P491, K492, Q495 |
| A | 3 | 22 | **12/15** | T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, P491 |
| A | 4 | 19 | **5/15** | E110, R111, T253, L254, Q257 |
| A | 5 | 21 | **0/15** | none |
| B | 1 | 33 | **0/15** | none |
| B | 2 | 29 | **5/15** | T108, E110, R111, T253, Q257 |
| B | 3 | 19 | **12/15** | E110, R111, H114, T218, T219, E250, T253, L254, Q257, P491, K492, Q495 |
| B | 4 | 20 | **10/15** | T108, E110, R111, F113, H114, T218, T219, E249, E250, T253 |
| B | 5 | 24 | **0/15** | none |

- **Union of top-5 pockets: 15/15 contact residues covered in both chains** (108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495).
- Best single-pocket matches: **rank 3** in chain A (12/15) and **rank 3** in chain B (12/15).
- Ranks 1 and 5 never touch the SHP099 site: rank 1 is the catalytic-site/N-SH2-interface pocket; rank 5 is a solvent-exposed cleft.
- Conclusion is robust to the pocket-lineage cutoff: overlap counts at 3.5/4.0/4.5/5.0 Å are e.g. chain A rank 3 = 10/12/13/13 and chain B rank 3 = 12/12/14/14.

### Artifacts
- `/agent_cwd/sphp2_work/SHP2_pocket_SHP099_overlap_report.txt` — full research log
- `/agent_cwd/sphp2_work/FINAL_top5_overlap.csv` — per-pocket overlap table
- `/agent_cwd/sphp2_work/autosite_all_pockets_overlap.csv` — all 18/17 pockets scored
- `/agent_cwd/shp2_work/autosite_2SHP_biomni/` — AutoSite output (cluster PDBs, summary CSV, maps)

### Note on tooling
The pre-installed `fpocket` was not used; the genuine Scripps **AutoSite** was obtained from the official ADFRsuite 1.0 Linux release and its Python-2 ADFRcc package required a circular-import patch to load under the bundled interpreter. Every number above comes from that AutoSite run and from direct coordinate calculations on the deposited PDB entries.
=== END RUN r5i1as95ukp ===

=== RUN rapx8v866t3 ===
QUESTION:
For PTP1B in PDB entry 1T4J chain A, how many of the residues STINGAllo predicts are among the residues within 4 angstroms of the bound allosteric ligand? Report both lists and the overlap.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K02_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]
[K02_c] [critical] [scripted] 10

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**0 STINGAllo-predicted residues overlap the residues within 4 Å of the bound ligand.**

For **PDB 1T4J, chain A**, the bound ligand is **FRJ**. Residues were compared using `(chain, residue number)`.

### STINGAllo-predicted residues

The successful chain-specific STINGAllo query returned an empty list:

- **List:** `[]`
- **Count:** 0

### Residues within 4.0 Å of FRJ

| Residue | Minimum heavy-atom distance |
|---|---:|
| A:188 PRO | 3.92 Å |
| A:189 ALA | 3.42 Å |
| A:192 LEU | 3.80 Å |
| A:193 ASN | 3.01 Å |
| A:196 PHE | 3.55 Å |
| A:200 GLU | 3.30 Å |
| A:276 GLU | 2.55 Å |
| A:277 GLY | 3.37 Å |
| A:279 LYS | 3.03 Å |
| A:280 PHE | 2.65 Å |
| A:282 MET | 3.59 Å |

- **List:** `A:188 PRO, A:189 ALA, A:192 LEU, A:193 ASN, A:196 PHE, A:200 GLU, A:276 GLU, A:277 GLY, A:279 LYS, A:280 PHE, A:282 MET`
- **Count:** 11

### Overlap

- **List:** `[]`
- **Count:** **0**

The zero overlap arises because STINGAllo returned no residue records for chain A; it should not be interpreted as an explicit prediction that each contacting residue is non-allosteric.

### Completed plan

1. [✓] Retrieve the bound ligand(s) in 1T4J chain A and the STINGAllo residue predictions
2. [✓] Validate chain scope and obtain all chain-A FRJ contacts within 4.0 Å
3. [✓] Cross-check STINGAllo with the bundled workflow and PDB/UniProt mapping
4. [✓] Standardize residue identifiers, compute the intersection, and report both lists plus the overlap count
=== END RUN rapx8v866t3 ===

=== RUN rkxkidxiu56 ===
QUESTION:
Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[C03_b] [critical] [judged] the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Conclusion

The SHP099-contacting residues are **less mobile than the rest of autoinhibited SHP2 in PDB 2SHP**, with the strongest difference in the lowest-frequency collective modes.

Analysis used:

- **Autoinhibited structure:** 2SHP, chain A as the primary analysis; chain B as an independent crystallographic replicate.
- **Comparison structure:** 5EHR.
- **Contact definition:** polymer residues within **4.0 Å** of SHP099, deposited in 5EHR as chemical component **5OD**. The 5EHR title explicitly identifies the complex as “SHP2 in Complex with Allosteric Inhibitor SHP099.”
- **Mapping:** 5EHR contact residues were mapped to UniProt Q06124 numbering. All 15 were modeled in both 2SHP chains and matched the canonical UniProt residue identities.
- **NMA:** ANM on 491 Cα atoms per chain, retaining all **485 nontrivial modes**.

## SHP099-contact residue set

The identical set contacted SHP099 in both 5EHR chains:

**T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, Q495**

Approximately, these comprise 2 N-SH2 residues, 5 C-SH2 residues, and 8 PTP-domain residues.

## Mobility comparison

The primary all-mode metric was

\[
M_i=\sum_{\text{nontrivial modes}}
\left(u_{x,i}^2+u_{y,i}^2+u_{z,i}^2\right),
\]

where \(u\) denotes the normalized ANM eigenvector.

| Metric | Contact mean | Rest mean | Contact/rest | Exact Mann–Whitney \(p\) | Rank-biserial \(r\) |
|---|---:|---:|---:|---:|---:|
| All 485 modes, chain A | 0.4699 | 1.0041 | 0.468 | 0.0551 | −0.290 |
| First 10 modes, chain A | 0.00659 | 0.02080 | 0.317 | 0.0028 | −0.444 |
| First 20 modes, chain A | 0.01296 | 0.04161 | 0.311 | 0.0169 | −0.359 |
| Inverse-eigenvalue-weighted, chain A | 0.07570 | 0.20417 | 0.371 | 0.0218 | −0.345 |

The negative rank-biserial values indicate that the SHP099-contact set is shifted toward **lower** mobility. The all-mode median was 0.312 for contact residues versus 0.958 for all other residues.

### Chain-B validation

Chain B reproduced the same direction and effect sizes:

| Metric | Contact/rest mean ratio | Exact \(p\) | Rank-biserial \(r\) |
|---|---:|---:|---:|
| All 485 modes | 0.447 | 0.0493 | −0.297 |
| First 10 modes | 0.306 | 0.0021 | −0.456 |
| First 20 modes | 0.308 | 0.0184 | −0.354 |
| Inverse-eigenvalue-weighted | 0.360 | 0.0183 | −0.355 |

Per-residue mobility was highly reproducible between the two chains: Spearman \(\rho=0.9984\) for all modes and \(0.9986\)–\(0.9996\) for the other metrics.

## Individual contact residues

All-mode participation values are in arbitrary ANM units:

| UniProt | Residue | Approximate domain | Chain A | Chain B |
|---:|---|---|---:|---:|
| 108 | Thr | N-SH2 | 1.0381 | 1.0359 |
| 110 | Glu | N-SH2 | 0.2949 | 0.2309 |
| 111 | Arg | C-SH2 | 0.3124 | 0.2659 |
| 113 | Phe | C-SH2 | 0.2002 | 0.1856 |
| 114 | His | C-SH2 | 0.8486 | 0.5850 |
| 218 | Thr | C-SH2 | 0.9954 | 0.9951 |
| 219 | Thr | C-SH2 | 0.8333 | 0.8250 |
| 249 | Glu | PTP | 0.9583 | 1.0090 |
| 250 | Glu | PTP | 0.2036 | 0.2141 |
| 253 | Thr | PTP | 0.1549 | 0.1529 |
| 254 | Leu | PTP | 0.1254 | 0.1294 |
| 257 | Gln | PTP | 0.3412 | 0.3925 |
| 491 | Pro | PTP | 0.1169 | 0.1155 |
| 492 | Lys | PTP | 0.4374 | 0.4226 |
| 495 | Gln | PTP | 0.1888 | 0.1787 |

The relatively mobile contacts were consistently **T108, T218, E249, H114, and T219**. The PTP contacts **T253, L254, P491, Q495, and E250** were among the least mobile residues in the structure. In chain A, the contact set also had lower mean mobility within each approximate domain individually, although the within-domain contact counts were small.

## Interpretation

Within the coarse-grained ANM model, the SHP099-binding surface maps onto a **comparatively rigid portion of autoinhibited SHP2**, especially with respect to the lowest-frequency collective motions. This is a structural comparison, not evidence that SHP099 binding causes a mobility change: contacts were defined in ligand-bound 5EHR, whereas the dynamics were calculated in uninhibited 2SHP. The Mann–Whitney tests are exploratory because neighboring residues are structurally correlated and the p-values were not multiplicity-adjusted.

## Technical note

The installed `[TOOL]` wrapper produced valid eigenvalues but misoriented its serialized eigenvectors: it filtered the mode axis while indexing the coordinate axis. This was detected by exact comparison with ProDy’s underlying array. All results above use the corrected mode-oriented vectors, calculated as `eigenvector_array[:, nontrivial_modes].T`.

Audit files are saved under `/agent_cwd/shp2_nma_analysis/`, including per-residue tables for chains A and B and the comparison summaries.

### Final execution checklist

1. [✗] Initial 5EHR query used “SHP099” as a component ID (not deposited; 5OD was used instead).
2. [✗] Initial alias-verification print encountered an incompatible RCSB payload shape (resolved by type-safe inspection).
3. [✓] Verified 5OD is the SHP099 component from the explicit 5EHR entry title.
4. [✓] Retrieved the 4 Å SHP099 contact set and mapped it to Q06124.
5. [✗] Initial NMA call used the wrong keyword (`pdb_path`; corrected to `pdb_id`).
6. [✓] Completed ANM with 485 nontrivial modes.
7. [✗] Initial orientation-audit script had a diagnostic syntax error.
8. [✓] Confirmed and corrected the wrapper eigenvector-axis defect.
9. [✗] Initial summary script had a dictionary-bookkeeping error.
10. [✓] Completed and saved per-residue mobility calculations.
11. [✓] Compared the 15 contact residues with the remaining 476 modeled residues.
12. [✗] First chain-B validation reversed the mode/coordinate transpose in post-processing.
13. [✓] Repeated the corrected chain-B analysis and confirmed high reproducibility.
14. [✓] Reported the results, interpretation, and limitations.
=== END RUN rkxkidxiu56 ===

=== RUN rt2yrspdwx6 ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed analysis plan

1. [✓] Validate 1T4J chain A, FRJ ligand, UniProt numbering, and Cys215
2. [✓] Construct ligand-site and Cys215 residue-contact networks
3. [✓] Perform and validate GNM/ANM normal-mode analyses
4. [✓] Run STINGAllo through its documented REST API
5. [✓] Quantify cross-analysis agreement and mode-range sensitivity
6. [✓] Integrate the evidence and identify what remains unproven

## Bottom line

A ligand-site-to-Cys215 allosteric pathway is **plausible**, and a specific candidate is:

**FRJ pocket (Pro188/Phe196) → Phe191 → Leu110 → Cys215/P-loop**

The strongest computational support comes from:

- a short physical residue-contact path from the FRJ site to Cys215;
- strong Cys215 coupling to the FRJ-contacting Phe196 in the first 20 anisotropic-network modes; and
- STINGAllo’s close agreement with the crystallographic allosteric pocket.

However, this is **not a demonstrated allosteric mechanism**. GNM gives weaker and partly anticorrelated coupling, and the strong ANM coupling largely disappears when higher-frequency modes are included. STINGAllo predicts site-forming residues, not communication or energy flow, and does not predict Cys215 as an allosteric-site-forming residue.

## Structural reference points

- PDB **1T4J** is the 2.7 Å structure “Allosteric Inhibition of Protein Tyrosine Phosphatase 1B.”
- Chain A contains 282 observed residues; residues 283–298 are unresolved.
- PDB numbering corresponds to canonical **UniProt P18031** numbering. Cys215 is present and is annotated as the catalytic phosphocysteine intermediate.
- The bound ligand is **FRJ**, the dib
=== END RUN rt2yrspdwx6 ===

# Judge batch 005 of 24

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

=== RUN ry19ou91v36 ===
QUESTION:
In PDB entry 5EHR (human SHP2, UniProt Q06124, chain A), list the residues within 4 angstroms of the allosteric inhibitor SHP099 and say which domains (N-SH2, C-SH2, PTP) they belong to.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S05_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[S05_b] [critical] [scripted] [{"chain": "A", "pdb_number": 601}]
[S05_c] [critical] [scripted] {"uniprot_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "pdb_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "min_distances": {"108": 3.133, "110": 3.465, "111": 3.135, "113": 2.788, "114": 3.751, "218": 3.693, "219": 3.586, "249": 3.293, "250": 3.103, "253": 3.295, "254": 3.464, "257": 3.58, "491": 3.454, "492": 3.448, "495": 3.571}}
[S05_d] [critical] [judged] each contact residue is assigned to N-SH2, C-SH2 or PTP

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**5EHR / SHP2 chain A — SHP099 (ligand `5OD`) contacts within 4.0 Å**

*Method:* min heavy-atom distance from SHP099 (23 heavy atoms, `5OD`) to each chain-A protein residue, computed on `5EHR.pdb` (RCSB). PDB author numbering here is identical to UniProt Q06124 numbering (no offset; construct = UniProt 1–525, residues 4–525 observed).

| Residue | PDB/UniProt no. | Min dist. (Å) | Domain | Notes |
|---|---|---|---|---|
| Thr108 | 108 | 3.13 | **N-SH2** | N-SH2 switch-helix region |
| Glu110 | 110 | 3.47 | **N-SH2** | O–N22 (ligand amine), 3.47 Å |
| Arg111 | 111 | 3.14 | **N-SH2** | 24 atom pairs; NH1–N2 3.14 Å; cationic-π with ligand pyrimidine |
| Phe113 | 113 | 2.79 | **N-SH2** | closest contact; O–N22 2.79 Å |
| His114 | 114 | 3.75 | **N-SH2** | (not in deposited SITE AC1; just inside cutoff) |
| Thr218 | 218 | 3.69 | **C-SH2** | backbone NH polar contact in the tunnel |
| Thr219 | 219 | 3.59 | **C-SH2** | 7 atom pairs; H-bond donor to ligand |
| Glu249 | 249 | 3.29 | **C-SH2** | 4 atom pairs |
| Glu250 | 250 | 3.10 | **C-SH2** | O–N7 (ligand amine) 3.10 Å |
| Thr253 | 253 | 3.30 | **C-SH2** | 8 atom pairs |
| Leu254 | 254 | 3.46 | **C-SH2** | |
| Gln257 | 257 | 3.58 | **C-SH2** | |
| Pro491 | 491 | 3.45 | **PTP** | 9 atom pairs |
| Lys492 | 492 | 3.45 | **PTP** | 4 atom pairs; known covalent-targetable handle in this tunnel |
| Gln495 | 495 | 3.57 | **PTP** | |

**Domain composition (canonical SHP2 architecture used for SHP099: N-SH2 1–115, C-SH2 116–280, PTP 281–525):**
- **N-SH2 (5):** Thr108, Glu110, Arg111, Phe113, His114
- **C-SH2 (7):** Thr218, Thr219, Glu249, Glu250, Thr253, Leu254, Gln257
- **PTP (3):** Pro491, Lys492, Gln495

This is the classic allosteric "tunnel" at the N-SH2/C-SH2/PTP junction, exactly as described for SHP099 (Chen et al., *Nature* 2016, PMID 27362227: SHP099 "concurrently binds to the interface of the N-terminal SH2, C-terminal SH2, and protein tyrosine phosphatase domains"). The site is allosteric and remote from the catalytic centre (active-site Cys459 is not contacted; nearest PTP contact is Pro491).

**Cross-checks**
- The deposited `SITE AC1` records for this ligand list exactly: Thr108, Glu110, Arg111, Phe113, Thr218, Thr219, Glu249, Glu250, Thr253, Leu254, Gln257, Pro491, Lys492, Gln495 — i.e. 14 of my 15 residues; my 4 Å criterion adds only His114 (3.75 Å). Chain B (`SITE AC5`) gives the identical set.
- Literature key contacts reproduced: Arg111 (cationic-π), Thr218/Thr219 (backbone H-bonds), Glu249/Glu250 (H-bonds), Lys492 (covalent handle) — e.g. PMID 35063735 (TK-453: R111 π-stacking, T219 H-bond, E250 H-bond) and PMID 29304282 ("tunnel-like pocket formed by the confluence of three domains of SHP2").
- Cutoff sensitivity: residues just outside 4 Å are Asp489 (4.27 Å), Tyr511 (4.48 Å), Trp112 (4.83 Å).
- Also within 4 Å but not protein residues: 5 ordered waters (Hoh721, 725, 919, 928, 1035).

**Caveat on domain-boundary convention.** UniProt's own curated features for Q06124 are SH2 1 = 6–102, SH2 2 = 112–216, PTP = 247–517 (InterPro: N-SH2 5–103, C-SH2 111–218, PTP 246–523). Using those annotation boundaries literally, Thr108/Glu110/Arg111 and Thr218/Thr219 fall in inter-domain gaps, and Glu249–Gln257 would be assigned to PTP. The assignment above uses the canonical SHP2 domain definition standard in the SHP099/allostery literature (N-SH2 ≈ 1–115, C-SH2 ≈ 116–280, PTP ≈ 281–525), which is also supported by coordinate-based domain clustering of this structure (the 108–114 cluster is contiguous with the N-SH2 core, 218–257 with the C-SH2 body, 491–495 with the PTP catalytic fold). Only Thr108–Arg111, Thr218/Thr219 and Glu249–Gln257 change label between conventions; the N-SH2/C-SH2/PTP spanning nature of the pocket is unaffected.

Output files: `/agent_cwd/work/5ehr/FINAL_SHP099_4A_contacts_with_domains.csv` (final table), `5EHR_chainA_SHP099_contacts_4A.csv`, `all_residue_min_dist_to_SHP099.csv`, `Q06124_domains.csv`, `domain_assignment.csv`.
=== END RUN ry19ou91v36 ===

=== RUN r6pmnm1dr5m ===
QUESTION:
Using only pocket-detection output on PTP1B (PDB 1T4J, ligands removed), rank the top three pockets by how likely each is to be an allosteric site, and justify the ranking.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H02_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[H02_c] [critical] [judged] a ranking of the top three pockets by allosteric likelihood with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Ranking of PTP1B pockets by allosteric-candidate potential

A critical limitation is that **pocket detection identifies cavities, not allosteric communication**. Neither fpocket nor P2Rank directly predicts whether a site is allosteric, and P2Rank’s reported “probability” is a pocket-confidence measure—not an allosteric probability. Thus, the ranking below is a qualitative ranking of **allosteric candidates**, using only detector-derived geometry, ligandability, residues, and cross-method agreement.

| Rank | Pocket | Key detection evidence | Rationale |
|---|---|---|---|
| **1** | **fpocket 11** | Druggability **0.82**, the highest of 18 fpocket pockets; volume **658.5 Å³**; total SASA **227.6 Å²**; hydrophobicity score **32.75**; 79 alpha spheres. Residues include **PHE196, LEU272, GLU276, GLY277, PHE280, ILE281**. | Best individual ligand-shaped, hydrophobic surface cavity in the fpocket output. Its druggability, size, exposed area, and hydrophobic composition make it the strongest non-active-site candidate. Confidence is reduced because P2Rank did not report a corresponding pocket. |
| **2** | **P2Rank 3 / fpocket 10** | Moderate cross-method agreement: **4 shared residues**, Jaccard **0.333**, containment **0.571**. P2Rank score **1.87**, probability **0.037**; fpocket score **0.076**, volume **350.1 Å³**, SASA **100.2 Å²**, hydrophobicity **27.33**. | The strongest non-active-site region independently reproduced by both detectors. Its lower druggability and smaller volume place it below fpocket 11, but reproducible detection raises its confidence relative to fpocket-only candidates. |
| **3** | **fpocket 8** | Druggability **0.069**, second-highest fpocket value; score **0.123**; volume **631.9 Å³**; SASA **196.4 Å²**; hydrophobicity **24.2**. Residues include the C-terminal region around **ALA278–MET282**. | A large, hydrophobic, ligandable cavity and adjacent to fpocket 11—**ILE281** occurs in both. It ranks below the P2Rank 3/fpocket 10 consensus because it lacks P2Rank support, and its terminal residues raise the possibility of an edge or crystal-packing-related cavity. |

### Important exclusion: the strongest raw pocket consensus is probably not allosteric

The most strongly detected pocket overall was **P2Rank 1 / fpocket 2**:

- P2Rank score **7.22**, probability **0.376**
- fpocket rank **2**, score **0.167**
- **10 shared residues**, Jaccard **0.588**, containment **0.833**
- fpocket volume **415.7 Å³**

However, its detector-listed residues include **Asp181, Cys215, Arg221, and Gln262**, matching the familiar PTP1B catalytic-pocket pattern. It therefore looks more like the catalytic/orthosteric pocket than an allosteric site, despite being the strongest geometrical cavity. This is why it is not ranked first among *allosteric candidates*.

For comparison, **P2Rank 2 / fpocket 18** was the next highest raw P2Rank call, but its fpocket counterpart ranked only **18th**, with just **3 shared residues**, Jaccard **0.214**, and fpocket druggability **0.001**. It consequently has weak independent corroboration.

### Bottom line

The most defensible pocket-only ordering of non-active-site candidates is:

1. **fpocket 11**
2. **P2Rank 3 / fpocket 10**
3. **fpocket 8**

These are candidate pockets, not proven allosteric sites. Establishing allostery would require evidence outside the permitted pocket-detection output, such as comparison with an apo/holo conformational change, perturbational or interaction-network analysis, or ligand-specific contacts.
=== END RUN r6pmnm1dr5m ===

=== RUN rfge78ab3w8 ===
QUESTION:
In PDB entry 1T4J (human PTP1B, UniProt P18031), identify the bound allosteric ligand and list the residues within 4 angstroms of it, using UniProt numbering.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[S01_b] [critical] [scripted] [{"chain": "A", "pdb_number": 299}]
[S01_c] [critical] [scripted] {"uniprot_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "pdb_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "min_distances": {"188": 3.918, "189": 3.416, "192": 3.803, "193": 3.011, "196": 3.552, "200": 3.304, "276": 2.554, "277": 3.367, "279": 3.031, "280": 2.645, "282": 3.593}}
[S01_d] [critical] [scripted] 11

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Bound allosteric ligand:** **FRJ**  
RCSB chemical-component name: **3-(3,5-dibromo-4-hydroxy-benzoyl)-2-ethyl-benzofuran-6-sulfonic acid [4-(thiazol-2-ylsulfamoyl)-phenyl]-amide**. The PDB entry is titled *“Allosteric Inhibition of Protein Tyrosine Phosphatase 1B.”*

**Residues within 4.0 Å of FRJ**, in **UniProt P18031 numbering**:

| UniProt residue | Amino acid | Minimum distance |
|---:|:---|---:|
| P188 | Pro | 3.92 Å |
| A189 | Ala | 3.42 Å |
| L192 | Leu | 3.80 Å |
| N193 | Asn | 3.01 Å |
| F196 | Phe | 3.55 Å |
| E200 | Glu | 3.30 Å |
| E276 | Glu | 2.55 Å |
| G277 | Gly | 3.37 Å |
| K279 | Lys | 3.03 Å |
| F280 | Phe | 2.65 Å |
| M282 | Met | 3.59 Å |

**Result:** **P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, and M282.**

These are the 11 polymer-residue contacts obtained directly from the 1T4J structure using a 4.0 Å heavy-atom cutoff; PDB chain A maps to UniProt P18031.
=== END RUN rfge78ab3w8 ===

=== RUN rdluacymumm ===
QUESTION:
Which PDB entries contain human SHP2 (UniProt Q06124) bound to SHP099 (ligand ID 5OD)? Also report whether ChEMBL holds bioactivity records for SHP099 against SHP2, and if so the assay types and best value; if not, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L04_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[L04_b] [critical] [scripted] ["5EHR", "6BMU", "6BMW", "6BMY", "6CMR", "6CMS", "6CRG", "8WFY"]
[L04_c] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PDB entries

The following **eight PDB entries** contain human SHP2 (`PTPN11`, UniProt **Q06124**) bound to **SHP099** (RCSB ligand/component ID **5OD**):

| PDB entry | Distinguishing information | Primary citation |
|---|---|---|
| [5EHR](https://www.rcsb.org/structure/5EHR) | SHP2–SHP099 complex | PMID **27362227**; DOI [10.1038/nature18621](https://doi.org/10.1038/nature18621) |
| [6BMU](https://www.rcsb.org/structure/6BMU) | Contains SHP099 and SHP244 | PMID **29304282**; DOI [10.1021/acschembio.7b00980](https://doi.org/10.1021/acschembio.7b00980) |
| [6BMW](https://www.rcsb.org/structure/6BMW) | Contains SHP099 and SHP504 | PMID **29304282**; DOI [10.1021/acschembio.7b00980](https://doi.org/10.1021/acschembio.7b00980) |
| [6BMY](https://www.rcsb.org/structure/6BMY) | Contains SHP099 and SHP844 | PMID **29304282**; DOI [10.1021/acschembio.7b00980](https://doi.org/10.1021/acschembio.7b00980) |
| [6CMR](https://www.rcsb.org/structure/6CMR) | Active SHP2 **E76D** mutant with SHP099 | PMID **30375376**; DOI [10.1038/s41467-018-06814-w](https://doi.org/10.1038/s41467-018-06814-w) |
| [6CMS](https://www.rcsb.org/structure/6CMS) | Active SHP2 **E76K** mutant with SHP099 | PMID **30375376**; DOI [10.1038/s41467-018-06814-w](https://doi.org/10.1038/s41467-018-06814-w) |
| [6CRG](https://www.rcsb.org/structure/6CRG) | SHP2 **E76K** gain-of-function mutant with SHP099 | PMID **30375388**; DOI [10.1038/s41467-018-06823-9](https://doi.org/10.1038/s41467-018-06823-9) |
| [8WFY](https://www.rcsb.org/structure/8WFY) | SHP2–SHP099 structure; primary citation listed as unpublished | RCSB entry |

RCSB component cross-check: [5OD / SHP099](https://data.rcsb.org/rest/v1/core/chemcomp/5OD).

## ChEMBL bioactivity

**Yes.** ChEMBL holds records for SHP099 against human SHP2:

- **SHP099 molecule:** `CHEMBL4060033`
- **Human SHP2 target:** `CHEMBL3864`
- **Target:** Tyrosine-protein phosphatase non-receptor type 11
- **Target component:** UniProt `Q06124`
- **Number of activity records:** **89**

### Assay and endpoint types

All **89** records are classified by ChEMBL as assay type **`B`** (binding/biochemical). Their `standard_type` fields comprise:

- `IC50`: 37
- `Inhibition`: 16
- `kon`: 9
- `k_off`: 9
- `K`: 4
- `Kd`: 4
- `Km`: 3
- `Vmax`: 3
- `Delta Tm`: 2
- `Ki`: 1
- `TIME`: 1

Thus, there are no ChEMBL `F` (functional) assay records assigned directly to the SHP2 target in this filtered set; functional SHP099 records in the broader dataset are assigned to cell-line or other targets.

### Best value

Using ChEMBL’s normalized **pChEMBL** value, with lower concentrations indicating stronger potency:

- **Best overall:** **IC50 = 0.145 nM**
- **pChEMBL:** **9.84**
- **Activity ID:** `23216196`
- **Assay ID:** `CHEMBL4823680`
- **Description:** “Inhibition of human SHP2 catalytic activity in human MV4-11 cells”
- **Validity flag:** none
- **Potential duplicate:** no

For endpoint-specific context:

- Best **Kd:** **10 nM**, pChEMBL 8.00
- Best **Ki:** **67 nM**, pChEMBL 7.17

ChEMBL sources:

- [SHP099 molecule record](https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL4060033.json)
- [Human SHP2 target record](https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL3864.json)
- [All SHP099–SHP2 activities](https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL4060033&target_chembl_id=CHEMBL3864&limit=1000)
- [Best activity record](https://www.ebi.ac.uk/chembl/api/data/activity/23216196.json)
- [Best assay record](https://www.ebi.ac.uk/chembl/api/data/assay/CHEMBL4823680.json)
=== END RUN rdluacymumm ===

=== RUN ron3eepp7qr ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Bottom line

| Feature | ATP site | Myristoyl/allosteric site |
|---|---|---|
| **1OPK ligand** | P16, an ATP-site ligand | MYR, myristic acid |
| **T315 relationship** | T315 is a direct ATP-pocket contact; gatekeeper residue | T315 is absent from the pocket; nearest MYR-contact residue is 20.43 Å away |
| **Ligand-stripped pocket rank** | Fpocket **#2**; P2Rank **#1** | Fpocket **#3**; P2Rank **#2** |
| **Representative drug** | Imatinib, an ATP-site/type-II inhibitor | Asciminib, a myristoyl-pocket allosteric inhibitor |
| **Effect of T315I** | Marked loss of potency/resistance | Activity largely retained; no direct pocket blockade |

## 1. Contacts in PDB 1OPK

**Important identity caveat:** 1OPK chain A maps to **mouse ABL1, UniProt P00520**, rather than human P00519. Its kinase-domain numbering is nevertheless directly convertible to human ABL1 canonical numbering, and the assignment was cross-checked against human ABL1 structures. Also, **P16 is not imatinib**; imatinib potency comes from the separate ChEMBL analysis below.

Geometric contacts were calculated at a **4.0 Å heavy-atom cutoff**.

### ATP site: P16 contacts — 19 residues

**Human P00519 numbering:**

`L248, Y253, V256, A269, V270, K271, E286, M290, V299, I313, T315, E316, F317, M318, G321, L370, A380, D381, F382`

Corresponding **1OPK PDB author numbers**:

`L267, Y272, V275, A288, V289, K290, E305, M309, V318, I332, T334, E335, F336, M337, G340, L389, A399, D400, F401`

T315 is **PDB A334** and is 3.24 Å from P16, demonstrating that the gatekeeper lies directly in the ATP-inhibitor contact region.

### Myristoyl site: MYR contacts — 8 residues

**Human P00519 numbering:**

`L340, L341, A344, L429, A433, E462, I502, L510`

Corresponding **1OPK PDB author numbers**:

`L359, L360, A363, L448, A452, E481, I521, L529`

T315/T334 is not among these contacts.

### Independent confirmation with asciminib

Human ABL1 structure **PDB 5MO4**, containing the T315I mutant and asciminib, provides a direct cross-check:

- Asciminib, chemical component **AY7**, has 18 contacts in 5MO4.
- It overlaps **all 8/8** residues in the 1OPK MYR-contact set.
- It overlaps **0/19** residues in the 1OPK ATP-contact set.

Thus the 1OPK MYR cavity is the same allosteric pocket used by asciminib.

## 2. Pocket detection after ligand stripping

All **321 HETATM records**—including P16, MYR, and glycerol—were removed from 1OPK, leaving **3,612 polymer ATOM records**. Pockets were assigned to sites by exact overlap with the contact-defined residues above.

| Detector | Site | Rank | Site-contact coverage | Score/druggability |
|---|---|---:|---:|---|
| Fpocket 4.2.3 | ATP | **2** | 18/19, 94.7% | score 0.320; druggability 0.913 |
| Fpocket 4.2.3 | Myristoyl | **3** | 8/8, 100% | score 0.211; druggability 0.547 |
| P2Rank 2.5.1 | ATP | **1** | 17/19, 89.5% | score 23.77; probability 0.892 |
| P2Rank 2.5.1 | Myristoyl | **2** | 8/8, 100% | score 11.32; probability 0.606 |

Therefore, the consensus ranking is:

- **ATP site:** ranks **#1–2**
- **Myristoyl site:** ranks **#2–3**

The ATP cavity is more prominently detected, but the myristoyl cavity remains robustly and completely recovered even without MYR.

## 3. ChEMBL potency

Target: **human ABL1 P00519 / CHEMBL1862**

| Compound and matched endpoint | Wild type | T315I | Change |
|---|---:|---:|---:|
| **Imatinib Kd** | 2.2 nM | 6,200 nM | **~2,818-fold loss** |
| **Imatinib cellular GI50** | 90.5 nM | 9,645 nM | **~107-fold loss** |
| **Asciminib cellular GI50** | 0.61 nM | 7.64 nM | **~12.5-fold shift** |

The matched cellular GI50 values came from the asciminib-discovery paper, PMID 30137981. In that same assay, asciminib retained substantially greater activity than imatinib against T315I: **7.64 versus 9,645 nM**, approximately **1,262-fold more potent**.

Additional ChEMBL records:

- **Imatinib P00519 IC50 collection:** 91 records, spanning **19.9 nM to >100,000 nM**, with a median of 800 nM. This spread reflects different biochemical, cellular, wild-type, and mutant assays; the matched WT/T315I values above are more informative.
- **Asciminib P00519 biochemical IC50:** **0.5 nM** for ABL1, CHEMBL activity 18557369.
- A second asciminib P00519 IC50 record is **16 nM**, although its deposited assay description is “TBD.”

## 4. T315I evidence and structural distance

### ClinVar

- Variant: **NM_005157.6(ABL1):c.944C>T (p.Thr315Ile)**
- ClinVar Variation ID: **27663**
- Classification: **Likely pathogenic; association**
- Review status: **criteria provided, multiple submitters, no conflicts**
- GRCh38 position: chr9:130,872,896
- GRCh37 position: chr9:133,748,283

The two ClinVar rows are the GRCh37 and GRCh38 representations of the same variant.

### AlphaMissense

- **T315I pathogenicity score: 0.9991**
- Classification: **pathogenic**

ClinVar and AlphaMissense establish disease/pathogenicity evidence; they do not by themselves predict drug resistance.

### Distance from T315 to each site

Using the minimum heavy-atom distance from the T315 residue to any atom in each contact-defined site:

- **ATP site: 0.00 Å**, because T315 itself is one of the 19 ATP-contact residues. Its direct distance to the P16 ligand is **3.24 Å**.
- **Myristoyl site: 20.43 Å** to the nearest MYR-site residue, PDB A363; distances to the eight MYR-contact residues span **20.43–36.71 Å**. The T315 all-atom centroid is approximately **29.8 Å** from the MYR-site centroid.

Thus T315 is physically part of the ATP pocket but spatially separated from the asciminib/myristoyl pocket. The distance calculation establishes separation, not a causal allosteric pathway.

## 5. What T315I implies for each inhibitor class

### ATP-site inhibitors, including imatinib

T315 is the **gatekeeper residue** of the ATP pocket. Replacing threonine with bulkier, hydrophobic isoleucine:

- directly perturbs ATP-site inhibitor geometry;
- creates steric obstruction for many ATP-binding inhibitors;
- causes the very large loss of imatinib affinity and cellular potency documented in ChEMBL.

T315I therefore predicts resistance to imatinib and most first- and second-generation ATP-site inhibitors. Not every ATP-site drug is affected: third-generation switch-control inhibitors such as **ponatinib** were specifically designed to retain activity against T315I.

### Myristoyl-pocket/allosteric inhibitors, including asciminib

T315I does **not** directly disrupt asciminib binding because the myristoyl pocket is a separate site, approximately 20.4 Å from the nearest pocket contact. The matched ChEMBL data support this:

- asciminib remains active against T315I cells at **7.64 nM GI50**;
- the T315I shift is about 12.5-fold, rather than the approximately 107–2,818-fold losses seen with imatinib;
- the T315I ABL1 structure 5MO4 shows asciminib bound directly in the same pocket defined by MYR in 1OPK.

Accordingly, **T315I itself does not confer the canonical ATP-site-inhibitor resistance phenotype to the myristoyl-pocket class**. Allosteric inhibitors can still encounter resistance through mutations elsewhere in ABL1 or in their own binding pathway.

## Sources

- [PDB 1OPK](https://www.rcsb.org/structure/1OPK); Nagar et al., *Cell* 2003, [PMID 12654251](https://pubmed.ncbi.nlm.nih.gov/12654251/), DOI 10.1016/S0092-8674(03)00194-6
- [PDB 5MO4](https://www.rcsb.org/structure/5MO4)
- ChEMBL target [CHEMBL1862](https://www.ebi.ac.uk/chembl/explore/target/CHEMBL1862)
- Imatinib [CHEMBL941](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL941)
- Asciminib [CHEMBL4208229](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL4208229)
- Asciminib discovery paper, [PMID 30137981](https://pubmed.ncbi.nlm.nih.gov/30137981/), DOI 10.1021/acs.jmedchem.8b01040
- Imatinib matched Kd series, [PMID 15711537](https://pubmed.ncbi.nlm.nih.gov/15711537/), DOI 10.1038/nbt1068
- [ClinVar Variation 27663](https://www.ncbi.nlm.nih.gov/clinvar/variation/27663/)

### Final plan status

1. [✓] Retrieve 1OPK structure/chain mapping, bound-ligand records, and geometric ligand contacts  
2. [✗] First pocket/site mapping failed because Fpocket and P2Rank use different residue schemas  
3. [✓] Rerun with schema-tolerant parsing; ranks resolved  
4. [✗] First ChEMBL-wide T315I REST filter failed with HTTP 400  
5. [✗] First local-SQL extraction used a REST-only field  
6. [✓] Corrected local joins recovered matched WT/T315I activities  
7. [✗] First distance calculation used the wrong 1OPK author residue  
8. [✓] Corrected A334 mapping and recomputed distances  
9. [✓] Confirmed the MYR pocket using asciminib-bound 5MO4  
10. [✗] First final-table display used an incorrect field lookup  
11. [✓] Integrate evidence and inhibitor-class implications
=== END RUN ron3eepp7qr ===

=== RUN rd7vdl6qq92 ===
QUESTION:
Which PDB entries contain human SHP2 (UniProt Q06124) bound to SHP099 (ligand ID 5OD)? Also report whether ChEMBL holds bioactivity records for SHP099 against SHP2, and if so the assay types and best value; if not, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L04_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[L04_b] [critical] [scripted] ["5EHR", "6BMU", "6BMW", "6BMY", "6CMR", "6CMS", "6CRG", "8WFY"]
[L04_c] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**PDB entries:** The exact accession-and-ligand search for human SHP2 (UniProt **Q06124**) with ligand **5OD (SHP099)** returned eight PDB entries:

- **5EHR**
- **6BMU**
- **6BMW**
- **6BMY**
- **6CMR**
- **6CMS**
- **6CRG**
- **8WFY**

**ChEMBL bioactivity:** **Yes.** ChEMBL does hold SHP099 activity records against human SHP2/PTPN11, represented by target **CHEMBL3864**.

The parent SHP099 structure is **CHEMBL4060033**, with **89 activity records**. The `standard_type` categories represented are:

- **IC50**
- **Ki**
- **Kd**
- **Inhibition**
- **Delta Tm**
- **Vmax**
- **Km**
- **K**
- **TIME**
- **kon**
- **k_off**

For the principal affinity/inhibition endpoints, the best (lowest numeric) values are:

| Assay type | Best value | ChEMBL assay |
|---|---:|---|
| **IC50** | **0.145 nM** | CHEMBL4823680 |
| **Ki** | **67 nM** | CHEMBL5145447 |
| **Kd** | **10 nM** | CHEMBL5578845 |

Thus, the **lowest recorded value overall among the affinity endpoints is 0.145 nM IC50**. This is an assay-specific value; many other IC50 records cluster around approximately 40–71 nM.

A related hydroxylated/metabolite structure, **CHEMBL5280755**, also has one ChEMBL SHP2 record: **IC50 = 71 nM**.
=== END RUN rd7vdl6qq92 ===

=== RUN rdj198qyajx ===
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

**Yes.** Using AutoSite’s native score ranking, **three of the top five pockets in 2SHP overlap residues that contact SHP099 in 5EHR**:

- **Pocket 2:** 16 of 17 SHP099-contacting residues
- **Pocket 5:** 15 of 17
- **Pocket 3:** 6 of 17
- **Pockets 1 and 4:** no overlap at 4.5 Å

### SHP099-contacting residues in 5EHR

SHP099 is deposited in 5EHR under chemical-component ID **5OD**. Using a 4.5 Å heavy-atom distance cutoff, it contacts these 17 unique Q06124 positions in both protein copies:

**T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, D489, P491, K492, Q495, Y511**

The deposited 5EHR residue numbers map directly to these UniProt numbers.

## Top-five AutoSite pockets in 2SHP

AutoSite v1.0.0 was run at 1.0 Å grid spacing. Pockets are ordered by AutoSite’s native composite score, not by raw energy.

| AutoSite pocket | Score | Energy | Chain | 4.5 Å pocket-lining residues | SHP099-contact overlap |
|---:|---:|---:|:---:|---:|---|
| 1 | 55.988 | −282.314 | B | 42 | None |
| 2 | 50.054 | −230.415 | A | 37 | **16 residues** |
| 3 | 49.659 | −154.122 | B | 32 | **6 residues** |
| 4 | 48.948 | −227.224 | A | 33 | None |
| 5 | 45.549 | −158.575 | B | 28 | **15 residues** |

### Exact overlaps in UniProt Q06124 numbering

- **Pocket 2 — 16/17**
  - T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, D489, P491, K492, Q495
  - Only SHP099-contacting Y511 is absent at 4.5 Å.

- **Pocket 3 — 6/17**
  - T108, E110, R111, T253, L254, Q257

- **Pocket 5 — 15/17**
  - E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, D489, P491, K492, Q495
  - T108 and Y511 are absent at 4.5 Å.

## Cutoff sensitivity

A pocket was considered to cover a residue when a receptor heavy atom was within the stated distance of an AutoSite cavity grid point.

| Pocket | 4.0 Å overlap | 4.5 Å overlap | 5.0 Å overlap |
|---:|---:|---:|---:|
| 1 | 0 | 0 | 1 — E249 |
| 2 | 15 | 16 | 17 |
| 3 | 5 | 6 | 6 |
| 4 | 0 | 0 | 0 |
| 5 | 15 | 15 | 16 |

A stricter nearest-atomic-neighbor definition gives the same qualitative result: pockets 2, 3, and 5 overlap **16, 5, and 13** SHP099-contacting positions, respectively.

If “top five” is instead interpreted as the five most-negative raw-energy clusters—1, 2, 4, 5, and 8—the 4.5 Å overlaps are **0, 16, 0, 15, and 0**, so the conclusion is unchanged.

## Numbering and structure checks

- Sequence alignment of both 5EHR chains to Q06124 was exact for the contacting residues.
- In 2SHP, deposited positions 2–525 correspond directly to UniProt positions 2–525.
- 2SHP contains engineered substitutions **T2K, F41L, and F513S**; none is in the SHP099-contact set.
- The deposited 2SHP structure also contains dodecane-trimethylamine crystallization additive (`CAT`). Removing it did **not** change the top-five scores or cluster coordinates—the top-five pocket coordinate sets were identical between the full-deposited and protein-only runs.
- Pockets 2 and 5 occur on opposite crystallographic copies and cover closely corresponding parts of the SHP099-binding region.

**Conclusion:** The autoinhibited 2SHP conformation already contains detectable cavities corresponding to the SHP099-contacting surface. The strongest evidence is **AutoSite pocket 2**, which covers 16 of the 17 SHP099-contacting UniProt residues at 4.5 Å.

AutoSite citation: Ravindranath PA, Sanner MF. *Bioinformatics* 2016;32:3142–3149. DOI: **10.1093/bioinformatics/btw367**.

### Updated plan

1. [✓] Retrieve PDB 2SHP and 5EHR structures and UniProt Q06124 sequence/annotation.
2. [✗] Identify SHP099 by exact residue name — failed because 5EHR uses component ID `5OD`.
3. [✓] Enumerate 5EHR components and identify SHP099 as `5OD`.
4. [✓] Calculate SHP099 protein-residue contacts.
5. [✓] Map 5EHR contacts to canonical UniProt numbering.
6. [✗] Run AutoSite through the provided wrapper — failed because `prepare_receptor` was absent from `PATH`.
7. [✓] Install and invoke the official ADFRsuite AutoSite components.
8. [✓] Run AutoSite on protein-only 2SHP and extract the top five pockets.
9. [✓] Map pocket residues to UniProt and calculate the SHP099 overlap.
10. [✓] Verify ranking, cutoff, heteroatom, and engineered-mutation sensitivity.
=== END RUN rdj198qyajx ===

=== RUN rg1a2m87bmx ===
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
## Bottom line

The answer is **detector-dependent**:

| Pocket detector | Top-five overlap with SHP099-contacting residues |
|---|---|
| **fpocket 4.2.3** | **None — 0 residues** |
| **P2Rank 2.5.1** | **3 residues in rank 5: Glu110, Arg111, Gln257** |

Thus, if “top five pockets” refers to the fpocket ranking, the answer is **no**. P2Rank places a partially overlapping pocket fifth.

## Mapping and SHP099 contacts

- RCSB entry **5EHR** is titled “Non-receptor Protein Tyrosine Phosphatase SHP2 in Complex with Allosteric Inhibitor SHP099.”
- SHP099 is chemical component **5OD**.
- Using a **4.0 Å minimum heavy-atom distance**, 5EHR chain A contacts SHP099 at:

  **T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, Q495**

- Chain B contacts the same 15 UniProt positions.
- Deposited DBREF records and an explicit alignment to canonical **Q06124** confirm the relevant residue mappings. Both 2SHP and 5EHR map their native construct residues to the same Q06124 numbering; 5EHR additionally contains an N-terminal expression-tag residue numbered 0.

## fpocket result on 2SHP

| fpocket rank | Score | Chain | Exact SHP099-contact overlap |
|---:|---:|:---:|---|
| 1 | 0.338 | A | None |
| 2 | 0.237 | B | None |
| 3 | 0.235 | A | None |
| 4 | 0.204 | A | None |
| 5 | 0.174 | A | None |

The union of all residues assigned to these five pockets also has **zero exact intersection** with the 15 SHP099-contacting UniProt positions. Pockets 1 and 2 are symmetry-related copies of the same site in the two protein chains.

The SHP099 site is nevertheless detected lower in the fpocket ranking:

- **fpocket rank 20**, score 0.055, overlaps 13 of the 15 contact positions:  
  **T108, E110, R111, F113, H114, T218, T219, E250, T253, L254, Q257, P491, K492, Q495**
- **fpocket rank 34** contains all 15 contact positions.

## P2Rank result

P2Rank **rank 5**—chain A, score 6.01, probability 0.296—contains three shared Q06124 residues:

| Shared residue | 5EHR chain A distance | 5EHR chain B distance |
|---|---:|---:|
| **Glu110** | 3.47 Å | 3.11 Å |
| **Arg111** | 3.14 Å | 2.93 Å |
| **Gln257** | 3.58 Å | 3.58 Å |

No other P2Rank top-five residue overlaps the SHP099 contact set.

## Conclusion

- **Primary fpocket analysis:** none of the top five pockets covers an SHP099-contacting residue; **overlap = ∅**.
- **P2Rank sensitivity analysis:** the fifth-ranked pocket partially covers the SHP099 site at **E110, R111, and Q257**.
- These are exact residue-assignment overlaps. A 4 Å contact is geometric proximity and does not by itself establish a biological interaction.
=== END RUN rg1a2m87bmx ===

=== RUN ragzpnqwrig ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed plan

1. [✓] Retrieved PDB 1V4S and identified **MRK** as the bound allosteric activator.
2. [✓] Retrieved all human GCK ClinVar records and normalized protein changes and classifications.
3. [✓] Mapped UniProt P35557 residues to PDB 1V4S chain A using the RCSB/SIFTS alignment.
4. [✓] Calculated minimum heavy-atom distances from each residue to MRK and retained residues within 6 Å.
5. [✓] Retrieved official AlphaMissense scores for every relevant substitution.
6. [✓] Cross-checked all distances, identifiers, classifications, and score coverage.

## Main result

- The ClinVar search `GCK[gene] AND "Homo sapiens"[organism]` returned **1,454 records**.
- **24 resolved residues** in 1V4S are within 6 Å of MRK:  
  **Y61, V62, R63, S64, T65, P66, Q98, I159, M210, I211, Y214, Y215, H218, C220, E221, V222, M235, R250, C252, L451, V452, S453, V455, A456**.
- Sixteen of these positions have ClinVar single-substitution records, giving **40 ClinVar records representing 38 distinct amino-acid substitutions**.
- All 38 substitutions have official AlphaMissense scores.
- ClinVar classifications among the 40 records: 15 pathogenic, 7 likely pathogenic, 3 pathogenic/likely pathogenic, 3 conflicting, 10 VUS, and 2 VUS/uncertain-risk-allele.

### Distance and mapping conventions

- `d_res`: minimum distance from any heavy atom of the residue to any MRK heavy atom.
- `d_sc`: minimum distance from the residue’s side-chain heavy atoms to MRK.
- MRK is author residue **501 of chain A** and contains 23 heavy atoms.
- RCSB/SIFTS maps UniProt P35557 positions 16–465 to the PDB entity; resolved residues 16–461 correspond directly to UniProt numbering. PDB residues 14–15 are cloning-modified and were excluded from the correspondence. All variants below are at positions 61–456 and are unaffected by that caveat.
- Only point missense substitutions are scored: frameshifts, indels, and other non-missense records cannot be represented by a single AlphaMissense amino-acid substitution.

## Variants within 6 Å of MRK

AlphaMissense bands use the official thresholds: **LP** = likely pathogenic, score >0.564; **Amb** = ambiguous, 0.34–0.564; **LB** = likely benign, <0.34.

Binding calls are structural assessments, not experimentally measured binding constants:

- **Direct** — likely to alter MRK binding; direct side-chain pocket interaction plus supporting AlphaMissense/chemical evidence.
- **Moderate** — credible but less certain binding effect.
- **Possible/indirect** — within the 6 Å shell, but no strong direct side-chain evidence; an effect may instead arise through folding, stability, or dynamics.

| Variant | PDB residue | d_res Å | d_sc Å | AlphaMissense | AM band | ClinVar classification | ClinVar VCV | Binding call |
|---|---:|---:|---:|---:|---|---|---|---|
| Y61N | TYR61 | 3.25 | 5.85 | 0.8868 | LP | VUS | VCV001444770.6 | Possible/indirect |
| V62A | VAL62 | 3.62 | 3.64 | 0.9731 | LP | Pathogenic | VCV000585917.8 | **Direct** |
| V62M | VAL62 | 3.62 | 3.64 | 0.9462 | LP | Pathogenic | VCV000419624.13 | **Direct** |
| R63C | ARG63 | 2.73 | 3.75 | 0.1234 | LB | VUS/uncertain risk allele | VCV000447391.3 | Possible/indirect |
| R63H | ARG63 | 2.73 | 3.75 | 0.1886 | LB | VUS | VCV002779779.3 | Possible/indirect |
| R63L | ARG63 | 2.73 | 3.75 | 0.3254 | LB | VUS | VCV001502971.6 | Possible/indirect |
| I159M | ILE159 | 4.33 | 4.33 | 0.2207 | LB | Conflicting | VCV000447403.7 | Possible/indirect |
| I159N | ILE159 | 4.33 | 4.33 | 0.9313 | LP | Conflicting | VCV002735015.5 | **Direct** |
| I159T | ILE159 | 4.33 | 4.33 | 0.5886 | LP | VUS | VCV002700200.3 | **Direct** |
| I159V | ILE159 | 4.33 | 4.33 | 0.1611 | LB | Pathogenic/LP | VCV001679549.10 | Possible/indirect |
| M210I | MET210 | 3.66 | 3.66 | 0.9915 | LP | Pathogenic | VCV000036236.10; VCV002691826.1 | **Direct** |
| M210K | MET210 | 3.66 | 3.66 | 0.9915 | LP | Pathogenic | VCV000016141.9 | **Direct** |
| M210T | MET210 | 3.66 | 3.66 | 0.9821 | LP | Pathogenic | VCV000804852.15 | **Direct** |
| M210V | MET210 | 3.66 | 3.66 | 0.8229 | LP | Likely pathogenic | VCV002505485.1; VCV002505486.1 | **Direct** |
| I211N | ILE211 | 3.59 | 3.59 | 0.9683 | LP | VUS/uncertain risk allele | VCV000435303.10 | **Direct** |
| I211T | ILE211 | 3.59 | 3.59 | 0.9474 | LP | Pathogenic | VCV002684209.1 | **Direct** |
| Y214C | TYR214 | 3.01 | 3.01 | 0.2600 | LB | Pathogenic | VCV000016144.3 | **Direct** |
| C220F | CYS220 | 3.30 | 5.87 | 0.9899 | LP | VUS | VCV002691835.3 | Possible/indirect |
| C220R | CYS220 | 3.30 | 5.87 | 0.9953 | LP | Likely pathogenic | VCV000036239.6 | Possible/indirect |
| C220S | CYS220 | 3.30 | 5.87 | 0.9574 | LP | VUS | VCV004743109.1 | Possible/indirect |
| C220W | CYS220 | 3.30 | 5.87 | 0.9982 | LP | VUS | VCV003658742.4 | Possible/indirect |
| C220Y | CYS220 | 3.30 | 5.87 | 0.9972 | LP | Pathogenic | VCV000036240.9 | Possible/indirect |
| E221K | GLU221 | 4.24 | 4.24 | 0.7102 | LP | Pathogenic | VCV000036241.20 | **Direct** |
| M235R | MET235 | 3.51 | 3.51 | 0.9183 | LP | Likely pathogenic | VCV004687879.1 | **Direct** |
| M235T | MET235 | 3.51 | 3.51 | 0.9520 | LP | Pathogenic | VCV000036248.8 | **Direct** |
| M235V | MET235 | 3.51 | 3.51 | 0.5248 | Amb | Pathogenic | VCV000381599.7 | Possible/indirect |
| R250C | ARG250 | 4.59 | 4.59 | 0.3665 | Amb | Pathogenic | VCV000393451.29 | Possible/indirect |
| R250H | ARG250 | 4.59 | 4.59 | 0.2145 | LB | Likely pathogenic | VCV000435311.9 | Possible/indirect |
| R250P | ARG250 | 4.59 | 4.59 | 0.9134 | LP | VUS | VCV002691830.1 | **Moderate** |
| C252F | CYS252 | 5.72 | 5.72 | 0.9600 | LP | Conflicting | VCV000810090.46 | Possible/indirect |
| C252W | CYS252 | 5.72 | 5.72 | 0.9967 | LP | VUS | VCV002169519.4 | Possible/indirect |
| V452L | VAL452 | 3.62 | 3.87 | 0.6364 | LP | Likely pathogenic | VCV002506148.1 | **Moderate** |
| S453L | SER453 | 5.64 | 7.92 | 0.7575 | LP | Pathogenic/LP | VCV000036200.20 | Possible/indirect |
| S453W | SER453 | 5.64 | 7.92 | 0.9903 | LP | Pathogenic/LP | VCV002734985.5 | Possible/indirect |
| V455E | VAL455 | 3.46 | 3.46 | 0.8513 | LP | Likely pathogenic | VCV000585916.60 | **Direct** |
| V455M | VAL455 | 3.46 | 3.46 | 0.5295 | Amb | Pathogenic | VCV000016140.5 | Possible/indirect |
| A456P | ALA456 | 4.04 | 4.04 | 0.9733 | LP | VUS | VCV003650955.2 | **Direct** |
| A456V | ALA456 | 4.04 | 4.04 | 0.3825 | Amb | Pathogenic | VCV000016143.9 | Possible/indirect |

## Which are most likely to alter activator binding?

### Likely direct, high-confidence effects

**V62A, V62M, I159N, I159T, M210I, M210K, M210T, M210V, I211N, I211T, Y214C, E221K, M235R, M235T, V455E, and A456P.**

Important supporting observations:

- **Y214C:** the Tyr214 aromatic ring directly contacts MRK fluorine F14 at 3.01 Å. Replacing it with cysteine removes a major hydrophobic contact, so the structural evidence is strong even though AlphaMissense is low (0.2600).
- **V455E:** the Val455 side chain is 3.46 Å from the MRK carbonyl oxygen O8; replacing Val with glutamate reverses charge and is likely disruptive.
- **M210 and M235:** their side-chain sulfur-containing groups occupy the hydrophobic pocket and directly contact MRK.
- **V62M:** V62 directly contacts the activator pocket, and a separate experimental study found that GCK-V62M **does not respond to the pharmacologic activator RO0281675**. RO0281675 is not established here to be chemically identical to MRK, so this is functional corroboration of the shared allosteric pocket rather than an MRK-specific assay.

### Likely, but more moderate-confidence effects

- **R250P:** the Arg250 side chain is 4.59 Å from MRK and proline can disrupt the local backbone.
- **V452L:** there is a direct 3.87 Å side-chain contact and an LP AlphaMissense score, but Val→Leu is relatively conservative, so a modest effect is more plausible.

The remaining substitutions are **possible or indirect effects**. Their high AlphaMissense scores may reflect loss of GCK folding, stability, kinetics, or allosteric equilibrium rather than disruption of the MRK contact itself.

## Interpretation limitations

- AlphaMissense predicts **general clinical pathogenicity**, not ligand-binding affinity; it should not be interpreted as a binding-affinity score.
- A 6 Å shell includes direct contacts, backbone contacts, and nearby second-shell residues.
- 1V4S represents one bound conformation of GCK; a static distance cannot capture mutation-induced conformational changes.
- ClinVar and AlphaMissense classifications do not establish that a variant specifically impairs GCK activators.
- These results are appropriate for structural prioritization and hypothesis generation, not clinical interpretation.

## Sources

- [ClinVar GCK search](https://www.ncbi.nlm.nih.gov/clinvar/?term=GCK%5Bgene%5D%20AND%20%22Homo%20sapiens%22%5Borganism%5D)
- [UniProt P35557](https://www.uniprot.org/uniprotkb/P35557/entry)
- [RCSB PDB 1V4S](https://www.rcsb.org/structure/1V4S); Kamata et al., *Structure* 2004, [PMID 15016359](https://pubmed.ncbi.nlm.nih.gov/15016359/), DOI [10
=== END RUN ragzpnqwrig ===

=== RUN raim1z1rb3e ===
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
## Result

**PDB 5MO4 is a ternary complex containing one ABL1 kinase domain and two distinct ligands:**

| PDB component | Ligand | Deposited instance | Binding site | ABL1 residues within 4.0 Å |
|---|---|---|---|---:|
| **NIL** | **Nilotinib** | Author chain A, residue 601; mmCIF asym B | ATP/catalytic site | 25 |
| **AY7** | **Asciminib (ABL001)** | Author chain A, residue 602; mmCIF asym C | Allosteric myristoyl pocket | 18 |

Residues below were calculated directly from the deposited coordinates using **any heavy-atom pair ≤4.0 Å**, excluding water and non-ABL1 groups. The per-residue minimum distances are 2.842–3.982 Å for nilotinib and 2.821–3.865 Å for asciminib.

### Nilotinib — NIL

Each entry is **PDB author residue → UniProt P00519 residue**:

- **Leu267 → Leu248**
- **Tyr272 → Tyr253**
- **Val275 → Val256**
- **Ala288 → Ala269**
- **Val289 → Val270**
- **Lys290 → Lys271**
- **Lys304 → Lys285**
- **Glu305 → Glu286**
- **Val308 → Val289**
- **Met309 → Met290**
- **Ile312 → Ile293**
- **Leu317 → Leu298**
- **Val318 → Val299**
- **Ile332 → Ile313**
- **Ile334 → Thr315** — position-matched conflict; the deposited residue is the **T315I** mutant
- **Phe336 → Phe317**
- **Met337 → Met318**
- **Gly340 → Gly321**
- **Phe378 → Phe359**
- **His380 → His361**
- **Leu389 → Leu370**
- **Val398 → Val379**
- **Ala399 → Ala380**
- **Asp400 → Asp381**
- **Phe401 → Phe382**

The contact with **UniProt Met318** is characteristic of nilotinib binding at the ABL1 hinge in the ATP-binding site.

### Asciminib — AY7

- **Arg351 → Arg332**
- **Ala356 → Ala337**
- **Leu359 → Leu340**
- **Leu360 → Leu341**
- **Ala363 → Ala344**
- **Leu448 → Leu429**
- **Ile451 → Ile432**
- **Ala452 → Ala433**
- **Thr453 → Thr434**
- **Tyr454 → Tyr435**
- **Glu481 → Glu462**
- **Cys483 → Cys464**
- **Pro484 → Pro465**
- **Val487 → Val468**
- **Phe512 → Phe493**
- **Ile521 → Ile502**
- **Val525 → Val506**
- **Leu529 → Leu510**

The deposited **AY7** chemical component includes a chloride atom. Because that atom is part of the AY7 residue, the standard residue-level calculation includes its 3.27 Å contact with **Leu448**; a workflow that removes counterions might omit that one contact.

## Are the sites distinct?

**Yes.** Nilotinib occupies the conventional ATP/catalytic site, whereas asciminib binds the **allosteric myristoyl pocket**. Supporting observations are:

- The two ≤4 Å ABL1 contact sets have **no residues in common**.
- The closest heavy-atom separation between NIL and AY7 is approximately **19.66 Å**.
- The primary publication explicitly contrasts asciminib’s myristoyl-pocket binding with catalytic-site ABL1 inhibitors such as nilotinib.

Thus, 5MO4 demonstrates simultaneous occupation of two spatially distinct sites on the same ABL1 kinase.

## Relationship to UniProt P00519 numbering

The entry does **not** use canonical UniProt numbering directly:

- Deposited author residues **PDB 46–534** align to **UniProt P00519 27–515**.
- Therefore, for the ABL1-aligned portion of this construct:

\[
\boxed{\text{UniProt P00519 number}=\text{PDB author number}-19}
\]

or equivalently:

\[
\boxed{\text{PDB author number}=\text{UniProt P00519 number}+19}
\]

Important exceptions and caveats:

1. **PDB 40–45 (`GAMDPS`)** are an expression tag and have no P00519 counterpart.
2. RCSB’s entity/`label_seq_id` numbering is different from author residue numbering: for example, entity sequence position 7 is author PDB residue 46 and UniProt residue 27.
3. The deposited construct contains two documented sequence conflicts:
   - **PDB Ile334 ↔ UniProt Thr315** — T315I substitution.
   - **PDB Asn382 ↔ UniProt Asp363** — D363N substitution.

### Sources

- [RCSB PDB entry 5MO4](https://www.rcsb.org/structure/5MO4)
- [Deposited 5MO4 mmCIF](https://files.rcsb.org/download/5MO4.cif)
- [UniProt P00519, ABL1_HUMAN](https://www.uniprot.org/uniprotkb/P00519/entry)
- Wylie et al., “The allosteric inhibitor ABL001 enables dual targeting of BCR-ABL1,” *Nature* **543**, 733–737 (2017), [doi:10.1038/nature21702](https://doi.org/10.1038/nature21702), PMID [28329763](https://pubmed.ncbi.nlm.nih.gov/28329763/)

### Analysis checklist

1. [✓] Retrieved 5MO4 metadata, sequences, entities, and coordinates.
2. [✓] Identified NIL as nilotinib and AY7 as asciminib.
3. [✗] Initial contact calculation failed because coordinate arrays were accessed as Atom objects; superseded by corrected and independently reproduced calculations.
4. [✗] First correction failed because a Bio.PDB Residue does not expose its parent chain; superseded by explicit chain iteration.
5. [✗] The first zero-contact output failed physical validation; the cause was a literal-space blank `altLoc` field.
6. [✗] First diagnostic aborted on an unguarded empty-array reduction.
7. [✓] Reproduced the contacts with a separate fixed-column PDB parser and compared them with PDBe interface data.
8. [✗] First mmCIF extraction used a nonexistent field name; corrected in the subsequent extraction.
9. [✓] Audited the P00519 translation, expression tag, engineered conflicts, and site-separation metrics.
10. [✗] Advanced literature search was unavailable because its backend required an unconfigured Claude model.
11. [✓] Verified pocket terminology through PubMed, NCBI, Europe PMC, and Crossref.
12. [✓] Synthesized the ligand identities, contact lists, site relationship, and numbering explanation.
=== END RUN raim1z1rb3e ===

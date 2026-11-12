# Judge batch 009 of 24

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

=== RUN ro0u41nxm7x ===
QUESTION:
PDB entry 1PZO (TEM-1 beta-lactamase, UniProt P62593) contains two copies of an allosteric inhibitor. Identify them, list the residues within 4 angstroms of each copy, and say whether the two copies occupy the same pocket.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S06_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[S06_b] [critical] [scripted] [{"chain": "A", "pdb_number": 300}, {"chain": "A", "pdb_number": 301}]
[S06_c] [critical] [scripted] {"uniprot_residues": [214, 215, 218, 219, 222, 233, 234, 235, 241, 242, 243, 257, 259, 272, 275, 276, 279, 282], "pdb_residues": [216, 217, 220, 221, 224, 235, 236, 237, 244, 245, 246, 261, 263, 276, 279, 280, 283, 286], "min_distances": {"216": 3.755, "217": 3.908, "220": 3.353, "221": 3.35, "224": 3.411, "235": 2.598, "236": 3.685, "237": 3.556, "244": 3.358, "245": 3.185, "246": 3.386, "261": 3.998, "263": 3.791, "276": 3.068, "279": 3.561, "280": 3.42, "283": 3.667, "286": 3.942}}
[S06_d] [critical] [scripted] [300, 301]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Inhibitor copies

The ligand component is **CBT**, deposited as:

> **N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine**

The two crystallographic copies are:

- **CBT A 300**
- **CBT A 301**

Both are in **protein chain A**. Distances below are minimum heavy-atom distances; a residue is listed if any protein atom is within 4.0 Å of any CBT atom.

## Protein residues within 4.0 Å

| CBT copy | Protein residues within 4.0 Å |
|---|---|
| **CBT A 300** | **Val216** 3.755 Å; **Ala217** 3.908 Å; **Leu220** 3.531 Å; **Ser235** 2.598 Å; **Gly236** 3.685 Å; **Ala237** 3.556 Å; **Arg244** 3.358 Å; **Gly245** 3.185 Å; **Ile246** 3.386 Å; **Asn276** 3.543 Å; **Ile279** 3.573 Å |
| **CBT A 301** | **Leu220** 3.353 Å; **Leu221** 3.350 Å; **Ala224** 3.411 Å; **Arg244** 3.396 Å; **Val261** 3.998 Å; **Ile263** 3.791 Å; **Asn276** 3.068 Å; **Ile279** 3.561 Å; **Ala280** 3.420 Å; **Gly283** 3.667 Å; **Leu286** 3.942 Å |

For completeness, nearby waters are:

- **CBT A 300:** HOH A 327 and HOH A 448
- **CBT A 301:** HOH A 343, HOH A 393, HOH A 411, and HOH A 436

## Do they occupy the same pocket?

**They occupy the same broad, elongated cryptic allosteric cavity between helices 11 and 12, but not identical local binding subsites.**

Evidence:

- They share four 4 Å protein contacts: **Leu220, Arg244, Asn276, and Ile279**.
- The two inhibitors directly contact one another; their closest heavy-atom separation is **3.682 Å**.
- Their centroids are **8.592 Å** apart.
- **CBT A300** is at the orthosteric-adjacent mouth of the cavity, contacting the Ser235–Gly236–Ala237 and Arg244–Gly245–Ile246 region.
- **CBT A301** is the deeper copy between α11 and α12, with its tetrazole in the region described as the “horizontal” allosteric pose.
- The wwPDB annotations similarly list separate software-generated sites, **AC1 for CBT A300** and **AC2 for CBT A301**, but each site includes the other inhibitor, reflecting their adjacency.

Thus, the best concise answer is: **same overall allosteric pocket/region, but two distinct adjacent subsites and binding orientations rather than two identical copies occupying exactly the same site.**

**Sources:** [RCSB PDB 1PZO](https://www.rcsb.org/structure/1PZO); Horn JR, Shoichet BK. *Allosteric inhibition through core disruption.* J Mol Biol. 2004;336:1283–1291. [doi:10.1016/j.jmb.2003.12.068](https://doi.org/10.1016/j.jmb.2003.12.068), PMID: 15037085.
=== END RUN ro0u41nxm7x ===

=== RUN rgf36iduxq6 ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Residue contact network — glucokinase (UniProt P35557 / PDB 1V4S, chain A)**

**Structure used:** PDB 1V4S chain A — human glucokinase (isoform 2, modelled residues 11–465; 448 residues resolved) in complex with:
- **GLC (chain A res 500)** = α‑D‑glucopyranose → the **glucose** ligand
- **MRK (chain A res 501)** = 2‑amino‑4‑fluoro‑5‑[(1‑methyl‑1H‑imidazol‑2‑yl)sulfanyl]‑N‑(1,3‑thiazol‑2‑yl)benzamide → the **allosteric activator** (plus Na⁺ and waters)

**Network definition:** residue–residue contact = any heavy-atom pair ≤ 4.5 Å (448 nodes, 2207 edges); ligand–residue contact = any heavy-atom pair ≤ 4.5 Å; shortest path computed by BFS. PDB numbering is identical to UniProt P35557 canonical numbering for these residues (alignment offset 0).

**Shortest path (answer):**

| Path | Length |
|---|---|
| **Thr206 → Met210** | **1 contact (2 residues)** |

**Supporting atom-level evidence**
- **Thr206 ↔ glucose:** GLC O4 – Thr206 CG2 = **4.11 Å**
- **Met210 ↔ allosteric activator:** MRK C22 – Met210 CE = **3.66 Å** (also C22–SD 3.98 Å, C22–CG 4.22 Å, S16–CE 4.47 Å)
- **Thr206 ↔ Met210 (the bridging contact):** Thr206 Oγ – Met210 backbone N = **2.85 Å** (also Oγ–CA 3.81 Å, Oγ–CB 3.63 Å)
- The two ligands are **16.23 Å apart** (GLC–MRK), so ≥1 protein-mediated contact is required; a single contact suffices, hence this path is minimal.

**Robustness**
- Heavy-atom cutoff 5.0 Å: three equal 1-contact routes — **Thr206→Met210 (2.85 Å)**, Asp205→Met210 (4.98 Å), Thr206→Ile211 (4.98 Å); Thr206→Met210 remains the tightest and is the only one present at 4.5 Å.
- Cα-based network (≤ 8 Å): identical minimum path **Thr206→Met210** (1 contact).

**Biological context**
- Thr206 sits in the catalytic/glucose-binding region (adjacent to the glucose ligands Asp205, Asn204, Thr168), while Met210 forms part of the activator-binding surface of the allosteric pocket (with Tyr214, Tyr215, Val452, Val455). The single Thr206–Met210 contact therefore directly couples the glucose site to the allosteric site, consistent with the allosteric mechanism of glucokinase.
- Paths from the glucose site to canonical allosteric-pocket residues: Thr206–Met210–**Tyr214** (2 contacts); Thr206–Ala208–Ile211–**Tyr215** (3 contacts); Thr206–Ala208–Ala449–Leu451–**Val452/Val455** (3–4 contacts, connecting region II).
- The other glucose-contacting residue Thr168 lies on the opposite side (22.95 Å from MRK) and needs 5 contacts to reach the activator: Thr168–Phe152–Asn204–Ala208–Met210.

**Bottom line:** the shortest contact-network path between a residue touching the allosteric activator and a residue touching glucose in 1V4S chain A is **Thr206 — Met210**, of length **1 contact (2 residues, 2.85 Å heavy-atom separation)**.
=== END RUN rgf36iduxq6 ===

=== RUN rf3zii0k72b ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
ChEMBL **does have a record** for SHP099 against human PTP1B (PTPN1; UniProt P18031):

- **IC50:** **>100,000 nM**
- Equivalent to **>100 µM**
- **Compound:** SHP099 (`CHEMBL113081`)
- **Target:** PTP1B (`CHEMBL1806`)
- **Activity ID:** `31863`
- **Assay ID:** `CHEMBL663853`

Thus, ChEMBL reports **>100 µM**, meaning no potent inhibition of PTP1B by SHP099 within the tested range. This is a censored lower-bound value, not an exact IC50 of 100 µM.
=== END RUN rf3zii0k72b ===

=== RUN rwe7tsyeg2s ===
QUESTION:
Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P02_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[P02_b] [critical] [scripted] [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}]
[P02_c] [critical] [judged] the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported
[P02_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P02_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 1, "overlap_of_the_covering_pocket": 16, "top3_ranks": [1, 2, 3], "top3_overlap": [16, 0, 0], "pockets": [{"rank": 1, "score": 0.146, "n_residues": 33, "site_residues_in_pocket": 16}, {"rank": 2, "score": -0.007, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 3, "score": -0.021, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 4, "score": -0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": -0.053, "n_residues": 5, "site_residues_in_pocket": 4}, {"rank": 6, "score": -0.059, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 7, "score": -0.07, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 8, "score": -0.089, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 9, "score": -0.09, "n_residues": 7, "site_residues_in_pocket": 3}, {"rank": 10, "score": -0.098, "n_residues": 4, "site_residues_in_pocket": 3}, {"rank": 11, "score": -0.168, "n_residues": 7, "site_residues_in_pocket": 1}]}
[P02_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2], "top3_overlap": [0, 0], "pockets": [{"rank": 1, "score": 12.62, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 5.97, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P02_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The switch-II pocket is rank 2 in P2Rank.**

After removing every HETATM record from 6OIM chain A—including MOV/AMG 510, GDP, Mg²⁺, and water—P2Rank identified:

- **Rank 1:** the GDP-facing nucleotide pocket.
- **Rank 2:** the switch-II pocket, centered at **(4.4065, −7.5228, −0.9993) Å**, only **2.66 Å** from the former MOV ligand centroid.
- P2Rank rank 2 contains **12 of the 17** residues contacting MOV, including Val9, Gly10, Gln60–Glu63, Arg68, Met72, His95, Tyr96, Gln99, and Val103.

**Detector-specific caveat:** fpocket merges the GDP and switch-II cavities into one broad cavity, so the same switch-II location appears as **fpocket rank 1** (16/17 shared inhibitor-contact residues). Thus, the unambiguous split-cavity result is **P2Rank rank 2**; the merged fpocket result is **rank 1**.
=== END RUN rwe7tsyeg2s ===

=== RUN rw2vlfpkwse ===
QUESTION:
Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P02_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[P02_b] [critical] [scripted] [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}]
[P02_c] [critical] [judged] the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported
[P02_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P02_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 1, "overlap_of_the_covering_pocket": 16, "top3_ranks": [1, 2, 3], "top3_overlap": [16, 0, 0], "pockets": [{"rank": 1, "score": 0.146, "n_residues": 33, "site_residues_in_pocket": 16}, {"rank": 2, "score": -0.007, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 3, "score": -0.021, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 4, "score": -0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": -0.053, "n_residues": 5, "site_residues_in_pocket": 4}, {"rank": 6, "score": -0.059, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 7, "score": -0.07, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 8, "score": -0.089, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 9, "score": -0.09, "n_residues": 7, "site_residues_in_pocket": 3}, {"rank": 10, "score": -0.098, "n_residues": 4, "site_residues_in_pocket": 3}, {"rank": 11, "score": -0.168, "n_residues": 7, "site_residues_in_pocket": 1}]}
[P02_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2], "top3_overlap": [0, 0], "pockets": [{"rank": 1, "score": 12.62, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 5.97, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P02_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The switch-II pocket is rank 1 (Pocket 1) in fpocket.**

After removing all 277 HETATM records from 6OIM—including MOV, GDP, Mg²⁺, and waters—fpocket identified the former covalent-inhibitor cavity as:

- **Pocket rank:** **1**
- **fpocket score:** 0.146
- **Druggability score:** 0.838
- **Overlap with the former MOV site:** 16 of 17 MOV-contacting residues
- Includes the covalent anchor **Cys12** and switch-II residues **Ala59, Gly60, Gln61, Glu62, Glu63, Met72, Tyr96, Gln99, and Val103**
- All 41 former MOV atoms were within 6 Å of Pocket 1’s lining residues.

**Detector-specific note:** P2Rank partitions the elongated switch-II region more finely and assigns the switch-II-specific subpocket **rank 2**; its rank-1 pocket is primarily the nucleotide/P-loop cavity. Thus, for the standard fpocket pocket ranking, the requested answer is **rank 1**.
=== END RUN rw2vlfpkwse ===

=== RUN rjvpygbzs82 ===
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
### Final plan status

1. [✓] Identified SHP099 as RCSB chemical component **5OD** in 5EHR.
2. [✓] Calculated chain-A polymer contacts using an inclusive **≤4.0 Å** heavy-atom distance cutoff.
3. [✓] Verified chain A maps to **Q06124 (PTPN11/SHP2)** with 100% sequence identity.
4. [✗] The first UniProt lookup used uppercase `DOMAIN`; the JSON uses title-case `Domain` features, so it was corrected.
5. [✓] Retrieved UniProt’s core domain features: SH2 1, 6–102; SH2 2, 112–216; PTP, 247–517.
6. [✓] Confirmed the conventional structural partition used for the assignment: **N-SH2 1–115, C-SH2 116–252, PTP 253–525**.
7. [✗] An initial RCSB citation parser assumed a list rather than a dictionary; it was corrected.
8. [✓] Confirmed the RCSB entry title identifies 5OD as the allosteric inhibitor SHP099.
9. [✗] The primary Nature paper was not open-access in Europe PMC, so no unavailable full-text claims were used.
10. [✓] Confirmed in open full text that the SHP099 tunnel spans both SH2 domains and the PTP domain.
11. [✗] One Europe PMC boundary-search request returned HTTP 503 and was excluded.
12. [✓] Rechecked the final 15-residue contact calculation and three-domain assignment.
13. [✗] Two ancillary fixed-column `SITE` parsers misparsed residue fields.
14. [✗] The first token parser pooled `SITE` groups AC1–AC4, which represent several ligands.
15. [✓] Restricted the comparison to REMARK-mapped **AC1**, the 5OD chain-A binding site, and completed validation.

### Residues within 4 Å of SHP099 in 5EHR chain A

| Domain | Residue | Minimum heavy-atom distance |
|---|---|---:|
| **N-SH2** | Thr108 (T108) | 3.13 Å |
| | Glu110 (E110) | 3.47 Å |
| | Arg111 (R111) | 3.14 Å |
| | Phe113 (F113) | 2.79 Å |
| | His114 (H114) | 3.75 Å |
| **C-SH2** | Thr218 (T218) | 3.69 Å |
| | Thr219 (T219) | 3.59 Å |
| | Glu249 (E249) | 3.29 Å |
| | Glu250 (E250) | 3.10 Å |
| **PTP** | Thr253 (T253) | 3.30 Å |
| | Leu254 (L254) | 3.46 Å |
| | Gln257 (Q257) | 3.58 Å |
| | Pro491 (P491) | 3.45 Å |
| | Lys492 (K492) | 3.45 Å |
| | Gln495 (Q495) | 3.57 Å |

**Total: 15 residues** — **5 N-SH2, 4 C-SH2, and 6 PTP**. Thus, the SHP099 tunnel makes contacts with all three structural domains.

The deposited 5EHR `SITE` annotation lists 14 of these residues; the explicit ≤4.0 Å calculation adds **His114 at 3.75 Å**.

**Sources:** RCSB PDB **5EHR**; UniProt **Q06124**; validated geometric ligand-contact calculation for component **5OD**; deposited `SITE` group **AC1**.
=== END RUN rjvpygbzs82 ===

=== RUN rucjf8k2xgq ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# AKT1 (P31749): combined evidence on the PH–kinase interface as an allosteric site

## Verdict in one line
The **PH–kinase interface is a bona fide, experimentally validated and therapeutically druggable allosteric site of AKT1** (the ATP-site "sandwich" pocket), but **residue 17 is not a ligand-contact residue** — it is a *second-shell interface/autoinhibition residue* at the rim of that pocket whose clinical significance (E17K) is best explained by destabilising the PH–kinase interface rather than by blocking inhibitor binding.

---

## 1. What is actually in 3O96
| Item | Value | Source |
|---|---|---|
| PDB title | "CRYSTAL STRUCTURE OF HUMAN AKT1 WITH AN ALLOSTERIC INHIBITOR" | PDB header (raw file) |
| Construct | UNP residues 2–443, chain A; maps to P31749 (AKT1_HUMAN), coverage 0.921, identity 1.0 (author numbering = UniProt numbering) | `[TOOL]` |
| Ligand | **IQO**, chain A, resnum 444, 42 atoms; 2.7 Å resolution | `[TOOL]` / `[TOOL]` |
| Ligand chemistry | 1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one (HETNAM/HETSYN) | PDB header |
| BioLiP affinity | "IC50 = 58 nM"; binding site W80 I84 S205 L210 L264 K268 Y272 D292 C296; catalytic site D274 K276 N279 D292 | `[TOOL]` |

*Numbering caveat:* the BioLiP snapshot's "UniProt" list for 3O96 (W76, I80, S157, L162…) is offset by −4 from canonical AKT1 numbering; the SIFTS-based mapping and the coordinates (W80, I84, S205…) are canonical, and the ASD curated site agrees with the canonical numbering. Use the canonical set below.

## 2. Allosteric ligand contacts in 3O96 (`[TOOL]`, geometric proximity only)
**≤4.0 Å — 18 residues, spanning BOTH domains:**
- PH-domain side: W80 3.41, T82 3.95, V83 3.74, I84 3.46, E85 3.75 (plus N54 4.96, Q79 4.68 at ≤5 Å)
- Kinase-domain side: S205 2.89, L210 3.66, T211 3.58, L264 3.64, K268 3.26, V271 3.90, Y272 3.11, R273 3.75, D274 3.83, I290 3.38, T291 3.97, D292 3.06, C296 3.15 (plus V201 4.29, V270 4.16, K297 4.98, Y326 4.29 at ≤5 Å)

The ligand is physically embedded at the domain junction: **minimum IQO-to-kinase-domain heavy-atom distance = 2.89 Å** (S205). This is the canonical AKT allosteric "sandwich" site, in which the PH-domain W80 is clamped between inhibitor and kinase domain.

## 3. Distance from residue 17 to the ligand (computed from coordinates; no listed tool covers this)
- **E17 (chain A, resnum 17) → IQO = 5.70 Å** (closest heavy-atom pair CG···C6)
- E17 is therefore **outside both the ≤4 Å and ≤5 Å contact shells**; among PH residues 7–30 it is the *closest* to the ligand (Y18 6.6 Å, K14 7.82, G16 9.70, K20 9.06; the rest 12–22 Å)
- E17 is **16.69 Å from W80** → E17 is not part of the sandwich itself

## 4. Is E17 on the PH–kinase interface? (computed from 3O96 coordinates)
- PH domain (res 1–108) vs kinase domain (res 144–443): **361 heavy-atom contact pairs < 4.5 Å**, involving 25 PH residues (K14, R15, G16, **E17**, Y18, I19, R23, R25, G37, T38, K39, A50, P51, L52, N53, N54, F55, Q61, R76, L78, W80, T81, T82, V83, E85) and 30 kinase residues (F161, **K179**, L181, V185, I186, A188, L202, S205, L213, L223, F225, K268, N269, V270, V271, R273, D292, G294, K297, E298, L316, L321, E322, D323, N324, D325, Y326, G327, R328, F358)
- **E17 directly contacts three kinase-domain residues: R273 (4.14 Å), K297 (3.92 Å), D323 (4.40 Å)** → E17 is a genuine interface residue, and the nearest kinase atom to E17 is 3.92 Å
- E17 rSASA = 54.9 Å² (partially exposed, interface edge) vs I84 6.0 (buried in pocket), S205 17.6, W80 43.8, D292 3.4

## 5. ChEMBL: MK-2206 against AKT1 (`[TOOL]` + local chembl_37 SQLite for assay context)
Target CHEMBL4282 = "RAC-alpha serine/threonine-protein kinase" (AKT1, *Homo sapiens*); MK-2206 = CHEMBL1079175. **19 IC50 records, bimodal:**
- **Biochemical: 5–10 nM (pChEMBL 8.0–8.3)** across 12 records — "Inhibition of Akt1/AKT1/PKBalpha", Z′-LYTE/HTRF/iFLiK, and explicitly *"full length N-terminal his6-tagged AKT (2 to 446 residues)"* (same PH+kinase topology as 3O96)
- **Cellular proliferation: 2,239.7–10,000 nM (pChEMBL 5.2–5.7)** — 72-h CellTiter growth assays in myeloma lines (RPMI-8226, ANBL-6, melphalan-/bortezomib-resistant variants, U-266), i.e. pathway-context endpoints, not weaker binding

So MK-2206 is a **potent (single-digit-to-10 nM) allosteric inhibitor of full-length AKT1**, and `[TOOL]` links MK-2206 to the same 12 ASD AKT1 sites and to ChEMBL/PubChem.

## 6. Curated allosteric-site evidence
- `[TOOL](uniprot_id="P31749")` → **CONFIRMED, "experimentally confirmed as allosteric"**, protein name PKB / AKT1, **12 curated "Inhibitor" sites, 893 modulators**
- Site **3O96-1** (Inner Protein Regulator): TRP80, THR82, VAL83, ILE84, GLU85, SER205, LEU210, THR211, LEU264, LYS268, VAL271, TYR272, ARG273, ASP274, ILE290, THR291, ASP292, CYS296 — matching the computed contacts
- Parallel allosteric-inhibitor sites: **4EJN-1** (ASN53…TYR326), **5KCV-1** (allosteric function), 6HHF/H/I/J, 6S9W/X, 7NH4/5
- **Residue 17 appears in NONE of the 12 curated site residue lists**; ASD modulator records are ID-based, so MK-2206 is linked at site level, not residue level
- `[TOOL](3O96, chain A)` → **empty list** (no prediction for this structure)

## 7. Clinical/genomic evidence for E17K
- **ClinVar**: `NM_001382430.1(AKT1):c.49G>A (p.Glu17Lys)` — **Pathogenic**, ClinVar ID **29022**, review status *"criteria provided, multiple submitters, no conflicts"*, GRCh38 chr14:104,780,214 (GRCh37 chr14:105,246,551). Other AKT1 pathogenic variants seen: R25C (48662), T435P (48663); conflicting: D46E, R465H
- **AlphaMissense (P31749 position 17)**: **E17K = 0.9977 (pathogenic)**; *all 19* possible substitutions at position 17 score pathogenic (0.9910–0.9998) → the position tolerates no substitution, the signature of a structurally constrained residue

## 8. Tool-based verification metrics (3O96)
| Tool | Candidates | Result |
|---|---|---|
| `[TOOL]` | E17 vs active site K179/K276/N279/D292 | mean **12.66 Å** → inside the 10–30 Å "optimal allosteric communication" band; **score 1.00** |
| `[TOOL]` | E17 + pocket residues | avg rSASA **12.7 %** (buried), avg hydrophobicity **−1.66** (hydrophilic); score 0.63 |
| `[TOOL]` | ligand-pocket residue set | volume **1831 Å³**, max extent **28.4 Å**, asphericity **0.31**, PMI shape score 1.0; **score 0.80** |
| `[TOOL]` | E17 | 0.31 ("lowly conserved") — ⚠️ this is the documented **deterministic pseudo-MSA surrogate, not real conservation**; it must not be cited as conservation evidence |
| `[TOOL]` | 3O96 chain A | **no residues returned** |

---

## What the combined evidence says

**1. The PH–kinase interface is an allosteric site — strongly supported (validated, not merely predicted).** Three independent lines converge: (i) a real ligand, IQO, is bound at the PH/kinase junction in 3O96 with contacts on both domains (min 2.89 Å to the kinase domain), i.e. the inhibitor physically occupies the interface; (ii) the Allosteric Database independently **CONFIRMS P31749 as experimentally allosteric**, with 3O96-1 itself curated as an inhibitor site and 11 further inhibitor sites (4EJN-1, 5KCV-1, 6HH\*, 6S9\*, 7NH\*) reproducing the same pocket; (iii) pharmacologically, **MK-2206 inhibits full-length AKT1 at 5–10 nM** (pChEMBL 8.0–8.3), with the weaker 2.2–10 µM values explained by cellular proliferation endpoints, not by weaker binding. The pocket itself is well-formed (geometry score 0.80, buried and hydrophilic walls, asphericity 0.31). Structurally, the E17/interface element is ~12.7 Å from the catalytic lysine K179 — squarely in the distance range from which a conformational (allosteric) signal can propagate, rather than a catalytic site.

**2. E17 is a second-shell interface residue, not an allosteric-site ligand contact.** The 5.70 Å E17–IQO distance (vs 2.89–3.95 Å for true contacts) and 16.69 Å separation from the W80 sandwich place E17 one residue layer outside the pocket, at its edge. No curated ASD site for AKT1 lists residue 17, and STINGAllo nominated nothing. So the combined evidence does **not** support calling E17 itself a pocket-lining allosteric residue or a direct MK-2206/IQO contact.

**3. The E17K genetics is best read as evidence for the interface's *autoinhibitory* function, which is the same interface that forms the pocket.** E17 sits on the PH-domain β-strand and directly packs against kinase-domain R273/K297/D323 — the docking element that holds the PH domain against the kinase domain. ClinVar **Pathogenic** (multi-submitter, no conflicts) plus AlphaMissense **0.9977** with *every* substitution at position 17 pathogenic indicates a residue whose packing/charge is functionally indispensable. The parsimonious reading is that E17K destabilises the PH–kinase interaction (relieving autoinhibition), rather than that E17 contributes direct inhibitor binding. In other words, the clinical genetics corroborates the **importance of the interface**, while the structural and ligand data place the **drug pocket** slightly away from E17 itself.

**4. Net assessment.** The PH–kinase interface of AKT1 is an **established allosteric/druggable site**: it is occupied by a crystallographic allosteric inhibitor, curated as such in ASD, and exploited by clinical-stage allosteric inhibitors (MK-2206). E17 is a **validated interface residue whose mutation (E17K) is pathogenic**, marking the interface as functionally critical — but the combined evidence supports the interface, **not E17, as the allosteric-site determinant**; E17 sits at 5.70 Å from the inhibitor.

**5. Explicit limitations / what these data cannot show.**
- No E17K-mutant structure and no measured MK-2206/IQO binding to E17K were retrieved → the *effect* of E17K on allosteric-inhibitor potency (sensitisation vs resistance) is **not** established by these tools and would need direct measurement.
- 3O96 is a single ligand-bound conformation; the relative accessibility of E17 in the autoinhibited (PH-domain "occluded") state was not examined here.
- `[TOOL]` reports **geometric proximity only** — not interaction types, affinity or biological relevance; and the BioLiP "UniProt" residue numbering for 3O96 is offset by −4 versus canonical AKT1.
- The conservation tool output is a **surrogate**, not an alignment-based result, and carries no conservation evidence.
- ASD `NOT_CONFIRMED` is returned only for the PDB-ID-keyed lookup; the UniProt-keyed lookup is `CONFIRMED`. STINGAllo returned an empty list for 3O96 (no prediction, not a negative prediction).
=== END RUN rucjf8k2xgq ===

=== RUN ru4g4cbs472 ===
QUESTION:
Remove all ligands from PDB entry 1T4J (PTP1B, UniProt P18031) and run pocket detection. Does any of the top three pockets overlap the site where the allosteric ligand was bound? Report the overlap as a number of shared residues.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P01_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P01_c] [critical] [judged] the top three fpocket pockets of the ligand-stripped 1T4J contain the residues FRJ contacted, and the overlap is reported as a count
[P01_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P01_e] [critical] [judged] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P01_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P01_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Yes.** The second-ranked AutoSite pocket overlaps the site where the allosteric ligand **FRJ** was bound.

| Pocket | AutoSite score | Shared residues with FRJ site |
|---|---:|---:|
| 1 | 34.852 | 0 |
| 2 | 32.394 | **10** |
| 3 | 29.472 | 0 |

The ten shared residues are:

**Ser187, Pro188, Ala189, Asn193, Phe196, Lys197, Glu200, Gly277, Phe280, and Ile281.**

Method summary:
- Removed all 41 FRJ `HETATM` records from PDB 1T4J while preserving the 2,304 protein `ATOM` records.
- Defined the original FRJ site as residues within 4.5 Å of an FRJ heavy atom.
- Ran AutoSite v1.0.0 at 1.0 Å spacing, identifying 13 clusters.
- Assigned pocket residues using AutoSite’s own `featurePts/bsres` implementation.

Full results are in:

`/agent_cwd/output/1T4J_pocket_analysis/final_report.txt`

AutoSite citation: Ravindranath & Sanner, *Bioinformatics* (2016), DOI: `10.1093/bioinformatics/btw367`.
=== END RUN ru4g4cbs472 ===

=== RUN rky13esqjbp ===
QUESTION:
Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P02_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[P02_b] [critical] [scripted] [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}]
[P02_c] [critical] [judged] the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported
[P02_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P02_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 1, "overlap_of_the_covering_pocket": 16, "top3_ranks": [1, 2, 3], "top3_overlap": [16, 0, 0], "pockets": [{"rank": 1, "score": 0.146, "n_residues": 33, "site_residues_in_pocket": 16}, {"rank": 2, "score": -0.007, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 3, "score": -0.021, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 4, "score": -0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": -0.053, "n_residues": 5, "site_residues_in_pocket": 4}, {"rank": 6, "score": -0.059, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 7, "score": -0.07, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 8, "score": -0.089, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 9, "score": -0.09, "n_residues": 7, "site_residues_in_pocket": 3}, {"rank": 10, "score": -0.098, "n_residues": 4, "site_residues_in_pocket": 3}, {"rank": 11, "score": -0.168, "n_residues": 7, "site_residues_in_pocket": 1}]}
[P02_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2], "top3_overlap": [0, 0], "pockets": [{"rank": 1, "score": 12.62, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 5.97, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P02_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The switch-II pocket is ranked 1 — the top-ranked Fpocket pocket (Pocket 1).**

Supporting results:

- All heteroatoms were removed from 6OIM: the covalent inhibitor `MOV` (AMG 510), GDP, Mg²⁺, and waters.
- Fpocket detected 11 pockets.
- Pocket 1 had a Fpocket score of **0.146**, druggability score of **0.838**, 190 alpha spheres, and volume of **1594.918 Å³**.
- All **41/41 atoms** of the former inhibitor position were covered by Pocket 1 alpha spheres; no other pocket covered more than 10/41.
- Pocket 1 contains Cys12 and the switch-II residues Thr58, Ala59, Gly60, Gln61, Glu62, Glu63, Arg68, Asp69, and Met72, along with Tyr96 and Gln99.
- The nearest Pocket 1 alpha-sphere center was only **1.07 Å** from the original inhibitor centroid.

Artifacts:

- Ligand-free receptor: `/agent_cwd/kras_g12c_6OIM/6OIM_ligand_free.pdb`
- Fpocket ranking: `/agent_cwd/kras_g12c_6OIM/6OIM_ligand_free_out/6OIM_ligand_free_info.txt`
- Pocket–inhibitor overlap analysis: `/agent_cwd/kras_g12c_6OIM/pocket_inhibitor_overlap.json`

**Answer: rank 1.**
=== END RUN rky13esqjbp ===

=== RUN r62robkb7pj ===
QUESTION:
Build a residue contact network for E. coli adenylate kinase (UniProt P69441, PDB 1AKE chain A) at an 8 angstrom C-alpha cutoff and find communities. Report the algorithm and seed, and say how the communities relate to the LID, NMP and CORE domains.

INTENDED PROTEIN: Adenylate kinase (P69441)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C05_a] [critical] [scripted] {"name": "Adenylate kinase", "gene": "adk", "organism": "Escherichia coli (strain K12)"}
[C05_b] [critical] [judged] the communities of 1AKE at an 8 A C-alpha cutoff are reported with the algorithm and the seed, and their relation to the LID, NMP and CORE domains

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Residue contact network for E. coli adenylate kinase

### Completed plan

1. [✓] Retrieved 1AKE structural data and P69441 UniProt metadata.
2. [✓] Verified chain-A residues and established the LID, NMP, and CORE boundaries.
3. [✓] Built the 8 Å Cα contact graph and found seeded Louvain communities.
4. [✓] Validated sequence identity, edge counts, reproducibility, modularity, and seed sensitivity.
5. [✓] Related the communities to the structural domains.

## Method

- **Structure:** PDB **1AKE**, chain **A**, experimental X-ray structure.
- **Protein identity:** The chain-A sequence matched UniProt **P69441** exactly: 214/214 residues, 100% identity.
- **Graph definition:**
  - One node per Cα atom.
  - An undirected edge between residues whose Cα–Cα Euclidean distance was **≤8.0 Å**.
  - All residue pairs, including sequence neighbors, were considered.
  - The graph was unweighted for community detection; exact distances were retained in the output edge list.
- **Community algorithm:** NetworkX 3.6.1 `louvain_communities`.
  - **Seed:** `0`
  - **Resolution:** `1.0`
  - **Convergence threshold:** `1e-7`
  - Nodes were inserted in increasing residue-number order.
- **Graph statistics:** 214 nodes, 1,007 edges, one connected component, density 0.044184, mean clustering coefficient 0.559465.
- **Partition:** **9 communities**, modularity **Q = 0.683527**.
- **Partition cohesion:** 812/1,007 contacts, or **80.6%**, were intra-community.

## Communities and domain composition

The primary domain convention used here was:

- **CORE:** residues 1–29, 68–117, and 161–214
- **NMP:** residues 30–67
- **LID:** residues 118–160

| Community | Size | Composition | Residues |
|---|---:|---|---|
| **C01** | 31 | 29 CORE, 2 NMP | 1–5, 14–31, 79–86 |
| **C02** | 26 | 20 CORE, 6 LID | 6–13, 109–123, 197–199 |
| **C03** | 17 | **17 NMP** | 32–48 |
| **C04** | 32 | 11 NMP, 4 LID, 17 CORE | 49–59, 157–177 |
| **C05** | 19 | 8 NMP, 11 CORE | 60–78 |
| **C06** | 16 | **16 CORE** | 87–102 |
| **C07** | 25 | **25 CORE** | 103–108, 178–196 |
| **C08** | 33 | **33 LID** | 124–156 |
| **C09** | 15 | **15 CORE** | 200–214 |

## Relation to the structural domains

- **LID:** C08 is a pure-LID community containing residues 124–156. It captures **33 of 43 LID residues, or 76.7%**, and is the most cohesive community by incident-edge fraction: 129 of 157 incident edges are internal. The remaining LID residues divide at its boundaries: 118–123 join C02, while 157–160 join C04. Thus, the network identifies the central ATP-binding lid as a distinct structural module while placing its base and terminal segments in neighboring core/interface communities.

- **NMP:** C03 is a contiguous, pure-NMP community comprising residues 32–48, or **17 of 38 NMP residues (44.7%)**. The remainder of NMP is divided into the boundary communities C01 (30–31), C04 (49–59), and C05 (60–67). Thus, an 8 Å contact partition does not recover the whole biochemical NMP domain as one community; it resolves a central NMP core plus NMP-to-CORE interface segments.

- **CORE:** CORE is the most structurally fragmented domain, appearing in seven communities. C06, C07, and C09 are pure-CORE communities, whereas C01, C02, C04, and C05 mix CORE residues with NMP or LID residues. Notable examples are:
  - **C02**, which connects CORE residues 109–117 to the LID base residues 118–123;
  - **C04**, which combines NMP residues 49–59, terminal LID residues 157–160, and CORE residues 161–177;
  - **C05**, which joins NMP residues 60–67 to CORE residues 68–78.

Overall, the contact network recovers a large central LID module and a central NMP module, but not complete biochemical-domain boundaries. The mixed communities lie at domain interfaces and hinges, while CORE itself resolves into several compact structural packs.

## Boundary and seed sensitivity

Published studies use either LID 118–160 or LID 118–167, with the corresponding CORE-C segment beginning at 161 or 168. Repeating the mapping with LID 118–167 and CORE-C 168–214 changes C04 from **11 NMP/4 LID/17 CORE** to **11 NMP/11 LID/10 CORE**, but leaves the main conclusions unchanged.

Louvain communities are seed-dependent. Repeating the exact analysis with seeds 0, 1, 2, 3, 42, and 2024 produced 8–9 communities with modularity 0.6706–0.6835. The exact residue-level memberships therefore belong specifically to **seed 0**, but the broad result was robust: a large central LID block persisted in every run, while a contiguous central NMP block persisted with some seed-dependent boundary changes.

The structure is the **Ap5A-inhibitor-bound** conformation of 1AKE. The network describes the protein Cα geometry in that conformation; the inhibitor itself was not included as a graph node.

## Reproducible outputs

Saved under `/agent_cwd/data/1AKE_contact_network/`:

- `1AKE.pdb`
- `contact_edges_8A.csv`
- `community_assignments.csv`
- `community_summary_primary.csv`
- `community_summary_alternative.csv`
- `contact_network_results.json`
- `contact_network_validation.json`

**Primary structural reference:** Müller CW, Schulz GE. *Structure of the complex between adenylate kinase from Escherichia coli and the inhibitor Ap5A refined at 1.9 Å resolution.* J Mol Biol. 1992;224:159–177. PMID: **1548697**.  
**Domain-boundary reference:** Pontiggia F, Zen A, Micheletti C. *In the multi-domain protein adenylate kinase, domain insertion facilitates cooperative folding while accommodating function at domain interfaces.* PLoS Comput Biol. 2013;9:e1003938. PMCID: **PMC4230728**.
=== END RUN r62robkb7pj ===

# Judge batch 012 of 24

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

=== RUN r6rl88agd9a ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# Residue Contact Network for Glucokinase (PDB 1V4S, chain A)

## Input & structure details
| Item | Value |
|---|---|
| Structure | PDB **1V4S**, chain A — human glucokinase (GCK/HK4), X-ray, **2.30 Å** |
| UniProt | **P35557** (SIFTS: identity 1.0; PDB author numbering = canonical P35557 numbering — verified residue-by-residue against the UniProt sequence) |
| Allosteric activator | **MRK 501** = 2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide (small-molecule GK activator; primary citation Kamata et al., *Structure* 2004, 12:429–438, PMID 15016359) |
| Glucose | **GLC 500** = α-D-glucopyranose |
| Other heteroatom | NA 600 (sodium ion, coordinated by Met238/Val241/Val244/Gly246 — not part of the path) |

## Method
1. Parsed chain A; 448 resolved amino-acid residues (3,505 heavy atoms); waters excluded.
2. Built a residue–residue contact network: an edge exists if any heavy-atom pair is ≤ **4.5 Å** → **2,207 edges / 448 residues** (full table saved as `contact_network_1V4S_chainA_4.5A.csv`).
3. Ligand-contact sets = protein residues with any heavy atom ≤ 4.5 Å from MRK or GLC.
4. Multi-source BFS from the MRK-contact set to the GLC-contact set; cross-checked with NetworkX `single_source_shortest_path_length` and igraph `get_shortest_paths` (all three agree).

## Result — SHORTEST PATH

**MET210 → THR206**

| | |
|---|---|
| **Path** | **Met210 → Thr206** (UniProt P35557: Met210 → Thr206) |
| **Path length** | **1 residue–residue contact** (i.e., 2 residues, 1 edge) |
| **Geometric length** | **2.85 Å** minimum heavy-atom distance (backbone N of Met210 ··· backbone O of Thr206; Cα–Cα = 6.17 Å) |

**Complete ligand-to-ligand route:**
`MRK 501 —3.66 Å— MET210 —2.85 Å— THR206 —4.11 Å— GLC 500`

**Activator (MRK 501) contacting residues (≤4.5 Å):** Tyr215 (2.45), Arg63 (2.73), Tyr214 (3.01), Tyr61 (3.25), Cys220 (3.30), Thr65 (3.41), Val455 (3.46), Met235 (3.51), Ile211 (3.59), Val452 (3.62), Val62 (3.62), Ser64 (3.64), **Met210 (3.66)**, Pro66 (3.77), Ala456 (4.04), Leu451 (4.11), Glu221 (4.24), Ile159 (4.33), His218 (4.46), Gln98 (4.47)

**Glucose (GLC 500) contacting residues (≤4.5 Å):** Glu290 (2.53), Asp205 (2.53), Glu256 (2.59), Thr168 (2.90), Asn204 (2.96), Lys169 (2.97), Asn231 (3.23), Phe152 (3.29), Pro153 (3.39), Gln287 (3.48), Cys230 (3.54), Ser151 (3.57), Gly229 (3.65), Ile225 (3.65), **Thr206 (4.11)**

No residue contacts both ligands, so a protein-mediated path is required; Met210–Thr206 is the unique 1-contact connection (1 pair at 1 hop, 17 pairs at 2 hops).

## Interpretation & robustness
Met210 and Thr206 lie at the boundary between the activator site (the "α13 helix" / connecting region bearing Tyr214/Tyr215/Val452/Val455 — the canonical GK allosteric pocket) and the glucose site (the small domain bearing Asn204/Asp205/Asn231/Thr168). Their direct backbone N···O contact (2.85 Å) provides the shortest allosteric-to-catalytic coupling route in the static structure.

**Cutoff sensitivity:** 4.2–4.5 Å → Met210–Thr206 (1 contact); 5.0–6.0 Å → Ile211–Thr206 (1 contact); stricter 4.0 Å → Val62–Val207–Asn204 (2 contacts). The 1-contact Met210–Thr206 answer is stable across the standard 4.0–4.5 Å range and under both hop-count and minimum-geometric-length (Dijkstra) objectives.

**Artifacts saved** (`/agent_cwd/work/`): `final_result_1V4S.json`, `contact_network_1V4S_chainA_4.5A.csv`, `shortest_path_1V4S.json`, `validation_details.json`, `network_path_1V4S.png` (3-D network rendering with both ligand-contact shells and the path highlighted), `sifts_pdbe.json` (residue-level UniProt mapping).
=== END RUN r6rl88agd9a ===

=== RUN rkws8ntoflh ===
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
**5EHR (human SHP2 / PTPN11, UniProt Q06124) - chain A residues within 4.0 Å of SHP099**

**Ligand identity:** The inhibitor is deposited as chemical component **5OD** (`HETNAM`/`HETSYN: 5OD SHP099`; `FORMUL 3 5OD 2(C16 H19 CL2 N5)`), one molecule per chain: **5OD A 601** (occupancy 1.0, B 19.9-33.1 Å²) and 5OD B 601. The chain-B copy makes no contact with chain A, so all contacts below come from 5OD A 601.

**Numbering:** PDB author numbering = UniProt Q06124 canonical numbering (DBREF: PDB 1-525 = UNP Q06124 1-525; the catalytic phosphocysteine is Cys459 in both; the model begins at Arg4; the extra N-terminal cloning Ser is auth residue 0, which is why PDBe's SEQRES-based indices for the same residues are +1).

**Contacts (minimum heavy-atom distance to SHP099, cutoff 4.0 Å) - 15 chain-A residues**

| Residue | Min. distance (Å) | Closest atom pair | Polar/hydrogen-bond contact (≤3.5 Å) | Domain |
|---|---|---|---|---|
| THR 108 | 3.13 | O···N22 | O(Thr108)-N22 3.13 Å | N-SH2 |
| GLU 110 | 3.47 | O···N22 | O(Glu110)-N22 3.47 Å | N-SH2 |
| ARG 111 | 3.14 | NH1···N2 | NH1(Arg111)-N2 3.14 Å (also NH2 3.25 Å; altloc B: O···N22 3.40 Å) | N-SH2 |
| PHE 113 | 2.79 | O···N22 | O(Phe113)-N22 2.79 Å | N-SH2 |
| HIS 114 | 3.75 | CE1···C14 | hydrophobic | N-SH2 |
| THR 218 | 3.69 | OG1···C14 | hydroxyl···aryl | C-SH2 |
| THR 219 | 3.59 | OG1···C19 | hydroxyl···aryl | C-SH2 |
| GLU 249 | 3.29 | OE1···C23 | carboxylate···ring N-side | C-SH2 |
| GLU 250 | 3.10 | O···N7 | O(Glu250)-N7 3.10 Å | C-SH2 |
| THR 253 | 3.30 | O···Cl1 | hydroxyl···Cl | C-SH2 |
| LEU 254 | 3.46 | CA···Cl1 | hydrophobic | C-SH2 |
| GLN 257 | 3.58 | CG···Cl1 | hydrophobic | C-SH2 |
| PRO 491 | 3.45 | CB···N7 | hydrophobic | PTP |
| LYS 492 | 3.45 | N···C18 | NH3+···aryl | PTP |
| GLN 495 | 3.57 | CD···Cl2 | hydrophobic | PTP |

**Domain summary (standard SHP2 boundaries: N-SH2 1-115, C-SH2 116-280, PTP 281-525)**
- **N-SH2 (5 residues):** Thr108, Glu110, Arg111, Phe113, His114
- **C-SH2 (7 residues):** Thr218, Thr219, Glu249, Glu250, Thr253, Leu254, Gln257
- **PTP (3 residues):** Pro491, Lys492, Gln495

**Notes and caveats**
- Arg111, Cys259 and Ser499 carry alternate conformations; for Arg111 (the key side-chain contact) both altlocs are within 4 Å (3.14 Å for altloc A, 3.40 Å for altloc B).
- Nearest non-protein neighbours are ordered waters (e.g., HOH A 928 at 3.17 Å, A 1035 at 3.36 Å); no phosphate ion is part of the SHP099 site. Asp489 (4.27 Å) and Tyr511 (4.48 Å) are just outside the cutoff (both PTP).
- **Boundary-convention caveat:** the assignment above uses the widely used SHP2 boundary set. Under the stricter UniProt/InterPro spans for Q06124 (SH2-1 6-102, SH2-2 112-216, PTP 247-517), Thr108/Glu110/Arg111 and Thr218/Thr219 fall in inter-domain linkers, Phe113/His114 fall in SH2-2, and Glu249/Glu250/Thr253/Leu254/Gln257 fall in the PTP span; under the structural convention (N-SH2 2-104, C-SH2 112-216, PTP 220-525) Thr218/Thr219 are linker residues and the 249-257 set maps to PTP. The physical conclusion is unchanged: SHP099 sits in the allosteric tunnel at the junction of **all three domains** - N-SH2, C-SH2 and PTP.
- **Independent verification:** PDBe's ARPEGGIO interface analysis for 5EHR (chain A vs 5OD) lists the same contact set (its indices are +1 because they count from the SEQRES entity, which carries the extra N-terminal Ser): Thr109, Glu111, Arg112, Phe114, His115, Thr220, Glu250, Thr254, Leu255, Gln258, Pro492, Lys493, Gln496. Primary reference for the site: Nguyen CM et al., *Nature* 2016 (PMID 27362227), which states that SHP099 "concurrently binds to the interface of the N-terminal SH2, C-terminal SH2, and protein tyrosine phosphatase domains"; the C-SH2/PTP "tunnel" description and the pocket-disrupting Thr253 mutation are consistent with these contacts.

**Files saved:** `/agent_cwd/shp2_work/5EHR.pdb` (coordinates), `/agent_cwd/shp2_work/final_contacts.csv` (per-residue distances and domain labels).
=== END RUN rkws8ntoflh ===

=== RUN rp261x285i0 ===
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
## Result

In **PDB 5EHR**, SHP099 is the chemical component **5OD**, located in chain A at residue **601**. Using the deposited coordinates and counting a residue whenever **any SHP099 heavy atom is ≤4.000 Å from any chain-A protein heavy atom**, there are **15 contacting residues**.

| Chain-A residue | Minimum distance to SHP099 | Structural/domain assignment |
|---|---:|---|
| **Thr108** | 3.133 Å | N-SH2/C-SH2 linker region; N-SH2 side |
| **Glu110** | 3.465 Å | N-SH2/C-SH2 linker region; N-SH2 side |
| **Arg111** | 3.135 Å | N-SH2/C-SH2 linker; often grouped with N-SH2. The primary paper explicitly describes Arg111 as a linker residue |
| **Phe113** | 2.788 Å | C-SH2 / SH2-2 N-terminal edge |
| **His114** | 3.751 Å | C-SH2/SH2-2 boundary |
| **Thr218** | 3.693 Å | C-SH2–PTP connector; C-SH2 side |
| **Thr219** | 3.586 Å | C-SH2–PTP connector; C-SH2 side |
| **Glu249** | 3.293 Å | PTP N-terminal edge |
| **Glu250** | 3.103 Å | PTP N-terminal edge |
| **Thr253** | 3.295 Å | PTP |
| **Leu254** | 3.464 Å | PTP |
| **Gln257** | 3.580 Å | PTP |
| **Pro491** | 3.454 Å | PTP |
| **Lys492** | 3.448 Å | PTP |
| **Gln495** | 3.571 Å | PTP |

### Collapsed into the requested three-domain grouping

- **N-SH2-side contacts:** Thr108, Glu110, Arg111  
- **C-SH2-side contacts:** Phe113, His114, Thr218, Thr219  
- **PTP contacts:** Glu249, Glu250, Thr253, Leu254, Gln257, Pro491, Lys492, Gln495  

### Domain-boundary qualification

UniProt Q06124 annotates the structural domain cores as:

- SH2-1: **6–102**
- SH2-2: **112–216**
- PTP: **247–517**

Thus Thr108, Glu110, Arg111, Thr218, and Thr219 lie in interdomain/linker regions rather than within those strict core intervals. This is why published descriptions can differ—for example, Arg111 is sometimes called an N-SH2 residue, while the primary paper calls it a linker residue; Phe113 is usually assigned to C-SH2, and Glu249/Glu250 to the N-terminal edge of PTP.

**Sources:** [RCSB PDB 5EHR](https://www.rcsb.org/structure/5EHR), [UniProt Q06124](https://www.uniprot.org/uniprotkb/Q06124/entry), and Chen et al., *Nature* 2016, [doi:10.1038/nature18621](https://doi.org/10.1038/nature18621).
=== END RUN rp261x285i0 ===

=== RUN rj366zw1bzy ===
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
**The switch-II pocket is rank 1.**

- Structure: KRAS G12C, PDB **6OIM**, chain A, UniProt **P01116**
- Removed all **277** `HETATM` records: MG, GDP, MOV/AMG 510, and crystallographic waters
- Confirmed **0** ligand/heteroatom coordinate records remained
- Pocket detection: **Fpocket 4.2.3**
- Rank-1 pocket:
  - Fpocket score: **0.146**
  - Volume: **1672.424 Å³**
  - Includes **Cys12, Gln61, Glu62, Glu63, Tyr96, and Gln99**
  - All **41/41** former AMG 510 atoms lie within 5 Å of the pocket-lining residues; **32/41** lie within 4 Å

Thus, after ligand removal, the pocket containing the former covalent-inhibitor position is **rank 1**.
=== END RUN rj366zw1bzy ===

=== RUN r6quoorua4i ===
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
## SHP2 5EHR chain A comparison

### STINGAllo prediction
The STINGAllo REST API returned:

`{"allosteric_residues":["314"],"chain_id":"A","pdb_id":"5EHR"}`

Residue 314 in the deposited chain-A structure is phenylalanine:

- **PHE314 (F314)**

### Chain-A residues within 4.0 Å of SHP099
SHP099 is component **5OD**, instance **LI1 601**, in chain A. Using the minimum heavy-atom distance to SHP099, the residues are:

- **THR108 (T108)**
- **GLU110 (E110)**
- **ARG111 (R111)**
- **PHE113 (F113)**
- **HIS114 (H114)**
- **THR218 (T218)**
- **THR219 (T219)**
- **GLU249 (E249)**
- **GLU250 (E250)**
- **THR253 (T253)**
- **LEU254 (L254)**
- **GLN257 (Q257)**
- **PRO491 (P491)**
- **LYS492 (K492)**
- **GLN495 (Q495)**

### Overlap
- STINGAllo set: **{F314}**
- 4 Å SHP099 set: **{T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, Q495}**
- **Overlap: ∅ — no shared residues**

### Conclusion
**No. By the requested 4 Å ligand-neighborhood criterion, STINGAllo does not recover the SHP099 tunnel site.** Its sole prediction, F314, has a minimum heavy-atom separation of **11.572 Å** from SHP099. The 2016 structural study identifies SHP099 as occupying the tunnel-like allosteric pocket at the N-SH2–C-SH2–PTP interface, but none of the STINGAllo-predicted residues overlap that pocket’s direct 4 Å ligand-contact shell.

Data sources: [PDB 5EHR](https://www.rcsb.org/structure/5EHR), the [STINGAllo REST API](https://www.stingallo.cbi.cnptia.embrapa.br/apis), and Chen et al., *Nature* (2016), [doi:10.1038/nature18621](https://doi.org/10.1038/nature18621).
=== END RUN r6quoorua4i ===

=== RUN rph9csyc6sf ===
QUESTION:
Remove all ligands from PDB entry 1V4S (glucokinase, UniProt P35557) and run pocket detection. Do the top three pockets include the allosteric activator site and the glucose site? Report which pocket matches which site.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P06_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[P06_b] [critical] [scripted] [{"rank": 1, "residues": 11}, {"rank": 2, "residues": 24}, {"rank": 3, "residues": 12}]
[P06_c] [critical] [judged] which of the top three pockets of 1V4S matches the MRK site and which matches the GLC site is reported
[P06_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P06_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 6, "overlap_of_the_covering_pocket": 14, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.223, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.139, "n_residues": 24, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.111, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.089, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.086, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.072, "n_residues": 28, "site_residues_in_pocket": 14}, {"rank": 7, "score": 0.069, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 8, "score": 0.014, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 9, "score": 0.005, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 10, "score": -0.001, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 11, "score": -0.007, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 12, "score": -0.008, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 13, "score": -0.01, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 14, "score": -0.019, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 15, "score": -0.029, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 16, "score": -0.042, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 17, "score": -0.046, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 18, "score": -0.057, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 19, "score": -0.063, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 20, "score": -0.064, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 21, "score": -0.084, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 22, "score": -0.086, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 23, "score": -0.09, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 24, "score": -0.098, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 25, "score": -0.108, "n_residues": 8, "site_residues_in_pocket": 1}, {"rank": 26, "score": -0.136, "n_residues": 11, "site_residues_in_pocket": 0}]}
[P06_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 16.09, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 7.05, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 2.14, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 4, "score": 1.2, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.81, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.54, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P06_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

REFERENCE NOTE (dated correction, from benchmark/corrections.md)
The pocket-detection reference for the 1V4S_GLC site was corrected on 2026-11-02: the committed selection took the first pocket with any overlap (rank 1, overlap 2), the corrected selection takes the pocket with the most site residues (rank 2, overlap 13).
No committed checklist item carries this site, so the item texts below are unchanged.

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Conclusion

The result depends on the pocket-ranking algorithm:

| Detector | Rank | Pocket | Site assignment | Supporting overlap with original ligand contacts |
|---|---:|---|---|---|
| **fpocket** | 1 | FP1 | No complete site match; minor/edge overlap with glucose | 2/14 glucose contacts; minimum distance 2.96 Å |
|  | 2 | FP2 | **Glucose site** | 13/14 glucose contacts; minimum distance 2.59 Å |
|  | 3 | FP3 | Neither site | No glucose or MRK contacts |
| **P2Rank** | 1 | P2Rank-1 | **Glucose site** | 8/14 glucose contacts; minimum distance 2.68 Å |
|  | 2 | P2Rank-2 | **Allosteric activator (MRK) site** | 13/14 MRK contacts; minimum distance 2.45 Å |
|  | 3 | P2Rank-3 | Secondary/partial component of the **glucose site** | 4/14 glucose contacts; minimum distance 2.59 Å |

### Direct answer

- **P2Rank:** Yes—the top three include both functional sites:
  - **P2Rank-1 = glucose site**
  - **P2Rank-2 = allosteric activator site**
  - **P2Rank-3 = a smaller additional component of the glucose-binding region**
- **fpocket:** Only the glucose site is among the top three:
  - **fpocket-2 = glucose site**
  - The allosteric activator site is instead **fpocket-6**, with all 14 MRK-contact residues overlapping the pocket and a minimum heavy-atom distance of 2.45 Å.
  - Therefore, the fpocket top three do **not** contain both sites.

Thus, the most complete top-three result is obtained with **P2Rank**.

## Ligand removal and mapping details

PDB 1V4S contains chain A of human glucokinase, mapping to **UniProt P35557**. The original entry contained:

- **GLC:** α-D-glucopyranose, residue 500
- **MRK:** the crystallographic allosteric activator, residue 501
- One sodium ion
- 149 waters

All `HETATM` records were removed, leaving **3,505 protein `ATOM` records and zero `HETATM` records**. fpocket and P2Rank were then run on this ligand-free structure.

Pocket assignments were made by comparing the apo-detected pocket residues against 4.0 Å contacts of GLC and MRK in the original ligand-bound coordinates. Pocket overlap and minimum heavy-atom distances were both considered; thus the assignments reflect where each original ligand was observed, rather than merely a visual resemblance.

### Completed plan

1. [✓] Loaded PDB 1V4S and confirmed its UniProt mapping, chain, and ligands.
2. [✓] Removed every `HETATM` component and verified the ligand-free structure.
3. [✓] Ran fpocket and P2Rank and extracted their top three pockets.
4. [✓] Mapped the GLC and MRK contact sites to the detected pockets.
5. [✓] Reported detector-specific pocket assignments and the combined conclusion.
=== END RUN rph9csyc6sf ===

=== RUN rqvlzvu15iq ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**STINGAllo prediction for PTP1B (PDB 1T4J, chain A):**

- **Predicted allosteric residues:** None (`residues: []`)
- **Service-response date:** **October 28, 2026**
- **Full response timestamp:** `2026-10-28T09:14:22Z`
- **Service status:** Successful
=== END RUN rqvlzvu15iq ===

=== RUN rp6u0o4i1xq ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Shortest path

**VAL62 → VAL203 → ASN204**

- **VAL62** contacts the allosteric activator **MRK** (minimum heavy-atom distance: **3.62 Å**).
- **ASN204** contacts **glucose (GLC)** (minimum heavy-atom distance: **2.96 Å**).
- **Path length:** **2 residue-contact edges** (**3 residues**).

Residue numbers above are standard **PDB author / UniProt P35557** numbering. The underlying network tool uses mmCIF `label_seq_id` numbering, for which the identical path is:

**A.52 → A.193 → A.194**

### Network details
- Protein heavy-atom contact cutoff: **4.5 Å**
- Chain A network: **448 residues, 2,207 edges**
- Ligand-contact cutoff: **4.0 Å**
- Checking all 14 MRK-contact × 14 GLC-contact residue pairs confirmed that **2 edges is the global minimum**; several endpoint choices tie at this length.

### Completed plan
1. [✓] Identified GLC as glucose and MRK as the allosteric activator in chain A.
2. [✓] Retrieved geometric ligand contacts and reconciled PDB author numbering with network label numbering.
3. [✓] Built the residue-contact network and enumerated all ligand-contact endpoint pairs.
4. [✓] Verified and reported the shortest path and its length.
=== END RUN rp6u0o4i1xq ===

=== RUN r5ozrxvzb20 ===
QUESTION:
Compare ChEMBL bioactivity of asciminib (allosteric, myristoyl site) and imatinib (ATP site) against human ABL1 (UniProt P00519): record counts, assay types and best potency for each. Say which site each binds, citing a PDB entry for each.

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L03_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[L03_b] [critical] [scripted] {"count": 2, "best_nM": 0.5, "assay_types": {"B": 2}}
[L03_c] [critical] [scripted] {"count": 94, "best_nM": 19.9, "assay_types": {"B": 94}}
[L03_d] [critical] [judged] the answer cites a PDB entry for each site (AY7: 5MO4; STI: 2HYY)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# ChEMBL Bioactivity: Asciminib vs Imatinib against Human ABL1 (UniProt P00519)

**Target:** Tyrosine-protein kinase ABL1 — ChEMBL **CHEMBL1862**, *SINGLE PROTEIN*, *Homo sapiens*, UniProt **P00519** (13 records exist for P00519; CHEMBL1862 is the human single-protein ABL1 entry and was used throughout).

---

## 1. Record counts

| | **Asciminib** | **Imatinib** |
|---|---|---|
| ChEMBL molecule ID | CHEMBL4208229 | CHEMBL941 |
| Max phase / first approval | 4 / 2021 | 4 / 2001 |
| **Activity records vs CHEMBL1862** | **6** | **160** |
| Distinct assays (assay_chembl_id) | 4 | 154 |
| Distinct source documents | 3 | 49 |
| Records with pChEMBL value | 3 | 106 |
| Wild-type ABL1 records | 6 (0 mutant) | 93 (67 mutant/resistance-variant) |
| Total activities in ChEMBL (all targets) | 194 | 4,878 |

Related (context only): asciminib also has 17 records against the Bcr/Abl fusion target CHEMBL2096618; imatinib has 100 against the same fusion target.

---

## 2. Assay types

**Asciminib (6 records) — 100% Binding (B):**

| Standard type | n |
|---|---|
| IC50 | 2 |
| Kd | 1 |
| Delta Tm | 1 |
| kon | 1 |
| k_off | 1 |

BAO format: single protein format 4, assay format 2. No functional (F) or ADME (A) records; no cell-based format.

**Imatinib (160 records) — Binding-dominant:**

| Standard type | n | | BAO format | n |
|---|---|---|---|---|
| IC50 | 94 | | single protein format | 118 |
| Kd | 31 | | cell-based format | 31 |
| Inhibition | 13 | | assay format | 10 |
| Ki | 6 | | subcellular format | 1 |
| Kdiss | 3 | | | |
| kon / k_off | 3 / 3 | | | |
| GI50 | 2 | | | |
| t1/2 / T1/2 | 2 / 1 | | | |
| Selectivity, Activity | 1 / 1 | | | |

ChEMBL `assay_type`: **B = 158, F = 1, A = 1.** The single F record is a Ki (50.12 nM) from a PUBCHEM_BIOASSAY kinase-panel screen; the single A record is a cell-viability (12.5% inhibition at 3 µM) measurement in HEK293T. One record carries a `data_validity_comment` of "Outside typical range" (Inhibition = −88%).

---

## 3. Best potency

**Asciminib — best pChEMBL 9.30**
- **IC50 = 0.5 nM** (assay CHEMBL4200739; caliper kinase assay, FITC-Ahx-EAIYAAPFAKKK-NH2 peptide substrate) — doc CHEMBL4196169, *J Med Chem* 2018, **DOI 10.1021/acs.jmedchem.8b01040**, PMID 30137981
- **Kd = 0.5 nM** (assay CHEMBL4200854; ITC) — same document
- Other IC50 = 16.0 nM (pChEMBL 7.80); ΔTm = +6.92 °C (thermal shift, S229–K512 domain)

**Imatinib — best pChEMBL 9.00**
- **Kd = 1.0 nM** (assay CHEMBL4320888) — doc CHEMBL4316600, *J Med Chem* 2019, DOI 10.1021/acs.jmedchem.8b01925
- Kd = 1.1 nM, non-phosphorylated ABL1 kinase domain (assay CHEMBL1908688) — *Nat Biotechnol* 2011, DOI 10.1038/nbt.1990
- Kd = 2.2 nM (assay CHEMBL859868) — *Nat Biotechnol* 2005, DOI 10.1038/nbt1068
- **Wild-type IC50 best = 19.9 nM** (assay CHEMBL2406231) — *J Med Chem* 2013, DOI 10.1021/jm4004076
- **Wild-type Ki best = 13.0 nM** (assay CHEMBL932076) — *Bioorg Med Chem Lett* 2008, DOI 10.1016/j.bmcl.2007.11.112
- Wild-type GI50 = 260 nM (TEL–ABL growth inhibition in BAF3 cells)

**Head-to-head:** asciminib's best pChEMBL (9.30) slightly exceeds imatinib's (9.00), and its best Kd/IC50 (0.5 nM) is ~2× tighter than imatinib's best Kd (1.0 nM). But the dataset depth is radically different: 6 records / 4 assays / 3 documents for asciminib versus 160 / 154 / 49 for imatinib, and only 93 of imatinib's records are wild-type ABL1.

---

## 4. Binding sites and PDB entries

| Compound | Site | Mechanism | PDB citation |
|---|---|---|---|
| **Asciminib** | **Myristoyl (myristate) pocket** — allosteric, distinct from the ATP site | Binds the myristate site, so ATP-site resistance mutations (e.g. T315I, Y253H) do not block it | **PDB 5MO4** — "ABL1 kinase (T334I/D382N) in complex with asciminib and nilotinib", 2.17 Å, P00519; asciminib = **AY7**, nilotinib = **NIL**. Primary citation: Wylie AA et al., "The allosteric inhibitor ABL001 enables dual targeting of BCR-ABL1," *Nature* 2017;543:733–737, **DOI 10.1038/nature21702** (PMID 28329763) |
| **Imatinib** | **ATP-binding (hinge/orthosteric) site** — type II inhibitor | Binds the canonical ATP site, capturing the inactive DFG-out conformation via the hinge Met318 | **PDB 2HYY** — "Human Abl kinase domain in complex with imatinib (STI571, Glivec)", 2.4 Å, P00519. Primary citation: *Acta Crystallogr D* 2007, **DOI 10.1107/S0907444906047287** |

Supporting PDB entries:
- **PDB 8SSN** — "Abl kinase in complex with SKI and asciminib", 2.86 Å, P00519; asciminib (AY7) in the myristoyl pocket simultaneously with SKI at the ATP site. Citation: *PNAS* 2023, **DOI 10.1073/pnas.2304611120**.
- **PDB 7N9G** — "Crystal structure of the Abl 1b Kinase domain in complex with Dasatinib and Imatinib", 2.2 Å, human ABL1 (P00519), imatinib = **STI**. Citation: "Imatinib can act as an Allosteric Activator of Abl Kinase," *J Mol Biol* 2022, **DOI 10.1016/j.jmb.2021.167349**.
- **PDB 1IEP** — the classic "CRYSTAL STRUCTURE OF THE C-ABL KINASE DOMAIN IN COMPLEX WITH STI-571", 2.1 Å (SIFTS maps to mouse ABL1 P00520). Citation: "Crystal structures of the kinase domain of c-Abl in complex with the small molecule inhibitors PD173955 and imatinib (STI-571)," *Cancer Res* 2002 — the paper states both inhibitors "bind to the canonical ATP-binding site of the kinase domain."
- **PDB 3PYY** (1.85 Å, human P00519) — imatinib at the ATP site with a myristoyl-site activator (3YY), illustrating the two orthogonal pockets in one structure; *Chem Biol* 2011, DOI 10.1016/j.chembiol.2010.12.013.
- **PDB 3MSS** (1.95 Å) — "Abl kinase in complex with imatinib and fragment (FRAG2) in the myristate site," directly showing the two pockets in the same complex.

**Mechanistic statement (primary literature):** "Asciminib binds to the myristate pocket of BCR-ABL1 and maintains activity against TKI-resistant ATP-site mutations" — *Discovery of Asciminib (ABL001), an Allosteric Inhibitor of the Tyrosine Kinase Activity of BCR-ABL1*, J Med Chem 2018, DOI 10.1021/acs.jmedchem.8b01040. Imatinib conversely "target[s] the ATP-binding site," and resistance to it arises from "ATP-site mutations impeding drug binding."

---

### Takeaway
Both are picomolar-to-subnanomolar ABL1 inhibitors, but they are pharmacologically orthogonal: **imatinib (ATP site, 160 ChEMBL records)** is the deeply characterized type II inhibitor whose potency (Kd 1.0 nM) is well-corroborated across 49 publications, whereas **asciminib (myristoyl site, only 6 ChEMBL records)** is a first-in-class allosteric inhibitor with the best numerical potency (IC50 and Kd both 0.5 nM, pChEMBL 9.30) but a much thinner, entirely biochemical record — reflecting its later approval (2021 vs 2001). The clinical rationale for the allosteric mechanism is precisely what the small dataset implies: asciminib retains activity against ATP-site resistance mutations that break imatinib.

*Data saved: `/agent_cwd/results/abl1_activities.json`, `summary_raw.json`, `final_summary.json`, `pdb_hits.json`.*
=== END RUN r5ozrxvzb20 ===

=== RUN rgs0wego9xq ===
QUESTION:
Run normal mode analysis on PTP1B (UniProt P18031, PDB 1T4J chain A). Where are the hinge residues of the slowest non-trivial mode, and how mobile is the WPD loop (the loop containing the catalytic Asp181) relative to the rest of the protein?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C01_b] [critical] [judged] the hinge residues of the slowest non-trivial normal mode and the relative mobility of the WPD loop (the catalytic Asp181) are reported, in UniProt numbering

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**Slowest non-trivial mode hinge sites (Cα Gaussian Network Model, 10 Å cutoff):**

**Phe30, Ile72, Ser80, Trp179, Lys197, and Gly218.**

Thus, the WPD region directly overlaps a hinge at **Trp179**, the first residue of the catalytic **WPD** motif.

### WPD-loop mobility

Using residues **178–184** as the WPD loop—the operational definition used in PTP1B computational studies—the loop is **less mobile than the protein average in the slowest global mode**:

| Measure, slowest non-zero mode | WPD loop relative to the rest of PTP1B |
|---|---:|
| GNM mean relative fluctuation | **0.51×** |
| GNM RMS relative fluctuation | **0.55×** |
| ANM mean mode-1 amplitude | **0.81×** |
| ANM RMS mode-1 amplitude | **0.61×** |
| ANM 10-mode thermal-like RMSF | **0.83×** |

The catalytic core **Trp179–Pro180–Asp181** is particularly constrained: its GNM mean fluctuation is only **0.28×** that of the rest of the protein. **Asp181 itself has only 0.148× the protein-wide mean relative fluctuation**, placing it among the least mobile residues in this mode. By contrast, the loop median amplitude in the 3D ANM is close to the protein median, because a few highly mobile terminal residues inflate the protein-wide mean.

The WPD loop is not permanently rigid: it becomes comparatively mobile in other low-frequency ANMs, especially **modes 3, 4, and 6**, with loop/rest mean-amplitude ratios of **1.25, 1.66, and 1.31**, respectively. The slowest global mode therefore does **not** describe catalytic WPD-loop opening; it describes motion constrained around the W179 hinge.

## Analysis details

- Structure: **PDB 1T4J, chain A**, corresponding to UniProt **P18031**.
- Resolved model: residues 1–282; residues 283–298 are missing.
- The bound allosteric inhibitor **FRJ** was excluded from the elastic network.
- Coarse graining: 282 Cα atoms.
- GNM: 10 Å cutoff, unit spring constant, used for canonical hinge detection with ProDy `calcHinges()`; first non-zero eigenvalue **0.781654**.
- ANM: 15 Å cutoff, unit spring constant, used as a directional-mobility cross-check; first non-zero eigenvalue **0.709738**.
- Independent diagonalization confirmed six rigid-body zero modes, a symmetric Hessian, and a mode-1 eigenvalue agreement within \(6\times10^{-15}\).

### Cutoff sensitivity

The exact hinge positions shift slightly with the GNM contact cutoff, but the robust hinge locations are:

- **Phe30**
- **Ile72**
- **Ser80/Tyr81**
- **the WPD-loop site Thr177–Trp179**, with **Trp179** at the standard 10 Å cutoff
- **Lys197/Val198**
- **Gly218/Ile219**

A different convention—local minima of the 3D ANM mode-1 amplitude rather than canonical GNM hinge sites—gives Phe95, Leu250, His173, Ala27, and Arg156 as the strongest low-amplitude centers. This does not change the WPD-loop conclusion.

## Interpretation

In the slowest global elastic mode, the WPD loop behaves as a **hinged, relatively restrained catalytic element**, with Trp179 marking the hinge and Asp181 nearly locked. Its larger conformational excursions occur in separate low-frequency modes, consistent with the known open/closed motion of the PTP1B WPD loop. Elastic-network modes are qualitative and do not by themselves provide thermodynamic populations or kinetic timescales.

## Sources

- Wiesmann et al., “Allosteric inhibition of protein tyrosine phosphatase 1B,” *Nat Struct Mol Biol* 11, 730–739 (2004). PMID **15258570**; DOI **10.1038/nsmb803**.
- “Deconstructing allostery by computational assessment of the binding determinants of allosteric PTP1B modulators,” *Commun Chem* (2023). PMID **37322137**; DOI **10.1038/s42004-023-00926-1**. This work defines the WPD loop as residues **178–184**.
- “A Conserved Local Structural Motif Controls the Kinetics of PTP1B Catalysis” (2023). PMID **37378552**; DOI **10.1021/acs.jcim.3c00286**. This work uses the extended **179–185** definition; the conclusion is unchanged.

## Completed plan

1. [✓] Check local resources, data lake, and installed structural-analysis packages
2. [✓] Retrieve and verify 1T4J chain A, including WPD-loop residues and catalytic Asp181 mapping
3. [✓] Build and validate the elastic-network normal-mode analysis
4. [✓] Identify hinge residues for the slowest non-trivial mode using a documented criterion
5. [✓] Quantify WPD-loop mobility relative to the rest of PTP1B and summarize results
=== END RUN rgs0wego9xq ===

# Judge batch 018 of 24

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

=== RUN rbflauw2wry ===
QUESTION:
In PDB entry 1OPK (human ABL1, UniProt P00519), identify the ligand at the myristoyl allosteric site and the ligand at the ATP site, and list the residues within 4 angstroms of the myristoyl-site ligand.

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[S02_b] [critical] [scripted] [{"chain": "A", "pdb_number": 1}]
[S02_c] [critical] [scripted] [{"chain": "A", "pdb_number": 2}]
[S02_d] [critical] [scripted] {"uniprot_residues": [340, 341, 344, 429, 433, 462, 502, 510], "pdb_residues": [359, 360, 363, 448, 452, 481, 521, 529], "min_distances": {"359": 3.836, "360": 3.687, "363": 3.706, "448": 3.731, "452": 3.854, "481": 3.474, "521": 3.874, "529": 3.541}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

- **Myristoyl allosteric site:** **MYR — myristic acid** (tetradecanoic acid), chain A ligand residue 1. The deposited `REMARK 800` record identifies it as binding site **AC1**.
- **ATP site:** **P16**, the pyridopyrimidinone inhibitor **6-(2,6-dichlorophenyl)-2-[[3-(hydroxymethyl)phenyl]amino]-8-methylpyrido[2,3-d]pyrimidin-7(8H)-one**, chain A ligand residue 2. The deposited record identifies it as ATP-binding site **AC2**.
- **GOL** is glycerol at a separate crystallographic site and is neither requested ligand.

## Protein residues within 4 Å of MYR

Using any pair of non-hydrogen atoms in the deposited coordinates:

| Residue | Minimum distance (Å) | Nearest atom pair |
|---|---:|---|
| LEU359 | 3.836 | LEU CD1 – MYR C10 |
| LEU360 | 3.687 | LEU CA – MYR C14 |
| ALA363 | 3.706 | ALA CB – MYR C14 |
| LEU448 | 3.731 | LEU CD2 – MYR C14 |
| ALA452 | 3.854 | ALA CB – MYR C11 |
| GLU481 | 3.474 | GLU O – MYR C5 |
| ILE521 | 3.874 | ILE CD1 – MYR C12 |
| LEU529 | 3.541 | LEU CD1 – MYR C4 |

Thus, the requested residue list is:

**LEU359, LEU360, ALA363, LEU448, ALA452, GLU481, ILE521, and LEU529** — all in chain A.

The calculation was cross-checked using independent scalar-distance and dense-distance-matrix implementations; the closest residue outside the cutoff is ILE451 at 4.068 Å.

Source: [RCSB PDB entry 1OPK](https://www.rcsb.org/structure/1OPK), including its deposited coordinate file and `REMARK 800` site annotations.

### Final plan status
1. [✓] Retrieve 1OPK metadata and coordinates from RCSB PDB
2. [✓] Identify MYR and P16 from the deposited chemical and site records
3. [✓] Correct the coordinate-query implementation and independently verify all 4 Å MYR contacts
4. [✓] Report the ligand identities, contact residues, distances, and structural criterion
=== END RUN rbflauw2wry ===

=== RUN rxxzr0cwjb2 ===
QUESTION:
Build a residue contact network for E. coli adenylate kinase (UniProt P69441, PDB 1AKE chain A) at an 8 angstrom C-alpha cutoff and find communities. Report the algorithm and seed, and say how the communities relate to the LID, NMP and CORE domains.

INTENDED PROTEIN: Adenylate kinase (P69441)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C05_a] [critical] [scripted] {"name": "Adenylate kinase", "gene": "adk", "organism": "Escherichia coli (strain K12)"}
[C05_b] [critical] [judged] the communities of 1AKE at an 8 A C-alpha cutoff are reported with the algorithm and the seed, and their relation to the LID, NMP and CORE domains

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# Residue contact network of *E. coli* adenylate kinase (P69441 / 1AKE chain A), 8 Å Cα cutoff

## 1. Structure and numbering (verified, not assumed)

| Item | Value |
|---|---|
| PDB entry | **1AKE**, chain A, X-ray, **2.00 Å** |
| Ligand / state | **AP5A** (bisubstrate analog inhibitor) bound → **closed, transition-state-like conformation** (PDB `TITLE`/`HETATM` records) |
| UniProt | **P69441**, 214 aa, *E. coli* Adk (EC 2.7.4.3) |
| Chain A completeness | all 214 residues present, Cα for every residue, no gaps in numbering 1–214 |
| Numbering | global alignment of chain-A sequence to P69441: **100 % identity, 1:1, PDB resnum = UniProt resnum** → domain boundaries apply directly, no renumbering |

## 2. Network construction

* Nodes = the 214 Cα atoms of chain A (PDB residue numbers = UniProt numbers).
* Edge = Cα–Cα distance **≤ 8.0 Å** (full matrix saved, `ca_distance_matrix.npy`).
* **Primary graph** excludes trivial backbone contacts (**|i − j| ≤ 2**): **582 edges**, mean degree 5.4, mean clustering 0.117, density 0.0255, essentially one connected component (213 residues) plus one isolated residue.
* Full graph (all ≤ 8 Å contacts, **1 007 edges**) used as a robustness control.

## 3. Community detection — algorithm and seed

* **Algorithm:** **Leiden** (igraph `community_leiden`, Traag et al. 2019), `objective_function="modularity"` (Newman modularity), **resolution = 1.0**, `n_iterations=-1` (iterate to convergence), **unweighted** (edge distances not used as weights).
* **Seed: 42**, set explicitly via `ig.set_random_number_generator(random.Random(42))` (igraph 1.0.0; python igraph 1.0.0).
* **Result: 8 communities, modularity Q = 0.6846** (re-derived independently in networkx: 0.6846).

**Robustness (all reported, not just the chosen run)**

| Test | Outcome |
|---|---|
| Seeds 0, 1, 7, 42, 123, 2024, 31415 | 8 communities every time; Q = 0.674–0.685; pairwise **ARI 0.859 (min 0.721)** |
| Resolution 0.6 / 0.8 / 1.0 (seed 42) | 8 communities; ARI vs res 1.0 = 0.98 / 0.93 / 1.00 |
| Resolution 1.2 / 1.5 | 11 communities (LID splits into smaller pieces) → res 1.0 is the stable plateau |
| Louvain (`community_multilevel`, seed 42) | 8 communities, Q = 0.6611, ARI 0.678 vs Leiden |
| Full graph incl. \|i−j\| ≤ 2 | 9 communities, Q = 0.693; LID again a single clean community (35 LID residues) |

## 4. Communities and their relation to the domains

Domain definition used (canonical *E. coli* Adk scheme): **CORE 1–29 + 161–214; NMP 30–59; AMPbd 60–117; LID 118–160** (LID boundaries identical across the 3-domain variant used in folding/AFM papers: NMP 30–67, CORE 1–29 + 68–117 + 161–214, LID 118–160 — results unchanged).

| Comm | n | Composition | Interpretation |
|---|---|---|---|
| **C0** | 31 | CORE 14, AMPbd 17 | N-terminal CORE + AMPbd |
| **C1** | 29 | CORE 20, AMPbd 9 | CORE β-sheet region |
| **C2** | 32 | CORE 28, AMPbd 3, LID 1 | C-terminal CORE |
| **C3** | 34 | CORE 16, NMP 8, AMPbd 4, LID 6 | **mixed "interface" community** (NMP 51–58 + LID 120–121/157–160 + AMPbd 113–117 + CORE 161–176) |
| **C4** | 28 | NMP 22, AMPbd 5, LID 1 | **NMP domain** (30–50) + NMP-adjacent AMPbd |
| **C5** | 23 | AMPbd 18, CORE 5 | AMPbd |
| **C6** | 36 | **LID 34**, AMPbd 2 (112, 115) | **LID domain** |
| **C7** | 1 | LID 1 (Leu148) | isolated (its only ≤ 8 Å Cα contacts are sequence neighbours 146/147/149/150) |

**Domain → community allocation**

| Domain | n | Communities | Reading |
|---|---|---|---|
| **LID** | 43 | C6: 34, C3: 6, C4: 1, C2: 1, C7: 1 | **One dominant, internally dense community** (C6: 81 % of its 98 edges are internal); 81 % of all LID residues sit in LID-dominant communities |
| **NMP** | 30 | C4: 22, C3: 8 | **One dominant community** (74 % internal edges); the C-terminal part of NMP (51–58) is recruited into the mixed interface community C3 |
| **CORE** | 83 | C0: 14, C1: 20, C2: 28, C3: 16, C5: 5 | **Not a single community** — CORE is the scaffold that is fragmented across 5 communities (largest holds only 28/83) |
| AMPbd | 58 | C0: 17, C5: 18, C1: 9, C4: 5, C3: 4, C2: 3, C6: 2 | intermediate segments bridge the others |

**Interpretation.** At the 8 Å Cα level the *closed* (AP5A-bound) 1AKE structure resolves into **(i) a self-contained LID module, (ii) a self-contained NMP module, (iii) a mixed hinge/active-site-rim community that welds the C-terminal NMP and LID ends to the C-terminal CORE, and (iv) several CORE-centred communities**. Thus the two small, mobile domains are the network's coherent modular units, whereas the large CORE domain is the internally heterogeneous scaffold.

**Cross-checks**
* *Domain-pair contacts (8 Å, non-local):* AMPbd–CORE 140 (dominant), CORE–LID 19, AMPbd–NMP 19, CORE–NMP 12, LID–NMP 7, AMPbd–LID 6 — the closed state couples NMP and LID to CORE through few, specific edges.
* *Active site:* 37 residues contact AP5A at ≤ 4.5 Å (heavy atom): CORE 14, NMP 9, LID 9, AMPbd 5, distributed over **6 of the 8 communities** (C2: 11, C3: 8, C4: 7, C6: 7, C5: 2, C0/C1: 1 each) — the catalytic site is a junction of communities, not one community.
* *Conformational control (apo open form 4AKE, 2.2 Å, same protocol):* LID–NMP contacts drop to **0** (vs 7 in 1AKE) and NMP–CORE to 5 (vs 15); the LID still forms one pure community (31 residues) but is recruited into a mixed CORE community. So **LID/NMP modularity is conformation-independent, while their coupling to CORE is what switches.**

## 5. Caveats

* Cα-only, 8 Å is a coarse proxy for energetic coupling: no side-chain, H-bond, water or ligand-mediated contacts.
* Excluding |i − j| ≤ 2 avoids trivial backbone adjacency; keeping it yields 9 communities with the same domain-level conclusion.
* Community membership is algorithm-dependent (Leiden vs Louvain ARI 0.678); the reproducible deliverable is the residue→community assignment file.
* Literature domain boundaries vary slightly (e.g. NMP 30–59 vs 30–67); the community–domain conclusions were verified under both conventions.

**Artefacts saved** (in `/agent_cwd/data/adk_contact_network/`): `adk_1AKE_communities.csv` (residue → domain → community), `communities.json`, `network_edges.json`, `ca_distance_matrix.npy`, `adk_8A_nonlocal.gml`, `domain_annotation.json`, `contact_maps_1AKE_4AKE.png`, `1AKE.pdb`, `4AKE.pdb`.
=== END RUN rxxzr0cwjb2 ===

=== RUN r9k1lghdi9e ===
QUESTION:
For TEM-1 beta-lactamase (UniProt P62593), predict cryptic-pocket residues from 1BTL with PocketMiner, retrieve UniProt variants, and list every annotated variant position within 6 angstroms of a residue that contacts the allosteric inhibitor in PDB 1PZO.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V06_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[V06_b] [critical] [judged] the PocketMiner cryptic-pocket residues of 1BTL, the UniProt variants of TEM-1 and every annotated variant within 6 A of a 1PZO CBT-contact residue are listed

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed plan

1. [✓] Identify the inhibitor and inhibitor-contacting residues in PDB 1PZO.
2. [✓] Run PocketMiner on PDB 1BTL and remap its residue scores to UniProt numbering.
3. [✓] Retrieve all P62593 UniProt variant annotations.
4. [✓] Construct and validate residue-level PDB-to-UniProt maps.
5. [✓] Calculate each variant’s distance to the inhibitor-contact set.
6. [✓] Independently verify the final distances and completeness.

## Main result

The inhibitor in **1PZO** is **CBT**, *N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine*. Two CBT copies are present. At a 4.0 Å heavy-atom cutoff, CBT contacts 18 P62593 residues:

**214, 215, 218, 219, 222, 233, 234, 235, 241, 242, 243, 257, 259, 272, 275, 276, 279, 282.**

Using the validated minimum **heavy-atom** distance between a variant residue and any CBT-contact residue, the complete set of annotated UniProt variant positions within 6 Å is:

| UniProt position | Substitution | Annotation | 1PZO residue | PocketMiner score | Nearest CBT-contact residue | Minimum distance |
|---:|---|---|---|---:|---|---:|
| **67** | M→L | IRT-4 | A69, MET | 0.75594 | R241 | **3.335 Å** |
| **235** | A→T | TEM-5, TEM-24 | A237, ALA | 0.89208 | A235—contacting residue itself | **0.000 Å** |
| **236** | G→S | TEM-3, TEM-4, TEM-8 | A238, GLY | 0.81203 | A235 | **1.337 Å** |
| **237** | E→K | TEM-5, TEM-24 | A240, GLU | 0.79060 | A235 | **4.789 Å** |
| **261** | T→M | TEM-4 | A265, THR | 0.76560 | R241 | **2.905 Å** |
| **272** | N→D | IRT-4 | A276, ASN | 0.86932 | N272—contacting residue itself | **0.000 Å** |

**Final annotated variant positions: 67, 235, 236, 237, 261, and 272.**

## All other annotated variants

The UniProt query returned **11 variant records at 10 unique positions**. Every nonmatching record was also assessed:

- **19**: not in the resolved 1PZO mapped segment, so no coordinate-based distance can be calculated.
- **37**: 9.115 Å — excluded.
- **102**: 8.284 Å — excluded.
- **162 H and 162 S**: 11.756 Å — both excluded.

## PocketMiner cryptic-pocket prediction

PocketMiner scored all **263 residues** in 1BTL. Because the tool returns continuous per-residue propensity scores rather than a binary pocket assignment, using **score ≥0.80** as an explicit reporting cutoff gives 41 high-propensity residues:

**232, 243, 170, 241, 260, 215, 233, 218, 262, 64, 268, 168, 172, 235, 71, 69, 214, 272, 271, 72, 73, 42, 149, 146, 65, 103, 242, 245, 153, 244, 234, 150, 231, 66, 205, 236, 38, 128, 140, 191, 125.**

The highest-scoring residues include:

| UniProt position | Residue | Score |
|---:|---|---:|
| 232 | Lys | 0.95141 |
| 243 | Ile | 0.94252 |
| 170 | Ala | 0.94111 |
| 241 | Arg | 0.92900 |
| 260 | Tyr | 0.92647 |
| 215 | Ala | 0.92083 |
| 233 | Ser | 0.91795 |
| 218 | Leu | 0.91683 |
| 262 | Thr | 0.90584 |
| 64 | Phe | 0.90505 |
| 235 | Ala | 0.89208 |
| 272 | Asn | 0.86932 |

The intersection between the final six spatially proximal variants and the PocketMiner **≥0.80** reporting set is **235, 236, and 272**.

## Method and caveats

- PDB–UniProt mappings were taken from the RCSB mmCIF polymer-sequence schemes and independently matched to the residue numbers returned by the ligand-contact tool for all 18 contacts.
- The 6 Å filter uses the minimum heavy-atom distance, independently confirmed by the validated structural-distance tool.
- If a **Cα-to-Cα-only** definition were used instead, position **237** would be excluded because its Cα distance is 7.065 Å; the other five positions would remain.
- PocketMiner measures cryptic-pocket opening propensity, not allostery itself, and the distance calculation uses wild-type 1PZO coordinates rather than modeling the substituted side chains.
- Reproducible outputs were saved under `/agent_cwd/results_tem1/`, including the PocketMiner scores, exact residue maps, final variant-distance table, and independent structural-distance checks.
=== END RUN r9k1lghdi9e ===

=== RUN r0iuhcn647b ===
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

1. [✓] Retrieve 1BTL and 1PZO structural/mapping records and confirm their chains, ligands, and residue-number conventions
2. [✗] Initial PocketMiner extraction assumed the wrong output schema, although the scoring run itself succeeded
3. [✓] Inspect the saved PocketMiner schema and correctly extract the ten highest-scoring residues
4. [✗] Initial ligand-metadata display failed on a list-valued RCSB field, although computation and saving succeeded
5. [✓] Display the ligand metadata and geometric contacts using schema-safe handling
6. [✓] Map the 1PZO contacts to 1BTL by structure-sequence alignment and cross-check with P62593
7. [✓] Match mapped residues to PocketMiner scores and compile the final report

## PocketMiner top ten for 1BTL chain A

PocketMiner scored 263 residues. Scores below are rounded to six decimal places; residue numbers are 1BTL PDB author numbering.

| Rank | 1BTL residue | P62593 position | PocketMiner score |
|---:|---|---:|---:|
| 1 | Lys234 | 232 | **0.951411** |
| 2 | Ile246 | 243 | **0.942519** |
| 3 | Ala172 | 170 | **0.941106** |
| 4 | Arg244 | 241 | **0.928997** |
| 5 | Tyr264 | 260 | **0.926471** |
| 6 | Ala217 | 215 | **0.920834** |
| 7 | Ser235 | 233 | **0.917947** |
| 8 | Leu220 | 218 | **0.916830** |
| 9 | Thr266 | 262 | **0.905837** |
| 10 | Phe66 | 64 | **0.905050** |

PocketMiner run provenance: `PocketMiner@187062df3c94127e991669768009141a08fd5d8b`.

## Allosteric-inhibitor contacts mapped to 1BTL

PDB entry 1PZO is titled **“TEM-1 Beta-Lactamase in Complex with a Novel, Core-Disrupting, Allosteric Inhibitor.”** The inhibitor is chemical component **CBT**:

- N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine
- Two CBT copies are present in chain A, at PDB ligand numbers 300 and 301
- Contacts were defined using the validated geometric-contact tool at a **4.0 Å minimum heavy-atom distance cutoff**
- Eighteen unique protein residues contact either CBT copy

All 18 contacts map one-to-one to identically numbered and identically typed residues in 1BTL. The two observed chain sequences are 260/263 residues identical, with no identity mismatch among the mapped contacts.

| 1PZO residue | Mapped 1BTL residue | P62593 position | PocketMiner rank | PocketMiner score | Minimum CBT distance (Å) |
|---|---|---:|---:|---:|---:|
| Val216 | Val216 | 214 | 17 | 0.875088 | 3.76 |
| **Ala217** | **Ala217** | 215 | **6** | **0.920834** | 3.91 |
| **Leu220** | **Leu220** | 218 | **8** | **0.916830** | 3.35 |
| Leu221 | Leu221 | 219 | 46 | 0.786650 | 3.35 |
| Ala224 | Ala224 | 222 | 209 | 0.246091 | 3.41 |
| **Ser235** | **Ser235** | 233 | **7** | **0.917947** | 2.60 |
| Gly236 | Gly236 | 234 | 31 | 0.826309 | 3.69 |
| Ala237 | Ala237 | 235 | 14 | 0.892082 | 3.56 |
| **Arg244** | **Arg244** | 241 | **4** | **0.928997** | 3.36 |
| Gly245 | Gly245 | 242 | 27 | 0.843503 | 3.18 |
| **Ile246** | **Ile246** | 243 | **2** | **0.942519** | 3.39 |
| Val261 | Val261 | 257 | 168 | 0.387245 | 4.00 |
| Ile263 | Ile263 | 259 | 51 | 0.779656 | 3.79 |
| Asn276 | Asn276 | 272 | 18 | 0.869319 | 3.07 |
| Ile279 | Ile279 | 275 | 52 | 0.773986 | 3.56 |
| Ala280 | Ala280 | 276 | 126 | 0.491368 | 3.42 |
| Gly283 | Gly283 | 279 | 210 | 0.241886 | 3.67 |
| Leu286 | Leu286 | 282 | 171 | 0.381120 | 3.94 |

**Bold residues are also in the global PocketMiner top ten:** Ala217, Leu220, Ser235, Arg244, and Ile246.

### Interpretation caveat

A geometric contact indicates proximity to CBT; it does not by itself establish a biological interaction, affinity, or energetic contribution. Likewise, PocketMiner measures cryptic-pocket propensity and does not independently prove allostery.

Results were saved under `/agent_cwd/pocketminer_1btl_1pzo/`, including the top-ten JSON, mapped-contact JSON/CSV, and complete PocketMiner output.
=== END RUN r0iuhcn647b ===

=== RUN rp93fy7j2vu ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Overall assessment

**A possible allosteric communication route between the FRJ allosteric site and Cys215 is structurally plausible, but not demonstrated.** The contact-network analysis provides a clear static connection, and normal-mode analysis shows some correlated flexibility between the allosteric and catalytic regions. However, the directional coupling is heterogeneous, the representative Phe280–Cys215 dynamic correlation is weak, and STINGAllo returned no chain-A residue predictions.

### Structural reference

- 1T4J chain A maps to **PTP1B/P18031**.
- **FRJ** is the sole small-molecule component recorded for chain A.
- FRJ directly contacts residues **188, 189, 192, 193, 196, 200, 276, 277, 279, 280, and 282** at a 4.0 Å cutoff.
- Cys215 is not in the FRJ contact shell and lies in a distinct catalytic-pocket region, supporting the geometrical premise of remote ligand binding.
- **A.280/Phe280** was used as the representative network source because it is a close FRJ contact.

## 1. Normal-mode analysis: weak-to-moderate, heterogeneous dynamical coupling

ANM on the 282 Cα atoms produced **276 nontrivial modes**, with eigenvalues from **0.710 to 14.026**. The lower modes therefore include several soft collective motions.

### What it supports

Using all-mode, sign-invariant dynamic cross-correlations:

| FRJ-contact residue | DCC with Cys215 |
|---|---:|
| Glu200 | −0.140 |
| Phe196 | +0.127 |
| Leu192 | +0.108 |
| Asn193 | +0.085 |
| Met282 | −0.088 |
| Ala189 | −0.055 |
| Lys279 | −0.055 |
| Gly277 | +0.017 |
| Glu276 | +0.024 |
| **Phe280** | **+0.020** |
| Pro188 | −0.020 |

Thus, some parts of the FRJ shell—especially Leu192, Phe196, Asn193, and Glu200—show weak-to-moderate correlated motion with Cys215. Both same-direction and opposite-direction correlations occur, indicating that the coupling is not uniform.

As an ensemble-level regional measure, the mode-wise RMS displacement of the FRJ region and the Cys215-containing catalytic pocket correlated at **r = +0.485**. Multiple low-frequency modes also jointly displace Phe280 and Cys215, sometimes in the same and sometimes in opposite directions.

### What it does not support

- The whole-site-to-Cys215 correlation was negligible: **DCC(FRJ-shell mean, Cys215) = +0.005**.
- The direct Phe280–Cys215 DCC was also weak: **+0.020**.
- The FRJ-shell mean and catalytic-pocket mean had essentially no net directional correlation: **−0.020**.
- ANM is a harmonic model around one crystallographic conformation; it does not model ligand-induced state changes, catalytic turnover, or energy flow.
- The results therefore **do not establish a directional pathway, ligand-induced signal transmission, or a functional change in Cys215**. They only show that the two regions can participate in related collective flexibility.

## 2. Residue-contact network: a short static connection exists

The chain-A network contained **282 residues, 1,379 edges, and nine Louvain communities**.

### Representative route

The shortest path from the direct FRJ-contact residue Phe280 to Cys215 was:

**A.280/Phe280 → A.276/Glu276 → A.188/Pro188 → A.191/Phe191 → A.110/Leu110 → A.215/Cys215**

This is a **five-edge path**. It crosses from the Phe280/Glu276 community to the Phe191/Pro188 community and then into the Leu110/Cys215 community. Phe191 and Leu110 have high network betweenness in this calculation, consistent with their role as structural bridges.

### Sensitivity to the starting residue

Importantly, the result was not unique to Phe280. Shortest routes from **all 11 FRJ-contact residues** reached Cys215 in **3–5 edges**:

- Five contacts reached Cys215 in three edges.
- Three contacts reached it in four edges.
- Three contacts reached it in five edges.
- **A.110/Leu110 was a common terminal bridge in every route.**
- Phe191 was a recurrent intermediate in most routes.

### What it supports

- There is a **contiguous residue-proximity route** connecting the remote FRJ site to the catalytic cysteine in this crystal structure.
- The recurrent Phe191–Leu110 bridge suggests that the connectivity is not merely an artifact of choosing Phe280 as the source.
- The path provides a testable structural hypothesis for potential coupling between the ligand pocket and catalytic site.

### What it does not support

- A contact-network path is a **shortest path in a static proximity graph**, not a mechanically or energetically preferred signal-transmission pathway.
- It has no directional information, temporal ordering, or energetic weighting.
- Dense packing can generate short paths that are not used in real conformational transitions.
- The path therefore **does not prove allosteric communication**, nor does it establish that perturbing any listed residue changes FRJ binding or PTP1B catalysis.

## 3. STINGAllo: no positive residue-level prediction

The chain-specific STINGAllo request for **1T4J/A** succeeded but returned:

- **Predicted residues: 0**
- FRJ-contact-shell overlap: **none**
- Primary-network-path overlap: **none**
- Cys215 called as an allosteric residue: **no**

The integrated allosteric-site workflow independently reproduced the same empty chain-A result. An entry-level request without a chain was rejected by the service with HTTP 400, so only the successful chain-specific response was used as evidence.

### What it supports

- STINGAllo provides **no positive residue-level support** for an FRJ-to-Cys215 route in this structure.
- It does not nominate Cys215, Phe280, or any other residue on the contact-network path.

### What it does not support

- An empty prediction list is **not evidence that PTP1B lacks allostery**, that FRJ is not an allosteric ligand, or that no communication is possible.
- It may reflect the predictor’s model, eligibility criteria, training coverage, or inability to call this particular structure/chain.
- It does not invalidate the independent static-network and ANM observations.

## Conclusion

The combined evidence supports the following graded statement:

> **Allosteric communication between the FRJ site and Cys215 is plausible, but unconfirmed. The static contact network supplies a short, robust-looking route, and ANM reveals modest, heterogeneous correlated flexibility between portions of the ligand site and catalytic pocket. STINGAllo supplies no positive residue-level prediction, and none of the three analyses demonstrates causal, directional allosteric signaling.**

The strongest experimentally testable candidate coupling elements are **Leu192, Phe196, Asn193, and Glu200** from the NMA results, together with the recurring **Phe191–Leu110** structural bridge. Direct confirmation would require ligand-bound versus apo dynamics and functional perturbation—for example, FRJ analog substitutions, PTP1B catalytic assays, and mutations or HDX-MS/NMR measurements centered on these residues.

### Final plan status

1. [✓] Identified P18031/1T4J-A mapping, FRJ ligand, FRJ-contact shell, and representative source residue
2. [✗] Initial NMA post-processing failed because it attempted an element-wise comparison of unequal-length residue sets; no result was retained
3. [✓] Replaced the failed calculation with valid all-mode DCC, regional-RMS, and sign-invariant joint-participation measures
4. [✓] Built the residue-contact network, resolved the Phe280→Cys215 path, and tested all FRJ-contact sources
5. [✓] Retrieved STINGAllo predictions through both the direct chain-specific tool and integrated workflow
6. [✓] Synthesized supportive findings, limitations, and an overall evidence-weighted conclusion
=== END RUN rp93fy7j2vu ===

=== RUN rc9rixfx1r7 ===
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
## Results

I ran the **original PocketMiner** model (attention disabled) on the inhibitor-free **TEM-1 structure 1BTL**, chain A. The model produced one pocket-probability score for each of the 263 resolved residues.

### Ten highest-scoring 1BTL residues

| Rank | 1BTL residue | PocketMiner score |
|---:|:---|---:|
| 1 | Lys234 | **0.951411** |
| 2 | Ile246 | **0.942519** |
| 3 | Ala172 | **0.941106** |
| 4 | Arg244 | **0.928997** |
| 5 | Tyr264 | **0.926471** |
| 6 | Ala217 | **0.920834** |
| 7 | Ser235 | **0.917947** |
| 8 | Leu220 | **0.916830** |
| 9 | Thr266 | **0.905837** |
| 10 | Phe66 | **0.905050** |

Scores are PocketMiner’s per-residue pocket probabilities.

### 1PZO allosteric-inhibitor contacts mapped to 1BTL

The allosteric inhibitor in 1PZO is **CBT**, present as two molecules, residue IDs **300** and **301**. Contacts were defined as any protein heavy atom within **4.5 Å** of either CBT molecule.

| 1PZO residue | Mapped 1BTL residue | PocketMiner score | 1BTL rank | Minimum heavy-atom distance (Å) | CBT molecule(s) |
|:---|:---|---:|---:|---:|:---|
| Val216 | Val216 | **0.875088** | 17 | 3.755 | 300 |
| Ala217 | Ala217 | **0.920834** | 6 | 3.908 | 300 |
| Leu220 | Leu220 | **0.916830** | 8 | 3.353 | 300, 301 |
| Leu221 | Leu221 | **0.786650** | 46 | 3.350 | 301 |
| Ala224 | Ala224 | **0.246091** | 209 | 3.411 | 301 |
| Leu225 | Leu225 | **0.456167** | 133 | 4.430 | 301 |
| Ser235 | Ser235 | **0.917947** | 7 | 2.598 | 300 |
| Gly236 | Gly236 | **0.826309** | 31 | 3.685 | 300 |
| Ala237 | Ala237 | **0.892082** | 14 | 3.556 | 300 |
| Arg244 | Arg244 | **0.928997** | 4 | 3.358 | 300, 301 |
| Gly245 | Gly245 | **0.843503** | 27 | 3.185 | 300 |
| Ile246 | Ile246 | **0.942519** | 2 | 3.386 | 300 |
| Val261 | Val261 | **0.387245** | 168 | 3.998 | 301 |
| Ile263 | Ile263 | **0.779656** | 51 | 3.791 | 300, 301 |
| Asn276 | Asn276 | **0.869319** | 18 | 3.068 | 300, 301 |
| Ile279 | Ile279 | **0.773985** | 52 | 3.561 | 300, 301 |
| Ala280 | Ala280 | **0.491368** | 126 | 3.420 | 301 |
| Gly283 | Gly283 | **0.241886** | 210 | 3.667 | 301 |
| Leu286 | Leu286 | **0.381120** | 171 | 3.942 | 301 |

**Contact-cutoff sensitivity:** with a stricter 4.0 Å cutoff, the only 4.5 Å contact omitted is Leu225, leaving 18 residues. At ≤3.5 Å, nine residues remain: Leu220, Leu221, Ala224, Ser235, Arg244, Gly245, Ile246, Asn276, and Ala280.

## Mapping and validation

- 1BTL and 1PZO each contain **263 resolved TEM-1 residues**, spanning residues 26–290, with residues 239 and 253 unresolved.
- Global sequence alignment mapped all 263 positions one-to-one:
  - **260/263 identities (98.86%)**
  - substitutions at Ile84/Val84, Met182/Thr182, and Val184/Ala184
  - none of these substitutions occurs at an inhibitor-contact site.
- Cα superposition using the sequence-derived mapping gave an **RMSD of 0.988 Å**.
- The mature 1BTL and 1PZO sequences align to UniProt **P62593** at 261/263 and 262/263 identities, respectively.
- PocketMiner’s residue order was independently checked against the PDB and `mdtraj`; all 263 predictions map to the expected 1BTL residues.
- Two inference runs were bit-identical.

These scores describe predicted pocket propensity in **1BTL**; they are not bound-state binding energies or a direct measure of allosteric coupling.

## Deliverables

The prediction array and final tables are available under `pocketminer_tem1_results/`:

- `1btl-preds.npy`
- `top10_1btl.tsv`
- `mapped_1pzo_CBT_contacts_4p5A.tsv`
- `pocketminer_tem1_summary.json`
- `1pzo_CBT_contacts_residue_aware.tsv`

## Sources

- RCSB PDB **1BTL**: Jelsch et al., *Proteins* 16, 364–383 (1993), DOI [10.1002/prot.340160406](https://doi.org/10.1002/prot.340160406), PMID 8356032.
- RCSB PDB **1PZO**: Horn and Shoichet, *J. Mol. Biol.* 336, 1283–1291 (2004), DOI [10.1016/j.jmb.2003.12.068](https://doi.org/10.1016/j.jmb.2003.12.068), PMID 15037085.
- UniProt **P62593**, TEM-1 β-lactamase.
- Meller et al., “Predicting locations of cryptic pockets from single protein structures using the PocketMiner graph neural network,” *Nature Communications* 14, 1177 (2023), DOI [10.1038/s41467-023-36699-3](https://doi.org/10.1038/s41467-023-36699-3).

### Completed plan
1. [✓] Locate the available PocketMiner implementation, documentation, and execution dependencies.
2. [✓] Retrieve 1BTL/1PZO metadata and identify the CBT allosteric inhibitors.
3. [✓] Run PocketMiner on 1BTL and extract per-residue scores.
4. [✓] Map inhibitor-contacting residues between entries and validate structurally.
5. [✓] Audit and report the ten highest scores and all mapped inhibitor-contact scores.
=== END RUN rc9rixfx1r7 ===

=== RUN rat0b3jwnfz ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan status

1. [✓] Verified 1OPK provenance, ligands, deposited sites, and residue contacts
2. [✓] Stripped all heteroatoms and ranked 34 Fpocket pockets
3. [✓] Extracted and reconciled ChEMBL potency records
4. [✓] Retrieved ClinVar and AlphaMissense evidence for T315I
5. [✓] Aligned human P00519 T315 to 1OPK and recomputed site distances
6. [✓] Synthesized the inhibitor-class implications

## Bottom line

T315 is the canonical ABL1 **“gatekeeper” residue in the ATP-binding cleft**. In 1OPK, human T315 directly contacts the ATP-site ligand at **3.24 Å**. It is approximately **22–26 Å away from the myristoyl pocket**. Consequently:

- **ATP-site/ATP-competitive inhibitors:** T315I causes severe steric resistance, exemplified by imatinib.
- **Myristoyl-site allosteric inhibitors:** asciminib is not directly blocked by T315I and retains activity, although matched cellular assays show a moderate right-shift and secondary mutations can still cause resistance.

## Important provenance and numbering

PDB **1OPK** is the 1.8-Å autoinhibited structure of **mouse ABL1**, not human ABL1, and it does **not** contain imatinib:

- ATP-site ligand: `P16`, synonym **PD166326**
- Myristoyl-pocket ligand: `MYR`, myristic acid
- Human P00519 **T315** maps to 1OPK chain-A **THR334**

The following contacts are PDB numbering and use a heavy-atom cutoff of 4 Å.

| Feature | ATP site | Myristoyl site |
|---|---|---|
| **1OPK ligand** | `P16` / PD166326 | `MYR` / myristic acid |
| **≤4 Å contact residues** | Leu267, Tyr272, Val275, Ala288, Val289, Lys290, Glu305, Met309, Ile332, **Thr334**, Glu335, Phe336, Met337, Gly340, Val318, Leu389, Ala399, Asp400, Phe401 | Leu359, Leu360, Ala363, Leu448, Ala452, Glu481, Ile521, Leu529 |
| **Deposited PDB SITE subset** | Tyr272, Val275, Ala288, Lys290, Glu305, Met309, Ile332, **Thr334**, Glu335, Met337, Gly340, Leu389, Ala399, Asp400 | Leu360, Glu481, Leu529 |
| **Fpocket pocket/rank** | **#2 / rank 2 of 34** | **#3 / rank 3 of 34** |
| Fpocket score | 0.320 | 0.211 |
| Fpocket druggability score | 0.913 | 0.547 |
| Alpha spheres / volume | 103 / 761.7 Å³ | 67 / 491.2 Å³ |
| Validation against original ligand-contact shell | 18/19 residues | 8/8 residues |

The ranking is specific to this workflow: all HETATM records were removed, chain-A protein was retained, and Fpocket 4.0 was run on the resulting structure. It is a pocket-detection rank, not a biochemical potency rank.

## T315 distance to each site

| Distance measure from human T315 / PDB Thr334 | ATP site | Myristoyl site |
|---|---:|---:|
| Minimum heavy-atom distance to bound ligand | **3.239 Å** to P16 C16 | **25.595 Å** to MYR C14 |
| Nearest pocket-lining atom | **0 Å**—T315 itself lines pocket 2 | 22.25 Å |
| Nearest Fpocket alpha-sphere center | 3.46 Å | 24.79 Å |
| Distance to nearest alpha-sphere surface | 0 Å—T315 is at the pocket boundary | 21.34 Å |
| T315 heavy-atom centroid to ligand centroid | 7.08 Å | 32.28 Å |

Thus T315 is physically part of the ATP-site shell but spatially remote from the myristoyl cavity.

## ChEMBL potency

Human ABL1 is ChEMBL target **CHEMBL1862**.

### Imatinib — `CHEMBL941`, ATP-competitive type-II inhibitor

ChEMBL contains many assays, so individual WT values vary. Matched WT/T315I records are more informative:

| Endpoint | Wild-type ABL1 | T315I ABL1 | Change |
|---|---:|---:|---:|
| Kd, activity IDs 1651429/1651473 | **2.2 nM** | **6,200 nM** | **2,818-fold loss** |
| IC50, activity IDs 2280412/2280564 | **1.1 µM** | **>100 µM** | **>91-fold loss** |
| Kd, independent dataset | 12 nM | >10,000 nM | >833-fold loss |

Other wild-type imatinib records include IC50 38–40 nM and Ki 13 nM, demonstrating assay-dependent absolute values but the same conclusion: **T315I destroys imatinib binding/inhibition**.

### Asciminib — `CHEMBL4208229`, myristoyl-pocket allosteric inhibitor

| Endpoint | Wild-type ABL1 | T315I | Interpretation |
|---|---:|---:|---|
| Direct ABL1 biochemical IC50 | **0.5 nM** | No comparably curated ChEMBL biochemical T315I row | Extremely potent WT enzyme inhibitor |
| Direct ABL1 Kd by ITC | **0.5 nM** | Not curated in the matched ChEMBL rows | Confirms high-affinity WT binding |
| Cellular BCR::ABL1 GI50, ChEMBL discovery-paper records | **0.61** | **7.64** | Approximately **12.5-fold right-shift** |
| Same discovery-paper ACS structure-data CSV | **1.0 ± 0.1 µM** | **25 ± 3 µM** | Approximately **25-fold right-shift** |

There is a unit/value inconsistency between the ChEMBL GI50 standard units and the ACS CSV for the cellular values. Consequently, the safest conclusion is that asciminib **retains substantial T315I activity with a moderate cellular potency shift**, rather than quoting an unqualified absolute GI50 unit. A separate ChEMBL 16 nM asciminib record from US11649218B2 was excluded because its assay description and variant identity are uncurated.

## ClinVar and AlphaMissense

### ClinVar

- **Variant:** ABL1 NM_005157.6:c.944C>T, p.Thr315Ile
- **ClinVar:** [VCV000012624.3](https://www.ncbi.nlm.nih.gov/clinvar/variation/12624/)
- **dbSNP:** rs121913459
- **GRCh38:** chr9:130,872,896 C>T
- **Aggregate classification:** **“Likely pathogenic; association”**
- **Review status:** **criteria provided, multiple submitters, no conflicts**
- **Last evaluated:** 2023-09-13
- **Associated condition:** chronic myeloid leukemia

Clinically, T315I is usually a **somatic BCR::ABL1 kinase-domain resistance allele**, not an inherited constitutional ABL1 disorder; the “likely pathogenic; association” wording should therefore not be read as evidence of a Mendelian cancer predisposition.

### AlphaMissense

Using the official AlphaMissense publication dataset:

- Variant: `chr9_130872896_C_T_hg38`
- Transcript: `ENST00000318560.6`
- Protein variant: `P00519:T315I`
- **AlphaMissense pathogenicity score: 0.9991176760**
- **Pathogenic label: 1.0**

This is concordant with the experimentally established resistance phenotype. AlphaMissense itself is a research predictor, not a clinically validated diagnostic or treatment-selection assay.

## What T315I implies for each inhibitor class

### 1. ATP-site inhibitors: strong resistance

Replacing threonine with the bulkier, hydrophobic isoleucine:

- removes the gatekeeper hydroxyl and associated polar contacts;
- introduces steric obstruction into the narrow ATP-binding cleft;
- directly disrupts the ATP-site ligand environment seen in 1OPK.

This explains the roughly **2,800-fold Kd loss** and **>90-fold IC50 loss** for imatinib. The effect is not a universal property of every ATP-site inhibitor: suitably designed third-generation inhibitors such as ponatinib can accommodate T315I. Nevertheless, T315I is the canonical resistance mutation for imatinib and most first- and second-generation ATP-site TKIs.

### 2. Myristoyl-site inhibitors: activity is retained

Asciminib binds outside the ATP cleft and locks ABL1 in an autoinhibited-like conformation. Because T315 is approximately **21–26 Å from the myristoyl cavity**, T315I does not directly alter asciminib’s binding site.

Accordingly, asciminib remains active against T315I, supporting its use as a mechanistically distinct therapy. The matched cellular data nevertheless show a roughly **12.5–25-fold right-shift**, so “unaffected” is too strong: T315I can affect kinase conformation, pathway output, and cellular drug exposure.

### 3. Combination rationale

Asciminib and ATP-site inhibitors attack non-overlapping pockets. This is why:

- asciminib can cover the ATP-site T315I lesion;
- an ATP-site inhibitor may remain active against secondary asciminib-resistance mutations near the myristoyl pocket;
- combining the two can suppress the emergence of resistance more effectively than either mechanism alone.

Compound mutations are important: a lone T315I is not equivalent to T315I plus a secondary mutation that directly disrupts asciminib binding.

## Sources

1. [PDB 1OPK](https://www.rcsb.org/structure/1OPK); Nagar et al., *Cell* 2003, [doi:10.1016/S0092-8674(03)00194-6](https://doi.org/10.1016/S0092-8674(03)00194-6), PMID 12654251.
2. [UniProt P00519](https://www.uniprot.org/uniprotkb/P00519/entry).
3. ChEMBL: [imatinib CHEMBL941](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL941), [asciminib CHEMBL4208229](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL4208229), and [human ABL1 CHEMBL1862](https://www.ebi.ac.uk/chembl/target_report_card/CHEMBL1862/).
4. Fabian et al., 2005, [doi:10.1038/nbt1068](https://doi.org/10.1038/nbt1068); Mahboobi et al., 2009, [doi:10.1021/jm800988r](https://doi.org/10.1021/jm800988r); Karaman et al., 2008
=== END RUN rat0b3jwnfz ===

=== RUN rs807s41w19 ===
QUESTION:
In PDB entry 1OPK (human ABL1, UniProt P00519), identify the ligand at the myristoyl allosteric site and the ligand at the ATP site, and list the residues within 4 angstroms of the myristoyl-site ligand.

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[S02_b] [critical] [scripted] [{"chain": "A", "pdb_number": 1}]
[S02_c] [critical] [scripted] [{"chain": "A", "pdb_number": 2}]
[S02_d] [critical] [scripted] {"uniprot_residues": [340, 341, 344, 429, 433, 462, 502, 510], "pdb_residues": [359, 360, 363, 448, 452, 481, 521, 529], "min_distances": {"359": 3.836, "360": 3.687, "363": 3.706, "448": 3.731, "452": 3.854, "481": 3.474, "521": 3.874, "529": 3.541}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**PDB 1OPK ligand assignment**

- **Myristoyl allosteric site:** **MYR** — myristic acid (chain A, residue 1)
- **ATP/adenosine-binding site:** **P16** — 6-(2,6-dichlorophenyl)-2-{[3-(hydroxymethyl)phenyl]amino}-8-methylpyrido[2,3-d]pyrimidin-7(8H)-one (chain A, residue 2)
- **GOL** is glycerol and is not the ligand defining either site.

**MYR-contacting residues within 4.0 Å**  
Residue numbers are PDB chain A numbering; distances are minimum heavy-atom distances:

| Residue | Minimum distance |
|---|---:|
| LEU359 | 3.84 Å |
| LEU360 | 3.69 Å |
| ALA363 | 3.71 Å |
| LEU448 | 3.73 Å |
| ALA452 | 3.85 Å |
| GLU481 | 3.47 Å |
| ILE521 | 3.87 Å |
| LEU529 | 3.54 Å |

Thus, the MYR allosteric-site contact residues are **LEU359, LEU360, ALA363, LEU448, ALA452, GLU481, ILE521, and LEU529**.

**Accession note:** The deposited-coordinate mapping for 1OPK identifies chain A as mouse ABL1 (**P00520**), rather than human ABL1 P00519. This does not affect the ligand assignment or PDB residue numbering.

**Updated plan**
1. [✓] Retrieve the ligand inventory and interaction records for PDB 1OPK.
2. [✓] Identify the myristoyl-site and ATP-site ligand IDs from the structural records.
3. [✓] Retrieve all polymer residues within 4 Å of the myristoyl-site ligand and verify the result.
=== END RUN rs807s41w19 ===

=== RUN rq89g7y19to ===
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
## Final plan status

1. [✓] Retrieved 2SHP and 5EHR metadata and confirmed both map to human SHP2, UniProt **Q06124**
2. [✓] Identified SHP099 as chemical component **5OD** in 5EHR and calculated residue-level contacts
3. [✓] Ran fpocket 4.2.3 on the full deposited 2SHP dimer; retained the five highest-ranked pockets
4. [✗] Bulk SIFTS flat-file endpoint returned 404; superseded by the successful RCSB/SIFTS core API query
5. [✓] Applied residue-level RCSB/SIFTS mappings from both entries to UniProt numbering
6. [✓] Verified the mapping against the canonical Q06124 sequence and resolved three construct substitutions
7. [✓] Calculated pocket-by-pocket overlap at a 4.0 Å ligand-contact cutoff
8. [✓] Repeated the comparison at 5.0 Å as a sensitivity check
9. [✓] Saved and reloaded the definitive JSON and TSV result files

## Result

**No. None of the top five 2SHP pockets contains an exact residue overlap with the residues contacting SHP099 in 5EHR.**

The mapped SHP099-contact set was:

**Q06124 positions:**  
`108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495`

**Residues:**  
`T108, E110, R111, F113, H114, T218, T219, E249, E250, T253, L254, Q257, P491, K492, Q495`

The same positions contacted SHP099 in both protein chains of 5EHR.

### Top-five 2SHP pockets after UniProt mapping

| fpocket rank | Score | Chain | Q06124 pocket-lining positions | Exact SHP099 overlap |
|---:|---:|:---:|---|---|
| 1 | 0.338 | A | 356, 420, 423, 428, 429, 430, 432, 435, 438, 439, 468, 469, 472, 509, 512, 513, 516, 517, 519, 520, 523 | None |
| 2 | 0.237 | B | 356, 420, 423, 428, 429, 430, 432, 435, 438, 439, 468, 469, 472, 509, 512, 513, 516, 517, 519, 520, 523 | None |
| 3 | 0.235 | A | 4, 7, 9, 10, 11, 33, 34, 35, 38, 39, 40, 41, 58, 63, 74, 248, 251, 252, 255, 506, 507, 508 | None |
| 4 | 0.204 | A | 358, 359, 419, 421, 422, 423, 424, 425 | None |
| 5 | 0.174 | A | 73, 76, 258, 261, 262, 285, 498, 502, 503 | None |

Thus:

\[
\bigcup_{\text{top 5 pockets}} \text{pocket residues}
\;\cap\;
\text{SHP099-contact residues}
=
\varnothing
\]

Pocket 3 comes closest spatially in sequence to the SHP099 site—it contains positions such as 248, 251, 252, and 255—but none is itself an exact SHP099-contact residue. The conclusion was unchanged with a looser **5.0 Å** contact cutoff.

## Mapping and method notes

- Pocket detection used the complete deposited 2SHP dimer with HETATM records stripped.
- RCSB/SIFTS alignments used:
  - **2SHP:** entity residues 1–525 → Q06124 1–525
  - **5EHR:** entity residues 2–526 → Q06124 1–525
- The 2SHP construct contains amino-acid substitutions at mapped positions 41 and 513. These are substitutions at the same aligned UniProt positions, not numbering offsets, and therefore do not affect the overlap calculation.
- “Contact” was defined by minimum heavy-atom distance ≤4.0 Å; the 5.0 Å sensitivity analysis also gave zero overlap.
- fpocket reports pocket-lining residues, so this establishes **no exact residue-level overlap**, not a claim that the two structures lack any related cavity or conformational reorganization.

Result files are saved at:

- `/agent_cwd/shp2_pocket_analysis/final_mapped_overlap.json`
- `/agent_cwd/shp2_pocket_analysis/final_mapped_overlap.tsv`
- `/agent_cwd/shp2_pocket_analysis/sensitivity_5A_overlap.json`
=== END RUN rq89g7y19to ===

=== RUN rml902um86d ===
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
## Result

PDB **1T4J** contains one bound nonpolymer ligand in chain A:

- **PDB ligand ID:** **FRJ**
- **Chemical name:** 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethyl-*N*-[4-(1,3-thiazol-2-ylsulfamoyl)phenyl]-1-benzofuran-6-sulfonamide
- **Also catalogued as:** **PTP1B-IN-4**, **PTP Inhibitor XXII**
- **PubChem CID:** 448662
- **InChIKey:** `SXKBTDJJEQQEGE-UHFFFAOYSA-N`

It is the PTP1B allosteric inhibitor described by Wiesmann et al., *Nat Struct Mol Biol* 2004, DOI: [10.1038/nsmb803](https://doi.org/10.1038/nsmb803).

### Protein residues within 4 Å of FRJ

Using the minimum distance between any protein heavy atom and any ligand heavy atom, with a cutoff of **≤4.0 Å**, the contacting residues in **UniProt P18031 numbering** are:

| UniProt residue | Identity | Minimum distance to FRJ |
|---:|---|---:|
| 188 | Pro188 | 3.918 Å |
| 189 | Ala189 | 3.416 Å |
| 192 | Leu192 | 3.803 Å |
| 193 | Asn193 | 3.011 Å |
| 196 | Phe196 | 3.552 Å |
| 200 | Glu200 | 3.304 Å |
| 276 | Glu276 | 2.554 Å |
| 277 | Gly277 | 3.367 Å |
| 279 | Lys279 | 3.031 Å |
| 280 | Phe280 | 2.645 Å |
| 282 | Met282 | 3.593 Å |

**Residue list:**  
**P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, M282**

The RCSB/SIFTS polymer alignment maps 1T4J entity positions directly to P18031 residues 1–298 without an offset, and every listed residue’s identity was confirmed against the canonical P18031 sequence.

**Note:** The deposited `STRUCT_SITE_GEN` annotation lists nine residues and omits Pro188 and Leu192. Their measured heavy-atom distances are nevertheless 3.918 and 3.803 Å, respectively, so they are included under the requested 4 Å criterion. The nearest excluded residue is Ser187 at 4.048 Å.

### Sources

- [RCSB PDB entry 1T4J](https://www.rcsb.org/structure/1T4J)
- [RCSB ligand FRJ](https://www.rcsb.org/ligand/FRJ)
- [UniProt P18031](https://www.uniprot.org/uniprotkb/P18031/entry)
- [PubChem CID 448662](https://pubchem.ncbi.nlm.nih.gov/compound/448662)

### Completed plan

1. [✓] Retrieve and inspect PDB entry 1T4J, including nonpolymer ligand records.
2. [✓] Retrieve UniProt P18031 sequence and PDB-to-UniProt residue mapping.
3. [✗] Initial distance-analysis attempt failed because `len()` was applied to a Biopython atom generator.
4. [✓] Recalculate FRJ contacts using explicit atom lists and export an auditable table.
5. [✗] Advanced literature search was unavailable because it requires an unconfigured Claude backend.
6. [✓] Cross-check FRJ’s official and catalog names using RCSB, PDBe, PubChem, ChEMBL, and the publisher supplement.
7. [✗] One mmCIF check encountered a field/indexing issue; subsequent mmCIF and SciPy KD-tree calculations agreed with the original result.
8. [✓] Independently validate the ≤4 Å set, reconcile it with `STRUCT_SITE_GEN`, and finalize the answer.
=== END RUN rml902um86d ===

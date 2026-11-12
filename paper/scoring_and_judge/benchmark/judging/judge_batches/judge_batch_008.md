# Judge batch 008 of 24

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

=== RUN rf8wlspa6q2 ===
QUESTION:
On PTP1B entry 1T4J (UniProt P18031) with ligands removed, compare fpocket, P2Rank and PocketMiner: report the rank or score each assigns to the residues that contacted the allosteric ligand, and say which methods agree. State clearly what these methods can and cannot say about allosteric character.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P07_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P07_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P07_c] [critical] [judged] the rank or score each of fpocket, P2Rank and PocketMiner assigns to the FRJ contact residues, which methods agree, and the caveat that a pocket detector cannot label an allosteric pocket
[P07_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P07_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P07_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P07_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PTP1B 1T4J: ligand-free pocket-method comparison

### Setup

- **Structure:** PTP1B, PDB **1T4J**, chain A, mapped to **UniProt P18031**.
- **Allosteric ligand:** **FRJ**. The deposited title is “Allosteric inhibition of protein tyrosine phosphatase 1B” (PMID **15258570**).
- **Ligand removal:** The 41 FRJ HETATM atoms were removed, leaving 2,304 protein ATOM records. All three methods were run on this identical ligand-free file.
- **Contact definition:** heavy-atom distance ≤4.0 Å to FRJ, giving 11 residues. The deposited PDB `SITE` record lists nine of these; **P188 and L192** are additional 4 Å geometric contacts.
- **fpocket/P2Rank:** lower pocket rank means higher-ranked. A residue is assigned to its best-ranked containing pocket.
- **PocketMiner:** higher residue score means greater cryptic-pocket propensity; the rank below is a 1-based global rank among all 282 scored residues, descending by score.

### Residue-level results

| Residue | FRJ distance | fpocket best pocket (score) | P2Rank | PocketMiner score (global rank) |
|---|---:|---:|---|---:|
| P188* | 3.92 Å | **#11** (0.069) | not assigned | 0.316257 (#212/282) |
| A189 | 3.42 Å | **#7** (0.123); also #11 | not assigned | 0.380703 (#181) |
| L192* | 3.80 Å | **#11** (0.069) | not assigned | 0.538886 (#105) |
| N193 | 3.01 Å | **#7** (0.123); also #11 | not assigned | 0.452781 (#143) |
| F196 | 3.55 Å | **#11** (0.069) | not assigned | **0.670946 (#54)** |
| E200 | 3.30 Å | **#16** (0.028) | not assigned | 0.323720 (#208) |
| E276 | 2.55 Å | **#11** (0.069) | not assigned | 0.416562 (#169) |
| G277 | 3.37 Å | **#11** (0.069) | not assigned | 0.426061 (#162) |
| K279 | 3.03 Å | **#8** (0.123) | not assigned | 0.335730 (#203) |
| F280 | 2.65 Å | **#11** (0.069) | not assigned | 0.362357 (#193) |
| M282 | 3.59 Å | **#8** (0.123) | not assigned | 0.326517 (#207) |

\*Additional 4 Å contact; not present in the deposited nine-residue PDB `SITE` annotation.

### Pocket-level findings

- **fpocket**
  - Recovers **all 11 FRJ-contact residues**, but across four pockets: #7, #8, #11 and #16.
  - Its strongest single FRJ-site pocket is **#11**, containing 8/11 contact residues: P188, A189, L192, N193, F196, E276, G277 and F280.
  - Pocket #11 has a relatively low pocket score of **0.069** and is only 11th overall, but a high **druggability score of 0.820**.
  - Thus fpocket detects the region, but does not rank it among its leading pockets.

- **P2Rank**
  - Returns three pockets: #1 (score 7.22, probability 0.376), #2 (2.03, 0.044), and #3 (1.87, 0.037).
  - **None contains any of the 11 FRJ-contact residues.**
  - Its top pocket includes catalytic-site residues such as D181, C215, R221 and Q262, indicating that it preferentially identifies the catalytic/active-site region rather than the FRJ site.

- **PocketMiner**
  - Gives its strongest contact-residue score to **F196** (0.670946, global rank #54), followed by **L192** (0.538886, #105).
  - Only F196 and L192 are in the top half of all scored residues; none is in the top decile.
  - It therefore provides partial support for a subset of the FRJ site, but not a strong or comprehensive match.

### Agreement

- **fpocket alone gives positive pocket-level agreement** with the crystallographic FRJ location: it includes every contact residue in one or more pockets.
- **PocketMiner partially agrees at residue level**, chiefly for F196 and L192, but nine of the eleven contact residues rank below the median.
- **P2Rank does not agree** with the FRO-site assignment: it assigns no FRJ-contact residue to any of its three reported pockets.
- Consequently, there is **no three-way consensus**. fpocket gives the strongest location recovery, PocketMiner gives weaker partial support, and P2Rank misses the FRJ site in this comparison.

### What these results mean—and do not mean

- **fpocket** can detect geometric cavities and estimate properties such as pocket score and druggability. It can say that the ligand-free structure contains a pocket compatible with the FRJ-contacting residues.
- **P2Rank** can rank candidate ligand-binding pockets and provide pocket scores/probabilities. It can say whether a geometric site resembles its learned binding-site features.
- **PocketMiner** can prioritize residues with predicted **cryptic-pocket propensity**. It does not directly output a pocket rank comparable to fpocket or P2Rank.

None of these methods, by itself, can establish that a site is **allosteric**. In particular, they cannot determine whether a site is orthosteric versus allosteric, prove that an unseen ligand will bind, show that a cryptic pocket will open, or demonstrate functional coupling to the catalytic site. Those conclusions require the holo/allosteric structural context and experimental evidence such as site-directed mutagenesis, binding/kinetic measurements, or conformational/dynamic studies. Here, the allosteric character comes from the FRJ-bound crystal structure and deposited annotation—not from the ligand-free pocket predictions.

### Checklist

1. [✓] Identified FRJ and its contact residues  
2. [✓] Prepared an FRJ-free 1T4J structure  
3. [✓] Ran fpocket, P2Rank, and PocketMiner on the same file  
4. [✗] Initial mapping failed because the tools used different residue keys  
5. [✓] Inspected the schemas and completed the robust comparison  
6. [✓] Verified the deposited allosteric annotation and quantified agreement  
7. [✓] Reported results and allosteric-inference limitations
=== END RUN rf8wlspa6q2 ===

=== RUN re8ovlczjxe ===
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
## Mapping and contact definition

- Both **1BTL chain A** and **1PZO chain A** map to **UniProt P62593**.
- A global alignment of the two 263-residue polymer sequences found no gaps and three substitutions: I84V, M182T, and V184A. None occurs in the CBT-contact set, so every contacted 1PZO residue maps to the identically numbered and identically named residue in 1BTL.
- 1PZO contains two copies of the allosteric inhibitor **CBT**—**CBT300** and **CBT301**—with the chemical name *N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine*.
- Contacts were defined as polymer heavy atoms within **4.0 Å** of either CBT copy. This produced **18 unique residues**.

## Ten highest-scoring PocketMiner residues in 1BTL

| Rank | 1BTL residue | PocketMiner score | Contacts CBT in 1PZO? |
|---:|---|---:|---|
| 1 | **A:LYS234** | **0.951411** | No |
| 2 | **A:ILE246** | **0.942519** | Yes |
| 3 | **A:ALA172** | **0.941106** | No |
| 4 | **A:ARG244** | **0.928997** | Yes |
| 5 | **A:TYR264** | **0.926471** | No |
| 6 | **A:ALA217** | **0.920834** | Yes |
| 7 | **A:SER235** | **0.917947** | Yes |
| 8 | **A:LEU220** | **0.916830** | Yes |
| 9 | **A:THR266** | **0.905837** | No |
| 10 | **A:PHE66** | **0.905050** | No |

Thus, **five of the ten highest-scoring residues** are CBT-contact residues: ILE246, ARG244, ALA217, SER235, and LEU220.

## PocketMiner scores for all mapped CBT-contact residues

Listed by decreasing PocketMiner score:

| Mapped 1BTL residue | 1PZO residue | P62593 position | CBT copy | Minimum distance (Å) | PocketMiner score |
|---|---|---:|---|---:|---:|
| **A:ILE246** | ILE246 | 243 | CBT300 | 3.39 | **0.942519** |
| **A:ARG244** | ARG244 | 241 | CBT300, CBT301 | 3.36 | **0.928997** |
| **A:ALA217** | ALA217 | 215 | CBT300 | 3.91 | **0.920834** |
| **A:SER235** | SER235 | 233 | CBT300 | 2.60 | **0.917947** |
| **A:LEU220** | LEU220 | 218 | CBT300, CBT301 | 3.35 | **0.916830** |
| **A:ALA237** | ALA237 | 235 | CBT300 | 3.56 | **0.892082** |
| **A:VAL216** | VAL216 | 214 | CBT300 | 3.76 | **0.875088** |
| **A:ASN276** | ASN276 | 272 | CBT300, CBT301 | 3.07 | **0.869319** |
| **A:GLY245** | GLY245 | 242 | CBT300 | 3.18 | **0.843503** |
| **A:GLY236** | GLY236 | 234 | CBT300 | 3.69 | **0.826309** |
| **A:LEU221** | LEU221 | 219 | CBT301 | 3.35 | **0.786650** |
| **A:ILE263** | ILE263 | 259 | CBT301 | 3.79 | **0.779656** |
| **A:ILE279** | ILE279 | 275 | CBT300, CBT301 | 3.56 | **0.773986** |
| **A:ALA280** | ALA280 | 276 | CBT301 | 3.42 | **0.491368** |
| **A:VAL261** | VAL261 | 257 | CBT301 | 4.00 | **0.387245** |
| **A:LEU286** | LEU286 | 282 | CBT301 | 3.94 | **0.381120** |
| **A:ALA224** | ALA224 | 222 | CBT301 | 3.41 | **0.246091** |
| **A:GLY283** | GLY283 | 279 | CBT301 | 3.67 | **0.241886** |

The highest-scoring CBT-contact residue is **ILE246** at **0.942519**, followed by **ARG244** at **0.928997**, **ALA217** at **0.920834**, **SER235** at **0.917947**, and **LEU220** at **0.916830**.

The contact distances are geometric heavy-atom proximities; they should not be interpreted as binding affinities or as proof of a specific interaction type.
=== END RUN re8ovlczjxe ===

=== RUN rq0g9o2q6ej ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Bottom line

The combined evidence supports the **AKT1 PH–kinase interface as a bona fide allosteric drug-binding site**. Residue E17 is a highly consequential, interface-proximal regulatory residue that can influence inhibitor sensitivity and the PH-in/PH-out conformational equilibrium. However, the 3O96 geometry does **not** establish E17 as a direct ligand-contacting residue: its closest heavy atom is **5.70 Å** from IQO, beyond the 4 Å contact cutoff.

The most defensible interpretation is:

> **The PH–kinase interface itself is experimentally validated as an allosteric site, while E17K is strong evidence for an interface-associated regulatory hotspot rather than a proven direct contact in the modeled inhibitor pose.**

## Evidence synthesis

| Evidence layer | Result | Interpretation |
|---|---|---|
| **PDB 3O96 structure** | The entry is titled “Crystal Structure of Human AKT1 with an Allosteric Inhibitor.” Inhibitor VIII, chemical component **IQO**, is bound at the combined interface of the PH domain and the N- and C-lobes of the kinase domain. | Direct structural validation of the PH–kinase interface as an allosteric site. |
| **IQO contacts** | Eighteen ≤4 Å contacts: W80, T82, V83, I84, E85, S205, L210, T211, L264, K268, V271, Y272, R273, D274, I290, T291, D292, and C296. These span PH- and kinase-domain sides. | The pocket is interface-spanning rather than confined to the catalytic ATP site. |
| **ASD curation** | P31749 is reported as experimentally confirmed as allosteric. The 3O96 site is labeled an **“Inner Protein Regulator”** and its curated residues exactly match the 18 computed IQO contacts. | Independent database confirmation of the structural allosteric-site assignment. |
| **E17 geometry** | E17 is modeled; minimum heavy-atom distance to IQO is **5.70 Å**. It is therefore absent from the ≤4 Å contact list but lies proximally to the allosteric ligand. | E17 is interface/ligand-proximal, but direct atomic contact is not demonstrated in this pose. |
| **MK-2206 ChEMBL data** | P31749/ChEMBL4282 has 19 IC50 records for MK-2206: **5–10,000 nM**, median **10 nM**; 12/19 are ≤100 nM and 7/19 are >1 µM. | Strong, although assay-variable, evidence that AKT1 has a druggable allosteric pharmacology. It does not, by itself, assign MK-2206’s contacts to E17. |
| **ClinVar** | AKT1 p.Glu17Lys, NM_001382430.1:c.49G>A, Variation ID 29022: **Pathogenic**, criteria provided by multiple submitters with no conflicts. | E17K is clinically established as a pathogenic activating AKT1 variant. |
| **AlphaMissense** | E17K score **0.9977**, classified **pathogenic**. | Independent computational support for strong deleterious effect. |
| **Mechanistic literature/UniProt** | E17K increases T308 phosphorylation and membrane recruitment, broadens PH-domain phosphoinositide specificity, and changes the closed PH-in/open PH-out equilibrium. The 3O96 paper reports that Inhibitor VIII is fivefold less potent against E17K and notes that loss of the stabilizing E17–Arg273 interaction shifts AKT1 toward the open PH-out form. | E17 affects the same conformational network that controls allosteric inhibitor binding. |

## Important ligand distinction

IQO/Inhibitor VIII in 3O96 is **not MK-2206**:

- IQO: C34H29N7O  
- MK-2206: C25H21N5O  
- MK-2206: CHEMBL1079175; AKT1 target: CHEMBL4282

Consequently, the structural contacts and E17 distance describe the **3O96/IQO pose**, whereas the ChEMBL data establish the potency of a separate allosteric inhibitor. Together they show convergent allosteric druggability, but they should not be presented as a direct IQO–MK-2206 structural comparison.

## Final interpretation

1. **Site-level conclusion: strong.** The PH–kinase interface is directly validated as an allosteric inhibitor-binding site in 3O96 and independently curated as an allosteric “Inner Protein Regulator” site for AKT1.

2. **E17-level conclusion: supportive but indirect.** E17K is pathogenic, nearly certain to be deleterious by AlphaMissense, changes AKT1 lipid recognition and domain-closing equilibrium, and reduces sensitivity to an allosteric inhibitor. Its 5.70 Å distance from IQO supports proximity, but the modeled pose does not show a direct E17–IQO contact.

3. **Best labeling of E17:**  
   **“Pathogenic, interface-proximing allosteric regulatory residue,”** rather than “direct allosteric ligand-contact residue” or an experimentally proven drug-binding hotspot.

A direct mechanistic claim would require an E17 mutation series with matched PH–kinase-interface structural work and binding/activity measurements, ideally complemented by HDX-MS, NMR, or biochemical allosteric coupling assays.

**Key references:** 3O96 structure, PMID 20886116, DOI 10.1371/journal.pone.0012913; E17K cancer study, PMID 17611497; E17K PH-domain lipid-specificity study, PMID 18954143; ClinVar Variation ID 29022; UniProt P31749.
=== END RUN rq0g9o2q6ej ===

=== RUN rhsc9ubgq5v ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Executive comparison

| Feature | ATP site | Myristoyl site |
|---|---|---|
| Ligand in 1OPK | P16, an ATP-site inhibitor | MYR, myristic acid |
| 4 Å contacts, P00519 numbering | L248, Y253, V256, A269, V270, K271, E286, M290, V299, I313, **T315**, E316, F317, M318, G321, L370, A380, D381, F382 | L340, L341, A344, L429, A433, E462, I502, L510 |
| fpocket rank, ligand-stripped 1OPK | **#2**: score 0.320, druggability 0.913; 18/19 ligand contacts recovered | **#3**: score 0.211, druggability 0.547; 8/8 contacts recovered |
| P2Rank rank, same ligand-stripped file | **#1**: score 23.77, probability 0.892; 17/19 contacts recovered | **#2**: score 11.32, probability 0.606; 8/8 contacts recovered |
| T315 relationship | Direct gatekeeper contact: **3.24 Å** from T315 OG1 to P16 | Spatially remote: **25.59 Å** from T315 to the nearest MYR atom |
| T315-to-ligand-centroid distance | 7.08 Å | 32.28 Å |
| Representative inhibitor | Imatinib, ATP-competitive | Asciminib, allosteric myristoyl/switch-pocket inhibitor |
| T315I implication | Strong loss of imatinib/ATP-site inhibitor binding | Direct binding retained; T315I is not the primary asciminib resistance determinant |

Thus, in this conformation the ATP pocket is the more prominent detected pocket—rank 1–2 depending on detector—whereas the myristoyl pocket is rank 2–3. Pocket rank is a geometric/druggability measure, not a biochemical potency measurement.

## Structural provenance

An important species correction is needed:

- PDB **1OPK** is annotated as ABL1 but maps to **mouse ABL1, UniProt P00520**, not human P00519.
- The deposited kinase-domain coordinates were aligned to human P00519 for the table above. In the relevant segment, human numbering is generally PDB author number minus 19; for example, **PDB A334 = human T315**.
- 1OPK contains P16 and MYR, but it does **not** contain imatinib or asciminib. Its contacts therefore define the ATP and natural myristoyl-pocket geometries, rather than being direct imatinib/asciminib contacts.
- The structure contains an engineered D363N substitution outside the listed contact sets.
- Pocket ranking was repeated on an explicit ATOM-only file with zero HETATM records.

The direct 4 Å contacts came from the deposited coordinates. The P16 contact set includes the ATP gatekeeper T315 and hinge residues E316/F317/M318. The MYR contact set is disjoint from T315.

## ChEMBL potency

### Wild-type P00519/ABL1

- **Imatinib**, CHEMBL941:
  - 91 IC50 records, all in nM: **19.9–100,000 nM**, median **800 nM**.
  - Six Ki records: **13–7,000 nM**, median **25 nM**.
  - These values span heterogeneous biochemical and cellular assays and should not be treated as a single intrinsic constant.
- **Asciminib**, CHEMBL4208229:
  - Biochemical ABL1 IC50: **0.5 nM** (CHEMBL4200739).
  - Kd: **0.5 nM** (CHEMBL4200854).
  - A second P00519 IC50 record is 16 nM (CHEMBL5739300).

### Explicit T315I measurements

- **Imatinib against T315I**
  - IC50 **>100,000 nM** — CHEMBL1022423.
  - Kd **>10,000 nM** — CHEMBL1051277.
  - Another Kd record is 6,200 nM, with the assay noting lack of activity at 10 µM — CHEMBL859873.
  - Thus the gatekeeper mutation produces a very large loss of imatinib binding/activity.

- **Asciminib against T315I**
  - Matched cellular BCR::ABL1 assays:
    - Wild type GI50 **0.61 nM** — CHEMBL4200740.
    - T315I GI50 **7.64 nM** — CHEMBL4200741.
  - This is an approximately **12.5-fold cellular potency shift**, but asciminib retains sub-10 nM cellular potency against T315I.

## T315I clinical and prediction evidence

- **ClinVar variation 27663**: NM_005157.6(ABL1):c.944C>T, p.Thr315Ile.
  - Clinical significance: **“Likely pathogenic; association.”**
  - Review status: criteria provided by multiple submitters, with no conflicts.
- **AlphaMissense**:
  - T315I pathogenicity score **0.9991**.
  - Classification: **pathogenic**.

These establish that T315I is a clinically important, highly deleterious substitution, but neither ClinVar nor AlphaMissense directly predicts drug response; that inference comes from the structure and ChEMBL assays.

## Mechanistic interpretation

### ATP-site inhibitors: T315I is a major resistance determinant

T315 is the ABL1 **gatekeeper residue**. Wild-type threonine places its hydroxyl directly against P16 at 3.24 Å. Replacing the small, polar threonine with bulky, hydrophobic isoleucine introduces steric obstruction at the narrow ATP-site entrance. This explains the direct loss of imatinib binding: wild-type Ki values in the tens of nM become mutant Kd values in the micromolar-to-no-activity range.

Therefore:

- T315I strongly impairs imatinib and many conventional ATP-competitive inhibitors.
- The effect is not necessarily identical for every ATP-site inhibitor; compounds deliberately designed around a gatekeeper substitution may retain varying activity.
- The mutation can also alter ABL1 conformational and catalytic behavior, not merely provide a docking clash.

### Myristoyl/switch-pocket inhibitors: T315I is largely bypassed

The MYR pocket is approximately **25.6 Å** from the nearest T315 atom and **32.3 Å** from the MYR ligand centroid. Asciminib acts in the allosteric myristoyl/switch pocket rather than at the ATP hinge-gatekeeper region. Consequently, T315I does not directly remove asciminib’s principal anchoring interactions.

The matched ChEMBL results support this: asciminib remains active against T315I, although with a measurable potency loss in the cellular assays.

Thus, T315I:

- **Favors resistance to ATP-site/hinge-binding inhibitors.**
- **Does not abolish the myristoyl-site allosteric strategy**, as exemplified by asciminib.
- Does not guarantee complete sensitivity to asciminib, because other ABL1 resistance mechanisms and cellular context can still matter.

## Completed analysis plan

1. [✓] Retrieve 1OPK metadata, ligands, UniProt/PDB mapping, and contacts  
2. [✗] Initial pocket step was only partly valid because auxiliary P2Rank used the original file; corrected in step 9  
3. [✓] Map the ATP and myristoyl/switch-pocket residues to detected pockets  
4. [✓] Retrieve ChEMBL potency records for imatinib and asciminib  
5. [✓] Retrieve ClinVar and AlphaMissense evidence for ABL1 T315I  
6. [✗] Initial distance calculation failed because of an incorrect Bio.PDB atom/residue accessor call; no result was emitted  
7. [✓] Correct the coordinate calculation and human-number mapping  
8. [✓] Verify assay context and final structure provenance  
9. [✓] Re-run both pocket detectors on one explicit ligand-stripped PDB and reconcile ranks  
10. [✓] Synthesize the comparison and inhibitor-class implications
=== END RUN rhsc9ubgq5v ===

=== RUN rsg1vk3ffhc ===
QUESTION:
Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C02_b] [critical] [judged] the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PTP1B residue contact network — 1T4J chain A

**Inputs verified**
- Structure: PDB **1T4J**, chain **A** → UniProt **P18031** (PTN1_HUMAN), author numbering 1–298 (mapping tool: 100% identity, 68.5% coverage).
- Local file used: `/agent_cwd/1T4J_rcsb.cif` (md5 `a380c7bf942ee973a368f7d1eea87f29`, byte-identical to the RCSB download and to the cached copies).
- Bound allosteric ligand: **FRJ** (RCSB chemical component; het residue A.299, 41 atoms), the PTP1B allosteric inhibitor.

**Residue closest to the allosteric ligand**
- **Glu276 (A.276), minimum heavy-atom distance = 2.55 Å** — the closest residue over all polymer residues (verified with a 6.0 Å contact cutoff as well as the 4.0 Å default). Runner-up: Phe280 at 2.65 Å, then Asn193 at 3.01 Å, Lys279 at 3.03 Å.

**Network**
- Built with `biomni.tool.[TOOL].[TOOL]` (Biotite 1.6.0 mmCIF parsing + NetworkX 3.6.1).
- **Contact cutoff used: 4.5 Å heavy-atom–heavy-atom** (fixed in the tool as `_CONTACT_CUTOFF_A = 4.5`).
- Graph: **282 residues, 1,379 edges**; Louvain communities, seed 42. Ligand/ions are excluded (amino-acid filter).
- Ligand-contact cutoff (separate, tool default): **4.0 Å**.

**Shortest path: allosteric-site Glu276 → catalytic Cys215**

| step | node | residue | min heavy-atom distance to next node |
|---|---|---|---|
| 1 | A.276 | Glu (allosteric site, 2.55 Å from FRJ) | 3.82 Å |
| 2 | A.188 | Pro | 3.16 Å |
| 3 | A.191 | Phe | 3.84 Å |
| 4 | A.110 | Leu | 4.41 Å |
| 5 | A.215 | **Cys215 (catalytic)** | — |

**Path string:** `A.276 → A.188 → A.191 → A.110 → A.215`
**Path length: 4 edges (5 residues)** — this is the minimum: no path of ≤3 edges exists (no direct Glu276–Cys215 edge; verified by exhaustive enumeration of simple paths).

**Alternative minimum-length (4-edge) routes** (5 exist in total): via A.192 (Leu) instead of A.188, and/or via A.194 (Phe) or A.221 (Arg) instead of A.110, e.g. `A.276 → A.192 → A.191 → A.221 → A.215`.

**Topology context:** Glu276 sits in Louvain community 8 (41 residues), Pro188/Phe191 in community 5 (35), and Leu110/Cys215 in community 7 (29) — i.e., the path crosses two community boundaries. Highest-betweenness nodes in the graph are A.257, A.254, A.98, A.214 and A.81.

**Caveat:** This is a geometric proximity network (residues in contact within 4.5 Å). It shows a plausible physical route connecting the allosteric ligand site to the catalytic cysteine, but it does not by itself establish that an allosteric signal is transmitted along this path; that would require energetic/dynamical analysis (e.g., normal modes, mutational validation).
=== END RUN rsg1vk3ffhc ===

=== RUN rt9q5yio4hv ===
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
## Results

| Variant | ClinVar classification | AlphaMissense score | 5EHR: minimum distance to SHP099 | 2SHP: minimum side-chain distance to PTP domain | Structural assignment |
|---|---|---:|---:|---:|---|
| **E76K** | **Conflicting classifications of pathogenicity**; predominantly **Pathogenic** by condition | **0.9998** | **14.714 Å** chain A; **14.827 Å** chain B | **2.797 Å** chain A; **2.819 Å** chain B | **Autoinhibitory N-SH2/PTP interface; not a direct allosteric-inhibitor contact** |
| **D61Y** | **Conflicting classifications of pathogenicity**; predominantly **Pathogenic** by condition | **0.9985** | **19.642 Å** chain A; **19.662 Å** chain B | **3.751 Å** chain A; **3.499 Å** chain B | **Autoinhibitory N-SH2/PTP interface; not a direct allosteric-inhibitor contact** |

### ClinVar details

- **E76K — VCV000013336**, `NM_002834.5:c.226G>A (p.Glu76Lys)`
  - Current aggregate germline classification: **Conflicting classifications of pathogenicity**.
  - **Pathogenic** for juvenile myelomonocytic leukemia, Noonan syndrome, PTPN11-related disorder, neoplasm, and pilocytic astrocytoma.
  - **Uncertain significance** for RASopathy and malignant neoplastic disease.
  - Additional somatic evidence includes an **Oncogenic** classification.

- **D61Y — VCV000228392**, `NM_002834.5:c.181G>T (p.Asp61Tyr)`
  - Current aggregate germline classification: **Conflicting classifications of pathogenicity**.
  - **Pathogenic** for juvenile myelomonocytic leukemia, Noonan syndrome 1, low-grade glioma, and unspecified condition.
  - **Uncertain significance** for RASopathy and embryonal rhabdomyosarcoma.
  - Additional clinical-impact evidence is **Tier I – Strong**.

Thus, neither variant should be described as having a single unqualified ClinVar germline classification, although the principal disease-specific assertions are pathogenic.

### Coordinate-based structural interpretation

**PDB 5EHR — allosteric inhibitor site**

- The structure contains SHP099, represented by ligand component **5OD**.
- Distances above are minimum heavy-atom distances from the deposited wild-type residue to the ligand.
- Neither residue approaches the conventional ≤5 Å direct-contact criterion:
  - E76: **14.714–14.827 Å**
  - D61: **19.642–19.662 Å**
- Even their nearest distances to protein atoms lining the SHP099 pocket are:
  - E76: **11.094–11.255 Å**
  - D61: **15.761–16.308 Å**

Therefore, **D61 and E76 are not direct residues of the 5EHR SHP099-binding interface**.

**PDB 2SHP — autoinhibitory interface**

The autoinhibitory interface was defined as cross-domain contacts between the **N-SH2 domain** and **PTP domain**, using a ≤5 Å heavy-atom cutoff:

- **E76**
  - OE2 directly contacts **Ser502 OG** at **2.797 Å** in chain A and **2.819 Å** in chain B.
- **D61**
  - Closest side-chain contacts are **3.751 Å** in chain A and **3.499 Å** in chain B.

Both residues therefore constitute members of the **autoinhibitory N-SH2/PTP interface**.

### Conclusion

Both substitutions map to the **autoinhibitory interface** rather than directly contacting the allosteric inhibitor site:

- **E76K:** autoinhibitory interface; AlphaMissense **0.9998**
- **D61Y:** autoinhibitory interface; AlphaMissense **0.9985**

Distances were calculated from the wild-type coordinates in the deposited structures; no mutation-specific side-chain modeling was performed.

### Sources

- UniProt SHP2, Q06124: https://rest.uniprot.org/uniprotkb/Q06124
- ClinVar E76K, VCV000013336: https://www.ncbi.nlm.nih.gov/clinvar/variation/13336/
- ClinVar D61Y, VCV000228392: https://www.ncbi.nlm.nih.gov/clinvar/variation/228392/
- AlphaMissense paper: https://doi.org/10.1126/science.adg7492
- AlphaMissense release documentation: https://storage.googleapis.com/dm_alphamissense/README.pdf
- Per-protein AlphaMissense scores derived from the official release: https://github.com/halbritter-lab/alpha-missense-scores
- RCSB PDB 5EHR: https://www.rcsb.org/structure/5EHR
- RCSB PDB 2SHP: https://www.rcsb.org/structure/2SHP

### Completed plan

1. [✓] Retrieve and verify ClinVar classifications for Q06124 E76K and D61Y
2. [✓] Retrieve and verify AlphaMissense pathogenicity scores for both substitutions
3. [✓] Download and parse PDB 5EHR and 2SHP coordinates; identify the inhibitor ligand and interdomain interface
4. [✗] Initial final-distance calculation attempt failed due to tuple-indexing errors in the reporting helper
5. [✓] Correct and independently validate the final two-chain distance table
6. [✓] Cross-check the structural interpretation and synthesize the results
=== END RUN rt9q5yio4hv ===

=== RUN r7lhpp1tnnk ===
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

**10 of the 14 residues predicted by STINGAllo are within 4.0 Å of the bound allosteric ligand.**

### 1. STINGAllo predictions for 1T4J chain A

Residue numbers returned by the STINGAllo REST API:

**129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282**

With deposited chain-A residue names:

**GLU129, GLU130, SER187, PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, ILE281, MET282**

### 2. Chain-A residues within 4.0 Å of the allosteric ligand

PDB 1T4J contains the allosteric ligand **FRJ at A/299**. Using the minimum heavy-atom distance between each protein residue and the 41 FRJ atoms:

| Residue | Minimum distance (Å) |
|---|---:|
| GLU276 | 2.554 |
| PHE280 | 2.645 |
| ASN193 | 3.011 |
| LYS279 | 3.031 |
| GLU200 | 3.304 |
| GLY277 | 3.367 |
| ALA189 | 3.416 |
| PHE196 | 3.552 |
| MET282 | 3.593 |
| LEU192 | 3.803 |
| PRO188 | 3.918 |

Thus, the contact list is:

**PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, GLY277, LYS279, PHE280, MET282**

### 3. Overlap

**PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, MET282**

Residue numbers:

**188, 189, 192, 193, 196, 200, 276, 279, 280, 282**

**Overlap count: 10**

For completeness:

- **STINGAllo only:** GLU129, GLU130, SER187, ILE281
- **Ligand-contact only:** GLY277
- **Important cutoff detail:** SER187 is close but outside the cutoff: its minimum distance is **4.048 Å**. Thus it is not included under an exact inclusive 4.0 Å criterion.

### Method and sources

- STINGAllo API: `https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A`
- API documentation: `https://www.stingallo.cbi.cnptia.embrapa.br/apis`
- Deposited structure: [RCSB PDB 1T4J](https://www.rcsb.org/structure/1T4J)
- Coordinates: `https://files.rcsb.org/download/1T4J.pdb`
- Primary structural citation: Wiesmann et al., *Nature Structural & Molecular Biology* (2004), DOI [10.1038/nsmb803](https://doi.org/10.1038/nsmb803), PMID 15258570.

The calculation used all heavy atoms, an inclusive **≤4.000 Å** cutoff, excluded waters and the ligand itself, and found no alternate-location ambiguity in the PDB file.

### Completed plan

1. [✗] Specialized literature search (failed: Claude-model restriction)
2. [✓] Locate and retrieve the authoritative STINGAllo output
3. [✓] Retrieve 1T4J and identify FRJ (A/299) as the bound allosteric ligand
4. [✓] Normalize residue identifiers and calculate the 4 Å contact list
5. [✓] Independently verify distances, overlap, and source metadata
6. [✓] Report both lists, the overlap, count, methods, and source identifiers
=== END RUN r7lhpp1tnnk ===

=== RUN rdhz24nqf7b ===
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
## 1. Identification of the two inhibitor copies

**Ligand: `CBT` — N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine** (non‑β‑lactam "core‑disrupting" allosteric inhibitor)

| | |
|---|---|
| PDB chem‑comp code | `CBT` (HETNAM: *N,N-BIS(4-CHLOROBENZYL)-1H-1,2,3,4-TETRAAZOL-5-AMINE*) |
| Formula / atoms | C15H13Cl2N5; 22 heavy atoms per copy, occupancy 1.00, no altlocs |
| Copy 1 | chain **A**, HETATM residue **300** |
| Copy 2 | chain **A**, HETATM residue **301** |
| Protein | one monomer of TEM‑1 β‑lactamase (chain A, auth residues 26–290; biological unit = monomeric) |
| Entry title | "TEM‑1 Beta‑Lactamase in Complex with a Novel, Core‑Disrupting, Allosteric Inhibitor" |
| Primary reference | Horn JR, Shoichet BK, *J Mol Biol* 2004;336:1283‑91 (PMID 15037085; DOI 10.1016/j.jmb.2003.12.068) |

Both copies are bound to the **same protein molecule** (not symmetry‑related copies of the enzyme). The sister structure **1PZP** (related entry) is the same protein with the companion inhibitor `FTA`.

## 2. Protein residues within 4.0 Å of each copy

Heavy‑atom contacts, computed from the deposited coordinates (independent numpy and scipy KD‑tree implementations gave identical lists). PDB author numbering (TEM‑1/Ambler convention) with UniProt P62593 equivalents in parentheses.

**Copy 1 — CBT A/300 (11 residues; inner, active‑site‑proximal end of the cleft)**

| PDB residue | UniProt P62593 | min dist (Å) | contacting atom |
|---|---|---|---|
| SER 235 | Ser 233 | 2.60 | OG |
| GLY 245 | Gly 242 | 3.18 | O |
| ARG 244 | Arg 241 | 3.36 | CD |
| ILE 246 | Ile 243 | 3.39 | CG2 |
| LEU 220 | Leu 218 | 3.53 | CD1 |
| ASN 276 | Asn 272 | 3.54 | ND2 |
| ALA 237 | Ala 235 | 3.56 | CB |
| ILE 279 | Ile 275 | 3.57 | CD1 |
| GLY 236 | Gly 234 | 3.69 | CA |
| VAL 216 | Val 214 | 3.76 | CG1 |
| ALA 217 | Ala 215 | 3.91 | CB |

**Copy 2 — CBT A/301 (11 residues; outer, distal end of the cleft)**

| PDB residue | UniProt P62593 | min dist (Å) | contacting atom |
|---|---|---|---|
| ASN 276 | Asn 272 | 3.07 | OD1 |
| LEU 221 | Leu 219 | 3.35 | CD2 |
| LEU 220 | Leu 218 | 3.35 | CB |
| ARG 244 | Arg 241 | 3.40 | NH2 |
| ALA 224 | Ala 222 | 3.41 | CB |
| ALA 280 | Ala 276 | 3.42 | CB |
| ILE 279 | Ile 275 | 3.56 | CB |
| GLY 283 | Gly 279 | 3.67 | CA |
| ILE 263 | Ile 259 | 3.79 | CD1 |
| LEU 286 | Leu 282 | 3.94 | CD2 |
| VAL 261 | Val 257 | 4.00 | CG1 |

*Numbering note:* the PDB uses TEM‑1 "Ambler" numbering (catalytic Ser 70/Lys 73/Ser 130/Glu 166), whereas UniProt P62593 numbers the precursor (signal peptide 1–23), giving Ser 68/Lys 71/Ser 128/Glu 164 (matching UniProt's annotated ACT_SITE residues). The offset is −2 (auth ≤238), −3 (240–252), −4 (≥254) because PDB auth 239 and 253 are unmodeled; the mapping was derived from the mmCIF `label_seq_id`/SIFTS alignment and is 100% identity to UniProt 24–286 apart from the single TEM‑1/TEM‑1B difference (model Thr 182 ↔ UniProt Met 180).

## 3. Do the two copies occupy the same pocket?

**No — they occupy two distinct, directly adjacent binding sites (sub‑pockets) that together fill one continuous elongated cavity.** They are *not* two copies in an identical site.

Evidence:

1. **Different contact sets.** Only **4 residues are shared** (LEU 220, ARG 244, ASN 276, ILE 279); each copy has **7 unique** contacts. Copy 300 grips the Ω‑loop/strand side (SER 235, GLY 236, ALA 237; RGT strand ARG 244–GLY 245–ILE 246) plus the start of α11 (VAL 216, ALA 217, LEU 220); copy 301 shifts outward to the end of α11 (LEU 221, ALA 224), the ARG 259–THR 266 strand (VAL 261, ILE 263) and α12 (ALA 280, GLY 283, LEU 286).
2. **The deposited SITE records define two separate sites**: `SITE_IDENTIFIER AC1` = "BINDING SITE FOR RESIDUE CBT A 300" and `AC2` = "BINDING SITE FOR RESIDUE CBT A 301", with different residue lists — and each site explicitly lists the *other* inhibitor molecule among its components (AC1 contains CBT A 301; AC2 contains CBT A 300), i.e. the two ligands sit side by side within one shared, contiguous groove.
3. **Geometry.** Centroid‑to‑centroid separation = **8.59 Å**, yet the closest heavy‑atom contact between the two inhibitor molecules is **3.68 Å** — they are in direct van der Waals contact, like two ligands packed side by side in one cavity, not superimposed in one site.
4. **Different relation to the active site.** Copy 300 (centroid) lies 9.7 Å from Ser 70 CB and 4.3 Å from Arg 244 CB; copy 301 lies 16.7 Å from Ser 70 CB and 8.4 Å from Arg 244 CB — consistent with the paper's statement that this cryptic site lies ~16 Å from the active‑site centre.

**Biological interpretation (Horn & Shoichet, PMID 15037085):** this is the classic *core‑disruption* mechanism. The inhibitor binds a cryptic site that it creates by prying apart helices **α11 (residues 217–225)** and **α12 (271–289)**, exposing the hydrophobic core; the two CBT molecules occupy the two halves of that elongated, newly opened pocket (one inner/Ω‑loop‑proximal, one outer/distal), and the conformational change is transmitted to the catalytic Ω‑loop residue **Arg 244**, which both copies contact and which adopts catalytically incompetent conformations in the complex. So: **one shared, contiguous cryptic cavity between α11 and α12, occupied by two distinguishable (adjacent, partially overlapping) binding sites rather than a single identical pocket.**

### Methods / reproducibility
- Coordinates: RCSB `1PZO.pdb` and `1PZO.cif` (X‑ray, 1.90 Å, R = 0.193 / Rfree = 0.247; deposited 2003, Horn & Shoichet).
- 4 Å contacts: all ligand heavy atoms vs. all protein heavy atoms; result reproduced independently with numpy broadcasting and `scipy.spatial.cKDTree`; waters and the other CBT copy excluded.
- Pocket comparison: author SITE records, ligand centroids, inter‑ligand distances, HELIX/SHEET element assignment.
- Numbering: mmCIF `label_seq_id` → UniProt via RCSB SIFTS (`entity 1 ↔ UniProt 24`, len 263), cross‑validated against UniProt ACT_SITE annotations.
=== END RUN rdhz24nqf7b ===

=== RUN rhkoje5bowh ===
QUESTION:
Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P02_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[P02_b] [critical] [scripted] [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}]
[P02_c] [critical] [judged] the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported
[P02_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P02_e] [critical] [judged] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 1, "overlap_of_the_covering_pocket": 16, "top3_ranks": [1, 2, 3], "top3_overlap": [16, 0, 0], "pockets": [{"rank": 1, "score": 0.146, "n_residues": 33, "site_residues_in_pocket": 16}, {"rank": 2, "score": -0.007, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 3, "score": -0.021, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 4, "score": -0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": -0.053, "n_residues": 5, "site_residues_in_pocket": 4}, {"rank": 6, "score": -0.059, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 7, "score": -0.07, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 8, "score": -0.089, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 9, "score": -0.09, "n_residues": 7, "site_residues_in_pocket": 3}, {"rank": 10, "score": -0.098, "n_residues": 4, "site_residues_in_pocket": 3}, {"rank": 11, "score": -0.168, "n_residues": 7, "site_residues_in_pocket": 1}]}
[P02_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2], "top3_overlap": [0, 0], "pockets": [{"rank": 1, "score": 12.62, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 5.97, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P02_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result: **Rank 1**

The pocket containing the former position of the covalent AMG 510/sotorasib inhibitor—the KRAS G12C switch-II pocket—is the **first-ranked AutoSite pocket**.

### Validation

- Original inhibitor centroid: `(1.872, −8.260, −1.361) Å`
- Rank-1 cluster centroid: `(5.268, −9.551, −3.023) Å`
- Distance between centroids: **3.996 Å**
- **36/41** inhibitor heavy atoms were within 1 Å of rank-1 cluster points.
- **40/41** were within 2 Å of rank-1 cluster points.
- Rank 2 had only 5/41 atoms within 1 Å; ranks 3–5 had none.
- The inhibitor was covalently connected to **CYS12** and contacted canonical switch-II-pocket residues including **TYR96, GLN99, HIS95, and ASP69**.

Thus, the former covalent-inhibitor site corresponds to **AutoSite pocket rank 1**.
=== END RUN rhkoje5bowh ===

=== RUN rzffxzac6j7 ===
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

| Chemical component | Identity | PDB chain/residue | Structural site |
|---|---|---|---|
| **AY7** | **Asciminib** | Chain A, residue 602 | Peripheral/myristoyl-binding pocket |
| **NIL** | **Nilotinib** | Chain A, residue 601 | ATP-binding pocket |

These identities come from the 5MO4 mmCIF chemical-component records; BioLiP independently confirms both ligands in chain A.

## Polymer residues within 4 Å

Distances are minimum heavy-atom distances. Each entry is shown as **PDB author residue → UniProt P00519 residue (distance)**.

### AY7 — asciminib: 18 residues

- ARG351→ARG332 (3.79 Å); ALA356→ALA337 (3.68 Å); LEU359→LEU340 (3.22 Å); LEU360→LEU341 (3.38 Å); ALA363→ALA344 (3.57 Å)
- LEU448→LEU429 (3.27 Å); ILE451→ILE432 (3.61 Å); ALA452→ALA433 (3.52 Å); THR453→THR434 (3.47 Å); TYR454→TYR435 (3.87 Å)
- GLU481→GLU462 (2.82 Å); CYS483→CYS464 (3.84 Å); PRO484→PRO465 (3.73 Å); VAL487→VAL468 (3.68 Å); PHE512→PHE493 (3.63 Å)
- ILE521→ILE502 (3.62 Å); VAL525→VAL506 (3.68 Å); LEU529→LEU510 (3.76 Å)

### NIL — nilotinib: 25 residues

- LEU267→LEU248 (3.71 Å); TYR272→TYR253 (3.55 Å); VAL275→VAL256 (3.81 Å); ALA288→ALA269 (3.29 Å); VAL289→VAL270 (3.98 Å)
- LYS290→LYS271 (3.39 Å); LYS304→LYS285 (3.83 Å); GLU305→GLU286 (2.95 Å); VAL308→VAL289 (3.63 Å); MET309→MET290 (3.47 Å)
- ILE312→ILE293 (3.64 Å); LEU317→LEU298 (3.55 Å); VAL318→VAL299 (3.57 Å); ILE332→ILE313 (3.49 Å); ILE334→ILE315 (3.25 Å)
- PHE336→PHE317 (3.45 Å); MET337→MET318 (2.84 Å); GLY340→GLY321 (3.86 Å); PHE378→PHE359 (3.63 Å); HIS380→HIS361 (3.38 Å)
- LEU389→LEU370 (3.70 Å); VAL398→VAL379 (3.75 Å); ALA399→ALA380 (3.20 Å); ASP400→ASP381 (3.01 Å); PHE401→PHE382 (3.34 Å)

## Do they occupy distinct sites?

**Yes.** Their 4 Å protein-contact sets are completely disjoint: 43 different contacting residues and **zero shared residues**.

- Nilotinib contacts the ATP-site region, including the gatekeeper **Thr315**, hinge **Met318**, and catalytic-loop **Asp381**.
- Asciminib contacts the peripheral ABL1 pocket associated with the myristoyl-binding region, including residues around **Arg332**, **Leu340/Leu341**, **Ala344**, and **Leu429–Leu510**.

From the same coordinates, the minimum heavy-atom distance between the two ligands is approximately **19.66 Å**; their centroid separation is approximately **27.78 Å**. Thus, they bind simultaneously in spatially separate pockets and do not directly contact one another in this structure.

## Relationship between PDB and P00519 numbering

For chain A, RCSB/SIFTS gives the following relationships:

- The mmCIF entity `label_seq_id` range **7–495** aligns to P00519 residues **27–515**, so:
  **P00519 number = mmCIF label_seq_id + 20**
- In this deposited structure:
  **PDB author_seq_id = label_seq_id + 39**
- Therefore, for every resolved chain-A residue:
  **P00519 number = PDB author residue number − 19**

Examples:

- PDB **Met337** = P00519 **Met318**
- PDB **Thr315-equivalent ILE334** = P00519 **Ile315**
- PDB **Asp400** = P00519 **Asp381**

The resolved coordinates span PDB author numbers **83–531**, mmCIF label numbers **44–492**, and P00519 numbers **64–512**. The +19 offset is specific to the numbering used in 5MO4 and should not be assumed for other ABL1 structures. Accordingly, ABL1 residues conventionally described in the literature by UniProt numbering—such as the **Thr315 gatekeeper** and **Met318 hinge**—appear as **PDB Thr-equivalent ILE334** and **PDB MET337**, respectively, in this entry.

The 4 Å results describe geometric proximity only; they do not by themselves distinguish hydrogen bonds, van der Waals contacts, or their energetic importance.

**Sources:** RCSB 5MO4 mmCIF and SIFTS mapping, BioLiP ligand records, and heavy-atom contact calculations from the deposited 5MO4 coordinates.
=== END RUN rzffxzac6j7 ===

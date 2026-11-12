# Judge batch 001 of 1

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

=== RUN rml902um86d ===
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
## Result in brief

Only **fpocket** recognizes a coherent pocket overlapping the FRJ allosteric-ligand site: its pocket **#11** contains **8 of 11** contacting residues and has a high druggability score of **0.820**. It is nevertheless outside fpocket’s top three.

**P2Rank does not assign any FRJ-contacting residue to one of its three predicted pockets.** **PocketMiner gives mixed, generally modest support**, although F196 and L192 stand out locally.

## Input and contact definition

- Structure: **PDB 1T4J**, human PTP1B chain A, UniProt **P18031**
- Bound allosteric inhibitor: **FRJ**
- All `HETATM` records were removed, leaving **2,304 protein atoms and 282 resolved residues**
- A contact was defined as a protein heavy atom within **4.0 Å** of an FRJ heavy atom

The resulting 11-contact set was:

**P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, M282.**

PDB and UniProt numbering coincide over this aligned segment. The deposited `SITE` annotation is a nine-residue subset of this 4 Å set.

## Residue-level comparison

Notation:

- fpocket: **#** = pocket rank among 18, **S** = native pocket score, **D** = druggability score
- P2Rank: **S** = native residue score, **p** = residue probability, **#** = global rank derived by sorting the 282 residue probabilities; **pocket 0** means unassigned
- PocketMiner: **p** = native per-residue pocket probability; **#** = global rank derived by sorting all 282 residue scores
- For both global rankings, **1 is highest propensity**

| FRJ contact | fpocket assignment | P2Rank residue output | PocketMiner output |
|---|---|---|---|
| **P188** | #11 (S 0.069, D 0.820) | S 0.0775; p 0.0017 (#184); pocket 0 | p 0.3163 (#212) |
| **A189** | #7 (S 0.123, D 0.005); #11 (S 0.069, D 0.820) | S 0.4189; p 0.0257 (#61); pocket 0 | p 0.3807 (#181) |
| **L192** | #11 (S 0.069, D 0.820) | S 1.1997; p 0.1962 (#14); pocket 0 | p 0.5389 (#105) |
| **N193** | #7 (S 0.123, D 0.005); #11 (S 0.069, D 0.820) | S 0.7399; p 0.0780 (#28); pocket 0 | p 0.4528 (#143) |
| **F196** | #11 (S 0.069, D 0.820) | S 1.4705; p 0.2742 (#10); pocket 0 | p 0.6709 (#54) |
| **E200** | #16 (S 0.028, D 0.001) | S 0.0875; p 0.0019 (#179); pocket 0 | p 0.3237 (#208) |
| **E276** | #11 (S 0.069, D 0.820) | S 0.6951; p 0.0687 (#34); pocket 0 | p 0.4166 (#169) |
| **G277** | #11 (S 0.069, D 0.820) | S 1.0179; p 0.1458 (#16); pocket 0 | p 0.4261 (#162) |
| **K279** | #8 (S 0.123, D 0.069) | S 0.4183; p 0.0256 (#62); pocket 0 | p 0.3357 (#203) |
| **F280** | #11 (S 0.069, D 0.820) | S 1.8274; p 0.3707 (#6); pocket 0 | p 0.3624 (#193) |
| **M282** | #8 (S 0.123, D 0.069) | S 0.4636; p 0.0311 (#52); pocket 0 | p 0.3265 (#207) |

### Pocket-level summary

- **fpocket**
  - Pocket **#11** contains **8/11** contacts: P188, A189, L192, N193, F196, E276, G277 and F280.
  - A189/N193 are also in #7; K279/M282 in #8; E200 in #16.
  - Thus fpocket covers all 11 contacts across four pockets, with one coherent pocket capturing 8/11.
  - Its top three pockets do **not** overlap the FRJ site; the overlapping pocket is ranked #11.

- **P2Rank**
  - Predicted only three pockets, with pocket scores/probabilities of **7.22/0.376**, **2.03/0.044**, and **1.87/0.037**.
  - **None of the 11 contacts belongs to any reported pocket**.
  - Its rank-1 pocket is the catalytic PTP1B pocket, containing D181, C215, S216, A217, R221 and Q262.
  - Some individual residues have appreciable P2Rank propensities—F280 #6, F196 #10, L192 #14 and G277 #16—but they were not clustered into an FRJ-site pocket.

- **PocketMiner**
  - Contact-residue scores ranged from **0.3163 to 0.6709**.
  - Their mean was **0.4137**, below the protein-wide mean of **0.4680**.
  - Only **F196
=== END RUN rml902um86d ===

=== RUN reykh0cmz73 ===
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
## Result

**Bottom line:** On the same protein-only 1T4J coordinates, **fpocket is the only method that forms a coherent pocket at the FRJ allosteric site**. P2Rank gives several FRJ-contacting residues high ligandability scores but does not assign them to a pocket, while original PocketMiner does not rank any FRJ-contacting residue among its top 20.

### Exact setup

- Structure: **PDB 1T4J**, human PTP1B, chain A, UniProt **P18031**.
- Allosteric ligand: **FRJ**, deposited as an allosteric inhibitor of PTP1B.
- Prediction input: the deposited chain with **all HETATM records removed**, including FRJ and waters; 2,304 protein atoms.
- Contacts: any FRJ heavy atom within **4.0 Å** of a protein heavy atom.
- The 282 observed residues map to P18031 with **zero numbering offset**.
- fpocket 4.0 and P2Rank 2.5.1 were run on that same input. PocketMiner used the canonical original 2023 checkpoint from `Mickdub/gvp` (`pocket_pred`), whose data-shard SHA-256 is `6f5ab62b9fb38b54040053ac321f3362d616bae9b31569249a032dbb50890b70`.

fpocket has no residue-level probability; therefore its entry below is the native **pocket rank** to which the residue was assigned. P2Rank and PocketMiner ranks are ranks among all 282 scored residues, with 1 = highest. P2Rank `pocket 0` means that residue was not assigned to a predicted pocket.

## Residue-level comparison

| P18031 residue | Minimum FRJ distance, Å | fpocket pocket rank(s) | P2Rank raw score; probability (residue rank; pocket) | PocketMiner score (residue rank) |
|---|---:|---:|---:|---:|
| P188 | 3.918 | 11 | 0.0775; 0.0017 (#184; 0) | 0.316 (#212) |
| A189 | 3.416 | 11, also 7 | 0.4189; 0.0257 (#61; 0) | 0.381 (#181) |
| L192 | 3.803 | 11 | 1.1997; 0.1962 (#14; 0) | 0.539 (#105) |
| N193 | 3.011 | 11, also 7 | 0.7399; 0.0780 (#28; 0) | 0.453 (#143) |
| F196 | 3.552 | 11 | 1.4705; 0.2742 (#10; 0) | 0.671 (#54) |
| E200 | 3.304 | 16 | 0.0875; 0.0019 (#178; 0) | 0.324 (#208) |
| E276 | 2.554 | 11 | 0.6951; 0.0687 (#34; 0) | 0.417 (#169) |
| G277 | 3.367 | 11 | 1.0179; 0.1458 (#16; 0) | 0.426 (#162) |
| K279 | 3.031 | 8 | 0.4183; 0.0256 (#62; 0) | 0.336 (#203) |
| F280 | 2.645 | 11 | 1.8274; 0.3707 (#6; 0) | 0.362 (#193) |
| M282 | 3.593 | 8 | 0.4636; 0.0311 (#52; 0) | 0.327 (#207) |

Using a more permissive 4.5 Å cutoff adds three borderline residues:

- **S187:** fpocket 11/7; P2Rank 0.0961; probability 0.0022, rank 172, pocket 0; PocketMiner 0.396, rank 172.
- **K197:** fpocket 16; P2Rank 0.7054; probability 0.0707, rank 33, pocket 0; PocketMiner 0.354, rank 197.
- **I281:** fpocket 11/8; P2Rank 1.4604; probability 0.2714, rank 11, pocket 0; PocketMiner 0.438, rank 154.

## Method-level findings

### fpocket

- Detected 18 cavities.
- The coherent FRJ-site cavity is **pocket 11**, containing 8 of the 11 primary contacts and 10 of the 14 contacts at 4.5 Å.
- It is only **11th by fpocket’s native pocket score**:
  - native pocket score: **0.069**
  - druggability score: **0.8205**, by far the highest among the 18 cavities.
- Thus fpocket sees a geometrically recognizable, highly druggable cavity, but it is not a top-ranked cavity under fpocket’s default ranking.
- The other FRJ contacts are split among pockets 7, 8, and 16.

### P2Rank

- Predicted three pockets:
  1. score **7.22**, probability **0.376** — the catalytic pocket, including C215/C216/C217;
  2. score **2.03**, probability **0.044**;
  3. score **1.87**, probability **0.037**.
- **None of the 11 primary FRJ-contacting residues was assigned to any P2Rank pocket.**
- Nevertheless, four individual FRJ contacts are high-scoring residues overall: F280 (#6), F196 (#10), L192 (#14), and G277 (#16). These are residue-level ligandability predictions, not a P2Rank allosteric-pocket call.

### Original PocketMiner

- Produced finite 0–1 scores for all 282 residues.
- The best-ranked FRJ contact was **F196: 0.671, rank 54**.
- **No FRJ-contacting residue was in PocketMiner’s top 20**, even at the 4.5 Å cutoff.
- PocketMiner instead scores the catalytic region strongly, including S216 (#3), A217 (#10), C215 (#17), W179 (#18), and R221 (#19).

## Which methods agree?

### At the FRJ allosteric site

- **fpocket agrees with the crystallographic site** by producing a coherent pocket containing most FRJ contacts, although that pocket is only #11 by native score.
- **P2Rank does not agree at the pocket level**: it assigns none of the FRJ contacts to a pocket. It shows only partial residue-level agreement with fpocket on F280, F196, L192, and G277.
- **PocketMiner does not strongly agree**: it gives no FRJ contact a top-20 score and instead emphasizes the catalytic region.

### At the catalytic site

- **fpocket pocket 2 and P2Rank pocket 1 overlap strongly**, sharing 10 catalytic-site residues.
- Eight of PocketMiner’s top 20 residues lie in the union of those two catalytic-pocket residue sets. Thus P2Rank and PocketMiner also agree that the catalytic region is a major predicted binding site.

## What these results can—and cannot—say about allostery

- **fpocket** can identify geometric cavities and rank them using shape, exposure, and heuristic druggability descriptors. It cannot determine whether a cavity is orthosteric, allosteric, cryptic, or coupled to enzyme activity.
- **P2Rank** can identify residues and surfaces that resemble ligand-binding sites under its learned model. It cannot classify a site as allosteric or demonstrate communication with the catalytic site.
- **Original PocketMiner** predicts residue-level propensity for pockets to open, particularly cryptic pockets. It does **not** predict allosteric coupling. The newer **AE-PocketMiner** is a distinct model that also attempts to predict allosteric coupling; it was not the model used here.
- Consequently, a high pocket score or residue score is a **testable pocketability hypothesis**, not proof of allostery. Even an AE-PocketMiner allostery score would be a prediction, not experimental evidence of causality.
- The FRJ site’s allosteric character comes from the **crystallographic and biochemical experiment**: FRJ binds a site roughly 20 Å from the catalytic site and inhibits PTP1B through an allosteric mechanism. None of these three algorithms independently establishes that fact.
- Removing FRJ computationally from a **holo crystal** is not equivalent to an experimentally solved apo structure: ligand-induced conformational selection can remain in the coordinates. This is particularly important when interpreting cryptic-pocket-opening methods.

Thus, the disagreement concerns whether these algorithms recognize the site as a ligandable or cryptic pocket from these coordinates; it does **not** overturn the experimentally established allosteric nature of FRJ.

### Sources

- RCSB PDB 1T4J: https://www.rcsb.org/structure/1T4J
- UniProt P18031: https://www.uniprot.org/uniprotkb/P18031/entry
- Wiesmann et al., “Allosteric inhibition of protein tyrosine phosphatase 1B,” *Nature* (2004), PMID 15258570, DOI: https://doi.org/10.1038/nature02970
- Le Guilloux and Hill, fpocket, *BMC Bioinformatics* (2009), DOI: https://doi.org/10.1186/1471-2105-10-168
- Krivák et al., P2Rank, *Bioinformatics* (2019), DOI: https://doi.org/10.1093/bioinformatics/btz298
- Meller et al., original PocketMiner, *Nature Communications* (2023), PMID 36859488, DOI: https://doi.org/10.1038/s41467-023-36699-3
- Canonical original PocketMiner source/checkpoint: https://github.com/Mickdub/gvp/tree/pocket_pred

### Completed plan

1. [✓] Inspect the environment and determine which predictors are available locally.
2. [✓] Verify 1T4J metadata, FRJ identity, UniProt mapping, and the ligand-contact residue set.
3. [✓] Run fpocket and P2Rank, and recover/run the canonical original PocketMiner checkpoint.
4. [✓] Convert all outputs into comparable residue rankings/scores for the FRJ-contacting residues.
5. [✓] Complete reproducibility checks and method-semantics validation.
6. [✓] Deliver the sourced comparison and allostery limitations.
=== END RUN reykh0cmz73 ===

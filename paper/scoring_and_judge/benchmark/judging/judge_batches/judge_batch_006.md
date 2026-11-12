# Judge batch 006 of 24

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

=== RUN r8mcq7r7mvh ===
QUESTION:
For AKT1 (UniProt P31749), report ClinVar classification and AlphaMissense score for E17K, give the domain containing residue 17, and report its distance from the allosteric inhibitor in PDB entry 3O96 if the residue is modeled there.

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V02_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[V02_b] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "29022"}
[V02_c] [critical] [scripted] 0.9977
[V02_d] [critical] [judged] the PH domain is named and the distance from residue 17 to the 3O96 inhibitor is reported (residue 17 IS modelled: UniProt 17 = label_seq_id 20, the PDB author number differs)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## AKT1 E17K summary

| Item | Result |
|---|---|
| **Variant** | AKT1 E17K, p.Glu17Lys, c.49G>A; ClinVar Variation ID **13983**; dbSNP **rs121434592** |
| **ClinVar classification** | **Pathogenic** — germline classification; *criteria provided, multiple submitters, no conflicts*. ClinVar separately lists it as **Oncogenic** for neoplasms. |
| **AlphaMissense** | **0.9977**, classified **pathogenic** |
| **Domain containing residue 17** | **PH domain** (pleckstrin homology domain); UniProt P31749 annotation spans residues **5–108**, so residue 17 is within the PH domain |
| **PDB 3O96** | Glu17 **is modeled** in chain A and maps unambiguously to UniProt residue 17 |
| **Allosteric inhibitor** | PDB ligand component **IQO** |
| **Distance to inhibitor** | **5.704 Å** minimum heavy-atom distance, between **Glu17 CG** and **IQO C6** |

### Distance definition

The primary distance is the minimum Euclidean separation between any heavy atom of deposited Glu17 and any heavy atom of IQO in the deposited 3O96 coordinates. Additional reference measurements are:

- Glu17 all-atom centroid to IQO all-atom centroid: **15.627 Å**
- Glu17 CB to nearest IQO heavy atom: **6.522 Å**

This is the distance for the **wild-type Glu17 side chain** in 3O96; the entry does not contain an E17K mutant model. Although the 5.704 Å minimum is geometrically close, residue 17 is not included in the deposited REMARK 800 IQO binding-site residue list.

### Sources

- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry)
- [ClinVar Variation 13983](https://www.ncbi.nlm.nih.gov/clinvar/variation/13983/)
- [AlphaMissense P31749 substitution record](https://raw.githubusercontent.com/halbritter-lab/alpha-missense-scores/main/scores/json/P31749.AlphaMissense_aa_substitutions.json), derived from DeepMind’s official `AlphaMissense_aa_substitutions.tsv.gz` dataset
- Tavtigian et al., *Nature Genetics* (2023), [doi:10.1038/s41588-023-01461-0](https://doi.org/10.1038/s41588-023-01461-0)
- [RCSB PDB 3O96](https://www.rcsb.org/structure/3O96)

### Final plan status

1. [✗] Initial combined retrieval failed because `advanced_web_search_claude` required a different model configuration; replaced with direct UniProt, ClinVar, RCSB, and AlphaMissense data queries.
2. [✓] Verified ClinVar and AlphaMissense records.
3. [✓] Mapped residue 17 to the AKT1 PH domain and confirmed residue identity.
4. [✓] Confirmed Glu17 modeling, identified IQO, and calculated structural distances.
5. [✗] Initial final-audit write failed because of a NumPy `int64` JSON serialization error.
6. [✓] Re-ran the audit with native Python scalars and completed the reconciliation.
=== END RUN r8mcq7r7mvh ===

=== RUN rfsax8z9qil ===
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
### Completed plan
1. [✗] Generic literature-search retrieval failed because the search backend returned empty results and the advanced agent required an unavailable Claude model.
2. [✗] The first alignment pass mishandled the installed Bio.Align coordinate representation.
3. [✓] Mapped human ABL1 P00519 T315 to the corresponding residue in PDB 1OPK.
4. [✓] Retrieved the exact AlphaMissense score from the official DeepMind release.
5. [✓] Calculated and independently verified the ligand distances from both PDB and mmCIF coordinates.
6. [✓] Completed provenance checks and structural interpretation.

## Results

| Feature | Result |
|---|---|
| Variant | **ABL1 p.Thr315Ile (T315I)**; dbSNP **rs121913459**; GRCh38 **9:130872896 C>T** |
| ClinVar | **Likely pathogenic; association** |
| ClinVar review status | **Criteria provided, multiple submitters, no conflicts**; last evaluated 2023-09-13 |
| AlphaMissense | **0.9991** (`am_pathogenicity`) |
| AlphaMissense class | **Pathogenic** |

### Distances in PDB 1OPK

PDB 1OPK is a mouse ABL1 structure. Human P00519 Thr315 aligns exactly to mouse ABL1 Thr315, represented as **chain A, author residue 334, label sequence index 295**.

Because “distance to a ligand” is convention-dependent, the primary values below are the **minimum heavy-atom separation**; Cα-to-ligand-centroid distances are included for clarity.

| Binding site | Ligand in 1OPK | Minimum heavy-atom distance from T315 | T315 Cα to ligand centroid | Closest atom pair |
|---|---|---:|---:|---|
| ATP-site ligand | **P16** | **3.24 Å** | **7.86 Å** | T315 OG1–P16 C16 |
| Myristoyl-site ligand | **MYR** (myristic acid) | **25.59 Å** | **32.82 Å** | T315 OG1–MYR C14 |

For reference, the T315 Cα-to-nearest-ligand-atom distances are **5.46 Å for P16** and **27.28 Å for MYR**. The PDB and mmCIF calculations agreed to within \(2\times10^{-6}\) Å.

## Interpretation

T315 is in direct contact range with the **ATP-site ligand P16**: the Thr315 hydroxyl is only 3.24 Å from the ligand. By contrast, T315 is nearly eight times farther from the myristoyl-site ligand in minimum-atom terms and is far too distant for direct contact.

Thus, the distances strongly implicate the **ATP-binding/ATP-competitive inhibitor site**, not the myristoyl site. This is consistent with T315 being the ABL1 “gatekeeper” residue: the T315I substitution removes the hydroxyl group and adds bulk near the ATP pocket, impairing ATP-competitive inhibitor binding. The structural distance establishes site proximity; the functional resistance effect additionally requires biochemical or clinical evidence.

### Sources
- [ClinVar VCV000012624](https://www.ncbi.nlm.nih.gov/clinvar/variation/12624/)
- [Official AlphaMissense UniProt substitution release](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz)
- [AlphaMissense file documentation](https://storage.googleapis.com/dm_alphamissense/README.pdf)
- [PDB 1OPK](https://www.rcsb.org/structure/1OPK)
- [UniProt P00519](https://www.uniprot.org/uniprotkb/P00519/entry)
=== END RUN rfsax8z9qil ===

=== RUN rrqartfkqjq ===
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
## Ligands in PDB 1OPK

- **Myristoyl allosteric site:** **MYR** — myristic acid (tetradecanoic acid), chain A, residue 1.
- **ATP site:** **P16** — also called **PD166326 / PD-166326**, a pyridopyrimidinone ABL kinase inhibitor, chain A, residue 2.
- **GOL** is glycerol and is not one of the two requested site ligands.

## Residues within 4 Å of MYR

| PDB residue | Minimum heavy-atom distance | Human ABL1 P00519 position* |
|---|---:|---:|
| A:LEU359 | 3.84 Å | L340 |
| A:LEU360 | 3.69 Å | L341 |
| A:ALA363 | 3.71 Å | A344 |
| A:LEU448 | 3.73 Å | L429 |
| A:ALA452 | 3.85 Å | A433 |
| A:GLU481 | 3.47 Å | E462 |
| A:ILE521 | 3.87 Å | I502 |
| A:LEU529 | 3.54 Å | L510 |

Thus, in **human UniProt P00519 numbering**, the MYR-contacting residues are:

**L340, L341, A344, L429, A433, E462, I502, and L510.**

\* **Entry-annotation correction:** Although the question describes 1OPK as human ABL1/P00519, the deposited PDB entry is annotated as **mouse ABL1, UniProt P00520**. Its PDB residue numbers are 19 higher than the aligned UniProt positions in this region. Sequence alignment shows that the eight listed human P00519 positions map directly and unambiguously.

**Source:** RCSB coordinates for PDB **1OPK**; primary citation Nagar et al., *Cell* (2003), DOI **10.1016/S0092-8674(03)00194-6**, PMID **12654251**.
=== END RUN rrqartfkqjq ===

=== RUN rpm8roj7m3a ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

- **Activator:** **MRK** in PDB **1V4S**, chemically named *2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide*. It occupies the allosteric pocket rather than the glucose-binding site.
- **Residue mapping:** For the modeled mature chain of 1V4S, PDB author numbering is **1:1 with canonical P35557 numbering** at every contact site.
- **ClinVar retrieval:** 2,845 assembly-specific records, deduplicated to 1,425 accessions. There are **59 unique protein alleles** at the 6 Å contact positions, including **38 missense** and **21 non-missense** alleles.
- **6 Å contact positions:** 61–66, 98, 159, 210–211, 214–215, 218, 220–222, 235, 250, 252, 451–453, and 455–456.
- The **core MRK site** identified independently by the structure workflow comprises 61–66, 210–211, 214–215, 220, 235, 452, and 455. Fpocket overlaps all 14 core residues; P2Rank overlaps 13.

### Missense variants with AlphaMissense scores

Binding priority is a transparent structural prioritization, not an experimentally established affinity prediction:

- **High:** core MRK residue, distance ≤4 Å, pathogenic AlphaMissense, and pathogenic/likely-pathogenic ClinVar evidence without a conflict.
- **Moderate/peripheral:** pathogenic evidence but outside the core site or at 4–6 Å.
- **Possible/uncertain:** one evidence stream supports concern but ClinVar is uncertain/conflicting or AlphaMissense is not pathogenic.
- **Low/uncertain:** direct contact, but AlphaMissense is benign and ClinVar is uncertain.

| P35557 / PDB position | Variant | Distance to MRK (Å) | AlphaMissense | ClinVar evidence | Binding priority |
|---:|---|---:|---:|---|---|
| 61 | Tyr61Asn | 3.25 | 0.8868 — pathogenic | Uncertain, CV 1384860 | Possible/uncertain |
| 62 | Val62Ala | 3.62 | 0.9731 — pathogenic | Pathogenic, CV 576995 | **High** |
| 62 | Val62Met | 3.62 | 0.9462 — pathogenic | Pathogenic, CV 407147 | **High** |
| 63 | Arg63Cys | 2.73 | 0.1234 — benign | Uncertain/risk allele, CV 441128 | Low/uncertain |
| 63 | Arg63His | 2.73 | 0.1886 — benign | Uncertain, CV 2946975 | Low/uncertain |
| 63 | Arg63Leu | 2.73 | 0.3254 — benign | Uncertain, CV 1404564 | Low/uncertain |
| 159 | Ile159Asn | 4.33 | 0.9313 — pathogenic | Conflicting, CV 2904927 | Possible/uncertain |
| 159 | Ile159Met | 4.33 | 0.2207 — benign | Conflicting, CV 441117 | Possible/uncertain |
| 159 | Ile159Thr | 4.33 | 0.5886 — pathogenic | Uncertain, CV 2859052 | Possible/uncertain |
| 159 | Ile159Val | 4.33 | 0.1611 — benign | Pathogenic/likely pathogenic, CV 1671470 | Possible/uncertain |
| 210 | Met210Ile | 3.66 | 0.9915 — pathogenic | Pathogenic, CV 2852830, 44900 | **High** |
| 210 | Met210Lys | 3.66 | 0.9915 — pathogenic | Pathogenic, CV 31180 | **High** |
| 210 | Met210Thr | 3.66 | 0.9821 — pathogenic | Pathogenic, CV 793234 | **High** |
| 210 | Met210Val | 3.66 | 0.8229 — pathogenic | Likely pathogenic, CV 2670449, 2670450 | **High** |
| 211 | Ile211Asn | 3.59 | 0.9683 — pathogenic | Uncertain/risk allele, CV 428731 | Possible/uncertain |
| 211 | Ile211Thr | 3.59 | 0.9474 — pathogenic | Pathogenic, CV 2845244 | **High** |
| 214 | Tyr214Cys | 3.01 |
=== END RUN rpm8roj7m3a ===

=== RUN rjuz2esl9ms ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Overall assessment

**Possible allosteric communication is structurally plausible, but not strongly or independently confirmed.** PTP1B has a short residue-contact route from the FRJ allosteric site to the catalytic Cys215, and several elements of that route show correlated low-frequency motions in anisotropic normal-mode analysis (ANM). However, direct dynamical coupling between the FRJ-contact ensemble and Cys215 is weak and mode-dependent, while STINGAllo returned **no predicted residues** for 1T4J chain A.

The defensible conclusion is therefore:

> **A candidate communication pathway exists, with especially coherent low-frequency motion near A110–Cys215, but these analyses do not establish that FRJ binding causes allosteric regulation of Cys215.**

## Structural setup

- PDB **1T4J chain A** maps to **PTP1B, UniProt P18031**, with mapping identity 1.0.
- The bound ligand is **FRJ**.
- FRJ contacts, within 4.0 Å, are:
  **A188, A189, A192, A193, A196, A200, A276, A277, A279, A280, and A282**.
- **Cys215** is the catalytic nucleophile.
- The residue-contact network contains **282 protein residues and 1,379 edges**, using a 4.5 Å heavy-atom contact cutoff.

## 1. Normal-mode analysis

ANM was calculated on the 282 Cα atoms. There were 276 nontrivial modes; the lowest 20 had eigenvalues from 0.710 to 2.869.

A representative shortest structural route,

**A196 → A194 → A110 → C215**

showed the following eigenvalue-weighted dynamic cross-correlations:

| Path edge | Lowest 20 modes | All 276 modes |
|---|---:|---:|
| A196–A194 | 0.887 | 0.289 |
| A194–A110 | 0.562 | 0.275 |
| A110–C215 | 0.847 | 0.691 |

The alternative route **A189 → A191 → A110 → C215** gave similarly coherent low-frequency edge correlations of 0.855, 0.594, and 0.847.

### What NMA supports

- Selected residues along the structural route participate in strongly correlated collective motions in the lowest-frequency modes.
- The A110–C215 segment is particularly dynamically coupled.
- This is consistent with a mechanically connected route that could transmit conformational information from the FRJ region toward the catalytic site.

### What NMA does not support

- Coupling is not uniform across the entire FRJ–C215 route. For example:
  - A196–C215 correlation was **0.182** in the lowest 20 modes but **−0.090** over all modes.
  - A189–C215 was **−0.080** in the lowest 20 modes and **−0.055** over all modes.
  - Across all 11 geometric FRJ contacts, the mean lowest-20-mode correlation with C215 was slightly negative (**−0.063**), with individual values ranging from **−0.270 to +0.182**.
- The analysis provides no direction of information flow and no energetic or causal measure.
- It uses a harmonic model of one crystal structure, does not include ligand-induced perturbations, and does not compare ligand-bound, apo, or mutant conformations.
- High correlation between adjacent residues may partly reflect local packing rather than long-range communication.

## 2. Residue-contact network

All 11 FRJ-contacting residues had a path to C215, with shortest-path lengths of three to five edges. Representative shortest paths are:

- **A196 → A194 → A110 → C215**
- **A189 → A191 → A110 → C215**
- **A192 → A191 → A110 → C215**
- **A193 → A191 → A110 → C215**

More distal routes include:

- A200 → A198 → A108 → A110 → C215
- A276 → A188 → A191 → A110 → C215
- A277 → A192 → A191 → A110 → C215
- A279/A280 → A276 → A188 → A191 → A110 → C215

A191 and A110 are high-betweenness network nodes, with betweenness values of approximately 1,268 and 1,244, respectively; C215 has approximately 853.

### What the contact network supports

- The allosteric ligand site and catalytic cysteine are connected by a short, convergent structural corridor.
- A191 and A110 are network bottlenecks through which many routes pass.
- The network therefore supplies a plausible sequence of residues through which a conformational perturbation could reach the catalytic site.

### What the contact network does not support

- A graph path is not automatically an energy-transfer pathway.
- The network is unweighted: it contains proximity information, but not interaction strengths, free-energy coupling, or catalytic effects.
- It provides neither directionality nor evidence that ligand binding changes the pathway.
- Paths are structure- and cutoff-dependent and may differ in other PTP1B conformations.

## 3. STINGAllo

Two independent access routes were used:

1. The direct STINGAllo contract query for **1T4J chain A**
2. The integrated allosteric workflow with **FRJ** and STINGAllo enabled

Both returned:

- `success: true`
- `residues: []`

A query without the required chain filter returned an HTTP 400 response, so the valid conclusion concerns the chain-specific result: **no STINGAllo residue predictions were returned for 1T4J chain A**.

### What STINGAllo supports

- There is **no positive, residue-level STINGAllo prediction available for this structure/chain** with which to corroborate the ANM or network results.
- Consequently, the three approaches do not show positive three-way convergence.

### What STINGAllo does not support

- An empty result does **not** mean that PTP1B lacks allostery or that C215 cannot participate in allosteric communication.
- It more likely reflects absence of a stored/service prediction for this particular structure.
- There are therefore no STINGAllo residues that can be compared with FRJ-site residues, A191/A110, or C215.

## Integrated conclusion

| Analysis | Evidence for possible communication | Principal limitation |
|---|---|---|
| ANM | Coherent low-frequency motions along candidate routes, especially A110–C215 | Weak/mode-dependent endpoint coupling; no direction, energy, causality, or ligand-bound/apo comparison |
| Contact network | Short, convergent physical paths from FRJ contacts to C215 | Static proximity graph; not an energetic or directional pathway |
| STINGAllo | None available for 1T4J chain A | Empty output cannot be interpreted as evidence against allostery |

**Final assessment:** The structural and local dynamical results make FRJ-site-to-Cys215 communication in 1T4J **plausible enough to test**, particularly through the A191/A110 corridor. The evidence is nevertheless **inconclusive**: direct FRJ-site–C215 dynamic correlation is not robust across the ANM spectrum, and STINGAllo supplies no independent positive prediction. Demonstrating communication would require additional evidence, such as ligand-bound versus apo dynamics, pathway-focused mutagenesis, or catalytic assays.

### Final plan status

1. [✓] Complete ligand-contact and residue-numbering verification for chain A.
2. [✓] Run the normal-mode calculation and save the 20 lowest nontrivial ANM modes.
3. [✗] Initial eigenvector post-processing failed because the saved rows were not in flattened 3N form; corrected by extracting ProDy’s native eigenvectors and confirming exact eigenvalue agreement.
4. [✓] Recover a consistent Cα/eigenvector mapping and calculate fluctuation and endpoint-coherence summaries.
5. [✓] Build the residue-contact network and extract shortest paths from the FRJ contact region to Cys215.
6. [✓] Verify STINGAllo through both the direct contract and integrated workflow; both returned no residues.
7. [✓] Quantify edge-wise dynamical coherence and synthesize what all three analyses support and do not support.
=== END RUN rjuz2esl9ms ===

=== RUN rpb2z6btcfy ===
QUESTION:
Using only pocket-detection output on PTP1B (PDB 1T4J, ligands removed), rank the top three pockets by how likely each is to be an allosteric site, and justify the ranking.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H02_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[H02_c] [critical] [judged] a ranking of the top three pockets by allosteric likelihood with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Pocket-detection-only ranking

**Important qualification:** Pocket detection can establish that a surface cavity is geometrically detectable, but it cannot determine whether that cavity is **allosteric**. The rankings below are therefore a **priority ranking for allosteric-candidate follow-up**, not assignments of allostery. In particular, the P2Rank “probability” is pocket-detection confidence, not probability of allostery.

### Method

- Loaded PDB **1T4J**, chain A.
- Retained all **2,304 protein ATOM records**.
- Removed all **41 HETATM records** and all CONECT records; confirmed **0 heteroatoms remain**.
- Ran **fpocket 4.2.3** and **P2Rank 2.5.1** on the identical ligand-free structure.
- fpocket detected 18 pockets; P2Rank detected 3.
- Matched pockets by shared residue identifiers using Jaccard overlap.
- Ordered the three P2Rank pockets by the mean of their two methods’ native ranks, avoiding arbitrary fitted weights.

### Ranking

| Priority | Consensus pocket | P2Rank evidence | fpocket evidence | Pocket geometry and overlap | Interpretation |
|---|---|---|---|---|---|
| **1** | **P2Rank pocket1 ↔ fpocket pocket2** | Rank 1; score **7.22**; confidence **0.376** | Rank 2; score **0.167** | Volume **422.2 Å³**; SASA **109.1 Å²**; **10 shared residues**; Jaccard **0.588**; mean native rank **1.5** | Best-supported and most reproducibly detected cavity. This makes it the strongest pocket-only candidate, although the output does not establish that it is allosteric. |
| **2** | **P2Rank pocket3 ↔ fpocket pocket10** | Rank 3; score **1.87**; confidence **0.037** | Rank 10; score **0.076** | Volume **350.2 Å³**; SASA **100.2 Å²**; flexibility **0.394**; **4 shared residues**; Jaccard **0.333**; mean native rank **6.5** | Moderate priority. Although P2Rank ranks it third, it has substantially better independent fpocket support and overlap than P2Rank pocket2. Its moderate size and exposed geometry are compatible with a secondary surface pocket, but that remains a structural inference. |
| **3** | **P2Rank pocket2 ↔ fpocket pocket18** | Rank 2; score **2.03**; confidence **0.044** | Rank 18; score **0.003** | Volume **279.1 Å³**; SASA **80.1 Å²**; highest alpha-sphere solvent accessibility **0.729**; **3 shared residues**; Jaccard **0.214**; mean native rank **10.0** | Weakest consensus. Its high surface exposure and small volume could be compatible with a cryptic peripheral site, but fpocket detects it very poorly and with little residue agreement, so it ranks last. |

### Why P2Rank pocket3 outranks P2Rank pocket2

P2Rank alone favors pocket2: rank 2 versus rank 3. However, pocket2 maps to **fpocket pocket18**, whose fpocket score is only **0.003**, and the methods share just three residues. P2Rank pocket3 maps to **fpocket pocket10**, has a much stronger fpocket score (**0.076**), and shares four residues. Thus, when independent reproducibility is emphasized, pocket3 is the better-supported candidate.

### Bottom line

1. **P2Rank pocket1 / fpocket pocket2** — strongest pocket-only candidate  
2. **P2Rank pocket3 / fpocket pocket10** — moderate, independently supported candidate  
3. **P2Rank pocket2 / fpocket pocket18** — plausible geometry but weak cross-method support  

No ligand contacts, curated allosteric records, catalytic-site distances, conservation, or allosteric communication analyses were used. Consequently, this ranking identifies **detectable cavities worth prioritizing**, not proven allosteric sites.
=== END RUN rpb2z6btcfy ===

=== RUN rpynxuio53m ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Updated plan**
1. [✓] Identified glucose (`GLC`) and allosteric activator (`MRK`) in PDB 1V4S, chain A.
2. [✓] Retrieved structure-derived ligand contacts at a 4.0 Å cutoff.
3. [✗] Initial RCSB metadata parsing failed because the descriptor field was a list; corrected in Step 4.
4. [✓] Obtained the mmCIF structure, confirmed P35557 residue mapping, and built the contact network: 448 residues and 2,207 edges at a 4.5 Å heavy-atom cutoff.
5. [✗] Initial all-pairs calculation used string rather than tuple node IDs; corrected in Step 6.
6. [✓] Exhaustively compared all 14 × 14 activator/glucose contact-residue pairs and validated both tied shortest paths with the public network tool.

## Result

The shortest path length is **1 edge**, connecting **2 residues**.

There are **two equally short paths** from the allosteric-activator contact site to the glucose contact site:

1. **MET A210 → ASN A204**
   - MET210 contacts `MRK` at **3.66 Å**
   - ASN204 contacts `GLC` at **2.96 Å**

2. **ILE A211 → ILE A225**
   - ILE211 contacts `MRK` at **3.59 Å**
   - ILE225 contacts `GLC` at **3.65 Å**

Thus, either of the following is a valid shortest path:

**MET210 — ASN204** or **ILE211 — ILE225**

PDB author numbering aligns with UniProt P35557 numbering over the resolved chain, so these are also UniProt residue numbers.

*Endpoint note:* If the endpoints are forced to be the single closest-contact residue for each ligand—TYR215 for `MRK` and ASP205 for `GLC`—the path is **TYR215 → VAL199 → ALA201 → ASP205**, with length **3 edges (4 residues)**. The one-edge paths above are the global minima over all ligand-contact residues.
=== END RUN rpynxuio53m ===

=== RUN r5em8a6c1wj ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# Assessment of possible allosteric communication in PTP1B

## Overall assessment

The three analyses are consistent with **possible allosteric communication between the FRJ allosteric pocket and the catalytic/WPD-loop region** of PTP1B, but they do **not** establish a unique, directional pathway to Cys215.

The most defensible interpretation is:

- **High confidence:** 1T4J contains a real, experimentally characterized FRJ allosteric site approximately 20 Å from the active site. The measured FRJ–Cys215 minimum heavy-atom separation is **20.305 Å**.
- **Moderate support:** A static contact route and low-frequency elastic modes connect the FRJ pocket to His214–Cys215, making collective rearrangement plausible.
- **Not established:** That communication proceeds specifically through Asn193–Phe194–Leu110–His214–Cys215, or that Cys215 is the residue through which FRJ controls catalysis.
- **STINGAllo supports site identity, not communication:** It independently flags the known pocket region, but does not identify Cys215 as an allosteric site-forming residue and provides no pathway, direction, or perturbation information.

Thus, the results favor a **distributed/collective allosteric mechanism** over a single rigid lever.

## 1. Structural and experimental context

- **Protein:** human PTP1B, UniProt **P18031 / PTPN1 / PTN1_HUMAN**
- **Structure:** PDB **1T4J**, X-ray resolution 2.70 Å
- **Chain:** A; observed coordinates contain residues 1–282, although the construct is annotated as 1–298
- **Allosteric ligand:** FRJ, HETATM residue 299
- **Catalytic residue:** UniProt annotates **Cys215** exactly as the active-site phosphocysteine intermediate
- **Original experimental result:** Wiesmann et al. showed that the allosteric site is approximately 20 Å from the catalytic site and that FRJ-class inhibitors prevent formation of the active enzyme by restricting catalytic-loop mobility.

The experimental paper establishes an allosteric endpoint at the catalytic-loop level, but it does not by itself identify a single residue-by-residue relay to Cys215.

---

## 2. Residue contact-network analysis

### Pocket definition

Residues with a minimum heavy-atom contact to FRJ of ≤4.0 Å were:

**Pro188, Ala189, Leu192, Asn193, Phe196, Glu200, Glu276, Gly277, Lys279, Phe280, Met282.**

### Selected ligand-site-to-Cys215 path

Using a heavy-atom residue-contact graph with a 4.5 Å contact cutoff and edge weights equal to the minimum inter-residue atomic distance, the selected path was:

**Asn193 → Phe194 → Leu110 → His214 → Cys215**

| Edge | Minimum heavy-atom distance | Structural character |
|---|---:|---|
| Asn193–Phe194 | 1.331 Å | Peptide-bond-connected adjacent residues |
| Phe194–Leu110 | 3.608 Å | Side-chain hydrophobic/core packing |
| Leu110–His214 | 2.981 Å | N(L110)···O(His214) contact, geometrically consistent with hydrogen bonding |
| His214–Cys215 | 1.331 Å | Peptide-bond-connected adjacent residues |

The same distance-weighted route persisted over graph cutoffs from 4.0 to 10.0 Å. Under a step-count definition, 11 distinct three-edge routes existed; for example:

**Pro188–Phe191–Leu110–Cys215.**

Deleting any one edge of a representative shortest route did not eliminate an equal-length alternative.

### What the contact network supports

- A **physically plausible static connection** exists between the FRJ pocket and Cys215 through the hydrophobic core and the catalytic/WPD-loop region.
- Phe194, Leu110, and His214 are reasonable candidate relay or coupling residues.
- The connection is not dependent on one unique graph edge or route.

### What the contact network does not support

- It does not show that ligand binding propagates **directionally** along this route.
- It does not show that the route is dynamically used rather than being a static consequence of the bound conformation.
- It does not establish energetic coupling, causality, or a change in catalytic turnover.
- Contacts in one ligand-bound crystal structure can be conformation-specific or influenced by crystal packing.

---

## 3. Normal-mode analysis

I performed both:

- **Gaussian Network Model (GNM):** scalar Cα model
- **Anisotropic Network Model (ANM):** three-dimensional Cα model

using 282 Cα atoms, isotropic springs, and 15 Å contact cutoff. GNM and ANM results were repeated at 12 and 18 Å to test cutoff sensitivity.

### Participation of Cys215

Across the first ten nonzero modes at 15 Å, the participation ratio of Cys215 was:

- GNM: **0.988–1.000**
- ANM: **0.99985–0.99999**

Cys215 therefore participates strongly in the low-frequency motions. However, many other residues have similarly high participation ratios, and Cys215 was not uniquely a hinge; its residue rank varied across the modes. Participation alone is therefore supportive but not diagnostic.

### Collective correlation along the contact path

Ten-mode dynamic cross-correlations for adjacent path residues were:

| Adjacent pair | GNM DCC | ANM DCC |
|---|---:|---:|
| Asn193–Phe194 | 0.953 | 0.970 |
| Phe194–Leu110 | 0.763 | 0.864 |
| Leu110–His214 | 0.714 | 0.699 |
| His214–Cys215 | 0.832 | 0.935 |

This shows that the proposed route lies within a strongly co-moving elastic network.

### Coupling between Cys215 and the FRJ pocket

At the primary 15 Å cutoff:

- The α3-side pocket residues 188–200 correlate **positively** with Cys215:
  - GNM: approximately **+0.082 to +0.252**
  - ANM: approximately **+0.275 to +0.371**
- The α7-side pocket residues 276–282 correlate **negatively** with Cys215:
  - GNM: approximately **−0.186 to −0.367**
  - ANM: approximately **−0.039 to −0.233**

The pocket-wide mean correlation was weak:

- GNM: **−0.024**
- ANM: **+0.100**

Across 12/15/18 Å cutoffs, the pocket-wide mean changed sign:

| Contact cutoff | GNM mean DCC | ANM mean DCC | Largest absolute local DCC |
|---:|---:|---:|---:|
| 12 Å | −0.104 | +0.097 | 0.37–0.50 |
| 15 Å | −0.024 | +0.100 | 0.37 |
| 18 Å | +0.001 | −0.068 | 0.30–0.45 |

### What normal-mode analysis supports

- The pocket and catalytic-loop region participate in related low-frequency elastic motions.
- Residues along the proposed path are strongly co-moving.
- The opposite signs on the two sides of the pocket are more consistent with a **torsional or relative rearrangement** than with a simple rigid-body translation of the allosteric site toward the active site.
- The results make a collective allosteric mechanism plausible.

### What normal-mode analysis does not support

- It does not show that FRJ binding **causes** a change in Cys215 or WPD-loop dynamics. NMA was performed on the ligand-bound structure and therefore describes intrinsic modes of that conformation.
- It does not provide a direction of information flow or an energetic pathway.
- High local correlations may partly reflect the dense elastic network and the fact that adjacent residues were selected from the same contact graph.
- The model is coarse-grained and omits ligand-mediated forces, side-chain chemistry, solvent, and entropy.
- Missing coordinates 283–298 could influence terminal modes, although the pocket and Cys215 lie in the well-resolved portion of the chain.

A direct claim that FRJ suppresses the Cys215-containing loop would require an apo–holo comparison, ligand-perturbation simulations, or experimental dynamics.

---

## 4. STINGAllo prediction

The live STINGAllo API was queried with:

`/api/afrs?pdb_id=1T4J&chain_id=A`

It returned 14 predicted allosteric site-forming residues:

**Glu129, Glu130, Ser187, Pro188, Ala189, Leu192, Asn193, Phe196, Glu200, Glu276, Lys279, Phe280, Ile281, Met282.**

### Agreement with the FRJ pocket

Of these:

- **10 directly contact FRJ at ≤4.0 Å:** Pro188, Ala189, Leu192, Asn193, Phe196, Glu200, Glu276, Lys279, Phe280, Met282
- Ser187 and Ile281 contact FRJ just beyond 4 Å, at 4.048 and 4.319 Å
- Glu129 and Glu130 form a more remote predicted cluster

Thus, STINGAllo recovered 10 of the 11 residues in the 4 Å FRJ contact set and grouped most of the known pocket into two coherent regions:

- approximately residues 187–200
- approximately residues 276–282

### Relation to the proposed path

- STINGAllo intersection with the selected contact path: **Asn193 only**
- Cys215 predicted by STINGAllo: **No**
- Closest STINGAllo AFR to Cys215: **Leu192, 15.068 Å heavy-atom separation**

### What STINGAllo supports

- The method recognizes the 1T4J FRJ-binding region as an allosteric-site-forming region.
- It identifies plausible allosteric hotspots within both faces of the pocket.
- Its per-residue output is consistent with the pocket being a distributed allosteric region rather than a single isolated cleft.

### What STINGAllo does not support

- It does not test or predict communication between the FRJ pocket and Cys215.
- It does not distinguish the Cys215 endpoint from other catalytic-loop residues.
- It provides no pathway, direction, causal perturbation, or energetic coupling.
- The API returns a binary residue list without confidence scores for individual calls.
- Because 1T4J is already a known FRJ-bound structure, the overlap is a **retrospective consistency check**, not prospective experimental validation; the web publication also does not establish that every tested PDB entry was excluded from model development.

STINGAllo’s contribution is therefore site-level corroboration, not independent evidence for a Cys215 communication route.

---

## 5. Integrated interpretation

| Evidence | What it supports | What it does not establish |
|---|---|---|
| Residue contact network | A robust static route from the FRJ pocket through Phe194–Leu110–His214 to Cys215 | Direction, dynamics, energetic transmission, or causality |
| GNM/ANM normal modes | Low-frequency collective coupling along that route; differential rather than rigid-body behavior | A ligand-induced change or a specific Cys215 control mechanism |
| STINGAllo | Recognition of the known FRJ allosteric-pocket residues and additional candidate hotspots | Any path to Cys215, endpoint coupling, or causal mechanism |
| Original 1T4J experiments | FRJ is an allosteric inhibitor that prevents the active catalytic-loop conformation | A unique residue relay from FRJ to Cys215 |

## Bottom line

**Possible allosteric communication is supported**, and the most plausible picture is a distributed collective rearrangement linking the FRJ-bound α3/α7 pocket to the His214–Cys215 catalytic-loop region. The contact network and normal modes nominate Asn193–Phe194–Leu110–His214 as a candidate route, while STINGAllo independently corroborates the allosteric-pocket identity.

Nevertheless, the strongest conclusion is not that this is **the** communication pathway. Rather:

> FRJ binding at the allosteric site is consistent with perturbing collective motions that couple the pocket to the catalytic-loop region, but the residue-by-residue route, direction, and causal role of Cys215 remain unresolved
=== END RUN r5em8a6c1wj ===

=== RUN r9gexb3zx24 ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Conclusion

The combined evidence strongly supports the **AKT1 PH–kinase interface as a genuine, therapeutically actionable allosteric site**. The evidence is convergent:

- A crystal structure directly visualizes an allosteric ligand bridging the PH and kinase domains.
- MK-2206 is a potent allosteric AKT inhibitor in ChEMBL.
- AKT1 E17K is an activating, clinically pathogenic interface-proximal variant that is overwhelmingly predicted pathogenic by AlphaMissense.
- E17K is near the interface but is **not itself a direct ligand-contact residue** in PDB 3O96, so its relevance is through long-range regulation of the interface rather than direct steric interference with the bound ligand.

### Evidence synthesis

| Evidence | Result | Interpretation |
|---|---|---|
| **PDB 3O96** | 2.7 Å AKT1 structure with allosteric inhibitor **IQO** bound at the PH–kinase interface | Direct proof that the interface forms a ligand-accessible allosteric pocket |
| **3O96 contacts** | 21 protein residues within 4.5 Å: **5 in the PH domain** and **16 in the kinase domain** | The pocket is formed jointly by both domains, rather than being an ordinary kinase-site inhibitor |
| **ChEMBL MK-2206** | MK-2206 = **CHEMBL1079175**; AKT1 = **CHEMBL4282**. Representative biochemical records: AKT1 IC50 **5–10 nM**, Kd **11 nM**; AKT2 IC50 **12 nM**, Kd **21 nM**; AKT3 IC50 **65 nM**, Kd **213 nM** | Potent allosteric engagement of intact AKT, with modest AKT1 preference but pan-AKT biochemical activity |
| **ClinVar** | **VCV000013983**, AKT1 c.49G>A p.Glu17Lys, rs121434592: germline **Pathogenic** and somatic **Oncogenic**, multiple submitters/no conflicts | The residue has strong clinical and oncogenic significance; linked to Proteus syndrome, Cowden syndrome 6, and neoplasia/meningioma |
| **AlphaMissense** | Official release score **0.9977**, **likely pathogenic**; the mirror rounds this to 0.998 | Independent computational evidence that E17K is highly deleterious |
| **Geometry** | E17 is fully modeled in chain A; minimum heavy-atom distance to IQO = **5.704 Å** | E17 is outside the conventional ≤4.5 Å direct-contact shell and does not directly contact IQO |
| **Interface proximity** | E17 is **3.919 Å** from kinase-domain Lys297 | E17 lies at the kinase-facing edge of the PH domain and can regulate the autoinhibitory interface |

## Structural detail

Using a 4.5 Å heavy-atom cutoff, IQO contacts:

- **PH domain:** Trp80, Thr82, Val83, Ile84, Glu85  
- **Kinase domain:** Val201, Ser205, Leu210, Thr211, Leu264, Lys268, Val270, Val271, Tyr272, Arg273, Asp274, Ile290, Thr291, Asp292, Cys296, Tyr326

The closest contacts include Ser205, Asp292, Tyr272, and Cys296. This broad footprint explains why allosteric AKT inhibitors require both the PH and kinase domains and why disrupting the interface can compromise inhibitor action.

The original 3O96 paper also concluded that the ligand stabilizes an inactive arrangement in which the PH domain restrains the kinase, reinforcing that this is a regulatory interface rather than a passive protein-protein contact.

## Important ligand distinction

The ligand in 3O96 is **not MK-2206**:

- **3O96 ligand IQO:** C34H29N7O; InChIKey `BIWGYFZAEWGBAL-UHFFFAOYSA-N`
- **MK-2206:** CHEMBL1079175; C25H21N5O; InChIKey `ULDXWLCXEDXJGE-UHFFFAOYSA-N`

Thus, 3O96 supplies the atomic model of a ligand-bound AKT1 allosteric pocket, while ChEMBL supplies independent target-engagement pharmacology for MK-2206. The two are strongly convergent at the level of **allosteric mechanism and site class**, but the exact IQO
=== END RUN r9gexb3zx24 ===

=== RUN r9iy6v2nqvw ===
QUESTION:
For AKT1 (UniProt P31749), report ClinVar classification and AlphaMissense score for E17K, give the domain containing residue 17, and report its distance from the allosteric inhibitor in PDB entry 3O96 if the residue is modeled there.

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V02_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[V02_b] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "29022"}
[V02_c] [critical] [scripted] 0.9977
[V02_d] [critical] [judged] the PH domain is named and the distance from residue 17 to the 3O96 inhibitor is reported (residue 17 IS modelled: UniProt 17 = label_seq_id 20, the PDB author number differs)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# AKT1 (P31749) E17K — ClinVar, AlphaMissense, domain, and distance to allosteric inhibitor in PDB 3O96

## 1. ClinVar classification for E17K
| Field | Value |
|---|---|
| Gene / variant | AKT1, NM_001382430.1:c.49G>A (p.Glu17Lys) |
| ClinVar accession | **VCV000013983.20** (Variation ID 13983) |
| **Classification** | **Pathogenic** |
| Review status | Criteria provided, multiple submitters, no conflicts |
| Location | GRCh38 chr14:104,780,214 (G>A), single nucleotide variant |

Cross-check for conflicts: the same variant returned under *likely_pathogenic* (0 hits), *conflicting* (0 hits), *uncertain* (0 hits), *benign* (0 hits) and *likely_benign* (0 hits) for AKT1 — i.e. there is no dissenting/second classification record for E17K. Note: the pinned local ClinVar snapshot returned 0 AKT1 records, so the live NCBI E-utilities mode was used for this query.

UniProt also annotates this position as **VAR_055422**: somatic mutation in PROTEUS and breast (also colorectal/ovarian) cancer; results in increased T308 phosphorylation, higher basal ubiquitination, more efficient plasma-membrane recruitment, and altered PIP lipid specificity of the AKT1 PH domain.

## 2. AlphaMissense score for E17K
| Field | Value |
|---|---|
| **am_pathogenicity** | **0.9977** |
| AlphaMissense class | **Pathogenic** |

(For context, all other substitutions at position 17 scored ≥0.991, i.e. the site is broadly constrained.) Source: AlphaMissense AA-substitution table for P31749.

## 3. Domain containing residue 17
UniProt P31749 feature annotation:
- **Domain: PH (pleckstrin homology) — residues 5–108** → **residue 17 (E17) lies in the PH domain**, at its N-terminal region, immediately adjacent to the annotated PIP-lipid **binding site residues 14–19**.
- Other domain boundaries for reference: Protein kinase domain 150–408; AGC-kinase C-terminal region 409–480; disordered regions 113–138 and 450–480.

## 4. Distance from E17 to the allosteric inhibitor in PDB 3O96
- **Entry:** 3O96 — "Crystal Structure of Human AKT1 with an Allosteric Inhibitor" (RCSB keywords: *Pleckstrin homology, protein kinase, allosteric inhibitor*).
- **Allosteric inhibitor:** ligand component **IQO** — 1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one (C34H29N7O), present in chain A.
- **Residue is modeled:** Yes. Chain A, author residue 17 = **GLU** = UniProt P31749 residue 17 (numbering coincides; verified against the deposited coordinates).
- **Distance (minimum heavy-atom separation, E17 ↔ IQO): 5.7 Å**

### Context: the inhibitor's contact neighborhood
| Residue (chain A) | Min distance to IQO (Å) |
|---|---|
| **E17 (Glu)** | **5.70** |
| Y18 | 6.60 |
| K14 | 7.82 |
| K20 | 9.06 |
| R15 | 9.27 |
| G16 | 9.70 |
| H13 / L12 / I19 | 14.29 / 15.61 / 12.07 |
| Tightest contacts overall | S205 2.89, D292 3.06, Y272 3.11, C296 3.15, K268 3.26, I290 3.38, W80 3.41, I84 3.46 |

Interpretation: IQO occupies the canonical allosteric site at the **PH-domain/kinase-domain interface** (contacts on both PH-domain residues such as W80/I84 and kinase-domain residues S205/K268–I290). E17 in the PH domain is **not** a direct ligand-contact residue — at 5.7 Å it sits just outside the inhibitor's first coordination shell, adjacent to the N-terminal PIP-binding surface of the PH domain. Its proximity to the allosteric pocket is consistent with the documented functional coupling of E17K to PH-domain lipid binding and membrane recruitment, but the 5.7 Å separation means the mutation is **allosteric to the inhibitor site rather than a direct contact**.

### Evidence provenance
- ClinVar: `biomni.tool.[TOOL]` (live NCBI E-utilities mode; local pinned snapshot had no AKT1 entries).
- AlphaMissense: `biomni.tool.[TOOL]` (local AlphaMissense AA-substitution table).
- Domain/binding-site/variant annotations: UniProtKB P31749 REST entry (no listed BioMNI tool covers domain features, so the raw UniProt entry was fetched directly).
- PDB 3O96 chain→UniProt mapping: `biomni.tool.[TOOL]` (chain A → P31749); ligand identity: `biomni.tool.biolip.[TOOL]`; distances: `biomni.tool.[TOOL]` (minimum heavy-atom distance to IQO, cutoff 100 Å); entry title/chem-comp metadata from the RCSB data API; residue identity confirmed from the deposited 3O96 coordinates.
=== END RUN r9iy6v2nqvw ===

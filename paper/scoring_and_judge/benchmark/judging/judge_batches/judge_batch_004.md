# Judge batch 004 of 24

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

=== RUN rt0mmt399j2 ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## STINGAllo prediction for PTP1B (PDB 1T4J, chain A)

**Predicted allosteric residue positions:**  
**129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282**

For added clarity, the deposited PTP1B chain-A residue identities are:

| Residue | Identity | Residue | Identity |
|---:|---|---:|---|
| 129 | Glu (E) | 196 | Phe (F) |
| 130 | Glu (E) | 200 | Glu (E) |
| 187 | Ser (S) | 276 | Glu (E) |
| 188 | Pro (P) | 279 | Lys (K) |
| 189 | Ala (A) | 280 | Phe (F) |
| 192 | Leu (L) | 281 | Ile (I) |
| 193 | Asn (N) | 282 | Met (M) |

**Service-response date:** **28 October 2026**  
HTTP `Date` header: `Wed, 28 Oct 2026 07:02:30 GMT`

The JSON payload itself contains no date field, so the date above is the service response’s HTTP date. The request was:

`GET https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A`

The API returned HTTP 200 with 14 unique residue sequence numbers. Residue identities above were mapped from the deposited 1T4J structure; the authoritative prediction is the position list from STINGAllo.
=== END RUN rt0mmt399j2 ===

=== RUN ri9t9wmz2yt ===
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
## Result

**The answer depends on the pocket-detection algorithm:**

- **fpocket:** The top three contain the **glucose site**, but **not** the allosteric-activator site.
- **P2Rank:** The top three contain **both** sites.

### Ligand removal audit

Starting from PDB **1V4S**, chain **A**, UniProt **P35557**:

- Retained **3,505 ATOM** records.
- Removed **185 HETATM** records.
- Removed components: **GLC** (glucose), **MRK** (allosteric activator), **NA** (sodium), and **HOH** (waters).
- Verified ligand-free structure: **0 HETATM records**.

Site matching was performed by comparing detected pocket-lining residues with the 4.0 Å heavy-atom contact residues of each ligand in the original structure.

## fpocket result

| fpocket pocket | Score | Site assignment | Contact-residue overlap |
|---|---:|---|---:|
| **1** | 0.223 | Neither site; weak glucose-site overlap only | GLC 2/14; MRK 0/14 |
| **2** | 0.139 | **Glucose site** | **GLC 13/14** |
| **3** | 0.111 | Neither site | GLC 0/14; MRK 0/14 |
| 4 | 0.089 | Neither site | 0/14 for both |
| 5 | 0.086 | Neither site | 0/14 for both |
| **6** | 0.072 | **Allosteric-activator site** | **MRK 14/14** |

Thus, for fpocket:

- **Glucose site → pocket 2**
- **Allosteric-activator site → pocket 6**
- The **top three do not include both sites**; they include the glucose site only.

## P2Rank cross-check

| P2Rank rank | Score | Probability | Site assignment | Contact-residue overlap |
|---|---:|---:|---|---:|
| **1** | 16.09 | 0.770 | **Main glucose-site pocket** | **GLC 8/14** |
| **2** | 7.05 | 0.365 | **Allosteric-activator site** | **MRK 13/14** |
| **3** | 2.14 | 0.050 | **Secondary glucose-site subpocket** | **GLC 4/14** |

Thus, for P2Rank:

- **Glucose site → ranks 1 and 3**; rank 1 is the principal match.
- **Allosteric-activator site → rank 2**.
- The **top three include both functional sites**.

The assignments are geometric matches based on overlap with the original ligand-contact residues, not affinity predictions.

Generated files:

- `1V4S_ligand_free.pdb`
- `1V4S_ligand_free_pocket_detection.json`
- `1V4S_pocket_site_overlap_summary.csv`

### Final plan

1. [✓] Identify the protein chain and all ligands bound to PDB 1V4S
2. [✓] Verify the ligand-free structure and create an auditable receptor copy
3. [✓] Run/confirm pocket detection and extract the top three ranked pockets
4. [✓] Identify glucose-site and allosteric-activator-site contacts in the original structure
5. [✓] Match each detected pocket to each site and report the evidence
=== END RUN ri9t9wmz2yt ===

=== RUN rjks36swza3 ===
QUESTION:
Which PDB entries contain human SHP2 (UniProt Q06124) bound to SHP099 (ligand ID 5OD)? Also report whether ChEMBL holds bioactivity records for SHP099 against SHP2, and if so the assay types and best value; if not, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L04_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[L04_b] [critical] [scripted] ["5EHR", "6BMU", "6BMW", "6BMY", "6CMR", "6CMS", "6CRG", "8WFY"]
[L04_c] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## 1. PDB entries: human SHP2 (Q06124) + SHP099 (ligand ID 5OD)

**8 entries** contain chem comp **5OD** bound to a polymer entity mapped to UniProt **Q06124**. Verified individually via the RCSB Data API (`rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession` = Q06124; `pdbx_entity_nonpoly.comp_id` = 5OD). A control query for *every* entry containing 5OD returned exactly this same set — no SHP099 complexes were missed.

| PDB ID | Method | Res. (Å) | Title | Other ligands | Citation (PMID) |
|---|---|---|---|---|---|
| **5EHR** | X-ray | 1.70 | SHP2 in complex with allosteric inhibitor SHP099 | PO4 | 27362227 (Nature, 2016) |
| **6BMU** | X-ray | 2.12 | SHP2 with allosteric inhibitors SHP099 and SHP244 | DZV (SHP244), PO4, GOL | 29304282 (ACS Chem Biol, 2018) |
| **6BMW** | X-ray | 2.10 | SHP2 with allosteric inhibitors SHP099 and SHP504 | DZS (SHP504), PO4, GOL | 29304282 (ACS Chem Biol, 2018) |
| **6BMY** | X-ray | 2.09 | SHP2 with allosteric inhibitors SHP099 and SHP844 | DYV (SHP844), PO4, GOL | 29304282 (ACS Chem Biol, 2018) |
| **6CMR** | X-ray | 2.21 | Closed structure of active SHP2 mutant **E76D** bound to SHP099 | — | 30375376 (Nat Commun, 2018) |
| **6CMS** | X-ray | 2.68 | Closed structure of active SHP2 mutant **E76K** bound to SHP099 | — | 30375376 (Nat Commun, 2018) |
| **6CRG** | X-ray | 2.75 | Crystal structure of SHP2 **E76K** GOF mutant with SHP099 | SO4, GOL | 30375388 (Nat Commun, 2018) |
| **8WFY** | X-ray | 2.60 | "The Crystal Structure of SHP2 from Biortus" (SHP099-bound) | — | not yet published |

Notes: 5OD was confirmed in the chemical-component dictionary as SHP099 — name *6-(4-amino-4-methylpiperidin-1-yl)-3-(2,3-dichlorophenyl)pyrazin-2-amine*, formula C16H19Cl2N5, InChIKey **YGUFCDOEKKVKJK-UHFFFAOYSA-N**, SMILES `CC1(N)CCN(c2cnc(-c3cccc(Cl)c3Cl)c(N)n2)CC1`. 6CMR/6CMS/6CRG are gain-of-function mutants (E76D/E76K) of the same Q06124 entity; all others are wild-type human SHP2.

## 2. ChEMBL: yes — SHP099 has extensive SHP2 bioactivity records

**Yes.** SHP099 is in ChEMBL as **CHEMBL4060033** — an exact structure match to PDB 5OD (same InChIKey `YGUFCDOEKKVKJK-UHFFFAOYSA-N`, C16H19Cl2N5). It carries **259 total activity records**, of which **89 are against human SHP2** (target **CHEMBL3864**, UniProt Q06124). There are **0** records against mouse SHP2 (CHEMBL2620/P35235).

**Assay types (all 89 SHP2 records are `assay_type = B`, i.e. Binding)** — standard types:

| Standard type | n | Notes |
|---|---|---|
| IC50 | 37 | Main potency metric |
| Inhibition (%) | 16 | Mostly non-numeric (4 have values: 100%, 100%, 100%, 93.42%) |
| kon | 9 | No numeric values recorded |
| k_off | 9 | No numeric values recorded |
| Kd | 4 | SPR / label-free kinetics |
| K | 4 | **Data-quality flag:** units are `/s`, `10^6/Ms`, `10^-2/s` — these are rate constants mis-typed as "K" |
| Km / Vmax | 3 / 3 | Non-competitive inhibition kinetic series (Km 89–136 µM; Vmax 23.8–38.6 /s) |
| Delta Tm | 2 | +7.5 °C and +4.37 °C |
| Ki | 1 | Reversible inhibition (non-competitive) |
| TIME | 1 | Pre-incubation time |

**Best values vs human SHP2:**

- **Most potent IC50: 0.145 nM** (pChEMBL 9.84) — assay CHEMBL4823680, "Inhibition of human SHP2 catalytic activity in human MV4-11 cells" (cell-based, BAO cell-based format; confidence 9).
- **Best cell-free/biochemical IC50: 39.7 nM** (pChEMBL 7.40) — CHEMBL5120329, DiFMUP substrate, wild-type SHP2.
- **Most consistently reproduced value: ~70–71 nM** (pChEMBL 7.15–7.16) — the canonical allosteric-inhibition IC50, reported in ~15 independent assays across many documents (e.g. CHEMBL4414125, CHEMBL4429517, CHEMBL4431936, CHEMBL4701889, CHEMBL5096979, CHEMBL5731422/5733838/5734235/5735724/5738278).
- **Best Ki: 67 nM** (pChEMBL 7.17) — CHEMBL5145447.
- **Best binding affinity: Kd = 10 nM** (pChEMBL 8.00) — CHEMBL5578845 by SPR; also 17 nM (CHEMBL6098074), 73 nM (CHEMBL4668481), and 1500 nM for the E76K mutant (CHEMBL4668480).
- **Median of the 37 IC50 values: 84 nM**; full range 0.145 nM → 250 µM. The weak/inactive end: 6.49 µM (E76K mutant, CHEMBL5622804), >10 µM (isolated PTP domain, CHEMBL5145445), >50 µM (PTPase domain, CHEMBL5622806), 250 µM (CHEMBL5739520).

**Caveats worth noting:** (a) the ChEMBL molecule record for CHEMBL4060033 has **no preferred name and no synonyms** (the molecule_synonym API returns 404 for it), so it must be identified by structure/InChIKey rather than by name — a text search for "SHP099" returns a *different* analog first (CHEMBL5280755, C18H22Cl2N4O, hydroxymethyl analog); (b) several SHP2 records have empty `standard_value` (all 9 kon and 9 k_off entries, most Inhibition-% entries), so they cannot contribute to a best-value determination.

*Sources queried live: RCSB Search API + RCSB Data/GraphQL REST API; ChEMBL REST API (ChEMBL_37).*
=== END RUN rjks36swza3 ===

=== RUN r0mvt6mp6vv ===
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
## Inhibitor identity

PDB **3O96** contains **AKT inhibitor VIII**, called **Inhibitor VIII** in the primary paper and also known as **Akti-1/2** or the **AKT1/2 inhibitor**.

- PDB ligand component: **IQO**
- PDB ligand residue: **A444**
- Molecular formula: **C34H29N7O**
- Systematic name: **1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one**

It is an allosteric inhibitor that binds at the interface between the AKT1 PH and kinase domains.

## AKT1 residues within 4 Å of IQO

Distances below are the minimum heavy-atom distance from any protein atom to any inhibitor atom.

| AKT1 residue | Minimum distance (Å) | UniProt P31749 domain |
|---|---:|---|
| TRP80 | 3.413 | PH domain, 5–108 |
| THR82 | 3.948 | PH domain, 5–108 |
| VAL83 | 3.739 | PH domain, 5–108 |
| ILE84 | 3.460 | PH domain, 5–108 |
| GLU85 | 3.745 | PH domain, 5–108 |
| SER205 | 2.893 | Protein kinase domain, 150–408 |
| LEU210 | 3.661 | Protein kinase domain, 150–408 |
| THR211 | 3.584 | Protein kinase domain, 150–408 |
| LEU264 | 3.640 | Protein kinase domain, 150–408 |
| LYS268 | 3.256 | Protein kinase domain, 150–408 |
| VAL271 | 3.905 | Protein kinase domain, 150–408 |
| TYR272 | 3.113 | Protein kinase domain, 150–408 |
| ARG273 | 3.752 | Protein kinase domain, 150–408 |
| ASP274 | 3.825 | Protein kinase domain, 150–408 |
| ILE290 | 3.376 | Protein kinase domain, 150–408 |
| THR291 | 3.975 | Protein kinase domain, 150–408 |
| ASP292 | 3.062 | Protein kinase domain, 150–408 |
| CYS296 | 3.146 | Protein kinase domain, 150–408 |

### Domain summary

Using the domain boundaries in UniProtKB **P31749 (AKT1_HUMAN)**:

- **PH domain, residues 5–108:** TRP80, THR82, VAL83, ILE84, GLU85 — **5 residues**
- **Protein kinase domain, residues 150–408:** SER205, LEU210, THR211, LEU264, LYS268, VAL271, TYR272, ARG273, ASP274, ILE290, THR291, ASP292, CYS296 — **13 residues**
- **AGC-kinase C-terminal domain, residues 409–480:** **none**

Thus, the inhibitor directly bridges the **PH domain and protein kinase domain**, consistent with its allosteric mechanism.

### Calculation and numbering notes

- Structure: PDB **3O96**, chain A, 2.70 Å resolution.
- Criterion: minimum Euclidean distance of **≤4.0 Å** between protein and ligand heavy atoms.
- The contact set is unchanged when all alternate conformers are included.
- PDB author numbering matches canonical UniProt P31749 numbering for all 367 coordinate residues.
- Two ordered waters, A449 and A455, are also within 4 Å but are excluded from the AKT1 residue list.

### Sources

- [RCSB PDB entry 3O96](https://www.rcsb.org/structure/3O96)
- [RCSB ligand IQO](https://www.rcsb.org/ligand/IQO)
- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry)
- Wu WI et al. *Crystal structure of human AKT1 with an allosteric inhibitor reveals a new mode of kinase inhibition.* **PLoS ONE** 2010;5:e12913. [doi:10.1371/journal.pone.0012913](https://doi.org/10.1371/journal.pone.0012913), PMID: [20886116](https://pubmed.ncbi.nlm.nih.gov/20886116/).
=== END RUN r0mvt6mp6vv ===

=== RUN rs2p1cdbk65 ===
QUESTION:
Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G02_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[G02_b] [critical] [judged] the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separated from the retrieved evidence

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan

1. [✓] Inspect the complete 1OPK coordinate/HETATM record, identify how the myristoyl group is represented, and calculate direct contacts for the ATP ligand and myristoyl group
2. [✓] Strip bound ligands and run pocket detection; map detected pockets to the ATP and myristoyl sites and record each site's detection rank
3. [✗] Initial ChEMBL assay-metadata join failed because the local schema uses `assays.chembl_id`, not `assay_chembl_id`
3a. [✓] Inspect the actual schema and complete the corrected potency, assay, and variant join
4. [✓] Retrieve ClinVar and AlphaMissense evidence for T315I
5. [✓] Calculate minimum heavy-atom distances from mouse T315 to the contact residues defining each site in 1OPK
6. [✗] Initial human–mouse mapping output failed only during NumPy-to-JSON serialization
6a. [✓] Rerun the mapping with native integer conversion and verify residue equivalence
7. [✓] Integrate the structural, potency, and variant evidence and explain the implications for ATP-competitive versus myristoyl-site/allosteric inhibitors

## Important provenance qualification

**PDB 1OPK is mouse ABL1, UniProt P00520, not human P00519.** It is a 1.8-Å structure of the SH3–SH2–kinase construct. However, alignment of human P00519 and mouse P00520 showed that:

- Human and mouse residue 315 are both threonine.
- All **27/27 mapped ATP- and myristoyl-site contact residues** are identical and retain the same canonical numbering.

Thus the topology and distances are directly transferable to human numbering, although the deposited structure itself is mouse.

The deposited ligands are:

- **P16 = PD166326**, an ATP-site inhibitor—not imatinib.
- **MYR = myristic acid**, defining the myristoyl pocket.

Therefore, 1OPK provides site topology but not an imatinib-specific bound pose.

## 1. Contacts in PDB 1OPK

Contacts were calculated as minimum heavy-atom distances ≤4.0 Å. Canonical ABL1 numbers are given first, followed by PDB author numbers.

### ATP-site probe P16/PD166326 — 19 contacts

| Canonical ABL1 | PDB | Canonical ABL1 | PDB |
|---:|---:|---:|---:|
| L248 | L267 | I313 | I332 |
| Y253 | Y272 | **T315** | **T334** |
| V256 | V275 | E316 | E335 |
| A269 | A288 | F317 | F336 |
| V270 | V289 | M318 | M337 |
| K271 | K290 | G321 | G340 |
| E286 | E305 | L370 | L389 |
| M290 | M309 | A380 | A399 |
| V299 | V318 | D381 | D400 |
|  |  | F382 | F401 |

This places the canonical gatekeeper **T315 directly on the ATP-site edge** and in direct contact with P16.

### Myristoyl probe MYR — 8 contacts

| Canonical ABL1 | PDB |
|---:|---:|
| L340 | L359 |
| L341 | L360 |
| A344 | A363 |
| L429 | L448 |
| A433 | A452 |
| E462 | E481 |
| I502 | I521 |
| L510 | L529 |

The MYR and ATP-site contact sets are spatially distinct.

## 2. Pocket-detection ranks on the ligand-stripped structure

All HETATM records, including MYR and P16, were removed before running fpocket 4.2.3 and P2Rank 2.5.1.

| Site | fpocket rank | fpocket score | Druggability | Volume, Å³ | P2Rank rank | P2Rank score | P2Rank probability |
|---|---:|---:|---:|---:|---:|---:|---:|
| **ATP/P16** | **2** | 0.320 | 0.913 | 736 | **1** | 23.77 | 0.892 |
| **MYR** | **3** | 0.211 | 0.547 | 491 | **2** | 11.32 | 0.606 |

Mapping audit:

- fpocket ATP pocket #2 contains **18/19 P16-contact residues**.
- fpocket myristoyl pocket #3 contains **8/8 MYR-contact residues**.
- P2Rank independently assigns the ATP pocket rank 1 and the myristoyl pocket rank 2.

Thus both detectors identify the ATP cavity as the more prominent pocket in this conformation.

## 3. ChEMBL potency

Values below are from the ChEMBL 37 target record **CHEMBL1862 / P00519** where available. IC50 is used as the common potency metric.

### Imatinib, CHEMBL941

- Wild-type/unspecified ABL1: 39 exact IC50 records spanning **19.9–7,700 nM**, median **223 nM**.
- T315I: three exact IC50 values—**1,100, 5,155, and 74,000 nM**—plus numerous right-censored values, generally `>1,000` to `>100,000 nM`.
- A particularly informative matched recombinant FRET assay pair:
  - Wild type, CHEMBL2320772: **98.2 nM**
  - T315I, CHEMBL2320771: **5,155 nM**
  - Approximately **52-fold loss of potency**

The heterogeneous IC50 distribution reflects different constructs and assay formats; the matched WT/T315I pair is more interpretable than the global median.

### Asciminib, CHEMBL4208229

Two exact target-linked IC50 records:

- **0.5 nM**, CHEMBL4200739
- **16 nM**, CHEMBL5739300

Broader ChEMBL records also contain mutant activity, although not as P00519 IC50 records:

- Human BCR-ABL1 T315I biochemical FRET **EC50: 6.45 nM**, CHEMBL5374124
- Mouse Ba/F3 T315I cellular **GI50: 7.64 nM**, CHEMBL4200741

The EC50 and GI50 should not be directly pooled with the IC50 values, but they support retained asciminib activity against T315I.

## 4. T315I evidence

- **ClinVar variation 27663:** NM_005157.6:c.944C>T, p.Thr315Ile  
  - Clinical significance: **Likely pathogenic; association**
  - Review status: **multiple submitters, no conflicts**
- **AlphaMissense T315I:**
  - Pathogenicity score: **0.9991**
  - Classification: **pathogenic**

## 5. Distance from T315 to each site

Distances were calculated directly from the wild-type 1OPK coordinates, using **PDB T334 = canonical T315**.

| Metric | ATP/P16 site | MYR site |
|---|---:|---:|
| Minimum heavy-atom distance, T315 to bound ligand | **3.24 Å** | **25.59 Å** |
| Residue-centroid to ligand-centroid distance | **7.08 Å** | **32.28 Å** |
| Closest site-contact residue other than T315 | E316, 1.33 Å | A344, **20.43 Å** |

For ATP/P16, the closest pair was T315 OG1–P16 C16. For MYR, it was T315 OG1–MYR C14.

These are wild-coordinate distances; they do not model the steric rearrangement caused by replacing threonine with isoleucine.

## Interpretation: what does T315I imply?

### ATP-competitive inhibitors, including imatinib

T315 is the **gatekeeper residue** and is already a direct ATP-pocket contact in 1OPK. Replacing threonine with isoleucine:

- Adds substantially greater side-chain bulk in a crowded ATP pocket.
- Removes the threonine hydroxyl and associated polar/H-bond complementarity.
- Can alter the local kinase conformation and ATP-binding geometry.

The ChEMBL matched data demonstrate the consequence directly: imatinib shifts from **98.2 nM for WT to 5,155 nM for T315I**, with other assays showing even greater loss of potency. Thus:

- **Imatinib and most conventional type-I/type-II ATP-site inhibitors are strongly challenged by T315I.**
- The effect is not universal: ATP-site inhibitors specifically engineered to accommodate the isoleucine gatekeeper can retain activity.

### Myristoyl-site/allosteric inhibitors, exemplified by asciminib

The myristoyl site is **25.6 Å from T315 at the closest ligand-atom level**, and no MYR-contact residue is closer than approximately 20.4 Å. Consequently, T315I does not directly obstruct asciminib binding or compete with the myristoyl-site interaction.

Accordingly:

- Asciminib retains biochemical and cellular activity against T315I, including the ChEMBL T315I EC50 of **6.45 nM**.
- Unlike ATP-competitive inhibitors, asciminib is not directly defeated by the gatekeeper substitution because it binds the N-terminal myristoyl pocket and stabilizes an inactive ABL conformation.
- Cellular efficacy can still depend on ABL abundance, myristoylation/N-terminal processing, and kinase state; T315I is therefore not a direct steric resistance mechanism for asciminib, but the cellular context can influence its magnitude of activity.

**Bottom line:** T315I severely compromises the ATP-site interaction used by imatinib-like inhibitors, whereas the distant myristoyl-site mechanism used by asciminib largely preserves activity.

### Data sources

- RCSB PDB **1OPK**
- BioLiP ligand/contact records for **P16** and **MYR**
- fpocket **4.2.3** and P2Rank **2.5.1**
- ChEMBL 37 target **CHEMBL1862**; compounds **CHEMBL941** and **CHEMBL4208229**
- ClinVar variation **27663**
- AlphaMissense **P00519:T315I**
=== END RUN rs2p1cdbk65 ===

=== RUN rwxrv7yxb85 ===
QUESTION:
Run PocketMiner on the autoinhibited SHP2 structure 2SHP chain A (UniProt Q06124). Map the residues that contact SHP099 in PDB entry 5EHR onto 2SHP through UniProt numbering and report their PocketMiner scores next to the scores of the ten highest-scoring residues. Are the SHP099 site residues among the high scorers?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P08_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[P08_b] [critical] [scripted] [{"chain": "A", "pdb_number": 220, "residue_name": "ARG", "score": 0.9235}, {"chain": "A", "pdb_number": 423, "residue_name": "TRP", "score": 0.9177}, {"chain": "A", "pdb_number": 218, "residue_name": "THR", "score": 0.9139}, {"chain": "A", "pdb_number": 111, "residue_name": "ARG", "score": 0.9138}, {"chain": "A", "pdb_number": 9, "residue_name": "PRO", "score": 0.9065}, {"chain": "A", "pdb_number": 460, "residue_name": "SER", "score": 0.9052}, {"chain": "A", "pdb_number": 129, "residue_name": "LYS", "score": 0.9043}, {"chain": "A", "pdb_number": 219, "residue_name": "THR", "score": 0.9002}, {"chain": "A", "pdb_number": 366, "residue_name": "LYS", "score": 0.8997}, {"chain": "A", "pdb_number": 33, "residue_name": "PRO", "score": 0.8994}]
[P08_c] [critical] [scripted] [{"uniprot_number": 108, "pdb_number_2SHP": 108, "pocketminer_score": 0.8084, "pocketminer_rank_in_chain_A": 63}, {"uniprot_number": 110, "pdb_number_2SHP": 110, "pocketminer_score": 0.8349, "pocketminer_rank_in_chain_A": 47}, {"uniprot_number": 111, "pdb_number_2SHP": 111, "pocketminer_score": 0.9138, "pocketminer_rank_in_chain_A": 4}, {"uniprot_number": 113, "pdb_number_2SHP": 113, "pocketminer_score": 0.7881, "pocketminer_rank_in_chain_A": 72}, {"uniprot_number": 114, "pdb_number_2SHP": 114, "pocketminer_score": 0.7931, "pocketminer_rank_in_chain_A": 68}, {"uniprot_number": 218, "pdb_number_2SHP": 218, "pocketminer_score": 0.9139, "pocketminer_rank_in_chain_A": 3}, {"uniprot_number": 219, "pdb_number_2SHP": 219, "pocketminer_score": 0.9002, "pocketminer_rank_in_chain_A": 8}, {"uniprot_number": 249, "pdb_number_2SHP": 249, "pocketminer_score": 0.7307, "pocketminer_rank_in_chain_A": 99}, {"uniprot_number": 250, "pdb_number_2SHP": 250, "pocketminer_score": 0.7727, "pocketminer_rank_in_chain_A": 78}, {"uniprot_number": 253, "pdb_number_2SHP": 253, "pocketminer_score": 0.8547, "pocketminer_rank_in_chain_A": 36}, {"uniprot_number": 254, "pdb_number_2SHP": 254, "pocketminer_score": 0.8423, "pocketminer_rank_in_chain_A": 43}, {"uniprot_number": 257, "pdb_number_2SHP": 257, "pocketminer_score": 0.6032, "pocketminer_rank_in_chain_A": 182}, {"uniprot_number": 491, "pdb_number_2SHP": 491, "pocketminer_score": 0.8492, "pocketminer_rank_in_chain_A": 42}, {"uniprot_number": 492, "pdb_number_2SHP": 492, "pocketminer_score": 0.8556, "pocketminer_rank_in_chain_A": 35}, {"uniprot_number": 495, "pdb_number_2SHP": 495, "pocketminer_score": 0.6891, "pocketminer_rank_in_chain_A": 122}]
[P08_d] [critical] [scripted] {"n_site_residues": 15, "n_scored": 15, "n_in_the_top10": 3, "best_rank": 3, "median_rank": 47}
[P08_e] [critical] [judged] the answer states that PocketMiner is a screening tool with modest accuracy (per-protein AUC about 0.65 on the independent test split), so the scores rank cryptic-pocket propensity and do not establish that a residue is a pocket or that the site is allosteric
[P08_f] [critical] [judged] the mapping between the two entries is stated (both are SHP2, Q06124; the 5EHR SHP099 contacts are given in UniProt numbering)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**Yes—some, but not all, SHP099-contacting residues are among the high scorers.**

Using a strict **2SHP chain-A-only** PocketMiner run:

- **3 of 15** SHP099-contacting residues are in the chain-A **top 10**:
  - **Thr218** — rank 2
  - **Arg111** — rank 3
  - **Thr219** — rank 6
- **14 of 15** are in PocketMiner’s top quartile by score percentile.
- Mean PocketMiner score:
  - SHP099-contact residues: **0.81251**
  - All 491 resolved chain-A residues: **0.50210**
- The 10th-highest chain-A score was **0.891590**.

## Ten highest-scoring residues in 2SHP chain A

| Rank | 2SHP PDB residue | UniProt Q06124 | PocketMiner score | Percentile | SHP099 contact? |
|---:|---|---|---:|---:|:---:|
| 1 | Arg220 | R220 | 0.924785 | 100.00 | No |
| 2 | **Thr218** | **T218** | **0.914970** | **99.80** | **Yes** |
| 3 | **Arg111** | **R111** | **0.914450** | **99.59** | **Yes** |
| 4 | Pro9 | P9 | 0.906765 | 99.39 | No |
| 5 | Lys129 | K129 | 0.904989 | 99.18 | No |
| 6 | **Thr219** | **T219** | **0.903089** | **98.98** | **Yes** |
| 7 | Ser460 | S460 | 0.901755 | 98.78 | No |
| 8 | Pro33 | P33 | 0.899030 | 98.57 | No |
| 9 | Lys325 | K325 | 0.891857 | 98.37 | No |
| 10 | Arg32 | R32 | 0.891590 | 98.16 | No |

## SHP099-contacting residues mapped through Q06124 to 2SHP

Contacts were defined geometrically as polymer residues with a minimum heavy-atom distance of **≤4.0 Å** to ligand component **5OD (SHP099)** in 5EHR chain A.

| Rank in 2SHP A | UniProt Q06124 | 2SHP PDB | Residue | 5EHR SHP099 min. distance (Å) | PocketMiner score | Percentile | Top 10? |
|---:|---|---:|---|---:|---:|---:|:---:|
| 2 | T218 | 218 | Thr | 3.69 | 0.914970 | 99.80 | **Yes** |
| 3 | R111 | 111 | Arg | 3.14 | 0.914450 | 99.59 | **Yes** |
| 6 | T219 | 219 | Thr | 3.59 | 0.903089 | 98.98 | **Yes** |
| 29 | T253 | 253 | Thr | 3.30 | 0.858000 | 94.29 | No |
| 31 | K492 | 492 | Lys | 3.45 | 0.856215 | 93.88 | No |
| 38 | P491 | 491 | Pro | 3.45 | 0.849655 | 92.45 | No |
| 41 | L254 | 254 | Leu | 3.46 | 0.843834 | 91.84 | No |
| 45 | E110 | 110 | Glu | 3.47 | 0.837000 | 91.02 | No |
| 55 | T108 | 108 | Thr | 3.13 | 0.812907 | 88.98 | No |
| 61 | H114 | 114 | His | 3.75 | 0.793019 | 87.76 | No |
| 64 | F113 | 113 | Phe | 2.79 | 0.788521 | 87.14 | No |
| 66 | E250 | 250 | Glu | 3.10 | 0.778364 | 86.73 | No |
| 84 | E249 | 249 | Glu | 3.29 | 0.742998 | 83.06 | No |
| 112 | Q495 | 495 | Gln | 3.57 | 0.690155 | 77.35 | No |
| 170 | Q257 | 257 | Gln | 3.58 | 0.604418 | 65.51 | No |

## Interpretation

The SHP099 interface is enriched in PocketMiner-high-scoring residues in autoinhibited 2SHP. In particular, **Thr218, Arg111, and Thr219 are among the ten highest-scoring residues**, with Thr218 ranked second overall. Only Gln257 falls outside the top quartile.

These are PocketMiner cryptic-pocket propensity scores for the **unliganded autoinhibited 2SHP chain A**; they are not binding-affinity predictions for SHP099.

### Mapping and run details

- 5EHR and 2SHP PDB DBREF records and RCSB’s SIFTS-provenance alignment map the respective chain-A residue ranges 1–525 one-to-one to UniProt Q06124 residues 1–525.
- All 15 SHP099 contacts are resolved in 2SHP chain A.
- A BioLiP UniProt-position column was offset relative to the primary PDB/RCSB/SIFTS records, so the primary entry mappings were used.
- PocketMiner was run after extracting chain A alone: 491 resolved residues, runtime approximately 7.5 seconds.
- Percentiles are empirical chain-A percentiles, with the highest score assigned 100 and the lowest 0.

**Completed plan**
1. [✓] Retrieved 2SHP and verified chain-A mapping to Q06124.
2. [✗] Initial residue-mapping attempt failed due to a missing Python import.
3. [✗] SIFTS download route returned HTML rather than the expected archive.
4. [✓] Completed mapping using PDB DBREF, RCSB/SIFTS alignment, and observed-sequence alignment.
5. [✓] Ran PocketMiner on full 2SHP and extracted provisional chain-A scores.
6. [✓] Performed the provisional SHP099-site comparison.
7. [✓] Extracted chain A and reran PocketMiner strictly on chain A alone.
8. [✓] Recomputed the final rankings using the chain-A-only scores.
9. [✓] Reported the residue-level results and direct conclusion.
=== END RUN rwxrv7yxb85 ===

=== RUN r9u7lhi674p ===
QUESTION:
Remove all ligands from PDB entry 1OPK (ABL1, UniProt P00519) and run pocket detection. What is the rank of the pocket that covers the myristoyl site?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P05_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[P05_b] [critical] [scripted] [{"rank": 1, "residues": 23}, {"rank": 2, "residues": 23}, {"rank": 3, "residues": 17}]
[P05_c] [critical] [judged] the rank of the pocket that covers the myristoyl site (the MYR contacts) is reported
[P05_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P05_e] [critical] [judged] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 3, "overlap_of_the_covering_pocket": 8, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 8], "pockets": [{"rank": 1, "score": 0.338, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.32, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.211, "n_residues": 17, "site_residues_in_pocket": 8}, {"rank": 4, "score": 0.121, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.112, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.111, "n_residues": 18, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.097, "n_residues": 32, "site_residues_in_pocket": 0}, {"rank": 8, "score": 0.09, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 9, "score": 0.049, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.044, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.038, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 12, "score": 0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.023, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.022, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.011, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.009, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 17, "score": -0.004, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 18, "score": -0.004, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 19, "score": -0.01, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 20, "score": -0.017, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 21, "score": -0.018, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 22, "score": -0.02, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 23, "score": -0.033, "n_residues": 10, "site_residues_in_pocket": 1}, {"rank": 24, "score": -0.036, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 25, "score": -0.037, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 26, "score": -0.045, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 27, "score": -0.047, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 28, "score": -0.06, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 29, "score": -0.085, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 30, "score": -0.09, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 31, "score": -0.103, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 32, "score": -0.131, "n_residues": 7, "site_residues_in_pocket": 2}, {"rank": 33, "score": -0.137, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 34, "score": -0.158, "n_residues": 17, "site_residues_in_pocket": 0}]}
[P05_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 23.77, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 11.32, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 10.44, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 4, "score": 9.99, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 5, "score": 4.5, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 6, "score": 2.04, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 7, "score": 1.74, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 8, "score": 1.24, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 9, "score": 1.09, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.46, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P05_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The pocket covering the myristoyl site is rank 2 — the second-highest-ranked P2Rank pocket.**

Validation:
- P2Rank pocket 2 score: **11.32**; probability: **0.606**
- Nearest original `MYR` atom to pocket 2 center: **0.87 Å**
- Nearest `MYR` atom to the pocket-2 surface: **3.47 Å**
- Pocket 2 contains **10/10** of the closest protein residues surrounding myristate and **18/20** of the next-nearest residues.
- As a positive control, the removed `P16` inhibitor maps to **pocket 1**, while myristate maps specifically to **pocket 2**.

Technical note: the deposited 1OPK polymer is annotated as mouse ABL1 (UniProt P00520), although the query specifies human ABL1 P00519; this does not affect the pocket assignment for the requested deposited entry.
=== END RUN r9u7lhi674p ===

=== RUN rklsyav8zky ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Shortest residue-contact path

**MET210 → THR206**

**Path length: 1 residue-contact edge** (two residue nodes)

Supporting geometry:

- **MET210** contacts the allosteric activator **MRK**: 3.664 Å.
- **THR206** contacts **glucose (GLC)**: 4.114 Å.
- MET210 and THR206 directly contact one another: MET210 `N`–THR206 `O` = **2.854 Å**, providing the single graph edge.

PDB 1V4S and UniProt P35557 numbering agree for these residues. The result was obtained for chain A using a minimum heavy-atom contact cutoff of 4.5 Å and confirmed by independently searching all activator-contact/glucose-contact endpoint pairs.
=== END RUN rklsyav8zky ===

=== RUN r5z28lksk6n ===
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
## AKT1 P31749 E17K summary

| Requested item | Result |
|---|---|
| **Variant** | AKT1 c.49G>A, p.Glu17Lys (E17K); ClinVar **VCV000013983** |
| **ClinVar classification** | **Pathogenic** — “criteria provided, multiple submitters, no conflicts” |
| **ClinVar oncogenicity classification** | **Oncogenic** |
| **AlphaMissense score** | **0.9977**; the GRCh38 canonical-transcript row is classified as **likely_pathogenic** |
| **Domain containing residue 17** | **PH (pleckstrin homology) domain**, UniProt residues **5–108** |
| **PDB 3O96** | **Glu17 is modeled** in chain A |
| **Distance to allosteric inhibitor** | **5.704 Å**, minimum heavy-atom distance between Glu17 and inhibitor ligand **IQO** |

### PDB distance detail

PDB 3O96 is titled *“Crystal Structure of Human AKT1 with an Allosteric Inhibitor”* and contains P31749 plus the allosteric inhibitor **IQO**. The closest deposited heavy-atom pair is:

- **Glu17 CG → IQO C6: 5.704 Å**
- Minimum backbone-to-ligand distance: **7.836 Å**
- Residue-centroid-to-ligand-centroid distance: **15.627 Å**

The reported **5.704 Å** is the standard minimum interatomic heavy-atom separation, not a van der Waals surface-to-surface distance. It was reproduced independently from both the mmCIF and PDB coordinate formats.

### Sources

- [ClinVar VCV000013983 / Variation 13983](https://www.ncbi.nlm.nih.gov/clinvar/variation/13983/)
- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry)
- [InterPro P31749](https://www.ebi.ac.uk/interpro/protein/UniProt/P31749/)
- [AlphaMissense GRCh38 release](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz) — row: `chr14  104780214  C  T  P31749  ENST00000554848.5  E17K  0.9977  likely_pathogenic`
- [AlphaMissense residue-substitution release](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz) — independently confirms `P31749 E17K 0.9977`
- [AlphaMissense paper](https://doi.org/10.1126/science.adg7492)
- [RCSB PDB 3O96](https://www.rcsb.org/structure/3O96)
- [3O96 structural paper](https://doi.org/10.1371/journal.pone.0012913)

### Completed plan

1. [✗] Initial broad web search failed because the specialist search agent required an unavailable Claude backend; replaced it with direct official database queries.
2. [✓] ClinVar identity and classifications verified.
3. [✓] AlphaMissense score retrieved and independently cross-checked: **0.9977**.
4. [✓] Residue-17 domain identified as the **PH domain, residues 5–108**.
5. [✓] PDB 3O96 residue and inhibitor coordinates inspected; **5.704 Å** minimum heavy-atom distance calculated.
6. [✓] Identifiers, coordinate calculation, and source records cross-checked.
=== END RUN r5z28lksk6n ===

=== RUN ra9ln5yq6sw ===
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
## Updated plan
1. [✓] Downloaded and inspected PDB entries 1BTL and 1PZO; confirmed chain A and UniProt P62593 mapping.
2. [✓] Identified CBT as the sole non-water ligand/allosteric inhibitor in 1PZO and calculated its contacts.
3. [✓] Ran PocketMiner on 1BTL and retained residue-level scores.
4. [✗] Initial score join failed because linear interpolation of UniProt mapping endpoints did not account for residue-level numbering shifts.
5. [✓] Established an exact 1PZO-to-1BTL mapping by globally aligning both 263-residue chain-A coordinate sequences and rejoined the contact and PocketMiner scores.
6. [✓] Compiled the top-ten residues and all mapped inhibitor-contact scores.

## Mapping and methods

- **1BTL and 1PZO structures:** chain A, mapped to **UniProt P62593**.
- **Allosteric inhibitor:** **CBT**, described in the 1PZO title as a “novel, core-disrupting, allosteric inhibitor.” Two CBT instances are present in chain A and were included in the contact calculation.
- **Contact criterion:** minimum heavy-atom distance ≤ **4.0 Å**, yielding **18 unique contacting residues**.
- **Cross-entry mapping:** both chain-A coordinate sequences contain 263 residues and align 1:1 by author PDB residue number. The only substitutions are at positions 84, 182, and 184, none of which is an inhibitor-contact residue. Thus every reported 1PZO contact maps unambiguously to the same-numbered 1BTL residue.
- **PocketMiner:** run on the unmodified **1BTL** structure, scoring all 263 residues. Scores below are rounded to six decimals.

## Ten highest-scoring 1BTL residues

| Rank | 1BTL residue | PocketMiner score |
|---:|---|---:|
| 1 | **A234 Lys (K)** | **0.951411** |
| 2 | **A246 Ile (I)** | **0.942519** |
| 3 | **A172 Ala (A)** | **0.941106** |
| 4 | **A244 Arg (R)** | **0.928997** |
| 5 | **A264 Tyr (Y)** | **0.926471** |
| 6 | **A217 Ala (A)** | **0.920834** |
| 7 | **A235 Ser (S)** | **0.917947** |
| 8 | **A220 Leu (L)** | **0.916830** |
| 9 | **A266 Thr (T)** | **0.905837** |
| 10 | **A66 Phe (F)** | **0.905050** |

## CBT-contacting 1PZO residues mapped to 1BTL

Because the validated mapping is residue-for-residue, the 1PZO and 1BTL author numbers are identical for these contacts.

| 1PZO residue | Mapped 1BTL residue | Minimum distance (Å) | 1BTL PocketMiner score | Overall 1BTL rank |
|---|---|---:|---:|---:|
| A246 Ile | A246 Ile | 3.39 | **0.942519** | 2 |
| A244 Arg | A244 Arg | 3.36 | **0.928997** | 4 |
| A217 Ala | A217 Ala | 3.91 | **0.920834** | 6 |
| A235 Ser | A235 Ser | 2.60 | **0.917947** | 7 |
| A220 Leu | A220 Leu | 3.35 | **0.916830** | 8 |
| A237 Ala | A237 Ala | 3.56 | **0.892082** | 14 |
| A216 Val | A216 Val | 3.76 | **0.875088** | 17 |
| A276 Asn | A276 Asn | 3.07 | **0.869319** | 18 |
| A245 Gly | A245 Gly | 3.18 | **0.843503** | 27 |
| A236 Gly | A236 Gly | 3.69 | **0.826309** | 31 |
| A221 Leu | A221 Leu | 3.35 | **0.786650** | 46 |
| A263 Ile | A263 Ile | 3.79 | **0.779656** | 51 |
| A279 Ile | A279 Ile | 3.56 | **0.773986** | 52 |
| A280 Ala | A280 Ala | 3.42 | **0.491368** | 126 |
| A261 Val | A261 Val | 4.00 | **0.387245** | 168 |
| A286 Leu | A286 Leu | 3.94 | **0.381120** | 171 |
| A224 Ala | A224 Ala | 3.41 | **0.246091** | 209 |
| A283 Gly | A283 Gly | 3.67 | **0.241886** | 210 |

Five of the inhibitor-contact residues—**A246, A244, A217, A235, and A220**—are also among the ten highest-scoring 1BTL residues.

**Interpretation caveat:** PocketMiner scores describe structural cryptic-pocket propensity, while the 4.0 Å contacts describe geometric proximity. Neither score nor contact alone establishes binding affinity, interaction energetics, or biological importance.
=== END RUN ra9ln5yq6sw ===

# Judge batch 006 of 8

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

=== RUN rnfrn080kom ===
QUESTION:
For the myristoyl-site ligand of PDB 5MO4 (the allosteric inhibitor of ABL1), report its ChEMBL identifier and its PubChem identifier, the residues BioLiP curates as its binding site in 5MO4 chain A, and the lowest IC50 recorded against ABL1 (CHEMBL1862) in the pinned ChEMBL 37 release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X09_a] [critical] [scripted] CHEMBL4208229
[X09_b] [critical] [scripted] 72165228
[X09_c] [critical] [scripted] {"residues": [359, 360, 451, 452, 453, 481, 483, 484, 487, 521, 525]}
[X09_d] [critical] [scripted] 0.5
[X09_e] [critical] [scripted] 2

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
The myristoyl-site ligand in **PDB 5MO4** is **asciminib**, represented by chemical component **AY7** in BioLiP. The other BioLiP ligand, NIL, occupies the catalytic/ATP-site record.

- **ChEMBL identifier:** CHEMBL4208229
- **PubChem identifier:** CID 72165228
- **BioLiP binding-site residues in 5MO4 chain A (PDB numbering):**  
  **L359, L360, I451, A452, T453, E481, C483, P484, V487, I521, V525**
- Equivalent UniProt P00519 numbering in the BioLiP record: L275, L276, I349, A350, T351, E379, C381, P382, V385, I419, V423

In the pinned local **ChEMBL 37** release, asciminib has two recorded IC50 values against **ABL1 (CHEMBL1862)**:

- **0.5 nM** — lowest value; ChEMBL activity ID **18557369**, assay **CHEMBL4200739**
- 16.0 nM — ChEMBL activity ID 29002802, assay CHEMBL5739300

**Reported lowest IC50: 0.5 nM.**

Provenance: BioLiP interaction records for PDB 5MO4 chain A; ChEMBL/PubChem cross-reference; and the pinned local ChEMBL 37 SQLite database at `/data/chembl/chembl_37_sqlite/chembl_37.db`.
=== END RUN rnfrn080kom ===

=== RUN rjvpygbzs82 ===
QUESTION:
In the Allosteric Set Database release 202306, the allosteric-protein table (AP) lists the curated allosteric sites: how many site records and how many distinct PDB entries does it hold for human ABL1 (P00519)? In the same release's hit-and-lead table (HL), how many modulator records are curated for ABL1, and what activity type and what modulator feature do those records carry?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X01_a] [critical] [scripted] 225
[X01_b] [critical] [scripted] 59
[X01_c] [critical] [scripted] 84
[X01_d] [critical] [scripted] IC50
[X01_e] [critical] [scripted] Inhibitor

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Answer**

- **AP — curated allosteric sites for human ABL1 (P00519):**
  - **4 site records**
  - **4 distinct PDB entries:** `1OPL`, `3PYY`, `5DC4`, and `5MO4`
  - The target identifier is `ASD03320000_1`.

- **HL — hit-and-lead modulators for ABL1 (P00519):**
  - **84 modulator records**
  - **Activity_Type:** `IC50` for all 84 records
  - **Modulator_Feature:** `Inhibitor` for all 84 records

These results were calculated from the official **ASD Release 5.01 / 202306** files dated June 1, 2023, namely `ASD_Release_202306_XF.tar.gz` and `ASD_Release_202306_HL.tar.gz`.

A counting nuance: the ABL1 XML includes an `allosteric__site__count` value of **3**, but the raw site-record list contains **4** records. The 5DC4 monobody/protein–protein-interaction record has no residue-level `Allosteric_Site_Residue` annotation, which explains the lower summary counter. Thus, for records held by the table, the requested counts are **4 records and 4 PDB entries**.
=== END RUN rjvpygbzs82 ===

=== RUN ry19ou91v36 ===
QUESTION:
For the myristoyl-site ligand of PDB 5MO4 (the allosteric inhibitor of ABL1), report its ChEMBL identifier and its PubChem identifier, the residues BioLiP curates as its binding site in 5MO4 chain A, and the lowest IC50 recorded against ABL1 (CHEMBL1862) in the pinned ChEMBL 37 release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X09_a] [critical] [scripted] CHEMBL4208229
[X09_b] [critical] [scripted] 72165228
[X09_c] [critical] [scripted] {"residues": [359, 360, 451, 452, 453, 481, 483, 484, 487, 521, 525]}
[X09_d] [critical] [scripted] 0.5
[X09_e] [critical] [scripted] 2

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PDB 5MO4 myristoyl-site ligand

**Ligand:** AY7 / **asciminib** (ABL001)  
**Standard InChIKey:** `VOVZXURTCKPRDQ-CQSZACIVSA-N`

- **ChEMBL identifier:** `CHEMBL4208229`
- **PubChem identifier:** CID `72165228`

### BioLiP binding-site residues

For **PDB 5MO4, chain A**, BioLiP site **BS02** lists these PDB-numbered residues:

**Leu359, Leu360, Ile451, Ala452, Thr453, Glu481, Cys483, Pro484, Val487, Ile521, Val525**

Corresponding UniProt-numbered residues in BioLiP are:

**Leu275, Leu276, Ile349, Ala350, Thr351, Glu379, Cys381, Pro382, Val385, Ile419, Val423**

### Lowest recorded IC50

Against **ABL1 (`CHEMBL1862`)** in the pinned **ChEMBL 37** release:

- **Lowest standardized IC50:** **0.5 nM**
- **Relation:** `=`
- **Activity ID:** `18557369`
- **Assay ID:** `CHEMBL4200739`
- **Confidence score:** `9`

The pinned query returned two IC50 records, **0.5 nM** and **16 nM**; therefore, **0.5 nM** is the lowest.

### Completed plan
1. [✓] Identified AY7 as the myristoyl-site ligand in PDB 5MO4 using BioLiP
2. [✓] Retrieved BioLiP’s chain-A binding-site residues
3. [✓] Reconciled AY7 with asciminib and obtained the ChEMBL and PubChem identifiers
4. [✓] Queried the pinned ChEMBL 37 database and calculated the minimum IC50
5. [✓] Reconciled identifiers, units, records, and provenance
=== END RUN ry19ou91v36 ===

=== RUN r6nv5g16tnm ===
QUESTION:
For the apo structure of PDB 2LAO chain A, which ten residues does the PocketMiner model score highest for cryptic-pocket propensity, what is the score of the highest-ranked residue, and how many of the published cryptic-pocket residues of that structure fall among those ten? Name the overlapping residues.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X05_a] [critical] [scripted] {"residues": [163, 14, 230, 90, 70, 235, 180, 233, 231, 191]}
[X05_b] [critical] [scripted] 0.93533
[X05_c] [critical] [scripted] 2
[X05_d] [critical] [scripted] {"residues": [14, 70]}
[X05_e] [critical] [scripted] 15

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Completed plan
1. [✓] Located the PocketMiner model and official 2LAO apo structure; verified that PDB 2LAO contains chain A with 238 residues and only crystallographic waters.
2. [✓] Ran the validated `[TOOL]` workflow and ranked all 238 residues.
3. [✓] Retrieved the published 2LAO annotation: 15 cryptic ligand-lining residues, with 2LAO in the published test set.
4. [✓] Intersected the published residues with the PocketMiner top ten.
5. [✓] Cross-checked the result using both the RCSB structure and the authors’ cleaned apo structure; both gave identical scores.

### PocketMiner top ten for 2LAO chain A

| Rank | Residue | Score |
|---:|---|---:|
| 1 | **VAL163** | **0.935330331326** |
| 2 | TYR14 | 0.919266402721 |
| 3 | TYR230 | 0.902997016907 |
| 4 | ALA90 | 0.902110517025 |
| 5 | SER70 | 0.899701297283 |
| 6 | VAL235 | 0.896404206753 |
| 7 | PHE180 | 0.894195377827 |
| 8 | PHE233 | 0.893886208534 |
| 9 | PHE231 | 0.893085300922 |
| 10 | PHE191 | 0.884182572365 |

The **highest-ranked residue is VAL163**, with a PocketMiner score of **0.935330331325531** (approximately **0.93533**).

### Overlap with the published cryptic-pocket residues

The published annotation contains 15 residues. **Two** of them occur among the PocketMiner top ten:

- **TYR14** — score 0.919266402721
- **SER70** — score 0.899701297283

Thus, the answer is **2 overlapping residues: TYR14 and SER70**.

**Provenance:** The official PocketMiner test label dictionary identifies `2lao` as a 238-residue test structure with 15 positive cryptic-pocket annotations. The supplementary structure table pairs apo 2LAO chain A with holo 1LAH chain E (ORN) and likewise reports 15 cryptic ligand-lining residues. The model run used PocketMiner commit `187062df3c94127e991669768009141a08fd5d8b` with weights SHA-256 `6f5ab62b9fb38b54040053ac321f3362d616bae9b31569249a032dbb50890b70`.

**Reference:** Meller A, et al. “Predicting locations of cryptic pockets from single protein structures using the PocketMiner graph neural network.” *Nature Communications* (2023). DOI: [10.1038/s41467-023-36699-3](https://doi.org/10.1038/s41467-023-36699-3); PMID: 36859488.
=== END RUN r6nv5g16tnm ===

=== RUN rio7urdg1oo ===
QUESTION:
In the pinned ClinVar release, list the pathogenic or likely pathogenic missense variants of human PTPN11 (Q06124) whose AlphaMissense score is above 0.9 and whose residue has a heavy atom within 8 A of any heavy atom of the SHP099 ligand in PDB 5EHR chain A. Give, for each, the variant, its ClinVar variation id, its AlphaMissense score and the nearest heavy-atom distance. The pinned release and the live service differ in how they classify a record, so answer from the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X06_a] [critical] [scripted] 7
[X06_b] [critical] [scripted] {"residues": [110, 491, 498]}
[X06_c] [critical] [scripted] {"E110K": 0.9908, "E110A": 0.9621, "P491H": 0.9611, "P491L": 0.9431, "R498Q": 0.9993, "R498W": 0.9998, "R498L": 0.9995}
[X06_d] [critical] [scripted] {"110": 3.465, "491": 3.454, "498": 7.154}
[X06_e] [critical] [scripted] {"variation_ids": [40507, 40508, 40551, 40552, 1805026, 40553, 40554], "allele_ids": [48977, 48978, 49021, 49022, 1862041, 49023, 49024]}
[X06_f] [critical] [judged] the answer states, for every variant it lists, the nearest heavy-atom distance from the variant residue to the SHP099 ligand in 5EHR chain A, and that every residue it lists lies within 8 A of it

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Completed plan
1. [✓] Locate the pinned ClinVar and AlphaMissense releases and checksums.
2. [✓] Extract non-conflicting pathogenic/likely-pathogenic PTPN11 missense variants from the pinned ClinVar release.
3. [✓] Join the pinned AlphaMissense scores and apply the score >0.9 filter.
4. [✓] Identify SHP099 as ligand `5OD` in PDB 5EHR chain A.
5. [✓] Calculate nearest heavy-atom distances using the deposited 5EHR coordinates.
6. [✓] Verify Q06124/PDB residue-number correspondence and the 8 Å cutoff.
7. [✓] Validate the final seven-row result.

### Result

Using the **pinned** ClinVar release—not the live service—there are **seven** qualifying variants:

| Variant | One-letter | ClinVar Variation ID | AlphaMissense score | Nearest heavy-atom distance to chain-A SHP099 (Å) | Closest atom pair |
|---|---:|---:|---:|---:|---|
| p.Glu110Lys | E110K | 40507 | 0.9908 | 3.465 | Glu110 O–5OD N22 |
| p.Glu110Ala | E110A | 40508 | 0.9621 | 3.465 | Glu110 O–5OD N22 |
| p.Pro491His | P491H | 40551 | 0.9611 | 3.454 | Pro491 CB–5OD N7 |
| p.Pro491Leu | P491L | 40552 | 0.9431 | 3.454 | Pro491 CB–5OD N7 |
| p.Arg498Gln | R498Q | 1805026 | 0.9993 | 7.154 | Arg498 NH1–5OD CL2 |
| p.Arg498Trp | R498W | 40553 | 0.9998 | 7.154 | Arg498 NH1–5OD CL2 |
| p.Arg498Leu | R498L | 40554 | 0.9995 | 7.154 | Arg498 NH1–5OD CL2 |

### Method and provenance

- **ClinVar:** pinned `variant_summary.txt.gz`, SHA-256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`.
- **AlphaMissense:** pinned `AlphaMissense_aa_substitutions.tsv.gz`, SHA-256 `bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d`.
- Records with the pinned aggregate classification **“Conflicting classifications of pathogenicity”** were excluded rather than treated as pathogenic or likely pathogenic.
- Distances are the minimum Euclidean distances between any heavy atom of the reference residue and any of the 23 heavy atoms of the chain-A SHP099 (`5OD`, residue 601) in **PDB 5EHR**.
- Chain-A PDB numbering matches UniProt **Q06124** numbering for these residues. Every listed residue is strictly within **8 Å**.
=== END RUN rio7urdg1oo ===

=== RUN re8ovlczjxe ===
QUESTION:
In the Allosteric Set Database release 202306, the hit-and-lead table (HL) lists the curated modulators: how many modulator records does it hold for human glucokinase (P35557), how many distinct modulator names do they carry, which activity types do they use and how many records use each type?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X02_a] [critical] [scripted] 171
[X02_b] [critical] [scripted] 170
[X02_c] [critical] [scripted] {"IC50": "IC50", "EC50": "EC50"}
[X02_d] [critical] [scripted] 170
[X02_e] [critical] [scripted] 1

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
For human glucokinase (UniProt **P35557**) in `ASD_Release_202306_HL.csv`:

| Measure | Count |
|---|---:|
| Total modulator records | **171** |
| Distinct modulator names | **170** |
| Records with activity type **EC50** | **170** |
| Records with activity type **IC50** | **1** |

Thus, the activity types are **EC50** and **IC50**, and their counts reconcile exactly to the total: **170 + 1 = 171 records**. The 171 records carry 170 distinct names, indicating one repeated name across two records.
=== END RUN re8ovlczjxe ===

=== RUN r0mvt6mp6vv ===
QUESTION:
In the pinned ChEMBL 37 release, compare sotorasib and adagrasib against the KRAS target CHEMBL2189121: how many IC50 records does each have, what is the median IC50 of each, and what are the smallest and the largest IC50 recorded for sotorasib? The live ChEMBL service serves a later release, so report the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X07_a] [critical] [scripted] 8
[X07_b] [critical] [scripted] 49.0
[X07_c] [critical] [scripted] 7
[X07_d] [critical] [scripted] 10.0
[X07_e] [critical] [scripted] 7.0
[X07_f] [critical] [scripted] 10000.0

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## ChEMBL 37 (pinned local release) — KRAS target CHEMBL2189121, standard_type = IC50

**Release provenance:** all numbers below come from the pinned local SQLite snapshot `/data/chembl/chembl_37_sqlite/chembl_37.db` (source string returned by the tool: `local:chembl_37`, release_date 2026-10-22; MANIFEST points to `.../releases/chembl_37/chembl_37_sqlite.tar.gz`). Queries were run with `mode="local"` so the live ChEMBL web service (later release) was never touched. Returned row counts equal the DB-reported `total_count` for both compounds, so no records were truncated.

| Compound | ChEMBL ID | # IC50 records | Median IC50 | Smallest IC50 | Largest IC50 |
|---|---|---|---|---|---|
| Sotorasib | CHEMBL4535757 | **8** | **49.0 nM** | **7.0 nM** | **10,000 nM** |
| Adagrasib | CHEMBL4594350 | **7** | **10.0 nM** | 5.0 nM | 133.0 nM |

All recorded values are in **nM** (single unit across both sets).

### Requested sotorasib range
- **Smallest IC50: 7.0 nM** (activity_id 25512445, assay CHEMBL5335102, relation `<`)
- **Largest IC50: 10,000 nM** (activity_id 22915790, assay CHEMBL4735449, relation `>`)

### Full underlying values
- **Sotorasib (8, sorted):** 7.0, 9.66, 24.5, 30.0, 68.0, 7500.0, 7500.0, 10000.0 nM → median 49.0 nM
- **Adagrasib (7, sorted):** 5.0, 5.0, 5.0, 10.0, 10.0, 14.0, 133.0 nM → median 10.0 nM

### Interpretation caveats
- Three sotorasib records are censored (non-`=` relations): 7.0 nM (`<`), 7500.0 nM (`>`), 10000.0 nM (`>`). One adagrasib record is censored: 5.0 nM (`<`). Medians above use the stored values as recorded for all rows.
- Sensitivity check using only exact (`=`) measurements: sotorasib median = **30.0 nM** (9.66, 24.5, 30.0, 68.0, 7500.0); adagrasib median remains **10.0 nM**. The large sotorasib values (7,500–10,000 nM) come from resistance/alternate-assay contexts and are what stretch its all-record median to 49 nM.
- These are assay-dependent biochemical/cellular IC50 values against the KRAS target entity; they are not clinical potency measures and should not be read as head-to-head efficacy comparisons.

**Artifacts saved:** `/agent_cwd/outputs/chembl37_kras_ic50_records.json` (full record sets with activity/assay IDs) and `/agent_cwd/outputs/chembl37_kras_ic50_summary.json` / `.csv`.
=== END RUN r0mvt6mp6vv ===

=== RUN rutc5g0c079 ===
QUESTION:
In the Allosteric Set Database release 202306, the hit-and-lead table (HL) lists the curated modulators: how many modulator records does it hold for human glucokinase (P35557), how many distinct modulator names do they carry, which activity types do they use and how many records use each type?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X02_a] [critical] [scripted] 171
[X02_b] [critical] [scripted] 170
[X02_c] [critical] [scripted] {"IC50": "IC50", "EC50": "EC50"}
[X02_d] [critical] [scripted] 170
[X02_e] [critical] [scripted] 1

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Result

For **human glucokinase (GCK; UniProt P35557)** in `ASD_Release_202306_HL.csv`:

- **Modulator records:** **171**
- **Distinct modulator names:** **170**
- **Activity types:**
  - **EC50:** **170 records**
  - **IC50:** **1 record**

The difference between 171 records and 170 distinct names is one modulator, **`2-amino-5-chloro-N-(thiazol-2-yl)benzamide`** (`ASD01200034`), which appears in two records: one EC50 and one IC50, both at 11 μM.

The counts were independently reproduced with both pandas and Python’s standard-library CSV parser. All 170 distinct HL modulator IDs were also found in the independently retrieved curated ASD XF record for P35557.

### Completed plan

1. [✓] Locate the ASD release-202306 hit-and-lead (HL) table in the local data lake
2. [✓] Inspect the HL schema and determine how P35557 and activity types are encoded
3. [✓] Filter the HL table for human glucokinase (P35557) and calculate all requested counts
4. [✓] Cross-check the result against an independent ASD lookup and report the evidence
=== END RUN rutc5g0c079 ===

=== RUN rw2vlfpkwse ===
QUESTION:
For the myristoyl-site ligand of PDB 5MO4 (the allosteric inhibitor of ABL1), report its ChEMBL identifier and its PubChem identifier, the residues BioLiP curates as its binding site in 5MO4 chain A, and the lowest IC50 recorded against ABL1 (CHEMBL1862) in the pinned ChEMBL 37 release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X09_a] [critical] [scripted] CHEMBL4208229
[X09_b] [critical] [scripted] 72165228
[X09_c] [critical] [scripted] {"residues": [359, 360, 451, 452, 453, 481, 483, 484, 487, 521, 525]}
[X09_d] [critical] [scripted] 0.5
[X09_e] [critical] [scripted] 2

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

| Item | Value |
|---|---|
| **Myristoyl-site ligand** | **Asciminib** (ABL001/NVP-ABL001), PDB component **AY7** |
| **ChEMBL identifier** | **CHEMBL4208229** |
| **PubChem identifier** | **CID 72165228** |
| **Structure cross-check** | InChIKey `VOVZXURTCKPRDQ-CQSZACIVSA-N` in both ChEMBL and PubChem |
| **BioLiP binding site, 5MO4 chain A** | **Leu359, Leu360, Ile451, Ala452, Thr453, Glu481, Cys483, Pro484, Val487, Ile521, Val525** |
| **Lowest ABL1 IC50 in ChEMBL 37** | **0.5 nM** (`=`) |

### Numbering clarification

BioLiP reports the residues above using the deposited **PDB/author numbering**. Its alternate sequence-renumbered representation is:

`Leu275, Leu276, Ile349, Ala350, Thr351, Glu379, Cys381, Pro382, Val385, Ile419, Val423`

The corresponding UniProt P00519 positions are:

`Leu340, Leu341, Ile432, Ala433, Thr434, Glu462, Cys464, Pro465, Val468, Ile502, Val506`

### ChEMBL 37 activity check

Filtering ChEMBL release 37 for:

- molecule: `CHEMBL4208229`
- target: `CHEMBL1862` — Tyrosine-protein kinase ABL1
- standard type: `IC50`

returned two records:

- **0.5 nM**, relation `=`, pChEMBL **9.30** — activity `CHEMBL activity 18557369`
- 16 nM, relation `=`, pChEMBL 7.80

Therefore, the **lowest recorded IC50 is 0.5 nM**. The winning record comes from assay `CHEMBL4200739` and the 2018 discovery paper by Schoepfer et al., DOI **10.1021/acs.jmedchem.8b01040**, PMID **30137981**.

### Sources

- [RCSB PDB 5MO4](https://www.rcsb.org/structure/5MO4)
- [RCSB ligand AY7](https://www.rcsb.org/ligand/AY7)
- [ChEMBL molecule CHEMBL4208229](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL4208229)
- [PubChem CID 72165228](https://pubchem.ncbi.nlm.nih.gov/compound/72165228)
- [ChEMBL target CHEMBL1862](https://www.ebi.ac.uk/chembl/explore/target/CHEMBL1862)
- [Winning ChEMBL activity record](https://www.ebi.ac.uk/chembl/api/data/activity/18557369)
- [BioLiP2 curation repository](https://github.com/kad-ecoli/mmCIF2BioLiP)

The BioLiP live host was unavailable during the query, so its interaction row was reproduced with the public BioLiP2 curation code against the deposited 5MO4 mmCIF and checked atom-for-atom against the official PDB coordinates.
=== END RUN rw2vlfpkwse ===

=== RUN rcknx5p3h5o ===
QUESTION:
In the pinned ClinVar release, list the pathogenic or likely pathogenic missense variants of human PTPN11 (Q06124) whose AlphaMissense score is above 0.9 and whose residue has a heavy atom within 8 A of any heavy atom of the SHP099 ligand in PDB 5EHR chain A. Give, for each, the variant, its ClinVar variation id, its AlphaMissense score and the nearest heavy-atom distance. The pinned release and the live service differ in how they classify a record, so answer from the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X06_a] [critical] [scripted] 7
[X06_b] [critical] [scripted] {"residues": [110, 491, 498]}
[X06_c] [critical] [scripted] {"E110K": 0.9908, "E110A": 0.9621, "P491H": 0.9611, "P491L": 0.9431, "R498Q": 0.9993, "R498W": 0.9998, "R498L": 0.9995}
[X06_d] [critical] [scripted] {"110": 3.465, "491": 3.454, "498": 7.154}
[X06_e] [critical] [scripted] {"variation_ids": [40507, 40508, 40551, 40552, 1805026, 40553, 40554], "allele_ids": [48977, 48978, 49021, 49022, 1862041, 49023, 49024]}
[X06_f] [critical] [judged] the answer states, for every variant it lists, the nearest heavy-atom distance from the variant residue to the SHP099 ligand in 5EHR chain A, and that every residue it lists lies within 8 A of it

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
Using the pinned ClinVar release identified by SHA-256 prefix `b235cd5742ac`—rather than live ClinVar classifications—and the pinned AlphaMissense table identified by SHA-256 prefix `bc18d954a9aa`, the qualifying variants are:

| Variant | ClinVar Variation ID | Pinned ClinVar classification | AlphaMissense score | Nearest heavy-atom distance (Å) |
|---|---:|---|---:|---:|
| NM_002834.5(PTPN11):c.328G>A (p.Glu110Lys) | **40507** | Pathogenic/Likely pathogenic | **0.9908** | **3.465** |
| NM_002834.5(PTPN11):c.329A>C (p.Glu110Ala) | **40508** | Pathogenic/Likely pathogenic | **0.9621** | **3.465** |
| NM_002834.5(PTPN11):c.1472C>A (p.Pro491His) | **40551** | Pathogenic/Likely pathogenic | **0.9611** | **3.454** |
| NM_002834.5(PTPN11):c.1472C>T (p.Pro491Leu) | **40552** | Pathogenic | **0.9431** | **3.454** |
| NM_002834.5(PTPN11):c.1493G>A (p.Arg498Gln) | **1805026** | Likely pathogenic | **0.9993** | **7.154** |
| NM_002834.5(PTPN11):c.1492C>T (p.Arg498Trp) | **40553** | Pathogenic/Likely pathogenic | **0.9998** | **7.154** |
| NM_002834.5(PTPN11):c.1493G>T (p.Arg498Leu) | **40554** | Pathogenic | **0.9995** | **7.154** |

Distances are minima over all heavy atoms of the variant residue and all heavy atoms of SHP099, represented as ligand component **5OD**, chain A, residue 601, in PDB **5EHR**. The nearest atom pairs were:

- Glu110: protein **O**–ligand **N22**, 3.465 Å  
- Pro491: protein **CB**–ligand **N7**, 3.454 Å  
- Arg498: protein **NH1**–ligand **CL2**, 7.154 Å  

The PDB and mmCIF coordinate calculations agreed. Live ClinVar labels were not used to determine inclusion.
=== END RUN rcknx5p3h5o ===

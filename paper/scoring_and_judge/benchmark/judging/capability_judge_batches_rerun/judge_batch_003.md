# Judge batch 003 of 8

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

=== RUN resm189h61i ===
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
## Result

Using the **pinned ClinVar release** (completed 2026-10-23; SHA-256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`) and the pinned AlphaMissense release, **seven** PTPN11 missense variants satisfy all criteria.

SHP099 is chemical component **5OD** in PDB **5EHR chain A**. Distance is the minimum Euclidean distance between any heavy atom of the listed PTPN11 residue and any heavy atom of 5OD.

| Variant | ClinVar Variation ID | Pinned ClinVar classification | AlphaMissense score | Nearest heavy-atom distance |
|---|---:|---|---:|---:|
| NM_002834.5(PTPN11):c.328G>A (p.Glu110Lys) | **40507** | Pathogenic/Likely pathogenic | **0.9908** | **3.47 Å** |
| NM_002834.5(PTPN11):c.329A>C (p.Glu110Ala) | **40508** | Pathogenic/Likely pathogenic | **0.9621** | **3.47 Å** |
| NM_002834.5(PTPN11):c.1472C>A (p.Pro491His) | **40551** | Pathogenic/Likely pathogenic | **0.9611** | **3.45 Å** |
| NM_002834.5(PTPN11):c.1472C>T (p.Pro491Leu) | **40552** | Pathogenic | **0.9431** | **3.45 Å** |
| NM_002834.5(PTPN11):c.1492C>T (p.Arg498Trp) | **40553** | Pathogenic/Likely pathogenic | **0.9998** | **7.15 Å** |
| NM_002834.5(PTPN11):c.1493G>T (p.Arg498Leu) | **40554** | Pathogenic | **0.9995** | **7.15 Å** |
| NM_002834.5(PTPN11):c.1493G>A (p.Arg498Gln) | **1805026** | Likely pathogenic | **0.9993** | **7.15 Å** |

### Validation notes

- ClinVar classifications above come directly from the compressed pinned release; no live ClinVar service was used.
- GRCh37 and GRCh38 copies were collapsed by Variation ID.
- Residues were mapped to canonical Q06124 numbering using the RCSB/SIFTS alignment.
- All scores are strictly greater than 0.9, and all distances are at or below 8 Å.
- Conflicting and uncertain-significance records were excluded even when their AlphaMissense scores exceeded 0.9.
- Distances were independently recomputed from the 5EHR mmCIF coordinates; agreement with the contact tool was within 0.005 Å.

### Completed plan

1. [✗] Direct validated-wrapper local call — timed out while re-hashing the large pinned file.
2. [✓] Queried the pinned sidecar indexes and verified the final records directly in the compressed pinned source files.
3. [✓] Retrieved pinned AlphaMissense scores for Q06124 and applied the strict >0.9 threshold.
4. [✓] Identified SHP099 as component 5OD and calculated its 8 Å heavy-atom contacts in 5EHR chain A.
5. [✓] Mapped contact residues to Q06124 numbering and joined variants, scores, distances, and Variation IDs.
6. [✓] Independently validated the source classifications, AlphaMissense values, and geometric distances.
=== END RUN resm189h61i ===

=== RUN re1ho6gs781 ===
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
In the **Allosteric Set Database release-202306 HL table**, human glucokinase **GCK / P35557** has:

- **171 row-level modulator records**
- **170 distinct modulator names**
- **170 distinct modulator IDs**
- Activity types:
  - **EC50:** 170 records
  - **IC50:** 1 record

The apparent extra record comes from **2-amino-5-chloro-N-(thiazol-2-yl)benzamide** (`Modulator_ID: ASD01200034`), which appears twice under the same name and ID: once as an `EC50` record and once as an `IC50` record. Thus, there are **171 records but 170 unique named modulators**.

Source: `/biolab_data/data_lake/ASD_Release_202306_HL.csv`  
SHA-256: `40bccd33113b7782323278a051e55127455548dd6dc8739f9f0033b58fa7b7fd`

The counts were independently reproduced using pandas, Python’s standard CSV parser, and shell `grep`.
=== END RUN re1ho6gs781 ===

=== RUN rlvlk2ycxvi ===
QUESTION:
In BioLiP, how many ligand binding entries are curated for human PTP1B (P18031)? How many of them are for a non-metal ligand, and how many carry a recorded binding affinity? For the ligand with the code INX, give its recorded affinity.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X03_a] [critical] [scripted] 409
[X03_b] [critical] [scripted] 400
[X03_c] [critical] [scripted] 92
[X03_d] [critical] [scripted] INX
[X03_e] [critical] [scripted] 0.25

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
BioLiP contains **409 ligand-binding entries** for human PTP1B (UniProt **P18031**).

| Quantity | Count |
|---|---:|
| Total ligand-binding entries | **409** |
| Entries for non-metal ligands | **400** |
| Entries with a recorded binding affinity | **92** |

For **INX**—found in PDB **1G7G**—the recorded affinity is **Ki = 0.25 µM** (`Ki=0.25uM`).

The non-metal count excludes entries whose ligand codes match the designated metal/ion list; for PTP1B, all 9 excluded entries are **Mg (MG)**. The affinity count uses BioLiP’s curated `Affinity_Processed` field. Source: `/biolab_data/biolip/biolip.pkl`, with the INX record independently checked via `[TOOL]`.

### Completed plan
1. [✗] Direct `[TOOL]` query (returned no BioLiP rows without PDB context)
2. [✓] Resolved P18031 to 441 mapped PDB entries
3. [✓] Queried and classified the complete BioLiP P18031 subset
4. [✓] Extracted and independently verified the INX affinity
5. [✓] Summarized the final counts and affinity
=== END RUN rlvlk2ycxvi ===

=== RUN rzffxzac6j7 ===
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
## Result

Using the official PocketMiner checkpoint on apo **PDB 2LAO, chain A**, the ten highest-scoring residues are:

| Rank | Residue | PocketMiner score |
|---:|---|---:|
| 1 | **VAL163** | **0.9353303313** |
| 2 | TYR14 | 0.9192664027 |
| 3 | TYR230 | 0.9029970765 |
| 4 | ALA90 | 0.9021105170 |
| 5 | SER70 | 0.8997011781 |
| 6 | VAL235 | 0.8964041471 |
| 7 | PHE180 | 0.8941954970 |
| 8 | PHE233 | 0.8938862085 |
| 9 | PHE231 | 0.8930854201 |
| 10 | PHE191 | 0.8841823936 |

- **Highest-ranked residue:** **VAL163**
- **Highest score:** **0.9353303313**, approximately **0.9353**
- **Published cryptic-pocket residues among the top ten:** **2**
- **Overlapping residues:** **TYR14** and **SER70**

The paper’s Supplementary Data 1 lists 15 published cryptic ligand-lining residues for 2LAO. Thresholding the reproduced predictions at 0.5 identifies 14 of those 15, reproducing the paper’s reported per-protein accuracy of **0.933**.

**Sources:** [Meller et al., Nature Communications (2023), PMID 36859488](https://doi.org/10.1038/s41467-023-36699-3); [RCSB PDB 2LAO](https://www.rcsb.org/structure/2LAO); [official PocketMiner repository](https://github.com/Mickdub/gvp/tree/187062df3c94127e991669768009141a08fd5d8b).
=== END RUN rzffxzac6j7 ===

=== RUN rz7rxttgsjv ===
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
## Result

The ten highest-scoring residues are:

| Rank | Residue | PocketMiner score |
|---:|---|---:|
| 1 | **VAL A163** | **0.935330331326** |
| 2 | TYR A14 | 0.919266402721 |
| 3 | TYR A230 | 0.902997016907 |
| 4 | ALA A90 | 0.902110517025 |
| 5 | SER A70 | 0.899701297283 |
| 6 | VAL A235 | 0.896404206753 |
| 7 | PHE A180 | 0.894195377827 |
| 8 | PHE A233 | 0.893886208534 |
| 9 | PHE A231 | 0.893085300922 |
| 10 | PHE A191 | 0.884182572365 |

- **Highest-ranked residue:** VAL A163  
- **Highest score:** **0.935330331326** (approximately 0.93533)

The published PocketMiner dataset lists 15 cryptic-pocket residues for 2LAO/A: D11, Y14, F52, S69, S70, L71, S72, R77, L117, G119, S120, T121, Q122, D161, and T195.

**Two of those published residues occur among the model’s top ten:**

- **TYR A14** — rank 2, score 0.919266402721
- **SER A70** — rank 5, score 0.899701297283

Thus, the overlap count is **2**, with overlapping residues **TYR14 and SER70**.

**Provenance:** PocketMiner commit `187062df3c94127e991669768009141a08fd5d8b`; model weights SHA-256 `6f5ab62b9fb38b54040053ac321f3362d616bae9b31569249a032dbb50890b70`. Published labels are from the PocketMiner dataset accompanying Meller et al., *Nature Communications* 14, 1177 (2023), DOI: https://doi.org/10.1038/s41467-023-36699-3; structure: https://www.rcsb.org/structure/2LAO.
=== END RUN rz7rxttgsjv ===

=== RUN rwgid3y0aj7 ===
QUESTION:
In the Allosteric Set Database release 202306, the allosteric-protein table (AP) lists the curated allosteric sites: how many site records and how many distinct PDB entries does it hold for human AKT1 (P31749)? For the 3O96 entry of that table: which chemical component is the bound ligand, which residues of chain A lie within 4 A of it, and which UniProt domain does each of those residues belong to?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X08_a] [critical] [scripted] 77
[X08_b] [critical] [scripted] 32
[X08_c] [critical] [scripted] IQO
[X08_d] [critical] [scripted] {"residues": [205, 292, 272, 296, 268, 290, 80, 84, 211, 264, 210, 83, 85, 273, 274, 271, 82, 291]}
[X08_e] [critical] [judged] the answer assigns every residue it lists to the UniProt PH domain (5-108), the protein kinase domain (150-408) or the AGC-kinase C-terminal region (409-480) of P31749, with the boundaries stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### AKT1 counts in ASD release 202306

For **AKT1_HUMAN / P31749**, the AP table contains:

- **77 site records** (AP rows)
- **31 distinct bona fide PDB entries**
- The raw `pdb_id` column contains **32 distinct identifiers**, because it also contains `P31749-F1`, an AlphaFold-model identifier rather than a four-character PDB ID.

### 3O96 bound ligand

The bound chemical component is:

- **PDB chemical component ID:** `IQO`
- **Name:** 1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one
- **Formula:** C34H29N7O

BioLiP records one IQO molecule in chain A.

### Chain-A residues within 4 Å of IQO

There are **18 polymer residues** at a minimum heavy-atom distance of ≤4.0 Å. For these residues, the chain-A PDB author number and canonical P31749 position coincide.

| Chain-A residue | P31749 residue | Minimum distance | UniProt domain |
|---|---:|---:|---|
| TRP80 | W80 | 3.41 Å | PH |
| THR82 | T82 | 3.95 Å | PH |
| VAL83 | V83 | 3.74 Å | PH |
| ILE84 | I84 | 3.46 Å | PH |
| GLU85 | E85 | 3.75 Å | PH |
| SER205 | S205 | 2.89 Å | Protein kinase |
| LEU210 | L210 | 3.66 Å | Protein kinase |
| THR211 | T211 | 3.58 Å | Protein kinase |
| LEU264 | L264 | 3.64 Å | Protein kinase |
| LYS268 | K268 | 3.26 Å | Protein kinase |
| VAL271 | V271 | 3.90 Å | Protein kinase |
| TYR272 | Y272 | 3.11 Å | Protein kinase |
| ARG273 | R273 | 3.75 Å | Protein kinase |
| ASP274 | D274 | 3.83 Å | Protein kinase |
| ILE290 | I290 | 3.38 Å | Protein kinase |
| THR291 | T291 | 3.97 Å | Protein kinase |
| ASP292 | D292 | 3.06 Å | Protein kinase |
| CYS296 | C296 | 3.15 Å | Protein kinase |

The relevant canonical UniProt P31749 domains are:

- **PH:** residues 5–108 — contains TRP80, THR82, VAL83, ILE84, and GLU85
- **Protein kinase:** residues 150–408 — contains the other 13 contacts
- **AGC-kinase C-terminal:** residues 409–480 — no contacts within 4 Å

Thus, the contacts divide into **5 PH-domain residues** and **13 protein-kinase-domain residues**, with no AGC-kinase C-terminal contacts.
=== END RUN rwgid3y0aj7 ===

=== RUN rf73864kw31 ===
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
## Pinned ChEMBL 37: sotorasib & adagrasib vs. KRAS (CHEMBL2189121)

**Source (pinned, no live API used):** local SQLite `/data/chembl/chembl_37_sqlite/chembl_37.db`, read via `[TOOL](..., mode="local")` → returned `source: local:chembl_37:2026-10-22T05:46:06Z`. The accompanying manifest (`MANIFEST.chembl_37.db`) records the official EBI tarball `.../chembl_37/releases/chembl_37/chembl_37_sqlite.tar.gz`, SHA256 `33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281`. The live ChEMBL REST service (later release) was deliberately bypassed.

**Target identity:** CHEMBL2189121 = "GTPase KRas", SINGLE PROTEIN, *Homo sapiens*.

### Headline results (standard_type = IC50)

| Compound | ChEMBL ID | # IC50 records | Median IC50 | Smallest IC50 | Largest IC50 |
|---|---|---|---|---|---|
| **Sotorasib** | CHEMBL4535757 | **8** | **49 nM** | **7 nM** | **10,000 nM** |
| **Adagrasib** | CHEMBL4594350 | **7** | **10 nM** | 5 nM | 133 nM |

### Underlying values (all in nM)

- **Sotorasib (n = 8):** 7, 9.66, 24.5, 30, 68, 7500, 7500, 10,000 → median = (30 + 68)/2 = **49 nM**; **min = 7 nM**, **max = 10,000 nM**; mean 3142 nM.
- **Adagrasib (n = 7):** 5, 5, 5, 10, 10, 14, 133 → median (4th value) = **10 nM**; range 5–133 nM.

### Verification and caveats

- Counts/medians/min/max were confirmed twice: once through the validated tool call and once by direct parameterized SQL against the same pinned file. Identical results.
- No truncation: `max_records` was set to 10,000 vs. actual counts of 8 and 7; no IC50 rows have a NULL `standard_value`; all 15 rows for the pair are already in **nM**, so the tool's unit filter and the unfiltered query give the same answer (no unit conversion applied).
- **Censored values (sotorasib):** the 7 nM record is `standard_relation = '<'` (i.e. IC50 < 7 nM), and the 10,000 nM record is `'>'` (IC50 > 10,000 nM); one of the 7,500 nM entries is also `'>'`. So the true bounds for sotorasib are *< 7 nM* and *> 10,000 nM*, and its 49 nM median is inflated by the two censored 7,500 nM values. Adagrasib's smallest value (5 nM) is also a `'<'` record.
- Scope: only `standard_type = 'IC50'` rows assigned to target CHEMBL2189121 itself. Excluded by type are sotorasib's 10 "Inhibition" (%) and 2 "Ki" rows, and adagrasib's 5 "Inhibition", 3 "Ki", and 1 "EC50" rows.
- These are pinned ChEMBL 37 numbers; the live service serves a later release and its counts/medians may differ.
=== END RUN rf73864kw31 ===

=== RUN rpdnxfpa2o2 ===
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
**ChEMBL 37 (pinned local SQLite) — KRAS target CHEMBL2189121**

Provenance: `local:chembl_37` snapshot at `/data/chembl/chembl_37_sqlite/chembl_37.db` (manifest: `https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz`; `DB Version chembl_37`). Queried with `[TOOL](..., mode="local", standard_type="IC50")`; the live ChEMBL service was **not** used.

| Compound | ChEMBL ID | # IC50 records | Median IC50 | Min | Max |
|---|---|---|---|---|---|
| Sotorasib | CHEMBL4535757 | **8** | **49 nM** | **7 nM** | **10,000 nM** |
| Adagrasib | CHEMBL4594350 | **7** | **10 nM** | 5 nM | 133 nM |

**Sotorasib — all 8 IC50 records (nM):** 7 (<), 9.66 (=), 24.5 (=), 30 (=), 68 (=), 7500 (=), 7500 (>), 10000 (>)
- **Smallest IC50: 7 nM** — assay CHEMBL5335102, relation `<` (i.e., IC50 < 7 nM; activity_id 25512445)
- **Largest IC50: 10,000 nM** — assay CHEMBL4735449, relation `>` (i.e., IC50 > 10,000 nM; activity_id 22915790)
- Median over all 8 records = (30 + 68)/2 = **49 nM**

**Adagrasib — all 7 IC50 records (nM):** 5 (=), 5 (<), 5 (=), 10 (=), 10 (=), 14 (=), 133 (=)
- Median = 4th value = **10 nM**

**Censoring caveat (transparency):** medians above use every IC50 record returned, including censored `<`/`>` entries. If only exact measurements (relation `=`) are used:
- Sotorasib: n = 5, values 9.66–7500 nM, median **30 nM**, min 9.66 nM, max 7500 nM
- Adagrasib: n = 6, values 5–133 nM, median **10 nM** (unchanged), min 5 nM, max 133 nM

An independent read-only SQL count on the same pinned `chembl_37.db` (activities → assays → target CHEMBL2189121) returned exactly 8 and 7 rows with identical values, confirming the counts are complete and not truncated.

Raw tool outputs saved as `chembl37_sotorasib_CHEMBL2189121_IC50.json`, `chembl37_adagrasib_CHEMBL2189121_IC50.json`, and `chembl37_kras_summary.json`.
=== END RUN rpdnxfpa2o2 ===

=== RUN rdj198qyajx ===
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
1. [✓] Retrieved PTPN11 pathogenic/likely pathogenic missense records from the pinned local ClinVar release.
2. [✓] Retrieved AlphaMissense scores from the pinned local AlphaMissense dataset.
3. [✓] Identified SHP099 as component `5OD` and calculated heavy-atom contacts in PDB 5EHR chain A.
4. [✓] Applied AlphaMissense score >0.9 and nearest heavy-atom distance ≤8 Å.
5. [✓] Audited classifications, residue mappings, and all thresholds.
6. [✓] Verified pinned-release and structure-file provenance.

### Matching variants

| Variant | ClinVar Variation ID | Pinned ClinVar classification | AlphaMissense | Nearest heavy-atom distance |
|---|---:|---|---:|---:|
| NM_002834.5(PTPN11):c.329A>C (p.Glu110Ala) | 40508 | Pathogenic/Likely pathogenic | 0.9621 | 3.47 Å |
| NM_002834.5(PTPN11):c.328G>A (p.Glu110Lys) | 40507 | Pathogenic/Likely pathogenic | 0.9908 | 3.47 Å |
| NM_002834.5(PTPN11):c.1472C>A (p.Pro491His) | 40551 | Pathogenic/Likely pathogenic | 0.9611 | 3.45 Å |
| NM_002834.5(PTPN11):c.1472C>T (p.Pro491Leu) | 40552 | Pathogenic | 0.9431 | 3.45 Å |
| NM_002834.5(PTPN11):c.1493G>T (p.Arg498Leu) | 40554 | Pathogenic | 0.9995 | 7.15 Å |
| NM_002834.5(PTPN11):c.1493G>A (p.Arg498Gln) | 1805026 | Likely pathogenic | 0.9993 | 7.15 Å |
| NM_002834.5(PTPN11):c.1492C>T (p.Arg498Trp) | 40553 | Pathogenic/Likely pathogenic | 0.9998 | 7.15 Å |

**Total: 7 variants.**

### Provenance and interpretation

- ClinVar was queried with `mode="local"`; the live service was not used. The pinned `variant_summary.txt.gz` has SHA-256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`, with the manifest recording completion at `2026-10-23T03:57:30Z`.
- The mixed label **“Pathogenic/Likely pathogenic”** is reproduced from that pinned release and was retained as qualifying.
- AlphaMissense came from the pinned local dataset `/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz`; the tool reported dataset SHA-256 `bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d`.
- SHP099 is chemical component `5OD` in 5EHR chain A. Distances are the minimum heavy-atom distance between the indicated PTPN11 residue and any heavy atom of `5OD`, calculated from the local 5EHR mmCIF.
=== END RUN rdj198qyajx ===

=== RUN ralukn6ou87 ===
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
## Result

For **human glucokinase** in ASD release **202306**, filtering the official HL table on `UniProt_ID = P35557` (`Gene_Symbol = GCK`, `Target_ID = ASD01200000_1`):

| Measure | Count |
|---|---:|
| Modulator records (HL rows) | **171** |
| Distinct modulator names | **170** |
| Records with activity type **EC50** | **170** |
| Records with activity type **IC50** | **1** |

The one-name difference is not a duplicate row: modulator `ASD01200034`, **2-amino-5-chloro-N-(thiazol-2-yl)benzamide**, occurs in two records—one annotated with IC50 and one with EC50.

### Verification

- Official source: [`ASD_Release_202306_HL.tar.gz`](https://mdl.shsmu.edu.cn/ASD2023Common/static_file/archive_2023/ASD_Release_202306_HL.tar.gz), listed by ASD as Release 5.01, created 2023-06-01.
- The archive’s P35557 subset contains **171 rows** with no blank activity types.
- Independent live-service retrieval by lead level returned **81 + 72 + 9 + 9 = 171** records.
- A field-by-field multiset comparison of the archive and live records was identical, including **170 EC50** and **1 IC50** records.

### Completed plan
1. [✓] Located the authoritative ASD release-202306 HL archive.
2. [✓] Downloaded, unpacked, and schema-audited the official table.
3. [✓] Filtered for P35557 and counted records, names, and activity types.
4. [✓] Audited duplicate names and cross-checked against the live ASD service.
5. [✓] Reported the verified results with provenance.
=== END RUN ralukn6ou87 ===

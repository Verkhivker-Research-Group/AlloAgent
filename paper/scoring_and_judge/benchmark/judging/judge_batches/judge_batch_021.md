# Judge batch 021 of 24

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

=== RUN r5z79a4o0mb ===
QUESTION:
Trametinib and cobimetinib are allosteric MEK inhibitors. Compare their ChEMBL IC50 records against human MAP2K1 (UniProt Q02750): number of records, median and best value for each.

INTENDED PROTEIN: Dual specificity mitogen-activated protein kinase kinase 1 (Q02750)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L02_a] [critical] [scripted] {"name": "Dual specificity mitogen-activated protein kinase kinase 1", "gene": "MAP2K1", "organism": "Homo sapiens"}
[L02_b] [critical] [scripted] {"count": 16, "median_nM": 2.8499999999999996, "best_nM": 0.48, "units": {"nM": 16}}
[L02_c] [critical] [scripted] {"count": 11, "median_nM": 4.2, "best_nM": 0.2, "units": {"nM": 11}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## ChEMBL IC50 comparison against human MAP2K1

**Target:** MAP2K1/MEK1, UniProt **Q02750** → ChEMBL target **CHEMBL3587**

| Drug | ChEMBL molecule ID | Number of IC50 records | Median IC50 | Best (lowest) IC50 |
|---|---|---:|---:|---:|
| **Trametinib** | CHEMBL2103875 | **16** | **2.85 nM** | **0.48 nM** |
| **Cobimetinib** | CHEMBL2146883 | **11** | **4.20 nM** | **0.20 nM** |

### Interpretation

- Across the complete ChEMBL record sets, **cobimetinib has the lower best-reported value** (0.20 versus 0.48 nM).
- **Trametinib has the lower median value** (2.85 versus 4.20 nM).
- Best trametinib record: activity **25754167**, 0.48 nM.
- Best cobimetinib record: activity **29186985**, 0.20 nM.

### Data-quality and assay-mix caveats

- All 27 records had `standard_relation = "="` and `standard_units = "nM"`, so no censored-value interpretation or unit conversion was required.
- Trametinib’s 16 records comprise **6 biochemical assays (B)** and **10 cell-based/phenotypic assays (F)**. Restricting trametinib to biochemical assays gives **n = 6, median 1.36 nM, best 0.70 nM**.
- Cobimetinib’s 11 records are all biochemical assays (**B**): **median 4.20 nM, best 0.20 nM**.
- Five cobimetinib rows are flagged by ChEMBL as potential duplicates, and one has a “potential transcription error” comment. Excluding all flagged rows reduces cobimetinib to **n = 6**, but its median (**4.20 nM**) and best value (**0.20 nM**) are unchanged.

The primary figures above use all exact ChEMBL IC50 records mapped to CHEMBL3587. Data were checked against the ChEMBL API reporting database version **ChEMBL_37**.
=== END RUN r5z79a4o0mb ===

=== RUN r7vbsq4rjdy ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## STINGAllo prediction for PTP1B (PDB 1T4J, chain A)

**Predicted allosteric residues:**

**E129, E130, S187, P188, A189, L192, N193, F196, E200, E276, K279, F280, I281, M282**

The API returned the residue numbers:

`129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282`

All 14 positions were confirmed to be standard protein residues in chain A of the deposited 1T4J structure.

**Service-response date:** **Wed, 28 Oct 2026 10:40:20 GMT**

This date comes from the HTTP `Date` header; the JSON response did not contain a separate date field.

**Request provenance:**  
`GET https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A`  
HTTP status: `200 OK`

STINGAllo reference: *Briefings in Bioinformatics* (2025), DOI [10.1093/bib/bbaf424](https://doi.org/10.1093/bib/bbaf424).
=== END RUN r7vbsq4rjdy ===

=== RUN rx1ouvzeruf ===
QUESTION:
Remove all ligands from PDB entry 1OPK (ABL1, UniProt P00519) and run pocket detection. What is the rank of the pocket that covers the myristoyl site?

INTENDED PROTEIN: Tyrosine-protein kinase ABL1 (P00519)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P05_a] [critical] [scripted] {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"}
[P05_b] [critical] [scripted] [{"rank": 1, "residues": 23}, {"rank": 2, "residues": 23}, {"rank": 3, "residues": 17}]
[P05_c] [critical] [judged] the rank of the pocket that covers the myristoyl site (the MYR contacts) is reported
[P05_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P05_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 3, "overlap_of_the_covering_pocket": 8, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 8], "pockets": [{"rank": 1, "score": 0.338, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.32, "n_residues": 23, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.211, "n_residues": 17, "site_residues_in_pocket": 8}, {"rank": 4, "score": 0.121, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.112, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.111, "n_residues": 18, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.097, "n_residues": 32, "site_residues_in_pocket": 0}, {"rank": 8, "score": 0.09, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 9, "score": 0.049, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.044, "n_residues": 13, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.038, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 12, "score": 0.025, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.023, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.022, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.011, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.009, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 17, "score": -0.004, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 18, "score": -0.004, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 19, "score": -0.01, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 20, "score": -0.017, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 21, "score": -0.018, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 22, "score": -0.02, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 23, "score": -0.033, "n_residues": 10, "site_residues_in_pocket": 1}, {"rank": 24, "score": -0.036, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 25, "score": -0.037, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 26, "score": -0.045, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 27, "score": -0.047, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 28, "score": -0.06, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 29, "score": -0.085, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 30, "score": -0.09, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 31, "score": -0.103, "n_residues": 5, "site_residues_in_pocket": 0}, {"rank": 32, "score": -0.131, "n_residues": 7, "site_residues_in_pocket": 2}, {"rank": 33, "score": -0.137, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 34, "score": -0.158, "n_residues": 17, "site_residues_in_pocket": 0}]}
[P05_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 23.77, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 11.32, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 10.44, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 4, "score": 9.99, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 5, "score": 4.5, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 6, "score": 2.04, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 7, "score": 1.74, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 8, "score": 1.24, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 9, "score": 1.09, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.46, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P05_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**The pocket covering the myristoyl site ranks 3rd.**

### Updated plan
1. [✓] Retrieved and inspected PDB 1OPK.
2. [✓] Removed all heteroatom records and verified the receptor contained zero HETATM records.
3. [✓] Ran fpocket and identified the myristoyl-site pocket.
4. [✓] Cross-checked the assignment against direct MYR contacts and repeated the detection on the explicit ligand-free file.

### Evidence
- Removed components: **MYR** (myristoyl group), **P16** inhibitor, **GOL**, and 270 waters.
- fpocket identified **34 pockets**.
- **Pocket 3** contained all eight residues contacting MYR within 4 Å: A359, A360, A363, A448, A452, A481, A521, and A529.
- Pocket 3 score: **0.211**; druggability score: **0.547**.
- Repeating detection on the explicitly saved ligand-free PDB produced an identical pocket-3 score and residue set.

**Answer: rank 3.**
=== END RUN rx1ouvzeruf ===

=== RUN rdqznls6gpu ===
QUESTION:
Trametinib and cobimetinib are allosteric MEK inhibitors. Compare their ChEMBL IC50 records against human MAP2K1 (UniProt Q02750): number of records, median and best value for each.

INTENDED PROTEIN: Dual specificity mitogen-activated protein kinase kinase 1 (Q02750)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[L02_a] [critical] [scripted] {"name": "Dual specificity mitogen-activated protein kinase kinase 1", "gene": "MAP2K1", "organism": "Homo sapiens"}
[L02_b] [critical] [scripted] {"count": 16, "median_nM": 2.8499999999999996, "best_nM": 0.48, "units": {"nM": 16}}
[L02_c] [critical] [scripted] {"count": 11, "median_nM": 4.2, "best_nM": 0.2, "units": {"nM": 11}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
1. [✓] Retrieve trametinib IC50 records for human MAP2K1 (Q02750)
2. [✓] Retrieve cobimetinib IC50 records for human MAP2K1 (Q02750)
3. [✓] Validate numeric values/units and calculate count, median, and best IC50
4. [✓] Present the side-by-side comparison with source provenance and caveats

### ChEMBL IC50 comparison

Human MAP2K1/Q02750 maps to ChEMBL target **CHEMBL3587**.

| Compound | ChEMBL molecule | IC50 records | Median IC50 | Best IC50* |
|---|---|---:|---:|---:|
| Trametinib | CHEMBL2103875 | **16** | **2.85 nM** | **0.48 nM** |
| Cobimetinib | CHEMBL2146883 | **11** | **4.20 nM** | **0.20 nM** |

\*“Best” is the lowest reported IC50, indicating the strongest inhibition.

### Comparison

- **Cobimetinib has the better best-reported potency:** 0.20 nM versus 0.48 nM for trametinib, a **2.4-fold lower IC50**.
- **Trametinib has the lower median IC50:** 2.85 nM versus 4.20 nM, approximately **32% lower**.
- Thus, the strongest individual ChEMBL measurement favors cobimetinib, while the central value across records favors trametinib.

All included records have an exact relation (`=`) and are reported in nM. The results come from the local **ChEMBL 37** release (`2026-10-22T05:46:06Z`). Because the records originate from multiple assays, these comparisons are descriptive rather than controlled head-to-head potency estimates.

Raw query results and the calculated summary were saved under `/agent_cwd/results/`.
=== END RUN rdqznls6gpu ===

=== RUN rbl8n24kvxn ===
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
## Final plan status

1. [✗] Initial ChEMBL retrieval failed because the SQLite assay identifier is `chembl_id`, not `assay_chembl_id`
2. [✗] First retry used `tid=1862`, which is not ChEMBL’s internal target key
3. [✓] Resolved human ABL1 as internal `tid=8`, ChEMBL target `CHEMBL1862`, and enumerated all records
4. [✓] Summarized endpoint counts, assay types, censored values, duplicates, and best potencies
5. [✗] Initial RCSB parser incorrectly treated non-polymer entity IDs as dictionaries
6. [✓] Corrected the parser and confirmed asciminib component `AY7` and imatinib component `STI`
7. [✓] Verified human P00519 mappings, ligand contacts, and binding-site assignments
8. [✓] Reconciled raw versus measurable record counts
9. [✓] Prepared the comparison with PDB and ChEMBL citations

## ChEMBL comparison

Scope: exact human ABL1 records, target `CHEMBL1862` / UniProt **P00519**. This excludes records assigned only to BCR–ABL1 fusion protein, cells, or other organisms.

| Measure | Asciminib, `CHEMBL4208229` | Imatinib, `CHEMBL941` |
|---|---:|---:|
| Raw direct-target activity rows | **6** | **160** |
| Rows with a numeric standardized value | **4** | **139** |
| ChEMBL `assay_type` | **B: 6**; numerically measurable B: 4 | **B: 158, A: 1, F: 1**; numerically measurable B: 137, A: 1, F: 1 |
| Best Kd | **0.5 nM** | **1.0 nM** |
| Best Ki | No Ki records | **13 nM** |
| Best equality-valued IC50 | **0.5 nM** | **19.9 nM** |
| Corresponding pChEMBL | 9.3 for both Kd and IC50 | 9.0 Kd; 7.89 Ki; 7.7 IC50 |

ChEMBL codes: **B = binding**, **A = ADMET**, **F = functional**.

### Endpoint record counts

- **Asciminib:** IC50 **2/2**, Kd **1/1**, ΔTm **1/1**, kon **1/0**, k_off **1/0** — raw/numerically measurable. The single thermal-shift assay is classified as binding, in vitro.
- **Imatinib:** IC50 **94/91**, Kd **31/31**, Ki **6/6**, Inhibition **13/5**, GI50 **2/2**, Kdiss **3/1**, Activity **1/1**, Selectivity **1/1**, T1/2 **1/1**, kon **3/0**, k_off **3/0**, t1/2 **2/0**.

### Best potency records

- **Asciminib**
  - **Kd 0.5 nM**, pChEMBL 9.3 — ITC binding to ABL1 residues 64–515: [CHEMBL4200854](https://www.ebi.ac.uk/chembl/assay_report/CHEMBL4200854/), PMID [30137981](https://pubmed.ncbi.nlm.nih.gov/30137981/), DOI [10.1021/acs.jmedchem.8b01040](https://doi.org/10.1021/acs.jmedchem.8b01040).
  - **IC50 0.5 nM**, pChEMBL 9.3 — enzymatic inhibition of ABL1 residues 64–515: [CHEMBL4200739](https://www.ebi.ac.uk/chembl/assay_report/CHEMBL4200739/), same publication.
  - The other IC50 is **16 nM** (`CHEMBL5739300`).

- **Imatinib**
  - **Kd 1.0 nM**, pChEMBL 9.0: [CHEMBL4320888](https://www.ebi.ac.uk/chembl/assay_report/CHEMBL4320888/), PMID [30807144](https://pubmed.ncbi.nlm.nih.gov/30807144/), DOI [10.1021/acs.jmedchem.8b01925](https://doi.org/10.1021/acs.jmedchem.8b01925).
  - **Ki 13 nM**, pChEMBL 7.89: [CHEMBL932076](https://www.ebi.ac.uk/chembl/assay_report/CHEMBL932076/).
  - **IC50 19.9 nM**, pChEMBL 7.7 — human wild-type ABL TR-FRET inhibition: [CHEMBL2406231](https://www.ebi.ac.uk/chembl/assay_report/CHEMBL2406231/), PMID [23773153](https://pubmed.ncbi.nlm.nih.gov/23773153/), DOI [10.1021/jm4004076](https://doi.org/10.1021/jm4004076).

Thus, on the same endpoints, asciminib’s nominal values are **2-fold lower for Kd** and **about 40-fold lower for IC50** than imatinib’s best equality-valued measurements. These are not head-to-head assays, so this should not be interpreted as a direct quantitative or clinical superiority claim.

Additional count caveats: 19 imatinib IC50 records are censored (`>`), and the 19.9 nM minimum uses only exact equality-valued records. ChEMBL flags **40 of imatinib’s 160 rows** as potential duplicates; none of asciminib’s six rows are flagged.

## Binding sites and PDB evidence

- **Asciminib — allosteric myristoyl-pocket site.**  
  [PDB **5MO4**](https://www.rcsb.org/structure/5MO4) contains asciminib (`AY7`) and maps to human ABL1 **P00519**. Its primary paper explicitly states that asciminib/ABL001 “binds to the myristoyl pocket of ABL1”: DOI [10.1038/nature21702](https://doi.org/10.1038/nature21702), PMID [28329763](https://pubmed.ncbi.nlm.nih.gov/28329763/). The deposited construct carries the engineered ABL1 T334I/D382N substitutions. [PDB **8SSN**](https://www.rcsb.org/structure/8SSN) provides another human P00519–asciminib structure.

- **Imatinib — ATP-binding site, type-II inhibitor.**  
  [PDB **2HYY**](https://www.rcsb.org/structure/2HYY) is titled “Human Abl kinase domain in complex with imatinib (STI571)” and maps to P00519. Imatinib contacts the ABL1 gatekeeper **Thr315**, hinge **Met318**, and DFG **Asp381/Phe382**, consistent with the ATP-site/DFG-out footprint. Primary citation: DOI [10.1107/S0907444906047287](https://doi.org/10.1107/S0907444906047287), PMID [17164530](https://pubmed.ncbi.nlm.nih.gov/17164530/).
=== END RUN rbl8n24kvxn ===

=== RUN ryas8zs8u07 ===
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
## SHP2–SHP099 comparison: PDB **5EHR**, chain **A**

In 5EHR, SHP099 is deposited under chemical component ID **5OD**; the mmCIF record explicitly lists **SHP099** as its synonym.

### STINGAllo-predicted residue

- **A314 — PHE314**

### SHP099 residues within 4 Å

| PDB residue | Minimum heavy-atom distance |
|---|---:|
| A108 — THR108 | 3.13 Å |
| A110 — GLU110 | 3.47 Å |
| A111 — ARG111 | 3.14 Å |
| A113 — PHE113 | 2.79 Å |
| A114 — HIS114 | 3.75 Å |
| A218 — THR218 | 3.69 Å |
| A219 — THR219 | 3.59 Å |
| A249 — GLU249 | 3.29 Å |
| A250 — GLU250 | 3.10 Å |
| A253 — THR253 | 3.30 Å |
| A254 — LEU254 | 3.46 Å |
| A257 — GLN257 | 3.58 Å |
| A491 — PRO491 | 3.45 Å |
| A492 — LYS492 | 3.45 Å |
| A495 — GLN495 | 3.57 Å |

### Overlap

**None (∅).**

### Interpretation

**No—the STINGAllo prediction does not recover the proximal SHP099 tunnel site.** Its sole prediction, **PHE314**, is not among the residues within 4 Å of SHP099.

**Technical note:** the raw STINGAllo payload reports `allosteric_residues: ["314"]` for chain A. The packaged wrapper expects a differently named response key and therefore displayed an empty list; the comparison above uses the raw service result.

### Completed plan

1. [✓] Retrieve STINGAllo predictions for PDB 5EHR, chain A
2. [✗] Initial literal “SHP099” component-ID query failed; 5EHR uses 5OD
3. [✓] Retrieve SHP099/5OD contacts within 4 Å
4. [✓] Verify the STINGAllo workflow and raw service response
5. [✓] Confirm 5OD = SHP099 from the deposited mmCIF
6. [✓] Compute the overlap
7. [✓] Assess tunnel-site recovery: no overlap
=== END RUN ryas8zs8u07 ===

=== RUN ruyknkp0syt ===
QUESTION:
Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[C03_b] [critical] [judged] the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

Normal-mode analysis of autoinhibited SHP2 in **2SHP** found no significant overall difference in mobility between residues contacting SHP099 in **5EHR** and the rest of SHP2.

The 15 SHP099-contact residues span both relatively rigid and highly mobile parts of 2SHP, rather than forming a uniformly mobile or rigid group.

### Contact definition and mapping

SHP099 is represented by chemical component **5OD** in 5EHR. Using a **4.0 Å heavy-atom cutoff**, chains A and B gave the same 15 contacts:

**108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495**

These were mapped to **Q06124** numbering and were all present in both chains of 2SHP.

## ANM analysis

- Structure: 2SHP, chains A and B
- Model: ProDy 2.6.1 Anisotropic Network Model
- Cα atoms analyzed: 982
- Total modes: 982
- Rigid-body/trivial modes removed: 6
- Non-trivial modes retained: **976**
- Eigenvalue range: **0.01626–14.3776**

Mobility was calculated from the ProDy ANM covariance diagonal:

\[
M_i=\sum_m \frac{u_{mi}^{2}}{\lambda_m}
\]

where \(u_{mi}\) is the amplitude of residue \(i\) in mode \(m\), and \(\lambda_m\) is the mode eigenvalue. These are **relative mobility units**, not experimentally calibrated Å RMSF values.

## Statistical comparison

To avoid treating the two crystallographic copies as independent observations, chains A and B were first averaged by UniProt position. The comparison therefore used **15 SHP099-contact positions versus 476 non-contact positions**.

| Metric | SHP099 contacts | Other residues | Median ratio | Mann–Whitney p |
|---|---:|---:|---:|---:|
| ANM variance/mobility, median | 0.06614 | 0.07027 | 0.941 | 0.959 |
| Relative RMS mobility index, median | 0.2562 | 0.2555 | 1.003 | 0.908 |
| Mode participation, median | 0.3128 | 0.3418 | 0.915 | 0.452 |
| Low-10-mode variance, median | 0.01913 | 0.01414 | 1.353 | 0.309 |

Additional statistics for the primary ANM-variance metric:

- 20,000-label permutation test: **p = 0.961**
- Cliff’s delta: **−0.008**, effectively no rank separation
- Hedges’ g: **0.103**, a negligible effect size
- Bootstrap 95% CI for the median ratio: **0.599–1.600**, including no difference
- Mean variance was slightly higher for contacts (**1.054×**) because of a few highly mobile contact residues, but the medians were essentially identical

Chain-specific analyses were directionally inconsistent:

- Chain A: median ratio **0.945**, p = 0.522
- Chain B: median ratio **1.086**, p = 0.243

This supports the conclusion of **no consistent mobility shift** at the contact-set level.

## Per-residue mobility

Percentiles are relative to all 491 resolved UniProt positions in 2SHP.

| Q06124 residue | Identity | ANM variance | Percentile |
|---:|---|---:|---:|
| 108 | Thr | 0.04621 | 23.0% |
| 110 | Glu | 0.06614 | 46.6% |
| 111 | Arg | 0.06052 | 40.7% |
| 113 | Phe | 0.03945 | 16.1% |
| 114 | His | 0.07431 | 54.4% |
| 218 | Thr | 0.03901 | 15.9% |
| 219 | Thr | 0.02781 | 4.5% |
| 249 | Glu | 0.18176 | **98.0%** |
| 250 | Glu | 0.08182 | 62.1% |
| 253 | Thr | 0.11826 | **86.6%** |
| 254 | Leu | 0.03889 | 15.7% |
| 257 | Gln | 0.05891 | 37.9% |
| 491 | Pro | 0.07383 | 53.8% |
| 492 | Lys | 0.15239 | **95.5%** |
| 495 | Gln | 0.14748 | **95.1%** |

The most mobile contacts are **Glu249, Lys492, Gln495, and Thr253**. The least mobile are **Thr219, Leu254, Thr218, and Phe113**.

## Interpretation

1. **No global mobility enrichment:** SHP099-contacting residues are not, as a group, intrinsically more mobile in autoinhibited 2SHP.
2. **Marked local heterogeneity:** Glu249, Lys492, Gln495, and Thr253 are highly mobile, whereas Thr219 and several other contacts are relatively constrained. This mixed pattern is more informative than the group average.
3. **Possible low-frequency tendency, but not significant:** Contacts show a modest increase in the variance contributed by the ten lowest-frequency modes, but the effect is small and statistically unsupported.
4. **Mechanistic implication:** The analysis is consistent with SHP099 engaging a pre-existing, heterogeneous flexibility landscape rather than contacting a uniformly mobile or uniformly rigid surface in 2SHP.

### Limitations

- ANM is an elastic-network approximation and produces relative, not physical, fluctuation amplitudes.
- 2SHP contains two chains that are modeled as one network, so collective and possible inter-chain modes can affect the values. The position-level averaging and chain-specific analyses mitigate but do not eliminate this issue.
- The contacts were defined in the SHP099-bound 5EHR structure and transferred as a residue set to 2SHP. This does not directly measure ligand-induced conformational change or binding energetics.
- Residue-level tests are descriptive because contacts are spatially structured and normal-mode fluctuations are correlated.

### Output artifacts

Saved under `/agent_cwd/sphp2_analysis/`:

- `2SHP_ANM_full.json` — complete 976-mode ANM output
- `step1_contacts.json` — 5EHR SHP099 contacts
- `2SHP_CA_index_mapping.csv` — exact ANM residue-index mapping
- `2SHP_residue_mobility_by_uniprot.csv`
- `2SHP_residue_mobility_by_chain.csv`
- `SHP099_contact_mobility_2SHP.csv`
- `mobility_comparison_results.json`
- `2SHP_SHP099_contact_mobility.png`

### Completed analysis checklist

1. [✓] Retrieve 2SHP/5EHR UniProt mappings and SHP099 contacts
2. [✓] Run ANM on 2SHP with all 976 non-trivial modes
3. [✓] Map SHP099 contacts to Q06124 and 2SHP ANM indices
4. [✓] Establish the correct ProDy covariance-based mobility metric
5. [✓] Compare contacts with the rest of the structure using rank, permutation, effect-size, and bootstrap analyses
6. [✓] Generate per-residue results and the mobility-profile figure
7. [✓] Synthesize the structural interpretation and limitations
=== END RUN ruyknkp0syt ===

=== RUN rtesgc80tg6 ===
QUESTION:
Remove all ligands from PDB entry 1T4J (PTP1B, UniProt P18031) and run pocket detection. Does any of the top three pockets overlap the site where the allosteric ligand was bound? Report the overlap as a number of shared residues.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P01_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P01_c] [critical] [judged] the top three fpocket pockets of the ligand-stripped 1T4J contain the residues FRJ contacted, and the overlap is reported as a count
[P01_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P01_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P01_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P01_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**No. None of the top three ligand-free pockets overlaps the original FRJ allosteric-ligand site.**

### Procedure
- Downloaded PDB **1T4J** (PTP1B, UniProt **P18031**).
- Removed all **41 HETATM records**, including the sole ligand **FRJ**; retained all **2,304 protein ATOM records**.
- Ran **fpocket** on the ligand-free receptor.
- Identified the original FRJ site using **11 residues within 4.0 Å** of FRJ in the holo structure:
  **A188, A189, A192, A193, A196, A200, A276, A277, A279, A280, A282**.
  These exactly matched the curated ASD allosteric-site annotation.

### Top-three pocket overlaps

| fpocket rank | Score | Shared residues with FRJ site |
|---|---:|---:|
| 1 | 0.235 | **0** |
| 2 | 0.167 | **0** |
| 3 | 0.142 | **0** |

**Maximum overlap among the top three pockets: 0 shared residues.**

For context, lower-ranked pockets did overlap the site: pocket 7 shared 2 residues, pocket 8 shared 2, and pocket 11 shared 8. Thus, fpocket detected the allosteric region, but it did **not** place it among the three highest-ranked pockets.

1. [✓] Step 1: Inventory ligands in 1T4J and identify the curated allosteric ligand for PTP1B (P18031)
2. [✓] Step 2: Download 1T4J and create/verify a ligand-free receptor structure
3. [✓] Step 3: Run pocket detection and retain the three highest-ranked pockets
4. [✓] Step 4: Determine the original allosteric-ligand contact residues
5. [✓] Step 5: Map each top pocket to residues and calculate shared-residue overlaps
6. [✓] Step 6: Cross-check with the integrated allosteric-site workflow and report the final result
=== END RUN rtesgc80tg6 ===

=== RUN rp2i45hgqw1 ===
QUESTION:
Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C06_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C06_b] [critical] [judged] the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Overall assessment

**Allosteric communication between the FRJ-binding pocket and the catalytic region of PTP1B is plausible, and the existence of an allosteric inhibitor mechanism is experimentally established. However, these analyses do not demonstrate a specific, directional, or causal communication pathway ending at Cys215.**

The strongest overall interpretation is:

- **High confidence:** FRJ occupies the experimentally characterized allosteric site of PTP1B, about 20 Å from the catalytic site.
- **Moderate confidence:** The ligand pocket and catalytic region are structurally connected through the P-loop/catalytic-loop region, and some low-frequency collective motions couple them.
- **Low confidence:** A particular route carries the ligand-induced perturbation specifically to Cys215.

## Final plan

1. [✓] Verify PTP1B identity, the 1T4J ligand, chain A numbering, and catalytic Cys215
2. [✓] Define the FRJ-contact/allosteric-site set and catalytic reference
3. [✓] Run ANM mode-shape and covariance analyses with cutoff and null-model checks
4. [✓] Construct and characterize residue contact-network paths
5. [✓] Retrieve and compare STINGAllo predictions
6. [✓] Check low-mode and full-spectrum robustness of the ANM results
7. [✓] Integrate the analyses and state their evidentiary boundaries

## Reference structure and site definition

- **Protein:** Human PTP1B, UniProt **P18031**
- **Structure:** PDB **1T4J**, chain A, X-ray resolution **2.70 Å**
- **Ligand:** **FRJ**, a PTP1B allosteric inhibitor
- **Catalytic residue:** **Cys215**
- UniProt maps 1T4J chain A to residues 1–298; 282 Cα atoms were resolved and used for ANM.
- The FRJ first shell was defined as residues with any heavy atom within **4.5 Å** of FRJ:
  **S187, P188, A189, L192, N193, F196, K197, E200, E276, G277, K279, F280, I281, M282**.

The original structural study reports that FRJ inhibits PTP1B by preventing formation of the active catalytic-loop conformation, providing experimental context beyond the calculations.

## 1. Normal-mode analysis

### Method

A three-dimensional anisotropic network model was built from the 282 chain-A Cα atoms using ProDy ANM:

- Spring constant: 1
- Contact cutoffs tested: **10 Å and 15 Å**
- 30 lowest nonzero modes examined, with rigid-body zero modes excluded
- Truncated 30-mode covariance and full 840-nonzero-mode covariance calculated as a sensitivity check
- Random null groups: 2,000 groups of 14 residues, excluding Cys215

Two measures were used:

1. Vector correlation between the mean displacement of the FRJ-contact set and Cys215.
2. Absolute cosine similarity between the FRJ-site centroid and Cys215 in each low-frequency mode.

### Main results

| Metric | 10 Å cutoff | 15 Å cutoff |
|---|---:|---:|
| FRJ-site centroid versus Cys215, 30 low modes | 0.149 | 0.276 |
| Random-group percentile | 61.6 | 72.5 |
| Proximal site subset, residues 187–200 | 0.201 | 0.363 |
| Distal pocket subset, residues 276–282 | 0.070 | 0.125 |
| Mean absolute mode cosine, first 10 modes | 0.631 | 0.621 |
| Random percentile for mode-cosine metric | 73.4 | 67.0 |
| FRJ-site centroid versus Cys215, all 840 modes | 0.012 | 0.014 |

The strongest individual low-mode correlations with Cys215 were to the ligand-proximal residues:

- N193: 0.368–0.478
- F196: 0.372–0.613
- K197: 0.336–0.566
- E200: 0.272–0.368

By comparison, the more distal pocket residues E276, K279, F280, I281, and M282 had weak, near-zero, or negative correlations.

### What NMA supports

- Some FRJ-contact residues and Cys215 participate in related low-frequency collective deformations.
- The ligand-proximal part of the pocket is more dynamically coupled to Cys215 than the distal E276–M282 segment.
- This is consistent with perturbations being transmitted through the P-loop/catalytic-loop region rather than uniformly through the entire ligand pocket.

### What NMA does not support

- It does **not** show that FRJ binding causes the observed motion; the ligand was not included in the elastic network, and no bound-versus-apo comparison was made.
- The aggregate site-to-Cys correlation is modest and disappears in absolute magnitude when all modes are included.
- Some correlations are expected from local packing near the catalytic site. Cys215’s strongest correlates include its immediate sequence neighbors, including H214, S216, S217, and S218.
- A Cα ANM cannot describe the side-chain orientation or chemical reactivity of the catalytic Cys215 thiol.
- Normal modes do not provide signal direction, energetic transfer rates, or causal information.

**Interpretation:** NMA provides **weak-to-moderate, model-dependent support for possible collective coupling**, not proof of ligand-induced communication with Cys215.

## 2. Residue contact-network path

### Method

A residue graph was built from minimum heavy-atom distances between chain-A residues. Immediate sequence-neighbor edges were excluded so that a trivial peptide-adjacency path could not be mistaken for tertiary communication. Paths were calculated at 4.0, 4.5, and 5.0 Å; a Cα graph at 8 Å was used as a sensitivity check.

### Representative paths

At a 4.5 Å cutoff:

- **E276–P188–F191–L110–Cys215**
- **E200–V198–V108–L110–Cys215**

At the stricter 4.0 Å cutoff:

- **E276–P188–S190–Y176–N111–Cys215**
- **N193–S190–Y176–N111–Cys215**

The Cα graph produced similar four- to five-residue-hop routes through Tyr176, Asn111, Met109, or Leu110.

Several intermediates were also among Cys215’s strongest low-mode correlates:

- Leu110: 0.903 at 10 Å and 0.890 at 15 Å
- Asn111: 0.817 and 0.852
- Tyr176: 0.626 and 0.732
- Val108: 0.579 and 0.867
- Phe191: 0.350 and 0.517

These correlations weakened substantially in the full-spectrum covariance—for example, Leu110 fell to 0.290 and 0.090—showing that much of the very strong low-mode correlation reflects collective-mode weighting rather than a robust unique pathway.

### What the contact network supports

- A continuous static structural route exists from the FRJ pocket through the P-loop/catalytic-loop region to the Cys215 neighborhood.
- The convergence of some path intermediates with low-mode Cys215 correlations gives the pathway plausible dynamical relevance.
- The network makes a ligand-site-to-catalytic-region connection geometrically credible.

### What the contact network does not support

- A shortest graph path is not necessarily the path followed by a ligand-induced perturbation.
- The preferred path changes with the contact cutoff, so it is not unique.
- Connectivity does not imply energetic coupling, direction, or functional causality.
- Because Cys215 is reached through residues already close to the catalytic site, the route may describe local structural continuity rather than a long-range allosteric cascade.

**Interpretation:** The contact network establishes **structural plausibility**, not a mechanistically validated pathway.

## 3. STINGAllo prediction

The public STINGAllo API was queried for 1T4J chain A:

`https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A`

### Prediction

STINGAllo returned 14 allosteric site-forming residues:

**E129, E130, S187, P188, A189, L192, N193, F196, E200, E276, K279, F280, I281, M282**

### Agreement with FRJ crystallography

- Direct FRJ contacts: 14 residues
- STINGAllo allosteric site-forming residues: 14 residues
- Overlap: **12 residues**
- Jaccard overlap: **0.75**
- FRJ-contact residues missed by STINGAllo: **K197 and G277**
- STINGAllo-only residues: **E129 and E130**
- Cys215 was **not** predicted

E129 and E130 are approximately 23.6 Å and 29.2 Å from FRJ, respectively. The API did not provide residue scores or clustering, so they may represent an additional/extended predicted site or false positives; they should not automatically be interpreted as part of the same FRJ pocket.

### What STINGAllo supports

- The FRJ-binding region is independently recognizable as an allosteric-site-forming region from the static protein nanoenvironment.
- Its substantial overlap with crystallographic FRJ contacts is a strong consistency check.
- This supports the localization of the allosteric pocket, which is also experimentally established.

### What STINGAllo does not support

- STINGAllo predicts **site-forming residues**, not dynamic communication, collective motions, propagation paths, or catalytic effects.
- It does not predict Cys215 and therefore does not provide a route to Cys215.
- It supplies neither a ligand-induced signal nor a direction of communication.
- Because 1T4J is an older PDB entry and the server covers the PDB, training-set leakage cannot be excluded; this should not be treated as a fully blind prediction.
- The benchmark performance reported for the model does not establish a calibrated confidence for this particular chain.

**Interpretation:** STINGAllo strongly supports the **identity of the allosteric region**, but contributes little direct evidence for communication with Cys215.

## Integrated interpretation

| Evidence | Supported conclusion | Not established |
|---|---|---|
| 1T4J structural biology and original study | FRJ is an experimentally validated allosteric inhibitor; inhibitor binding restricts catalytic-loop mobility | A specific residue-by-residue signal route to Cys215 |
| ANM | Some low-frequency collective coupling exists, especially between proximal FRJ-contact residues and the catalytic region | Ligand-induced direction, unique pathway, strong site-wide coupling, or catalytic Cys side-chain motion |
| Contact network | A short structural route connects FRJ contacts through the P-loop/catalytic region to Cys215 | Functional use of that route, energetic transmission, or cutoff-independent uniqueness |
| STINGAllo | The FRJ pocket is independently identified as an allosteric-site-forming region | Communication, a path to Cys215, or catalytic-site modulation |
| Combined analysis | Allosteric coupling is biologically and computationally plausible | Causal, residue-specific communication ending at Cys215 |

## Bottom line

**The combined results support the possibility of allosteric communication, but not a proven Cys215-directed pathway.** The most defensible model is that FRJ binding at the experimentally established distal pocket alters collective mobility in the adjacent P-loop/catalytic-loop machinery, which can influence the catalytic state. The analyses do not isolate a unique route to Cys215, and the strongest numerical correlations are partly explained by proximity, coarse graining, and low-mode weighting.

To establish the proposed communication, the most decisive follow-up would be:

1. Comparison of FRJ-bound and apo PTP1B by HDX-MS or solution NMR.
2. Mutagenesis of path residues such as P188, F191, L110, Y176, N111, N193, F196, K197, and E200, measuring both ligand binding and catalytic activity separately.
3. Side-chain-resolved dynamics or spectroscopy for the catalytic loop and Cys215.
4. Coupled-mutant or double-mutant analysis to test whether the ligand-site and catalytic-site perturbations are energetically coupled.

## Primary sources

- RCSB PDB 1T4J: https://www.rcsb.org/structure/1T4J
- UniProt P18031: https://www.uniprot.org/uniprotkb/P18031/entry
- Wiesmann C, et al. **Allosteric inhibition of protein tyrosine phosphatase 1B.** *Nature Structural & Molecular Biology.* 2004;11:730–737. DOI: **10.1038/nsmb803**; PMID: **15258570**.
- Atilgan AR, et al. **Anisotropy of fluctuation dynamics of proteins with an elastic network model.** *Biophysical Journal.* 2001;80:505–515. DOI: **10.1016/S0006-3495(01)76033-X**.
- Omage FB, et al. **STINGAllo: a web server for high-throughput prediction of allosteric site-forming residues using internal protein nanoenvironment descriptors.** *Briefings in Bioinformatics.* 2025. DOI: **10.1093/bib/bbaf424**; PMID: **40838783**.
- Omage FB, et al. **Protein allosteric site identification using machine learning and per amino acid residue reported internal protein nanoenvironment descriptors.** *Computational and Structural Biotechnology Journal.* 2024. DOI: **10.1016/j.csbj.2024.10.036**; PMID: **39559776**.
=== END RUN rp2i45hgqw1 ===

=== RUN rutc5g0c079 ===
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
## Plan status

1. [✓] Retrieved 2SHP/5EHR structure mappings, identified SHP099’s ligand component in 5EHR, and obtained its contacting residues
2. [✓] Ran pocket detection on autoinhibited 2SHP and extracted the five highest-ranked fpocket and P2Rank pockets
3. [✓] Mapped pocket and ligand-contact residues from both entries to Q06124 UniProt numbering using residue-level RCSB SIFTS alignments
4. [✗] Initial final audit failed at JSON serialization because a Python set was not converted to a list; the underlying overlap calculation was unaffected
5. [✓] Re-ran and saved the final overlap audit with serializable tables
6. [✓] Prepared the detector-specific result and interpretation

## Result

**Yes—using P2Rank, one of the five highest-ranked pockets overlaps residues that contact SHP099.**  
The overlap occurs in **P2Rank pocket rank 5** and contains three UniProt positions:

| Q06124 UniProt position | Residue | 2SHP pocket residue | 5EHR SHP099 contact distance |
|---:|---|---|---:|
| 110 | Glu110 | 2SHP A:110 | 3.47 Å in chain A; 3.11 Å in chain B |
| 111 | Arg111 | 2SHP A:111 | 3.14 Å in chain A; 2.93 Å in chain B |
| 257 | Gln257 | 2SHP A:257 | 3.58 Å in both chains |

Thus, the top-five P2Rank pockets cover **3 of the 15 unique SHP099-contacting positions (20%)**.

### Detector-specific summary

| Detector | Pocket rank with overlap | Overlapping Q06124 positions | Top-five union overlap |
|---|---:|---|---|
| P2Rank 2.5.1 | 5 | 110, 111, 257 | 3 / 15 |
| fpocket 4.2.3 | None | None | 0 / 15 |

The conclusion is therefore **method-dependent**: P2Rank detects a partial site overlap, whereas none of the five highest-ranked fpocket pockets contains a residue from the SHP099-contact set.

## SHP099 contact set in 5EHR

SHP099 is chemical component **5OD** in 5EHR. Using a 4.0 Å minimum heavy-atom distance cutoff, it contacts the same 15 unique Q06124 positions in each of the two 5EHR chains:

**108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, and 495.**

Both structures map to human SHP2, **UniProt Q06124**. The reported overlap is at the UniProt-sequence level rather than by directly comparing the differing author residue numbering of the two PDB entries.

## Interpretation

The P2Rank rank-5 site in autoinhibited 2SHP partially occupies the 5EHR SHP099-contact surface, but it captures only three of the 15 contact positions. Thus, 2SHP does not present the complete SHP099 contact geometry in that pocket. Pocket membership and ligand contacts are geometric predictions, not evidence of binding affinity, interaction type, or biological modulation.
=== END RUN rutc5g0c079 ===

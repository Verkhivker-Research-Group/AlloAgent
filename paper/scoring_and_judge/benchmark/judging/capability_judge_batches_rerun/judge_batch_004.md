# Judge batch 004 of 8

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

=== RUN rdhz24nqf7b ===
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
**BioLiP (BioLiP2) — human PTP1B, UniProt P18031**

| Quantity | Count |
|---|---|
| Total curated ligand-binding (receptor–ligand interaction) entries | **409** |
| Of these, entries with a **metal** ligand | **9** (all Mg²⁺; PDBs 1OEU, 1WAX, 6XE8 ×2, 6XED ×3, 6XEF, 6XEG) |
| Of these, entries with a **non-metal** ligand | **400** (374 "regular" small molecules + 26 peptide ligands; no DNA/RNA entries) |
| Entries carrying a **recorded binding affinity** | **109** (all 109 are among the non-metal entries; none of the 9 metal or 26 peptide entries have one) |
| **INX recorded affinity** | **Ki = 0.25 µM (250 nM)** — Binding MOAD value for PDB **1g7g**, chain A, binding site BS01 (PubMed 11341829) |

**Supporting detail**

- The BioLiP web interface for P18031 states: *"Download all results in tab-separated text for 409 receptor-ligand interactions"*; the three paginated HTML result pages (200 + 200 + 9) and the `outfmt=txt` API download both yield 409 rows, and the raw `BioLiP.txt.gz` dump (AWS S3 `biolip` bucket, region ap-southeast-1) independently contains exactly 409 P18031 rows (all 409 carry UniProt = P18031; 326 distinct PDB IDs, 258 distinct ligand codes).
- Affinity source breakdown of the 109 affinity-bearing entries: Binding MOAD = 92, BindingDB = 70 (53 entries have both); manual-literature = 0 and PDBbind-CN = 0 (BioLiP removed 24,809 PDBbind-CN affinity records in January 2025 for licensing reasons, so PDBbind-CN-derived values are absent in this snapshot).
- Metal/non-metal assignment uses BioLiP's own ligand categories (`qsearch.cgi?lig3=metal` yields 60 metal CCD codes, including MG; `lig3=regular/peptide/rna/dna` the others) rather than an external heuristic. Note that "non-metal" here = regular + peptide + RNA + DNA ligands; if a narrower definition is intended (regular small molecules only), that number is **374**.
- Ligand identity: BioLiP's chemical-information endpoint (`sym.cgi?code=INX`) confirms INX has exactly **one** BioLiP entry, formula C30H37N3O10, i.e. the single 1g7g site above with Ki = 0.25 µM.

**Provenance / citations**
- Queried live BioLiP2 (Zhang Lab, University of Michigan / EMBL-EBI): `https://seq2fun.dcmb.med.umich.edu/BioLiP/qsearch.cgi?uniprot=P18031&outfmt=txt` and the HTML interface; raw data from `s3://biolip/BioLiP.txt.gz` (AWS Open Data registry entry "biolip").
- Yang J, Roy A, Zhang Y. *BioLiP: a semi-manually curated database for biologically relevant ligand-protein interactions.* Nucleic Acids Res. 2013;41(D1):D1096–D1103.
- Zhang C, Zhang X, Freddolino PL, Zhang Y. *BioLiP2: an updated structure database for biologically relevant ligand-protein interactions.* Nucleic Acids Res. 2024;52(D1):D404–D412 (doi:10.1093/nar/gkad630).

Caveat: these are snapshot-specific counts (current BioLiP2 release, 2025); they will change as new PDB structures/affinity data are curated.
=== END RUN rdhz24nqf7b ===

=== RUN rrqartfkqjq ===
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
BioLiP has **409 ligand-binding entries** for human PTP1B (**P18031**) across 326 PDB entries.

- **Non-metal ligands:** **400 entries**. The remaining 9 entries are magnesium (**MG**) records, using the stated metal-ion exclusion list.
- **Entries with a recorded binding affinity:** **92**, based on the non-empty `Affinity_Processed` field. (Only 70 have the separately populated normalized numeric `Affinity_Value` field.)
- **INX affinity:** **Ki = 0.25 µM** (equivalent to **250 nM**), recorded in PDB **1G7G**, chain **A**.

Source: BioLiP binding-site snapshot `/biolab_data/biolip/biolip.pkl`; all counts were independently reproduced through the provided `[TOOL]` function.
=== END RUN rrqartfkqjq ===

=== RUN rml902um86d ===
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
For human **ABL1 (UniProt P00519)** in ASD release 202306:

| Table | Result |
|---|---|
| **AP — allosteric-protein sites** | **225 site records** |
| **AP — distinct `pdb_id` values** | **59** |
| **HL — modulator records** | **84 records**, representing 84 distinct modulator IDs |
| **HL — activity type** | **IC50** for all 84 records |
| **HL — modulator feature** | **Inhibitor** for all 84 records |

A terminology nuance: of the 59 AP `pdb_id` values, **58 are conventional four-character RCSB PDB entries**; the other is `P00519-F1`, an AlphaFold-style model identifier represented by 10 AP rows. Thus the table-level count is **59 distinct identifiers**, while the strict RCSB-only count is **58 PDB entries**.

Source files:
- `/biolab_data/data_lake/ASD_Release_202306_AP.csv`
- `/biolab_data/data_lake/ASD_Release_202306_HL.csv`
=== END RUN rml902um86d ===

=== RUN rlm5cfo4j2k ===
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
## Counts in ASD release 202306

Filtering `ASD_Release_202306_AP.csv` for UniProt **P31749 (AKT1_HUMAN)** gives:

- **77 AP site-record rows**
- **32 distinct values in the AP table’s `pdb_id` column**

A numbering nuance: those 32 values consist of **31 conventional four-character PDB entries** plus the modeled-structure label **`P31749-F1`**. Thus, the table-level distinct-`pdb_id` count is **32**.

For **3O96**, the AP table contains one site record with 82 listed residues.

## Ligand and 4 Å contacts in 3O96 chain A

The bound non-polymer chemical component is:

- **IQO**
- Chemical name: **1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one**

Using heavy-atom minimum distances, the following **18 chain-A residues** lie within 4 Å of IQO. The numbers below are 3O96 author residue numbers; SIFTS maps these contacts to the corresponding canonical P31749 positions.

| Chain-A residue | Minimum distance | UniProt domain |
|---|---:|---|
| Trp80 | 3.41 Å | **PH**, residues 5–108 |
| Thr82 | 3.95 Å | **PH**, residues 5–108 |
| Val83 | 3.74 Å | **PH**, residues 5–108 |
| Ile84 | 3.46 Å | **PH**, residues 5–108 |
| Glu85 | 3.75 Å | **PH**, residues 5–108 |
| Ser205 | 2.89 Å | **Protein kinase**, residues 150–408 |
| Leu210 | 3.66 Å | **Protein kinase**, residues 150–408 |
| Thr211 | 3.58 Å | **Protein kinase**, residues 150–408 |
| Leu264 | 3.64 Å | **Protein kinase**, residues 150–408 |
| Lys268 | 3.26 Å | **Protein kinase**, residues 150–408 |
| Val271 | 3.90 Å | **Protein kinase**, residues 150–408 |
| Tyr272 | 3.11 Å | **Protein kinase**, residues 150–408 |
| Arg273 | 3.75 Å | **Protein kinase**, residues 150–408 |
| Asp274 | 3.83 Å | **Protein kinase**, residues 150–408 |
| Ile290 | 3.38 Å | **Protein kinase**, residues 150–408 |
| Thr291 | 3.97 Å | **Protein kinase**, residues 150–408 |
| Asp292 | 3.06 Å | **Protein kinase**, residues 150–408 |
| Cys296 | 3.15 Å | **Protein kinase**, residues 150–408 |

In summary:

- **PH-domain contacts:** W80, T82, V83, I84, E85
- **Protein-kinase contacts:** S205, L210, T211, L264, K268, V271, Y272, R273, D274, I290, T291, D292, C296
- **AGC-kinase C-terminal contacts:** none

The relevant UniProt domain features are **PH (5–108)**, **Protein kinase (150–408)**, and **AGC-kinase C-terminal (409–480)**.

**Sources checked:** ASD release-202306 AP table, BioLiP ligand records, RCSB 3O96 coordinates and chemical-component metadata, RCSB/PDBe SIFTS residue mapping, and the UniProt P31749 domain-feature record.
=== END RUN rlm5cfo4j2k ===

=== RUN rpj0yim2cbs ===
QUESTION:
For the apo structure of PDB 6HB0 chain A, which ten residues does the PocketMiner model score highest for cryptic-pocket propensity, what is the score of the highest-ranked residue, and how many of the published cryptic-pocket residues of that structure fall among those ten? Name the overlapping residues.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X04_a] [critical] [scripted] {"residues": [53, 52, 234, 208, 262, 281, 54, 264, 261, 284]}
[X04_b] [critical] [scripted] 0.926939
[X04_c] [critical] [scripted] 5
[X04_d] [critical] [scripted] {"residues": [52, 53, 208, 234, 262]}
[X04_e] [critical] [scripted] 15

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
For **apo PDB 6HB0, chain A**, PocketMiner’s ten highest-scoring residues are:

| Rank | Residue | Cryptic-pocket propensity |
|---:|---|---:|
| 1 | **ARG53** | **0.93** |
| 2 | TRP52 | 0.90 |
| 3 | PHE208 | 0.89 |
| 4 | ASN234 | 0.89 |
| 5 | ASP262 | 0.88 |
| 6 | THR54 | 0.86 |
| 7 | GLU281 | 0.86 |
| 8 | VAL261 | 0.85 |
| 9 | THR264 | 0.85 |
| 10 | PRO284 | 0.85 |

- **Highest-ranked residue:** **ARG53**
- **Highest score:** **0.93**
- **Published cryptic-pocket residues represented in the top ten:** **5 of 15**
- **Overlapping residues:** **TRP52, ARG53, PHE208, ASN234, and ASP262**

The calculation used the authors’ cleaned apo structure `6hb0A_clean_h.pdb`, submitted to the official PocketMiner service, and compared the ranked residues with the `6hb0` validation labels from the PocketMiner dataset, where label `1` denotes residues forming the cryptic pocket in the corresponding holo structure.

**Sources**
- Meller et al., *Predicting locations of cryptic pockets from single protein structures using the PocketMiner graph neural network*, **Nature Communications** 14, 1177 (2023), DOI: **10.1038/s41467-023-36699-3**.
- PocketMiner implementation and validation data: **https://github.com/Mickdub/gvp/tree/pocket_pred**
- PDB 6HB0: **https://www.rcsb.org/structure/6HB0**
- Original 6HB0 structure publication: Li et al., *Cell Chemical Biology* 26, 852–863 (2019), DOI: **10.1016/j.chembiol.2019.03.002**.

*Scores are reported at the two-decimal precision returned by the official PocketMiner service.*
=== END RUN rpj0yim2cbs ===

=== RUN r8l54d81ig1 ===
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
### Result

Using the **pinned ClinVar release**, **10 variants** satisfy all three criteria:

1. classified in the pinned release as pathogenic or likely pathogenic;
2. AlphaMissense score **> 0.9**; and
3. at least one heavy atom of the variant’s residue lies within **8 Å** of an SHP099 heavy atom in **PDB 5EHR chain A**.

| Variant | ClinVar variation ID | Pinned classification | AlphaMissense score | Nearest heavy-atom distance | Minimizing atom pair |
|---|---:|---|---:|---:|---|
| NM_002834.5(PTPN11):c.328G>A (p.Glu110Lys) | [40507](https://www.ncbi.nlm.nih.gov/clinvar/variation/40507/) — VCV000040507 | Pathogenic/Likely pathogenic | 0.9908 | **3.4650 Å** | Glu110 O – SHP099 N22 |
| NM_002834.5(PTPN11):c.329A>C (p.Glu110Ala) | [40508](https://www.ncbi.nlm.nih.gov/clinvar/variation/40508/) — VCV000040508 | Pathogenic/Likely pathogenic | 0.9621 | **3.4650 Å** | Glu110 O – SHP099 N22 |
| NM_002834.5(PTPN11):c.330A>C (p.Glu110Asp) | [561745](https://www.ncbi.nlm.nih.gov/clinvar/variation/561745/) — VCV000561745 | Likely pathogenic | 0.9630 | **3.4650 Å** | Glu110 O – SHP099 N22 |
| NM_002834.5(PTPN11):c.772G>A (p.Glu258Lys) | [982429](https://www.ncbi.nlm.nih.gov/clinvar/variation/982429/) — VCV000982429 | Likely pathogenic | 0.9988 | **6.6297 Å** | Glu258 N – SHP099 CL2 |
| NM_002834.5(PTPN11):c.774G>T (p.Glu258Asp) | [44613](https://www.ncbi.nlm.nih.gov/clinvar/variation/44613/) — VCV000044613 | Pathogenic/Likely pathogenic | 0.9577 | **6.6297 Å** | Glu258 N – SHP099 CL2 |
| NM_002834.5(PTPN11):c.1472C>A (p.Pro491His) | [40551](https://www.ncbi.nlm.nih.gov/clinvar/variation/40551/) — VCV000040551 | Pathogenic/Likely pathogenic | 0.9611 | **3.4540 Å** | Pro491 CB – SHP099 N7 |
| NM_002834.5(PTPN11):c.1472C>T (p.Pro491Leu) | [40552](https://www.ncbi.nlm.nih.gov/clinvar/variation/40552/) — VCV000040552 | Pathogenic/Likely pathogenic | 0.9431 | **3.4540 Å** | Pro491 CB – SHP099 N7 |
| NM_002834.5(PTPN11):c.1493G>A (p.Arg498Gln) | [1805026](https://www.ncbi.nlm.nih.gov/clinvar/variation/1805026/) — VCV001805026 | Likely pathogenic | 0.9993 | **7.1542 Å** | Arg498 NH1 – SHP099 CL2 |
| NM_002834.5(PTPN11):c.1492C>T (p.Arg498Trp) | [40553](https://www.ncbi.nlm.nih.gov/clinvar/variation/40553/) — VCV000040553 | Pathogenic | 0.9998 | **7.1542 Å** | Arg498 NH1 – SHP099 CL2 |
| NM_002834.5(PTPN11):c.1493G>T (p.Arg498Leu) | [40554](https://www.ncbi.nlm.nih.gov/clinvar/variation/40554/) — VCV000040554 | Pathogenic | 0.9995 | **7.1542 Å** | Arg498 NH1 – SHP099 CL2 |

### Method and provenance

- **ClinVar:** The pinned export was `pub/clinvar/clinvar_result.txt` in the [Zenodo companion archive 10951364](https://zenodo.org/records/10951364), with ZIP-member date **2023-11-16**. Its classifications were verified directly against NCBI’s dated [`variant_summary_2023-11.txt.gz`](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/2023/variant_summary_2023-11.txt.gz) archive.
- **AlphaMissense:** Scores came from the official [`AlphaMissense_hg38.tsv.gz`](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz) release for UniProt **Q06124**. All 122 pinned P/LP PTPN11 missense records joined to a unique AlphaMissense protein substitution and score. ClinVar Canonical SPDI positions are 0-based, so they were converted to the AlphaMissense 1-based positions by adding one.
- **Structure:** In [PDB 5EHR](https://www.rcsb.org/structure/5EHR), SHP099 is component **5OD**, chain A residue 601, with 23 heavy atoms. Chain A was aligned to UniProt Q06124; the relevant residues are observed and retain the same residue numbering.
- **Distance:** For each residue, the distance is the minimum Euclidean distance between any protein-residue heavy atom and any SHP099 heavy atom. Hydrogens, waters, alternate heteroatoms, and phosphate ions were excluded. As a boundary check, the next-nearest score-qualified residue was Asp106 at **8.7546 Å**, and was therefore excluded.

This is intentionally the **pinned-release** answer. For example, the live service currently classifies **561745 (E110D), 44613 (E258D), and 982429 (E258K)** as conflicting; they remain in the table because the pinned release classifies them as pathogenic/likely pathogenic or likely pathogenic.

### Analysis checklist

1. [✓] Located and verified the pinned ClinVar and AlphaMissense release sources.
2. [✓] Extracted all 385 pinned PTPN11 records and 122 pathogenic/likely pathogenic missense records.
3. [✓] Joined every record to its Q06124 AlphaMissense score.
4. [✓] Identified SHP099 as 5OD A601 and verified chain-A/Q06124 residue mapping.
5. [✓] Calculated and independently recomputed all heavy-atom distances.
6. [✗] Initial coordinate checks used inconsistent SPDI/AlphaMissense coordinate and chromosome normalization; corrected by converting SPDI to 1-based `chr12` coordinates and verifying every selected AlphaMissense protein-key row directly.
7. [✓] Verified the final classifications against the NCBI 2023-11 archive and prepared the requested table.
=== END RUN r8l54d81ig1 ===

=== RUN rkws8ntoflh ===
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
Updated plan:
1. [✓] Search the local data lake and workspace for release `202306` files.
2. [✗] Initial endpoint-inspection script failed because of a malformed Python string literal.
3. [✓] Retry with corrected parsing and resolve the official archive path.
4. [✓] Download and verify the official AP and HL release archives.
5. [✓] Filter AP for human ABL1 (`P00519`) and count records and PDB identifiers.
6. [✓] Filter HL for ABL1 and count records and category values.
7. [✓] Cross-check the counts and prepare the release-specific result.

## Results

### AP — allosteric-protein/site table

For `uniprot_id = P00519`:

- **Site records:** **225**
- **Distinct `pdb_id` values:** **59**

Of the 59 identifiers, **58 are conventional four-character PDB IDs** and one is `P00519-F1`, an AlphaFold-style model identifier. Thus, the raw table’s distinct-`pdb_id` count is **59**; the count restricted strictly to conventional PDB IDs is **58**.

### HL — hit-and-lead table

For `UniProt_ID = P00519`:

- **Modulator records:** **84**
- **Unique modulator IDs:** **84**
- **Activity type:** **IC50** for all 84 records
- **Modulator feature:** **Inhibitor** for all 84 records

**Concise answer:** AP holds **225 site records across 59 distinct `pdb_id` values**; HL holds **84 ABL1 modulator records**, all classified as **IC50 activity** and **Inhibitor** modulators.

Source: official ASD **Release 5.01 (202306)** archives:
- `ASD_Release_202306_AP.tar.gz`
- `ASD_Release_202306_HL.tar.gz`

Database paper: He et al., *ASD2023: towards the integrating landscapes of allosteric knowledgebase*, DOI [10.1093/nar/gkad915](https://doi.org/10.1093/nar/gkad915).
=== END RUN rkws8ntoflh ===

=== RUN rfge78ab3w8 ===
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
### ASD release 202306 — human ABL1 (P00519)

**Allosteric-protein table (AP)**  
Source: `ASD_Release_202306_AP.csv`, filtered on `uniprot_id == "P00519"`

- **Site records:** **225 AP rows**
- **Distinct `pdb_id` values:** **59**
  - **58** are canonical four-character PDB IDs.
  - The remaining value is the noncanonical structure label **`P00519-F1`**, covering 10 of the 225 rows.
  - Therefore, if “PDB entries” is interpreted strictly as canonical RCSB PDB IDs, the count is **58**; the table-level distinct-`pdb_id` count is **59**.

**Hit-and-lead table (HL)**  
Source: `ASD_Release_202306_HL.csv`, filtered on `UniProt_ID == "P00519"`

- **Modulator records:** **84** rows, representing **84 distinct `Modulator_ID`s**
- **Activity type:** **IC50** in all **84/84** records
- **Modulator feature:** **Inhibitor** in all **84/84** records

In short: **225 AP site records across 59 distinct `pdb_id` values** (58 literal PDB entries plus `P00519-F1`), and **84 HL modulators, uniformly annotated as IC50 inhibitors**.
=== END RUN rfge78ab3w8 ===

=== RUN rk6kj8ux2jw ===
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
### Result

Using the **pinned local ClinVar release** (`mode="local"`; SHA-256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`), the qualifying variants are:

| Variant | Protein change | ClinVar Variation ID | Pinned classification | AlphaMissense score | Nearest heavy-atom distance to SHP099 |
|---|---:|---:|---|---:|---:|
| NM_002834.5(PTPN11):c.329A>C | p.Glu110Ala (E110A) | 40508 | Pathogenic/Likely pathogenic | 0.9621 | 3.47 Å |
| NM_002834.5(PTPN11):c.328G>A | p.Glu110Lys (E110K) | 40507 | Pathogenic/Likely pathogenic | 0.9908 | 3.47 Å |
| NM_002834.5(PTPN11):c.1472C>A | p.Pro491His (P491H) | 40551 | Pathogenic/Likely pathogenic | 0.9611 | 3.45 Å |
| NM_002834.5(PTPN11):c.1472C>T | p.Pro491Leu (P491L) | 40552 | Pathogenic | 0.9431 | 3.45 Å |
| NM_002834.5(PTPN11):c.1493G>T | p.Arg498Leu (R498L) | 40554 | Pathogenic | 0.9995 | 7.15 Å |
| NM_002834.5(PTPN11):c.1493G>A | p.Arg498Gln (R498Q) | 1805026 | Likely pathogenic | 0.9993 | 7.15 Å |
| NM_002834.5(PTPN11):c.1492C>T | p.Arg498Trp (R498W) | 40553 | Pathogenic/Likely pathogenic | 0.9998 | 7.15 Å |

### Provenance and filtering

- PDB **5EHR chain A** maps to **PTPN11/Q06124**. The official PDB record identifies component **5OD** as **SHP099**.
- Distances are minimum heavy-atom separations from each PTPN11 residue to any SHP099 heavy atom, calculated with an 8 Å cutoff.
- AlphaMissense values came from the pinned local release whose manifest SHA-256 is `bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d`; the sidecar index records the same source hash.
- Only an affirmative pinned classification of **Pathogenic**, **Likely pathogenic**, or **Pathogenic/Likely pathogenic** was retained. Records labeled **“Conflicting classifications of pathogenicity”** were excluded.
- The strict **score > 0.9** threshold was applied; for example, P491T scored 0.8966 and was excluded.

### Completed plan

1. [✗] Initial pinned ClinVar query (failed because `max_results=0` returns an empty list)
2. [✓] Queried the local pinned ClinVar release for pathogenic and likely pathogenic records
3. [✓] Identified 5OD as SHP099 and retrieved all chain-A residues within 8 Å
4. [✗] First intersection attempt (failed because the parser used the wrong HGVS title pattern)
5. [✓] Parsed the pinned three-letter protein substitutions and intersected them with contact residues
6. [✗] Batched AlphaMissense wrapper query (failed because repeated full-file scans exceeded the execution limit)
7. [✗] Single-position wrapper retry (failed for the same reason)
8. [✓] Diagnosed and bypassed the wrapper issue using the manifest-hash-matched pinned sidecar index
9. [✗] Combined audit scripts (failed with empty process records; replaced by minimal diagnostics)
10. [✓] Reconfirmed all qualifying ClinVar records and applied the strict AlphaMissense threshold
11. [✓] Verified the 5OD/SHP099 alias and reported the final records
=== END RUN rk6kj8ux2jw ===

=== RUN rtevbbsnof7 ===
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

The myristoyl-site ligand in PDB **5MO4** is **asciminib**, represented by RCSB ligand code **AY7**. ChEMBL explicitly lists `AY7` as an asciminib synonym, and the structures share InChIKey `VOVZXURTCKPRDQ-CQSZACIVSA-N`.

- **ChEMBL identifier:** `CHEMBL4208229`
- **PubChem identifier:** CID `72165228`

### BioLiP-curated binding site in chain A

BioLiP site **BS02** lists these chain-A residues in PDB/author numbering:

**L359, L360, I451, A452, T453, E481, C483, P484, V487, I521, V525**

The corresponding UniProt ABL1 (`P00519`) numbering is:

**L275, L276, I349, A350, T351, E379, C381, P382, V385, I419, V423**

### Lowest IC50 against ABL1

The pinned local **ChEMBL 37** release at `/data/chembl/chembl_37_sqlite/chembl_37.db` returned two IC50 records for `CHEMBL4208229` against `CHEMBL1862`: **0.5 nM** and **16 nM**.

- **Lowest IC50:** **0.5 nM**
- **Relation:** `=`
- **Activity ID:** `18557369`
- **Assay ID:** `CHEMBL4200739`
- **Target:** ABL1 / `CHEMBL1862`

### Completed plan
1. [✓] Retrieved 5MO4 chain-A BioLiP ligands and interaction rows; identified `AY7` as the myristoyl-site ligand.
2. [✓] Cross-referenced `AY7`/asciminib to ChEMBL and PubChem identifiers.
3. [✓] Queried the pinned ChEMBL 37 IC50 records and selected the numeric minimum.
4. [✓] Reported identifiers, BioLiP binding-site residues, and lowest IC50 with provenance.
=== END RUN rtevbbsnof7 ===

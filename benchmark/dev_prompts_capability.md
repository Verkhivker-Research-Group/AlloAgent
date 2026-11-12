# Arm D capability-gate prompts (6, development set only)

These six prompts are the **capability gate** for the benchmark launch.
They use only the four **development** proteins (FBP1, PKM2, p38 alpha,
PDK1) - **no protein that appears in the 40 benchmark prompts is used
here**, and none of the benchmark checklists is touched.

Every prompt needs something that only arm D has:

* the **PocketMiner** cryptic-pocket model (a local TensorFlow model in
  `pocketminer_env`),
* the **STINGAllo** allosteric-site prediction service,
* the **local ChEMBL 37 SQLite** (29 GB) and the **local ClinVar /
  AlphaMissense release files** with their sidecar indexes.

Arm A (the baseline) has none of these: no PocketMiner, no STINGAllo
access, no local database.  The gate asks whether arm D actually turns
that into answers, and whether arm A fails them.

## The prompts

| # | id | prompt | tools it should reach for |
|---|---|---|---|
| 1 | D1 | "In PDB entry 7WVB (human fructose-1,6-bisphosphatase 1, UniProt P09467, the ligand-free R-state structure), score every residue with PocketMiner. Then tell me the PocketMiner score of each of the fifteen residues that contact AMP in the allosteric site of PDB entry 1FTA (UniProt numbering), and the mean PocketMiner score of that set against the mean over all scored residues." | PocketMiner wrapper; structure code |
| 2 | D2 | "For p38 alpha MAP kinase (UniProt Q16539) in PDB entry 1KV2 chain A, which residues does STINGAllo predict as allosteric, how many of them lie within 4 angstroms of the bound allosteric inhibitor BIRB 796 (ligand ID B96), and what is the chance-level overlap for that number of predictions in a chain of this size?" | STINGAllo; structure code |
| 3 | D3 | "Using the local ChEMBL 37 database, compare the two allosteric p38 MAP kinase inhibitors: BIRB 796 (DORAMAPIMOD, CHEMBL103667) and AMG-548 (CHEMBL585902). For each, against human p38 alpha (UniProt Q16539), give the number of IC50 records, their median and their best value." | get_chembl_bioactivity |
| 4 | D4 | "For human fructose-1,6-bisphosphatase 1 (UniProt P09467), report the ClinVar classification and the AlphaMissense score of the variants G164S and A177D, and the distance from each of those residues to the AMP allosteric site of PDB entry 1FTA (chain A)." | get_clinvar_variants; get_alphamissense_score; structure code |
| 5 | D5 | "For human pyruvate kinase PKM2 (UniProt P14618) in PDB entry 3GQY, identify the allosteric activator and list the residues within 4 angstroms of it in UniProt numbering. Then give the AlphaMissense score of the substitution D354M at one of those residues, and say whether STINGAllo predicts any of those contact residues for chain A of 3GQY, with the chance-level overlap." | structure code; get_alphamissense_score; STINGAllo |
| 6 | D6 | "For human fructose-1,6-bisphosphatase 1 (UniProt P09467): compare three independent predictions of the AMP allosteric site in PDB entry 1FTA chain A - the residues within 4 angstroms of AMP, the residues STINGAllo predicts, and the PocketMiner scores of the AMP-contacting residues in the ligand-free structure 7WVB. Report both overlaps against the contact set and the chance base rate for the STINGAllo overlap." | structure code; STINGAllo; PocketMiner wrapper |

## Expected answers (committed BEFORE the runs)

Derived from the primary sources on 2026-10-25: the RCSB mmCIF files
(`files.rcsb.org/download/<id>.cif`), the RCSB Data API SIFTS
alignments, the UniProt REST API, the ChEMBL 37 SQLite by direct SQL,
the pinned ClinVar release file (`data/clinvar/variant_summary.txt.gz`,
sha256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`),
the pinned AlphaMissense release file
(`data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz`, sha256
`bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d`)
and the STINGAllo service (response date 2026-10-25).  The PocketMiner
numbers are a **reference output** of the local model, not ground truth
about the protein.

### D1 - PocketMiner on the apo FBP1 structure

* 7WVB is "Human Fructose-1,6-bisphosphatase 1 mutant R50A in APO
  R-state" - no non-polymer ligand at all.
* The AMP site of 1FTA (chain A) has **15** contacts within 4 A, in
  UniProt numbering: **18, 21, 22, 25, 27, 28, 29, 30, 31, 32, 113,
  114, 141, 161, 178**.
* PocketMiner on 7WVB (1165 scored residues) gives, at those positions:

  | UniProt | score | rank in 7WVB |
  |---|---|---|
  | 18 | 0.6251 | 114 |
  | 21 | 0.4704 | 187 |
  | 22 | not scored | - |
  | 25 | not scored | - |
  | 27 | not scored | - |
  | 28 | not scored | - |
  | 29 | 0.5525 | 154 |
  | 30 | 0.3368 | 250 |
  | 31 | 0.7305 | 63 |
  | 32 | 0.7813 | 44 |
  | 113 | 0.4816 | 184 |
  | 114 | 0.4516 | 197 |
  | 141 | 0.5697 | 143 |
  | 161 | 0.5020 | 175 |
  | 178 | 0.6745 | 91 |

* mean score over the **11 scored** AMP-contact residues: **0.5615**;
  mean over **all 1165** scored residues: **0.5488**.
* Scoring: correct if the contact count (15) and the contact set are
  right, the mean at the contacts is **0.5615 +/- 0.02**, the mean over
  all residues is **0.5488 +/- 0.02**, and at least 8 of the 11
  per-residue scores are within +/- 0.01.

### D2 - STINGAllo on p38 alpha

* STINGAllo for 1KV2 chain A (2026-10-25): **["106", "75"]** - two
  residues.
* The B96 (BIRB 796) contacts within 4 A in chain A: **19** residues,
  UniProt numbering **38, 51, 53, 67, 71, 74, 75, 78, 84, 104, 106,
  108, 109, 110, 148, 166, 167, 168, 169**.
* Overlap: **2** (both predicted residues, 75 and 106, are contacts).
* Chance level: 2 predicted x 19 contacts / 325 modelled chain-A
  residues = **0.117** expected overlaps by chance, i.e. an enrichment
  of about **17x**.
* Scoring: correct if the two predicted residues and the overlap of 2
  are right and the chance-level expectation is within 0.05 of 0.117.

### D3 - the local ChEMBL records for the two p38 allosteric inhibitors

| compound | ChEMBL id | target | IC50 rows | median | best | units |
|---|---|---|---|---|---|---|
| DORAMAPIMOD (BIRB 796) | CHEMBL103667 | CHEMBL260 (p38 alpha, Q16539) | **21** | **17 nM** | **0.1 nM** | nM |
| AMG-548 | CHEMBL585902 | CHEMBL260 | **2** | **75 nM** | **35 nM** | nM |

* Scoring: correct if both row counts are right (21 and 2) and both
  medians are within a factor of two (17 nM and 75 nM).

### D4 - the two FBP1 variants at the AMP site

| variant | ClinVar (pinned release) | VariationID | AlphaMissense | class | distance to AMP in 1FTA chain A |
|---|---|---|---|---|---|
| G164S (Gly164Ser) | **Pathogenic/Likely pathogenic** | 15907 | **0.8159** | pathogenic | **12.679 A** |
| A177D (Ala177Asp) | **Pathogenic** | 15908 | **0.9670** | pathogenic | **8.510 A** |

* Neither residue is an AMP contact (the nearest contacts are V161 at
  3.663 A and M178 at 3.871 A).
* Scoring: correct if both classifications are right, both AlphaMissense
  scores are within 0.01, and both distances are within 0.5 A.

### D5 - the PKM2 allosteric activator pipeline

* The allosteric activator of 3GQY is **DZG** (the PDB component id;
  its chemical name is
  1-(2,3-dihydro-1,4-benzodioxin-6-ylsulfonyl)-4-[(4-methoxyphenyl)sulfonyl]piperazine,
  i.e. the TEZ-165 series), bound at **chain B, residue 540** (and chain
  C).
* Its 4 A contacts in chain B, UniProt numbering: **26, 27, 30, 318,
  353, 354, 390, 393, 394, 397** (10 residues; ASP354 is the closest
  at 3.194 A).
* AlphaMissense for the substitution **D354M** at that residue:
  **0.9998**, class **pathogenic**.
* STINGAllo for 3GQY chain A: **["431", "482", "514", "520", "522",
  "70"]** (6 residues); **none** of them is a contact residue (the
  overlap is **0**); chain A has 514 modelled residues, so the chance
  level is 6 x 10 / 514 = **0.117** expected overlaps.
* Scoring: correct if the activator is identified (DZG, chain B 540),
  the 10 contact residues are right, D354M = 0.9998 +/- 0.01, and the
  STINGAllo overlap is 0 with the chance level near 0.117.

### D6 - three independent predictions of the FBP1 AMP site

* The AMP contacts of 1FTA chain A: the same 15 residues as in D1.
* STINGAllo for 1FTA chain A: **["112", "17", "177", "26", "27", "274",
  "29", "30"]** (8 residues); the overlap with the contact set is
  **3** (residues **27, 29, 30**); chain A has 319 modelled residues,
  so the chance level is 8 x 15 / 319 = **0.376** expected overlaps
  (an enrichment of about 8x).
* PocketMiner on the apo structure 7WVB: the scores at the 15 contact
  positions are the D1 table above (11 of 15 scored; the mean over the
  contacts is 0.5615 against 0.5488 over all residues) - i.e. the
  cryptic-pocket model shows **no enrichment** at the known AMP site,
  while STINGAllo does.
* Scoring: correct if both contact sets are right, the STINGAllo overlap
  is 3 with a chance level near 0.376, and the PocketMiner mean at the
  contacts (0.5615) is reported next to the overall mean (0.5488) -
  including the conclusion that the two methods disagree.

### What counts as a success

A prompt counts as a success for an arm when the final answer states
every value listed as "correct if" above, with no contradiction of the
committed facts.  An answer that invents a value that the trace does
not support counts as a failure, and an explicit statement that a
resource is unavailable is acceptable only when the resource really is
unavailable.

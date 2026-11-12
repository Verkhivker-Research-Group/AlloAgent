# Arm D capability gate 2 - six development prompts on the four development proteins

Gate 2 asks the harder question gate 1 did not: can arm D use the
**local curated data** (the ASD release, the BioLiP snapshot, the pinned
ChEMBL 37 / ClinVar / AlphaMissense releases) where the **baseline arm
cannot**?

The four development proteins are FBP1 (P09467), PKM2 (P14618), p38 alpha
(Q16539) and PDPK1 (O15530).  **No protein that appears in the 40
benchmark prompts is used here**, and no benchmark prompt or checklist is
touched.  (Correction to the previous report: 2PE0 is **PDPK1**
(UniProt O15530), not PTPN11 - the earlier report mislabelled it; the
SIFTS accession of 2PE0 is O15524/O15530 = PDPK1 = the human PDK1
kinase, and the ASD record for it is ASD00060000_1.)

Arm A for this gate runs the **upstream baseline worktree with no
`/data` mounts and no `pocketminer_env`**, with internet allowed.

## The prompts

| # | id | prompt | the resource it needs |
|---|---|---|---|
| 1 | D1 | "The Allosteric Database annotates human fructose-1,6-bisphosphatase 1 (UniProt P09467) as an allosteric protein. From the ASD release, list the allosteric modulators it records for FBP1, giving for each the PDB entry it was seen in and the modulator residue number, and give the record's headline counts: annotated allosteric sites, allosteric activators, allosteric inhibitors and allosteric regulators." | the local ASD release (the bulk download needs a login) |
| 2 | D2 | "For PDB entry 1KV2 (human p38 alpha MAP kinase, UniProt Q16539), what does BioLiP record: which ligand, in which protein chain, what are its binding-site residues, and what is the catalytic site?" | the local BioLiP snapshot (the per-entry export is not served as data) |
| 3 | D3 | "The ASD records the allosteric modulator B96 (BIRB 796) for human p38 alpha (UniProt Q16539) in entry 1KV2 at residue 391. What is its ChEMBL identity, how many IC50 records does ChEMBL 37 hold against p38 alpha, what are their median and best value, and which residues of 1KV2 does B96 contact within 4 angstroms?" | the local ASD release + the pinned ChEMBL 37 + the coordinates |
| 4 | D4 | "For the p38 alpha allosteric site in 1KV2: compare the binding-site residues BioLiP records with the residues within 4 angstroms of the B96 ligand in the deposited coordinates - which residues are in the coordinates but not in the BioLiP site list? - and give the ChEMBL 37 IC50 count, median and best value for BIRB 796 against p38 alpha." | BioLiP + the pinned ChEMBL 37 + the coordinates (three sources) |
| 5 | D5 | "For human fructose-1,6-bisphosphatase 1 (UniProt P09467): report the ClinVar classification and the AlphaMissense score of the variants G164S and A177D, and the distance from each of those residues to the AMP allosteric site of PDB entry 1FTA (chain A). Are the two residues part of the AMP site?" | the pinned ClinVar and AlphaMissense releases |
| 6 | D6 | "For the FBP1 allosteric site: ASD records AMP as an allosteric regulator of FBP1 in entry 1FTA at residue 338, and BioLiP records AMP in 1FTA with a binding-site residue list. Give the BioLiP binding-site residues in PDB numbering and in UniProt numbering, the number of residues within 4 angstroms of AMP in the coordinates, and the residues the two sources share." | the local ASD release + BioLiP + the coordinates (three sources) |

## Expected answers (committed BEFORE the runs)

Read directly from the local files on 2026-10-25:
`/biolab_data/data_lake/ASD_Release_202309_AS.csv` (the ASD allosteric-site
release), `/biolab_data/asd/ASD_Release_202306_XF.zip` (the ASD
cross-reference records), the BioLiP snapshot, and the pinned
`/data/chembl/chembl_37_sqlite/chembl_37.db`,
`/data/clinvar/variant_summary.txt.gz` and
`/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz`.  The second
source for each answer is given in brackets.

### D1 - the ASD record for FBP1

* target id **ASD01120000_1** (UniProt P09467, FBP1, *Homo sapiens*);
  the AS release has **36** FBP1 rows;
* headline counts from the XF record: **15** annotated allosteric sites,
  **2** allosteric activators, **521** allosteric inhibitors, **1**
  allosteric regulator;
* the modulators and their entries / modulator residues (the first rows
  of the release): **AMP 1FTA 338**, **A37 2FHY**, **A74 2FIE**,
  **870 2FIX**, **R15 2JJK**, **ROK 2VT5**, **RO3 2WBB**, **RO5 2WBD**,
  **YCU 2Y5K**, **RO8 2Y5L**, **2T0 3A29**, **2T4 3KBZ**, **2T5 3KC0**,
  **2T6 3KC1** (36 rows in total, all chain A).
  [second source: the RCSB entry titles, e.g. 1FTA is FBP1 with AMP]

### D2 - the BioLiP record for 1KV2

* ligand **B96**, protein chain **A**, `total_interactions` **1**;
* binding-site residues (PDB numbering): **V38 R67 E71 L75 T106 L108 M109
  G110 H148 L167 D168 F169** (13);
* BioLiP's own UniProt column for the same site: **V34 R63 E67 L71 T102
  L104 M105 G106 H136 L155 D156 F157**;
* catalytic site (PDB numbering) starts **D150**; the record's resolution is
  2.8 A.
  [second source: the coordinates - the residues within 4 A of B96 in
  1KV2 chain A are the 19 residues listed under D3]

### D3 - ASD x ChEMBL x the structure for p38 alpha

* the ASD row: modulator **B96**, allosteric PDB **1KV2**, modulator
  chain A, modulator residue **391**, ASD serial **ASD00740009**, target
  **ASD03490000_1**, `site_overlap` **Yes**;
* ChEMBL identity: **DORAMAPIMOD** = **CHEMBL103667** (BIRB 796), target
  **CHEMBL260** (human MAPK14, SINGLE PROTEIN, UniProt Q16539);
* ChEMBL 37 IC50 records: **21** (all `standard_relation` "=", units nM),
  median **17 nM**, best **0.1 nM**;
* the 4 A contacts of B96 in 1KV2 chain A (UniProt numbering): **38, 51,
  53, 67, 71, 74, 75, 78, 84, 104, 106, 108, 109, 110, 148, 166, 167,
  168, 169** (19 residues).
  [second source: the RCSB SIFTS alignment of 1KV2 (Q16539) for the
  numbering, and the deposited SITE record for the site list]

### D4 - the three-source pipeline for the p38 alpha site

* BioLiP's 13 site residues (PDB): V38 R67 E71 L75 T106 L108 M109 G110
  H148 L167 D168 F169;
* the 4 A contacts (PDB numbering, from the coordinates): 38, 51, 53, 67,
  71, 74, 75, 78, 84, 104, 106, 108, 109, 110, 148, 166, 167, 168, 169
  (19);
* the residues in the coordinates but **not** in the BioLiP list: **51, 53,
  78, 84, 104, 166** (6);
* ChEMBL 37 for BIRB 796: **21** IC50 records, median **17 nM**, best
  **0.1 nM**.
  [second source: the coordinates for the contact set, the ChEMBL REST API
  for the same molecules]

### D5 - the two FBP1 variants at the AMP site

| variant | ClinVar (pinned release) | VariationID | AlphaMissense | class | distance to AMP, 1FTA chain A |
|---|---|---|---|---|---|
| G164S (Gly164Ser) | **Pathogenic/Likely pathogenic** | 15907 | **0.8159** | pathogenic | **12.679 A** |
| A177D (Ala177Asp) | **Pathogenic** | 15908 | **0.9670** | pathogenic | **8.510 A** |

* Neither is an AMP contact: the nearest AMP contacts are V161 (3.663 A)
  and M178 (3.871 A) in UniProt numbering.
  [second source: the UniProt REST record of P09467 and the coordinates]

### D6 - the three-source pipeline for the FBP1 AMP site

* ASD: modulator **AMP**, allosteric PDB **1FTA**, chain A, modulator
  residue **338**, target **ASD01120000_1**, `function` "Inner Protein
  Regulator", `site_overlap` **No**;
* BioLiP for 1FTA: ligand **AMP**, `total_interactions` **4**, protein
  chains **A, B, C, D**, uniprot **P09467**; the binding-site residues
  (PDB numbering) **V17 E20 G21 A24 G26 T27 G28 E29 L30 T31 K112 Y113**
  (12); BioLiP's own UniProt column for the same site **V9 E12 G13 A16 G18
  T19 G20 E21 L22 T23 K96 Y97** - i.e. **9 lower** than the canonical
  UniProt numbering, and the chain-A UniProt numbers of the same
  residues are 18, 21, 22, 25, 27, 28, 29, 30, 31, 32, 113, 114;
* the coordinates: **15** residues within 4 A of AMP in 1FTA chain A
  (UniProt **18, 21, 22, 25, 27, 28, 29, 30, 31, 32, 113, 114, 141,
  161, 178**; PDB **17, 20, 21, 24, 26, 27, 28, 29, 30, 31, 112, 113,
  140, 160, 177**);
* the residues the two sources share: all **12** of the BioLiP site
  residues (PDB numbering 17, 20, 21, 24, 26, 27, 28, 29, 30, 31, 112,
  113); the coordinates add three more (140, 160, 177).
  [second source: the coordinates for the contact set, the RCSB SITE
  record of 1FTA for the site list]

### What counts as a success

A prompt counts as a success for an arm when the final answer states
every value listed above, with no contradiction of the committed facts,
and does not assert a value the trace does not support.  An explicit
statement that a resource is unavailable counts as a success only when
the resource really is unavailable to that arm.

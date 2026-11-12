# Judge batch 019 of 24

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

=== RUN rpcwrjcl5vf ===
QUESTION:
For TEM-1 beta-lactamase (UniProt P62593), predict cryptic-pocket residues from 1BTL with PocketMiner, retrieve UniProt variants, and list every annotated variant position within 6 angstroms of a residue that contacts the allosteric inhibitor in PDB 1PZO.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V06_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[V06_b] [critical] [judged] the PocketMiner cryptic-pocket residues of 1BTL, the UniProt variants of TEM-1 and every annotated variant within 6 A of a 1PZO CBT-contact residue are listed

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

Using **minimum heavy-atom distances** in PDB 1PZO, the annotated UniProt P62593 variant positions within **6.0 Å of a residue that contacts the allosteric inhibitor CBT** are:

| UniProt position | Variant | 1PZO residue | PocketMiner probability from 1BTL | Nearest CBT-contacting residue | Distance | Direct CBT contact? |
|---:|---|---|---:|---|---:|:---:|
| **67** | M→L | Met69 | 0.755940 | Arg244 | 3.335 Å | No |
| **235** | A→T | Ala237 | 0.892082 | Ala237 | 0.000 Å | **Yes** |
| **236** | G→S | Gly238 | 0.812030 | Ala237 | 1.337 Å | No |
| **237** | E→K | Glu240 | 0.790595 | Ala237 | 4.789 Å | No |
| **261** | T→M | Thr265 | 0.765603 | Arg244 | 2.905 Å | No |
| **272** | N→D | Asn276 | 0.869319 | Asn276 | 0.000 Å | **Yes** |

Therefore, the complete requested position list is:

**UniProt P62593: 67, 235, 236, 237, 261, and 272.**

## PocketMiner prediction

- Ran the published PocketMiner GVP-GNN using the official `Mickdub/gvp` `pocket_pred` branch and the official `models/pocketminer` checkpoint on **PDB 1BTL**.
- PocketMiner produced 263 residue-level probabilities, ranging from **0.0258 to 0.9514**.
- Using the official pipeline’s **0.5 probability threshold**, **124 of 263 residues** were classified as pocket-forming.
- High-scoring residues in and around the CBT-contacting region included:
  - **Lys234 0.9514**
  - **Ile246 0.9425**
  - **Arg244 0.9290**
  - **Ala217 0.9208**
  - **Ser235 0.9179**
  - **Leu220 0.9168**
  - **Ala237 0.8921**
  - **Asn276 0.8693**
  - **Gly245 0.8435**
  - **Gly236 0.8263**
  - **Ile263 0.7797**
  - **Ile279 0.7740**

All six final variant sites have PocketMiner probabilities above 0.5.

## 1PZO inhibitor-contact definition

The allosteric inhibitor in 1PZO is **CBT**,  
*N,N-BIS(4-CHLOROBENZYL)-1H-1,2,3,4-TETRAAZOL-5-AMINE*.

The contact analysis used the union of:

1. Protein residues with any heavy atom within **4.5 Å** of either CBT molecule; and
2. Protein residues listed in the deposited PDB `SITE` records for AC1/CBT A300 and AC2/CBT A301.

The resulting contact set was:

**Arg191, Lys192, Val216, Ala217, Leu220, Leu221, Ala224, Leu225, Ser235, Gly236, Ala237, Arg244, Gly245, Ile246, Val261, Ile263, Asn276, Ile279, Ala280, Gly283, and Leu286.**

Variant-to-contact distances were calculated as the minimum heavy-atom distance between the two residues.

## Excluded and non-evaluable annotations

- **19 L→F:** cannot be evaluated because UniProt position 19 is in the signal peptide and is absent from the resolved 1BTL/1PZO chains.
- **37 Q→K:** 9.115 Å.
- **102 E→K:** 8.284 Å.
- **162 R→H and R→S:** 11.756 Å.

Both **Ala235** and **Asn272** directly contact CBT; the other four accepted positions are within 6 Å of a contacting residue but do not directly contact CBT.

### Sources and reproducibility

- UniProt: **P62593**, natural-variant annotations.
- Structures: RCSB PDB **1BTL** and **1PZO**.
- PocketMiner: Meller et al., *Nature Communications* 2023, DOI **10.1038/s41467-023-36699-3**; official code at `Mickdub/gvp`, branch `pocket_pred`.
- Computed outputs:
  - `output/1BTL_preds.npy`
  - `output/pocketminer_residues.csv`
  - `output/variants_with_distances.csv`
  - `output/structure_analysis.json`
=== END RUN rpcwrjcl5vf ===

=== RUN rsz6pdopad9 ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**ChEMBL has no IC50 record for SHP099 against human PTP1B/PTPN1 (UniProt P18031).**

- SHP099: **CHEMBL5280755**
- Human PTP1B/PTPN1: **CHEMBL335** (UniProt **P18031**)
- Direct SHP099–CHEMBL335 IC50 query: **0 records**

The only ChEMBL activity for SHP099 is against human **SHP2/PTPN11** (CHEMBL3864), with **IC50 = 71 nM** (pChEMBL 7.15; assay CHEMBL5241497). That value is for SHP2, not PTP1B.
=== END RUN rsz6pdopad9 ===

=== RUN rree7xbckqm ===
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
**The myristoyl-site pocket is rank 3.**

After removing all HETATM records—including MYR (myristic acid), P16, glycerol, and waters—from 1OPK, Fpocket identified 34 pockets. The MYR binding site overlapped **8/8 MYR-contact residues** with **pocket 3**, which had an Fpocket score of **0.211** and druggability score of **0.547**. The result was identical in the explicit ligand-stripped run and the integrated allosteric-site workflow.

Note: the deposited 1OPK entry is mouse ABL1 and maps to **P00520**, rather than human ABL1 **P00519**, but this does not affect the requested pocket ranking.
=== END RUN rree7xbckqm ===

=== RUN rwv71izfo20 ===
QUESTION:
In PDB entry 1T4J (human PTP1B, UniProt P18031), identify the bound allosteric ligand and list the residues within 4 angstroms of it, using UniProt numbering.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[S01_b] [critical] [scripted] [{"chain": "A", "pdb_number": 299}]
[S01_c] [critical] [scripted] {"uniprot_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "pdb_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "min_distances": {"188": 3.918, "189": 3.416, "192": 3.803, "193": 3.011, "196": 3.552, "200": 3.304, "276": 2.554, "277": 3.367, "279": 3.031, "280": 2.645, "282": 3.593}}
[S01_d] [critical] [scripted] 11

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**Bound allosteric ligand:** PDB chemical component **FRJ**  
**Deposited name:** **3-(3,5-dibromo-4-hydroxy-benzoyl)-2-ethyl-benzofuran-6-sulfonic acid [4-(thiazol-2-ylsulfamoyl)-phenyl]-amide**  
**Formula:** C₂₆H₁₉Br₂N₃O₇S₃

This is the single nonpolymer ligand in **PDB 1T4J**, the PTP1B–allosteric inhibitor structure reported by Wiesmann et al. (PMID: 15258570).

## Residues within 4.0 Å

Using the minimum distance between any FRJ heavy atom and any protein heavy atom, the following **11 residues** meet the inclusive **≤4.0 Å** criterion:

| UniProt P18031 residue | PDB residue | Minimum distance |
|---|---|---:|
| **Pro188** | PRO A188 | 3.918 Å |
| **Ala189** | ALA A189 | 3.416 Å |
| **Leu192** | LEU A192 | 3.803 Å |
| **Asn193** | ASN A193 | 3.011 Å |
| **Phe196** | PHE A196 | 3.552 Å |
| **Glu200** | GLU A200 | 3.304 Å |
| **Glu276** | GLU A276 | 2.554 Å |
| **Gly277** | GLY A277 | 3.367 Å |
| **Lys279** | LYS A279 | 3.031 Å |
| **Phe280** | PHE A280 | 2.645 Å |
| **Met282** | MET A282 | 3.593 Å |

**Compact list:** **P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, M282**

### Numbering note

PDB `DBREF` and RCSB/SIFTS map chain A residues 1–298 to **UniProt P18031 residues 1–298**; an independent alignment showed 282/282 observed residues identical to the canonical sequence. Therefore, the PDB and UniProt residue numbers are identical here.

The deposited PDB `SITE` annotation lists nine of these residues—A189, N193, F196, E200, E276, G277, K279, F280, and M282—but omits **Pro188** and **Leu192**, whose direct minimum distances to FRJ are 3.918 and 3.803 Å, respectively.

## Completed plan

1. [✓] Retrieve 1T4J coordinates and P18031 sequence  
2. [✓] Identify and verify the FRJ allosteric ligand  
3. [✓] Calculate residue-level ligand contacts at ≤4.0 Å  
4. [✓] Map contacts to UniProt P18031 numbering  
5. [✓] Cross-check independently against the mmCIF coordinates and RCSB/SIFTS mapping  

**Sources:** [PDB 1T4J](https://www.rcsb.org/structure/1T4J), [UniProt P18031](https://www.uniprot.org/uniprotkb/P18031/entry), [Wiesmann et al., PMID 15258570](https://pubmed.ncbi.nlm.nih.gov/15258570/)
=== END RUN rwv71izfo20 ===

=== RUN rvhxi75n0ai ===
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
## SHP2/PTPN11 variant summary

| Variant | ClinVar classification | AlphaMissense | PDB 5EHR allosteric inhibitor interface | PDB 2SHP autoinhibitory interface |
|---|---|---:|---|---|
| **E76K** | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications. HGVS: `NM_002834.5:c.226G>A (p.Glu76Lys)`; ClinVar Variation ID **28375** | **0.9998**, pathogenic | **No.** Minimum heavy-atom distance to inhibitor `5OD`: **14.714 Å** in chain A and **14.827 Å** in chain B. | **Yes.** Minimum distance to the opposing PTP domain: **2.797 Å** in chain A and **2.819 Å** in chain B. |
| **D61Y** | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications. HGVS: `NM_002834.5:c.181G>T (p.Asp61Tyr)`; ClinVar Variation ID **230257** | **0.9985**, pathogenic | **No.** Minimum heavy-atom distance to inhibitor `5OD`: **19.642 Å** in chain A and **19.662 Å** in chain B. | **Yes.** Minimum distance to the opposing PTP domain: **3.689 Å** in chain A and **3.499 Å** in chain B. |

### Coordinate-level evidence

**5EHR—allosteric inhibitor site**

- `5OD` is the allosteric-inhibitor chemical component in 5EHR.
- **E76:** nearest pairs were `GLU76 OE2–5OD CL2`, at **14.714 Å** (A) and **14.827 Å** (B).
- **D61:** nearest pairs were `ASP61 O–5OD CL2`, at **19.642 Å** (A) and **19.662 Å** (B).
- These are far outside direct ligand-contact range. Accordingly, neither residue directly contacts the inhibitor in 5EHR.

**2SHP—N-SH2/PTP-domain autoinhibitory interface**

Using Q06124 residues 1–115 as the N-SH2 domain and 224–525 as the PTP domain, with a heavy-atom contact cutoff of 4.5 Å:

- **E76 directly participates in the interface.**
  - Chain A: **2.797 Å**, `GLU76 OE2–SER502 OG`.
  - Chain B: **2.819 Å**, same atom pair.
  - Other opposing-domain contacts include L262, R265, N281 and F285.
- **D61 directly participates in the interface.**
  - Chain A: **3.689 Å**, `ASP61 O–ILE463 CG1`; it also contacts R465 at **3.833 Å**.
  - Chain B: **3.499 Å**, `ASP61 OD1–ARG465 CD`.
  - Other contacts include S460, A461, I463/G464 and Q506.

## Conclusion

Both **E76K** and **D61Y** are residues of the **autoinhibitory N-SH2/PTP-domain interface**, not residues directly forming the **5EHR allosteric-inhibitor interface**. This is consistent with a possible mechanism in which these substitutions perturb autoinhibition, although the coordinate analysis establishes the wild-type residue locations rather than proving the effects of the mutant side chains.

Distances are minimum heavy-atom distances from the deposited structures; UniProt–PDB mappings confirmed D61 and E76 in both chains. The ClinVar wording above is the exact aggregate classification in the local ClinVar snapshot, while AlphaMissense independently classifies both substitutions as pathogenic.
=== END RUN rvhxi75n0ai ===

=== RUN rl3bhidewpy ===
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
1. [✓] Identified the ligands and resolved T315 numbering in PDB 1OPK.
2. [✓] Calculated and independently validated the minimum heavy-atom distances.
3. [✓] Retrieved the ClinVar classification.
4. [✓] Retrieved the AlphaMissense score.
5. [✓] Interpreted the site-specific structural implications.

### Results for ABL1 T315I

| Evidence | Result |
|---|---|
| ClinVar | **Likely pathogenic; association** |
| ClinVar review status | Criteria provided, multiple submitters, **no conflicts** |
| ClinVar record | `NM_005157.6(ABL1):c.944C>T (p.Thr315Ile)`, ClinVar Variation ID **27663** |
| AlphaMissense | **0.9991 — pathogenic** |
| ATP-pocket ligand **P16** | **3.24 Å** from T315 |
| Myristoyl-pocket ligand **MYR** (myristic acid) | **25.59 Å** from T315 |

The closest-atom calculations identify:

- T315 OG1–P16 C16: **3.2394 Å**
- T315 OG1–MYR C14: **25.5947 Å**

### Structural interpretation

T315 is directly adjacent to the **ATP-pocket ligand P16**, whereas it is far from the myristoyl-pocket ligand. The distances therefore support the variant affecting **ATP-site ligand binding**, not the myristoyl site. Biologically, T315 is the ABL1 **gatekeeper residue**; replacing threonine with the bulkier isoleucine can sterically obstruct ATP/inhibitor occupancy and is consistent with altered inhibitor sensitivity.

One structural caveat is that 1OPK contains **mouse ABL1 (UniProt P00520)**, not human P00519 itself. Its mapping places mouse residue 315 at deposited PDB chain A residue **THR 334**, corresponding to the human gatekeeper T315. These distances were measured from the deposited wild-type threonine coordinates; they identify the affected site but do not by themselves prove the binding-affinity change of the T315I mutant.
=== END RUN rl3bhidewpy ===

=== RUN rfeu2zfc5v6 ===
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
1. [✗] Initial web-search route was unavailable; replaced it with direct access to the official AlphaMissense Google Cloud dataset.
2. [✓] Retrieved the ClinVar classification and AlphaMissense score.
3. [✓] Identified the 1OPK ATP-site ligand (P16), myristoyl-site ligand (MYR), and the canonical-to-PDB residue mapping.
4. [✓] Calculated and cross-checked the interatomic distances.
5. [✓] Interpreted the structural result.

## Variant annotation

| Field | Result |
|---|---|
| Gene/protein | ABL1, UniProt **P00519** |
| Variant | **T315I**; ClinVar `NM_005157.6:c.944C>T` |
| ClinVar record | [VCV000012624.3](https://www.ncbi.nlm.nih.gov/clinvar/variation/12624/) |
| Current ClinVar aggregate classification | **Likely pathogenic; association** |
| Review status | **Criteria provided, multiple submitters, no conflicts** |
| Condition | Chronic myeloid leukemia |
| AlphaMissense | **0.9991**, AlphaMissense class **pathogenic** |

The AlphaMissense value comes directly from the official `P00519` substitution table: `P00519  T315I  0.9991  pathogenic`. The score is a computational pathogenicity score, not a patient-specific probability.

## Distances in PDB 1OPK

An important numbering correction is needed: **PDB author residue A315 is proline and is not UniProt T315**. Sequence alignment of the deposited ABL1 construct to P00519 maps:

- UniProt P00519 **T315** → 1OPK chain A **THR334**

The 1OPK nonpolymer entities are:

- **P16** — the ATP-site ligand; deposited `SITE` records explicitly include THR334 among its contacts.
- **MYR (myristic acid)** — the myristoyl-site ligand; its contacts are L360, E481, and L529.

Distances were calculated as the minimum separation between heavy atoms of T315/THR334 and each ligand:

| Ligand/site | Minimum heavy-atom distance | T315 Cβ to nearest ligand atom | T315 Cα to nearest ligand atom |
|---|---:|---:|---:|
| **P16, ATP site** | **3.24 Å** — T315 OG1–P16 C16 | 4.42 Å | 5.46 Å |
| **MYR, myristoyl site** | **25.59 Å** — T315 OG1–MYR C14 | 26.07 Å | 27.28 Å |

## Interpretation

The distances strongly favor an effect on the **ATP-binding site**, not the myristoyl pocket:

- T315’s side-chain hydroxyl is only **3.24 Å** from the ATP-site ligand, consistent with a direct interaction.
- The nearest myristoyl-site ligand atom is **25.59 Å** away, far beyond normal direct-contact range.
- Replacing threonine with isoleucine removes that hydroxyl and introduces a bulkier hydrophobic side chain at the ATP-cleft gatekeeper position. This is therefore expected to alter ATP-site ligand binding and sterically/chemically impair inhibitor engagement.
- This is the classic structural basis for ABL1 gatekeeper resistance mutations such as T315I.

Thus, 1OPK supports direct disruption of **ATP-site ligand recognition**, with no evidence that T315I directly perturbs the myristoyl-site ligand. This is a static, wild-type structural inference and does not by itself quantify effects on ATP turnover or allosteric signaling.

**Primary sources:** [UniProt P00519](https://www.uniprot.org/uniprotkb/P00519/entry), [ClinVar VCV000012624](https://www.ncbi.nlm.nih.gov/clinvar/variation/12624/), [RCSB PDB 1OPK](https://www.rcsb.org/structure/1OPK) (Nagar et al., *Cell* 2003; DOI: [10.1016/S0092-8674(03)00194-6](https://doi.org/10.1016/S0092-8674(03)00194-6)), and the official [AlphaMissense substitution dataset](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz).
=== END RUN rfeu2zfc5v6 ===

=== RUN rbl9xtb84er ===
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
# ChEMBL Bioactivity Comparison: Asciminib vs Imatinib against Human ABL1 (UniProt P00519)

**Target:** Tyrosine-protein kinase ABL1 — `CHEMBL1862` (SINGLE PROTEIN, *Homo sapiens*, UniProt **P00519**)
**Drugs:** Asciminib = `CHEMBL4208229`; Imatinib = `CHEMBL941` (both max_phase 4)
**Source:** ChEMBL web services (activities endpoint, `target_chembl_id=CHEMBL1862`); RCSB PDB Data API; PubMed E-utilities

---

## 1. Headline comparison

| Metric (vs ABL1 / CHEMBL1862) | **Asciminib** | **Imatinib** |
|---|---|---|
| **Activity records** | **6** | **160** |
| Distinct assays / documents | 4 / 3 | 154 / 49 |
| **Assay types** | **B = 6 (100% binding)** | **B = 158 (98.8%), F = 1 (functional), A = 1 (ADME)** |
| Records with pChEMBL | 3 | 106 |
| **Best potency** | **Kd = 0.5 nM** and **IC₅₀ = 0.5 nM** (pChEMBL **9.3**) | **Kd = 1.0 nM** (pChEMBL **9.0**) |
| Best wild-type ABL1 biochemical IC₅₀ | 0.5 nM (pChEMBL 9.3) | 19.9 nM (pChEMBL 7.7) |
| Best Kᵢ | not reported | 13 nM (pChEMBL 7.89) |
| Other endpoints | ΔTm = +6.92 °C; IC₅₀ 16 nM; k_on/k_off (non-numeric) | Inhibition (13), K_diss (3), k_on/k_off (3), GI₅₀ (2), t½ (2), Selectivity (1), Activity (1), T½ (1) |
| Data-validity flagged records | 0 | 1 ("Outside typical range") |
| Record split | all isolated-ABL1 biochemical | **93 wild-type ABL1 / 67 mutant-or-BCR-ABL** |
| **Binding site** | **Myristoyl (myristate) pocket — allosteric, non-ATP-competitive** | **ATP-binding (orthosteric) site of the kinase domain** |
| **PDB citation** | **5MO4** (also 8SSN) | **2HYY** (classic: 1IEP; also 3K5V) |
| Total records in ChEMBL (all targets) | 194 | 4,878 |

### Best-potency records (exact)

**Asciminib** — assay `CHEMBL4200854`, doc `CHEMBL4196169` (Schoepfer *et al.*, *J Med Chem* 2018, PMID 30137981):
- Kd = 0.5 nM (ITC), ABL1 (64–515 residues) expressed in *E. coli* — pChEMBL 9.3
- IC₅₀ = 0.5 nM (Caliper kinase assay, FITC-Ahx-EAIYAAPFAKKK-NH2 peptide substrate), same construct — pChEMBL 9.3 (`CHEMBL4200739`)
- Plus: ΔTm = 6.92 °C (DSF, `CHEMBL5060015`); IC₅₀ = 16 nM (`CHEMBL5739300`, 2023)

**Imatinib** — assay `CHEMBL4320888`, doc `CHEMBL4316600` (Bauer & Mackey, *J Med Chem* 2019, DOI 10.1021/acs.jmedchem.8b01925):
- Kd = 1.0 nM for ABL1 (vs 10 nM for ABL2) — pChEMBL 9.0
- Also Kd = 1.1 nM for non-phosphorylated wild-type ABL1 kinase domain (Davis *et al.*, *Nat Biotechnol* 2011, `CHEMBL1908688`)
- Best wild-type biochemical IC₅₀ = 19.9 nM (pChEMBL 7.7, `CHEMBL2406231`, *J Med Chem* 2013)

---

## 2. Binding sites and PDB citations

**Asciminib → myristoyl site (allosteric).** PDB **5MO4** — *"ABL1 kinase (T334I_D382N) in complex with asciminib and nilotinib"*, X-ray 2.17 Å, *Nature* 2017, PMID **28329763**, DOI **10.1038/nature21702**. RCSB maps the polymer entity to **UniProt P00519**; asciminib is ligand `AY7` and nilotinib (`NIL`) occupies the ATP site in the same structure — a direct structural demonstration of the two distinct sites. Supplementary: PDB **8SSN** (*PNAS* 2023, PMID 37590418, DOI 10.1073/pnas.2304611120), ABL1 (P00519) with asciminib + the ATP-site inhibitor SKI. The site is stated explicitly in the asciminib discovery paper (PMID 30137981): *"Asciminib binds to the myristate pocket of BCR-ABL1 and maintains activity against TKI-resistant ATP-site mutations."*

**Imatinib → ATP site (orthosteric).** PDB **2HYY** — *"Human Abl kinase domain in complex with imatinib (STI571, Glivec)"*, 2.4 Å, *Acta Crystallogr D* 2007, PMID **17164530**, DOI **10.1107/S0907444906047287**; RCSB maps this ABL1 entity to **UniProt P00519**. The historical classic is PDB **1IEP** (2.1 Å, *Cancer Res* 2002, PMID **12154025**), whose abstract states: *"Both compounds bind to the canonical ATP-binding site of the kinase domain"* — note RCSB's SIFTS maps 1IEP (like 3K5V, 6HD4, 6HD6) to **P00520 (ABL2)**, not P00519. PDB **3K5V** (*Nature* 2010, PMID 20072125) is the cleanest side-by-side proof: imatinib in the ATP site with GNF-2 occupying the **myristate pocket**.

---

## 3. Interpretation and caveats

1. **Asymmetry in data volume:** asciminib has only 6 ABL1 records (all binding-type, 3 papers), so its "best potency" rests on a single biochemical study on an isolated ABL1(64–515) construct from *E. coli*; imatinib has 160 records across 49 documents spanning 1999–2023. The 0.5 nM vs 1.0 nM pChEMBL gap is **not** a fair head-to-head potency comparison.
2. **Biochemical vs cellular:** asciminib's 0.5 nM values are in vitro (Caliper/ITC); imatinib's best wild-type cellular-relevant value is ~19.9 nM IC₅₀ in biochemical phosphorylation assays. Against the disease-relevant **BCR-ABL fusion** (`CHEMBL2096618`), both are sub-nM: asciminib 17 records (best Kd 0.45 nM; GI₅₀ 0.61 nM in Ba/F3 cells), imatinib 100 records (best IC₅₀ 1.1 nM).
3. **Imatinib's 160 records include 67 mutant/BCR-ABL records** (T315I, Y253H, F317L, M351T, H396P, etc.); the strongest wild-type numbers above are separated from these deliberately.
4. **Target mapping:** the chimeric/family targets carrying P00519 as a component (`CHEMBL2096618` Bcr/Abl fusion, `CHEMBL2111414` ABL family) hold additional relevant data and were counted separately rather than merged into the ABL1 single-protein target.
5. All ChEMBL counts are raw record counts (including parent/salt forms mapped to the same molecule ID); one imatinib record carries a ChEMBL data-validity flag ("Outside typical range") and was excluded from "best potency" selections.

**Artifacts saved** in `chembl_abl1/`: per-drug activity CSVs and raw JSON, classified (wild-type vs mutant) CSVs, `assays.json`, `documents.json`, PDB inspection JSONs, PubMed XML/JSON, and the consolidated `ABL1_asciminib_vs_imatinib_report.json`.
=== END RUN rbl9xtb84er ===

=== RUN rwpmca1qsqb ===
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
| **AKT1 / UniProt** | P31749 |
| **ClinVar classification** | **Pathogenic** |
| **ClinVar record** | Variation ID **29022**; `NM_001382430.1:c.49G>A (p.Glu17Lys)`; review status: *criteria provided, multiple submitters, no conflicts* |
| **AlphaMissense** | **0.9977**, classified **pathogenic** |
| **Domain containing residue 17** | **Pleckstrin homology (PH) domain**, UniProt residues **5–108** |
| **Residue 17 modeled in PDB 3O96?** | **Yes** — chain A, PDB residue 17, GLU, mapped to P31749 residue 17 |
| **Allosteric inhibitor in 3O96** | Chemical component **IQO**; the entry is titled *Crystal Structure of Human AKT1 with an Allosteric Inhibitor* |
| **Glu17–IQO distance** | **5.70 Å** minimum heavy-atom distance |

### Structural interpretation

- The **5.70 Å** value is the shortest distance between any heavy atom of deposited Glu17 and any heavy atom of IQO.
- Glu17 did **not** appear among the residues within the conventional **4.0 Å** ligand-contact cutoff, so it is spatially near the inhibitor but is not a 4 Å direct contact in this structure.
- PDB 3O96 models **wild-type Glu17**, not Lys17. Therefore, the measured distance describes the deposited E17 side chain and should not be interpreted as a structural measurement of the E17K mutant.

### Sources

- [ClinVar variation 29022](https://www.ncbi.nlm.nih.gov/clinvar/variation/29022/)
- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry)
- [RCSB PDB 3O96](https://www.rcsb.org/structure/3O96)
- [RCSB chemical component IQO](https://www.rcsb.org/ligand/IQO)
=== END RUN rwpmca1qsqb ===

=== RUN r8mju8n9z6h ===
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

**10 of the 14 STINGAllo-predicted residues are within 4.0 Å of the bound allosteric ligand.**

### STINGAllo-predicted residues for 1T4J chain A
1. GLU129
2. GLU130
3. SER187
4. PRO188
5. ALA189
6. LEU192
7. ASN193
8. PHE196
9. GLU200
10. GLU276
11. LYS279
12. PHE280
13. ILE281
14. MET282

### Residues within 4.0 Å of ligand FRJ
1. PRO188
2. ALA189
3. LEU192
4. ASN193
5. PHE196
6. GLU200
7. GLU276
8. GLY277
9. LYS279
10. PHE280
11. MET282

### Overlap
1. PRO188
2. ALA189
3. LEU192
4. ASN193
5. PHE196
6. GLU200
7. GLU276
8. LYS279
9. PHE280
10. MET282

**Overlap count: 10**

### Method
- Ligand: **FRJ**, the allosteric inhibitor bound as PDB residue **A 299**.
- Contact criterion: minimum Euclidean distance between any chain-A protein atom and any FRJ heavy atom of **≤4.0 Å**.
- Hydrogens are absent from the X-ray structure.
- SER187 and ILE281 were predicted by STINGAllo but fall just outside the cutoff, at 4.048 Å and 4.319 Å, respectively.
- GLY277 is within 4 Å but was not predicted by STINGAllo.

Sources: [1T4J at RCSB PDB](https://www.rcsb.org/structure/1T4J), [STINGAllo API result](https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A), and Omage et al., *Briefings in Bioinformatics* (2025), [doi:10.1093/bib/bbaf424](https://doi.org/10.1093/bib/bbaf424).

### Completed plan
1. [✓] Retrieve PDB metadata, coordinates, chain mapping, and ligand information.
2. [✓] Retrieve the authoritative STINGAllo prediction list.
3. [✓] Identify FRJ A 299 and its heavy-atom coordinates.
4. [✓] Calculate the ≤4.0 Å contact residues and their overlap.
5. [✓] Verify the calculation independently and save the auditable results.
=== END RUN r8mju8n9z6h ===

# Judge batch 016 of 24

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

=== RUN rmog6eybwo9 ===
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
[P06_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 16.09, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 7.05, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 2.14, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 4, "score": 1.2, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.81, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.54, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P06_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

REFERENCE NOTE (dated correction, from benchmark/corrections.md)
The pocket-detection reference for the 1V4S_GLC site was corrected on 2026-11-02: the committed selection took the first pocket with any overlap (rank 1, overlap 2), the corrected selection takes the pocket with the most site residues (rank 2, overlap 13).
No committed checklist item carries this site, so the item texts below are unchanged.

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
# Ligand removal and pocket detection for PDB 1V4S (human glucokinase, P35557)

## 1. Starting point
| Item | Value |
|---|---|
| Entry | 1V4S — "Structural basis for allosteric regulation of the monomeric allosteric enzyme human glucokinase" (Kamata et al., *Structure* 2004, PMID 15016359) |
| Polymer | Human glucokinase isoform 2, chain A, UniProt **P35557**, X-ray 2.3 Å (448 residues, 3,505 protein atoms) |
| Ligands present | **GLC** glucose (res 500, 12 atoms) · **MRK** 2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide (res 501, 23 atoms) = the small-molecule **allosteric activator** · **NA** sodium (res 600) · 149 waters |

Reference ligand positions (centroids of the original deposited coordinates):
- GLC (glucose): [24.8, 3.0, 65.7] — contacts Asn204, Asp205, Thr168, Lys169, Asn231, Cys230, Gly229, Ile225, Gln287, **Glu256, Glu290** (catalytic pocket)
- MRK (activator): [40.2, 15.1, 62.0] — contacts Tyr61, Val62, Arg63, Ser64, Thr65, Pro66, Ile159, Met210, Ile211, Cys220, **Tyr214, Tyr215**, Met235, Leu451, Val452, Val455, Ala456 (allosteric pocket)
- The two ligand centroids are **20 Å apart** → two distinct, adjacent pockets.

## 2. Ligand removal
All HETATM records were stripped (185 atoms: GLC 12, MRK 23, NA 1, HOH 149), leaving protein only:
- `1V4S_noligands.pdb` — **3,505 ATOM records, 0 HETATM records**, chain A, residues 14–461.
- For AutoSite, the receptor needs polar hydrogens (AutoGrid aborts otherwise), so `reduce` was used to add them → `1V4S_noligands_H.pdb` (7,970 polar H) → `prepare_receptor` → PDBQT with 4,302 atoms / 797 polar H, still zero ligands.

## 3. Pocket detection — AutoSite v1.0.0 (ADFRsuite 1.0, Scripps), run via `run_autosite`
AutoSite was not present in the image (no `autosite`/`prepare_receptor` binaries), so ADFRsuite 1.0 was installed from Scripps and repaired (Python-2 `ADFRcc` circular-import bug; `libSM.so.6` added to `LD_LIBRARY_PATH` so OpenBabel plugins load). Run: receptor-only mode, spacing 1.0 Å, box center (32.7, 26.6, 54.9), box size 86×86×86 Å → **16 clusters** ranked by AutoSite energy.

### Top three AutoSite clusters
| Rank | Energy | #points | Radius | Centroid | Dist. to GLC | Dist. to MRK | Points ≤4 Å of GLC / MRK | Lining residues | Assignment |
|---|---|---|---|---|---|---|---|---|---|
| **Cluster 1** | −260.8 | 550 | 7.47 Å | 41.1, 18.0, 60.6 | 22.8 Å | **3.4 Å** | 0 / **101** | Tyr61, Val62, Arg63, Ser64, Thr65, Pro66, Val455, Ile211, Tyr214/215 | **Allosteric activator site (MRK)** |
| **Cluster 2** | −117.7 | 201 | 4.90 Å | 25.4, 3.5, 69.4 | **3.8 Å** | 20.2 Å | **96** / 0 | Ser151, Phe152, Thr168, Lys169, Asn204, Asp205, Thr228, Gly229, Cys230, Asn231, Gln287, **Glu256, Glu290** | **Glucose (catalytic) site** |
| **Cluster 3** | −90.1 | 184 | 4.38 Å | 31.4, −21.8, 72.8 | 26.7 Å | 39.5 Å | 0 / 0 | Glu17, Leu20, Ala21, Phe23, Gln24, Arg369, Ser373, Thr376 (exterior face) | No ligand site — surface cavity |

**Answer: YES.** With AutoSite the top three pockets do contain both functional sites: **Cluster 1 = allosteric activator site, Cluster 2 = glucose site, Cluster 3 = neither** (an exterior surface cavity).

## 4. Independent cross-check — fpocket 4.0 (same ligand-free structure, 26 pockets)
| fpocket rank | Score | Volume | Centroid dist. to GLC / MRK | Assignment |
|---|---|---|---|---|
| Pocket 1 | 0.223 | 128 Å³ | 9.4 / 14.1 Å | Small surface groove (Leu58, Pro59, Thr60, Phe150/152, Val154) — not a ligand site |
| **Pocket 2** | 0.139 | 579 Å³ | **3.9** / 19.7 Å | **Glucose site** (catalytic residues Asp205, Glu256, Glu290, Asn204, Lys169, Thr228…) |
| Pocket 3 | 0.111 | 302 Å³ | 25.5 / 38.8 Å | Exterior pocket near the N-terminus — not a ligand site |
| Pocket 6 | 0.072 | **1,220 Å³ (largest)** | 21.6 / **3.4** Å | **Allosteric activator site** (Tyr61, Arg63, Val62, Thr65, Tyr214/215, Met235, Val452/455) |

The two methods agree on the *identity* of both pockets (fpocket pocket 2 ≡ AutoSite cluster 2 = glucose; fpocket pocket 6 ≡ AutoSite cluster 1 = allosteric activator). They differ only in **ranking convention**: fpocket's score metric favours small exposed grooves, so the buried allosteric cavity falls to rank 6 despite being the **largest** pocket by volume, whereas AutoSite's energy ranking puts it first.

## 5. Answer to the question
- **Allosteric activator site → AutoSite Cluster 1** (energy −260.8, 550 points, radius 7.47 Å; centroid 3.4 Å from the MRK ligand; 101 cluster points within 4 Å of MRK; flanked by Tyr61/Arg63/Val62/Thr65 and Tyr214/Tyr215, Leu451/Val452/Val455/Ala456). In fpocket this is **pocket 6** (1,220 Å³, the largest cavity).
- **Glucose site → AutoSite Cluster 2** (energy −117.7, 201 points, radius 4.90 Å; centroid 3.8 Å from the glucose ligand; 96 points within 4 Å of GLC; contains the catalytic Asn204/Asp205/Thr228/Glu256/Glu290 and the Thr168/Lys169 loop). In fpocket this is **pocket 2**.
- The two sites are adjacent but spatially distinct (ligand centroids 20 Å apart), and both are recovered as top-ranked pockets by AutoSite; only the glucose site is in fpocket's top three by score (the activator site ranks first by pocket volume).

## 6. Artifacts produced
`/agent_cwd/work/`: `1V4S.pdb`, `1V4S_noligands.pdb` (ligand-free), `1V4S_noligands_H.pdb`, `1V4S_noligands_H.pdbqt`, `ligand_sites.json`, `autosite_out_H/` (16 `_cl_*.pdb` clusters, `_fp_*.pdb` feature points, `1V4S_noligands_H_summary.csv`), `autosite_out_H_AutoSiteSummary.log`, `autosite_result_H.txt`, `1V4S_noligands_out/` (fpocket output, 26 pockets), `fpocket_pockets.json`, `autosite_clusters.json`.

## 7. Plan checklist (completed)
1. [✓] Retrieve PDB 1V4S metadata and coordinates; confirm human GCK (P35557) — done
2. [✓] Catalogue all ligands (GLC, MRK, Na⁺, 149 H₂O) and define the glucose and allosteric-activator binding sites — done
3. [✓] Build and verify the ligand-free structure (3,505 protein atoms, 0 HETATM) — done
4. [✓] Install/patch AutoSite v1.0.0 (ADFRsuite) and run pocket detection on the ligand-free receptor → 16 clusters — done
5. [✓] Map the top three pockets to the two sites (AutoSite + independent fpocket cross-check) and report the assignment — done

*Note on tooling: the image shipped without AutoSite binaries (the `run_autosite` wrapper failed with "No such file or directory: 'prepare_receptor'"), so ADFRsuite 1.0 was installed from Scripps and two packaging defects were repaired (Python-2 `ADFRcc.adfr` circular import; missing `libSM.so.6` for OpenBabel). fpocket 4.0 (already present at /usr/local/bin/fpocket) was used as the independent cross-check.*
=== END RUN rmog6eybwo9 ===

=== RUN rbqijp3qlhm ===
QUESTION:
For KRAS (UniProt P01116), report ClinVar classification and AlphaMissense score for G12C, G12D and G12V, and the distance from residue 12 to the covalent inhibitor in PDB 6OIM. Do the scores distinguish the three variants?

INTENDED PROTEIN: GTPase KRas (P01116)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V03_a] [critical] [scripted] {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"}
[V03_b] [critical] [scripted] {"clinical_significance": "Likely pathogenic", "variation_id": "27617"}
[V03_c] [critical] [scripted] 0.9975
[V03_d] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "20046"}
[V03_e] [critical] [scripted] 0.9984
[V03_f] [critical] [scripted] {"clinical_significance": "Pathogenic", "variation_id": "27622"}
[V03_g] [critical] [scripted] 0.9949
[V03_h] [critical] [judged] the distance from residue 12 to the 6OIM covalent inhibitor is reported
[V03_i] [critical] [judged] the answer says whether the three scores separate the variants

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### KRAS (UniProt P01116) variant summary

| Variant | ClinVar classification | ClinVar ID | AlphaMissense score | AlphaMissense class |
|---|---|---:|---:|---|
| **G12C** (c.34G>T) | **Likely pathogenic** | 27617 | **0.9975** | Pathogenic |
| **G12D** (c.35G>A) | **Pathogenic/Likely pathogenic** | 27621 | **0.9984** | Pathogenic |
| **G12V** (c.35G>T) | **Pathogenic** | 27622 | **0.9949** | Pathogenic |

All three ClinVar records had the review status “criteria provided, multiple submitters, no conflicts.”

### Distance to the covalent inhibitor in PDB 6OIM

- Structure/chain: **6OIM, chain A**
- Inhibitor component: **MOV**
- Target residue: **CYS12**
- Minimum heavy-atom distance, CYS12–MOV: **1.81 Å**

This short separation is consistent with covalent attachment, although the contact calculation itself reports geometry rather than independently assigning an interaction type or binding energy. It describes the **G12C structure** in 6OIM and should not be interpreted as a measured distance for G12D or G12V.

### Do the scores distinguish the variants?

**Not meaningfully with AlphaMissense.** The numerical scores are distinct—G12D (0.9984) > G12C (0.9975) > G12V (0.9949)—but the full range is only **0.0035**, and all three receive the same **pathogenic** class. Thus, AlphaMissense does not separate these substitutions in a practically or biologically useful way.

**ClinVar does distinguish their asserted clinical classifications:** Likely pathogenic for G12C, Pathogenic/Likely pathogenic for G12D, and Pathogenic for G12V. Neither ClinVar nor AlphaMissense, however, predicts differential sensitivity to a G12C covalent inhibitor; the 6OIM distance is specific to the G12C-containing structure.
=== END RUN rbqijp3qlhm ===

=== RUN rqbq6wgmbf1 ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Glucokinase variants near the 1V4S allosteric activator

### Key results

- **Target:** human glucokinase, UniProt **P35557**
- **Structure:** PDB **1V4S**, chain A
  - Deposited mapping: P35557 residues **16–465**
  - For the residues discussed here, PDB author numbering and UniProt numbering are identical.
- **Allosteric activator:** **MRK**
  - Systematic name: 2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide
  - The other ligand, **GLC**, is glucose.
- MRK has measured P35557 EC50 values of **67.11 nM** and **80 nM** in ChEMBL.
- Contact criterion: minimum heavy-atom distance **≤6.0 Å** from MRK.
- Result:
  - **24 protein residues** contact MRK.
  - **18 positions** have simple ClinVar protein changes.
  - **38 unique missense changes**, all with AlphaMissense scores.
  - **6 unique stop-gain changes**, for which AlphaMissense is not applicable.
  - **3 additional in-frame indel consequences** overlap contacting residues.
  - **11 synonymous ClinVar records** occur at contacted positions but do not change the encoded residue.

AlphaMissense measures predicted pathogenicity, **not affinity for MRK**. The binding-impact calls below are therefore based primarily on direct side-chain contact distance, contact geometry, and the chemical consequence of the substitution.

### Missense and stop-gain variants

ClinVar classifications are abbreviated as: **P** pathogenic, **LP** likely pathogenic, **P/LP** pathogenic/likely pathogenic, **VUS** uncertain significance, **Conflicting** conflicting classifications, and **Uncertain/Uncertain risk** uncertain significance/uncertain risk allele.

| PDB / UniProt position | MRK contact geometry | ClinVar consequence(s), ID, classification, and AlphaMissense | Binding-effect assessment |
|---|---|---|---|
| **A:61 / 61, Tyr** | 3.25 Å; backbone-nearest | p.Y61N, ID 1384860, VUS, **0.8868 pathogenic**; p.Y61*, ID 790725, P, **N/A** | Y61N: **plausible secondary effect**; Y61*: likely loss of function rather than a clean binding mutant |
| **A:62 / 62, Val** | 3.62 Å; side chain | p.V62A, ID 576995, P, **0.9731 pathogenic**; p.V62M, ID 407147, P, **0.9462 pathogenic** | **Likely direct perturbation** of MRK-pocket shape |
| **A:63 / 63, Arg** | 3.75 Å side chain | p.R63C, ID 441128, Uncertain/Uncertain risk, **0.1234 benign**; p.R63H, ID 2946975, VUS, **0.1886 benign**; p.R63L, ID 1404564, VUS, **0.3254 benign** | **Likely direct structural candidates**, because the charged Arg side chain directly contacts MRK; low AlphaMissense scores make their global functional effect uncertain |
| **A:98 / 98, Gln** | 4.47 Å; side chain | p.Q98*, ID 3194177, P, **N/A** | Truncation likely impairs overall function; binding-specific effect cannot be separated |
| **A:159 / 159, Ile** | 4.33 Å; side chain | p.I159M, ID 441117, Conflicting, **0.2207 benign**; p.I159N, ID 2904927, Conflicting, **0.9313 pathogenic**; p.I159T, ID 2859052, VUS, **0.5886 pathogenic**; p.I159V, ID 1671470, P/LP, **0.1611 benign** | p.I159N/T: **likely direct**; p.I159M/V: **plausible secondary/edge effects** |
| **A:210 / 210, Met** | 3.66 Å; side chain | p.M210I, IDs 44900/2852830, P, **0.9915 pathogenic**; p.M210K, ID 31180, P, **0.9915 pathogenic**; p.M210T, ID 793234, P, **0.9821 pathogenic**; p.M210V, IDs 2670449/2670450, LP, **0.8229 pathogenic** | **Likely direct perturbation** for all four substitutions |
| **A:211 / 211, Ile** | 3.59 Å; side chain | p.I211N, ID 428731, Uncertain/Uncertain risk, **0.9683 pathogenic**; p.I211T, ID 2845244, P, **0.9474 pathogenic** | **Likely direct perturbation** |
| **A:214 / 214, Tyr** | 3.01 Å; side chain | p.Y214*, ID 1691320, P/LP, **N/A**; p.Y214C, ID 31183, P, **0.2600 benign** | Y214C: **likely direct** because it removes an aromatic side chain in a 3.01 Å contact, despite the low AlphaMissense score; Y214*: truncation/loss of function |
| **A:215 / 215, Tyr** | 2.45 Å; side chain | p.Y215*, IDs 444135/44902, P or P/LP, **N/A** | Truncation at the tightest MRK contact is very likely to disrupt the intact activator pocket, but mainly through loss of intact protein |
| **A:220 / 220, Cys** | 3.30 Å overall; backbone-nearest, side chain 5.87 Å | p.C220*, ID 1162055, P, **N/A**; p.C220F, ID 2852839, VUS, **0.9899 pathogenic**; p.C220R, ID 44903, LP, **0.9953 pathogenic**; p.C220S, ID 4855326, VUS, **0.9574 pathogenic**; p.C220W, ID 3797163, VUS, **0.9982 pathogenic**; p.C220Y, ID 44904, P, **0.9972 pathogenic** | Missenses: **plausible secondary/edge effects** because the nearest contact is mainly to the backbone; high AlphaMissense scores indicate likely functional effects but do not prove altered MRK affinity |
| **A:221 / 221, Glu** | 4.24 Å; side chain | p.E221K, ID 44905, P, **0.7102 pathogenic** | **Likely direct perturbation**, particularly because this is a charge reversal |
| **A:235 / 235, Met** | 3.51 Å; side chain | p.M235R, ID 4799352, LP, **0.9183 pathogenic**; p.M235T, ID 44912, P, **0.9520 pathogenic**; p.M235V, ID 369460, P, **0.5248 ambiguous** | **Likely direct perturbation** |
| **A:250 / 250, Arg** | 4.59 Å; side chain | p.R250C, ID 380270, P, **0.3665 ambiguous**; p.R250H, ID 428728, LP, **0.2145 benign**; p.R250P, ID 2852834, VUS, **0.9134 pathogenic** | p.R250P: **likely direct**, especially because Pro introduces backbone restriction; p.R250C/H: **plausible secondary effects** |
| **A:252 / 252, Cys** | 5.72 Å; side chain | p.C252F, ID 796041, Conflicting, **0.9600 pathogenic**; p.C252W, ID 1903466, VUS, **0.9967 pathogenic** | **Plausible but weaker/edge effects** because the contact is close to the 6 Å cutoff |
| **A:452 / 452, Val** | 3.87 Å; side chain | p.V452L, ID 2671107, LP, **0.6364 pathogenic** | **Likely direct**, although the Val→Leu change is relatively conservative |
| **A:453 / 453, Ser** | 5.64 Å; backbone-only, side chain 7.92 Å | p.S453*, ID 3184688, LP, **N/A**; p.S453L, ID 44864, P/LP, **0.7575 pathogenic**; p.S453W, ID 2904897, P/LP, **0.9903 pathogenic** | Missenses: **plausible secondary/less direct effects** because only the backbone is near MRK; stop-gain likely disrupts overall structure/function |
| **A:455 / 455, Val** | 3.46 Å; side chain | p.V455E, ID 576976, LP, **0.8513 pathogenic**; p.V455M, ID 31179, P, **0.5295 ambiguous** | **Likely direct perturbation**; Val→Glu is especially disruptive |
| **A:456 / 456, Ala** | 4.04 Å; side chain | p.A456P, ID 3781685, VUS, **0.9733 pathogenic**; p.A456V, ID 31182, P, **0.3825 ambiguous** | p.A456P: **likely direct**, because Pro restricts backbone geometry; p.A456V: **plausible secondary effect** |

### In-frame indels overlapping the MRK-contacting region

AlphaMissense is not applicable to in-frame insertions/deletions.

| ClinVar consequence | Contacted residues affected | ClinVar classification | Binding assessment |
|---|---|---|---|
| **p.Met210_Ile211insMet**, ID 1801162 | M210 and I211, both direct side-chain contacts | Conflicting | **Likely to alter the MRK pocket** |
| **p.Leu451_Ala454del**, ID 793214 | Removes L451, V452, and S453; L451/V452/S453 lie in the 6 Å shell | VUS | **Likely to alter the MRK pocket** |
| **p.Val427_Ser453delinsLeuGln**, ID 44854 | Replaces a C-terminal segment that includes contacting S453 | VUS | **Likely to perturb the C-terminal activator-pocket region** |

### Synonymous records at contacted positions

These are within the mapped 6 Å residues but do not alter the encoded amino acid; AlphaMissense is therefore not applicable, and they are not expected to alter MRK binding directly through the protein structure:

- p.Tyr61= — ID 1859040
- p.Ser64= — ID 2828423
- p.Pro66= — ID 306348
- p.Ile159= — ID 5009587
- p.Cys220= — ID 491932
- p.Val222= — IDs 44906 and 2845245
- p.Arg250= — ID 3382321
- p.Cys252= — ID 1813178
- p.Tyr215= — ID 252884
- p.Ser453= — ID 2004094

## Best candidates for altered MRK/activator binding

The **23 missense substitutions with the strongest structural case for directly changing activator binding** are:

- **p.V62A, p.V62M**
- **p.R63C, p.R63H, p.R63L**
- **p.I159N, p.I159T**
- **p.M210I, p.M210K, p.M210T, p.M210V**
- **p.I211N, p.I211T**
- **p.Y214C**
- **p.E221K**
- **p.M235R, p.M235T, p.M235V**
- **p.R250P**
- **p.V452L**
- **p.V455E, p.V455M**
- **p.A456P**

The three in-frame indels listed above are also strong structural candidates.

The following **15 missense substitutions are plausible secondary or edge-case effects** rather than the strongest direct-binding candidates:

- **p.Y61N**
- **p.I159M, p.I159V**
- **p.C220F, p.C220R, p.C220S, p.C220W, p.C220Y**
- **p.R250C, p.R250H**
- **p.C252F, p.C252W**
- **p.S453L, p.S453W**

These are structural predictions. A conclusion that a particular allele changes MRK affinity would ideally be confirmed by an MRK binding or activation assay.

### Primary structural reference

Kamata K, Mitsuya M, Nishimura T, Eiki J, Nagata Y. **Structural basis for allosteric regulation of the monomeric allosteric enzyme human glucokinase.** *Structure*. 2004;12:429–438. DOI: **10.1016/j.str.2004.02.005**; PMID: **15016359**.

### Completed plan

1. [✓] Retrieve GCK ClinVar variants and save/inspect the complete result
2. [✓] Establish the 1V4S–P35557 mapping and identify MRK as the allosteric activator
3. [✓] Calculate MRK contacts within 6 Å and map them to ClinVar positions
4. [✓] Retrieve and join AlphaMissense scores for all intersecting missense variants
5. [✓] Audit synonymous, indel, and truncating consequences for completeness
6. [✓] Integrate structural evidence and present the final binding-impact assessment
=== END RUN rqbq6wgmbf1 ===

=== RUN rgldaht1c4v ===
QUESTION:
Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C02_b] [critical] [judged] the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PTP1B (P18031) — 1T4J chain A residue contact network and shortest path

**Setup**
- Structure: PDB **1T4J**, chain A (RCSB title: *"Allosteric Inhibition of Protein Tyrosine Phosphatase 1B"*; X-ray, released 2004-07-20). Chain A maps to UniProt **P18031** residues 1–298, identity 1.0.
- Allosteric ligand: **FRJ** — 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethyl-benzofuran-6-sulfonamide derivative; the only ligand bound in chain A (BioLiP: 1 ligand, 1 interaction).
- Closest polymer residue to FRJ: **Glu276 (A.276)**, minimum heavy-atom distance **2.55 Å** (next closest: Phe280 at 2.65 Å). This is unchanged at the 4.0 Å and 4.5 Å contact cutoffs (11 contacts at 4.0 Å; 14 at 4.5 Å).
- Catalytic residue: **Cys215 (A.215)** — nucleophilic cysteine of the PTP1B `HCXAGXXR` motif (`…VVVHCSAGIGRS…`, P18031 position 215).

**Network**
- Tool: `biomni.tool.[TOOL].[TOOL]` (Biotite 1.6.0 mmCIF parser + NetworkX 3.6.1), heavy-atom contact graph.
- **Cutoff used: 4.5 Å** (module constant `_CONTACT_CUTOFF_A = 4.5`; an edge exists when any pair of heavy atoms of two residues is ≤ 4.5 Å apart). Seeds: 42; community algorithm: louvain.
- Network size: **282 residues, 1379 edges** (independently rebuilt and matched exactly).

**Shortest path (allosteric-site residue → catalytic Cys215)**

**A.276 (GLU) → A.188 (PRO) → A.191 (PHE) → A.110 (LEU) → A.215 (CYS)**

- **Path length: 4 edges (5 residues)** — the minimum possible between these two nodes.
- Per-edge heavy-atom minimum distances: **3.82 Å (276–188), 3.16 Å (188–191), 3.84 Å (191–110), 4.41 Å (110–215)** — all within the 4.5 Å cutoff.

**Tied alternatives (same 4-edge length; 5 shortest paths exist in total)**
1. 276 GLU – 188 PRO – 191 PHE – 110 LEU – 215 CYS (3.82, 3.16, 3.84, 4.41 Å) ← returned by the tool
2. 276 GLU – 192 LEU – 191 PHE – 110 LEU – 215 CYS (4.01, 1.33, 3.84, 4.41 Å)
3. 276 GLU – 192 LEU – 194 PHE – 110 LEU – 215 CYS (4.01, 3.24, 3.61, 4.41 Å)
4. 276 GLU – 188 PRO – 191 PHE – 221 ARG – 215 CYS (3.82, 3.16, 4.27, 4.00 Å)
5. 276 GLU – 192 LEU – 191 PHE – 221 ARG – 215 CYS (4.01, 1.33, 4.27, 4.00 Å)

All paths traverse the β-sheet/loop region between the FRJ allosteric pocket (residues ~276–282) and the PTP loop, entering the catalytic site via Leu110 (or Arg221) adjacent to Cys215.

**Interpretation caveat:** the contact network encodes *geometric proximity* (heavy-atom distances ≤ 4.5 Å) only. A shortest path in this graph is not evidence that an allosteric signal is transmitted along those residues; experimental validation (e.g., mutational analysis, MD/NMA) would be required to support an allosteric communication mechanism. Also note the ligand-contact cutoff used to pick the anchor residue (4.0 Å in `[TOOL]`) is independent of the network cutoff (4.5 Å), and it does not change the anchor (Glu276 is closest either way).
=== END RUN rgldaht1c4v ===

=== RUN r523c6dqzee ===
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
All ligand, coordinate, and residue-numbering checks are complete.

### Plan
1. [✓] Retrieve 1OPK coordinate and metadata; enumerate its ligands and chains  
2. [✗] Initial P16 alias verification failed: P16 does not match PD180970’s formula/structure  
3. [✓] Calculate all residues within 4.0 Å of MYR using normalized mmCIF handling  
4. [✓] Recalculate with normalized atom-element handling  
5. [✓] Cross-check numbering and alternate locations with two independent parsers  
6. [✓] Identify P16 as PD166326 via the wwPDB/PDBe synonym record  
7. [✓] Verify PD166326’s ATP-site role and map contacts to UniProt numbering  
8. [✗] Final identity-check snippet failed because of a malformed quote  
9. [✓] Re-run the final human-sequence identity check and report results  

## Ligands in 1OPK

- **Myristoyl allosteric site:** **Myristic acid** — PDB chemical component **MYR**, chain A, residue 1; designated binding site **AC1**.
- **ATP site:** **PD166326** — PDB chemical component **P16**, chain A, residue 2; designated binding site **AC2**. PD166326 is an ATP-competitive Src/Abl inhibitor.

## Protein residues within 4.0 Å of MYR

Distances are the minimum heavy-atom distance from any atom of the residue to any heavy atom of MYR.

| PDB chain/residue | Human ABL1 P00519 equivalent | Minimum distance |
|---|---:|---:|
| **LEU359** | Leu340 | 3.836 Å |
| **LEU360** | Leu341 | 3.687 Å |
| **ALA363** | Ala344 | 3.706 Å |
| **LEU448** | Leu429 | 3.731 Å |
| **ALA452** | Ala433 | 3.854 Å |
| **GLU481** | Glu462 | 3.474 Å |
| **ILE521** | Ile502 | 3.874 Å |
| **LEU529** | Leu510 | 3.541 Å |

Thus, the residue list is:

**LEU359, LEU360, ALA363, LEU448, ALA452, GLU481, ILE521, LEU529 — all in chain A.**

The nearest excluded residue is **ILE451**, at 4.068 Å. The deposited `SITE AC1` record lists only the curated pocket residues Leu360, Glu481, and Leu529; the table above is the broader coordinate-defined 4 Å contact set. Three crystallographic waters—HOH577, HOH680, and HOH753—are also within 4 Å but are not protein residues.

**Metadata note:** Although the question identifies the entry as human ABL1/P00519, the deposited 1OPK macromolecule is **mouse ABL1, UniProt P00520** (SH3–SH2–kinase construct, D382N mutation). The kinase-domain sequence maps 1:1 to human P00519 at these positions, so the human equivalents are included above.

**Sources:** [RCSB 1OPK](https://www.rcsb.org/structure/1OPK), [PDBe ligand records](https://www.ebi.ac.uk/pdbe/api/pdb/entry/molecules/1opk), [PubChem PD166326, CID 447700](https://pubchem.ncbi.nlm.nih.gov/compound/447700); Nagar et al., *Cell* 112:859–871 (2003), [PMID 12654251](https://pubmed.ncbi.nlm.nih.gov/12654251/), [doi:10.1016/S0092-8674(03)00194-6](https://doi.org/10.1016/S0092-8674(03)00194-6).
=== END RUN r523c6dqzee ===

=== RUN r82ojnr6vih ===
QUESTION:
For TEM-1 beta-lactamase (UniProt P62593), predict cryptic-pocket residues from 1BTL with PocketMiner, retrieve UniProt variants, and list every annotated variant position within 6 angstroms of a residue that contacts the allosteric inhibitor in PDB 1PZO.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V06_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[V06_b] [critical] [judged] the PocketMiner cryptic-pocket residues of 1BTL, the UniProt variants of TEM-1 and every annotated variant within 6 A of a 1PZO CBT-contact residue are listed

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

Using the literal criterion—**the annotated variant residue is within 6 Å of a residue that contacts the allosteric inhibitor**—the complete UniProt position set is:

**67, 235, 236, 237, 261, and 272.**

If the intended criterion was instead **the variant residue itself is within 6 Å of the inhibitor**, the subset is:

**235, 261, and 272.**

## Workflow and results

1. [✓] Load 1BTL and run PocketMiner, retaining its cryptic-pocket residue predictions.
2. [✓] Retrieve all sequence-altering UniProt `VARIANT` annotations for P62593 and normalize their positions.
3. [✓] Identify the allosteric inhibitor in 1PZO, calculate its polymer-residue contacts within 6 Å, and map those contacts to UniProt numbering.
4. [✓] Intersect the mapped contact positions with every annotated UniProt variant and report the complete matched list with provenance.

### PocketMiner prediction from 1BTL

PocketMiner scored 263 protein residues:

- Mean score: **0.495868**
- Score ≥0.5: **124 residues**
- Score ≥0.7: **70 residues**
- Score ≥0.8: **41 residues**
- Score ≥0.9: **10 residues**

PocketMiner does not prescribe a universal residue cutoff, so these should be treated as screening-level cryptic-pocket-opening propensities rather than confirmed pocket assignments. The ten highest-scoring residues, expressed in canonical P62593 numbering, were:

| UniProt position | Residue | 1BTL residue | PocketMiner score |
|---:|---|---|---:|
| 232 | Lys | A:234 | 0.951411 |
| 243 | Ile | A:246 | 0.942519 |
| 170 | Ala | A:172 | 0.941106 |
| 241 | Arg | A:244 | 0.928997 |
| 260 | Tyr | A:264 | 0.926471 |
| 215 | Ala | A:217 | 0.920834 |
| 233 | Ser | A:235 | 0.917947 |
| 218 | Leu | A:220 | 0.916830 |
| 262 | Thr | A:266 | 0.905837 |
| 64 | Phe | A:66 | 0.905050 |

The complete 263-residue prediction is saved as `/agent_cwd/1BTL_pocketminer_result.json`.

### UniProt variants retrieved

The UniProt endpoint returned **11 annotations at 10 unique positions**:

| Position | Reference → alternative | Description |
|---:|---|---|
| 19 | L→F | TEM-4 |
| 37 | Q→K | TEM-2, TEM-3, TEM-8, TEM-16, TEM-24 |
| 67 | M→L | IRT-4 |
| 102 | E→K | TEM-3, TEM-4, TEM-6, TEM-8, TEM-16, TEM-24 |
| 162 | R→H | TEM-6, TEM-16 |
| 162 | R→S | TEM-5, TEM-8, TEM-24 |
| 235 | A→T | TEM-5, TEM-24 |
| 236 | G→S | TEM-3, TEM-4, TEM-8 |
| 237 | E→K | TEM-5, TEM-24 |
| 261 | T→M | TEM-4 |
| 272 | N→D | IRT-4 |

### Allosteric inhibitor and contact geometry

PDB 1PZO identifies ligand **CBT** as a:

> “novel, core-disrupting, 2 allosteric inhibitor”

Chemical component: **N,N-bis(4-chlorobenzyl)-1H-1,2,3,4-tetrazol-5-amine**. Two CBT instances are present in chain A, at PDB residue numbers 300 and 301.

Using heavy-atom geometry against both CBT instances, **33 polymer residues** lie within 6 Å of CBT. PDB author numbering was mapped to canonical P62593 numbering by sequence alignment because the crystal structure contains the mature chain while UniProt numbering includes the signal peptide.

### Final matched variant positions

| UniProt position | Annotated alternative | PocketMiner score | Direct distance to CBT, Å | Nearest other CBT-contact residue | Distance to that residue, Å | Within 6 Å of CBT-contact set |
|---:|---|---:|---:|---|---:|---|
| **67** | M→L, IRT-4 | 0.755940 | 6.767 | Ser68 / PDB Ser70 | **1.323** | **Yes** |
| **235** | A→T, TEM-5/TEM-24 | 0.892082 | 3.556 | Gly234 / PDB Gly236 | **1.327** | **Yes** |
| **236** | G→S, TEM-3/TEM-4/TEM-8 | 0.812030 | 6.565 | Ala235 / PDB Ala237 | **1.337** | **Yes** |
| **237** | E→K, TEM-5/TEM-24 | 0.790595 | 9.919 | Ala235 / PDB Ala237 | **4.789** | **Yes** |
| **261** | T→M, TEM-4 | 0.765603 | 5.979 | Tyr260 / PDB Tyr264 | **1.331** | **Yes** |
| **272** | N→D, IRT-4 | 0.869319 | 3.068 | Arg273 / PDB Arg277 | **1.323** | **Yes** |

The remaining annotated positions were excluded because their nearest qualifying contact residue was farther than 6 Å:

- Position **37**: 6.749 Å
- Position **102**: 6.200 Å
- Position **162**: 10.165 Å; both annotations at this position fail
- Position **19**: not spatially assessable because it lies in the N-terminal signal peptide and is absent from the mature 1PZO crystal chain

The complete integrated table is saved as:

`/agent_cwd/P62593_integrated_PocketMiner_CBT_variant_results.csv`
=== END RUN r82ojnr6vih ===

=== RUN roly0ro3ba0 ===
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
### Completed plan
1. [✓] Loaded 2SHP and 5EHR structures and their UniProt mappings.
2. [✓] Identified SHP099 as PDB chemical component **5OD** and mapped its chain-A contact residues to Q06124 numbering.
3. [✓] Ran PocketMiner on a chain-A-only 2SHP protein structure.
4. [✓] Ranked the 491 scored residues and compared the mapped SHP099 site with the top ten.
5. [✓] Verified that 5EHR chains A and B produce the same UniProt contact-residue set.

### Mapping and analysis details

- **Target:** SHP2/SHP099, UniProt **Q06124**
- **Autoinhibited structure:** PDB **2SHP**, chain A
- **Allosteric-site reference:** PDB **5EHR**, SHP099 component **5OD**
- **Contact criterion:** minimum heavy-atom distance ≤ **4.0 Å**
- **Contact residues:** 15
- **PocketMiner:** 491 observed chain-A residues scored
- Both 5EHR chains A and B contact the same 15 Q06124 residues, so the chain choice does not alter the mapped site set.
- The deposited PDB mappings align 2SHP and 5EHR residues 1–525 with Q06124 1–525. Residue identities were also checked at all 15 mapped positions.

### Mapped SHP099-contacting residues

| 2SHP residue | UniProt residue | SHP099 distance (Å) | PocketMiner score | Overall rank |
|---|---:|---:|---:|---:|
| THR108 | THR108 | 3.13 | 0.812907 | 55 |
| GLU110 | GLU110 | 3.47 | 0.837000 | 45 |
| **ARG111** | **ARG111** | 3.14 | **0.914450** | **3** |
| PHE113 | PHE113 | 2.79 | 0.788521 | 64 |
| HIS114 | HIS114 | 3.75 | 0.793019 | 61 |
| **THR218** | **THR218** | 3.69 | **0.914970** | **2** |
| **THR219** | **THR219** | 3.59 | **0.903089** | **6** |
| GLU249 | GLU249 | 3.29 | 0.742998 | 84 |
| GLU250 | GLU250 | 3.10 | 0.778364 | 66 |
| THR253 | THR253 | 3.30 | 0.857999 | 29 |
| LEU254 | LEU254 | 3.46 | 0.843834 | 41 |
| GLN257 | GLN257 | 3.58 | 0.604418 | 170 |
| PRO491 | PRO491 | 3.45 | 0.849655 | 38 |
| LYS492 | LYS492 | 3.45 | 0.856215 | 31 |
| GLN495 | GLN495 | 3.57 | 0.690155 | 112 |

Bold entries are also among the ten highest-scoring residues.

### Ten highest-scoring 2SHP chain-A residues

| Rank | 2SHP residue | UniProt residue | PocketMiner score | SHP099-contact residue? |
|---:|---|---|---:|:---:|
| 1 | ARG220 | ARG220 | 0.924785 | No |
| 2 | **THR218** | **THR218** | **0.914970** | **Yes** |
| 3 | **ARG111** | **ARG111** | **0.914450** | **Yes** |
| 4 | PRO9 | PRO9 | 0.906765 | No |
| 5 | LYS129 | LYS129 | 0.904989 | No |
| 6 | **THR219** | **THR219** | **0.903089** | **Yes** |
| 7 | SER460 | SER460 | 0.901755 | No |
| 8 | PRO33 | PRO33 | 0.899030 | No |
| 9 | LYS325 | LYS325 | 0.891857 | No |
| 10 | ARG32 | ARG32 | 0.891590 | No |

### Are the SHP099 site residues among the high scorers?

**Yes, partially.** Three of the 15 SHP099-contacting residues occur in the strict PocketMiner top ten:

- **THR218 — rank 2**
- **ARG111 — rank 3**
- **THR219 — rank 6**

The broader site is also strongly enriched for elevated PocketMiner scores:

- SHP099-site mean score: **0.8125**, versus **0.5021** across all 491 scored residues.
- SHP099-site median score: **0.8370**, versus **0.5039** globally.
- **All 15** site residues score above the global mean.
- Only **3/15** exceed the top-ten cutoff score of **0.891590**.

Thus, PocketMiner identifies the SHP099 site as generally high-scoring and places three central site residues among the ten strongest candidates, although it does not rank every contacting residue in the top ten. PocketMiner scores reflect cryptic-pocket propensity rather than direct ligand contacts, so the ranking supports—but does not itself prove—correspondence with the allosteric site.
=== END RUN roly0ro3ba0 ===

=== RUN r6ovsbufx8y ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**STINGAllo result for PTP1B (PDB 1T4J, chain A):**

- **Predicted allosteric residues:** None — the service returned an empty list (`residues: []`).
- **Service-response timestamp:** **2026-10-28 11:20:44 UTC** (`query_time_utc`).

The query completed successfully (`success: true`). An empty result means that STINGAllo did not return predicted residues for this structure/query; it does not by itself establish that no allosteric sites exist.
=== END RUN r6ovsbufx8y ===

=== RUN reykh0cmz73 ===
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
### Result

**PDB:** 1T4J — human protein-tyrosine phosphatase 1B (PTP1B; UniProt **P18031**)  
**Bound allosteric ligand:** **FRJ** (chain A, ligand residue 299)

FRJ is annotated in the Allosteric Database as an **allosteric inhibitor / inner protein regulator** (ASD02440027). Its chemical identity is:

- **IUPAC name:** 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethyl-N-[4-(1,3-thiazol-2-ylsulfamoyl)phenyl]-1-benzofuran-6-sulfonamide
- **Formula:** C₂₆H₁₉Br₂N₃O₇S₃
- **PubChem CID:** 448662

### Polymer residues within 4 Å of FRJ

Residues are given using **UniProt P18031 numbering**; distances are minimum heavy-atom distances.

| UniProt residue | Minimum distance |
|---|---:|
| Pro188 | 3.92 Å |
| Ala189 | 3.42 Å |
| Leu192 | 3.80 Å |
| Asn193 | 3.01 Å |
| Phe196 | 3.55 Å |
| Glu200 | 3.30 Å |
| Glu276 | 2.55 Å |
| Gly277 | 3.37 Å |
| Lys279 | 3.03 Å |
| Phe280 | 2.65 Å |
| Met282 | 3.59 Å |

**Residue list:** **P18031 Pro188, Ala189, Leu192, Asn193, Phe196, Glu200, Glu276, Gly277, Lys279, Phe280, and Met282.**

The calculation used a 4.0 Å heavy-atom contact cutoff. The PDB-to-UniProt mapping for chain A has 100% sequence identity in the covered region, and the resulting 11-residue set agrees with the curated ASD 1T4J allosteric site.

### Completed plan
1. [✓] Identified the ligand using BioLiP and Allosteric Database records
2. [✓] Retrieved FRJ contacts within 4 Å
3. [✓] Mapped PDB residue numbering to UniProt P18031
4. [✓] Validated and reported the ligand and residue list
=== END RUN reykh0cmz73 ===

=== RUN ra7od1yjx80 ===
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
## Summary for SHP2/PTPN11 (UniProt Q06124)

| Variant | ClinVar aggregate classification | AlphaMissense score¹ | 5EHR: distance to SHP099 | 2SHP: distance to PTP domain | Structural assignment |
|---|---|---:|---|---|---|
| **E76K** — p.Glu76Lys, c.226G>A | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications ([ClinVar 13336](https://www.ncbi.nlm.nih.gov/clinvar/variation/13336/)) | **0.9998**, **likely_pathogenic** | Side-chain minimum **14.714 Å** in chain A and **14.827 Å** in chain B; no direct contact | Side-chain minimum **2.797 Å** in chain A and **2.819 Å** in chain B | **Autoinhibitory N-SH2–PTP interface: yes. Allosteric inhibitor interface: no.** |
| **D61Y** — p.Asp61Tyr, c.181G>T | **Conflicting classifications of pathogenicity**; criteria provided, conflicting classifications ([ClinVar 228392](https://www.ncbi.nlm.nih.gov/clinvar/variation/228392/)) | **0.9985**, **likely_pathogenic** | Side-chain minimum **21.918 Å** in chain A and **21.974 Å** in chain B; all-heavy minimum **19.642/19.662 Å** | Side-chain minimum **3.751 Å** in chain A and **3.499 Å** in chain B; all-heavy minimum **3.689/3.499 Å** | **Autoinhibitory N-SH2–PTP interface: yes. Allosteric inhibitor interface: no.** |

¹ AlphaMissense’s official `am_pathogenicity` value from the canonical Q06124/ENST00000351677 release row. The separate dbNSFP/MyVariant converted `rankscore` values are **0.99585** for E76K and **0.9785** for D61Y.

### ClinVar condition-level context

- **E76K:** pathogenic submissions for JMML, Noonan syndrome 1, and PTPN11-related disorder; uncertain-significance submissions for RASopathy and some malignancy submissions.
- **D61Y:** pathogenic submissions for JMML and “not provided”; conflicting interpretations for Noonan syndrome 1.

## Coordinate-based interpretation

Distances were calculated from the deposited heavy atoms, excluding hydrogens. A **≤4.5 Å** heavy-atom criterion was used for direct contact; both autoinhibitory-interface assignments also remain valid at a stricter 4.0 Å cutoff.

### 5EHR allosteric inhibitor site

Ligand **5OD is SHP099**. Neither D61 nor E76 is part of its binding-site lining:

- **E76–5OD:** 14.714/14.827 Å, represented by **GLU76 OE2–5OD CL2**.
- **D61–5OD:** side-chain minimum 21.918/21.974 Å and all-heavy minimum 19.642/19.662 Å.
- Even the nearest atoms lining the SHP099 pocket are **11.094/11.255 Å from E76** and **16.325/16.436 Å from D61**.

Thus, neither residue directly contacts or lines the 5EHR allosteric inhibitor site.

### 2SHP autoinhibitory interface

The interface was defined as same-chain contacts between the UniProt-annotated **N-SH2 domain (6–102)** and **PTP domain (247–517)**. Both deposited chains reproduce the result:

- **D61:** contacts **Ser460** and **Arg465**:
  - Chain A: **ASP61 CG–SER460 OG = 3.751 Å**
  - Chain B: **ASP61 OD1–ARG465 CD = 3.499 Å**
- **E76:** contacts **Leu262, Arg265, Asn281, Phe285,** and **Ser502**:
  - Chain A: **GLU76 OE2–SER502 OG = 2.797 Å**
  - Chain B: **GLU76 OE2–SER502 OG = 2.819 Å**

Therefore, **both E76 and D61 are autoinhibitory-interface residues, whereas neither lies at the SHP099-binding interface in 5EHR**. These measurements describe the wild-type deposited coordinates; mutation-induced side-chain rearrangement is not modeled.

### Sources

- UniProt: [Q06124](https://rest.uniprot.org/uniprotkb/Q06124)
- AlphaMissense official release: [data](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz), [schema/README](https://storage.googleapis.com/dm_alphamissense/README.pdf), and [Science 2023](https://doi.org/10.1126/science.adg7492)
- PDB coordinates: [5EHR](https://www.rcsb.org/structure/5EHR), [2SHP](https://www.rcsb.org/structure/2SHP)
- Primary structural papers: [Chen et al., Nature 2016](https://doi.org/10.1038/nature18621); [Hofmann et al., Cell 1998](https://doi.org/10.1016/S0092-8674(00)80938-1)

**Updated plan**
1. [✓] Retrieve ClinVar classifications and AlphaMissense scores for PTPN11 E76K and D61Y.
2. [✓] Download PDB 5EHR and 2SHP coordinate data and identify the bound allosteric inhibitor and relevant interface atoms.
3. [✓] Calculate minimum heavy-atom distances from E76 and D61 to the 5EHR inhibitor and to the 2SHP autoinhibitory interface.
4. [✓] Reconcile the distance evidence with the structural interface definition and document any chain/alternate-location caveats.
5. [✓] Report the source-linked classifications, scores, distances, and conclusions.
=== END RUN ra7od1yjx80 ===

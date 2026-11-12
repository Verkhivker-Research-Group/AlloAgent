# AlloAgent v2 Benchmark: Design Draft (revision 2)

Status: DRAFT, nothing run. This revision (1) checks every identifier against UniProt and RCSB, and (2) restricts the benchmark to allosteric tasks that arm D's tools can perform.

## 0. Identifier verification (done 22 Oct 2026)

All 22 UniProt accessions in the first draft were looked up in UniProt, and the 15 PDB entries were read from RCSB header files. Accession-to-name checks:

| Accession | UniProt name | Used in benchmark |
|---|---|---|
| P00519 | ABL1, Tyrosine-protein kinase ABL1 | yes |
| P01116 | KRAS, GTPase KRas | yes |
| P18031 | PTPN1, Tyrosine-protein phosphatase non-receptor type 1 (PTP-1B) | yes |
| Q06124 | PTPN11, Tyrosine-protein phosphatase non-receptor type 11 (SHP-2) | yes |
| P62593 | bla, Beta-lactamase TEM (TEM-1) | yes |
| P35557 | GCK, glucokinase | yes |
| P31749 | AKT1, serine/threonine kinase | yes |
| Q02750 | MAP2K1, MEK1 | yes |
| P69441 | adk, E. coli adenylate kinase | yes |
| P04637 TP53, P15056 BRAF, P42336 PIK3CA, P38398 BRCA1, P13569 CFTR | correct names | removed: not allosteric tasks |
| P14618 PKM, Q16539 MAPK14, O15530 PDPK1, P09467 FBP1, P69905 HBA1/HBA2, O14757 CHEK1, P56817 BACE1, P11217 PYGM | correct genes | reserved for the development set |

Note: the second batch of 11 accessions was returned as a paraphrased summary (gene and protein description), not the raw table, so those are confirmed by gene and function, not by the exact UniProt protein-name string.

Sequence check: in canonical P00519, position 315 is threonine (context YIITEFM), so "ABL1 T315" is correct in UniProt numbering. PDB 5MO4 labels the same mutation T334I, so entries can use a different numbering. Mapping through UniProt is therefore a real test, not a formality.

PDB entries (title, ligands as read from the RCSB header):

| Entry | Content | Ligands (HET) | Note |
|---|---|---|---|
| 1T4J | PTP1B, "Allosteric inhibition of protein tyrosine phosphatase 1B" | FRJ (A 299) | allosteric ligand |
| 6OIM | KRAS G12C covalently bound to AMG 510 (sotorasib) | MOV (A 303), GDP, MG | ligand ID is MOV, not "sotorasib" |
| 1OPK | c-Abl SH3-SH2-kinase, autoinhibited | MYR (A 1), P16 (A 2, PD166326), GOL | MYR at myristoyl site, P16 at ATP site |
| 5MO4 | ABL1 T334I/D382N with asciminib and nilotinib | NIL (A 601), AY7 (A 602) | contains nilotinib, not imatinib |
| 2HYY | ABL kinase domain with imatinib | STI (chains A to D) | |
| 3CS9 | ABL with nilotinib | NIL (chains A to D) | |
| 1V4S | human glucokinase | GLC (A 500), MRK (A 501), NA | MRK = activator |
| 3O96 | AKT1 with allosteric inhibitor | IQO (A 444) | |
| 5EHR | SHP2 with SHP099 | 5OD (A 601, B 601), phosphates | SHP099 ligand ID is 5OD |
| 2SHP | SHP-2 tyrosine phosphatase | CAT (detergent) | autoinhibited, no inhibitor |
| 1PZO | TEM-1 with core-disrupting allosteric inhibitor | CBT (A 300, A 301) | two copies |
| 1BTL | TEM-1 at 1.8 A | SO4 | no inhibitor |
| 1AKE | E. coli adenylate kinase with AP5A | AP5 (A 215, B 215) | closed, ligand-bound form, not apo |
| 1UWH | wild-type B-RAF with sorafenib | BAX | no longer used |
| 1TSR | p53 core domain with DNA | ZN | no longer used |

Corrections this forced on the first draft: the ligand IDs (MOV, 5OD, AY7, FRJ, MRK) are used instead of drug names where a PDB search needs the ID; the old C06 asked for an imatinib/asciminib structure pair, but 5MO4 has asciminib with nilotinib, so the comparison now cites 2HYY for imatinib and 5MO4 for asciminib; 1AKE is the closed liganded form, so it is used only for contact-network and domain questions, not as an "apo" structure.

Not yet verified (do in the validation script, before checklists are final): the ligand-contact residue lists, SIFTS mappings, ClinVar and AlphaMissense values, ChEMBL counts, whether 3O96 models residue 17, and whether ChEMBL holds any SHP099 record against PTPN1.

## 1. What changed in this revision, and why

The first draft included tasks that were not allosteric (TP53 domains, BRAF V600E, BRCA1, CFTR, generic imatinib lookups) and a docking prompt. Those are removed. The rule now is that every prompt must (a) be about allosteric sites, ligands, communication or variants near them, and (b) be answerable with tools arm D actually has and has been verified.

Capability audit (what arm D can do, from the tool verification table):
- Verified and used: residue mapping (SIFTS), UniProt variants, STINGAllo, fpocket, P2Rank, PocketMiner (modest accuracy), normal mode analysis, residue contact network, PDB search by protein and ligand, ChEMBL (local), ClinVar and AlphaMissense (pending their final verdicts), ligand and contact analysis by agent-written structure code.
- Deliberately not tested: docking (failed its criterion), GPU-only models (not installed), ASD queries (optional data), literature search (not exposed), anything that needs a tool that was excluded.
- Honest gap: there is no dedicated "residues within X angstroms of a ligand" tool. Many prompts (S01 to S07, K02, K03, V01 to V06) depend on that step, which both arms must do with their own code. Adding one small, verified `get_ligand_contacts` tool would make arm D's advantage on these prompts about tooling rather than about who writes better code, and it is cheap. Decide whether to add it before the freeze; if not, the paper should say these prompts test code generation plus mapping, not a tool.

## 2. Composition

Total: 40 prompts. By tier: {1: 7, 2: 23, 3: 10} (1 = single lookup or single analysis, 2 = two to three coupled steps, 3 = multi-step with a conclusion).

| Category | Prompts |
|---|---|
| Site characterization | 7 |
| Pocket detection | 5 |
| Cryptic pockets | 2 |
| Dynamics & communication | 6 |
| Variants & allostery | 6 |
| Allosteric modulators | 5 |
| Allosteric site prediction | 3 |
| Synthesis | 4 |
| Honest reporting | 2 |

Proteins in the benchmark (prompt count each):

| Accession | Prompts |
|---|---|
| P18031 | 11 |
| P00519 | 7 |
| Q06124 | 7 |
| P35557 | 4 |
| P31749 | 3 |
| P62593 | 3 |
| P01116 | 3 |
| P69441 | 1 |
| Q02750 | 1 |

Only 9 proteins appear, and PTP1B, ABL1 and SHP2 carry most prompts. Prompts on the same protein are not independent, which lowers the effective sample size below 40. Options: accept and state this; or move some prompts to the reserved proteins (FBP1, PKM2, p38 alpha, PDK1) once their allosteric PDB entries are verified. I recommend adding 6 to 8 prompts on other proteins if time allows; it is the most useful change for validity.

Baseline route (Y = baseline can do it with standard tools or code and public web access; P = possible with extra work such as installs or knowing an API; N = needs a resource only arm D has: PocketMiner, STINGAllo, local ClinVar/AlphaMissense tables). Counts: {'P': 22, 'N': 16, 'Y': 2}. N prompts measure tool access; Y and P prompts measure whether the framework helps. Report the primary result on all 40 and the split by route. Open question: can the baseline sandbox reach the internet and install packages? If not, P becomes N for arm A.

## 3. How each prompt is tested

Each prompt names the protein, accession, PDB entry and (where relevant) ligand ID, and no tool. Each has: a validated accession; a checklist of 3 to 6 facts (critical or supporting) with a source; the tools arm D is expected to use (analysis only); and a blocklist entry for any tool that would return the checklist answer verbatim. Checklist items are, in order of preference: exact identifiers (script), numbers with tolerance (script or judge against the reference value), qualitative claims (judge against a written criterion). Ligand-stripped prompts (P01, P02, P05, P06, P07) test whether a pocket detector recovers a known allosteric site without being shown the ligand.

## 4. Scoring

Keep the v1 rubric for continuity and add: Correctness (fraction of critical items correct); primary success = Goal Completion full and all critical items correct; Unsupported claim (a specific number or residue with no supporting tool output in the trace); honest-reporting items correct only if the caveat is present. Judge: Claude Sonnet 5.5 with the checklist and masked outputs, fresh sessions of at most 10 runs; about 30 runs blind-scored by a human (an author). Script-checkable items are scored by script first.

## 5. Design and analysis

Arms A and D, 40 prompts x 3 repeats x 2 arms = 240 runs, paired by prompt: per-prompt success proportion, mean difference D minus A, bootstrap 95% CI over prompts, exact sign-flip test; mixed-model sensitivity with a prompt intercept; pooled Wilson and Fisher for continuity with v1. Secondary: correctness fraction, steps, time, tokens, early terminations by cause, failure events, tool calls. Pre-specified descriptive subgroups: tier, category, baseline route. Power (assumption): with per-prompt difference SD 0.30 to 0.40, about 14 to 18 points detectable at 80% power, less if the protein clustering above lowers the effective n. Estimate the SD from the development runs. Commit the analysis plan and checklists with checksums before the final run; a prompt found invalid afterwards is excluded in both arms and listed.

## 6. Bias controls

Leakage: tools are tuned on the development set only; the blocklist covers checklist answers. Identifiers: every accession and PDB entry is validated, so a null cannot be blamed on a bad prompt. Order: arms in separate processes from one image; shuffled run order; no state shared between repeats; the judge sees masked, shuffled outputs. Memory: the proteins are well known, so a model may answer parts from memory; most checklist items need computed values (contacts, ranks, distances, database counts), and the unsupported-claim score flags untied answers. Rate limits: STINGAllo is called for only 2 structures (1T4J, 5EHR), inside the 30-structure daily quota; check caching in the dev run.

## 7. Development set (disjoint proteins, not in the 40)

Candidates: PKM2 (P14618), p38 alpha (Q16539), PDK1 (O15530), FBP1 (P09467), hemoglobin alpha (P69905), CHK1 (O14757), BACE1 (P56817), muscle glycogen phosphorylase (P11217). Their allosteric PDB entries and ligand IDs still have to be verified the same way before prompts are written. Use: pipeline check, SD estimate, exposed-tool selection.

## 8. Decisions needed

1. Add a `get_ligand_contacts` tool before the freeze (recommended) or accept that these prompts test code generation.
2. Baseline sandbox internet and package access.
3. Broaden the protein set (recommended).
4. Human scorer sees checklists (recommended yes).
5. Numeric tolerances (suggest scores 0.01, distances 0.5 angstroms, IC50 exact to the database value).

## 9. Draft prompts

| ID | Tier | Accession | Prompt |
|---|---|---|---|
| S01 | 1 | P18031 | In PDB entry 1T4J (human PTP1B, UniProt P18031), identify the bound allosteric ligand and list the residues within 4 angstroms of it, using UniProt numbering. |
| S02 | 1 | P00519 | In PDB entry 1OPK (human ABL1, UniProt P00519), identify the ligand at the myristoyl allosteric site and the ligand at the ATP site, and list the residues within 4 angstroms of the myristoyl-site ligand. |
| S03 | 2 | P35557 | In PDB entry 1V4S (human glucokinase, UniProt P35557), identify the allosteric activator and the glucose ligand, list the residues within 4 angstroms of the activator, and give the minimum distance between the two ligands. |
| S04 | 2 | P31749 | In PDB entry 3O96 (human AKT1, UniProt P31749), identify the allosteric inhibitor, list the residues within 4 angstroms of it, and say which AKT1 domains (using UniProt domain boundaries) those residues belong to. |
| S05 | 2 | Q06124 | In PDB entry 5EHR (human SHP2, UniProt Q06124, chain A), list the residues within 4 angstroms of the allosteric inhibitor SHP099 and say which domains (N-SH2, C-SH2, PTP) they belong to. |
| S06 | 2 | P62593 | PDB entry 1PZO (TEM-1 beta-lactamase, UniProt P62593) contains two copies of an allosteric inhibitor. Identify them, list the residues within 4 angstroms of each copy, and say whether the two copies occupy the same pocket. |
| S07 | 3 | P00519 | PDB entry 5MO4 contains ABL1 bound to both asciminib and nilotinib. Identify each ligand, list the residues within 4 angstroms of each, state whether they occupy distinct sites, and explain how the entry's residue numbering relates to UniProt P00519 numbering. |
| P01 | 2 | P18031 | Remove all ligands from PDB entry 1T4J (PTP1B, UniProt P18031) and run pocket detection. Does any of the top three pockets overlap the site where the allosteric ligand was bound? Report the overlap as a number of shared residues. |
| P02 | 2 | P01116 | Remove all ligands from KRAS G12C PDB entry 6OIM (UniProt P01116) and run pocket detection. What is the rank of the pocket that contains the former position of the covalent inhibitor (switch-II pocket)? |
| P03 | 3 | Q06124 | Run pocket detection on the autoinhibited SHP2 structure 2SHP (UniProt Q06124). Do any of the top five pockets cover residues that contact SHP099 in PDB entry 5EHR? Map residues between the entries through UniProt numbering and report the overlap. |
| P04 | 2 | P62593 | Use PocketMiner on the TEM-1 beta-lactamase structure 1BTL (UniProt P62593). Report the ten highest-scoring residues and the scores of the residues that contact the allosteric inhibitors in PDB entry 1PZO, after mapping between the two entries. |
| P05 | 2 | P00519 | Remove all ligands from PDB entry 1OPK (ABL1, UniProt P00519) and run pocket detection. What is the rank of the pocket that covers the myristoyl site? |
| P06 | 2 | P35557 | Remove all ligands from PDB entry 1V4S (glucokinase, UniProt P35557) and run pocket detection. Do the top three pockets include the allosteric activator site and the glucose site? Report which pocket matches which site. |
| P07 | 3 | P18031 | On PTP1B entry 1T4J (UniProt P18031) with ligands removed, compare fpocket, P2Rank and PocketMiner: report the rank or score each assigns to the residues that contacted the allosteric ligand, and say which methods agree. State clearly what these methods can and cannot say about allosteric character. |
| C01 | 1 | P18031 | Run normal mode analysis on PTP1B (UniProt P18031, PDB 1T4J chain A). Where are the hinge residues of the slowest non-trivial mode, and how mobile is the WPD loop (the loop containing the catalytic Asp181) relative to the rest of the protein? |
| C02 | 2 | P18031 | Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used. |
| C03 | 2 | Q06124 | Run normal mode analysis on autoinhibited SHP2 (UniProt Q06124, PDB 2SHP). Compare the mobility of the residues that contact SHP099 in PDB entry 5EHR (mapped by UniProt numbering) with the rest of the structure. |
| C04 | 2 | P35557 | Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length. |
| C05 | 2 | P69441 | Build a residue contact network for E. coli adenylate kinase (UniProt P69441, PDB 1AKE chain A) at an 8 angstrom C-alpha cutoff and find communities. Report the algorithm and seed, and say how the communities relate to the LID, NMP and CORE domains. |
| C06 | 3 | P18031 | Assess possible allosteric communication in PTP1B (UniProt P18031, PDB 1T4J chain A) by combining normal mode analysis, a residue contact network path from the allosteric ligand site to Cys215, and STINGAllo predictions. State what each analysis supports and what it does not. |
| V01 | 2 | Q06124 | For SHP2 (UniProt Q06124), report ClinVar classification and AlphaMissense score for E76K and D61Y, and say whether each residue lies at the interface with the allosteric inhibitor site (PDB 5EHR) or in the autoinhibitory interface (PDB 2SHP), using distances from coordinates. |
| V02 | 2 | P31749 | For AKT1 (UniProt P31749), report ClinVar classification and AlphaMissense score for E17K, give the domain containing residue 17, and report its distance from the allosteric inhibitor in PDB entry 3O96 if the residue is modeled there. |
| V03 | 2 | P01116 | For KRAS (UniProt P01116), report ClinVar classification and AlphaMissense score for G12C, G12D and G12V, and the distance from residue 12 to the covalent inhibitor in PDB 6OIM. Do the scores distinguish the three variants? |
| V04 | 2 | P00519 | For ABL1 (UniProt P00519), report ClinVar classification and AlphaMissense score for T315I, and its distance from the ATP-site ligand and from the myristoyl-site ligand in PDB entry 1OPK. What do the distances suggest about which site the variant affects? |
| V05 | 3 | P35557 | For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding. |
| V06 | 3 | P62593 | For TEM-1 beta-lactamase (UniProt P62593), predict cryptic-pocket residues from 1BTL with PocketMiner, retrieve UniProt variants, and list every annotated variant position within 6 angstroms of a residue that contacts the allosteric inhibitor in PDB 1PZO. |
| L01 | 1 | P00519 | Which PDB entries contain human ABL1 (UniProt P00519) bound to asciminib (ligand ID AY7)? List the entry IDs. |
| L02 | 2 | Q02750 | Trametinib and cobimetinib are allosteric MEK inhibitors. Compare their ChEMBL IC50 records against human MAP2K1 (UniProt Q02750): number of records, median and best value for each. |
| L03 | 2 | P00519 | Compare ChEMBL bioactivity of asciminib (allosteric, myristoyl site) and imatinib (ATP site) against human ABL1 (UniProt P00519): record counts, assay types and best potency for each. Say which site each binds, citing a PDB entry for each. |
| L04 | 2 | Q06124 | Which PDB entries contain human SHP2 (UniProt Q06124) bound to SHP099 (ligand ID 5OD)? Also report whether ChEMBL holds bioactivity records for SHP099 against SHP2, and if so the assay types and best value; if not, say so. |
| L05 | 1 | P18031 | Which PDB entries contain human PTP1B (UniProt P18031) bound to ligand FRJ, the allosteric ligand in entry 1T4J? |
| K01 | 1 | P18031 | What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response. |
| K02 | 2 | P18031 | For PTP1B in PDB entry 1T4J chain A, how many of the residues STINGAllo predicts are among the residues within 4 angstroms of the bound allosteric ligand? Report both lists and the overlap. |
| K03 | 2 | Q06124 | For SHP2 in PDB entry 5EHR chain A, compare the residues STINGAllo predicts with those within 4 angstroms of SHP099. Report both lists and the overlap, and say whether the prediction recovers the tunnel site. |
| G01 | 3 | P01116 | Assess the switch-II pocket of KRAS G12C (UniProt P01116, PDB 6OIM): pocket detection on the ligand-stripped structure, ChEMBL bioactivity for sotorasib, ClinVar and AlphaMissense for G12C, and the distance from residue 12 to the inhibitor. Do the structural, chemical and variant evidence agree? |
| G02 | 3 | P00519 | Compare the ATP site and the myristoyl site of ABL1 (UniProt P00519): contacts from PDB 1OPK, pocket-detection rank of each site on the ligand-stripped structure, ChEMBL potency for imatinib and asciminib, and T315I (ClinVar, AlphaMissense, distance to each site). What does T315I imply for each class of inhibitor? |
| G03 | 3 | Q06124 | For SHP2 (UniProt Q06124), combine ClinVar and AlphaMissense for E76K and D61Y, distances to the autoinhibitory interface in 2SHP, pocket detection on 2SHP, and normal mode analysis. Does the evidence support activating variants destabilizing the autoinhibited state that SHP099 stabilizes? |
| G04 | 3 | P31749 | For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site? |
| H01 | 1 | P18031 | What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so. |
| H02 | 2 | P18031 | Using only pocket-detection output on PTP1B (PDB 1T4J, ligands removed), rank the top three pockets by how likely each is to be an allosteric site, and justify the ranking. |

## 10. Draft checklists and expected tools

| ID | D tools | Draft checklist (verify from source) | Baseline |
|---|---|---|---|
| S01 | map_residues_uniprot_pdb; structure code | Ligand FRJ (chain A 299); contact list computed from coordinates; SIFTS-mapped numbers | P |
| S02 | structure code; map_residues_uniprot_pdb | MYR at allosteric site; P16 at ATP site; contacts of MYR from coordinates | P |
| S03 | structure code | MRK activator; GLC; contacts; minimum ligand-ligand distance from coordinates | P |
| S04 | structure code; map_residues_uniprot_pdb | Ligand IQO (A 444); contacts; domain assignment from UniProt features | P |
| S05 | structure code; map_residues_uniprot_pdb | Ligand 5OD (A 601); contacts; domain assignment from UniProt features | P |
| S06 | structure code; map_residues_uniprot_pdb | Two CBT ligands (A 300, A 301); contacts for each; overlap of contact sets | P |
| S07 | structure code; map_residues_uniprot_pdb | AY7 and NIL; two contact sets with small or no overlap; numbering offset established from SIFTS (entry labels the mutation T334I) | P |
| P01 | detect_pockets_fpocket or p2rank; structure code | Ligand-stripped input; top-3 pockets; overlap with FRJ contact residues | P |
| P02 | detect_pockets_*; structure code | Ligand-stripped input; rank of pocket overlapping MOV contacts | P |
| P03 | detect_pockets_*; map_residues_uniprot_pdb | Pocket residue list; 5EHR contact list; both mapped to UniProt numbering; overlap count | P |
| P04 | PocketMiner wrapper; map_residues_uniprot_pdb | Ten top residues with scores; scores for 1PZO contact residues; mapping stated | N |
| P05 | detect_pockets_*; structure code | Ligand-stripped input; rank of pocket overlapping MYR contacts | P |
| P06 | detect_pockets_*; structure code | Ligand-stripped input; ranks for MRK site and GLC site | P |
| P07 | detect_pockets_fpocket; detect_pockets_p2rank; PocketMiner wrapper | Three method outputs with ranks/scores for FRJ contacts; agreement summary; caveat that detectors do not label allosteric pockets | N |
| C01 | normal_mode_analysis | Hinge residues; relative mobility of WPD loop residues; mapping to UniProt numbering | P |
| C02 | residue_contact_network; structure code | Closest residue from coordinates; path valid in graph; cutoff stated | P |
| C03 | normal_mode_analysis; map_residues_uniprot_pdb | Per-residue mobility; mapped site residues; comparison with distribution | P |
| C04 | residue_contact_network; structure code | Two contact residues chosen from coordinates; path valid in graph | P |
| C05 | residue_contact_network | Reproducible communities; algorithm/seed stated; domain relation from UniProt/literature | P |
| C06 | normal_mode_analysis; residue_contact_network; get_stingallo_allosteric_residues | Three analyses present; conclusion hedged; limits of each method stated | N |
| V01 | get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb | ClinVar classes; AM scores; distances computed from mapped residues | N |
| V02 | get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb | ClinVar class; AM score; PH domain; distance or statement that residue is not modeled | N |
| V03 | get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb | Three ClinVar classes and AM scores; distance; honest comment on resolution | N |
| V04 | get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb | ClinVar class; AM score; two distances from coordinates; hedged inference | N |
| V05 | get_clinvar_variants; map_residues_uniprot_pdb; get_alphamissense_score | Variants in site by coordinates; scores; hedged inference | N |
| V06 | PocketMiner wrapper; get_uniprot_variants; map_residues_uniprot_pdb | Predicted residues; variant list; pair list from coordinates | N |
| L01 | search_pdb_by_uniprot_and_ligand | Entry list from RCSB and PDBe, both routes agree; includes 5MO4 | Y |
| L02 | get_chembl_bioactivity | Counts, median, best per compound from ChEMBL 37 | P |
| L03 | get_chembl_bioactivity; search_pdb_by_uniprot_and_ligand | Counts and best values from ChEMBL 37; AY7 entry (5MO4) and STI entry (2HYY) retrieved | P |
| L04 | search_pdb_by_uniprot_and_ligand; get_chembl_bioactivity | Entry list (RCSB found 8 entries incl. 5EHR; re-derive); ChEMBL 37 has NO SHP099 record per validation, so correct answer is explicit absence | P |
| L05 | search_pdb_by_uniprot_and_ligand | Entry list from both routes; includes 1T4J | Y |
| K01 | get_stingallo_allosteric_residues | Residue list returned by the service; date | N |
| K02 | get_stingallo_allosteric_residues; structure code | Prediction list; contact list; overlap count | N |
| K03 | get_stingallo_allosteric_residues; structure code | Prediction list; contact list; overlap; hedged statement | N |
| G01 | pockets; ChEMBL; ClinVar; AlphaMissense; structure code | All components present; each consistent with the individual-tool checks; hedged conclusion | N |
| G02 | pockets; ChEMBL; ClinVar; AlphaMissense; structure code | Components present; claims for allosteric site separated from retrieved evidence | N |
| G03 | ClinVar; AlphaMissense; pockets; normal_mode_analysis | Components present; conclusion hedged; limits stated | N |
| G04 | ChEMBL; ClinVar; AlphaMissense; structure code | Components present; ChEMBL records for MK-2206 or an explicit absence; hedged conclusion | N |
| H01 | get_chembl_bioactivity | Validation found SHP099 absent from ChEMBL 37, so the correct answer is explicit absence; any invented value is wrong | P |
| H02 | detect_pockets_* | Ranking given with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets; no claim beyond the data | P |

## 11. Validation findings so far (agent run, 24 Oct; the full 40-prompt validation has NOT been run yet)

Confirmed from primary sources: 10 of 10 PDB entries exist with the named ligands (2SHP has none); contact counts at 4 A for the dev answers reproduce; ChEMBL 37: imatinib vs ABL1 94 IC50 rows (91 in nM), best 19.9 nM; trametinib 16, cobimetinib 11, asciminib 2, sotorasib 8 records; AlphaMissense KRAS G12C 0.9975, G12D 0.9984, G12V 0.9949, ABL1 T315I 0.9991, AKT1 E17K 0.9977; ligand+protein PDB lists: AY7+ABL1 = 5MO4, 8SSN; FRJ+PTP1B = 1T4J, 6B8Z; 5OD+SHP2 = 8 entries; STINGAllo returns 14 residues for 1T4J chain A and 314 for 5EHR chain A.

Problems that change prompts:
- SHP099 is not in ChEMBL 37. L04 and H01 were rewritten so that explicit absence is the correct answer. Any prompt that needs SHP099 potency from ChEMBL is invalid.
- AlphaMissense returned no entry for PTPN11 E76K or D61Y. Both are single-nucleotide changes, so a missing entry is suspicious. Before V01 and G03 use them, scan the raw table directly for any Q06124 rows (isoform suffix, different identifier). If truly absent, replace the AlphaMissense part for SHP2 with another SHP2 variant that is present, or drop that part and keep ClinVar.
- MK-2206 (G04) has not been checked in ChEMBL 37. Validate or replace.
- AKT1 residue 17 is modelled in 3O96, but the PDB author number differs from the UniProt number (UniProt 17 = label_seq_id 20). V02 and G04 are valid and double as a numbering trap.
- Pinned ClinVar release and the live API give slightly different counts (16,066 vs 16,106 unique; 4,138 vs 4,154). Checklists must use classification and tolerance bands, not exact counts, and record the release used.
- STINGAllo on 5EHR returns 314 residues, so K03's overlap with the SHP099 contacts will be high by chance. Report it against the base rate (314 of about 520 residues) or the prompt cannot show the prediction recovers the site.

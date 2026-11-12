# Judge batch 020 of 24

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

=== RUN r0zugx5704b ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**ChEMBL does have a record.** For SHP099 (**CHEMBL4060033**) against human PTP1B/PTPN1 (**P18031; CHEMBL335**), the reported IC50 is:

**>100,000 nM (>100 µM)**

This is a censored/no-50%-inhibition result rather than a finite measured IC50, indicating essentially no detectable inhibitory activity under that assay’s conditions.

- **Assay:** CHEMBL5145449  
- **Assay description:** Inhibition of wild-type PTP1B using DiFMUP as substrate  
- **Assay organism:** *Homo sapiens*  
- **Confidence score:** 9
=== END RUN r0zugx5704b ===

=== RUN r7vytul5130 ===
QUESTION:
What allosteric residues does STINGAllo predict for PTP1B (PDB 1T4J chain A)? Report the residues and the date of the service response.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K01_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**STINGAllo prediction for PTP1B (PDB 1T4J, chain A)**

**Predicted allosteric site-forming residues (AFRs): 14 total**
`129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282`

Residue identities (mapped from the deposited 1T4J chain A coordinates):
- Glu129, Glu130
- Ser187, Pro188, Ala189
- Leu192, Asn193
- Phe196
- Glu200
- Glu276
- Lys279, Phe280, Ile281, Met282

Clustered into contiguous segments: **129–130, 187–189, 192–193, 196, 200, 276, 279–282**

**Date of the service response: 2026-10-28 (Wednesday, 28 October 2026).** The REST JSON payload itself contains only `allosteric_residues`, `pdb_id`, and `chain_id`, so the response date is the server's HTTP `Date` header: `Wed, 28 Oct 2026 17:22:22 GMT` for the final canonical call (earlier calls in this session: 17:21:16 GMT and 17:21:29 GMT; the interactive results page: 17:21:56 GMT — all 2026-10-28).

**How it was obtained (reproducible):**
- REST endpoint (documented at `https://www.stingallo.cbi.cnptia.embrapa.br/apis`):
  `GET https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A` → HTTP 200, `{"allosteric_residues":["129","130","187","188","189","192","193","196","200","276","279","280","281","282"],"chain_id":"A","pdb_id":"1T4J"}`
- Independent cross-check through the interactive server page (`POST /visualize` with `pdb_id=1T4J`, `chain_id=A`, results page "1T4J chain A — STINGAllo results") embedded the identical residue array, confirming the prediction.

**Provenance:** STINGAllo (Computational Biology Research Group, CNPTIA, Embrapa) — method paper: *Protein allosteric site identification using machine learning and per amino acid residue reported internal protein nanoenvironment descriptors*, Computational and Structural Biotechnology Journal; web-server paper: *STINGAllo: a web server for high-throughput prediction of allosteric site-forming residues using internal protein nanoenvironment descriptors*, Briefings in Bioinformatics. Residue numbering is the STINGAllo-reported sequence numbering; amino-acid identities were added from the RCSB-deposited 1T4J chain A coordinates (annotation only, not from STINGAllo).
=== END RUN r7vytul5130 ===

=== RUN rwpzfzkwwcp ===
QUESTION:
For SHP2 (UniProt Q06124), combine ClinVar and AlphaMissense for E76K and D61Y, distances to the autoinhibitory interface in 2SHP, pocket detection on 2SHP, and normal mode analysis. Does the evidence support activating variants destabilizing the autoinhibited state that SHP099 stabilizes?

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G03_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[G03_b] [critical] [judged] the ClinVar and AlphaMissense records for E76K and D61Y, the distances to the 2SHP autoinhibitory interface, the pocket detection on 2SHP and the normal mode analysis are present, with the conclusion hedged and the limits stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Bottom line

**Yes—with strong direct support for E76K and substantial, though more indirect, support for D61Y.** Both substitutions lie in the N-SH2–PTP autoinhibitory interface and favor access to the PTP catalytic site. SHP099 acts through a **separate three-domain allosteric pocket** and stabilizes the closed, autoinhibited conformation; it does **not** directly contact E76 or D61.

Thus, the evidence supports the model:

> **Activating PTPN11 variants weaken the autoinhibitory N-SH2–PTP closure and increase the open-state population; SHP099 counters this by binding a separate N-SH2/C-SH2/PTP pocket and trapping the closed state.**

The strongest direct demonstration is for **E76K**. The D61Y conclusion remains mechanistically plausible but would be strengthened by a D61Y–SHP099 co-crystal or direct open/closed population thermodynamics.

## Evidence summary

| Evidence | E76K | D61Y | Interpretation |
|---|---:|---:|---|
| **ClinVar** | Variation 28375; local snapshot: “conflicting classifications of pathogenicity” | Variation 230257; local snapshot: “conflicting classifications of pathogenicity” | Supports clinical relevance, but does not identify gain-of-function mechanism or establish a consensus classification |
| **AlphaMissense** | **0.9998**, pathogenic | **0.9985**, pathogenic | Strong missense-pathogenicity support; not a direct activation or autoinhibition measurement |
| **2SHP interface geometry** | Minimum heavy-atom distance to PTP S502: **2.797 Å** | Minimum heavy-atom distance to PTP I463: **3.689 Å** | Both residues are direct components of the N-SH2–PTP autoinhibitory interface |
| **fpocket on 2SHP** | E76-containing pocket 5: 105.7 Å³; score 0.174; druggability 0.002 | D61-containing pocket 8: 202.4 Å³; score 0.144; druggability 0.001 | Small, low-confidence cavities adjacent to the variants; supportive but not decisive |
| **P2Rank on 2SHP** | E76 in pocket 14; score 1.31; probability 0.014 | D61 in pocket 10; score 3.22; probability 0.111 | Independently locates both sites near interface cavities, but with low confidence |
| **ANM normal modes** | Participates in interface-straining modes | Participates in interface-straining modes | The closed conformation has intrinsic collective motions capable of perturbing the interface; this does not model the mutation itself |
| **Direct experimental state comparison** | Open E76K has only 30 N-SH2–PTP residue-pair contacts versus 68 in 2SHP; SHP099-bound E76K has 72 or 66 contacts | MD predicts altered interface interactions and catalytic-site exposure; no verified D61Y–SHP099 co-crystal | Direct evidence for E76K; convergent computational/biophysical evidence for D61Y |

## 1. ClinVar and AlphaMissense

The local ClinVar records identify:

- **PTPN11 c.226G>A, p.Glu76Lys (E76K)** — ClinVar Variation **28375**
- **PTPN11 c.181G>T, p.Asp61Tyr (D61Y)** — ClinVar Variation **230257**

Both are summarized as having **conflicting classifications of pathogenicity**. Therefore, ClinVar should not be presented as providing a clean mechanistic or consensus activation label here.

AlphaMissense is more decisive for missense pathogenicity:

- **E76K:** 0.9998, classified pathogenic
- **D61Y:** 0.9985, classified pathogenic

These values strongly support that both substitutions are damaging, but AlphaMissense does not distinguish:

- gain-of-function versus loss-of-function,
- destabilization of autoinhibition from other activation mechanisms, or
- sensitivity to SHP099.

Indeed, the local AlphaMissense output classified all 19 possible substitutions at each position as pathogenic, indicating strong positional constraint but reducing variant-specific mechanistic discrimination.

## 2. Distance to the autoinhibitory interface in 2SHP

I analyzed chain A of 2SHP using:

- N-SH2: residues 1–115
- C-SH2: residues 116–220
- PTP: residues 221–525
- interface criterion: any heavy-atom contact ≤4.5 Å

The analysis identified **68 N-SH2–PTP residue-pair contacts** in 2SHP.

### D61

D61 is not merely close to the interface; it is an interface residue:

- closest PTP residue: **I463**, **3.689 Å**
- other contacting PTP residues include S460, A461, R465, and Q506

This agrees remarkably well with the D61Y molecular-dynamics study, which implicates the D61/Y61–Q506 and D61/Y61–C459–I463/R465 interaction network.

### E76

E76 is also a direct interface residue:

- closest PTP residue: **S502**, **2.797 Å**
- additional contacts include L262, R265, N281, and F285

Thus, both substitutions alter residues that physically stabilize the N-SH2 domain against the PTP domain.

## 3. Pocket detection

### Variant-adjacent cavities

fpocket identified:

- **Pocket 5:** contains E76, T73, E258, L261/L262, F285, R498, S502, and G503  
  Volume 105.7 Å³; score 0.174; druggability 0.002.
- **Pocket 8:** contains D61, T59, G60, PTP R465/Q510 and other residues  
  Volume 202.4 Å³; score 0.144; druggability 0.001.

P2Rank independently found:

- **Pocket 14:** E76 plus PTP residues 264/265/269; score 1.31; probability 1.4%.
- **Pocket 10:** D61 plus PTP residues 361/362/364/366/424/425/427/460/465; score 3.22; probability 11.1%.

These results support the presence of **small, geometry-dependent cavities around the interface residues**, but the low scores/probabilities show that these are not robust, preformed drug pockets.

### The actual SHP099 pocket is different

The experimental wild-type SHP099–SHP2 structure is **PDB 5EHR**. In chain A, SHP099 contacts:

- N-SH2: T108, E110, R111, F113, H114
- C-SH2: T218, T219
- PTP: E249, E250, T253, L254, Q257, P491, K492, Q495

In apo 2SHP:

- fpocket pocket 34 overlaps **all 15** experimentally contacted SHP099 residues, although it is a broad, low-scoring surface cleft: volume 1187.1 Å³, score 0.006, druggability 0.020.
- P2Rank pocket 5 overlaps three of the contact residues, score 6.01, probability 0.296.

Moreover:

- E76 is **14.714 Å** from bound SHP099 in 5EHR.
- D61 is **19.642 Å** from bound SHP099.
- In the E76K–SHP099 structures 6CMS and 6CRG, residue 76 remains approximately **15.7–16.3 Å** from the ligand.

Therefore, E76 and D61 do not directly contact SHP099. The inhibitor stabilizes the **domain arrangement** indirectly by binding a separate interface formed by all three domains.

## 4. Normal-mode analysis

ANM was run on the full 2SHP dimer and on isolated chain A, using the lowest 20 nontrivial Cα modes. I quantified:

- relative N-SH2–PTP centroid displacement,
- strain across the 68 interface residue pairs, and
- participation of D61 and E76.

### Full 2SHP dimer

Modes 1 and 2 had the largest relative domain-centroid displacement among the low modes:

- mode 1: **0.0384**, interface strain **0.00843**
- mode 2: **0.0460**, interface strain **0.00974**

Higher-frequency modes produced the largest mean contact strain, including modes 13, 18, and 16. Both D61 and E76 participate in several of these interface-straining modes.

### Isolated chain A

Removing chain B changed the spectrum but not the conclusion:

- mode 5: relative displacement **0.0466**, interface strain **0.0143**
- mode 6: relative displacement **0.0372**, interface strain **0.0173**

For example, in chain-A mode 6, D61 and E76 amplitudes were 0.0388 and 0.0270, respectively.

This demonstrates that the closed 2SHP conformation has collective motions that can deform the N-SH2–PTP interface and that both mutation sites are mechanically coupled to that region. However, ANM of wild-type 2SHP cannot calculate the mutation-induced free-energy change or prove that either variant shifts the open/closed equilibrium. Eigenvector signs are also arbitrary.

## 5. Direct experimental evidence for the proposed mechanism

### E76K: direct and strong

The primary structural study by Choi et al. provides the decisive evidence:

- unliganded E76K adopts an **open conformation**, with a 120° C-SH2 rotation, relocation of N-SH2 away from the catalytic-site mask, and exposure of the PTP active site;
- SHP099 restores E76K to a **closed, near-wild-type autoinhibited conformation**;
- E76K reduces SHP099 inhibitory potency by **more than 100-fold**;
- SHP099 potency inversely tracks the activating strength of the tested oncogenic variants;
- strongly activating variants can therefore be effectively resistant to SHP099 in cells.

The coordinate results in this analysis quantify the same effect:

| Structure | State | N-SH2–PTP contact pairs |
|---|---|---:|
| 2SHP wild type | closed | 68 |
| 6CRF E76K | open | 30 |
| 6CMS E76K + SHP099 | closed | 72 |
| 6CRG E76K + SHP099 | closed | 66 |

Thus, the open E76K structure retains only about **44%** of the wild-type interface residue-pair contacts, whereas ligand binding restores the interface to approximately wild-type or greater contact retention.

### D61Y: strong convergent support, but less direct

The D61Y-specific molecular-dynamics study found:

- increased flexibility in PTP regions H458–S460 and Q506–A509;
- secondary-structure changes that expose the catalytic region;
- altered interaction networks involving D/Y61–Q506, Q506–Q510, Q506–F251, Q506–G60/Y63, D/Y61–C459, and C459–I463/R465.

Combined with the 2SHP result that D61 directly contacts Q506/I463, this supports a mechanism in which D61Y weakens the autoinhibitory interface and increases catalytic-site exposure.

The 2018 SHP099 study did not test D61Y itself, so the following must be stated carefully:

- **D61V**, a closely related strongly activating N-SH2/PTP-interface mutation, was orders of magnitude less sensitive to SHP099 than wild type.
- That supports the mutation-family mechanism, but it is not direct D61Y evidence.

No verified D61Y–SHP099 closed-state co-crystal was obtained in this analysis.

## Mechanistic conclusion

The overall evidence supports the proposed model, but with appropriately different confidence levels:

### E76K — strong direct support

E76K is a direct N-SH2–PTP interface mutation. Its unliganded structure is open, loses more than half of the wild-type interface contacts, and is trapped back into a closed state by SHP099. The loss of SHP099 potency and cellular resistance of strongly activating variants are consistent with SHP099 relying on access to, and stabilization of, the closed conformation.

### D61Y — moderate-to-strong indirect support

D61Y lies directly in the autoinhibitory interface, has a nearly saturated AlphaMissense score, and has been independently modeled to alter the D61–Q506/C459 interaction network, expose the catalytic site, and increase active-state flexibility. It is therefore very likely to favor the open state. Direct D61Y-specific structural or thermodynamic data would still be needed to claim the same level of mechanistic certainty as E76K.

### Relationship to SHP099

SHP099 should be viewed as an **allosteric conformational trap**, not a residue-capping inhibitor:

- It binds a separate N-SH2/C-SH2/PTP pocket.
- E76 and D61 are not direct ligand-contact residues.
- Strong activating mutations shift the ensemble toward open conformations, reducing the thermodynamic advantage of SHP099.
- E76K can nevertheless be rebound to the closed state in vitro, explaining why the compound can retain some activity, although much weaker than against wild type.
- In phosphotyrosine-rich cellular environments, the continued stabilization of the open state makes strongly activating mutants particularly resistant.

## Important limitations

1. **ClinVar is not mechanism-specific.** The local records say conflicting classifications; functional gain-of-function evidence comes from the primary experimental literature.
2. **AlphaMissense predicts pathogenicity, not activation.** It cannot quantify interface destabilization or SHP099 sensitivity.
3. **Pocket detection is weak evidence by itself.** The variant-adjacent cavities are small and low-ranked, and P2Rank and fpocket do not agree strongly on their boundaries.
4. **Normal modes are not free-energy calculations.** They show accessible deformation directions, not mutant-induced state populations.
5. **D61Y evidence is less complete than E76K evidence.** A D61Y–SHP099 structure, HDX or SAXS ensemble, and equilibrium open/closed population measurements would provide the strongest confirmation.

## Key sources

- ClinVar Variation **28375** — E76K  
  https://www.ncbi.nlm.nih.gov/clinvar/variation/28375/
- ClinVar Variation **230257** — D61Y  
  https://www.ncbi.nlm.nih.gov/clinvar/variation/230257/
- PDB **2SHP** — autoinhibited wild-type SHP2
- PDB **5EHR** — wild-type SHP2–SHP099 complex
- PDB **6CRF** — open E76K SHP2
- PDB **6CMS**, **6CRG** — SHP099-bound E76K structures
- Nguyen et al., *Nature* 2016, PMID **27362227**, DOI **10.1038/nature18621**: SHP099 stabilizes the autoinhibited conformation.
- Choi et al., *Nature Communications* 2018, PMID **30375388**, DOI **10.1038/s41467-018-06823-9**: open E76K structure, SHP099-induced closure, and reduced inhibitor potency.
- Chen et al., 2018, PMID **30508783**, DOI **10.1016/j.compbiolchem.2018.10.013**: D61Y-specific molecular-dynamics mechanism.
- Ekert et al., *Protein Science* 2011, PMID **21365683**, DOI **10.1002/prot.22984**: structural basis of domain opening in SHP2 gain-of-function mutants.
- Communications Biology 2023, PMID **38129686**, DOI **10.1038/s42003-023-05682-5**: atomistic ensemble of active E76K SHP2.

### Final plan status

1. [✓] ClinVar records retrieved  
2. [✓] AlphaMissense scores retrieved  
3. [✓] 2SHP interface defined and variant distances calculated  
4. [✗] Initial pocket formatting failed because residue labels were parsed incorrectly; corrected and completed  
5. [✓] fpocket and P2Rank results cross-validated against experimental SHP099 contacts  
6. [✗] Initial ANM vector interpretation used the wrapper’s transposed serialization; corrected using verified ProDy mode vectors  
7. [✓] Interface strain and variant participation quantified  
8. [✓] Wild-type and E76K SHP099 co-crystals verified  
9. [✓] D61Y-specific mechanism literature retrieved without substituting D61V evidence  
10. [✗] Initial E76K comparison used unrelated PDB 6CRM; corrected to 6CRF  
11. [✓] Open versus ligand-bound E76K interface closure quantified  
12. [✓] Evidence integrated into the mechanistic conclusion
=== END RUN rwpzfzkwwcp ===

=== RUN rjnz6w2rzrz ===
QUESTION:
On PTP1B entry 1T4J (UniProt P18031) with ligands removed, compare fpocket, P2Rank and PocketMiner: report the rank or score each assigns to the residues that contacted the allosteric ligand, and say which methods agree. State clearly what these methods can and cannot say about allosteric character.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P07_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P07_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P07_c] [critical] [judged] the rank or score each of fpocket, P2Rank and PocketMiner assigns to the FRJ contact residues, which methods agree, and the caveat that a pocket detector cannot label an allosteric pocket
[P07_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P07_e] [critical] [scripted] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P07_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P07_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed plan

1. [✓] Verify 1T4J, FRJ, and the experimentally established allosteric site.
2. [✓] Define ligand-contact residues and prepare the ligand-free structure.
3. [✓] Run fpocket 4.0, P2Rank 2.5.1, and the original PocketMiner model.
4. [✓] Map pocket ranks and residue scores onto the contact residues.
5. [✓] Assess agreement and the limits of geometric pocket detection.
6. [✓] Assemble the comparison with sources and caveats.

## Result

### Input and contact definition

- Structure: human PTP1B [1T4J](https://www.rcsb.org/structure/1T4J), UniProt [P18031](https://www.uniprot.org/uniprotkb/P18031).
- The sole heteroatom record is **FRJ**, compound 2 from the allosteric-inhibitor study. It was removed, leaving 282 protein residues and 2,304 atoms.
- “Contacted” means at least one protein heavy atom within **4.5 Å** of FRJ. This gives 14 residues:  
  **Ser187, Pro188, Ala189, Leu192, Asn193, Phe196, Lys197, Glu200, Glu276, Gly277, Lys279, Phe280, Ile281, Met282**.
- At a stricter **4.0 Å** cutoff, the set is 11 residues; Ser187, Lys197, and Ile281 are the three added only at 4.5 Å.
- This is a **ligand-stripped holo/open structure**, not a true apo structure.

### Residue-level comparison

fpocket does not assign a native score to each residue; it assigns ranked pockets. Thus its column gives every overlapping pocket as **rank (native score; druggability score)**. P2Rank values are **residue score (probability)**; “none” means the residue was not assigned to a retained pocket. PocketMiner gives a **per-residue cryptic-pocket probability**; the rank is its competition rank among all 282 residues.

| FRJ-contact residue | fpocket: pocket rank (score; druggability) | P2Rank: residue score (prob.); retained pocket | PocketMiner: prob. (rank) |
|---|---|---|---|
| Ser187* | P7 (0.123; 0.005); P11 (0.069; 0.820) | 0.0961 (0.0022); none | 0.40 (#171) |
| Pro188 | P11 (0.069; 0.820) | 0.0775 (0.0017); none | 0.32 (#208) |
| Ala189 | P7 (0.123; 0.005); P11 (0.069; 0.820) | 0.4189 (0.0257); none | 0.38 (#180) |
| Leu192 | P11 (0.069; 0.820) | 1.1997 (0.1962); none | 0.54 (#102) |
| Asn193 | P7 (0.123; 0.005); P11 (0.069; 0.820) | 0.7399 (0.0780); none | 0.45 (#141) |
| Phe196 | P11 (0.069; 0.820) | 1.4705 (0.2742); none | **0.67 (#54)** |
| Lys197
=== END RUN rjnz6w2rzrz ===

=== RUN rxxqzj86eld ===
QUESTION:
Remove all ligands from PDB entry 1T4J (PTP1B, UniProt P18031) and run pocket detection. Does any of the top three pockets overlap the site where the allosteric ligand was bound? Report the overlap as a number of shared residues.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[P01_b] [critical] [scripted] [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}]
[P01_c] [critical] [judged] the top three fpocket pockets of the ligand-stripped 1T4J contain the residues FRJ contacted, and the overlap is reported as a count
[P01_d] [critical] [judged] the answer names the pocket-detection method it used (fpocket or P2Rank); an answer that does not name the method is wrong on this item
[P01_e] [critical] [judged] {"method": "fpocket", "rank_of_the_pocket_covering_the_site": 7, "overlap_of_the_covering_pocket": 2, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 0.235, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 2, "score": 0.167, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 3, "score": 0.142, "n_residues": 15, "site_residues_in_pocket": 0}, {"rank": 4, "score": 0.139, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 5, "score": 0.129, "n_residues": 12, "site_residues_in_pocket": 0}, {"rank": 6, "score": 0.123, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 7, "score": 0.123, "n_residues": 10, "site_residues_in_pocket": 2}, {"rank": 8, "score": 0.123, "n_residues": 15, "site_residues_in_pocket": 2}, {"rank": 9, "score": 0.076, "n_residues": 6, "site_residues_in_pocket": 0}, {"rank": 10, "score": 0.076, "n_residues": 9, "site_residues_in_pocket": 0}, {"rank": 11, "score": 0.069, "n_residues": 12, "site_residues_in_pocket": 8}, {"rank": 12, "score": 0.068, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 13, "score": 0.067, "n_residues": 11, "site_residues_in_pocket": 0}, {"rank": 14, "score": 0.062, "n_residues": 10, "site_residues_in_pocket": 0}, {"rank": 15, "score": 0.057, "n_residues": 7, "site_residues_in_pocket": 0}, {"rank": 16, "score": 0.028, "n_residues": 11, "site_residues_in_pocket": 1}, {"rank": 17, "score": 0.015, "n_residues": 8, "site_residues_in_pocket": 0}, {"rank": 18, "score": 0.003, "n_residues": 7, "site_residues_in_pocket": 0}]}
[P01_f] [critical] [judged] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P01_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**Yes. AutoSite pocket rank 2 overlaps the FRJ allosteric-ligand site, with 13 shared protein residues.**

| AutoSite pocket rank | Score | Energy | Pocket residues | Shared with FRJ site |
|---:|---:|---:|---:|---:|
| 1 | 34.85 | -97.04 | 15 | **0** |
| 2 | 32.39 | -98.31 | 13 | **13** |
| 3 | 29.47 | -74.08 | 14 | **0** |

The FRJ binding site was defined as protein residues with any heavy atom within **4.5 Å** of FRJ, giving 14 residues. Pocket 2 shared 13 of these:

- SER187
- PRO188
- ALA189
- LEU192
- ASN193
- PHE196
- LYS197
- GLU200
- GLU276
- GLY277
- LYS279
- PHE280
- ILE281

The only 4.5 Å FRJ-contact residue not assigned to pocket 2 was **MET282**.

At a stricter 4.0 Å contact cutoff, pocket 2 still overlaps the site, with **10 shared residues**. Pockets 1 and 3 remain at zero.

**Primary answer: 13 shared residues (AutoSite pocket rank 2).**

Reference structures: PDB **1T4J**, PMID **15258570**, DOI **10.1038/nsmb803**.  
Pocket detection: AutoSite, DOI **10.1093/bioinformatics/btw367**.
=== END RUN rxxqzj86eld ===

=== RUN rm6cmpbfyos ===
QUESTION:
What is the ChEMBL IC50 of the SHP2 allosteric inhibitor SHP099 against human PTP1B (PTPN1, UniProt P18031)? If ChEMBL has no such record, say so.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: HONEST-REPORTING

CHECKLIST (ground truth):
[H01_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[H01_b] [critical] [scripted] {"present": false, "count": 0, "molecule_in_chembl_37": false}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**ChEMBL does have a record.** The standardized ChEMBL result is:

> **IC50 >100,000 nM, equivalent to >100 µM**

This is a censored lower-bound result, **not** an exact IC50 of 100 µM; half-maximal inhibition was not reached at 100 µM under the assay conditions.

| Field | ChEMBL record |
|---|---|
| Compound | SHP099, `CHEMBL4060033` |
| Target | Human PTP1B/PTPN1, `CHEMBL335` |
| Target component | UniProt `P18031` |
| Activity ID | `24840632` |
| Assay ID | `CHEMBL5145449` |
| Standardized IC50 | `>100000 nM` |
| Original reported value | `>100 µM` |
| Assay type | Biochemical inhibition assay using DiFMUP as substrate |
| Assay confidence | 9, “Direct protein target assigned” |
| Source | Tang et al., *Eur J Med Chem* (2022), DOI: `10.1016/j.ejmech.2022.114106` |

Direct ChEMBL activity record:  
https://www.ebi.ac.uk/chembl/api/data/activity/24840632.json
=== END RUN rm6cmpbfyos ===

=== RUN rcbbsjvh3yd ===
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

**Target:** MAP2K1 / MEK1, human  
**UniProt:** Q02750  
**ChEMBL target:** CHEMBL3587  
**Metric:** standardized `IC50` activity records; lower values indicate greater measured potency.

| Compound | ChEMBL molecule ID | IC50 records | Median IC50 | Best IC50 (minimum) |
|---|---|---:|---:|---:|
| **Trametinib** | CHEMBL2103875 | **16** | **2.85 nM** | **0.48 nM** |
| **Cobimetinib** | CHEMBL2146883 | **11** | **4.2 nM** | **0.2 nM** |

### Interpretation
- **Trametinib has the lower median IC50:** 2.85 nM versus 4.2 nM for cobimetinib.
- **Cobimetinib has the lower single best value:** 0.2 nM versus 0.48 nM for trametinib.
- These are distributions across heterogeneous assays, so the median is more representative than the single minimum for typical potency.

### Record-quality check
- All records were already standardized to **nM** with exact (`=`) relations; no censored values required special handling.
- One cobimetinib record is ChEMBL-flagged as a **“Potential transcription error”** (activity ID **24984327**, 4200 nM). Excluding it changes the cobimetinib count to **10**, but its median remains **4.2 nM** and its best remains **0.2 nM**.
- Some cobimetinib records are marked as potential duplicates by ChEMBL; the primary statistics above follow the requested raw-record count.

### Source endpoints
- [Target CHEMBL3587](https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL3587.json)
- [Trametinib IC50 activities](https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL3587&standard_type=IC50&molecule_chembl_id=CHEMBL2103875)
- [Cobimetinib IC50 activities](https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL3587&standard_type=IC50&molecule_chembl_id=CHEMBL2146883)
=== END RUN rcbbsjvh3yd ===

=== RUN rz7rxttgsjv ===
QUESTION:
In PDB entry 1V4S (human glucokinase, UniProt P35557), identify the allosteric activator and the glucose ligand, list the residues within 4 angstroms of the activator, and give the minimum distance between the two ligands.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S03_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[S03_b] [critical] [scripted] [{"chain": "A", "pdb_number": 501}]
[S03_c] [critical] [scripted] [{"chain": "A", "pdb_number": 500}]
[S03_d] [critical] [scripted] {"uniprot_residues": [61, 62, 63, 64, 65, 66, 210, 211, 214, 215, 220, 235, 452, 455], "pdb_residues": [61, 62, 63, 64, 65, 66, 210, 211, 214, 215, 220, 235, 452, 455], "min_distances": {"61": 3.248, "62": 3.624, "63": 2.731, "64": 3.64, "65": 3.411, "66": 3.771, "210": 3.664, "211": 3.589, "214": 3.011, "215": 2.454, "220": 3.3, "235": 3.512, "452": 3.618, "455": 3.458}}
[S03_e] [critical] [scripted] 16.23

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PDB 1V4S — Human glucokinase (GCK, UniProt P35557)

**Structure context:** X-ray, space group **P 6₅ 2 2** (Z = 12 molecules/cell), one glucokinase molecule in the deposited asymmetric unit (chain A, residues 6–455 of UniProt numbering), plus bound glucose, a small-molecule allosteric activator, one Na⁺, and 149 waters. Primary citation: Kamata et al., *Structure* 2004;12:429–438 (PMID 15016359) — the paper that first revealed glucokinase's allosteric site.

### 1. The two ligands

| Role | PDB comp ID | Chemical name | Location | Heavy atoms | Identifiers |
|---|---|---|---|---|---|
| **Allosteric activator** | **MRK** | 2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide (a glucokinase activator, "GKA") | Chain A, residue **501** — the allosteric site (small domain / connecting region II / C-terminal helix) | 23 | InChIKey `YUCYMQBDBXVNCE-UHFFFAOYSA-N`; PubChem CID 449003; ChEMBL CHEMBL608393; DrugBank DB08210 |
| **Glucose** | **GLC** | α-D-glucopyranose | Chain A, residue **500** — the catalytic (active) site | 12 | WWPDB synonyms: alpha-D-glucose, glucose, D-glucose |

Also present: **NA** (sodium ion, residue 600) and 149 HOH waters. MRK's identity was cross-verified three ways: the deposited `_chem_comp` record, the RCSB chem_comp API, and ChEMBL CHEMBL608393 (identical canonical SMILES `Cn1ccnc1Sc1cc(C(=O)Nc2nccs2)c(N)cc1F`).

### 2. Residues within 4.0 Å of the allosteric activator (MRK) — 14 protein residues

| Residue | Min heavy-atom distance (Å) | Closest atom pair (protein…MRK) | Structural region |
|---|---|---|---|
| **TYR 215** | **2.454** | OH … N23 | Connecting region II |
| **ARG 63** | **2.731** | N … N4 | Small domain |
| **TYR 214** | 3.011 | CG … F14 | Connecting region II |
| **TYR 61** | 3.248 | O … C3 | Small domain (N-terminal loop) |
| **CYS 220** | 3.300 | O … C22 | Connecting region II |
| **THR 65** | 3.411 | N … N19 | Small domain |
| **VAL 455** | 3.458 | CB … O8 | C-terminal helix (small domain) |
| **MET 235** | 3.512 | CE … S16 | Connecting region II |
| **ILE 211** | 3.589 | CD1 … C12 | Connecting region II |
| **VAL 452** | 3.618 | CA … O8 | C-terminal helix (small domain) |
| **VAL 62** | 3.624 | C … N4 | Small domain |
| **SER 64** | 3.640 | OG … N19 | Small domain |
| **MET 210** | 3.664 | CE … C22 | Connecting region II |
| **PRO 66** | 3.771 | CD … N6 | Small domain / CR-II |

Plus one ordered water, **HOH 729**, at 3.76 Å from MRK.

The two closest protein contacts are the hydrogen bonds to the activator's terminal groups — **Tyr215 OH···N23 (2.45 Å)** and **Arg63 N···N4 (2.73 Å)**. The residue set (Val62/Arg63/Ser64/Thr65, Met210/Ile211/Tyr214/Tyr215/Cys220/Met235, Val452/Val455) is the canonical glucokinase allosteric-activator pocket, and it is completely disjoint from the catalytic-site shell around glucose (which is instead Asp205, Asn204, Thr168, Lys169, Ser151, Phe152, Pro153, Asn231, Cys230, Ile225, Glu256, Gln287, Glu290, Gly229).

### 3. Minimum distance between the two ligands

**16.23 Å** (heavy-atom GLC O4 ↔ MRK C22; 16.919 Å for the next pair, GLC O4 ↔ MRK S16)

- This is the minimum in the deposited asymmetric unit **and** the global minimum in the crystal: expanding all 12 symmetry operators of P 6₅ 2 2 gives the closest cross-copy GLC–MRK approach at 51.18 Å, so no symmetry-related contact is closer.
- Centroid-to-centroid separation: **19.97 Å**; closest van der Waals *surface* approach ≈ **13.0 Å** (center distance minus summed vdW radii).
- Conclusion: the activator and glucose occupy completely separate sites with no direct interaction — the ~16 Å gap is the physical separation between the allosteric site and the active site, which is the mechanistic basis for the allosteric coupling.

### Method note
Distances were computed on the deposited heavy-atom coordinates (no hydrogens are present in the file) and independently reproduced by three code paths: Biopython brute-force pairwise distances, `scipy.spatial.cKDTree` neighbour search, and `gemmi` `ContactSearch`/`NeighborSearch` run both in the asymmetric unit and with the periodic cell for symmetry-aware checking. All three agree exactly on the 14-residue 4 Å list and the 16.230 Å minimum.
=== END RUN rz7rxttgsjv ===

=== RUN rpk3jsgd9mv ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Combined evidence

| Evidence layer | Finding | Interpretation |
|---|---|---|
| **PDB 3O96 structure** | AKT1 chain A, P31749, 2.7 Å resolution; ligand **IQO** | IQO is a bound allosteric inhibitor |
| **IQO identity** | IQO is **Akt inhibitor VIII** (PubChem CID 135398501), **not MK-2206** | Structural contacts cannot be attributed to MK-2206 |
| **ASD site annotation** | The 3O96 site is an **Inhibitor / Inner Protein Regulator**, with **zero overlap** with the catalytic-site residues | The IQO site is noncatalytic/allosteric relative to the catalytic machinery |
| **≤4 Å ligand contacts** | W80, T82, V83, I84, E85, S205, L210, T211, L264, K268, V271, Y272, R273, D274, I290, T291, D292, C296 | The direct ligand pocket lies in the kinase domain, not in the PH domain |
| **Residue 17 geometry** | GLU17 is modeled and its minimum heavy-atom distance to IQO is **5.70 Å** | E17 is spatially close, but it is **not a direct ≤4 Å ligand contact** |
| **ChEMBL: MK-2206** | AKT1/CHEMBL4282; 19 IC50 records, median **10 nM**, range **5 nM–10 µM**; 12/19 ≤10 nM, 7/19 ≥2.24 µM; no Ki record | MK-2206 is a potent but assay-dependent AKT1 inhibitor; ChEMBL does not establish its residue-level contacts |
| **ClinVar** | AKT1 c.49G>A, p.Glu17Lys; ClinVar Variation ID **29022**; **Pathogenic**, multiple submitters, no conflicts | E17K has clear clinical/pathogenic significance |
| **AlphaMissense** | E17K pathogenicity score **0.9977**, classified pathogenic | Position 17 is highly constrained and functionally important |

## Conclusion

The evidence supports the **PH–kinase interface as a plausible indirect allosteric regulatory interface**, with E17 as a near-shell, functionally constrained candidate rather than a demonstrated direct ligand-contact residue.

Specifically:

- AKT1 is experimentally represented in ASD as having curated allosteric sites, and the IQO site in 3O96 is classified as an inhibitor/inner-protein-regulator site without catalytic-site overlap.
- E17 lies **5.7 Å** from IQO in the inhibitor-bound conformation, making it close enough to plausibly participate in second-shell communication between the PH domain and inhibitor-bound kinase domain.
- The pathogenic ClinVar classification and very high AlphaMissense score show that E17 is critical, but they do not distinguish interface disruption from local PH-domain misfolding, altered membrane binding, or another mechanism.
- MK-2206’s ChEMBL potency supports potent allosteric inhibition of AKT1 generally, but **MK-2206 is not the ligand in 3O96**. Therefore, its bioactivity cannot validate IQO’s contacts or the 5.7 Å E17–IQO distance.

**Overall confidence:**  
- **Strong:** AKT1 has allosterically inhibited ligand sites; IQO occupies a noncatalytic kinase-site pocket; E17K is pathogenic and highly constrained.  
- **Moderate/suggestive:** the PH–kinase interface participates indirectly in allosteric regulation and E17 is a candidate second-shell transmitter.  
- **Not established:** E17 is a direct MK-2206/IQO allosteric contact, or that MK-2206 acts through E17.

A definitive claim would require a **MK-2206-bound AKT1 structure**, direct binding measurements with E17K, and interface-distance/kinase-activity experiments showing that the mutation alters ligand binding or kinase regulation.
=== END RUN rpk3jsgd9mv ===

=== RUN rjmhcyfzfp5 ===
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
**3O96 inhibitor:** AKT inhibitor VIII (Akti-1/2; Inhibitor VIII, Compound 16h), PDB ligand **IQO**.

**4 Å contacts, chain A:**

- **PH domain (P31749 5–108):** Trp80, Thr82, Val83, Ile84, Glu85
- **Protein kinase domain (150–408):** Ser205, Leu210, Thr211, Leu264, Lys268, Val271, Tyr272, Arg273, Asp274, Ile290, Thr291, Asp292, Cys296
- **AGC-kinase C-terminal domain (409–480):** none

There are **18 contacts total**. The inhibitor binds at the **PH-domain/kinase-domain interface**, consistent with allosteric inhibition.
=== END RUN rjmhcyfzfp5 ===

# Judge batch 011 of 24

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

=== RUN rhyfghmc59c ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Bottom line

The combined evidence strongly supports the **AKT1 PH–kinase interface as a genuine, conformationally coupled, druggable allosteric site**. It also shows that **Glu17 is not a direct ligand-contact residue**: in PDB 3O96, the closest Glu17–ligand heavy atoms are **5.704 Å** apart. Instead, E17 controls the allosteric pocket indirectly through the interface network, notably a Glu17–Arg273 interaction. Consequently, the pathogenic/oncogenic E17K variant shifts AKT1 toward the active, membrane-associated “PH-out” state and can reduce sensitivity to PH-interface allosteric inhibitors.

### 1. Structural evidence from PDB 3O96

PDB 3O96 is the 2.7 Å X-ray structure of human AKT1 with **IQO**, which is **AKT inhibitor VIII**, not MK-2206.

The ligand binds at the combined interface of:

- the **PH domain**,
- the kinase **N-lobe**, and
- the kinase **C-lobe**.

Using a heavy-atom cutoff of ≤4.5 Å, the calculated IQO-contacting residues are:

- **PH domain:** Trp80, Thr82, Val83, Ile84, Glu85
- **Kinase domain:** Val201, Ser205, Leu210, Thr211, Leu264, Lys268, Val270, Val271, Tyr272, Arg273, Asp274, Ile290, Thr291, Asp292, Cys296, Tyr326

At the stricter ≤4.0 Å cutoff, 18 residues remain. Key features reported in the 3O96 paper include:

- π-stacking of the inhibitor with **Trp80** in the PH domain;
- a polar interaction involving **Lys268/Ser205**;
- direct binding-site separation from the ATP pocket of **more than 10 Å**.

Functionally, inhibitor VIII stabilizes the inactive, closed **“PH-in”** AKT conformation, blocking membrane recruitment and phosphorylation. This is a defining allosteric mechanism rather than ATP-site competition.

### 2. Where is Glu17?

Glu17 is explicitly modeled in chain A.

- Minimum **Glu17–IQO heavy-atom distance:** **5.704 Å**
- Closest pair: **Glu17 CG–IQO C6**
- Therefore, Glu17 is **not** a conventional direct ligand contact at either a 4.0 or 4.5 Å cutoff.

Nevertheless, Glu17 is functionally connected to the pocket. The 3O96 paper identifies a stabilizing **Glu17–Arg273 interface interaction**, with Arg273 itself being a direct IQO-contact residue. In the deposited coordinates, the closest Glu17 O–Arg273 N pair is 4.137 Å, consistent with the paper’s interpretation of an electrostatic/salt-bridge interaction in a 2.7 Å, hydrogen-free model.

The paper reports that:

- E17K removes this stabilizing interface interaction;
- the equilibrium shifts from closed **PH-in** toward open, membrane-associated **PH-out**;
- AKT inhibitor VIII is approximately **fivefold less potent against E17K** than against wild-type AKT1.

Thus, E17 behaves as an **allosteric coupling or second-shell hotspot**, not as a residue that directly touches the ligand.

### 3. ChEMBL evidence for MK-2206

MK-2206 is:

- **ChEMBL molecule:** CHEMBL1079175
- **AKT1 target:** CHEMBL4282, “RAC-alpha serine/threonine-protein kinase”

There are 32 ChEMBL activity records against AKT1. The dominant high-confidence direct measurements are:

- biochemical **IC₅₀ values of approximately 5–10 nM**;
- corresponding **pChEMBL values of approximately 8.0–8.3**;
- an 11 nM binding measurement in one assay.

This provides strong pharmacological evidence that the allosteric AKT mechanism is potently and selectively druggable. Cellular growth endpoints are much weaker, approximately 2.24–10 µM, reflecting pathway context, cell permeability, downstream rewiring, and exposure rather than weak target binding. One lower-confidence patent assay reports 3.489 µM and should be treated as assay-context heterogeneity.

A crucial identity caveat is that **MK-2206 is not the IQO ligand in 3O96**. Therefore:

- the 3O96 contact list describes **AKT inhibitor VIII**;
- ChEMBL MK-2206 data independently validate the allosteric mechanism and AKT1 target;
- the 3O96 contacts should not be assigned directly to MK-2206.

### 4. ClinVar and AlphaMissense for E17K

The variant is:

- **AKT1 NM_001382430.1:c.49G>A (p.Glu17Lys)**
- ClinVar **VCV000013983.20**
- dbSNP **rs121434592**

ClinVar reports:

- germline classification: **Pathogenic**, with criteria provided by multiple submitters and no conflicts;
- oncogenicity classification: **Oncogenic**;
- clinical impact classification: **Tier I – Strong**;
- associations including Cowdon syndrome 6, Proteus syndrome, and meningioma.

AlphaMissense reports for E17K:

- **am_pathogenicity score: 0.9977**
- classification: **Pathogenic**

The live AlphaMissense service independently includes Lys17 among the pathogenic substitutions at AKT1 residue 17. AlphaMissense and ClinVar establish that the variant is highly deleterious; they do not by themselves establish the drug-binding mechanism. Their importance here is that the variant’s clinical/oncogenic significance agrees with the experimentally demonstrated interface-disrupting mechanism.

## Integrated interpretation

The evidence supports the following model:

1. **The PH–kinase interface is a bona fide allosteric pocket.** A ligand can bind across the PH domain and both kinase lobes, far from the ATP site, and stabilize an inactive AKT conformation.
2. **Glu17 is an indirect but important allosteric determinant.** It does not contact inhibitor VIII directly, but it stabilizes Arg273 and therefore the closed pocket geometry.
3. **E17K converts the interface from a brake into an activation switch.** Loss of the Glu17–Arg273 interaction favors PH-out, membrane localization, and constitutive AKT signaling.
4. **This creates a plausible resistance mechanism for classical PH-interface allosterics.** The fivefold loss of inhibitor VIII potency on E17K demonstrates that a pathogenic interface mutation can alter inhibitor sensitivity even when the mutated residue is outside the ligand-contact shell.
5. **MK-2206 validates the pathway pharmacologically but not the exact 3O96 contacts.** Genotype-resolved MK-2206 measurements in AKT1-E17K would be needed to determine its specific potency or resistance against that mutant.

Therefore, the strongest conclusion is: **the PH–kinase interface is a structurally and pharmacologically validated allosteric site, and E17K is a highly pathogenic, oncogenic interface-destabilizing variant that can weaken—but does not necessarily abolish—susceptibility to this class of allosteric inhibitors.**

### Primary sources and data

- [RCSB PDB 3O96](https://www.rcsb.org/structure/3O96)
- Wu et al., PLOS ONE (2010), [doi:10.1371/journal.pone.0012913](https://doi.org/10.1371/journal.pone.0012913), PMID 20886116
- [ChEMBL MK-2206, CHEMBL1079175](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL1079175)
- [ChEMBL AKT1 target, CHEMBL4282](https://www.ebi.ac.uk/chembl/explore/target/CHEMBL4282)
- [ClinVar VCV000013983](https://www.ncbi.nlm.nih.gov/clinvar/variation/13983/)
- [Live AlphaMissense P31749 residue 17](https://alphamissense.hegelab.org/hotspotapi?uid=P31749&resi=17)
- Carpten et al., Nature (2007), [doi:10.1038/nature05933](https://doi.org/10.1038/nature05933)
- Landgraf et al., Biochemistry (2008), [doi:10.1021/bi801683k](https://doi.org/10.1021/bi801683k)
- Calleja et al., PLoS Biology (2009), [doi:10.1371/journal.pbio.1000017](https://doi.org/10.1371/journal.pbio.1000017)
- Lindsley et al., Bioorg. Med. Chem. Lett. (2005), [doi:10.1016/j.bmcl.2004.11.011](https://doi.org/10.1016/j.bmcl.2004.11.011)
=== END RUN rhyfghmc59c ===

=== RUN r0zaeqtr4ac ===
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
## SHP2/PTPN11 (UniProt Q06124)

| Variant | ClinVar classification | AlphaMissense | PDB 5EHR: allosteric inhibitor site | PDB 2SHP: autoinhibitory interface | Assignment |
|---|---|---:|---|---|---|
| **E76K** | **Conflicting classifications of pathogenicity**; review status: *criteria provided, conflicting classifications* | **0.9998 — pathogenic** | E76–SHP099 nearest heavy-atom distance: **14.71 Å** (chain A), **14.83 Å** (chain B). **Not in the inhibitor pocket.** | E76 contacts PTP-domain Ser502 at **2.80 Å** (chain A) and **2.82 Å** (chain B); additional contacts include Leu262, Arg265, and Phe285. **At the autoinhibitory interface.** | **Autoinhibitory N-SH2–PTP interface**, not the SHP099 allosteric site |
| **D61Y** | **Conflicting classifications of pathogenicity**; review status: *criteria provided, conflicting classifications* | **0.9985 — pathogenic** | D61–SHP099 nearest heavy-atom distance: **19.64 Å** (chain A), **19.66 Å** (chain B). **Not in the inhibitor pocket.** | D61 contacts PTP-domain Ile463 at **3.69 Å** in chain A and Arg465 at **3.50 Å** in chain B; Ser460 and Ala461 are also within approximately **3.64–3.77 Å**. **At the autoinhibitory interface.** | **Autoinhibitory N-SH2–PTP interface**, not the SHP099 allosteric site |

### Coordinate-based interpretation

- In **5EHR**, ligand component **5OD is SHP099**, confirmed by the deposited structure title, *“SHP2 in Complex with Allosteric Inhibitor SHP099.”* Residues directly contacting SHP099 are approximately 2.8–3.8 Å away, whereas:
  - E76 is **14.71–14.83 Å** away.
  - D61 is **19.64–19.66 Å** away.
  
  Thus, neither residue directly contacts the allosteric inhibitor.

- In **2SHP**, the autoinhibitory contact is between the N-SH2 domain and the PTP domain. The observed sub-4 Å contacts above place **both E76 and D61 directly on that interface**.

### Method and caveats

Distances were calculated from the official RCSB mmCIF coordinates as minimum heavy-atom distances, using the Q06124-to-PDB residue alignment. A direct interface was treated as approximately ≤4 Å, with ≤5 Å used as supporting evidence. These measurements use the deposited **wild-type** structures; they establish the starting locations of E76 and D61 but do not model side-chain rearrangements caused by E76K or D61Y.

ClinVar’s conflicting aggregate classification should not be interpreted as “benign,” and the AlphaMissense scores are computational pathogenicity predictions rather than clinical classifications.

### Completed plan

1. [✓] Retrieve ClinVar records for PTPN11 p.E76K and p.D61Y
2. [✓] Retrieve AlphaMissense scores for UniProt Q06124 positions 76 and 61
3. [✓] Identify the bound allosteric inhibitor in PDB 5EHR and calculate its nearest distances to E76/D61
4. [✓] Map E76/D61 in PDB 2SHP and calculate cross-domain distances at the N-SH2–PTP autoinhibitory interface
5. [✓] Integrate the evidence and report each residue’s interface assignment with method-specific caveats
=== END RUN r0zaeqtr4ac ===

=== RUN rb4mtvyhyyo ===
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
### Result

- **Myristoyl allosteric site:** **MYR — myristic acid** (C14H28O2)
- **ATP site:** **P16**, the pyridopyrimidinone inhibitor deposited as  
  **6-(2,6-dichlorophenyl)-2-{[3-(hydroxymethyl)phenyl]amino}-8-methylpyrido[2,3-d]pyrimidin-7(8H)-one**  
  *(commonly known as PD173955; no ATP molecule itself is bound).*

### Residues within 4 Å of MYR

All are in **chain A** of PDB 1OPK:

| PDB residue | Residue | Minimum heavy-atom distance |
|---|---:|---:|
| 359 | LEU | 3.84 Å |
| 360 | LEU | 3.69 Å |
| 363 | ALA | 3.71 Å |
| 448 | LEU | 3.73 Å |
| 452 | ALA | 3.85 Å |
| 481 | GLU | 3.47 Å |
| 521 | ILE | 3.87 Å |
| 529 | LEU | 3.54 Å |

Thus, the 4 Å MYR contact set is **LEU359, LEU360, ALA363, LEU448, ALA452, GLU481, ILE521, and LEU529**.

**Sequence-mapping note:** RCSB/SIFTS maps chain A of 1OPK to **mouse ABL1, UniProt P00520**, rather than human ABL1 P00519 stated in the question. The ligand identities and PDB residue numbers above are directly from entry 1OPK.

### Completed plan
1. [✓] Enumerate ligands and interactions recorded for PDB 1OPK  
2. [✓] Assign the myristoyl-site and ATP-site ligands using site-specific evidence  
3. [✓] Retrieve all residues within 4 Å of the myristoyl-site ligand  
4. [✓] Cross-check and present the ligand identities and residue list
=== END RUN rb4mtvyhyyo ===

=== RUN rlvlk2ycxvi ===
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
### Completed plan
1. [✓] Retrieved the 1OPK coordinates, chemical-component records, and binding-site annotations.
2. [✗] An initial RCSB nested-metadata query failed because a returned field was list-valued; replaced it with the deposited mmCIF `HET`/`SITE` records.
3. [✓] Assigned MYR and P16 to the myristoyl and ATP sites, respectively.
4. [✓] Calculated minimum heavy-atom distances from MYR to every ABL1 residue.
5. [✓] Cross-checked ligand identity and numbering against RCSB, PDBe, and the primary publication.

## Ligands

| Site | Component | Ligand |
|---|---|---|
| Myristoyl allosteric site | **MYR** | **Myristic acid** (tetradecanoic acid) |
| ATP site | **P16** | **PD166326**, formally 6-(2,6-dichlorophenyl)-2-{[3-(hydroxymethyl)phenyl]amino}-8-methylpyrido[2,3-d]pyrimidin-7(8H)-one |

The deposited `SITE` records explicitly identify MYR as the AC1 binding-site ligand and P16 as the AC2 ligand at the ATP site.

## ABL1 residues within 4.0 Å of MYR

Using 1OPK chain-A author residue numbering and including any protein residue with at least one heavy atom at a minimum distance of ≤4.0 Å from MYR:

| Residue | Minimum distance |
|---|---:|
| **LEU359** | 3.836 Å |
| **LEU360** | 3.687 Å |
| **ALA363** | 3.706 Å |
| **LEU448** | 3.731 Å |
| **ALA452** | 3.854 Å |
| **GLU481** | 3.474 Å |
| **ILE521** | 3.874 Å |
| **LEU529** | 3.541 Å |

Thus, the 4 Å myristoyl-pocket residue set is:

**LEU359, LEU360, ALA363, LEU448, ALA452, GLU481, ILE521, LEU529.**

### Numbering note

Although the question identifies the protein as human ABL1/P00519, the accession deposited in 1OPK is actually **ABL1_MOUSE/P00520**. The coordinates and `SITE` records use the deposited 1OPK numbering above. Mapped to canonical human P00519 sequence numbering, these residues correspond to:

**LEU340, LEU341, ALA344, LEU429, ALA433, GLU462, ILE502, LEU510.**

**Sources:** [RCSB PDB 1OPK](https://www.rcsb.org/structure/1OPK); deposited [1OPK mmCIF](https://files.rcsb.org/download/1OPK.cif); Choi et al., *Cell* (2003), [doi:10.1016/S0092-8674(03)00194-6](https://doi.org/10.1016/S0092-8674(03)00194-6).
=== END RUN rlvlk2ycxvi ===

=== RUN rmy15bzm2vl ===
QUESTION:
For AKT1 (UniProt P31749), combine the allosteric ligand contacts in PDB 3O96, ChEMBL bioactivity for the allosteric inhibitor MK-2206, ClinVar and AlphaMissense for E17K, and the distance from residue 17 to the ligand where modeled. What does the combined evidence say about the PH-kinase interface as an allosteric site?

INTENDED PROTEIN: RAC-alpha serine/threonine-protein kinase (P31749)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[G04_a] [critical] [scripted] {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"}
[G04_b] [critical] [judged] the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedged conclusion

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Bottom line

**The combined evidence strongly supports the AKT1 PH–kinase interface as a bona fide allosteric site and a pathologically important regulatory hotspot.**  

However, there are two important qualifications:

1. **The ligand in PDB 3O96 is Inhibitor VIII (PDB ligand IQO), not MK-2206.**
2. **E17K is an interfacial residue, but not a direct ligand-contact residue in 3O96.** Its closest heavy atom is **5.704 Å from Inhibitor VIII**, outside the usual 4.0–4.5 Å contact criterion. Nevertheless, E17 directly contacts kinase-domain residues **K297, R273, and D323**, so it can influence the allosteric network without touching the ligand.

Thus, E17K is best viewed as a **pathogenic perturbation of PH-domain/membrane regulation and PH–kinase coupling**, not as a mutation that directly blocks the MK-2206/Inhibitor VIII contact shell.

### Completed work log

1. [✓] Retrieved PDB 3O96 metadata and coordinates.
2. [✓] Calculated all ligand contacts and E17–ligand geometry.
3. [✗] Initial ChEMBL summarization failed because of a local result-key typo; raw responses were preserved.
4. [✓] Recovered and summarized MK-2206 ChEMBL bioactivity.
5. [✗] Initial variant-literature agent failed because it requires a Claude-model configuration.
6. [✓] Retrieved ClinVar and the exact official AlphaMissense E17K record directly.
7. [✗] Initial Europe PMC integration attempt hit a transient 503.
8. [✗] Literature integration exposed an incorrect premise: PDB 3O96 does not contain MK-2206.
9. [✗] First chemical-identity parser encountered a null RCSB metadata field.
10. [✓] Resolved IQO versus MK-2206 by formula, InChIKey, PubChem, ChEMBL, and the primary structure paper.
11. [✗] First PH–kinase interface calculation had an atom-pair unpacking bug.
12. [✓] Correctly established that E17 directly contacts K297, R273, and D323.
13. [✓] Synthesized the structural, pharmacological, and clinical-variant evidence.

## Evidence synthesis

### 1. PDB 3O96 defines a genuine PH–kinase allosteric pocket

PDB 3O96 is a **2.7 Å** AKT1 structure in which the PH domain nestles between the kinase N- and C-lobes. The primary paper describes the ligand as **Inhibitor VIII**, bound at the combined PH-domain/kinase-domain interface. It reports predominantly hydrophobic contacts, a ring-stacking interaction with **W80**, and only one direct hydrogen bond. The ligand stabilizes the closed, inactive **“PH-in”** AKT conformation and obstructs the activation-loop/αC changes required for kinase activation.

Using a **4.5 Å minimum heavy-atom distance**, the deposited coordinates give:

| Domain | Residues contacting IQO/Inhibitor VIII | Minimum distances |
|---|---|---|
| **PH domain, UniProt 5–108** | W80, T82, V83, I84, E85 | 3.413–3.948 Å |
| **Kinase domain, UniProt 150–408** | V201, S205, L210, T211, L264, K268, V270, V271, Y272, R273, D274, I290, T291, D292, C296, Y326 | 2.893–4.322 Å |

This distribution across two domains is the structural hallmark of an allosteric site rather than a conventional ATP-site inhibitor.

### 2. Important ligand-identity correction

The 3O96 ligand should **not** be labeled MK-2206:

| Compound | Identifiers | Formula / MW |
|---|---|---|
| **Inhibitor VIII / IQO** | PDB 3O96; PubChem CID **10196499**; ChEMBL **CHEMBL4780754** | **C34H29N7O**, 551.64 Da |
| **MK-2206** | ChEMBL **CHEMBL1079175**; PubChem CID **24964624** | **C25H21N5O**, 407.48 Da |

The 3O96 paper likewise calls its ligand “Inhibitor VIII” and reports AKT1/AKT2/AKT3 IC50 values of approximately **58/210/2119 nM**. Consequently:

- The 3O96 contact list is evidence for the **Inhibitor VIII** pocket.
- It is not a residue-level contact map for MK-2206.
- No E17–MK-2206 distance can be inferred from 3O96.

### 3. E17 is interfacial but peripheral to the ligand

Residue 17 is fully modeled as **GLU17**. In the 3O96 coordinates:

- Minimum **E17–IQO heavy-atom distance:** **5.704 Å**  
  - Contacting atoms: E17 CG–IQO C6
- E17 is therefore **not** part of the ≤4.5 Å ligand-contact set.

But E17 is not remote from the regulatory interface. It directly forms the following PH–kinase protein–protein contacts:

| E17 atom | Kinase residue | Distance |
|---|---|---:|
| O | K297 NZ | 3.919 Å |
| OE2 | R273 NH1 | 4.137 Å |
| OE1 | D323 OD2 | 4.400 Å |

Thus E17 is best viewed as an **interfacial/peripheral allosteric residue**: close enough to participate in the PH–kinase contact network, but not a direct ligand-contact determinant.

### 4. ChEMBL independently validates potent allosteric AKT1 inhibition by MK-2206

For MK-2206, **CHEMBL1079175**, ChEMBL records:

- Mechanism: **“Allosteric AKT inhibitor”**
- Direct interaction: yes
- Human AKT1 target: **CHEMBL4282**
- **32 AKT1-target activity records**
- Repeated single-protein AKT1 IC50 values of **5–10 nM**
- Binding records of **Kd 11 nM** and **69 nM**
- Full-length AKT1 cellular HTRF readout at approximately **10 nM**
- Much weaker cellular viability endpoints, approximately **2.24–10 μM**, which are downstream pharmacologic effects rather than evidence of direct binding

This independently establishes that MK-2206 is a potent, direct, allosteric AKT1 inhibitor. ChEMBL’s mechanism annotation does not itself specify residue-level contacts, so the PDB and ChEMBL evidence should be treated as complementary rather than as a literal same-ligand contact analysis.

### 5. E17K is strongly clinically and computationally deleterious

**ClinVar — VCV000013983**

- Variant: **NM_001382430.1(AKT1):c.49G>A, p.Glu17Lys**
- dbSNP: **rs121434592**
- GRCh38: **chr14:104780214 C>T**
- Germline classification: **Pathogenic**
  - criteria provided, multiple submitters, no conflicts
- Oncology classification: **Oncogenic**

ClinVar’s separate germline and oncology assertions should not be interpreted as proof that every E17K occurrence is inherited or somatic, but together they establish substantial clinical significance.

**AlphaMissense**

- Official canonical-transcript record: **ENST00000554848.5**
- **E17K score: 0.9977**
- Official class: **likely_pathogenic**
- Official threshold: likely pathogenic above 0.564

This is very strong computational evidence that E17K is highly deleterious, although AlphaMissense is not itself a clinical diagnostic classifier or a mechanistic experiment.

### 6. Mechanistic interpretation of E17K

The most direct functional work indicates that E17K changes the PH domain’s membrane-targeting behavior:

- The E17K PH domain has markedly increased affinity for **PI(4,5)P2**, enabling constitutive plasma-membrane localization and AKT activation (PMID **18954143**).
- Molecular-dynamics work has also reported increased conformational drift in the E17K PH domain (PMID **23741320**).
- Separately, experimentally designed **PH–kinase interface-disrupting AKT1 mutants** were shown to be constitutively active and less effectively inhibited by allosteric AKT inhibitors, demonstrating the importance of an intact interface (PMID **23134728**).

The last result concerns interface mutants as a class; it does not prove that E17K acts by the same mechanism. In fact, the E17K-specific literature points more strongly to altered lipid specificity and membrane recruitment.

## Conclusion

The evidence supports a **high-confidence, two-part conclusion**:

1. **The PH–kinase interface is a genuine, druggable allosteric site.**  
   A ligand can bridge the PH domain and both lobes of the kinase domain, and unrelated allosteric chemotypes such as MK-2206 potently inhibit AKT through this regulatory architecture.

2. **E17K is a pathogenic allosteric-interface residue, but not a direct MK-2206-contact residue.**  
   Its 5.704 Å distance from the 3O96 ligand and its direct contacts with K297/R273/D323 show that it lies at the interface one step away from the ligand shell. E17K can therefore perturb PH-domain conformation, lipid sensing, membrane recruitment, and PH–kinase coupling without occupying the inhibitor pocket.

Accordingly, **E17K should not be interpreted as “sterically blocking MK-2206.”** Its actual sensitivity or resistance to MK-2206 requires direct testing, especially because interface-disrupting AKT mutants can alter allosteric-inhibitor activity. The combined evidence instead supports a model in which E17K is a highly consequential pathogenic mutation that changes the conformational and membrane-regulatory network feeding into the PH–kinase allosteric state.

### Principal sources

- [PDB 3O96](https://www.rcsb.org/structure/3O96); Wu et al., *PLoS One* 2010, [PMID 20886116](https://pubmed.ncbi.nlm.nih.gov/20886116/), DOI [10.1371/journal.pone.0012913](https://doi.org/10.1371/journal.pone.0012913)
- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry)
- [ChEMBL MK-2206, CHEMBL1079175](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL1079175)
- [ClinVar VCV000013983](https://www.ncbi.nlm.nih.gov/clinvar/variation/13983/)
- [AlphaMissense official dataset](https://storage.googleapis.com/dm_alphamissense/AlphaMissense_hg38.tsv.gz); Cheng et al., DOI [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492)
- E17K lipid specificity: [PMID 18954143](https://pubmed.ncbi.nlm.nih.gov/18954143/)
- PH–kinase interface and allosteric-inhibitor resistance: [PMID 23134728](https://pubmed.ncbi.nlm.nih.gov/23134728/)
- E17K conformational dynamics: [PMID 23741320](https://pubmed.ncbi.nlm.nih.gov/23741320/)
=== END RUN rmy15bzm2vl ===

=== RUN rhskruh4b5k ===
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
**PDB:** 1T4J — human protein tyrosine phosphatase 1B (PTPN1), chain A  
**UniProt:** P18031

### Bound allosteric ligand
- **Chemical component:** **FRJ**
- **Chemical name:** 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethylbenzofuran-6-sulfonic acid [4-(thiazol-2-ylsulfamoyl)phenyl]amide
- **Molecular formula:** C₂₆H₁₉Br₂N₃O₇S₃
- The PDB title identifies the structure as **“Allosteric Inhibition of Protein Tyrosine Phosphatase 1B,”** and the ASD record classifies site 1T4J-1 as an inhibitor site with an **“Inner Protein Regulator”** function.

### Polymer residues within 4.0 Å of FRJ
Using UniProt P18031 numbering:

| Residue | Minimum heavy-atom distance (Å) |
|---|---:|
| **Pro188** | 3.92 |
| **Ala189** | 3.42 |
| **Leu192** | 3.80 |
| **Asn193** | 3.01 |
| **Phe196** | 3.55 |
| **Glu200** | 3.30 |
| **Glu276** | 2.55 |
| **Gly277** | 3.37 |
| **Lys279** | 3.03 |
| **Phe280** | 2.65 |
| **Met282** | 3.59 |

**Residue list:** **P188, A189, L192, N193, F196, E200, E276, G277, K279, F280, M282**.

The independently curated ASD record for 1T4J lists the identical 11-residue site.
=== END RUN rhskruh4b5k ===

=== RUN rjc6y41ppjj ===
QUESTION:
Build a residue contact network for glucokinase (UniProt P35557, PDB 1V4S chain A). Find the shortest path between a residue in contact with the allosteric activator and a residue in contact with glucose. Report the path and its length.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C04_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[C04_b] [critical] [judged] the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**PDB 1V4S, chain A; UniProt P35557**

A shortest path is:

**Val62 → Val203 → Asn204**

| Position | PDB residue | Role |
|---|---|---|
| 1 | **A.62 VAL** | Contacts the allosteric activator **MRK** (minimum heavy-atom distance: **3.62 Å**) |
| 2 | **A.203 VAL** | Intermediate network residue |
| 3 | **A.204 ASN** | Contacts **glucose (GLC)** (minimum heavy-atom distance: **2.96 Å**) |

**Shortest-path length: 2 edges**  
This path contains **3 residues**.

### Validation
- Residue-contact network: heavy-atom distance cutoff **4.5 Å**
- Graph size: **448 residues, 2,207 edges**
- Val62–Val203 distance: **4.186 Å**
- Val203–Asn204 distance: **1.332 Å**
- Direct Val62–Asn204 distance: **6.912 Å**, so no one-edge shortcut exists
- The network tool’s internal label-sequence IDs for this path are `A.52 → A.193 → A.194`; the table above uses standard **PDB author numbering**

There were 11 tied minimum-length endpoint combinations; the path above is one deterministic shortest representative.

### Provenance
- `[TOOL]`: confirmed 1V4S chain A ↔ P35557
- `[TOOL]` / `[TOOL]`: identified MRK and GLC and their contacting residues
- `[TOOL]`: annotated the matching 1V4S site as an **Activator** site
- `[TOOL]`: constructed the 4.5 Å contact graph and verified the path

### Completed plan
1. [✓] Identify and verify the allosteric-activator and glucose ligands
2. [✓] Compute ligand-contacting residues in chain A
3. [✓] Build the residue-contact network and calculate the shortest path
4. [✓] Validate and report the path and length
=== END RUN rjc6y41ppjj ===

=== RUN rg61c3fzuyn ===
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
### Plan status
1. [✓] Retrieve ClinVar and AlphaMissense annotations for AKT1 E17K.
2. [✓] Map residue 17 to its AKT1 domain.
3. [✓] Inspect PDB 3O96 and identify the inhibitor and modeled residue.
4. [✗] Initial distance calculation failed because of an unnecessary unavailable Biopython import.
5. [✗] Second attempt failed because the hetero-ligand was selected with an invalid numeric residue key.
6. [✓] Corrected calculation completed and independently reproduced.
7. [✓] Records, coordinates, compound identity, and citations verified.

## Results

| Item | Result |
|---|---|
| **Variant** | AKT1 p.Glu17Lys, E17K; UniProt **P31749**; `NM_001382430.1:c.49G>A`; dbSNP `rs121434592` |
| **ClinVar classification** | **Pathogenic** — germline classification; “criteria provided, multiple submitters, no conflicts” |
| **ClinVar oncogenicity** | **Oncogenic** — “criteria provided, multiple submitters, no conflicts” |
| **ClinVar record** | **VCV000013983.20** |
| **AlphaMissense score** | **0.9977** |
| **AlphaMissense class** | **Likely pathogenic** |
| **Domain containing residue 17** | **PH (pleckstrin-homology) domain**; UniProt annotates it as residues **5–108**. InterPro maps the corresponding PH/PKB PH domains to approximately residues 4–111. |
| **PDB 3O96 residue status** | **Modeled**: wild-type **GLU 17**, chain A, full occupancy |
| **Allosteric inhibitor** | **Inhibitor VIII**, PDB ligand **IQO**, bound to the PH domain |
| **Minimum Glu17–inhibitor heavy-atom distance** | **5.704 Å**, between Glu17 **CG** and IQO **C6** |
| **Cα-to-nearest-inhibitor-atom distance** | **7.836 Å** |

### Distance convention

The primary distance is the minimum Euclidean separation between any non-hydrogen atom of Glu17 and any non-hydrogen atom of inhibitor IQO in the deposited PDB coordinates. Two independent coordinate parsers agreed within \(3.2\times10^{-7}\) Å. If a centroid-based convention is preferred, the Glu17 atom centroid–IQO centroid separation is **15.627 Å** and the Cα–IQO centroid separation is **16.805 Å**.

**Important:** PDB 3O96 contains the **wild-type Glu17**, not an E17K model. Therefore, 5.704 Å describes the native Glu17 side chain in the inhibitor-bound structure; the exact corresponding distance for the mutant Lys17 side chain would require structural modeling.

### Sources

- [ClinVar VCV000013983](https://www.ncbi.nlm.nih.gov/clinvar/variation/13983/)
- [Ensembl VEP record with AlphaMissense enabled](https://rest.ensembl.org/vep/human/region/14:104780214-104780214/T?AlphaMissense=1); AlphaMissense dataset [DOI: 10.6019/tol.alphamissense2024-w.2024.00001.1](https://doi.org/10.6019/tol.alphamissense2024-w.2024.00001.1)
- [UniProt P31749](https://www.uniprot.org/uniprotkb/P31749/entry); [InterPro PH domain IPR001849](https://www.ebi.ac.uk/interpro/entry/InterPro/IPR001849/); [InterPro PKB PH domain IPR039026](https://www.ebi.ac.uk/interpro/entry/InterPro/IPR039026/)
- [PDB 3O96](https://www.rcsb.org/structure/3O96), [ligand IQO](https://www.rcsb.org/ligand/IQO), and [deposited coordinates](https://files.rcsb.org/download/3O96.pdb)
- Wu et al., *PLoS ONE* 2010, PMID [20886116](https://pubmed.ncbi.nlm.nih.gov/20886116/), DOI [10.1371/journal.pone.0012913](https://doi.org/10.1371/journal.pone.0012913)
=== END RUN rg61c3fzuyn ===

=== RUN rcknx5p3h5o ===
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
[P01_f] [critical] [scripted] [low-information item] {"method": "p2rank", "rank_of_the_pocket_covering_the_site": null, "overlap_of_the_covering_pocket": 0, "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0], "pockets": [{"rank": 1, "score": 7.22, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 2, "score": 2.03, "n_residues": 0, "site_residues_in_pocket": 0}, {"rank": 3, "score": 1.87, "n_residues": 0, "site_residues_in_pocket": 0}]}
[P01_g] [critical] [judged] the answer states the limit of the method: a pocket detector does not distinguish allosteric from orthosteric pockets, so a pocket overlapping the allosteric site is evidence of a pocket, not of allostery

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**No. None of the top three detected pockets overlapped the experimental allosteric-ligand site.**

| Ranked pocket | Fpocket score | Shared residues with FRJ site |
|---|---:|---:|
| Pocket 1 | 0.235 | **0** |
| Pocket 2 | 0.167 | **0** |
| Pocket 3 | 0.142 | **0** |

The reference site was the deposited PDB `SITE AC1` annotation for FRJ: Ala189, Asn193, Phe196, Glu200, Glu276, Gly277, Lys279, Phe280, and Met282. The same zero-overlap result was obtained using FRJ contact residues defined at 4.0, 4.5, and 5.0 Å. As a diagnostic check, the allosteric region was detected in lower-ranked pocket 11, which shared six residues with the reference site.

Reference: PDB 1T4J; Wiesmann et al., *Nat. Struct. Mol. Biol.* 11:730–737 (2004), DOI: 10.1038/nsmb803.
=== END RUN rcknx5p3h5o ===

=== RUN r6nv5g16tnm ===
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
## Results for PDB 1V4S

### Ligands

- **Allosteric activator:** **MRK** — chain A, ligand residue 501  
  Chemical name: **2-amino-4-fluoro-5-[(1-methyl-1H-imidazol-2-yl)sulfanyl]-N-(1,3-thiazol-2-yl)benzamide**
- **Glucose ligand:** **GLC** — chain A, ligand residue 500  
  Chemical name: **α-D-glucopyranose**

### Polymer residues within 4 Å of MRK

The following 14 residues are within the inclusive **≤4.0 Å** cutoff:

| Residue | Minimum heavy-atom distance to MRK (Å) |
|---|---:|
| TYR61 (Y61) | 3.25 |
| VAL62 (V62) | 3.62 |
| ARG63 (R63) | 2.73 |
| SER64 (S64) | 3.64 |
| THR65 (T65) | 3.41 |
| PRO66 (P66) | 3.77 |
| MET210 (M210) | 3.66 |
| ILE211 (I211) | 3.59 |
| TYR214 (Y214) | 3.01 |
| TYR215 (Y215) | 2.45 |
| CYS220 (C220) | 3.30 |
| MET235 (M235) | 3.51 |
| VAL452 (V452) | 3.62 |
| VAL455 (V455) | 3.46 |

For these residues, the PDB author numbering coincides with the canonical **UniProt P35557** numbering.

### Minimum distance between the two ligands

The minimum **MRK–GLC heavy-atom distance is 16.23 Å**, defined by:

- **MRK atom C22**
- **GLC atom O4**

Thus, the activator and glucose occupy separate binding sites and do not directly contact one another.

### Plan

1. [✓] Retrieve BioLiP ligand records for PDB 1V4S and identify glucose and the allosteric activator
2. [✓] Retrieve the residues within 4 Å of the allosteric activator
3. [✓] Calculate the minimum heavy-atom distance between the activator and glucose from the deposited structure
4. [✗] Cross-check residue numbering/chain assignments (initial alignment block unpacking failed)
5. [✓] Complete the corrected alignment/entry-metadata check and present the final result

Primary entry citation: Kamata et al., *Structure* (2004), PMID **15016359**, DOI **10.1016/j.str.2004.02.005**.
=== END RUN r6nv5g16tnm ===

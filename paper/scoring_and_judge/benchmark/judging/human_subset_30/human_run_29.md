# Human rating sheet: run ri6qrmbyvxr (29 of 30)

## Before you start

- You get one file per run with the same fields the judge sees: question,
  intended protein, checklist, and the final answer with arm labels and
  one-sided tool names removed.
- Do not open the key file, the judge outputs, or the run records.
- Score each run on its own. Do not go back and change a score after moving on.
- Aim for about 5 minutes per run. Stop and take a break after 10.

## Rubric (same as the judge)

Goal Completion: full / partial / deferred / null.
Data Grounding: 0 / 1 / 2.
Final Answer Complete: yes / no.
Checklist items: correct / incorrect / missing (skip items marked `scripted`).
For HONEST-REPORTING prompts, a clear and correct statement that the data do
not support a claim is full.

---

=== RUN ri6qrmbyvxr ===
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
=== END RUN ri6qrmbyvxr ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

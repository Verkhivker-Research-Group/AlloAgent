# Human rating sheet: run rbyhrzqqclc (25 of 30)

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

=== RUN rbyhrzqqclc ===
QUESTION:
Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C02_b] [critical] [judged] the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
**Residue contact network: PTP1B (P18031), PDB 1T4J, chain A**

**Allosteric ligand:** FRJ (RCSB chemical component ID; bound in chain A at residue 299). BioLiP's interaction record for 1T4J assigns FRJ the binding site A189/N193/F196/E200/E276/G277/K279/F280, which is distinct from the annotated catalytic site (D181, C215, R221, S222, Q262) — i.e. it is the allosteric-site ligand.

**Residue closest to the allosteric ligand:** GLU276 (A.276), minimum heavy-atom distance to FRJ = **2.55 Å** (next closest: PHE280 2.65 Å, LYS279 3.03 Å, ASN193 3.01 Å).

**Shortest path (A.276 → catalytic Cys215):**

| Step | Residue | Identity | Min heavy-atom distance to next residue |
|---|---|---|---|
| 0 | A.276 | GLU276 (ligand-proximal) | 3.82 Å |
| 1 | A.188 | PRO188 | 3.16 Å |
| 2 | A.191 | PHE191 | 3.84 Å |
| 3 | A.110 | LEU110 | 4.41 Å |
| 4 | A.215 | **CYS215 (catalytic)** | — |

**Path string:** `A.276 (GLU276) → A.188 (PRO188) → A.191 (PHE191) → A.110 (LEU110) → A.215 (CYS215)`

**Path length:** **4 edges** (5 residues; 4 residue–residue contacts)

**Cutoff used:** **4.5 Å** heavy-atom contact cutoff for the residue–residue contact graph (tool-internal constant `_CONTACT_CUTOFF_A = 4.5`; Biotope/Biotite mmCIF parsing, model 1, chain A amino-acid residues only, hydrogens and waters/ligands excluded). Network size: 282 residue nodes, 1379 edges; community detection Louvain, seed 42 (affects communities only, not the path).

**Other equal-length (4-edge) shortest paths found:** A.276→A.192→A.191→A.110→A.215; A.276→A.192→A.194→A.110→A.215; A.276→A.188→A.191→A.221→A.215; A.276→A.192→A.191→A.221→A.215.

**Provenance / caveats:** Ligand identity and contacts from `biomni.tool.biolip` (BioLiP snapshot) and `biomni.tool.[TOOL]` (RCSB structure, 4.0 Å ligand-contact cutoff, 11 contacts); network/path from `biomni.tool.[TOOL]` on the RCSB mmCIF for 1T4J (downloaded directly because no listed function supplies an mmCIF file); node identities verified against the mmCIF (A.215 = CYS, A.276 = GLU). The STINGAllo service returned an empty residue list for 1T4J chain A, so no prediction-based allostery annotation was available; FRJ's allosteric-site assignment rests on the curated BioLiP binding-site annotation. These are geometric contacts and a graph-theoretic shortest path — they indicate possible coupling routes but do not demonstrate that an allosteric signal is actually transmitted along this path.
=== END RUN rbyhrzqqclc ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

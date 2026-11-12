# Human rating sheet: run rsnhu96575y (2 of 30)

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

=== RUN rsnhu96575y ===
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
=== END RUN rsnhu96575y ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

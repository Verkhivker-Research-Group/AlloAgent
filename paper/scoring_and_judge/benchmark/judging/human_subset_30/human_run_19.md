# Human rating sheet: run rq2ddkpl3dv (19 of 30)

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

=== RUN rq2ddkpl3dv ===
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
=== END RUN rq2ddkpl3dv ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

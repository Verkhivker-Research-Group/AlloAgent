# Human rating sheet: run rtxpx2z4cqn (21 of 30)

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

=== RUN rtxpx2z4cqn ===
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
## Completed plan

1. [✓] Retrieved canonical human KRAS (UniProt P01116) and confirmed residue 12 is Gly.
2. [✓] Retrieved the exact ClinVar records for G12C, G12D, and G12V.
3. [✗] Advanced literature-search agent failed at initialization; the official AlphaMissense/VEP data were used instead.
4. [✗] First narrow VEP inspection had a syntax error; the corrected query succeeded.
5. [✓] Retrieved and cross-checked the three AlphaMissense scores.
6. [✗] First coordinate-calculation attempt had an indexing error; the corrected calculation succeeded.
7. [✓] Identified the covalent inhibitor and linkage in PDB 6OIM and independently recomputed the distance.
8. [✗] Optional ClinVar XML cross-check returned an empty set/rate-limit response; the primary ClinVar query records and VCV accessions were used.
9. [✓] Consolidated the results and comparison.

## Results

ClinVar classifications are context-dependent, so both the aggregate **germline** and **oncogenicity** classifications are shown.

| KRAS variant | Exact allele | ClinVar record and germline classification | ClinVar oncogenicity / clinical impact | AlphaMissense |
|---|---|---|---|---|
| **G12C**, p.Gly12Cys | NM_004985.5:c.34G>T; GRCh38 chr12:25,245,351 C>A | **VCV000012578.47** — **Likely pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9975** — likely pathogenic |
| **G12D**, p.Gly12Asp | NM_004985.5:c.35G>A; GRCh38 chr12:25,245,350 C>T | **VCV000012582.69** — **Pathogenic/Likely pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9984** — likely pathogenic |
| **G12V**, p.Gly12Val | NM_004985.5:c.35G>T; GRCh38 chr12:25,245,350 C>A | **VCV000012083.79** — **Pathogenic**; criteria provided, multiple submitters, no conflicts | **Oncogenic**; clinical impact **Tier I – Strong** | **0.9949** — likely pathogenic |

AlphaMissense scores were obtained through the official Ensembl VEP AlphaMissense plugin for canonical KRAS transcript **ENST00000311936.8**, corresponding to the P01116 residue-12 substitutions. Its thresholds are:

- likely benign: `<0.34`
- ambiguous: `0.34–0.564`
- likely pathogenic: `>0.564`

All three therefore fall in the **likely-pathogenic** category.

### G12C ClinVar record caveat

ClinVar also contains a separate allele **VCV001701193.30**, NM_004985.5:c.33_34delinsCT (p.Gly12Cys), classified **Pathogenic**. The table above uses the canonical single-nucleotide allele **c.34G>T / VCV000012578**.

## Distance in PDB 6OIM

PDB 6OIM is the structure of **human KRAS G12C covalently bound to AMG 510 (sotorasib)**. The deposited linker is:

`SG CYS A 12 — C25 MOV A 303`

where `MOV` is AMG 510 in its bound form.

- Deposited covalent-bond length: **1.81 Å**
- Independently recomputed from the coordinates: **1.805 Å**
- This is also the minimum atom-to-atom distance between Cys12 and the inhibitor.

Thus, the chemically meaningful **residue-12-to-covalent-inhibitor distance is 1.81 Å**. For comparison, an unweighted Cys12-atom-centroid to inhibitor-atom-centroid distance is **9.06 Å**, but that centroid distance does not represent the covalent contact.

This structural measurement applies specifically to **G12C**; it does not establish covalent binding of sotorasib to G12D or G12V.

## Do the scores distinguish the variants?

**Numerically, yes; categorically, no.**

The ordering is:

**G12D (0.9984) > G12C (0.9975) > G12V (0.9949)**

However:

- G12D versus G12C differs by only **0.0009**
- The full G12D–G12V range is only **0.0035**
- All three are near 1.0 and have the identical AlphaMissense class, **likely pathogenic**

Therefore, the scores provide **no meaningful categorical distinction** among these variants. The small numerical differences should not be interpreted as evidence that one is substantially more pathogenic or clinically consequential than the others. AlphaMissense is a computational pathogenicity predictor, not a clinical classification or a substitute for ClinVar and functional evidence.

### Sources

- UniProt P01116: https://www.uniprot.org/uniprotkb/P01116/entry
- ClinVar G12C: https://www.ncbi.nlm.nih.gov/clinvar/variation/12578/
- ClinVar G12D: https://www.ncbi.nlm.nih.gov/clinvar/variation/12582/
- ClinVar G12V: https://www.ncbi.nlm.nih.gov/clinvar/variation/12583/
- AlphaMissense data documentation: https://storage.googleapis.com/dm_alphamissense/README.pdf
- AlphaMissense paper: https://doi.org/10.1126/science.adg7492
- PDB 6OIM: https://www.rcsb.org/structure/6OIM
- Structure primary paper: https://doi.org/10.1038/s41586-019-1694-1
=== END RUN rtxpx2z4cqn ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

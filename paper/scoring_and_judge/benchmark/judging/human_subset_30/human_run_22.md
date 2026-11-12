# Human rating sheet: run rd8pa4rgjcm (22 of 30)

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

=== RUN rd8pa4rgjcm ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan status

1. [✗] Initial UniProt mapping validation — Biopython alignment-block format differed
2. [✗] Second alignment mapping attempt — Biopython coordinate layout mismatch
3. [✓] Validated PDB-to-P35557 mapping
4. [✗] First ClinVar summary rendering — pandas could not group list-valued positions
5. [✗] Second ClinVar summary rendering — pandas could not sort list-valued positions
6. [✓] Retrieved 1,454 human GCK ClinVar records and filtered to 65 contact-position records
7. [✗] Advanced literature agent — unavailable because it required a Claude backend
8. [✗] Initial bulk AlphaMissense probe — timed out while streaming
9. [✗] First GRCh38 table stream — stopped on the copyright header
10. [✗] Second GRCh38 table stream — chromosome ordering made chr7 inefficient to reach sequentially
11. [✗] Ensembl VEP query — public REST response did not include AlphaMissense plugin fields
12. [✗] First BGZF range extraction — header was outside the chr7 byte range
13. [✓] Extracted official P35557 AlphaMissense rows by validated BGZF byte-range access
14. [✓] Checked activator-binding interpretations against primary literature
15. [✓] Audited completeness and generated the final ranked tables

# Results

## Structural and retrieval criteria

- **Protein:** human glucokinase, UniProt [P35557](https://www.uniprot.org/uniprotkb/P35557/entry).
- **Structure:** [PDB 1V4S](https://www.rcsb.org/structure/1V4S), chain A.
- **Allosteric activator:** **MRK**, chain A residue 501. GLC residue 500 is glucose, not the activator.
- **Distance criterion:** minimum heavy-atom distance from the wild-type amino-acid residue to any MRK heavy atom; cutoff ≤6.0 Å.
- **Residue mapping:** for all relevant positions, PDB author numbering matches P35557 numbering.
- **ClinVar search:** `GCK[gene] AND 9606[Taxonomy ID]`, giving **1,454 records**. Applying the 24 structural contact positions gave **65 records**, including **40 missense** and **25 non-missense** records.
- **AlphaMissense:** obtained from the official Google DeepMind `AlphaMissense_hg38.tsv.gz` table. Scores are the calibrated `am_pathogenicity` values. Official classes are:
  - likely benign: <0.34
  - ambiguous: 0.34–0.564
  - likely pathogenic: >0.564

The structural contact positions are p.61, 62, 63, 64, 65, 66, 98, 159, 210, 211, 214, 215, 218, 220, 221, 222, 235, 250, 252, 451, 452, 453, 455, and 456. No retrieved ClinVar record was anchored at p.65 or p.218.

## AlphaMissense-scored ClinVar variants

Assessment codes:

- **D — likely direct effect:** side-chain contact ≤4.5 Å plus AlphaMissense likely-pathogenic.
- **D\*** — likely ligand-specific effect; experimental activator evidence is mixed.
- **A — likely allosteric effect:** established allosteric-site biology, but MRK-affinity direction is not established.
- **I — possible/indirect:** high AlphaMissense, but no side-chain contact ≤4.5 Å.
- **P — possible direct effect:** direct contact, but AlphaMissense is not likely-pathogenic.
- **L — no high AlphaMissense support:** contact alone is insufficient; ClinVar evidence may still override this.

| VCV | Protein change | AlphaMissense | Residue–MRK Å | Side-chain–MRK Å | ClinVar | Assessment |
|---|---|---:|---:|---:|---|---|
| VCV001444770 | p.Tyr61Asn | 0.8868 (LP) | 3.25 | 5.85 | VUS | I |
| VCV000585917 | p.Val62Ala | 0.9731 (LP) | 3.62 | 3.64 | Pathogenic | **D** |
| VCV000419624 | p.Val62Met | 0.9462 (LP) | 3.62 | 3.64 | Pathogenic | **D\*** |
| VCV001502971 | p.Arg63Leu | 0.3254 (LB) | 2.73 | 3.75 | VUS | P |
| VCV002779779 | p.Arg63His | 0.1886 (LB) | 2.73 | 3.75 | VUS | P |
| VCV000447391 | p.Arg63Cys | 0.1234 (LB) | 2.73 | 3.75 | VUS / uncertain risk | P |
| VCV002735015 | p.Ile159Asn | 0.9313 (LP) | 4.33 | 4.33 | Conflicting | **D** |
| VCV002700200 | p.Ile159Thr | 0.5886 (LP) | 4.33 | 4.33 | VUS | **D** |
| VCV000447403 | p.Ile159Met | 0.2207 (LB) | 4.33 | 4.33 | Conflicting | P |
| VCV001679549 | p.Ile159Val | 0.1611 (LB) | 4.33 | 4.33 | Pathogenic/Likely pathogenic | P |
| VCV002505485; VCV002505486 | p.Met210Val | 0.8229 (LP) | 3.66 | 3.66 | Likely pathogenic | **D** |
| VCV000016141 | p.Met210Lys | 0.9915 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV000804852 | p.Met210Thr | 0.9821 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV002691826; VCV000036236 | p.Met210Ile | 0.9915 (LP) | 3.66 | 3.66 | Pathogenic | **D** |
| VCV000435303 | p.Ile211Asn | 0.9683 (LP) | 3.59 | 3.59 | VUS / uncertain risk | **D** |
| VCV002684209 | p.Ile211Thr | 0.9474 (LP) | 3.59 | 3.59 | Pathogenic | **D** |
| VCV000016144 | p.Tyr214Cys | 0.2600 (LB) | 3.01 | 3.01 | Pathogenic | **A** |
| VCV004743109 | p.Cys220Ser | 0.9574 (LP) | 3.30 | 5.87 | VUS | I |
| VCV000036239 | p.Cys220Arg | 0.9953 (LP) | 3.30 | 5.87 | Likely pathogenic | I |
| VCV000036240 | p.Cys220Tyr | 0.
=== END RUN rd8pa4rgjcm ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

# Human rating sheet: run rxekfxt0p2o (7 of 30)

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

=== RUN rxekfxt0p2o ===
QUESTION:
For PTP1B in PDB entry 1T4J chain A, how many of the residues STINGAllo predicts are among the residues within 4 angstroms of the bound allosteric ligand? Report both lists and the overlap.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[K02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[K02_b] [critical] [scripted] ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"]
[K02_c] [critical] [scripted] 10

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Result

**10 of the 14 residues predicted by STINGAllo are within 4.0 Å of the bound allosteric ligand.**

### 1. STINGAllo predictions for 1T4J chain A

Residue numbers returned by the STINGAllo REST API:

**129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282**

With deposited chain-A residue names:

**GLU129, GLU130, SER187, PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, ILE281, MET282**

### 2. Chain-A residues within 4.0 Å of the allosteric ligand

PDB 1T4J contains the allosteric ligand **FRJ at A/299**. Using the minimum heavy-atom distance between each protein residue and the 41 FRJ atoms:

| Residue | Minimum distance (Å) |
|---|---:|
| GLU276 | 2.554 |
| PHE280 | 2.645 |
| ASN193 | 3.011 |
| LYS279 | 3.031 |
| GLU200 | 3.304 |
| GLY277 | 3.367 |
| ALA189 | 3.416 |
| PHE196 | 3.552 |
| MET282 | 3.593 |
| LEU192 | 3.803 |
| PRO188 | 3.918 |

Thus, the contact list is:

**PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, GLY277, LYS279, PHE280, MET282**

### 3. Overlap

**PRO188, ALA189, LEU192, ASN193, PHE196, GLU200, GLU276, LYS279, PHE280, MET282**

Residue numbers:

**188, 189, 192, 193, 196, 200, 276, 279, 280, 282**

**Overlap count: 10**

For completeness:

- **STINGAllo only:** GLU129, GLU130, SER187, ILE281
- **Ligand-contact only:** GLY277
- **Important cutoff detail:** SER187 is close but outside the cutoff: its minimum distance is **4.048 Å**. Thus it is not included under an exact inclusive 4.0 Å criterion.

### Method and sources

- STINGAllo API: `https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=1T4J&chain_id=A`
- API documentation: `https://www.stingallo.cbi.cnptia.embrapa.br/apis`
- Deposited structure: [RCSB PDB 1T4J](https://www.rcsb.org/structure/1T4J)
- Coordinates: `https://files.rcsb.org/download/1T4J.pdb`
- Primary structural citation: Wiesmann et al., *Nature Structural & Molecular Biology* (2004), DOI [10.1038/nsmb803](https://doi.org/10.1038/nsmb803), PMID 15258570.

The calculation used all heavy atoms, an inclusive **≤4.000 Å** cutoff, excluded waters and the ligand itself, and found no alternate-location ambiguity in the PDB file.

### Completed plan

1. [✗] Specialized literature search (failed: Claude-model restriction)
2. [✓] Locate and retrieve the authoritative STINGAllo output
3. [✓] Retrieve 1T4J and identify FRJ (A/299) as the bound allosteric ligand
4. [✓] Normalize residue identifiers and calculate the 4 Å contact list
5. [✓] Independently verify distances, overlap, and source metadata
6. [✓] Report both lists, the overlap, count, methods, and source identifiers
=== END RUN rxekfxt0p2o ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

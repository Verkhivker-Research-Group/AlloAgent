# Human rating sheet: run runua3bei46 (26 of 30)

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

=== RUN runua3bei46 ===
QUESTION:
In PDB entry 5EHR (human SHP2, UniProt Q06124, chain A), list the residues within 4 angstroms of the allosteric inhibitor SHP099 and say which domains (N-SH2, C-SH2, PTP) they belong to.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 11 (Q06124)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[S05_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"}
[S05_b] [critical] [scripted] [{"chain": "A", "pdb_number": 601}]
[S05_c] [critical] [scripted] {"uniprot_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "pdb_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "min_distances": {"108": 3.133, "110": 3.465, "111": 3.135, "113": 2.788, "114": 3.751, "218": 3.693, "219": 3.586, "249": 3.293, "250": 3.103, "253": 3.295, "254": 3.464, "257": 3.58, "491": 3.454, "492": 3.448, "495": 3.571}}
[S05_d] [critical] [judged] each contact residue is assigned to N-SH2, C-SH2 or PTP

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Final plan status

1. [✓] Identified SHP099 as RCSB chemical component **5OD** in 5EHR.
2. [✓] Calculated chain-A polymer contacts using an inclusive **≤4.0 Å** heavy-atom distance cutoff.
3. [✓] Verified chain A maps to **Q06124 (PTPN11/SHP2)** with 100% sequence identity.
4. [✗] The first UniProt lookup used uppercase `DOMAIN`; the JSON uses title-case `Domain` features, so it was corrected.
5. [✓] Retrieved UniProt’s core domain features: SH2 1, 6–102; SH2 2, 112–216; PTP, 247–517.
6. [✓] Confirmed the conventional structural partition used for the assignment: **N-SH2 1–115, C-SH2 116–252, PTP 253–525**.
7. [✗] An initial RCSB citation parser assumed a list rather than a dictionary; it was corrected.
8. [✓] Confirmed the RCSB entry title identifies 5OD as the allosteric inhibitor SHP099.
9. [✗] The primary Nature paper was not open-access in Europe PMC, so no unavailable full-text claims were used.
10. [✓] Confirmed in open full text that the SHP099 tunnel spans both SH2 domains and the PTP domain.
11. [✗] One Europe PMC boundary-search request returned HTTP 503 and was excluded.
12. [✓] Rechecked the final 15-residue contact calculation and three-domain assignment.
13. [✗] Two ancillary fixed-column `SITE` parsers misparsed residue fields.
14. [✗] The first token parser pooled `SITE` groups AC1–AC4, which represent several ligands.
15. [✓] Restricted the comparison to REMARK-mapped **AC1**, the 5OD chain-A binding site, and completed validation.

### Residues within 4 Å of SHP099 in 5EHR chain A

| Domain | Residue | Minimum heavy-atom distance |
|---|---|---:|
| **N-SH2** | Thr108 (T108) | 3.13 Å |
| | Glu110 (E110) | 3.47 Å |
| | Arg111 (R111) | 3.14 Å |
| | Phe113 (F113) | 2.79 Å |
| | His114 (H114) | 3.75 Å |
| **C-SH2** | Thr218 (T218) | 3.69 Å |
| | Thr219 (T219) | 3.59 Å |
| | Glu249 (E249) | 3.29 Å |
| | Glu250 (E250) | 3.10 Å |
| **PTP** | Thr253 (T253) | 3.30 Å |
| | Leu254 (L254) | 3.46 Å |
| | Gln257 (Q257) | 3.58 Å |
| | Pro491 (P491) | 3.45 Å |
| | Lys492 (K492) | 3.45 Å |
| | Gln495 (Q495) | 3.57 Å |

**Total: 15 residues** — **5 N-SH2, 4 C-SH2, and 6 PTP**. Thus, the SHP099 tunnel makes contacts with all three structural domains.

The deposited 5EHR `SITE` annotation lists 14 of these residues; the explicit ≤4.0 Å calculation adds **His114 at 3.75 Å**.

**Sources:** RCSB PDB **5EHR**; UniProt **Q06124**; validated geometric ligand-contact calculation for component **5OD**; deposited `SITE` group **AC1**.
=== END RUN runua3bei46 ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

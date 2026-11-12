# Human rating sheet: run rgfe41pq8xs (23 of 30)

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

=== RUN rgfe41pq8xs ===
QUESTION:
Use PocketMiner on the TEM-1 beta-lactamase structure 1BTL (UniProt P62593). Report the ten highest-scoring residues and the scores of the residues that contact the allosteric inhibitors in PDB entry 1PZO, after mapping between the two entries.

INTENDED PROTEIN: Beta-lactamase TEM (P62593)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[P04_a] [critical] [scripted] {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"}
[P04_b] [critical] [scripted] [{"chain": "A", "pdb_number": 234, "residue_name": "LYS", "score": 0.9514}, {"chain": "A", "pdb_number": 246, "residue_name": "ILE", "score": 0.9425}, {"chain": "A", "pdb_number": 172, "residue_name": "ALA", "score": 0.9411}, {"chain": "A", "pdb_number": 244, "residue_name": "ARG", "score": 0.929}, {"chain": "A", "pdb_number": 264, "residue_name": "TYR", "score": 0.9265}, {"chain": "A", "pdb_number": 217, "residue_name": "ALA", "score": 0.9208}, {"chain": "A", "pdb_number": 235, "residue_name": "SER", "score": 0.9179}, {"chain": "A", "pdb_number": 220, "residue_name": "LEU", "score": 0.9168}, {"chain": "A", "pdb_number": 266, "residue_name": "THR", "score": 0.9058}, {"chain": "A", "pdb_number": 66, "residue_name": "PHE", "score": 0.9051}]
[P04_c] [critical] [scripted] {"214": 0.8751, "215": 0.9208, "218": 0.9168, "219": 0.7866, "222": 0.2461, "233": 0.9179, "234": 0.8263, "235": 0.8921, "241": 0.929, "242": 0.8435, "243": 0.9425, "257": 0.3872, "259": 0.7797, "272": 0.8693, "275": 0.774, "276": 0.4914, "279": 0.2419, "282": 0.3811}
[P04_d] [critical] [judged] the mapping between the two entries is stated (both are TEM-1, P62593; the 1PZO CBT contacts are given in UniProt numbering)

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Results

I ran the **original PocketMiner** model (attention disabled) on the inhibitor-free **TEM-1 structure 1BTL**, chain A. The model produced one pocket-probability score for each of the 263 resolved residues.

### Ten highest-scoring 1BTL residues

| Rank | 1BTL residue | PocketMiner score |
|---:|:---|---:|
| 1 | Lys234 | **0.951411** |
| 2 | Ile246 | **0.942519** |
| 3 | Ala172 | **0.941106** |
| 4 | Arg244 | **0.928997** |
| 5 | Tyr264 | **0.926471** |
| 6 | Ala217 | **0.920834** |
| 7 | Ser235 | **0.917947** |
| 8 | Leu220 | **0.916830** |
| 9 | Thr266 | **0.905837** |
| 10 | Phe66 | **0.905050** |

Scores are PocketMiner’s per-residue pocket probabilities.

### 1PZO allosteric-inhibitor contacts mapped to 1BTL

The allosteric inhibitor in 1PZO is **CBT**, present as two molecules, residue IDs **300** and **301**. Contacts were defined as any protein heavy atom within **4.5 Å** of either CBT molecule.

| 1PZO residue | Mapped 1BTL residue | PocketMiner score | 1BTL rank | Minimum heavy-atom distance (Å) | CBT molecule(s) |
|:---|:---|---:|---:|---:|:---|
| Val216 | Val216 | **0.875088** | 17 | 3.755 | 300 |
| Ala217 | Ala217 | **0.920834** | 6 | 3.908 | 300 |
| Leu220 | Leu220 | **0.916830** | 8 | 3.353 | 300, 301 |
| Leu221 | Leu221 | **0.786650** | 46 | 3.350 | 301 |
| Ala224 | Ala224 | **0.246091** | 209 | 3.411 | 301 |
| Leu225 | Leu225 | **0.456167** | 133 | 4.430 | 301 |
| Ser235 | Ser235 | **0.917947** | 7 | 2.598 | 300 |
| Gly236 | Gly236 | **0.826309** | 31 | 3.685 | 300 |
| Ala237 | Ala237 | **0.892082** | 14 | 3.556 | 300 |
| Arg244 | Arg244 | **0.928997** | 4 | 3.358 | 300, 301 |
| Gly245 | Gly245 | **0.843503** | 27 | 3.185 | 300 |
| Ile246 | Ile246 | **0.942519** | 2 | 3.386 | 300 |
| Val261 | Val261 | **0.387245** | 168 | 3.998 | 301 |
| Ile263 | Ile263 | **0.779656** | 51 | 3.791 | 300, 301 |
| Asn276 | Asn276 | **0.869319** | 18 | 3.068 | 300, 301 |
| Ile279 | Ile279 | **0.773985** | 52 | 3.561 | 300, 301 |
| Ala280 | Ala280 | **0.491368** | 126 | 3.420 | 301 |
| Gly283 | Gly283 | **0.241886** | 210 | 3.667 | 301 |
| Leu286 | Leu286 | **0.381120** | 171 | 3.942 | 301 |

**Contact-cutoff sensitivity:** with a stricter 4.0 Å cutoff, the only 4.5 Å contact omitted is Leu225, leaving 18 residues. At ≤3.5 Å, nine residues remain: Leu220, Leu221, Ala224, Ser235, Arg244, Gly245, Ile246, Asn276, and Ala280.

## Mapping and validation

- 1BTL and 1PZO each contain **263 resolved TEM-1 residues**, spanning residues 26–290, with residues 239 and 253 unresolved.
- Global sequence alignment mapped all 263 positions one-to-one:
  - **260/263 identities (98.86%)**
  - substitutions at Ile84/Val84, Met182/Thr182, and Val184/Ala184
  - none of these substitutions occurs at an inhibitor-contact site.
- Cα superposition using the sequence-derived mapping gave an **RMSD of 0.988 Å**.
- The mature 1BTL and 1PZO sequences align to UniProt **P62593** at 261/263 and 262/263 identities, respectively.
- PocketMiner’s residue order was independently checked against the PDB and `mdtraj`; all 263 predictions map to the expected 1BTL residues.
- Two inference runs were bit-identical.

These scores describe predicted pocket propensity in **1BTL**; they are not bound-state binding energies or a direct measure of allosteric coupling.

## Deliverables

The prediction array and final tables are available under `pocketminer_tem1_results/`:

- `1btl-preds.npy`
- `top10_1btl.tsv`
- `mapped_1pzo_CBT_contacts_4p5A.tsv`
- `pocketminer_tem1_summary.json`
- `1pzo_CBT_contacts_residue_aware.tsv`

## Sources

- RCSB PDB **1BTL**: Jelsch et al., *Proteins* 16, 364–383 (1993), DOI [10.1002/prot.340160406](https://doi.org/10.1002/prot.340160406), PMID 8356032.
- RCSB PDB **1PZO**: Horn and Shoichet, *J. Mol. Biol.* 336, 1283–1291 (2004), DOI [10.1016/j.jmb.2003.12.068](https://doi.org/10.1016/j.jmb.2003.12.068), PMID 15037085.
- UniProt **P62593**, TEM-1 β-lactamase.
- Meller et al., “Predicting locations of cryptic pockets from single protein structures using the PocketMiner graph neural network,” *Nature Communications* 14, 1177 (2023), DOI [10.1038/s41467-023-36699-3](https://doi.org/10.1038/s41467-023-36699-3).

### Completed plan
1. [✓] Locate the available PocketMiner implementation, documentation, and execution dependencies.
2. [✓] Retrieve 1BTL/1PZO metadata and identify the CBT allosteric inhibitors.
3. [✓] Run PocketMiner on 1BTL and extract per-residue scores.
4. [✓] Map inhibitor-contacting residues between entries and validate structurally.
5. [✓] Audit and report the ten highest scores and all mapped inhibitor-contact scores.
=== END RUN rgfe41pq8xs ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

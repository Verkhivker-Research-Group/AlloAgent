# Human rating sheet: run rnux5boya8e (1 of 30)

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

=== RUN rnux5boya8e ===
QUESTION:
Build a residue contact network for PTP1B (UniProt P18031, PDB 1T4J chain A). Find the shortest path between the residue closest to the allosteric ligand and the catalytic Cys215. Report the path, its length and the cutoff used.

INTENDED PROTEIN: Tyrosine-protein phosphatase non-receptor type 1 (P18031)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[C02_a] [critical] [scripted] {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"}
[C02_b] [critical] [judged] the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PTP1B (P18031) residue contact network — 1T4J chain A

### Structure / ligand identification
| Item | Value |
|---|---|
| PDB | **1T4J**, chain A (X-ray, **2.7 Å**), residues modeled 1–282 of a 1–298 construct (283–298 disordered/unmodeled) |
| Title | *Allosteric Inhibition of Protein Tyrosine Phosphatase 1B* — Wiesmann C. *et al.*, **Nat Struct Mol Biol 2004**, DOI 10.1038/nsmb803 |
| Allosteric ligand | **FRJ** (1 copy, 41 heavy atoms) = 3-(3,5-dibromo-4-hydroxybenzoyl)-2-ethyl-benzofuran-6-sulfonic acid [4-(thiazol-2-ylsulfamoyl)-phenyl]-amide; BindingDB IC₅₀ 2–8 µM |
| Catalytic residue | **Cys215** (C–N distances to His214/Arg221 as expected for the P-loop; UniProt P18031 numbering = PDB numbering here) |

### Method
Nodes = 282 chain-A residues; edge = two residues in contact if their **minimum heavy-atom distance ≤ cutoff**; one HETATM excluded (FRJ kept only as the ligand probe). Ligand proximity = min heavy-atom distance from each residue to FRJ. Shortest path = minimum number of edges (hops), found by BFS and independently cross-checked with `scipy.sparse.csgraph.shortest_path` on an unweighted graph.

### Result
**Closest residue to the allosteric ligand: Glu276** — OE1···N16(FRJ) = **2.55 Å** (next: Phe280 backbone O 2.65 Å, Asn193 3.01 Å, Lys279 3.03 Å).

**Shortest path (cutoff 4.5 Å):**
**Cys215 → Leu110 → Phe191 → Pro188 → Glu276**

**Path length = 4 edges (5 residues)**; summed inter-residue contact distances = 15.23 Å

| Edge | min heavy-atom distance |
|---|---|
| Cys215 – Leu110 | 4.41 Å (CB–CB) |
| Leu110 – Phe191 | 3.84 Å (CD2–CE1) |
| Phe191 – Pro188 | 3.16 Å (O–N) |
| Pro188 – Glu276 | 3.82 Å (CG–CG) |

### Cutoff used
**4.5 Å** (minimum heavy-atom distance between residues) — the standard residue-contact-network threshold. The 4.5 Å network is a **single connected component containing all 282 residues** (no isolated residues).

### Robustness / degeneracy
* **Cutoff sensitivity:** 4.0 Å → 5 edges (e.g. Cys215–Asn111–Leu110–Phe191–Pro188–Glu276); **4.5 Å and 5.0 Å → 4 edges (same answer)**; 5.5–6.0 Å → still 4 edges but rerouted (Cys215–Val108–Phe194–Leu192–Glu276).
* **Covalent-neighbor convention:** identical result whether peptide-bonded sequential neighbors are included or excluded (the reported path contains no covalent pair).
* **Degeneracy:** 5 distinct 4-edge minimal paths exist at 4.5 Å: (A) Cys215–Leu110–Phe191–Pro188–Glu276; (B) …Phe191–Leu192–Glu276; (C) Cys215–Leu110–Phe194–**Leu192**–Glu276; (D/E) via the catalytic **Arg221**. Path A is reported because it is entirely non-covalent; paths B/C/E pass through **Leu192**, the literature-established α3-helix allosteric residue shown to lock the WPD loop in the open conformation.
* **Alternative endpoint:** if "closest residue" is defined by CA/CB-to-ligand-centroid instead of minimum any-atom distance, the target becomes **Phe280** and the path is 5 edges: Cys215–Leu110–Phe191–Pro188–Glu276–Phe280 (Glu276 is still on it).
* **Distance context:** FRJ lies **20.3 Å** from Cys215 (closest atom pair O12/CB; centroid–centroid 24.6 Å), consistent with the allosteric site being remote from the active site — hence a multi-residue coupling path is required.

### Artifacts saved (working dir `/tmp/agent_cwd/C02_r1_1`)
`PTP1B_1T4J_contact_network_path.png` (3D path + FRJ contact shell + edge-distance plot), `network_int.pkl` (residue-pair distance matrix), `1T4J_entry_metadata.json`, `chemcomp_FRJ.json`, `primary_citation.json`, `closest_defs.pkl`, `uniprot_P18031.json`.
=== END RUN rnux5boya8e ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

# Human rating sheet: run rcg6gv1i8aq (6 of 30)

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

=== RUN rcg6gv1i8aq ===
QUESTION:
For glucokinase (UniProt P35557), retrieve ClinVar variants, map their positions onto PDB entry 1V4S, and list those within 6 angstroms of the allosteric activator. Give the AlphaMissense score for each and say which are likely to alter activator binding.

INTENDED PROTEIN: Hexokinase-4 (P35557)
PROMPT TYPE: normal

CHECKLIST (ground truth):
[V05_a] [critical] [scripted] {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"}
[V05_b] [critical] [scripted] 2845
[V05_c] [critical] [judged] the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Completed plan

1. [✓] Retrieved PDB 1V4S and identified **MRK** as the bound allosteric activator.
2. [✓] Retrieved all human GCK ClinVar records and normalized protein changes and classifications.
3. [✓] Mapped UniProt P35557 residues to PDB 1V4S chain A using the RCSB/SIFTS alignment.
4. [✓] Calculated minimum heavy-atom distances from each residue to MRK and retained residues within 6 Å.
5. [✓] Retrieved official AlphaMissense scores for every relevant substitution.
6. [✓] Cross-checked all distances, identifiers, classifications, and score coverage.

## Main result

- The ClinVar search `GCK[gene] AND "Homo sapiens"[organism]` returned **1,454 records**.
- **24 resolved residues** in 1V4S are within 6 Å of MRK:  
  **Y61, V62, R63, S64, T65, P66, Q98, I159, M210, I211, Y214, Y215, H218, C220, E221, V222, M235, R250, C252, L451, V452, S453, V455, A456**.
- Sixteen of these positions have ClinVar single-substitution records, giving **40 ClinVar records representing 38 distinct amino-acid substitutions**.
- All 38 substitutions have official AlphaMissense scores.
- ClinVar classifications among the 40 records: 15 pathogenic, 7 likely pathogenic, 3 pathogenic/likely pathogenic, 3 conflicting, 10 VUS, and 2 VUS/uncertain-risk-allele.

### Distance and mapping conventions

- `d_res`: minimum distance from any heavy atom of the residue to any MRK heavy atom.
- `d_sc`: minimum distance from the residue’s side-chain heavy atoms to MRK.
- MRK is author residue **501 of chain A** and contains 23 heavy atoms.
- RCSB/SIFTS maps UniProt P35557 positions 16–465 to the PDB entity; resolved residues 16–461 correspond directly to UniProt numbering. PDB residues 14–15 are cloning-modified and were excluded from the correspondence. All variants below are at positions 61–456 and are unaffected by that caveat.
- Only point missense substitutions are scored: frameshifts, indels, and other non-missense records cannot be represented by a single AlphaMissense amino-acid substitution.

## Variants within 6 Å of MRK

AlphaMissense bands use the official thresholds: **LP** = likely pathogenic, score >0.564; **Amb** = ambiguous, 0.34–0.564; **LB** = likely benign, <0.34.

Binding calls are structural assessments, not experimentally measured binding constants:

- **Direct** — likely to alter MRK binding; direct side-chain pocket interaction plus supporting AlphaMissense/chemical evidence.
- **Moderate** — credible but less certain binding effect.
- **Possible/indirect** — within the 6 Å shell, but no strong direct side-chain evidence; an effect may instead arise through folding, stability, or dynamics.

| Variant | PDB residue | d_res Å | d_sc Å | AlphaMissense | AM band | ClinVar classification | ClinVar VCV | Binding call |
|---|---:|---:|---:|---:|---|---|---|---|
| Y61N | TYR61 | 3.25 | 5.85 | 0.8868 | LP | VUS | VCV001444770.6 | Possible/indirect |
| V62A | VAL62 | 3.62 | 3.64 | 0.9731 | LP | Pathogenic | VCV000585917.8 | **Direct** |
| V62M | VAL62 | 3.62 | 3.64 | 0.9462 | LP | Pathogenic | VCV000419624.13 | **Direct** |
| R63C | ARG63 | 2.73 | 3.75 | 0.1234 | LB | VUS/uncertain risk allele | VCV000447391.3 | Possible/indirect |
| R63H | ARG63 | 2.73 | 3.75 | 0.1886 | LB | VUS | VCV002779779.3 | Possible/indirect |
| R63L | ARG63 | 2.73 | 3.75 | 0.3254 | LB | VUS | VCV001502971.6 | Possible/indirect |
| I159M | ILE159 | 4.33 | 4.33 | 0.2207 | LB | Conflicting | VCV000447403.7 | Possible/indirect |
| I159N | ILE159 | 4.33 | 4.33 | 0.9313 | LP | Conflicting | VCV002735015.5 | **Direct** |
| I159T | ILE159 | 4.33 | 4.33 | 0.5886 | LP | VUS | VCV002700200.3 | **Direct** |
| I159V | ILE159 | 4.33 | 4.33 | 0.1611 | LB | Pathogenic/LP | VCV001679549.10 | Possible/indirect |
| M210I | MET210 | 3.66 | 3.66 | 0.9915 | LP | Pathogenic | VCV000036236.10; VCV002691826.1 | **Direct** |
| M210K | MET210 | 3.66 | 3.66 | 0.9915 | LP | Pathogenic | VCV000016141.9 | **Direct** |
| M210T | MET210 | 3.66 | 3.66 | 0.9821 | LP | Pathogenic | VCV000804852.15 | **Direct** |
| M210V | MET210 | 3.66 | 3.66 | 0.8229 | LP | Likely pathogenic | VCV002505485.1; VCV002505486.1 | **Direct** |
| I211N | ILE211 | 3.59 | 3.59 | 0.9683 | LP | VUS/uncertain risk allele | VCV000435303.10 | **Direct** |
| I211T | ILE211 | 3.59 | 3.59 | 0.9474 | LP | Pathogenic | VCV002684209.1 | **Direct** |
| Y214C | TYR214 | 3.01 | 3.01 | 0.2600 | LB | Pathogenic | VCV000016144.3 | **Direct** |
| C220F | CYS220 | 3.30 | 5.87 | 0.9899 | LP | VUS | VCV002691835.3 | Possible/indirect |
| C220R | CYS220 | 3.30 | 5.87 | 0.9953 | LP | Likely pathogenic | VCV000036239.6 | Possible/indirect |
| C220S | CYS220 | 3.30 | 5.87 | 0.9574 | LP | VUS | VCV004743109.1 | Possible/indirect |
| C220W | CYS220 | 3.30 | 5.87 | 0.9982 | LP | VUS | VCV003658742.4 | Possible/indirect |
| C220Y | CYS220 | 3.30 | 5.87 | 0.9972 | LP | Pathogenic | VCV000036240.9 | Possible/indirect |
| E221K | GLU221 | 4.24 | 4.24 | 0.7102 | LP | Pathogenic | VCV000036241.20 | **Direct** |
| M235R | MET235 | 3.51 | 3.51 | 0.9183 | LP | Likely pathogenic | VCV004687879.1 | **Direct** |
| M235T | MET235 | 3.51 | 3.51 | 0.9520 | LP | Pathogenic | VCV000036248.8 | **Direct** |
| M235V | MET235 | 3.51 | 3.51 | 0.5248 | Amb | Pathogenic | VCV000381599.7 | Possible/indirect |
| R250C | ARG250 | 4.59 | 4.59 | 0.3665 | Amb | Pathogenic | VCV000393451.29 | Possible/indirect |
| R250H | ARG250 | 4.59 | 4.59 | 0.2145 | LB | Likely pathogenic | VCV000435311.9 | Possible/indirect |
| R250P | ARG250 | 4.59 | 4.59 | 0.9134 | LP | VUS | VCV002691830.1 | **Moderate** |
| C252F | CYS252 | 5.72 | 5.72 | 0.9600 | LP | Conflicting | VCV000810090.46 | Possible/indirect |
| C252W | CYS252 | 5.72 | 5.72 | 0.9967 | LP | VUS | VCV002169519.4 | Possible/indirect |
| V452L | VAL452 | 3.62 | 3.87 | 0.6364 | LP | Likely pathogenic | VCV002506148.1 | **Moderate** |
| S453L | SER453 | 5.64 | 7.92 | 0.7575 | LP | Pathogenic/LP | VCV000036200.20 | Possible/indirect |
| S453W | SER453 | 5.64 | 7.92 | 0.9903 | LP | Pathogenic/LP | VCV002734985.5 | Possible/indirect |
| V455E | VAL455 | 3.46 | 3.46 | 0.8513 | LP | Likely pathogenic | VCV000585916.60 | **Direct** |
| V455M | VAL455 | 3.46 | 3.46 | 0.5295 | Amb | Pathogenic | VCV000016140.5 | Possible/indirect |
| A456P | ALA456 | 4.04 | 4.04 | 0.9733 | LP | VUS | VCV003650955.2 | **Direct** |
| A456V | ALA456 | 4.04 | 4.04 | 0.3825 | Amb | Pathogenic | VCV000016143.9 | Possible/indirect |

## Which are most likely to alter activator binding?

### Likely direct, high-confidence effects

**V62A, V62M, I159N, I159T, M210I, M210K, M210T, M210V, I211N, I211T, Y214C, E221K, M235R, M235T, V455E, and A456P.**

Important supporting observations:

- **Y214C:** the Tyr214 aromatic ring directly contacts MRK fluorine F14 at 3.01 Å. Replacing it with cysteine removes a major hydrophobic contact, so the structural evidence is strong even though AlphaMissense is low (0.2600).
- **V455E:** the Val455 side chain is 3.46 Å from the MRK carbonyl oxygen O8; replacing Val with glutamate reverses charge and is likely disruptive.
- **M210 and M235:** their side-chain sulfur-containing groups occupy the hydrophobic pocket and directly contact MRK.
- **V62M:** V62 directly contacts the activator pocket, and a separate experimental study found that GCK-V62M **does not respond to the pharmacologic activator RO0281675**. RO0281675 is not established here to be chemically identical to MRK, so this is functional corroboration of the shared allosteric pocket rather than an MRK-specific assay.

### Likely, but more moderate-confidence effects

- **R250P:** the Arg250 side chain is 4.59 Å from MRK and proline can disrupt the local backbone.
- **V452L:** there is a direct 3.87 Å side-chain contact and an LP AlphaMissense score, but Val→Leu is relatively conservative, so a modest effect is more plausible.

The remaining substitutions are **possible or indirect effects**. Their high AlphaMissense scores may reflect loss of GCK folding, stability, kinetics, or allosteric equilibrium rather than disruption of the MRK contact itself.

## Interpretation limitations

- AlphaMissense predicts **general clinical pathogenicity**, not ligand-binding affinity; it should not be interpreted as a binding-affinity score.
- A 6 Å shell includes direct contacts, backbone contacts, and nearby second-shell residues.
- 1V4S represents one bound conformation of GCK; a static distance cannot capture mutation-induced conformational changes.
- ClinVar and AlphaMissense classifications do not establish that a variant specifically impairs GCK activators.
- These results are appropriate for structural prioritization and hypothesis generation, not clinical interpretation.

## Sources

- [ClinVar GCK search](https://www.ncbi.nlm.nih.gov/clinvar/?term=GCK%5Bgene%5D%20AND%20%22Homo%20sapiens%22%5Borganism%5D)
- [UniProt P35557](https://www.uniprot.org/uniprotkb/P35557/entry)
- [RCSB PDB 1V4S](https://www.rcsb.org/structure/1V4S); Kamata et al., *Structure* 2004, [PMID 15016359](https://pubmed.ncbi.nlm.nih.gov/15016359/), DOI [10
=== END RUN rcg6gv1i8aq ===

## Your scores

Write them in the CSV (`human_subset_scores.csv`), one row for this run id, in this order:

```
run_id,goal_completion,data_grounding,final_answer_complete,item_verdicts,notes
```

Skip the items marked `scripted`; the `item_verdicts` field holds `item_id:verdict` pairs separated by semicolons.

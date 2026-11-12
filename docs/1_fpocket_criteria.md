# Part 1 - fpocket wrapper: pass criteria (written BEFORE the fix)

Committed before the fix. The numbers below come from an **independent
calculation** that parses fpocket's own output files directly
(`pockets/pocketN_atm.pdb`) without the wrapper - so the wrapper has
to agree with it, and the wrapper's own behaviour is not what defines
the target.

The independent calculation was run on **1T4J, ligand-stripped** (the
HETATM records removed, as the wrapper does by default), fpocket
4.2.3, in `alloagent-eval:v4`. The FRJ contact set is the 11 residues
that `get_ligand_contacts` reports for 1T4J / FRJ / chain A:
**188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282**.

## Criterion 1 - every pocket has a non-empty residue list

fpocket reports **18 pockets** for 1T4J and every one of them has
atoms in `pockets/pocketN_atm.pdb`. The independent residue counts are:

| pocket | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| residues | 9 | 12 | 15 | 10 | 12 | 8 | 10 | 15 | 6 |

| pocket | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|
| residues | 9 | 12 | 11 | 11 | 10 | 7 | 11 | 8 | 7 |

**Criterion: the wrapper returns 18 pockets for 1T4J and every pocket
carries a residue list whose length is exactly the number above.** A
pocket with an empty residue list is a failure, and so is a residue
count that differs from the independent parse.

## Criterion 2 - the residues themselves agree with the independent parse

Each residue must carry the **chain**, the **PDB (author) residue
number** and the **residue name**, exactly as they appear in
`pockets/pocketN_atm.pdb`.

**Criterion: for every pocket, the set of (chain, residue number,
residue name) triples returned by the wrapper equals the set parsed
from `pockets/pocketN_atm.pdb`.**

## Criterion 3 - the FRJ overlap

The independent calculation of the overlap between each pocket's
residues and the 11 FRJ contact residues:

| pocket | FRJ-contact residues in the pocket | overlap |
|---|---|---|
| 1, 2, 3, 4, 5, 6 | none | 0 |
| 7 | 189, 193 | 2 |
| 8 | 279, 282 | 2 |
| 9, 10 | none | 0 |
| **11** | **188, 189, 192, 193, 196, 276, 277, 280** | **8** |
| 12, 13, 14, 15 | none | 0 |
| 16 | 200 | 1 |
| 17, 18 | none | 0 |

**Criterion: the maximum FRJ overlap over the 18 pockets is 8, and it
is reached by pocket 11**, whose residue list contains 8 of the 11 FRJ
contact residues. The wrapper's overlap arithmetic must reproduce
this number.

## Criterion 4 - the "top-3 pockets" expectation is NOT met by fpocket, and that is a fact about the model

The expectation that a top-ranked fpocket pocket would cover the FRJ
site **does not hold for 1T4J**, and the independent calculation says
so before any wrapper change:

* ranked by fpocket's own `Score`, the top three pockets are
  **1 (0.235), 2 (0.167), 3 (0.142)** and their FRJ overlap is
  **0, 0 and 0**;
* the FRJ-covering pocket 11 has score **0.069** and ranks **11th of
  18**.

So "the top-3 pockets include one whose residues overlap the FRJ
contacts" is **not satisfiable by fpocket on 1T4J**. This is recorded
as a fact about the model, not as a pass/fail of the wrapper: the
wrapper's job is to report the pockets and their residues correctly
(Criteria 1-3), and it must not be judged on fpocket's ranking. The
criterion that stands is Criterion 3 (the maximum overlap is 8, at
pocket 11), and the report must state the ranking fact next to it.

## Criterion 5 - the UniProt numbers

The pocket residues must carry the UniProt number where the mapping is
available, and `null` where it is not. The mapping is the PDBe
mappings API (the same source `map_residues_uniprot_pdb` uses):
`https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<PDB>`. For 1T4J,
chain A maps to **P09467** and the author numbering equals the
UniProt numbering, so the FRJ contact residues are the same integers
in both.

**Criterion: for 1T4J chain A, every pocket residue has
`uniprot_number` equal to its PDB residue number, and
`uniprot_accession` equal to `P09467`.** A residue whose mapping is
not available must have `uniprot_number: null` - it must never be
guessed.

> **Dated correction 2026-10-26 (the text above is left as it was
> committed).** The accession in Criterion 5 is **P18031, not
> P09467**. 1T4J is *not* FBP1: the RCSB entry title is "Allosteric
> Inhibition of Protein Tyrosine Phosphatase 1B", the gene is
> **PTPN1 / PTP1B**, and the PDBe mappings API returns
> `{"1t4j": {"UniProt": {"P18031": {"mappings": [{"chain_id": "A",
> "unp_start": 1, "unp_end": 298, "start": {"author_residue_number":
> 1}}]}}}}` - one chain, the author numbering equal to the UniProt
> numbering. P09467 (FBP1) belongs to the gate-2 D1/D6 proteins
> (1FTA, 7WVB) and was carried over into this criterion by mistake.
> Everything else in Criterion 5 stands: the mapping comes from the
> PDBe mappings API, the UniProt number is the author number plus the
> per-chain offset, and it is `null` when the mapping is not
> available.

## Criterion 6 - the P2Rank wrapper is checked the same way

The P2Rank wrapper already returns a residue list per pocket, from
`<input>_residues.csv`. It is checked the same way:

**Criterion: for 1T4J, every P2Rank pocket has a non-empty residue
list, and the residue lists agree with an independent parse of
`<input>_residues.csv`** (the chain, the residue number and the
residue name per residue, in the same order).

## What is recorded

The pocket count, the per-pocket residue counts, the maximum FRJ
overlap and the pocket that reaches it, and the ranking fact from
Criterion 4. If a criterion is not met, it is a FAIL with the
numbers; the criteria are not changed afterwards.

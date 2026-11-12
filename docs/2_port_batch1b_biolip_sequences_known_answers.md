# Port batch 1b — BioLiP sequence lookups: known-answer expectations

**Committed BEFORE the batch was implemented or run, and never edited
afterwards.** Companion to `docs/2_port_batch1_allosteric_known_answers.md`,
which covers the interaction-table functions. The four functions here
need their own file because their expected values come from a different
artefact (the BioLiP FASTA pickles, not the interaction table).

Scope: `biolip_protein`, `biolip_dna`, `biolip_rna`, `biolip_peptide`
(ours-only, old repo `Biolab/alloagent/tool/biolip.py`).

## The artefact

The BioLiP FASTA snapshots are pandas pickles in the Biolab data lake
(`biolip/*.pkl`), mounted read-only at `/biolab_data`. Each has the
columns `identifier`, `chain`, `type`, `uniprot_id` (protein only),
`pdb_id` (nucleic acids only), `length`, `sequence`.

| file | rows | identifier format | example |
|---|---|---|---|
| `protein.pkl` | 512,101 | `<pdb><chain>` | `1a1kA` |
| `dna.pkl` | 23,734 | `<pdb>_dna_<chain>` | `1a1k_dna_B` |
| `rna.pkl` | 18,920 | `<pdb>_rna_<chain>` | `8a3w_rna_S1` |
| `peptide.pkl` | 30,668 | `<pdb>_peptide_<chain>` | `4a1g_peptide_E` |

## The expectations

| # | input | expectation | source |
|---|---|---|---|
| B-1 | `biolip_protein("1A1K")` | `success=True`; `data.total == 1`; the single record has `identifier == "1a1kA"`, `chain == "A"`, `sequence` of length **85** beginning `RPYACPVESCDRRFSRSADLTRHIRIHTGQKPFQCRICMRNFSRSDHLTTHIRTHTGEKP` | `protein.pkl` |
| B-2 | `biolip_protein("1a1k", chain="A")` | identical to B-1 (the accessor lower-cases the PDB id and upper-cases the chain) | same |
| B-3 | `biolip_protein("1A1K", chain="B")` | `success=True` with `data.total == 0` — chain B is not in the protein snapshot | same |
| B-4 | `biolip_dna("1A1K")` | `success=True`; `data.total == 2`; identifiers `1a1k_dna_B` and `1a1k_dna_C`; the first record's `sequence` is `agcgtgggacc` (11 bases) | `dna.pkl` |
| B-5 | `biolip_dna("1A1K", chain="B")` | `data.total == 1`; identifier `1a1k_dna_B` | same |
| B-6 | `biolip_dna("1A1K", chain="BC")` | `success=False`; `error` mentions that the DNA chain must be a single letter | input validation |
| B-7 | `biolip_rna("8A3W")` | `success=True`; `data.total == 10`; the first identifier is `8a3w_rna_S1`; that record's `sequence` has length **1663** | `rna.pkl` |
| B-8 | `biolip_rna("8A3W", chain="S1")` | `data.total == 1`; identifier `8a3w_rna_S1` | same |
| B-9 | `biolip_peptide("4A1G")` | `success=True`; `data.total == 4`; identifiers `4a1g_peptide_E`, `4a1g_peptide_F`, `4a1g_peptide_G`, `4a1g_peptide_H`; the first record's `sequence` is `KIDTTSFLANLK` (12 residues) | `peptide.pkl` |
| B-10 | `biolip_peptide("4A1G", chain="E")` | `data.total == 1`; identifier `4a1g_peptide_E` | same |
| B-11 | a PDB id that is neither 4 nor 12 characters (e.g. `"ABC"`) | `success=False`; `error` mentions the 4-or-12-character requirement | input validation |
| B-12 | a chain longer than the allowed length for the polymer type | `success=False`; `error` names the allowed length (1 for DNA/peptide, 1-2 for RNA) | input validation |

## Non-goals

- These functions return sequences **as stored in the snapshot**; they
  do not reconstruct a biological assembly, do not align, and do not
  check that the sequence matches the PDB entry's current content.
- The row counts above pin the snapshot; a newer BioLiP release would
  change them.

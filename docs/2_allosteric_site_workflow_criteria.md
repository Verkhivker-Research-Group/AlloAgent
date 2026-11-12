# Part 3 - allosteric_site_workflow: pass criteria (written BEFORE running)

Committed before the tool is written.

## What the tool is

`allosteric_site_workflow(pdb_id, chain, ligand_id=None, run_stingallo=False)`
runs, in one call and returns **one structured report** with a
per-component result:

| component | what it runs |
|---|---|
| `ligand_contacts` | the residues within 4 A of `ligand_id` (only when a ligand is given), in the entry's numbering and in UniProt numbering |
| `fpocket` | fpocket on a **ligand-stripped** copy of the structure |
| `p2rank` | P2Rank on the same ligand-stripped copy |
| `pocketminer` | PocketMiner on the full structure |
| `normal_modes` | the normal mode analysis of the structure |
| `contact_network` | the residue contact network of the structure |
| `overlap` | the overlap of the pocket components with the known-site contacts (only when a ligand is given) |
| `stingallo` | the STINGAllo prediction (only when `run_stingallo=True`) |

Each component in the report must equal **the direct call of the
underlying tool** on the same input: the same tool, the same arguments,
the same returned values.

## Criteria

* **W1 (1T4J / FRJ)**: the report has a component `fpocket` whose
  pockets include the pocket that contains the FRJ contact residues -
  i.e. the overlap between the FRJ 4 A contact set and at least one
  fpocket pocket is not empty - and the `ligand_contacts` component
  equals the direct call of `get_ligand_contacts("1T4J", ligand_id="FRJ")`
  (the same 11 UniProt residues: 188, 189, 192, 193, 196, 200, 276,
  277, 279, 280, 282).
* **W2 (1OPK / MYR)**: the report's `ligand_contacts` equals the direct
  call of `get_ligand_contacts("1OPK", ligand_id="MYR")` (the same 8
  UniProt residues: 359, 360, 363, 448, 452, 481, 521, 529), and every
  component that is present in the report has `success=True` **or** a
  clear per-component error string (a component that failed must not
  silently disappear from the report).
* **W3 (component equality)**: for the components that run, the report
  value equals the value of the direct call of the same tool, field by
  field, for `fpocket`, `p2rank`, `pocketminer`, `normal_modes` and
  `contact_network`.
* **W4 (the exposed list)**: the tool is added to
  `alloagent/exposed_tools.txt` **only if** W1-W3 pass.  If they do
  not, the tool stays registered but out of the exposed list, and the
  failure is recorded with the numbers.

## Notes

* The tool must not change the behaviour of the tools it calls: it
  calls them, it does not re-implement them.
* A ligand-stripped copy is written to a temporary directory, never
  into the repository.
* If a component's dependency is missing (no PocketMiner env, no GPU
  for the model), the component reports its own error and the rest of
  the report is still produced.

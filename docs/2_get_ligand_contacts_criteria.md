# P32 — get_ligand_contacts: pass criteria (written BEFORE running)

Per the standing rule, the criteria below are committed before the
implementation and the known-answer tests are written. Every expected
value was computed from the **real RCSB files** by an independent
reference calculation (see "How the expected values were fixed"), not
by the tool.

## Tool summary

- Engine: the RCSB PDB coordinate file for the entry
  (`https://files.rcsb.org/download/<pdb_id>.cif`, mmCIF) plus the RCSB
  Data API for the SIFTS alignment
  (`https://data.rcsb.org/rest/v1/core/polymer_entity/<pdb_id>/<entity_id>`).
- Input: a PDB entry id **or** a local mmCIF file, the RCSB chemical
  component id of the ligand, an optional chain, and a distance cutoff.
- Output: the polymer residues whose closest heavy atom lies within the
  cutoff of the ligand's heavy atoms, each with its chain, the PDB
  (author) residue number, the residue name, the minimum distance, and
  the UniProt residue number from SIFTS when one exists.
- **Scope**: this tool reports **geometric proximity**. It does NOT
  compute a binding energy, an affinity, a docking score, or an
  interaction type, and a contact is not evidence of biological
  significance. The card and the docstring say so.

## How the expected values were fixed

A standalone reference script (not part of the repo, kept outside it)
downloaded the four mmCIF files, took the ligand's heavy atoms
(`type_symbol` not in `H`/`D`), took every polymer residue's heavy
atoms (rows with a `label_seq_id`), and computed the minimum
heavy-atom distance for every residue. The UniProt numbers come from
the SIFTS alignment in the RCSB Data API: for a polymer entity the
aligned region gives `entity_beg_seq_id` (the entity label_seq_id) and
`ref_beg_seq_id` (the UniProt residue number), so
`uniprot_number = label_seq_id + (ref_beg_seq_id - entity_beg_seq_id)`
for residues inside the aligned region.

The tool must reproduce these numbers with the same definitions:
heavy atoms only, `<= cutoff` (a residue at exactly the cutoff counts),
and the PDB (author) residue number as the "PDB number".

Reference data actually used (all fetched from RCSB on 2026-10-24):

| entry | ligand | ligand heavy atoms | ligand instance (chain, PDB number) | other non-water components present |
|---|---|---|---|---|
| 1T4J | FRJ | 41 | A 299 | (none) |
| 1OPK | MYR | 16 | A 1 | GOL, P16 |
| 1OPK | P16 | 29 | A 2 | GOL, MYR |
| 5MO4 | AY7 | 31 | A 602 | NIL |
| 5MO4 | NIL | 39 | A 601 | AY7 |
| 1V4S | MRK | 23 | A 501 | GLC, NA |
| 1V4S | GLC | 12 | A 500 | MRK, NA |

## Criteria

| # | Criterion | Verification |
|---|---|---|
| GLC-1 | `biomni/tool/get_ligand_contacts.py` exists with the entry point `get_ligand_contacts(pdb_id=None, structure_file=None, ligand_id=..., chain=None, cutoff=4.0)` | `git ls-files` returns the path; the test imports the function. |
| GLC-2 | Return contract: the function returns `{success, data, error, source, source_version, query_time_utc}` (the Part-1c decorator) | The test asserts all 6 keys are present for a success and for a failure. |
| GLC-3 | The ligand is found by its chemical component id, and its instance is reported as (chain, PDB number): 1T4J/FRJ -> A 299; 1OPK/MYR -> A 1; 1OPK/P16 -> A 2; 5MO4/AY7 -> A 602; 5MO4/NIL -> A 601; 1V4S/MRK -> A 501; 1V4S/GLC -> A 500 | The test asserts `data["ligand"]["chain"]` and `data["ligand"]["pdb_number"]` for each of the 7 cases. |
| GLC-4 | Known answer, 1T4J / FRJ at 4.0 A: exactly 11 contacts, in this order, with these minimum distances (A): PRO188 3.92, ALA189 3.42, LEU192 3.80, ASN193 3.01, PHE196 3.55, GLU200 3.30, GLU276 2.55, GLY277 3.37, LYS279 3.03, PHE280 2.65, MET282 3.59 | The test asserts the exact list of (chain, pdb_number, residue_name, min_distance) tuples. |
| GLC-5 | Known answer, 1OPK / MYR at 4.0 A: exactly 8 contacts (A): LEU359 3.84, LEU360 3.69, ALA363 3.71, LEU448 3.73, ALA452 3.85, GLU481 3.47, ILE521 3.87, LEU529 3.54 | The test asserts the exact list. |
| GLC-6 | Known answer, 1OPK / P16 at 4.0 A: exactly 19 contacts (A): LEU267 3.85, TYR272 3.31, VAL275 3.56, ALA288 3.45, VAL289 3.91, LYS290 3.65, GLU305 3.32, MET309 3.34, VAL318 3.95, ILE332 3.63, THR334 3.24, GLU335 3.35, PHE336 3.77, MET337 2.84, GLY340 3.48, LEU389 3.56, ALA399 3.59, ASP400 3.56, PHE401 3.75 | The test asserts the exact list. |
| GLC-7 | Known answer, 5MO4 / AY7 at 4.0 A: exactly 18 contacts (A): ARG351 3.79, ALA356 3.68, LEU359 3.22, LEU360 3.38, ALA363 3.57, LEU448 3.27, ILE451 3.61, ALA452 3.52, THR453 3.48, TYR454 3.87, GLU481 2.82, CYS483 3.84, PRO484 3.73, VAL487 3.68, PHE512 3.63, ILE521 3.62, VAL525 3.67, LEU529 3.76 | The test asserts the exact list. |
| GLC-8 | Known answer, 5MO4 / NIL at 4.0 A: exactly 25 contacts (A): LEU267 3.71, TYR272 3.55, VAL275 3.81, ALA288 3.29, VAL289 3.98, LYS290 3.39, LYS304 3.83, GLU305 2.95, VAL308 3.63, MET309 3.47, ILE312 3.64, LEU317 3.55, VAL318 3.57, ILE332 3.49, ILE334 3.25, PHE336 3.45, MET337 2.84, GLY340 3.86, PHE378 3.63, HIS380 3.38, LEU389 3.70, VAL398 3.75, ALA399 3.20, ASP400 3.01, PHE401 3.34 | The test asserts the exact list. |
| GLC-9 | Known answer, 1V4S / MRK at 4.0 A: exactly 14 contacts (A): TYR61 3.25, VAL62 3.62, ARG63 2.73, SER64 3.64, THR65 3.41, PRO66 3.77, MET210 3.66, ILE211 3.59, TYR214 3.01, TYR215 2.45, CYS220 3.30, MET235 3.51, VAL452 3.62, VAL455 3.46 | The test asserts the exact list. |
| GLC-10 | Known answer, 1V4S / GLC at 4.0 A: exactly 14 contacts (A): SER151 3.57, PHE152 3.29, PRO153 3.39, THR168 2.90, LYS169 2.97, ASN204 2.96, ASP205 2.53, ILE225 3.65, GLY229 3.65, CYS230 3.54, ASN231 3.23, GLU256 2.59, GLN287 3.48, GLU290 2.53 | The test asserts the exact list. |
| GLC-11 | Cutoff monotonicity: for every one of the 7 cases the contact set at 3.0 A is a strict subset of the contact set at 4.0 A, and equals exactly: 1T4J/FRJ -> GLU276, PHE280 (2); 1OPK/MYR -> empty (0); 1OPK/P16 -> MET337 (1); 5MO4/AY7 -> GLU481 (1); 5MO4/NIL -> GLU305, MET337 (2); 1V4S/MRK -> ARG63, TYR215 (2); 1V4S/GLC -> THR168, LYS169, ASN204, ASP205, GLU256, GLU290 (6) | The test asserts the 3.0 A list per case and that it is a subset of the 4.0 A list. |
| GLC-12 | SIFTS mapping: every contact carries the UniProt accession and the UniProt residue number of its own entity, with a per-entry constant offset between the PDB (author) number and the UniProt number: 1T4J -> P18031, offset 0 (PDB 188 -> UniProt 188); 1OPK -> P00520, offset -19 (PDB 359 -> UniProt 340, PDB 267 -> UniProt 248); 5MO4 -> P00519, offset -19 (PDB 351 -> UniProt 332, PDB 481 -> UniProt 462); 1V4S -> P35557, offset 0 (PDB 61 -> UniProt 61) | The test asserts the accession per case and the exact UniProt number for at least 3 residues per case. |
| GLC-13 | Negative control: an unknown ligand id returns `success=False` and names the ligand ids that ARE present in the entry: 1T4J -> [FRJ]; 1OPK -> [GOL, MYR, P16]; 5MO4 -> [AY7, NIL]; 1V4S -> [GLC, MRK, NA] | The test asserts `success is False` and that the present-id list appears in the returned payload (the `data` dict, with `success=False`). |
| GLC-14 | A local structure file gives the same answer as the entry id: `get_ligand_contacts(structure_file=<the downloaded 1T4J.cif>, ligand_id="FRJ")` returns the same 11 contacts as `get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ")`, and needs no network for the coordinates | The test downloads the file once, writes it to `tmp_path`, and compares the two results. |
| GLC-15 | Invalid input handling: an empty `ligand_id`, a non-positive `cutoff`, and neither `pdb_id` nor `structure_file` given each return `success=False` with a descriptive error (no exception) | The test asserts `success is False` and a non-empty `error`. |
| GLC-16 | The docstring states the scope: the tool reports geometric proximity, not binding energy | The test asserts the phrases "geometric proximity" and "not" + "binding energy" are in the function docstring. |
| GLC-17 | Tool card exists at `docs/tool_cards/P32_get_ligand_contacts.md` and does not contain the forbidden `self-reported` substring | The Part-1f audit test asserts no `self-reported` substring. |
| GLC-18 | The tool is exposed to arm D: `get_ligand_contacts` is in `alloagent/exposed_tools.txt` (44 names in total) and is registered | The test reads the exposed list and asserts the name is present and that the count is 44. |

## Verdict (filled ONCE after the test runs)

| # | Status | Value / note |
|---|---|---|
| GLC-1 | (filled) | (filled) |
| GLC-2 | (filled) | (filled) |
| GLC-3 | (filled) | (filled) |
| GLC-4 | (filled) | (filled) |
| GLC-5 | (filled) | (filled) |
| GLC-6 | (filled) | (filled) |
| GLC-7 | (filled) | (filled) |
| GLC-8 | (filled) | (filled) |
| GLC-9 | (filled) | (filled) |
| GLC-10 | (filled) | (filled) |
| GLC-11 | (filled) | (filled) |
| GLC-12 | (filled) | (filled) |
| GLC-13 | (filled) | (filled) |
| GLC-14 | (filled) | (filled) |
| GLC-15 | (filled) | (filled) |
| GLC-16 | (filled) | (filled) |
| GLC-17 | (filled) | (filled) |
| GLC-18 | (filled) | (filled) |

## Status

Criteria committed first. Implementation, known-answer tests, the tool
card and the exposed-list update follow in later commits.

## Dated notes (added after running; do NOT change the original criterion text above)

### 2026-10-24 — the stated distances are 2-decimal values, so they are checked to 0.01 A

Three of the 96 distances stated in GLC-4..GLC-10 differ from the
tool's own rounding by exactly 0.01 A:

| case | residue | stated here | tool (`round(distance, 2)`) |
|---|---|---|---|
| 1OPK / P16 | ILE332 | 3.63 | 3.64 |
| 5MO4 / AY7 | THR453 | 3.48 | 3.47 |
| 5MO4 / AY7 | VAL525 | 3.67 | 3.68 |

Cause: the reference values were rendered from a distance that had
already been rounded to 3 decimals, so the stated 2-decimal number can
land on the other side of a 2-decimal rounding boundary. The two
implementations agree on the distance to ~1e-16 A (one is a pure-Python
min over the atom pairs, the other a numpy reduction); only the final
rounding differs, and only where the true value sits on a boundary.

Consequence for the verification: the distance is asserted as
`|reported - stated| <= 0.01 A`, i.e. to the precision at which the
criterion states it. The count, the order, the chain, the PDB residue
number and the residue name of every contact are still asserted
exactly, and the 3.0 A contact lists are asserted exactly (as
residue names and PDB numbers).

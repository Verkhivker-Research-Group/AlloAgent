# P32 get_ligand_contacts

## Question the tool answers

"Which polymer residues of this PDB entry lie within a distance cutoff
of the named ligand?"

## What it does NOT answer

- It does **not** report a binding energy, an affinity, a docking score
  or an interaction type. The output is **geometric proximity**: the
  minimum heavy-atom distance between the ligand and each residue.
- A contact is not evidence that the interaction is biological, that it
  is made by the ligand in solution, or that the residue is a hotspot.
- It does not say whether the ligand is a co-crystallized drug, a
  buffer component, a crystallization additive or a physiological
  ligand. The ligand is selected by its chemical component id only.
- It does not include waters, ions or other non-polymer components in
  the contact list (they are not polymer residues); it does not report
  ligand-ligand or ligand-water contacts.
- It does not model protonation, occupancy, alternate conformations or
  disorder: every modelled atom of the residue counts, and hydrogens
  and deuteriums are excluded.
- It does not predict binding for a structure that is not in the PDB.
  Use a docking tool (for example B2 `dock_ligand_vina`) for that, and
  treat its poses as hypotheses.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | `str` or None | no | `None` | 4-character PDB entry id (e.g. `1T4J`). Ignored when `structure_file` is given. |
| `structure_file` | `str` or None | no | `None` | Path to a local mmCIF file. The entry id is taken from the file's `_entry.id`, so the UniProt mapping matches the `pdb_id` route. |
| `ligand_id` | `str` | yes | `""` | RCSB chemical component id of the ligand (e.g. `FRJ`, `MYR`). Case-insensitive. |
| `chain` | `str` or None | no | `None` | Restrict the query to one chain (e.g. `A`). `None` searches every chain. |
| `cutoff` | `float` | no | `4.0` | Maximum distance in Angstrom; a residue whose closest heavy atom is at or below the cutoff is a contact. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is:

```python
{
    "pdb_id": "1T4J",
    "ligand": {
        "id": "FRJ",
        "chain": "A",
        "pdb_number": 299,
        "atom_count": 41,
        "instances": [{"chain": "A", "pdb_number": 299}],
    },
    "cutoff": 4.0,
    "contacts": [
        {
            "chain": "A",
            "pdb_number": 276,
            "insertion_code": None,
            "residue_name": "GLU",
            "min_distance": 2.55,
            "uniprot_accession": "P18031",
            "uniprot_number": 276,
        },
    ],
    "contact_count": 11,
    "ligand_ids_present": ["FRJ"],
    "source_structure": "RCSB",
}
```

`pdb_number` is the PDB **author** numbering of the entry (the number
in the `HETATM`/`ATOM` records). `uniprot_number` comes from the SIFTS
alignment and is `None` when the residue is not covered by one.

## Source and version

- coordinates: `https://files.rcsb.org/download/<pdb_id>.cif` (mmCIF)
- SIFTS alignment: `https://data.rcsb.org/rest/v1/core/polymer_entity/<pdb_id>/<entity_id>`
- source version: RCSB PDB, current as of 2026-10-24
- license: RCSB PDB data is in the public domain

## Runtime

- typical latency: ~2-4 s per call (one mmCIF download, one Data API
  call per polymer entity in the entry)
- offline vs online: online for the `pdb_id` route; the
  `structure_file` route reads the coordinates from disk and still
  needs the Data API for the UniProt mapping (the contacts themselves
  are computed offline)

## Determinism

- deterministic? yes. The coordinates and the SIFTS alignment of a
  given entry are fixed; the contact list is a function of the
  coordinates, the cutoff and the definitions below.
- definitions that make it reproducible: heavy atoms only (element H
  and D excluded), a contact is a minimum distance `<= cutoff`,
  the PDB number is the author numbering, and the contact list is
  sorted by (chain, PDB number).

## Failure modes

- Network unreachable: `{"success": false, "error": "RCSB download failed: ..."}`
- RCSB returns non-200: `{"success": false, "error": "could not read the structure: RCSB download failed for ... with status 404"}`
- The file is not an mmCIF file: `{"success": false, "error": "could not read the structure: the mmCIF file has no _atom_site loop"}`
- Unknown ligand id: `{"success": false, "error": "ligand ZZZ not found in 1T4J; ligand ids present: FRJ", "data": {"ligand_ids_present": ["FRJ"], ...}}`
- Invalid input (empty ligand id, non-positive cutoff, neither
  `pdb_id` nor `structure_file`): `{"success": false, "error": "<reason>"}`
- The SIFTS call fails: the contacts are still returned, with
  `uniprot_accession`/`uniprot_number` `None` and a note in
  `data["uniprot_error"]`.

## Known-answer test

`tests/test_get_ligand_contacts.py`, criteria GLC-1..GLC-18 in
`docs/2_get_ligand_contacts_criteria.md`. The expected values were
computed independently from the real RCSB files before the tool was
written:

- 1T4J / FRJ at 4.0 A: 11 contacts (PRO188 3.92, ALA189 3.42,
  LEU192 3.80, ASN193 3.01, PHE196 3.55, GLU200 3.30, GLU276 2.55,
  GLY277 3.37, LYS279 3.03, PHE280 2.65, MET282 3.59)
- 1OPK / MYR: 8 contacts; 1OPK / P16: 19 contacts
- 5MO4 / AY7: 18 contacts; 5MO4 / NIL: 25 contacts
- 1V4S / MRK: 14 contacts; 1V4S / GLC: 14 contacts
- SIFTS accessions P18031 / P00520 / P00519 / P35557

## Negative control

- input: `ligand_id="ZZZ"` on any of the four entries
- expected: `success=False`, and `data["ligand_ids_present"]` names
  the ids that are in the entry (`[FRJ]`, `[GOL, MYR, P16]`,
  `[AY7, NIL]`, `[GLC, MRK, NA]`)

## Code location and version

- function: `biomni/tool/get_ligand_contacts.py::get_ligand_contacts`
- recorded in: the per-run JSON at the key `image_id`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

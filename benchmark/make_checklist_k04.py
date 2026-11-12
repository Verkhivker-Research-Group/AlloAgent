"""Write the checklist of the K04 prompt (the KRAS contact-network prompt).

K04 was **deferred** on 2026-10-28: the STINGAllo question had no
non-empty prediction that did not duplicate another prompt.  The launch
set recorded its replacement, and on 2026-11-03 that replacement was
written, validated and run:

    "Build a residue contact network for KRAS in PDB entry 6OIM chain A.
     Find the shortest path between a residue within 4 angstroms of the
     covalent inhibitor and a residue within 4 angstroms of GDP.  Report
     both residues, the path, its length and the cutoff used."

The reference output of that question was measured before any run
(``benchmark/k04_reference_output.json``: the ligand contacts from
``get_ligand_contacts`` and the network from ``residue_contact_network``),
and this script writes the checklist from it.

The deferred question was **removed** from the benchmark on 2026-11-10: it
was never run, so nothing that was run changes.  The prompt table has 40
rows and every one of them is run.

This script writes the prompt table, the checklists, the launch set and
the restricted set, and it refreshes the criteria hash of the restricted
set.  It is idempotent: running it again leaves the files byte for byte
as they are.  The validation report is written by the validator
(``benchmark/validate_benchmark.py``) and the dated notes of the plan by
hand; neither is written here.

    python benchmark/make_checklist_k04.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BENCHMARK = REPO / "benchmark"
DRAFT = BENCHMARK / "benchmark_draft.json"
CHECKLISTS = BENCHMARK / "checklists.json"
LAUNCH_SET = BENCHMARK / "launch_prompt_set.json"
RESTRICTED_SET = BENCHMARK / "restricted_prompt_set.json"
CRITERIA_CHECKSUMS = BENCHMARK / "criteria_checksums.txt"
REFERENCE = BENCHMARK / "k04_reference_output.json"

PROMPT = (
    "Build a residue contact network for KRAS in PDB entry 6OIM chain A. "
    "Find the shortest path between a residue within 4 angstroms of the "
    "covalent inhibitor and a residue within 4 angstroms of GDP. Report both "
    "residues, the path, its length and the cutoff used."
)
TOOLS = "residue_contact_network; get_ligand_contacts"

GENERATED = "2026-11-10"
REMOVAL_DATE = "2026-11-10"

K04_NOTE = (
    "Dated note 2026-11-03: K04 is the replacement the launch set recorded on "
    "2026-10-28 - the residue contact network of KRAS in 6OIM chain A and the "
    "shortest path between a residue within 4 A of the covalent inhibitor "
    "(MOV) and a residue within 4 A of GDP. Its reference output was measured "
    "from the primary sources before any run of it "
    "(benchmark/k04_reference_output.json) and its checklist was committed "
    "before its runs."
)
REMOVAL_NOTE = (
    "Dated note 2026-11-10: the deferred STINGAllo question that K04 replaced "
    "was removed from the prompt table, the checklists, the launch set and "
    "the restricted set: it was never run, so the criteria of K04 and of every "
    "other prompt are unchanged."
)
CHECKLISTS_2026_11_03_NOTE = (
    "The deferred question was replaced by the question the launch set named "
    "(the residue contact network of KRAS in 6OIM chain A and the shortest "
    "path between a residue within 4 A of the covalent inhibitor and a "
    "residue within 4 A of GDP), which took the id K04; its criteria were "
    "written from the measured reference output "
    "(benchmark/k04_reference_output.json) before any run of the prompt."
)
CHECKLISTS_REMOVAL_NOTE = (
    "The deferred question was removed from the prompt table, the checklists, "
    "the launch set and the restricted set: it was never run, so nothing that "
    "was run changes. The prompt table has 40 rows and all of them are run."
)
LAUNCH_2026_10_28_NOTE = (
    "Dated note 2026-10-28: the launch set is committed BEFORE the launch and "
    "the driver refuses to start without it. The prompt table itself (40 "
    "prompts, the deferred one included) is unchanged: a deferred prompt "
    "keeps its committed criteria."
)
LAUNCH_2026_11_03_NOTE = (
    "Dated note 2026-11-03: the deferred question was replaced. The "
    "replacement the launch set named on 2026-10-28 (the residue contact "
    "network of KRAS in 6OIM chain A and the shortest path between a residue "
    "within 4 A of the covalent inhibitor (MOV) and a residue within 4 A of "
    "GDP) took the id K04; it was validated from the primary sources, its "
    "checklist was committed before its runs, and its six runs (3 repeats x 2 "
    "arms) were made as a separate batch under their own launch tag. The "
    "deferred question kept its committed criteria until it was removed on "
    "2026-11-10 (see the note below). The 39 prompts of the main run and its "
    "234 runs are unchanged."
)
LAUNCH_REMOVAL_NOTE = (
    "Dated note 2026-11-10: the deferred prompt was removed from the prompt "
    "table and from the checklists; it was never run, so nothing that was run "
    "changes. The launch set is now the whole prompt table (40 prompts) and "
    "nothing is deferred."
)
RESTRICTED_LAUNCH_SET_NOTE = (
    "Dated note 2026-10-28: the launch set is benchmark/launch_prompt_set.json "
    "(39 prompts) and one prompt was deferred with a dated note; the "
    "restricted set was unchanged at 15 'yes' prompts. Dated note 2026-11-03: "
    "the deferred question was replaced by the K04 residue contact network of "
    "KRAS in 6OIM chain A, which was run as a separate batch of six runs; the "
    "restricted set is still 15 'yes' prompts, with K04 a 'no' (the 6OIM "
    "structure is in the local cache and the network is built from the "
    "coordinates). Dated note 2026-11-10: the deferred question was removed "
    "from the benchmark; it was never run. The launch set is now the whole "
    "prompt table (40 prompts) and the restricted set has 40 rows, still 15 "
    "'yes' prompts."
)
RESTRICTED_K04_NOTE = (
    "Dated note 2026-11-03: the replacement of the deferred question, run as "
    "a separate batch in the main scenario (3 repeats x 2 arms). Dated note "
    "2026-11-10: the deferred question itself was removed from the benchmark; "
    "it was never run, so this row and its criteria are unchanged."
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload, eol: str, ensure_ascii: bool = False) -> None:
    """Write a JSON file with the line ending the file already uses."""
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=ensure_ascii) + "\n",
        encoding="utf-8", newline=eol)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(path: Path) -> str:
    """The hash the criteria guard uses: the text of the file."""
    return hashlib.sha256(
        path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def alternatives(reference: list[dict]) -> dict:
    """The contact residues as alternatives of the committed `set` kind.

    The `set` kind asks for ONE of the alternative lists: a list with a
    single residue passes when the answer reports that residue, so a
    value with one list per reference residue passes when the answer
    names any of them.
    """
    return {
        f"{contact['residue_name']}{contact['pdb_number']}": [contact["pdb_number"]]
        for contact in reference
    }


def build_items(reference: dict) -> list[dict]:
    mov = reference["mov_contacts"]
    gdp = reference["gdp_contacts"]
    network = reference["network"]
    source_contacts = "RCSB mmCIF 6OIM (chain A) at 4 A, via get_ligand_contacts"
    source_network = (
        "the residue contact network of 6OIM (a heavy-atom contact cutoff of "
        f"{network['contact_cutoff_angstrom']} A, {network['n_residues']} residues, "
        f"{network['n_edges']} edges), via residue_contact_network"
    )
    return [
        {
            "key": "accession_P01116",
            "kind": "exact",
            "value": {"name": "GTPase KRas", "gene": "KRAS",
                      "organism": "Homo sapiens"},
            "tolerance": None,
            "source": "UniProt REST",
            "note": None,
            "status": "PASS",
        },
        {
            "key": "mov_contact_residue_P01116",
            "kind": "set",
            "value": alternatives(mov),
            "tolerance": 0,
            "source": source_contacts,
            "note": (
                "the answer names one residue of chain A that is within 4 A of "
                "the covalent inhibitor (MOV); the value lists the 17 reference "
                "residues, each as an alternative, so the item passes when the "
                "answer names any of them"
            ),
            "status": "PASS",
        },
        {
            "key": "gdp_contact_residue_P01116",
            "kind": "set",
            "value": alternatives(gdp),
            "tolerance": 0,
            "source": source_contacts,
            "note": (
                "the answer names one residue of chain A that is within 4 A of "
                "GDP; the value lists the 18 reference residues, each as an "
                "alternative"
            ),
            "status": "PASS",
        },
        {
            "key": "path_length_edges",
            "kind": "number",
            "value": 1,
            "tolerance": 1,
            "source": source_network,
            "note": (
                "the shortest path between a residue within 4 A of MOV and a "
                "residue within 4 A of GDP has one edge; the band of the "
                "tolerance admits zero edges (CYS12 and LYS16 are within 4 A of "
                "both ligands, so the same residue can serve both roles) and "
                "two edges"
            ),
            "status": "PASS",
        },
        {
            "key": "contact_cutoff_stated",
            "kind": "qualitative",
            "value": (
                "the answer states the cutoff it used for the residue contact "
                "network (the reference: a heavy-atom contact cutoff of 4.5 A; "
                "the ligand contacts are at 4 A, as the prompt asks)"
            ),
            "tolerance": None,
            "source": "the prompt's own criterion (the cutoff decides the path)",
            "note": None,
            "status": "PASS",
        },
        {
            "key": "contact_definition_named",
            "kind": "qualitative",
            "value": (
                "the answer names the contact definition it used (for example a "
                "heavy-atom contact at a stated cutoff between residues, over "
                "the residues of the chain)"
            ),
            "tolerance": None,
            "source": "the prompt's own criterion (the definition decides the network)",
            "note": None,
            "status": "PASS",
        },
        {
            "key": "path_reported_with_its_residues",
            "kind": "qualitative",
            "value": (
                "the answer reports the path with its residues: the residue it "
                "used for the covalent inhibitor, the residue it used for GDP "
                "and the residues between them"
            ),
            "tolerance": None,
            "source": "the prompt's own criterion",
            "note": (
                "fifteen residue pairs are one edge apart at the reference "
                "cutoff, so any of them is a correct shortest path"
            ),
            "status": "PASS",
        },
        {
            "key": "several_shortest_paths_stated",
            "kind": "qualitative",
            "value": (
                "the answer says that more than one shortest path can exist "
                "(fifteen residue pairs are one edge apart at a 4.5 A contact "
                "cutoff) and/or that the path depends on the contact cutoff, "
                "instead of presenting one path as the unique answer"
            ),
            "tolerance": None,
            "source": "the measured reference (the shortest path is not unique)",
            "note": (
                "the honest limit; the degenerate case (the same residue within "
                "4 A of both ligands) is the strongest form of it"
            ),
            "status": "PASS",
        },
    ]


def upsert(rows: list[dict], row: dict) -> list[dict]:
    """The row with the id of `row`, in place; appended if it is missing."""
    for index, existing in enumerate(rows):
        if existing.get("id") == row["id"]:
            rows[index] = row
            return rows
    rows.append(row)
    return rows


def set_notes(notes: list, wanted: list[dict]) -> list:
    """The notes of `wanted`, in their order; the other ones are kept."""
    for note in wanted:
        notes[:] = [existing for existing in notes
                    if not (existing.get("date") == note["date"]
                            and existing.get("prompt") == note.get("prompt"))]
        notes.append(note)
    return notes


def main() -> int:
    reference = read_json(REFERENCE)
    items = build_items(reference)

    # 1. the prompt table: the row of the K04 prompt.
    draft = read_json(DRAFT)
    draft = upsert(draft, {
        "id": "K04",
        "category": "Allosteric site prediction",
        "tier": 2,
        "accession": "P01116",
        "prompt": PROMPT,
        "d_tools_expected": TOOLS,
        "draft_checklist": (
            "the residues of chain A within 4 A of MOV and within 4 A of GDP; "
            "the shortest path between a residue of each set in the residue "
            "contact network; the length of that path; the contact cutoff used"
        ),
        "baseline_route": "P",
        "dated_note": K04_NOTE + " " + REMOVAL_NOTE,
    })
    write_json(DRAFT, draft, "\r\n")
    draft_sha = sha256_file(DRAFT)

    # 2. the checklists: the entry of the K04 prompt.
    checklists = read_json(CHECKLISTS)
    checklists["prompts"] = upsert(checklists["prompts"], {
        "id": "K04",
        "category": "Allosteric site prediction",
        "tier": 2,
        "accession": "P01116",
        "baseline_route": "P",
        "d_tools_expected": TOOLS,
        "status": "PASS",
        "checklist": items,
        "dated_notes": [
            {"date": "2026-11-03", "note": K04_NOTE, "prompt": "K04"},
            {"date": REMOVAL_DATE, "note": REMOVAL_NOTE, "prompt": "K04"},
        ],
    })
    checklists["summary"] = {
        "total": len(checklists["prompts"]),
        "pass": sum(1 for p in checklists["prompts"] if p.get("status") == "PASS"),
        "problem": sum(1 for p in checklists["prompts"]
                       if p.get("status") != "PASS"),
    }
    checklists.setdefault("dated_notes", [])
    set_notes(checklists["dated_notes"], [
        {"date": "2026-11-03", "note": CHECKLISTS_2026_11_03_NOTE},
        {"date": REMOVAL_DATE, "note": CHECKLISTS_REMOVAL_NOTE},
    ])
    write_json(CHECKLISTS, checklists, "\n", ensure_ascii=True)

    # 3. the launch set: the whole prompt table, nothing deferred.
    draft_ids = [row["id"] for row in draft]
    launch = read_json(LAUNCH_SET)
    launch["generated"] = GENERATED
    launch["source_sha256"] = draft_sha
    launch["launch_prompts"] = list(draft_ids)
    launch["deferred"] = []
    launch["counts"] = {
        "draft_prompts": len(draft_ids),
        "launch_prompts": len(launch["launch_prompts"]),
        "deferred": len(launch["deferred"]),
    }
    launch["dated_notes"] = [
        LAUNCH_2026_10_28_NOTE, LAUNCH_2026_11_03_NOTE, LAUNCH_REMOVAL_NOTE,
    ]
    write_json(LAUNCH_SET, launch, "\r\n")

    # 4. the restricted set: one row per prompt of the table.
    restricted = read_json(RESTRICTED_SET)
    restricted["prompts"] = upsert(restricted["prompts"], {
        "id": "K04",
        "category": "Allosteric site prediction",
        "tier": 2,
        "accession": "P01116",
        "prompt": PROMPT,
        "solvable_from_local_resources_alone": "no",
        "reason": (
            "the prompt was added on 2026-11-03, after the restricted "
            "scenario was run, so it is not part of that scenario; it would be "
            "solvable there (the 6OIM structure is in the local cache and the "
            "network is built from the coordinates)"
        ),
        "tools": TOOLS,
        "data": "the structure cache (6OIM)",
        "would_become_yes_if": (
            "a restricted-scenario run that includes it (no network is needed: "
            "the structure is local)"
        ),
        "launch": True,
        "deferred_reason": "",
        "deferred_note": RESTRICTED_K04_NOTE,
    })
    restricted["source_sha256"] = draft_sha
    restricted["generated"] = GENERATED
    yes = [row["id"] for row in restricted["prompts"]
           if row["solvable_from_local_resources_alone"] == "yes"]
    restricted["the_set"] = yes
    restricted["counts"] = {
        "prompts": len(restricted["prompts"]),
        "yes": len(yes),
        "no": len(restricted["prompts"]) - len(yes),
    }
    restricted["launch_set_note"] = RESTRICTED_LAUNCH_SET_NOTE
    write_json(RESTRICTED_SET, restricted, "\r\n")

    # 5. the criteria hash of the restricted set.
    lines = []
    for line in CRITERIA_CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            lines.append(line)
            continue
        name = line.split("  ", 1)[1].strip()
        if name == "benchmark/restricted_prompt_set.json":
            lines.append(f"{sha256_text(RESTRICTED_SET)}  {name}")
        else:
            lines.append(line)
    CRITERIA_CHECKSUMS.write_text(
        "\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="")

    print("the prompt table, the checklists, the launch set and the restricted "
          "set carry the K04 checklist")
    print(f"  {draft_sha}  benchmark/benchmark_draft.json")
    print(f"  {sha256_text(RESTRICTED_SET)}  benchmark/restricted_prompt_set.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

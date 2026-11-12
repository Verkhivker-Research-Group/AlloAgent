"""Build the machine-readable form of the pocket-reference correction.

The dated note of 2026-11-02 lives in ``benchmark/corrections.md``; this
script writes the values it corrects, so that they come from the
measurement and not from a hand-written number.

It reads the corrected reference output
(``benchmark/pocket_reference_outputs_v2.json``) and the committed one
(``benchmark/pocket_reference_outputs.json``), compares the two selections
for every site, and writes only the items whose corrected value differs
from the committed item of ``benchmark/checklists.json``.

    python benchmark/make_pocket_reference_correction.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BENCHMARK = REPO / "benchmark"
COMMITTED = BENCHMARK / "pocket_reference_outputs.json"
CORRECTED = BENCHMARK / "pocket_reference_outputs_v2.json"
CHECKLISTS = BENCHMARK / "checklists.json"
OUT = BENCHMARK / "corrections" / "pocket_reference_selection_2026-11-02.json"

# The site of every pocket prompt, and the committed item that carries it.
SITE_OF_ITEM = {
    "fpocket_reference_P01": "1T4J",
    "p2rank_reference_P01": "1T4J",
    "fpocket_reference_P02": "6OIM",
    "p2rank_reference_P02": "6OIM",
    "fpocket_reference_P03": "5EHR",
    "p2rank_reference_P03": "5EHR",
    "fpocket_reference_P05": "1OPK",
    "p2rank_reference_P05": "1OPK",
    "fpocket_reference_P06": "1V4S",
    "p2rank_reference_P06": "1V4S",
    "fpocket_reference_P07": "1T4J",
    "p2rank_reference_P07": "1T4J",
}
# The site of every prompt, for the sites that no committed item carries.
PROMPTS_OF_SITE = {
    "1T4J": ["P01", "P07"],
    "1OPK": ["P05"],
    "1V4S": ["P06"],
    "1V4S_GLC": ["P06"],
    "6OIM": ["P02"],
    "5EHR": ["P03"],
}


def main() -> int:
    committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
    corrected = json.loads(CORRECTED.read_text(encoding="utf-8"))
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    items = {
        item["key"]: item
        for prompt in checklists["prompts"]
        for item in prompt["checklist"]
    }

    corrections: dict[str, dict] = {}
    sites_without_an_item: dict[str, dict] = {}
    degenerate: dict[str, dict] = {}
    items_without_a_value: dict[str, dict] = {}

    # Every committed reference item, with the site and the method it
    # judges: the two items of one site are separate items.
    reference_items = {
        key: (SITE_OF_ITEM[key], key.split("_reference_")[0])
        for key in items
        if key.startswith(("fpocket_reference_", "p2rank_reference_"))
    }

    for key, (site, method) in reference_items.items():
        measured = corrected["sites"].get(site, {}).get(method)
        old = committed["sites"].get(site, {}).get(method)
        if not measured or not old:
            continue
        new_rank = measured["rank_of_the_pocket_covering_the_site"]
        new_overlap = measured["overlap_of_the_covering_pocket"]
        old_rank = old["rank_of_the_pocket_covering_the_site"]
        old_overlap = old["overlap_of_the_covering_pocket"]
        if (old_rank, old_overlap) != (new_rank, new_overlap):
            corrections[key] = {
                "rank_of_the_pocket_covering_the_site": new_rank,
                "overlap_of_the_covering_pocket": new_overlap,
            }
        if method == "p2rank" and all(
            pocket["n_residues"] == 0 for pocket in measured["pockets"]
        ):
            degenerate[key] = {
                "reason": (
                    "no P2Rank pocket carries a residue in the measurement, "
                    "so the item only asks the answer for the number 0 and "
                    "cannot discriminate"
                ),
                "measured_p2rank_pockets": len(measured["pockets"]),
                "measured_p2rank_residues": [
                    pocket["n_residues"] for pocket in measured["pockets"]
                ],
            }

    # The sites whose committed selection and corrected selection differ,
    # and that no committed item carries: their prompts are judged, not
    # scripted, so the judge needs the corrected numbers.
    for site, spec in corrected["sites"].items():
        for method in ("fpocket", "p2rank"):
            measured = spec.get(method)
            old = committed["sites"].get(site, {}).get(method)
            if not measured or not old:
                continue
            new_rank = measured["rank_of_the_pocket_covering_the_site"]
            new_overlap = measured["overlap_of_the_covering_pocket"]
            old_rank = old["rank_of_the_pocket_covering_the_site"]
            old_overlap = old["overlap_of_the_covering_pocket"]
            if (old_rank, old_overlap) == (new_rank, new_overlap):
                continue
            if any(site == item_site for item_site, _ in reference_items.values()):
                continue
            sites_without_an_item[site] = {
                "method": method,
                "prompts": PROMPTS_OF_SITE.get(site, []),
                "committed": {
                    "rank_of_the_pocket_covering_the_site": old_rank,
                    "overlap_of_the_covering_pocket": old_overlap,
                },
                "corrected": {
                    "rank_of_the_pocket_covering_the_site": new_rank,
                    "overlap_of_the_covering_pocket": new_overlap,
                },
            }

    # The prompts whose pocket criteria are judged (qualitative) and whose
    # site has no committed reference item: the judge needs the numbers.
    for site, entry in list(sites_without_an_item.items()):
        for prompt_id in entry["prompts"]:
            items_without_a_value.setdefault(prompt_id, {})[site] = entry["corrected"]

    payload = {
        "dated_note": "2026-11-02",
        "note": (
            "The pocket reference picked the first pocket with any site "
            "residue instead of the pocket with the most site residues "
            "(benchmark/pocket_reference_outputs.py).  These are the "
            "corrected values of the committed items; the committed "
            "checklists and the committed reference output are unchanged."
        ),
        "dated_note_file": "benchmark/corrections.md",
        "sources": {
            "committed_reference": "benchmark/pocket_reference_outputs.json",
            "corrected_reference": "benchmark/pocket_reference_outputs_v2.json",
            "measurement_script": "benchmark/pocket_reference_outputs_v2.py",
        },
        "corrections": corrections,
        "sites_without_a_committed_item": sites_without_an_item,
        "judge_needs_these_numbers": items_without_a_value,
        "degenerate_items": degenerate,
        "unchanged_items": sorted(
            key for key in reference_items
            if key not in corrections and key not in degenerate
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  corrected items: {sorted(corrections)}")
    print(f"  degenerate items: {sorted(degenerate)}")
    print(f"  sites without a committed item: {sorted(sites_without_an_item)}")
    print(f"  unchanged reference items: {payload['unchanged_items']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

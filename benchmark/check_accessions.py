"""The accession cross-check: every benchmark prompt's accession must
match the UniProt gene the checklists record.

Three identifier slips have happened in this project (1T4J listed as
P09467, 2PE0 as PTPN11, 1T4J as FBP1), so the check compares, for every
prompt, the accession in ``benchmark/benchmark_draft.json`` with the
accession and the gene name in the prompt's checklist entry
(``accession_<ACCESSION>``), and it also resolves the gene from the
UniProt REST API and compares the gene symbol.

    python benchmark/check_accessions.py
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DRAFT = REPO / "benchmark" / "benchmark_draft.json"
CHECKLISTS = REPO / "benchmark" / "checklists.json"
OFFLINE = "--offline" in sys.argv


def uniprot_gene(accession: str) -> tuple[str | None, str | None, str | None]:
    """(the gene symbol, the protein name, the organism) or Nones."""
    url = (
        "https://rest.uniprot.org/uniprotkb/"
        f"{accession}.json?fields=gene_names,protein_name,organism_name"
    )
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "accession-check/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return None, None, None
    gene = None
    for entry in data.get("genes") or []:
        if entry.get("geneName", {}).get("value"):
            gene = entry["geneName"]["value"]
            break
    name = None
    description = data.get("proteinDescription") or {}
    for block in description.get("recommendedName", {}), description.get("submissionNames", [{}])[0] if description.get("submissionNames") else {}:
        if block.get("fullName", {}).get("value"):
            name = block["fullName"]["value"]
            break
    organism = data.get("organism", {}).get("scientificName")
    return gene, name, organism


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    checklists = json.loads(CHECKLISTS.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in checklists["prompts"]}

    mismatches = []
    problems = []
    print(f"{'id':6s} {'draft':10s} {'checklist':10s} {'gene':10s} {'the checklist gene':22s} verdict")
    print("-" * 100)
    for prompt in draft:
        pid = prompt["id"]
        draft_accession = prompt.get("accession")
        entry = by_id.get(pid)
        if entry is None:
            problems.append(f"{pid}: no checklist entry")
            continue
        checklist_accession = entry.get("accession")
        gene = None
        name = None
        organism = None
        for item in entry.get("checklist", []):
            if item["key"].startswith("accession_"):
                value = item.get("value") or {}
                gene = value.get("gene")
                name = value.get("name")
                organism = value.get("organism")
                checklist_accession = item["key"].split("accession_", 1)[1]
                break
        verdict = "ok"
        if draft_accession != checklist_accession:
            verdict = "MISMATCH"
            mismatches.append(
                f"{pid}: the draft says {draft_accession}, the checklist says {checklist_accession}")
        if not OFFLINE:
            live_gene, live_name, live_organism = uniprot_gene(draft_accession)
            if live_gene and gene and live_gene.split()[0] != gene.split()[0]:
                verdict = "GENE MISMATCH"
                mismatches.append(
                    f"{pid}: the checklist gene is {gene}, UniProt says {live_gene}")
            if live_organism and organism and live_organism != organism:
                verdict = "ORGANISM MISMATCH"
                mismatches.append(
                    f"{pid}: the checklist organism is {organism}, UniProt says {live_organism}")
        print(f"{pid:6s} {str(draft_accession):10s} {str(checklist_accession):10s} "
              f"{str(gene):10s} {str(name)[:22]:22s} {verdict}")

    print()
    if mismatches:
        print(f"{len(mismatches)} MISMATCHES:")
        for line in mismatches:
            print("  " + line)
    else:
        print("no mismatches: every prompt's accession matches its checklist entry")
    if problems:
        print("problems:")
        for line in problems:
            print("  " + line)
    return 1 if (mismatches or problems) else 0


if __name__ == "__main__":
    raise SystemExit(main())

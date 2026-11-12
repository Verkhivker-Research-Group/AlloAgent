"""The ClinVar variant scan, with a small fixture of the release file.

A protein change is not unique in ClinVar: the pinned release holds 86
rows with "Gly12Asp" and the first of them is GJB4, not the KRAS of the
V03 prompt.  The scan therefore matches the gene of the prompt as well as
the protein change, and these cases pin that behaviour with a fixture that
reproduces the ordering of the release file (the GJB4 row comes first).
"""
from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "benchmark_validator", REPO / "benchmark" / "validate_benchmark.py")
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

HEADER = (
    "#AlleleID\tType\tName\tGeneID\tGeneSymbol\tHGNC_ID\tClinicalSignificance"
    "\tVariationID\tReviewStatus\tGermlineClassification\n"
)


def _row(allele_id: str, gene: str, change: str, significance: str) -> str:
    return "\t".join([
        allele_id, "single nucleotide variant",
        f"NM_004985.5({gene}):c.35G>A (p.{change})",
        "3", gene, "HGNC:6407", significance, "126183",
        "criteria provided, multiple submitters, no conflicts", "-",
    ]) + "\n"


FIXTURE_ROWS = (
    # the GJB4 row of Gly12Asp comes first in the release file
    _row("20046", "GJB4", "Gly12Asp", "Pathogenic"),
    _row("27621", "KRAS", "Gly12Asp", "Pathogenic/Likely pathogenic"),
    _row("27617", "KRAS", "Gly12Cys", "Likely pathogenic"),
    _row("27622", "KRAS", "Gly12Val", "Pathogenic"),
)


@pytest.fixture()
def clinvar_release(tmp_path: Path) -> Path:
    path = tmp_path / "variant_summary.txt.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(HEADER)
        handle.writelines(FIXTURE_ROWS)
    return path


def test_the_gene_aware_scan_picks_the_row_of_the_prompt_gene(clinvar_release: Path):
    """G12D of the KRAS prompt is 27621, not the GJB4 row that comes first."""
    found = validator.scan_clinvar(
        clinvar_release,
        {"G12D": "Gly12Asp", "G12C": "Gly12Cys"},
        {"G12D": "KRAS", "G12C": "KRAS"},
    )
    assert found["G12D"]["variation_id"] == "27621"
    assert found["G12D"]["gene"] == "KRAS"
    assert found["G12D"]["clinical_significance"] == "Pathogenic/Likely pathogenic"
    assert found["G12C"]["variation_id"] == "27617"


def test_the_change_alone_would_pick_the_wrong_row(clinvar_release: Path):
    """Without the gene the first row of the release file wins: GJB4."""
    found = validator.scan_clinvar(
        clinvar_release, {"G12D": "Gly12Asp"}, {})
    assert found == {}, "a variant without a gene must not be matched at all"


def test_a_gene_that_is_not_in_the_row_does_not_match(clinvar_release: Path):
    found = validator.scan_clinvar(
        clinvar_release, {"G12D": "Gly12Asp"}, {"G12D": "HRAS"})
    assert found == {}


def test_the_gene_of_a_variant_comes_from_the_uniprot_record():
    """The gene symbol is the one of the prompt's accession (PTPN11 for
    Q06124, whose prompt text says SHP2), because that is the symbol
    ClinVar uses."""
    draft = [
        {"id": "V01", "accession": "Q06124", "prompt": "For SHP2 (UniProt Q06124), ..."},
        {"id": "V03", "accession": "P01116", "prompt": "For KRAS (UniProt P01116), ..."},
        {"id": "S01", "accession": "P00519", "prompt": "not a variant prompt"},
    ]
    facts = {"uniprot": {"Q06124": {"gene": "PTPN11"}, "P01116": {"gene": "KRAS"}}}
    genes = validator.variant_prompt_genes(draft, facts)
    assert genes == {"E76K": "PTPN11", "D61Y": "PTPN11",
                     "G12C": "KRAS", "G12D": "KRAS", "G12V": "KRAS"}


def test_the_variant_prompts_are_the_ones_of_the_draft():
    draft = json.loads(
        (REPO / "benchmark" / "benchmark_draft.json").read_text(encoding="utf-8"))
    wanted = {variant for variants in validator.VARIANT_PROMPT_VARIANTS.values()
              for variant in variants}
    assert wanted == {"E76K", "D61Y", "E17K", "G12C", "G12D", "G12V", "T315I"}
    for prompt in draft:
        if prompt["id"] in validator.VARIANT_PROMPT_VARIANTS:
            assert prompt["accession"]

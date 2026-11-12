"""P32 allosteric_site_workflow: the criteria W1-W3 of
docs/2_allosteric_site_workflow_criteria.md.

The workflow must equal the direct call of each underlying tool, the
FRJ pocket must appear in the fpocket result for 1T4J, and the
ligand-contacts component must equal the direct get_ligand_contacts
call for 1T4J/FRJ and 1OPK/MYR.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest


def _live_rcsb() -> bool:
    try:
        import requests

        return requests.get("https://files.rcsb.org/download/1T4J.pdb", timeout=20).status_code == 200
    except Exception:
        return False


_LIVE = pytest.mark.skipif(not _live_rcsb(), reason="RCSB not reachable from this host")


def test_w1_1t4j_frj_pocket_and_contacts():
    """W1: the FRJ pocket appears in the fpocket result and the
    ligand-contacts component equals the direct call.

    The strict xfail that was here in the previous phase is removed:
    the fpocket wrapper now returns the per-pocket residues (the fix
    and its criteria are in docs/1_fpocket_criteria.md), so the
    overlap with the FRJ contact set is 8 - the independently computed
    maximum, reached by fpocket's pocket 11.
    """
    from biomni.tool.allosteric_site_workflow import allosteric_site_workflow
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    report = allosteric_site_workflow("1T4J", "A", ligand_id="FRJ")
    data = report["data"]
    assert "error" not in data, data.get("error")

    direct = get_ligand_contacts(pdb_id="1T4J", ligand_id="FRJ", chain="A")
    assert data["components"]["ligand_contacts"]["data"] == direct["data"], (
        "the workflow's ligand_contacts component must equal the direct call")
    assert [c["uniprot_number"] for c in direct["data"]["contacts"]] == [
        188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282]

    fpocket = data["components"]["fpocket"]
    assert fpocket["success"] is True, fpocket.get("error")
    assert data["overlap"]["fpocket_best_overlap"] == 8, (
        "the fpocket component's overlap with the FRJ contact set must be "
        f"8, got {data['overlap']['fpocket_best_overlap']}")
    assert all(pocket["residues"] for pocket in fpocket["data"]["pockets"]), (
        "every fpocket pocket must carry a non-empty residue list")


def test_w2_1opk_myr_contacts_and_component_errors():
    """W2: the 1OPK/MYR contacts equal the direct call and every
    component that is present carries success or an error."""
    from biomni.tool.allosteric_site_workflow import allosteric_site_workflow
    from biomni.tool.get_ligand_contacts import get_ligand_contacts

    report = allosteric_site_workflow("1OPK", "A", ligand_id="MYR")
    data = report["data"]
    direct = get_ligand_contacts(pdb_id="1OPK", ligand_id="MYR", chain="A")
    assert data["components"]["ligand_contacts"]["data"] == direct["data"]
    assert [c["uniprot_number"] for c in direct["data"]["contacts"]] == [
        340, 341, 344, 429, 433, 462, 502, 510]
    for name, component in data["components"].items():
        assert component.get("success") is True or component.get("error"), (
            f"the {name} component must carry success or an error, got {component}")


def test_w3_components_equal_the_direct_calls():
    """W3: the pocket components equal the direct calls of the same
    tools on the same structure."""
    from biomni.tool.allosteric_site_workflow import allosteric_site_workflow
    from biomni.tool.detect_pockets_p2rank import detect_pockets_p2rank

    report = allosteric_site_workflow("1T4J", "A", ligand_id="FRJ")
    data = report["data"]
    assert data["components"]["fpocket"]["success"] is True
    assert data["components"]["p2rank"]["success"] is True
    assert data["components"]["pocketminer"]["success"] is True
    assert data["components"]["normal_modes"]["success"] is True
    assert data["components"]["contact_network"]["success"] is True

    direct = detect_pockets_p2rank(pdb_path=_stripped_1t4j())
    assert len(data["components"]["p2rank"]["data"]["pockets"]) == len(
        direct["data"]["pockets"])
    for workflow_pocket, direct_pocket in zip(
        data["components"]["p2rank"]["data"]["pockets"], direct["data"]["pockets"]
    ):
        assert workflow_pocket["residues"] == direct_pocket["residues"]


def _stripped_1t4j() -> str:
    import tempfile
    import urllib.request

    with urllib.request.urlopen(
        "https://files.rcsb.org/download/1T4J.pdb", timeout=60
    ) as response:
        text = response.read().decode("utf-8", "replace")
    stripped = "\n".join(
        line for line in text.splitlines() if not line.startswith("HETATM")
    ) + "\n"
    handle = tempfile.NamedTemporaryFile("w", suffix=".pdb", delete=False, encoding="utf-8")
    handle.write(stripped)
    handle.close()
    return handle.name

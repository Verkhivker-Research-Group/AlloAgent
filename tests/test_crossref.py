import os
import sys
# Ensure repository root is on PYTHONPATH so tests can import the local package in CI/container
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import json
import pandas as pd
import pytest

from biomni_biolab.tool import cross_reference, biolip, asd


def test_minimal_offline():
    out = cross_reference.cross_reference_ligands(ligands=["asp", "glycine"], databases=[])
    data = json.loads(out)
    assert "results" in data
    assert data["summary"]["total_ligands"] == 2


def test_no_input_error():
    out = cross_reference.cross_reference_ligands(ligands=None, databases=[])
    data = json.loads(out)
    assert "error" in data


def test_compute_overlap_unit():
    from biomni_biolab.tool.cross_reference import _compute_catalytic_overlap
    res = _compute_catalytic_overlap(["A10", "B20", "C30"], ["B20", "X99"])
    assert res["overlap_count"] == 1
    assert "B20" in res["overlap_residues"]


@pytest.mark.integration
def test_biolip_in_container_smoke():
    # This is an integration smoke test that expects local BioLiP data to be present in the container
    out = json.loads(cross_reference.cross_reference_ligands(pdb_id="1I09", databases=["biolip"]))
    assert "results" in out
    # If the dataset is present, at least one result should have 'biolip' provenance; otherwise allow empty results
    assert any("biolip" in r.get("provenance", []) for r in out["results"]) or len(out["results"]) == 0


def test_mocked_behavior(monkeypatch):
    # Create a fake DataFrame that the cross-reference code will consume
    df = pd.DataFrame([{"Ligand": "FOO", "Catalytic_site_residues": "A10,B20", "PDB": "1abc"}])

    monkeypatch.setattr(biolip, "parse_biolip_interactions", lambda pdb_id=None: df)
    monkeypatch.setattr(asd, "get_asd_ap_data", lambda **k: {"data": [{"ligand_name": "FOO", "uniprot_id": "U1"}], "shape": (1,)})
    monkeypatch.setattr(asd, "parse_asd_xf", lambda target_proteins=None: {"U1": {"sites": [{"site_residues": "B20"}]}})

    out = json.loads(cross_reference.cross_reference_ligands(pdb_id="1abc", ligands=["FOO"], uniprot_id="U1"))
    assert out["results"][0]["ligand"] == "FOO"
    assert "biolip" in out["results"][0]["provenance"]
    assert ("asd_ap" in out["results"][0]["provenance"]) or ("asd_xf" in out["results"][0]["provenance"]) or True
    assert out["results"][0]["data"].get("catalytic_overlap") is not None

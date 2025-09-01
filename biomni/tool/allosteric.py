from database import query_uniprot, query_pdb
from biolip import fetch_protein_data, filter_ligands, enrich_ligand_data
from asd import parse_asd_xf, load_asd_ap, load_asd_dr

import logging
from typing import Dict, Any


def get_ligand_ids_from_protein(uniprot_id: str):
    """
    Retrieve ligands (with enrichment + provenance) for a given UniProt protein ID.
    Uses UniProt → PDB → BioLiP pipeline.
    """
    results = {
        "protein_id": uniprot_id,
        "ligands": []
    }

    try:
        # Step 1: Map UniProt → PDB
        uniprot_data = query_uniprot(uniprot_id)
        pdb_ids = uniprot_data.get("pdb_ids", [])

        for pdb_id in pdb_ids:
            # Step 2: BioLiP fetch ligands
            protein_data = fetch_protein_data(pdb_id=pdb_id)

            # Step 3: Filter ligands (keep non-catalytic / allosteric)
            filtered_ligands = filter_ligands(
                ligands=protein_data.get("ligands", []),
                exclude_catalytic=True,
                biological_relevance="allosteric"
            )

            # Step 4: Enrich each ligand
            for ligand in filtered_ligands:
                ligand_code = ligand.get("ligand_code")
                if not ligand_code:
                    continue

                enriched = enrich_ligand_data(ligand_code=ligand_code)

                results["ligands"].append({
                    "ligand_code": ligand_code,
                    "source_pdb": pdb_id,
                    "biolip_data": ligand,
                    "enriched_data": enriched,
                    "provenance": ["BioLiP", "PDB"]
                })

    except Exception as e:
        results["error"] = str(e)

    return results


def cross_reference_ligands(uniprot_id: str, ligands: list):
    """
    Cross-reference ligands against UniProt, PDB, and ASD.
    """
    results = {
        "protein_id": uniprot_id,
        "cross_references": []
    }

    try:
        # UniProt cross-links
        uniprot_data = query_uniprot(uniprot_id)

        # ASD data - direct function calls
        asd_experimental = parse_asd_xf(target_proteins=[uniprot_id])
        asd_predicted_sites = load_asd_ap(target_proteins=[uniprot_id])
        asd_all_modulators = load_asd_dr()  # Load all modulators for cross-referencing

        for ligand in ligands:
            ligand_code = ligand.get("ligand_code")

            cross_ref = {
                "ligand_code": ligand_code,
                "from_biolip": ligand,
                "cross_refs": {},
                "provenance": []
            }

            # Add UniProt refs
            if uniprot_data:
                cross_ref["cross_refs"]["uniprot"] = uniprot_data.get("ligand_links", {})
                cross_ref["provenance"].append("UniProt")

            # Add PDB confirmation
            pdb_info = query_pdb(ligand.get("source_pdb"))
            if pdb_info:
                cross_ref["cross_refs"]["pdb"] = pdb_info
                cross_ref["provenance"].append("PDB")

            # Add ASD allosteric annotation
            asd_match = None
            # Cross-reference ligand_code against ASD modulators
            for modulator_id, modulator_data in asd_all_modulators.items():
                # Check if ligand matches any ASD identifiers
                if (ligand_code in modulator_data.get('name', '') or
                    ligand_code in modulator_data.get('cas_id', '') or
                    ligand_code in modulator_data.get('drugbank_id', '')):
                    asd_match = modulator_data
                    break
            
            if asd_match or asd_experimental.get(uniprot_id) or asd_predicted_sites.get(uniprot_id):
                cross_ref["cross_refs"]["asd"] = {
                    "modulator_match": asd_match,
                    "experimental_sites": asd_experimental.get(uniprot_id, {}),
                    "predicted_sites": asd_predicted_sites.get(uniprot_id, [])
                }
                cross_ref["provenance"].append("ASD")

            results["cross_references"].append(cross_ref)

    except Exception as e:
        results["error"] = str(e)

    return results


def test_cross_reference_ligands(uniprot_id="P41240"):
    """
    Minimal test for cross_reference_ligands function.
    """
    print(f"Testing cross-reference for {uniprot_id}...")
    
    # Get ligands from protein
    ligand_data = get_ligand_ids_from_protein(uniprot_id)
    ligands = ligand_data.get('ligands', [])
    print(f"Found {len(ligands)} ligands")
    
    # Cross-reference ligands
    results = cross_reference_ligands(uniprot_id, ligands)
    
    # Print results
    print(f"Cross-references: {len(results.get('cross_references', []))}")
    for i, cross_ref in enumerate(results.get('cross_references', [])):
        asd_found = 'asd' in cross_ref['cross_refs']
        print(f"  {cross_ref['ligand_code']}: ASD match = {asd_found}")

test_cross_reference_ligands()







'''

def build_energy_landscape(protein_id: str) -> Dict[str, Any]:
    """
    Build a structured dataset for energy landscape theory in allostery.
    
    Combines conformational states (PDB), allosteric modulators (ASD),
    and molecular dynamics ensembles (MoDEL/Dynameomics).
    
    Args:
        protein_id (str): UniProt or PDB identifier of the protein.
        
    Returns:
        Dict[str, Any]: Structured JSON with provenance for citation.
    """
    landscape_data = {"protein_id": protein_id, "sources": {}}

    try:
        # Step 1: PDB conformations
        pdb_data = query_pdb(protein_id)
        landscape_data["sources"]["PDB"] = {
            "provenance": "RCSB Protein Data Bank",
            "conformations": pdb_data.get("conformations", []),
            "ligand_bound_states": pdb_data.get("ligand_states", []),
        }

        # Step 2: Allosteric modulators (ASD)
        asd_data = query_asd(protein_id)
        landscape_data["sources"]["ASD"] = {
            "provenance": "Allosteric Database (ASD)",
            "allosteric_sites": asd_data.get("sites", []),
            "modulators": asd_data.get("modulators", []),
        }

        # Step 3: Dynamics (MoDEL/Dynameomics)
        dynamics_data = query_dynamics(protein_id)
        landscape_data["sources"]["Dynamics"] = {
            "provenance": "MoDEL / Dynameomics",
            "trajectories": dynamics_data.get("trajectories", []),
            "states": dynamics_data.get("states", []),
        }

        # Integrate into a draft "energy landscape"
        landscape_data["energy_landscape"] = {
            "nodes": {
                "apo": pdb_data.get("apo_structures", []),
                "holo": pdb_data.get("holo_structures", []),
                "intermediates": dynamics_data.get("states", []),
            },
            "edges": dynamics_data.get("transitions", []),
            "perturbations": {
                "allosteric_ligands": asd_data.get("modulators", []),
                "binding_site_shifts": asd_data.get("sites", []),
            },
        }

    except Exception as e:
        logging.error(f"Error building energy landscape for {protein_id}: {e}")
        landscape_data["error"] = str(e)

    return landscape_data

    
'''




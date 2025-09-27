#!/usr/bin/env python3
"""
Minimal single-function tool for cross-referencing ligands between ASD and BioLiP databases.
Returns JSON-style string suitable for RAG/MCP pipelines.
"""

import json
import pickle
import pandas as pd
import xml.etree.ElementTree as ET
import os
from pathlib import Path
from biomni.tool.asd_index import asd_index

# Hard-coded paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/biomni_data")

ASD_XF_PATH = os.path.join(DATA_DIR, "asd/ASD_Release_202306_XF")
ASD_DR_PATH = os.path.join(DATA_DIR, "data_lake/ASD_Release_201909_DR.csv")
ASD_AP_PATH = os.path.join(DATA_DIR, "data_lake/ASD_Release_202306_AP.csv")
BIOLIP_PATH = os.path.join(DATA_DIR, "biolip/biolip.pkl")

def cross_reference_ligands():
    """
    Cross-references ligands between ASD and BioLiP databases.
    
    Returns:
        str: JSON-style string containing merged ligand data with fields:
             - ligand_name (from BioLiP)
             - binding_site_residues (from BioLiP) 
             - chain (from BioLiP)
             - pdb_id (from BioLiP)
             - catalytic_site_residues (from BioLiP)
             - protein_name (from BioLiP)
             - affinity (from BioLiP)
             - function (from ASD XML)
             - organism (from ASD XML)
             - allosteric_site (from ASD XML)
             - ligand_class (from ASD AP CSV)
             - uniprot_id (from ASD AP CSV)
             - drug_info (from ASD DR CSV)
             - catalytic_site_overlap (computed from BioLiP + ASD XML)
    """
    
    try:
        # Load BioLiP data
        with open(BIOLIP_PATH, 'rb') as f:
            biolip_data = pickle.load(f)
        
        # Load ASD CSV files
        asd_ap_df = pd.read_csv(ASD_AP_PATH)
        asd_dr_df = pd.read_csv(ASD_DR_PATH)
        
        # Initialize result list
        merged_results = []
        
        # Process BioLiP interactions
        for entry in biolip_data:
            # Extract BioLiP fields
            biolip_record = {
                "ligand_name": entry.get("ligand_name", ""),
                "binding_site_residues": entry.get("binding_site_residues", []),
                "chain": entry.get("chain", ""),
                "pdb_id": entry.get("pdb_id", ""),
                "catalytic_site_residues": entry.get("catalytic_site_residues", []),
                "protein_name": entry.get("protein_name", ""),
                "affinity": entry.get("affinity", ""),
            }
            
            # Get PDB ID for matching
            pdb_id = biolip_record["pdb_id"]
            
            # Find matching UniProt ID from ASD AP CSV
            uniprot_match = asd_ap_df[asd_ap_df['pdb_id'] == pdb_id] if 'pdb_id' in asd_ap_df.columns else pd.DataFrame()
            
            if not uniprot_match.empty:
                uniprot_id = uniprot_match.iloc[0]['uniprot_id'] if 'uniprot_id' in uniprot_match.columns else ""
                ligand_class = uniprot_match.iloc[0]['ligand_class'] if 'ligand_class' in uniprot_match.columns else ""
            else:
                uniprot_id = ""
                ligand_class = ""
            
            # Find drug info from ASD DR CSV
            drug_info = ""
            if uniprot_id:
                drug_match = asd_dr_df[asd_dr_df['uniprot_id'] == uniprot_id] if 'uniprot_id' in asd_dr_df.columns else pd.DataFrame()
                if not drug_match.empty and 'drug_info' in drug_match.columns:
                    drug_info = drug_match.iloc[0]['drug_info']
            
            # Load ASD XML data
            asd_xml_data = _load_asd_xml_data(uniprot_id)
            
            # Compute catalytic site overlap
            catalytic_overlap = _compute_catalytic_overlap(
                biolip_record["catalytic_site_residues"],
                asd_xml_data.get("allosteric_site", [])
            )
            
            # Merge all data
            merged_record = {
                **biolip_record,
                "function": asd_xml_data.get("function", ""),
                "organism": asd_xml_data.get("organism", ""),
                "allosteric_site": asd_xml_data.get("allosteric_site", []),
                "ligand_class": ligand_class,
                "uniprot_id": uniprot_id,
                "drug_info": drug_info,
                "catalytic_site_overlap": catalytic_overlap
            }
            
            merged_results.append(merged_record)
        
        # Return JSON string
        return json.dumps(merged_results, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_result = [{"error": f"Failed to cross-reference ligands: {str(e)}"}]
        return json.dumps(error_result, indent=2)


def _load_asd_xml_data(uniprot_id):
    """
    Load ASD XML data for given UniProt ID.
    
    Args:
        uniprot_id (str): UniProt identifier
        
    Returns:
        dict: Dictionary containing function, organism, and allosteric_site
    """
    if not uniprot_id:
        return {"function": "", "organism": "", "allosteric_site": []}
    
    xml_file = Path(ASD_XF_PATH) / f"{asd_index.get(uniprot_id)}.xml"
    
    if not xml_file.exists():
        return {"function": "", "organism": "", "allosteric_site": []}
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extract function
        function_elem = root.find(".//function")
        function = function_elem.text if function_elem is not None else ""
        
        # Extract organism
        organism_elem = root.find(".//organism")
        organism = organism_elem.text if organism_elem is not None else ""
        
        # Extract allosteric sites
        allosteric_sites = []
        for site in root.findall(".//allosteric_site"):
            residues = []
            for residue in site.findall(".//residue"):
                if residue.text:
                    residues.append(residue.text.strip())
            if residues:
                allosteric_sites.extend(residues)
        
        return {
            "function": function,
            "organism": organism,
            "allosteric_site": allosteric_sites
        }
        
    except ET.ParseError:
        return {"function": "", "organism": "", "allosteric_site": []}


def _compute_catalytic_overlap(catalytic_residues, allosteric_residues):
    """
    Compute overlap between catalytic site residues and allosteric site residues.
    
    Args:
        catalytic_residues (list): List of catalytic site residues from BioLiP
        allosteric_residues (list): List of allosteric site residues from ASD XML
        
    Returns:
        dict: Dictionary containing overlap information
    """
    if not catalytic_residues or not allosteric_residues:
        return {"overlap_count": 0, "overlap_residues": [], "overlap_percentage": 0.0}
    
    # Convert to sets for intersection
    cat_set = set(str(res).strip() for res in catalytic_residues if res)
    allo_set = set(str(res).strip() for res in allosteric_residues if res)
    
    # Find overlap
    overlap = cat_set.intersection(allo_set)
    overlap_count = len(overlap)
    overlap_percentage = (overlap_count / len(cat_set)) * 100 if cat_set else 0.0
    
    return {
        "overlap_count": overlap_count,
        "overlap_residues": list(overlap),
        "overlap_percentage": round(overlap_percentage, 2)
    }


if __name__ == "__main__":
    # Example usage
    result = cross_reference_ligands("1I09", "P49841")
    print(result)
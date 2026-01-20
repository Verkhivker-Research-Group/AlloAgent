#from biomni_biolab.tool.database import query_uniprot, query_pdb
from biomni_biolab.tool.biolip import parse_biolip_interactions, biolip_ligands
from biomni_biolab.tool.asd import parse_asd_xf, get_asd_ap_data, get_asd_dr_data


from chembl_webresource_client.new_client import new_client
import pubchempy as pcp
import pandas as pd
import json
import logging
from typing import Dict, Any
import os
from typing import Dict, List, Tuple, Any, Optional
import re
import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from collections import Counter, defaultdict
import numpy as np

load_dotenv()



# VERIFIED
def biolip_ligands(pdb_id, chain=None):
    """
    Get ligand IDs for a given PDB ID and optionally chain.
    """
    interactions = parse_biolip_interactions(pdb_id, chain)
    print(f"Interactions: {interactions}")
    return interactions['Ligand'].unique().tolist()




def pdb_to_uniprot(pdb_id: str) -> dict:
    pdb_id = pdb_id.strip().upper()
    if len(pdb_id) != 4:
        raise ValueError("PDB ID must be 4 characters")

    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb_id}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # API returns lowercase key (e.g., "1tim")
        entry = data.get(pdb_id.lower()) or data.get(pdb_id.upper())
        if not entry or "UniProt" not in entry:
            return {}

        result = {}
        for uniprot, details in entry["UniProt"].items():
            for mapping in details.get("mappings", []):
                chain = mapping.get("chain_id")
                if chain:
                    chain = chain.upper()
                    result.setdefault(chain, []).append(uniprot)
        return result

    except Exception:
        return {}


def uniprot_to_pdb(uniprot_id: str) -> list:
    uniprot_id = uniprot_id.strip().upper()
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/all_isoforms/{uniprot_id}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        entry = data.get(uniprot_id)
        if not entry or "PDB" not in entry:
            return []

        pdb_ids = list(entry["PDB"].keys())
        return sorted(set(p.upper() for p in pdb_ids if len(p) == 4))

    except Exception:
        return []




def cross_reference_ligands_chembl_pubchem(uniprot_id: str, ligands: list, detail_level: str = "slim"):
    """
    Cross-reference ligands against ChEMBL + PubChem and return a structured output.
    
    Args:
        uniprot_id (str): UniProt identifier for the target protein.
        ligands (list): List of dicts with ligand metadata (e.g., {"ligand_name": "Gefitinib"}).
        detail_level (str): "slim" for cleaned output, "full" for raw ChEMBL/PubChem dumps.
    """
    molecule = new_client.molecule
    results = {"protein_id": uniprot_id, "ligands": []}

    for ligand in ligands:
        ligand_name = ligand.get("ligand_name")
        cross_ref = {"name": ligand_name}

        try:
            # --- ChEMBL query ---
            chembl_match = molecule.filter(pref_name__icontains=ligand_name)
            if chembl_match:
                chembl_data = chembl_match[0]  # take best match
                if detail_level == "slim":
                    cross_ref.update({
                        "chembl_id": chembl_data.get("molecule_chembl_id"),
                        "synonyms": chembl_data.get("molecule_synonyms", [])[:3],  # top 3 synonyms
                        "properties": {
                            "formula": chembl_data.get("molecule_properties", {}).get("full_molformula"),
                            "molecular_weight": chembl_data.get("molecule_properties", {}).get("full_mwt"),
                            "alogp": chembl_data.get("molecule_properties", {}).get("alogp"),
                            "psa": chembl_data.get("molecule_properties", {}).get("psa")
                        },
                        "structure": {
                            "smiles": chembl_data.get("molecule_structures", {}).get("canonical_smiles"),
                            "inchi_key": chembl_data.get("molecule_structures", {}).get("standard_inchi_key")
                        },
                        "classification": {
                            "atc": chembl_data.get("atc_classifications", []),
                            "usan_stem": chembl_data.get("usan_stem")
                        },
                        "approval": {
                            "first_approval": chembl_data.get("first_approval"),
                            "max_phase": chembl_data.get("max_phase")
                        }
                    })
                else:
                    cross_ref["chembl_raw"] = chembl_data

            # --- PubChem query ---
            pubchem_matches = pcp.get_compounds(ligand_name, "name")
            if pubchem_matches:
                compound = pubchem_matches[0]
                if detail_level == "slim":
                    cross_ref["pubchem_cid"] = compound.cid
                else:
                    cross_ref["pubchem_raw"] = compound.to_dict()

        except Exception as e:
            cross_ref["error"] = str(e)

        results["ligands"].append(cross_ref)

    return results



def map_covalent_probes_to_allosteric(uniprot_id: str,
                                      dataset_path: str = "./data/biomni_data/data_lake/CovInDB_All.csv"
                                     ) -> pd.DataFrame:
    """
    Steps:
    1. Load and filter by UniProt ID
    2. Extract site information with better parsing
    3. Use protein family-specific knowledge to identify catalytic/orthosteric sites
    4. Apply intelligent filtering based on residue patterns and context
    """

    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"Dataset not found at {dataset_path}")
        return pd.DataFrame()

    df = df[df["Target"].str.contains(uniprot_id, case=False, na=False)]
    if df.empty:
        print(f"No entries found for UniProt {uniprot_id}")
        return df

    cols = [
        "Inhibitor_Name", "Target_Name", "Target_Gene", "Target", 
        "Site", "War_head", "Reaction_type", "Method", "Assay", "Reference"
    ]
    available_cols = [col for col in cols if col in df.columns]
    subset = df[available_cols].copy()

    def parse_site(site_str):
        """Parse site string into individual residues"""
        if pd.isna(site_str):
            return []
        
        site_str = str(site_str).strip()
        if site_str in ["NT", "N-term", "N-terminal"]:
            return ["NT"]
        if "cofactor" in site_str.lower() or "enzyme" in site_str.lower():
            return ["COFACTOR"]
        
        sites = []
        for part in re.split(r'[，,;]', site_str):
            part = part.strip()
            if not part:
                continue
            match = re.match(r'([A-Z]+)[-\s]*(\d+)', part)
            if match:
                residue, number = match.groups()
                sites.append(f"{residue}-{number}")
            elif part in ["NT", "N-term"]:
                sites.append("NT")
            else:
                sites.append(part)
        return sites

    def is_orthosteric_site(site: str, target_gene: str) -> bool:
        """Determine if a site is likely orthosteric based on protein family knowledge"""
        if site in ["NT", "COFACTOR"]:
            return False
        
        match = re.match(r'([A-Z]+)-(\d+)', site)
        if not match:
            return False
        
        residue, number = match.groups()
        number = int(number)
        

        orthosteric_sites = {
            'EGFR': ['CYS-797'],  
            'KRAS': ['CYS-12'],   
            'BTK': ['CYS-481'],   
            'JAK': ['CYS-909'],   
            
            'SERINE_PROTEASE': ['SER-195', 'HIS-57', 'ASP-102'],
            'CYSTEINE_PROTEASE': ['CYS-25', 'HIS-159'],
            
   
            'GENERAL_CATALYTIC': [
                'CYS-25', 'CYS-145', 'SER-195', 'HIS-41', 'HIS-57', 
                'ASP-102', 'LYS-72', 'ASP-189', 'SER-221', 'CYS-481'
            ]
        }
        
        target_upper = str(target_gene).upper() if pd.notna(target_gene) else ""

        for gene_pattern, sites in orthosteric_sites.items():
            if gene_pattern in target_upper:
                if site in sites:
                    return True

        if site in orthosteric_sites['GENERAL_CATALYTIC']:
            return True

        if residue in ['SER', 'CYS', 'HIS', 'ASP', 'GLU', 'LYS']:
            return True
        
        return False

    def is_allosteric_candidate(site_str, target_gene):
        """Determine if site is a potential allosteric candidate"""
        sites = parse_site(site_str)
        if not sites:
            return True
        
        for site in sites:
            if is_orthosteric_site(site, target_gene):
                return False
        
        allosteric_indicators = [
            'NT', 'COFACTOR', 
            'CYS-', 'SER-', 'LYS-', 
        ]
        
        for site in sites:
            if any(indicator in site for indicator in allosteric_indicators):
                return True
        
        return True

    # classify
    subset["Parsed_Sites"] = subset["Site"].apply(parse_site)
    subset["Allosteric_Candidate"] = subset.apply(
        lambda row: is_allosteric_candidate(row["Site"], row.get("Target_Gene", "")), 
        axis=1
    )
    
    subset["Site_Count"] = subset["Parsed_Sites"].apply(len)
    
    def get_confidence_level(sites, is_allosteric):
        if not is_allosteric:
            return "High (Orthosteric)"
        
        site_str = '|'.join(sites) if sites else str(sites)
        
        # high confidence allosteric indicators
        high_conf_indicators = ['NT', 'COFACTOR', 'CYS-1', 'CYS-2']
        if any(indicator in site_str for indicator in high_conf_indicators):
            return "High (Allosteric)"
        
        # medium confidence allosteric indicators
        medium_conf_indicators = ['CYS-', 'SER-', 'LYS-']
        if any(indicator in site_str for indicator in medium_conf_indicators):
            return "Medium (Allosteric)"
        
        return "Low (Investigate)"

    subset["Confidence"] = subset.apply(
        lambda row: get_confidence_level(row["Parsed_Sites"], row["Allosteric_Candidate"]), 
        axis=1
    )

    return subset.reset_index(drop=True)


def analyze_site_patterns(df: pd.DataFrame) -> Dict:
    """
    Analyze site patterns in the dataset to help refine classification.
    """
    from collections import Counter
    
    all_sites = []
    for sites in df.get("Parsed_Sites", []):
        all_sites.extend(sites)
    
    site_counter = Counter(all_sites)
    
    # finds most common sites
    common_sites = site_counter.most_common(20)
    
    # analyzes data extracted by residue type
    residue_counter = Counter()
    for site in all_sites:
        if '-' in site:
            residue = site.split('-')[0]
            residue_counter[residue] += 1
    
    return {
        "total_unique_sites": len(site_counter),
        "most_common_sites": common_sites,
        "residue_distribution": residue_counter.most_common(),
        "total_entries": len(df)
    }

# STINGAllo
def fetch_allosteric_residue_potential(pdb_id: str, chain_id: str) -> dict:
    url = "https://stingallo.cbi.cnptia.embrapa.br/api/afrs"
    params = {"pdb_id": pdb_id, "chain_id": chain_id}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log or handle error as needed in the agent system
        print(f"API request failed: {e}")
        return {}

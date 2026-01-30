import pandas as pd
import xml.etree.ElementTree as ET
import os
import glob
from collections import Counter
from typing import Dict, List, Any, Optional
import logging

from biomni_biolab.tool.asd_index import asd_index

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/biomni_data")

ASD_XF_PATH = os.path.join(DATA_DIR, "asd/ASD_Release_202306_XF")
ASD_2D_PATH = os.path.join(DATA_DIR, "asd/ASD_Release_202306_2D")
ASD_3D_PATH = os.path.join(DATA_DIR, "asd/ASD_Release_202306_3D")
ASD_AM_PATH = os.path.join(DATA_DIR, "data_lake/ASD_Release_201909_AM.csv")
ASD_DR_PATH = os.path.join(DATA_DIR, "data_lake/ASD_Release_201909_DR.csv")
ASD_AP_PATH = os.path.join(DATA_DIR, "data_lake/ASD_Release_202306_AP.csv")

# number of proteins that overlap between XF and AP datasets
#df = pd.read_csv(ASD_AP_PATH)
#print(df[df["uniprot_id"].isin(asd_index.keys())].drop_duplicates(subset="uniprot_id").shape)


def parse_asd_xf(
    target_proteins: List[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Parse ASD_Release_202306_XF XML files to extract
    protein → allosteric site → modulator mapping.

    Args:
        target_proteins: List of specific protein IDs to extract.
                         If None, loads all in the index.

    Returns:
        Dict: {protein_id: {"sites": [...], "modulators": [...]} }
    """
    result = {}
    target_set = set(target_proteins) if target_proteins else set(asd_index.keys())

    for protein_id in target_set:
        xml_filename = asd_index.get(protein_id)
        if not xml_filename:
            # Skip if protein not in index
            print("Not in asd_index")
            continue
        xml_file = os.path.join(ASD_XF_PATH, xml_filename + ".xml")
        print(xml_file)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            _parse_xml_content(root, result, {protein_id})
        except Exception as e:
            print(f"Error parsing {xml_file} for {protein_id}: {e}")

    return result

def _parse_xml_content(root: ET.Element, result: Dict, target_proteins: set = None) -> None:
    """Parse ASD XF-style XML content for protein → site → modulator mapping."""
    
    # Grab UniProt ID (acts as protein_id here)
    protein_id = root.findtext("UniProt_ID")
    if not protein_id:
        return
    
    # Skip if we only want certain proteins
    if target_proteins is not None and protein_id not in target_proteins:
        return
    
    # --- Extract Allosteric Sites ---
    sites = []
    for site in root.findall(".//Allosteric_Site"):
        site_info = {
            "pdb_id": site.findtext("Allosteric_PDB"),
            "site_residues": site.findtext("Allosteric_Site_Residue"),
            "feature": site.findtext("Modulator_Feature"),
            "function": site.findtext("Function"),
            "pdb_site": site.findtext("PDB_Site")
        }
        sites.append(site_info)
    
    # --- Extract Modulators ---
    modulators = []
    for mod in root.findall(".//Modulator"):
        mod_info = {
            "modulator_id": mod.findtext("ASD_ID"),
            "feature": mod.findtext("Modulator_Feature"),
            "drugbank": mod.findtext("drugbank__id") or "No"
        }
        modulators.append(mod_info)
    
    # Store result
    result[protein_id] = {
        "sites": sites,
        "modulators": modulators
    }


def load_asd_2d(protein_ids: List[str], modulator_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load 2D chemical structures from ASD .mol files for given protein IDs and optional modulator IDs.

    Args:
        protein_ids: List of protein IDs to look up in asd_index.
        modulator_ids: Optional list of specific modulator ASD IDs to filter.

    Returns:
        Dict mapping modulator ASD ID -> parsed 2D info (name, formula, atom_count, bond_count, smiles)
    """
    result = {}
    target_mods = set(modulator_ids) if modulator_ids else None

    for protein_id in protein_ids:
        # Lookup protein metadata in asd_index
        xml_filename = asd_index.get(protein_id)
        
        if not xml_filename or not os.path.exists(xml_filename):
            logger.warning(f"XML file not found for protein {protein_id}: {xml_filename}")
            continue
        xml_path = os.path.join(ASD_XF_PATH, xml_filename + ".xml")
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Iterate over all allosteric sites in XML
            for site in root.findall('.//Allosteric_Site'):
                mod_id_elem = site.find('Modulator_ASD_ID')
                if mod_id_elem is None or not mod_id_elem.text:
                    continue
                mod_id = mod_id_elem.text

                # Skip if not in target modulator_ids set
                if target_mods and mod_id not in target_mods:
                    continue

                # Construct .mol file path
                mol_path = os.path.join(ASD_2D_PATH, f"{mod_id}.mol")
                if not os.path.exists(mol_path):
                    logger.warning(f"MOL file not found for {mod_id}: {mol_path}")
                    continue

                # Parse MOL file
                try:
                    with open(mol_path, 'r') as f:
                        mol_data = _parse_mol_file(f.read())
                        if mol_data:
                            result[mod_id] = mol_data
                except Exception as e:
                    logger.error(f"Failed to read or parse MOL file for {mod_id}: {e}")

        except Exception as e:
            logger.error(f"Failed to parse protein XML {xml_path}: {e}")

    return result


def _parse_mol_file(mol_content: str) -> Optional[Dict[str, Any]]:
    """Parse MOL file content to extract chemical information."""
    lines = mol_content.strip().split('\n')
    if len(lines) < 4:
        return None

    try:
        name = lines[0].strip()
        counts_line = lines[3].split()
        atom_count = int(counts_line[0]) if len(counts_line) >= 1 else 0
        bond_count = int(counts_line[1]) if len(counts_line) >= 2 else 0

        atoms = []
        for i in range(4, min(4 + atom_count, len(lines))):
            atom_line = lines[i].split()
            if len(atom_line) >= 4:
                atoms.append(atom_line[3])  # Element symbol

        atom_counts = Counter(atoms)
        formula = ''.join([f"{atom}{count if count > 1 else ''}" 
                          for atom, count in sorted(atom_counts.items())])

        return {
            'name': name,
            'formula': formula,
            'atom_count': atom_count,
            'bond_count': bond_count,
            'smiles': None  # can generate with RDKit later
        }

    except Exception as e:
        logger.warning(f"Error parsing MOL content: {e}")
        return None


def load_asd_3d(protein_ids: List[str], modulator_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load 3D chemical structures from ASD MOL2 files for given protein IDs and optional modulator IDs.

    Args:
        protein_ids: List of protein IDs to look up in asd_index (values are XML file paths).
        modulator_ids: Optional list of specific modulator ASD IDs to filter.

    Returns:
        Dict mapping modulator ASD ID -> parsed 3D info (atoms, coordinates, bonds, counts)
    """
    result = {}
    target_mods = set(modulator_ids) if modulator_ids else None

    for protein_id in protein_ids:
        xml_filename = asd_index.get(protein_id)
        
        if not xml_filename or not os.path.exists(xml_filename):
            logger.warning(f"XML file not found for protein {protein_id}: {xml_filename}")
            continue
        xml_path = os.path.join(ASD_XF_PATH, xml_filename + ".xml")
        
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Iterate over all allosteric sites
            for site in root.findall('.//Allosteric_Site'):
                mod_id_elem = site.find('Modulator_ASD_ID')
                if mod_id_elem is None or not mod_id_elem.text:
                    continue  # skip sites with missing or empty ASD ID
                mod_id = mod_id_elem.text.strip()

                # Skip if not in target modulator_ids set
                if target_mods and mod_id not in target_mods:
                    continue

                # Construct .mol2 file path
                mol2_path = os.path.join(ASD_3D_PATH, f"{mod_id}.mol2")
                if not os.path.exists(mol2_path):
                    logger.warning(f"MOL2 file not found for {mod_id}: {mol2_path}")
                    continue

                # Parse MOL2 file
                try:
                    with open(mol2_path, 'r') as f:
                        mol2_data = _parse_mol2_file(f.read())
                        if mol2_data:
                            result[mod_id] = mol2_data
                except Exception as e:
                    logger.error(f"Failed to read or parse MOL2 file for {mod_id}: {e}")

        except Exception as e:
            logger.error(f"Failed to parse protein XML {xml_path}: {e}")

    return result


def _parse_mol2_file(mol2_content: str) -> Optional[Dict[str, Any]]:
    """Parse MOL2 file content to extract 3D coordinates and atom information."""
    lines = mol2_content.strip().split('\n')
    
    atoms = []
    coordinates = []
    bonds = []
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('@<TRIPOS>'):
            current_section = line[9:]  # Remove '@<TRIPOS>'
            continue
            
        if current_section == 'ATOM' and line and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 6:
                atom_id = parts[0]
                atom_name = parts[1]
                x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                atom_type = parts[5]
                
                atoms.append({
                    'id': atom_id,
                    'name': atom_name,
                    'type': atom_type
                })
                coordinates.append([x, y, z])
                
        elif current_section == 'BOND' and line and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 4:
                bond_id = parts[0]
                atom1 = parts[1]
                atom2 = parts[2]
                bond_type = parts[3]
                
                bonds.append({
                    'id': bond_id,
                    'atom1': atom1,
                    'atom2': atom2,
                    'type': bond_type
                })
    
    if not atoms:
        return None
        
    return {
        'atoms': atoms,
        'coordinates': coordinates,
        'bonds': bonds,
        'atom_count': len(atoms),
        'bond_count': len(bonds)
    }




import pandas as pd
import xml.etree.ElementTree as ET
import os
import glob
from collections import Counter
from typing import Dict, List, Any, Optional
import logging

from asd_index import asd_index

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hard-coded file paths
ASD_XF_PATH = "../../data/biomni_data/asd/ASD_Release_202306_XF"  # XML files directory
ASD_2D_PATH = "../../data/biomni_data/asd/ASD_Release_202306_2D"  # MOL files directory  
ASD_3D_PATH = "../../data/biomni_data/asd/ASD_Release_202306_3D"  # MOL2 files directory
ASD_AM_PATH = "../../data/biomni_data/data_lake/ASD_Release_201909_AM.csv"  # Mutation CSV
ASD_DR_PATH = "../../data/biomni_data/data_lake/ASD_Release_201909_DR.csv"  # Drug CSV
ASD_AP_PATH = "../../data/biomni_data/data_lake/ASD_Release_202306_AP.csv"  # Predicted sites CSV

def parse_asd_xf(
    target_proteins: Optional[List[str]] = None
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
        xml_file = asd_index.get(protein_id)
        if not xml_file:
            # Skip if protein not in index
            print("Not in asd_index")
            continue

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
        xml_path = asd_index.get(protein_id)
        if not xml_path or not os.path.exists(xml_path):
            logger.warning(f"XML file not found for protein {protein_id}: {xml_path}")
            continue

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
        xml_path = asd_index.get(protein_id)
        if not xml_path or not os.path.exists(xml_path):
            logger.warning(f"XML file not found for protein {protein_id}: {xml_path}")
            continue

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

def load_asd_am(target_uniprot_ids: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load allosteric mutation data from ASD_Release_201909_AM.csv filtered by UniProt IDs.
    
    Args:
        target_uniprot_ids: List of UniProt IDs to load. If None, loads all.
        
    Returns:
        Dict: {uniprot_id: [{"mutation": ..., "effect": ...}, ...]}
    """
    result = {}
    target_set = set([uid.strip().upper() for uid in target_uniprot_ids]) if target_uniprot_ids else None

    try:
        df = pd.read_csv(ASD_AM_PATH)
        
        if 'uniprot_id' not in df.columns:
            logger.warning(f"No uniprot_id column found in {ASD_AM_PATH}")
            return result

        # Normalize CSV IDs
        df['uniprot_id'] = df['uniprot_id'].astype(str).str.strip().str.upper()

        # Filter for target UniProt IDs if provided
        if target_set is not None:
            df = df[df['uniprot_id'].isin(target_set)]

        # Group by UniProt ID
        for uniprot_id, group in df.groupby('uniprot_id'):
            mutations = []
            for _, row in group.iterrows():
                mutations.append({
                    'mutation': row.get('mut_info', ''),
                    'effect': row.get('phenotype', ''),
                    'position': row.get('mut_site', ''),
                    'wild_type': '',  # can be filled if available
                    'mutant': '',     # can be filled if available
                    'experimental_method': '',  # empty if not in CSV
                    'reference': row.get('pdb_id', '')  # using PDB ID as reference
                })
            result[uniprot_id] = mutations

    except Exception as e:
        logger.error(f"Error loading mutation data: {e}")

    return result





def load_asd_dr(target_modulators: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load allosteric drug/modulator info with expanded target/activity information.
    
    Args:
        target_modulators: List of specific modulator IDs to load. If None, loads all.
        
    Returns:
        Dict: {modulator_id: {"name": ..., "targets": [...], "activities": [...]}}
    """
    result = {}
    target_set = set(target_modulators) if target_modulators else None
    
    try:
        df = pd.read_csv(ASD_DR_PATH)
        
        modulator_col = 'modulator_serial'
        
        if modulator_col not in df.columns:
            logger.warning(f"Modulator identifier column '{modulator_col}' not found in {ASD_DR_PATH}")
            logger.info(f"Available columns: {list(df.columns)}")
            return result
        
        # Filter dataframe first if we have target modulators
        if target_set is not None:
            df = df[df[modulator_col].astype(str).isin(target_set)]
            
        for _, row in df.iterrows():
            modulator_id = str(row[modulator_col])
            
            # Parse semicolon-separated values
            activities = []
            if pd.notna(row.get('mod_feature', '')):
                activities = [act.strip() for act in str(row['mod_feature']).split(';')]
            
            targets = []
            if pd.notna(row.get('target_name', '')):
                targets = [tgt.strip() for tgt in str(row['target_name']).split(';')]
            
            target_ids = []
            if pd.notna(row.get('target_id', '')):
                target_ids = [tid.strip() for tid in str(row['target_id']).split(';')]
            
            # Create target-activity pairs
            target_info = []
            max_len = max(len(targets), len(activities), len(target_ids))
            for i in range(max_len):
                target_info.append({
                    'name': targets[i] if i < len(targets) else '',
                    'id': target_ids[i] if i < len(target_ids) else '',
                    'activity': activities[i] if i < len(activities) else ''
                })
            
            result[modulator_id] = {
                'name': str(row.get('drug_all_name', '')),
                'type': 'Drug',
                'primary_activity': activities[0] if activities else '',
                'all_activities': activities,
                'primary_target': targets[0] if targets else '',
                'all_targets': targets,
                'target_info': target_info,
                'phase': str(row.get('highest_phase', '')),
                'disease_condition': str(row.get('disease_condition', '')),
                'formula': str(row.get('formula', '')),
                'smiles': str(row.get('tr_smiles', '')),
                'cas_id': str(row.get('cas_id', '')),
                'drugbank_id': str(row.get('drugbank_id', '')),
                'pubmed_id': str(row.get('pubmed_id', '')),
                'reference': str(row.get('ref_title', ''))
            }
            
    except Exception as e:
        logger.error(f"Error loading drug data: {e}")
        
    return result




def load_asd_ap(target_proteins: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load predicted allosteric sites with detailed site grouping by PDB structure.
    
    Args:
        target_proteins: List of specific protein IDs to load. If None, loads all.
        
    Returns:
        Dict: {protein_id: [{"site": ..., "confidence": ...}, ...]}
    """
    result = {}
    target_set = set(target_proteins) if target_proteins else None
    
    try:
        df = pd.read_csv(ASD_AP_PATH)
        
        protein_col = 'uniprot_id'
        
        if protein_col not in df.columns:
            logger.warning(f"Protein identifier column '{protein_col}' not found in {ASD_AP_PATH}")
            logger.info(f"Available columns: {list(df.columns)}")
            return result
        
        # Filter dataframe first if we have target proteins
        if target_set is not None:
            df = df[df[protein_col].astype(str).isin(target_set)]
            
        for protein_id, group in df.groupby(protein_col):
            sites = []
            
            # Group by PDB ID to create separate sites for each structure
            for pdb_id, pdb_group in group.groupby('pdb_id'):
                for idx, row in pdb_group.iterrows():
                    # Parse residue information
                    residues_raw = str(row.get('site_residue', ''))
                    residues_parsed = []
                    residues_summary = []
                    
                    if pd.notna(row.get('site_residue', '')) and residues_raw != 'nan':
                        residue_parts = [part.strip() for part in residues_raw.split(';')]
                        for residue_part in residue_parts:
                            if residue_part:
                                try:
                                    res_info = residue_part.split(',')
                                    if len(res_info) >= 4:
                                        parsed_res = {
                                            'name_full': res_info[0].strip(),
                                            'name_short': res_info[1].strip(), 
                                            'position': res_info[2].strip(),
                                            'chain': res_info[3].strip()
                                        }
                                        residues_parsed.append(parsed_res)
                                        residues_summary.append(f"{res_info[1].strip()}{res_info[2].strip()}:{res_info[3].strip()}")
                                except:
                                    continue
                    
                    site_data = {
                        'site': f"{pdb_id}_pocket",
                        'confidence': float(row.get('score', 0.0)),
                        'residues': '; '.join(residues_summary),  # Formatted residue list
                        'residues_raw': residues_raw,  # Original raw string
                        'residues_parsed': residues_parsed,  # Structured residue data
                        'prediction_method': 'ASD_cavity_detection',
                        'score': float(row.get('score', 0.0)),
                        'cavity_volume': float(row.get('pocket_volume', 0.0)),
                        'druggability': float(row.get('drug_score', 0.0)),
                        'pdb_id': str(pdb_id),
                        'polar_sasa': float(row.get('polar_sasa', 0.0)),
                        'total_sasa': float(row.get('total_sasa', 0.0)),
                        'protein_class': str(row.get('protein_class_2', '')),
                        'gene_name': str(row.get('gene_name', '')),
                        'uniprot_entry': str(row.get('uniprot_entry', '')),
                        'has_substrate_site': str(row.get('no_substrate_site', '')).lower() != 'yes',
                        'residue_count': len(residues_parsed)
                    }
                    sites.append(site_data)
                
            result[str(protein_id)] = sites
            
    except Exception as e:
        logger.error(f"Error loading predicted sites: {e}")
        
    return result


def test_asd_functions():
    """Minimal test function for all ASD data loading functions."""
    
    # Sample test data
    test_proteins = ["P10636", "P04637", "P42336"]
    test_modulators = ["ASD01140224", "ASD03930089", "ASD07150007"]
    
    print("Testing ASD Data Loading Functions")
    print("=" * 40)
    
    # Test 1: XML protein data
    try:
        xf_data = parse_asd_xf(test_proteins)
        print(f"✓ XML data: {len(xf_data)} proteins loaded")
    except Exception as e:
        print(f"✗ XML data failed: {e}")
    
    # Test 2: 2D structures
    try:
        struct_2d = load_asd_2d(test_proteins)
        print(f"✓ 2D structures: {len(struct_2d)} modulators loaded")
    except Exception as e:
        print(f"✗ 2D structures failed: {e}")
    
    # Test 3: 3D structures
    try:
        struct_3d = load_asd_3d(test_proteins)
        print(f"✓ 3D structures: {len(struct_3d)} modulators loaded")
    except Exception as e:
        print(f"✗ 3D structures failed: {e}")
    
    # Test 4: Mutations
    try:
        mutations = load_asd_am(test_proteins)
        for protein_id, mut_list in mutations.items():
            print(f"{protein_id}: {len(mut_list)} mutations")
    except Exception as e:
        print(f"✗ Mutations failed: {e}")
    
    
    # Test 5: Drug data
    try:
        drugs = load_asd_dr(test_modulators)
        print(f"✓ Drug data: {len(drugs)} modulators loaded")
    except Exception as e:
        print(f"✗ Drug data failed: {e}")

    # Test 6: Predicted sites
    try:
        predicted = load_asd_ap(test_proteins)
        print(f"✓ Predicted sites: {len(predicted)} proteins loaded")
    except Exception as e:
        print(f"✗ Predicted sites failed: {e}")
    

test_asd_functions()
"""
BioLiP Tool Functions for Agent Systems

Modular tool functions for querying the BioLiP protein-ligand database
designed for integration with LangChain and other agent frameworks.

Each function is self-contained and can be called independently by agent systems.

Author: Expert Python Engineer
Purpose: Allosteric research tool functions for agent systems
"""

import requests
import pandas as pd
import re
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BIOLIP_BASE_URL = "https://zhanglab.comp.nus.edu.sg/BioLiP"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0


@dataclass
class LigandInfo:
    """Data class for ligand information"""
    code: str
    name: str
    type: str
    binding_affinity: Optional[float] = None
    biological_relevance: Optional[str] = None
    binding_site_id: Optional[str] = None
    binding_residues: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class BindingSite:
    """Data class for binding site information"""
    site_id: str
    residues: List[str]
    ligand_codes: List[str]
    is_catalytic: bool = False
    distance_to_catalytic: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


# Utility Functions
def _make_request(url: str, params: Dict[str, Any] = None) -> requests.Response:
    """
    Make HTTP request with retry logic and error handling
    
    Args:
        url: Target URL
        params: Query parameters
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: If request fails after all retries
    """
    session = requests.Session()

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://zhanglab.comp.nus.edu.sg/BioLiP"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, params=params, timeout=DEFAULT_TIMEOUT, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Request attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise


def _parse_protein_response(raw_data: str, pdb_id: str, chain: str = None) -> Dict[str, Any]:
    """Parse raw BioLiP response data into structured format"""
    lines = raw_data.strip().split('\n')
    
    protein_data = {
        'pdb_id': pdb_id.upper(),
        'chain': chain.upper() if chain else None,
        'catalytic_residues': [],
        'ligands': [],
        'mapped_residues': {},
        'metadata': {}
    }
    
    current_ligand = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('PDB:'):
            protein_data['metadata']['resolution'] = _extract_resolution(line)
            protein_data['metadata']['method'] = _extract_method(line)
        elif line.startswith('LIGAND:'):
            current_ligand = _parse_ligand_info(line)
            if current_ligand:
                protein_data['ligands'].append(current_ligand)
        elif line.startswith('BINDING_SITE:') and current_ligand:
            residue_pattern = r'[A-Z]\d+'
            residues = re.findall(residue_pattern, line)
            current_ligand.binding_residues = residues
        elif line.startswith('CATALYTIC:'):
            residue_pattern = r'[A-Z]\d+'
            catalytic_residues = re.findall(residue_pattern, line)
            protein_data['catalytic_residues'].extend(catalytic_residues)
        elif line.startswith('MAPPED:') and '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                original = parts[0].strip().split()[-1]
                mapped = parts[1].strip()
                protein_data['mapped_residues'][original] = mapped
    
    return protein_data


def _parse_ligand_info(line: str) -> Optional[LigandInfo]:
    """Parse ligand information line"""
    try:
        parts = line.split()
        if len(parts) >= 4:
            ligand_code = parts[1]
            chain = parts[2] if len(parts) > 2 else None
            residue_num = parts[3] if len(parts) > 3 else None
            ligand_type = parts[4] if len(parts) > 4 else "unknown"
            
            return LigandInfo(
                code=ligand_code,
                name=ligand_code,
                type=ligand_type,
                binding_site_id=f"{chain}_{residue_num}" if chain and residue_num else None
            )
    except Exception as e:
        logger.warning(f"Failed to parse ligand info: {line}, error: {e}")
    
    return None


def _extract_resolution(line: str) -> Optional[float]:
    """Extract resolution from PDB info line"""
    resolution_match = re.search(r'(\d+\.\d+)\s*A', line)
    return float(resolution_match.group(1)) if resolution_match else None


def _extract_method(line: str) -> Optional[str]:
    """Extract experimental method from PDB info line"""
    methods = ['X-RAY', 'NMR', 'CRYO-EM', 'ELECTRON MICROSCOPY']
    for method in methods:
        if method in line.upper():
            return method
    return None


def _calculate_site_distance(site1_residues: List[str], site2_residues: List[str]) -> Optional[float]:
    """Calculate simplified distance between two binding sites based on residue numbers"""
    try:
        site1_nums = [int(re.search(r'\d+', res).group()) for res in site1_residues if re.search(r'\d+', res)]
        site2_nums = [int(re.search(r'\d+', res).group()) for res in site2_residues if re.search(r'\d+', res)]
        
        if site1_nums and site2_nums:
            min_distance = min(abs(s1 - s2) for s1 in site1_nums for s2 in site2_nums)
            return float(min_distance)
    except Exception:
        pass
    
    return None


# Main Tool Functions
def fetch_protein_data(pdb_id: str, chain: Optional[str] = None) -> Dict[str, Any]:
    """
    Core tool: Retrieve all essential data for a given protein chain
    
    This tool fetches comprehensive protein-ligand interaction data from BioLiP,
    including catalytic residues, ligands, binding sites, and non-standard residue mappings.
    
    Args:
        pdb_id: PDB identifier (4-character string)
        chain: Specific chain identifier (optional)
        
    Returns:
        Dictionary containing:
        - pdb_id: PDB identifier
        - chain: Chain identifier
        - catalytic_residues: List of catalytic residue positions
        - ligands: List of ligand dictionaries with binding information
        - binding_sites: List of binding site dictionaries
        - mapped_residues: Dictionary of non-standard residue mappings
        - metadata: Additional protein metadata (resolution, method)
        
    Raises:
        ValueError: If PDB ID is invalid
        requests.RequestException: If API request fails
    """
    if not pdb_id or len(pdb_id) != 4:
        raise ValueError("PDB ID must be a 4-character string")
    
    logger.info(f"Fetching protein data for {pdb_id}" + (f" chain {chain}" if chain else ""))
    
    params = {"pdbid": pdb_id.lower(), "outfmt": "txt"}
    if chain:
        params["chain"] = chain.upper()
    
    try:
        response = _make_request(f"{BIOLIP_BASE_URL}/qsearch.cgi", params)
        print("\n Response: ", response.text)
        protein_data = _parse_protein_response(response.text, pdb_id, chain)
        print("\n Protein Data", protein_data)
        # Enrich ligand data
        protein_data['ligands'] = [
            enriched for lig in protein_data['ligands']
            if (enriched := enrich_ligand_data(lig.get("ligand_code"))) is not None
        ]

        # Analyze binding sites
        protein_data['binding_sites'] = analyze_binding_sites(
            protein_data['ligands'], 
            protein_data['catalytic_residues']
        )
        
        return protein_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch protein data for {pdb_id}: {e}")
        raise


def enrich_ligand_data(ligand_code: str) -> Dict[str, Any]:
    """
    Tool: Fetch detailed chemical information for a ligand
    
    Args:
        ligand_code: 3-letter ligand code from PDB Chemical Component Dictionary
        
    Returns:
        Dictionary containing detailed ligand information:
        - code: Ligand code
        - name: Full chemical name
        - biological_relevance: Functional role description
        - molecular_weight: Molecular weight if available
        - formula: Chemical formula if available
    """
    try:
        response = _make_request(f"{BIOLIP_BASE_URL}/sym.cgi", {"code": ligand_code})
        
        ligand_details = {
            'code': ligand_code,
            'name': ligand_code,
            'biological_relevance': None,
            'molecular_weight': None,
            'formula': None
        }
        
        lines = response.text.split('\n')
        for line in lines:
            if 'NAME:' in line:
                ligand_details['name'] = line.split('NAME:')[-1].strip()
            elif 'FUNCTION:' in line or 'ROLE:' in line:
                ligand_details['biological_relevance'] = line.split(':')[-1].strip()
            elif 'WEIGHT:' in line or 'MW:' in line:
                weight_match = re.search(r'(\d+\.?\d*)', line)
                if weight_match:
                    ligand_details['molecular_weight'] = float(weight_match.group(1))
            elif 'FORMULA:' in line:
                ligand_details['formula'] = line.split('FORMULA:')[-1].strip()
        
        time.sleep(0.1)  # Rate limiting
        return ligand_details
        
    except Exception as e:
        logger.warning(f"Failed to enrich ligand {ligand_code}: {e}")
        return {
            'code': ligand_code,
            'name': ligand_code,
            'biological_relevance': None,
            'molecular_weight': None,
            'formula': None
        }


def analyze_binding_sites(ligands: List[Dict[str, Any]], catalytic_residues: List[str]) -> List[Dict[str, Any]]:
    """
    Tool: Analyze binding sites and classify as catalytic or allosteric
    
    Args:
        ligands: List of ligand dictionaries from protein data
        catalytic_residues: List of known catalytic residues
        
    Returns:
        List of binding site dictionaries with classification
    """
    binding_sites = []
    site_id_counter = 1
    
    for ligand in ligands:
        binding_residues = ligand.get('binding_residues', [])
        if binding_residues:
            # Check if binding site overlaps with catalytic residues
            is_catalytic = any(
                res in catalytic_residues 
                for res in binding_residues
            ) if catalytic_residues else False
            
            # Calculate distance to catalytic site
            distance_to_catalytic = None
            if catalytic_residues and binding_residues:
                distance_to_catalytic = _calculate_site_distance(binding_residues, catalytic_residues)
            
            binding_site = {
                'site_id': ligand.get('binding_site_id') or f"SITE_{site_id_counter}",
                'residues': binding_residues,
                'ligand_codes': [ligand.get('code')],
                'is_catalytic': is_catalytic,
                'distance_to_catalytic': distance_to_catalytic
            }
            
            binding_sites.append(binding_site)
            site_id_counter += 1
    
    return binding_sites


def filter_ligands(ligands: List[Dict[str, Any]], 
                  ligand_type: Optional[str] = None,
                  min_affinity: Optional[float] = None,
                  biological_relevance: Optional[str] = None,
                  exclude_catalytic: bool = False,
                  catalytic_residues: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Tool: Filter ligands by various criteria
    
    Args:
        ligands: List of ligand dictionaries
        ligand_type: Filter by ligand type (e.g., 'enzyme', 'inhibitor')
        min_affinity: Minimum binding affinity threshold
        biological_relevance: Filter by biological relevance keyword
        exclude_catalytic: Exclude ligands that bind to catalytic sites
        catalytic_residues: List of catalytic residues for filtering
        
    Returns:
        Filtered list of ligand dictionaries
    """
    filtered = ligands.copy()
    
    if ligand_type:
        filtered = [lig for lig in filtered if lig.get('type') == ligand_type]
    
    if min_affinity is not None:
        filtered = [lig for lig in filtered 
                   if lig.get('binding_affinity') and lig['binding_affinity'] >= min_affinity]
    
    if biological_relevance:
        filtered = [lig for lig in filtered 
                   if lig.get('biological_relevance') and 
                   biological_relevance.lower() in lig['biological_relevance'].lower()]
    
    if exclude_catalytic and catalytic_residues:
        filtered = [lig for lig in filtered 
                   if not any(res in catalytic_residues 
                            for res in (lig.get('binding_residues') or []))]
    
    logger.info(f"Filtered {len(ligands)} ligands to {len(filtered)} ligands")
    return filtered


def identify_allosteric_sites(protein_data: Dict[str, Any], 
                            distance_threshold: float = 10.0) -> List[Dict[str, Any]]:
    """
    Tool: Identify candidate allosteric binding sites
    
    Identifies binding sites that are spatially separated from catalytic sites
    and likely to be allosteric regulation sites.
    
    Args:
        protein_data: Complete protein data dictionary from fetch_protein_data
        distance_threshold: Minimum distance from catalytic site to be considered allosteric
        
    Returns:
        List of allosteric binding site dictionaries
    """
    binding_sites = protein_data.get('binding_sites', [])
    catalytic_residues = protein_data.get('catalytic_residues', [])
    
    allosteric_sites = []
    
    for site in binding_sites:
        # Skip if it's already identified as catalytic
        if site.get('is_catalytic', False):
            continue
        
        # Check distance from catalytic site
        distance = site.get('distance_to_catalytic')
        if distance is not None and distance >= distance_threshold:
            allosteric_sites.append(site)
        elif not catalytic_residues:
            # If no catalytic residues defined, consider all non-enzyme ligands as potential allosteric
            allosteric_sites.append(site)
    
    logger.info(f"Identified {len(allosteric_sites)} potential allosteric binding sites")
    return allosteric_sites


def get_binding_residue_summary(protein_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Create a summary of binding residues and their classifications
    
    Args:
        protein_data: Complete protein data dictionary from fetch_protein_data
        
    Returns:
        Dictionary containing binding residue analysis summary:
        - total_ligands: Total number of ligands
        - catalytic_sites: Number of catalytic binding sites
        - allosteric_sites: Number of potential allosteric sites  
        - residue_details: List of dictionaries with per-residue information
    """
    ligands = protein_data.get('ligands', [])
    catalytic_residues = protein_data.get('catalytic_residues', [])
    
    residue_details = []
    catalytic_count = 0
    allosteric_count = 0
    
    for ligand in ligands:
        binding_residues = ligand.get('binding_residues', [])
        if binding_residues:
            has_catalytic = any(res in catalytic_residues for res in binding_residues)
            if has_catalytic:
                catalytic_count += 1
            else:
                allosteric_count += 1
                
            for residue in binding_residues:
                is_catalytic = residue in catalytic_residues
                
                residue_details.append({
                    'ligand_code': ligand.get('code'),
                    'ligand_name': ligand.get('name'),
                    'ligand_type': ligand.get('type'),
                    'residue': residue,
                    'is_catalytic': is_catalytic,
                    'site_type': 'catalytic' if is_catalytic else 'allosteric',
                    'binding_site_id': ligand.get('binding_site_id')
                })
    
    return {
        'total_ligands': len(ligands),
        'catalytic_sites': catalytic_count,
        'allosteric_sites': allosteric_count,
        'residue_details': residue_details
    }


def fetch_pubmed_abstracts(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Tool: Fetch PubMed abstracts for protein or ligand research
    
    Args:
        query: Search query (protein name, ligand name, PDB ID, etc.)
        max_results: Maximum number of abstracts to retrieve
        
    Returns:
        List of dictionaries containing abstract information:
        - pmid: PubMed ID
        - title: Article title
        - abstract: Abstract text (may be limited)
    """
    try:
        params = {"pubmed": query, "outfmt": "txt"}
        response = _make_request(f"{BIOLIP_BASE_URL}/qsearch.cgi", params)
        
        abstracts = []
        lines = response.text.split('\n')
        
        for line in lines:
            if 'PMID:' in line:
                pmid_match = re.search(r'PMID:\s*(\d+)', line)
                if pmid_match:
                    abstracts.append({
                        'pmid': pmid_match.group(1),
                        'title': 'Title not available from BioLiP',
                        'abstract': 'Abstract not available from BioLiP'
                    })
        
        return abstracts[:max_results]
        
    except Exception as e:
        logger.error(f"Failed to fetch PubMed abstracts for {query}: {e}")
        return []


def map_nonstandard_residues(protein_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Tool: Map non-standard residues to standard amino acids
    
    Args:
        protein_data: Protein data dictionary from fetch_protein_data
        
    Returns:
        Updated mapping dictionary of non-standard residues to standard ones
    """
    existing_mappings = protein_data.get('mapped_residues', {})
    
    # Common non-standard residue mappings
    standard_mappings = {
        'MSE': 'MET',  # Selenomethionine -> Methionine
        'CSE': 'CYS',  # Selenocysteine -> Cysteine  
        'PYL': 'LYS',  # Pyrrolysine -> Lysine
        'SEC': 'CYS',  # Selenocysteine -> Cysteine
        'XAA': 'ALA',  # Unknown -> Alanine
        'ASX': 'ASN',  # Asparagine or Aspartic acid -> Asparagine
        'GLX': 'GLN',  # Glutamine or Glutamic acid -> Glutamine
    }
    
    # Merge with existing mappings (existing takes precedence)
    all_mappings = {**standard_mappings, **existing_mappings}
    
    logger.info(f"Mapped {len(all_mappings)} non-standard residues")
    return all_mappings


def search_by_sequence(sequence: str, seq_type: str = 'protein') -> Dict[str, Any]:
    """
    Tool: Search for similar protein-ligand interactions by sequence
    
    Args:
        sequence: Amino acid, DNA, RNA, or peptide sequence
        seq_type: Type of sequence ('protein', 'dna', 'rna', 'peptide')
        
    Returns:
        Dictionary containing search results with similar sequences and their ligand interactions
    """
    valid_types = ['protein', 'dna', 'rna', 'peptide']
    if seq_type not in valid_types:
        raise ValueError(f"seq_type must be one of {valid_types}")
    
    params = {
        'seq_type': seq_type,
        'sequence': sequence
    }
    
    try:
        response = _make_request(f"{BIOLIP_BASE_URL}/ssearch.cgi", params)
        
        # Parse sequence search results
        results = {
            'query_sequence': sequence,
            'sequence_type': seq_type,
            'matches': [],
            'total_matches': 0
        }
        
        # Basic parsing of sequence search results
        lines = response.text.split('\n')
        for line in lines:
            if 'PDB:' in line and 'Chain:' in line:
                # Extract PDB and chain information from matches
                pdb_match = re.search(r'PDB:\s*(\w{4})', line)
                chain_match = re.search(r'Chain:\s*(\w)', line)
                
                if pdb_match and chain_match:
                    results['matches'].append({
                        'pdb_id': pdb_match.group(1),
                        'chain': chain_match.group(1),
                        'similarity': None  # Would need more parsing for actual similarity scores
                    })
        
        results['total_matches'] = len(results['matches'])
        return results
        
    except Exception as e:
        logger.error(f"Sequence search failed: {e}")
        raise



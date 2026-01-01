description = [
{
    "description": "Map a PDB ID to its corresponding UniProt identifiers using the PDBe API, returning a dictionary of chains to UniProt IDs.",
    "name": "pdb_to_uniprot",
    "required_parameters": [
        {
            "default": None,
            "description": "Four-character PDB identifier (case-insensitive). Must be exactly 4 characters (e.g., '1TIM').",
            "name": "pdb_id",
            "type": "str"
        }
    ],
    "optional_parameters": []
},
{
    "description": "Retrieve all PDB entries associated with a given UniProt ID using the PDBe API, returning a sorted list of 4-character PDB IDs.",
    "name": "uniprot_to_pdb",
    "required_parameters": [
        {
            "default": None,
            "description": "UniProt identifier (case-insensitive) for the target protein (e.g., 'P00533').",
            "name": "uniprot_id",
            "type": "str"
        }
    ],
    "optional_parameters": []
},
{
    "description": "Cross-reference ligands against ChEMBL and PubChem databases to retrieve chemical properties, structures, classifications, and approval status.",
    "name": "cross_reference_ligands_chembl_pubchem",
    "required_parameters": [
        {
            "default": None,
            "description": "UniProt identifier for the target protein (e.g., 'P00533')",
            "name": "uniprot_id",
            "type": "str"
        },
        {
            "default": None,
            "description": "List of dictionaries containing ligand metadata, each with at least a 'ligand_name' key (e.g., [{'ligand_name': 'Gefitinib'}])",
            "name": "ligands",
            "type": "list"
        }
    ],
    "optional_parameters": [
        {
            "default": "slim",
            "description": "Level of detail in output: 'slim' returns curated chemical properties (molecular weight, LogP, SMILES, drug approval status); 'full' returns raw ChEMBL and PubChem data dumps",
            "name": "detail_level",
            "type": "str"
        }
    ]
},
{
    "description": "Classify covalent inhibitor binding sites from CovInDB as allosteric or orthosteric based on protein family knowledge, catalytic residue patterns, and binding site characteristics.",
    "name": "map_covalent_probes_to_allosteric",
    "required_parameters": [
        {
            "default": None,
            "description": "UniProt identifier for the target protein to filter CovInDB entries",
            "name": "uniprot_id",
            "type": "str"
        }
    ],
    "optional_parameters": [
        {
            "default": "./data/biomni_data/data_lake/CovInDB_All.csv",
            "description": "Path to CovInDB dataset file containing covalent inhibitor data with columns: Inhibitor_Name, Target_Name, Target_Gene, Target, Site, War_head, Reaction_type, Method, Assay, Reference",
            "name": "dataset_path",
            "type": "str"
        }
    ]
},
{
    "description": "Analyze binding site patterns in covalent inhibitor data to identify most common target residues, residue type distributions, and site frequency statistics.",
    "name": "analyze_site_patterns",
    "required_parameters": [
        {
            "default": None,
            "description": "DataFrame output from map_covalent_probes_to_allosteric containing parsed site information in 'Parsed_Sites' column",
            "name": "df",
            "type": "pd.DataFrame"
        }
    ],
    "optional_parameters": []
},
{
    "description": "Retrieve predicted allosteric residues for a specific protein chain using STINGAllo, a computational tool for allosteric site prediction based on protein structure analysis.",
    "name": "fetch_allosteric_residue_potential",
    "required_parameters": [
        {
            "default": None,
            "description": "4-character PDB ID of the target protein (e.g., '1A01')",
            "name": "pdb_id",
            "type": "str"
        },
        {
            "default": None,
            "description": "Chain ID of the protein structure (e.g., 'A')",
            "name": "chain_id",
            "type": "str"
        }
    ],
    "optional_parameters": []
}




]
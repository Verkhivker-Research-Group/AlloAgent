BIOLIP_TOOL_DESCRIPTIONS = [
    {
        "description": "Retrieve comprehensive protein-ligand interaction data from BioLiP database including catalytic residues, ligands, binding sites, and non-standard residue mappings.",
        "name": "fetch_protein_data",
        "required_parameters": [
            {
                "default": None,
                "description": "PDB identifier (4-character string, e.g., '1azs', '3pqr')",
                "name": "pdb_id",
                "type": "str",
            }
        ],
        "optional_parameters": [
            {
                "default": None,
                "description": "Specific chain identifier (single letter, e.g., 'A', 'B')",
                "name": "chain",
                "type": "str",
            }
        ],
    },
    {
        "description": "Fetch detailed chemical information for a ligand including full name, biological relevance, molecular weight, and chemical formula.",
        "name": "enrich_ligand_data",
        "required_parameters": [
            {
                "default": None,
                "description": "3-letter ligand code from PDB Chemical Component Dictionary (e.g., 'ATP', 'FMB', 'GTP')",
                "name": "ligand_code",
                "type": "str",
            }
        ],
        "optional_parameters": [],
    },
    {
        "description": "Analyze binding sites and classify them as catalytic or allosteric based on residue overlap analysis and distance calculations.",
        "name": "analyze_binding_sites",
        "required_parameters": [
            {
                "default": None,
                "description": "List of ligand dictionaries containing binding residue information",
                "name": "ligands",
                "type": "list",
            },
            {
                "default": None,
                "description": "List of catalytic residue identifiers (e.g., ['H57', 'D102', 'S195'])",
                "name": "catalytic_residues",
                "type": "list",
            }
        ],
        "optional_parameters": [],
    },
    {
        "description": "Filter ligands by various criteria including type, binding affinity, biological relevance, or proximity to catalytic sites.",
        "name": "filter_ligands",
        "required_parameters": [
            {
                "default": None,
                "description": "List of ligand dictionaries to be filtered",
                "name": "ligands",
                "type": "list",
            }
        ],
        "optional_parameters": [
            {
                "default": None,
                "description": "Filter by ligand type (e.g., 'enzyme', 'inhibitor', 'cofactor')",
                "name": "ligand_type",
                "type": "str",
            },
            {
                "default": None,
                "description": "Minimum binding affinity threshold (if affinity data available)",
                "name": "min_affinity",
                "type": "float",
            },
            {
                "default": None,
                "description": "Filter by biological relevance keyword (e.g., 'allosteric', 'regulatory')",
                "name": "biological_relevance",
                "type": "str",
            },
            {
                "default": False,
                "description": "Exclude ligands that bind to catalytic sites",
                "name": "exclude_catalytic",
                "type": "bool",
            },
            {
                "default": None,
                "description": "List of catalytic residues for filtering (required if exclude_catalytic=True)",
                "name": "catalytic_residues",
                "type": "list",
            }
        ],
    },
    {
        "description": "Identify candidate allosteric binding sites that are spatially separated from catalytic sites and likely involved in allosteric regulation.",
        "name": "identify_allosteric_sites",
        "required_parameters": [
            {
                "default": None,
                "description": "Complete protein data dictionary from fetch_protein_data function",
                "name": "protein_data",
                "type": "dict",
            }
        ],
        "optional_parameters": [
            {
                "default": 10.0,
                "description": "Minimum distance (in residue numbers) from catalytic site to be considered allosteric",
                "name": "distance_threshold",
                "type": "float",
            }
        ],
    },
    {
        "description": "Create a comprehensive summary of binding residues and their classifications including catalytic vs allosteric site statistics.",
        "name": "get_binding_residue_summary",
        "required_parameters": [
            {
                "default": None,
                "description": "Complete protein data dictionary from fetch_protein_data function",
                "name": "protein_data",
                "type": "dict",
            }
        ],
        "optional_parameters": [],
    },
    {
        "description": "Fetch relevant PubMed abstracts for protein or ligand research using BioLiP's literature database connections.",
        "name": "fetch_pubmed_abstracts",
        "required_parameters": [
            {
                "default": None,
                "description": "Search query (protein name, ligand name, PDB ID, research topic, etc.)",
                "name": "query",
                "type": "str",
            }
        ],
        "optional_parameters": [
            {
                "default": 10,
                "description": "Maximum number of abstracts to retrieve",
                "name": "max_results",
                "type": "int",
            }
        ],
    },
    {
        "description": "Map non-standard amino acids and nucleotides to their standard counterparts for sequence analysis and structural comparisons.",
        "name": "map_nonstandard_residues",
        "required_parameters": [
            {
                "default": None,
                "description": "Protein data dictionary from fetch_protein_data containing residue information",
                "name": "protein_data",
                "type": "dict",
            }
        ],
        "optional_parameters": [],
    },
    {
        "description": "Search for similar protein-ligand interactions using sequence similarity search across protein, DNA, RNA, or peptide sequences.",
        "name": "search_by_sequence",
        "required_parameters": [
            {
                "default": None,
                "description": "Input sequence string (amino acids for proteins, nucleotides for DNA/RNA)",
                "name": "sequence",
                "type": "str",
            }
        ],
        "optional_parameters": [
            {
                "default": "protein",
                "description": "Type of sequence ('protein', 'dna', 'rna', 'peptide')",
                "name": "seq_type",
                "type": "str",
            }
        ],
    }
]
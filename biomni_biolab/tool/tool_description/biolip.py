description = [
    {
        "description": "Parse BioLiP interactions from a preprocessed pickle file, optionally filtering by PDB ID and chain.",
        "name": "parse_biolip_interactions",
        "optional_parameters": [
            {
                "default": None,
                "description": "Chain identifier to filter interactions (e.g., 'A', 'B')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters, lowercase in stored BioLiP data)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    },
    {
        "description": "Retrieve DNA sequence data from BioLiP database for a specific PDB structure, optionally filtered by chain.",
        "name": "biolip_dna",
        "optional_parameters": [
            {
                "default": None,
                "description": "Single letter chain identifier (e.g., 'A', 'B')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    },
    {
        "description": "Retrieve peptide sequence data from BioLiP database for a specific PDB structure, optionally filtered by chain.",
        "name": "biolip_peptide",
        "optional_parameters": [
            {
                "default": None,
                "description": "Single letter chain identifier (e.g., 'A', 'B')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    },
    {
        "description": "Retrieve protein sequence data from BioLiP database for a specific PDB structure, optionally filtered by chain.",
        "name": "biolip_protein",
        "optional_parameters": [
            {
                "default": None,
                "description": "Single letter chain identifier (e.g., 'A', 'B')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    },
    {
        "description": "Retrieve RNA sequence data from BioLiP database for a specific PDB structure, optionally filtered by chain.",
        "name": "biolip_rna",
        "optional_parameters": [
            {
                "default": None,
                "description": "Chain identifier (1-2 letters, e.g., 'A', 'S1')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    },
    {
        "description": "Get unique ligand identifiers for a given PDB structure, optionally filtered by chain.",
        "name": "biolip_ligands",
        "optional_parameters": [
            {
                "default": None,
                "description": "Chain identifier to filter ligands (e.g., 'A', 'B')",
                "name": "chain",
                "type": "str"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "Protein Data Bank identifier (4 or 12 characters)",
                "name": "pdb_id",
                "type": "str"
            }
        ]
    }
]

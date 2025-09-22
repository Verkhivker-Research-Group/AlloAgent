description = [{
    "description": "Retrieve ligands associated with a UniProt protein ID, enriched with BioLiP and external provenance information. Uses UniProt → PDB → BioLiP pipeline with ligand filtering and enrichment.",
    "name": "get_ligand_ids_from_protein",
    "optional_parameters": [],
    "required_parameters": [
        {
            "default": None,
            "description": "UniProt accession ID of the protein to query.",
            "name": "uniprot_id",
            "type": "str",
        }
    ],
},
{
    "description": "Cross-reference ligands retrieved from BioLiP against UniProt, PDB, and the Allosteric Database (ASD) to build provenance-aware ligand annotations.",
    "name": "cross_reference_ligands",
    "optional_parameters": [],
    "required_parameters": [
        {
            "default": None,
            "description": "UniProt accession ID of the protein to cross-reference.",
            "name": "uniprot_id",
            "type": "str",
        },
        {
            "default": None,
            "description": "List of ligands (from BioLiP or similar) containing ligand codes and source PDB identifiers.",
            "name": "ligands",
            "type": "list",
        }
    ],
},
{
    "description": "Validate predicted allosteric binding sites against BioLiP catalytic site data to determine if sites are genuinely allosteric or overlap with known active sites.",
    "name": "validate_allosteric_sites_with_biolip",
    "optional_parameters": [
        {
            "default": None,
            "description": "List of ligand types to include in analysis (e.g., ['ATP', 'HEM'])",
            "name": "ligand_types",
            "type": "list",
        },
        {
            "default": None,
            "description": "Maximum resolution cutoff in Angstroms for filtering BioLiP entries",
            "name": "resolution_cutoff",
            "type": "float",
        },
        {
            "default": "position",
            "description": "Residue matching method: 'position' (compare residue numbers only) or 'exact' (compare full residue codes)",
            "name": "match_type",
            "type": "str",
        }
    ],
    "required_parameters": [
        {
            "default": None,
            "description": "Dictionary of predicted sites with residue lists (e.g., {'site1': ['W118', 'A119']})",
            "name": "user_sites",
            "type": "dict",
        },
        {
            "default": None,
            "description": "Pandas DataFrame containing BioLiP database entries with catalytic site information",
            "name": "biolip_df",
            "type": "DataFrame",
        },
        {
            "default": None,
            "description": "4-character PDB identifier to filter BioLiP data (e.g., '9xim')",
            "name": "pdb_id",
            "type": "str",
        }
    ]
}


]
{
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
    "description": "Build a structured dataset representing an energy landscape for a protein, integrating PDB conformations, ASD allosteric modulators, and molecular dynamics ensembles (MoDEL/Dynameomics).",
    "name": "build_energy_landscape",
    "optional_parameters": [],
    "required_parameters": [
        {
            "default": None,
            "description": "Protein identifier, either UniProt accession ID or PDB ID.",
            "name": "protein_id",
            "type": "str",
        }
    ],
},

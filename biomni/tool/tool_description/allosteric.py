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
    "description": "Build a comprehensive energy landscape for a protein, integrating PDB conformations, ASD allosteric modulators, and molecular dynamics ensembles. Returns detailed structural information, energy barriers, and allosteric mechanisms.",
    "name": "build_energy_landscape",
    "optional_parameters": [
        {
            "default": None,
            "description": "Optional protein name for enhanced context.",
            "name": "protein_name",
            "type": "str",
        }
    ],
    "required_parameters": [
        {
            "default": None,
            "description": "Protein identifier, either UniProt accession ID or PDB ID.",
            "name": "protein_id",
            "type": "str",
        }
    ],
},
{
    "description": "Explain energy landscape theory in the context of allostery for a specific protein, providing comprehensive theoretical framework and structural mechanisms.",
    "name": "explain_energy_landscape_theory",
    "optional_parameters": [
        {
            "default": None,
            "description": "Protein identifier for specific examples.",
            "name": "protein_id",
            "type": "str",
        },
        {
            "default": None,
            "description": "Protein name for enhanced context.",
            "name": "protein_name",
            "type": "str",
        }
    ],
    "required_parameters": [],
},
{
    "description": "Create a visualization of an energy landscape with conformational states, energy barriers, and transition paths. Returns plot data and file path.",
    "name": "create_energy_landscape_plot",
    "optional_parameters": [
        {
            "default": None,
            "description": "Output file path for the plot. If None, returns plot data only.",
            "name": "output_file",
            "type": "str",
        }
    ],
    "required_parameters": [
        {
            "default": None,
            "description": "Energy landscape data dictionary from build_energy_landscape function.",
            "name": "landscape_data",
            "type": "dict",
        }
    ],
},

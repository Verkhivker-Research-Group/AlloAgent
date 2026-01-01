description = [
    {
        "description": "Cross-reference ligands across local BioLiP and ASD datasets and optionally external chemical databases (ChEMBL/PubChem). Returns structured JSON suitable for downstream LLM/agent consumption, including provenance and optional catalytic-site overlap summaries.",
        "name": "cross_reference_ligands",
        "required_parameters": [],
        "optional_parameters": [
            {
                "default": None,
                "description": "Four-character PDB identifier; used to fetch ligands from BioLiP (e.g., '1I09')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "UniProt identifier to query ASD datasets (e.g., 'P49841')",
                "name": "uniprot_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "Explicit list of ligand names to cross-reference (e.g., ['Gefitinib'])",
                "name": "ligands",
                "type": "list"
            },
            {
                "default": ["biolip", "asd_ap", "asd_dr", "asd_xf"],
                "description": "Datasets to include: 'biolip', 'asd_ap', 'asd_dr', 'asd_xf', and optionally 'chembl_pubchem'",
                "name": "databases",
                "type": "list"
            },
            {
                "default": "slim",
                "description": "Detail level for external cross-references: 'slim' returns curated fields, 'full' returns raw dumps where supported",
                "name": "detail_level",
                "type": "str"
            },
            {
                "default": False,
                "description": "Attempt an LLM-based concise summary (best-effort); requires provider credentials if True",
                "name": "use_llm",
                "type": "bool"
            },
            {
                "default": "openai",
                "description": "LLM provider to attempt when use_llm is True (e.g., 'openai')",
                "name": "llm_provider",
                "type": "str"
            }
        ]
    }
]

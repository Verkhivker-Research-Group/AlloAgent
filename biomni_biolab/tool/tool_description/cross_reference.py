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
    },
    {
        "description": "Efficiently loads and filters large CSV datasets with memory optimization. Supports loading specific columns, filtering by row values, and returning results as DataFrame or JSON. Useful for querying large databases like CovInDB without memory overflow.",
        "name": "retrieve_and_filter_large_dataset",
        "required_parameters": [
            {
                "description": "Path to the CSV file (e.g., './data/biomni_data/data_lake/CovInDB_All.csv')",
                "name": "filepath",
                "type": "str"
            }
        ],
        "optional_parameters": [
            {
                "default": None,
                "description": "List of specific columns to load. If None, loads all columns (e.g., ['Target', 'Inhibitor_Name', 'War_head', 'Site'])",
                "name": "columns_to_load",
                "type": "list"
            },
            {
                "default": None,
                "description": "Column name to filter on (e.g., 'Target' for UniProt ID filtering, 'War_head' for warhead type)",
                "name": "filter_column",
                "type": "str"
            },
            {
                "default": None,
                "description": "Value to match in filter_column (e.g., 'P01116' for KRAS, 'acrylamide' for warhead type filtering)",
                "name": "filter_value",
                "type": "str"
            },
            {
                "default": "dataframe",
                "description": "Output format: 'dataframe' returns pandas DataFrame, 'json' returns dict with data and metadata",
                "name": "return_format",
                "type": "str"
            }
        ]
    }
]

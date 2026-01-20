description = [
    {
        "description": "Convert a UniProt ID to its corresponding ASD (Allosteric Database) ID using the ASD index mapping.",
        "name": "convert_uniprot_to_asd",
        "required_parameters": [
            {
                "default": None,
                "description": "UniProt identifier to convert (e.g., 'P00533' for EGFR)",
                "name": "uniprot_id",
                "type": "str"
            }
        ],
        "optional_parameters": []
    },
    {
        "description": "Convert an ASD (Allosteric Database) ID to its corresponding UniProt ID using the ASD index mapping.",
        "name": "convert_asd_to_uniprot",
        "required_parameters": [
            {
                "default": None,
                "description": "ASD identifier to convert (e.g., 'ASD01020000_1' for EGFR)",
                "name": "asd_id",
                "type": "str"
            }
        ],
        "optional_parameters": []
    },
    {
        "description": "Automatically detect whether a protein ID is UniProt or ASD format and return both identifiers as a tuple (uniprot_id, asd_id).",
        "name": "normalize_protein_id",
        "required_parameters": [
            {
                "default": None,
                "description": "Either UniProt ID (e.g., 'P00533') or ASD ID (e.g., 'ASD01020000_1')",
                "name": "protein_id",
                "type": "str"
            }
        ],
        "optional_parameters": []
    },
    {
        "description": "Build residue-residue interaction networks from ASD experimental allosteric sites and BioLiP protein-ligand interactions to identify communication pathways between allosteric sites. Returns network topology, inter-site pathways, and centrality metrics for understanding allosteric signal transmission.",
        "name": "residue_interaction_networks",
        "required_parameters": [
            {
                "default": None,
                "description": "UniProt ID or ASD ID of the protein to analyze (e.g., 'P00533' or 'ASD01020000_1')",
                "name": "uniprot_id",
                "type": "str"
            }
        ],
        "optional_parameters": [
            {
                "default": None,
                "description": "PDB ID for extracting BioLiP protein-ligand interaction data (e.g., '1IVO')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "Path to directory containing PPI parquet files (genetic_interaction.parquet, two-hybrid.parquet, etc.) for enriching network edges",
                "name": "ppi_data_path",
                "type": "str"
            },
            {
                "default": 2,
                "description": "Minimum edge weight (interaction count) required to include an edge in the network",
                "name": "min_interactions",
                "type": "int"
            }
        ]
    },
    {
        "description": "Identify critical allosteric hotspot residues by analyzing which residues appear across multiple modulators in ASD data. Scores residues by modulator connectivity, diversity, and residue type (cysteine residues scored highest). Returns ranked hotspots in the top percentile for potential therapeutic targeting.",
        "name": "allosteric_hotspot_detection",
        "required_parameters": [
            {
                "default": None,
                "description": "UniProt ID or ASD ID of the protein to analyze (e.g., 'P00533' or 'ASD01020000_1')",
                "name": "uniprot_id",
                "type": "str"
            }
        ],
        "optional_parameters": [
            {
                "default": None,
                "description": "Path to ASD_Release_201909_DR.csv file containing drug/modulator data for more comprehensive analysis",
                "name": "asd_dr_path",
                "type": "str"
            },
            {
                "default": None,
                "description": "Path to marker_celltype.parquet file for filtering by tissue-specific expression patterns",
                "name": "celltype_data_path",
                "type": "str"
            },
            {
                "default": 3,
                "description": "Minimum number of different modulators that must interact with a residue for it to be considered a hotspot candidate",
                "name": "min_modulator_count",
                "type": "int"
            },
            {
                "default": 75.0,
                "description": "Percentile threshold for calling hotspots (default 75th percentile, only top 25% of candidate residues are marked as hotspots)",
                "name": "percentile_threshold",
                "type": "float"
            }
        ]
    }
]

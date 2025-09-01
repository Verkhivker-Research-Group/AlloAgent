description = [
    {
        "description": "Parses ASD XF XML files to extract protein → allosteric site → modulator mappings.",
        "name": "parse_asd_xf",
        "optional_parameters": [
            {
                "default": None,
                "description": "List of specific protein IDs to extract. If None, loads all proteins in the index.",
                "name": "target_proteins",
                "type": "List[str]"
            }
        ],
        "required_parameters": []
    },
    {
        "description": "Parses MOL file content to extract 2D chemical information such as atom and bond counts.",
        "name": "_parse_mol_file",
        "optional_parameters": [],
        "required_parameters": [
            {
                "default": None,
                "description": "The string content of the MOL file to parse.",
                "name": "mol_content",
                "type": "str"
            }
        ]
    },
    {
        "description": "Loads 2D chemical structures from ASD MOL files for given protein IDs and optional modulator IDs.",
        "name": "load_asd_2d",
        "optional_parameters": [
            {
                "default": None,
                "description": "Optional list of specific modulator ASD IDs to filter.",
                "name": "modulator_ids",
                "type": "List[str]"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "List of protein IDs to look up in asd_index.",
                "name": "protein_ids",
                "type": "List[str]"
            }
        ]
    },
    {
        "description": "Parses MOL2 file content to extract 3D coordinates, atom, and bond information.",
        "name": "_parse_mol2_file",
        "optional_parameters": [],
        "required_parameters": [
            {
                "default": None,
                "description": "The string content of the MOL2 file to parse.",
                "name": "mol2_content",
                "type": "str"
            }
        ]
    },
    {
        "description": "Loads 3D chemical structures from ASD MOL2 files for given protein IDs and optional modulator IDs.",
        "name": "load_asd_3d",
        "optional_parameters": [
            {
                "default": None,
                "description": "Optional list of specific modulator ASD IDs to filter.",
                "name": "modulator_ids",
                "type": "List[str]"
            }
        ],
        "required_parameters": [
            {
                "default": None,
                "description": "List of protein IDs to look up in asd_index (values are XML file paths).",
                "name": "protein_ids",
                "type": "List[str]"
            }
        ]
    },
    {
        "description": "Loads allosteric mutation data from ASD_Release_201909_AM.csv filtered by UniProt IDs.",
        "name": "load_asd_am",
        "optional_parameters": [
            {
                "default": None,
                "description": "List of UniProt IDs to load. If None, loads all mutations from the dataset.",
                "name": "target_uniprot_ids",
                "type": "List[str]"
            }
        ],
        "required_parameters": []
    },
    {
        "description": "Loads allosteric drug/modulator information with expanded target/activity information from ASD_Release_201909_DR.csv.",
        "name": "load_asd_dr",
        "optional_parameters": [
            {
                "default": None,
                "description": "List of specific modulator IDs to load. If None, loads all modulators from the dataset.",
                "name": "target_modulators",
                "type": "List[str]"
            }
        ],
        "required_parameters": []
    },
    {
        "description": "Loads predicted allosteric sites with detailed site grouping by PDB structure from ASD_Release_202306_AP.csv.",
        "name": "load_asd_ap",
        "optional_parameters": [
            {
                "default": None,
                "description": "List of specific protein IDs (UniProt IDs) to load. If None, loads all predicted sites from the dataset.",
                "name": "target_proteins",
                "type": "List[str]"
            }
        ],
        "required_parameters": []
    }
]

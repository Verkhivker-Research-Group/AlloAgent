description = [
    {
        "description": "Compute spatial distance from candidate allosteric site residues to active/catalytic site residues. Scores based on optimal allosteric distance range (10-30 Å). Returns distance metrics and druggability score.",
        "name": "structural_distance_tool",
        "required_parameters": [
            {
                "default": None,
                "description": "PDB identifier for the protein structure (e.g., '1A3N')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "List of tuples specifying candidate allosteric residues as (chain_id, residue_number), e.g., [('A', 42), ('A', 92)]",
                "name": "candidate_residues",
                "type": "List[Tuple[str, int]]"
            },
            {
                "default": None,
                "description": "List of tuples specifying active/catalytic site residues as (chain_id, residue_number), e.g., [('A', 58), ('A', 87)]",
                "name": "active_residues",
                "type": "List[Tuple[str, int]]"
            }
        ]
    },
    {
        "description": "Analyze geometric properties of potential allosteric binding pockets including volume, depth, and shape sphericity. Evaluates pocket druggability based on structural characteristics favorable for small molecule binding.",
        "name": "pocket_geometry_tool",
        "required_parameters": [
            {
                "default": None,
                "description": "PDB identifier for the protein structure (e.g., '1A3N')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "List of tuples specifying candidate allosteric residues as (chain_id, residue_number), e.g., [('A', 42), ('A', 92)]",
                "name": "candidate_residues",
                "type": "List[Tuple[str, int]]"
            }
        ],
    },
    {
        "description": "Calculate solvent-accessible surface area (SASA) and hydrophobicity profiles for candidate residues. Scores druggability based on accessibility and chemical properties suitable for small molecule interaction.",
        "name": "residue_accessibility_tool",
        "required_parameters": [
            {
                "default": None,
                "description": "PDB identifier for the protein structure (e.g., '1A3N')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "List of tuples specifying candidate allosteric residues as (chain_id, residue_number), e.g., [('A', 42), ('A', 92)]",
                "name": "candidate_residues",
                "type": "List[Tuple[str, int]]"
            }
        ]
    },
    {
        "description": "Assess evolutionary conservation of candidate residues across homologous sequences. High conservation indicates functional importance and potential for allosteric regulation. Fetches sequence data from UniProt.",
        "name": "evolutionary_conservation_tool",
        "required_parameters": [
            {
                "default": None,
                "description": "UniProt accession identifier (e.g., 'P69905' for human hemoglobin alpha)",
                "name": "uniprot_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "List of tuples specifying candidate allosteric residues as (chain_id, residue_number), e.g., [('A', 42), ('A', 92)]",
                "name": "candidate_residues",
                "type": "List[Tuple[str, int]]"
            }
        ],
        "optional_parameters": []
    },
    {
        "description": "Query the Allosteric Database (ASD) and literature for known allosteric sites, modulators, and regulatory mechanisms. Cross-references candidate residues with experimentally validated allosteric sites.",
        "name": "allosteric_evidence_tool",
        "required_parameters": [],
        "optional_parameters": [
            {
                "default": None,
                "description": "PDB identifier for the protein structure (e.g., '1A3N')",
                "name": "pdb_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "UniProt accession identifier (e.g., 'P69905')",
                "name": "uniprot_id",
                "type": "str"
            },
            {
                "default": None,
                "description": "List of tuples specifying candidate allosteric residues as (chain_id, residue_number), e.g., [('A', 42), ('A', 92)]",
                "name": "candidate_residues",
                "type": "List[Tuple[str, int]]"
            }
        ]
    }
]
PROMPTS = {
    "prompt_1_kras_g12c_full_pipeline": (
        "I'm developing a covalent drug discovery pipeline for KRAS G12C (UniProt ID: P01116). "
        "Here's what I need: First, I want to gather detailed chemical information on three known "
        "KRAS inhibitors: Sotorasib, Adagrasib, and AMG510. I need their molecular properties and "
        "structures for comparison. Second, I want to understand the landscape of covalent inhibitors "
        "targeting KRAS. Specifically, I need to know which inhibitors bind to allosteric sites versus "
        "the active site, since G12C is in a switching region. Can you classify the available KRAS "
        "covalent inhibitors by their binding site type? Finally, I'd like to see an analysis of which "
        "residues are most commonly targeted across all KRAS covalent inhibitors. This will help me "
        "understand if there are hotspot residues beyond Cys12 that might be worth investigating. "
        "Can you help me with this complete analysis?"
    ),

    "prompt_2_egfr_covalent_residue_distribution": (
        "I've been looking at covalent inhibitors for EGFR and noticed they seem to target many "
        "different residues. Can you analyze the binding site data to show me which residues are "
        "most commonly targeted? I want to understand if there are preferred residue types (like "
        "cysteines or serines) and see the overall distribution of target sites."
    ),

    "prompt_3_kras_g12c_comparative_report": (
        "I’m working on a covalent inhibitor analysis for KRAS G12C (UniProt: P01116) and I want a "
        "report that’s useful for guiding next experiments. Start by comparing Sotorasib and "
        "Adagrasib with a small table of key chemical and physicochemical details that help "
        "differentiate them, and note any major structural or warhead differences if known. "
        "Then identify several additional covalent KRAS inhibitors that you can support with "
        "evidence and group them by binding-site type, such as binding in a switching-region "
        "pocket versus a more active or functional-site region. For each group, briefly explain "
        "the reasoning. Across the covalent KRAS inhibitors used, summarize which residues are "
        "most commonly targeted and whether there are potential hotspot residues beyond Cys12 "
        "worth paying attention to. End with 2–3 testable follow-up ideas, either experiments or "
        "analyses, that would validate the binding-site grouping and residue hotspot conclusions. "
        "Please clearly label anything that’s uncertain instead of guessing."
    ),

    "prompt_4_kras_g12c_sotorasib_vs_adagrasib": (
        "I’m working on a covalent inhibitor analysis for KRAS G12C (UniProt: P01116) and want a "
        "report that helps guide next experiments. Start by comparing Sotorasib and Adagrasib "
        "in a small table that highlights key chemical and physicochemical properties that "
        "differentiate them. Note any major structural features or warhead differences, if known, "
        "and clearly label any uncertainties."
    ),

    "prompt_5_kras_g12c_additional_inhibitors_binding_sites": (
        "For KRAS G12C (UniProt: P01116), identify several additional covalent KRAS inhibitors "
        "beyond Sotorasib and Adagrasib that you can support with evidence, such as published "
        "literature or structural data. Group these inhibitors by binding-site type, such as "
        "binding in a switching-region pocket versus a more active or functional-site region. "
        "For each group, briefly explain the reasoning behind the binding-site classification "
        "and clearly label any uncertainty."
    ),

    "prompt_6_kras_g12c_residue_hotspots": (
        "Using a set of covalent inhibitors of KRAS G12C (UniProt: P01116), summarize which protein "
        "residues are most commonly targeted by covalent binding. In addition to Cys12, evaluate "
        "whether there are any other residues that may represent potential hotspot sites worth "
        "paying attention to. Clearly distinguish well-supported conclusions from more speculative "
        "observations."
    ),

    "prompt_7_kras_g12c_followup_validation": (
        "Based on an analysis of covalent KRAS G12C inhibitors, including their binding-site "
        "groupings and targeted residue hotspots, propose 2–3 concrete, testable follow-up ideas. "
        "These may be experimental or computational analyses that would help validate the "
        "binding-site classifications and residue hotspot conclusions. Clearly label assumptions "
        "and uncertainties rather than guessing."
    ),

    "prompt_8_hexokinase1_allosteric_sites": (
        "I'm studying hexokinase 1 (UniProt: P19327) and I want to understand what allosteric sites "
        "have been experimentally verified for this protein. Can you help me find that information?"
    ),

    "prompt_9_alcohol_dehydrogenase_ligand_crossref": (
        "I found that alcohol dehydrogenase (UniProt: P00888) has several ligands in the BioLiP "
        "database. Can you cross-reference these ligands with ChEMBL and PubChem to determine which "
        "ones might have allosteric properties and what their pharmacological profiles look like?"
    ),

    "prompt_10_ldh_allosteric_residue_validation": (
        "I've identified some potential allosteric residues in L-lactate dehydrogenase "
        "(UniProt: P0AB91) based on sequence analysis. I now need to validate whether these "
        "residues are actually accessible for ligand binding and understand their structural "
        "properties. Can you analyze the 3D structure to determine the accessibility and "
        "geometric properties of these candidate sites?"
    ),

    "prompt_11_p65_allosteric_communication": (
        "I'm interested in understanding how allosteric information flows through the transcription "
        "factor p65 (UniProt: P23979). Can you identify the key allosteric hotspots where modulators "
        "bind and trace the communication pathways through the protein structure to the functional "
        "sites? Also indicate which residues show the strongest evidence of involvement in "
        "allosteric mechanisms."
    ),

    "prompt_12_acylcoa_hydrolase_covalent_probes": (
        "I'm developing covalent probes for allosteric modulation of acyl-CoA hydrolase "
        "(UniProt: P51639). I need a comprehensive analysis that includes: (1) known allosteric "
        "sites and their modulators, (2) potential covalent probe binding sites based on structural "
        "and evolutionary data, (3) residues that are most conserved across species, and (4) how "
        "these sites relate to the active site. Synthesize all this evidence to identify the most "
        "promising sites for probe development."
    ),

    "prompt_13_erk2_allosteric_modulators": (
        "I'm looking for known allosteric modulators of ERK2 (UniProt: P28564). Can you summarize "
        "which small molecules have been reported to bind outside the active site and how they "
        "influence ERK2 activity or signaling outcomes?"
    ),

    "prompt_14_erk1_allosteric_validation_plan": (
        "I'd like to design a quick validation plan for an allosteric inhibitor of ERK1 "
        "(UniProt: P28565). Propose a concise experimental setup to measure changes in substrate "
        "phosphorylation and downstream pathway readouts, and suggest controls that would help "
        "differentiate allosteric from orthosteric effects."
    ),

    "prompt_15_adh_isoform_selective_allostery": (
        "I want to explore isoform-selective allosteric modulation in alcohol dehydrogenases "
        "(UniProt: P00887). Identify candidate allosteric sites and modulators for ADH1A and "
        "discuss how these might differ from the closely related ADH1B. Highlight features that "
        "could drive selectivity and the types of assays that would detect isoform-specific "
        "allosteric effects."
    ),
}

# Allosteric data descriptions used across test scripts
ALLOSTERIC_DATA = {
    "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
}

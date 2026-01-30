ALLOSTERIC_DATA = {
    "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202309_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
}
PROMPTS = {
    "prompt_01": "I'm developing a covalent drug discovery pipeline for KRAS G12C (UniProt ID: P01116). Here's what I need: First, I want to gather detailed chemical information on three known KRAS inhibitors: Sotorasib, Adagrasib, and AMG510. I need their molecular properties and structures for comparison. Second, I want to understand the landscape of covalent inhibitors targeting KRAS. Specifically, I need to know which inhibitors bind to allosteric sites versus the active site, since G12C is in a switching region. Can you classify the available KRAS covalent inhibitors by their binding site type? Finally, I'd like to see an analysis of which residues are most commonly targeted across all KRAS covalent inhibitors. This will help me understand if there are hotspot residues beyond Cys12 that might be worth investigating. Can you help me with this complete analysis.",

    "prompt_02": "I've been looking at covalent inhibitors for EGFR and noticed they seem to target many different residues. Can you analyze the binding site data to show me which residues are most commonly targeted? I want to understand if there are preferred residue types (like cysteines or serines) and see the overall distribution of target sites.",

    "prompt_03": "I’m working on a covalent inhibitor analysis for KRAS G12C (UniProt: P01116) and I want a report that’s useful for guiding next experiments. Start by comparing Sotorasib and Adagrasib with a small table of key chemical/physicochemical details that help differentiate them (and note any major structural/warhead differences if known). Then identify several additional covalent KRAS inhibitors (pick ones you can support with evidence) and group them by binding-site type (for example, binding in a switching-region pocket vs a more “active/functional-site” region). For each group, explain the reasoning briefly. Across the covalent KRAS inhibitors you used, summarize which residues are most commonly targeted and whether there are any potential hotspot residues beyond Cys12 worth paying attention to. End with 2–3 testable follow-up ideas (either experiments or analyses) that would validate the binding-site grouping and residue hotspot conclusions. Please clearly label anything that’s uncertain instead of guessing.",

    "prompt_04": "I’m working on a covalent inhibitor analysis for KRAS G12C (UniProt: P01116) and want a report that helps guide next experiments. Start by comparing Sotorasib and Adagrasib in a small table that highlights key chemical and physicochemical properties that differentiate them. Note any major structural features or warhead differences, if known, and clearly label any uncertainties.",

    "prompt_05": "For KRAS G12C (UniProt: P01116), identify several additional covalent KRAS inhibitors beyond Sotorasib and Adagrasib that you can support with evidence (for example, published literature or structural data). Group these inhibitors by binding-site type (such as binding in a switching-region pocket versus a more active or functional-site region). For each group, briefly explain the reasoning behind the binding-site classification, and clearly label any uncertainty.",

    "prompt_06": "Using a set of covalent inhibitors of KRAS G12C (UniProt: P01116), summarize which protein residues are most commonly targeted by covalent binding. In addition to Cys12, evaluate whether there are any other residues that may represent potential hotspot sites worth paying attention to. Clearly distinguish well-supported conclusions from more speculative observations.",

    "prompt_07": "Based on an analysis of covalent KRAS G12C inhibitors, including their binding-site groupings and targeted residue hotspots, propose 2–3 concrete, testable follow-up ideas. These may be experimental or computational analyses that would help validate the binding-site classifications and residue hotspot conclusions. Clearly label assumptions and uncertainties rather than guessing.",

    "prompt_08": "I'm studying hexokinase 1 (P19327) and I want to understand what allosteric sites have been experimentally verified for this protein. Can you help me find that information?",

    "prompt_09": "I found that alcohol dehydrogenase (P00888) has several ligands in the BioLiP database. Can you cross-reference these ligands with ChEMBL and PubChem to tell me which ones might have allosteric properties, and what their pharmacological profiles look like?",

    "prompt_10": "I've identified some potential allosteric residues in L-lactate dehydrogenase (P0AB91) based on sequence analysis. Now I need to validate whether these residues are actually accessible for ligand binding and understand their structural properties. Can you analyze the 3D structure to determine the accessibility and geometric properties of these candidate sites?",

    "prompt_11": "I'm interested in understanding how allosteric information flows through the transcription factor p65 (P23979). Can you identify the key allosteric hotspots where modulators bind and trace the communication pathways through the protein structure to the functional sites? Also, let me know which residues show the strongest evidence of being involved in allosteric mechanisms.",

    "prompt_12": "I'm developing covalent probes for allosteric modulation of acyl-CoA hydrolase (P51639). I need a comprehensive analysis: (1) what are the known allosteric sites and their modulators, (2) where could covalent probes bind based on structural and evolutionary data, (3) which residues are most conserved across species, and (4) how do these sites relate to the active site? Synthesize all this evidence to identify the most promising sites for probe development.",

    "prompt_13": "I'm looking for known allosteric modulators of ERK2 (P28564). Can you summarize which small molecules have been reported to bind outside the active site and how they influence ERK2 activity or signaling outcomes?",

    "prompt_14": "I'd like to design a quick validation plan for an allosteric inhibitor of ERK1 (P28565). Propose a concise experimental setup to measure changes in substrate phosphorylation and downstream pathway readouts, and suggest controls to differentiate allosteric from orthosteric effects.",

    "prompt_15": "I want to explore isoform-selective allosteric modulation in alcohol dehydrogenases (P00887). Identify candidate allosteric sites and modulators for ADH1A , and discuss how these might differ from the closely related ADH1B. Highlight features that could drive selectivity and the types of assays that would detect isoform-specific allosteric effects.",

    "prompt_16": "I’m looking at BRAF kinase (UniProt: P15056) and I keep seeing resistance mutations pop up against ATP-site inhibitors. Are there any experimentally reported allosteric or non-ATP-site binding pockets on BRAF that people have tried to exploit, and how do they mechanistically bypass common resistance mutations?",

    "prompt_17": "For pyruvate kinase M2 (PKM2, UniProt: P14618), I know it’s regulated by metabolites like fructose-1,6-bisphosphate. Can you explain where these allosteric regulators bind, how they shift PKM2’s conformational state, and whether those sites have been targeted by small-molecule modulators?",

    "prompt_18": "I’m studying Hsp90-alpha (UniProt: P07900) and want to understand whether conformational dynamics reveal allosteric opportunities beyond the N-terminal ATP pocket. Based on known structures and dynamics studies, are there regions that act as conformational control points, even if no strong ligands are known yet?",

    "prompt_19": "I’ve seen allosteric inhibitors reported for protein tyrosine phosphatase 1B (PTP1B, UniProt: P18031) that bind far from the catalytic site. Do similar allosteric mechanisms or pocket architectures appear in other classical PTPs, or does PTP1B seem unusually “allosterically druggable”?",

    "prompt_20": "I’m interested in allosteric control of the glucocorticoid receptor (NR3C1, UniProt: P04150). Please synthesize evidence across ligand-binding domain structures, cofactor interactions, post-translational modifications, and disease-associated mutations to identify plausible allosteric control points.I’m especially interested in sites that could modulate transcriptional output without directly competing with hormone binding. Clearly separate well-supported sites from more speculative hypotheses.",

    "prompt_21": "I heard MEK inhibitors can be allosteric. For MEK1, what’s the known allosteric pocket, which residues define it, and what ligands bind there?.",

    "prompt_22": "Does ABL1 have any allosteric inhibitors that bind outside the ATP site? If yes, where do they bind and what residues matter most for binding?",

    "prompt_23": "For PPARγ, list any non-canonical ligand sites (like alternate/allosteric pockets). For each site: key residues + example ligands + confidence.",

    "prompt_24": "Are there known allosteric modulators of GSK3β? If so, identify the binding site(s) and the most important residues.",

    "prompt_25": "For AMPK alpha-2, I want only experimentally verified allosteric sites. Please separate ‘structural evidence’ vs ‘functional evidence’ and list residues for each site.",

    "prompt_26": "I’ve seen different descriptions of mTOR’s non-ATP pockets. Can you combine sources into one clean map of allosteric sites → residues → ligands, and point out where sources disagree?",

    "prompt_27": "For p38α, identify the main allosteric pocket(s) (not ATP). Which residues show up repeatedly across different modulators as important contact points?",

    "prompt_28": "For β2 adrenergic receptor, are there known allosteric modulators? If yes, compare them and tell me which residues overlap across multiple modulators vs which are unique..",

    "prompt_29": "I want a map of allosteric sites for HIV-1 integrase, the ligands that bind them, and the key residues per site. Then explain whether any sites look ‘druggable’ based on how many ligands share the same residue contacts.",

    "prompt_30": "For PDE5A, compile allosteric sites and modulators. Build a confidence table that marks each site as: verified structurally, verified functionally, both, or uncertain. Include the residues used to define each site."
}

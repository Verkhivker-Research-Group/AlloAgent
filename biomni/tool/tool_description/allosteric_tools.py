allosteric_tools = [
    {
        "Name": "analyze_enzyme_kinetics_assay",
        "Source File": "biochemistry.py",
        "Short Description": "Analyzes dose-dependent effects of modulators, key for studying allosteric regulation",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Measures changes in enzyme activity due to allosteric modulators",
        "Allosteric Research Area": "Functional Assay"
    },
    {
        "Name": "analyze_itc_binding_thermodynamics",
        "Source File": "biochemistry.py",
        "Short Description": "Measures direct binding of allosteric modulators to proteins",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Confirms interaction between modulator and allosteric site",
        "Allosteric Research Area": "Structural/Binding Analysis"
    },
    {
        "Name": "analyze_circular_dichroism_spectra",
        "Source File": "biochemistry.py",
        "Short Description": "Detects conformational changes in proteins upon binding of allosteric modulators",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Identifies structural changes induced by allosteric modulators",
        "Allosteric Research Area": "Structural/Conformational Analysis"
    },
    {
        "Name": "perform_crispr_cas9_genome_editing",
        "Source File": "bioengineering.py",
        "Short Description": "Introduces mutations to test hypotheses about allosteric binding sites",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Validates functional significance of suspected allosteric sites",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "analyze_calcium_imaging_data",
        "Source File": "bioengineering.py",
        "Short Description": "Measures downstream cellular effects of allosteric modulators via calcium signaling changes",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Tracks functional consequences of allosteric modulation in cells",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "simulate_whole_cell_ode_model",
        "Source File": "bioengineering.py",
        "Short Description": "Simulates and predicts system-wide effects of altering allosteric interactions computationally",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Predicts cellular-level outcomes of allosteric regulation",
        "Allosteric Research Area": "Systems Modeling"
    },
    {
        "Name": "predict_protein_disorder_regions",
        "Source File": "biophysics.py",
        "Short Description": "Identifies intrinsically disordered regions that may mediate allosteric conformational changes",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Suggests regions that contribute to allosteric flexibility",
        "Allosteric Research Area": "Structural/Conformational Analysis"
    },
    {
        "Name": "analyze_cell_morphology_and_cytoskeleton",
        "Source File": "biophysics.py",
        "Short Description": "Observes downstream effects on cell shape/structure when allosteric modulators target cytoskeletal proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Reveals functional impact of allosteric modulators",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_ddr_network_in_cancer",
        "Source File": "cancer_biology.py",
        "Short Description": "Analyzes downstream effects of allosteric drugs on DNA Damage Response pathway proteins in cancer",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Connects allosteric modulation to cancer pathway outcomes",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "analyze_cell_senescence_and_apoptosis",
        "Source File": "cancer_biology.py",
        "Short Description": "Measures phenotypic outcomes like apoptosis triggered by allosteric modulators targeting cell survival pathways",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Evaluates cellular responses to allosteric interventions",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "detect_and_annotate_somatic_mutations",
        "Source File": "cancer_biology.py",
        "Short Description": "Identifies mutations affecting allosteric sites, informing drug resistance studies and new inhibitor development",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Detects potential allosteric sites and variants",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "quantify_cell_cycle_phases_from_microscopy",
        "Source File": "cell_biology.py",
        "Short Description": "Measures how allosteric inhibitors targeting cell cycle regulators affect progression, relevant to cancer therapy",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Tracks cell cycle alterations due to allosteric modulation",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "quantify_and_cluster_cell_motility",
        "Source File": "cell_biology.py",
        "Short Description": "Quantifies changes in cell movement caused by allosteric modulators targeting motility/cytoskeletal pathways",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Reveals impact on cytoskeletal dynamics",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "perform_facs_cell_sorting",
        "Source File": "cell_biology.py",
        "Short Description": "Sorts cell populations to study subset-specific effects of allosteric modulators",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Enables analysis of subpopulation-specific allosteric effects",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_flow_cytometry_immunophenotyping",
        "Source File": "cell_biology.py",
        "Short Description": "Identifies and quantifies cell subpopulations affected by allosteric modulators via flow cytometry",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Measures functional distribution of allosteric effects",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_mitochondrial_morphology_and_potential",
        "Source File": "cell_biology.py",
        "Short Description": "Assesses downstream effects of allosteric modulators on mitochondrial health, metabolism, and apoptosis",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Monitors organelle-level outcomes",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "query_pdb",
        "Source File": "database.py",
        "Short Description": "Retrieves experimentally determined 3D protein structures to identify potential allosteric binding pockets or observe modulator-induced conformational changes",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Provides structural basis for allosteric site identification",
        "Allosteric Research Area": "Structural Analysis"
    },
    {
        "Name": "query_pdb_identifiers",
        "Source File": "database.py",
        "Short Description": "Retrieves PDB entries by ID for structural analysis of potential allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Allows targeted structural studies of known proteins",
        "Allosteric Research Area": "Structural Analysis"
    },
    {
        "Name": "query_alphafold",
        "Source File": "database.py",
        "Short Description": "Retrieves AI-predicted protein structures for allosteric site exploration",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Expands structural coverage for potential allosteric sites",
        "Allosteric Research Area": "Structural Analysis"
    },
    {
        "Name": "query_emdb",
        "Source File": "database.py",
        "Short Description": "Retrieves electron microscopy data to visualize structural states relevant to allostery",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Observes conformational states under experimental conditions",
        "Allosteric Research Area": "Structural Analysis"
    },
    {
        "Name": "query_gtopdb",
        "Source File": "database.py",
        "Short Description": "Provides drug target and ligand data, including known allosteric modulators",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Identifies candidate allosteric modulators and targets",
        "Allosteric Research Area": "Drug Discovery"
    },
    {
        "Name": "query_uniprot",
        "Source File": "database.py",
        "Short Description": "Provides comprehensive protein information including annotated regulatory sites that may indicate allosteric regions",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Annotates potential allosteric regions",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "query_cbioportal",
        "Source File": "database.py",
        "Short Description": "Identifies disease-associated mutations in allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Links allosteric sites to disease relevance",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "query_clinvar",
        "Source File": "database.py",
        "Short Description": "Retrieves clinically relevant variants that may alter allosteric regulation",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Provides variant-level functional relevance",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "query_dbsnp",
        "Source File": "database.py",
        "Short Description": "Retrieves single nucleotide polymorphisms that could affect allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Supplies population-level variant data",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "query_gnomad",
        "Source File": "database.py",
        "Short Description": "Provides population-level variant data for potential allosteric site alterations",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Highlights natural variability in allosteric sites",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "query_kegg",
        "Source File": "database.py",
        "Short Description": "Shows pathways involving allosterically-regulated proteins to predict downstream effects",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Maps functional pathway consequences of allosteric modulation",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "query_reactome",
        "Source File": "database.py",
        "Short Description": "Provides pathway maps to contextualize the biological role of allosterically-regulated proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Places allosteric effects in system-level context",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "query_stringdb",
        "Source File": "database.py",
        "Short Description": "Explores protein-protein interaction networks to map potential allosteric influence between proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Infers indirect regulatory connections",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "bayesian_finemapping_with_deep_vi",
        "Source File": "genetics.py",
        "Short Description": "Pinpoints likely causal variants after GWAS; variants outside active sites may indicate allosteric regulation",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Guides identification of regulatory allosteric variants",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "analyze_cas9_mutation_outcomes",
        "Source File": "genetics.py",
        "Short Description": "Confirms CRISPR-created mutations in suspected allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Validates functional impact of targeted edits",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "analyze_crispr_genome_editing",
        "Source File": "genetics.py",
        "Short Description": "Verifies success of CRISPR edits in suspected allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Confirms intended perturbations",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "identify_transcription_factor_binding_sites",
        "Source File": "genetics.py",
        "Short Description": "Identifies genes regulated by transcription factors that may be allosterically modulated",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Suggests downstream targets influenced by allosteric regulation",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "analyze_protein_phylogeny",
        "Source File": "genetics.py",
        "Short Description": "Finds conserved protein regions that could represent functionally important allosteric sites",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Highlights conserved structural/functional regions",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "perform_pcr_and_gel_electrophoresis",
        "Source File": "genetics.py",
        "Short Description": "Verifies genetic modifications or genotypes relevant to allosteric site studies",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Confirms mutation presence",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "annotate_celltype_scRNA",
        "Source File": "genomics.py",
        "Short Description": "Analyzes single-cell expression to identify which cells express the target protein and how they respond to allosteric modulation",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Determines cell-specific expression patterns",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "annotate_celltype_with_panhumanpy",
        "Source File": "genomics.py",
        "Short Description": "Determines cell types expressing the target to assess potential effects of allosteric modulators",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Guides tissue-specific targeting",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "get_rna_seq_archs4",
        "Source File": "genomics.py",
        "Short Description": "Identifies tissue-level expression of the target protein to predict drug activity distribution",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Guides prediction of drug efficacy",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "gene_set_enrichment_analysis",
        "Source File": "genomics.py",
        "Short Description": "Analyzes pathway-level effects of gene expression changes after allosteric drug treatment",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Connects allosteric modulation to biological pathways",
        "Allosteric Research Area": "Pathway Analysis"
    },
    {
        "Name": "analyze_chromatin_interactions",
        "Source File": "genomics.py",
        "Short Description": "Studies 3D genome changes in response to allosteric modulation of DNA-binding proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Reveals genomic-level effects",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "perform_chipseq_peak_calling_with_macs2",
        "Source File": "genomics.py",
        "Short Description": "Identifies genome binding sites of proteins before and after allosteric modulation",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Maps allosteric effects on chromatin binding",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "find_enriched_motifs_with_homer",
        "Source File": "genomics.py",
        "Short Description": "Finds DNA sequence motifs bound preferentially after allosteric modulation",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Infers sequence-level regulation",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "analyze_comparative_genomics_and_haplotypes",
        "Source File": "genomics.py",
        "Short Description": "Identifies conserved genomic regions and haplotypes that may contain allosteric sites",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Highlights functionally important regulatory regions",
        "Allosteric Research Area": "Genetic/Mutational Analysis"
    },
    {
        "Name": "analyze_atac_seq_differential_accessibility",
        "Source File": "immunology.py",
        "Short Description": "Measures genome-wide changes in chromatin accessibility caused by allosteric modulation of transcription factors or chromatin remodelers",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Reveals transcriptional changes mediated by allosteric regulators",
        "Allosteric Research Area": "Genomic/Chromatin Analysis"
    },
    {
        "Name": "analyze_cfse_cell_proliferation",
        "Source File": "immunology.py",
        "Short Description": "Quantifies proliferation changes in immune cells after treatment with allosteric modulators targeting cell-cycle or metabolic regulators",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Tracks functional cellular response",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "estimate_cell_cycle_phase_durations",
        "Source File": "immunology.py",
        "Short Description": "Measures durations of cell-cycle phases to detect effects of allosteric inhibitors on cell-cycle progression",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Detects modulation of cell cycle",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_bacterial_growth_curve",
        "Source File": "immunology.py",
        "Short Description": "Quantifies how allosteric modulators (e.g., drugs targeting bacterial enzymes) affect bacterial growth dynamics",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Determines bacterial sensitivity to allosteric inhibitors",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "analyze_cytokine_production_in_cd4_tcells",
        "Source File": "immunology.py",
        "Short Description": "Functional readout of signaling pathways (e.g., JAK-STAT) frequently targeted allosterically; indicates whether a drug blocks cytokine production",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Evaluates pathway-level impact of allosteric modulation",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "track_immune_cells_under_flow",
        "Source File": "immunology.py",
        "Short Description": "Assesses adhesion and motility changes (integrin regulation, etc.) that can result from allosteric modulation of adhesion/motility proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Monitors cellular behavior changes",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_cns_lesion_histology",
        "Source File": "immunology.py",
        "Short Description": "Tissue-level histology to evaluate immune infiltration, lesion size, and in-vivo effects of allosteric treatments",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Confirms physiological effects",
        "Allosteric Research Area": "Tissue/Histology"
    },
    {
        "Name": "analyze_immunohistochemistry_image",
        "Source File": "immunology.py",
        "Short Description": "Detects spatial/expression changes of target proteins in tissue after allosteric treatment — useful for validating target engagement in vivo",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Provides localization of effects",
        "Allosteric Research Area": "Tissue/Histology"
    },
    {
        "Name": "isolate_purify_immune_cells",
        "Source File": "immunology.py",
        "Short Description": "Prepares purified immune cell populations for downstream assays to test allosteric effects (flow, functional assays, imaging)",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Enables controlled studies",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "query_pubmed",
        "Source File": "literature.py",
        "Short Description": "Searches peer-reviewed biomedical literature to find prior work on allosteric regulation, targets, and mechanisms",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Guides research with published evidence",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "query_arxiv",
        "Source File": "literature.py",
        "Short Description": "Finds preprints on allosteric mechanisms, computational models, and novel inhibitor designs before formal publication",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Identifies cutting-edge research",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "query_scholar",
        "Source File": "literature.py",
        "Short Description": "Broad academic search across multiple disciplines for studies on allosteric drugs and targets",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Supports comprehensive literature coverage",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "fetch_supplementary_info_from_doi",
        "Source File": "literature.py",
        "Short Description": "Retrieves supplementary data from published papers, often containing raw kinetics or structural details of allosteric modulators",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Accesses detailed experimental data",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "extract_pdf_content",
        "Source File": "literature.py",
        "Short Description": "Extracts key experimental and structural data from downloaded papers on allosteric research",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Enables rapid data extraction",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "extract_url_content",
        "Source File": "literature.py",
        "Short Description": "Pulls relevant research data from linked resources in publications on allosteric regulation",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Supplements primary literature",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "search_google",
        "Source File": "literature.py",
        "Short Description": "Finds additional background info, protocols, and vendor sources for allosteric drugs not in academic databases",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Provides practical and technical context",
        "Allosteric Research Area": "Literature Review"
    },
    {
        "Name": "count_bacterial_colonies",
        "Source File": "microbiology.py",
        "Short Description": "Measures bacterial growth inhibition caused by allosteric inhibitors targeting essential bacterial enzymes",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Functional readout of bacterial drug effects",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "enumerate_bacterial_cfu_by_serial_dilution",
        "Source File": "microbiology.py",
        "Short Description": "Quantifies bacterial viability under allosteric drug treatment by colony forming unit counts",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Confirms inhibitory effects",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "quantify_biofilm_biomass_crystal_violet",
        "Source File": "microbiology.py",
        "Short Description": "Measures inhibition of biofilm formation regulated by allosteric signaling pathways",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Assesses pathway-level effect",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "segment_and_analyze_microbial_cells",
        "Source File": "microbiology.py",
        "Short Description": "Quantifies morphological changes due to allosteric inhibitors of bacterial cell wall synthesis proteins",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Detects cellular changes from modulation",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "segment_cells_with_deep_learning",
        "Source File": "microbiology.py",
        "Short Description": "Uses AI to segment bacterial cells to detect shape changes caused by allosteric inhibition",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Automates detection of phenotypic changes",
        "Allosteric Research Area": "Microbial Phenotyping"
    },
    {
        "Name": "annotate_bacterial_genome",
        "Source File": "microbiology.py",
        "Short Description": "Identifies bacterial genes and predicts functions to find new allosteric drug targets",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Highlights potential allosteric targets",
        "Allosteric Research Area": "Genetic/Target Discovery"
    },
    {
        "Name": "model_bacterial_growth_dynamics",
        "Source File": "microbiology.py",
        "Short Description": "Computationally models effects of allosteric inhibitors on bacterial growth parameters and population dynamics",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Predicts drug impact",
        "Allosteric Research Area": "Microbial Modeling"
    },
    {
        "Name": "simulate_generalized_lotka_volterra_dynamics",
        "Source File": "microbiology.py",
        "Short Description": "Simulates microbial interactions affected by allosteric modulation in complex communities",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "System-level predictions of allosteric effects",
        "Allosteric Research Area": "Microbial Modeling"
    },
    {
        "Name": "simulate_microbial_population_dynamics",
        "Source File": "microbiology.py",
        "Short Description": "Models system-level consequences of altering bacterial populations with allosteric drugs",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Predicts ecological impact",
        "Allosteric Research Area": "Microbial Modeling"
    },
    {
        "Name": "predict_rna_secondary_structure",
        "Source File": "microbiology.py",
        "Short Description": "Predicts structural changes in RNA riboswitches regulated allosterically by small molecules binding",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Identifies RNA-based allosteric mechanisms",
        "Allosteric Research Area": "Structural/Functional Analysis"
    },
    {
        "Name": "find_sequence_mutations",
        "Source File": "molecular_biology.py",
        "Short Description": "Confirms intended mutations in genes targeting allosteric sites, validating site-directed mutagenesis experiments",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Validates experimental edits",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "design_primer",
        "Source File": "molecular_biology.py",
        "Short Description": "Designs primers for mutagenesis and sequencing verification of allosteric site mutations",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Supports experimental design",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "design_verification_primers",
        "Source File": "molecular_biology.py",
        "Short Description": "Creates primers to verify mutations in gene sequences related to allosteric regulation",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Confirms successful modifications",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "get_gene_coding_sequence",
        "Source File": "molecular_biology.py",
        "Short Description": "Retrieves coding sequences of target proteins for cloning and expression studies of allosteric mechanisms",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Enables protein expression studies",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "get_plasmid_sequence",
        "Source File": "molecular_biology.py",
        "Short Description": "Retrieves plasmid backbone sequences for inserting genes related to allosteric research",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Provides cloning vectors",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "get_golden_gate_assembly_protocol",
        "Source File": "molecular_biology.py",
        "Short Description": "Provides protocol for efficient cloning of mutant or wild-type genes to study allostery",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Supports experimental cloning",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "design_golden_gate_oligos",
        "Source File": "molecular_biology.py",
        "Short Description": "Designs oligos for Golden Gate assembly cloning used in constructing allosteric study plasmids",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Prepares DNA constructs for experiments",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "golden_gate_assembly",
        "Source File": "molecular_biology.py",
        "Short Description": "Performs the DNA assembly step to create plasmids with genes of interest for allosteric research",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Enables experimental validation",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "get_bacterial_transformation_protocol",
        "Source File": "molecular_biology.py",
        "Short Description": "Describes bacterial transformation to produce plasmids for protein expression in allosteric studies",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Supports protein expression workflows",
        "Allosteric Research Area": "Molecular Biology"
    },
    {
        "Name": "design_knockout_sgrna",
        "Source File": "molecular_biology.py",
        "Short Description": "Designs guide RNAs for gene knockout to validate on-target effects of allosteric drugs",
        "Allosteric Function": "Direct",
        "Allosteric Relevance": "Confirms functional site targeting",
        "Allosteric Research Area": "Genetic Validation"
    },
    {
        "Name": "analyze_atp_luminescence_assay",
        "Source File": "pathology.py",
        "Short Description": "Measures cellular ATP levels, reflecting metabolic enzyme activity regulated allosterically; indicates drug effectiveness on metabolism",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Functional metabolic readout",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_intracellular_calcium_with_rhod2",
        "Source File": "pathology.py",
        "Short Description": "Quantifies intracellular calcium changes caused by allosteric modulation of channels or receptors, showing functional drug impact",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Tracks signaling modulation",
        "Allosteric Research Area": "Cellular Phenotyping"
    },
    {
        "Name": "analyze_thrombus_histology",
        "Source File": "pathology.py",
        "Short Description": "Examines blood clots formed via allosteric regulation of coagulation factors; assesses in vivo efficacy of allosteric anticoagulants",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Confirms physiological modulation",
        "Allosteric Research Area": "Tissue/Histology"
    },
    {
        "Name": "segment_and_quantify_cells_in_multiplexed_images",
        "Source File": "pathology.py",
        "Short Description": "Measures changes in cell populations and protein expression in tissues treated with allosteric drugs, revealing tissue-level drug effects",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Quantifies tissue-level outcomes",
        "Allosteric Research Area": "Tissue/Histology"
    },
    {
        "Name": "analyze_aortic_diameter_and_geometry",
        "Source File": "pathology.py",
        "Short Description": "Quantifies vascular changes as a physiological outcome of allosteric drugs affecting smooth muscle or related pathways",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Assesses cardiovascular impact",
        "Allosteric Research Area": "Physiological Modeling"
    },
    {
        "Name": "quantify_corneal_nerve_fibers",
        "Source File": "pathology.py",
        "Short Description": "Measures nerve fiber changes potentially caused by allosteric modulation of neuronal pathways; indicates drug impact on nerve health",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Assesses nervous system impact",
        "Allosteric Research Area": "Physiological Modeling"
    },
    {
        "Name": "analyze_bone_microct_morphometry",
        "Source File": "pathology.py",
        "Short Description": "Assesses bone microarchitecture changes following treatment with allosteric modulators targeting bone metabolism pathways",
        "Allosteric Function": "Indirect",
        "Allosteric Relevance": "Detects skeletal effects",
        "Allosteric Research Area": "Physiological Modeling"
    },
    {
    "Name": "validate_allosteric_sites_with_biolip",
    "Source File": "allosteric.py",
    "Short Description": "Validates computationally predicted allosteric binding sites by comparing against known catalytic sites in BioLiP database",
    "Allosteric Function": "Direct",
    "Allosteric Relevance": "Site validation and druggability assessment",
    "Allosteric Research Area": "Computational Drug Discovery"
    }
]

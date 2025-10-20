# Data lake dictionary with detailed descriptions
data_lake_dict = {
    "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation.",
    "affinity_capture-ms.parquet": "Protein-protein interactions detected via affinity capture and mass spectrometry.",
    "affinity_capture-rna.parquet": "Protein-RNA interactions detected by affinity capture.",
    "BindingDB_All_202409.tsv": "Measured binding affinities between proteins and small molecules for drug discovery.",
    "broad_repurposing_hub_molecule_with_smiles.parquet": "Molecules from Broad Institute's Drug Repurposing Hub with SMILES annotations.",
    "broad_repurposing_hub_phase_moa_target_info.parquet": "Drug phases, mechanisms of action, and target information from Broad Institute.",
    "CovInDB_All.csv": "Covalent inhibitors with reactive warheads, target proteins, and bioactivity data for covalent drug design.",
    "co-fractionation.parquet": "Protein-protein interactions from co-fractionation experiments.",
    "czi_census_datasets_v4.parquet": "Datasets from the Chan Zuckerberg Initiative's Cell Census.",
    "DepMap_CRISPRGeneDependency.csv": "Gene dependency probability estimates for cancer cell lines, including all DepMap models.",
    "DepMap_CRISPRGeneEffect.csv": "Genome-wide CRISPR gene effect estimates for cancer cell lines, including all DepMap models.",
    "DepMap_Model.csv": "Metadata describing all cancer models/cell lines which are referenced by a dataset contained within the DepMap portal.",
    "DepMap_OmicsExpressionProteinCodingGenesTPMLogp1.csv": "Gene expression in TPMs for cancer cell lines, including all DepMap models.",
    "ddinter_alimentary_tract_metabolism.csv": "Drug-drug interactions for alimentary tract and metabolism drugs from DDInter 2.0 database.",
    "ddinter_antineoplastic.csv": "Drug-drug interactions for antineoplastic and immunomodulating agents from DDInter 2.0 database.",
    "ddinter_antiparasitic.csv": "Drug-drug interactions for antiparasitic products from DDInter 2.0 database.",
    "ddinter_blood_organs.csv": "Drug-drug interactions for blood and blood forming organs drugs from DDInter 2.0 database.",
    "ddinter_dermatological.csv": "Drug-drug interactions for dermatological drugs from DDInter 2.0 database.",
    "ddinter_hormonal.csv": "Drug-drug interactions for systemic hormonal preparations from DDInter 2.0 database.",
    "ddinter_respiratory.csv": "Drug-drug interactions for respiratory system drugs from DDInter 2.0 database.",
    "ddinter_various.csv": "Drug-drug interactions for various drugs from DDInter 2.0 database.",
    "DisGeNET.parquet": "Gene-disease associations from multiple sources.",
    "dosage_growth_defect.parquet": "Gene dosage changes affecting growth.",
    "enamine_cloud_library_smiles.pkl": "Compounds from Enamine REAL library with SMILES annotations.",
    "evebio_assay_table.csv": "Assay metadata with one row per assay from EveBio pharmome mapping.",
    "evebio_bundle_table.csv": "Target subfamily bundles used for screening-to-profiling progression.",
    "evebio_compound_table.csv": "Compound metadata with common identifiers from EveBio screening.",
    "evebio_control_table.csv": "Control datapoints for all screening and profiling plates.",
    "evebio_detailed_result_table.csv": "Expanded results on evebio_summary_result_table with curve fit parameters and phase categories.",
    "evebio_observed_points_table.csv": "Raw observed datapoints from all screening and profiling experiments.",
    "evebio_summary_result_table.csv": "Succinct summary of results for each assay-compound combination.",
    "evebio_target_table.csv": "Target metadata with common identifiers from EveBio screening.",
    "genebass_missense_LC_filtered.pkl": "Filtered missense variants from GeneBass.",
    "genebass_pLoF_filtered.pkl": "Predicted loss-of-function variants from GeneBass.",
    "genebass_synonymous_filtered.pkl": "Filtered synonymous variants from GeneBass.",
    "gene_info.parquet": "Comprehensive gene information.",
    "genetic_interaction.parquet": "Genetic interactions between genes.",
    "go-plus.json": "Gene ontology data for functional gene annotations.",
    "gtex_tissue_gene_tpm.parquet": "Gene expression (TPM) across human tissues from GTEx.",
    "gwas_catalog.pkl": "Genome-wide association studies (GWAS) results.",
    "hp.obo": "Official HPO release in obographs format",
    "kg.csv": "Precision medicine knowledge graph with 17,080 diseases and 4+ million relationships across biological scales.",
    "marker_celltype.parquet": "Cell type marker genes for identification.",
    "McPAS-TCR.parquet": "T-cell receptor sequences and specificity data from McPAS database.",
    "miRDB_v6.0_results.parquet": "Predicted microRNA targets from miRDB.",
    "miRTarBase_microRNA_target_interaction.parquet": "Experimentally validated microRNA-target interactions from miRTarBase.",
    "miRTarBase_microRNA_target_interaction_pubmed_abtract.txt": "PubMed abstracts for microRNA-target interactions in miRTarBase.",
    "miRTarBase_MicroRNA_Target_Sites.parquet": "Binding sites of microRNAs on target genes from miRTarBase.",
    "mousemine_m1_positional_geneset.parquet": "Positional gene sets from MouseMine.",
    "mousemine_m2_curated_geneset.parquet": "Curated gene sets from MouseMine.",
    "mousemine_m3_regulatory_target_geneset.parquet": "Regulatory target gene sets from MouseMine.",
    "mousemine_m5_ontology_geneset.parquet": "Ontology-based gene sets from MouseMine.",
    "mousemine_m8_celltype_signature_geneset.parquet": "Cell type signature gene sets from MouseMine.",
    "mousemine_mh_hallmark_geneset.parquet": "Hallmark gene sets from MouseMine.",
    "msigdb_human_c1_positional_geneset.parquet": "Human positional gene sets from MSigDB.",
    "msigdb_human_c2_curated_geneset.parquet": "Curated human gene sets from MSigDB.",
    "msigdb_human_c3_regulatory_target_geneset.parquet": "Regulatory target gene sets from MSigDB.",
    "msigdb_human_c3_subset_transcription_factor_targets_from_GTRD.parquet": "Transcription factor targets from GTRD/MSigDB.",
    "msigdb_human_c4_computational_geneset.parquet": "Computationally derived gene sets from MSigDB.",
    "msigdb_human_c5_ontology_geneset.parquet": "Ontology-based gene sets from MSigDB.",
    "msigdb_human_c6_oncogenic_signature_geneset.parquet": "Oncogenic signatures from MSigDB.",
    "msigdb_human_c7_immunologic_signature_geneset.parquet": "Immunologic signatures from MSigDB.",
    "msigdb_human_c8_celltype_signature_geneset.parquet": "Cell type signatures from MSigDB.",
    "msigdb_human_h_hallmark_geneset.parquet": "Hallmark gene sets from MSigDB.",
    "omim.parquet": "Genetic disorders and associated genes from OMIM.",
    "proteinatlas.tsv": "Protein expression data from Human Protein Atlas.",
    "proximity_label-ms.parquet": "Protein interactions via proximity labeling and mass spectrometry.",
    "reconstituted_complex.parquet": "Protein complexes reconstituted in vitro.",
    "sgRNA_KO_SP_mouse.txt": "sgRNA knockout data for mouse.",
    "sgRNA_KO_SP_human.txt": "sgRNA knockout data for human.",
    "synthetic_growth_defect.parquet": "Synthetic growth defects from genetic interactions.",
    "synthetic_lethality.parquet": "Synthetic lethal interactions.",
    "synthetic_rescue.parquet": "Genetic interactions rescuing phenotypes.",
    "two-hybrid.parquet": "Protein-protein interactions detected by yeast two-hybrid assays.",
    "variant_table.parquet": "Annotated genetic variants table.",
    "Virus-Host_PPI_P-HIPSTER_2020.parquet": "Virus-host protein-protein interactions from P-HIPSTER.",
    "txgnn_name_mapping.pkl": "Name mapping for TXGNN.",
    "txgnn_prediction.pkl": "Prediction data for TXGNN.",
    }

# Updated library_content as a dictionary with detailed descriptions
library_content_dict = {
    # === PYTHON PACKAGES ===
    # Core Bioinformatics Libraries (Python)
    "biopython": "[Python Package] A set of tools for biological computation including parsers for bioinformatics files, access to online services, and interfaces to common bioinformatics programs.",
    "biom-format": "[Python Package] The Biological Observation Matrix (BIOM) format is designed for representing biological sample by observation contingency tables with associated metadata.",
    "scanpy": "[Python Package] A scalable toolkit for analyzing single-cell gene expression data, specifically designed for large datasets using AnnData.",
    "scikit-bio": "[Python Package] Data structures, algorithms, and educational resources for bioinformatics, including sequence analysis, phylogenetics, and ordination methods.",
    "anndata": "[Python Package] A Python package for handling annotated data matrices in memory and on disk, primarily used for single-cell genomics data.",
    "mudata": "[Python Package] A Python package for multimodal data storage and manipulation, extending AnnData to handle multiple modalities.",
    "pyliftover": "[Python Package] A Python implementation of UCSC liftOver tool for converting genomic coordinates between genome assemblies.",
    "biopandas": "[Python Package] A package that provides pandas DataFrames for working with molecular structures and biological data.",
    "biotite": "[Python Package] A comprehensive library for computational molecular biology, providing tools for sequence analysis, structure analysis, and more.",
    # Genomics & Variant Analysis (Python)
    "gget": "[Python Package] A toolkit for accessing genomic databases and retrieving sequences, annotations, and other genomic data.",
    "lifelines": "[Python Package] A complete survival analysis library for fitting models, plotting, and statistical tests.",
    # "scvi-tools": "[Python Package] A package for probabilistic modeling of single-cell omics data, including deep generative models.",
    "gseapy": "[Python Package] A Python wrapper for Gene Set Enrichment Analysis (GSEA) and visualization.",
    "scrublet": "[Python Package] A tool for detecting doublets in single-cell RNA-seq data.",
    "cellxgene-census": "[Python Package] A tool for accessing and analyzing the CellxGene Census, a collection of single-cell datasets. To download a dataset, use the download_source_h5ad function with the dataset id as the argument (856c1b98-5727-49da-bf0f-151bdb8cb056, no .h5ad extension).",
    "hyperopt": "[Python Package] A Python library for optimizing hyperparameters of machine learning algorithms.",
    "scvelo": "[Python Package] A tool for RNA velocity analysis in single cells using dynamical models.",
    "pysam": "[Python Package] A Python module for reading, manipulating and writing genomic data sets in SAM/BAM/VCF/BCF formats.",
    "pyfaidx": "[Python Package] A Python package for efficient random access to FASTA files.",
    "pyranges": "[Python Package] A Python package for interval manipulation with a pandas-like interface.",
    "pybedtools": "[Python Package] A Python wrapper for Aaron Quinlan's BEDTools programs.",
    # "panhumanpy": "A Python package for hierarchical, cross-tissue cell type annotation of human single-cell RNA-seq data",
    # Structural Biology & Drug Discovery (Python)
    "rdkit": "[Python Package] A collection of cheminformatics and machine learning tools for working with chemical structures and drug discovery.",
    "deeppurpose": "[Python Package] A deep learning library for drug-target interaction prediction and virtual screening.",
    "pyscreener": "[Python Package] A Python package for virtual screening of chemical compounds.",
    "openbabel": "[Python Package] A chemical toolbox designed to speak the many languages of chemical data, supporting file format conversion and molecular modeling.",
    "descriptastorus": "[Python Package] A library for computing molecular descriptors for machine learning applications in drug discovery.",
    # "pymol": "[Python Package] A molecular visualization system for rendering and animating 3D molecular structures.",
    "openmm": "[Python Package] A toolkit for molecular simulation using high-performance GPU computing.",
    "pytdc": "[Python Package] A Python package for Therapeutics Data Commons, providing access to machine learning datasets for drug discovery.",
    # Data Science & Statistical Analysis (Python)
    "pandas": "[Python Package] A fast, powerful, and flexible data analysis and manipulation library for Python.",
    "numpy": "[Python Package] The fundamental package for scientific computing with Python, providing support for arrays, matrices, and mathematical functions.",
    "scipy": "[Python Package] A Python library for scientific and technical computing, including modules for optimization, linear algebra, integration, and statistics.",
    "scikit-learn": "[Python Package] A machine learning library featuring various classification, regression, and clustering algorithms.",
    "matplotlib": "[Python Package] A comprehensive library for creating static, animated, and interactive visualizations in Python.",
    "seaborn": "[Python Package] A statistical data visualization library based on matplotlib with a high-level interface for drawing attractive statistical graphics.",
    "statsmodels": "[Python Package] A Python module for statistical modeling and econometrics, including descriptive statistics and estimation of statistical models.",
    "pymc3": "[Python Package] A Python package for Bayesian statistical modeling and probabilistic machine learning.",
    # "pystan": "[Python Package] A Python interface to Stan, a platform for statistical modeling and high-performance statistical computation.",
    "umap-learn": "[Python Package] Uniform Manifold Approximation and Projection, a dimension reduction technique.",
    "faiss-cpu": "[Python Package] A library for efficient similarity search and clustering of dense vectors.",
    "harmony-pytorch": "[Python Package] A PyTorch implementation of the Harmony algorithm for integrating single-cell data.",
    # General Bioinformatics & Computational Utilities (Python)
    "tiledb": "[Python Package] A powerful engine for storing and analyzing large-scale genomic data.",
    "tiledbsoma": "[Python Package] A library for working with the SOMA (Stack of Matrices) format using TileDB.",
    "h5py": "[Python Package] A Python interface to the HDF5 binary data format, allowing storage of large amounts of numerical data.",
    "tqdm": "[Python Package] A fast, extensible progress bar for loops and CLI applications.",
    "joblib": "[Python Package] A set of tools to provide lightweight pipelining in Python, including transparent disk-caching and parallel computing.",
    "opencv-python": "[Python Package] OpenCV library for computer vision tasks, useful for image analysis in biological contexts.",
    "PyPDF2": "[Python Package] A library for working with PDF files, useful for extracting text from scientific papers.",
    "googlesearch-python": "[Python Package] A library for performing Google searches programmatically.",
    "scikit-image": "[Python Package] A collection of algorithms for image processing in Python.",
    "pymed": "[Python Package] A Python library for accessing PubMed articles.",
    "arxiv": "[Python Package] A Python wrapper for the arXiv API, allowing access to scientific papers.",
    "scholarly": "[Python Package] A module to retrieve author and publication information from Google Scholar.",
    "cryosparc-tools": "[Python Package] Tools for working with cryoSPARC, a platform for cryo-EM data processing.",
    "mageck": "[Python Package] Analysis of CRISPR screen data.",
    "igraph": "[Python Package] Network analysis and visualization.",
    "pyscenic": "[Python Package] Analysis of single-cell RNA-seq data and gene regulatory networks.",
    "cooler": "[Python Package] Storage and analysis of Hi-C data.",
    "trackpy": "[Python Package] Particle tracking in images and video.",
    # "flowcytometrytools": "[Python Package] Analysis and visualization of flow cytometry data.",
    "cellpose": "[Python Package] Cell segmentation in microscopy images.",
    "viennarna": "[Python Package] RNA secondary structure prediction.",
    "PyMassSpec": "[Python Package] Mass spectrometry data analysis.",
    "python-libsbml": "[Python Package] Working with SBML files for computational biology.",
    "cobra": "[Python Package] Constraint-based modeling of metabolic networks.",
    "reportlab": "[Python Package] Creation of PDF documents.",
    "flowkit": "[Python Package] Toolkit for processing flow cytometry data.",
    "hmmlearn": "[Python Package] Hidden Markov model analysis.",
    "msprime": "[Python Package] Simulation of genetic variation.",
    "tskit": "[Python Package] Handling tree sequences and population genetics data.",
    "cyvcf2": "[Python Package] Fast parsing of VCF files.",
    "pykalman": "[Python Package] Kalman filter and smoother implementation.",
    "fanc": "[Python Package] Analysis of chromatin conformation data.",
    "loompy": "A Python implementation of the Loom file format for efficiently storing and working with large omics datasets.",
    "pyBigWig": "A Python library for accessing bigWig and bigBed files for genome browser track data.",
    "pymzml": "A Python module for high-throughput bioinformatics analysis of mass spectrometry data.",
    "optlang": "A Python package for modeling optimization problems symbolically.",
    "FlowIO": "A Python package for reading and writing flow cytometry data files.",
    "FlowUtils": "Utilities for processing and analyzing flow cytometry data.",
    "arboreto": "A Python package for inferring gene regulatory networks from single-cell RNA-seq data.",
    "pdbfixer": "A Python package for fixing problems in PDB files in preparation for molecular simulations.",
    # === R PACKAGES ===
    # Core R Packages for Data Analysis
    "ggplot2": "[R Package] A system for declaratively creating graphics, based on The Grammar of Graphics. Use with subprocess.run(['Rscript', '-e', 'library(ggplot2); ...']).",
    "dplyr": "[R Package] A grammar of data manipulation, providing a consistent set of verbs that help you solve the most common data manipulation challenges. Use with subprocess.",
    "tidyr": "[R Package] A package that helps you create tidy data, where each column is a variable, each row is an observation, and each cell is a single value. Use with subprocess.",
    "readr": "[R Package] A fast and friendly way to read rectangular data like CSV, TSV, and FWF. Use with subprocess.run(['Rscript', '-e', 'library(readr); ...']).",
    "stringr": "[R Package] A cohesive set of functions designed to make working with strings as easy as possible. Use with subprocess calls.",
    "Matrix": "[R Package] A package that provides classes and methods for dense and sparse matrices. Required for Seurat. Use with subprocess calls.",
    # "Rcpp": "[R Package] Seamless R and C++ Integration, allowing R functions to call compiled C++ code. Use with subprocess calls.",
    # "devtools": "[R Package] Tools to make developing R packages easier, including functions to install packages from GitHub. Use with subprocess calls.",
    # "remotes": "[R Package] Install R packages from GitHub, GitLab, Bitbucket, or other remote repositories. Use with subprocess calls.",
    # Bioinformatics R Packages
    "DESeq2": "[R Package] Differential gene expression analysis based on the negative binomial distribution. Use with subprocess.run(['Rscript', '-e', 'library(DESeq2); ...']).",
    "clusterProfiler": "[R Package] A package for statistical analysis and visualization of functional profiles for genes and gene clusters. Use with subprocess calls.",
    # "DADA2": "[R Package] A package for modeling and correcting Illumina-sequenced amplicon errors. Use with subprocess calls.",
    # "xcms": "[R Package] A package for processing and visualization of LC-MS and GC-MS data. Use with subprocess calls.",
    # "FlowCore": "[R Package] Basic infrastructure for flow cytometry data. Use with subprocess calls.",
    "edgeR": "[R Package] Empirical Analysis of Digital Gene Expression Data in R, for differential expression analysis. Use with subprocess calls.",
    "limma": "[R Package] Linear Models for Microarray Data, for differential expression analysis. Use with subprocess calls.",
    "harmony": "[R Package] A method for integrating and analyzing single-cell data across datasets. Use with subprocess calls.",
    "WGCNA": "[R Package] Weighted Correlation Network Analysis for studying biological networks. Use with subprocess calls.",
    # === CLI TOOLS ===
    # Sequence Analysis Tools
    "samtools": "[CLI Tool] A suite of programs for interacting with high-throughput sequencing data. Use with subprocess.run(['samtools', ...]).",
    "bowtie2": "[CLI Tool] An ultrafast and memory-efficient tool for aligning sequencing reads to long reference sequences. Use with subprocess.run(['bowtie2', ...]).",
    "bwa": "[CLI Tool] Burrows-Wheeler Aligner for mapping low-divergent sequences against a large reference genome. Use with subprocess.run(['bwa', ...]).",
    "bedtools": "[CLI Tool] A powerful toolset for genome arithmetic, allowing operations like intersect, merge, count, and complement on genomic features. Use with subprocess.run(['bedtools', ...]).",
    "macs2": "[CLI Tool] Model-based Analysis of ChIP-Seq data, a tool for identifying transcript factor binding sites.",
    # Quality Control and Processing Tools
    "fastqc": "[CLI Tool] A quality control tool for high throughput sequence data. Use with subprocess.run(['fastqc', ...]).",
    "trimmomatic": "[CLI Tool] A flexible read trimming tool for Illumina NGS data. Use with subprocess.run(['trimmomatic', ...]).",
    # Multiple Sequence Alignment and Phylogenetics
    "mafft": "[CLI Tool] A multiple sequence alignment program for unix-like operating systems. Use with subprocess.run(['mafft', ...]).",
    "Homer": "[CLI Tool] Motif discovery and next-gen sequencing analysis.",
    "FastTree": "[CLI Tool] Phylogenetic trees from sequence alignments.",
    "muscle": "[CLI Tool] Multiple sequence alignment tool.",
    # Genetic Analysis Tools
    "plink": "[CLI Tool] A comprehensive toolkit for genome association studies that can perform a range of large-scale analyses in a computationally efficient manner. Use with subprocess.run(['plink', ...]).",
    "plink2": "[CLI Tool] A comprehensive toolkit for genome association studies that can perform a range of large-scale analyses in a computationally efficient manner. Use with subprocess.run(['plink2', ...]).",
    "gcta64": "[CLI Tool] Genome-wide Complex Trait Analysis (GCTA) tool for estimating the proportion of phenotypic variance explained by genome-wide SNPs and analyzing genetic relationships. Use with subprocess.run(['gcta64', ...]).",
    "iqtree2": "[CLI Tool] An efficient phylogenetic software for maximum likelihood analysis with built-in model selection and ultrafast bootstrap. Use with subprocess.run(['iqtree2', ...]).",
    "ADFR": "AutoDock for Receptors suite for molecular docking and virtual screening. ",
    "diamond": "A sequence aligner for protein and translated DNA searches, designed for high performance analysis of big sequence data. ",
    "fcsparser": "A command-line tool for parsing and analyzing flow cytometry standard (FCS) files. ",
    "plannotate": "[CLI Tool] A tool for annotating plasmid sequences with common features. ",
    "vina": "[CLI Tool] An open-source program for molecular docking and virtual screening, known for its speed and accuracy improvements over AutoDock 4.",
    "autosite": "[CLI Tool] A binding site detection tool used to identify potential ligand binding pockets on protein structures for molecular docking.",
}


allosteric_data_lake = {
    "affinity_capture-ms": {
        "name": "Affinity Capture MS",
        "description": "Protein-protein interactions detected via affinity capture and mass spectrometry.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "co-fractionation": {
        "name": "Co-fractionation",
        "description": "Protein-protein interactions from co-fractionation experiments.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "proximity_label-ms": {
        "name": "Proximity Label MS",
        "description": "Protein interactions via proximity labeling and mass spectrometry.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "two-hybrid": {
        "name": "Yeast Two-Hybrid",
        "description": "Protein-protein interactions detected by yeast two-hybrid assays.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "reconstituted_complex": {
        "name": "Reconstituted Complex",
        "description": "Protein complexes reconstituted in vitro.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "virus-host_ppi": {
        "name": "Virus-Host PPI",
        "description": "Virus-host protein-protein interactions from P-HIPSTER.",
        "allosteric_category": ["PPI", "Structural", "Functional"]
    },
    "bindingdb": {
        "name": "BindingDB",
        "description": "Measured binding affinities between proteins and small molecules for drug discovery.",
        "allosteric_category": ["Ligand", "Modulator", "Functional"]
    },
    "broad_repurposing_molecule": {
        "name": "Broad Repurposing Hub Molecules",
        "description": "Molecules from Broad Institute's Drug Repurposing Hub with SMILES annotations.",
        "allosteric_category": ["Ligand", "Modulator"]
    },
    "broad_repurposing_moa_target": {
        "name": "Broad Repurposing MOA & Target Info",
        "description": "Drug phases, mechanisms of action, and target information from Broad Institute.",
        "allosteric_category": ["Ligand", "Modulator", "Target info"]
    },
    "enamine_cloud_library": {
        "name": "Enamine Cloud Library",
        "description": "Compounds from Enamine REAL library with SMILES annotations.",
        "allosteric_category": ["Ligand", "Modulator"]
    },
    "evebio_assay_table": {
        "name": "EveBio Assay Table",
        "description": "Assay metadata with one row per assay from EveBio pharmome mapping.",
        "allosteric_category": ["Assay", "Functional"]
    },
    "evebio_bundle_table": {
        "name": "EveBio Bundle Table",
        "description": "Target subfamily bundles used for screening-to-profiling progression.",
        "allosteric_category": ["Assay", "Target info"]
    },
    "evebio_compound_table": {
        "name": "EveBio Compound Table",
        "description": "Compound metadata with common identifiers from EveBio screening.",
        "allosteric_category": ["Ligand", "Assay", "Functional"]
    },
    "evebio_control_table": {
        "name": "EveBio Control Table",
        "description": "Control datapoints for all screening and profiling plates.",
        "allosteric_category": ["Assay", "Functional"]
    },
    "evebio_detailed_result_table": {
        "name": "EveBio Detailed Result Table",
        "description": "Expanded results on evebio_summary_result_table with curve fit parameters and phase categories.",
        "allosteric_category": ["Assay", "Functional"]
    },
    "evebio_observed_points_table": {
        "name": "EveBio Observed Points Table",
        "description": "Raw observed datapoints from all screening and profiling experiments.",
        "allosteric_category": ["Assay", "Functional"]
    },
    "evebio_summary_result_table": {
        "name": "EveBio Summary Result Table",
        "description": "Succinct summary of results for each assay-compound combination.",
        "allosteric_category": ["Assay", "Functional"]
    },
    "evebio_target_table": {
        "name": "EveBio Target Table",
        "description": "Target metadata with common identifiers from EveBio screening.",
        "allosteric_category": ["Target info", "Functional"]
    },
    "depmap_gene_dependency": {
        "name": "DepMap Gene Dependency",
        "description": "Gene dependency probability estimates for cancer cell lines, including all DepMap models.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "depmap_gene_effect": {
        "name": "DepMap Gene Effect",
        "description": "Genome-wide CRISPR gene effect estimates for cancer cell lines.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "sgRNA_KO_mouse": {
        "name": "sgRNA Knockout Mouse",
        "description": "sgRNA knockout data for mouse.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "sgRNA_KO_human": {
        "name": "sgRNA Knockout Human",
        "description": "sgRNA knockout data for human.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "synthetic_growth_defect": {
        "name": "Synthetic Growth Defect",
        "description": "Gene dosage changes affecting growth.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "synthetic_lethality": {
        "name": "Synthetic Lethality",
        "description": "Synthetic lethal interactions.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "synthetic_rescue": {
        "name": "Synthetic Rescue",
        "description": "Genetic interactions rescuing phenotypes.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "genetic_interaction": {
        "name": "Genetic Interaction",
        "description": "Genetic interactions between genes.",
        "allosteric_category": ["Genetic perturbation", "Functional"]
    },
    "gene_info": {
        "name": "Gene Info",
        "description": "Comprehensive gene information.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "variant_table": {
        "name": "Variant Table",
        "description": "Annotated genetic variants table.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "proteinatlas": {
        "name": "Protein Atlas",
        "description": "Protein expression data from Human Protein Atlas.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "gtex_tissue_gene_tpm": {
        "name": "GTEx Tissue Gene Expression",
        "description": "Gene expression (TPM) across human tissues from GTEx.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "disgenet": {
        "name": "DisGeNET",
        "description": "Gene-disease associations from multiple sources.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "omim": {
        "name": "OMIM",
        "description": "Genetic disorders and associated genes.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "marker_celltype": {
        "name": "Marker Celltype",
        "description": "Cell type marker genes for identification.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "go-plus": {
        "name": "Gene Ontology Plus",
        "description": "Gene ontology data for functional gene annotations.",
        "allosteric_category": ["Functional annotation", "Target info"]
    },
    "miRDB": {
        "name": "miRDB",
        "description": "Predicted microRNA targets from miRDB.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "miRTarBase_interactions": {
        "name": "miRTarBase microRNA Target Interactions",
        "description": "Experimentally validated microRNA-target interactions from miRTarBase.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "miRTarBase_sites": {
        "name": "miRTarBase MicroRNA Target Sites",
        "description": "Binding sites of microRNAs on target genes from miRTarBase.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "mousemine_m1_positional_geneset": {
        "name": "MouseMine M1 Positional Geneset",
        "description": "Positional gene sets from MouseMine.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "mousemine_m2_curated_geneset": {
        "name": "MouseMine M2 Curated Geneset",
        "description": "Curated gene sets from MouseMine.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "mousemine_m3_regulatory_target_geneset": {
        "name": "MouseMine M3 Regulatory Target Geneset",
        "description": "Regulatory target gene sets from MouseMine.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "mousemine_m5_ontology_geneset": {
        "name": "MouseMine M5 Ontology Geneset",
        "description": "Ontology-based gene sets from MouseMine.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "mousemine_m8_celltype_signature_geneset": {
        "name": "MouseMine M8 Celltype Signature Geneset",
        "description": "Cell type signature gene sets from MouseMine.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "mousemine_mh_hallmark_geneset": {
        "name": "MouseMine MH Hallmark Geneset",
        "description": "Hallmark gene sets from MouseMine.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c1_positional_geneset": {
        "name": "MSigDB Human C1 Positional Geneset",
        "description": "Human positional gene sets from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c2_curated_geneset": {
        "name": "MSigDB Human C2 Curated Geneset",
        "description": "Curated human gene sets from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c3_regulatory_target_geneset": {
        "name": "MSigDB Human C3 Regulatory Target Geneset",
        "description": "Regulatory target gene sets from MSigDB.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "msigdb_human_c3_subset_tf_targets": {
        "name": "MSigDB Human C3 Subset TF Targets",
        "description": "Transcription factor targets from GTRD/MSigDB.",
        "allosteric_category": ["Regulatory", "Functional"]
    },
    "msigdb_human_c4_computational_geneset": {
        "name": "MSigDB Human C4 Computational Geneset",
        "description": "Computationally derived gene sets from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c5_ontology_geneset": {
        "name": "MSigDB Human C5 Ontology Geneset",
        "description": "Ontology-based gene sets from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c6_oncogenic_signature_geneset": {
        "name": "MSigDB Human C6 Oncogenic Signature Geneset",
        "description": "Oncogenic signatures from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c7_immunologic_signature_geneset": {
        "name": "MSigDB Human C7 Immunologic Signature Geneset",
        "description": "Immunologic signatures from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_c8_celltype_signature_geneset": {
        "name": "MSigDB Human C8 Celltype Signature Geneset",
        "description": "Cell type signatures from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "msigdb_human_h_hallmark_geneset": {
        "name": "MSigDB Human H Hallmark Geneset",
        "description": "Hallmark gene sets from MSigDB.",
        "allosteric_category": ["Functional annotation", "Pathway"]
    },
    "kg": {
        "name": "Precision Medicine Knowledge Graph",
        "description": "Knowledge graph with 17,080 diseases and 4+ million relationships across biological scales.",
        "allosteric_category": ["Functional annotation", "Pathway", "Regulatory"]
    },
    "ASD_Release_201909_AM": {
        "name": "Allosteric Mutations (AM)",
        "description": "Contains experimentally identified mutations that affect allosteric regulation of proteins, useful for linking sequence changes to functional effects.",
        "allosteric_category": ["Mutation", "Functional", "Structural"]
    },
    "ASD_Release_201909_DR": {
        "name": "Allosteric Drugs (DR)",
        "description": "Lists allosteric modulators and drugs characterized in ASD, including their targets and functional annotations, suitable for pharmacological studies.",
        "allosteric_category": ["Ligand", "Functional", "Pharmacological"]
    },
    "ASD_Release_202306_AP": {
        "name": "AlloSite-Potential (AP)",
        "description": "Predicted potential allosteric sites for human proteins, derived from computational models, providing candidates for experimental validation.",
        "allosteric_category": ["Site Prediction", "Structural", "Functional"]
    },
    "ASD_Release_202306_HL": {
        "name": "Hit-to-Lead Records (HL)",
        "description": "Contains hit-to-lead optimization data for allosteric modulators, useful for medicinal chemistry and lead development.",
        "allosteric_category": ["Ligand", "Functional", "Drug Discovery"]
    },
    "ASD_Release_202208_AS": {
        "name": "Allosteric Sites (AS)",
        "description": "Comprehensive experimentally determined allosteric sites of proteins, providing residue-level information on binding pockets and ligand interactions.",
        "allosteric_category": ["Site", "Structural", "Functional"]
    },
    "ASD_Release_202309_PP": {
        "name": "Allosteric Protein-Protein Interactions (PP)",
        "description": "Allosteric modulators affecting protein-protein interactions, detailing targets and functional effects relevant to signaling and complex formation.",
        "allosteric_category": ["PPI", "Functional", "Structural"]
    }

}

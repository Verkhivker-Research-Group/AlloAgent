# The new tools and the new data

Dated note 2026-11-05.  Everything here was read out of the repository;
where a fact is not recorded, it says **not found** instead of a guess.

The reference point for "upstream" is the pinned upstream Biomni commit
in `PINNED_UPSTREAM` (`400c1f366b96a35ca253e13c9b06c5076af41d65`).  The
upstream tool functions are the public functions of the upstream
implementation modules `biomni/tool/*.py` at that commit
(`git grep -h -E "^def [A-Za-z_][A-Za-z0-9_]*" 400c1f3 -- "biomni/tool/*.py"`
-> 229 public functions).

## Part 1 - the tools

### How the tool set is built (the runtime registry, not a file count)

The runtime registry of an arm is built in three steps:

1. `biomni/utils.py::read_module2api` reads the **22 upstream
   `biomni/tool/tool_description/<topic>.py` modules** - that is the
   upstream tool set (the `description` list of each module).
2. `biomni/tool/schema_generator.py::discover_tool_functions` walks every
   `biomni/tool/<topic>.py` implementation module and takes its **public
   functions**; `biomni/tool/_registration.py::_describe_missing_tools`
   (lines 83-102) adds the entries for the exposed tools that the
   upstream description modules do not carry - that is how our new tools
   enter the registry.
3. `biomni/tool/_registration.py::apply_exposed_tools` (line 105) filters
   the registry down to the names in `alloagent/exposed_tools.txt`
   (the path is `biomni/tool/_registration.py` line 24); everything else
   stays registered but is not exposed.

### The counts

| item | count |
|---|---:|
| the exposed tools (`alloagent/exposed_tools.txt`, the names on lines 25-94) | **45** |
| **new**: not present in the upstream Biomni at `400c1f3` | **44** |
| **modified upstream**: present upstream and changed by us | **1** (`run_python_repl`) |
| **unchanged upstream**: present upstream and identical to upstream | **0** |

`run_python_repl` lives in `biomni/tool/support_tools.py` upstream (1
occurrence at `400c1f3`) and is **modified** here: the upstream function
is 1,114 characters, ours is 2,677, and the difference is the import
restriction (the `set_restricted_imports` policy: a blocked module is
refused by a static scan *and* by the importer installed for the
duration of the execution).

The 44 new tools are listed below with their group, the question the
tool answers (from its tool card), the backend and the version, and
whether the tool came from my original tool set or was added during the
rebuild (the git history).

**The modified-upstream tools are not listed** (there is one:
`run_python_repl`).

| `map_residues_uniprot_pdb` | structural analysis | "Given a PDB ID, what UniProt accession does it map to, and which chains + residue ranges are covered?" Also: "Given a UniProt accession, which PDB structures are the best (highest-coverage, highest-identity) structures  | - upstream URL: `https://www.ebi.ac.uk/pdbe/api/mappings/` - pinned release tag: PDBe mappings API v1 - license: EMBL-EBI terms of use | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `map_pdb_to_best_structures` | structural analysis | not found | not found | unknown |
| `get_uniprot_variants` | database access | "Given a UniProt accession, what sequence-altering variants are annotated on the canonical protein sequence, and at what positions?" | - upstream URL: `https://www.ebi.ac.uk/proteins/api/features?accession=<acc>&types=VARIANT` - pinned release: EBI Proteins API v1 - license: EMBL-EBI terms of u | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `get_stingallo_allosteric_residues` | ML-based prediction | "Given a PDB ID, what allosteric residues are annotated on the structure, and on which chain?" | - upstream URL: `https://www.stingallo.cbi.cnptia.embrapa.br/api/afrs?pdb_id=<pdb>&chain_id=<chain>` - release: STINGAllo (SITE-DIRECTED ALlosteric Residues in  | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `detect_pockets_fpocket` | structural analysis | "Given a PDB structure, what are its ligand-binding pockets (as predicted by fpocket 4.2.3), and what are their druggability scores and the residues lining each pocket?" | - upstream URL: `https://github.com/Discngine/fpocket` (pinned tag: `4.2.3` or `v4.2.3`) - license: MIT - checksum: recorded in `docs/tool_cards/T4_fpocket_chec | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `detect_pockets_p2rank` | structural analysis | "Given a PDB structure, what are its predicted binding pockets per P2Rank 2.5.1, and which residues line each pocket?" | - upstream URL: `https://github.com/rdk/p2rank` (pinned tag: `2.5.1`) - license: GPL-3.0 - Java: 17 (the function asserts Java is on PATH or uses JAVA_HOME) | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `normal_mode_analysis` | dynamics and network analysis | "Given a PDB structure, what are its dominant low-frequency normal modes (ANM or GNM), and what residues move together?" | ProDy 2.6.1 (`https://github.com/prody/proDy`, MIT license). The wrapper calls `prody.calcModes(n_modes=N, zeros=True)` so the trivial near-zero modes are retur | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `residue_contact_network` | dynamics and network analysis | "Given a PDB structure, what is the contact graph between residues (heavy atoms within 4.5 Å), what are the betweenness-centrality scores, what are the residue communities, and what is the shortest path between two resid | - upstream: Biotite 1.6.0 (mmCIF parser) + NetworkX 3.6.1 - license: BSD-3-Clause (both) | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `search_pdb_by_uniprot_and_ligand` | structural analysis | "Which PDB entries have a polymer entity with the given UniProt accession AND a chemical component with the given ligand ID?" | - upstream URL: `https://search.rcsb.org/rcsbsearch/v2/query` - API docs: `https://search.rcsb.org/redoc/index.html` - API version: RCSB Search API v2 (current  | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `get_clinvar_variants` | database access | "What are the ClinVar-annotated variants for a given gene symbol (optionally filtered by clinical significance)?" The wrapper has two modes, local pinned (default) and live: - **Local mode (default when the file is prese | - upstream URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` - API docs: `https://www.ncbi.nlm.nih.gov/books/NBK25500/` - API version: NCBI E-utilities (cur | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `get_alphamissense_score` | database access | "What is the AlphaMissense pathogenicity score and class for missense variants in a given UniProt accession (optionally at a specific protein position)?" | - upstream URL: `https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz` - paper: Cheng et al. 2023, "Accurate proteome-wide miss | my original tool set (the T-series allosteric evaluation tools, October 2026) |
| `get_chembl_bioactivity` | database access | not found | not found | unknown |
| `dock_ligand_vina` | dynamics and network analysis | "What are the docked poses and Vina energies when a small molecule (from SMILES) is docked against a receptor (from PDB) using AutoDock Vina?" | - upstream URL: `https://vina.scripps.edu/` - Vina: 1.2.7 (the `vina` Python binding, the validated path; the Vina CLI is not in the image) - RDKit: 2024.09.6 - | my original tool set (the B-series baseline tools, October 2026) |
| `pocketminer_score` | ML-based prediction | not found | not found | unknown |
| `get_ligand_contacts` | structural analysis | "Which polymer residues of this PDB entry lie within a distance cutoff of the named ligand?" | - coordinates: `https://files.rcsb.org/download/<pdb_id>.cif` (mmCIF) - SIFTS alignment: `https://data.rcsb.org/rest/v1/core/polymer_entity/<pdb_id>/<entity_id> | added during the rebuild (2026-10-24, commit 8ead898: "P32: add the get_ligand_contacts tool") |
| `allosteric_site_workflow` | structural analysis | not found | not found | unknown |
| `pdb_to_uniprot` | structural analysis | Which UniProt accession does each chain of a given PDB entry map to? | - upstream URL: PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<pdb_id>`; no release tag, live service | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `uniprot_to_pdb` | structural analysis | Which PDB entries are known for a given UniProt accession? | - upstream URL: PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/mappings/all_isoforms/<uniprot_id>`; live service | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `cross_reference_ligands_chembl_pubchem` | structural analysis | What do ChEMBL and PubChem record about a named ligand? | - upstream URL: ChEMBL 37 web service via `chembl_webresource_client`; PubChem PUG REST via `pubchempy`; live services | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `cross_reference_ligands` | structural analysis | Which local ligand datasets have a record for each of these ligands, and what do those records say? | - upstream URL: BioLiP, ASD AP/DR/XF, and the ChEMBL 37 + PubChem web services, depending on `databases` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `map_covalent_probes_to_allosteric` | structural analysis | Where do covalent probes attach to a target, and is each attachment site orthosteric-like or an allosteric candidate? | - upstream URL: CovInDB (CovalentInDB) `CovInDB_All.csv`, mounted read-only from the Biolab data lake (17,774 rows in this snapshot) | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `analyze_site_patterns` | structural analysis | How often does each residue site, and each residue type, occur in a set of covalent-probe records? | - upstream URL: pure computation over the caller's own records; no external source | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `parse_biolip_interactions` | database access | Which ligand-protein interactions does the BioLiP snapshot record for a PDB entry and chain? | - upstream URL: BioLiP `biolip.pkl` snapshot, 989,058 rows, mounted read-only from the Biolab data lake | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `biolip_ligands` | database access | Which ligands are bound in a given PDB entry (and chain)? | - upstream URL: BioLiP `biolip.pkl` snapshot (989,058 rows), read-only mount | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `biolip_protein` | database access | What protein sequence does the BioLiP snapshot store for a PDB entry and chain? | - upstream URL: BioLiP `protein.pkl` snapshot (512,101 rows), read-only mount | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `biolip_dna` | database access | What DNA sequence does the BioLiP snapshot store for a PDB entry and chain? | - upstream URL: BioLiP `dna.pkl` snapshot (23,734 rows), read-only mount | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `biolip_rna` | database access | What RNA sequence does the BioLiP snapshot store for a PDB entry and chain? | - upstream URL: BioLiP `rna.pkl` snapshot (18,920 rows), read-only mount | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `biolip_peptide` | database access | What peptide sequence does the BioLiP snapshot store for a PDB entry and chain? | - upstream URL: BioLiP `peptide.pkl` snapshot (30,668 rows), read-only mount | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `parse_asd_xf` | database access | Which allosteric sites and modulators does the Allosteric Database record for a protein? | - upstream URL: ASD (Allosteric Database) `ASD_Release_202306_XF` XML files, 2,419 files over 2,412 proteins, mounted read-only at `/biolab_data`; protein -> fi | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `load_asd_2d` | database access | What 2D chemical structure does the Allosteric Database ship for a protein's modulators? | - upstream URL: ASD `ASD_Release_202306_2D` MOL files, 99,961 files, mounted read-only at `/biolab_data` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `load_asd_3d` | database access | What 3D chemical structure does the Allosteric Database ship for a protein's modulators? | - upstream URL: ASD `ASD_Release_202306_3D` MOL2 files, 99,959 files, mounted read-only at `/biolab_data` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `retrieve_and_filter_large_dataset` | database access | Which rows of a large CSV dataset match a filter? | - upstream URL: any local CSV; the Biolab data lake is mounted read-only at /biolab_data | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `convert_uniprot_to_asd` | database access | What is the Allosteric Database file id for a UniProt accession? | - upstream URL: ASD protein index, 2,412 proteins, committed as `biomni/tool/_asd_index.tsv` and generated from the real `ASD_Release_202306_XF` directory | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `convert_asd_to_uniprot` | database access | What is the UniProt accession for an Allosteric Database file id? | - upstream URL: ASD protein index (`biomni/tool/_asd_index.tsv`) | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `normalize_protein_id` | database access | Given either a UniProt accession or an ASD file id, what are both forms? | - upstream URL: ASD protein index (`biomni/tool/_asd_index.tsv`) | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `allosteric_hotspot_detection` | dynamics and network analysis | Which residues of a protein are acted on by several modulators? | - upstream URL: ASD `ASD_Release_202309_AS.csv` (3,102 rows), mounted read-only at `/biolab_data` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `residue_interaction_networks` | dynamics and network analysis | What residue-interaction network connects the curated allosteric sites of a protein? | - upstream URL: ASD XF XML files plus, optionally, BioLiP and PPI parquet files; all mounted read-only at `/biolab_data` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `allosteric_evidence` | dynamics and network analysis | Does the Allosteric Database confirm that this protein has curated allosteric sites? | - upstream URL: ASD `ASD_Release_202306_XF` XML files, mounted read-only at `/biolab_data` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `load_pdb` | structural analysis | Can the structure for a PDB id be fetched and parsed? | - upstream URL: RCSB `https://files.rcsb.org/download/<id>.pdb` | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `structural_distance` | structural analysis | How far do the candidate residues sit from the active-site residues? | - upstream URL: RCSB PDB structures; heavy-atom coordinates from the parsed entry | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `pocket_geometry` | structural analysis | What is the volume, extent and shape of the region the candidate residues span? | - upstream URL: RCSB PDB structures; convex hull over the candidate heavy atoms | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `residue_accessibility` | structural analysis | How exposed and how hydrophobic are the candidate residues? | - upstream URL: RCSB PDB structures; Shrake-Rupley SASA with the Tien et al. 2013 maximum-SASA table; Kyte-Doolittle hydropathy | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `evolutionary_conservation` | dynamics and network analysis | What conservation surrogate score does each candidate residue get? | - upstream URL: UniProt FASTA (`https://www.uniprot.org/uniprot/<acc>.fasta`) plus the deterministic entropy surrogate | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |
| `set_restricted_imports` | neither (a policy tool, not an analysis) | Which module prefixes must the Python REPL refuse to import? | - upstream URL: no external source; a process-level setting | my original tool set, ported into biomni (the P-series port batches of 2026-10-23) |

### The registered but NOT exposed new tools

The new tools that the runtime registry carries but that the exposed list
leaves out (they stay callable by an explicit import):

| tool | module | why it is not exposed |
|---|---|---|
| `ae_pocketminer_score` | `biomni/tool/ae_pocketminer.py` | the "AE" variant of the PocketMiner scorer; it is not in the exposed list and no card is recorded for it (**not found**) |
| `fetch_allosteric_residue_potential` | `biomni/tool/allosteric.py` | it reads the live STINGAllo service; the exposed list keeps the curated T3 tool instead (`alloagent/exposed_tools.txt`, the rules at the top of the file) |
| `out_path_size_zero` | `biomni/tool/dock_ligand_vina.py` | a helper of the Vina wrapper, not a tool of its own |
| `predict_complex_boltz2` | `biomni/tool/predict_complex_boltz2.py` | the GPU Boltz-2 path: it needs the GPU tool env, which arm D does not get |
| `query_opentarget_genetics` | `biomni/tool/database.py` | "the OpenTargets Genetics API host no longer resolves" (`alloagent/exposed_tools.txt`, the rules at the top of the file) |
| `sample_conformations_bioemu` | `biomni/tool/sample_conformations_bioemu.py` | the GPU BioEmu path: it needs the GPU tool env, which arm D does not get |

(The reasons for the last two are the header of `alloagent/exposed_tools.txt`;
the first, the third and the fourth are recorded in the source and in
the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md), and no card is committed for them.)

## Part 2 - the data

### How the data reaches the tools

| where | what |
|---|---|
| the image | the image (`alloagent-eval:v6`) carries the **code** and the public binaries; the Dockerfile has **no** data copy of the ASD, of BioLiP or of the curated releases |
| the HF dataset | the data bundle (`Biolab/scripts/build_data_bundle.py`) packs the upstream Biomni data lake plus the extra sources, and the **ASD is excluded** (`build_data_bundle.py` lines 42-43: `"asd",  # user fetches ASD separately (per-request licensing)`) |
| the user | the ASD is fetched **by hand** (`Biolab/DATA.md` lines 37-57), and the local releases (ChEMBL 37, ClinVar, AlphaMissense) are fetched by their own scripts (`biomni/tool/get_clinvar_variants.py` line 12 names `scripts/fetch_clinvar.py --download --out <dir>`) |
| the mounts | at run time the curated lake is mounted read-only at `/biolab_data` and the local releases at `/data/<name>` (`biomni/tool/asd.py` lines 19-20, `biomni/tool/get_chembl_bioactivity.py` line 27, `biomni/tool/get_clinvar_variants.py` line 39) |

### The sources, one line each

| source | what it is | the tools that read it | where it is | the licence / terms recorded in the repository |
|---|---|---|---|---|
| **ASD** (Allosteric Database) | the curated allosteric sites and modulators, with the XF functional files and the 2D/3D structures of the modulators | `parse_asd_xf`, `load_asd_2d`, `load_asd_3d`, `convert_uniprot_to_asd`, `convert_asd_to_uniprot`, `normalize_protein_id`, `allosteric_hotspot_detection`, `residue_interaction_networks`, `allosteric_evidence`, `cross_reference_ligands` | the Biolab data lake (`data/biomni_data/asd`), mounted read-only at `/biolab_data`; **excluded from the uploaded bundle**, fetched by the user | "Academic use, registration required." (`Biolab/scripts/build_data_bundle.py` line 152; `Biolab/DATA.md` line 39: the upstream licence requires per-request registration) |
| **BioLiP** | the protein-ligand interaction database (a snapshot with the interactions, the proteins, the DNA, the RNA and the peptides) | `parse_biolip_interactions`, `biolip_ligands`, `biolip_protein`, `biolip_dna`, `biolip_rna`, `biolip_peptide` | the Biolab data lake (`data/biomni_data/biolip`), read-only at `/biolab_data`; in the bundle | "Free for academic use." (`build_data_bundle.py` line 156) |
| **ChEMBL 37** | the ChEMBL 37 SQLite release (the local copy the bioactivity tool reads) | `get_chembl_bioactivity`, `cross_reference_ligands_chembl_pubchem` | the image mount `/data/chembl/chembl_37_sqlite/chembl_37.db` (`biomni/tool/get_chembl_bioactivity.py` line 27); the live ChEMBL web service otherwise | **not recorded** in the third-party licence list of `build_data_bundle.py` (lines 143-176) |
| **ClinVar** | the NCBI ClinVar variant summary (the local release) | `get_clinvar_variants` | the image mount `/data/clinvar/variant_summary.txt.gz` (`biomni/tool/get_clinvar_variants.py` line 39); fetched by `scripts/fetch_clinvar.py --download` (named at line 12) | **not recorded** in `build_data_bundle.py` |
| **AlphaMissense** | the DeepMind pathogenicity scores per substitution | `get_alphamissense_score` | the local release; the upstream file is `https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz` (the tool card `docs/tool_cards/T10_get_alphamissense_score.md`) | **not recorded** in `build_data_bundle.py` |
| **CovInDB** | the covalent-probe attachment sites (17,774 rows in this snapshot) | `map_covalent_probes_to_allosteric`, `analyze_site_patterns` | the Biolab data lake, read-only at `/biolab_data` | **not recorded** in `build_data_bundle.py` |
| **the PDB structures** | the RCSB entries and the structure cache the tools parse | every structural tool (`load_pdb`, `get_ligand_contacts`, the pocket detectors, `structural_distance`, ...) | live from RCSB (`https://files.rcsb.org/download/<id>.cif`) and the cache mounted at `/data/structures` | **not recorded** in `build_data_bundle.py` |
| **the upstream Biomni data lake** | the 76 curated upstream datasets (the `data_lake_dict` of `biomni/env_desc.py` at `400c1f3`, line 50): BindingDB, DepMap, DisGeNET, BioGRID, GTEx, EveBio, the DDInter tables, the co-fractionation and affinity-capture parquets, ... | the upstream tools | the bundle, and copied into the Biolab lake as `data/biomni_data/data_lake` | the third-party list of `build_data_bundle.py` (lines 143-176): BioLiP free for academic use; BioGRID free for academic use, citation required; DepMap CC-BY-4.0; BindingDB CC-BY-3.0; GTEx dbGaP controlled access, summary data public; DisGeNET CC-BY-NC-4.0; EveBio per upstream agreement, academic use only; ASD academic use, registration required |

### How many datasets differ from the upstream data lake

The upstream Biomni data lake has **76** datasets (the `data_lake_dict`
of `biomni/env_desc.py` at `400c1f3`, line 50).  **Seven sources are
ours** (they are not in the upstream lake and they are what the AlloAgent
tools read):

1. the **ASD** (the Allosteric Database),
2. **BioLiP**,
3. the **ChEMBL 37** local SQLite release,
4. the **ClinVar** local release,
5. the **AlphaMissense** local release,
6. **CovInDB** (the covalent probes),
7. the **structure cache** (the cached PDB entries the tools parse).

The upstream lake itself is carried unchanged (the `data_lake` folder of
the Biolab lake) and the extra sources that the upstream lake does not
have are the seven above.

"""Generate the tool cards for the ported allosteric/biolip tools.

The per-function content (question, what it does NOT answer, inputs,
outputs, source, runtime, determinism, failure modes, known answer,
negative control) is written by hand in CARDS below; this script only
renders the markdown scaffold so every card has the same required
sections. Re-run it after editing CARDS.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _paths import expand_home  # noqa: E402

REPO = expand_home(r"<HOME>\Documents\CPSC\AlloAgent-v2")
OUT = REPO / "docs" / "tool_cards"

CARDS = {
    "P1_pdb_to_uniprot": {
        "title": "P1 pdb_to_uniprot",
        "q": "Which UniProt accession does each chain of a given PDB entry map to?",
        "notq": ("It does not say whether the structure is an allosteric or an "
                 "orthosteric form, and it does not list residues in contact "
                 "with a ligand."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id, case-insensitive"),
        ],
        "outputs": ("`data` is `{pdb_id, chains: {chain: [uniprot, ...]}, "
                    "uniprot_ids: [str, ...], mappings: [{chain_id, uniprot_id, "
                    "unp_start, unp_end}, ...]}`."),
        "source": ("PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/"
                   "mappings/uniprot/<pdb_id>`; no release tag, live service"),
        "runtime": ("typical latency 0.2-1 s; 30 s HTTP timeout; one request "
                    "per call; online"),
        "determ": ("deterministic for a given PDB id while the PDBe mapping "
                   "set is unchanged"),
        "failures": [
            "pdb_id not 4 characters -> `success=False`, error names the 4-character requirement",
            "network failure -> `success=False`, error starts `PDBe request failed`",
            "non-JSON body -> `success=False`, error starts `PDBe returned invalid JSON`",
        ],
        "ka": ("input `1TIM` -> `chains` contains `A` and `B`, both mapping to "
               "`P00940`; `uniprot_ids == [\"P00940\"]`"),
        "ka_src": "PDBe live response, 2026-10-23 (see docs/2_port_batch1_allosteric_known_answers.md A-1)",
        "nc": ("input `ZZZZ` (well-formed, no such entry) -> `success=True`, "
               "`chains == {}`, `uniprot_ids == []`"),
        "code": "biomni/tool/allosteric.py::pdb_to_uniprot",
    },
    "P2_uniprot_to_pdb": {
        "title": "P2 uniprot_to_pdb",
        "q": "Which PDB entries are known for a given UniProt accession?",
        "notq": ("It does not say which entry shows a particular conformational "
                 "state, and it does not indicate whether any of them is "
                 "allosteric."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession, case-insensitive"),
        ],
        "outputs": ("`data` is `{uniprot_id, pdb_ids: [str, ...], total: int}`; "
                    "`pdb_ids` is sorted."),
        "source": ("PDBe SIFTS mappings API, `https://www.ebi.ac.uk/pdbe/api/"
                   "mappings/all_isoforms/<uniprot_id>`; live service"),
        "runtime": ("typical latency 0.2-1 s; 30 s HTTP timeout; one request "
                    "per call; online"),
        "determ": ("deterministic for a given accession while the PDBe mapping "
                   "set is unchanged"),
        "failures": [
            "empty accession -> `success=False`",
            "network failure -> `success=False`, error starts `PDBe request failed`",
            "non-JSON body -> `success=False`, error starts `PDBe returned invalid JSON`",
        ],
        "ka": ("input `P04637` -> 321 entries; the first ten sorted are "
               "`1A1U, 1AIE, 1C26, 1DT7, 1GZH, 1H26, 1HS5, 1JSP, 1KZY, 1MA3`"),
        "ka_src": "PDBe live response, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-5)",
        "nc": ("input `P05142` (mouse TIM, no PDB entry) -> `success=True`, "
               "`pdb_ids == []`"),
        "code": "biomni/tool/allosteric.py::uniprot_to_pdb",
    },
    "P3_cross_reference_ligands_chembl_pubchem": {
        "title": "P3 cross_reference_ligands_chembl_pubchem",
        "q": "What do ChEMBL and PubChem record about a named ligand?",
        "notq": ("It does not say whether the ligand is an allosteric or an "
                 "orthosteric binder of the target, and it does not give an "
                 "activity measurement against that target."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession of the target"),
            ("ligands", "list", "yes", "-", "list of dicts with a `ligand_name` key"),
            ("detail_level", "str", "no", "\"slim\"", "`\"slim\"` for curated fields, `\"full\"` for raw records"),
        ],
        "outputs": ("`data` is `{protein_id, ligands: [{name, chembl_id, "
                    "chembl_synonyms, chembl_properties, chembl_structure, "
                    "chembl_classification, chembl_approval, pubchem_cid}], "
                    "total, detail_level}`."),
        "source": ("ChEMBL 37 web service via `chembl_webresource_client`; "
                   "PubChem PUG REST via `pubchempy`; live services"),
        "runtime": ("typical latency 1-3 s per ligand; 30 s client timeout; "
                    "online; one ChEMBL and one PubChem call per ligand"),
        "determ": ("partial: ChEMBL and PubChem rankings can change, and the "
                   "ChEMBL match is the first of a name-similarity search"),
        "failures": [
            "a ligand that matches nothing -> that entry carries `error`; the other ligands are still returned",
            "ChEMBL or PubChem exception -> that entry carries `error` naming the lookup",
            "empty ligand list -> `success=True` with `ligands == []`",
        ],
        "ka": ("input `P04637` + `[{\"ligand_name\": \"imatinib\"}]` -> "
               "`chembl_id == \"CHEMBL941\"`, formula `C29H31N7O`, molecular "
               "weight `493.62`, inchi_key `KTUFNOKKBVMGRW-UHFFFAOYSA-N`, "
               "`max_phase == 4.0`, `first_approval == 2001`, `pubchem_cid == 5291`"),
        "ka_src": "ChEMBL 37 + PubChem live responses, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-8)",
        "nc": ("input `P04637` + `[{\"ligand_name\": \"zzzznotacomound\"}]` -> "
               "`success=True`, that entry carries `error`"),
        "code": "biomni/tool/allosteric.py::cross_reference_ligands_chembl_pubchem",
    },
    "P4_map_covalent_probes_to_allosteric": {
        "title": "P4 map_covalent_probes_to_allosteric",
        "q": "Where do covalent probes attach to a target, and is each attachment site orthosteric-like or an allosteric candidate?",
        "notq": ("It does not predict an allosteric site. It reports observed "
                 "covalent-probe attachment sites and labels them with "
                 "residue-type rules; a site labelled `Allosteric_Candidate` is "
                 "a candidate, not a call."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession, matched against the `Target` column"),
            ("dataset_path", "str", "no", "\"/biolab_data/data_lake/CovInDB_All.csv\"", "path to CovInDB_All.csv; override with `ALLOAGENT_COVINDB`"),
        ],
        "outputs": ("`data` is `{uniprot_id, total_entries, records, columns, "
                    "war_head_counts, unique_inchi_keys}`. Each record carries the "
                    "CovInDB columns plus `Parsed_Sites`, `Allosteric_Candidate`, "
                    "`Site_Count` and `Confidence`."),
        "source": ("CovInDB (CovalentInDB) `CovInDB_All.csv`, mounted read-only "
                   "from the Biolab data lake (17,774 rows in this snapshot)"),
        "runtime": ("typical latency 1-3 s (reads and filters the 18 MB CSV); "
                    "offline; no network"),
        "determ": "deterministic for a given dataset snapshot",
        "failures": [
            "dataset file missing -> `success=False`, error names the missing path",
            "CSV unreadable -> `success=False`, error starts `could not read`",
            "no `Target` column -> `success=False`, error lists the columns found",
        ],
        "ka": ("input `P00519` -> 23 entries, every `Target_Gene == \"ABL1\"`, "
               "every `Site == \"NT\"`, `war_head_counts == {\"Michael Acceptor\": 21, "
               "\"Halohydrocarbon\": 2}`, `unique_inchi_keys == 6`"),
        "ka_src": "CovInDB_All.csv, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-12)",
        "nc": ("input `P04637` -> `success=True` with `total_entries == 0`"),
        "code": "biomni/tool/allosteric.py::map_covalent_probes_to_allosteric",
    },
    "P5_analyze_site_patterns": {
        "title": "P5 analyze_site_patterns",
        "q": "How often does each residue site, and each residue type, occur in a set of covalent-probe records?",
        "notq": ("It does not decide whether a site is allosteric and it does "
                 "not test the records for anything; it only counts."),
        "inputs": [
            ("sites", "DataFrame|list|dict", "yes", "-", "a DataFrame with a `Parsed_Sites` column, a list of records, or the `data` dict from `map_covalent_probes_to_allosteric`"),
        ],
        "outputs": ("`data` is `{total_unique_sites, most_common_sites: "
                    "[[site, count], ...], residue_distribution: [[residue, count], ...], "
                    "total_entries}`."),
        "source": "pure computation over the caller's own records; no external source",
        "runtime": "typical latency under 0.1 s; offline",
        "determ": "deterministic",
        "failures": [
            "input is not a DataFrame / list / dict -> `success=False`, error names the accepted types",
        ],
        "ka": ("input records with `Parsed_Sites` = `[[\"NT\"], [\"CYS-481\"], "
               "[\"SER-195\"]]` -> `total_unique_sites == 3`, `total_entries == 3`, "
               "`most_common_sites[0] == [\"NT\", 1]`, residue distribution contains "
               "`[\"CYS\", 1]` and `[\"SER\", 1]`"),
        "ka_src": "hand-computed expectation, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-15)",
        "nc": ("a DataFrame with no `Parsed_Sites` column -> `success=True`, "
               "`total_unique_sites == 0`"),
        "code": "biomni/tool/allosteric.py::analyze_site_patterns",
    },
    "P6_fetch_allosteric_residue_potential": {
        "title": "P6 fetch_allosteric_residue_potential",
        "q": "Which residues does STINGAllo list as allosteric for a PDB entry and chain?",
        "notq": ("It does not say whether a residue is allosteric in a "
                 "particular conformational transition, and it does not rank "
                 "the residues."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id"),
            ("chain_id", "str", "no", "None", "optional chain id"),
        ],
        "outputs": ("`data` is `{pdb_id, chain_id, residues: [...], "
                    "`merged_into: \"get_stingallo_allosteric_residues\"}`."),
        "source": ("STINGAllo API, `https://stingallo.cbi.cnptia.embrapa.br/api/"
                   "afrs`; the same endpoint as the verified T3 tool"),
        "runtime": ("typical latency 0.5-2 s; 30 s HTTP timeout; STINGAllo "
                    "limits 100 requests/IP/day and 30 unique PDBs/IP/day, "
                    "enforced by the shared T3 counter; online"),
        "determ": "deterministic for a given entry while the STINGAllo data is unchanged",
        "failures": [
            "daily request or unique-PDB limit reached -> `success=False`, error states the limit",
            "upstream HTTP error -> `success=False` with the upstream message",
        ],
        "ka": ("the returned `residues` list is identical to "
               "`get_stingallo_allosteric_residues(pdb_id, chain_id)` for the "
               "same inputs"),
        "ka_src": ("MERGE into T3 (docs/2_port_batch1_allosteric_known_answers.md "
                   "A-22); T3's own known-answer test is the authority"),
        "nc": ("an empty `pdb_id` -> `success=False`"),
        "code": "biomni/tool/allosteric.py::fetch_allosteric_residue_potential",
    },
    "P7_parse_biolip_interactions": {
        "title": "P7 parse_biolip_interactions",
        "q": "Which ligand-protein interactions does the BioLiP snapshot record for a PDB entry and chain?",
        "notq": ("It does not say which ligand modulates the target, and it "
                 "does not score the affinity."),
        "inputs": [
            ("pdb_id", "str", "no", "None", "4-character (or 12) PDB id; None returns the whole table"),
            ("chain", "str", "no", "None", "optional chain id"),
        ],
        "outputs": ("`data` is `{pdb_id, chain, total, records, columns}`; the "
                    "records carry the BioLiP interaction columns (PDB, Chain, "
                    "Ligand, UniProt_ID, ...)."),
        "source": ("BioLiP `biolip.pkl` snapshot, 989,058 rows, mounted "
                   "read-only from the Biolab data lake"),
        "runtime": ("first call loads the 265 MB pickle (several seconds); "
                    "later calls in the same process are in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `1GG1`, chain `A` -> `total == 2`"),
        "ka_src": "biolip.pkl, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-21)",
        "nc": ("input `1TIM` -> `success=True` with `total == 0`; 1TIM is absent "
               "from the BioLiP snapshot"),
        "code": "biomni/tool/biolip.py::parse_biolip_interactions",
    },
    "P8_biolip_ligands": {
        "title": "P8 biolip_ligands",
        "q": "Which ligands are bound in a given PDB entry (and chain)?",
        "notq": ("It does not say whether a ligand is an allosteric or an "
                 "orthosteric binder, and it does not give the binding "
                 "affinity."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character (or 12) PDB id"),
            ("chain", "str", "no", "None", "optional chain id"),
        ],
        "outputs": ("`data` is `{pdb_id, chain, ligands: [str, ...], "
                    "total_interactions: int, chains: [str, ...], "
                    "uniprot_ids: [str, ...]}`."),
        "source": "BioLiP `biolip.pkl` snapshot (989,058 rows), read-only mount",
        "runtime": ("first call loads the 265 MB pickle (several seconds); "
                    "later calls are in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `1GG1` -> `ligands == [\"MN\", \"PGA\"]`, "
               "`total_interactions == 8`, `chains == [\"A\",\"B\",\"C\",\"D\"]`, "
               "`uniprot_ids == [\"P0AB91\"]`"),
        "ka_src": "biolip.pkl, 2026-10-23 (docs/2_port_batch1_allosteric_known_answers.md A-17)",
        "nc": ("input `1TIM` -> `success=True` with `ligands == []` and "
               "`total_interactions == 0`"),
        "code": "biomni/tool/biolip.py::biolip_ligands",
    },
    "P9_biolip_protein": {
        "title": "P9 biolip_protein",
        "q": "What protein sequence does the BioLiP snapshot store for a PDB entry and chain?",
        "notq": ("It does not verify the stored sequence against the current "
                 "PDB entry, and it does not say which residues bind a ligand."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character (or 12) PDB id"),
            ("chain", "str", "no", "None", "optional chain id"),
        ],
        "outputs": ("`data` is `{pdb_id, chain, kind, total, records, columns}`; "
                    "each record carries `identifier`, `chain`, `type`, "
                    "`uniprot_id`, `length`, `sequence`."),
        "source": "BioLiP `protein.pkl` snapshot (512,101 rows), read-only mount",
        "runtime": ("first call loads the 164 MB pickle (several seconds); "
                    "later calls are in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `1A1K` -> `total == 1`; the record's `identifier` is "
               "`1a1kA` and its sequence is 85 residues beginning "
               "`RPYACPVESCDRRFSRSADLTRHIRIHTGQKPFQCRICMRNFSRSDHLTTHIRTHTGEKP`"),
        "ka_src": "protein.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-1)",
        "nc": ("input `1A1K`, chain `B` -> `success=True` with `total == 0`"),
        "code": "biomni/tool/biolip.py::biolip_protein",
    },
    "P10_biolip_dna": {
        "title": "P10 biolip_dna",
        "q": "What DNA sequence does the BioLiP snapshot store for a PDB entry and chain?",
        "notq": ("It does not verify the stored sequence against the current "
                 "PDB entry, and it does not say which nucleotides bind a ligand."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character (or 12) PDB id"),
            ("chain", "str", "no", "None", "optional chain id (single letter)"),
        ],
        "outputs": ("`data` is `{pdb_id, chain, kind, total, records, columns}`."),
        "source": "BioLiP `dna.pkl` snapshot (23,734 rows), read-only mount",
        "runtime": ("first call loads the 1.6 MB pickle; later calls are "
                    "in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "chain longer than one letter -> `success=False`, error says the DNA chain must be a single letter",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `1A1K` -> `total == 2`, identifiers `1a1k_dna_B` and "
               "`1a1k_dna_C`; the first record's sequence is `agcgtgggacc` (11 bases)"),
        "ka_src": "dna.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-4)",
        "nc": ("input `1A1K`, chain `BC` -> `success=False` with an error "
               "naming the single-letter requirement"),
        "code": "biomni/tool/biolip.py::biolip_dna",
    },
    "P11_biolip_rna": {
        "title": "P11 biolip_rna",
        "q": "What RNA sequence does the BioLiP snapshot store for a PDB entry and chain?",
        "notq": ("It does not verify the stored sequence against the current "
                 "PDB entry, and it does not say which nucleotides bind a ligand."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character (or 12) PDB id"),
            ("chain", "str", "no", "None", "optional chain id (1-2 letters)"),
        ],
        "outputs": "`data` is `{pdb_id, chain, kind, total, records, columns}`.",
        "source": "BioLiP `rna.pkl` snapshot (18,920 rows), read-only mount",
        "runtime": ("first call loads the 12 MB pickle; later calls are "
                    "in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "chain longer than two letters -> `success=False`, error says the RNA chain must be 1-2 letters",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `8A3W` -> `total == 10`; the first identifier is "
               "`8a3w_rna_S1` and that record's sequence is 1663 nucleotides long"),
        "ka_src": "rna.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-7)",
        "nc": ("input `8A3W`, chain `S1` -> `success=True` with `total == 1` "
               "and identifier `8a3w_rna_S1`"),
        "code": "biomni/tool/biolip.py::biolip_rna",
    },
    "P12_biolip_peptide": {
        "title": "P12 biolip_peptide",
        "q": "What peptide sequence does the BioLiP snapshot store for a PDB entry and chain?",
        "notq": ("It does not verify the stored sequence against the current "
                 "PDB entry, and it does not say which residues bind a ligand."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character (or 12) PDB id"),
            ("chain", "str", "no", "None", "optional chain id (single letter)"),
        ],
        "outputs": "`data` is `{pdb_id, chain, kind, total, records, columns}`.",
        "source": "BioLiP `peptide.pkl` snapshot (30,668 rows), read-only mount",
        "runtime": ("first call loads the 1.9 MB pickle; later calls are "
                    "in-memory; offline"),
        "determ": "deterministic for a given snapshot",
        "failures": [
            "pdb_id not 4 or 12 characters -> `success=False`",
            "chain longer than one letter -> `success=False`, error says the peptide chain must be a single letter",
            "data file missing -> `success=False`, error names the missing path",
        ],
        "ka": ("input `4A1G` -> `total == 4` with identifiers `4a1g_peptide_E`, "
               "`4a1g_peptide_F`, `4a1g_peptide_G`, `4a1g_peptide_H`; the first "
               "record's sequence is `KIDTTSFLANLK` (12 residues)"),
        "ka_src": "peptide.pkl, 2026-10-23 (docs/2_port_batch1b_biolip_sequences_known_answers.md B-9)",
        "nc": ("input `4A1G`, chain `E` -> `success=True` with `total == 1`"),
        "code": "biomni/tool/biolip.py::biolip_peptide",
    },
    "P13_parse_asd_xf": {
        "title": "P13 parse_asd_xf",
        "q": "Which allosteric sites and modulators does the Allosteric Database record for a protein?",
        "notq": ("It does not predict an allosteric site and it does not score "
                 "the sites; it reports the curated ASD record."),
        "inputs": [
            ("target_proteins", "list", "no", "None", "UniProt accessions to extract; None extracts all 2,412 indexed proteins"),
        ],
        "outputs": ("`data` is `{proteins: {<uniprot_id>: {protein_metadata, "
                    "sites, modulators}}, total_proteins, requested}`."),
        "source": ("ASD (Allosteric Database) `ASD_Release_202306_XF` XML files, "
                   "2,419 files over 2,412 proteins, mounted read-only at "
                   "`/biolab_data`; protein -> file map committed as "
                   "`biomni/tool/_asd_index.tsv`"),
        "runtime": ("a few milliseconds per protein (one XML file each); the "
                    "protein -> file map is a committed TSV, so no directory "
                    "scan is needed; offline"),
        "determ": "deterministic for a given ASD snapshot",
        "failures": [
            "ASD XF directory missing -> `success=False`, error names the missing directory",
            "target_proteins not a list -> `success=False`",
            "an accession that is not in the index -> simply absent from the result",
        ],
        "ka": ("input `[\"P0AB91\"]` -> one protein; `gene_name == \"aroG\"`; "
               "1 site with `pdb_id == \"1KFL\"`, `pdb_site == \"1KFL-1\"`, "
               "`feature == \"Inhibitor\"`, `function == \"Inner Protein Regulator\"`; "
               "5 modulators, the first `ASD00020003` (drugbank `No`) and the "
               "fourth `ASD02170001` (drugbank `Yes`)"),
        "ka_src": "ASD_Release_202306_XF, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-1..D-5)",
        "nc": ("input `[\"P51639\"]` -> 0 sites and 1 modulator "
               "(`ASD00030001`, feature `Activator`)"),
        "code": "biomni/tool/asd.py::parse_asd_xf",
    },
    "P14_load_asd_2d": {
        "title": "P14 load_asd_2d",
        "q": "What 2D chemical structure does the Allosteric Database ship for a protein's modulators?",
        "notq": ("It does not say whether a modulator is an allosteric or an "
                 "orthosteric binder, and it does not give the binding affinity."),
        "inputs": [
            ("protein_ids", "list", "yes", "-", "UniProt accessions to look up"),
            ("modulator_ids", "list", "no", "None", "optional ASD modulator ids to restrict the result to"),
        ],
        "outputs": ("`data` is `{modulators: {<asd_id>: {name, formula, "
                    "atom_count, bond_count, smiles}}, total_modulators}`."),
        "source": ("ASD `ASD_Release_202306_2D` MOL files, 99,961 files, "
                   "mounted read-only at `/biolab_data`"),
        "runtime": "a few milliseconds per modulator; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": [
            "protein_ids not a list -> `success=False`",
            "a protein with no curated site -> an empty `modulators` dict, not an error",
        ],
        "ka": ("input `[\"P0AB91\"]` -> modulator `ASD02170001` with "
               "`name == \"ASD02170001.mol\"`, `atom_count == 12`, "
               "`bond_count == 12`, `formula == \"C9NO2\"`"),
        "ka_src": "ASD_Release_202306_2D, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-8)",
        "nc": ("input `[\"P0AB91\"]` with `modulator_ids=[\"ASD00320001\"]` -> the "
               "site's modulator is `ASD02170001`, so the filtered result is empty"),
        "code": "biomni/tool/asd.py::load_asd_2d",
    },
    "P15_load_asd_3d": {
        "title": "P15 load_asd_3d",
        "q": "What 3D chemical structure does the Allosteric Database ship for a protein's modulators?",
        "notq": ("It does not say whether a modulator is an allosteric or an "
                 "orthosteric binder, and it does not give the binding pose in "
                 "the protein."),
        "inputs": [
            ("protein_ids", "list", "yes", "-", "UniProt accessions to look up"),
            ("modulator_ids", "list", "no", "None", "optional ASD modulator ids to restrict the result to"),
        ],
        "outputs": ("`data` is `{modulators: {<asd_id>: {atoms, coordinates, "
                    "bonds, atom_count, bond_count}}, total_modulators}`."),
        "source": ("ASD `ASD_Release_202306_3D` MOL2 files, 99,959 files, "
                   "mounted read-only at `/biolab_data`"),
        "runtime": "a few milliseconds per modulator; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": [
            "protein_ids not a list -> `success=False`",
            "a protein with no curated site -> an empty `modulators` dict, not an error",
        ],
        "ka": ("input `[\"P0AB91\"]` -> modulator `ASD02170001` with "
               "`atom_count == 23` and `bond_count == 23`; its first atom is "
               "`{id: \"1\", name: \"C1\", x: 5.6138, y: -1.2175, z: 3.0667, "
               "type: \"C.ar\"}` and its first bond is "
               "`{id: \"1\", atom1: \"1\", atom2: \"2\", type: \"ar\"}`"),
        "ka_src": "ASD_Release_202306_3D, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-9)",
        "nc": ("input `[\"P51639\"]` -> `data.modulators == {}`; P51639 has no "
               "curated allosteric site and therefore no site-level modulator"),
        "code": "biomni/tool/asd.py::load_asd_3d",
    },
    "P16_cross_reference_ligands": {
        "title": "P16 cross_reference_ligands",
        "q": "Which local ligand datasets have a record for each of these ligands, and what do those records say?",
        "notq": ("It does not answer whether a ligand is an allosteric or an "
                 "orthosteric binder, and it does not give a binding affinity."),
        "inputs": [
            ("pdb_id", "str", "no", "None", "PDB id, used for the BioLiP lookup"),
            ("uniprot_id", "str", "no", "None", "UniProt accession, used for the ASD AP and ASD XF lookups"),
            ("ligands", "list", "no", "None", "explicit ligand names; None derives them from `pdb_id` via BioLiP"),
            ("databases", "list", "no", "None", "dataset ids: biolip, asd_ap, asd_dr, asd_xf, chembl_pubchem"),
            ("detail_level", "str", "no", "\"slim\"", "`\"slim\"` or `\"full\"`; passed to the ChEMBL/PubChem lookup"),
            ("use_llm", "bool", "no", "False", "best-effort LLM summary of the counts"),
        ],
        "outputs": ("`data` is `{query, databases, results: [{ligand, "
                    "provenance, data}], summary: {total_ligands, per_database}, "
                    "llm_summary, metadata}`."),
        "source": ("BioLiP, ASD AP/DR/XF, and the ChEMBL 37 + PubChem web "
                   "services, depending on `databases`"),
        "runtime": ("BioLiP and ASD reads are in-memory after the first call; "
                    "the ChEMBL/PubChem branch is one network call per ligand; "
                    "offline unless `chembl_pubchem` is requested"),
        "determ": ("deterministic for a given snapshot, except the "
                   "ChEMBL/PubChem branch whose rankings can change"),
        "failures": [
            "no ligands, no uniprot_id and no pdb_id -> `success=False`, error says there is nothing to cross-reference",
            "unknown database id -> `success=False`, error lists the supported ids",
            "detail_level other than slim/full -> `success=False`",
        ],
        "ka": ("`pdb_id=\"1GG1\"`, `databases=[\"biolip\"]` -> 2 results, "
               "ligands `MN` and `PGA`, each with `provenance == [\"biolip\"]` "
               "and a non-empty `data.biolip`"),
        "ka_src": "BioLiP 1gg1, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-12)",
        "nc": ("`uniprot_id=\"P41240\"`, `databases=[\"asd_ap\"]` -> the result "
               "carries `provenance == [\"asd_ap\"]` with 16 AP rows, the first "
               "with `pdb_id == \"1BYG\"` and `score == 0.535`"),
        "code": "biomni/tool/cross_reference.py::cross_reference_ligands",
    },
    "P17_retrieve_and_filter_large_dataset": {
        "title": "P17 retrieve_and_filter_large_dataset",
        "q": "Which rows of a large CSV dataset match a filter?",
        "notq": ("It does not answer anything about the biology in the file; "
                 "it only reports the matching rows."),
        "inputs": [
            ("filepath", "str", "yes", "-", "path to the CSV file"),
            ("columns_to_load", "list", "no", "None", "columns to read; None reads every column"),
            ("filter_column", "str", "no", "None", "column to filter on"),
            ("filter_value", "str", "no", "None", "value to match in `filter_column` (case-insensitive substring)"),
        ],
        "outputs": ("`data` is `{data: [ {<column>: <value>} ], metadata: "
                    "{filepath, columns_loaded, columns_requested, filter_applied, "
                    "rows_returned, status}, filter_summary}`."),
        "source": "any local CSV; the Biolab data lake is mounted read-only at /biolab_data",
        "runtime": ("one to a few seconds for an 18 MB CSV; the filter is applied "
                    "after the read; offline"),
        "determ": "deterministic for a given file",
        "failures": [
            "file missing -> `success=False`; `data.metadata.status == \"error\"` and the error names the path",
            "unreadable CSV -> `success=False`; `data.metadata.status == \"error\"`",
            "no matching rows -> `success=True`; `data.metadata.status == \"no_matches\"` and `rows_returned == 0`",
        ],
        "ka": ("the real `CovInDB_All.csv` with `filter_column=\"Target\"` and "
               "`filter_value=\"P00519\"` -> `rows_returned == 23`, "
               "`status == \"success\"`, and every record's `Target_Gene` is "
               "`\"ABL1\"`"),
        "ka_src": "CovInDB_All.csv, 2026-10-23 (docs/2_port_batch2_asd_crossref_known_answers.md D-16)",
        "nc": ("the same file with `filter_value=\"P04637\"` -> `rows_returned == 0` "
               "and `status == \"no_matches\"`"),
        "code": "biomni/tool/cross_reference.py::retrieve_and_filter_large_dataset",
    },
    "P18_convert_uniprot_to_asd": {
        "title": "P18 convert_uniprot_to_asd",
        "q": "What is the Allosteric Database file id for a UniProt accession?",
        "notq": ("It does not say whether the protein has curated allosteric "
                 "sites, and it does not name the modulators."),
        "inputs": [("uniprot_id", "str", "yes", "-", "UniProt accession")],
        "outputs": "`data` is `{uniprot_id, asd_id}`; `asd_id` is null when the accession is not in ASD.",
        "source": ("ASD protein index, 2,412 proteins, committed as "
                   "`biomni/tool/_asd_index.tsv` and generated from the real "
                   "`ASD_Release_202306_XF` directory"),
        "runtime": "under a millisecond; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": ["empty accession -> `success=False`"],
        "ka": "input `P0AB91` -> `asd_id == \"ASD00020000_1\"`",
        "ka_src": "ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-1)",
        "nc": "input `P99999` -> `asd_id` is null",
        "code": "biomni/tool/allosteric2.py::convert_uniprot_to_asd",
    },
    "P19_convert_asd_to_uniprot": {
        "title": "P19 convert_asd_to_uniprot",
        "q": "What is the UniProt accession for an Allosteric Database file id?",
        "notq": ("It does not say whether the protein has curated allosteric "
                 "sites, and it does not name the modulators."),
        "inputs": [("asd_id", "str", "yes", "-", "ASD file id, e.g. `ASD00020000_1`")],
        "outputs": "`data` is `{asd_id, uniprot_id}`; `uniprot_id` is null when the id is not in ASD.",
        "source": "ASD protein index (`biomni/tool/_asd_index.tsv`)",
        "runtime": "a few milliseconds; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": ["empty id -> `success=False`"],
        "ka": "input `ASD00020000_1` -> `uniprot_id == \"P0AB91\"`",
        "ka_src": "ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-2)",
        "nc": "input `ASD99999999_1` -> `uniprot_id` is null",
        "code": "biomni/tool/allosteric2.py::convert_asd_to_uniprot",
    },
    "P20_normalize_protein_id": {
        "title": "P20 normalize_protein_id",
        "q": "Given either a UniProt accession or an ASD file id, what are both forms?",
        "notq": "It does not answer anything about the protein's allosteric sites.",
        "inputs": [("protein_id", "str", "yes", "-", "a UniProt accession or an ASD file id")],
        "outputs": "`data` is `{protein_id, uniprot_id, asd_id, found}`.",
        "source": "ASD protein index (`biomni/tool/_asd_index.tsv`)",
        "runtime": "a few milliseconds; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": ["empty id -> `success=False`"],
        "ka": ("input `P0AB91` and input `ASD00020000_1` both give "
               "`uniprot_id == \"P0AB91\"` and `asd_id == \"ASD00020000_1\"`"),
        "ka_src": "ASD index, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-3, E-4)",
        "nc": "input `P99999` -> both ids null and `found` is false",
        "code": "biomni/tool/allosteric2.py::normalize_protein_id",
    },
    "P21_allosteric_hotspot_detection": {
        "title": "P21 allosteric_hotspot_detection",
        "q": "Which residues of a protein are acted on by several modulators?",
        "notq": ("It does not predict an allosteric site. It ranks residues "
                 "that the curated ASD AS table already lists; a residue "
                 "called a hotspot is one that several modulators act on."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession or ASD id"),
            ("celltype_data_path", "str", "no", "None", "optional parquet of tissue marker genes"),
            ("min_modulator_count", "int", "no", "3", "minimum modulator observations before a residue is a candidate"),
            ("percentile_threshold", "float", "no", "75.0", "percentile above which a candidate is called a hotspot"),
            ("asd_as_path", "str", "no", "None", "path to `ASD_Release_202309_AS.csv`"),
        ],
        "outputs": ("`data` is `{uniprot_id, asd_id, hotspots, hotspot_count, "
                    "residue_scores, candidate_count, percentile_threshold_value, "
                    "data_sources, summary}`."),
        "source": ("ASD `ASD_Release_202309_AS.csv` (3,102 rows), mounted "
                   "read-only at `/biolab_data`"),
        "runtime": "a second or two to read the 3,102-row CSV; offline",
        "determ": "deterministic for a given ASD AS snapshot",
        "failures": [
            "a protein outside the ASD index -> `success=False`",
            "the ASD AS file missing -> `success=False`, error lists the missing column",
        ],
        "ka": ("input `P00533` with `min_modulator_count=2` -> 1 hotspot, "
               "residue `\"6P1D\"`, `importance_score == 0.62`, "
               "`modulator_count == 2`, `unique_modulators == 1`"),
        "ka_src": "ASD_Release_202309_AS.csv, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-6)",
        "nc": ("input `P04150` with `min_modulator_count=2` -> 0 candidates; "
               "P04150 has no rows in the ASD AS file"),
        "code": "biomni/tool/allosteric2.py::allosteric_hotspot_detection",
    },
    "P22_residue_interaction_networks": {
        "title": "P22 residue_interaction_networks",
        "q": "What residue-interaction network connects the curated allosteric sites of a protein?",
        "notq": ("It does not assert that any pathway transmits a signal; it "
                 "reports the network built from the curated sites and its "
                 "topology."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession or ASD id"),
            ("pdb_id", "str", "no", "None", "optional PDB id, used to add BioLiP contact residues"),
            ("ppi_data_path", "str", "no", "None", "optional directory of PPI parquet files"),
            ("min_interactions", "int", "no", "2", "minimum edge weight to include"),
        ],
        "outputs": ("`data` is `{uniprot_id, asd_id, allosteric_sites, "
                    "network_nodes, network_edges, communication_pathways, "
                    "network_metrics, data_sources, summary}`."),
        "source": ("ASD XF XML files plus, optionally, BioLiP and PPI "
                   "parquet files; all mounted read-only at `/biolab_data`"),
        "runtime": "a second or two; offline",
        "determ": "deterministic for a given snapshot",
        "failures": ["a protein outside the ASD index -> `success=False`"],
        "ka": ("input `P0AB91` -> 1 allosteric site, 13 residue nodes, "
               "`total_edges == 0`, `density == 0.0`, "
               "`allosteric_node_count == 13`, `data_sources == [\"ASD_XF\"]`"),
        "ka_src": "ASD XF, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-10)",
        "nc": "input `P99999` -> `success=False`",
        "code": "biomni/tool/allosteric2.py::residue_interaction_networks",
    },
    "P23_load_pdb": {
        "title": "P23 load_pdb",
        "q": "Can the structure for a PDB id be fetched and parsed?",
        "notq": "It does not answer anything about allostery; it only loads the structure.",
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id"),
            ("query_pdb_identifiers", "callable", "no", "None", "optional downloader, tried before RCSB"),
        ],
        "outputs": "`data` is `{pdb_id, atom_count, residue_count, chains, source}`.",
        "source": "RCSB `https://files.rcsb.org/download/<id>.pdb`",
        "runtime": "a few hundred milliseconds; online",
        "determ": "deterministic for a given PDB entry",
        "failures": [
            "RCSB returns a non-200 -> `success=False`, error states the status",
            "network error -> `success=False`, error starts `RCSB download failed`",
        ],
        "ka": "input `1CRN` -> 327 atoms, 46 residues, chains `[\"A\"]`",
        "ka_src": "RCSB 1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-16)",
        "nc": "input `ZZZZ` -> `success=False`",
        "code": "biomni/tool/allosteric_verification_tools.py::load_pdb",
    },
    "P24_structural_distance": {
        "title": "P24 structural_distance",
        "q": "How far do the candidate residues sit from the active-site residues?",
        "notq": ("It does not say whether the candidate residues are "
                 "allosteric; it only measures the heavy-atom distance."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id"),
            ("candidate_residues", "list", "yes", "-", "list of `(chain_id, residue_number)` pairs"),
            ("active_residues", "list", "yes", "-", "list of `(chain_id, residue_number)` pairs"),
            ("query_pdb_identifiers", "callable", "no", "None", "optional downloader"),
        ],
        "outputs": "`data` is `{pdb_id, score, avg_distance, all_distances, summary}`.",
        "source": "RCSB PDB structures; heavy-atom coordinates from the parsed entry",
        "runtime": "a few hundred milliseconds; online",
        "determ": "deterministic for a given PDB entry",
        "failures": [
            "structure cannot be loaded -> `success=False`",
            "a residue is missing from the structure -> `success=False` naming the counts",
        ],
        "ka": ("input `1CRN`, candidate `[(\"A\", 10)]`, active `[(\"A\", 40)]` -> "
               "`avg_distance == 5.49`, `all_distances == [5.49]`, `score == 0.3`"),
        "ka_src": "1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-17)",
        "nc": ("a residue number outside the structure -> `success=False`"),
        "code": "biomni/tool/allosteric_verification_tools.py::structural_distance",
    },
    "P25_pocket_geometry": {
        "title": "P25 pocket_geometry",
        "q": "What is the volume, extent and shape of the region the candidate residues span?",
        "notq": ("It does not say whether the region is a binding pocket; it "
                 "only measures the geometry of the candidate residues."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id"),
            ("candidate_residues", "list", "yes", "-", "list of `(chain_id, residue_number)` pairs"),
            ("query_pdb_identifiers", "callable", "no", "None", "optional downloader"),
        ],
        "outputs": "`data` is `{pdb_id, score, volume, max_extent, asphericity, shape_score_pmi, summary}`.",
        "source": "RCSB PDB structures; convex hull over the candidate heavy atoms",
        "runtime": "a few hundred milliseconds; online",
        "determ": "deterministic for a given PDB entry",
        "failures": [
            "structure cannot be loaded -> `success=False`",
            "fewer than three heavy atoms -> `success=False` naming the count",
        ],
        "ka": ("input `1CRN` with residues A/10..A/19 -> `volume == 928.3`, "
               "`max_extent == 18.74`, `asphericity == 0.21`, "
               "`shape_score_pmi == 1.0`, `score == 1.0`"),
        "ka_src": "1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-18)",
        "nc": ("a residue list with one residue -> `success=False` naming the "
               "insufficient atom count"),
        "code": "biomni/tool/allosteric_verification_tools.py::pocket_geometry",
    },
    "P26_residue_accessibility": {
        "title": "P26 residue_accessibility",
        "q": "How exposed and how hydrophobic are the candidate residues?",
        "notq": ("It does not say whether the residues are allosteric; it "
                 "only measures accessibility and hydropathy."),
        "inputs": [
            ("pdb_id", "str", "yes", "-", "4-character PDB id"),
            ("candidate_residues", "list", "yes", "-", "list of `(chain_id, residue_number)` pairs"),
            ("query_pdb_identifiers", "callable", "no", "None", "optional downloader"),
        ],
        "outputs": "`data` is `{pdb_id, score, avg_rsasa, avg_hydrophobicity, summary}`.",
        "source": ("RCSB PDB structures; Shrake-Rupley SASA with the Tien "
                   "et al. 2013 maximum-SASA table; Kyte-Doolittle hydropathy"),
        "runtime": "a few seconds (the SASA is computed over the whole model); online",
        "determ": "deterministic for a given PDB entry",
        "failures": [
            "structure cannot be loaded -> `success=False`",
            "no residue could be analysed -> `success=False`",
        ],
        "ka": ("input `1CRN` with A/10, A/20, A/30 -> `avg_rsasa == 27.16`, "
               "`avg_hydrophobicity == -1.87`, `score == 0.772`"),
        "ka_src": "1CRN, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-19)",
        "nc": "a residue number outside the structure -> `success=False`",
        "code": "biomni/tool/allosteric_verification_tools.py::residue_accessibility",
    },
    "P27_evolutionary_conservation": {
        "title": "P27 evolutionary_conservation",
        "q": "What conservation surrogate score does each candidate residue get?",
        "notq": ("**It does not measure sequence conservation.** It builds no "
                 "alignment and consults no ortholog database; it evaluates a "
                 "deterministic pseudo-MSA entropy model. Treat the score as a "
                 "reproducible stand-in, never as evidence of conservation."),
        "inputs": [
            ("uniprot_id", "str", "yes", "-", "UniProt accession, used to fetch the sequence and seed the surrogate"),
            ("candidate_residues", "list", "yes", "-", "list of `(chain_id, residue_number)` pairs; the residue number drives the surrogate"),
            ("query_pdb", "callable", "no", "None", "unused by the surrogate; accepted for signature symmetry"),
        ],
        "outputs": "`data` is `{uniprot_id, score, avg_conservation, summary}`.",
        "source": ("UniProt FASTA (`https://www.uniprot.org/uniprot/<acc>.fasta`) "
                   "plus the deterministic entropy surrogate"),
        "runtime": "a few hundred milliseconds; online",
        "determ": ("deterministic: the old implementation seeded numpy with "
                   "Python's salted `hash()`, so the same input gave a "
                   "different score in every process; the port uses a stable "
                   "sha256-derived seed"),
        "failures": [
            "UniProt returns a non-200 -> `success=False`, error states the status",
            "the FASTA cannot be parsed -> `success=False`",
        ],
        "ka": ("input `P00688` with A/10 and A/50 -> `avg_conservation == 0.02`, "
               "`score == 0.034`, and the same values on every call and in "
               "every process"),
        "ka_src": "UniProt P00688, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-20)",
        "nc": "an accession UniProt does not know -> `success=False`",
        "code": "biomni/tool/allosteric_verification_tools.py::evolutionary_conservation",
    },
    "P28_allosteric_evidence": {
        "title": "P28 allosteric_evidence",
        "q": "Does the Allosteric Database confirm that this protein has curated allosteric sites?",
        "notq": ("It does not predict allostery for a protein ASD does not "
                 "cover: `NOT_CONFIRMED` means the database has no record, not "
                 "that the protein has no allostery."),
        "inputs": [
            ("uniprot_id", "str", "no", "None", "UniProt accession"),
            ("pdb_id", "str", "no", "None", "PDB id, used when no UniProt accession is given"),
        ],
        "outputs": ("`data` is `{status, message, protein_id, protein_name, "
                    "gene_name, known_sites, modulator_count, modulators}`; "
                    "`status` is `CONFIRMED`, `UNCERTAIN` or `NOT_CONFIRMED`."),
        "source": "ASD `ASD_Release_202306_XF` XML files, mounted read-only at `/biolab_data`",
        "runtime": "a few hundred milliseconds; offline",
        "determ": "deterministic for a given ASD snapshot",
        "failures": [
            "neither id given -> `success=False`",
            "the ASD snapshot is missing -> `success=False`",
        ],
        "ka": ("input `P0AB91` -> `status == \"CONFIRMED\"`, 1 known site with "
               "`pdb_id == \"1KFL\"` and `site_id == \"1KFL-1\"`, "
               "`modulator_count == 5`, `gene_name == \"aroG\"`"),
        "ka_src": "ASD XF, 2026-10-23 (docs/2_port_batch3_allosteric_core_known_answers.md E-12)",
        "nc": ("input `P51639` -> `status == \"UNCERTAIN\"` (in ASD, no "
               "curated site) and `modulator_count == 1`"),
        "code": "biomni/tool/allosteric_verification_tools.py::allosteric_evidence",
    },
    "P29_set_restricted_imports": {
        "title": "P29 set_restricted_imports",
        "q": "Which module prefixes must the Python REPL refuse to import?",
        "notq": ("It does not sandbox the REPL. It is a prefix list enforced "
                 "on the REPL's own imports; `importlib`'s direct machinery "
                 "call is not intercepted."),
        "inputs": [
            ("prefixes", "list", "yes", "-", "module name prefixes to block; None or an empty list clears the restrictions"),
        ],
        "outputs": "`data` is `{\"prefixes\": [str, ...]}` -- the prefixes now in force.",
        "source": "no external source; a process-level setting",
        "runtime": "under a millisecond; offline",
        "determ": "deterministic",
        "failures": ["prefixes that is not a list of strings -> `success=False`"],
        "ka": ("input `[\"os\", \"shutil\"]` -> `data.prefixes == "
               "[\"os\", \"shutil\"]`"),
        "ka_src": "2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-1)",
        "nc": "input `None` -> `data.prefixes == []`; the restrictions are cleared",
        "code": "biomni/tool/support_tools.py::set_restricted_imports",
    },
    "P30_run_python_repl": {
        "title": "P30 run_python_repl",
        "q": "What does this Python code print or return when run in the persistent REPL namespace?",
        "notq": ("It does not sandbox the interpreter. A module prefix "
                 "registered with `set_restricted_imports` is refused by the "
                 "REPL's imports, but `importlib.import_module` bypasses that "
                 "check because it calls the import machinery directly."),
        "inputs": [
            ("command", "str", "yes", "-", "the Python command to run"),
        ],
        "outputs": ("A string: the captured stdout, or `\"Error: <message>\"` "
                    "when the command raised."),
        "source": "no external source; the local interpreter",
        "runtime": "as long as the command takes; offline",
        "determ": "deterministic for a deterministic command",
        "failures": [
            "the command raises -> the output is `\"Error: <message>\"`; the REPL does not propagate the exception",
            "a restricted module is imported -> the output is the blocked message",
        ],
        "ka": ("with `os` restricted, `\"import os\"` -> `\"Error: Import of "
               "restricted module prefix 'os' is blocked by agent policy.\"`; "
               "with no restrictions, `\"print(1 + 1)\"` -> `\"2\\n\"`"),
        "ka_src": "2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-7, F-12)",
        "nc": ("with no restrictions, `\"import os\"` -> `\"\"`; the import "
               "succeeds and prints nothing"),
        "code": "biomni/tool/support_tools.py::run_python_repl",
    },
    "P31_query_opentarget_genetics": {
        "title": "P31 query_opentarget_genetics",
        "q": "What does the OpenTargets Genetics GraphQL API say about a variant, QTL or locus-to-gene mapping?",
        "notq": ("**The upstream service is gone.** The host "
                 "`api.genetics.opentargets.org` no longer resolves: the "
                 "OpenTargets Genetics API was retired and folded into the "
                 "Platform API, which `query_opentarget` uses. Calls fail "
                 "with a structured error. For questions about the Platform "
                 "API, use `query_opentarget` instead."),
        "inputs": [
            ("prompt", "str", "no", "None", "natural-language request; translated into GraphQL by the configured model"),
            ("query", "str", "no", "None", "a direct GraphQL query string"),
            ("variables", "dict", "no", "None", "variables for the GraphQL query"),
            ("verbose", "bool", "no", "True", "whether to return the full result envelope"),
        ],
        "outputs": ("The `_query_rest_api` envelope: `{success, query_info, "
                    "result}` on success, `{error, ...}` on failure."),
        "source": ("OpenTargets Genetics GraphQL API, "
                   "`https://api.genetics.opentargets.org/graphql` -- hostname "
                   "no longer resolves as of 2026-10-23"),
        "runtime": "one model call to translate the prompt, then one POST; online",
        "determ": "the GraphQL result is deterministic; the translated query is not",
        "failures": [
            "neither prompt nor query -> `{\"error\": \"Either a prompt or a GraphQL query must be provided\"}`",
            "the API host cannot be resolved -> a structured `error` naming the endpoint",
        ],
        "ka": ("`query=\"query { __typename }\"` -> either "
               "`result.data.__typename == \"Query\"`, or a structured `error` "
               "naming `api.genetics.opentargets.org`; today it is the latter"),
        "ka_src": "2026-10-23 (docs/2_port_batch4_database_support_known_answers.md F-15, corrections C-10)",
        "nc": "no prompt and no query -> the \"must be provided\" error",
        "code": "biomni/tool/database.py::query_opentarget_genetics",
    },
}

TEMPLATE = """# {title}

## Question the tool answers

{q}

## What it does NOT answer

{notq}

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
{input_rows}

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{{success, data, error, source, source_version, query_time_utc}}`.

{outputs}

## Source and version

- upstream URL: {source}

## Runtime

- {runtime}

## Determinism

- {determ}

## Failure modes

{failures}

## Known-answer test

- expectation: {ka}
- source of the expectation: {ka_src}

## Negative control

- expectation: {nc}

## Code location and version

- function: `{code}`
- recorded in: the per-run JSON at the key `tools_meta`
- version: `biomni.__version__`
"""


def render(name: str, card: dict) -> str:
    input_rows = "\n".join(
        f"| `{n}` | `{t}` | {'yes' if r == 'yes' else 'no'} | `{d}` | {desc} |"
        for n, t, r, d, desc in card["inputs"]
    )
    failures = "\n".join(f"- {f}" for f in card["failures"])
    return TEMPLATE.format(
        title=card["title"],
        q=card["q"],
        notq=card["notq"],
        input_rows=input_rows,
        outputs=card["outputs"],
        source=card["source"],
        runtime=card["runtime"],
        determ=card["determ"],
        failures=failures,
        ka=card["ka"],
        ka_src=card["ka_src"],
        nc=card["nc"],
        code=card["code"],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, card in CARDS.items():
        path = OUT / f"{name}.md"
        path.write_text(render(name, card), encoding="utf-8", newline="\n")
        print(f"wrote {path.name}")


if __name__ == "__main__":
    main()
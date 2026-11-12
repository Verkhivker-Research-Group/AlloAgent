# Benchmark validation report

Generated 2026-11-09T06:08:09Z by `scripts/validate_benchmark.py` in the container.

Every checklist value below was recomputed from the primary source (RCSB mmCIF, UniProt REST, the RCSB SIFTS alignment, the ChEMBL 37 SQLite by direct SQL, the ClinVar and AlphaMissense release files, the STINGAllo API). The pocket / dynamics checklists also carry one reference output of our own tools; a reference output is the number to compare against, not the ground truth of the science.

**40 PASS, 0 PROBLEM, 40 prompts.**

> **Dated note 2026-11-10.**  The STINGAllo question for 1T4J chain A -
> the prompt the launch set of 2026-10-28 deferred, which was never run -
> was removed from the benchmark on 2026-11-10.  Its section below and the
> count above were removed by hand on that day; the validator was **not**
> re-run, because the removed prompt carried no validated checklist item
> (the validator listed it with none: it was deferred, so no value of it
> was ever validated against a source) and because no run of it exists.
> The `benchmark_draft` sha256 in the table below is therefore the sha256
> of the draft this run validated, and the criteria of the 40 prompts that
> remain are the ones this run validated.

## Sources

| source | version / sha256 |
|---|---|
| clinvar_release | `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f` |
| alphamissense_release | `bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d` |
| chembl_37_sqlite | `4be13df3b68e25dcd0bff44bf094033b5aebe98f415acdc8c1cdf380e0c15142` |
| benchmark_draft | `8bd86c040e106e92a244e859341bbe1cba0dd7ea2f0fc2258a83cb1c459f1ddc` |

## PROBLEM prompts and the proposed fix

None.
## Per-prompt checklist

### S01 - Site characterization, tier 1, route P - **PASS**

* accession: `P18031`
* expected tools: `map_residues_uniprot_pdb; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_1T4J_FRJ | exact | [{"chain": "A", "pdb_number": 299}] | RCSB mmCIF 1T4J | - |
| contacts_1T4J_FRJ_4A | set | {"uniprot_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "pdb_residues": [188, 189, 192, 193, 196, 200, 276, 277, 279, 280, 282], "min_distances": {"188": 3.918, "189": 3.416, "192": 3.803, "193":... | RCSB mmCIF 1T4J + SIFTS (offset 0) | 0 |
| contact_count_1T4J_FRJ_4A | number | 11 | RCSB mmCIF 1T4J | 0 |

### S02 - Site characterization, tier 1, route P - **PASS**

* accession: `P00519`
* expected tools: `structure code; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_1OPK_MYR | exact | [{"chain": "A", "pdb_number": 1}] | RCSB mmCIF 1OPK | - |
| ligand_1OPK_P16 | exact | [{"chain": "A", "pdb_number": 2}] | RCSB mmCIF 1OPK | - |
| contacts_1OPK_MYR_4A | set | {"uniprot_residues": [340, 341, 344, 429, 433, 462, 502, 510], "pdb_residues": [359, 360, 363, 448, 452, 481, 521, 529], "min_distances": {"359": 3.836, "360": 3.687, "363": 3.706, "448": 3.731, "452": 3.854, "481": 3... | RCSB mmCIF 1OPK + SIFTS (offset 20) | 0 |

### S03 - Site characterization, tier 2, route P - **PASS**

* accession: `P35557`
* expected tools: `structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P35557 | exact | {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_1V4S_MRK | exact | [{"chain": "A", "pdb_number": 501}] | RCSB mmCIF 1V4S | - |
| ligand_1V4S_GLC | exact | [{"chain": "A", "pdb_number": 500}] | RCSB mmCIF 1V4S | - |
| contacts_1V4S_MRK_4A | set | {"uniprot_residues": [61, 62, 63, 64, 65, 66, 210, 211, 214, 215, 220, 235, 452, 455], "pdb_residues": [61, 62, 63, 64, 65, 66, 210, 211, 214, 215, 220, 235, 452, 455], "min_distances": {"61": 3.248, "62": 3.624, "63"... | RCSB mmCIF 1V4S + SIFTS (offset 10) | 0 |
| min_distance_MRK_GLC_1V4S | number | 16.23 | RCSB mmCIF 1V4S | 0.5 |

### S04 - Site characterization, tier 2, route P - **PASS**

* accession: `P31749`
* expected tools: `structure code; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P31749 | exact | {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_3O96_IQO | exact | [{"chain": "A", "pdb_number": 444}] | RCSB mmCIF 3O96 | - |
| contacts_3O96_IQO_4A | set | {"uniprot_residues": [80, 82, 83, 84, 85, 205, 210, 211, 264, 268, 271, 272, 273, 274, 290, 291, 292, 296], "pdb_residues": [80, 82, 83, 84, 85, 205, 210, 211, 264, 268, 271, 272, 273, 274, 290, 291, 292, 296], "min_d... | RCSB mmCIF 3O96 + SIFTS (offset -3) | 0 |
| akt1_domains | qualitative | the contact residues fall in the PH domain of AKT1 | UniProt domain features | - |

### S05 - Site characterization, tier 2, route P - **PASS**

* accession: `Q06124`
* expected tools: `structure code; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_5EHR_5OD | exact | [{"chain": "A", "pdb_number": 601}] | RCSB mmCIF 5EHR | - |
| contacts_5EHR_5OD_4A | set | {"uniprot_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "pdb_residues": [108, 110, 111, 113, 114, 218, 219, 249, 250, 253, 254, 257, 491, 492, 495], "min_distances": {"108": 3... | RCSB mmCIF 5EHR + SIFTS (offset -1) | 0 |
| shp2_domains | qualitative | each contact residue is assigned to N-SH2, C-SH2 or PTP | UniProt domain features | - |

### S06 - Site characterization, tier 2, route P - **PASS**

* accession: `P62593`
* expected tools: `structure code; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P62593 | exact | {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"} | UniProt REST | - |
| ligand_1PZO_CBT | exact | [{"chain": "A", "pdb_number": 300}, {"chain": "A", "pdb_number": 301}] | RCSB mmCIF 1PZO | - |
| contacts_1PZO_CBT_4A | set | {"uniprot_residues": [214, 215, 218, 219, 222, 233, 234, 235, 241, 242, 243, 257, 259, 272, 275, 276, 279, 282], "pdb_residues": [216, 217, 220, 221, 224, 235, 236, 237, 244, 245, 246, 261, 263, 276, 279, 280, 283, 28... | RCSB mmCIF 1PZO + SIFTS (offset 23) | 0 |
| cbt_copies | exact | [300, 301] | RCSB mmCIF 1PZO | - |

### S07 - Site characterization, tier 3, route P - **PASS**

* accession: `P00519`
* expected tools: `structure code; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| ligand_5MO4_AY7 | exact | [{"chain": "A", "pdb_number": 602}] | RCSB mmCIF 5MO4 | - |
| ligand_5MO4_NIL | exact | [{"chain": "A", "pdb_number": 601}] | RCSB mmCIF 5MO4 | - |
| contacts_5MO4_AY7_4A | set | {"uniprot_residues": [332, 337, 340, 341, 344, 429, 432, 433, 434, 435, 462, 464, 465, 468, 493, 502, 506, 510], "pdb_residues": [351, 356, 359, 360, 363, 448, 451, 452, 453, 454, 481, 483, 484, 487, 512, 521, 525, 52... | RCSB mmCIF 5MO4 + SIFTS (offset 20) | 0 |
| contacts_5MO4_NIL_4A | set | {"uniprot_residues": [248, 253, 256, 269, 270, 271, 285, 286, 289, 290, 293, 298, 299, 313, 315, 317, 318, 321, 359, 361, 370, 379, 380, 381, 382], "pdb_residues": [267, 272, 275, 288, 289, 290, 304, 305, 308, 309, 31... | RCSB mmCIF 5MO4 + SIFTS (offset 20) | 0 |
| ay7_nil_overlap | number | 0 | RCSB mmCIF 5MO4 | 0 |
| numbering_offset_5MO4 | number | {"sifts_label_to_uniprot": 20, "auth_T334_to_uniprot_T315": -19} | RCSB SIFTS alignment + the T334I mutation | 0 |

### P01 - Pocket detection, tier 2, route P - **PASS**

* accession: `P18031`
* expected tools: `detect_pockets_fpocket or p2rank; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}] | fpocket on the ligand-stripped 1T4J | - |
| pocket_recovery | qualitative | the top three fpocket pockets of the ligand-stripped 1T4J contain the residues FRJ contacted, and the overlap is reported as a count | the prompt's own criterion | - |

### P02 - Pocket detection, tier 2, route P - **PASS**

* accession: `P01116`
* expected tools: `detect_pockets_*; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P01116 | exact | {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 33}, {"rank": 2, "residues": 9}, {"rank": 3, "residues": 13}] | fpocket on the ligand-stripped 6OIM | - |
| pocket_recovery | qualitative | the rank of the pocket that covers the former switch-II inhibitor site (the MOV contacts) is reported | the prompt's own criterion | - |

### P03 - Pocket detection, tier 3, route P - **PASS**

* accession: `Q06124`
* expected tools: `detect_pockets_*; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 21}, {"rank": 2, "residues": 21}, {"rank": 3, "residues": 22}] | fpocket on the ligand-stripped 2SHP | - |
| pocket_recovery | qualitative | the overlap of the top five pockets of 2SHP with the 5EHR SHP099 contact residues, mapped through UniProt numbering, is reported | the prompt's own criterion | - |

### P04 - Cryptic pockets, tier 2, route N - **PASS**

* accession: `P62593`
* expected tools: `PocketMiner wrapper; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P62593 | exact | {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"} | UniProt REST | - |
| pocketminer_top10_1BTL | exact | [{"chain": "A", "pdb_number": 234, "residue_name": "LYS", "score": 0.9514}, {"chain": "A", "pdb_number": 246, "residue_name": "ILE", "score": 0.9425}, {"chain": "A", "pdb_number": 172, "residue_name": "ALA", "score": ... | PocketMiner on 1BTL (our tool, reference output) | - |
| pocketminer_scores_for_1PZO_contacts | exact | {"214": 0.8751, "215": 0.9208, "218": 0.9168, "219": 0.7866, "222": 0.2461, "233": 0.9179, "234": 0.8263, "235": 0.8921, "241": 0.929, "242": 0.8435, "243": 0.9425, "257": 0.3872, "259": 0.7797, "272": 0.8693, "275": ... | PocketMiner on 1BTL, mapped to UniProt numbering through the 1BTL SIFTS alignment | - |
| mapping_stated | qualitative | the mapping between the two entries is stated (both are TEM-1, P62593; the 1PZO CBT contacts are given in UniProt numbering) | RCSB SIFTS | - |

### P05 - Pocket detection, tier 2, route P - **PASS**

* accession: `P00519`
* expected tools: `detect_pockets_*; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 23}, {"rank": 2, "residues": 23}, {"rank": 3, "residues": 17}] | fpocket on the ligand-stripped 1OPK | - |
| pocket_recovery | qualitative | the rank of the pocket that covers the myristoyl site (the MYR contacts) is reported | the prompt's own criterion | - |

### P06 - Pocket detection, tier 2, route P - **PASS**

* accession: `P35557`
* expected tools: `detect_pockets_*; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P35557 | exact | {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 11}, {"rank": 2, "residues": 24}, {"rank": 3, "residues": 12}] | fpocket on the ligand-stripped 1V4S | - |
| pocket_recovery | qualitative | which of the top three pockets of 1V4S matches the MRK site and which matches the GLC site is reported | the prompt's own criterion | - |

### P07 - Cryptic pockets, tier 3, route N - **PASS**

* accession: `P18031`
* expected tools: `detect_pockets_fpocket; detect_pockets_p2rank; PocketMiner wrapper`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}] | fpocket on the ligand-stripped 1T4J | - |
| pocket_recovery | qualitative | the rank or score each of fpocket, P2Rank and PocketMiner assigns to the FRJ contact residues, which methods agree, and the caveat that a pocket detector cannot label an allosteric pocket | the prompt's own criterion | - |

### C01 - Dynamics & communication, tier 1, route P - **PASS**

* accession: `P18031`
* expected tools: `normal_mode_analysis`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| analysis_present | qualitative | the hinge residues of the slowest non-trivial normal mode and the relative mobility of the WPD loop (the catalytic Asp181) are reported, in UniProt numbering | the prompt's own criterion | - |

### C02 - Dynamics & communication, tier 2, route P - **PASS**

* accession: `P18031`
* expected tools: `residue_contact_network; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| analysis_present | qualitative | the shortest path from the residue closest to the allosteric ligand to Cys215 is reported with its length and the cutoff used | the prompt's own criterion | - |

### C03 - Dynamics & communication, tier 2, route P - **PASS**

* accession: `Q06124`
* expected tools: `normal_mode_analysis; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| analysis_present | qualitative | the mobility of the 5EHR SHP099-contact residues (mapped through UniProt numbering) is compared with the rest of the structure | the prompt's own criterion | - |

### C04 - Dynamics & communication, tier 2, route P - **PASS**

* accession: `P35557`
* expected tools: `residue_contact_network; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P35557 | exact | {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"} | UniProt REST | - |
| analysis_present | qualitative | the shortest path between an MRK-contact residue and a GLC-contact residue is reported with its length | the prompt's own criterion | - |

### C05 - Dynamics & communication, tier 2, route P - **PASS**

* accession: `P69441`
* expected tools: `residue_contact_network`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P69441 | exact | {"name": "Adenylate kinase", "gene": "adk", "organism": "Escherichia coli (strain K12)"} | UniProt REST | - |
| analysis_present | qualitative | the communities of 1AKE at an 8 A C-alpha cutoff are reported with the algorithm and the seed, and their relation to the LID, NMP and CORE domains | the prompt's own criterion | - |

### C06 - Dynamics & communication, tier 3, route N - **PASS**

* accession: `P18031`
* expected tools: `normal_mode_analysis; residue_contact_network; get_stingallo_allosteric_residues`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| analysis_present | qualitative | the normal-mode analysis, the contact-network path to Cys215 and the STINGAllo prediction are each present with their limits stated | the prompt's own criterion | - |

### V01 - Variants & allostery, tier 2, route N - **PASS**

* accession: `Q06124`
* expected tools: `get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| clinvar_E76K | exact | {"clinical_significance": "Conflicting classifications of pathogenicity", "variation_id": "28375"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_E76K | number | 0.9998 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| clinvar_D61Y | exact | {"clinical_significance": "Conflicting classifications of pathogenicity", "variation_id": "230257"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_D61Y | number | 0.9985 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| distances | qualitative | the distances of residues 76 and 61 to the 5EHR inhibitor site and to the 2SHP autoinhibitory interface are reported | RCSB mmCIF 5EHR + 2SHP | - |

### V02 - Variants & allostery, tier 2, route N - **PASS**

* accession: `P31749`
* expected tools: `get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P31749 | exact | {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"} | UniProt REST | - |
| clinvar_E17K | exact | {"clinical_significance": "Pathogenic", "variation_id": "29022"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_E17K | number | 0.9977 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| domain_and_distance | qualitative | the PH domain is named and the distance from residue 17 to the 3O96 inhibitor is reported (residue 17 IS modelled: UniProt 17 = label_seq_id 20, the PDB author number differs) | UniProt + RCSB mmCIF 3O96 | - |

### V03 - Variants & allostery, tier 2, route N - **PASS**

* accession: `P01116`
* expected tools: `get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P01116 | exact | {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"} | UniProt REST | - |
| clinvar_G12C | exact | {"clinical_significance": "Likely pathogenic", "variation_id": "27617"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_G12C | number | 0.9975 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| clinvar_G12D | exact | {"clinical_significance": "Pathogenic/Likely pathogenic", "variation_id": "27621"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_G12D | number | 0.9984 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| clinvar_G12V | exact | {"clinical_significance": "Pathogenic", "variation_id": "27622"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_G12V | number | 0.9949 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| distance | qualitative | the distance from residue 12 to the 6OIM covalent inhibitor is reported | RCSB mmCIF 6OIM | - |
| resolution | qualitative | the answer says whether the three scores separate the variants | the prompt | - |

### V04 - Variants & allostery, tier 2, route N - **PASS**

* accession: `P00519`
* expected tools: `get_clinvar_variants; get_alphamissense_score; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| clinvar_T315I | exact | {"clinical_significance": "Likely pathogenic; association", "variation_id": "27663"} | ClinVar release (b235cd5742ac) | - |
| alphamissense_T315I | number | 0.9991 | AlphaMissense release (bc18d954a9aa) | 0.01 |
| distances | qualitative | the distances from T315I to the ATP-site ligand (P16) and to the myristoyl-site ligand (MYR) in 1OPK are reported, with a hedged inference | RCSB mmCIF 1OPK | - |

### V05 - Variants & allostery, tier 3, route N - **PASS**

* accession: `P35557`
* expected tools: `get_clinvar_variants; map_residues_uniprot_pdb; get_alphamissense_score`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P35557 | exact | {"name": "Hexokinase-4", "gene": "GCK", "organism": "Homo sapiens"} | UniProt REST | - |
| clinvar_variant_count_GCK | number | 2845 | ClinVar release (b235cd5742ac) | +/- 284 (10 % band: the release and the live API differ) |
| variant_list | qualitative | the ClinVar variants of glucokinase are mapped onto 1V4S and the ones within 6 A of the MRK activator are listed with their AlphaMissense scores | the prompt's own criterion | - |

### V06 - Variants & allostery, tier 3, route N - **PASS**

* accession: `P62593`
* expected tools: `PocketMiner wrapper; get_uniprot_variants; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P62593 | exact | {"name": "Beta-lactamase TEM", "gene": "bla", "organism": "Escherichia coli"} | UniProt REST | - |
| variant_list | qualitative | the PocketMiner cryptic-pocket residues of 1BTL, the UniProt variants of TEM-1 and every annotated variant within 6 A of a 1PZO CBT-contact residue are listed | the prompt's own criterion | - |

### K04 - Allosteric site prediction, tier 2, route P - **PASS**

* accession: `P01116`
* expected tools: `residue_contact_network; get_ligand_contacts`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P01116 | exact | {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"} | UniProt REST | - |
| stingallo_residues | exact | ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"] | STINGAllo (2026-10-27T15:13:30Z) | - |
| overlap_1T4J_FRJ | number | 10 | STINGAllo + RCSB mmCIF 1T4J (FRJ, chain A) | 0 |
| chance_base_rate_1T4J_FRJ | exact | {"predicted_residues": 14, "predicted_residue_numbers": [129, 130, 187, 188, 189, 192, 193, 196, 200, 276, 279, 280, 281, 282], "contact_residues": 11, "modelled_chain_A_residues": 282, "predicted_fraction_of_chain": ... | STINGAllo + RCSB mmCIF 1T4J | 0 |
| chance_comparison_stated | qualitative | the answer compares the observed overlap with the chance expectation and says whether the prediction is better than chance | the prompt's own criterion | - |

### L02 - Allosteric modulators, tier 2, route P - **PASS**

* accession: `Q02750`
* expected tools: `get_chembl_bioactivity`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q02750 | exact | {"name": "Dual specificity mitogen-activated protein kinase kinase 1", "gene": "MAP2K1", "organism": "Homo sapiens"} | UniProt REST | - |
| chembl_trametinib | exact | {"count": 16, "median_nM": 2.8499999999999996, "best_nM": 0.48, "units": {"nM": 16}} | ChEMBL 37 SQLite, direct SQL | - |
| chembl_cobimetinib | exact | {"count": 11, "median_nM": 4.2, "best_nM": 0.2, "units": {"nM": 11}} | ChEMBL 37 SQLite, direct SQL | - |

### L03 - Allosteric modulators, tier 2, route P - **PASS**

* accession: `P00519`
* expected tools: `get_chembl_bioactivity; search_pdb_by_uniprot_and_ligand`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| chembl_asciminib | exact | {"count": 2, "best_nM": 0.5, "assay_types": {"B": 2}} | ChEMBL 37 SQLite, direct SQL | - |
| chembl_imatinib | exact | {"count": 94, "best_nM": 19.9, "assay_types": {"B": 94}} | ChEMBL 37 SQLite, direct SQL | - |
| site_evidence | qualitative | the answer cites a PDB entry for each site (AY7: 5MO4; STI: 2HYY) | RCSB | - |

### L04 - Allosteric modulators, tier 2, route P - **PASS**

* accession: `Q06124`
* expected tools: `search_pdb_by_uniprot_and_ligand; get_chembl_bioactivity`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| 5od_shp2_entries | exact | ["5EHR", "6BMU", "6BMW", "6BMY", "6CMR", "6CMS", "6CRG", "8WFY"] | RCSB Search API v2 | - |
| chembl_shp099_absence | exact | {"present": false, "count": 0, "molecule_in_chembl_37": false} | ChEMBL 37 SQLite, direct SQL | - |

### P08 - Cryptic pockets, tier 2, route N - **PASS**

* accession: `Q06124`
* expected tools: `PocketMiner wrapper; get_ligand_contacts; map_residues_uniprot_pdb`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| pocketminer_top10_2SHP_chain_A | exact | [{"chain": "A", "pdb_number": 220, "residue_name": "ARG", "score": 0.9235}, {"chain": "A", "pdb_number": 423, "residue_name": "TRP", "score": 0.9177}, {"chain": "A", "pdb_number": 218, "residue_name": "THR", "score": ... | PocketMiner on 2SHP chain A (our tool, reference output) | - |
| mapped_5EHR_SHP099_contacts_on_2SHP | exact | [{"uniprot_number": 108, "pdb_number_2SHP": 108, "pocketminer_score": 0.8084, "pocketminer_rank_in_chain_A": 63}, {"uniprot_number": 110, "pdb_number_2SHP": 110, "pocketminer_score": 0.8349, "pocketminer_rank_in_chain... | the 5EHR SHP099 contact residues (4 A, chain A) mapped onto 2SHP through the UniProt numbering, with their PocketMiner scores | - |
| site_rank_comparison | exact | {"n_site_residues": 15, "n_scored": 15, "n_in_the_top10": 3, "best_rank": 3, "median_rank": 47} | PocketMiner on 2SHP chain A (our tool, reference output) | - |
| modest_accuracy_caveat | qualitative | the answer states that PocketMiner is a screening tool with modest accuracy (per-protein AUC about 0.65 on the independent test split), so the scores rank cryptic-pocket propensity and do not establish that a residue ... | the tool card of pocketminer_score | - |
| mapping_stated | qualitative | the mapping between the two entries is stated (both are SHP2, Q06124; the 5EHR SHP099 contacts are given in UniProt numbering) | RCSB SIFTS | - |

### K01 - Allosteric site prediction, tier 1, route N - **PASS**

* accession: `P18031`
* expected tools: `get_stingallo_allosteric_residues`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| stingallo_residues | exact | ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"] | STINGAllo (2026-10-27T15:13:30Z) | - |

### K02 - Allosteric site prediction, tier 2, route N - **PASS**

* accession: `P18031`
* expected tools: `get_stingallo_allosteric_residues; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| stingallo_residues | exact | ["129", "130", "187", "188", "189", "192", "193", "196", "200", "276", "279", "280", "281", "282"] | STINGAllo (2026-10-27T15:13:30Z) | - |
| overlap_1T4J | number | 10 | STINGAllo + RCSB mmCIF 1T4J | 0 |

### K03 - Allosteric site prediction, tier 2, route N - **PASS**

* accession: `Q06124`
* expected tools: `get_stingallo_allosteric_residues; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| stingallo_residues | exact | ["314"] | STINGAllo (2026-10-27T15:13:31Z) | - |
| overlap_5EHR | number | 0 | STINGAllo + RCSB mmCIF 5EHR | 0 |
| chance_base_rate_5EHR | exact | {"predicted_residues": 1, "predicted_residue_numbers": [314], "contact_residues": 15, "modelled_chain_A_residues": 485, "predicted_fraction_of_chain": 0.002061855670103093, "expected_overlap_by_chance": 0.030927835051... | computed from the same two sources | - |

### G01 - Synthesis, tier 3, route N - **PASS**

* accession: `P01116`
* expected tools: `pockets; ChEMBL; ClinVar; AlphaMissense; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P01116 | exact | {"name": "GTPase KRas", "gene": "KRAS", "organism": "Homo sapiens"} | UniProt REST | - |
| components_present | qualitative | the pocket detection on the ligand-stripped 6OIM, the ChEMBL bioactivity of sotorasib, the ClinVar and AlphaMissense records for KRAS G12C and the distance from residue 12 to the inhibitor are all present, with a hedg... | the prompt's own criterion | - |

### G02 - Synthesis, tier 3, route N - **PASS**

* accession: `P00519`
* expected tools: `pockets; ChEMBL; ClinVar; AlphaMissense; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P00519 | exact | {"name": "Tyrosine-protein kinase ABL1", "gene": "ABL1", "organism": "Homo sapiens"} | UniProt REST | - |
| components_present | qualitative | the 1OPK contacts for both sites, the pocket ranks on the ligand-stripped structure, the ChEMBL potency of imatinib and asciminib and the T315I records and distances are present, with the allosteric-site claim separat... | the prompt's own criterion | - |

### G03 - Synthesis, tier 3, route N - **PASS**

* accession: `Q06124`
* expected tools: `ClinVar; AlphaMissense; pockets; normal_mode_analysis`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_Q06124 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 11", "gene": "PTPN11", "organism": "Homo sapiens"} | UniProt REST | - |
| components_present | qualitative | the ClinVar and AlphaMissense records for E76K and D61Y, the distances to the 2SHP autoinhibitory interface, the pocket detection on 2SHP and the normal mode analysis are present, with the conclusion hedged and the li... | the prompt's own criterion | - |

### G04 - Synthesis, tier 3, route N - **PASS**

* accession: `P31749`
* expected tools: `ChEMBL; ClinVar; AlphaMissense; structure code`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P31749 | exact | {"name": "RAC-alpha serine/threonine-protein kinase", "gene": "AKT1", "organism": "Homo sapiens"} | UniProt REST | - |
| components_present | qualitative | the 3O96 ligand contacts, the ChEMBL records for MK-2206 (or an explicit absence), the ClinVar and AlphaMissense records for E17K and the distance from residue 17 to the ligand where modelled are present, with a hedge... | the prompt's own criterion | - |

### H01 - Honest reporting, tier 1, route P - **PASS**

* accession: `P18031`
* expected tools: `get_chembl_bioactivity`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| shp099_ptpn1_absence | exact | {"present": false, "count": 0, "molecule_in_chembl_37": false} | ChEMBL 37 SQLite, direct SQL | - |

### H02 - Honest reporting, tier 2, route P - **PASS**

* accession: `P18031`
* expected tools: `detect_pockets_*`

| item | kind | value | source | tolerance |
|---|---|---|---|---|
| accession_P18031 | exact | {"name": "Tyrosine-protein phosphatase non-receptor type 1", "gene": "PTPN1", "organism": "Homo sapiens"} | UniProt REST | - |
| fpocket_top3 | exact | [{"rank": 1, "residues": 9}, {"rank": 2, "residues": 12}, {"rank": 3, "residues": 15}] | fpocket on the ligand-stripped 1T4J | - |
| pocket_recovery | qualitative | a ranking of the top three pockets by allosteric likelihood with the stated limit that pocket detectors do not distinguish allosteric from orthosteric pockets | the prompt's own criterion | - |


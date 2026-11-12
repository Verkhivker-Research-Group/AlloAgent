# The restricted-scenario prompt set (2026-10-26)

Which of the 40 benchmark prompts (`benchmark/benchmark_draft.json`) can
arm D answer **from local resources alone**, with the container's only
outbound access being the LLM endpoint?

**This file is committed BEFORE any run of the restricted scenario.** No
prompt was selected by looking at a result, and the benchmark was not
launched.

## The rule used

A prompt is **LOCAL** when every fact it needs is available inside the
container with no outbound access:

* the **local structure cache** - the 11 benchmark entries (1T4J, 1OPK,
  1V4S, 3O96, 5EHR, 1PZO, 5MO4, 6OIM, 1BTL, 2SHP, 1AKE) as PDB and
  mmCIF, mounted read-only and identically into both arms at
  `/data/structures` (`scripts/fetch_structure_cache.py`);
* the **local data lake** - ChEMBL 37 (`/data/chembl`), the ClinVar
  release (`/data/clinvar`), the AlphaMissense TSV
  (`/data/alphamissense`), the ASD release (`/biolab_data/asd`), the
  BioLiP data (`/biolab_data/biolip`);
* the **local models** - fpocket, P2Rank, PocketMiner, the normal-mode
  analysis, the contact network;
* the **local binaries** - vina.

A prompt is **LIVE** when it needs an outbound service, and **MIXED**
when one part of it is local and another part is not. The only live
services the benchmark tools use are:

| service | host | used by |
|---|---|---|
| the UniProt-PDB residue mapping (SIFTS) | `data.rcsb.org`, `www.ebi.ac.uk` (PDBe) | `map_residues_uniprot_pdb`, `get_ligand_contacts` (the UniProt numbers), `get_uniprot_variants` (the UniProt features) |
| the PDB search | RCSB / PDBe search | `search_pdb_by_uniprot_and_ligand` |
| STINGAllo | `www.stingallo.cbi.cnptia.embrapa.br` | `get_stingallo_allosteric_residues` |

## The classification

| id | prompt (one line) | class | reason |
|---|---|---|---|
| S01 | 1T4J: the allosteric ligand and its 4 A contacts, UniProt numbering | MIXED | the ligand and the contacts are local (the cached mmCIF); the UniProt numbering is the live SIFTS mapping |
| S02 | 1OPK: the myristoyl and ATP ligands, the 4 A contacts of MYR | **LOCAL** | the cached structure; the ligand IDs and the contacts come from the coordinates |
| S03 | 1V4S: the activator and glucose, the contacts, the ligand-ligand distance | **LOCAL** | the cached structure; the contacts and the distance are computed from the coordinates |
| S04 | 3O96: the allosteric inhibitor, the contacts, the AKT1 domains | MIXED | the contacts are local; the domain boundaries are UniProt features (live) |
| S05 | 5EHR: the SHP099 contacts and the N-SH2 / C-SH2 / PTP domains | MIXED | the contacts are local; the domain boundaries are UniProt features (live) |
| S06 | 1PZO: two inhibitor copies, the contacts, the same pocket? | **LOCAL** | the cached structure |
| S07 | 5MO4: two ligands, the contacts, the relation to P00519 numbering | MIXED | the contacts are local; the numbering offset is the live SIFTS mapping |
| P01 | 1T4J: do the top three pockets overlap the FRJ site? | **LOCAL** | fpocket/P2Rank on the cached, ligand-stripped structure; the overlap in PDB numbering |
| P02 | 6OIM: the rank of the switch-II pocket | **LOCAL** | the pockets and the inhibitor contacts from the cached structure |
| P03 | 2SHP pockets vs the 5EHR SHP099 contacts, mapped through UniProt | MIXED | the pockets and the contacts are local; the inter-entry mapping is live |
| P04 | PocketMiner on 1BTL and the 1PZO inhibitor-contact scores, mapped | MIXED | PocketMiner is local; the inter-entry mapping is live |
| P05 | 1OPK: the rank of the pocket covering the myristoyl site | **LOCAL** | the cached structure |
| P06 | 1V4S: do the top three pockets include the activator and glucose sites? | **LOCAL** | the cached structure |
| P07 | 1T4J: fpocket, P2Rank and PocketMiner on the FRJ residues | **LOCAL** | all three are local; the FRJ residues come from the cached structure |
| C01 | 1T4J: normal modes, the hinge residues, the WPD loop | MIXED | the normal-mode analysis is local; the UniProt numbering of the residues is live |
| C02 | 1T4J: the contact network, the path to Cys215 | **LOCAL** | the network and the path are local; Cys215 is the PDB numbering |
| C03 | 2SHP: normal modes vs the 5EHR SHP099 residues, mapped by UniProt | MIXED | the normal-mode analysis is local; the mapping is live |
| C04 | 1V4S: the contact network path between the activator and glucose | **LOCAL** | the cached structure |
| C05 | 1AKE: the contact network at 8 A and the communities | **LOCAL** | the cached structure; the community detection is local (networkx) |
| C06 | 1T4J: normal modes + a contact-network path + STINGAllo | LIVE* | STINGAllo is a live service (the other two parts are local) |
| V01 | SHP2 E76K / D61Y: ClinVar, AlphaMissense, the distances to the sites | MIXED | ClinVar and AlphaMissense are local; the variant positions come from UniProt and must be mapped (live) |
| V02 | AKT1 E17K: ClinVar, AlphaMissense, the PH domain, the distance | MIXED | as V01 |
| V03 | KRAS G12C / G12D / G12V: ClinVar, AlphaMissense, the distance | MIXED | as V01 |
| V04 | ABL1 T315I: ClinVar, AlphaMissense, the two distances | MIXED | as V01 |
| V05 | glucokinase: the ClinVar variants near the activator, their AM scores | MIXED | as V01 |
| V06 | TEM-1: PocketMiner, the UniProt variants, the pairs near the inhibitor | MIXED | PocketMiner is local; the UniProt variant list is live |
| L01 | which entries contain ABL1 with asciminib? | LIVE | the RCSB/PDBe search is live |
| L02 | trametinib and cobimetinib: the ChEMBL record counts, median, best | **LOCAL** | the local ChEMBL 37 |
| L03 | asciminib vs imatinib: the ChEMBL counts, the assay types, the best potency, a PDB entry for each | **LOCAL** | the local ChEMBL 37; the entries (5MO4, 2HYY) are in the structure cache |
| L04 | which entries contain SHP2 with SHP099, and is SHP099 in ChEMBL? | LIVE* | the entry search is live; the ChEMBL part is local |
| L05 | which entries contain PTP1B with FRJ? | LIVE | the RCSB/PDBe search is live |
| K01 | the STINGAllo prediction for 1T4J | LIVE | STINGAllo is live |
| K02 | the STINGAllo prediction vs the FRJ contacts | LIVE* | STINGAllo is live; the contacts are local |
| K03 | the STINGAllo prediction vs the SHP099 contacts (5EHR) | LIVE* | STINGAllo is live; the contacts are local |
| G01 | KRAS: the pockets, the ChEMBL activity, ClinVar/AlphaMissense, the distance | MIXED | the pockets, the ChEMBL and the coordinates are local; the variant mapping is live |
| G02 | ABL1: the contacts, the pocket ranks, the ChEMBL potency, T315I | MIXED | as G01 |
| G03 | SHP2: ClinVar/AlphaMissense, the distances, the pockets, the normal modes | MIXED | as G01 |
| G04 | AKT1: the contacts, the ChEMBL activity, E17K, the distance | MIXED | as G01 |
| H01 | is SHP099 in ChEMBL against PTP1B? (the answer is an explicit absence) | **LOCAL** | the local ChEMBL 37 |
| H02 | rank the top three 1T4J pockets as allosteric candidates, with the limits stated | **LOCAL** | the cached structure and the local detectors |

`*` LIVE* means: the prompt has a local part and a live-service part,
and the live part cannot be replaced by a local resource.

## The counts

| class | count | ids |
|---|---|---|
| **LOCAL** (answerable with the current tools and the local cache) | **15** | S02, S03, S06, P01, P02, P05, P06, P07, C02, C04, C05, L02, L03, H01, H02 |
| MIXED - local except for the UniProt-PDB mapping | 18 | S01, S04, S05, S07, P03, P04, C01, C03, V01, V02, V03, V04, V05, V06, G01, G02, G03, G04 |
| MIXED - local except for a live service (STINGAllo or the PDB search) | 4 | C06, L04, K02, K03 |
| LIVE (a live service is the answer) | 3 | L01, L05, K01 |
| total | **40** | |

## The restricted-scenario prompt set

**Set A - the restricted scenario as the tools stand today: 15 prompts.**
S02, S03, S06, P01, P02, P05, P06, P07, C02, C04, C05, L02, L03, H01,
H02. These need nothing but the local cache, the local data lake and the
local models.

**Set B - the restricted scenario with a local residue mapping: 33
prompts.** The 18 MIXED prompts of the first group need one thing
only: the UniProt-PDB residue mapping. That mapping is *in the cached
mmCIF files* (the `struct_ref` / `struct_ref_seq_dif` records carry the
UniProt alignment), so serving it from the cache instead of the RCSB
Data API makes all 18 local. Set B = Set A plus those 18, i.e. every
prompt except the 7 that need a live service (C06, L01, L04, L05, K01,
K02, K03).

Set B is the set the restricted scenario should use, because it is the
largest set that a network-restricted arm can answer *and* that the
baseline arm cannot answer by browsing: the answer requires the local
data lake and the local models, and the join between them.

## What the local structure cache has to contain

The 11 entries the LOCAL prompts need (and the 4 more the MIXED
prompts need): 1T4J, 1OPK, 1V4S, 3O96, 5EHR, 1PZO, 5MO4, 6OIM, 1BTL,
2SHP, 1AKE - as PDB **and** mmCIF, so that the ligand records, the
contacts and the UniProt alignment are all available offline. The cache
is 22 files, 9.3 MB, and it is mounted read-only and identically into
both arms.

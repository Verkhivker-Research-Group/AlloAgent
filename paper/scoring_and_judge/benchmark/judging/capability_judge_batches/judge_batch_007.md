# Judge batch 007 of 8

## Instructions to the judge (paste at the top of every session)

You are scoring answers to protein-science questions. You will see up to 10
runs. Each run has an opaque run ID, the question that was asked, the protein
the question is about, a list of checklist items, and the final answer that a
software agent produced. Score each run independently of the others.

Rules:

1. Judge only what is written in the final answer. Do not reward effort, tools
   used, or confidence. Do not guess what the agent did.
2. Use only the facts in the checklist as ground truth. If the answer states a
   fact that is not in the checklist and you cannot tell whether it is true,
   do not count it for or against the run.
3. Tool names that exist in only one system have been replaced by `[TOOL]`.
   Do not try to infer which system produced an answer.
4. If the answer is about a different protein than the intended one, Goal
   Completion is null.
5. Quote the shortest span of the answer that supports each decision.
6. Do not read, compare, or refer to other runs in the batch when scoring one.

### Goal Completion

- full: every part of the request is answered with substantive results for the
  intended protein.
- partial: some parts are answered, others are missing or wrong.
- deferred: the answer explains how the analysis could be done, or asks the
  user to clarify, without doing it.
- null: empty, truncated, an error message, off topic, or about a different
  protein.

For questions marked HONEST-REPORTING in the checklist, the correct answer is
that the data do not support a claim. Score a clear, correct statement of that
limit as full. Score an invented answer as null.

### Data Grounding (0, 1, 2)

- 0: conclusions rest on narrative only, with no identifiers, numbers, residues
  or structures stated.
- 1: some conclusions cite specific data (a database identifier, a numeric
  value, a residue index, a structure ID); others do not.
- 2: the main conclusions all cite specific data stated in the answer.

### Final Answer Complete

yes if the answer ends in a clear final response to the question; no if it is
cut off, ends mid-analysis, or only describes a plan.

### Checklist items

For each item listed for the run, give one of:

- correct: the answer states the fact or result the item asks for.
- incorrect: the answer states something that contradicts the item.
- missing: the answer does not address the item.
- not_applicable: the item names a specific method, or gives a reference result
  for a specific method, and the answer used a different method. Do not score
  it as incorrect or missing.

Rules for deciding:

1. If an item only asks that something be reported (for example "the rank is
   reported"), it is correct when the answer reports it. Do not compare the
   value with a reference that belongs to another method.
2. If an item requires a statement (for example a stated limit of a method),
   it is correct when the answer says it in substance. The wording does not
   need to match the item.
3. If an item says the answer must name its method and lists example methods,
   any named method satisfies it unless the item says otherwise.
4. An item that lists several required parts (for example "X, Y and Z are all
   present") is correct only when every part is present. If any part is absent,
   give `missing`; if a part contradicts the item, give `incorrect`.
5. An item that is only a JSON object is the reference output of the method it
   names. It is correct when the answer's result for that method has the same
   rank and overlap values (differences in rounding do not matter) and
   `not_applicable` when the answer used a different method.
6. Give exactly one verdict for every item marked `[judged]`, including items
   tagged `[low-information item]`. Never leave a judged item out. If you cannot
   tell, use `missing`, or `not_applicable` if the answer used a different
   method. Before you answer, check that your list of items for each run has
   every `[judged]` item from that run's checklist.

### Reading of one item

- S04_d ("the contact residues fall in the PH domain of AKT1"): the ligand's
  contacts lie at the PH-kinase interface, so some contacts are in the PH domain
  (residues 5-108) and some in the kinase domain. Give `correct` when the answer
  identifies the contacts that lie in the PH domain and puts the domain boundary
  in the right place, even if it also reports kinase-domain contacts. Give
  `incorrect` only if it assigns the contacts to the wrong domains.

Items marked `scripted` were already scored by a program. Do not score them;
they appear only for context. Items marked `critical` decide success.
Items that depend on the method (pocket-detection prompts) are written so that
any listed method counts; read the item text.

### Output format

Return one JSON object per run, in a single JSON array, and nothing else:

```
[
  {
    "run_id": "<opaque id>",
    "goal_completion": "full|partial|deferred|null",
    "data_grounding": 0,
    "final_answer_complete": "yes|no",
    "items": [
      {"item_id": "<id>", "verdict": "correct|incorrect|missing|not_applicable",
       "evidence": "<shortest supporting quote, or empty if missing>"}
    ],
    "notes": "<one sentence, only if something unusual affected the score>"
  }
]
```

---

=== RUN ro0u41nxm7x ===
QUESTION:
In BioLiP, how many ligand binding entries are curated for human PTP1B (P18031)? How many of them are for a non-metal ligand, and how many carry a recorded binding affinity? For the ligand with the code INX, give its recorded affinity.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X03_a] [critical] [scripted] 409
[X03_b] [critical] [scripted] 400
[X03_c] [critical] [scripted] 92
[X03_d] [critical] [scripted] INX
[X03_e] [critical] [scripted] 0.25

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Answer

| Quantity (BioLiP, UniProt **P18031** = human PTP1B) | Value |
|---|---|
| Curated ligand-binding entries | **113** |
| …of which for a **non-metal** ligand | **112** (103 regular + 9 peptide-ligand entries) |
| …of which are **metal** ligands | 1 (Mg²⁺, PDB **1WAX**, site BS01) |
| Entries carrying a **recorded binding affinity** | **92** (21 have none) |
| Ligand **INX** recorded affinity | **Ki = 0.25 µM** (Binding MOAD *and* PDBbind-CN); BindingDB additionally records **Kd = 220–250 nM** |

Supporting detail for INX: BioLiP entry **PDB 1G7G**, chain A, binding site BS01 (resolution 2.20 Å); source reference PubMed **11341829** (Bleasdale et al., *Biochemistry* 2001 — “Small molecule peptidomimetics … inhibit protein tyrosine phosphatase 1B”). BioLiP's manual-literature-survey column is empty for this row.

---

## How these numbers were obtained (and provenance)

**Important context:** the BioLiP web service (`bilip.biochem.duke.edu`) has been retired — the hostname is now NXDOMAIN, and there are no Wayback/Common-Crawl copies. I therefore worked from the **official legacy BioLiP1 database release** that the BioLiP group published to Zenodo:
- *“Data for the legacy BioLiP1 database, part 1 / part 2”* — Zenodo records **10.5281/zenodo.8407896** and **10.5281/zenodo.8407920** (“web service data for version 1 of the BioLiP database, last update in April 01, 2022”). I streamed/decompressed this 67 GB bzip2 archive in-part and extracted BioLiP's live web-service files.

**Data used:** `BioLiP/download/All.txt` (identical in content to `BioLiP/download/BioLiP_2013-03-6.txt`), BioLiP's 20-column annotation format:
`PDB ID | PDB chain | Resolution | Site# | Ligand ID | Ligand chain | serial | binding residues | (renumbered) | catalytic residues | (renumbered) | EC | GO | affinity-manual | affinity-BindingMOAD | affinity-PDBbind-CN | affinity-BindingDB | UniProt ID | PubMed ID | receptor sequence`.

**“Non-metal” definition:** taken from BioLiP's own site logic — its homepage defines “metal ligands” by an explicit 47-code list (`LA, NI, 3CO, K, CR, ZN, CD, PD, TB, YT3, OS, EU, NA, RB, W, YB, HO3, CE, MN, TL, LI, MN3, AU3, AU, EU3, AL, 3NI, FE2, PT, FE, CA, AG, CU1, LU, HG, CO, SR, MG, PB, CS, GA, BA, SM, SB, CU, MO, CU2`), with peptide ligands `III/UUU/NUC` counted separately. For P18031, only one entry uses a metal ligand (Mg²⁺ in 1WAX), so 112/113 are non-metal.

**Validation performed**
- My affinity criterion (“any of BioLiP’s four affinity columns populated”) reproduces BioLiP’s own published global statistic **exactly** (“entries with binding affinity data = 23,492”).
- INX occurs in **only one** PDB structure overall (1G7G, confirmed via RCSB/wwPDB search of all entries containing chemical component INX).
- The INX value is independently confirmed in **PDBbind v2020**’s index: `1g7g 2.20 2001 6.60 Ki=0.25uM // 1g7g.pdf (INX)`.
- Cross-checked the P18031 entry set against RCSB (441 PDB entries map to P18031; BioLiP’s curated set covers 100 of them with 102 distinct PDB–ligand pairs and 89 distinct ligand codes).

**Caveat on completeness:** BioLiP1’s live database was larger (573,225 entries; “last update April 1, 2022”) than the annotation export I could extract in the available time. Its December-2021 peptide-ligand export (`BioLiP_20211210016_154_.csv`) contains **4 additional P18031 peptide entries not present in the annotation export** (3ZMP ×2, 3ZMQ, 4ZRT). So a live-site query may report **≥117 total (≥116 non-metal)** entries, while the affinity-bearing count (92) and the INX value (Ki = 0.25 µM) are unchanged.

---

## Plan (completed)

1. [✓] Check environment/network access and locate the BioLiP binding data — live site confirmed retired (DNS NXDOMAIN); located the official BioLiP1 database release on Zenodo.
2. [✓] Download/stream the BioLiP data and inspect its schema — extracted BioLiP’s annotation file, download README, homepage statistics and CGI scripts (incl. the site’s own metal-ligand code list).
3. [✓] Filter records for UniProt P18031 and count: total entries, non-metal entries, entries with a recorded affinity (113 / 112 / 92), with the affinity criterion validated against BioLiP’s published global stat.
4. [✓] Extract the recorded affinity for ligand code INX (PDB 1G7G): Ki = 0.25 µM (Binding MOAD + PDBbind-CN), Kd = 220–250 nM (BindingDB); independently confirmed via PDBbind v2020.
5. [✗] Cross-check against the live BioLiP web record — not possible: the BioLiP domain no longer resolves and no archived snapshots exist; substituted with cross-checks against BioLiP’s own published statistics, its CGI query logic, PDBbind v2020 and RCSB/wwPDB.
=== END RUN ro0u41nxm7x ===

=== RUN rq89g7y19to ===
QUESTION:
In the pinned ClinVar release, list the pathogenic or likely pathogenic missense variants of human PTPN11 (Q06124) whose AlphaMissense score is above 0.9 and whose residue has a heavy atom within 8 A of any heavy atom of the SHP099 ligand in PDB 5EHR chain A. Give, for each, the variant, its ClinVar variation id, its AlphaMissense score and the nearest heavy-atom distance. The pinned release and the live service differ in how they classify a record, so answer from the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X06_a] [critical] [scripted] 7
[X06_b] [critical] [scripted] {"residues": [110, 491, 498]}
[X06_c] [critical] [scripted] {"E110K": 0.9908, "E110A": 0.9621, "P491H": 0.9611, "P491L": 0.9431, "R498Q": 0.9993, "R498W": 0.9998, "R498L": 0.9995}
[X06_d] [critical] [scripted] {"110": 3.465, "491": 3.454, "498": 7.154}
[X06_e] [critical] [scripted] {"variation_ids": [40507, 40508, 40551, 40552, 1805026, 40553, 40554], "allele_ids": [48977, 48978, 49021, 49022, 1862041, 49023, 49024]}
[X06_f] [critical] [judged] the answer states, for every variant it lists, the nearest heavy-atom distance from the variant residue to the SHP099 ligand in 5EHR chain A, and that every residue it lists lies within 8 A of it

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Final plan status

1. [✓] Queried the pinned local ClinVar release for PTPN11 pathogenic and likely-pathogenic records.
2. [✗] Direct RCSB retrieval was blocked by a proxy error; [✓] used the local 5EHR mmCIF instead.
3. [✗] Live UniProt/SIFTS mapping was blocked; [✓] derived residue mapping from the deposited 5EHR mmCIF alignment.
4. [✗] Bulk AlphaMissense wrapper queries timed out; [✓] extracted scores from the pinned AlphaMissense SQLite index.
5. [✓] Joined missense ClinVar records to AlphaMissense scores and SHP099 contacts.
6. [✓] Independently recomputed and verified the nearest heavy-atom distances.
7. [✓] Finalized the pinned-release result below.

## Result

Using the pinned release’s own pathogenic/likely-pathogenic filters, **11 records** satisfy all three conditions:

- Human PTPN11, UniProt **Q06124**
- Missense substitution
- AlphaMissense score **strictly >0.9**
- Residue within **8 Å** of SHP099 in PDB **5EHR**, chain A

SHP099 is chemical component **5OD** in 5EHR.

| Variant | ClinVar variation ID | Pinned ClinVar classification | AlphaMissense score | Nearest heavy-atom distance |
|---|---:|---|---:|---:|
| p.Glu110Ala | 40508 | Pathogenic/Likely pathogenic | 0.9621 | 3.47 Å |
| p.Glu110Asp | 561745 | Conflicting classifications of pathogenicity | 0.9630 | 3.47 Å |
| p.Glu110Gly | 1339747 | Conflicting classifications of pathogenicity | 0.9705 | 3.47 Å |
| p.Glu110Lys | 40507 | Pathogenic/Likely pathogenic | 0.9908 | 3.47 Å |
| p.Glu258Asp | 44613 | Conflicting classifications of pathogenicity | 0.9577 | 6.63 Å |
| p.Glu258Lys | 982429 | Conflicting classifications of pathogenicity | 0.9988 | 6.63 Å |
| p.Pro491His | 40551 | Pathogenic/Likely pathogenic | 0.9611 | 3.45 Å |
| p.Pro491Leu | 40552 | Pathogenic | 0.9431 | 3.45 Å |
| p.Arg498Gln | 1805026 | Likely pathogenic | 0.9993 | 7.15 Å |
| p.Arg498Leu | 40554 | Pathogenic | 0.9995 | 7.15 Å |
| p.Arg498Trp | 40553 | Pathogenic/Likely pathogenic | 0.9998 | 7.15 Å |

### Strict aggregate P/LP interpretation

If “pathogenic or likely pathogenic” is intended to require the **strict aggregate ClinVar label** to be Pathogenic, Likely pathogenic, or Pathogenic/Likely pathogenic, the requested list is the following **seven** records:

- p.Glu110Ala — **40508** — 0.9621 — 3.47 Å
- p.Glu110Lys — **40507** — 0.9908 — 3.47 Å
- p.Pro491His — **40551** — 0.9611 — 3.45 Å
- p.Pro491Leu — **40552** — 0.9431 — 3.45 Å
- p.Arg498Gln — **1805026** — 0.9993 — 7.15 Å
- p.Arg498Leu — **40554** — 0.9995 — 7.15 Å
- p.Arg498Trp — **40553** — 0.9998 — 7.15 Å

The other four records are shown separately in the full table because the pinned `pathogenic` significance filter is keyword-based and therefore also returns records whose aggregate label is **“Conflicting classifications of pathogenicity.”** I have not silently relabeled them as pathogenic or likely pathogenic.

### Provenance and verification

- ClinVar source: **pinned local release**, completed **2026-10-23**, SHA-256 `b235cd5742ac615d55703672751fa3ea71c8222d5ff0547cd1e9b107fd8a647f`
- The live ClinVar service was **not used**.
- AlphaMissense source SHA-256 recorded by the pinned index: `bc18d954a9aa6b9efab8e40d6d1912e32b774906cd3846a1f51066588e9c176d`
- Structure: local `/data/structures/5ehr.cif`
- Independent coordinate calculations reproduced the rounded distances as 3.465 Å (GLU110), 6.630 Å (GLU258), 3.454 Å (PRO491), and 7.154 Å (ARG498).
=== END RUN rq89g7y19to ===

=== RUN rs807s41w19 ===
QUESTION:
In BioLiP, how many ligand binding entries are curated for human PTP1B (P18031)? How many of them are for a non-metal ligand, and how many carry a recorded binding affinity? For the ligand with the code INX, give its recorded affinity.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X03_a] [critical] [scripted] 409
[X03_b] [critical] [scripted] 400
[X03_c] [critical] [scripted] 92
[X03_d] [critical] [scripted] INX
[X03_e] [critical] [scripted] 0.25

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Plan completed
1. [✓] Retrieve PDB entries linked to human PTP1B UniProt P18031.
2. [✓] Retrieve and inspect BioLiP interaction records, affinity fields, and ligand composition.
3. [✓] Aggregate PTP1B ligand-binding entries and classify metal-containing ligands.
4. [✓] Cross-check all counts with `[TOOL]` across the 326 relevant PDB entries.

### BioLiP results for PTP1B (P18031)

| Metric | Count |
|---|---:|
| Total ligand-binding entries | **409** |
| Non-metal ligand entries | **395** |
| Entries with a curated recorded affinity (`Affinity_Processed`) | **92** |
| `INX` recorded affinity | **Ki = 0.25 µM** |

The **395 non-metal entries** exclude 14 metal-containing entries: 9 magnesium (`MG`), 3 tungstate (`WO4`), and 2 vanadate (`VO4`) entries.

The `INX` record is PDB **1G7G**, chain **A**, binding site **BS01**, with the exact BioLiP affinity string **`Ki=0.25uM`**.

**Definition notes:** If “metal ligand” means only an elemental metal ion, only `MG` is excluded and the non-metal count is **400**. Likewise, counting any populated affinity-related column—including the auxiliary `Affinity_Value` field—gives **109** affinity-bearing entries; **92** is the curated `Affinity_Processed` count.
=== END RUN rs807s41w19 ===

=== RUN r94yagbv16i ===
QUESTION:
In the Allosteric Set Database release 202306, the hit-and-lead table (HL) lists the curated modulators: how many modulator records does it hold for human glucokinase (P35557), how many distinct modulator names do they carry, which activity types do they use and how many records use each type?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X02_a] [critical] [scripted] 171
[X02_b] [critical] [scripted] 170
[X02_c] [critical] [scripted] {"IC50": "IC50", "EC50": "EC50"}
[X02_d] [critical] [scripted] 170
[X02_e] [critical] [scripted] 1

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
Filtering the official **`ASD_Release_202306_HL.tar.gz`** table on `UniProt_ID == "P35557"` gives:

| Measure | Count |
|---|---:|
| Modulator records | **171** |
| Distinct modulator names | **170** |
| Distinct modulator IDs | **170** |
| `EC50` records | **170** |
| `IC50` records | **1** |

The one-record difference is explained by a single modulator appearing in two activity records: **2-amino-5-chloro-N-(thiazol-2-yl)benzamide** (`ASD01200034`) is listed once as `IC50` and once as `EC50`, both at 11.0 μM. Thus, the activity counts total 171 while there are only 170 distinct names.

**Provenance**
- Official archive: `https://mdl.shsmu.edu.cn/ASD2023Common/static_file/archive_2023/ASD_Release_202306_HL.tar.gz`
- Table: `ASD_Release_202306_HL.txt` — Release 5.01, created 2023-06-01
- Archive SHA-256: `6c5fcbe009de2206a47c32c1d46566596fe79101e9295e60f18cf0829c4f1159`
- The results were reproduced independently with three parsing methods.
=== END RUN r94yagbv16i ===

=== RUN rmowm6fk0p2 ===
QUESTION:
In the pinned ChEMBL 37 release, compare sotorasib and adagrasib against the KRAS target CHEMBL2189121: how many IC50 records does each have, what is the median IC50 of each, and what are the smallest and the largest IC50 recorded for sotorasib? The live ChEMBL service serves a later release, so report the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X07_a] [critical] [scripted] 8
[X07_b] [critical] [scripted] 49.0
[X07_c] [critical] [scripted] 7
[X07_d] [critical] [scripted] 10.0
[X07_e] [critical] [scripted] 7.0
[X07_f] [critical] [scripted] 10000.0

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
` block). The underlying work is nearly complete: the pinned ChEMBL 37 database is verified, and the unbounded row counts have been confirmed directly in the pinned DB (sotorasib = 8 IC50 rows, adagrasib = 7 IC50 rows, all in nM, no NULL values). I still need one final pass that prints every row with its relation/quality flags and computes the median, min, and max in code from the database itself, so every reported number is traceable to the pinned release rather than hand-copied.

**Plan update:**
1. [✓] Verify the local pinned ChEMBL 37 SQLite database (and its MANIFEST) is present and readable.
2. [✓] Query ChEMBL 37 (mode="local") for sotorasib IC50 records against target CHEMBL2189121.
3. [✓] Query ChEMBL 37 (mode="local") for adagrasib IC50 records against target CHEMBL2189121.
4. [ ] Compute counts, medians, and sotorasib min/max directly from the pinned DB rows (final verification with quality flags).
5. [ ] Report the pinned-release results with provenance (no live-service values).


import sqlite3, statistics, json
DB = "/data/chembl/chembl_37_sqlite/chembl_37.db"
con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
cur = con.cursor()
q = "SELECT m.pref_name, a.activity_id, a.standard_value, a.standard_units, a.standard_relation, a.pchembl_value, a.data_validity_comment, a.potential_duplicate, a.assay_type FROM activities a JOIN assays s ON s.assay_id=a.assay_id JOIN target_dictionary t ON t.tid=s.tid JOIN molecule_dictionary m ON m.molregno=a.molregno WHERE t.chembl_id='CHEMBL2189121' AND m.chembl_id=? AND a.standard_type='IC50' ORDER BY m.pref_name, a.standard_value"
out = {}
for mid in ["CHEMBL4535757", "CHEMBL4594350"]:
    rows = cur.execute(q, (mid,)).fetchall()
    for r in rows:
        print(r)
    vals = sorted(float(r[2]) for r in rows)
    med = statistics.median(vals)
    print("SUMMARY", mid, "n", len(vals), "median", med, "min", min(vals), "max", max(vals))
    out[mid] = {"n": len(vals), "median": med, "min": min(vals), "max": max(vals), "values": vals}
con.close()
print(json.dumps(out))
=== END RUN rmowm6fk0p2 ===

=== RUN rpjhwahv0fd ===
QUESTION:
In the Allosteric Set Database release 202306, the hit-and-lead table (HL) lists the curated modulators: how many modulator records does it hold for human glucokinase (P35557), how many distinct modulator names do they carry, which activity types do they use and how many records use each type?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X02_a] [critical] [scripted] 171
[X02_b] [critical] [scripted] 170
[X02_c] [critical] [scripted] {"IC50": "IC50", "EC50": "EC50"}
[X02_d] [critical] [scripted] 170
[X02_e] [critical] [scripted] 1

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Final plan
1. [✗] Locate the release using the specialized literature agent — failed because the configured credential/service was unusable.
2. [✗] Locate the release through PubMed/Scholar endpoints and the data lake — failed because the endpoints were proxy-blocked and the data lake was empty.
3. [✓] Locate the release through platform resources — identified `ASD_Release_202306_HL.csv`.
4. [✓] Recover and filter the P35557 records.
5. [✓] Compute record, distinct-name, and activity-type counts.
6. [✓] Cross-check against the archived release analysis.

### Result

Filtering **`ASD_Release_202306_HL.csv`** from the Allosteric Set Database release 202306 for human glucokinase (**UniProt P35557**) gives:

| Measure | Result |
|---|---:|
| Modulator records | **171** |
| Distinct modulator names | **170** |
| Records with activity type **EC50** | **170** |
| Records with activity type **IC50** | **1** |

Thus, the HL table contains **171 P35557 modulator records representing 170 distinct names**, and the only activity types used are **EC50** and **IC50**.
=== END RUN rpjhwahv0fd ===

=== RUN rs52nzz01g1 ===
QUESTION:
In the pinned ClinVar release, list the pathogenic or likely pathogenic missense variants of human PTPN11 (Q06124) whose AlphaMissense score is above 0.9 and whose residue has a heavy atom within 8 A of any heavy atom of the SHP099 ligand in PDB 5EHR chain A. Give, for each, the variant, its ClinVar variation id, its AlphaMissense score and the nearest heavy-atom distance. The pinned release and the live service differ in how they classify a record, so answer from the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X06_a] [critical] [scripted] 7
[X06_b] [critical] [scripted] {"residues": [110, 491, 498]}
[X06_c] [critical] [scripted] {"E110K": 0.9908, "E110A": 0.9621, "P491H": 0.9611, "P491L": 0.9431, "R498Q": 0.9993, "R498W": 0.9998, "R498L": 0.9995}
[X06_d] [critical] [scripted] {"110": 3.465, "491": 3.454, "498": 7.154}
[X06_e] [critical] [scripted] {"variation_ids": [40507, 40508, 40551, 40552, 1805026, 40553, 40554], "allele_ids": [48977, 48978, 49021, 49022, 1862041, 49023, 49024]}
[X06_f] [critical] [judged] the answer states, for every variant it lists, the nearest heavy-atom distance from the variant residue to the SHP099 ligand in 5EHR chain A, and that every residue it lists lies within 8 A of it

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Result

Using the **pinned ClinVar release**—release timestamp `2026-10-23T03:57:30Z`, SHA-256 `b235cd57…647f`—rather than the live service, **seven** PTPN11 missense variants satisfy all criteria:

| Variant | ClinVar Variation ID | Pinned ClinVar classification | AlphaMissense score | Nearest heavy-atom distance to SHP099 |
|---|---:|---|---:|---:|
| NM_002834.5(PTPN11):c.329A>C (p.Glu110Ala) | 40508 | Pathogenic/Likely pathogenic | 0.9621 | 3.465 Å |
| NM_002834.5(PTPN11):c.328G>A (p.Glu110Lys) | 40507 | Pathogenic/Likely pathogenic | 0.9908 | 3.465 Å |
| NM_002834.5(PTPN11):c.1472C>A (p.Pro491His) | 40551 | Pathogenic/Likely pathogenic | 0.9611 | 3.454 Å |
| NM_002834.5(PTPN11):c.1472C>T (p.Pro491Leu) | 40552 | Pathogenic | 0.9431 | 3.454 Å |
| NM_002834.5(PTPN11):c.1493G>T (p.Arg498Leu) | 40554 | Pathogenic | 0.9995 | 7.154 Å |
| NM_002834.5(PTPN11):c.1493G>A (p.Arg498Gln) | 1805026 | Likely pathogenic | 0.9993 | 7.154 Å |
| NM_002834.5(PTPN11):c.1492C>T (p.Arg498Trp) | 40553 | Pathogenic/Likely pathogenic | 0.9998 | 7.154 Å |

### Method and audit

- SHP099 is RCSB chemical component **5OD** in **PDB 5EHR, chain A**.
- The deposited `DBREF` maps chain A to **Q06124 residues 1–525**; the relevant structural residues are **Glu110, Pro491, and Arg498**.
- Distances are the minimum heavy-atom distances from the reference residue in the deposited structure to any of SHP099’s 23 heavy atoms. They were calculated independently from the PDB coordinates and agreed with the dedicated ligand-contact tool.
- The intersection contained **120** pinned pathogenic/likely-pathogenic missense alleles, **105** with AlphaMissense score `>0.9`, and **7** additionally within **8 Å** of SHP099.
- Labels explicitly marked “Conflicting classifications of pathogenicity” were excluded. All classifications above are the **pinned release’s** labels, not live-service classifications.
=== END RUN rs52nzz01g1 ===

=== RUN romg3ld2wdx ===
QUESTION:
For the apo structure of PDB 2LAO chain A, which ten residues does the PocketMiner model score highest for cryptic-pocket propensity, what is the score of the highest-ranked residue, and how many of the published cryptic-pocket residues of that structure fall among those ten? Name the overlapping residues.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X05_a] [critical] [scripted] {"residues": [163, 14, 230, 90, 70, 235, 180, 233, 231, 191]}
[X05_b] [critical] [scripted] 0.93533
[X05_c] [critical] [scripted] 2
[X05_d] [critical] [scripted] {"residues": [14, 70]}
[X05_e] [critical] [scripted] 15

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## PocketMiner ranking for PDB 2LAO chain A

| Rank | Residue | PocketMiner score |
|---:|---|---:|
| 1 | **VAL163** | **0.935330331326** |
| 2 | TYR14 | 0.919266402721 |
| 3 | TYR230 | 0.902997016907 |
| 4 | ALA90 | 0.902110517025 |
| 5 | SER70 | 0.899701297283 |
| 6 | VAL235 | 0.896404206753 |
| 7 | PHE180 | 0.894195377827 |
| 8 | PHE233 | 0.893886208534 |
| 9 | PHE231 | 0.893085300922 |
| 10 | PHE191 | 0.884182572365 |

- **Highest-ranked residue:** **VAL163**
- **Highest score:** **0.935330331326** (approximately **0.93533**)
- **Published cryptic-pocket residues represented in the top ten:** **2**
- **Overlapping residues:** **TYR14** and **SER70**

The published PocketMiner dataset contains 15 label-1 cryptic-pocket residues for 2LAO: Asp11, Tyr14, Phe52, Ser69, Ser70, Leu71, Ser72, Arg77, Leu117, Gly119, Ser120, Thr121, Gln122, Asp161, and Thr195. Thus, the top ten capture **2 of the 15 published residues**.

**Provenance:** PDB 2LAO; validated `[TOOL]` implementation; upstream PocketMiner `pm-dataset` label dictionary, where label 1 denotes residues forming a cryptic pocket based on the corresponding holo structure. Publication: Meller et al., *Nature Communications* 14 (2023), DOI **10.1038/s41467-023-36699-3**. Residue numbers are the deposited PDB chain-A numbering. The cleaned publication apo structure and unmodified RCSB 2LAO gave the same top-ten residues and scores.
=== END RUN romg3ld2wdx ===

=== RUN rjmhcyfzfp5 ===
QUESTION:
In the Allosteric Set Database release 202306, the allosteric-protein table (AP) lists the curated allosteric sites: how many site records and how many distinct PDB entries does it hold for human AKT1 (P31749)? For the 3O96 entry of that table: which chemical component is the bound ligand, which residues of chain A lie within 4 A of it, and which UniProt domain does each of those residues belong to?

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X08_a] [critical] [scripted] 77
[X08_b] [critical] [scripted] 32
[X08_c] [critical] [scripted] IQO
[X08_d] [critical] [scripted] {"residues": [205, 292, 272, 296, 268, 290, 80, 84, 211, 264, 210, 83, 85, 273, 274, 271, 82, 291]}
[X08_e] [critical] [judged] the answer assigns every residue it lists to the UniProt PH domain (5-108), the protein kinase domain (150-408) or the AGC-kinase C-terminal region (409-480) of P31749, with the boundaries stated

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
## Allosteric Set Database release 202306

For **human AKT1** (`uniprot_entry = AKT1_HUMAN`, `uniprot_id = P31749`), `ASD_Release_202306_AP.csv` contains:

- **77 curated site records**
- **31 distinct actual PDB entries**
- **32 distinct values in the `pdb_id` column**, because one value is `P31749-F1`, an AlphaFold-style model identifier rather than a four-character PDB ID.

The 32 values in the table are:

`1H10, 1UNP, 1UNQ, 1UNR, 2UVM, 2UZR, 2UZS, 3MV5, 3MVH, 3O96, 3OW4, 3QKK, 3QKL, 3QKM, 4EJN, 4EKK, 4EKL, 4GV1, 5KCV, 6BUU, 6CCY, 6HHF, 6HHG, 6HHH, 6HHI, 6HHJ, 6NPZ, 6S9W, 6S9X, 7NH4, 7NH5, P31749-F1`

## PDB 3O96

The AP table contains **one site record** for 3O96.

### Bound ligand

- **Chemical-component ID:** `IQO`
- **Chemical name:** 1-(1-(4-(7-phenyl-1H-imidazo[4,5-g]quinoxalin-6-yl)benzyl)piperidin-4-yl)-1H-benzo[d]imidazol-2(3H)-one
- **Location in 3O96:** chain A, residue 444

### Chain-A polymer residues within 4 Å of IQO

Distances below are minimum heavy-atom distances.

| Residue | Minimum distance (Å) | UniProt P31749 domain |
|---|---:|---|
| Trp80 (W80) | 3.41 | PH domain |
| Thr82 (T82) | 3.95 | PH domain |
| Val83 (V83) | 3.74 | PH domain |
| Ile84 (I84) | 3.46 | PH domain |
| Glu85 (E85) | 3.75 | PH domain |
| Ser205 (S205) | 2.89 | Protein kinase domain |
| Leu210 (L210) | 3.66 | Protein kinase domain |
| Thr211 (T211) | 3.58 | Protein kinase domain |
| Leu264 (L264) | 3.64 | Protein kinase domain |
| Lys268 (K268) | 3.26 | Protein kinase domain |
| Val271 (V271) | 3.90 | Protein kinase domain |
| Tyr272 (Y272) | 3.11 | Protein kinase domain |
| Arg273 (R273) | 3.75 | Protein kinase domain |
| Asp274 (D274) | 3.83 | Protein kinase domain |
| Ile290 (I290) | 3.38 | Protein kinase domain |
| Thr291 (T291) | 3.97 | Protein kinase domain |
| Asp292 (D292) | 3.06 | Protein kinase domain |
| Cys296 (C296) | 3.15 | Protein kinase domain |

**Total: 18 chain-A residues.**

The relevant UniProt P31749 domain boundaries are:

- **PH:** residues 5–108
- **Protein kinase:** residues 150–408
- **AGC-kinase C-terminal:** residues 409–480

Thus, the IQO contact shell comprises **five PH-domain residues and thirteen protein-kinase-domain residues**; none lies in the AGC-kinase C-terminal region.

**Sources:** `/biolab_data/data_lake/ASD_Release_202306_AP.csv`; local 3O96 mmCIF `/data/structures/3o96.cif`; UniProt P31749 domain annotations.
=== END RUN rjmhcyfzfp5 ===

=== RUN rc9rixfx1r7 ===
QUESTION:
In the pinned ClinVar release, list the pathogenic or likely pathogenic missense variants of human PTPN11 (Q06124) whose AlphaMissense score is above 0.9 and whose residue has a heavy atom within 8 A of any heavy atom of the SHP099 ligand in PDB 5EHR chain A. Give, for each, the variant, its ClinVar variation id, its AlphaMissense score and the nearest heavy-atom distance. The pinned release and the live service differ in how they classify a record, so answer from the pinned release.

INTENDED PROTEIN:  ()
PROMPT TYPE: normal

CHECKLIST (ground truth):
[X06_a] [critical] [scripted] 7
[X06_b] [critical] [scripted] {"residues": [110, 491, 498]}
[X06_c] [critical] [scripted] {"E110K": 0.9908, "E110A": 0.9621, "P491H": 0.9611, "P491L": 0.9431, "R498Q": 0.9993, "R498W": 0.9998, "R498L": 0.9995}
[X06_d] [critical] [scripted] {"110": 3.465, "491": 3.454, "498": 7.154}
[X06_e] [critical] [scripted] {"variation_ids": [40507, 40508, 40551, 40552, 1805026, 40553, 40554], "allele_ids": [48977, 48978, 49021, 49022, 1862041, 49023, 49024]}
[X06_f] [critical] [judged] the answer states, for every variant it lists, the nearest heavy-atom distance from the variant residue to the SHP099 ligand in 5EHR chain A, and that every residue it lists lies within 8 A of it

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
### Result

Using the **pinned local ClinVar snapshot**—reported by the local tool as release `2026-10-23T03:57:30Z`—the following seven PTPN11 missense variants satisfy all three criteria:

1. aggregate classification is **Pathogenic**, **Likely pathogenic**, or **Pathogenic/Likely pathogenic**;
2. AlphaMissense score is **> 0.9**; and
3. the reference residue has a heavy atom within **8 Å** of SHP099 (`5OD`, chain A, residue 601) in PDB 5EHR.

| Variant | Transcript / cDNA | ClinVar Variation ID | Pinned ClinVar classification | AlphaMissense | Nearest heavy-atom distance |
|---|---|---:|---|---:|---:|
| p.Glu110Ala | NM_002834.5(PTPN11):c.329A>C | **40508** | Pathogenic/Likely pathogenic | **0.9621** | **3.465 Å** |
| p.Glu110Lys | NM_002834.5(PTPN11):c.328G>A | **40507** | Pathogenic/Likely pathogenic | **0.9908** | **3.465 Å** |
| p.Pro491His | NM_002834.5(PTPN11):c.1472C>A | **40551** | Pathogenic/Likely pathogenic | **0.9611** | **3.454 Å** |
| p.Pro491Leu | NM_002834.5(PTPN11):c.1472C>T | **40552** | Pathogenic | **0.9431** | **3.454 Å** |
| p.Arg498Gln | NM_002834.5(PTPN11):c.1493G>A | **1805026** | Likely pathogenic | **0.9993** | **7.154 Å** |
| p.Arg498Leu | NM_002834.5(PTPN11):c.1493G>T | **40554** | Pathogenic | **0.9995** | **7.154 Å** |
| p.Arg498Trp | NM_002834.5(PTPN11):c.1492C>T | **40553** | Pathogenic/Likely pathogenic | **0.9998** | **7.154 Å** |

### Structural verification

Distances are minimum heavy-atom separations in chain A:

- **Glu110 O → 5OD N22:** 3.465 Å  
- **Pro491 CB → 5OD N7:** 3.454 Å  
- **Arg498 NH1 → 5OD CL2:** 7.154 Å  

The deposited 5EHR construct is the Q06124-2 sequence. Sequence alignment against canonical Q06124 confirmed that canonical and PDB author numbering coincide for the modeled residues 1–525.

### Release-control note

The live service was **not** used to determine classification. Records whose pinned aggregate label was “Conflicting classifications of pathogenicity” were excluded rather than treated as pathogenic or likely pathogenic.

### Final checklist

1. [✓] Verify the pinned ClinVar and AlphaMissense snapshots and their schemas
2. [✓] Retrieve and filter pinned PTPN11 pathogenic/likely-pathogenic missense records
3. [✓] Join the pinned Q06124 AlphaMissense scores and retain scores above 0.9
4. [✓] Identify SHP099 contacts in PDB 5EHR chain A and compute heavy-atom minima
5. [✓] Validate canonical-to-PDB numbering and audit all final rows
6. [✓] Compile the final seven-record table
=== END RUN rc9rixfx1r7 ===

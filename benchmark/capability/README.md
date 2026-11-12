# The capability benchmark: nine prompts (X01-X09)

**Status: FROZEN (2026-11-07).** The nine pilot AlloAgent runs (one per
prompt) were executed on 2026-11-07 and every prompt was scored; the set is
frozen. The pilot results, the three problems they exposed and the fixes are
in `pilot/pilot_report.md`.

This folder is a **new registry**. Nothing in `benchmark/benchmark_draft.json`,
`benchmark/checklists.json`, `benchmark/analysis_set.json`, `benchmark/results*`
or `docs/criteria_checksums.txt` is touched, and no id of the existing set is
reused.

| file | what it holds |
|---|---|
| `prompts.json` | the nine prompts (X01-X09), the restricted-egress repeat and the cache check |
| `checklists.json` | the items of every prompt, in the shape of `benchmark/checklists.json` |
| `keys.json` | every item's key value with its source file, version or checksum, and the tool-check result |
| `run_list_main.json` | the 27 (prompt, repeat) pairs of the main scenario |
| `run_list_restricted.json` | the 9 (prompt, repeat) pairs of the restricted repeat |
| `run_commands.sh` | the run commands for the 54 + 18 runs - **written, not run** |
| `pilot/pilot_report.md` | the pilot gate: the per-prompt results, the causes and the fixes |
| `pilot/pilot_item_verdicts.csv` | the per-item verdicts of the pilot runs |

## The purpose

These prompts expose capabilities **AlloAgent has and the baseline
(upstream BioMNI) arm lacks**. Every key comes from a **primary source**:
the ASD release 202306, the BioLiP table, the PocketMiner authors' published
dataset and reference implementation, the pinned ChEMBL 37, the pinned ClinVar
and AlphaMissense releases, the PDB coordinates and the UniProt records. No key
value is copied out of an AlloAgent tool's output.

### The honest limit of the claim

The gap these prompts measure is the **exposed tool set and the mounted
data**, and under the current harness it is enforced by the mounts. The
baseline arm's container gets the baseline worktree (read-only), the
per-run working directory, `/runs` and the **structure cache** (`/data/structures`,
the public PDB coordinates); it does **not** get `/biolab_data` (the Biolab
data lake: the ASD release 202306, the BioLiP pickles), `/data/chembl`,
`/data/clinvar` or `/data/alphamissense` (the pinned releases), or
`/opt/pocketminer` (the model, the authors' dataset and the reference
implementation - the pocketminer conda env, the model directory and the
weights are masked behind empty mounts). Every capability key file except
the public PDB coordinates is therefore unreadable by the baseline arm.

One thing this does **not** cover: the earlier 240-run launch of
2026-10-28 gave the baseline arm a copy of the data lake inside its own
per-run working directory (`/agent_cwd/data/biomni_data`), so 26 of its
traces mention that path, 10 mention the vendored `pocketminer-gvp` checkout
and one (`P04_r1`) actually ran the PocketMiner model from it. The current
harness does not stage it, and the capability runs therefore do not have it.

## The prompts

| id | the capability it needs | the AlloAgent-only tool or data | why the baseline arm cannot get it |
|---|---|---|---|
| X01 | the ASD curation of ABL1 | the ASD release 202306 (the AP and HL tables) through the ASD tools and the mounted lake | no ASD tool in the 221-name registry, no ASD path |
| X02 | the ASD modulators of glucokinase | the ASD release 202306 HL table (the modulators and their activity types) | the upstream BioMNI has no ASD curation |
| X03 | the BioLiP ligands of PTP1B | the BioLiP binding-site table (the ligands, the affinities, the non-metal split) | no BioLiP tool and no BioLiP table in the baseline |
| X04 | PocketMiner on the apo structure 6HB0 | the PocketMiner checkpoint and the authors' published test-set labels | no model, no checkpoint, no labels |
| X05 | PocketMiner on the apo structure 2LAO | the same | the same |
| X06 | the PTPN11 variants near the SHP099 ligand | the pinned ClinVar and AlphaMissense releases joined with the 5EHR coordinates | the pinned releases are not in the baseline's tools and it cannot join them to the structure |
| X07 | sotorasib and adagrasib against KRAS in ChEMBL 37 | the pinned ChEMBL 37 SQLite | the public API serves a later release with different counts |
| X08 | the ASD sites of AKT1 and the 3O96 contacts | the ASD AP table, the 3O96 coordinates and the UniProt domain features | no ASD curation, no route to the domain features |
| X09 | the 5MO4 myristoyl ligand, cross-referenced | the PDB chemical component, BioLiP and the pinned ChEMBL 37 joined | the baseline has neither BioLiP nor the pinned ChEMBL |

## The rules the items follow

* **3 to 6 items per prompt** (5 for X01-X05 and X08-X09, 6 for X06 and X07).
* **No naming-string items.** The prompt gives the accession; no item asks for
  the protein name, the gene symbol or the organism.
* **Exact identifiers and numbers are scored by script** (`kind` `exact`,
  `number`, `set`); only genuinely qualitative claims are `qualitative` items
  for the judge (X06's distance statement and X08's domain assignment).
* **Numbers accept PDB-style tokens.** The scorer reads `A601` as `601`
  (the `CHAIN_NUMBER_RE` of `benchmark/score_scripted.py`).
* **Method-conditional items defer.** Where a fact depends on the method the
  answer used, the item is judged only if the answer names the method; the
  two items of this set that could be method-dependent (the fpocket top-3 and
  the reference overlaps) are keyed on the single method the prompt names
  (PocketMiner), so they are not method-conditional here.
* **Where the pinned release and the live service differ, the item says so and
  carries a band.** X07 states that the live ChEMBL serves a later release, and
  the count items use the +/-10 % band that the V05 item uses.
* **No item asks for a name string the prompt gives away.**

## The overlaps with the 40 prompts (rule 5)

The proteins and the structures of the existing set are reused where the
curated records exist only for them. Every overlap is listed here.

| the capability prompt | the reused protein and structure | the existing prompts that use it | why it is unavoidable |
|---|---|---|---|
| X01 (ASD) | ABL1 P00519; the ASD entries include **5MO4** | S02, P05, L03, V04 (1OPK); S07, L03 (5MO4) | the ASD curation of ABL1 is the capability; the question asks about the curation, not a structure |
| X02 (ASD) | glucokinase P35557; the ASD entries include **1V4S** | S03, P06, V05 | the same |
| X03 (BioLiP) | PTP1B P18031; the BioLiP entries include **1T4J** (326 entries in total) | S01, P01, P07, H02, C01 | the BioLiP curation of PTP1B is the capability; the structure is not used by the question |
| X04, X05 (PocketMiner) | 6HB0 and 2LAO - **neither appears in the 40 prompts** (the authors' test set was checked against all 11 structures of the 40 prompts) | none | the authors' test set was chosen to avoid them |
| X06 (variants) | PTPN11 Q06124; the structure **5EHR** | S05, G03, L04 | the SHP099 ligand of 5EHR is the allosteric site the prompt asks about |
| X07 (ChEMBL) | KRAS CHEMBL2189121 | G01 (6OIM KRAS), V03 (6OIM KRAS) | the target is KRAS; no structure is used |
| X08 (ASD) | AKT1 P31749; the structure **3O96** | S04, V02 | the ASD curation names the 3O96 site; the prompt asks for that site's contacts |
| X09 (cross-reference) | the 5MO4 myristoyl ligand | S07, L03 | the prompt is about that ligand |

The **tool verification cases** (`docs/tool_cards/`) were checked as well:
the PocketMiner card's known answer is 1AKE, the ligand-contact card's cases
are 1T4J/FRJ, 1OPK/MYR+P16, 5MO4/AY7+NIL and 1V4S/MRK+GLC, and the
allosteric-workflow card's cases are 1T4J and 1OPK. **X04 and X05 (6HB0 and
2LAO) overlap with none of them**; X01, X02, X03, X06, X08 and X09 reuse
the structures those cards already verify, because the curation of the
protein they ask about exists only there.

## The pinned release against the live service

| source | the pinned release | the live service |
|---|---|---|
| ChEMBL 37 | the KRAS target CHEMBL2189121: sotorasib 8 IC50 records (median 49 nM), adagrasib 7 (median 10 nM) | the public API returns **the same** 8 and 7 records with the same medians today, but it serves a later release in general, so the items stay keyed on the pinned release |
| ClinVar (b235cd5742ac) | PTPN11: 568 pathogenic and 206 likely pathogenic records | the live service counts 392 pathogenic PTPN11 records, and the pinned release's aggregate strings also carry "Conflicting classifications of pathogenicity" - so the two classify differently |

The X07 items therefore name the pinned release, and the X06 items are
per-variant presence checks with a band of +/-2 on the count.

## The waiver (rule 3)

The existing rule "a tool must not return the key verbatim" is **waived for
this set**. The point of these prompts is whether the agent can use the
capability at all, not whether it can be kept from reading the answer off a
tool's output. The waiver is recorded here, as the rule requires.

## The pilot runs

One AlloAgent run per prompt (repeat 1) was executed on 2026-11-07 and scored
with the committed scorer and this folder's checklist: **45 of the 47 items
pass** - the two that remain are the judged items deferred to the judge, and the
two X08 items that the first pilot missed pass after the wording was tightened. The three
problems the pilots exposed - a bad key for X02, a bad key for X06 and
ambiguous wording for X08 - were fixed in the wording and the keys, and each
fix was re-run and re-scored. The details are in `pilot/pilot_report.md`.

## The tool check (the step before the pilots)

Every needed tool was called directly in the eval image, with no LLM, and its
output compared with the key. **All the calls succeeded and all agreed with
the key**; the results are in `keys.json`
(`the_tool_check.the_tool_check_result`). The PocketMiner tool returns exactly
the authors' reference implementation's scores on the authors' apo structures
(6HB0: 0.926939, 0.904469, 0.89051, 0.889284, 0.882455; 2LAO: 0.93533,
0.919266, 0.902997, 0.902111, 0.899701).

The failures seen during the check were in the harness, not in the tools: the
BioLiP directory convention (the tool wants `<dir>/biolip/biolip.pkl`), the
ClinVar significance spelling (the tool wants `pathogenic`, not
`Pathogenic`), and the AlphaMissense data path (the tool wants the release
under `/data/alphamissense`). Nothing was patched in the evaluated code.

## The compatibility with the existing pipeline

* `benchmark/analyze_benchmark.py` reads three fixed paths
  (`benchmark/analysis_set.json`, `benchmark/checklists.json`,
  `benchmark/benchmark_draft.json`). The X prompts live in this folder, so
  the analysis of the 40 prompts is untouched.
* `benchmark/export_judge_batches.py` takes `--analysis-set`, `--checklists` and
  `--draft` as **file paths**, so the judge batches of this set are made by
  pointing it at this folder; no new judge script is needed.
* The criteria checksum guard (`tests/test_criteria_checksum_guard.py`) hashes
  the 23 files listed in `docs/criteria_checksums.txt`, all of them
  `docs/*_criteria.md`. Nothing in `benchmark/capability/` is listed, so the
  guard is untouched.
* No test walks `benchmark/` recursively.
* The new scripts are `benchmark/run_capability_launch.py` (builds a throwaway
  launch checkout with the X prompt table and calls the driver) and
  `benchmark/score_capability.py` (scores the capability runs with the committed
  scorer and this folder's checklists).

## The restricted repeat

X02, X06 and X07 are also run under the existing restricted-egress
configuration (3 repeats x 2 arms = 18 runs). The structures and the data
they need are all present locally, so **nothing is missing from the read-only
cache and nothing in it has to be changed**:

* X06 needs 5EHR - present in the read-only structure cache
  (`data/structures_cache/5ehr.pdb`), the pinned ClinVar and AlphaMissense
  releases - present (`data/clinvar`, `data/alphamissense`);
* X07 needs the pinned ChEMBL 37 - present
  (`data/chembl/chembl_37_sqlite/chembl_37.db`);
* X02 needs the ASD release 202306 - present in the mounted lake
  (`data/biomni_data/asd` and `data/biomni_data/data_lake`).

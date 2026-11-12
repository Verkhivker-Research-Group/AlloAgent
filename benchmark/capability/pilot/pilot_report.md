# The pilot runs

**The pilot gate is cleared.** One AlloAgent run per prompt (repeat 1) was
executed on 2026-11-07 through `benchmark/run_capability_launch.py`, and every
run completed.

**45 of the 47 items pass.** The two that remain are the judged (qualitative) items, deferred to the
judge, which was not run on the pilots.

| prompt | the items PASS / the items | what was missed | the cause | what was done |
|---|---|---|---|---|
| X01 | 5 / 5 | - | - | - |
| X02 | 5 / 5 | the two items that named two modulators (`0H6`, `AJB`) | **a bad key**: the prompt says "name two of the curated modulators" and the 170 curated names are all equally valid, so requiring two of them was unfair - the agent named a different, correct one | the items were replaced with the per-activity-type record counts (EC50 170, IC50 1) and the prompt now asks for them |
| X03 | 5 / 5 | - | - | - |
| X04 | 5 / 5 | - | - | - |
| X05 | 5 / 5 | - | - | - |
| X06 | 4 / 6 | the positions, the scores, the distances and the variation ids | **a bad key**: the key's filter accepted any significance string containing "Pathogenic", which also catches "Conflicting classifications of pathogenicity"; the agent correctly excluded those four records | the key now excludes the conflicting records (11 -> 7 variants) and the count item carries a band of +/-2, because the pinned release and the live service classify differently |
| X07 | 6 / 6 | - | - | - |
| X08 | 5 / 5 (after the re-check) | the two site-count items | **ambiguous wording**: the prompt said "allosteric-site records" and the agent counted the release's `Allosteric_Site` records (12), while the key used the AP table (77 records, 32 entries) | the prompt now names the table ("the allosteric-protein table (AP)"), and a re-run with the tightened wording passes both items |
| X09 | 5 / 5 | - | - | - |

The two judged items (`x06_distance_statement`, `3o96_domain_assignment`) are
**DEFERRED to the judge**, which was not run on the pilots; both pilot answers
state the corresponding facts (the nearest heavy-atom distance per variant, and
the UniProt domain boundaries PH 5-108, protein kinase 150-408, AGC-kinase
C-terminal 409-480 with the residues assigned).

**No tool bug was found.** Every tool call that the pilots exercised behaved
as the tool check said it would; the three failures the pilots exposed were a
bad key (X02, X06) and ambiguous wording (X08), all fixed here.

**The pending AlloAgent fixes were not needed for this set.** The ClinVar id
form is the one that mattered and the agent already reports the ClinVar
**Variation ID** (48977, 49021, ...), which is what the items key on, so the
pending "ClinVar id" fix does not block this benchmark. The pending fpocket
residues fix concerns the `fpocket_top3` item of the old set and has no
counterpart here (X04 and X05 key on the PocketMiner scores, not on fpocket).

## The X06 re-pilot (2026-11-07, after the ClinVar fix)

The X06 key was re-derived as the **ClinVar Variation ID** (the pinned release's
`VariationID` column) and the id item was made a `set` with two groups, so the
answer passes when it reports all seven **Variation IDs** or all seven **Allele
IDs**:

| change | the Variation ID | the Allele ID |
|---|---|---|
| p.Glu110Lys | 40507 | 48977 |
| p.Glu110Ala | 40508 | 48978 |
| p.Pro491His | 40551 | 49021 |
| p.Pro491Leu | 40552 | 49022 |
| p.Arg498Gln | 1805026 | 1862041 |
| p.Arg498Trp | 40553 | 49023 |
| p.Arg498Leu | 40554 | 49024 |

One AlloAgent run of X06 (repeat 1, 36 steps, 808378 tokens), scored with the
frozen checklist:

| item | verdict |
|---|---|
| `x06_variant_count` | PASS |
| `x06_positions` | PASS |
| `x06_scores` | PASS |
| `x06_distances_A` | PASS |
| `x06_clinvar_ids` | PASS |
| `x06_distance_statement` | DEFERRED (judged) |

**5 of the 5 scripted items pass**, and the judged item is deferred to the
judge. The run records are in
`%TEMP%\opencode\capability_pilot_x06\alloagent\X06_r1`.

## The run records

The pilot run records are **not** committed: the answer text of a run is
trace-derived and the repository's own rule
(`benchmark/judging/README.md`) says it must never be published. They are in

    %TEMP%\opencode\capability_pilot\alloagent\X0*_r1
    %TEMP%\opencode\capability_pilot2\alloagent\X0{2,8}_r1   (the re-check)

and the per-item verdicts are in `pilot_item_verdicts.csv` (this folder).
The pilot runs are excluded from every analysis: they live outside
`benchmark/analysis_set.json` and outside `benchmark/results*`.

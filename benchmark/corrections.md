# The dated correction notes of the benchmark

Every correction is dated, names the committed value it keeps, and states
the measurement that the corrected value rests on.  **No committed
checklist is edited by this file**: the checklists stay exactly as they
were committed, the corrected values live here and in the machine-readable
file next to this note, and the scoring reports both.

The corrections are applied by `benchmark/score_analysis_set.py` with
`--corrections`; the primary scoring (the committed values) is always
produced too, so the reader can see what the correction changes and what
it does not.

---

## Dated note 2026-11-02: the pocket reference picked the wrong pocket

### What is contradicted

The committed item `fpocket_reference_P01` (and its twin
`fpocket_reference_P07`, the same structure and the same site) carries

```json
{"method": "fpocket",
 "rank_of_the_pocket_covering_the_site": 7,
 "overlap_of_the_covering_pocket": 2,
 "top3_ranks": [1, 2, 3], "top3_overlap": [0, 0, 0]}
```

while the dated note attached to the same prompt (2026-10-26) says

> for 1T4J the FRJ pocket is fpocket's **pocket 11**, rank 11 by score,
> and the top three fpocket pockets overlap the FRJ site by 0

and the analysis plan's dated note of 2026-10-29 records the same
contradiction and kept both:

> the `fpocket_reference_P01` item expects the covering pocket at rank 7
> with an overlap of 2, while its own dated note says the FRJ pocket is
> fpocket's pocket 11 with 8 shared residues.  Both are in the committed
> file and both are kept; the results are reported as committed.

### The cause

`benchmark/pocket_reference_outputs.py` defines the covering pocket in its
docstring as "the pocket with the **most** site residues", but the code
takes the **first** pocket in rank order that contains **any** site
residue:

```python
best = None
for row in rows:
    if row["site_residues_in_pocket"] > 0:
        best = row
        break
```

The two rules differ whenever a later pocket covers the site better.

### The measurement

The reference was **re-measured** with the current code, in the same image
the benchmark runs in (`alloagent-eval:v6`), with the same wrappers the
agent uses and the same site residues (the residues within 4 A of the
ligand, from `get_ligand_contacts`):

* the script: `benchmark/pocket_reference_outputs_v2.py` (new; it computes
  **both** selections and writes the per-pocket residue numbers, so every
  number below can be checked);
* the output: `benchmark/pocket_reference_outputs_v2.json` (new);
* the committed `benchmark/pocket_reference_outputs.json` is **unchanged**.

For the ligand-stripped 1T4J, fpocket returns 18 pockets and the FRJ
contact residues are 188, 189, 192, 193, 196, 200, 276, 277, 279, 280,
282. The pockets that contain them:

| fpocket rank | score | residues in the pocket | FRJ residues in the pocket |
|---:|---:|---:|---:|
| 7 | 0.123 | 10 | **2** |
| 8 | 0.123 | 15 | 2 |
| 11 | 0.069 | 12 | **8** |
| 16 | 0.028 | 11 | 1 |

The pocket that **covers** the site is rank 11 with 8 shared residues -
the number the dated note gives.  The committed value (rank 7, overlap 2)
is the first pocket with any overlap.

### The correction (the committed value is kept)

| item | committed (kept) | corrected |
|---|---|---|
| `fpocket_reference_P01` | rank 7, overlap 2 | **rank 11, overlap 8** |
| `fpocket_reference_P07` | rank 7, overlap 2 | **rank 11, overlap 8** |

The other three fields of the two items (`top3_ranks`, `top3_overlap`) are
unchanged by the correction: the top three fpocket pockets of 1T4J
overlap the FRJ site by 0, 0, 0 in both measurements.

### What was checked in the other pocket prompts

The same selection rule was applied to every site of the committed
reference file, and the corrected reference was measured for all six:

| site | prompts | committed (first with any overlap) | corrected (most site residues) | a committed item changes? |
|---|---|---|---|---|
| 1T4J (FRJ) | P01, P07 | rank 7, overlap 2 | **rank 11, overlap 8** | **yes** |
| 1OPK (MYR) | P05 | rank 3, overlap 8 | rank 3, overlap 8 | no |
| 1V4S (MRK) | P06 | rank 6, overlap 14 | rank 6, overlap 14 | no |
| 1V4S (GLC) | P06 (the glucose site) | rank 1, overlap 2 | **rank 2, overlap 13** | no committed item uses this site |
| 6OIM (MOV) | P02 | rank 1, overlap 16 | rank 1, overlap 16 | no |
| 5EHR (5OD) | P03 | rank 7, overlap 3 | **rank 40, overlap 15** | no committed item uses this site |

* **P02, P05, P06**: the committed items are already the corrected
  values; nothing changes.
* **P03**: the prompt asks about the pockets of **2SHP** against the
  SHP099 residues of 5EHR, and its pocket-detection criteria are
  qualitative (`pocket_recovery`, `method_named_P03`,
  `detector_limit_stated_P03`); there is **no** `fpocket_reference_P03`
  or `p2rank_reference_P03` item, so the 5EHR difference reaches no
  committed item.  It is recorded here because the judge of P03 needs it.
* **P06 and the glucose site**: the committed `fpocket_reference_P06` is
  the MRK (activator) site and is correct; the **glucose** site is a
  second site of the same structure and no committed item carries it.
  The judge of P06 needs the corrected glucose numbers (rank 2, 13
  shared residues).

### A second defect, in the P2Rank reference items

The same measurement shows that **no P2Rank pocket carries any residue**
in any of the six sites (every pocket has `n_residues = 0`), with the
current code as well as with the committed file.  The
`p2rank_reference_*` items therefore carry
`rank_of_the_pocket_covering_the_site: null` and
`overlap_of_the_covering_pocket: 0`, and the scorer's semantics turn
them into "the answer reports the number 0" (plus the top-three ranks
`[1, 2, 3]`, which almost every answer contains).  The item cannot
discriminate between an answer that used P2Rank correctly and one that
did not use it at all.

No value is changed for it here: the items are kept as committed, the
defect is recorded, and the judge's criterion for these items has to say
what a P2Rank answer must contain.  The recommendation is in the last
section.

### What was re-run

* the **primary** scoring of the 234-run analysis set is unchanged: the
  committed values are what the primary numbers use;
* the **corrected** scoring of the affected prompts (P01 and P07) was
  produced with the corrected values
  (`benchmark/score_analysis_set.py --corrections`), and the difference
  is this:

| run | committed criterion | corrected criterion | reason under the committed criterion | reason under the corrected criterion | verdict |
|---|---|---|---|---|---|
| alloagent P01 r1 | rank 7, overlap 2 | rank 11, overlap 8 | - | - | PASS / PASS |
| alloagent P01 r2 | rank 7, overlap 2 | rank 11, overlap 8 | - | - | PASS / PASS |
| alloagent P01 r3 | rank 7, overlap 2 | rank 11, overlap 8 | rank 7, overlap 2, top-3 ranks 2 and 3 missing | top-3 ranks 2 and 3 missing | FAIL / FAIL |
| baseline P01 r1 | rank 7, overlap 2 | rank 11, overlap 8 | rank 7 missing | overlap 8 missing | FAIL / FAIL |
| baseline P01 r2 | rank 7, overlap 2 | rank 11, overlap 8 | the answer names no method (deferred) | the answer names no method (deferred) | DEFERRED / DEFERRED |
| baseline P01 r3 | rank 7, overlap 2 | rank 11, overlap 8 | the answer names no method (deferred) | the answer names no method (deferred) | DEFERRED / DEFERRED |
| the six P07 runs | rank 7, overlap 2 | rank 11, overlap 8 | - | - | PASS / PASS |

**The correction changes no verdict and no total.**  The reason is
visible in the answers: they report the truth - "rank 11 (pocket 11) with
8 shared residues" - and they also mention the weaker pocket ("ranks 7
and 8 with 2 each"), so they satisfy both criteria at once.  The one
arm-A answer that fails does so under both criteria, because it does not
report the top-three ranks; the arm-A answer that reports "pocket 11 with
six shared residues" fails both criteria, because six is neither eight
nor two.

The two failures are therefore **not** caused by the wrong reference
value, and the correction does not rescue a run.

### The recommendation (not applied here)

1. Fix the selection rule in `benchmark/pocket_reference_outputs.py` (take
   the pocket with the most site residues, as its docstring says), and
   regenerate `benchmark/pocket_reference_outputs.json` **and** the two
   affected checklist items **in one commit**, with the checksums
   recomputed, as the plan requires for any change to the committed
   inputs.  This note is that change's dated record; it does not make it.
2. Give the `p2rank_reference_*` items a criterion that can discriminate
   (the P2Rank wrapper has to report the residues of a pocket, or the
   items have to be replaced by a criterion about the ranks P2Rank
   assigns to the site residues).
3. The judge batch of P03 and P06 needs the corrected reference for the
   5EHR and glucose sites, because their pocket criteria are judged, not
   scripted.

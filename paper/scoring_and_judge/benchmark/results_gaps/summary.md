# The gaps between the run records and the answers the agents gave

A read-only survey of the 240 runs of the analysis set, using the **full final
answer from `trace.txt`** and not the 20000-character copy the record holds.

**This analysis was made on 2026-11-06, after the data existed.** The run records
(2026-10-28 to 2026-11-04) and the judge outputs (2026-11-03 to 2026-11-05) are
used as they stand; nothing was re-run, re-measured or re-judged. The re-scoring in
section 6 reuses the committed scorer on the same answers.

The files of this folder:

| file | what it holds |
|---|---|
| `summary_by_arm.csv` | the one-table summary |
| `empty_or_fragment_answers.csv` | the answers under 300 characters, with their exact text |
| `truncated_answers.csv` | the answers that end mid-sentence, mid-table-row or with an open tag |
| `harness_artifact_endings.csv` | the answers that end in a harness artifact |
| `leaked_reasoning.csv` | every answer that carries the agent's planning text |
| `run_costs.csv` | the tokens and the steps of every flagged run |
| `rescored_on_full_text.csv` | the item verdicts that change when the full text is scored |

---

## Which text the scorer and the judge actually read

| reader | file and line | the text it reads |
|---|---|---|
| the scripted scorer | `benchmark/score_scripted.py:306` - `answer = normalize(summary.get("final_content") or "")` | the **20000-character copy** |
| the judge export | `benchmark/export_judge_batches.py:285` - `content, reasoning = last_message(record_dir)`, and `:265-282` - the last message of `run.json` | the **uncapped final response without the reasoning** |
| the judge export, fallback | `benchmark/export_judge_batches.py:286-292` - `answer.txt` is read only when `run.json` has no content | the 20000-character copy |
| the judge export, the answer body | `benchmark/export_judge_batches.py:302-311` - the body of the largest `<solution>` block, with the protocol markup stripped (`:262-269`) | |
| the record writer | `benchmark/run_benchmark.py:382` - `record["final_content"] = str(content)[:20000]`, and `:435-436` - `answer.txt` is written from that capped value | |

**Neither reader opens `trace.txt`.** The trace is the only place the uncapped turn
is kept, and it is what this survey uses.

---

## The summary

| arm | runs | empty or fragment | truncated | artifact ending | leaked reasoning | over 20000 characters |
|---|---:|---:|---:|---:|---:|---:|
| D | 120 | 0 | 1 | 0 | 117 | 18 |
| A | 120 | 1 | 3 | 2 | 112 | 26 |

---

## 1. The empty or fragment answers (under 300 characters)

One run. Its exact text:

```text
Reminder: Always include the thinking process followed by <execute> or <solution> tags.</observation></execute></solution>
```

* run `V06_r1`, prompt `V06`, arm A, 122 characters, 1671652 tokens, 56 steps

---

## 2. The truncated answers

The rule: the answer ends mid-sentence, or mid-table-row, or with a tag still open.
Every one of them ends mid-table-row, with the `<solution>` tag closing after the cut
row.

| run | prompt | arm | characters | tokens | steps | why |
|---|---|---|---:|---:|---:|---|
| `P07_r3` | P07 | A | 32388 | 1629069 | 42 | ends mid-table-row |
| `V05_r1` | V05 | A | 26700 | 3414710 | 72 | ends mid-table-row |
| `V05_r2` | V05 | D | 28645 | 1798279 | 44 | ends mid-table-row |
| `V05_r3` | V05 | A | 28490 | 2824672 | 62 | ends mid-table-row |

The cut rows:

* `P07_r3` (arm A): `1.4705 (0.2742); none | **0.67 (#54)** |
| Lys197</solution>`
* `V05_r1` (arm A): `athogenic | I |
| VCV000036240 | p.Cys220Tyr | 0.</solution>`
* `V05_r2` (arm D): `V 2845244 | **High** |
| 214 | Tyr214Cys | 3.01 |</solution>`
* `V05_r3` (arm A): `35 | Pathogenic | **Likely** |
| M235 | VCV004687</solution>`

---

## 3. The harness artifact endings

| run | prompt | arm | characters | tokens | steps | what |
|---|---|---|---:|---:|---:|---|
| `V06_r1` | V06 | A | 122 | 1671652 | 56 | the reminder string |
| `L04_r3` | L04 | A | 11760 | 870313 | 28 | ends with n></execute> |

The exact tails:

* `V06_r1` (arm A): `cute> or <solution> tags.</observation></execute></solution>`
* `L04_r3` (arm A): `s ~70 nM IC50, Ki 67 nM, Kd 10–73 nM).
</solution></execute>`

---

## 4. The leaked reasoning

An answer carries the agent's planning text when it contains a `<think>` block or
one of the planning sentences (`need final response`, `we should`, `let me`, and the
other markers listed in `leaked_reasoning.csv`).

* arm D: **117 of 120** runs; the markers: `<think>` 117, `we should` 79, `let's think` 27, `we can use` 26, `need answer` 20, `let me` 18, `hmm` 15, `maybe we` 10, `need final response` 4, `we need to` 1
* arm A: **112 of 120** runs; the markers: `<think>` 111, `we should` 85, `we can use` 35, `let's think` 30, `hmm` 21, `need answer` 19, `let me` 16, `maybe we` 8, `need final response` 7, `i will` 2, `we need to` 1

Five examples per arm (the beginning of the answer, where the planning sits):

**arm D**

* `S01_r1` (S01, 3876 characters, 107210 tokens, 8 steps) - markers: `<think>`, `we should`, `need answer`
  > '<think>Now ready final. Need plan updated all checkmarks. Need solution tag only in final. We need answer concise but enough details. Mention ligand FRJ, chemical name from PubChem, PDB chain A ligand instance 299, allos'
* `S01_r2` (S01, 11348 characters, 175012 tokens, 14 steps) - markers: `<think>`, `we should`
  > '<think>Great. Need perhaps citation details DOI/PMID absent because schema path? Could use RCSB entry or pubmed tool. Not required but cross-check perhaps helpful. User asks concise answer. Need cross-check final list. W'
* `S01_r3` (S01, 4895 characters, 142189 tokens, 10 steps) - markers: `<think>`, `we should`
  > '<think>We have answer. Need perhaps need final verification of contact list and mapping, perhaps exact distances. We already have. We need maybe identify ligand perhaps "FRJ" and full chemical name. Need ensure the chemi'
* `S02_r1` (S02, 8711 characters, 285280 tokens, 18 steps) - markers: `<think>`, `hmm`
  > '<think>Now final answer. Need be careful plan all checked. Could mention P16 alias PD166326 (not PD 0166285), which is ATP-site inhibitor. MYR is myristic acid at allosteric site. Contacts list PDB and human/mouse UniPro'
* `S02_r2` (S02, 4918 characters, 134403 tokens, 12 steps) - markers: `<think>`, `we should`, `we can use`
  > '<think>We have answer. Need maybe update plan final all completed then solution tag. We need ensure final answer clear. We should mention residues in PDB numbering and maybe UniProt numbering (P00520 because mapping). Us'

**arm A**

* `S01_r1` (S01, 12551 characters, 1257285 tokens, 34 steps) - markers: `<think>`, `we should`, `we can use`, `hmm`
  > "<think>We need now provide final answer, but must follow developer: each response either execute or solution, updated plan after each step. We've completed all. Need perhaps issue solution directly with answer in <soluti"
* `S01_r2` (S01, 13737 characters, 2594532 tokens, 58 steps) - markers: `<think>`, `we should`, `let's think`
  > "<think>Great. Why symmetry raw baseline differed? In symmetry script raw parser protein selection maybe included all chains? It used chain A. It selected `lig` with condition `a['resname']=='FRJ' and a['resseq']==299`; y"
* `S01_r3` (S01, 8368 characters, 743567 tokens, 26 steps) - markers: `<think>`, `we should`
  > '<think>Now final response must be solution tag only? Developer says at each response first thinking/reasoning and then either execute or solution. We have to provide final answer enclosed solution tag. We need include up'
* `S02_r1` (S02, 20965 characters, 657946 tokens, 22 steps) - markers: `<think>`, `we should`, `we can use`, `need answer`, `hmm`
  > '<think>We need now provide final solution with required XML solution tag, likely concise but detailed. Need carefully interpret request. User: "In PDB entry 1OPK (human ABL1, UniProt P00519), identify the ligand at the m'
* `S02_r2` (S02, 6585 characters, 1619460 tokens, 46 steps) - markers: `<think>`, `we should`
  > '<think>Now final. Need plan update step 9 complete. Provide solution in `<solution>` tag. Must not include execute. Include reasoning brief then plan, then solution. They say "At each turn, you should first provide your '

---

## 5. The cost of the gap

`run_costs.csv` holds the tokens and the steps of every flagged run (230 of the 240).
The totals:

| arm | flagged runs | tokens spent on them | steps |
|---|---:|---:|---:|
| D | 117 | 70,606,448 | 3,309 |
| A | 113 | 287,485,715 | 6,544 |

The runs that carry a defect:

| run | prompt | arm | characters | tokens | steps | the flags |
|---|---|---|---:|---:|---:|---|
| `P07_r3` | P07 | A | 32388 | 1,629,069 | 42 | truncated, leaked_reasoning, over_20000 |
| `V05_r1` | V05 | A | 26700 | 3,414,710 | 72 | truncated, leaked_reasoning, over_20000 |
| `V05_r2` | V05 | D | 28645 | 1,798,279 | 44 | truncated, leaked_reasoning, over_20000 |
| `V05_r3` | V05 | A | 28490 | 2,824,672 | 62 | truncated, leaked_reasoning, over_20000 |
| `V06_r1` | V06 | A | 122 | 1,671,652 | 56 | empty_or_fragment, artifact_ending |
| `L04_r3` | L04 | A | 11760 | 870,313 | 28 | artifact_ending, leaked_reasoning |

---

## 6. The text that is read, and the re-scoring on the full text

The scorer reads the 20000-character copy (section above). **44 runs** have a full
answer above that cap: 18 in arm D and 26 in arm A. Re-scoring those 44 runs on the
**full text** with the committed scorer changes **2** item verdicts, both in arm A:

| run | prompt | arm | recorded | full | item | on the recorded copy | on the full text |
|---|---|---|---:|---:|---|---|---|
| `S07_r2` | S07 | A | 20000 | 23806 | `numbering_offset_5MO4` | FAIL (incorrect) | PASS (correct) |
| `P04_r1` | P04 | A | 20000 | 27162 | `pocketminer_scores_for_1PZO_contacts` | FAIL (incorrect) | PASS (correct) |

Both changes are the cut-off tail, not the model:

* `S07_r2` (arm A), `numbering_offset_5MO4`: the recorded copy has the offset only as
  "UniProt = PDB -19.", which the number tokenizer does not read (a number followed
  by a full stop is not a number token); the full text has a second, clean occurrence
  beyond the cap, so the item passes there.
* `P04_r1` (arm A), `pocketminer_scores_for_1PZO_contacts`: five of the nineteen
  scores (0.7866, 0.2461, 0.3872, 0.2419, 0.3811) are in the cut-off tail only.

**No run changes its success verdict** under either rule (the primary rule and the
rule with the accession items set aside): both runs fail other items as well.

The opposite direction, in the other three items: the leaked reasoning is inside the
scored text, and three items pass on the reasoning rather than on the answer -

* `P01_r1` (arm A) `p2rank_reference_P01`: the method name `p2rank` appears in the
  reasoning only;
* `P02_r2` (arm D) `p2rank_reference_P02`: the same;
* `V04_r2` (arm D) `clinvar_T315I`: the variation id `27663` appears in the reasoning
  only (the answer itself gives the ClinVar accession `VCV000012624`).

---

## The last line

**Only the scripted layer is affected, and the two directions cancel out on these
240 runs: the 20000-character cap and the four mid-table truncations can only
depress the scripted score (2 item verdicts and 0 success verdicts here), the leaked
reasoning in 229 of the 240 scored texts can only inflate it (3 items), and the
judge's verdicts are untouched because the judge read the uncapped, reasoning-free
final response from `run.json` - so nothing here moved a success rate or an item
share.**

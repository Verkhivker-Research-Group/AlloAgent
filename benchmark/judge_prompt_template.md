# Judge prompt template (AlloAgent v2 benchmark)

Used by Claude Sonnet 5.5, one fresh session per batch of at most 10 runs.
Batches are shuffled across prompts and arms. The judge never sees the arm.
Fields in {{double braces}} are filled by the batch exporter from the committed
`benchmark/checklists.json` and the run records. Nothing else is added.

---

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

## Per-run block (repeated, up to 10 per session)

```
=== RUN {{run_id}} ===
QUESTION:
{{prompt_text}}

INTENDED PROTEIN: {{protein_name}} ({{uniprot_accession}})
PROMPT TYPE: {{normal|HONEST-REPORTING}}

CHECKLIST (ground truth):
{{for each item: [item_id] [critical|non-critical] [scripted|judged] item text}}

FINAL ANSWER (tool names replaced by [TOOL]; arm labels removed):
{{final_answer_text}}
=== END RUN {{run_id}} ===
```

---

## Exporter requirements (for the coding agent, not the judge)

- Run IDs are random, unique, and not derived from arm, prompt or repeat.
  The key (run_id -> arm, prompt, repeat) is stored in a separate file that is
  never placed in a batch.
- Redaction: replace every tool name that exists in only one arm with `[TOOL]`;
  remove the arm names, the prompt name `AlloAgent`, branch names and
  file paths that reveal the arm. Keep every number, identifier and residue.
- Order within a batch is random. A batch never has more than 10 runs.
- Each batch is a separate file, `judge_batch_NNN.md`, containing the
  instructions above followed by the run blocks.
- Log which runs were redacted in a way that changed an identifier or number
  (there should be none) and report them.
- Judge outputs are saved as `judge_batch_NNN.json`, one per batch, unedited.
- Scripted items are excluded from judging but listed for context.

---

## Change log (not sent to the judge)

The original text is in commit f0f9efe.

2026-11-03 (first change): added the `not_applicable` verdict and rules 1 to 3
to "Checklist items", and the verdict to the output format. Reason: in the first
three judged batches, a run that used a different pocket detector than the
reference was marked incorrect on method-specific items, and one item that only
asked for a rank to be reported was marked incorrect.

2026-11-03 (second change): added the rule that every `[judged]` item gets a
verdict, including `[low-information item]` items. Reason: in the rerun of
batches 1 to 4 the judge left out verdicts for P2Rank reference items (P05_f in
`r9u7lhi674p`, P06_f in `ro4vn8qojku` and `ri9t9wmz2yt`).

2026-11-03 (third change, after reading all 154 checklist items in the 24
batches): added rule 4 (multi-part items need every part), rule 5 (a bare JSON
item is the reference output of the method it names), renumbered the
verdict-for-every-item rule as rule 6, and added a reading of S04_d (the
checklist wording says the contacts fall in the PH domain, but the scripted
ground truth has 5 PH-domain and 13 kinase-domain contacts). The checklist
item itself is unchanged. All 24 batches are regenerated with this version, and
batches 1 to 4 are rerun.

For analysis, `not_applicable` items do not count against success; a sensitivity
analysis counts them as not correct.

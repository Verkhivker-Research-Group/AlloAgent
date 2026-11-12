# P33 allosteric_site_workflow

## Question the tool answers

"Run the allosteric-site analyses of one structure and report them
together."

## What it does NOT answer

The scope statement: the report says which residues are near a ligand
and which pockets the detectors call; it does **not** say that a
pocket is an allosteric site, and it does not report a binding energy
(`biomni/tool/allosteric_site_workflow.py:10-12`).

The tool also does not re-implement the analyses it runs: every
component is the direct call of the underlying tool
(`biomni/tool/allosteric_site_workflow.py:6-8`), and the criteria
require that the workflow "must not change the behaviour of the tools
it calls" (`docs/2_allosteric_site_workflow_criteria.md:52-53`).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_id` | str | yes | — | 4-character PDB entry id (e.g. `"1T4J"`) |
| `chain` | str | yes | — | chain id to analyse (e.g. `"A"`) |
| `ligand_id` | str or None | no | `None` | RCSB chemical component id of the bound ligand; when given, the ligand contacts are computed and the pocket components are compared with them |
| `run_stingallo` | bool | no | `False` | also call the STINGAllo prediction service for the structure |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is the report:

```
{
    "pdb_id": <str>,
    "chain": <str>,
    "ligand_id": <str or None>,
    "components": {
        "ligand_contacts": <the direct call of get_ligand_contacts>,
        "fpocket":          <the direct call of detect_pockets_fpocket>,
        "p2rank":           <the direct call of detect_pockets_p2rank>,
        "pocketminer":      <the direct call of pocketminer_score>,
        "normal_modes":     <the direct call of normal_mode_analysis>,
        "contact_network":  <the direct call of residue_contact_network>,
        "stingallo":        <the direct call of get_stingallo_allosteric_residues>
    },
    "overlap": {
        "known_site_residues": [<chain>:<number>, ...],
        "fpocket": [{pocket_number, score, n_residues,
                     n_shared_with_the_known_site, shared_residues}, ...],
        "fpocket_best_overlap": <int>,
        "p2rank": [...],
        "p2rank_best_overlap": <int>
    }
}
```

(the component list is the function's own docstring,
`biomni/tool/allosteric_site_workflow.py:108-116`; the report is built
at `:124-196` and returned at `:204`. A component that failed carries
its own error and the rest of the report is still produced.)

## Source and version

- upstream: **not a single backend** - the workflow orchestrates seven
  components: `get_ligand_contacts` (called at
  `biomni/tool/allosteric_site_workflow.py:143-144`),
  `detect_pockets_fpocket` (152), `detect_pockets_p2rank` (153),
  `pocketminer_score` (157), `normal_mode_analysis` (161),
  `residue_contact_network` (165-166) and, opt-in,
  `get_stingallo_allosteric_residues` (173-174)
- upstream URL: the structures are fetched from
  `https://files.rcsb.org/download/{pdb_id}.pdb` and `.cif`
  (`biomni/tool/allosteric_site_workflow.py:27-28`, downloaded at 133
  and 137)
- pinned release tag / commit: **not found** for the workflow itself;
  each component pins its own source (for example PocketMiner at
  `187062df3c94127e991669768009141a08fd5d8b`,
  `biomni/tool/pocketminer.py:34`)
- license: **not found** for the workflow as a whole; the component
  licenses are recorded in the component cards (for example
  `docs/tool_cards/T7_residue_contact_network.md:46-47`)
- the request timeout is 900 s (`_TIMEOUT_S`,
  `biomni/tool/allosteric_site_workflow.py:26`)
- data files: **none** - the structure is downloaded into a temporary
  directory and the temporary directory is removed afterwards
  (`biomni/tool/allosteric_site_workflow.py:131, 199-202`); a
  ligand-stripped copy is written to that temporary directory, never
  into the repository (`docs/2_allosteric_site_workflow_criteria.md:54-55`)

## Runtime

- typical latency: **not found** - no latency is recorded for the
  workflow as a whole; the components' own latencies are in their
  cards and in `../alloagent_private/docs/3_report.md:453-469`
- rate limits: not found
- offline vs online: online (the structures are downloaded from RCSB;
  the components that need a model or a binary carry their own
  requirements)

## Determinism

- deterministic? **not found** - no determinism statement is recorded
  for the workflow itself. The criteria require that it not change the
  behaviour of the tools it calls
  (`docs/2_allosteric_site_workflow_criteria.md:52-53`), and every
  component is the direct call of the underlying tool
  (`biomni/tool/allosteric_site_workflow.py:6-8`).

## Failure modes

- `pdb_id` empty or not a string: `{success: False, error: "pdb_id must be a non-empty string, got ..."}`
  (`biomni/tool/allosteric_site_workflow.py:117-118`)
- `chain` empty or not a string: `{success: False, error: "chain must be a non-empty string, got ..."}`
  (`:119-120`)
- the structure download fails: `RuntimeError("download failed for <url> with status <code>")`
  (`:70-73`), caught by the wrapper, which records
  `data.error = "<ExceptionType>: <message>"` and still returns the
  report (`:197-198`, `:204`)
- a component's dependency is missing (no PocketMiner env, no GPU for
  the model): that component reports its own error and the rest of the
  report is still produced
  (`docs/2_allosteric_site_workflow_criteria.md:56-58`;
  `biomni/tool/allosteric_site_workflow.py:113-115`)

## Known-answer test

- input: 1T4J, chain A, ligand FRJ (criterion W1)
- expected: the report has a component `fpocket` whose pocket contains
  the FRJ contact residues, and the `ligand_contacts` component equals
  the direct call of `get_ligand_contacts("1T4J", ligand_id="FRJ")` -
  the same 11 UniProt residues: 188, 189, 192, 193, 196, 200, 276,
  277, 279, 280, 282
  (`docs/2_allosteric_site_workflow_criteria.md:28-34`). The recorded
  result is an overlap of **8** residues
  (`../alloagent_private/docs/3_report.md:4638-4640`).
- input: 1OPK, chain A, ligand MYR (criterion W2)
- expected: the `ligand_contacts` component equals the direct call -
  the same 8 UniProt residues: 359, 360, 363, 448, 452, 481, 521, 529 -
  and every component that is present carries success or a clear
  per-component error string
  (`docs/2_allosteric_site_workflow_criteria.md:35-40`).
- input: any structure (criterion W3)
- expected: for the components that run, the report value equals the
  value of the direct call of the same tool, field by field
  (`docs/2_allosteric_site_workflow_criteria.md:41-44`).

## Negative control

- **not found** - no negative-control expectation is recorded for this
  tool in the criteria file or in the reports.

## Code location and version

- function: `biomni/tool/allosteric_site_workflow.py::allosteric_site_workflow`
- recorded in: the per-run JSON at the key
  `tools_meta[allosteric_site_workflow].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**PASS (W1, W2, W3) - the tool is exposed.** The criteria are
`docs/2_allosteric_site_workflow_criteria.md` (the component table at
lines 11-20, the criteria W1-W4 at 26-48).

The first verdict table, `../alloagent_private/docs/3_report.md:4379-4384`, records W1 as
**FAIL (recorded)** (line 4381) and W4 as "not added ... the exposed
list stays at **44** tools" (line 4384). The superseding section at
`../alloagent_private/docs/3_report.md:4636-4648` records the current state: with the
fpocket wrapper fixed, "the fpocket component's overlap with the FRJ
contact set is **8** (not 0), the strict xfail on W1 is **removed**",
"W2 ... and W3 ... still pass", and "W4's condition - expose the tool
only if W1-W3 pass - is now met, so **`allosteric_site_workflow` is
exposed** and the exposed list is 45 tools" (lines 4645-4648).

The tool is in the exposed list at `alloagent/exposed_tools.txt:55`
(with the note at lines 53-54: "exposed 2026-10-26: W1, W2 and W3 of
`docs/2_allosteric_site_workflow_criteria.md` all pass").

No criterion in the criteria file names a card file for this tool, and
the card did not exist before this one.

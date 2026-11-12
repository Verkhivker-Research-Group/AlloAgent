# Part 1a — Tool framework design note

This note locks the layout for Parts 1b–1f and Parts 2 (T1–T7). It
keeps upstream's directory structure and adds the schema-audit,
return-contract, blocklist, exposed-list, and tool-card conventions
required by the brief. Pass criteria for each part are committed
in their own file BEFORE the implementation.

## 1. Upstream conventions we keep

`biomni/tool/` at the pinned commit (`400c1f3`) has the following
layout. **We keep it exactly as-is for the file locations**; new
content goes only into existing files or into `biomni/agent/a1.py`
for the registry wiring.

```
biomni/tool/
  schema_db/                  # one pickle per database (kegg.pkl, uniprot.pkl, …)
  tool_description/
    biochemistry.py            # one Python file per topic
    bioengineering.py
    bioimaging.py
    biophysics.py
    cancer_biology.py
    cell_biology.py
    database.py                # query_uniprot, query_kegg, query_reactome, …
    genetics.py
    genomics.py
    glycoengineering.py
    immunology.py
    lab_automation.py
    literature.py
    microbiology.py
    molecular_biology.py
    pathology.py
    pharmacology.py
    physiology.py
    protocols.py
    support_tools.py
    synthetic_biology.py
    systems_biology.py
  tool_registry.py            # ToolRegistry(name, description, required_parameters)
  <topic>.py                  # the actual function bodies (kept from upstream)
  schemas.py, schema_db/, tool_description/ are the upstream "single source of truth" for tool metadata.
```

The upstream `ToolRegistry` (`biomni/tool/tool_registry.py`) requires
each tool dict to carry `name`, `description`, and
`required_parameters`. Functions are converted to these dicts by the
upstream `biomni.utils.function_to_api_schema` / `read_module2api`
helpers (the existing hand-rolled code). The registry exposes
`get_id_by_name`, `get_tool_by_id`, `list_tools`, `register_tool`,
`remove_tool_by_*`, and `save_registry` / `load_registry` (pickle).

## 2. What Part 1 changes about the registry

- **Part 1b**: schemas are **generated** from each function's
  `inspect.signature` + docstring, NOT hand-typed in
  `tool_description/*.py`. A new `biomni/tool/schema_generator.py`
  produces a `dict` with the same shape
  `ToolRegistry.register_tool` expects
  (`name`, `description`, `required_parameters`, plus `parameters`
  with `type` and `description` per arg). `tool_description/*.py`
  becomes the place where the function LIVES; metadata is NOT
  retyped there.
  - A `tests/test_schema_audit.py` test iterates the registry and
    asserts every tool's schema matches its function signature
    (param names, defaults, types) and that every
    `tool_description/<topic>.py` imports without error. The test
    fails if any mismatch or ImportError is present (the brief
    says version 1 had 5 mismatches + 1 ImportError; that must be
    green from the start).
- **Part 1c**: every tool returns a dict
  `{"success": bool, "data": Any, "error": str | None, "source": str,
  "source_version": str, "query_time_utc": ISO-8601 str}`. The
  never-empty-success rule is enforced by a test that asserts
  `success=True` implies `data is not None` OR `error is not None`.
  Network tools get a shared decorator
  (`@net_call(timeout_s=30, retries=3, backoff_s=0.5, cache=True)`)
  that lives in `biomni/tool/_netcall.py`. The cache key is the
  call's `args` + `kwargs` (JSON-serialized) and lives at
  `~/.cache/alloagent/netcall/<sha256-of-key>.json`.
- **Part 1d**: `@benchmark_blocklist` decorator (in
  `biomni/tool/_blocklist.py`). The decorator reads
  `BENCHMARK_BLOCKLIST_FILE` (defaults to
  `Biolab/prep_reports/benchmark_blocklist.tsv`). When the file
  exists, the wrapped function checks its first positional
  argument against the first column (a TSV of PDB IDs / UniProt
  accessions) and returns
  `{"success": False, "error": "blocked by benchmark blocklist",
  ...}`. When the env var is unset, the decorator is a no-op.
- **Part 1e**: a new file `alloagent/exposed_tools.txt` lists tool
  names D exposes (one per line, `# comment` allowed). The
  per-run recording JSON gets a new top-level key
  `exposed_tools` (list[str], subset of registered) plus
  `tools_meta` (`{name: {version, schema_hash}}`). Tools that need
  an optional binary or dataset (fpocket, P2Rank/Java, prody,
  biotite, vina, meeko) register with availability check; the
  registry logs `"tool X skipped: <reason>"` at A1 init when the
  binary/dataset is missing.
- **Part 1f**: one card per tool at
  `docs/tool_cards/<tool>.md`. The card template (see below) is the
  single source of truth for the tool's contract; the function's
  docstring is generated from the card and vice versa, by a
  pre-commit-style check (or a simple test). Tools must never quote
  a predictor's self-reported accuracy — the audit test asserts the
  card and docstring don't contain the literal substring
  `self-reported`.

## 3. New files (this is the layout I will use)

```
biomni/tool/
  _netcall.py           # Part 1c: timeout, retry, backoff, cache decorator
  _blocklist.py         # Part 1d: @benchmark_blocklist
  schema_generator.py   # Part 1b: signature+docstring -> ToolRegistry dict
alloagent/
  __init__.py
  exposed_tools.txt     # Part 1e: one tool name per line
  tools_meta.json       # Part 1e: optional, generated snapshot
docs/
  tool_framework.md     # this file
  tool_cards/
    T_template.md       # the template (Part 1f) for copy-paste
    T1_map_residues_uniprot_pdb.md
    T2_get_uniprot_variants.md
    T3_get_stingallo_allosteric_residues.md
    T4_detect_pockets_fpocket.md
    T5_detect_pockets_p2rank.md
    T6_normal_mode_analysis.md
    T7_residue_contact_network.md
tests/
  test_schema_audit.py          # Part 1b
  test_return_contract.py       # Part 1c
  test_blocklist.py             # Part 1d
  test_exposed_tools.py         # Part 1e
  test_tool_cards.py            # Part 1f
  test_T1_map_residues_uniprot_pdb.py  # Part 2
  test_T2_get_uniprot_variants.py
  … (one per tool, Part 2)
```

## 4. Tool card template (Part 1f)

```markdown
# T<id> <tool_name>

## What it answers (and does NOT)

- Question the tool answers: …
- What it does NOT answer (e.g. fpocket finds ligand-binding pockets
  and does not distinguish allosteric sites; this sentence is
  mandatory for any pocket / annotation / prediction tool).

## Inputs / outputs

- inputs: (table of parameter name, type, required, description, default)
- output dict shape: {success, data, error, source, source_version, query_time_utc}

## Source and version

- upstream URL: …
- pinned commit / DOI / release tag: …
- license: …

## Runtime

- typical latency: …
- rate limits: …
- offline vs online: …

## Determinism

- deterministic? (yes / no / partial)
- if partial: which inputs cause non-determinism

## Failure modes

- … (list of common failure modes and the error text each produces)

## Known-answer test

- input: …
- expected: …

## Negative control

- input: … (a deliberately-bad input that should produce a clear error)
- expected: {"success": False, "error": "…"}

## Code location and version

- function: <module path>
- recorded in: <per-run JSON path> at <key>
```

The card is the source of truth; the function's docstring is
regenerated from the card by a test in `tests/test_tool_cards.py`.
The card is regenerated when the function changes; the test fails
on drift.

## 5. What this commit does NOT do

- No `tool_description/*.py` is edited in this commit (Part 1b/2).
- No test file is added (each Part-1 sub-item gets its own
  criteria + commit).
- The card template lives at `docs/tool_cards/T_template.md`
  but is filled in only as each Part-2 tool is built.

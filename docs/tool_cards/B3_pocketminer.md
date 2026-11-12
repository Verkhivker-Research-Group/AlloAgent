# B3 pocketminer_score

## Question the tool answers

"Score residues in a PDB structure for cryptic-pocket propensity."

## What it does NOT answer

PocketMiner predicts MD-defined pocket-opening propensity (cryptic
pockets), not allosteric sites specifically
(`biomni/tool/pocketminer.py:229-230`).

The output scores are SCREENING EVIDENCE for potential
cryptic-pocket-forming residues, not a quantitative prediction of
cryptic-pocket geometry or opening probability; the model was trained
on a 37-apo-structure set and evaluated on a subset of the CryptoBench
benchmark. On the independent CryptoBench test split (222 apo
structures) performance is modest: per-protein AUC mean = 0.650
(bootstrap 95% CI [0.622, 0.677]), pooled residue-level AUC = 0.649,
with 78% of proteins scoring above chance. These numbers are
screening-grade, not assay-grade. Do not treat a high score as a
positive identification of a cryptic pocket without orthogonal evidence
(e.g. MD simulation, experimental validation)
(`biomni/tool/pocketminer.py:234-247`).

The tool also does NOT mix the chains of a multi-chain structure into a
single number: the result is reported per chain
(`biomni/tool/pocketminer.py:225-227`).

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `pdb_path` | str | yes | — | Path to the PDB file to score |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data`:

```
{
    "residue_scores": [<float in [0, 1]>, ...],
    "residues": [{chain, residue_number, residue_name, score}, ...],
    "chains": {<chain>: {n_residues, mean, min, max, residue_numbers}, ...},
    "all_residue_mean": <float>,
    "chain_mapping_note": <str>,
    "n_residues": <int>,
    "source": "PocketMiner@<model repo commit>",
    "weights_sha256": <str>,
    "runtime_seconds": <float>
}
```

(the shape is the function's own docstring and return dict,
`biomni/tool/pocketminer.py:213-227` and `:428-441`)

## Source and version

- upstream: PocketMiner, `github.com/Mickdub/gvp`, branch `pocket_pred`
- pinned commit: `187062df3c94127e991669768009141a08fd5d8b`
  (`_POCKETMINER_GIT_COMMIT`, `biomni/tool/pocketminer.py:34`; the
  criteria record the short form `187062df3c94`,
  `docs/2_pocketminer_criteria.md:19` and criterion B3-2 at line 55)
- license: MIT, verified at build time
  (`docs/2_pocketminer_criteria.md:57`, criterion B3-4 at line 57;
  the build-time check is `Dockerfile:368-370`)
- runtime: the `pocketminer_env` conda env (Python 3.11,
  `tensorflow==2.15.0`, `numpy==1.26.4`, `mdtraj==1.11.1`) at
  `/opt/conda/envs/pocketminer_env/bin/python`, with the model cloned
  at `/opt/pocketminer` (`biomni/tool/pocketminer.py:6-7, 28-29`;
  `docs/2_pocketminer_criteria.md:13-16`)
- the build-time patch `tf.keras.optimizers.legacy.Adam` is applied to
  the clone (`docs/2_pocketminer_criteria.md:23-25`;
  `docs/dev_container.md:145-162`)
- the weights checksum is written at image build time to
  `/opt/pocketminer_weights.sha256` (`biomni/tool/pocketminer.py:33`;
  `Dockerfile:394-404`, the `sha256sum ... | tee` step at 399-401) and
  is returned in `data.weights_sha256` (`pocketminer.py:438`)
- the file `docs/build/pocketminer_weights.sha256` that criterion B3-6
  names is **not found** in the repository
  (`docs/2_pocketminer_criteria.md:59`); the weights download URL is
  **not found** as well
- data files: the tool reads **no** local data file - the structure is
  the caller's input. The CryptoBench test split at `data/cryptobench/`
  is the **validation** set of criteria B3-18..B3-24, not an input of
  the tool (`docs/2_pocketminer_criteria.md:43-48, 76`)

## Runtime

- typical latency: ~15-20 s per structure (`../alloagent_private/docs/3_report.md:469`)
- rate limits: none recorded
- offline vs online: offline; the model runs in a subprocess on the CPU
  (`CUDA_VISIBLE_DEVICES = "-1"`, `biomni/tool/pocketminer.py:78`)
- the subprocess is capped at 600 s (`_TIMEOUT_S`,
  `biomni/tool/pocketminer.py:35`, used at 346) and the structure is
  capped at 10,000 protein residues (`_MAX_RESIDUES`,
  `biomni/tool/pocketminer.py:42`)

## Determinism

- deterministic? yes
- the same PDB input gives the same 428 scores in the same order
  (`../alloagent_private/docs/3_report.md:469`)

## Failure modes

- `pdb_path` empty or not a string: `{success: False, error: "pdb_path must be a non-empty string, got ..."}`
  (`biomni/tool/pocketminer.py:262-266`)
- the file does not exist: `{success: False, error: "PDB file not found: <path>"}`
  (`:267-272`)
- the `pocketminer_env` is not built: `{success: False, error: "pocketminer_env not built (... not found); rebuild the Docker image with the layered Dockerfile"}`
  (`:273-279`)
- the structure exceeds the model's residue capacity: `{success: False, error: "Structure too large: N protein residues exceeds PocketMiner model capacity (10000 residues). ..."}`
  (`:322-332`)
- the subprocess exceeds the timeout: `{success: False, error: "PocketMiner timed out after 600s"}`
  (`:349-353`)
- the subprocess exits non-zero, or the output file is missing or
  empty: `{success: False, error: "..."}` (`:354-357`); the docstring
  lists the four failure families at `:249-260`

## Known-answer test

- input: the 1AKE PDB (`tests/fixtures/1ake.pdb`)
- expected: 428 per-residue scores in [0, 1], range 0.02-0.98; the
  first 5 values are 0.5353, 0.7912, 0.7100, 0.8246, 0.8816 and match
  the Phase 2c reproduction to atol=1e-3 (`../alloagent_private/docs/3_report.md:469`)

## Negative control

- input: a PDB path that does not exist
- expected: `{success: False, error: "PDB file not found: ..."}`
  (`../alloagent_private/docs/3_report.md:469`; the code path is
  `biomni/tool/pocketminer.py:267-272`)

## Code location and version

- function: `biomni/tool/pocketminer.py::pocketminer_score`
- recorded in: the per-run JSON at the key
  `tools_meta[pocketminer_score].schema_hash`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy. The
  `tests/test_tool_cards.py` audit test asserts that no card or
  docstring contains the substring that begins with s-e-l-f minus r-e-p-o-r-t-e-d (i.e. the forbidden rule-name).
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Status

**PASS** - criteria `docs/2_pocketminer_criteria.md` (B3-1 .. B3-17,
and the validation criteria B3-18 .. B3-24).

Criterion **B3-13** (`docs/2_pocketminer_criteria.md:66`) is the one
that names a card for this tool: "The PocketMiner tool card and
AE-PocketMiner tool card do not contain the forbidden
`s-e-l-f minus r-e-p-o-r-t-e-d` substring". The card did not exist
before this one, although
`../alloagent_private/docs/3_report.md:2301` refers to `docs/tool_cards/B3_pocketminer.md`
as if it did; the criteria file's own verdict table is still unfilled
(lines 88-90 read "(filled)").

The per-tool verdict is recorded in `../alloagent_private/docs/3_report.md:469`:
"**PASS** (14/16 tests; 2 skipped on the missing-env path)", with the
known answer "1AKE -> 428 per-residue scores in [0, 1], range
0.02-0.98", the negative control "missing PDB file returns
`success=False`" and the determinism "same PDB input gives the same
428 scores in the same order".

The CryptoBench validation: **B3-21 PASS** ("pooled AUC 0.6490 > 0.5,
p < 0.05", `../alloagent_private/docs/3_report.md:1872` and `:2047`; the earlier 0.6492
figure at `:1704` is the n=191 run), and **B3-23 not determined** -
the training-set overlap with the CryptoBench test structures cannot
be established because the training set is not publicly listed
(`../alloagent_private/docs/3_report.md:1718`, `:1881`, `:2072`). The report also corrects
an earlier pooled-AUC figure at `../alloagent_private/docs/3_report.md:2748-2757`.

The "AE" variant `ae_pocketminer_score` (`biomni/tool/ae_pocketminer.py`)
stays **PARTIAL** (`../alloagent_private/docs/3_report.md:469`); it is registered but not
exposed and has no card (`docs/new_tools_and_data.md:109`).

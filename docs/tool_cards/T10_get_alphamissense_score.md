# T10 get_alphamissense_score

## Question the tool answers

"What is the AlphaMissense pathogenicity score and class for
missense variants in a given UniProt accession (optionally at a
specific protein position)?"

## What it does NOT answer

- It does not return scores for non-missense variants (synonymous,
  nonsense, frameshift, splice-site, indels). AlphaMissense
  covers all ~216M possible single amino-acid substitutions
  across the human proteome, one per row.
- It does not return scores keyed by gene symbol. The TSV is
  indexed by UniProt accession. Use T1 `map_residues_uniprot_pdb`
  or the UniProt API to map a gene symbol to a UniProt accession
  first.
- It does not return structural context (e.g., whether the
  residue is in a binding pocket or on the surface). Use T7
  `residue_contact_network` for that.
- It does not compare to other pathogenicity predictors
  (SIFT, PolyPhen, REVEL). The wrapper returns only the
  AlphaMissense score and class.
- It does not claim clinical validity. The AlphaMissense
  `am_class` is a model prediction, not a ClinVar curation.
  Use T9 `get_clinvar_variants` for ClinVar-curated clinical
  significance.

## Inputs

| name | type | required | default | description |
|---|---|---|---|---|
| `uniprot_id` | `str` | yes | — | UniProt accession (e.g. `"P69905"`, `"P69441"`). Case-sensitive. |
| `position` | `int` or `None` | no | `None` | 1-indexed protein position. `None` (default) returns all missense variants for the protein. |
| `data_path` | `str` or `Path` or `None` | no | `/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz` | Path to the local AlphaMissense TSV. Must be downloaded via `scripts/fetch_alphamissense.py --download --out <dir>`. |

## Outputs

`dict` with the 6 required keys from `biomni/tool/_netcall.py`:
`{success, data, error, source, source_version, query_time_utc}`.

`data` is:

```python
{
    "uniprot_id": "A0A024R1R8",
    "position": None,  # or int if filtered
    "variants": [
        {
            "uniprot_id": "A0A024R1R8",
            "protein_variant": "M1A",
            "am_pathogenicity": 0.4673,
            "am_class": "ambiguous",
            "position": 1,
            "ref_aa": "M",
            "alt_aa": "A",
        },
        ...
    ],
    "total_count": 21,  # rows returned (not total in TSV)
    "data_path": "/data/alphamissense/AlphaMissense_aa_substitutions.tsv.gz",
}
```

## Source and version

- upstream URL: `https://storage.googleapis.com/dm_alphamissense/AlphaMissense_aa_substitutions.tsv.gz`
- paper: Cheng et al. 2023, "Accurate proteome-wide missense
  variant effects with AlphaMissense", Nature 622, 735-745.
- DOI: `10.1038/s41586-023-06488-3`
- license: CC BY-NC-SA 4.0
- data version: 2023-09 (DeepMind's initial release)

## Runtime

- typical latency: ~3-8 s for a single UniProt accession (the
  wrapper streams the full ~5 GB uncompressed TSV; the first call
  on a cold file cache is slower). Sub-second for a position
  filter (still streams the full file, but returns fewer rows).
- rate limits: none (local file)
- offline vs online: offline once the TSV is downloaded

## Determinism

- deterministic? yes (the TSV is immutable; gzip + csv streaming
  is deterministic)
- if partial: none

## Failure modes

- TSV file missing: `{"success": false, "error": "AlphaMissense TSV not found at <path>; run scripts/fetch_alphamissense.py --download --out <dir>"}`
- TSV file present but malformed: `{"success": false, "error": "AlphaMissense TSV at <path> is malformed: <details>"}`
- `uniprot_id=""` or `None`: `{"success": false, "error": "uniprot_id must be a non-empty string, got <repr>"}`
- `position <= 0`: `{"success": false, "error": "position must be a positive int (1-indexed), got <value>"}`
- Unknown UniProt: `{"success": true, "data": {"variants": [], "total_count": 0, ...}}`

## Known-answer test

- input: `("A0A024R1R8",)` (no position filter)
- expected: `data.variants[0].protein_variant == "M1A"`,
  `data.variants[0].am_pathogenicity == 0.4673`,
  `data.variants[0].am_class == "ambiguous"`,
  `data.variants[0].position == 1`,
  `data.variants[0].ref_aa == "M"`,
  `data.variants[0].alt_aa == "A"`.

- input: `("A0A024R1R8", 1)` (position 1 only)
- expected: `len(data.variants) == 19` (all 19 possible
  missense substitutions at position 1, excluding M1M which is
  synonymous); the first two records are `M1A`, `M1C` (sorted by
  position then alt_aa).

## Negative control

- input: `("ZZZZZZ",)` (unknown UniProt)
- expected: `{"success": true, "data": {"variants": [], "total_count": 0, ...}}`

## Code location and version

- function: `biomni/tool/get_alphamissense_score.py::get_alphamissense_score`
- recorded in: the per-run JSON at the key `image_id`
- version: `biomni.__version__`

---

## Cross-cutting rules (every card must respect)

- Tools must never quote a predictor's advertised accuracy.
- The function's docstring mirrors the card's "Question the tool
  answers" sentence.

## Data source note

The AlphaMissense TSV is 1151.4 MB compressed (~5 GB uncompressed,
~20M rows). It is downloaded once via
`scripts/fetch_alphamissense.py --download --out <dir>`. The
wrapper does NOT download it on demand; the user must run the
fetch script first. If the file is missing, the wrapper returns
`success=False` with a clear error pointing to the fetch script
(graceful degradation).

# The ASD (Allosteric Database): what the tools read and where the data comes from

Dated note 2026-11-05.  Every claim below names the file and the line it
comes from; where the repository does not record something, it says
**not found**.

## 1. The files and the releases the tools read

The ASD constants are in `biomni/tool/asd.py`:

| line | the file or directory | the release | the tool that reads it | required or optional |
|---|---|---|---|---|
| `asd.py:38` | `ASD_Release_202306_XF/` (the XF functional XML files) | **202306** | `parse_asd_xf` (`biomni/tool/allosteric.py`, the card `docs/tool_cards/P13_parse_asd_xf.md`: 2,419 files over 2,412 proteins) | **required** - `asd.py:186-191` returns `success: False` with "ASD XF directory not found at {xf_dir}; mount the Biolab data lake read-only or set ASD_ROOT" when the directory is missing |
| `asd.py:39` | `ASD_Release_202306_2D/` (the `.mol` files) | **202306** | `load_asd_2d` (the card `docs/tool_cards/P14_load_asd_2d.md`: 99,961 files) | optional - a missing file gives `None` (`asd.py:99`, `asd.py:225`) |
| `asd.py:40` | `ASD_Release_202306_3D/` (the `.mol2` files) | **202306** | `load_asd_3d` (the card `docs/tool_cards/P15_load_asd_3d.md`: 99,959 files) | optional - a missing file gives `None` (`asd.py:249`) |
| `asd.py:41` | `ASD_Release_202306_AP.csv` (the allosteric pairs) | **202306** | `cross_reference_ligands` (the card `docs/tool_cards/P16_cross_reference_ligands.md`) | optional - `_load_csv` returns `None` when the file is absent (`asd.py:416`) |
| `asd.py:42` | `ASD_Release_201909_DR.csv` (the distance/relationship table) | **201909** | `cross_reference_ligands` (the card `docs/tool_cards/P16_cross_reference_ligands.md`) | optional - `_load_csv` returns `None` (`asd.py:416`) |
| the card `docs/tool_cards/P21_allosteric_hotspot_detection.md` | `ASD_Release_202309_AS.csv` (3,102 rows) | **202309** | `allosteric_hotspot_detection` | optional - the tool reports no hotspot when the file is absent |

**The 202208 release**: `ASD_Release_202208_AS_Filtered.json` is listed in
`Biolab/DATA.md` line 48 as a file the user places in the data lake, but
**no tool in this repository reads it**: the ASD tool reads the 202306
releases, the 201909 DR table and the 202309 AS table.  The 202208 file
was the subject of a separate investigation of a 403
(`Biolab/prep_reports/investigation/item6_asd_403.md`, which states at
line 46 that the file is missing from the data lake and from the `asd/`
directory).

**If only the latest release is present** (the 202306 XF/2D/3D
directories, and none of the CSVs): the XF, 2D and 3D tools work; the
AP and DR cross-references and the hotspot detection return nothing,
because the CSVs are optional and the code returns `None`
(`asd.py:416`) instead of failing.  If the XF directory itself is
missing, every ASD lookup fails with the explicit error of `asd.py:186-191`.

## 2. The folder the tools expect, and the setting that points at it

| what | where | the line |
|---|---|---|
| the default ASD root in the container | `/biolab_data/asd` | `biomni/tool/asd.py:34` (`_DEFAULT_ASD_ROOT`), described at lines 19-20 |
| the environment variable that overrides it | `ASD_ROOT` | `biomni/tool/asd.py:49` (`_asd_root()`) |
| the environment variable that overrides the lake root | `ASD_LAKE_ROOT` | `biomni/tool/asd.py:53` (`_lake_root()`); the default lake is `/biolab_data` |
| the host folder the data is read from | `<HOME>\Documents\CPSC\Biolab\data\biomni_data\asd` | `scripts/_gen_asd_index.py:17` (`XF`) |
| the container mount | `/biolab_data` (read-only) | `biomni/tool/asd.py:19-20`; the tools' cards say the same ("mounted read-only at `/biolab_data`") |

## 3. The local index: what builds it and how to run it

* The index is the committed file **`biomni/tool/_asd_index.tsv`** (the
  path is `biomni/tool/asd.py:36`, `_INDEX_TSV`; it maps a UniProt
  accession to the ASD XF file stem).
* The builder is **`scripts/_gen_asd_index.py`**.  It reads the real
  `ASD_Release_202306_XF` directory (line 17), scans the `<UniProt_ID>`
  of every XML file (line 20, the pattern) and writes the TSV (line 18,
  `OUT`).
* **How to run it**: `python scripts/_gen_asd_index.py` (a plain script
  with no arguments; it prints "wrote {OUT} (N proteins, N bytes) from N
  XML files"; an extra argument prints a sample).
* **At run time** the index is rebuilt from the directory when the TSV is
  missing (`biomni/tool/asd.py:17`: "the index is rebuilt by scanning the
  directory"; the scan is `asd.py:82`).

## 4. Is any ASD file baked in, uploaded, or in the dataset?

| question | answer | the evidence |
|---|---|---|
| baked into the image `alloagent-eval:v6`? | **no** | the `Dockerfile` of this repository has **no** `ASD`, `asd` or `biolab_data` line (a search of `Dockerfile` for `asd\|biolab_data\|ASD` returns nothing); the data is mounted at run time (`biomni/tool/asd.py:19-20`) |
| in a folder that would be uploaded (the HF dataset / the data bundle)? | **no** | the bundle excludes the ASD: `Biolab/scripts/build_data_bundle.py` line 43, `"asd",  # user fetches ASD separately (per-request licensing)`, and the exclusion globs at lines 51-53 (`**/ASD_Release_*.csv`, `*.json`, `*.zip`); `Biolab/DATA.md` line 39: "The bundle **does not** include the Allosteric Database (ASD) files because their upstream license requires per-request registration" |
| the paths that would hold it | the host: `data/biomni_data/asd/ASD_Release_202306_{XF,2D,3D}.zip`, `.../ASD_Release_202208_AS_Filtered.json`, and the extracted `ASD_Release_202306_{XF,2D,3D}/` directories (`Biolab/DATA.md` lines 45-51); the container: `/biolab_data/asd/...` (`biomni/tool/asd.py:34`) |

## 5. Is there an ASD download script?

**No.**  `Biolab/scripts/download_data.py` does not mention the ASD (a
search for `asd`, `ASD`, `rate`, `sleep`, `delay`, `licen`, `register`
returns nothing), and no other script in either repository downloads
the ASD.  The instructions are for the user:

1. visit `https://mdl.shsmu.edu.cn/ASD` and request an academic download
   of the v202306 release (2D, 3D, XF) - `Biolab/DATA.md` line 55;
2. place the three `.zip` files and `ASD_Release_202208_AS_Filtered.json`
   at the paths of `DATA.md` lines 45-51 - line 56;
3. unzip the three archives in place - line 57.

**The terms are shown to the user**, in two places: `Biolab/DATA.md`
line 39 (the per-request registration) and the third-party licence file
that the bundle writes (`Biolab/scripts/build_data_bundle.py` line 149-
152: "ASD - Allosteric Database (excluded from bundle) ... License:
Academic use, registration required").

**The rate limit is not the ASD's.**  The repository's rate-limit
counter is on the **STINGAllo** service
(`biomni/tool/get_stingallo_allosteric_residues.py`, the card
`docs/tool_cards/T3_get_stingallo_allosteric_residues.md`: 30 PDB
entries per day, 5 per minute).  Nothing in the repository rate-limits an
ASD download, because nothing in the repository downloads the ASD.

What the repository does record about the ASD's download side is the
shape of the download page: it is a server-rendered page whose file
URLs live behind the download module and that offers the releases as
`.tar.gz` archives
(`Biolab/prep_reports/phase2/b8_asd.md`, lines 5-7 and 53-54).

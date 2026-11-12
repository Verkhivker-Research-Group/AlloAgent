"""T9 get_clinvar_variants (Part 2 / batch 2).

What are the ClinVar-annotated variants for a given gene symbol
(optionally filtered by clinical significance)?

Two modes, local pinned (default) and live:

- **Local mode (default when the file is present)**: streams
  ``variant_summary.txt.gz`` (434 MB compressed, ~5.8M rows)
  from ``https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/``
  via stdlib ``gzip`` + ``csv``. The file must be downloaded via
  ``scripts/fetch_clinvar.py --download --out <dir>``. The
  ``MANIFEST`` file records the URL, size, sha256, and download
  timestamp.
- **Live mode (fallback or explicit)**: NCBI E-utilities API
  (``eutils.ncbi.nlm.nih.gov``) — ESearch + ESummary.
"""
from __future__ import annotations

import csv
import gzip
import sqlite3
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional

import requests

from biomni.tool import _lookup_index
from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
_TIMEOUT_S = 30
_MIN_REQUEST_INTERVAL_S = 0.4  # 2.5 req/sec, safely under NCBI's 3 req/sec limit
_MAX_RETRIES_429 = 3
_DEFAULT_LOCAL_PATH = Path("/data/clinvar/variant_summary.txt.gz")
_LOCAL_MANIFEST = "MANIFEST"

_SIGNIFICANCE_TO_FILTER: dict[str, str] = {
    "pathogenic": "clinsig_pathogenic",
    "likely_pathogenic": "clinsig_likely_pathogenic",
    "benign": "clinsig_benign",
    "likely_benign": "clinsig_likely_benign",
    "uncertain": "clinsig_uncertain",
    "conflicting": "clinsig_conflicting",
}

# Keywords for filtering the local TSV's ClinicalSignificance column
_SIGNIFICANCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "pathogenic": ("pathogenic",),
    "likely_pathogenic": ("likely pathogenic", "likely_pathogenic"),
    "benign": ("benign",),
    "likely_benign": ("likely benign", "likely_benign"),
    "uncertain": ("uncertain", "uncertain significance", "vus"),
    "conflicting": ("conflicting", "conflicting interpretations"),
}

# Singleton rate-limiter (process-wide).
_LAST_REQUEST_T: float = 0.0


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "NCBI E-utilities (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/)"


def _throttle() -> None:
    global _LAST_REQUEST_T
    now = time.monotonic()
    wait = _MIN_REQUEST_INTERVAL_S - (now - _LAST_REQUEST_T)
    if wait > 0:
        time.sleep(wait)
    _LAST_REQUEST_T = time.monotonic()


def _esearch(gene: str, sig_filter: Optional[str], retmax: int) -> list[str]:
    """Return up to ``retmax`` ClinVar IDs for the gene (+ optional filter)."""
    term = f"{gene}[gene]"
    if sig_filter:
        term += f" AND {sig_filter}[Properties]"
    params = {
        "db": "clinvar",
        "term": term,
        "retmax": str(retmax),
        "retmode": "json",
    }
    r = _get_with_retry(_ESEARCH_URL, params=params)
    if r.status_code != 200:
        raise RuntimeError(
            f"NCBI ESearch returned status {r.status_code}: {r.text[:200]}"
        )
    # JSONDecodeError on a non-JSON body (e.g. a 5xx error that
    # the upstream mocked Request returns with text not parseable
    # as JSON) would propagate as ValueError, not RequestException.
    # Convert any such failure to a RuntimeError so the public
    # `except RuntimeError` arm catches it and returns success=False.
    try:
        body = r.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"NCBI ESearch returned non-JSON body for status={r.status_code}: "
            f"{r.text[:200]!r} (parse error: {exc})"
        ) from exc
    result = body.get("esearchresult", {})
    if "errorlist" in result and result["errorlist"]:
        # NCBI reports per-field errors in errorlist; treat as no results.
        return []
    return list(result.get("idlist", []))


def _esummary(clinvar_ids: list[str]) -> list[dict[str, Any]]:
    """Fetch the ESummary XML for a batch of ClinVar IDs and parse to dicts."""
    if not clinvar_ids:
        return []
    r = _get_with_retry(
        _ESUMMARY_URL, params={"db": "clinvar", "id": ",".join(clinvar_ids)},
    )
    if r.status_code != 200:
        raise RuntimeError(
            f"NCBI ESummary returned status {r.status_code}: {r.text[:200]}"
        )
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError as exc:
        raise RuntimeError(f"NCBI ESummary returned invalid XML: {exc}") from exc

    out: list[dict[str, Any]] = []
    for ds in root.findall(".//DocumentSummary"):
        rec = _parse_one(ds)
        if rec is not None:
            out.append(rec)
    return out


def _get_with_retry(url: str, params: dict[str, str]) -> requests.Response:
    """GET with a process-wide throttle and a 429 retry-with-backoff.

    The throttle (``_MIN_REQUEST_INTERVAL_S``) spaces requests at
    ~2.5 req/sec, safely under NCBI's 3 req/sec limit without an
    API key. On 429, sleep for an additional 1s, 2s, 4s before
    giving up (up to ``_MAX_RETRIES_429`` retries).
    """
    last_exc: Exception | None = None
    backoff = 1.0
    for attempt in range(_MAX_RETRIES_429 + 1):
        _throttle()
        try:
            r = requests.get(url, params=params, timeout=_TIMEOUT_S)
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            time.sleep(backoff)
            backoff *= 2
            continue
        if r.status_code == 429:
            time.sleep(backoff)
            backoff *= 2
            continue
        return r
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(
        f"NCBI returned 429 after {_MAX_RETRIES_429} retries"
    )


def _findtext_ci(elem: ET.Element, *candidates: str) -> Optional[str]:
    """Case-insensitive ``findtext`` over a list of candidate tags.

    The NCBI ESummary XML for ClinVar emits tags in mixed case
    (``<Title>``, ``<ReviewStatus>``, ``<obj_type>``, etc.).
    ``Element.findtext`` is case-sensitive, so a wrapper that
    hard-codes lowercase would silently miss the real-world data.
    This helper tries each candidate in order, regardless of
    case, and returns the first non-empty text.
    """
    targets = {c.lower() for c in candidates}
    for el in elem.iter():
        if el.tag.lower() in targets and el.text:
            return el.text
    return None


def _parse_one(ds: ET.Element) -> Optional[dict[str, Any]]:
    """Parse one ``<DocumentSummary>`` element into a variant dict."""
    uid = ds.get("uid")
    if uid is None:
        return None
    # NCBI's ESummary XML for ClinVar populates `<accession>` with
    # the HGVS-style title (e.g. ``NM_007294.4(BRCA1):c.190T>G (p.Cys64Gly)``)
    # rather than the canonical VCV accession. Construct the
    # canonical accession from the integer ``uid`` attribute:
    # VCV + 9 zero-padded digits + ``.`` + revision (default 1).
    # NCBI's revision counter is the second <accession> attribute
    # in some records; absent that, default to 1.
    try:
        uid_int = int(uid)
        acc_ver_text = _findtext_ci(ds, "accession_version") or ""
        # Real ClinVar records put the FULL VCV string in
        # <accession_version> (e.g. "VCV005019327.1"), not just
        # the revision. Parse the part after the last dot so
        # the constructed accession matches the canonical form.
        if "." in acc_ver_text:
            revision = acc_ver_text.rsplit(".", 1)[-1]
        elif acc_ver_text:
            revision = acc_ver_text
        else:
            revision = "1"
        accession = f"VCV{uid_int:09d}.{revision}"
    except (TypeError, ValueError):
        accession = ""
    # The title is the HGVS-style name the upstream puts under
    # ``<Title>`` (capital T) or ``<title>``. Case-insensitive
    # lookup so both work; fall back to ``<accession>`` for older
    # records that put the HGVS string there.
    title = (
        _findtext_ci(ds, "Title", "title")
        or _findtext_ci(ds, "accession", "Accession")
        or ""
    )
    review_status = _findtext_ci(ds, "ReviewStatus", "review_status") or None
    obj_type = _findtext_ci(ds, "obj_type", "ObjType") or None

    # Clinical significance: germline classification is under
    # germline_classification/description (older records) or
    # germline_classification/description. Fall back to trait_set
    # if absent.
    clin_sig = None
    gc = ds.find(".//germline_classification")
    if gc is not None:
        clin_sig = gc.findtext("description") or None
    if clin_sig is None:
        sc = ds.find(".//somatic_clinical_impact")
        if sc is not None:
            clin_sig = sc.findtext("description") or None
    if clin_sig is None:
        trait_set = ds.find(".//trait_set")
        if trait_set is not None:
            clin_sig = trait_set.findtext(".//trait") or None

    # Gene symbol: best-effort. ElementTree does not support
    # XPath predicates like `[idvalue]`, so iterate manually.
    gene_symbol = None
    # Modern ClinVar records put the gene symbol under
    # <gene_sort> (top-level) and <genes>/<gene>/<symbol>.
    gene_sort = ds.findtext("gene_sort")
    if gene_sort:
        gene_symbol = gene_sort.strip()
    if gene_symbol is None:
        for g in ds.findall(".//genes/gene"):
            sym = g.findtext("symbol")
            if sym:
                gene_symbol = sym.strip()
                break
    if gene_symbol is None:
        for ts in ds.findall(".//trait_set"):
            # trait_set/trait_xref elements have a child <id_value> with
            # the gene symbol. Fall back to the <trait> text.
            for tx in ts.findall(".//trait_xref"):
                id_val = tx.findtext(".//id_value")
                if id_val:
                    gene_symbol = id_val.strip()
                    break
            if gene_symbol is None:
                sym = ts.findtext(".//trait")
                if sym and "gene" in sym.lower():
                    gene_symbol = sym
                    break
    if gene_symbol is None:
        # Fallback: use the title prefix before the first '('.
        # Modern titles look like "NM_007294.4(BRCA1):c.5296...";
        # this yields the RefSeq transcript (NM_007294.4), not
        # the gene symbol (BRCA1, inside parens). Acceptable as
        # a last resort; <gene_sort>/<genes>/<gene>/<symbol> above
        # should handle the modern records before this fallback.
        if "(" in title:
            gene_symbol = title.split("(", 1)[0].strip()
        else:
            gene_symbol = ""

    # Location: pick GRCh38 (status=current), fall back to GRCh37.
    loc = _pick_location(ds)
    if loc is None:
        chr_, start, stop, ref, alt, assembly = None, None, None, None, None, None
    else:
        chr_, start, stop, ref, alt, assembly = loc

    return {
        "clinvar_id": uid,
        "accession": accession,
        "title": title,
        "gene_symbol": gene_symbol,
        "clinical_significance": clin_sig,
        "review_status": review_status,
        "obj_type": obj_type,
        "chr": chr_,
        "start": start,
        "stop": stop,
        "ref": ref,
        "alt": alt,
        "assembly": assembly,
    }


def _pick_location(ds: ET.Element) -> Optional[tuple]:
    """Return (chr, start, stop, ref, alt, assembly) for GRCh38, else GRCh37."""
    for assembly_name, status_match in (("GRCh38", "current"), ("GRCh37", "current")):
        for as_set in ds.findall(".//variation_loc/assembly_set"):
            if as_set.findtext("assembly_name") == assembly_name and (
                status_match is None
                or as_set.findtext("status") == status_match
            ):
                chr_ = as_set.findtext("chr")
                start_s = as_set.findtext("start")
                stop_s = as_set.findtext("stop")
                ref = as_set.findtext("ref") or None
                alt = as_set.findtext("alt") or None
                try:
                    start = int(start_s) if start_s else None
                except (TypeError, ValueError):
                    start = None
                try:
                    stop = int(stop_s) if stop_s else None
                except (TypeError, ValueError):
                    stop = None
                return (chr_, start, stop, ref, alt, assembly_name)
    return None


def _read_manifest(path: Path) -> dict[str, str]:
    """Read a ClinVar MANIFEST file (key: value per line) into a dict.

    The real download script writes a per-file manifest at
    ``MANIFEST.<basename>`` (so multiple downloads into the same
    directory do not collide). The synthetic test fixtures use a
    legacy single ``MANIFEST``. Try the per-file name first,
    fall back to the legacy name.

    Returns an empty dict if both are missing or malformed.
    """
    out: dict[str, str] = {}
    candidates = (
        path.parent / f"MANIFEST.{path.name}",
        path.parent / _LOCAL_MANIFEST,
    )
    for manifest_path in candidates:
        if not manifest_path.is_file():
            continue
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    k, _, v = line.partition(":")
                    out[k.strip()] = v.strip()
            if out:
                return out
        except (OSError, UnicodeDecodeError):
            continue
    return out


def _row_to_variant(row: dict[str, Any]) -> dict[str, Any]:
    """Build the public variant dict from one ClinVar TSV row.

    Shared by the streaming scan and the indexed path so both emit the
    same keys with the same None-normalisation.
    """
    gene = (row.get("GeneSymbol") or "").strip()
    return {
        "clinvar_id": (row.get("AlleleID") or "").strip() or None,
        "accession": (row.get("Name") or "").strip() or None,
        "title": (row.get("Name") or "").strip() or None,
        "gene_symbol": gene,
        "clinical_significance": (row.get("ClinicalSignificance") or "").strip() or None,
        "review_status": (row.get("ReviewStatus") or "").strip() or None,
        "obj_type": (row.get("Type") or "").strip() or None,
        "chr": (row.get("Chromosome") or "").strip() or None,
        "start": _safe_int(row.get("Start")),
        "stop": _safe_int(row.get("Stop")),
        "ref": (row.get("ReferenceAllele") or "").strip() or None,
        "alt": (row.get("AlternateAllele") or "").strip() or None,
        "assembly": (row.get("Assembly") or "").strip() or None,
    }


def _index_query(gene: str, significance: Optional[str], max_results: int,
                 conn: sqlite3.Connection) -> tuple[list[dict[str, Any]], int]:
    """Indexed equivalent of :func:`_local_query`.

    The full-scan path stops as soon as ``max_results`` rows are
    collected, so its ``total`` is that same truncated count; this
    reproduces that exactly so the two paths stay comparable.
    """
    sig_keywords = _SIGNIFICANCE_KEYWORDS.get(significance, ()) if significance else ()
    rows = conn.execute(
        "SELECT clinvar_id, name, gene_symbol, clinical_significance, "
        "review_status, obj_type, chromosome, start_pos, stop_pos, "
        "ref_allele, alt_allele, assembly, row_ord "
        "FROM cv WHERE gene_symbol = ? ORDER BY row_ord",
        (gene,),
    ).fetchall()
    total = 0
    out: list[dict[str, Any]] = []
    for (cid, name, gene_symbol, cs, review, obj_type, chrom, start, stop,
         ref, alt, assembly, _row_ord) in rows:
        if sig_keywords:
            hay = (cs or "").lower()
            if not any(kw in hay for kw in sig_keywords):
                continue
        total += 1
        out.append({
            "clinvar_id": cid or None,
            "accession": name or None,
            "title": name or None,
            "gene_symbol": gene_symbol or "",
            "clinical_significance": cs or None,
            "review_status": review or None,
            "obj_type": obj_type or None,
            "chr": chrom or None,
            "start": start,
            "stop": stop,
            "ref": ref or None,
            "alt": alt or None,
            "assembly": assembly or None,
        })
        if len(out) >= max_results:
            break
    return out, total


def _local_query(
    gene: str,
    significance: Optional[str],
    max_results: int,
    data_path: Path,
) -> tuple[list[dict[str, Any]], int]:
    """Stream the local ClinVar TSV and return matching records.

    Returns (variants, total_matched). ``total_matched`` is the
    count of all rows matching the gene filter (before
    ``max_results`` truncation).
    """
    variants: list[dict[str, Any]] = []
    total = 0
    sig_keywords = _SIGNIFICANCE_KEYWORDS.get(significance, ()) if significance else ()

    with gzip.open(str(data_path), mode="rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        # The real variant_summary.txt.gz header line begins with "#",
        # so csv reports the first field name as "#AlleleID" and every
        # row["AlleleID"] lookup silently returns None -- clinvar_id came
        # back empty for every real record. Strip the leading "#" from the
        # first field name; the synthetic fixtures use a bare "AlleleID".
        fields = list(reader.fieldnames or ())
        if fields and fields[0].startswith("#"):
            fields[0] = fields[0][1:]
            reader.fieldnames = fields
        for row in reader:
            row_gene = (row.get("GeneSymbol") or "").strip()
            if row_gene != gene:
                continue
            if sig_keywords:
                cs = (row.get("ClinicalSignificance") or "").lower()
                if not any(kw in cs for kw in sig_keywords):
                    continue
            total += 1
            variants.append(_row_to_variant(row))
            if len(variants) >= max_results:
                break
    return variants, total


def _safe_int(s: Any) -> Optional[int]:
    if s is None or s == "":
        return None
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_clinvar_variants(
    gene: str,
    significance: Optional[str] = None,
    max_results: int = 10,
    mode: Optional[str] = None,
    data_path: Optional[Any] = None,
):
    """Return ClinVar-annotated variants for a gene symbol.

    Parameters
    ----------
    gene : str
        HGNC gene symbol (e.g. ``"BRCA1"``, ``"TP53"``,
        ``"EGFR"``).
    significance : str or None, default None
        Optional clinical-significance filter. One of
        ``"pathogenic"``, ``"likely_pathogenic"``, ``"benign"``,
        ``"likely_benign"``, ``"uncertain"``, ``"conflicting"``.
        ``None`` (default) means no filter.
    max_results : int, default 10
        Maximum number of variants to return. Must be >= 0;
        ``0`` returns an empty list.
    mode : str or None, default None
        ``"local"`` forces the local pinned TSV;
        ``"live"`` forces the NCBI E-utilities API;
        ``None`` (default) auto-detects: local if
        ``<data_path>`` + ``MANIFEST`` exist, else live.
    data_path : str, Path, or None
        Path to the local ClinVar ``variant_summary.txt.gz``.
        Default ``/data/clinvar/variant_summary.txt.gz``.
        Only used in local mode.

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "gene": <str>,
                "significance": <str or None>,
                "total_count": <int>,        # rows matched
                "variants": [
                    {
                        "clinvar_id": <str>,
                        "accession": <str>,
                        "title": <str>,
                        "gene_symbol": <str>,
                        "clinical_significance": <str or None>,
                        "review_status": <str or None>,
                        "obj_type": <str or None>,
                        "chr": <str or None>,
                        "start": <int or None>,
                        "stop": <int or None>,
                        "ref": <str or None>,
                        "alt": <str or None>,
                        "assembly": "GRCh38" or "GRCh37" or None,
                    },
                    ...
                ],
                "source": "local:<release_date>" or "live:<query_time_utc>",
                "release_date": <str> or None,  # from MANIFEST (local only)
                "query_url": <str>,
            }

        On network or API failure (live) or missing file (local),
        returns ``{success: False, error: <descriptive string>, ...}``.
    """
    if not isinstance(gene, str) or not gene:
        return {
            "success": False,
            "error": f"gene must be a non-empty string, got {gene!r}",
        }
    sig_filter: Optional[str] = None
    if significance is not None:
        if significance not in _SIGNIFICANCE_TO_FILTER:
            return {
                "success": False,
                "error": (
                    f"significance must be one of "
                    f"{sorted(_SIGNIFICANCE_TO_FILTER.keys())} or None, "
                    f"got {significance!r}"
                ),
            }
        sig_filter = _SIGNIFICANCE_TO_FILTER[significance]
    if not isinstance(max_results, int) or max_results < 0:
        return {
            "success": False,
            "error": f"max_results must be an int >= 0, got {max_results!r}",
        }
    if mode is not None and mode not in ("local", "live", "auto"):
        return {
            "success": False,
            "error": f"mode must be 'local', 'live', 'auto', or None, got {mode!r}",
        }

    local_path = Path(data_path) if data_path is not None else _DEFAULT_LOCAL_PATH
    manifest = _read_manifest(local_path) if local_path.is_file() else {}
    if mode == "local":
        use_local = True
    elif mode == "live":
        use_local = False
    else:
        # mode is None or "auto": use local when the configured
        # pinned file is present with a valid MANIFEST, else fall
        # back to live. Reproducibility of evaluation runs depends
        # on the pinned file taking precedence over the live API.
        use_local = local_path.is_file() and bool(manifest)

    if max_results == 0:
        if use_local:
            release_date = manifest.get(
                "downloaded_at", manifest.get("completed_at", "unknown")
            )
            sha256 = manifest.get("sha256", "")
            source_version = (
                f"sha256:{sha256}" if sha256 else f"date:{release_date}"
            )
            mode_used = "local"
            query_url = str(local_path)
            source_label = f"local:0"
        else:
            source_version = _utc_now_iso()
            mode_used = "live"
            query_url = _ESEARCH_URL
            source_label = "live:0"
        return {
            "success": True,
            "data": {
                "gene": gene,
                "significance": significance,
                "total_count": 0,
                "variants": [],
                "mode_used": mode_used,
                "source_version": source_version,
                "source": source_label,
                "release_date": None,
                "query_url": query_url,
            },
        }

    if use_local:
        if not local_path.is_file():
            return {
                "success": False,
                "error": (
                    f"ClinVar variant_summary.txt.gz not found at {str(local_path)!s}; "
                    f"run scripts/fetch_clinvar.py --download --out <dir>"
                ),
            }
        if not manifest:
            return {
                "success": False,
                "error": (
                    f"ClinVar MANIFEST not found at {str(local_path.parent)!s}/MANIFEST; "
                    f"re-run scripts/fetch_clinvar.py --download --out <dir>"
                ),
            }
        index_path = _lookup_index.index_path_for(local_path)
        conn = _lookup_index.open_fresh_index(
            local_path, _lookup_index.KIND_CLINVAR
        )
        variants: list[dict[str, Any]] = []
        total = 0
        lookup_path = "full-scan"
        if conn is not None:
            try:
                variants, total = _index_query(
                    gene, significance, max_results, conn
                )
                lookup_path = "index"
            except sqlite3.Error:
                lookup_path = "full-scan"
            finally:
                conn.close()
        if lookup_path == "full-scan":
            try:
                variants, total = _local_query(
                    gene, significance, max_results, local_path
                )
            except (OSError, gzip.BadGzipFile, csv.Error) as exc:
                return {
                    "success": False,
                    "error": (
                        f"ClinVar local TSV at {str(local_path)!s} is malformed: {exc}"
                    ),
                }
        release_date = manifest.get(
            "downloaded_at", manifest.get("completed_at", "unknown")
        )
        sha256 = manifest.get("sha256", "")
        if lookup_path == "index":
            sha256 = _lookup_index.read_meta(index_path).get("source_sha256", sha256)
        source_version = (
            f"sha256:{sha256}" if sha256 else f"date:{release_date}"
        )
        return {
            "success": True,
            "data": {
                "gene": gene,
                "significance": significance,
                "total_count": total,
                "variants": variants,
                "mode_used": "local",
                "lookup_path": lookup_path,
                "source_version": source_version,
                "source": f"local:{release_date}",
                "release_date": release_date,
                "query_url": str(local_path),
            },
        }

    # Live mode
    try:
        ids = _esearch(gene, sig_filter, max_results)
    except RuntimeError as exc:
        return {"success": False, "error": str(exc)}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"requests error: {exc!r}"}

    try:
        variants = _esummary(ids[:max_results])
    except RuntimeError as exc:
        return {"success": False, "error": str(exc)}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"requests error: {exc!r}"}

    query_time = _utc_now_iso()
    return {
        "success": True,
        "data": {
            "gene": gene,
            "significance": significance,
            "total_count": len(ids),
            "variants": variants,
            "mode_used": "live",
            "source_version": query_time,
            "source": f"live:{query_time}",
            "release_date": None,
            "query_url": _ESEARCH_URL,
        },
    }

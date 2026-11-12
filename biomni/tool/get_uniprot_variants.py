"""T2 get_uniprot_variants (Part 2).

Wrapper around the EBI Proteins API. Returns the variant features
for a UniProt accession. Uses `/api/features?types=VARIANT` (NOT
`/variation` — that endpoint returns 0 features per the brief's
prior-session note).
"""
from __future__ import annotations

import time

import requests

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 30
_API_BASE = "https://www.ebi.ac.uk/proteins/api"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return "EBI Proteins API (https://www.ebi.ac.uk/proteins/api)"


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def get_uniprot_variants(accession):
    """Given a UniProt accession, return the list of VARIANT features
    (sequence-altering variants annotated by UniProt).

    Returns the contract dict. `data` is::

        {
            "accession": <accession uppercased>,
            "variants": [
                {
                    "type": "VARIANT",
                    "description": "...",
                    "location": {"start": ..., "end": ..., "position": ...},
                    "alternativeSequence": {"alternativeSequence": "..."},
                    "xrefs": [...],
                    "featureId": "...",
                    "source": "...",
                },
                ...
            ]
        }
    """
    acc_norm = accession.upper()
    url = f"{_API_BASE}/features?accession={acc_norm}&types=VARIANT"
    resp = requests.get(url, timeout=_TIMEOUT_S)
    resp.raise_for_status()
    payload = resp.json()
    features: list = []
    if isinstance(payload, list):
        # legacy PDBe shape: list of {accession, features} records.
        inner = next(
            (it for it in payload
             if isinstance(it, dict) and it.get("accession") == acc_norm),
            {},
        )
        if isinstance(inner, dict):
            features = inner.get("features", []) or []
    elif isinstance(payload, dict):
        # current EBI shape: top-level dict with `accession`,
        # `features`, etc. keys. Mirrored endpoints may wrap the
        # dict in another `{accession: features}` shape; fall back
        # to scanning in that case.
        if payload.get("accession") == acc_norm and "features" in payload:
            features = payload.get("features", []) or []
        else:
            inner = next(iter(payload.values()), {}) if payload else {}
            if isinstance(inner, dict):
                features = inner.get("features", []) or []
    return {
        "data": {
            "accession": acc_norm,
            "variants": features,
        }
    }

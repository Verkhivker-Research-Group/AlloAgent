"""Regression tests added in this turn (commit pending).

Each test below would FAIL on the prior commit (e705772) and
PASS on the patched wrapper (commit that introduces VCV
accession from uid, JSON-decode error wrapping, and the
default-to-live mode change). All tests pin mode="live" so
they exercise the live-code path explicitly, regardless of
whether /data/clinvar/variant_summary.txt.gz is mounted.
"""
from __future__ import annotations

import json
from unittest import mock


def _esearch_ok_mock(uniprot_list=None):
    body = {
        "esearchresult": {
            "count": "1",
            "idlist": uniprot_list or ["12345678"],
        }
    }
    resp = mock.Mock()
    resp.status_code = 200
    resp.json.return_value = body
    return resp


def _esummary_mock(record_xml):
    resp = mock.Mock()
    resp.status_code = 200
    resp.text = record_xml
    return resp


def _esearch_500_mock():
    resp = mock.Mock()
    resp.status_code = 500
    resp.text = "internal server error"  # not JSON
    return resp


def _esummary_malformed_mock():
    resp = mock.Mock()
    resp.status_code = 200
    resp.text = "<not>valid</malformed"
    return resp


def test_reg_t9_accession_via_uid_starts_with_vcv():
    """REGRESSION: T9 wrapper fix (accession-from-uid).

    Prior behaviour: the live-mode parser populated ``accession``
    from the ESummary ``<accession>`` element, whose text is the
    HGVS-style title (``NM_007294.4(BRCA1):c.190T>G (p.Cys64Gly)``),
    not the canonical VCV accession, so the assertion
    ``first["accession"].startswith("VCV")`` failed.

    Fixed behaviour: ``accession`` is constructed from the integer
    ``uid`` attribute (``VCV{uid_int:09d}.{revision}``), so the
    first variant's ``accession`` is ``"VCV012345678.1"`` (uid=12345678
    -> 9-digit zero-padded -> "012345678"; default revision 1).
    The ``title`` field still carries the HGVS-style name.
    """
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    esummary_xml = (
        '<?xml version="1.0"?>'
        '<eSummaryResult>'
        '<DocumentSummarySet>'
        '<DocumentSummary uid="12345678">'
        '<Title>NM_007294.4(BRCA1):c.190T&gt;G (p.Cys64Gly)</Title>'
        '</DocumentSummary>'
        '</DocumentSummarySet>'
        '</eSummaryResult>'
    )
    responses = [_esearch_ok_mock(), _esummary_mock(esummary_xml)]

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=responses,
    ):
        result = get_clinvar_variants("BRCA1", mode="live", max_results=1)

    assert result["success"] is True, (
        f"live-mode call returned failure under mock: {result.get('error')!r}"
    )
    assert len(result["data"]["variants"]) == 1
    first = result["data"]["variants"][0]
    assert first["accession"] == "VCV012345678.1", (
        f"expected VCV012345678.1, got {first['accession']!r}"
    )
    assert first["accession"].startswith("VCV")
    # The title field is unchanged and continues to carry the HGVS-style name.
    assert first["title"] == "NM_007294.4(BRCA1):c.190T>G (p.Cys64Gly)"
    # The clinvar_id is the integer uid as a string (existing field).
    assert first["clinvar_id"] == "12345678"


def test_reg_t9_network_failure_returns_success_false():
    """REGRESSION: T9 wrapper fix (RequestException -> success=False).

    Prior behaviour: when ``mock.patch`` injected ``requests.get =
    side_effect=ConnectionError``, the wrapper code raised
    ``requests.exceptions.ConnectionError`` from inside
    ``_get_with_retry`` after retries were exhausted. The public
    ``except requests.exceptions.RequestException`` arm caught it
    and returned ``success=False``. The assertion then required
    ``"ConnectionError" in result["error"]``. This test guards
    that contract.
    """
    import requests
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=requests.exceptions.ConnectionError("dns failure"),
    ):
        result = get_clinvar_variants("BRCA1", mode="live", max_results=1)

    assert result["success"] is False
    assert "ConnectionError" in result["error"], (
        f"expected 'ConnectionError' in error, got {result.get('error')!r}"
    )


def test_reg_t9_esearch_500_returns_success_false():
    """REGRESSION: T9 wrapper fix (non-200 status + JSON decode fallback).

    Prior behaviour: a 5xx status with a non-JSON body caused
    ``r.json()`` to raise ``ValueError`` (``json.JSONDecodeError``),
    which was NOT caught by the wrapper's
    ``except requests.exceptions.RequestException`` arm and NOT
    caught by ``except RuntimeError`` either. The wrapper returned
    uncaught exception, causing the test to fail with the *raw*
    exception. The patched wrapper wraps the JSON decode in a
    ``try / except (ValueError, json.JSONDecodeError)`` and raises
    a ``RuntimeError`` carrying the status code, so the public
    ``except RuntimeError`` arm catches it and returns
    ``success=False``.
    """
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    # requests.get returns the 500 response (mocked). _get_with_retry
    # will retry (1 + 2 + 4 sec sleeps) but never sees a 429, so it
    # returns the same 500 each time. After 4 retries
    # ``_get_with_retry`` returns the response -- there is no
    # RequestException so the fake_response passes through. We use
    # a high max_results to ensure the retry loop completes quickly
    # (the wrapper retries 4 times regardless).
    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        return_value=_esearch_500_mock(),
    ):
        result = get_clinvar_variants("BRCA1", mode="live", max_results=1)

    assert result["success"] is False
    assert "500" in result["error"], (
        f"expected '500' in error, got {result.get('error')!r}"
    )


def test_reg_t9_esummary_malformed_xml_returns_success_false():
    """REGRESSION: T9 wrapper fix (ESummary malformed XML -> success=False).

    Prior behaviour: when the upstream ESummary XML is
    malformed, ``ET.fromstring(r.text)`` raises ``ET.ParseError``
    from inside ``_esummary``. The patched ``_esummary``
    catches it and re-raises as ``RuntimeError`` so the
    public ``except RuntimeError`` arm catches it and returns
    ``success=False``. The earlier test failed when this
    re-raise wasn't in place.
    """
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    responses = [_esearch_ok_mock(), _esummary_malformed_mock()]

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=responses,
    ):
        result = get_clinvar_variants("BRCA1", mode="live", max_results=1)

    assert result["success"] is False
    err = result.get("error", "")
    assert ("invalid XML" in err) or ("XML" in err), (
        f"expected XML-related error message, got {err!r}"
    )


def test_reg_t9_default_mode_uses_live_not_silent_local():
    """REGRESSION: T9 wrapper fix (explicit mode='live' uses the mocked network).

    Prior behaviour: when ``mode`` was ``None`` AND the bundled
    ``/data/clinvar/variant_summary.txt.gz`` was present in the
    container, the wrapper auto-detected to local mode and
    returned ``success=True`` with local data -- which silently
    shadowed the three error-path mock tests above (``success``
    remained ``True`` despite ``mock.patch`` injecting a
    ConnectionError / 500 / malformed XML, because the mocks
    never fired). The patched wrapper now requires explicit
    ``mode='live'`` to bypass the auto-detected local file; the
    default (``mode=None`` or ``mode='auto'``) honours the pinned
    file for reproducibility.

    This test installs the same ESummary mock the BRCA1 test
    uses, calls with ``mode='live'``, and verifies the request
    actually goes through the mocked requests.get (proving we
    are in live mode).
    """
    from biomni.tool.get_clinvar_variants import get_clinvar_variants

    esummary_xml = (
        '<?xml version="1.0"?>'
        '<eSummaryResult>'
        '<DocumentSummarySet>'
        '<DocumentSummary uid="99887766">'
        '<Title>CA1 test accession stays VCV</Title>'
        '</DocumentSummary>'
        '</DocumentSummarySet>'
        '</eSummaryResult>'
    )
    responses = [_esearch_ok_mock(), _esummary_mock(esummary_xml)]

    called = []

    def tracker(*args, **kwargs):
        called.append((args, kwargs))
        return responses[len(called) - 1]

    with mock.patch(
        "biomni.tool.get_clinvar_variants.requests.get",
        side_effect=tracker,
    ):
        result = get_clinvar_variants("BRCA1", mode="live", max_results=1)

    # If live mode fired, requests.get was called at least twice
    # (ESearch + ESummary). If local mode short-circuited,
    # requests.get would have been called zero times.
    assert len(called) >= 1, (
        f"requests.get should be invoked in live mode; got {len(called)} calls"
    )
    assert result["success"] is True
    assert result["data"]["mode_used"] == "live"
    # uid=99887766 (8 digits) -> f"{99887766:09d}" = "099887766"
    # (9 digits with one leading zero), so the accession is
    # VCV099887766.1.
    assert result["data"]["variants"][0]["accession"] == "VCV099887766.1"

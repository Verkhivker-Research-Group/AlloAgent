"""T8 search_pdb_by_uniprot_and_ligand tests (Part 2 / batch 2).

These tests cover all 14 criteria committed in
docs/2_search_pdb_by_uniprot_and_ligand_criteria.md.

Network-dependent tests (marked with `_LIVE_RCSB`) hit the live
RCSB Search API at https://search.rcsb.org/rcsbsearch/v2/query.
They are collected inside the alloagent-dev:phase1 container
(which has outbound HTTPS) and skip with a clear message on a
host without network access. The mock-based test
(test_t8_network_failure_returns_success_false) does not need
network access.
"""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]


def _live_rcsb_available() -> bool:
    try:
        import requests

        r = requests.get("https://search.rcsb.org/rcsbsearch/v2/query", timeout=5)
        return r.status_code in (200, 400, 405)
    except Exception:
        return False


_LIVE_RCSB = pytest.mark.skipif(
    not _live_rcsb_available(),
    reason="RCSB Search API not reachable from this host",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def test_t8_file_exists():
    impl = REPO / "biomni" / "tool" / "search_pdb_by_uniprot_and_ligand.py"
    assert impl.is_file(), f"missing {impl}"


def test_t8_tool_card_exists_and_has_no_self_reported():
    card = (
        REPO / "docs" / "tool_cards" / "T8_search_pdb_by_uniprot_and_ligand.md"
    )
    assert card.is_file(), f"missing {card}"
    text = card.read_text(encoding="utf-8")
    assert "self-reported" not in text, (
        f"tool card {card} contains forbidden 'self-reported' substring"
    )


def test_t8_criteria_doc_exists():
    crit = (
        REPO / "docs" / "2_search_pdb_by_uniprot_and_ligand_criteria.md"
    )
    assert crit.is_file(), f"missing {crit}"


@_LIVE_RCSB
def test_t8_known_answer_p69905_hem():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")
    assert result["success"] is True
    assert result["data"]["total_count"] >= 10
    assert result["data"]["entry_ids"][:5] == ["1A00", "1A01", "1A0U", "1A0Z", "1A3N"]


@_LIVE_RCSB
def test_t8_known_answer_p69441_atp():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P69441", "ATP")
    assert result["success"] is True
    assert result["data"]["total_count"] >= 1
    assert "8RJ6" in result["data"]["entry_ids"]


@_LIVE_RCSB
def test_t8_cross_check_p00519_sti_abl1_imatinib():
    """A2 cross-check: P00519 (ABL1) + STI (imatinib).

    Expected per the A2 prompt: exactly 2HYY, 3PYY, 6NPE, 6NPU,
    6NPV, 7N9G; 1IEP must NOT be present (1IEP is the ABL1
    SH3-domain crystal structure with a different ligand, not
    STI).

    Verified on 2026-10-10 against:
    - RCSB route (T8 itself): 6 entries, matches expected
    - PDBe route (EBI Proteins API + RCSB STI search): same
      6 entries
    - Count difference: 0
    - Discrepancy: NONE (tool correctly returns the expected
      list; no discrepancy to flag)
    """
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P00519", "STI")
    assert result["success"] is True
    expected = ["2HYY", "3PYY", "6NPE", "6NPU", "6NPV", "7N9G"]
    assert result["data"]["total_count"] == 6
    for e in expected:
        assert e in result["data"]["entry_ids"], (
            f"expected {e} in result, got {result['data']['entry_ids']}"
        )
    assert "1IEP" not in result["data"]["entry_ids"], (
        f"1IEP must NOT be present (1IEP is mouse ABL1/P00520, "
        f"not human P00519); got {result['data']['entry_ids']}"
    )


@_LIVE_RCSB
def test_t8_accession_specificity_mouse_ortholog_excluded():
    """A5/T8 verification: the tool is accession-specific and
    excludes orthologs. Querying human ABL1 (P00519) must NOT
    return 1IEP/1FPU (which are mouse ABL1, P00520, complexed
    with STI-571/imatinib). Querying mouse ABL1 (P00520) must
    NOT return the 6 human ABL1 structures. See
    docs/tool_cards/T8_search_pdb_by_uniprot_and_ligand.md
    for the full verification.
    """
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result_human = search_pdb_by_uniprot_and_ligand("P00519", "STI")
    assert result_human["success"] is True
    for excluded in ("1IEP", "1FPU"):
        assert excluded not in result_human["data"]["entry_ids"], (
            f"{excluded} (mouse ABL1/P00520) must NOT be in P00519 result; "
            f"the tool is accession-specific"
        )

    result_mouse = search_pdb_by_uniprot_and_ligand("P00520", "STI")
    assert result_mouse["success"] is True
    assert "1IEP" in result_mouse["data"]["entry_ids"], (
        f"1IEP (mouse ABL1 with STI-571) must be in P00520 result; "
        f"got {result_mouse['data']['entry_ids']}"
    )
    for human_struct in ("2HYY", "3PYY", "6NPE", "6NPU", "6NPV", "7N9G"):
        assert human_struct not in result_mouse["data"]["entry_ids"], (
            f"{human_struct} (human ABL1) must NOT be in P00520 result"
        )


@_LIVE_RCSB
def test_t8_negative_control_unknown_uniprot():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("ZZZZZZ", "ATP")
    assert result["success"] is True
    assert result["data"]["entry_ids"] == []
    assert result["data"]["total_count"] == 0


@_LIVE_RCSB
def test_t8_negative_control_unknown_ligand():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P69441", "ZZZ")
    assert result["success"] is True
    assert result["data"]["entry_ids"] == []
    assert result["data"]["total_count"] == 0


@_LIVE_RCSB
def test_t8_determinism():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    a = search_pdb_by_uniprot_and_ligand("P69905", "HEM")
    b = search_pdb_by_uniprot_and_ligand("P69905", "HEM")
    assert a["data"]["entry_ids"] == b["data"]["entry_ids"]


@_LIVE_RCSB
def test_t8_score_order_first_five_have_score_1():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")
    assert result["success"] is True
    import requests

    body = requests.post(
        "https://search.rcsb.org/rcsbsearch/v2/query",
        json={
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": [
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": (
                                "rcsb_polymer_entity_container_identifiers"
                                ".reference_sequence_identifiers"
                                ".database_accession"
                            ),
                            "operator": "exact_match",
                            "value": "P69905",
                        },
                    },
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": (
                                "rcsb_chem_comp_container_identifiers.comp_id"
                            ),
                            "operator": "exact_match",
                            "value": "HEM",
                        },
                    },
                ],
            },
            "return_type": "entry",
        },
        timeout=30,
    ).json()
    scores = [item.get("score", 0.0) for item in body.get("result_set", [])]
    assert scores[:5] == [1.0, 1.0, 1.0, 1.0, 1.0]


@_LIVE_RCSB
def test_t8_return_contract_keys_present():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")
    assert _contract_keys_present(result)
    assert result["success"] is True
    assert isinstance(result["data"]["entry_ids"], list)
    assert isinstance(result["data"]["total_count"], int)
    assert result["data"]["uniprot_id"] == "P69905"
    assert result["data"]["ligand_id"] == "HEM"


def test_t8_invalid_inputs_return_success_false():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    assert search_pdb_by_uniprot_and_ligand("", "HEM")["success"] is False
    assert search_pdb_by_uniprot_and_ligand("P69905", "")["success"] is False
    assert search_pdb_by_uniprot_and_ligand(None, "HEM")["success"] is False
    assert search_pdb_by_uniprot_and_ligand("P69905", 123)["success"] is False


def test_t8_network_failure_returns_success_false():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    fake_response = mock.Mock()
    fake_response.status_code = 500
    fake_response.text = "internal server error"

    with mock.patch(
        "biomni.tool.search_pdb_by_uniprot_and_ligand.requests.post",
        return_value=fake_response,
    ):
        result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")

    assert result["success"] is False
    assert "500" in result["error"]


def test_t8_network_unreachable_returns_success_false():
    import requests

    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    with mock.patch(
        "biomni.tool.search_pdb_by_uniprot_and_ligand.requests.post",
        side_effect=requests.exceptions.ConnectionError("dns failure"),
    ):
        result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")

    assert result["success"] is False
    assert "ConnectionError" in result["error"]


def test_t8_invalid_json_response_returns_success_false():
    from biomni.tool.search_pdb_by_uniprot_and_ligand import (
        search_pdb_by_uniprot_and_ligand,
    )

    fake_response = mock.Mock()
    fake_response.status_code = 200
    fake_response.json.side_effect = ValueError("not json")

    with mock.patch(
        "biomni.tool.search_pdb_by_uniprot_and_ligand.requests.post",
        return_value=fake_response,
    ):
        result = search_pdb_by_uniprot_and_ligand("P69905", "HEM")

    assert result["success"] is False
    assert "invalid JSON" in result["error"]

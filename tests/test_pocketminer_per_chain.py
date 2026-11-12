"""Part 1 - the PocketMiner result must be per chain.

The criteria are committed at docs/1_pocketminer_criteria.md; the
numbers here are the ones an independent per-chain calculation on
7WVB produced in alloagent-eval:v4 (1165 standard residues in four
chains: A 293, B 293, C 293, D 286).

This file is the **failing-before** test: against the previous
wrapper, which returned a flat `residue_scores` list with no chain
information at all, every test below fails.
"""
from __future__ import annotations

import os
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest

EXPECTED_CHAIN_MEANS = {
    "A": 0.542914,
    "B": 0.539538,
    "C": 0.545426,
    "D": 0.549240,
}
EXPECTED_CHAIN_COUNTS = {"A": 293, "B": 293, "C": 293, "D": 286}
EXPECTED_ALL_RESIDUE_MEAN = 0.544250
EXPECTED_ALL_RESIDUES = 1165


def _rcsb_available() -> bool:
    try:
        with urllib.request.urlopen(
            "https://files.rcsb.org/download/7WVB.pdb", timeout=30
        ) as response:
            return response.status == 200
    except Exception:
        return False


_LIVE = pytest.mark.skipif(
    not _rcsb_available(),
    reason="RCSB is unreachable from this host, so 7WVB cannot be fetched",
)


@pytest.fixture(scope="module")
def scored_7wvb():
    from biomni.tool.pocketminer import pocketminer_score

    with tempfile.TemporaryDirectory() as tmp:
        pdb = Path(tmp) / "7WVB.pdb"
        urllib.request.urlretrieve("https://files.rcsb.org/download/7WVB.pdb", pdb)
        result = pocketminer_score(str(pdb))
    assert result["success"] is True, result.get("error")
    return result["data"]


@_LIVE
def test_pocketminer_reports_every_chain_with_its_own_mean(scored_7wvb):
    """Criterion 1 and 2: the four chains of 7WVB are reported, each
    with its own mean, and the means match the independent calculation."""
    data = scored_7wvb

    chains = data.get("chains")
    assert isinstance(chains, dict) and chains, (
        "the result carries no per-chain block, so a multi-chain "
        "structure cannot be reported per chain")
    assert set(chains) == set(EXPECTED_CHAIN_MEANS), (
        f"the chains reported are {sorted(chains)}, expected "
        f"{sorted(EXPECTED_CHAIN_MEANS)}")
    for chain_name, expected_mean in EXPECTED_CHAIN_MEANS.items():
        block = chains[chain_name]
        assert block["n_residues"] == EXPECTED_CHAIN_COUNTS[chain_name], (
            f"chain {chain_name}: {block['n_residues']} residues, expected "
            f"{EXPECTED_CHAIN_COUNTS[chain_name]}")
        assert abs(block["mean"] - expected_mean) < 5e-7, (
            f"chain {chain_name}: mean {block['mean']!r}, expected {expected_mean}")


@_LIVE
def test_pocketminer_residue_rows_carry_the_chain(scored_7wvb):
    """Criterion 1: every scored residue carries its chain and its
    residue number, in the order of residue_scores."""
    data = scored_7wvb

    residues = data.get("residues")
    assert isinstance(residues, list) and residues, (
        "the result carries no per-residue chain information")
    scores = data["residue_scores"]
    assert len(residues) == len(scores) == EXPECTED_ALL_RESIDUES, (
        f"{len(residues)} residue rows for {len(scores)} scores, expected "
        f"{EXPECTED_ALL_RESIDUES}")
    for row, score in zip(residues, scores):
        assert row["chain"] in EXPECTED_CHAIN_MEANS, row
        assert isinstance(row["residue_number"], int), row
        assert row["score"] == score, (row, score)


@_LIVE
def test_pocketminer_the_uniprot_keyed_collapse_cannot_happen(scored_7wvb):
    """Criterion 3: the four chains have four DIFFERENT means, so the
    collapse is visible, and no single field mixes the chains."""
    data = scored_7wvb

    chains = data["chains"]
    means = {name: block["mean"] for name, block in chains.items()}
    assert len(set(round(value, 9) for value in means.values())) == 4, (
        f"the per-chain means are not distinct: {means} - a chain collapse "
        f"would be invisible")

    all_mean = data.get("all_residue_mean")
    assert all_mean is not None, "the all-residue mean is not reported"
    assert abs(all_mean - EXPECTED_ALL_RESIDUE_MEAN) < 5e-7, (
        f"the all-residue mean is {all_mean!r}, expected {EXPECTED_ALL_RESIDUE_MEAN}")

    # No field may carry a single "the mean for this protein" number
    # that a caller could mistake for a per-chain value: the only
    # aggregates are the per-chain means and the explicitly named
    # all-residue mean.
    for key in data:
        if key in {"residue_scores", "residues", "chains", "all_residue_mean",
                   "n_residues", "source", "weights_sha256", "runtime_seconds",
                   "chain_mapping_note"}:
            continue
        raise AssertionError(f"unexpected aggregate field in the result: {key}")

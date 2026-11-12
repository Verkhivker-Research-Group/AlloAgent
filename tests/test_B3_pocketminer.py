"""B3 PocketMiner + AE-PocketMiner tests (Part 2 / batch 2).

These tests cover the Step 1 criteria committed in
docs/2_pocketminer_criteria.md. The live tests run the actual
PocketMiner and AE-PocketMiner inference on 1AKE and assert the
known-shape outputs (428 per-residue scores in [0, 1], attention
weights of shape (1, 2, 428, 428) for AE-PocketMiner). They skip
when the pocketminer_env is not built. The Step 2 CryptoBench
validation is in a separate file (to be written when the dataset
is available).
"""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE_PDB = REPO / "tests" / "fixtures" / "1ake.pdb"

_POCKETMINER_PYTHON = Path("/opt/conda/envs/pocketminer_env/bin/python")
_AE_POCKETMINER_DIR = Path("/opt/ae-pocketminer")
_POCKETMINER_DIR = Path("/opt/pocketminer")
_POCKETMINER_NN_PREFIX = _POCKETMINER_DIR / "models" / "pocketminer"
_POCKETMINER_NN_DATA = _POCKETMINER_NN_PREFIX.with_suffix(".data-00000-of-00001")
_POCKETMINER_NN_INDEX = _POCKETMINER_NN_PREFIX.with_suffix(".index")
_AE_POCKETMINER_NN_PREFIX = _AE_POCKETMINER_DIR / "models" / "aepocketminer"
_AE_POCKETMINER_NN_DATA = _AE_POCKETMINER_NN_PREFIX.with_suffix(".data-00000-of-00001")
_AE_POCKETMINER_NN_INDEX = _AE_POCKETMINER_NN_PREFIX.with_suffix(".index")

_ENV_AVAILABLE = _POCKETMINER_PYTHON.is_file()
_REPO_AVAILABLE = _POCKETMINER_DIR.is_dir()
_AE_REPO_AVAILABLE = _AE_POCKETMINER_DIR.is_dir()
_WEIGHTS_AVAILABLE = _POCKETMINER_NN_DATA.is_file() and _POCKETMINER_NN_INDEX.is_file()
_AE_WEIGHTS_AVAILABLE = _AE_POCKETMINER_NN_DATA.is_file() and _AE_POCKETMINER_NN_INDEX.is_file()

_ENV_SKIP_REASON = (
    "pocketminer_env not built; rebuild the Docker image with the "
    "layered Dockerfile (Dockerfile target dev or eval)"
)

# 1AKE has chains A and B; mdtraj loads it as a 428-standard-residue
# complex (214 residues per chain * 2 chains = 428). PocketMiner
# predicts one sigmoid score per standard residue. Published
# first-five values for PocketMiner on 1AKE (Meller et al. 2023,
# Phase 2c reproduction): 0.5353, 0.7912, 0.7100, 0.8246, 0.8816.
_EXPECTED_1AKE_POCKETMINER_FIRST5 = [0.5353, 0.7912, 0.7100, 0.8246, 0.8816]
_EXPECTED_1AKE_N_RESIDUES = 428



def test_b3_pocketminer_file_exists():
    impl = REPO / "biomni" / "tool" / "pocketminer.py"
    assert impl.is_file(), f"missing {impl}"


def test_b3_ae_pocketminer_file_exists():
    impl = REPO / "biomni" / "tool" / "ae_pocketminer.py"
    assert impl.is_file(), f"missing {impl}"


def test_b3_dockerfile_patch_doc_exists():
    patch = REPO / "docs" / "build" / "b3_pocketminer_env_dockerfile_patch.md"
    assert patch.is_file(), f"missing {patch}"


def test_b3_pocketminer_tool_card_no_self_reported():
    card = REPO / "docs" / "tool_cards" / "B3_pocketminer.md"
    if card.is_file():
        text = card.read_text(encoding="utf-8")
        assert "self-reported" not in text


def test_b3_ae_pocketminer_tool_card_no_self_reported():
    card = REPO / "docs" / "tool_cards" / "B3_ae_pocketminer.md"
    if card.is_file():
        text = card.read_text(encoding="utf-8")
        assert "self-reported" not in text


def test_b3_pocketminer_docstring_contains_disclaimer():
    impl = REPO / "biomni" / "tool" / "pocketminer.py"
    text = impl.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert (
        "PocketMiner predicts MD-defined pocket-opening propensity "
        "(cryptic pockets), not allosteric sites specifically" in normalized
    )


def test_b3_ae_pocketminer_docstring_contains_disclaimer():
    impl = REPO / "biomni" / "tool" / "ae_pocketminer.py"
    text = impl.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert (
        "AE-PocketMiner is experimental (unreplicated preprint) "
        "and is NOT on the default exposed list" in normalized
    )


def test_b3_pocketminer_return_contract_keys():
    from biomni.tool.pocketminer import pocketminer_score

    result = pocketminer_score(str(FIX_1AKE_PDB)) if FIX_1AKE_PDB.is_file() else pocketminer_score("dummy")
    for key in ("success", "source", "source_version", "query_time_utc"):
        assert key in result
    if result["success"]:
        assert "data" in result
        assert "residue_scores" in result["data"]
        assert "source" in result["data"]


def test_b3_ae_pocketminer_return_contract_keys():
    from biomni.tool.ae_pocketminer import ae_pocketminer_score

    result = ae_pocketminer_score(str(FIX_1AKE_PDB)) if FIX_1AKE_PDB.is_file() else ae_pocketminer_score("dummy")
    for key in ("success", "source", "source_version", "query_time_utc"):
        assert key in result
    if result["success"]:
        assert "data" in result
        assert "residue_scores" in result["data"]
        assert "source" in result["data"]


def test_b3_pocketminer_invalid_inputs():
    from biomni.tool.pocketminer import pocketminer_score

    assert pocketminer_score("")["success"] is False
    assert pocketminer_score(None)["success"] is False
    assert pocketminer_score("/nonexistent.pdb")["success"] is False


def test_b3_ae_pocketminer_invalid_inputs():
    from biomni.tool.ae_pocketminer import ae_pocketminer_score

    assert ae_pocketminer_score("")["success"] is False
    assert ae_pocketminer_score(None)["success"] is False
    assert ae_pocketminer_score("/nonexistent.pdb")["success"] is False


@pytest.mark.skipif(not _ENV_AVAILABLE, reason=_ENV_SKIP_REASON)
@pytest.mark.skipif(not FIX_1AKE_PDB.is_file(), reason="1ake.pdb fixture not found")
def test_b3_pocketminer_smoke_1ake():
    """Smoke test: run PocketMiner on 1AKE and assert the real
    per-residue output shape (428 scores in [0, 1])."""
    from biomni.tool.pocketminer import pocketminer_score

    result = pocketminer_score(str(FIX_1AKE_PDB))
    assert result["success"] is True, f"PocketMiner wrapper failed: {result.get('error')}"
    assert "residue_scores" in result["data"]
    scores = result["data"]["residue_scores"]
    assert len(scores) == _EXPECTED_1AKE_N_RESIDUES, (
        f"expected {_EXPECTED_1AKE_N_RESIDUES} per-residue scores, got {len(scores)}"
    )
    assert all(0.0 <= s <= 1.0 for s in scores), (
        f"residue_scores out of [0, 1] range: min={min(scores)}, max={max(scores)}"
    )
    assert result["data"]["source"].startswith("PocketMiner@")
    assert result["data"]["n_residues"] == _EXPECTED_1AKE_N_RESIDUES


@pytest.mark.skipif(not _ENV_AVAILABLE, reason=_ENV_SKIP_REASON)
@pytest.mark.skipif(not _WEIGHTS_AVAILABLE, reason="PocketMiner checkpoint not in image")
@pytest.mark.skipif(not FIX_1AKE_PDB.is_file(), reason="1ake.pdb fixture not found")
def test_b3_pocketminer_first5_matches_phase2c():
    """The first 5 PocketMiner per-residue scores on 1AKE must
    match the Phase 2c reproduction (0.5353, 0.7912, 0.7100,
    0.8246, 0.8816) within atol=1e-3."""
    from biomni.tool.pocketminer import pocketminer_score

    result = pocketminer_score(str(FIX_1AKE_PDB))
    assert result["success"] is True, f"PocketMiner wrapper failed: {result.get('error')}"
    scores = result["data"]["residue_scores"]
    actual = scores[:5]
    expected = _EXPECTED_1AKE_POCKETMINER_FIRST5
    assert all(abs(a - e) < 1e-3 for a, e in zip(actual, expected)), (
        f"first 5 PocketMiner scores on 1AKE drift: expected {expected}, got {actual}"
    )


@pytest.mark.skipif(not _ENV_AVAILABLE, reason=_ENV_SKIP_REASON)
@pytest.mark.skipif(not _AE_WEIGHTS_AVAILABLE, reason="AE-PocketMiner checkpoint not in image")
@pytest.mark.skipif(not FIX_1AKE_PDB.is_file(), reason="1ake.pdb fixture not found")
def test_b3_ae_pocketminer_smoke_1ake():
    """Smoke test: run AE-PocketMiner on 1AKE and assert the real
    per-residue output shape (428 scores) and attention weights
    shape (1, 2, 428, 428)."""
    from biomni.tool.ae_pocketminer import ae_pocketminer_score

    result = ae_pocketminer_score(str(FIX_1AKE_PDB))
    assert result["success"] is True, f"AE-PocketMiner wrapper failed: {result.get('error')}"
    assert "residue_scores" in result["data"]
    scores = result["data"]["residue_scores"]
    assert len(scores) == _EXPECTED_1AKE_N_RESIDUES, (
        f"expected {_EXPECTED_1AKE_N_RESIDUES} per-residue scores, got {len(scores)}"
    )
    assert all(0.0 <= s <= 1.0 for s in scores), (
        f"AE-PocketMiner residue_scores out of [0, 1]: min={min(scores)}, max={max(scores)}"
    )
    aw_shape = result["data"].get("attention_weights_shape")
    assert aw_shape is not None, "AE-PocketMiner must report attention_weights_shape"
    assert aw_shape == [1, 2, _EXPECTED_1AKE_N_RESIDUES, _EXPECTED_1AKE_N_RESIDUES], (
        f"AE-PocketMiner attention_weights shape mismatch: expected "
        f"[1, 2, {_EXPECTED_1AKE_N_RESIDUES}, {_EXPECTED_1AKE_N_RESIDUES}], got {aw_shape}"
    )
    assert result["data"]["source"].startswith("AE-PocketMiner@")



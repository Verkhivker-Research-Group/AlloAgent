"""Registration test (Part 1e)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

from biomni.tool._registration import (
    EXPOSED_TOOLS_PATH,
    binary_available,
    build_tools_meta,
    compute_schema_hash,
    log_skip,
    read_exposed_tools,
)
from biomni.tool.schema_generator import generate_schema


@pytest.fixture
def exposed_tools_file(tmp_path, monkeypatch):
    p = tmp_path / "exposed_tools.txt"
    p.write_text(
        "# header comment\n"
        "query_uniprot\n"
        "query_kegg\n"
        "query_reactome\n"
        "\n"
        "# T1 placeholder\n"
        "map_residues_uniprot_pdb\n",
        encoding="utf-8",
    )
    return p


def test_e1_alloagent_package_and_file_present():
    assert (Path(__file__).resolve().parents[1] / "alloagent" / "__init__.py").is_file()
    assert EXPOSED_TOOLS_PATH.is_file()


def test_e2_read_exposed_tools(exposed_tools_file):
    names = read_exposed_tools(exposed_tools_file)
    assert names == [
        "query_uniprot",
        "query_kegg",
        "query_reactome",
        "map_residues_uniprot_pdb",
    ]


def test_e2_read_exposed_tools_skips_comments_blanks(tmp_path):
    text = "# c1\nA\n\n# c2\nB\n   \nC\n"
    p = tmp_path / "_exposed_tools_skip.txt"
    p.write_text(text, encoding="utf-8")
    assert read_exposed_tools(p) == ["A", "B", "C"]


def test_e5_compute_schema_hash_known_value():
    """A known dict must produce a known hash."""
    h = compute_schema_hash({"name": "f", "required_parameters": ["x"], "y": 1})
    assert h == hashlib.sha256(
        json.dumps(
            {"name": "f", "required_parameters": ["x"], "y": 1},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def test_e4_build_tools_meta_has_version_and_schema_hash():
    def a(x=1):
        """tool a doc."""
        return x

    def b(y=2):
        """tool b doc."""
        return y

    schemas = [generate_schema(a), generate_schema(b)]
    meta = build_tools_meta(schemas)
    assert "a" in meta and "b" in meta
    assert "version" in meta["a"]
    assert "schema_hash" in meta["a"]
    assert len(meta["a"]["schema_hash"]) == 64  # sha256 hex


def test_e4_build_tools_meta_default_schemas():
    """If schemas is None, build_tools_meta calls collect_all_schemas().
    The exact count depends on the test env (which tool modules import
    cleanly); the test asserts the return shape, not the count.
    """
    meta = build_tools_meta(schemas=None)
    assert isinstance(meta, dict)
    for name, info in meta.items():
        assert "version" in info
        assert "schema_hash" in info
        assert len(info["schema_hash"]) == 64  # sha256 hex


def test_e6_binary_available_uses_path():
    """If `which` finds the binary, return True; if not, False."""
    # `python` is always on PATH; `nonexistent-binary-xyz` is not.
    assert binary_available(sys.executable.split("/")[-1]) is True
    assert binary_available("nonexistent-binary-xyz-12345") is False


def test_e6_binary_available_env_var_override(monkeypatch):
    """An env-var override flips the answer even if the binary is absent."""
    monkeypatch.setenv("ALLOAGENT_DUMMY_BINARY_PRESENT", "1")
    assert binary_available("nonexistent-binary-xyz-12345", env_var="ALLOAGENT_DUMMY_BINARY_PRESENT") is True


def test_e6_log_skip_emits_one_line(capsys):
    log_skip("map_residues_uniprot_pdb", "no PDBe mapping binary on PATH")
    captured = capsys.readouterr()
    assert "map_residues_uniprot_pdb" in captured.err
    assert "no PDBe mapping binary" in captured.err


class _Dummy:
    def __init__(self, name, **kwargs):
        self.__name__ = name
        for k, v in kwargs.items():
            setattr(self, k, v)

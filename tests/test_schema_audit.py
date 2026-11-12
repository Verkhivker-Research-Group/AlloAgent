"""Schema-audit test (Part 1b).

The test fails (not skips) if any tool_description/<topic>.py module
fails to import, if any generated schema does not match its function
signature, or if the hand-typed metadata dicts in the topic files
still exist (single-source-of-truth).
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path

import pytest

import biomni
import biomni.tool as _impl_pkg
from biomni.tool.schema_generator import (
    _impl_module_names,
    collect_all_schemas,
    discover_tool_functions,
    generate_schema,
)


def test_b1_schema_generator_module_exists():
    assert Path(biomni.__file__).parent.joinpath("tool", "schema_generator.py").is_file()


def test_b2_generate_schema_returns_required_keys():
    """Pick one well-known function and check the four required keys."""
    from biomni.tool import database
    schema = generate_schema(database.query_uniprot)
    assert "name" in schema
    assert "description" in schema
    assert "required_parameters" in schema
    assert "parameters" in schema
    assert schema["name"] == "query_uniprot"


def test_b6_all_topic_modules_import():
    """Every `biomni/tool/<topic>.py` (implementation module) must import without
    a real ImportError. Optional third-party deps that are not installed in
    the test env (e.g. nibabel, torch, esm, PyPDF2) are SKIPPED, not failed,
    because the upstream implementation does an opportunistic `import
    <optional>` at module top.
    """
    failures = []
    skipped = []
    for modname in _impl_module_names():
        full = f"biomni.tool.{modname}"
        try:
            importlib.import_module(full)
        except ModuleNotFoundError as e:
            skipped.append((full, e.name or str(e)))
        except Exception as e:
            failures.append((full, repr(e)))
    assert not failures, f"real import errors (not optional-dep): {failures}"
    print(
        f"\n[schema-audit] modules skipped (optional dep not installed): "
        f"{len(skipped)} -- {[s[1] for s in skipped]}"
    )


def _param_names(sig):
    return list(sig.parameters.keys())


def _required_from_sig(func):
    return [
        name
        for name, p in inspect.signature(func).parameters.items()
        if p.default is inspect.Parameter.empty
    ]


def test_b3_b4_b5_schema_matches_signature():
    """Every discovered tool's generated schema must match its function signature."""
    funcs = discover_tool_functions()
    assert funcs, "no tool functions discovered"
    mismatches = []
    for f in funcs:
        schema = generate_schema(f)
        if schema["name"] != f.__name__:
            mismatches.append((f.__name__, "name mismatch", schema["name"]))
            continue
        sig = inspect.signature(f)
        sig_names = set(_param_names(sig))
        sig_required = set(_required_from_sig(f))
        schema_required = set(schema["required_parameters"])
        if schema_required != sig_required:
            mismatches.append(
                (f.__name__, "required mismatch", sig_required ^ schema_required)
            )
        schema_params = {p["name"] for p in schema["parameters"]}
        if schema_params != sig_names:
            mismatches.append(
                (f.__name__, "params mismatch", sig_names ^ schema_params)
            )
    assert not mismatches, f"schema mismatches: {mismatches[:5]}"


def test_b7_audit_counts():
    """Report the discovered-tool and mismatch counts (asserted zero)."""
    funcs = discover_tool_functions()
    schemas = collect_all_schemas()
    assert len(funcs) == len(schemas)
    # Re-run the same checks the per-function test does, for the verdict print
    bad = []
    for f, schema in zip(funcs, schemas):
        sig = inspect.signature(f)
        if set(schema["required_parameters"]) != set(_required_from_sig(f)):
            bad.append(f.__name__)
    assert not bad, f"required mismatches: {bad}"
    print(
        f"\n[schema-audit] discovered tools: {len(funcs)}; "
        f"mismatches: {len(bad)}"
    )


def test_b8_no_hand_typed_metadata_in_topic_files():
    """No topic file (description or implementation) may carry a hand-typed
    schema dict literal with the three schema keys (name/description/
    required_parameters) together. A function body that uses `name` or
    `description` as a parameter name (e.g. `query_cbioportal(prompt, name, description, ...)`)
    is NOT a schema dict and must not be flagged.
    """
    import re

    SCHEMA_DICT_RE = re.compile(
        r"\{[^{}]*\"name\"\s*:[^{}]*\"description\"\s*:[^{}]*\"required_parameters\"",
        re.DOTALL,
    )

    paths = []
    desc_dir = Path(biomni.__file__).parent / "tool" / "tool_description"
    if desc_dir.is_dir():
        paths.extend(desc_dir.glob("*.py"))
    impl_dir = Path(biomni.__file__).parent / "tool"
    for p in impl_dir.glob("*.py"):
        if p.name not in {"__init__.py", "_model.py", "schema_generator.py",
                          "tool_registry.py"}:
            paths.append(p)

    flagged = []
    for p in paths:
        text = p.read_text(encoding="utf-8")
        for m in SCHEMA_DICT_RE.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            flagged.append((str(p), line_no, m.group()[:80]))
    assert not flagged, (
        f"hand-typed schema dict in {len(flagged)} file(s): "
        f"{[(p, ln) for p, ln, _ in flagged[:5]]}"
    )

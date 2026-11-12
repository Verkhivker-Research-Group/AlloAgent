"""Port batch 4 known-answer tests: database genetics + support tools.

Every expectation here is committed BEFORE the batch was run, in
``docs/2_port_batch4_database_support_known_answers.md`` (F-1..F-16).
Each test cites the F- number it implements.
"""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_restrictions():
    """Every test starts with no import restrictions and leaves none."""
    from biomni.tool import support_tools

    support_tools.set_restricted_imports([])
    yield
    support_tools.set_restricted_imports([])


# --------------------------------------------------------------------------
# set_restricted_imports / _is_import_restricted  (F-1 .. F-6)
# --------------------------------------------------------------------------


def test_f1_set_restricted_imports():
    """F-1: the prefixes in force are reported back."""
    from biomni.tool.support_tools import set_restricted_imports

    r = set_restricted_imports(["os", "shutil"])
    assert r["success"] is True, r.get("error")
    assert r["data"]["prefixes"] == ["os", "shutil"]


def test_f2_set_restricted_imports_none_clears():
    """F-2: None clears the restrictions."""
    from biomni.tool.support_tools import set_restricted_imports

    set_restricted_imports(["os"])
    r = set_restricted_imports(None)
    assert r["success"] is True
    assert r["data"]["prefixes"] == []


def test_f3_set_restricted_imports_rejects_non_list():
    """F-3: a bare string is not a list of prefixes."""
    from biomni.tool.support_tools import set_restricted_imports

    r = set_restricted_imports("os")
    assert r["success"] is False
    assert "list" in r["error"]


def test_f4_is_import_restricted_exact_match():
    """F-4: the module itself is blocked."""
    from biomni.tool.support_tools import (
        _is_import_restricted, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    assert _is_import_restricted("os") is True


def test_f5_is_import_restricted_submodule():
    """F-5: the dotted subtree is blocked."""
    from biomni.tool.support_tools import (
        _is_import_restricted, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    assert _is_import_restricted("os.path") is True


def test_f6_is_import_restricted_is_not_a_substring_match():
    """F-6: 'osaka' is not blocked by the prefix 'os'."""
    from biomni.tool.support_tools import (
        _is_import_restricted, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    assert _is_import_restricted("osaka") is False


# --------------------------------------------------------------------------
# run_python_repl with restrictions  (F-7 .. F-13)
# --------------------------------------------------------------------------


def test_f7_run_python_repl_blocks_plain_import():
    """F-7: `import os` is refused."""
    from biomni.tool.support_tools import (
        run_python_repl, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    out = run_python_repl("import os")
    assert out == (
        "Error: Import of restricted module prefix 'os' is blocked by agent policy."
    )


def test_f8_run_python_repl_blocks_from_import():
    """F-8: `from os import path` is refused."""
    from biomni.tool.support_tools import (
        run_python_repl, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    out = run_python_repl("from os import path")
    assert "blocked by agent policy" in out


def test_f9_run_python_repl_blocks_submodule_import():
    """F-9: `import os.path` is refused by the static scan."""
    from biomni.tool.support_tools import (
        run_python_repl, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    out = run_python_repl("import os.path")
    assert "blocked by agent policy" in out


def test_f10_run_python_repl_blocks_direct_dunder_import():
    """F-10 (see corrections C-8): the replaced importer refuses a
    direct __import__ call.

    importlib.import_module is NOT blocked: it calls the import
    machinery directly rather than builtins.__import__, so it bypasses
    the override. The old tool had the same gap.
    """
    from biomni.tool.support_tools import (
        run_python_repl, set_restricted_imports,
    )

    set_restricted_imports(["os"])
    out = run_python_repl("__import__('os')")
    assert out.startswith(
        "Error: Import of module 'os' is restricted by agent configuration"
    )


def test_f11_run_python_repl_allows_unrestricted_import():
    """F-11: with no restrictions the import succeeds silently."""
    from biomni.tool.support_tools import run_python_repl

    out = run_python_repl("import os")
    assert out == ""


def test_f12_run_python_repl_captures_stdout():
    """F-12: stdout is captured and returned."""
    from biomni.tool.support_tools import run_python_repl

    assert run_python_repl("print(1 + 1)") == "2\n"


def test_f13_run_python_repl_reports_errors():
    """F-13: an exception comes back as an error string, not a raise."""
    from biomni.tool.support_tools import run_python_repl

    out = run_python_repl("1/0")
    assert out.startswith("Error: division by zero")


# --------------------------------------------------------------------------
# query_opentarget_genetics  (F-14 .. F-16)
# --------------------------------------------------------------------------


def test_f14_query_opentarget_genetics_requires_prompt_or_query():
    """F-14: neither a prompt nor a query is an error."""
    from biomni.tool.database import query_opentarget_genetics

    result = query_opentarget_genetics()
    assert result["error"] == (
        "Either a prompt or a GraphQL query must be provided"
    )


def test_f15_query_opentarget_genetics_live_minimal_query():
    """F-15: a real GraphQL query against the live Genetics API."""
    from biomni.tool.database import query_opentarget_genetics

    result = query_opentarget_genetics(query="query { __typename }")
    if result.get("success") is True:
        assert result["result"]["data"]["__typename"] == "Query"
        assert result["query_info"]["endpoint"] == (
            "https://api.genetics.opentargets.org/graphql"
        )
    else:
        # The Genetics API host no longer resolves (see corrections
        # C-10), so the live branch today is the structured failure.
        assert "error" in result
        assert "api.genetics.opentargets.org" in result["error"]


def test_f16_query_opentarget_genetics_non_verbose_keeps_result():
    """F-16: verbose=False still returns the payload."""
    from biomni.tool.database import query_opentarget_genetics

    result = query_opentarget_genetics(
        query="query { __typename }", verbose=False
    )
    if result.get("success") is True:
        assert result["result"]
    else:
        assert "error" in result
        assert "api.genetics.opentargets.org" in result["error"]

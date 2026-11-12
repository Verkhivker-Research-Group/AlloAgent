"""Single source of truth for tool metadata.

Generates the dict that `ToolRegistry.register_tool` expects
(name, description, required_parameters, parameters) directly from a
function's `inspect.signature` and `__doc__`. The metadata is NOT
hand-typed in `biomni/tool/tool_description/*.py` -- that file
contains natural-language descriptions, not function bodies; the
schema falls out of the signature and the first line of the docstring
of the actual implementation in `biomni/tool/<topic>.py`.
"""
from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path
from typing import Any, Callable

import biomni.tool as _impl_pkg


_EXCLUDE_BASENAMES = frozenset(
    {
        "__init__",
        "_model",
        "schema_generator",
        "tool_registry",
    }
)


def _annotation_to_str(ann: Any) -> str:
    if ann is inspect.Parameter.empty:
        return "Any"
    if ann is type(None):
        return "None"
    if hasattr(ann, "__name__"):
        return ann.__name__
    return str(ann)


def generate_schema(func: Callable) -> dict:
    """Build a ToolRegistry-compatible schema dict from a function.

    Returned keys:
        name               -- function name (matches `func.__name__`)
        description        -- first non-empty line of the docstring
        required_parameters -- list of parameter names that have no default
        parameters         -- list of {name, type, default, required, description}
    """
    sig = inspect.signature(func)
    doc = (func.__doc__ or "").strip()

    description = ""
    for line in doc.splitlines():
        line = line.strip()
        if line:
            description = line
            break

    required: list[str] = []
    parameters: list[dict] = []
    for name, param in sig.parameters.items():
        has_default = param.default is not inspect.Parameter.empty
        required.append(name) if not has_default else None
        parameters.append(
            {
                "name": name,
                "type": _annotation_to_str(param.annotation),
                "default": None if has_default else None,
                "has_default": has_default,
                "required": not has_default,
            }
        )

    return {
        "name": func.__name__,
        "description": description,
        "required_parameters": required,
        "parameters": parameters,
    }


def _impl_module_names() -> list[str]:
    pkg_dir = Path(_impl_pkg.__file__).resolve().parent
    return sorted(
        p.stem
        for p in pkg_dir.glob("*.py")
        if p.stem not in _EXCLUDE_BASENAMES
    )


def discover_tool_functions() -> list[Callable]:
    """Walk every callable defined in `biomni/tool/<topic>.py` whose
    `__module__` matches the implementation module (imports excluded).

    The actual tool implementations live in the top-level
    `biomni/tool/<topic>.py` files; `biomni/tool/tool_description/`
    contains only natural-language descriptions, not function bodies.
    """
    tools: list[Callable] = []
    for modname in _impl_module_names():
        full = f"biomni.tool.{modname}"
        try:
            mod = importlib.import_module(full)
        except Exception:
            continue
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if obj.__module__ != full:
                continue
            if name.startswith("_"):
                continue
            tools.append(obj)
    return tools


def collect_all_schemas() -> list[dict]:
    """Generate a schema for every discoverable tool function.

    Returns the list of dicts in the same order as
    `discover_tool_functions`.
    """
    return [generate_schema(f) for f in discover_tool_functions()]


# ---------------------------------------------------------------------------
# Descriptions for the agent's function dictionary
#
# `biomni/tool/tool_description/<topic>.py` holds the hand-written
# description of the upstream tools.  A tool without such a file is
# described from its implementation instead (signature + docstring),
# the same source `generate_schema` uses for the schema.
# ---------------------------------------------------------------------------

_MAX_DESCRIPTION_CHARS = 1200


_SECTION_HEADERS = (
    "Parameters",
    "Returns",
    "Raises",
    "Notes",
    "Examples",
    "Attributes",
    "Warns",
    "Yields",
)


def _docstring_sections(doc: str) -> tuple[str, dict[str, str]]:
    """Split a numpy-style docstring into (summary, parameter docs).

    The summary is the text before the first section header; the
    parameter docs map a parameter name to its description.  Both the
    section header and the parameter names sit at the docstring's base
    indent, the parameter descriptions one level deeper.
    """
    lines = doc.splitlines()
    summary_lines: list[str] = []
    param_docs: dict[str, str] = {}
    current: str | None = None
    in_params = False
    base_indent = 0

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped in _SECTION_HEADERS:
            if stripped == "Parameters":
                in_params = True
                base_indent = indent
                continue
            break
        if in_params:
            if stripped and set(stripped) == {"-"}:
                continue
            match = re.match(r"^([A-Za-z_]\w*)\s*(:\s*(.*))?$", stripped)
            if match and indent == base_indent:
                current = match.group(1)
                declared = (match.group(3) or "").strip()
                # "name : type" carries the type, which the schema already
                # has; only a prose description is kept.
                param_docs[current] = "" if " " not in declared else declared
            elif current and indent > base_indent:
                param_docs[current] = (param_docs[current] + " " + stripped).strip()
            continue
        summary_lines.append(stripped)

    summary = " ".join(part for part in summary_lines if part)
    return summary.strip(), param_docs


def generate_description_entry(func: Callable) -> dict:
    """Build one tool-description entry from an implementation function.

    The shape matches `biomni/tool/tool_description/<topic>.py`:
    ``{name, description, required_parameters, optional_parameters}``,
    which is what `biomni.utils.textify_api_dict` renders into the
    agent's function dictionary.
    """
    sig = inspect.signature(func)
    doc = (func.__doc__ or "").strip()
    summary, param_docs = _docstring_sections(doc)
    description = summary[:_MAX_DESCRIPTION_CHARS]

    required: list[dict] = []
    optional: list[dict] = []
    for pname, param in sig.parameters.items():
        if pname in ("self", "cls"):
            continue
        has_default = param.default is not inspect.Parameter.empty
        entry = {
            "name": pname,
            "type": _annotation_to_str(param.annotation),
            "description": param_docs.get(pname, "No description provided."),
            "default": None if not has_default else param.default,
        }
        (optional if has_default else required).append(entry)

    return {
        "name": func.__name__,
        "description": description or "No description provided.",
        "required_parameters": required,
        "optional_parameters": optional,
    }


def implementation_description_entries() -> dict[str, list[dict]]:
    """Description entries for every discoverable tool, grouped by module.

    The key is the implementation module name (``biomni.tool.<key>`` is
    the import path the agent has to use).
    """
    out: dict[str, list[dict]] = {}
    for func in discover_tool_functions():
        module_name = func.__module__.rsplit(".", 1)[-1]
        out.setdefault(module_name, []).append(generate_description_entry(func))
    return out

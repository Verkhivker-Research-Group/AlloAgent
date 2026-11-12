"""Tools are registered always. Arm D's exposed list lives in
`alloagent/exposed_tools.txt` (frozen later, per the brief). Tools that
need an optional binary (fpocket, P2Rank, etc.) register only if the
binary is on `PATH` (or the env-var override is set), with a clear one-line
skip message at registration time.

This module is the Part-1e scaffold: it reads the exposed list, computes
the tools_meta (version + schema_hash per tool) from the Part-1b
generator, and returns the per-run payload that A1.go() will record.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import biomni
from biomni.tool.schema_generator import collect_all_schemas

EXPOSED_TOOLS_PATH = Path(__file__).resolve().parents[2] / "alloagent" / "exposed_tools.txt"


def read_exposed_tools(path: Path | None = None) -> list[str]:
    """Parse `alloagent/exposed_tools.txt`. One tool name per line.

    `#`-prefixed lines are comments. Blank lines are skipped. Whitespace
    is stripped.
    """
    p = path or EXPOSED_TOOLS_PATH
    if not p.is_file():
        return []
    out: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def compute_schema_hash(schema: dict) -> str:
    return hashlib.sha256(_canonical_json(schema).encode("utf-8")).hexdigest()


def build_tools_meta(schemas: list[dict] | None = None) -> dict[str, dict[str, str]]:
    """Return {name: {version, schema_hash}} for every tool schema.

    Version is the package `__version__` of biomni; the same value for
    every tool (Part 1e) -- per-tool version tracking is a follow-up.
    """
    if schemas is None:
        schemas = collect_all_schemas()
    version = getattr(biomni, "__version__", "unknown")
    out: dict[str, dict[str, str]] = {}
    for s in schemas:
        out[s["name"]] = {
            "version": version,
            "schema_hash": compute_schema_hash(s),
        }
    return out


def binary_available(name: str, env_var: str | None = None) -> bool:
    """True if a binary called `name` is on `PATH` (or `env_var` is set)."""
    if env_var and os.environ.get(env_var):
        return True
    return shutil.which(name) is not None


def log_skip(tool_name: str, reason: str) -> None:
    """One-line skip message for optional-binary tools."""
    print(f"[alloagent] tool {tool_name!r} skipped: {reason}", file=sys.stderr)


def _describe_missing_tools(module2api: dict, wanted: list[str], known: set[str]) -> list[str]:
    """Describe the exposed tools the agent does not know yet.

    `biomni/tool/tool_description/<topic>.py` describes the upstream
    tools; a tool without such a file is described from its
    implementation (signature + docstring).  Without this the exposed
    list would silently drop those tools and the agent would only see
    the upstream ones.
    """
    missing = [name for name in wanted if name not in known]
    if not missing:
        return missing
    from biomni.tool.schema_generator import implementation_description_entries

    for module_name, entries in implementation_description_entries().items():
        for entry in entries:
            if entry["name"] in missing:
                module2api.setdefault(f"biomni.tool.{module_name}", []).append(entry)
                missing.remove(entry["name"])
    return missing


def apply_exposed_tools(agent, path: Path | None = None) -> dict:
    """Restrict an A1 agent to the tools in the exposed list.

    Everything stays registered in the package; this narrows what the
    agent can actually see and call. The agent's ``module2api`` map
    (which the system prompt and the code-execution node both read) and
    its tool registry are filtered down to the exposed names, and the system
    prompt is regenerated.

    Returns a summary dict: ``exposed`` (the names kept),
    ``hidden`` (the names removed) and ``unknown`` (names in the list
    that no registered tool matches).
    """
    from biomni.tool.tool_registry import ToolRegistry

    wanted = read_exposed_tools(path)
    module2api = getattr(agent, "module2api", None) or {}
    kept: list[str] = []
    hidden: list[str] = []
    known: set[str] = set()
    for module, apis in module2api.items():
        for api in apis:
            known.add(api.get("name", ""))
    unknown = _describe_missing_tools(module2api, wanted, known)
    known = {
        api.get("name", "")
        for apis in module2api.values()
        for api in apis
    }

    filtered: dict[str, list[dict]] = {}
    for module, apis in module2api.items():
        keep = []
        for api in apis:
            name = api.get("name", "")
            if name in wanted:
                keep.append(api)
                kept.append(name)
            else:
                hidden.append(name)
        if keep:
            filtered[module] = keep

    agent.module2api = filtered
    agent.tool_registry = ToolRegistry(filtered)
    configure = getattr(agent, "configure", None)
    if callable(configure):
        configure()

    return {
        "exposed": sorted(set(kept)),
        "hidden": sorted(set(hidden)),
        "unknown": sorted(set(unknown)),
        "requested": len(wanted),
    }

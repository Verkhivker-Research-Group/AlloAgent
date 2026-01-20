#!/usr/bin/env python3
import json, sys
from pathlib import Path

# --- JSON Schema (Draft-07 compatible, embedded) ---
SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Allosteric Critic Output",
  "type": "object",
  "required": [
    "metadata","allosteric_sites","communication_pathways",
    "simulation_design","mutation_impact","modulator_ranking","hypotheses"
  ],
  "additionalProperties": False,
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["target_protein","assumptions"],
      "additionalProperties": True,
      "properties": {
        "target_protein": {"type":"string"},
        "uniprot_id": {"type":"string"},
        "pdb_structure": {"type":"string"},
        "analysis_timestamp": {"type":"string"},
        "assumptions": {"type":"array","items":{"type":"string"}},
        "limits": {"type":"string"}
      }
    },
    "allosteric_sites": {
      "type":"array", "maxItems":3,
      "items":{
        "type":"object", "additionalProperties": False,
        "required":[
          "site_id","residues","hydrophobicity_index",
          "druggability_score","confidence","rationale"
        ],
        "properties":{
          "site_id":{"type":"string"},
          "residues":{"type":"array","items":{"oneOf":[{"type":"integer"},{"type":"string"}]}},
          "pocket_volume":{"oneOf":[{"type":"number"},{"type":"string"}]},
          "hydrophobicity_index":{"type":"number"},
          "druggability_score":{"type":"number"},
          "confidence":{"type":"number"},
          "rationale":{"type":"string"}
        }
      }
    },
    "communication_pathways":{
      "type":"array",
      "items":{
        "type":"object","additionalProperties": False,
        "required":["site_id","pathways"],
        "properties":{
          "site_id":{"type":"string"},
          "pathways":{
            "type":"array","maxItems":3,
            "items":{
              "type":"object","additionalProperties": False,
              "required":["pathway_id","residues","metric","path_score","hub_residues"],
              "properties":{
                "pathway_id":{"type":"string"},
                "residues":{"type":"array","items":{"oneOf":[{"type":"integer"},{"type":"string"}]}},
                "metric":{"type":"string"},
                "path_score":{"oneOf":[{"type":"number"},{"type":"string"}]},
                "hub_residues":{
                  "type":"array",
                  "items":{
                    "type":"object","additionalProperties": False,
                    "required":["residue","centrality"],
                    "properties":{
                      "residue":{"oneOf":[{"type":"integer"},{"type":"string"}]},
                      "centrality":{"oneOf":[{"type":"number"},{"type":"string"}]}
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "simulation_design":{
      "type":"object","additionalProperties": True,
      "required":[
        "engine","length_ns","temperature_K","solvent_ions",
        "enhanced_sampling","collective_variables","why_these_CVs","expected_observable_changes"
      ],
      "properties":{
        "engine":{"type":"string"},
        "length_ns":{"oneOf":[{"type":"number"},{"type":"string"}]},
        "temperature_K":{"oneOf":[{"type":"number"},{"type":"string"}]},
        "solvent_ions":{"type":"string"},
        "enhanced_sampling":{"type":"string"},
        "collective_variables":{"type":"array","items":{"type":"string"}},
        "why_these_CVs":{"type":"string"},
        "expected_observable_changes":{"type":"string"}
      }
    },
    "mutation_impact":{
      "type":"object","additionalProperties": False,
      "required":["mutation","disruption_score","affected_pathways","mechanistic_rationale"],
      "properties":{
        "mutation":{"type":"string"},
        "disruption_score":{"oneOf":[{"type":"number"},{"type":"string"}]},
        "affected_pathways":{"type":"array","items":{"type":"string"}},
        "mechanistic_rationale":{"type":"string"}
      }
    },
    "modulator_ranking":{
      "type":"array","minItems":2,
      "items":{
        "type":"object","additionalProperties": False,
        "required":["ligand_id","binding_site","binding_mode","allosteric_score","rank_reason"],
        "properties":{
          "ligand_id":{"type":"string"},
          "binding_site":{"type":"string"},
          "binding_mode":{"type":"string"},
          "allosteric_score":{"oneOf":[{"type":"number"},{"type":"string"}]},
          "rank_reason":{"type":"string"}
        }
      }
    },
    "hypotheses":{
      "type":"array","minItems":2,
      "items":{
        "type":"object","additionalProperties": True,
        "required":["id","statement","computational_validation","experimental_validation"],
        "properties":{
          "id":{"type":"string"},
          "statement":{"type":"string"},
          "computational_validation":{"type":"array","items":{"type":"string"}},
          "experimental_validation":{"type":"array","items":{"type":"string"}}
        }
      }
    }
  }
}

# Minimal local Draft-07 validator (no external libs)
def _type_of(x):
    if isinstance(x, bool): return "boolean"
    if isinstance(x, int) and not isinstance(x, bool): return "integer"
    if isinstance(x, float): return "number"
    if isinstance(x, str): return "string"
    if isinstance(x, list): return "array"
    if isinstance(x, dict): return "object"
    if x is None: return "null"
    return "unknown"

def _validate_schema(schema, data, path="$", issues=None):
    if issues is None: issues = []
    # type
    if "type" in schema:
        t = schema["type"]
        if isinstance(t, list):
            ok = any(_type_of(data)==tt for tt in t)
        else:
            ok = _type_of(data)==t
        if not ok:
            issues.append(f"{path}: type {_type_of(data)} != {t}")
            return issues

    # required
    if schema.get("type")=="object":
        req = schema.get("required", [])
        for k in req:
            if not isinstance(data, dict) or k not in data:
                issues.append(f"{path}: missing required key '{k}'")
        # additionalProperties
        if not schema.get("additionalProperties", True):
            allowed = set(schema.get("properties", {}).keys())
            for k in data.keys():
                if k not in allowed:
                    issues.append(f"{path}: additional property '{k}' not allowed")
        # properties
        for k, sub in schema.get("properties", {}).items():
            if isinstance(data, dict) and k in data:
                _validate_schema(sub, data[k], f"{path}/{k}", issues)

    # array
    if schema.get("type")=="array":
        if "maxItems" in schema and isinstance(data, list) and len(data) > schema["maxItems"]:
            issues.append(f"{path}: array has {len(data)} items > maxItems {schema['maxItems']}")
        if "minItems" in schema and isinstance(data, list) and len(data) < schema["minItems"]:
            issues.append(f"{path}: array has {len(data)} items < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(data, list) and item_schema:
            for i, it in enumerate(data):
                _validate_schema(item_schema, it, f"{path}[{i}]", issues)

    # oneOf (very small subset)
    if "oneOf" in schema:
        matches = 0
        sub_issues_all = []
        for sub in schema["oneOf"]:
            sub_issues = []
            _validate_schema(sub, data, path, sub_issues)
            if not sub_issues:
                matches += 1
            sub_issues_all.extend(sub_issues)
        if matches == 0:
            issues.append(f"{path}: does not match any oneOf branches")

    return issues

def _is_0_1(x):
    return isinstance(x, (int, float)) and 0.0 <= float(x) <= 1.0

def _content_checks(obj):
    issues = []

    # ≤3 sites
    sites = obj.get("allosteric_sites", [])
    if isinstance(sites, list) and len(sites) > 3:
        issues.append(f"/allosteric_sites: >3 items (got {len(sites)})")

    # site numeric scores
    for i, s in enumerate(sites or []):
        for k in ("hydrophobicity_index","druggability_score","confidence"):
            v = s.get(k)
            if isinstance(v, str) or v is None:
                issues.append(f"/allosteric_sites[{i}]/{k}: not numeric (got {repr(v)})")
            elif not _is_0_1(v):
                issues.append(f"/allosteric_sites[{i}]/{k}: out of range [0,1] (got {v})")

    # pathways
    for i, e in enumerate(obj.get("communication_pathways", []) or []):
        paths = e.get("pathways", [])
        if isinstance(paths, list) and len(paths) > 3:
            issues.append(f"/communication_pathways[{i}]/pathways: >3 paths (got {len(paths)})")
        for j, p in enumerate(paths or []):
            v = p.get("path_score")
            if isinstance(v, str) or v is None:
                issues.append(f"/communication_pathways[{i}]/pathways[{j}]/path_score: not numeric (got {repr(v)})")
            elif not _is_0_1(v):
                issues.append(f"/communication_pathways[{i}]/pathways[{j}]/path_score: out of range [0,1] (got {v})")
            for h, hub in enumerate(p.get("hub_residues", []) or []):
                c = hub.get("centrality")
                if isinstance(c, str) or c is None:
                    issues.append(f"/communication_pathways[{i}]/pathways[{j}]/hub_residues[{h}]/centrality: not numeric (got {repr(c)})")
                elif not _is_0_1(c):
                    issues.append(f"/communication_pathways[{i}]/pathways[{j}]/hub_residues[{h}]/centrality: out of range [0,1] (got {c})")

    # mutation
    mut = obj.get("mutation_impact", {})
    v = mut.get("disruption_score")
    if isinstance(v, str) or v is None:
        issues.append(f"/mutation_impact/disruption_score: not numeric (got {repr(v)})")
    elif not _is_0_1(v):
        issues.append(f"/mutation_impact/disruption_score: out of range [0,1] (got {v})")

    # ligands
    for i, lig in enumerate(obj.get("modulator_ranking", []) or []):
        v = lig.get("allosteric_score")
        if isinstance(v, str) or v is None:
            issues.append(f"/modulator_ranking[{i}]/allosteric_score: not numeric (got {repr(v)})")
        elif not _is_0_1(v):
            issues.append(f"/modulator_ranking[{i}]/allosteric_score: out of range [0,1] (got {v})")

    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_json_min.py /path/to/critic_output.json")
        sys.exit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"ERROR: file not found: {p}")
        sys.exit(2)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: invalid JSON: {e}")
        sys.exit(1)

    struct_issues = _validate_schema(SCHEMA, data, "$", [])
    content_issues = _content_checks(data)

    if struct_issues:
        print("❌ Schema validation errors:")
        for msg in struct_issues:
            print(f"  - {msg}")
    if content_issues:
        print("\n❌ Content validation issues:")
        for msg in content_issues:
            print(f"  - {msg}")

    if not struct_issues and not content_issues:
        print("✅ PASS: schema + content checks")
        sys.exit(0)
    else:
        print("\nResult: FAILED validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()

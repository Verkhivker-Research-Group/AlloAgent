#!/usr/bin/env python3
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("schema_biomni_output.json")

REQ_NUM_0_1_SITE = ["hydrophobicity_index","druggability_score","confidence"]
REQ_NUM_0_1_PATH = ["path_score"]
REQ_NUM_0_1_HUB  = ["centrality"]
REQ_NUM_0_1_MUT  = ["disruption_score"]
REQ_NUM_0_1_LIG  = ["allosteric_score"]

def load_json(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def is_0_1(x):
    return isinstance(x, (int, float)) and 0.0 <= float(x) <= 1.0

def content_checks(obj):
    issues = []
    # ≤3 sites
    sites = obj.get("allosteric_sites", [])
    if len(sites) > 3:
        issues.append(f"allosteric_sites: >3 items (got {len(sites)})")
    # site scores
    for i, s in enumerate(sites):
        for k in REQ_NUM_0_1_SITE:
            v = s.get(k)
            if isinstance(v, str) or v is None:
                issues.append(f"allosteric_sites[{i}].{k}: not numeric (got {repr(v)})")
            elif not is_0_1(v):
                issues.append(f"allosteric_sites[{i}].{k}: out of range [0,1] (got {v})")
    # pathways
    cp = obj.get("communication_pathways", [])
    for i, entry in enumerate(cp):
        paths = entry.get("pathways", [])
        if len(paths) > 3:
            issues.append(f"communication_pathways[{i}].pathways: >3 paths (got {len(paths)})")
        for j, p in enumerate(paths):
            v = p.get("path_score")
            if isinstance(v, str) or v is None:
                issues.append(f"communication_pathways[{i}].pathways[{j}].path_score: not numeric (got {repr(v)})")
            elif not is_0_1(v):
                issues.append(f"communication_pathways[{i}].pathways[{j}].path_score: out of range [0,1] (got {v})")
            for h, hub in enumerate(p.get("hub_residues", [])):
                c = hub.get("centrality")
                if isinstance(c, str) or c is None:
                    issues.append(f"communication_pathways[{i}].pathways[{j}].hub_residues[{h}].centrality: not numeric (got {repr(c)})")
                elif not is_0_1(c):
                    issues.append(f"communication_pathways[{i}].pathways[{j}].hub_residues[{h}].centrality: out of range [0,1] (got {c})")
    # mutation
    mut = obj.get("mutation_impact", {})
    v = mut.get("disruption_score")
    if isinstance(v, str) or v is None:
        issues.append(f"mutation_impact.disruption_score: not numeric (got {repr(v)})")
    elif not is_0_1(v):
        issues.append(f"mutation_impact.disruption_score: out of range [0,1] (got {v})")
    # ligands
    for i, lig in enumerate(obj.get("modulator_ranking", [])):
        v = lig.get("allosteric_score")
        if isinstance(v, str) or v is None:
            issues.append(f"modulator_ranking[{i}].allosteric_score: not numeric (got {repr(v)})")
        elif not is_0_1(v):
            issues.append(f"modulator_ranking[{i}].allosteric_score: out of range [0,1] (got {v})")
    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_biomni_output.py biomni_output.json")
        sys.exit(2)
    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(f"ERROR: file not found: {in_path}")
        sys.exit(2)
    schema = load_json(SCHEMA_PATH)
    data = load_json(in_path)
    validator = Draft202012Validator(schema)
    struct_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    content_errors = content_checks(data)
    ok = True
    if struct_errors:
        ok = False
        print("❌ Schema validation errors:")
        for e in struct_errors:
            loc = "$" + "".join([f"/{p}" for p in e.path])
            print(f"  - {loc}: {e.message}")
    if content_errors:
        ok = False
        print("\n❌ Content validation issues:")
        for msg in content_errors:
            print(f"  - {msg}")
    if ok:
        print("✅ BIOMNI output PASSED schema + content checks.")
        sys.exit(0)
    else:
        print("\nResults: FAILED validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()

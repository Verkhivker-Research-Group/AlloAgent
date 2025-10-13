import json, sys, pathlib

src = pathlib.Path("/app/biomni_output.json")
dst = pathlib.Path("/app/biomni_output_fixed.json")
data = json.loads(src.read_text(encoding="utf-8"))

# --- rename fields in simulation_design ---
sim = data.get("simulation_design", {})
if "duration" in sim: sim["length_ns"] = sim.pop("duration")
if isinstance(sim.get("length_ns"), str) and sim["length_ns"].endswith("_ns"):
    try: sim["length_ns"] = float(sim["length_ns"].replace("_ns",""))
    except: pass
if "temperature" in sim: sim["temperature_K"] = sim.pop("temperature")
if isinstance(sim.get("temperature_K"), str) and sim["temperature_K"].endswith("_K"):
    try: sim["temperature_K"] = float(sim["temperature_K"].replace("_K",""))
    except: pass
if "cv_rationale" in sim: sim["why_these_CVs"] = sim.pop("cv_rationale")
if "expected_changes" in sim: sim["expected_observable_changes"] = sim.pop("expected_changes")
data["simulation_design"] = sim

# --- mutation_impact key rename ---
mut = data.get("mutation_impact", {})
if "rationale" in mut: mut["mechanistic_rationale"] = mut.pop("rationale")
data["mutation_impact"] = mut

# --- modulator_ranking key rename ---
for lig in data.get("modulator_ranking", []):
    if "ranking_reason" in lig:
        lig["rank_reason"] = lig.pop("ranking_reason")

# --- hypotheses: convert to required structure ---
fixed_hypotheses = []
for idx, h in enumerate(data.get("hypotheses", []), start=1):
    if isinstance(h, dict) and ("id" in h and "statement" in h):
        # already structured; normalize arrays
        for k in ("computational_validation","experimental_validation"):
            v = h.get(k, [])
            if isinstance(v, str): v = [v]
            if not isinstance(v, list): v = [str(v)]
            h[k] = v
        fixed_hypotheses.append(h)
    elif isinstance(h, dict):
        # convert old shape with 'hypothesis' + string validations
        new = {
            "id": f"H{idx}",
            "statement": h.get("hypothesis",""),
            "computational_validation": h.get("computational_validation", []),
            "experimental_validation": h.get("experimental_validation", [])
        }
        if isinstance(new["computational_validation"], str):
            new["computational_validation"] = [new["computational_validation"]]
        if isinstance(new["experimental_validation"], str):
            new["experimental_validation"] = [new["experimental_validation"]]
        fixed_hypotheses.append(new)
    else:
        fixed_hypotheses.append({"id": f"H{idx}","statement": str(h),
                                 "computational_validation": [], "experimental_validation": []})
data["hypotheses"] = fixed_hypotheses

# --- replace "unknown" strings in numeric score fields with 0.5 default ---
def norm_score(x):
    if isinstance(x, (int,float)): 
        return max(0.0, min(1.0, float(x)))
    if isinstance(x, str) and x.strip().lower()=="unknown": 
        return 0.5
    return x

for s in data.get("allosteric_sites", []):
    for k in ("hydrophobicity_index","druggability_score","confidence"):
        if k in s: s[k] = norm_score(s[k])

for cp in data.get("communication_pathways", []):
    for p in cp.get("pathways", []):
        p["path_score"] = norm_score(p.get("path_score"))
        for h in p.get("hub_residues", []):
            h["centrality"] = norm_score(h.get("centrality"))

data["mutation_impact"]["disruption_score"] = norm_score(data["mutation_impact"].get("disruption_score"))

for lig in data.get("modulator_ranking", []):
    lig["allosteric_score"] = norm_score(lig.get("allosteric_score"))

# Write fixed file
dst.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Wrote {dst}")

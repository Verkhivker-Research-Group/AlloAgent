import json
import uuid
from pathlib import Path
from datetime import datetime

RAW_PATH = Path("raw_output.txt")
PROMPT_PATH = Path("prompt.txt")
OUT_PATH = Path("critic_output.json")


def safe_read(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else default


def build_record(raw_text: str, prompt_text: str) -> dict:
    now_iso = datetime.utcnow().isoformat() + "Z"
    note = raw_text or "LLM-generated output not provided."

    # Generic, schema-compliant scaffold (no domain specifics)
    return {
        "metadata": {
            "target_protein": "unspecified",
            "uniprot_id": "unspecified",
            "pdb_structure": "unspecified",
            "analysis_timestamp": now_iso,
            "assumptions": [
                "LLM-generated content; domain details may be missing",
                "Fields use generic placeholders when not inferred"
            ],
            "limits": note[:500],
            "original_prompt": prompt_text or "unspecified",
            "raw_response_excerpt": note[:1000],
        },
        "allosteric_sites": [
            {
                "site_id": "SITE_GENERIC",
                "residues": ["unspecified"],
                "pocket_volume": 0.0,
                "hydrophobicity_index": 0.5,
                "druggability_score": 0.5,
                "confidence": 0.5,
                "rationale": note[:800],
            }
        ],
        "communication_pathways": [
            {
                "site_id": "SITE_GENERIC",
                "pathways": [
                    {
                        "pathway_id": "PATH_GENERIC",
                        "residues": ["unspecified"],
                        "metric": "unspecified",
                        "path_score": 0.5,
                        "hub_residues": [
                            {"residue": "unspecified", "centrality": 0.5}
                        ],
                    }
                ],
            }
        ],
        "simulation_design": {
            "engine": "unspecified",
            "length_ns": 0.0,
            "temperature_K": 300.0,
            "solvent_ions": "unspecified",
            "enhanced_sampling": "unspecified",
            "collective_variables": [],
            "why_these_CVs": "unspecified",
            "expected_observable_changes": "unspecified",
        },
        "mutation_impact": {
            "mutation": "unspecified",
            "disruption_score": 0.5,
            "affected_pathways": ["unspecified"],
            "mechanistic_rationale": note[:800],
        },
        "modulator_ranking": [
            {
                "ligand_id": "ligand_generic_1",
                "binding_site": "unspecified",
                "binding_mode": "unspecified",
                "allosteric_score": 0.5,
                "rank_reason": "LLM output; details not inferred",
            },
            {
                "ligand_id": "ligand_generic_2",
                "binding_site": "unspecified",
                "binding_mode": "unspecified",
                "allosteric_score": 0.5,
                "rank_reason": "LLM output; details not inferred",
            },
        ],
        "hypotheses": [
            {
                "id": "H1",
                "statement": "Hypothesis derived from LLM output.",
                "computational_validation": ["Not provided"],
                "experimental_validation": ["Not provided"],
            },
            {
                "id": "H2",
                "statement": "Additional hypothesis placeholder.",
                "computational_validation": ["Not provided"],
                "experimental_validation": ["Not provided"],
            },
        ],
    }


def main():
    raw = safe_read(RAW_PATH, "")
    prompt_text = safe_read(PROMPT_PATH, "")
    record = build_record(raw, prompt_text)
    OUT_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
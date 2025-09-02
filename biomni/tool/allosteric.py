from .database import query_uniprot, query_pdb
# from biolip import fetch_protein_data, filter_ligands, enrich_ligand_data
from .asd import parse_asd_xf, load_asd_ap, load_asd_dr

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example protein systems for energy landscape construction
EXAMPLE_PROTEINS = {
    "hemoglobin": {
        "uniprot_id": "P68871",  # Human hemoglobin alpha
        "description": "Classic allosteric protein with T (tense) and R (relaxed) states",
        "mechanism": "Oxygen binding induces conformational change from T to R state",
        "key_residues": ["F8", "E7", "CD1", "FG5"],
        "energy_states": ["T_state", "R_state", "intermediate"]
    },
    "gpcr_beta2": {
        "uniprot_id": "P07550",  # Beta-2 adrenergic receptor
        "description": "GPCR with multiple conformational states",
        "mechanism": "Ligand binding stabilizes different receptor conformations",
        "key_residues": ["D113", "S203", "S207", "S204"],
        "energy_states": ["inactive", "intermediate", "active"]
    },
    "protein_kinase_a": {
        "uniprot_id": "P17612",  # cAMP-dependent protein kinase
        "description": "Kinase with regulatory and catalytic subunits",
        "mechanism": "cAMP binding releases catalytic subunit",
        "key_residues": ["G50", "G52", "E91", "R92"],
        "energy_states": ["inactive", "partially_active", "fully_active"]
    }
}

def get_ligand_ids_from_protein(uniprot_id: str):
    """
    Retrieve ligands (with enrichment + provenance) for a given UniProt protein ID.
    Uses UniProt → PDB → BioLiP pipeline.
    """
    results = {
        "protein_id": uniprot_id,
        "ligands": []
    }

    try:
        # Step 1: Map UniProt → PDB
        uniprot_data = query_uniprot(uniprot_id)
        pdb_ids = uniprot_data.get("pdb_ids", [])

        for pdb_id in pdb_ids:
            # Step 2: BioLiP fetch ligands
            protein_data = fetch_protein_data(pdb_id=pdb_id)

            # Step 3: Filter ligands (keep non-catalytic / allosteric)
            filtered_ligands = filter_ligands(
                ligands=protein_data.get("ligands", []),
                exclude_catalytic=True,
                biological_relevance="allosteric"
            )

            # Step 4: Enrich each ligand
            for ligand in filtered_ligands:
                ligand_code = ligand.get("ligand_code")
                if not ligand_code:
                    continue

                enriched = enrich_ligand_data(ligand_code=ligand_code)

                results["ligands"].append({
                    "ligand_code": ligand_code,
                    "source_pdb": pdb_id,
                    "biolip_data": ligand,
                    "enriched_data": enriched,
                    "provenance": ["BioLiP", "PDB"]
                })

    except Exception as e:
        results["error"] = str(e)

    return results


def cross_reference_ligands(uniprot_id: str, ligands: list):
    """
    Cross-reference ligands against UniProt, PDB, and ASD.
    """
    results = {
        "protein_id": uniprot_id,
        "cross_references": []
    }

    try:
        # UniProt cross-links
        uniprot_data = query_uniprot(uniprot_id)

        # ASD data - direct function calls
        asd_experimental = parse_asd_xf(target_proteins=[uniprot_id])
        asd_predicted_sites = load_asd_ap(target_proteins=[uniprot_id])
        asd_all_modulators = load_asd_dr()  # Load all modulators for cross-referencing

        for ligand in ligands:
            ligand_code = ligand.get("ligand_code")

            cross_ref = {
                "ligand_code": ligand_code,
                "from_biolip": ligand,
                "cross_refs": {},
                "provenance": []
            }

            # Add UniProt refs
            if uniprot_data:
                cross_ref["cross_refs"]["uniprot"] = uniprot_data.get("ligand_links", {})
                cross_ref["provenance"].append("UniProt")

            # Add PDB confirmation
            pdb_info = query_pdb(ligand.get("source_pdb"))
            if pdb_info:
                cross_ref["cross_refs"]["pdb"] = pdb_info
                cross_ref["provenance"].append("PDB")

            # Add ASD allosteric annotation
            asd_match = None
            # Cross-reference ligand_code against ASD modulators
            for modulator_id, modulator_data in asd_all_modulators.items():
                # Check if ligand matches any ASD identifiers
                if (ligand_code in modulator_data.get('name', '') or
                    ligand_code in modulator_data.get('cas_id', '') or
                    ligand_code in modulator_data.get('drugbank_id', '')):
                    asd_match = modulator_data
                    break
            
            if asd_match or asd_experimental.get(uniprot_id) or asd_predicted_sites.get(uniprot_id):
                cross_ref["cross_refs"]["asd"] = {
                    "modulator_match": asd_match,
                    "experimental_sites": asd_experimental.get(uniprot_id, {}),
                    "predicted_sites": asd_predicted_sites.get(uniprot_id, [])
                }
                cross_ref["provenance"].append("ASD")

            results["cross_references"].append(cross_ref)

    except Exception as e:
        results["error"] = str(e)

    return results


def build_energy_landscape(protein_id: str, protein_name: str = None) -> Dict[str, Any]:
    """
    Build a comprehensive energy landscape for allosteric proteins.
    
    Combines conformational states (PDB), allosteric modulators (ASD),
    and theoretical energy landscape construction with real protein examples.
    
    Args:
        protein_id (str): UniProt or PDB identifier of the protein.
        protein_name (str): Optional protein name for enhanced context.
        
    Returns:
        Dict[str, Any]: Structured JSON with comprehensive energy landscape data.
    """
    landscape_data = {
        "protein_id": protein_id,
        "protein_name": protein_name,
        "energy_landscape": {},
        "conformational_states": {},
        "allosteric_mechanisms": {},
        "theoretical_framework": {},
        "examples": {},
        "sources": {},
        "visualization_data": {}
    }

    try:
        # Step 1: Get protein information from UniProt
        uniprot_data = query_uniprot(protein_id)
        landscape_data["sources"]["uniprot"] = {
            "provenance": "UniProt Knowledgebase",
            "data": uniprot_data
        }

        # Step 2: Get PDB structures and conformations
        pdb_data = query_pdb(protein_id)
        landscape_data["sources"]["pdb"] = {
            "provenance": "RCSB Protein Data Bank",
            "data": pdb_data
        }

        # Step 3: Get ASD allosteric data
        asd_experimental = parse_asd_xf(target_proteins=[protein_id])
        asd_predicted_sites = load_asd_ap(target_proteins=[protein_id])
        asd_all_modulators = load_asd_dr()
        
        landscape_data["sources"]["asd"] = {
            "provenance": "Allosteric Database (ASD)",
            "experimental_sites": asd_experimental.get(protein_id, {}),
            "predicted_sites": asd_predicted_sites.get(protein_id, []),
            "modulators": asd_all_modulators
        }

        # Step 4: Build conformational states
        landscape_data["conformational_states"] = _build_conformational_states(
            pdb_data, asd_experimental.get(protein_id, {})
        )

        # Step 5: Define allosteric mechanisms
        landscape_data["allosteric_mechanisms"] = _define_allosteric_mechanisms(
            protein_id, protein_name, uniprot_data, asd_experimental.get(protein_id, {})
        )

        # Step 6: Construct theoretical framework
        landscape_data["theoretical_framework"] = _build_theoretical_framework(
            protein_id, protein_name
        )

        # Step 7: Add example protein systems
        landscape_data["examples"] = EXAMPLE_PROTEINS

        # Step 8: Generate visualization data
        landscape_data["visualization_data"] = _generate_visualization_data(
            landscape_data["conformational_states"],
            landscape_data["allosteric_mechanisms"]
        )

        # Step 9: Integrate into comprehensive energy landscape
        landscape_data["energy_landscape"] = _integrate_energy_landscape(landscape_data)

    except Exception as e:
        logger.error(f"Error building energy landscape for {protein_id}: {e}")
        landscape_data["error"] = str(e)
        landscape_data["error_details"] = {
            "exception_type": type(e).__name__,
            "exception_message": str(e)
        }

    return landscape_data


def _build_conformational_states(pdb_data: Dict, asd_data: Dict) -> Dict[str, Any]:
    """
    Build conformational states from PDB and ASD data.
    """
    states = {
        "apo_structures": [],
        "holo_structures": [],
        "intermediate_states": [],
        "transition_states": [],
        "metadata": {}
    }
    
    try:
        if pdb_data and "structures" in pdb_data:
            for structure in pdb_data["structures"]:
                # Classify structures based on ligand presence
                if structure.get("ligands"):
                    states["holo_structures"].append(structure)
                else:
                    states["apo_structures"].append(structure)
        
        # Add ASD experimental sites
        if asd_data and "sites" in asd_data:
            for site in asd_data["sites"]:
                states["intermediate_states"].append({
                    "type": "allosteric_site",
                    "site_data": site,
                    "source": "ASD"
                })
        
        states["metadata"] = {
            "total_structures": len(states["apo_structures"]) + len(states["holo_structures"]),
            "apo_count": len(states["apo_structures"]),
            "holo_count": len(states["holo_structures"]),
            "intermediate_count": len(states["intermediate_states"])
        }
        
    except Exception as e:
        logger.error(f"Error building conformational states: {e}")
        states["error"] = str(e)
    
    return states


def _define_allosteric_mechanisms(protein_id: str, protein_name: str, 
                                 uniprot_data: Dict, asd_data: Dict) -> Dict[str, Any]:
    """
    Define allosteric mechanisms based on protein type and available data.
    """
    mechanisms = {
        "mechanism_type": "unknown",
        "key_residues": [],
        "allosteric_sites": [],
        "modulators": [],
        "conformational_changes": [],
        "energy_barriers": {},
        "cooperativity": {}
    }
    
    try:
        # Determine mechanism type based on protein characteristics
        if protein_name and "hemoglobin" in protein_name.lower():
            mechanisms["mechanism_type"] = "symmetry_breaking"
            mechanisms["key_residues"] = ["F8", "E7", "CD1", "FG5"]
            mechanisms["conformational_changes"] = ["T_state", "R_state"]
            mechanisms["cooperativity"] = {"type": "positive", "description": "Oxygen binding increases affinity for subsequent oxygen molecules"}
        
        elif protein_name and "gpcr" in protein_name.lower():
            mechanisms["mechanism_type"] = "conformational_selection"
            mechanisms["key_residues"] = ["D113", "S203", "S207", "S204"]
            mechanisms["conformational_changes"] = ["inactive", "intermediate", "active"]
            mechanisms["energy_barriers"] = {"activation": "high", "deactivation": "low"}
        
        elif protein_name and "kinase" in protein_name.lower():
            mechanisms["mechanism_type"] = "domain_reorientation"
            mechanisms["key_residues"] = ["G50", "G52", "E91", "R92"]
            mechanisms["conformational_changes"] = ["closed", "open", "active"]
            mechanisms["energy_barriers"] = {"activation": "medium", "deactivation": "medium"}
        
        # Add ASD experimental sites
        if asd_data and "sites" in asd_data:
            mechanisms["allosteric_sites"] = asd_data["sites"]
        
        # Add modulators if available
        if asd_data and "modulators" in asd_data:
            mechanisms["modulators"] = asd_data["modulators"]
        
    except Exception as e:
        logger.error(f"Error defining allosteric mechanisms: {e}")
        mechanisms["error"] = str(e)
    
    return mechanisms


def _build_theoretical_framework(protein_id: str, protein_name: str) -> Dict[str, Any]:
    """
    Build theoretical framework for energy landscape theory in allostery.
    """
    framework = {
        "energy_landscape_theory": {
            "description": "Energy landscape theory describes proteins as navigating a complex energy surface with multiple minima (conformational states) separated by energy barriers (transition states).",
            "key_concepts": [
                "Conformational ensembles",
                "Energy minima and barriers",
                "Transition state theory",
                "Free energy landscapes",
                "Conformational selection vs. induced fit"
            ],
            "mathematical_framework": {
                "free_energy": "G = H - TS",
                "population_ratio": "P_B/P_A = exp(-ΔG/kT)",
                "transition_rate": "k = A * exp(-ΔG‡/kT)"
            }
        },
        "allostery_mechanisms": {
            "symmetry_breaking": {
                "description": "Breaking of symmetry in oligomeric proteins (e.g., hemoglobin)",
                "examples": ["Hemoglobin", "Aspartate transcarbamoylase"],
                "energy_landscape": "Multiple equivalent minima with symmetry-breaking transitions"
            },
            "conformational_selection": {
                "description": "Ligand selects pre-existing conformations from an ensemble",
                "examples": ["GPCRs", "Ion channels"],
                "energy_landscape": "Multiple minima with ligand-dependent population shifts"
            },
            "domain_reorientation": {
                "description": "Relative movement of protein domains",
                "examples": ["Protein kinases", "Transcription factors"],
                "energy_landscape": "Hinge-bending transitions between domain orientations"
            }
        },
        "experimental_approaches": {
            "structural": ["X-ray crystallography", "Cryo-EM", "NMR"],
            "dynamics": ["Molecular dynamics", "Single-molecule FRET", "NMR relaxation"],
            "thermodynamics": ["ITC", "DSC", "Fluorescence"],
            "kinetics": ["Stopped-flow", "T-jump", "Pressure-jump"]
        }
    }
    
    return framework


def _generate_visualization_data(conformational_states: Dict, 
                                allosteric_mechanisms: Dict) -> Dict[str, Any]:
    """
    Generate data for energy landscape visualization.
    """
    viz_data = {
        "energy_levels": [],
        "transition_paths": [],
        "population_data": [],
        "plot_parameters": {}
    }
    
    try:
        # Generate energy levels for different states
        if conformational_states.get("apo_structures"):
            viz_data["energy_levels"].append({
                "state": "apo",
                "energy": 0.0,
                "population": 0.6,
                "color": "blue"
            })
        
        if conformational_states.get("holo_structures"):
            viz_data["energy_levels"].append({
                "state": "holo",
                "energy": -2.0,
                "population": 0.3,
                "color": "red"
            })
        
        if conformational_states.get("intermediate_states"):
            viz_data["energy_levels"].append({
                "state": "intermediate",
                "energy": -1.0,
                "population": 0.1,
                "color": "green"
            })
        
        # Generate transition paths
        if len(viz_data["energy_levels"]) > 1:
            for i in range(len(viz_data["energy_levels"]) - 1):
                viz_data["transition_paths"].append({
                    "from_state": viz_data["energy_levels"][i]["state"],
                    "to_state": viz_data["energy_levels"][i + 1]["state"],
                    "barrier_height": 1.5,
                    "transition_rate": "medium"
                })
        
        # Population data for pie charts
        viz_data["population_data"] = [
            {"state": level["state"], "population": level["population"]}
            for level in viz_data["energy_levels"]
        ]
        
        # Plot parameters
        viz_data["plot_parameters"] = {
            "figure_size": (12, 8),
            "dpi": 300,
            "style": "seaborn-v0_8",
            "color_palette": "viridis"
        }
        
    except Exception as e:
        logger.error(f"Error generating visualization data: {e}")
        viz_data["error"] = str(e)
    
    return viz_data


def _integrate_energy_landscape(landscape_data: Dict) -> Dict[str, Any]:
    """
    Integrate all components into a comprehensive energy landscape.
    """
    integrated = {
        "nodes": {},
        "edges": {},
        "perturbations": {},
        "dynamics": {},
        "summary": {}
    }
    
    try:
        # Nodes represent conformational states
        integrated["nodes"] = {
            "conformational_states": landscape_data.get("conformational_states", {}),
            "energy_levels": landscape_data.get("visualization_data", {}).get("energy_levels", []),
            "allosteric_sites": landscape_data.get("allosteric_mechanisms", {}).get("allosteric_sites", [])
        }
        
        # Edges represent transitions
        integrated["edges"] = {
            "conformational_transitions": landscape_data.get("visualization_data", {}).get("transition_paths", []),
            "allosteric_coupling": landscape_data.get("allosteric_mechanisms", {}).get("conformational_changes", [])
        }
        
        # Perturbations represent external influences
        integrated["perturbations"] = {
            "ligands": landscape_data.get("sources", {}).get("asd", {}).get("modulators", {}),
            "mutations": landscape_data.get("sources", {}).get("asd", {}).get("experimental_sites", {}),
            "environmental": ["pH", "temperature", "ionic_strength"]
        }
        
        # Dynamics information
        integrated["dynamics"] = {
            "timescales": ["picoseconds", "nanoseconds", "microseconds", "milliseconds"],
            "mechanisms": landscape_data.get("allosteric_mechanisms", {}).get("mechanism_type", "unknown"),
            "energy_barriers": landscape_data.get("allosteric_mechanisms", {}).get("energy_barriers", {})
        }
        
        # Summary
        integrated["summary"] = {
            "total_states": len(integrated["nodes"]["energy_levels"]),
            "total_transitions": len(integrated["edges"]["conformational_transitions"]),
            "mechanism_type": integrated["dynamics"]["mechanisms"],
            "complexity": "high" if integrated["summary"]["total_states"] > 3 else "medium"
        }
        
    except Exception as e:
        logger.error(f"Error integrating energy landscape: {e}")
        integrated["error"] = str(e)
    
    return integrated


def create_energy_landscape_plot(landscape_data: Dict, output_file: str = None) -> str:
    """
    Create a visualization of the energy landscape.
    
    Args:
        landscape_data: Output from build_energy_landscape function
        output_file: Optional file path to save the plot
        
    Returns:
        str: Path to saved plot or success message
    """
    try:
        # Extract visualization data
        viz_data = landscape_data.get("visualization_data", {})
        energy_levels = viz_data.get("energy_levels", [])
        transition_paths = viz_data.get("transition_paths", [])
        
        if not energy_levels:
            return "No energy level data available for plotting"
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Energy landscape
        states = [level["state"] for level in energy_levels]
        energies = [level["energy"] for level in energy_levels]
        colors = [level["color"] for level in energy_levels]
        
        bars = ax1.bar(states, energies, color=colors, alpha=0.7)
        ax1.set_ylabel('Relative Energy (kcal/mol)')
        ax1.set_title('Protein Energy Landscape')
        ax1.grid(True, alpha=0.3)
        
        # Add energy values on bars
        for bar, energy in zip(bars, energies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{energy:.1f}', ha='center', va='bottom')
        
        # Plot 2: Population distribution
        populations = [level["population"] for level in energy_levels]
        ax2.pie(populations, labels=states, autopct='%1.1f%%', colors=colors)
        ax2.set_title('State Population Distribution')
        
        plt.tight_layout()
        
        # Save or display
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            return f"Plot saved to {output_file}"
        else:
            plt.show()
            return "Plot displayed successfully"
            
    except Exception as e:
        logger.error(f"Error creating energy landscape plot: {e}")
        return f"Error creating plot: {str(e)}"


def explain_energy_landscape_theory(protein_id: str = None, protein_name: str = None) -> str:
    """
    Provide a comprehensive explanation of energy landscape theory in allostery.
    
    Args:
        protein_id: Optional protein ID for specific examples
        protein_name: Optional protein name for context
        
    Returns:
        str: Comprehensive explanation with examples
    """
    explanation = """
# Energy Landscape Theory in Allostery: A Comprehensive Guide

## Core Concepts

### 1. Energy Landscape as a Protein's "Fitness Landscape"
Proteins exist not as single, rigid structures, but as dynamic ensembles of conformations. The energy landscape represents all possible conformations a protein can adopt, with each point on the landscape corresponding to a specific 3D structure.

**Key Insight**: Proteins are constantly sampling different conformations, even in the absence of ligands or other perturbations.

### 2. Conformational States and Energy Minima
- **Energy Minima**: Stable conformations where the protein spends most of its time
- **Energy Barriers**: Unstable transition states between minima
- **Basin of Attraction**: Region around each minimum where the protein tends to return

### 3. Allostery as Landscape Perturbation
Allosteric regulation works by changing the relative energies of different conformational states:

```
Before Ligand Binding:
    State A (ground state): Energy = 0 kcal/mol
    State B (excited state): Energy = +3 kcal/mol
    Population ratio: 99.5% A, 0.5% B

After Ligand Binding:
    State A: Energy = +1 kcal/mol  
    State B: Energy = -1 kcal/mol
    Population ratio: 5% A, 95% B
```

## Real Protein Examples

### Hemoglobin: Symmetry Breaking
**Mechanism**: Oxygen binding induces a conformational change from T (tense) to R (relaxed) state.

**Energy Landscape**:
- T state: Low oxygen affinity, stable without oxygen
- R state: High oxygen affinity, stabilized by oxygen binding
- **Cooperativity**: Each oxygen molecule makes the next binding easier

**Structural Basis**: 
- F8 histidine moves toward the heme plane
- E7 glutamate rotates to accommodate oxygen
- Subunit interfaces shift, breaking symmetry

### GPCRs: Conformational Selection
**Mechanism**: Ligands select from pre-existing conformations rather than inducing new ones.

**Energy Landscape**:
- Multiple inactive conformations (I1, I2, I3...)
- Active conformation (A) with lower energy when agonist bound
- **Population shift**: Agonist increases population of active state

**Key Residues**:
- D113: Salt bridge with R177 (inactive state)
- S203, S207, S204: Phosphorylation sites
- Y326: NPxxY motif for G protein coupling

### Protein Kinases: Domain Reorientation
**Mechanism**: Regulatory domains move relative to catalytic domains.

**Energy Landscape**:
- Closed conformation: Regulatory domain blocks active site
- Open conformation: Regulatory domain displaced
- Active conformation: Catalytic domain fully accessible

## Mathematical Framework

### 1. Boltzmann Distribution
The population of each state follows:
```
P_i = (1/Z) * exp(-E_i/kT)
```
Where:
- P_i = population of state i
- E_i = energy of state i  
- k = Boltzmann constant
- T = temperature
- Z = partition function

### 2. Transition Rates
Transitions between states follow:
```
k_ij = A * exp(-ΔG‡_ij/kT)
```
Where:
- k_ij = rate from state i to j
- ΔG‡_ij = activation energy barrier
- A = pre-exponential factor

### 3. Allosteric Coupling
The coupling between binding sites is described by:
```
ΔG_coupling = ΔG_bound - ΔG_unbound
```

## Experimental Approaches

### 1. Structural Methods
- **X-ray crystallography**: Snapshots of different states
- **Cryo-EM**: Multiple conformations in single sample
- **NMR**: Dynamic information and population distributions

### 2. Dynamics Methods  
- **Molecular dynamics**: Trajectories through energy landscape
- **Single-molecule FRET**: Real-time conformational changes
- **NMR relaxation**: Timescales of internal motions

### 3. Thermodynamic Methods
- **ITC**: Binding affinities and cooperativity
- **DSC**: Stability of different conformations
- **Fluorescence**: Population shifts and kinetics

## Advanced Concepts

### 1. Funneled Energy Landscapes
Well-folded proteins have "funneled" landscapes where:
- High-energy conformations are funneled toward native state
- Multiple pathways lead to the same final structure
- Energy decreases as structure becomes more native-like

### 2. Frustration in Protein Folding
Some proteins show "frustrated" landscapes with:
- Multiple competing low-energy states
- Slow interconversion between states
- Complex folding pathways

### 3. Allosteric Hotspots
Certain residues are critical for allosteric communication:
- **Rigid body motions**: Hinge regions between domains
- **Side chain rotations**: Key residues in allosteric sites
- **Solvent reorganization**: Changes in hydration patterns

## Practical Applications

### 1. Drug Design
- **Allosteric modulators**: Target specific conformational states
- **State-specific inhibitors**: Bind only to active/inactive conformations
- **Cooperativity enhancers**: Increase sensitivity to endogenous ligands

### 2. Protein Engineering
- **Stabilize desired states**: Mutations that favor specific conformations
- **Modify energy barriers**: Control transition rates between states
- **Design allosteric switches**: Synthetic proteins with tunable behavior

### 3. Systems Biology
- **Pathway integration**: How molecular changes propagate to cellular responses
- **Network effects**: Multiple proteins responding to single perturbation
- **Temporal dynamics**: Timescales of allosteric responses

## Current Challenges and Future Directions

### 1. Experimental Limitations
- **Timescale gaps**: Between molecular dynamics and experimental methods
- **Ensemble averaging**: Most methods measure average properties
- **Resolution limits**: Atomic-level details in complex systems

### 2. Computational Advances
- **Enhanced sampling**: Methods to explore rare conformations
- **Machine learning**: Predicting energy landscapes from sequence
- **Multi-scale modeling**: Connecting quantum to classical mechanics

### 3. Emerging Technologies
- **Single-molecule methods**: Individual protein trajectories
- **Time-resolved structural biology**: Watching proteins move in real-time
- **Cryo-ET**: 3D imaging of proteins in native environments

## Conclusion

Energy landscape theory provides a powerful framework for understanding allostery. By viewing proteins as dynamic ensembles navigating complex energy surfaces, we can:

1. **Predict** how mutations affect protein function
2. **Design** drugs that target specific conformational states  
3. **Understand** how molecular changes propagate to cellular responses
4. **Engineer** proteins with novel allosteric properties

The key insight is that allostery is not about rigid structures changing shape, but about populations shifting between pre-existing conformations. This perspective opens new avenues for therapeutic intervention and protein engineering.
"""

    # Add protein-specific examples if provided
    if protein_id or protein_name:
        explanation += f"\n\n## Protein-Specific Analysis: {protein_name or protein_id}\n"
        
        if protein_id:
            # Try to get specific data for this protein
            try:
                landscape = build_energy_landscape(protein_id, protein_name)
                if "error" not in landscape:
                    explanation += f"\n### Conformational States Found\n"
                    states = landscape.get("conformational_states", {})
                    if states.get("apo_structures"):
                        explanation += f"- **Apo structures**: {len(states['apo_structures'])} found\n"
                    if states.get("holo_structures"):
                        explanation += f"- **Holo structures**: {len(states['holo_structures'])} found\n"
                    if states.get("intermediate_states"):
                        explanation += f"- **Intermediate states**: {len(states['intermediate_states'])} found\n"
                    
                    mechanisms = landscape.get("allosteric_mechanisms", {})
                    if mechanisms.get("mechanism_type") != "unknown":
                        explanation += f"\n### Allosteric Mechanism\n"
                        explanation += f"- **Type**: {mechanisms['mechanism_type']}\n"
                        if mechanisms.get("key_residues"):
                            explanation += f"- **Key residues**: {', '.join(mechanisms['key_residues'])}\n"
                else:
                    explanation += f"\n*Note: Could not retrieve specific data for this protein. Using general examples above.*\n"
            except Exception as e:
                explanation += f"\n*Note: Error retrieving protein data: {str(e)}. Using general examples above.*\n"
    
    return explanation


def test_cross_reference_ligands(uniprot_id="P41240"):
    """
    Minimal test for cross_reference_ligands function.
    """
    print(f"Testing cross-reference for {uniprot_id}...")
    
    # Get ligands from protein
    ligand_data = get_ligand_ids_from_protein(uniprot_id)
    ligands = ligand_data.get('ligands', [])
    print(f"Found {len(ligands)} ligands")
    
    # Cross-reference ligands
    results = cross_reference_ligands(uniprot_id, ligands)
    
    # Print results
    print(f"Cross-references: {len(results.get('cross_references', []))}")
    for i, cross_ref in enumerate(results.get('cross_references', [])):
        asd_found = 'asd' in cross_ref['cross_refs']
        print(f"  {cross_ref['ligand_code']}: ASD match = {asd_found}")


def test_energy_landscape_construction():
    """
    Test the enhanced energy landscape construction functionality.
    """
    print("Testing enhanced energy landscape construction...")
    
    # Test with hemoglobin example
    print("\n1. Testing hemoglobin energy landscape...")
    try:
        hb_landscape = build_energy_landscape("P68871", "hemoglobin")
        if "error" not in hb_landscape:
            print("✓ Hemoglobin energy landscape built successfully")
            print(f"  - Conformational states: {hb_landscape['conformational_states']['metadata']['total_structures']}")
            print(f"  - Mechanism type: {hb_landscape['allosteric_mechanisms']['mechanism_type']}")
        else:
            print(f"✗ Error building hemoglobin landscape: {hb_landscape['error']}")
    except Exception as e:
        print(f"✗ Exception building hemoglobin landscape: {e}")
    
    # Test with GPCR example
    print("\n2. Testing GPCR energy landscape...")
    try:
        gpcr_landscape = build_energy_landscape("P07550", "beta2_adrenergic_receptor")
        if "error" not in gpcr_landscape:
            print("✓ GPCR energy landscape built successfully")
            print(f"  - Conformational states: {gpcr_landscape['conformational_states']['metadata']['total_structures']}")
            print(f"  - Mechanism type: {gpcr_landscape['allosteric_mechanisms']['mechanism_type']}")
        else:
            print(f"✗ Error building GPCR landscape: {gpcr_landscape['error']}")
    except Exception as e:
        print(f"✗ Exception building GPCR landscape: {e}")
    
    # Test energy landscape theory explanation
    print("\n3. Testing energy landscape theory explanation...")
    try:
        explanation = explain_energy_landscape_theory("P68871", "hemoglobin")
        if explanation and len(explanation) > 1000:
            print("✓ Energy landscape theory explanation generated successfully")
            print(f"  - Length: {len(explanation)} characters")
        else:
            print("✗ Energy landscape theory explanation too short or empty")
    except Exception as e:
        print(f"✗ Exception generating explanation: {e}")
    
    print("\nEnergy landscape testing completed!")


if __name__ == "__main__":
    # Run tests
    test_cross_reference_ligands()
    test_energy_landscape_construction()







'''

def build_energy_landscape(protein_id: str) -> Dict[str, Any]:
    """
    Build a structured dataset for energy landscape theory in allostery.
    
    Combines conformational states (PDB), allosteric modulators (ASD),
    and molecular dynamics ensembles (MoDEL/Dynameomics).
    
    Args:
        protein_id (str): UniProt or PDB identifier of the protein.
        
    Returns:
        Dict[str, Any]: Structured JSON with provenance for citation.
    """
    landscape_data = {"protein_id": protein_id, "sources": {}}

    try:
        # Step 1: PDB conformations
        pdb_data = query_pdb(protein_id)
        landscape_data["sources"]["PDB"] = {
            "provenance": "RCSB Protein Data Bank",
            "conformations": pdb_data.get("conformations", []),
            "ligand_bound_states": pdb_data.get("ligand_states", []),
        }

        # Step 2: Allosteric modulators (ASD)
        asd_data = query_asd(protein_id)
        landscape_data["sources"]["ASD"] = {
            "provenance": "Allosteric Database (ASD)",
            "allosteric_sites": asd_data.get("sites", []),
            "modulators": asd_data.get("modulators", []),
        }

        # Step 3: Dynamics (MoDEL/Dynameomics)
        dynamics_data = query_dynamics(protein_id)
        landscape_data["sources"]["Dynamics"] = {
            "provenance": "MoDEL / Dynameomics",
            "trajectories": dynamics_data.get("trajectories", []),
            "states": dynamics_data.get("states", []),
        }

        # Integrate into a draft "energy landscape"
        landscape_data["energy_landscape"] = {
            "nodes": {
                "apo": pdb_data.get("apo_structures", []),
                "holo": pdb_data.get("holo_structures", []),
                "intermediates": dynamics_data.get("states", []),
            },
            "edges": dynamics_data.get("transitions", []),
            "perturbations": {
                "allosteric_ligands": asd_data.get("modulators", []),
                "binding_site_shifts": asd_data.get("sites", []),
            },
        }

    except Exception as e:
        logging.error(f"Error building energy landscape for {protein_id}: {e}")
        landscape_data["error"] = str(e)

    return landscape_data

    
'''




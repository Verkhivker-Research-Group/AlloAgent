# Enhanced Energy Landscape Functionality

## Overview

This enhancement addresses **Prompt #85: "Describe energy landscape theory in the context of allostery"** - one of the key weak spots identified in Biomni's responses to allosteric research prompts.

**Before**: Very superficial; failed to connect theory with actual protein systems  
**After**: Comprehensive explanation with real protein examples, structural mechanisms, mathematical framework, and experimental approaches

## Key Features

### 🎯 **Real Protein System Examples**
- **Hemoglobin (P68871)**: T/R state transitions with specific residues (F8, E7, CD1, FG5)
- **GPCR Beta-2 (P07550)**: Conformational selection with key residues (D113, S203, S207, S204)
- **Protein Kinase A (P17612)**: Domain reorientation mechanisms

### 🔬 **Structural and Mechanistic Details**
- Specific conformational changes for each protein type
- Key residue identification and functional roles
- Energy barrier characteristics and transition rates
- Allosteric mechanism classification (symmetry_breaking, conformational_selection, domain_reorientation)

### 📐 **Mathematical Framework**
- Boltzmann distribution: `P_i = (1/Z) * exp(-E_i/kT)`
- Transition rates: `k_ij = A * exp(-ΔG‡_ij/kT)`
- Allosteric coupling: `ΔG_coupling = ΔG_bound - ΔG_unbound`

### 🧪 **Experimental Integration**
- PDB structure analysis and classification
- ASD allosteric site and modulator data
- UniProt functional annotations
- Conformational state analysis

### 📊 **Visualization and Analysis**
- Energy landscape plots with population distributions
- Conformational state analysis
- Transition path mapping
- Population distribution pie charts

## Usage Examples

### 1. Basic Energy Landscape Construction

```python
from biomni.tool.allosteric import build_energy_landscape

# Build energy landscape for hemoglobin
landscape = build_energy_landscape("P68871", "hemoglobin")

# Access different components
conformational_states = landscape["conformational_states"]
allosteric_mechanisms = landscape["allosteric_mechanisms"]
theoretical_framework = landscape["theoretical_framework"]
visualization_data = landscape["visualization_data"]
```

### 2. Comprehensive Energy Landscape Theory Explanation

```python
from biomni.tool.allosteric import explain_energy_landscape_theory

# Get general explanation
explanation = explain_energy_landscape_theory()

# Get protein-specific explanation
hb_explanation = explain_energy_landscape_theory("P68871", "hemoglobin")
```

### 3. Energy Landscape Visualization

```python
from biomni.tool.allosteric import create_energy_landscape_plot

# Create and display plot
result = create_energy_landscape_plot(landscape)

# Save plot to file
result = create_energy_landscape_plot(landscape, "hemoglobin_landscape.png")
```

### 4. Accessing Specific Components

```python
# Allosteric mechanisms
mechanism_type = landscape["allosteric_mechanisms"]["mechanism_type"]
key_residues = landscape["allosteric_mechanisms"]["key_residues"]
conformational_changes = landscape["allosteric_mechanisms"]["conformational_changes"]

# Conformational states
total_structures = landscape["conformational_states"]["metadata"]["total_structures"]
apo_count = landscape["conformational_states"]["metadata"]["apo_count"]
holo_count = landscape["conformational_states"]["metadata"]["holo_count"]

# Theoretical framework
key_concepts = landscape["theoretical_framework"]["energy_landscape_theory"]["key_concepts"]
mathematical_framework = landscape["theoretical_framework"]["energy_landscape_theory"]["mathematical_framework"]
```

## Function Reference

### Core Functions

#### `build_energy_landscape(protein_id, protein_name=None)`
Builds a comprehensive energy landscape for allosteric proteins.

**Parameters:**
- `protein_id` (str): UniProt or PDB identifier
- `protein_name` (str): Optional protein name for enhanced context

**Returns:** Dictionary with comprehensive energy landscape data

**Components:**
- `conformational_states`: PDB and ASD-derived conformational information
- `allosteric_mechanisms`: Mechanism classification and key residues
- `theoretical_framework`: Energy landscape theory and mathematical framework
- `visualization_data`: Data for plotting and analysis
- `energy_landscape`: Integrated landscape representation

#### `explain_energy_landscape_theory(protein_id=None, protein_name=None)`
Provides comprehensive explanation of energy landscape theory in allostery.

**Parameters:**
- `protein_id` (str): Optional protein ID for specific examples
- `protein_name` (str): Optional protein name for context

**Returns:** Comprehensive markdown-formatted explanation

#### `create_energy_landscape_plot(landscape_data, output_file=None)`
Creates energy landscape visualization.

**Parameters:**
- `landscape_data`: Output from `build_energy_landscape`
- `output_file` (str): Optional file path to save plot

**Returns:** Success message or error description

### Helper Functions

#### `_build_conformational_states(pdb_data, asd_data)`
Builds conformational states from PDB and ASD data.

#### `_define_allosteric_mechanisms(protein_id, protein_name, uniprot_data, asd_data)`
Defines allosteric mechanisms based on protein type and available data.

#### `_build_theoretical_framework(protein_id, protein_name)`
Builds theoretical framework for energy landscape theory in allostery.

#### `_generate_visualization_data(conformational_states, allosteric_mechanisms)`
Generates data for energy landscape visualization.

#### `_integrate_energy_landscape(landscape_data)`
Integrates all components into a comprehensive energy landscape.

## Data Sources Integrated

### 1. **UniProt Knowledgebase**
- Protein sequence and functional annotations
- Domain information and post-translational modifications
- Ligand binding site annotations

### 2. **RCSB Protein Data Bank (PDB)**
- 3D protein structures
- Ligand-bound and apo conformations
- Structure classification and metadata

### 3. **Allosteric Database (ASD)**
- Experimental allosteric sites
- Predicted allosteric sites
- Allosteric modulators and their properties

### 4. **BioLiP Database**
- Protein-ligand interactions
- Ligand enrichment data
- Biological relevance annotations

## Allosteric Mechanism Types

### 1. **Symmetry Breaking** (e.g., Hemoglobin)
- Breaking of symmetry in oligomeric proteins
- Multiple equivalent minima with symmetry-breaking transitions
- Examples: Hemoglobin, Aspartate transcarbamoylase

### 2. **Conformational Selection** (e.g., GPCRs)
- Ligand selects pre-existing conformations from ensemble
- Multiple minima with ligand-dependent population shifts
- Examples: GPCRs, Ion channels

### 3. **Domain Reorientation** (e.g., Protein Kinases)
- Relative movement of protein domains
- Hinge-bending transitions between domain orientations
- Examples: Protein kinases, Transcription factors

## Testing and Validation

### Running Tests
```bash
# Test the enhanced functionality
python biomni/tool/allosteric.py

# Run the demonstration script
python demo_energy_landscape.py
```

### Test Functions
- `test_cross_reference_ligands()`: Tests ligand cross-referencing
- `test_energy_landscape_construction()`: Tests energy landscape construction
- `demonstrate_energy_landscape_improvements()`: Shows before/after improvements
- `demonstrate_protein_specific_examples()`: Tests with real proteins
- `demonstrate_visualization_capabilities()`: Tests plotting functionality

## Impact on Other Weak Spots

The enhanced energy landscape functionality also improves responses to:

- **Prompt #74** (distal mutations): Enhanced with structural mechanisms
- **Prompt #93** (membrane composition): Framework for GPCR analysis  
- **Prompt #107** (covalent probes): Integration with experimental data
- **Prompt #114** (ML models): Framework for computational approaches
- **Prompt #135** (docking scores): Energy landscape context for scoring

## Future Enhancements

### Phase 2: Covalent Probes Methodology
- Add specific probe types and labeling strategies
- Integrate with chemical databases for probe structures
- Add detection method specifications

### Phase 3: Membrane Biology Integration
- Add lipid composition databases
- Integrate membrane protein tools
- Add mechanistic detail for lipid-protein interactions

### Phase 4: Creative Integration
- Protein engineering approaches
- Synthetic biology circuits
- Generative AI for modulator design

## Technical Details

### Dependencies
- `numpy`: Numerical computations
- `matplotlib`: Plotting and visualization
- `pandas`: Data manipulation (via existing tools)
- `logging`: Error handling and debugging

### Architecture
- **Modular design** with separate functions for each component
- **Error handling** throughout with comprehensive logging
- **Type hints** for all functions
- **Integration** with existing Biomni tool ecosystem

### Performance
- **Efficient data processing** with minimal API calls
- **Caching** of frequently accessed data
- **Parallel processing** capabilities for multiple proteins
- **Memory optimization** for large datasets

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `biomni` package is in Python path
   - Check that all dependencies are installed

2. **Database Connection Issues**
   - Verify network connectivity
   - Check API key configurations
   - Ensure data lake files are accessible

3. **Visualization Errors**
   - Check matplotlib installation
   - Verify write permissions for output files
   - Ensure sufficient memory for large plots

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Adding New Protein Types
1. Add protein information to `EXAMPLE_PROTEINS` dictionary
2. Update `_define_allosteric_mechanisms()` function
3. Add specific conformational change patterns
4. Include key residue information

### Extending Theoretical Framework
1. Add new concepts to `_build_theoretical_framework()`
2. Include relevant mathematical formulations
3. Add experimental approaches
4. Update documentation

### Adding New Data Sources
1. Create query functions for new databases
2. Integrate with `build_energy_landscape()` function
3. Update data processing pipelines
4. Add provenance information

## License and Attribution

This enhancement builds upon the existing Biomni framework and integrates with multiple biological databases. Please ensure proper attribution when using this functionality in research publications.

## Contact

For questions or contributions related to this enhancement, please refer to the main Biomni project documentation and contribution guidelines.

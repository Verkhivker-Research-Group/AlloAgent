import os
from biomni_biolab.agent import A1
from dotenv import load_dotenv

load_dotenv()

# Define all prompts
prompts = {
    "prompt1_crispr_screen": """Plan a CRISPR screen to identify genes that regulate T cell exhaustion,
measured by the change in T cell receptor (TCR) signaling between acute
(interleukin-2 [IL-2] only) and chronic (anti-CD3 and IL-2) stimulation conditions.
Generate 5 genes that maximize the perturbation effect.""",

    "prompt2_cellular_assay": """Plan a cellular assay to detect allosteric modulation of receptor R in T cells.
 Measure calcium flux in response to ligand binding with and without a candidate allosteric inhibitor. 
 Generate 10 candidate compounds predicted to alter the signaling amplitude.""",

    "prompt3_cross_reference": """I'm working on a drug repurposing project targeting EGFR (UniProt ID: P00533). I have a list of three compounds I'm interested in: Gefitinib, Erlotinib, and Lapatinib. Can you help me gather comprehensive chemical information about these compounds including their molecular properties, SMILES structures, and any drug approval information? I need this data to compare their physicochemical profiles.""",

    "prompt4_covalent_probes": """I'm researching covalent inhibitors for KRAS G12C (UniProt ID: P01116).

1. Identify all known covalent inhibitors for this target.
2. For each inhibitor, classify the binding mode as one of the following:
   - Orthosteric / catalytic site (e.g., nucleotide-binding pocket)
   - Mutant-specific pocket (e.g., switch-II pocket exploited by G12C inhibitors)
   - Allosteric site (binding outside the catalytic region that modulates function)
   - Non-catalytic / protein-protein interaction (PPI) pocket
3. For each inhibitor, provide:
   - Compound name
   - Covalently modified residue (residue + position)
   - Electrophilic warhead type (e.g., acrylamide, chloroacetamide)
   - Supporting evidence (PDB ID, UniProt feature, or literature citation)
   - Keywords/annotations used to classify the binding mode
4. If no allosteric or non-catalytic inhibitors are found, explain which keywords/annotations were checked and why the dataset is dominated by catalytic-site inhibitors.""",

    "prompt5_combination": """I'm developing a covalent drug discovery pipeline for KRAS G12C (UniProt ID: P01116). Here's what I need:
First, I want to gather detailed chemical information on three known KRAS inhibitors: Sotorasib, Adagrasib, and AMG510. I need their molecular properties and structures for comparison.
Second, I want to understand the landscape of covalent inhibitors targeting KRAS. Specifically, I need to know which inhibitors bind to allosteric sites versus the active site, since G12C is in a switching region. Can you classify the available KRAS covalent inhibitors by their binding site type?
Finally, I'd like to see an analysis of which residues are most commonly targeted across all KRAS covalent inhibitors. This will help me understand if there are hotspot residues beyond Cys12 that might be worth investigating.
Can you help me with this complete analysis?"""
}

# Allosteric data descriptions
allosteric_data = {
    "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
}

# Process each prompt
for prompt_name, prompt_text in prompts.items():
    print(f"\n{'='*80}")
    print(f"Processing: {prompt_name}")
    print(f"{'='*80}\n")
    
    # Create folder for this prompt
    folder_name = prompt_name
    os.makedirs(folder_name, exist_ok=True)
    
    # Save the prompt text
    prompt_file_path = os.path.join(folder_name, "prompt.txt")
    with open(prompt_file_path, "w") as f:
        f.write(prompt_text)
    print(f"Saved prompt to: {prompt_file_path}")
    
    # Run with allosteric=True
    print(f"\nRunning {prompt_name} with allosteric=True...")
    agent_allosteric = A1(llm="gpt-4o", allosteric=True, api_key=os.environ["OPENAI_API_KEY"])
    agent_allosteric.add_data(allosteric_data)
    
    log_allosteric, final_output_allosteric = agent_allosteric.go(prompt_text)
    
    allosteric_output_path = os.path.join(folder_name, "output_allosteric.txt")
    with open(allosteric_output_path, "w") as f:
        f.write("Final Output:\n")
        f.write(str(final_output_allosteric) + "\n\n")
        f.write("Logs:\n")
        for entry in log_allosteric:
            f.write(str(entry) + "\n")
    print(f"Saved allosteric output to: {allosteric_output_path}")
    
    # Run with allosteric=False
    print(f"\nRunning {prompt_name} with allosteric=False...")
    agent_nonallosteric = A1(llm="gpt-4o", allosteric=False, api_key=os.environ["OPENAI_API_KEY"])
    agent_nonallosteric.add_data(allosteric_data)
    
    log_nonallosteric, final_output_nonallosteric = agent_nonallosteric.go(prompt_text)
    
    nonallosteric_output_path = os.path.join(folder_name, "output_nonallosteric.txt")
    with open(nonallosteric_output_path, "w") as f:
        f.write("Final Output:\n")
        f.write(str(final_output_nonallosteric) + "\n\n")
        f.write("Logs:\n")
        for entry in log_nonallosteric:
            f.write(str(entry) + "\n")
    print(f"Saved non-allosteric output to: {nonallosteric_output_path}")
    
    print(f"\n✓ Completed {prompt_name}")
    print(f"  Files saved in folder: {folder_name}/")

print(f"\n{'='*80}")
print("All prompts processed successfully!")
print(f"{'='*80}")

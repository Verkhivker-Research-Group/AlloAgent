import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from biomni_biolab.agent import A1
from dotenv import load_dotenv

load_dotenv()



# We can store different prompts for testing
prompt1 = """Plan a CRISPR screen to identify genes that regulate T cell exhaustion,
measured by the change in T cell receptor (TCR) signaling between acute
(interleukin-2 [IL-2] only) and chronic (anti-CD3 and IL-2) stimulation conditions.
Generate 32 genes that maximize the perturbation effect."""

prompt2 = """Plan a cellular assay to detect allosteric modulation of receptor R in T cells.
 Measure calcium flux in response to ligand binding with and without a candidate allosteric inhibitor. 
 Generate 10 candidate compounds predicted to alter the signaling amplitude."""


cross_reference_chembl_pubchem_prompt = '''
I'm working on a drug repurposing project targeting EGFR (UniProt ID: P00533). I have a list of three compounds I'm interested in: Gefitinib, Erlotinib, and Lapatinib. Can you help me gather comprehensive chemical information about these compounds including their molecular properties, SMILES structures, and any drug approval information? I need this data to compare their physicochemical profiles.
'''
map_covalent_probes_to_allosteric_prompt = """
I'm researching covalent inhibitors for KRAS G12C (UniProt ID: P01116).

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
4. If no allosteric or non-catalytic inhibitors are found, explain which keywords/annotations were checked and why the dataset is dominated by catalytic-site inhibitors.
"""

analyze_site_patterns_prompt = '''
I've been looking at covalent inhibitors for EGFR and noticed they seem to target many different residues. Can you analyze the binding site data to show me which residues are most commonly targeted? I want to understand if there are preferred residue types (like cysteines or serines) and see the overall distribution of target sites.
'''

covalent_probe_prompt = '''
"Given the protein with UniProt ID 'P00533' (EGFR), identify and cross-reference the following ligands: Gefitinib, Erlotinib, and a fictitious ligand called NonexistentLigand123. For each ligand, retrieve detailed chemical and biological information, including database identifiers, synonyms, chemical properties, structural information, classification, and approval status. If a ligand cannot be found, indicate that an error occurred or the data is unavailable. Summarize the results in a structured format that clearly associates each ligand with the protein and its corresponding information."
'''

# combines cross reference tool, covalent probe tool, anaylze_site_patterns tool
combination_prompt_1 = '''
I'm developing a covalent drug discovery pipeline for KRAS G12C (UniProt ID: P01116). Here's what I need:
First, I want to gather detailed chemical information on three known KRAS inhibitors: Sotorasib, Adagrasib, and AMG510. I need their molecular properties and structures for comparison.
Second, I want to understand the landscape of covalent inhibitors targeting KRAS. Specifically, I need to know which inhibitors bind to allosteric sites versus the active site, since G12C is in a switching region. Can you classify the available KRAS covalent inhibitors by their binding site type?
Finally, I'd like to see an analysis of which residues are most commonly targeted across all KRAS covalent inhibitors. This will help me understand if there are hotspot residues beyond Cys12 that might be worth investigating.
Can you help me with this complete analysis?
'''

allosteric_analysis_prompt = '''
I need to analyze allosteric regulation mechanisms for several proteins known to have allosteric properties. Specifically, I want to understand:

1. How residues communicate between different allosteric sites
2. Which residues are most critical for allosteric signal transmission (hotspots)
3. The network topology connecting these regulatory sites

The proteins I'm interested in are:
- EGFR (P00533) - a receptor tyrosine kinase involved in cancer signaling
- PDPK1 (O15530) - a kinase with extensive allosteric regulation
- BRAF (P15056) - a RAF kinase with known allosteric inhibitors
- Alcohol dehydrogenase from yeast (P32449) - a classic allosteric enzyme

For each protein, I'd like to know:
- What are the key allosteric sites and how many residues are involved?
- Which residues appear across multiple modulators (potential therapeutic targets)?
- Are there communication pathways between different allosteric sites?
- What are the most important residues for allosteric transmission based on their connectivity?

Please analyze these proteins and provide detailed information about their allosteric mechanisms, including network properties, hotspot residues, and any patterns that emerge across the dataset.
'''


allosteric = True
# gpt-3.5-turbo, gpt-4o
agent = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=True, api_key=os.environ["OPENAI_API_KEY"])
'''
agent.add_data(
    {"ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
    }) # remember to add to allosteric_file_ids in a1.py too.
'''

# prompt
prompt = allosteric_analysis_prompt
prompt_file = "allosteric_analysis_prompt.txt"
with open(prompt_file, "w") as f:
    f.write(prompt)


log, final_output = agent.go(prompt)


# output
print('Final Output: ', final_output)
print('Logs: \n')
for entry in log:
    print(entry)

if allosteric:
    output_file = "allosteric_analysis_prompt_prompt.txt"
else:
    output_file = "allosteric_analysis_biomni_prompt.txt"



with open(output_file, "w") as f:
    f.write("Final Output:\n")
    f.write(str(final_output) + "\n\n")
    f.write("Logs:\n")
    for entry in log:
        f.write(str(entry) + "\n")


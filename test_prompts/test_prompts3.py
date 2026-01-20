from biomni_biolab.agent import A1
from dotenv import load_dotenv
import os
import time

load_dotenv()

# We can store different prompts for testing
prompt1 = """Plan a CRISPR screen to identify genes that regulate T cell exhaustion,
measured by the change in T cell receptor (TCR) signaling between acute
(interleukin-2 [IL-2] only) and chronic (anti-CD3 and IL-2) stimulation conditions.
Generate 32 genes that maximize the perturbation effect."""

prompt2 = """Plan a cellular assay to detect allosteric modulation of receptor R in T cells.
 Measure calcium flux in response to ligand binding and without a candidate allosteric inhibitor. 
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

allosteric = True
prompt = map_covalent_probes_to_allosteric_prompt

print("=" * 80)
print("VECTOR DATABASE RETRIEVAL BENCHMARK")
print("=" * 80)
print(f"\nTesting prompt:\n{prompt[:100]}...\n")

# Test 1: WITH Vector Search
print("\n" + "=" * 80)
print("TEST 1: WITH Vector Database (use_vector_search=True)")
print("=" * 80)

agent_vector = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=True, api_key=os.environ["OPENAI_API_KEY"])

agent_vector.add_data(
    {
        "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
        "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
        "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
        "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
        "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
        "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
    }
)

start_time_vector = time.time()
log_vector, final_output_vector = agent_vector.go(prompt)
end_time_vector = time.time()

time_vector = end_time_vector - start_time_vector
print(f"\n✓ Total execution time: {time_vector:.2f} seconds")
print(f"Final Output (first 200 chars): {str(final_output_vector)[:200]}...")

# Test 2: WITHOUT Vector Search (LLM-based)
print("\n" + "=" * 80)
print("TEST 2: WITHOUT Vector Database (use_vector_search=False)")
print("=" * 80)

agent_llm = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=False, api_key=os.environ["OPENAI_API_KEY"])

agent_llm.add_data(
    {
        "ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
        "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
        "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
        "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
        "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
        "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
    }
)

start_time_llm = time.time()
log_llm, final_output_llm = agent_llm.go(prompt)
end_time_llm = time.time()

time_llm = end_time_llm - start_time_llm
print(f"\n✓ Total execution time: {time_llm:.2f} seconds")
print(f"Final Output (first 200 chars): {str(final_output_llm)[:200]}...")

# Comparison
print("\n" + "=" * 80)
print("BENCHMARK RESULTS")
print("=" * 80)
print(f"\nVector Database (use_vector_search=True):  {time_vector:.2f} seconds")
print(f"LLM-based (use_vector_search=False):       {time_llm:.2f} seconds")
print(f"\nSpeed improvement: {time_llm / time_vector:.2f}x faster with vector database")
print(f"Time saved: {time_llm - time_vector:.2f} seconds")

# Save results
output_file = "test_prompts3_results.txt"
with open(output_file, "w") as f:
    f.write("VECTOR DATABASE RETRIEVAL BENCHMARK\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Prompt tested:\n{prompt}\n\n")
    f.write("=" * 80 + "\n")
    f.write("RESULTS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Vector Database (use_vector_search=True):  {time_vector:.2f} seconds\n")
    f.write(f"LLM-based (use_vector_search=False):       {time_llm:.2f} seconds\n\n")
    f.write(f"Speed improvement: {time_llm / time_vector:.2f}x faster with vector database\n")
    f.write(f"Time saved: {time_llm - time_vector:.2f} seconds\n\n")
    f.write("=" * 80 + "\n")
    f.write("VECTOR DATABASE TEST OUTPUT\n")
    f.write("=" * 80 + "\n")
    f.write("Final Output:\n")
    f.write(str(final_output_vector) + "\n\n")
    f.write("Logs:\n")
    for entry in log_vector:
        f.write(str(entry) + "\n")
    f.write("\n" + "=" * 80 + "\n")
    f.write("LLM-BASED TEST OUTPUT\n")
    f.write("=" * 80 + "\n")
    f.write("Final Output:\n")
    f.write(str(final_output_llm) + "\n\n")
    f.write("Logs:\n")
    for entry in log_llm:
        f.write(str(entry) + "\n")

print(f"\n✓ Results saved to: {output_file}")

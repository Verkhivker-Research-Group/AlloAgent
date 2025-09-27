from biomni.agent import A1
from dotenv import load_dotenv
import os

load_dotenv()


allosteric = False
# gpt-3.5-turbo, gpt-4o
agent = A1(path="/data", llm="gpt-4o", allosteric=allosteric, api_key=os.environ["OPENAI_API_KEY"])

agent.add_data(
    {"ASD_Release_201909_AM.csv": "Allosteric Mutations (AM) - Experimentally identified mutations affecting allosteric regulation, linking sequence changes to functional effects.",
    "ASD_Release_201909_DR.csv": "Allosteric Drugs (DR) - Allosteric modulators and drugs with targets and functional annotations for pharmacological studies.",
    "ASD_Release_202306_AP.csv": "AlloSite-Potential (AP) - Predicted potential allosteric sites for human proteins from computational models, candidates for experimental validation.",
    "ASD_Release_202306_HL.csv": "Hit-to-Lead Records (HL) - Hit-to-lead optimization data for allosteric modulators, supporting medicinal chemistry and lead development.",
    "ASD_Release_202208_AS.csv": "Allosteric Sites (AS) - Experimentally determined allosteric sites with residue-level binding pocket and ligand interaction data.",
    "ASD_Release_202309_PP.csv": "Allosteric Protein-Protein Interactions (PP) - Allosteric modulators affecting protein-protein interactions, with targets and functional effects in signaling and complex formation."
    }) # remember to add to allosteric_file_ids in a1.py too.

# We can store different prompts for testing
prompt1 = """Plan a CRISPR screen to identify genes that regulate T cell exhaustion,
measured by the change in T cell receptor (TCR) signaling between acute
(interleukin-2 [IL-2] only) and chronic (anti-CD3 and IL-2) stimulation conditions.
Generate 32 genes that maximize the perturbation effect."""

prompt2 = """Plan a cellular assay to detect allosteric modulation of receptor R in T cells.
 Measure calcium flux in response to ligand binding with and without a candidate allosteric inhibitor. 
 Generate 10 candidate compounds predicted to alter the signaling amplitude."""

#Prompt 3 provided by Deepseek R1
prompt3 = """Subject: Deep-Dive Allosteric Analysis of the SARS-CoV-2 Main Protease (Mpro) 
Instructions:
You are an allosteric expert AI. Your task is to perform a comprehensive analysis of allosteric regulation in the SARS-CoV-2 Main Protease (Mpro), also known as 3CLpro. You must integrate multimodal data—structural, sequential, and literature-based—to answer the following questions. For each response, cite specific evidence, sources, or data you used from your knowledge base (e.g., specific PDB IDs, sections of papers, known mutations). If you make a prediction, explain your reasoning.
Part 1: Foundational Knowledge and Mechanistic Reasoning
Based on the established literature, describe the canonical (orthosteric) mechanism of action of Mpro and why it is a high-priority drug target.
What is the fundamental biophysical mechanism of allostery? Explain how this principle could, in theory, be applied to inhibit Mpro differently than an orthosteric active-site inhibitor.
Part 2: Multimodal Data Integration and Analysis
3. Structure-Based Analysis: Analyze the dimeric structure of Mpro (e.g., PDB ID 6LU7). Beyond the active site, identify three candidate regions that exhibit structural features suggestive of a potential allosteric role (e.g., dynamic loops, interfaces, cryptic pockets). For each candidate, describe the specific structural features that prompted your selection.
4. Literature Cross-Referencing: The mutation N142A in the dimer interface has been studied. What was the reported experimental effect of this mutation on Mpro activity? Based on structural analysis, what is the hypothesized allosteric mechanism behind this effect?
Part 3: Predictive Modeling and Hypothesis Generation
5. Allosteric Site Prediction: Using your integrated model, predict the most likely location of a high-impact allosteric pocket in Mpro. Provide the predicted 3D coordinates (or a descriptive location, e.g., "near the hinge of domain II"). Justify your prediction by combining evidence from:
* Evolutionary conservation analysis of the Mpro sequence.
* Computed structural dynamics (e.g., areas of high flexibility/rigidity).
* Known homologous allosteric sites in related coronaviral proteases.
6. Ligand Prediction: Propose the top 2 chemical features or scaffolds (e.g., "a planar heteroaromatic system with a hydrogen bond donor") that would make an effective small molecule binder for the pocket you predicted in question 5. Explain why these features are suitable for that specific pocket's geometry and physicochemical properties.
7. Mutation Analysis: A novel mutation, V186F, is discovered in a viral isolate. Predict its potential allosteric effect on enzyme function and drug binding. Is it likely to be activating, deactivating, or neutral? Could it confer resistance to known orthosteric drugs like Nirmatrelvir? Outline your logical pathway for this prediction.
Part 4: Experimental Design
8. Based on your entire analysis, design a key experiment to validate your predicted allosteric pocket from question 5. Specify the technique (e.g., NMR, HDX-MS, fragment-based screening, mutagenesis) and describe the expected outcome that would confirm your hypothesis.
"""

#Prompt 4 provided by GPT5
prompt4 = """You are an advanced biomedical AI agent (like Biomni). Your task is to demonstrate comprehensive capabilities addressing allostery. Please perform the following tasks sequentially:
Define allostery, PAM, NAM, bidirectional allostery, and feedback allostery.
For phosphofructokinase regulated by ATP and ADP, classify the modulators and explain the mechanism.
Given the 3D structure of the protein (PDB: XXXX), predict at least two potential allosteric sites and explain your reasoning.
Propose a structural modulator (small molecule or peptide) for one site, describing anchor/driver features.
Outline an MD-based simulation to test modulation, including readouts and interpretation strategy.
Design an allosteric feedback simulation model (differential equations or network) for the enzyme under conditions of high and low ATP.
Using Biomni’s tools, sketch a pipeline that automates steps 3–5 (site identification, design, validation)."
Please include citations for definitions and mechanistic claims, and explain how Biomni’s components—tool selection, code execution, literature retrieval—enable these tasks."""

biolip_database_prompt = '''I need information about molecular interactions and bound biomolecules for specific PDB entries from the Biolip Database.

Give me all interactions for the protein with PDB ID 1GG1.

For the structure 1a1k, list all DNA sequences it binds, both per chain (B) and across all chains.

For the structure 4a1g, provide the peptide sequences bound to chain G and to all chains.

For 8q5w, list the proteins bound to chain B and all chains.

For 8a3w, provide RNA sequences bound to chain S1 and all chains.
Give results clearly, specifying chain where relevant.'''


asd_database_prompt = ''' Can you give me all the information for the protein with uniprot id: O94925  from the ASD database. Let me know if you don't have the ASD database. Do not under any circumstances query anything else. Hint: It should be in your datalake'''
# prompt
log, final_output = agent.go(asd_database_prompt)


# output
print('Final Output: ', final_output)
print('Logs: \n')
for entry in log:
    print(entry)

if allosteric:
    output_file = "asd_database_results.txt"
else:
    output_file = "biomni_results.txt"


with open(output_file, "w") as f:
    f.write("Final Output:\n")
    f.write(str(final_output) + "\n\n")
    f.write("Logs:\n")
    for entry in log:
        f.write(str(entry) + "\n")


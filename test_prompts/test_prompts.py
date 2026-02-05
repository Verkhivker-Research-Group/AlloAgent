import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from biomni_biolab.agent import A1
from dotenv import load_dotenv

load_dotenv()


allosteric = True
# gpt-3.5-turbo, gpt-4o
agent = A1(llm="gpt-4o", allosteric=True, api_key=os.environ["OPENAI_API_KEY"])
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
prompt = """

    >> Enter Prompt Here <<

"""
prompt_file = "prompt_results.txt"
with open(prompt_file, "w") as f:
    f.write(prompt)


log, final_output = agent.go(prompt)


# output
print('Final Output: ', final_output)
print('Logs: \n')
for entry in log:
    print(entry)

if allosteric:
    output_file = "allosteric_prompt_results.txt"
else:
    output_file = "non_allosteric_prompt_results.txt"



with open(output_file, "w") as f:
    f.write("Final Output:\n")
    f.write(str(final_output) + "\n\n")
    f.write("Logs:\n")
    for entry in log:
        f.write(str(entry) + "\n")


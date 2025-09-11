from biomni.agent import A1
from dotenv import load_dotenv
import os

load_dotenv()

# gpt-3.5-turbo, gpt-4o
agent = A1(path="/data", llm="gpt-4o", allosteric=True, api_key=os.environ["OPENAI_API_KEY"])


# We can store different prompts for testing
prompt1 = """Describe energy landscape theory in the context of allostery for hemoglobin. 
Build a comprehensive energy landscape that shows how conformational changes in hemoglobin 
affect oxygen binding and allosteric regulation. Include specific structural details, 
energy barriers, and the role of key residues like His146 and Asp94 in the allosteric mechanism
Specifiy what methods within our databse that you used to get this information."""

prompt2 = """Plan a cellular assay to detect allosteric modulation of receptor R in T cells.
 Measure calcium flux in response to ligand binding with and without a candidate allosteric inhibitor. 
 Generate 10 candidate compounds predicted to alter the signaling amplitude."""

# prompt
log, final_output = agent.go(prompt1)


# output
print('Final Output: ', final_output)
print('Logs: \n')
for entry in log:
    print(entry)

with open("results.txt", "w") as f:
    f.write("Final Output:\n")
    f.write(str(final_output) + "\n\n")
    f.write("Logs:\n")
    for entry in log:
        f.write(str(entry) + "\n")

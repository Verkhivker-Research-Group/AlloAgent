from biomni.agent import A1
from dotenv import load_dotenv
import os

load_dotenv()

# gpt-3.5-turbo, gpt-4o
agent = A1(path="/data", llm="gpt-4o", api_key=os.environ["OPENAI_API_KEY"])


# prompt
log, final_output = agent.go("""
Plan a CRISPR screen to identify genes that regulate T cell exhaustion,
measured by the change in T cell receptor (TCR) signaling between acute
(interleukin-2 [IL-2] only) and chronic (anti-CD3 and IL-2) stimulation conditions.
Generate 32 genes that maximize the perturbation effect.
"""
)


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

from biomni.agent import A1
from dotenv import load_dotenv
import os

load_dotenv()

# gpt-3.5-turbo, gpt-4o
agent = A1(path="/data", llm="gpt-4o", api_key=os.environ["OPENAI_API_KEY"])


# prompt
log, final_output = agent.go(
    "test"
)


# output
print('Final Output: ', final_output)
print('Logs: \n')
for entry in log:
    print(entry)
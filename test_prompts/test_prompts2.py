import os
from biomni_biolab.agent import A1
from dotenv import load_dotenv
from prompts import PROMPTS, ALLOSTERIC_DATA

load_dotenv()

# Process each prompt
for prompt_name, prompt_text in PROMPTS.items():
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
    agent_allosteric.add_data(ALLOSTERIC_DATA)
    
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
    agent_nonallosteric.add_data(ALLOSTERIC_DATA)
    
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


import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biomni_biolab.agent import A1
from dotenv import load_dotenv
from prompts import PROMPTS, ALLOSTERIC_DATA

load_dotenv()

prompt_items = list(PROMPTS.items())
# Start with prompt n
n = 21 - 1 # prompt number -1 (0 indexed)
# Process prompts from start to end (set n above)
for prompt_name, prompt_text in prompt_items[n:n+3]:
    try:
        print(f"\n{'='*80}")
        print(f"Processing: {prompt_name}")
        print(f"{'='*80}\n")

        # Create folder for this prompt inside 'results'
        results_dir = os.path.join("results", "comparison_results")
        os.makedirs(results_dir, exist_ok=True)
        folder_name = os.path.join(results_dir, prompt_name)
        os.makedirs(folder_name, exist_ok=True)

        # Save the prompt text
        prompt_file_path = os.path.join(folder_name, "prompt.txt")
        with open(prompt_file_path, "w") as f:
            f.write(prompt_text)
        print(f"Saved prompt to: {prompt_file_path}")

        # Run with allosteric=True
        print(f"\nRunning {prompt_name} with allosteric=True...")
        agent_allosteric = A1(llm="gpt-4o", allosteric=True, use_vector_search=False, api_key=os.environ["OPENAI_API_KEY"])
        agent_allosteric.add_data(ALLOSTERIC_DATA)  # remember to add to allosteric_file_ids in a1.py too.

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
        agent_nonallosteric = A1(llm="gpt-4o", allosteric=False, use_vector_search=False, api_key=os.environ["OPENAI_API_KEY"])

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

    except Exception as e:
        print(f"Error processing {prompt_name}: {e}")
        # Log error to a file in the prompt's folder
        results_dir = os.path.join("results", "comparison_results")
        folder_name = os.path.join(results_dir, prompt_name)
        os.makedirs(folder_name, exist_ok=True)
        error_path = os.path.join(folder_name, "error.txt")
        with open(error_path, "w") as f:
            f.write(str(e))
        continue

print(f"\n{'='*80}")
print("All prompts processed successfully!")
print(f"{'='*80}")

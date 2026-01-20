from biomni_biolab.agent import A1
from dotenv import load_dotenv
from prompts import PROMPTS, ALLOSTERIC_DATA
import os
import time

load_dotenv()

# Process each prompt
for prompt_name, prompt in PROMPTS.items():
    allosteric = True

    print("=" * 80)
    print(f"VECTOR DATABASE RETRIEVAL BENCHMARK - {prompt_name}")
    print("=" * 80)
    print(f"\nTesting prompt:\n{prompt[:100]}...\n")

    # Test 1: WITH Vector Search
    print("\n" + "=" * 80)
    print("TEST 1: WITH Vector Database (use_vector_search=True)")
    print("=" * 80)

    agent_vector = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=True, api_key=os.environ["OPENAI_API_KEY"])
    agent_vector.add_data(ALLOSTERIC_DATA)

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
    agent_llm.add_data(ALLOSTERIC_DATA)

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
    output_file = f"test_prompts3_results_{prompt_name}.txt"
    with open(output_file, "w") as f:
        f.write(f"VECTOR DATABASE RETRIEVAL BENCHMARK - {prompt_name}\n")
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

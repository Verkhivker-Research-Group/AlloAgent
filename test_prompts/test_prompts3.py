import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biomni_biolab.agent import A1
from dotenv import load_dotenv
from prompts import PROMPTS, ALLOSTERIC_DATA
import time

load_dotenv()

def _extract_tool_names(tools):
    names = []
    for tool in tools:
        if isinstance(tool, dict):
            names.append(tool.get("name", str(tool)))
        else:
            names.append(getattr(tool, "name", str(tool)))
    return names

prompt_items = list(PROMPTS.items())
# Start with prompt n
n = 9 - 1 # prompt number - 1 (0 indexed)
# Process prompts from start to end (set n above)
for prompt_name, prompt in prompt_items[n:n+4]:
    try:
        allosteric = True

        print("=" * 80)
        print(f"VECTOR DATABASE RETRIEVAL BENCHMARK - {prompt_name}")
        print("=" * 80)
        print(f"\nTesting prompt:\n{prompt[:100]}...\n")


        # --- Tool Selection Timing Only ---
        print("\n" + "=" * 80)
        print("TOOL SELECTION BENCHMARK - VECTOR DATABASE")
        print("=" * 80)
        agent_vector = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=True, api_key=os.environ["OPENAI_API_KEY"])
        agent_vector.add_data(ALLOSTERIC_DATA)
        # Gather resources as in agent.go()
        all_tools = agent_vector.tool_registry.tools if hasattr(agent_vector, "tool_registry") else []
        data_lake_path = agent_vector.path + "/data_lake"
        data_lake_content = os.listdir(data_lake_path) if os.path.exists(data_lake_path) else []
        data_lake_items = [os.path.basename(x) for x in data_lake_content]
        if allosteric:
            from biomni_biolab.env_desc import allosteric_data_lake
            data_lake_descriptions = []
            allosteric_keys = set(allosteric_data_lake.keys())
            for item in data_lake_items:
                stem, _ = os.path.splitext(item)
                key = stem if stem in allosteric_keys else (item if item in allosteric_keys else None)
                if not key:
                    continue
                entry = allosteric_data_lake[key]
                data_lake_descriptions.append({
                    "name": item,
                    "description": entry.get("description", f"Data lake item: {item}"),
                    "categories": entry.get("allosteric_category", []),
                })
        else:
            from biomni_biolab.env_desc import data_lake_dict
            data_lake_descriptions = []
            for item in data_lake_items:
                description = data_lake_dict.get(item, f"Data lake item: {item}")
                data_lake_descriptions.append({"name": item, "description": description})
        from biomni_biolab.env_desc import library_content_dict
        library_descriptions = [{"name": k, "description": v} for k, v in library_content_dict.items()]
        resources = {
            "tools": all_tools,
            "data_lake": data_lake_descriptions,
            "libraries": library_descriptions,
        }
        # Time the tool selection step only
        start_sel_vector = time.time()
        if agent_vector.retriever.use_vector_search:
            selected_vector = agent_vector.retriever.vector_based_retrieval(prompt, resources)
        else:
            selected_vector = agent_vector.retriever.prompt_based_retrieval(prompt, resources, llm=agent_vector.llm)
        end_sel_vector = time.time()
        sel_time_vector = end_sel_vector - start_sel_vector
        selected_vector_tools = _extract_tool_names(selected_vector.get("tools", []))
        print(f"✓ Tool selection time (vector): {sel_time_vector:.4f} seconds")

        print("\n" + "=" * 80)
        print("TOOL SELECTION BENCHMARK - LLM")
        print("=" * 80)
        agent_llm = A1(llm="gpt-4o", allosteric=allosteric, use_vector_search=False, api_key=os.environ["OPENAI_API_KEY"])
        agent_llm.add_data(ALLOSTERIC_DATA)
        all_tools = agent_llm.tool_registry.tools if hasattr(agent_llm, "tool_registry") else []
        data_lake_path = agent_llm.path + "/data_lake"
        data_lake_content = os.listdir(data_lake_path) if os.path.exists(data_lake_path) else []
        data_lake_items = [os.path.basename(x) for x in data_lake_content]
        if allosteric:
            from biomni_biolab.env_desc import allosteric_data_lake
            data_lake_descriptions = []
            allosteric_keys = set(allosteric_data_lake.keys())
            for item in data_lake_items:
                stem, _ = os.path.splitext(item)
                key = stem if stem in allosteric_keys else (item if item in allosteric_keys else None)
                if not key:
                    continue
                entry = allosteric_data_lake[key]
                data_lake_descriptions.append({
                    "name": item,
                    "description": entry.get("description", f"Data lake item: {item}"),
                    "categories": entry.get("allosteric_category", []),
                })
        else:
            from biomni_biolab.env_desc import data_lake_dict
            data_lake_descriptions = []
            for item in data_lake_items:
                description = data_lake_dict.get(item, f"Data lake item: {item}")
                data_lake_descriptions.append({"name": item, "description": description})
        from biomni_biolab.env_desc import library_content_dict
        library_descriptions = [{"name": k, "description": v} for k, v in library_content_dict.items()]
        resources = {
            "tools": all_tools,
            "data_lake": data_lake_descriptions,
            "libraries": library_descriptions,
        }
        start_sel_llm = time.time()
        selected_llm = agent_llm.retriever.prompt_based_retrieval(prompt, resources, llm=agent_llm.llm)
        end_sel_llm = time.time()
        sel_time_llm = end_sel_llm - start_sel_llm
        selected_llm_tools = _extract_tool_names(selected_llm.get("tools", []))
        print(f"✓ Tool selection time (LLM):   {sel_time_llm:.4f} seconds")

        print("\n" + "=" * 80)
        print("TOOL SELECTION BENCHMARK RESULTS")
        print("=" * 80)
        print(f"\nVector Database (tool selection):  {sel_time_vector:.4f} seconds")
        print(f"LLM-based (tool selection):       {sel_time_llm:.4f} seconds")
        print(f"\nSpeed improvement: {sel_time_llm / sel_time_vector:.2f}x faster with vector database" if sel_time_vector > 0 else "N/A")
        print(f"Time saved: {sel_time_llm - sel_time_vector:.4f} seconds")


        # Save tool selection benchmark results only
        results_dir = os.path.join("results", "vdb_results")
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, f"{prompt_name}_tool_selection_results.txt")
        with open(output_file, "w") as f:
            f.write(f"TOOL SELECTION BENCHMARK - {prompt_name}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Prompt tested:\n{prompt}\n\n")
            f.write("=" * 80 + "\n")
            f.write("TOOL SELECTION RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Vector Database (tool selection):  {sel_time_vector:.4f} seconds\n")
            f.write(f"LLM-based (tool selection):       {sel_time_llm:.4f} seconds\n\n")
            if sel_time_vector > 0:
                f.write(f"Speed improvement: {sel_time_llm / sel_time_vector:.2f}x faster with vector database\n")
            else:
                f.write("Speed improvement: N/A\n")
            f.write(f"Time saved: {sel_time_llm - sel_time_vector:.4f} seconds\n\n")
            f.write("SELECTED TOOLS\n")
            f.write("=" * 80 + "\n")
            f.write("Vector Database selection:\n")
            if selected_vector_tools:
                for name in selected_vector_tools:
                    f.write(f"- {name}\n")
            else:
                f.write("(no tools selected)\n")
            f.write("\nLLM-based selection:\n")
            if selected_llm_tools:
                for name in selected_llm_tools:
                    f.write(f"- {name}\n")
            else:
                f.write("(no tools selected)\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("=" * 80 + "\n")

        print(f"\n✓ Results saved to: {output_file}")

    except Exception as e:
        print(f"Error processing {prompt_name}: {e}")
        # Log error to a file in results folder
        results_dir = os.path.join("results", "vdb_results")
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, f"{prompt_name}_vdb_error.txt")
        with open(output_file, "w") as f:
            f.write(str(e))
        continue

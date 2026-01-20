#!/usr/bin/env python3
"""
Rebuild the vector database for BIOMNI.

Usage:
    python rebuild_vectorstore.py [--allosteric] [--delete-only]
    
Options:
    --allosteric    Build vectorstore for allosteric mode
    --delete-only   Only delete the existing vectorstore without rebuilding
"""

import argparse
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables from .env file
if os.path.exists(".env"):
    load_dotenv(".env", override=False)
    print("Loaded environment variables from .env")

from biomni_biolab.utils import read_module2api, read_module2api_allosteric
from biomni_biolab.tool.tool_registry import ToolRegistry
from biomni_biolab.model.vector_database import rebuild_vectorstore, delete_vectorstore, load_vectorstore
from biomni_biolab.env_desc import data_lake_dict, library_content_dict, allosteric_data_lake
import glob


def main():
    parser = argparse.ArgumentParser(description="Rebuild the BIOMNI vector database")
    parser.add_argument("--allosteric", action="store_true", help="Build for allosteric mode")
    parser.add_argument("--delete-only", action="store_true", help="Only delete without rebuilding")
    args = parser.parse_args()
    
    persist_directory = "./data/vectorstore"
    
    if args.delete_only:
        print("Deleting vector store...")
        delete_vectorstore(persist_directory)
        print("Done!")
        return
    
    # Load the appropriate module2api based on mode
    if args.allosteric:
        print("Building vectorstore for ALLOSTERIC mode")
        module2api = read_module2api_allosteric()
    else:
        print("Building vectorstore for STANDARD mode")
        module2api = read_module2api()
    
    # Create tool registry
    tool_registry = ToolRegistry(module2api)
    all_tools = tool_registry.tools
    
    # Get data lake items
    data_lake_path = "./data/biomni_data/data_lake"
    if not os.path.exists(data_lake_path):
        print(f"⚠ Warning: Data lake path not found: {data_lake_path}")
        data_lake_items = []
    else:
        data_lake_content = glob.glob(data_lake_path + "/*")
        data_lake_items = [os.path.basename(x) for x in data_lake_content]
    
    # Build data lake descriptions
    data_lake_descriptions = []
    
    if args.allosteric:
        # Filter for allosteric datasets only
        allosteric_keys = set(allosteric_data_lake.keys())
        for item in data_lake_items:
            stem, _ = os.path.splitext(item)
            key = None
            if stem in allosteric_keys:
                key = stem
            elif item in allosteric_keys:
                key = item
            
            if key:
                entry = allosteric_data_lake[key]
                data_lake_descriptions.append({
                    "name": item,
                    "description": entry.get("description", ""),
                    "categories": entry.get("allosteric_category", []),
                })
        print(f"Allosteric datasets: {len(data_lake_descriptions)} of {len(data_lake_items)} total files")
    else:
        # Use all datasets
        for item in data_lake_items:
            description = data_lake_dict.get(item, f"Data lake item: {item}")
            data_lake_descriptions.append({"name": item, "description": description})
        print(f"Standard datasets: {len(data_lake_descriptions)}")
    
    # Build library descriptions
    library_descriptions = []
    for lib_name, lib_desc in library_content_dict.items():
        library_descriptions.append({"name": lib_name, "description": lib_desc})
    
    # Prepare resources
    resources = {
        "tools": all_tools,
        "data_lake": data_lake_descriptions,
        "libraries": library_descriptions,
    }
    
    print(f"\nResources to embed:")
    print(f"  Tools: {len(all_tools)}")
    print(f"  Data lake items: {len(data_lake_descriptions)}")
    print(f"  Libraries: {len(library_descriptions)}")
    print()
    
    # Rebuild the vectorstore
    vectorstore = rebuild_vectorstore(
        resources=resources,
        persist_directory=persist_directory
    )
    
    if vectorstore:
        print("\n✓ Successfully rebuilt vector store!")
        print(f"  Location: {os.path.abspath(persist_directory)}")
        print("\nYou can now run the agent - it will load this vectorstore from disk.")
    else:
        print("\n✗ Failed to rebuild vector store")
        sys.exit(1)


if __name__ == "__main__":
    main()

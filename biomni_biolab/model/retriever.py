import contextlib
import os
import re
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from biomni_biolab.model.vector_database import load_vectorstore


class ToolRetriever:
    """Retrieve tools from the tool registry using vector search or LLM-based retrieval."""

    def __init__(self, use_vector_search: bool = True, embedding_model: str = "text-embedding-3-small", persist_directory: str = "./data/vectorstore"):
        """Initialize the retriever.
        
        Args:
            use_vector_search: If True, use vector database for retrieval. If False, use LLM-based retrieval.
            embedding_model: The embedding model to use for vector search.
            persist_directory: Directory where the vector store is persisted.
        """
        self.use_vector_search = use_vector_search
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        self.vectorstore = None
        
        # Load vectorstore from disk if vector search is enabled
        if self.use_vector_search:
            try:
                self.vectorstore = load_vectorstore(
                    persist_directory=persist_directory,
                    embedding_model=embedding_model
                )
                if self.vectorstore is None:
                    print("⚠ Vector store not available. Falling back to LLM-based retrieval.")
                    print("  Run rebuild_vectorstore() from biomni_biolab.model.vector_database to create it.")
                    self.use_vector_search = False
            except Exception as e:
                print(f"⚠ Failed to load vector store: {e}")
                print("  Falling back to LLM-based retrieval")
                self.use_vector_search = False



    def vector_based_retrieval(self, query: str, resources: dict, k: int = 30) -> dict:
        """Use vector similarity search to retrieve relevant resources.
        
        Args:
            query: The user's query
            resources: The full resource dictionary
            k: Number of results to retrieve per category
            
        Returns:
            Dictionary with selected resources
        """
        # Initialize vectorstore if not already done
        if self.vectorstore is None:
            self.initialize_vectorstore(resources)
        
        if self.vectorstore is None:
            # Fallback to LLM-based retrieval
            print("Falling back to LLM-based retrieval")
            return self.prompt_based_retrieval(query, resources)
        
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=k)
            
            # Organize results by type
            selected_indices = {
                "tools": [],
                "data_lake": [],
                "libraries": []
            }
            
            for result in results:
                metadata = result.metadata
                result_type = metadata.get("type")
                index = metadata.get("index")
                
                if result_type == "tool":
                    selected_indices["tools"].append(index)
                elif result_type == "data_lake":
                    selected_indices["data_lake"].append(index)
                elif result_type == "library":
                    selected_indices["libraries"].append(index)
            
            # Get unique indices (preserve order)
            selected_indices["tools"] = list(dict.fromkeys(selected_indices["tools"]))
            selected_indices["data_lake"] = list(dict.fromkeys(selected_indices["data_lake"]))
            selected_indices["libraries"] = list(dict.fromkeys(selected_indices["libraries"]))
            
            # Retrieve actual resources
            selected_resources = {
                "tools": [
                    resources["tools"][i] 
                    for i in selected_indices["tools"] 
                    if i < len(resources.get("tools", []))
                ],
                "data_lake": [
                    resources["data_lake"][i]
                    for i in selected_indices["data_lake"]
                    if i < len(resources.get("data_lake", []))
                ],
                "libraries": [
                    resources["libraries"][i]
                    for i in selected_indices["libraries"]
                    if i < len(resources.get("libraries", []))
                ],
            }
            
            print(f"✓ Vector retrieval: {len(selected_resources['tools'])} tools, "
                  f"{len(selected_resources['data_lake'])} datasets, "
                  f"{len(selected_resources['libraries'])} libraries")
            
            return selected_resources
            
        except Exception as e:
            print(f"Error in vector retrieval, falling back to LLM-based: {e}")
            return self.prompt_based_retrieval(query, resources)

    def prompt_based_retrieval(self, query: str, resources: dict, llm=None) -> dict:
        """Use a prompt-based approach to retrieve the most relevant resources for a query.

        Args:
            query: The user's query
            resources: A dictionary with keys 'tools', 'data_lake', and 'libraries',
                      each containing a list of available resources
            llm: Optional LLM instance to use for retrieval (if None, will create a new one)

        Returns:
            A dictionary with the same keys, but containing only the most relevant resources

        """
        # Create a prompt for the LLM to select relevant resources
        prompt = f"""
You are an expert biomedical research assistant. Your task is to select the relevant resources to help answer a user's query.

USER QUERY: {query}

Below are the available resources. For each category, select items that are directly or indirectly relevant to answering the query.
Be generous in your selection - include resources that might be useful for the task, even if they're not explicitly mentioned in the query.
It's better to include slightly more resources than to miss potentially useful ones.

AVAILABLE TOOLS:
{self._format_resources_for_prompt(resources.get("tools", []))}

AVAILABLE DATA LAKE ITEMS:
{self._format_resources_for_prompt(resources.get("data_lake", []))}

AVAILABLE SOFTWARE LIBRARIES:
{self._format_resources_for_prompt(resources.get("libraries", []))}

For each category, respond with ONLY the indices of the relevant items in the following format:
TOOLS: [list of indices]
DATA_LAKE: [list of indices]
LIBRARIES: [list of indices]

For example:
TOOLS: [0, 3, 5, 7, 9]
DATA_LAKE: [1, 2, 4]
LIBRARIES: [0, 2, 4, 5, 8]

If a category has no relevant items, use an empty list, e.g., DATA_LAKE: []

IMPORTANT GUIDELINES:
1. Be generous but not excessive - aim to include all potentially relevant resources
2. ALWAYS prioritize database tools for general queries - include as many database tools as possible
3. Include all literature search tools
4. For wet lab sequence type of queries, ALWAYS include molecular biology tools
5. For data lake items, include datasets that could provide useful information
6. For libraries, include those that provide functions needed for analysis
7. Don't exclude resources just because they're not explicitly mentioned in the query
8. When in doubt about a database tool or molecular biology tool, include it rather than exclude it
"""

        # Use the provided LLM or create a new one
        if llm is None:
            llm = ChatOpenAI(model="gpt-4o")

        # Invoke the LLM
        if hasattr(llm, "invoke"):
            # For LangChain-style LLMs
            response = llm.invoke([HumanMessage(content=prompt)])
            response_content = response.content
        else:
            # For other LLM interfaces
            response_content = str(llm(prompt))

        # Parse the response to extract the selected indices
        selected_indices = self._parse_llm_response(response_content)

        # Get the selected resources
        selected_resources = {
            "tools": [
                resources["tools"][i] for i in selected_indices.get("tools", []) if i < len(resources.get("tools", []))
            ],
            "data_lake": [
                resources["data_lake"][i]
                for i in selected_indices.get("data_lake", [])
                if i < len(resources.get("data_lake", []))
            ],
            "libraries": [
                resources["libraries"][i]
                for i in selected_indices.get("libraries", [])
                if i < len(resources.get("libraries", []))
            ],
        }

        return selected_resources

    def _format_resources_for_prompt(self, resources: list) -> str:
        """Format resources for inclusion in the prompt."""
        formatted = []
        for i, resource in enumerate(resources):
            if isinstance(resource, dict):
                # Handle dictionary format (from tool registry or data lake/libraries with descriptions)
                name = resource.get("name", f"Resource {i}")
                description = resource.get("description", "")
                formatted.append(f"{i}. {name}: {description}")
            elif isinstance(resource, str):
                # Handle string format (simple strings)
                formatted.append(f"{i}. {resource}")
            else:
                # Try to extract name and description from tool objects
                name = getattr(resource, "name", str(resource))
                desc = getattr(resource, "description", "")
                formatted.append(f"{i}. {name}: {desc}")

        return "\n".join(formatted) if formatted else "None available"

    def _parse_llm_response(self, response: str) -> dict:
        """Parse the LLM response to extract the selected indices."""
        selected_indices = {"tools": [], "data_lake": [], "libraries": []}

        # Extract indices for each category
        tools_match = re.search(r"TOOLS:\s*\[(.*?)\]", response, re.IGNORECASE)
        if tools_match and tools_match.group(1).strip():
            with contextlib.suppress(ValueError):
                selected_indices["tools"] = [int(idx.strip()) for idx in tools_match.group(1).split(",") if idx.strip()]

        data_lake_match = re.search(r"DATA_LAKE:\s*\[(.*?)\]", response, re.IGNORECASE)
        if data_lake_match and data_lake_match.group(1).strip():
            with contextlib.suppress(ValueError):
                selected_indices["data_lake"] = [
                    int(idx.strip()) for idx in data_lake_match.group(1).split(",") if idx.strip()
                ]

        libraries_match = re.search(r"LIBRARIES:\s*\[(.*?)\]", response, re.IGNORECASE)
        if libraries_match and libraries_match.group(1).strip():
            with contextlib.suppress(ValueError):
                selected_indices["libraries"] = [
                    int(idx.strip()) for idx in libraries_match.group(1).split(",") if idx.strip()
                ]

        return selected_indices

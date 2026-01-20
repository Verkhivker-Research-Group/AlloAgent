"""Vector database management for BIOMNI."""
import os
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def load_vectorstore(
    persist_directory: str = "./data/vectorstore",
    embedding_model: str = "text-embedding-3-small",
    collection_name: str = "biomni_resources"
) -> Optional[Chroma]:
    """Load an existing vectorstore from disk.
    
    Args:
        persist_directory: Directory where the vector store is persisted
        embedding_model: The embedding model to use
        collection_name: Name of the collection to load
        
    Returns:
        Loaded Chroma vectorstore or None if it doesn't exist
    """
    # Check if vectorstore exists on disk
    if not os.path.exists(persist_directory):
        print(f"⚠ Vector store not found at {persist_directory}")
        print("  Run rebuild_vectorstore() to create it.")
        return None
    
    try:
        embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Load existing vectorstore from disk (no API calls, fast)
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        # Get count of items
        collection = vectorstore._collection
        count = collection.count()
        
        print(f"✓ Loaded vector store from disk: {count} resources")
        return vectorstore
        
    except Exception as e:
        print(f"⚠ Failed to load vector store: {e}")
        print("  You may need to rebuild it with rebuild_vectorstore()")
        return None


def rebuild_vectorstore(
    resources: dict,
    persist_directory: str = "./data/vectorstore",
    embedding_model: str = "text-embedding-3-small",
    collection_name: str = "biomni_resources"
) -> Optional[Chroma]:
    """Rebuild the vectorstore from scratch with current resources.
    
    This function embeds all resources and creates a new vectorstore.
    Use this when:
    - Creating the vectorstore for the first time
    - Tool/data/library descriptions have been updated
    - You've added new datasets to allosteric_data_lake
    - Switching between allosteric and non-allosteric modes
    
    Args:
        resources: Dictionary with 'tools', 'data_lake', and 'libraries'
        persist_directory: Directory to persist the vector store
        embedding_model: The embedding model to use
        collection_name: Name of the collection
        
    Returns:
        Newly created Chroma vectorstore or None if failed
    """
    print("🔄 Rebuilding vector store from scratch...")
    print("   This will embed all resources and may take a moment...")
    
    try:
        embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Combine all resources into documents
        documents = []
        metadatas = []
        
        # Add tools (ONLY tools for vector similarity)
        for i, tool in enumerate(resources.get("tools", [])):
            if isinstance(tool, dict):
                text = f"Tool: {tool.get('name', '')}\n{tool.get('description', '')}"
                metadata = {
                    "type": "tool",
                    "index": i,
                    "name": tool.get("name", ""),
                    "module": tool.get("module", "")
                }
            else:
                text = f"Tool: {getattr(tool, 'name', '')}\n{getattr(tool, 'description', '')}"
                metadata = {
                    "type": "tool",
                    "index": i,
                    "name": getattr(tool, "name", "")
                }
            documents.append(text)
            metadatas.append(metadata)
        
        # NOTE: Data lake items and libraries are NOT added to vector store
        # They should be selected by other means (e.g., LLM-based or include all)
        
        # Delete old vectorstore if it exists
        if os.path.exists(persist_directory):
            import shutil
            shutil.rmtree(persist_directory)
            print(f"   Removed old vector store at {persist_directory}")
        
        # Create new vector store
        os.makedirs(persist_directory, exist_ok=True)
        vectorstore = Chroma.from_texts(
            texts=documents,
            embedding=embeddings,
            metadatas=metadatas,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        
        print(f"✓ Vector store rebuilt successfully!")
        print(f"   Location: {persist_directory}")
        print(f"   Tools embedded: {len(documents)}")
        print(f"   Data lake items: {len(resources.get('data_lake', []))} (not in vector store)")
        print(f"   Libraries: {len(resources.get('libraries', []))} (not in vector store)")
        
        return vectorstore
        
    except Exception as e:
        print(f"✗ Failed to rebuild vector store: {e}")
        return None


def delete_vectorstore(persist_directory: str = "./data/vectorstore") -> bool:
    """Delete the vectorstore from disk.
    
    Args:
        persist_directory: Directory where the vector store is persisted
        
    Returns:
        True if successfully deleted, False otherwise
    """
    if not os.path.exists(persist_directory):
        print(f"⚠ Vector store not found at {persist_directory}")
        return False
    
    try:
        import shutil
        shutil.rmtree(persist_directory)
        print(f"✓ Deleted vector store at {persist_directory}")
        return True
    except Exception as e:
        print(f"✗ Failed to delete vector store: {e}")
        return False

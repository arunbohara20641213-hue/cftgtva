"""
Embeddings configuration for Ollama local models.
Provides vector representations of text using local LLM embeddings.
"""

from langchain_ollama import OllamaEmbeddings
from config import settings


def initialize_embeddings() -> OllamaEmbeddings:
    """
    Initialize Ollama embeddings with nomic-embed-text.
    
    Returns:
        OllamaEmbeddings: Configured embeddings instance
        
    Raises:
        Exception: If Ollama is not running or model not available
    """
    try:
        embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        
        # Test embeddings by embedding a test phrase
        test_embedding = embeddings.embed_query("test")
        if len(test_embedding) > 0:
            print(f"✓ Embeddings initialized: {settings.OLLAMA_EMBEDDING_MODEL}")
            print(f"  Embedding dimension: {len(test_embedding)}")
            return embeddings
        else:
            raise Exception("Embeddings test returned empty vector")
            
    except Exception as e:
        raise Exception(
            f"Failed to initialize embeddings. "
            f"Ensure Ollama is running at {settings.OLLAMA_BASE_URL} "
            f"and model '{settings.OLLAMA_EMBEDDING_MODEL}' is available.\n"
            f"Error: {e}"
        )


if __name__ == "__main__":
    # Test embeddings initialization
    emb = initialize_embeddings()
    print("Embeddings test successful!")

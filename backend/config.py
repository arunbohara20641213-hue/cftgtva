"""
Configuration settings for the RAG system.
Manage Ollama models, ChromaDB paths, and RAG parameters.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama2"  # Options: llama2, llama3.1, mistral, neural-chat
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"  # Best for RAG
    OLLAMA_REQUEST_TIMEOUT: int = 300  # 5 minutes for local inference

    # ChromaDB Configuration
    CHROMA_DB_PATH: str = str(Path(__file__).parent / "storage" / "chroma")
    CHROMA_COLLECTION_NAME: str = "documents"

    # Text Processing Configuration
    CHUNK_SIZE: int = 1000  # Characters per chunk
    CHUNK_OVERLAP: int = 200  # 20% overlap for context continuity
    SEPARATOR: str = "\n\n"  # Primary separator for splitting

    # Retrieval Configuration
    RETRIEVAL_K: int = 3  # Number of documents to retrieve
    HYBRID_SEARCH_ENABLED: bool = True
    BM25_WEIGHT: float = 0.5  # Weight for BM25 in hybrid search (0-1)
    VECTOR_WEIGHT: float = 0.5  # Weight for vector similarity

    # Agent Configuration
    MAX_CONVERSATION_HISTORY: int = 10  # Max messages to keep in memory
    AGENT_MAX_ITERATIONS: int = 10  # Max iterations for agent reasoning
    AGENT_TEMPERATURE: float = 0.7  # LLM temperature (0=deterministic, 1=creative)

    # FastAPI Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # HTTP Client Configuration
    USER_AGENT: str = "RAG-System/1.0 (Document Q&A with Local LLM)"

    # Frontend Configuration
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


# Validation: Check Ollama connectivity at startup (optional)
def verify_ollama_connection() -> bool:
    """Verify Ollama is running and accessible."""
    import requests

    try:
        headers = {"User-Agent": settings.USER_AGENT}
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5,
            headers=headers
        )
        if response.status_code == 200:
            print(f"✓ Ollama connected at {settings.OLLAMA_BASE_URL}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Ollama connection failed: {e}")
        return False

    return False


if __name__ == "__main__":
    # Print current configuration on script execution
    print("RAG System Configuration:")
    print(f"  Ollama LLM: {settings.OLLAMA_LLM_MODEL}")
    print(f"  Embedding Model: {settings.OLLAMA_EMBEDDING_MODEL}")
    print(f"  ChromaDB Path: {settings.CHROMA_DB_PATH}")
    print(f"  Chunk Size: {settings.CHUNK_SIZE}")
    print(f"  Retrieval K: {settings.RETRIEVAL_K}")
    print(f"  FastAPI: {settings.API_HOST}:{settings.API_PORT}")
    verify_ollama_connection()

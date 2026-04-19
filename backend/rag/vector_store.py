"""
ChromaDB vector store initialization and operations.
Manages embedding and storage of documents for retrieval.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from typing import List, Optional
from pathlib import Path
from config import settings
from core.embeddings import initialize_embeddings
import logging

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Wrapper for ChromaDB vector store operations."""

    def __init__(self, embeddings: Optional[Embeddings] = None):
        """
        Initialize ChromaDB vector store.

        Args:
            embeddings: Embeddings model (uses Ollama if None)
        """
        if embeddings is None:
            embeddings = initialize_embeddings()

        self.embeddings = embeddings

        # Ensure storage directory exists
        Path(settings.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)

        # Initialize Chroma with persistent storage
        self.vector_store = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_DB_PATH,
        )

        logger.info(
            f"✓ ChromaDB initialized: {settings.CHROMA_DB_PATH} "
            f"(collection: {settings.CHROMA_COLLECTION_NAME})"
        )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to vector store.

        Args:
            documents: List of Document objects to index

        Returns:
            List of document IDs
        """
        try:
            ids = self.vector_store.add_documents(documents)
            logger.info(f"Added {len(ids)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def similarity_search(
        self, query: str, k: int = None
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        k = k or settings.RETRIEVAL_K
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Similarity search found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise

    def similarity_search_with_score(
        self, query: str, k: int = None
    ) -> List[tuple]:
        """
        Search with similarity scores.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (Document, score) tuples
        """
        k = k or settings.RETRIEVAL_K
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.debug(f"Scored search found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Scored search failed: {e}")
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.vector_store.delete_collection()
            logger.info("Deleted entire vector store collection")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        try:
            info = {
                "name": self.vector_store._collection.name,
                "count": self.vector_store._collection.count(),
            }
            logger.debug(f"Collection info: {info}")
            return info
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}


def initialize_vector_store(
    embeddings: Optional[Embeddings] = None,
) -> ChromaVectorStore:
    """
    Initialize and return a ChromaDB vector store instance.

    Args:
        embeddings: Custom embeddings model (uses Ollama if None)

    Returns:
        Initialized ChromaVectorStore instance
    """
    return ChromaVectorStore(embeddings=embeddings)

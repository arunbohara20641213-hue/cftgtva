"""
Hybrid retrieval system combining vector and BM25 keyword search.
Provides better recall for diverse query types.
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from .vector_store import ChromaVectorStore
from config import settings
import logging

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever combining vector and BM25 search."""

    def __init__(self, vector_store: ChromaVectorStore, documents: List[Document]):
        """
        Initialize hybrid retriever.

        Args:
            vector_store: ChromaDB vector store instance
            documents: All documents for BM25 indexing
        """
        self.vector_store = vector_store
        self.documents = documents

        # Initialize BM25 retriever (keyword-based)
        # Handle empty documents case - will be initialized lazily when documents are added
        if documents:
            self.bm25_retriever = BM25Retriever.from_documents(documents)
            self.bm25_retriever.k = settings.RETRIEVAL_K
        else:
            self.bm25_retriever = None
            logger.info("Initialized hybrid retriever with no documents (BM25 will be initialized when documents are added)")

        logger.info(
            f"Initialized hybrid retriever with {len(documents)} documents"
        )

    def retrieve(
        self,
        query: str,
        k: int = None,
        vector_weight: float = None,
        bm25_weight: float = None,
    ) -> List[Document]:
        """
        Perform hybrid search combining vector and keyword matching.

        Args:
            query: Search query
            k: Number of results (default from settings)
            vector_weight: Weight for vector search (0-1)
            bm25_weight: Weight for BM25 search (0-1)

        Returns:
            List of retrieved documents ranked by combined score
        """
        k = k or settings.RETRIEVAL_K
        vector_weight = vector_weight or settings.VECTOR_WEIGHT
        bm25_weight = bm25_weight or settings.BM25_WEIGHT

        # Normalize weights
        total_weight = vector_weight + bm25_weight
        vector_weight = vector_weight / total_weight
        bm25_weight = bm25_weight / total_weight

        # Vector search with scores
        try:
            vector_results = self.vector_store.similarity_search_with_score(
                query, k=k
            )
            vector_docs = {
                doc.metadata.get("id", i): (doc, 1.0 - score)
                for i, (doc, score) in enumerate(vector_results)
            }
        except Exception as e:
            logger.warning(f"Vector search failed: {e}, using BM25 only")
            vector_docs = {}

        # BM25 search
        try:
            if self.bm25_retriever is not None:
                bm25_docs_list = self.bm25_retriever.invoke(query)
                bm25_docs = {
                    doc.metadata.get("id", i): (doc, 1.0 - (i / k))
                    for i, doc in enumerate(bm25_docs_list)
                }
            else:
                bm25_docs = {}
        except Exception as e:
            logger.warning(f"BM25 search failed: {e}, using vector only")
            bm25_docs = {}

        # Combine and rank results
        combined_scores: Dict[str, tuple] = {}

        # Add vector results
        for doc_id, (doc, score) in vector_docs.items():
            combined_scores[doc_id] = (doc, vector_weight * score)

        # Add BM25 results with combined score
        for doc_id, (doc, score) in bm25_docs.items():
            if doc_id in combined_scores:
                _, existing_score = combined_scores[doc_id]
                combined_scores[doc_id] = (doc, existing_score + bm25_weight * score)
            else:
                combined_scores[doc_id] = (doc, bm25_weight * score)

        # Sort by score and return top k
        sorted_results = sorted(
            combined_scores.values(), key=lambda x: x[1], reverse=True
        )
        results = [doc for doc, _ in sorted_results[:k]]

        # Log retrieval results for observability
        logger.info(
            f"\n{'='*70}"
            f"\n[Retriever] Query: '{query}'"
            f"\n[Retriever] Top {min(len(results), 3)} documents retrieved:"
        )
        
        for i, doc in enumerate(results[:3], 1):
            source = doc.metadata.get("source", "unknown")
            preview = doc.page_content[:80].replace("\n", " ").strip()
            logger.info(
                f"\n  #{i}. Source: {source}"
                f"\n      Preview: {preview}..."
            )
        
        logger.info(f"\n{'='*70}\n")

        return results

    def retrieve_with_scores(
        self,
        query: str,
        k: int = None,
        vector_weight: float = None,
        bm25_weight: float = None,
    ) -> List[tuple]:
        """
        Retrieve documents with their combined scores.

        Returns:
            List of (Document, score) tuples
        """
        k = k or settings.RETRIEVAL_K
        vector_weight = vector_weight or settings.VECTOR_WEIGHT
        bm25_weight = bm25_weight or settings.BM25_WEIGHT

        # Normalize weights
        total_weight = vector_weight + bm25_weight
        vector_weight = vector_weight / total_weight
        bm25_weight = bm25_weight / total_weight

        # Get scores from both searches
        vector_results = self.vector_store.similarity_search_with_score(
            query, k=k
        )
        
        if self.bm25_retriever is not None:
            bm25_docs_list = self.bm25_retriever.invoke(query)
        else:
            bm25_docs_list = []

        vector_docs = {
            doc.metadata.get("id", i): (doc, 1.0 - score)
            for i, (doc, score) in enumerate(vector_results)
        }
        bm25_docs = {
            doc.metadata.get("id", i): (doc, 1.0 - (i / k))
            for i, doc in enumerate(bm25_docs_list)
        }

        # Combine scores
        combined_scores: Dict[str, tuple] = {}

        for doc_id, (doc, score) in vector_docs.items():
            combined_scores[doc_id] = (doc, vector_weight * score)

        for doc_id, (doc, score) in bm25_docs.items():
            if doc_id in combined_scores:
                _, existing_score = combined_scores[doc_id]
                combined_scores[doc_id] = (doc, existing_score + bm25_weight * score)
            else:
                combined_scores[doc_id] = (doc, bm25_weight * score)

        # Sort and return
        sorted_results = sorted(
            combined_scores.values(), key=lambda x: x[1], reverse=True
        )
        return sorted_results[:k]

    def update_documents(self, documents: List[Document]) -> None:
        """
        Update the retriever with new documents.
        Called when documents are added to the vector store.

        Args:
            documents: Updated list of all documents
        """
        self.documents = documents
        
        if documents:
            try:
                self.bm25_retriever = BM25Retriever.from_documents(documents)
                self.bm25_retriever.k = settings.RETRIEVAL_K
                logger.info(f"Updated BM25 retriever with {len(documents)} documents")
            except Exception as e:
                logger.error(f"Failed to update BM25 retriever: {e}")
                self.bm25_retriever = None
        else:
            self.bm25_retriever = None
            logger.info("BM25 retriever cleared (no documents)")


def create_hybrid_retriever(
    vector_store: ChromaVectorStore, documents: List[Document]
) -> HybridRetriever:
    """
    Factory function to create a hybrid retriever.

    Args:
        vector_store: ChromaDB vector store
        documents: All indexed documents

    Returns:
        Initialized HybridRetriever
    """
    return HybridRetriever(vector_store, documents)

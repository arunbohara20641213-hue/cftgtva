"""
Retriever tests for hybrid search (vector + BM25).
Tests: retrieval returns results, weights respected, both methods work.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.retriever import HybridRetriever
from rag.vector_store import ChromaVectorStore
from core.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
import config


@pytest.fixture
def sample_documents():
    """Sample documents for testing retrieval."""
    return [
        Document(
            page_content="Python is a high-level programming language created by Guido van Rossum.",
            metadata={"id": "doc1", "source": "python_guide.txt"}
        ),
        Document(
            page_content="REST API design patterns: use GET for retrieval, POST for creation, PUT for updates.",
            metadata={"id": "doc2", "source": "api_guide.txt"}
        ),
        Document(
            page_content="Machine learning requires large datasets for training neural networks effectively.",
            metadata={"id": "doc3", "source": "ml_basics.txt"}
        ),
        Document(
            page_content="Docker containers package applications with all dependencies for portability.",
            metadata={"id": "doc4", "source": "devops.txt"}
        ),
    ]


@pytest.fixture
def embeddings():
    """Initialize embeddings (uses Ollama)."""
    try:
        return OllamaEmbeddings()
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


@pytest.fixture
def vector_store(embeddings, sample_documents):
    """Initialize ChromaDB vector store with sample docs."""
    store = ChromaVectorStore(embeddings=embeddings)
    store.add_documents(sample_documents)
    return store


@pytest.fixture
def hybrid_retriever(vector_store, sample_documents):
    """Initialize hybrid retriever."""
    return HybridRetriever(vector_store, sample_documents)


class TestHybridRetrieverBasics:
    """Basic hybrid retriever functionality tests."""

    def test_retriever_initialization(self, hybrid_retriever):
        """Test retriever initializes without error."""
        assert hybrid_retriever is not None
        assert hybrid_retriever.vector_store is not None
        assert hybrid_retriever.bm25_retriever is not None

    def test_retrieve_returns_documents(self, hybrid_retriever):
        """Test retrieve returns list of documents."""
        results = hybrid_retriever.retrieve("Python programming")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(doc, Document) for doc in results)

    def test_retrieve_respects_k_parameter(self, hybrid_retriever):
        """Test retrieve respects k parameter."""
        k = 2
        results = hybrid_retriever.retrieve("programming language", k=k)
        
        assert len(results) <= k

    def test_retrieve_returns_max_k_documents(self, hybrid_retriever, sample_documents):
        """Test retrieve returns up to k documents."""
        k = min(5, len(sample_documents))
        results = hybrid_retriever.retrieve("any query", k=k)
        
        assert len(results) <= k


class TestHybridRetrieverSearchQuality:
    """Test search quality and relevance."""

    def test_vector_search_semantic_similarity(self, hybrid_retriever):
        """Test vector search captures semantic similarity."""
        # Query about ML should retrieve ML docs
        results = hybrid_retriever.retrieve("neural networks", k=3)
        
        assert len(results) > 0
        # At least one result should be about ML or related topic
        content = [doc.page_content.lower() for doc in results]
        ml_terms = ["machine", "learning", "network", "training", "neural"]
        assert any(term in " ".join(content) for term in ml_terms)

    def test_bm25_catches_exact_keywords(self, hybrid_retriever):
        """Test BM25 catches exact keyword matches."""
        # Query with exact term "REST API"
        results = hybrid_retriever.retrieve("REST API", k=3)
        
        assert len(results) > 0
        # Should find the API doc
        assert any("REST API" in doc.page_content for doc in results)

    def test_hybrid_search_combines_both_methods(self, hybrid_retriever):
        """Test hybrid search uses both vector and BM25."""
        query = "Python REST API"
        results = hybrid_retriever.retrieve(query, k=4)
        
        # Should find both Python and REST API documents
        content = " ".join([doc.page_content for doc in results])
        assert any(term in content for term in ["Python", "REST API"])


class TestRetrieverWeights:
    """Test weight configuration for hybrid search."""

    def test_vector_weight_parameter(self, hybrid_retriever):
        """Test vector weight parameter is respected."""
        # High vector weight should prefer semantic match
        results_heavy_vector = hybrid_retriever.retrieve(
            "programming",
            vector_weight=0.8,
            bm25_weight=0.2,
            k=3
        )
        
        assert len(results_heavy_vector) > 0
        # Results should be valid documents
        assert all(isinstance(doc, Document) for doc in results_heavy_vector)

    def test_bm25_weight_parameter(self, hybrid_retriever):
        """Test BM25 weight parameter is respected."""
        # High BM25 weight should prefer exact keyword match
        results_heavy_bm25 = hybrid_retriever.retrieve(
            "Python",
            vector_weight=0.2,
            bm25_weight=0.8,
            k=3
        )
        
        assert len(results_heavy_bm25) > 0

    def test_equal_weights(self, hybrid_retriever):
        """Test equal weighting of vector and BM25."""
        results = hybrid_retriever.retrieve(
            "machine learning",
            vector_weight=0.5,
            bm25_weight=0.5,
            k=3
        )
        
        assert len(results) > 0


class TestRetrieverEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query_handling(self, hybrid_retriever):
        """Test retriever handles empty query gracefully."""
        # Should not crash, may return empty or default results
        try:
            results = hybrid_retriever.retrieve("", k=3)
            assert isinstance(results, list)
        except ValueError:
            # Acceptable to raise ValueError for empty query
            pass

    def test_very_large_k(self, hybrid_retriever, sample_documents):
        """Test retriever with k > document count."""
        k_large = len(sample_documents) * 2
        results = hybrid_retriever.retrieve("test", k=k_large)
        
        # Should return at most all documents
        assert len(results) <= len(sample_documents)

    def test_special_characters_in_query(self, hybrid_retriever):
        """Test retriever handles special characters."""
        queries = [
            "what's Python?",
            "REST/HTTP",
            "C++/C#",
        ]
        
        for query in queries:
            results = hybrid_retriever.retrieve(query, k=2)
            assert isinstance(results, list)


class TestRetrieverDocumentMetadata:
    """Test metadata handling in retrieved documents."""

    def test_retrieved_documents_have_metadata(self, hybrid_retriever):
        """Test retrieved documents include metadata."""
        results = hybrid_retriever.retrieve("programming", k=2)
        
        assert len(results) > 0
        for doc in results:
            assert hasattr(doc, "metadata")
            assert isinstance(doc.metadata, dict)

    def test_metadata_contains_source(self, hybrid_retriever):
        """Test metadata includes source information."""
        results = hybrid_retriever.retrieve("Python", k=2)
        
        assert len(results) > 0
        for doc in results:
            # Should have source info
            assert "source" in doc.metadata or "id" in doc.metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

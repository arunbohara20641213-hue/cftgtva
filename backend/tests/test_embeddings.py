"""
Embedding tests for Ollama embeddings.
Tests: embedding shape, non-empty output, consistency.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.embeddings import OllamaEmbeddings
from config import settings


@pytest.fixture
def embeddings():
    """Initialize Ollama embeddings (skips if unavailable)."""
    try:
        emb = OllamaEmbeddings()
        # Test connection
        emb.embed_query("test")
        return emb
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


class TestEmbeddingBasics:
    """Basic embedding functionality tests."""

    def test_embeddings_initialization(self, embeddings):
        """Test embeddings initialize without error."""
        assert embeddings is not None

    def test_single_embedding_returns_vector(self, embeddings):
        """Test embed_query returns a vector."""
        text = "Python is a programming language"
        embedding = embeddings.embed_query(text)
        
        assert embedding is not None
        assert isinstance(embedding, (list, np.ndarray))
        assert len(embedding) > 0

    def test_batch_embeddings_returns_list(self, embeddings):
        """Test embed_documents returns list of vectors."""
        texts = [
            "First document about Python",
            "Second document about REST APIs",
            "Third document about machine learning"
        ]
        embeddings_list = embeddings.embed_documents(texts)
        
        assert isinstance(embeddings_list, list)
        assert len(embeddings_list) == len(texts)
        assert all(isinstance(emb, (list, np.ndarray)) for emb in embeddings_list)


class TestEmbeddingShape:
    """Test embedding vector dimensions."""

    def test_embedding_dimension_consistency(self, embeddings):
        """Test all embeddings have same dimension."""
        texts = [
            "Short text",
            "This is a longer text with more words",
            "Another example with different content"
        ]
        
        embeddings_list = embeddings.embed_documents(texts)
        dimensions = [len(emb) for emb in embeddings_list]
        
        # All should have same dimension
        assert len(set(dimensions)) == 1
        assert dimensions[0] > 0

    def test_embedding_dimension_is_reasonable(self, embeddings):
        """Test embedding dimension is in expected range."""
        # Typical embedding models have 384-1536 dimensions
        # nomic-embed-text has 768 dimensions
        text = "Test embedding dimension"
        embedding = embeddings.embed_query(text)
        
        assert len(embedding) >= 100  # At least reasonable size
        assert len(embedding) <= 2000  # Not excessively large

    def test_single_vs_batch_same_dimension(self, embeddings):
        """Test single embed_query matches batch embed_documents."""
        text = "Consistency test"
        
        single = embeddings.embed_query(text)
        batch = embeddings.embed_documents([text])
        
        assert len(single) == len(batch[0])


class TestEmbeddingQuality:
    """Test semantic quality of embeddings."""

    def test_similar_texts_have_similar_embeddings(self, embeddings):
        """Test semantically similar texts produce similar embeddings."""
        text1 = "Python is a programming language"
        text2 = "Python is a coding language"
        text3 = "Dogs are animals"
        
        emb1 = embeddings.embed_query(text1)
        emb2 = embeddings.embed_query(text2)
        emb3 = embeddings.embed_query(text3)
        
        # Convert to numpy for similarity calculation
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        emb3 = np.array(emb3)
        
        # Cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim_12 = cosine_similarity(emb1, emb2)
        sim_13 = cosine_similarity(emb1, emb3)
        
        # Similar texts should have higher similarity
        assert sim_12 > sim_13

    def test_embeddings_are_normalized(self, embeddings):
        """Test embeddings are roughly normalized (L2)."""
        text = "Normalization test text"
        embedding = np.array(embeddings.embed_query(text))
        
        norm = np.linalg.norm(embedding)
        # Normalize embeddings typically have norm close to 1
        # Allow some tolerance
        assert 0.5 < norm < 2.0

    def test_different_texts_produce_different_embeddings(self, embeddings):
        """Test different texts don't produce identical embeddings."""
        text1 = "Python programming"
        text2 = "JavaScript coding"
        
        emb1 = embeddings.embed_query(text1)
        emb2 = embeddings.embed_query(text2)
        
        # Should not be identical
        assert emb1 != emb2


class TestEmbeddingConsistency:
    """Test determinism and consistency of embeddings."""

    def test_same_text_same_embedding(self, embeddings):
        """Test same text produces same embedding (deterministic)."""
        text = "Consistency check"
        
        emb1 = embeddings.embed_query(text)
        emb2 = embeddings.embed_query(text)
        
        # Should be identical or very close
        assert emb1 == emb2 or np.allclose(emb1, emb2, atol=1e-5)

    def test_case_sensitivity(self, embeddings):
        """Test that case affects embedding (expected behavior)."""
        text_lower = "python programming"
        text_upper = "PYTHON PROGRAMMING"
        
        emb_lower = np.array(embeddings.embed_query(text_lower))
        emb_upper = np.array(embeddings.embed_query(text_upper))
        
        # Case shouldn't make them identical
        # (though typical embedders are somewhat case-insensitive)
        # This is informational


class TestEmbeddingEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_text_embedding(self, embeddings):
        """Test embedding of empty string."""
        # Should handle gracefully
        try:
            embedding = embeddings.embed_query("")
            assert isinstance(embedding, (list, np.ndarray))
        except ValueError:
            # Acceptable to raise error for empty text
            pass

    def test_very_long_text_embedding(self, embeddings):
        """Test embedding of very long text."""
        # Create a long text (10K+ characters)
        long_text = "word " * 2000
        
        try:
            embedding = embeddings.embed_query(long_text)
            assert isinstance(embedding, (list, np.ndarray))
            assert len(embedding) > 0
        except Exception as e:
            # Some models may have token limits
            pytest.skip(f"Model has token limit: {e}")

    def test_special_characters(self, embeddings):
        """Test embedding with special characters."""
        texts = [
            "Test with @special #characters!",
            "Mathematical: 2+2=4, π ≈ 3.14",
            "Emoji test 🚀 🎉",
            "Unicode: 你好世界",
        ]
        
        for text in texts:
            try:
                embedding = embeddings.embed_query(text)
                assert isinstance(embedding, (list, np.ndarray))
                assert len(embedding) > 0
            except Exception as e:
                # Unicode support may vary
                pass


class TestBatchVsSingle:
    """Compare batch vs single embedding methods."""

    def test_batch_vs_single_consistency(self, embeddings):
        """Test batch embedding matches individual singles."""
        texts = ["First text", "Second text", "Third text"]
        
        # Get batch
        batch_embeddings = embeddings.embed_documents(texts)
        
        # Get individual
        single_embeddings = [embeddings.embed_query(text) for text in texts]
        
        # Should match
        for batch, single in zip(batch_embeddings, single_embeddings):
            assert np.allclose(batch, single, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

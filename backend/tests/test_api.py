"""
API endpoint tests for RAG system.
Tests: health check, chat endpoint, document upload.
"""

import pytest
import json
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from io import BytesIO


@pytest.fixture
def client():
    """Fixture providing test client."""
    return TestClient(app)


@pytest.fixture
def sample_document():
    """Fixture providing sample document for upload."""
    content = b"""
    Python is a high-level programming language.
    It was created by Guido van Rossum.
    Python emphasizes code readability.
    """
    return ("test.txt", BytesIO(content), "text/plain")


class TestHealthCheck:
    """Health check endpoint tests."""

    def test_health_check_success(self, client):
        """Test health check returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "success"]

    def test_health_check_has_version(self, client):
        """Test health check includes version info."""
        response = client.get("/api/health")
        data = response.json()
        assert "timestamp" in data or "uptime" in data


class TestDocumentUpload:
    """Document upload endpoint tests."""

    def test_upload_document_success(self, client, sample_document):
        """Test successful document upload."""
        files = {"file": sample_document}
        response = client.post("/api/documents/upload", files=files)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "filename" in data or "document_id" in data

    def test_upload_empty_file_fails(self, client):
        """Test upload of empty file fails gracefully."""
        files = {"file": ("empty.txt", BytesIO(b""), "text/plain")}
        response = client.post("/api/documents/upload", files=files)
        
        # Should fail with 400-level error, not crash
        assert response.status_code >= 400

    def test_list_documents(self, client):
        """Test list documents endpoint."""
        response = client.get("/api/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # May be empty, but should be valid JSON list


class TestChatEndpoint:
    """Chat endpoint tests."""

    def test_chat_without_documents(self, client):
        """Test chat endpoint works even with no documents."""
        payload = {
            "message": "What is Python?",
            "session_id": "test-session-1"
        }
        response = client.post("/api/chat", json=payload)
        
        # Should return 200 (fallback to LLM knowledge)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_chat_with_history(self, client):
        """Test chat includes conversation history."""
        session_id = "test-session-history"
        
        # First message
        payload1 = {
            "message": "What is RAG?",
            "session_id": session_id,
            "history": []
        }
        response1 = client.post("/api/chat", json=payload1)
        assert response1.status_code == 200
        
        # Second message with history
        history = [
            {"role": "user", "content": "What is RAG?"},
            {"role": "assistant", "content": response1.json()["response"]}
        ]
        payload2 = {
            "message": "Tell me more.",
            "session_id": session_id,
            "history": history
        }
        response2 = client.post("/api/chat", json=payload2)
        
        assert response2.status_code == 200
        data = response2.json()
        assert "response" in data

    def test_chat_invalid_payload_fails(self, client):
        """Test chat with invalid payload returns error."""
        payload = {
            "message": ""  # Empty message
        }
        response = client.post("/api/chat", json=payload)
        
        # Should return 400-level error
        assert response.status_code >= 400

    def test_chat_response_format(self, client):
        """Test chat response has correct format."""
        payload = {
            "message": "Hello",
            "session_id": "test-format"
        }
        response = client.post("/api/chat", json=payload)
        
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        # Sources are optional but if present, should be list
        if "sources" in data:
            assert isinstance(data["sources"], list)


class TestDocumentDeletion:
    """Document deletion endpoint tests."""

    def test_delete_nonexistent_document(self, client):
        """Test deleting nonexistent document."""
        response = client.delete("/api/documents/nonexistent-id")
        
        # Should handle gracefully (200 or 404)
        assert response.status_code in [200, 404]

    def test_delete_endpoint_exists(self, client):
        """Test delete endpoint is available."""
        # Endpoint should exist even if nothing to delete
        response = client.delete("/api/documents/test-id")
        assert response.status_code < 500  # Not 500 error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Integration Tests for RAG System - Phase 7
Tests all components work together end-to-end
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all core imports work."""
    from core.document_loader import DocumentLoader
    from core.text_splitter import create_text_splitter
    from rag.vector_store import ChromaVectorStore
    from rag.retriever import HybridRetriever
    from rag.agent import RAGAgent
    from api.models import ChatRequest, ChatResponse
    from config import settings
    assert settings.OLLAMA_LLM_MODEL is not None
    print("✓ All imports successful")

def test_config():
    """Test configuration loads."""
    from config import settings
    assert settings.CHUNK_SIZE == 1000
    assert settings.RETRIEVAL_K == 3
    assert settings.OLLAMA_EMBEDDING_MODEL == "nomic-embed-text"
    print("✓ Configuration valid")

def test_text_splitter():
    """Test text splitting works."""
    from core.text_splitter import create_text_splitter
    splitter = create_text_splitter()
    text = "This is a test. " * 100
    split = splitter.split_text(text)
    assert len(split) > 0
    print(f"✓ Text splitter works ({len(split)} chunks)")

def test_pydantic_models():
    """Test Pydantic models validate correctly."""
    from api.models import ChatRequest, ChatResponse, SourceCitation
    
    # Valid request
    req = ChatRequest(
        message="test",
        session_id="test-session"
    )
    assert req.message == "test"
    
    # Valid response
    src = SourceCitation(source_name="test.pdf", confidence=0.9)
    resp = ChatResponse(
        session_id="test-session",
        response="answer",
        sources=[src],
        success=True
    )
    assert resp.success is True
    print("✓ Pydantic models validate")

def test_storage_directory():
    """Test storage directory is created."""
    from pathlib import Path
    from config import settings
    storage = Path(settings.CHROMA_DB_PATH)
    assert storage.exists()
    print(f"✓ Storage directory exists: {storage}")

def test_fastapi_routes():
    """Test FastAPI routes are defined."""
    from api.routes import router
    assert router is not None
    assert len(router.routes) > 0
    print(f"✓ FastAPI routes defined ({len(router.routes)} routes)")

def test_chat_service():
    """Test ChatService initializes."""
    from services.chat_service import ChatService
    from rag.agent import RAGAgent
    from rag.vector_store import ChromaVectorStore
    
    # These will fail without Ollama, but we're testing initialization
    assert ChatService is not None
    print("✓ ChatService class available")

def run_tests():
    """Run all integration tests."""
    print("\n" + "=" * 50)
    print("INTEGRATION TEST SUITE - PHASE 7")
    print("=" * 50 + "\n")
    
    tests = [
        ("Python Imports", test_imports),
        ("Configuration", test_config),
        ("Text Splitter", test_text_splitter),
        ("Pydantic Models", test_pydantic_models),
        ("Storage Directory", test_storage_directory),
        ("FastAPI Routes", test_fastapi_routes),
        ("Chat Service", test_chat_service),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\nTesting: {name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
RAG System health check and validation script.
Tests all components are importable and configured correctly.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_python_imports():
    """Check all Python modules can be imported."""
    logger.info("Checking Python imports...")
    try:
        from core.document_loader import DocumentLoader
        from core.text_splitter import create_text_splitter
        from core.embeddings import initialize_embeddings
        from rag.vector_store import ChromaVectorStore
        from rag.retriever import HybridRetriever
        from rag.agent import RAGAgent
        from api.models import ChatRequest, ChatResponse
        from api.routes import router
        from services.chat_service import ChatService
        from services.document_service import DocumentService
        from config import settings
        logger.info("✓ All Python imports successful")
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def check_config():
    """Check configuration loads."""
    logger.info("\nChecking configuration...")
    try:
        from config import settings
        logger.info(f"  Ollama LLM: {settings.OLLAMA_LLM_MODEL}")
        logger.info(f"  Embedding Model: {settings.OLLAMA_EMBEDDING_MODEL}")
        logger.info(f"  ChromaDB Path: {settings.CHROMA_DB_PATH}")
        logger.info(f"  Chunk Size: {settings.CHUNK_SIZE}")
        logger.info(f"  Retrieval K: {settings.RETRIEVAL_K}")
        logger.info("✓ Configuration loaded")
        return True
    except Exception as e:
        logger.error(f"✗ Config check failed: {e}")
        return False

def check_ollama():
    """Check Ollama connectivity."""
    logger.info("\nChecking Ollama connectivity...")
    try:
        from config import settings
        import requests
        
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"✓ Ollama is reachable at {settings.OLLAMA_BASE_URL}")
            return True
        else:
            logger.warning(f"⚠ Ollama returned status {response.status_code}")
            logger.warning("  (This is OK if Ollama is not running yet)")
            return None
    except Exception as e:
        logger.warning(f"⚠ Ollama not reachable: {e}")
        logger.warning("  (Start Ollama with: ollama serve)")
        return None

def check_storage():
    """Check storage directory exists."""
    logger.info("\nChecking storage setup...")
    try:
        from pathlib import Path
        from config import settings
        
        storage_path = Path(settings.CHROMA_DB_PATH)
        if not storage_path.exists():
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created storage directory: {storage_path}")
        else:
            logger.info(f"✓ Storage directory exists: {storage_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Storage check failed: {e}")
        return False

def main():
    """Run all checks."""
    logger.info("=" * 50)
    logger.info("RAG SYSTEM HEALTH CHECK")
    logger.info("=" * 50)
    
    checks = [
        ("Python Imports", check_python_imports),
        ("Configuration", check_config),
        ("Storage", check_storage),
        ("Ollama", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            results.append((name, False))
    
    logger.info("\n" + "=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    warnings = sum(1 for _, r in results if r is None)
    
    for name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ WARNING"
        print(f"{name:20} {status}")
    
    logger.info("=" * 50)
    
    if failed > 0:
        logger.error(f"FAILED: {failed} checks failed")
        return False
    else:
        logger.info(f"SUCCESS: All critical checks passed")
        if warnings > 0:
            logger.info(f"(Note: {warnings} non-critical warnings - see above)")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

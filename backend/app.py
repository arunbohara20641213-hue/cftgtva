"""
FastAPI application for RAG system.
Main entry point with service initialization and startup/shutdown handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from config import settings, verify_ollama_connection
from core.embeddings import initialize_embeddings
from rag.vector_store import initialize_vector_store
from rag.retriever import create_hybrid_retriever
from rag.agent import create_rag_agent
from services.chat_service import ChatService
from services.document_service import DocumentService
from api.routes import router, set_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global service instances
_chat_service: ChatService = None
_document_service: DocumentService = None
_vector_store = None
_rag_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global _chat_service, _document_service, _vector_store, _rag_agent

    logger.info("=== RAG System Starting ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    try:
        # Verify Ollama connection
        logger.info("Checking Ollama connectivity...")
        if not verify_ollama_connection():
            logger.warning("Ollama not reachable, but continuing...")

        # Initialize embeddings
        logger.info("Initializing embeddings...")
        embeddings = initialize_embeddings()

        # Initialize vector store
        logger.info("Initializing vector store...")
        _vector_store = initialize_vector_store(embeddings)

        # For now, create retriever with empty documents
        # In production, you'd load existing documents from the vector store
        _retriever = create_hybrid_retriever(_vector_store, [])

        # Initialize RAG agent
        logger.info("Initializing RAG agent...")
        _rag_agent = create_rag_agent(_vector_store, _retriever)

        # Initialize services
        logger.info("Initializing services...")
        _chat_service = ChatService(_rag_agent, _vector_store)
        _document_service = DocumentService()

        # Inject services into router
        set_services(_chat_service, _document_service)

        logger.info("RAG System started successfully")
        logger.info(f"FastAPI running on {settings.API_HOST}:{settings.API_PORT}")

    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise

    yield

    # Shutdown
    logger.info("=== RAG System Shutting Down ===")
    logger.info("Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation system for document Q&A",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "localhost:3000", "127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG System API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/api/status")
async def status():
    """Get system status."""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "chat": "active" if _chat_service else "inactive",
            "vector_store": "active" if _vector_store else "inactive",
            "rag_agent": "active" if _rag_agent else "inactive",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Use import string when reload is enabled for proper hot reloading
    if settings.API_RELOAD:
        uvicorn.run(
            "app:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
            log_level="info",
        )
    else:
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info",
        )

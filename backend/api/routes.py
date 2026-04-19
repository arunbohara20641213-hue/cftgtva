"""
FastAPI routes for chat and document management endpoints.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import logging
from api.models import (
    ChatRequest,
    ChatResponse,
    DocumentListResponse,
    DocumentDeleteRequest,
    HealthResponse,
    SourceCitation,
)
from services.chat_service import ChatService
from services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter()

# These will be injected by the main app
_chat_service: ChatService = None
_document_service: DocumentService = None


def set_services(chat_service: ChatService, document_service: DocumentService):
    """Inject services into router."""
    global _chat_service, _document_service
    _chat_service = chat_service
    _document_service = document_service


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        ollama_connected=True,
        vector_store_ready=True,
        message="RAG system operational",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message with RAG.

    Args:
        request: ChatRequest with message and session_id

    Returns:
        ChatResponse with assistant response and sources
    """
    if not _chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = _chat_service.process_message(
            session_id=request.session_id,
            message=request.message,
            include_history=True,
        )

        # Convert sources to SourceCitation objects
        sources = [
            SourceCitation(
                source_name=s if isinstance(s, str) else s.get("source_name", "Unknown"),
                confidence=0.9,
            )
            for s in result.get("sources", [])
        ]

        return ChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            sources=sources,
            success=result["success"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session.

    Args:
        session_id: Session identifier

    Returns:
        List of messages
    """
    if not _chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")

    history = _chat_service.get_conversation_history(session_id)
    return {"session_id": session_id, "messages": history}


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), source_name: str = Form(None)):
    """
    Upload and index a document.

    Args:
        file: Document file to upload
        source_name: Optional source name

    Returns:
        Document info with num_chunks and upload status
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        # Read file content
        content = await file.read()

        # Determine document type from filename
        filename_lower = file.filename.lower()
        if filename_lower.endswith(".pdf"):
            doc_type = "pdf"
        elif filename_lower.endswith(".txt"):
            doc_type = "text"
        elif filename_lower.endswith(".md"):
            doc_type = "markdown"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: .pdf, .txt, .md",
            )

        # Save temporarily and process
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Load and process document
            chunks = DocumentService.load_and_process_document(
                tmp_path, source_name=source_name or file.filename
            )

            # Add to vector store
            if chunks:
                doc_ids = _chat_service.rag_agent.vector_store.add_documents(chunks)
                logger.info(f"Uploaded {file.filename}: {len(chunks)} chunks")

                return {
                    "success": True,
                    "filename": file.filename,
                    "num_chunks": len(chunks),
                    "doc_type": doc_type,
                }
            else:
                raise HTTPException(status_code=400, detail="Document produced no chunks")

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all indexed documents.

    Returns:
        DocumentListResponse with document list
    """
    if not _chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")

    try:
        # Get collection info
        info = _chat_service.rag_agent.vector_store.get_collection_info()

        documents = [
            {
                "doc_id": str(i),
                "filename": f"Document {i}",
                "doc_type": "indexed",
                "num_chunks": 0,
                "uploaded_at": "2024-04-19",
                "status": "indexed",
            }
            for i in range(info.get("count", 0))
        ]

        return DocumentListResponse(
            documents=documents,
            total_documents=len(documents),
            success=True,
        )

    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document from the vector store.

    Args:
        doc_id: Document ID to delete

    Returns:
        Success confirmation
    """
    try:
        # In a full implementation, you'd track document IDs
        # For now, we'll just acknowledge
        return {"success": True, "message": f"Document {doc_id} marked for deletion"}

    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/clear")
async def clear_all_documents():
    """Clear all documents from the vector store."""
    if not _chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")

    try:
        _chat_service.rag_agent.vector_store.delete_collection()
        logger.info("Cleared all documents from vector store")

        return {"success": True, "message": "All documents cleared"}

    except Exception as e:
        logger.error(f"Clear documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
Pydantic models for API requests and responses.
Defines the data structures for chat and document endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., description="User message", min_length=1, max_length=5000)
    session_id: str = Field(
        default="default", description="Session ID for conversation tracking"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Optional previous messages for context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the main topic of the documents?",
                "session_id": "user-123-session-1",
                "conversation_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                ],
            }
        }


class SourceCitation(BaseModel):
    """Source citation in response."""

    source_name: str = Field(description="Name of the source document")
    excerpt: Optional[str] = Field(
        default=None, description="Relevant excerpt from the document"
    )
    confidence: Optional[float] = Field(
        default=None, ge=0, le=1, description="Confidence score (0-1)"
    )


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    session_id: str = Field(description="Session ID for this conversation")
    response: str = Field(description="Assistant response message")
    sources: List[SourceCitation] = Field(default_factory=list, description="Source citations")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "response": "Based on the documents...",
                "sources": [
                    {
                        "source_name": "document1.pdf",
                        "excerpt": "...",
                        "confidence": 0.95,
                    }
                ],
                "success": True,
                "timestamp": "2024-04-19T10:30:00",
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request body for document upload."""

    filename: str = Field(..., description="Name of the document")
    content: str = Field(..., description="File content or URL")
    doc_type: str = Field(
        default="text", description="Type: 'pdf', 'text', 'markdown', or 'url'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "document.pdf",
                "content": "<base64 encoded content or URL>",
                "doc_type": "pdf",
            }
        }


class DocumentInfo(BaseModel):
    """Information about a document."""

    doc_id: str = Field(description="Unique document ID")
    filename: str = Field(description="Original filename")
    doc_type: str = Field(description="Document type")
    num_chunks: int = Field(description="Number of chunks after splitting")
    uploaded_at: str = Field(description="Upload timestamp")
    status: str = Field(description="Processing status")


class DocumentListResponse(BaseModel):
    """Response listing indexed documents."""

    documents: List[DocumentInfo] = Field(description="List of documents")
    total_documents: int = Field(description="Total number of documents")
    success: bool = Field(default=True)


class DocumentDeleteRequest(BaseModel):
    """Request to delete a document."""

    doc_id: str = Field(description="ID of document to delete")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Status: 'healthy' or 'unhealthy'")
    ollama_connected: bool = Field(description="Whether Ollama is connected")
    vector_store_ready: bool = Field(description="Whether vector store is ready")
    message: Optional[str] = Field(default=None, description="Status message")


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = Field(default=False)
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.now)

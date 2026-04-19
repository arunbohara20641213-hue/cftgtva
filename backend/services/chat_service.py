"""
Chat service managing conversation state and RAG agent interaction.
Handles session management and message processing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .document_service import DocumentService
from rag.agent import RAGAgent
from rag.vector_store import ChromaVectorStore
from rag.retriever import HybridRetriever
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and RAG interactions."""

    def __init__(
        self,
        rag_agent: RAGAgent,
        vector_store: ChromaVectorStore,
    ):
        """
        Initialize chat service.

        Args:
            rag_agent: RAGAgent instance for processing queries
            vector_store: Vector store for document management
        """
        self.rag_agent = rag_agent
        self.vector_store = vector_store

        # Session storage: session_id -> {messages: [], created_at, last_active}
        self.sessions: Dict[str, Dict[str, Any]] = {}

        logger.info("Chat service initialized")

    def process_message(
        self, session_id: str, message: str, include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.

        Args:
            session_id: Session identifier
            message: User message
            include_history: Whether to include conversation history

        Returns:
            Response dict with response, sources, and metadata
        """
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "last_active": datetime.now(),
            }

        session = self.sessions[session_id]
        session["last_active"] = datetime.now()

        # Prepare conversation history
        history = None
        if include_history and session["messages"]:
            history = session["messages"][-10:]  # Last 10 messages

        try:
            # Get response from RAG agent
            result = self.rag_agent.invoke(message, conversation_history=history)

            # Add to session history
            session["messages"].append({"role": "user", "content": message})
            session["messages"].append(
                {"role": "assistant", "content": result["response"]}
            )

            # Keep only last 50 messages
            if len(session["messages"]) > 50:
                session["messages"] = session["messages"][-50:]

            logger.info(
                f"Session {session_id}: processed message ({len(result['response'])} chars)"
            )

            return {
                "session_id": session_id,
                "response": result["response"],
                "sources": result.get("sources", []),
                "success": result.get("success", True),
                "error": result.get("error"),
            }

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return {
                "session_id": session_id,
                "response": f"Error processing your message: {e}",
                "sources": [],
                "success": False,
                "error": str(e),
            }

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of message dicts with role and content
        """
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id].get("messages", [])

    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if cleared, False if session didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
            return True
        return False

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.

        Args:
            session_id: Session identifier

        Returns:
            Dict with session info or None
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "last_active": session["last_active"].isoformat(),
            "message_count": len(session["messages"]),
        }

    def cleanup_inactive_sessions(self, max_age_minutes: int = 60) -> int:
        """
        Remove sessions inactive for longer than max age.

        Args:
            max_age_minutes: Maximum inactivity age in minutes

        Returns:
            Number of sessions removed
        """
        from datetime import timedelta

        now = datetime.now()
        max_age = timedelta(minutes=max_age_minutes)

        sessions_to_remove = [
            sid
            for sid, session in self.sessions.items()
            if now - session["last_active"] > max_age
        ]

        for sid in sessions_to_remove:
            del self.sessions[sid]

        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} inactive sessions")

        return len(sessions_to_remove)

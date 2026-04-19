"""
Agentic RAG pipeline using LangChain LLM with simple reasoning.
The LLM decides when and how to search documents.
"""

from typing import Dict, Any, List, Optional
from langchain_ollama import OllamaLLM
from .vector_store import ChromaVectorStore
from .retriever import HybridRetriever
from .prompt_templates import (
    SYSTEM_PROMPT,
    RETRIEVAL_SYSTEM_PROMPT,
    format_context,
)
from config import settings
import logging
import re

logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Agentic RAG system using LangChain LLM.
    The LLM decides when to search documents vs. respond from knowledge.
    """

    def __init__(
        self,
        llm: OllamaLLM,
        vector_store: ChromaVectorStore,
        retriever: HybridRetriever,
    ):
        """
        Initialize RAG agent.

        Args:
            llm: OllamaLLM instance
            vector_store: ChromaDB vector store
            retriever: Hybrid retriever for searching
        """
        self.llm = llm
        self.vector_store = vector_store
        self.retriever = retriever
        logger.info("RAG Agent initialized")

    def invoke(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process user message through the agentic RAG.

        Args:
            message: User message
            conversation_history: Optional previous messages for context

        Returns:
            Dict with response, sources, and metadata
        """
        try:
            logger.info(f"Processing message: {message[:100]}...")

            # Build conversation context
            history_context = ""
            if conversation_history:
                history_lines = [
                    f"{msg['role']}: {msg['content'][:200]}"
                    for msg in conversation_history[-5:]
                ]
                history_context = "Previous conversation:\n" + "\n".join(history_lines) + "\n\n"

            # Retrieve relevant documents
            logger.info("Retrieving documents...")
            docs = self.retriever.retrieve(message, k=settings.RETRIEVAL_K)
            has_context = bool(docs)

            # Format retrieved documents
            context_str = ""
            if has_context:
                context_str = format_context(docs, max_length=8000)
                logger.info(f"Retrieved {len(docs)} documents")

            # Build the prompt based on whether we have context
            if has_context:
                prompt = f"""{RETRIEVAL_SYSTEM_PROMPT}

{history_context}

Retrieved Documents:
{context_str}

User Question: {message}

Provide a helpful answer. If the documents help answer the question, cite them."""
            else:
                prompt = f"""{SYSTEM_PROMPT}

{history_context}

User Question: {message}

Respond based on your knowledge."""

            # Get LLM response
            logger.info("Invoking LLM...")
            response = self.llm.invoke(prompt)

            # Extract sources from response and retrieved documents
            sources = self._extract_sources(response, docs)

            logger.info(f"Response generated: {len(response)} chars, {len(sources)} sources")

            return {
                "response": response,
                "sources": sources,
                "success": True,
                "error": None,
                "metadata": {
                    "docs_retrieved": len(docs),
                    "has_context": has_context,
                },
            }

        except Exception as e:
            logger.error(f"Agent error: {str(e)}", exc_info=True)
            return {
                "response": "",
                "sources": [],
                "success": False,
                "error": str(e),
                "metadata": {"error_type": type(e).__name__},
            }

    def _extract_sources(
        self, response: str, docs: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract source citations from LLM response and retrieved docs.

        Args:
            response: LLM response text
            docs: List of retrieved documents

        Returns:
            List of source citations
        """
        sources = []
        seen = set()

        # Extract from response text using patterns
        patterns = [
            r"(?:according to|from|based on)\s+(?:the\s+)?(.+?)(?:\.|,|\n|$)",
            r"\[(.+?)\]",
            r"(?:document|source):\s*(.+?)(?:\.|,|\n|$)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches[:3]:
                match = match.strip().strip("\"'")
                if match and len(match) > 2 and match not in seen:
                    sources.append(
                        {
                            "source_name": match,
                            "confidence": 0.7,
                        }
                    )
                    seen.add(match)

        # Add source names from retrieved documents
        for doc in docs[:3]:
            if hasattr(doc, "metadata"):
                source = doc.metadata.get(
                    "source_name",
                    doc.metadata.get("source", "Document"),
                )
                if source and source not in seen:
                    sources.append(
                        {
                            "source_name": source,
                            "confidence": 0.9,
                        }
                    )
                    seen.add(source)

        return sources[:5]  # Return max 5 sources


def create_rag_agent(
    llm: OllamaLLM,
    vector_store: ChromaVectorStore,
    retriever: HybridRetriever,
) -> RAGAgent:
    """Factory function to create a RAG agent."""
    return RAGAgent(llm, vector_store, retriever)

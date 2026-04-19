"""
Document service for managing document operations.
Handles loading, processing, batching, and metadata management.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.document_loader import DocumentLoader
from core.text_splitter import split_documents
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document loading and processing operations."""

    @staticmethod
    def load_and_process_document(
        file_path: str,
        source_name: Optional[str] = None,
        **metadata,
    ) -> List[Document]:
        """
        Load a document and process it into chunks.

        Args:
            file_path: Path to document file or URL
            source_name: Name to identify the source
            **metadata: Additional metadata to attach

        Returns:
            List of processed Document chunks
        """
        # Determine source name from file if not provided
        if source_name is None:
            source_name = Path(file_path).stem if not file_path.startswith(
                "http"
            ) else file_path

        # Load document
        try:
            docs = DocumentLoader.load_document(file_path)
            logger.info(f"Loaded {len(docs)} pages/sections from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise

        # Add metadata
        metadata["uploaded_at"] = datetime.now().isoformat()
        metadata["file_path"] = file_path
        docs = DocumentLoader.add_metadata(docs, source_name, **metadata)

        # Split into chunks
        chunks = split_documents(docs)
        logger.info(f"Processed into {len(chunks)} chunks")

        return chunks

    @staticmethod
    def load_batch(file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Load multiple documents and return metadata about each.

        Args:
            file_paths: List of file paths or URLs to load

        Returns:
            List of dicts with 'source_name', 'chunks', 'file_path', 'num_chunks'
        """
        results = []

        for file_path in file_paths:
            try:
                chunks = DocumentService.load_and_process_document(file_path)
                result = {
                    "source_name": Path(file_path).stem
                    if not str(file_path).startswith("http")
                    else file_path,
                    "chunks": chunks,
                    "file_path": file_path,
                    "num_chunks": len(chunks),
                    "status": "success",
                }
                results.append(result)
                logger.info(f"✓ Loaded {file_path}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"✗ Failed to load {file_path}: {e}")
                results.append(
                    {
                        "file_path": file_path,
                        "status": "failed",
                        "error": str(e),
                    }
                )

        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(
            f"Batch processing complete: {success_count}/{len(file_paths)} successful"
        )
        return results

    @staticmethod
    def get_document_stats(chunks: List[Document]) -> Dict[str, Any]:
        """
        Get statistics about a set of document chunks.

        Args:
            chunks: List of Document chunks

        Returns:
            Dict with stats: total_chars, total_tokens (est.), num_chunks, avg_size
        """
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        num_chunks = len(chunks)
        avg_size = total_chars // max(num_chunks, 1)

        # Rough token estimation (1 token ~= 4 chars)
        est_tokens = total_chars // 4

        return {
            "num_chunks": num_chunks,
            "total_characters": total_chars,
            "estimated_tokens": est_tokens,
            "average_chunk_size": avg_size,
        }

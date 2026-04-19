"""
Multi-format document loader for PDFs, text files, Markdown, and web URLs.
Provides unified interface for loading different document types.
"""

from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document
import logging

from config import settings

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load documents from various sources: PDFs, text, markdown, URLs."""

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """Load a PDF file and return list of documents (one per page)."""
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded PDF: {file_path} ({len(docs)} pages)")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {e}")
            raise

    @staticmethod
    def load_text_file(file_path: str, encoding: str = "utf-8") -> List[Document]:
        """Load a text file."""
        try:
            loader = TextLoader(file_path, encoding=encoding)
            docs = loader.load()
            logger.info(f"Loaded text file: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
            raise

    @staticmethod
    def load_markdown(file_path: str) -> List[Document]:
        """Load a Markdown file (treated as text)."""
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            logger.info(f"Loaded markdown: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load markdown {file_path}: {e}")
            raise

    @staticmethod
    def load_web_url(url: str) -> List[Document]:
        """Load content from a web URL."""
        try:
            # Create headers with USER_AGENT to identify requests
            headers = {
                "User-Agent": settings.USER_AGENT
            }
            loader = WebBaseLoader(url, headers=headers)
            docs = loader.load()
            logger.info(f"Loaded web URL: {url}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            raise

    @staticmethod
    def load_directory(dir_path: str, pattern: str = "**/*.pdf") -> List[Document]:
        """Load all matching files from a directory."""
        try:
            loader = DirectoryLoader(
                dir_path,
                glob=pattern,
                loader_cls=PyPDFLoader,
                show_progress=True,
            )
            docs = loader.load()
            logger.info(f"Loaded directory {dir_path}: {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Failed to load directory {dir_path}: {e}")
            raise

    @staticmethod
    def load_document(file_path: str) -> List[Document]:
        """
        Auto-detect file type and load accordingly.

        Supports: .pdf, .txt, .md, and URLs (starting with http)
        """
        file_path = str(file_path).lower()

        # Handle URLs
        if file_path.startswith(("http://", "https://")):
            return DocumentLoader.load_web_url(file_path)

        # Handle local files
        path = Path(file_path)

        if path.suffix == ".pdf":
            return DocumentLoader.load_pdf(file_path)
        elif path.suffix == ".txt":
            return DocumentLoader.load_text_file(file_path)
        elif path.suffix == ".md":
            return DocumentLoader.load_markdown(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported types: .pdf, .txt, .md, or URLs"
            )

    @staticmethod
    def add_metadata(docs: List[Document], source_name: str, **kwargs) -> List[Document]:
        """
        Add or update metadata for all documents.

        Args:
            docs: List of documents
            source_name: Name to use as the source
            **kwargs: Additional metadata fields
        """
        for doc in docs:
            doc.metadata["source_name"] = source_name
            doc.metadata["original_source"] = doc.metadata.get("source", "unknown")
            for key, value in kwargs.items():
                doc.metadata[key] = value
        return docs

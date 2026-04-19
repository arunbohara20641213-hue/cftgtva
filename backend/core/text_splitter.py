"""
Text splitting strategies for preparing documents for embedding.
Provides semantic chunking with configurable parameters.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from config import settings
import logging

logger = logging.getLogger(__name__)


def create_text_splitter(
    chunk_size: int = None,
    chunk_overlap: int = None,
    separators: List[str] = None,
) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter with specified parameters.

    Args:
        chunk_size: Characters per chunk (default from settings)
        chunk_overlap: Overlap between chunks (default from settings)
        separators: List of separators to use (hierarchical)

    Returns:
        Configured RecursiveCharacterTextSplitter instance
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    # Default separators: paragraphs -> sentences -> words -> characters
    if separators is None:
        separators = [
            "\n\n",  # Paragraph breaks
            "\n",  # Line breaks
            ". ",  # Sentence breaks
            " ",  # Word breaks
            "",  # Character level fallback
        ]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
        is_separator_regex=False,
    )

    logger.info(
        f"Created text splitter: chunk_size={chunk_size}, "
        f"chunk_overlap={chunk_overlap}"
    )
    return splitter


def split_documents(
    documents: List[Document],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Document]:
    """
    Split a list of documents into chunks.

    Args:
        documents: List of Document objects to split
        chunk_size: Characters per chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of split Document objects with preserved metadata
    """
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    splits = splitter.split_documents(documents)

    logger.info(
        f"Split {len(documents)} documents into {len(splits)} chunks "
        f"(avg {len(splits) // max(len(documents), 1)} chunks per doc)"
    )
    return splits


def split_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[str]:
    """
    Split raw text into chunks (without Document wrapper).

    Args:
        text: Raw text to split
        chunk_size: Characters per chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks

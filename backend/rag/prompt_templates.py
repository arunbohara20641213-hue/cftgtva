"""
Prompt templates for RAG system.
Defines system prompts and context formatting for agentic RAG.
"""

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on provided documents.

Your responsibilities:
1. Answer questions accurately using only the provided document context
2. If the answer is not in the documents, explicitly state "I don't have information about that in the provided documents"
3. Cite the source document when using information from it
4. Maintain a conversational tone while being precise
5. Ask clarifying questions if the user's query is ambiguous

Important rules:
- Treat the provided context as factual and authoritative
- Do not make up information or use knowledge outside the documents
- Be transparent about the limitations of the documents
- If multiple documents contain relevant information, synthesize across them
"""

RETRIEVAL_SYSTEM_PROMPT = """You are an expert at determining when to search documents for information.

Your role:
1. Decide if the user's query requires searching the documents
2. If the user is asking a general question or making conversation, respond without searching
3. If the user asks for specific information that might be in the documents, use the search tool
4. Always be helpful and natural in your responses

Use the search_documents tool when:
- The user asks specific questions about document content
- The user requests information that might be in the documents
- The user wants summaries or analysis of the documents

Don't use the search tool when:
- The user is making small talk or asking general knowledge questions
- The user is asking for help with formatting or other non-document tasks
- The conversation doesn't require document information
"""

CONTEXT_FORMAT = """<documents>
{context}
</documents>

Cite the source when using information: "According to [source], ..."
"""

RAG_PROMPT = """{context}

Based on the documents above, answer the following question:
{question}

If the information is not in the documents, say so explicitly."""


def get_system_prompt() -> str:
    """Get the main system prompt for the RAG agent."""
    return SYSTEM_PROMPT


def get_retrieval_system_prompt() -> str:
    """Get the system prompt for the retrieval decision agent."""
    return RETRIEVAL_SYSTEM_PROMPT


def format_context(documents: list, max_context_length: int = 8000) -> str:
    """
    Format retrieved documents for inclusion in prompt.

    Args:
        documents: List of Document objects
        max_context_length: Maximum characters to include

    Returns:
        Formatted context string
    """
    context_parts = []
    total_length = 0

    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source_name", f"Document {i}")
        content = doc.page_content

        # Truncate if adding this doc would exceed max length
        available_length = max_context_length - total_length
        if len(content) > available_length:
            content = content[:available_length] + "..."
            context_parts.append(f"Source: {source}\n{content}")
            break
        else:
            context_parts.append(f"Source: {source}\n{content}")
            total_length += len(content) + len(source) + 20

    if not context_parts:
        return "No relevant documents found."

    return "\n\n---\n\n".join(context_parts)


def format_rag_context(
    question: str, documents: list, max_context_length: int = 8000
) -> str:
    """
    Format a RAG prompt with question and context.

    Args:
        question: User question
        documents: Retrieved documents
        max_context_length: Max context length

    Returns:
        Formatted prompt
    """
    context = format_context(documents, max_context_length)
    return RAG_PROMPT.format(context=context, question=question)


def format_conversation_context(
    messages: list, max_history_length: int = 2000
) -> str:
    """
    Format conversation history for context.

    Args:
        messages: List of (role, content) tuples
        max_history_length: Max history to include

    Returns:
        Formatted conversation string
    """
    conversation = []
    total_length = 0

    for role, content in reversed(messages):  # Reverse to include most recent
        msg_text = f"{role.upper()}: {content}\n"
        if total_length + len(msg_text) <= max_history_length:
            conversation.insert(0, msg_text)
            total_length += len(msg_text)
        else:
            break

    if not conversation:
        return ""

    return "Previous conversation:\n" + "".join(conversation)

from typing import List, Tuple
from langchain_core.documents import Document
from langchain_core.tools import tool

from app.data.data_embedding import get_vectorstore


@tool
def similarity_search_with_score_tool(query: str, k: int = 3) -> str:
    """
    Retrieve top-k similar documents with similarity scores.
    
    Args:
        query: The search query string
        k: Number of top documents to retrieve (default: 3)
        
    Returns:
        Formatted string containing retrieved documents with scores
    """
    vectorstore = get_vectorstore()
    results: List[Tuple[Document, float]] = (
        vectorstore.similarity_search_with_score(query, k)
    )

    if not results:
        return "No relevant documents found."

    text_pieces: List[str] = []

    for idx, (doc, score) in enumerate(results, 1):
        text_pieces.append(
            f"Document {idx}:\n"
            f"Score: {score:.4f}\n"
            f"Source: {doc.metadata.get('source', 'Unknown')}\n"
            f"Content:\n{doc.page_content}\n"
        )

    return "\n" + "=" * 60 + "\n".join(text_pieces)

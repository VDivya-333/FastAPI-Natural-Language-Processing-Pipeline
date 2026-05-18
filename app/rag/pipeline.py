import logging
from typing import List
from app.rag.retriever import retrieve_documents
from app.services.reranker_service import rerank
from app.core.constants import RAG_CONTEXT_COUNT

logger = logging.getLogger(__name__)

def build_context(query: str) -> str:
    """
    Orchestrates the retrieval and reranking process to create a context string.
    
    Args:
        query: The input text/query to find context for.
        
    Returns:
        A string containing the concatenated top-ranked documents.
    """
    try:
        # 1. Retrieve initial candidate documents
        retrieved_data = retrieve_documents(query)
        if not retrieved_data:
            return ""
        docs = [item["text"] for item in retrieved_data]

        # 2. Rerank candidates based on task relevance
        ranked_docs = rerank(query, docs)

        # 3. Join the top N documents into a single context block
        return "\n".join(ranked_docs[:RAG_CONTEXT_COUNT])
    except Exception as e:
        logger.error(f"Failed to build RAG context for query '{query}': {e}")
        return ""
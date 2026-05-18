from typing import List, Dict, Any
from app.rag.vector_store import get_collection
from app.services.embedding_service import create_embedding
from app.core.constants import TOP_K_RESULTS

def retrieve_documents(query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
    """
    Retrieves the most relevant document snippets from ChromaDB based on query embedding.
    """
    try:
        query_embedding = create_embedding(query)

        collection = get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        structured_results = []
        if results.get("ids") and results["ids"]:
            for i in range(len(results["ids"][0])):
                structured_results.append({
                    "doc_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "score": results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                })
        return structured_results
    except Exception:
        return []
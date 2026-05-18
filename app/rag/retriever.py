import uuid

from app.core.constants import TOP_K_RESULTS
from app.rag.vector_store import get_collection
from app.services.embedding_service import create_embedding


def retrieve_documents(query: str, top_k: int = TOP_K_RESULTS):
    collection = get_collection()
    embedding = create_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
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


def store_documents(text: str):
    """Generates an embedding and stores the document in ChromaDB."""
    collection = get_collection()
    embedding = create_embedding(text)
    doc_id = str(uuid.uuid4())
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
    )
    return doc_id

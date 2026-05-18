from app.rag.vector_store import get_collection
from app.services.embedding_service import create_embedding


def ingest_document(doc_id: str, text: str):

    embedding = create_embedding(text)
    collection = get_collection()
    
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding]
    )
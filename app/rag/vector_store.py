import chromadb

from app.core.config import settings

_COLLECTION_NAME = "nlp_rag_collection"

# NOTE:
# Do NOT create Chroma client/collection at import time.
# This app is started by uvicorn which imports modules on startup.
# If Chroma is not running yet, the whole API crashes.
_collection = None
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    return _client


def get_collection():
    """Get (and lazily initialize) the Chroma collection.

    Raises a clear error only when the collection is actually needed.
    """
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(name=_COLLECTION_NAME)
    return _collection


import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

# Global ChromaDB client instance
_chroma_client = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB client."""
    global _chroma_client

    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            )
        )

    return _chroma_client


def get_collection(collection_name: str = None):
    """Get or create a ChromaDB collection."""
    client = get_chroma_client()
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

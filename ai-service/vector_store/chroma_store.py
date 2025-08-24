# ai-service/vector_store/chroma_store.py
from typing import List, Dict, Optional
import chromadb
from .embeddings import embed_texts

# Persistent DB under project root; change path if you prefer
_client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(name: str):
    # cosine space is recommended for normalized embeddings
    return _client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )

def index_chunks(
    collection_name: str,
    doc_id: str,
    chunks: List[str],
    base_metadata: Optional[Dict] = None
) -> int:
    """
    Adds chunked text + embeddings to Chroma.
    Returns number of chunks indexed.
    """
    col = get_collection(collection_name)
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    metas = [
        {**(base_metadata or {}), "doc_id": doc_id, "chunk_index": i}
        for i in range(len(chunks))
    ]
    vectors = embed_texts(chunks)
    col.add(ids=ids, documents=chunks, metadatas=metas, embeddings=vectors)
    return len(chunks)

def query_similar(
    collection_name: str,
    query_text: str,
    top_k: int = 5
):
    """
    Simple similarity search (we’ll wire this into an endpoint later).
    """
    col = get_collection(collection_name)
    qvec = embed_texts([query_text])[0]
    return col.query(query_embeddings=[qvec], n_results=top_k)

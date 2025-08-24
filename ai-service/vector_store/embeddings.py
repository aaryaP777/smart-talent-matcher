# ai-service/vector_store/embeddings.py
from typing import List
from sentence_transformers import SentenceTransformer

_model = None

def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        # small, fast, great for semantic search
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedder()
    # normalize for cosine similarity in Chroma
    vecs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return vecs.tolist()

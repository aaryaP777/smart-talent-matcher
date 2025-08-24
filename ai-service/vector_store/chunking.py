# ai-service/vector_store/chunking.py
from typing import List

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    chunks, i = [], 0
    n = len(text)
    while i < n:
        chunk = text[i:i+max_chars]
        if chunk.strip():
            chunks.append(chunk.strip())
        i += max_chars - overlap if max_chars > overlap else max_chars
    return chunks

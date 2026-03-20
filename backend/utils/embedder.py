from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

_model = None

def get_model() -> SentenceTransformer:
    """
    Lazy-loads the model on first call.
    Downloads ~80MB on first run, then cached locally.
    Uses all-MiniLM-L6-v2: fast, accurate, free.
    """
    global _model
    if _model is None:
        print("[Embedder] Loading all-MiniLM-L6-v2...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[Embedder] Model loaded")
    return _model

def embed(text: str) -> List[float]:
    """
    Converts text to a 384-dimensional embedding vector.
    Truncates to first 2000 chars to stay within model limits.
    Returns a normalized float list.
    """
    model = get_model()
    vec = model.encode(
        text[:2000],
        normalize_embeddings=True,
        show_progress_bar=False
    )
    return vec.tolist()

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Computes cosine similarity between two embedding vectors.
    Returns float between 0.0 and 1.0.
    Vectors must already be normalized (embed() does this).
    """
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))

def score_to_100(similarity: float) -> float:
    """Converts 0.0-1.0 cosine score to 0-100 scale."""
    return round(similarity * 100, 1)

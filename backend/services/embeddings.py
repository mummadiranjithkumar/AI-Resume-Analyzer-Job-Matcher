from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


_MODEL: Optional[SentenceTransformer] = None
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_model() -> SentenceTransformer:
    """
    Lazily load and cache the sentence-transformers model.
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_texts(model: SentenceTransformer, texts: Sequence[str]) -> np.ndarray:
    """
    Embed a list of texts into a 2D numpy array [n_texts, dim].
    """
    if not texts:
        return np.zeros((0, model.get_sentence_embedding_dimension()), dtype="float32")
    embeddings = model.encode(list(texts), convert_to_numpy=True, show_progress_bar=False)
    return embeddings.astype("float32")


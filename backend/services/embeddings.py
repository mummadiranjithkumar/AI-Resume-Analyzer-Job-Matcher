from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


# 🔥 Global cached model
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


def embed_texts(model, texts):
    if not texts:
        dim = model.get_sentence_embedding_dimension()
        return np.zeros((0, dim), dtype="float32")

    return model.encode(
        list(texts),
        batch_size=8,   # 🔥 REDUCED (IMPORTANT)
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    ).astype("float32")
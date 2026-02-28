from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
import json

from .parser import DATA_DIR


FAISS_DIR = DATA_DIR / "faiss_index"


def _index_path(resume_id: str) -> Path:
    return FAISS_DIR / f"{resume_id}.index"


def _chunks_path(resume_id: str) -> Path:
    return FAISS_DIR / f"{resume_id}_chunks.json"


def create_and_persist_index(
    resume_id: str,
    chunks: List[str],
    vectors: np.ndarray,
) -> None:
    """
    Create a FAISS index for the given resume chunks and persist index + metadata.
    """
    if vectors.ndim != 2:
        raise ValueError("Vectors must be a 2D array.")

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(_index_path(resume_id)))

    with _chunks_path(resume_id).open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_index_and_chunks(resume_id: str) -> Tuple[faiss.IndexFlatL2, List[str]]:
    """
    Load a FAISS index and associated chunk metadata for a resume.
    """
    index_path = _index_path(resume_id)
    chunks_path = _chunks_path(resume_id)

    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError(f"FAISS index for resume_id={resume_id} not found.")

    index = faiss.read_index(str(index_path))
    with chunks_path.open("r", encoding="utf-8") as f:
        chunks: List[str] = json.load(f)
    return index, chunks


def search_top_k(
    index: faiss.IndexFlatL2,
    chunks: List[str],
    query_vector: np.ndarray,
    k: int = 5,
) -> List[str]:
    """
    Search top-k most similar chunks for the given query vector.
    """
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    k = min(k, len(chunks))
    if k == 0:
        return []

    distances, indices = index.search(query_vector, k)
    idxs = indices[0]
    return [chunks[i] for i in idxs if 0 <= i < len(chunks)]


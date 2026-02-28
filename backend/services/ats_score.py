from __future__ import annotations

from typing import Iterable, List, Set

import numpy as np

from backend.models.schemas import InternalATSComputationResult
from backend.services import embeddings


def _normalize_tokens(tokens: Iterable[str]) -> Set[str]:
    return {t.lower() for t in tokens}


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.ndim == 2:
        a = a[0]
    if b.ndim == 2:
        b = b[0]
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
    return float(np.dot(a, b) / denom)


def compute_ats_score(
    resume_text: str,
    job_description: str,
    job_keywords: List[str],
) -> InternalATSComputationResult:
    """
    Compute a simple ATS-style score using:
    - keyword overlap between resume and provided job keywords
    - embedding-based semantic similarity between resume and job description
    - basic section completeness heuristics.
    """
    # Keyword overlap
    resume_tokens = resume_text.lower().split()
    resume_set = _normalize_tokens(resume_tokens)
    job_kw_set = _normalize_tokens(job_keywords)

    matched_keywords = sorted(resume_set & job_kw_set)
    missing_keywords = sorted(job_kw_set - resume_set)

    if job_kw_set:
        keyword_match_score = 100.0 * len(matched_keywords) / len(job_kw_set)
    else:
        keyword_match_score = 0.0

    # Semantic similarity using sentence-transformers
    try:
        model = embeddings.get_embedding_model()
        embed_resume = embeddings.embed_texts(model, [resume_text])
        embed_job = embeddings.embed_texts(model, [job_description])
        sim = _cosine_similarity(embed_resume, embed_job)
        semantic_similarity_score = max(0.0, min(1.0, sim))
    except Exception:
        semantic_similarity_score = 0.0

    # Section completeness heuristics
    text_lower = resume_text.lower()
    sections_present = 0
    total_sections = 4
    if "experience" in text_lower or "work history" in text_lower:
        sections_present += 1
    if "education" in text_lower:
        sections_present += 1
    if "skills" in text_lower:
        sections_present += 1
    if "projects" in text_lower or "project" in text_lower:
        sections_present += 1

    section_completeness_score = 100.0 * sections_present / total_sections

    # Aggregate overall score (0-100)
    score = (
        0.4 * keyword_match_score
        + 0.4 * (semantic_similarity_score * 100.0)
        + 0.2 * section_completeness_score
    )

    explanation = (
        "ATS score is a weighted blend of keyword overlap, semantic similarity, "
        "and presence of common resume sections."
    )

    return InternalATSComputationResult(
        score=score,
        keyword_match_score=keyword_match_score,
        semantic_similarity_score=semantic_similarity_score,
        section_completeness_score=section_completeness_score,
        explanation=explanation,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
    )


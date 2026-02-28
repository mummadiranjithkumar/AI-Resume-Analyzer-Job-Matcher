from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Set

from backend.models.schemas import (
    InternalJobSkillExtractionResult,
    InternalSkillExtractionResult,
)


_STOPWORDS: Set[str] = {
    "the",
    "and",
    "a",
    "an",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "at",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "this",
    "that",
    "as",
    "or",
    "from",
    "your",
    "our",
    "we",
    "you",
    "i",
}

_KNOWN_TOOLS: Set[str] = {
    "python",
    "pandas",
    "numpy",
    "sql",
    "postgresql",
    "mysql",
    "excel",
    "powerbi",
    "tableau",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "github",
    "gitlab",
    "tensorflow",
    "pytorch",
    "sklearn",
    "scikit-learn",
    "jira",
    "confluence",
}


def _normalize(text: str) -> str:
    return text.lower()


def _tokenize(text: str) -> List[str]:
    cleaned = _normalize(text)
    tokens = re.findall(r"[a-zA-Z+#.\-]{2,}", cleaned)
    return [t for t in tokens if t not in _STOPWORDS]


def _unique(tokens: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered


def _extract_tools(tokens: Iterable[str]) -> List[str]:
    token_set = {t.lower() for t in tokens}
    tools = [tool for tool in _KNOWN_TOOLS if tool in token_set]
    return tools


def extract_job_skills(job_description: str) -> InternalJobSkillExtractionResult:
    """
    Lightweight heuristic job skill + tool extraction.

    This intentionally stays simple and deterministic so the backend works
    out of the box without an external NLP model.
    """
    tokens = _tokenize(job_description)
    skills = _unique(tokens)
    tools = _extract_tools(tokens)
    return InternalJobSkillExtractionResult(job_skills=skills, tools=tools)


def extract_skills_and_profile(
    resume_text: str,
    job_description: str,
) -> InternalSkillExtractionResult:
    """
    Extract skills from resume and job description and compute simple overlaps.
    """
    resume_tokens = _tokenize(resume_text)
    job_tokens = _tokenize(job_description)

    resume_skills = _unique(resume_tokens)
    job_skills = _unique(job_tokens)

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    tools = _extract_tools(resume_tokens + job_tokens)

    education = []
    text_lower = _normalize(resume_text)
    if "bachelor" in text_lower or "b.sc" in text_lower or "bsc" in text_lower:
        education.append("Bachelor's degree")
    if "master" in text_lower or "m.sc" in text_lower or "msc" in text_lower:
        education.append("Master's degree")
    if "phd" in text_lower or "ph.d" in text_lower:
        education.append("PhD")

    experience_summary = "Experience details extracted from resume text."

    return InternalSkillExtractionResult(
        resume_skills=resume_skills,
        job_skills=job_skills,
        matched_skills=matched,
        missing_skills=missing,
        tools=tools,
        education=education,
        experience_summary=experience_summary,
    )


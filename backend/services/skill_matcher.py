import re
import numpy as np
from typing import Set, Dict, Any

from services.embeddings import get_embedding_model, embed_texts


# 🔹 remove junk words
STOPWORDS = {
    "a","an","the","is","are","was","were","in","on","at","of","for","to",
    "and","or","with","by","as","from","that","this","it","be","have",
    "has","had","we","you","your","good","along"
}


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()

    # 🔹 improved keyword extraction
    def _extract_keywords(self, text: str) -> Set[str]:
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+\-\.#]*\b', text.lower())

        return {
            w for w in words
            if len(w) > 2 and w not in STOPWORDS
        }

    # 🔹 cosine similarity safe
    def _cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 🔹 Extract keywords
        resume_skills = self._extract_keywords(resume_text)
        job_skills = self._extract_keywords(job_description)

        # 🔹 Keyword matching
        matching = resume_skills & job_skills
        missing = job_skills - resume_skills

        keyword_score = len(matching) / max(len(job_skills), 1)

        # 🔥 USE YOUR OPTIMIZED EMBEDDINGS (IMPORTANT)
        embeddings = embed_texts(self.model, [resume_text, job_description])
        emb_sim = self._cosine(embeddings[0], embeddings[1])

        # 🔥 HYBRID SCORE
        final_score = (0.6 * emb_sim) + (0.4 * keyword_score)

        # 🔥 PENALTY SYSTEM
        if len(missing) > 5:
            final_score *= 0.85
        if len(missing) > 10:
            final_score *= 0.75

        # 🔥 CAP SCORE
        final_score = min(final_score, 0.92)

        final_score = int(final_score * 100)

        # 🔹 clean output
        def clean(skills):
            return [s for s in skills if len(s) > 2][:10]

        return {
            "match_score": final_score,
            "matching_skills": clean(list(matching)),
            "missing_skills": clean(list(missing)),
            "suggestions": [
                f"Add experience with {s}" for s in clean(list(missing))[:5]
            ]
        }
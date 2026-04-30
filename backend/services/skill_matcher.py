import re
import numpy as np
from services.embeddings import get_embedding_model


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()

    def _extract_keywords(self, text: str):
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+\-\.#]*\b', text.lower())
        return set(words)

    def analyze_match(self, resume_text: str, job_description: str):

        # 🔹 Extract keywords
        resume_skills = self._extract_keywords(resume_text)
        job_skills = self._extract_keywords(job_description)

        # 🔹 Keyword matching
        matching = resume_skills & job_skills
        missing = job_skills - resume_skills

        keyword_score = len(matching) / max(len(job_skills), 1)

        # 🔹 Embedding similarity (FAST)
        embeddings = self.model.encode(
            [resume_text, job_description],
            convert_to_numpy=True,
            show_progress_bar=False
        )

        emb_sim = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )

        # 🔥 HYBRID SCORE (IMPORTANT)
        final_score = (0.6 * emb_sim) + (0.4 * keyword_score)

        # 🔥 PENALTY SYSTEM (VERY IMPORTANT)
        if len(missing) > 5:
            final_score *= 0.85

        if len(missing) > 10:
            final_score *= 0.75

        # 🔥 CAP SCORE (NO FAKE 100%)
        final_score = min(final_score, 0.92)

        # Convert to %
        final_score = int(final_score * 100)

        return {
            "match_score": final_score,
            "matching_skills": list(matching)[:10],
            "missing_skills": list(missing)[:10],
            "suggestions": [
                f"Add experience with {skill}" for skill in list(missing)[:5]
            ]
        }
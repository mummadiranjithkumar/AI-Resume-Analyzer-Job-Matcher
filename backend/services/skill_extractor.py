from typing import Dict, Any, List, Set
import numpy as np

from services.embeddings import get_embedding_model, embed_texts


STOPWORDS = {
    "a","an","the","is","are","was","were","in","on","at","of","for","to",
    "and","or","with","by","as","from","that","this","it","be","have",
    "has","had","good","along","including","they","we","you","your"
}


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()

    # 🔹 Clean tokens
    def _clean_tokens(self, text: str) -> Set[str]:
        words = text.lower().split()
        return {
            w.strip(".,()")
            for w in words
            if len(w) > 2 and w not in STOPWORDS
        }

    # 🔹 Extract candidate skills (basic)
    def _extract_skills(self, text: str) -> Set[str]:
        return self._clean_tokens(text)

    # 🔹 Cosine similarity
    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    # 🔥 MAIN FUNCTION
    def analyze_match(self, resume_text: str, job_text: str) -> Dict[str, Any]:

        # 1️⃣ Extract skills
        resume_skills = self._extract_skills(resume_text)
        job_skills = self._extract_skills(job_text)

        # 2️⃣ Keyword match
        matching_keywords = resume_skills & job_skills
        missing_keywords = job_skills - resume_skills

        keyword_score = len(matching_keywords) / max(len(job_skills), 1)

        # 3️⃣ Semantic similarity (AI)
        embeddings = embed_texts(self.model, [resume_text, job_text])
        semantic_score = self._cosine(embeddings[0], embeddings[1])

        # 4️⃣ Hybrid score
        final_score = int((0.5 * keyword_score + 0.5 * semantic_score) * 100)

        # 🚫 Prevent fake 100%
        if final_score > 95:
            final_score = 95

        # 5️⃣ Clean output (remove junk words)
        def clean_output(skills: List[str]) -> List[str]:
            return [s for s in skills if len(s) > 2][:15]

        return {
            "match_score": final_score,
            "matching_skills": clean_output(list(matching_keywords)),
            "missing_skills": clean_output(list(missing_keywords)),
            "suggestions": [
                f"Add experience with {s}" for s in clean_output(list(missing_keywords))[:5]
            ]
        }
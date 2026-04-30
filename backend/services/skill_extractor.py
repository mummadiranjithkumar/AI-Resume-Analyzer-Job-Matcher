import re
import numpy as np
from typing import Dict, Any, List

from services.embeddings import get_embedding_model, embed_texts


STOPWORDS = {
    "a","an","the","is","are","was","were","in","on","at","of","for","to",
    "and","or","with","by","as","from","that","this","it","be","have",
    "has","had","we","you","your"
}


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()

    # 🔹 Extract phrases (important!)
    def extract_phrases(self, text: str) -> List[str]:
        text = text.lower()

        # capture phrases like "rest api", "spring boot"
        phrases = re.findall(r"\b[a-zA-Z]+(?:\s+[a-zA-Z]+){0,2}\b", text)

        # clean
        cleaned = []
        for p in phrases:
            words = p.split()
            if all(w not in STOPWORDS for w in words) and len(p) > 3:
                cleaned.append(p.strip())

        return list(set(cleaned))

    # 🔹 Cosine similarity
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    # 🔥 MAIN
    def analyze_match(self, resume_text: str, job_text: str) -> Dict[str, Any]:

        # 1️⃣ Extract phrases
        jd_skills = self.extract_phrases(job_text)
        resume_skills = self.extract_phrases(resume_text)

        # 2️⃣ Keyword match
        matching = [
            skill for skill in jd_skills
            if any(skill in r or r in skill for r in resume_skills)
        ]

        missing = [s for s in jd_skills if s not in matching]

        keyword_score = len(matching) / max(len(jd_skills), 1)

        # 3️⃣ Semantic match (full text)
        emb = embed_texts(self.model, [resume_text, job_text])
        semantic_score = self.cosine(emb[0], emb[1])

        # 4️⃣ Final score
        final_score = int((0.6 * keyword_score + 0.4 * semantic_score) * 100)

        # avoid fake 100
        final_score = min(final_score, 95)

        return {
            "match_score": final_score,
            "matching_skills": matching[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add experience with {s}" for s in missing[:5]]
        }
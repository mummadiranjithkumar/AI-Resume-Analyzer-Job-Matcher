import re
import numpy as np
from typing import List, Dict, Any
import spacy


class SkillMatcher:

    def __init__(self):
        # ⚡ fast load (small model only)
        self.nlp = spacy.load("en_core_web_sm")

    # 🔹 normalize
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9+\-\.#\s]', '', text)
        return text

    # 🔹 extract skills
    def extract_skills(self, text: str) -> List[str]:
        doc = self.nlp(text)
        skills = []

        for chunk in doc.noun_chunks:
            phrase = self.normalize(chunk.text)

            if len(phrase) < 3:
                continue

            if chunk.root.pos_ in {"PRON", "DET"}:
                continue

            if any(w in phrase for w in [
                "experience", "knowledge", "ability",
                "candidate", "responsibility"
            ]):
                continue

            skills.append(phrase)

        return list(set(skills))

    # 🔹 simple vector (no ML model)
    def text_to_vector(self, text: str):
        words = text.split()
        return np.array([hash(w) % 10000 for w in words], dtype=np.float32)

    # 🔹 similarity
    def similarity(self, a, b):
        if len(a) == 0 or len(b) == 0:
            return 0.0

        return float(len(set(a) & set(b)) / max(len(set(a)), 1))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 🔹 extract skills
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        # 🔹 score
        keyword_score = len(matched) / max(len(jd_skills), 1)

        # 🔹 simple semantic (word overlap)
        resume_words = resume_text.lower().split()
        jd_words = job_description.lower().split()

        semantic_score = self.similarity(resume_words, jd_words)

        final_score = int((0.7 * keyword_score + 0.3 * semantic_score) * 100)
        final_score = min(final_score, 92)

        return {
            "match_score": final_score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [
                f"Add experience with {s}" for s in missing[:5]
            ]
        }
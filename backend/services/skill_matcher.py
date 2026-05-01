import re
import numpy as np
from typing import List, Dict, Any


class SkillMatcher:

    def __init__(self):
        # ✅ No spaCy model needed (ultra fast)
        pass

    # 🔹 normalize text
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9+\-\.#\s]', ' ', text)
        return text

    # 🔹 simple skill extraction (FAST + NO MODEL)
    def extract_skills(self, text: str) -> List[str]:
        text = self.normalize(text)

        words = text.split()

        # simple phrases (2–3 word chunks)
        skills = set()

        for i in range(len(words)):
            if len(words[i]) > 2:
                skills.add(words[i])

            if i < len(words) - 1:
                phrase = f"{words[i]} {words[i+1]}"
                skills.add(phrase)

        return list(skills)

    # 🔹 cosine similarity
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 🔹 extract skills
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        # 🔹 basic scoring
        score = int((len(matched) / max(len(jd_skills), 1)) * 100)
        score = min(score, 95)

        return {
            "match_score": score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add {s}" for s in missing[:5]]
        }
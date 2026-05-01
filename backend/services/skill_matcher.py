import re
from typing import List, Dict, Any


class SkillMatcher:

    def __init__(self):
        pass

    # 🔹 normalize text
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9+\-\.#\s]', ' ', text)
        return text

    # 🔹 dynamic skill extraction
    def extract_skills(self, text: str) -> List[str]:
        text = self.normalize(text)

        words = text.split()

        stopwords = {
            "the", "and", "or", "with", "for", "in", "on", "at",
            "a", "an", "to", "of", "is", "are", "be",
            "candidate", "seeking", "experience", "using",
            "developer", "role", "job", "required", "responsible"
        }

        skills = set()

        for i in range(len(words)):
            w1 = words[i]

            if w1 in stopwords or len(w1) < 3:
                continue

            skills.add(w1)

            if i < len(words) - 1:
                w2 = words[i + 1]

                if w2 not in stopwords and len(w2) > 2:
                    phrase = f"{w1} {w2}"

                    if not any(sw in phrase for sw in ["seeking", "responsible", "candidate"]):
                        skills.add(phrase)

        return list(skills)

    # 🔹 analyze match
    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        score = int((len(matched) / max(len(jd_skills), 1)) * 100)

        if len(missing) > len(matched):
            score -= 20

        score = max(min(score, 85), 10)

        return {
            "match_score": score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add {s}" for s in missing[:5]]
        }
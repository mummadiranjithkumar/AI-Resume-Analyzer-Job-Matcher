import re
from typing import Dict, Any, List


STOPWORDS = {
    "a","an","the","is","are","was","were","in","on","at","of","for","to",
    "and","or","with","by","as","from","that","this","it","be","have",
    "has","had","we","you","your"
}


class SkillMatcher:

    def __init__(self):
        pass

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

    # 🔹 Simple word overlap similarity
    def word_overlap_similarity(self, words1: List[str], words2: List[str]) -> float:
        set1, set2 = set(words1), set(words2)
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / max(len(union), 1)

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

        # 3️⃣ Final score (keyword-based only)
        final_score = int(keyword_score * 100)

        # avoid fake 100
        final_score = min(final_score, 95)

        return {
            "match_score": final_score,
            "matching_skills": matching[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add experience with {s}" for s in missing[:5]]
        }
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

    # 🔹 clean keyword-based skill extraction (ATS style)
    def extract_skills(self, text: str) -> List[str]:
        text = self.normalize(text)

        skill_keywords = [
            # backend
            "java", "spring boot", "rest api", "apis",

            # cloud
            "aws", "ec2", "s3", "lambda", "rds", "dynamodb",

            # AI
            "generative ai", "llm", "llms", "embeddings",

            # tools
            "github", "postman",

            # devops
            "ci/cd", "pipeline", "monitoring", "logging", "cloud security"
        ]

        found_skills = set()

        for skill in skill_keywords:
            if skill in text:
                found_skills.add(skill)

        return list(found_skills)

    # 🔹 analyze match
    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        # 🎯 realistic scoring
        score = int((len(matched) / max(len(jd_skills), 1)) * 100)

        if len(missing) > 0:
            score -= min(len(missing) * 3, 25)

        score = max(min(score, 90), 15)

        return {
            "match_score": score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [
                f"Consider adding or highlighting experience with {s}"
                for s in missing[:5]
            ]
        }
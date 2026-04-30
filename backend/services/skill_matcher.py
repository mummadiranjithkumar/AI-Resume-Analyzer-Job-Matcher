import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np


class SkillMatcher:
    def __init__(self):
        # 🔥 Core skill vocabulary (expand anytime)
        self.skill_vocab = {
            "java", "spring", "spring boot", "aws", "ec2", "s3", "lambda",
            "api gateway", "dynamodb", "cloudwatch",
            "rest api", "api", "postman", "ci/cd", "git", "github",
            "docker", "kubernetes",
            "generative ai", "llm", "embeddings", "prompt engineering",
            "python", "sql", "machine learning", "nlp"
        }

        # 🔥 Synonyms mapping
        self.synonyms = {
            "rest api": ["api", "rest", "web service"],
            "ci/cd": ["pipeline", "deployment"],
            "github": ["git"],
            "generative ai": ["gen ai", "llm"],
        }

        # 🔥 Load embedding model (lightweight)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # -----------------------------
    # Normalize text
    # -----------------------------
    def normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower())

    # -----------------------------
    # Extract candidate keywords
    # -----------------------------
    def extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z\+\/#\.]+\b', text.lower())

        stopwords = {
            "and", "or", "the", "with", "for", "in", "on",
            "a", "an", "to", "of", "is", "are", "we", "you",
            "looking", "experience", "working", "knowledge",
            "skills", "required", "strong"
        }

        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        return list(set(keywords))

    # -----------------------------
    # Match with vocab + synonyms
    # -----------------------------
    def match_with_vocab(self, keywords: List[str]) -> List[str]:
        matched = []

        for word in keywords:
            if word in self.skill_vocab:
                matched.append(word)
                continue

            # check synonyms
            for skill, syns in self.synonyms.items():
                if word in syns:
                    matched.append(skill)

        return list(set(matched))

    # -----------------------------
    # Semantic similarity
    # -----------------------------
    def similarity(self, a: str, b: str) -> float:
        vecs = self.model.encode([a, b])
        return np.dot(vecs[0], vecs[1]) / (
            np.linalg.norm(vecs[0]) * np.linalg.norm(vecs[1])
        )

    # -----------------------------
    # MAIN MATCH FUNCTION
    # -----------------------------
    def analyze_match(self, resume_text: str, job_description: str) -> Dict:
        resume_text = self.normalize(resume_text)
        job_description = self.normalize(job_description)

        # 🔹 Step 1: Extract keywords
        jd_keywords = self.extract_keywords(job_description)
        resume_keywords = self.extract_keywords(resume_text)

        # 🔹 Step 2: Filter to skills
        jd_skills = self.match_with_vocab(jd_keywords)
        resume_skills = self.match_with_vocab(resume_keywords)

        matched = []
        missing = []

        # 🔹 Step 3: Matching
        for jd_skill in jd_skills:
            found = False

            for r_skill in resume_skills:
                # direct match
                if jd_skill == r_skill:
                    found = True
                    break

                # semantic match
                sim = self.similarity(jd_skill, r_skill)
                if sim > 0.7:
                    found = True
                    break

            if found:
                matched.append(jd_skill)
            else:
                missing.append(jd_skill)

        # 🔹 Step 4: Score
        score = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0

        return {
            "match_score": score,
            "matching_skills": matched,
            "missing_skills": missing,
            "suggestions": [
                f"Consider adding experience in {skill}"
                for skill in missing[:5]
            ]
        }
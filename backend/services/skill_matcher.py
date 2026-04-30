import re
import numpy as np
from typing import List, Dict, Any
import spacy

from services.embeddings import get_embedding_model, embed_texts


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()
        self.nlp = spacy.load("en_core_web_sm")

    # 🔹 Normalize
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9+\-\.#\s]', '', text)
        return text

    # 🔹 FAST skill extraction (LIMITED TEXT)
    def extract_skills(self, text: str) -> List[str]:
        text = text[:2000]  # 🔥 LIMIT TEXT (HUGE SPEED BOOST)
        doc = self.nlp(text)

        skills = []

        for chunk in doc.noun_chunks:
            phrase = self.normalize(chunk.text)

            if len(phrase) < 3:
                continue

            if chunk.root.pos_ in {"PRON", "DET"}:
                continue

            skills.append(phrase)

        return list(set(skills))[:30]  # 🔥 LIMIT COUNT

    # 🔹 Experience extraction
    def extract_experience_years(self, text: str) -> int:
        matches = re.findall(r'(\d+)\+?\s*(years|yrs)', text.lower())
        if matches:
            return max(int(m[0]) for m in matches)
        return 0

    # 🔹 Cosine
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 🔥 LIMIT TEXT SIZE (CRITICAL)
        resume_text = resume_text[:3000]
        job_description = job_description[:3000]

        # 🔹 Extract skills
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        # 🔹 Embed (LIMIT SIZE)
        jd_emb = embed_texts(self.model, jd_skills[:20])
        res_emb = embed_texts(self.model, resume_skills[:30])

        matched = []
        missing = []

        for i, jd_vec in enumerate(jd_emb):

            if len(res_emb) == 0:
                missing.append(jd_skills[i])
                continue

            sims = res_emb @ jd_vec  # ⚡ faster

            if np.max(sims) > 0.7:
                matched.append(jd_skills[i])
            else:
                missing.append(jd_skills[i])

        keyword_score = len(matched) / max(len(jd_skills), 1)

        # 🔹 Semantic similarity (ONLY 2 embeddings)
        full_emb = embed_texts(self.model, [resume_text, job_description])
        semantic_score = self.cosine(full_emb[0], full_emb[1])

        # 🔹 Experience
        jd_exp = self.extract_experience_years(job_description)
        res_exp = self.extract_experience_years(resume_text)

        exp_score = 1.0 if jd_exp == 0 else min(res_exp / jd_exp, 1.0)

        # 🔥 FINAL SCORE
        final_score = (0.6 * keyword_score + 0.3 * semantic_score + 0.1 * exp_score)
        final_score = int(min(final_score * 100, 92))

        return {
            "match_score": final_score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [
                f"Add experience with {s}" for s in missing[:5]
            ]
        }
import numpy as np
from typing import List, Dict, Any

import spacy

from services.embeddings import get_embedding_model, embed_texts


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()
        self.nlp = spacy.load("en_core_web_sm")

    # 🔹 Extract meaningful skills using NLP
    def extract_skills(self, text: str) -> List[str]:
        doc = self.nlp(text)

        skills = []

        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip().lower()

            # basic filtering (minimal, not manual rules)
            if len(phrase) < 3:
                continue

            # remove pronouns / weak chunks
            if chunk.root.pos_ in {"PRON", "DET"}:
                continue

            skills.append(phrase)

        return list(set(skills))

    # 🔹 cosine similarity
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 1️⃣ Extract skills using NLP
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        # 2️⃣ Embed skills
        jd_emb = embed_texts(self.model, jd_skills)
        res_emb = embed_texts(self.model, resume_skills)

        matched = []
        missing = []

        # 3️⃣ Semantic matching
        for i, jd_vec in enumerate(jd_emb):

            if len(res_emb) == 0:
                missing.append(jd_skills[i])
                continue

            sims = np.dot(res_emb, jd_vec)

            if np.max(sims) > 0.7:
                matched.append(jd_skills[i])
            else:
                missing.append(jd_skills[i])

        keyword_score = len(matched) / max(len(jd_skills), 1)

        # 4️⃣ Full text similarity
        full_emb = embed_texts(self.model, [resume_text, job_description])
        semantic_score = self.cosine(full_emb[0], full_emb[1])

        # 5️⃣ Final score
        final_score = int((0.6 * keyword_score + 0.4 * semantic_score) * 100)
        final_score = min(final_score, 95)

        return {
            "match_score": final_score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add experience with {s}" for s in missing[:5]]
        }
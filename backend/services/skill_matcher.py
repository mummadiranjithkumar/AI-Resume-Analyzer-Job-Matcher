import numpy as np
from typing import List, Dict, Any
import re
import spacy

from services.embeddings import get_embedding_model, embed_texts


class SkillMatcher:

    def __init__(self):
        # ✅ LAZY LOAD (CRITICAL FOR RENDER)
        self.model = None
        self.nlp = None

    def get_model(self):
        if self.model is None:
            self.model = get_embedding_model()
        return self.model

    def get_nlp(self):
        if self.nlp is None:
            self.nlp = spacy.load("en_core_web_sm")
        return self.nlp

    # 🔹 Clean + normalize phrases
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9+\-\.#\s]', '', text)
        return text

    # 🔹 Extract meaningful skills using NLP
    def extract_skills(self, text: str) -> List[str]:
        nlp = self.get_nlp()
        doc = nlp(text)

        skills = []

        for chunk in doc.noun_chunks:
            phrase = self.normalize(chunk.text)

            # 🔥 FILTER NOISE (IMPORTANT)
            if len(phrase) < 3:
                continue

            if chunk.root.pos_ in {"PRON", "DET"}:
                continue

            # remove generic useless phrases
            if any(word in phrase for word in [
                "experience", "knowledge", "ability",
                "candidate", "responsibility", "understanding"
            ]):
                continue

            skills.append(phrase)

        return list(set(skills))

    # 🔹 cosine similarity
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        model = self.get_model()

        # 1️⃣ Extract skills
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume_text)

        # 2️⃣ Embed
        jd_emb = embed_texts(model, jd_skills)
        res_emb = embed_texts(model, resume_skills)

        matched = []
        missing = []

        # 3️⃣ Semantic skill matching
        for i, jd_vec in enumerate(jd_emb):

            if len(res_emb) == 0:
                missing.append(jd_skills[i])
                continue

            sims = np.dot(res_emb, jd_vec)

            if np.max(sims) > 0.72:  # 🔥 tuned threshold
                matched.append(jd_skills[i])
            else:
                missing.append(jd_skills[i])

        keyword_score = len(matched) / max(len(jd_skills), 1)

        # 4️⃣ Full semantic similarity
        full_emb = embed_texts(model, [resume_text, job_description])
        semantic_score = self.cosine(full_emb[0], full_emb[1])

        # 5️⃣ Final ATS-style score
        final_score = int((0.65 * keyword_score + 0.35 * semantic_score) * 100)

        # 🔥 avoid fake 100
        final_score = min(final_score, 94)

        return {
            "match_score": final_score,
            "matching_skills": matched[:10],
            "missing_skills": missing[:10],
            "suggestions": [f"Add experience with {s}" for s in missing[:5]]
        }
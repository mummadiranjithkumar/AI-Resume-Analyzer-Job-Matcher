import re
import numpy as np
from typing import List, Dict, Any

from services.embeddings import get_embedding_model, embed_texts


class SkillMatcher:

    def __init__(self):
        self.model = get_embedding_model()

    # 🔹 Extract meaningful phrases (NOT words)
    def extract_phrases(self, text: str) -> List[str]:
        text = text.lower()

        # capture phrases: "spring boot", "rest api"
        phrases = re.findall(r'\b[a-zA-Z]+(?:\s+[a-zA-Z]+){0,2}\b', text)

        # filter very short phrases
        return list(set([p.strip() for p in phrases if len(p) > 3]))

    # 🔹 cosine similarity
    def cosine(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def analyze_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:

        # 1️⃣ Extract phrases
        jd_phrases = self.extract_phrases(job_description)
        resume_phrases = self.extract_phrases(resume_text)

        # 2️⃣ Embed phrases
        jd_emb = embed_texts(self.model, jd_phrases)
        res_emb = embed_texts(self.model, resume_phrases)

        # 3️⃣ Semantic phrase matching
        matched = []
        missing = []

        for i, jd_vec in enumerate(jd_emb):
            sims = np.dot(res_emb, jd_vec)
            if len(sims) > 0 and np.max(sims) > 0.65:
                matched.append(jd_phrases[i])
            else:
                missing.append(jd_phrases[i])

        keyword_score = len(matched) / max(len(jd_phrases), 1)

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
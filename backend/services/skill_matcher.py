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

        # filter weak words
        if w1 in stopwords or len(w1) < 3:
            continue

        # keep technical-looking words
        if any(c.isdigit() for c in w1) or "+" in w1 or "#" in w1:
            skills.add(w1)
        else:
            skills.add(w1)

        # 2-word phrases (important)
        if i < len(words) - 1:
            w2 = words[i + 1]

            if w2 not in stopwords and len(w2) > 2:
                phrase = f"{w1} {w2}"

                # filter weak phrases
                if not any(sw in phrase for sw in ["seeking", "responsible", "candidate"]):
                    skills.add(phrase)

    return list(skills)
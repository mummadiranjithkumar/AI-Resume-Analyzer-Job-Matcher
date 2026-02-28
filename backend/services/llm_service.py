from __future__ import annotations

from typing import Tuple

from backend.models.schemas import (
    ATSScoreResult,
    InternalRoadmapResult,
    SkillAnalysis,
)


def run_full_analysis(
    *,
    resume_text: str,
    job_description: str,
    rag_context: str,
    skill_analysis: SkillAnalysis,
    ats_result: ATSScoreResult,
) -> Tuple[str, InternalRoadmapResult, str]:
    """
    Lightweight, rule-based stand-in for an LLM-powered analysis.

    This keeps the system fully local and dependency-free while still
    providing useful feedback derived from the computed skill and ATS data.
    """
    missing = skill_analysis.missing_skills or []
    matched = skill_analysis.matched_skills or []

    gap_lines: list[str] = []
    if missing:
        gap_lines.append(
            "Your profile is missing several skills mentioned in the job description: "
            + ", ".join(missing[:20])
            + ("..." if len(missing) > 20 else "")
        )
    else:
        gap_lines.append("Your skills closely match the job requirements.")

    if matched:
        gap_lines.append(
            "You already demonstrate strength in: " + ", ".join(matched[:20])
        )

    gap_lines.append(
        f"Current ATS score is {ats_result.score:.1f}/100 with "
        f"keyword match {ats_result.keyword_match_score:.1f}/100 "
        f"and semantic similarity {ats_result.semantic_similarity_score:.2f}."
    )

    skill_gap_summary = "\n".join(gap_lines)

    # Very simple time-phased roadmap based on missing skills
    top_missing = missing[:15]
    early_focus = ", ".join(top_missing[:5]) or "core job-related fundamentals"
    mid_focus = ", ".join(top_missing[5:10]) or "projects that deepen your existing skills"
    late_focus = ", ".join(top_missing[10:15]) or "advanced topics and interview preparation"

    roadmap = InternalRoadmapResult(
        plan_30_days=(
            "Focus on building strong foundations for the most critical missing skills: "
            f"{early_focus}."
        ),
        plan_60_days=(
            "Consolidate your knowledge with 1–2 portfolio projects highlighting: "
            f"{mid_focus}."
        ),
        plan_90_days=(
            "Polish your profile with advanced topics, systematized practice, and interview prep around: "
            f"{late_focus}."
        ),
        raw_reasoning="Roadmap generated from simple rules using missing and matched skills.",
    )

    ats_feedback = (
        "To improve ATS compatibility, weave missing job keywords naturally into your resume, "
        "ensure key sections (Experience, Education, Skills, Projects) are clearly labeled, "
        "and keep formatting simple so automated parsers can read it reliably."
    )

    return skill_gap_summary, roadmap, ats_feedback


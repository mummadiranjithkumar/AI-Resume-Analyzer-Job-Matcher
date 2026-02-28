from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, HTTPException, status

from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ATSScoreResult,
    LLMAnalysis,
    SkillAnalysis,
)
from backend.services import (
    parser,
    vector_store,
    embeddings,
    skill_extractor,
    ats_score,
    llm_service,
)


router = APIRouter(tags=["analysis"])

_RESULT_STORE: Dict[str, AnalyzeResponse] = {}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a previously uploaded resume against a job description.
    """
    try:
        resume_text = parser.load_extracted_text(request.resume_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found. Please upload the resume again.",
        ) from exc

    job_text = request.job_description
    if not job_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty.",
        )

    # Embedding model
    model = embeddings.get_embedding_model()

    # RAG: retrieve top chunks relevant to job description
    try:
        index, chunk_metadata = vector_store.load_index_and_chunks(request.resume_id)
        jd_vector = embeddings.embed_texts(model, [job_text])
        top_chunks = vector_store.search_top_k(index, chunk_metadata, jd_vector[0], k=5)
        context_for_llm = "\n\n".join(top_chunks)
    except FileNotFoundError:
        context_for_llm = resume_text

    # Skill extraction
    skill_result = skill_extractor.extract_skills_and_profile(
        resume_text=resume_text,
        job_description=job_text,
    )

    skill_analysis = SkillAnalysis(
        resume_skills=skill_result.resume_skills,
        job_skills=skill_result.job_skills,
        matched_skills=skill_result.matched_skills,
        missing_skills=skill_result.missing_skills,
        tools=skill_result.tools,
        education=skill_result.education,
        experience_summary=skill_result.experience_summary,
    )

    # ATS-style scoring
    ats_result = ats_score.compute_ats_score(
        resume_text=resume_text,
        job_description=job_text,
        job_keywords=skill_result.job_skills,
    )

    ats_score_result = ATSScoreResult(
        score=ats_result.score,
        keyword_match_score=ats_result.keyword_match_score,
        semantic_similarity_score=ats_result.semantic_similarity_score,
        section_completeness_score=ats_result.section_completeness_score,
        explanation=ats_result.explanation,
        matched_keywords=ats_result.matched_keywords,
        missing_keywords=ats_result.missing_keywords,
    )

    # Overall match percentage (blend semantic similarity and ATS score)
    match_percentage = max(
        0.0,
        min(
            100.0,
            0.5 * ats_result.score
            + 0.5 * (ats_result.semantic_similarity_score * 100.0),
        ),
    )

    # LLM-based analysis
    try:
        llm_gap, roadmap, ats_feedback = llm_service.run_full_analysis(
            resume_text=resume_text,
            job_description=job_text,
            rag_context=context_for_llm,
            skill_analysis=skill_analysis,
            ats_result=ats_score_result,
        )

        llm_analysis = LLMAnalysis(
            skill_gap_summary=llm_gap,
            learning_roadmap_30=roadmap.plan_30_days,
            learning_roadmap_60=roadmap.plan_60_days,
            learning_roadmap_90=roadmap.plan_90_days,
            resume_improvement_tips=ats_feedback,
            raw_reasoning=roadmap.raw_reasoning,
        )
    except Exception as exc:  # noqa: BLE001
        # Fallback if LLM is unavailable
        llm_analysis = LLMAnalysis(
            skill_gap_summary=f"LLM analysis unavailable: {exc}",
            learning_roadmap_30="LLM not available.",
            learning_roadmap_60="LLM not available.",
            learning_roadmap_90="LLM not available.",
            resume_improvement_tips="LLM not available.",
            raw_reasoning=None,
        )

    result = AnalyzeResponse(
        id=request.resume_id,
        match_percentage=match_percentage,
        skill_analysis=skill_analysis,
        ats=ats_score_result,
        llm_analysis=llm_analysis,
        created_at=datetime.now(timezone.utc),
    )

    _RESULT_STORE[result.id] = result
    return result


@router.get("/results/{analysis_id}", response_model=AnalyzeResponse)
def get_results(analysis_id: str) -> AnalyzeResponse:
    """
    Retrieve a previously computed analysis result.
    """
    result = _RESULT_STORE.get(analysis_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found.",
        )
    return result


from fastapi import APIRouter

from backend.models.schemas import JobSkillExtractionRequest, JobSkillExtractionResponse
from backend.services import skill_extractor


router = APIRouter(tags=["job"])


@router.post("/job/skills", response_model=JobSkillExtractionResponse)
def extract_job_skills(payload: JobSkillExtractionRequest) -> JobSkillExtractionResponse:
    """
    Extract key skills and tools from a job description.
    Useful for debugging the NLP pipeline independently of resumes.
    """
    result = skill_extractor.extract_job_skills(job_description=payload.job_description)
    return JobSkillExtractionResponse(
        job_skills=result.job_skills,
        tools=result.tools,
    )


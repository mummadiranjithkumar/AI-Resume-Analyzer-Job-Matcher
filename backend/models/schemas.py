from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    id: str = Field(..., description="Server-generated identifier for the uploaded resume.")
    filename: str = Field(..., description="Original filename of the uploaded resume.")
    text_preview: str = Field(..., description="Truncated preview of extracted resume text.")


class AnalyzeRequest(BaseModel):
    resume_id: str = Field(..., description="ID returned by /upload-resume.")
    job_description: str = Field(..., description="Raw text of the job description.")


class SkillAnalysis(BaseModel):
    resume_skills: List[str]
    job_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    tools: List[str]
    education: List[str]
    experience_summary: str


class ATSScoreResult(BaseModel):
    score: float
    keyword_match_score: float
    semantic_similarity_score: float
    section_completeness_score: float
    explanation: str
    matched_keywords: List[str]
    missing_keywords: List[str]


class LLMAnalysis(BaseModel):
    skill_gap_summary: str
    learning_roadmap_30: str
    learning_roadmap_60: str
    learning_roadmap_90: str
    resume_improvement_tips: str
    raw_reasoning: Optional[str] = None


class AnalyzeResponse(BaseModel):
    id: str
    match_percentage: float
    skill_analysis: SkillAnalysis
    ats: ATSScoreResult
    llm_analysis: LLMAnalysis
    created_at: datetime


class JobSkillExtractionRequest(BaseModel):
    job_description: str


class JobSkillExtractionResponse(BaseModel):
    job_skills: List[str]
    tools: List[str]


class InternalJobSkillExtractionResult(BaseModel):
    job_skills: List[str]
    tools: List[str]


class InternalSkillExtractionResult(BaseModel):
    resume_skills: List[str]
    job_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    tools: List[str]
    education: List[str]
    experience_summary: str


class InternalATSComputationResult(BaseModel):
    score: float
    keyword_match_score: float
    semantic_similarity_score: float
    section_completeness_score: float
    explanation: str
    matched_keywords: List[str]
    missing_keywords: List[str]


class InternalRoadmapResult(BaseModel):
    plan_30_days: str
    plan_60_days: str
    plan_90_days: str
    raw_reasoning: Optional[str] = None


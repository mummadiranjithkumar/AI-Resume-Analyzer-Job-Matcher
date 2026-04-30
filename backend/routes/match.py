from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
import io

from services.pdf_extractor import PDFExtractor
from services.skill_matcher import SkillMatcher
from services.job_parser import JobParser


router = APIRouter()

pdf_extractor = PDFExtractor()
skill_matcher = SkillMatcher()
job_parser = JobParser()


@router.post("/match", summary="Upload resume + JD (text or file)")
async def match_resume_to_job(
    resume: UploadFile = File(..., description="Upload resume PDF"),

    # 👇 IMPORTANT CHANGE (remove Optional)
    job_description: str = Form(
        default="",
        description="Paste job description text"
    ),

    # 👇 IMPORTANT CHANGE (remove Optional typing)
    job_file: UploadFile = File(
        default=None,
        description="Upload job description file (PDF/Image)"
    ),
) -> Dict[str, Any]:

    try:
        # ✅ Resume validation
        if not resume.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are allowed for resume")

        pdf_bytes = await resume.read()

        if len(pdf_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Resume must be less than 10MB")

        resume_text = pdf_extractor.extract_text_from_pdf(io.BytesIO(pdf_bytes))

        if not resume_text or len(resume_text.strip()) < 100:
            raise HTTPException(400, "Could not extract sufficient resume text")

        # 🔥 PRIORITY: FILE FIRST
        final_job_description = ""

        if job_file is not None and job_file.filename:
            job_file_ext = job_file.filename.lower().split(".")[-1]
            allowed = ["pdf", "jpg", "jpeg", "png", "bmp", "tiff"]

            if job_file_ext not in allowed:
                raise HTTPException(400, f"Allowed formats: {allowed}")

            job_bytes = await job_file.read()

            if len(job_bytes) > 10 * 1024 * 1024:
                raise HTTPException(400, "Job file must be less than 10MB")

            final_job_description = job_parser.extract_text_from_file(
                job_bytes, job_file.filename
            )

        # ✅ TEXT fallback
        elif job_description.strip():
            final_job_description = job_description.strip()

        else:
            raise HTTPException(
                400,
                "Provide either job_file OR job_description"
            )

        # ✅ Validate JD
        if len(final_job_description.strip()) < 50:
            raise HTTPException(400, "Invalid job description")

        # 🔥 AI Matching
        result = skill_matcher.analyze_match(
            resume_text,
            final_job_description
        )

        return result

    except ValueError as e:
        raise HTTPException(400, str(e))

    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
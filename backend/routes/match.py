from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any, Optional
import io

# ✅ FIXED IMPORTS (removed backend)
from services.pdf_extractor import PDFExtractor
from services.skill_matcher import SkillMatcher
from services.job_parser import JobParser


router = APIRouter()
pdf_extractor = PDFExtractor()
skill_matcher = SkillMatcher()
job_parser = JobParser()


@router.post("/match", response_model=Dict[str, Any])
async def match_resume_to_job(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:

    try:
        # Validate resume file type
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed for resume")

        # Validate that either job_description or job_file is provided
        if not job_description and not job_file:
            raise HTTPException(
                status_code=400,
                detail="Either job_description text or job_file must be provided"
            )

        # Process job description
        final_job_description = ""

        if job_description and job_description.strip():
            if len(job_description.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Job description must be at least 50 characters long"
                )
            final_job_description = job_description.strip()

        elif job_file:
            job_file_ext = job_file.filename.lower().split('.')[-1]
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']

            if job_file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job file must be one of: {', '.join(allowed_extensions)}"
                )

            job_file_bytes = await job_file.read()

            if len(job_file_bytes) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Job file size must be less than 10MB")

            final_job_description = job_parser.extract_text_from_file(job_file_bytes, job_file.filename)

            if not final_job_description or len(final_job_description.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract sufficient text from the job file."
                )

        # Process resume
        pdf_bytes = await resume.read()

        if len(pdf_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Resume PDF file size must be less than 10MB")

        resume_text = pdf_extractor.extract_text_from_pdf(io.BytesIO(pdf_bytes))

        if not resume_text or len(resume_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the resume PDF."
            )

        # 🔥 AI matching
        result = skill_matcher.analyze_match(resume_text, final_job_description)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
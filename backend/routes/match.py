from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any, Optional
import io

# ✅ FIXED IMPORTS
from backend.services.pdf_extractor import PDFExtractor
from backend.services.skill_matcher import SkillMatcher
from backend.services.job_parser import JobParser


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
            # Use provided text job description
            if len(job_description.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Job description must be at least 50 characters long"
                )
            final_job_description = job_description.strip()
        
        elif job_file:
            # Extract text from uploaded job file
            job_file_ext = job_file.filename.lower().split('.')[-1]
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
            
            if job_file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job file must be one of: {', '.join(allowed_extensions)}"
                )
            
            # Validate job file size (max 10MB)
            job_file_bytes = await job_file.read()
            if len(job_file_bytes) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Job file size must be less than 10MB")
            
            # Extract text from job file
            final_job_description = job_parser.extract_text_from_file(job_file_bytes, job_file.filename)
            
            # Validate extracted job description
            if not final_job_description or len(final_job_description.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract sufficient text from the job file. Please ensure the file contains readable text."
                )

        # Read and process resume PDF
        pdf_bytes = await resume.read()

        # Validate PDF file size (max 10MB)
        if len(pdf_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Resume PDF file size must be less than 10MB")

        # Extract text from resume
        resume_text = pdf_extractor.extract_text_from_pdf(io.BytesIO(pdf_bytes))

        # Validate extracted resume text
        if not resume_text or len(resume_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the resume PDF."
            )

        # 🔥 Main AI logic
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
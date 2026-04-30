from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
import io

from services.pdf_extractor import PDFExtractor
from services.skill_matcher import SkillMatcher
from services.job_parser import JobParser


router = APIRouter()

# ✅ Initialize services (singleton-style)
pdf_extractor = PDFExtractor()
skill_matcher = SkillMatcher()
job_parser = JobParser()


@router.post("/match", summary="Upload resume + JD (text or file)")
async def match_resume_to_job(
    resume: UploadFile = File(..., description="Upload resume PDF"),
    job_description: str = Form("", description="Paste job description text"),
    job_file: UploadFile = File(None, description="Upload job description file (PDF/Image)"),
) -> Dict[str, Any]:

    try:
        # =========================
        # ✅ RESUME VALIDATION
        # =========================
        if not resume or not getattr(resume, "filename", None):
            raise HTTPException(400, "Resume file is required")

        if not resume.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files are allowed for resume")

        pdf_bytes = await resume.read()

        if not pdf_bytes:
            raise HTTPException(400, "Empty resume file")

        if len(pdf_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Resume must be less than 10MB")

        try:
            resume_text = pdf_extractor.extract_text_from_pdf(io.BytesIO(pdf_bytes))
        except Exception:
            raise HTTPException(400, "Failed to parse resume PDF")

        if not resume_text or len(resume_text.strip()) < 100:
            raise HTTPException(400, "Could not extract sufficient resume text")

        # =========================
        # 🔥 JOB DESCRIPTION LOGIC (FULLY SAFE)
        # =========================
        final_job_description = ""

        # 1️⃣ Try FILE first (safe)
        if job_file is not None and getattr(job_file, "filename", None):
            try:
                job_file_ext = job_file.filename.lower().split(".")[-1]
                allowed = ["pdf", "jpg", "jpeg", "png"]

                if job_file_ext in allowed:
                    job_bytes = await job_file.read()

                    if job_bytes and len(job_bytes) <= 10 * 1024 * 1024:
                        extracted = job_parser.extract_text_from_file(
                            job_bytes, job_file.filename
                        )

                        # Accept only meaningful text
                        if extracted and len(extracted.strip()) > 50:
                            final_job_description = extracted

            except Exception:
                # Never break — fallback handles it
                pass

        # 2️⃣ Fallback to TEXT
        if not final_job_description:
            if job_description and job_description.strip():
                final_job_description = job_description.strip()

        # 3️⃣ Final validation
        if not final_job_description or len(final_job_description.strip()) < 50:
            raise HTTPException(
                400,
                "Invalid job description (file parsing failed and no valid text provided)"
            )

        # =========================
        # 🔥 AI MATCHING
        # =========================
        try:
            result = skill_matcher.analyze_match(
                resume_text,
                final_job_description
            )
        except Exception:
            raise HTTPException(500, "Error during AI matching")

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
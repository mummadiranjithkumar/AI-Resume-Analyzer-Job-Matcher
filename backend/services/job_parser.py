import re
import io
from typing import Optional
from pypdf import PdfReader


class JobParser:
    """Service for extracting text from job description files"""

    def __init__(self):
        pass

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract text from uploaded file (PDF only for now)"""
        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'pdf':
            return self._extract_from_pdf(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported types: PDF")

    def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return self._clean_text(text)

        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\/\@\#\$]', ' ', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

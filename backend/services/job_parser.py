import re
import io
import os
from typing import Optional
from PIL import Image
import numpy as np
from pypdf import PdfReader

# ✅ SAFE OCR IMPORT
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    pytesseract = None
    TESSERACT_AVAILABLE = False


class JobParser:
    """Service for extracting text from job description files"""

    def __init__(self):
        if TESSERACT_AVAILABLE and os.name == "nt":
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'pdf':
            return self._extract_from_pdf(file_bytes)

        elif file_ext in ['jpg', 'jpeg', 'png']:
            return self._extract_from_image(file_bytes)

        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return self._clean_text(text)

    def _extract_from_image(self, image_bytes: bytes) -> str:

        # 🔥 SAFE FALLBACK (NO OCR IN PRODUCTION)
        if not TESSERACT_AVAILABLE:
            return "Image OCR not supported on server. Please upload PDF."

        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return self._clean_text(text)

        except Exception:
            return "OCR failed. Please upload PDF."

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\/\@\#\$]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text
import re
import io
import os
from typing import Optional
from PIL import Image
import cv2
import numpy as np
from pypdf import PdfReader

# ✅ SAFE IMPORT (IMPORTANT)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    pytesseract = None
    TESSERACT_AVAILABLE = False


class JobParser:
    """Service for extracting text from job description files (PDF and images)"""

    def __init__(self):
        # ✅ Set tesseract path ONLY for Windows (local dev)
        if TESSERACT_AVAILABLE and os.name == "nt":
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        file_ext = filename.lower().split('.')[-1]

        try:
            if file_ext == 'pdf':
                return self._extract_from_pdf(file_bytes)

            elif file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                return self._extract_from_image(file_bytes)

            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            raise ValueError(f"Failed to extract text from {filename}: {str(e)}")

    def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
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

    def _extract_from_image(self, image_bytes: bytes) -> str:
        """
        OCR handling:
        - Works locally if tesseract installed
        - Safe fallback in production (Render)
        """

        if not TESSERACT_AVAILABLE:
            return "OCR not available on server"

        try:
            # Convert image
            image = Image.open(io.BytesIO(image_bytes))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            processed_image = self._preprocess_image(cv_image)

            try:
                text = pytesseract.image_to_string(processed_image)
            except Exception:
                return "OCR failed or tesseract not installed"

            return self._clean_text(text)

        except Exception as e:
            raise ValueError(f"Image OCR failed: {str(e)}")

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        denoised = cv2.medianBlur(binary, 3)
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        return dilated

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\/\@\#\$]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text
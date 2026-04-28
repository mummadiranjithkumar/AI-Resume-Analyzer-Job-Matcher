import re
from typing import List
from pypdf import PdfReader


class PDFExtractor:
    """Service for extracting and cleaning text from PDF resumes"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF file bytes
        
        Args:
            pdf_bytes: Raw bytes of the PDF file
            
        Returns:
            Extracted and cleaned text
        """
        try:
            reader = PdfReader(pdf_bytes)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return self._clean_text(text)
            
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\/\@\#\$]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

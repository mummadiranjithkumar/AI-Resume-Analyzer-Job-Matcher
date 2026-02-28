from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RESUME_DIR = DATA_DIR / "resumes"


def generate_resume_id() -> str:
    return uuid.uuid4().hex


def get_resume_storage_dir() -> Path:
    return RESUME_DIR


async def save_upload_file(file: UploadFile, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    contents = await file.read()
    with destination.open("wb") as f:
        f.write(contents)


def extract_text_from_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _extract_text_from_pdf(path)
    return _extract_text_from_text_file(path)


def _extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            text = ""
        texts.append(text)
    return "\n".join(texts)


def _extract_text_from_text_file(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = min(start + max_chars, length)
        chunk = cleaned[start:end]
        chunks.append(chunk)
        if end == length:
            break
        start = max(0, end - overlap)

    return chunks


def _extracted_text_path(resume_id: str) -> Path:
    return RESUME_DIR / f"{resume_id}.txt"


def save_extracted_text(resume_id: str, text: str) -> None:
    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    path = _extracted_text_path(resume_id)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def load_extracted_text(resume_id: str) -> str:
    path = _extracted_text_path(resume_id)
    if not path.exists():
        raise FileNotFoundError(f"Extracted text for resume_id={resume_id} not found.")
    with path.open("r", encoding="utf-8") as f:
        return f.read()


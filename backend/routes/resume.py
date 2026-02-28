from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi import status

from backend.models.schemas import ResumeUploadResponse
from backend.services import parser, embeddings, vector_store


router = APIRouter(tags=["resume"])


@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(file: UploadFile = File(...)) -> ResumeUploadResponse:
    """
    Upload a resume (PDF or text), extract text, chunk, embed and build FAISS index.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename.",
        )

    try:
        resume_id = parser.generate_resume_id()
        storage_dir = parser.get_resume_storage_dir()
        storage_dir.mkdir(parents=True, exist_ok=True)

        stored_path = storage_dir / f"{resume_id}_{Path(file.filename).name}"
        await parser.save_upload_file(file=file, destination=stored_path)

        text = parser.extract_text_from_file(stored_path)
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to extract text from the uploaded file.",
            )

        # Persist normalized text for later analysis
        parser.save_extracted_text(resume_id=resume_id, text=text)

        # Chunk and embed into FAISS
        chunks = parser.chunk_text(text)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No meaningful text chunks could be created from the resume.",
            )

        model = embeddings.get_embedding_model()
        vectors = embeddings.embed_texts(model, chunks)
        vector_store.create_and_persist_index(resume_id, chunks, vectors)

        preview = text[:600].replace("\n", " ")

        return ResumeUploadResponse(
            id=resume_id,
            filename=file.filename,
            text_preview=preview,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {exc}",
        ) from exc


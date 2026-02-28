from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.resume import router as resume_router
from backend.routes.analysis import router as analysis_router
from backend.routes.job import router as job_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Resume Analyzer + Job Matcher",
        version="1.0.0",
        description="Local LLM + RAG powered resume analyzer and job matcher.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "*",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(resume_router)
    app.include_router(analysis_router)
    app.include_router(job_router)

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


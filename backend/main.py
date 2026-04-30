from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.match import router as match_router
from routes.job import router as job_router
from routes.resume import router as resume_router

# 🔥 MODEL PRELOAD (IMPORTANT FOR SPEED)
from services.embeddings import get_embedding_model
import spacy

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Analyze resume vs job description and return match score",
    version="1.0.0"
)


# 🔥 LOAD HEAVY MODELS ON STARTUP (NO RUNTIME DELAY)
@app.on_event("startup")
def load_models():
    print("🚀 Loading AI models...")
    get_embedding_model()
    spacy.load("en_core_web_sm")
    print("✅ Models loaded successfully")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(match_router, prefix="/api", tags=["match"])
app.include_router(job_router, prefix="/api", tags=["job"])
app.include_router(resume_router, prefix="/api", tags=["resume"])


@app.get("/")
async def root():
    return {
        "message": "AI Resume Analyzer API running",
        "docs": "/docs",
        "endpoint": "/api/match"
    }
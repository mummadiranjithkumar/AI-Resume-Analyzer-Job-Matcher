from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.match import router as match_router


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Analyze resume vs job description and return match score",
    version="1.0.0"
)


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


@app.get("/")
async def root():
    return {
        "message": "AI Resume Analyzer API running",
        "docs": "/docs",
        "endpoint": "/api/match"
    }
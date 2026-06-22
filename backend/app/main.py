"""
LeadForge AI — Backend entrypoint.

Run locally (outside Docker):
    uvicorn app.main:app --reload --port 8000

Run via Docker Compose:
    docker compose up backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="AI-powered lead generation, website analysis, and sales pipeline for freelance web developers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "status": "running", "docs": "/docs"}

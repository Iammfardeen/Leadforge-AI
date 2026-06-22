from fastapi import APIRouter

from app.api.routes import (
    ai_reports,
    analyzer,
    crm,
    health,
    leads,
    mockups,
    proposals,
    reports,
    screenshots,
    settings,
    whatsapp,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(leads.router)
api_router.include_router(analyzer.router)
api_router.include_router(ai_reports.router)
api_router.include_router(mockups.router)
api_router.include_router(screenshots.router)
api_router.include_router(whatsapp.router)
api_router.include_router(proposals.router)
api_router.include_router(crm.router)
api_router.include_router(reports.router)
api_router.include_router(settings.router)

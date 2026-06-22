"""
AI Analysis (Business Summary, Weaknesses, Improvements, etc.)

Generation logic lives in app/services/ai_report.py. A report typically
takes a few seconds to a couple minutes depending on the local machine
running Ollama and which model is selected — small models on CPU-only
hardware can be slow. The frontend should show a clear loading state.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import ai_report as ai_report_service

router = APIRouter(prefix="/ai-reports", tags=["ai-reports"])


@router.post("/{lead_id}")
def generate_ai_report(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    analysis_resp = (
        db.table("website_analyses")
        .select("*")
        .eq("lead_id", lead_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    latest_analysis = analysis_resp.data[0] if analysis_resp.data else None

    profile_resp = db.table("profiles").select("ai_model").eq("id", user.id).maybe_single().execute()
    preferred_model = (profile_resp.data or {}).get("ai_model") or "llama-3.3-70b-versatile"

    try:
        report = ai_report_service.generate_report(lead_resp.data, latest_analysis, model=preferred_model)
    except ai_report_service.AIReportError as exc:
        raise HTTPException(status_code=502, detail=f"Could not generate AI report: {exc}")

    row = {
        **report,
        "lead_id": lead_id,
        "user_id": user.id,
        "analysis_id": latest_analysis["id"] if latest_analysis else None,
    }
    insert_resp = db.table("ai_reports").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}")
def get_latest_ai_report(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("ai_reports")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="No AI report found for this lead yet")
    return resp.data[0]

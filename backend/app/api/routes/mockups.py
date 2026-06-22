"""
AI Website Redesign — generates a wireframe spec (image prompt + HTML
preview) for a lead's proposed new homepage.

If the lead already has an AI Report with suggested colors/fonts/style,
those are reused here so the Mockup stays visually consistent with the AI
Report rather than the two features independently inventing different
design directions for the same lead.

A full run involves two Ollama calls (image prompt, then HTML) and can
take anywhere from several seconds to a couple minutes depending on the
local machine and model — the frontend should show a clear loading state.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import mockup as mockup_service

router = APIRouter(prefix="/mockups", tags=["mockups"])


@router.post("/{lead_id}")
def generate_mockup(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    ai_report_resp = (
        db.table("ai_reports")
        .select("suggested_colors, suggested_fonts, suggested_design_style")
        .eq("lead_id", lead_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    latest_ai_report = ai_report_resp.data[0] if ai_report_resp.data else None

    profile_resp = db.table("profiles").select("ai_model").eq("id", user.id).maybe_single().execute()
    preferred_model = (profile_resp.data or {}).get("ai_model") or "llama-3.3-70b-versatile"

    try:
        mockup = mockup_service.generate_mockup(lead_resp.data, ai_report=latest_ai_report, model=preferred_model)
    except mockup_service.MockupGenerationError as exc:
        raise HTTPException(status_code=502, detail=f"Could not generate mockup: {exc}")

    row = {**mockup, "lead_id": lead_id, "user_id": user.id}
    insert_resp = db.table("website_mockups").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}")
def list_mockups(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("website_mockups")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"mockups": resp.data}

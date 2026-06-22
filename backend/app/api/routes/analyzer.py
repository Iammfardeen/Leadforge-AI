"""
Website Analyzer API.

POST /analyzer/{lead_id} kicks off an analysis run for the lead's website_url
and persists a new row in website_analyses. The actual scanning logic
(SSL check, Lighthouse-style scoring, broken link crawl, etc.) lives in
app/services/analyzer.py — this route stays thin.

A full run typically takes 5-20 seconds (most of it spent waiting on the
PageSpeed Insights API, which runs a real Lighthouse audit against the
live site) — the frontend should show a loading state, not assume this
completes instantly.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import analyzer as analyzer_service

router = APIRouter(prefix="/analyzer", tags=["analyzer"])


@router.post("/{lead_id}")
def analyze_website(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead = lead_resp.data
    if not lead.get("website_url"):
        raise HTTPException(status_code=400, detail="This lead has no website_url to analyze")

    # An optional user-supplied PageSpeed Insights API key raises the free
    # rate limit; analysis still works without one for light usage.
    settings_resp = (
        db.table("user_settings")
        .select("google_psi_api_key")
        .eq("user_id", user.id)
        .maybe_single()
        .execute()
    )
    psi_key = (settings_resp.data or {}).get("google_psi_api_key")

    try:
        report = analyzer_service.run_analysis(lead["website_url"], google_psi_api_key=psi_key)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not complete website analysis: {exc}")

    row = {**report, "lead_id": lead_id, "user_id": user.id}
    insert_resp = db.table("website_analyses").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}/history")
def analysis_history(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("website_analyses")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"analyses": resp.data}

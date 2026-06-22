"""
Website Screenshots — captures a screenshot of the lead's website and
stores it (Supabase Storage), keeping full history for before/after compare.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import screenshot as screenshot_service

router = APIRouter(prefix="/screenshots", tags=["screenshots"])


@router.post("/{lead_id}")
def capture_screenshot(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead = lead_resp.data
    if not lead.get("website_url"):
        raise HTTPException(status_code=400, detail="This lead has no website_url to screenshot")

    try:
        result = screenshot_service.capture(lead["website_url"])
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Screenshot capture not yet implemented (foundation phase stub)")

    row = {
        "lead_id": lead_id,
        "user_id": user.id,
        "storage_path": result["storage_path"],
        "page_url": lead["website_url"],
        "capture_type": result.get("capture_type", "full_page"),
    }
    insert_resp = db.table("screenshots").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}/history")
def screenshot_history(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("screenshots")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"screenshots": resp.data}

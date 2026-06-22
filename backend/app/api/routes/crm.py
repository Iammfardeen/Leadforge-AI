"""
CRM activity log — timeline of events per lead (status changes, notes added,
messages generated, proposals sent, etc.) used to render the CRM activity
feed and feed the Reports module's "Meetings" / "Clients" counters.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin

router = APIRouter(prefix="/crm", tags=["crm"])


class ActivityCreateRequest(BaseModel):
    event_type: str
    description: str | None = None
    metadata: dict | None = None


@router.post("/{lead_id}/activity")
def log_activity(lead_id: str, payload: ActivityCreateRequest, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("id").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    row = {**payload.model_dump(), "lead_id": lead_id, "user_id": user.id}
    insert_resp = db.table("activity_log").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}/activity")
def get_activity(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("activity_log")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"activity": resp.data}


@router.get("/follow-ups")
def upcoming_follow_ups(user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("leads")
        .select("id,business_name,status,follow_up_at")
        .eq("user_id", user.id)
        .not_.is_("follow_up_at", "null")
        .order("follow_up_at")
        .execute()
    )
    return {"follow_ups": resp.data}

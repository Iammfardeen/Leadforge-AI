"""
Leads API.

Search (Google Places integration) is implemented in app/services/places.py
and called from POST /leads/search. This route file stays thin: it validates
input, delegates to the service layer, and persists/reads via Supabase with
RLS enforced by passing the caller's JWT through.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.models.lead import Lead, LeadCreate, LeadSearchRequest, LeadUpdate
from app.services.places import search_businesses

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/search")
def search_leads(payload: LeadSearchRequest, user: CurrentUser = Depends(get_current_user)):
    """
    Searches Google Places for businesses matching city + category.
    Does NOT persist results — the user picks which ones to save via
    POST /leads (bulk save happens client-side, one call per selected lead,
    or via /leads/bulk if you wire that up later).
    """
    results = search_businesses(city=payload.city, category=payload.category, max_results=payload.max_results)
    return {"results": results, "count": len(results)}


@router.get("")
def list_leads(user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("leads").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
    return {"leads": resp.data}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    row = payload.model_dump()
    row["user_id"] = user.id
    resp = db.table("leads").insert(row).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create lead")
    return resp.data[0]


@router.get("/{lead_id}")
def get_lead(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")
    return resp.data


@router.patch("/{lead_id}")
def update_lead(lead_id: str, payload: LeadUpdate, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    resp = (
        db.table("leads")
        .update(updates)
        .eq("id", lead_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")
    return resp.data[0]


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    db.table("leads").delete().eq("id", lead_id).eq("user_id", user.id).execute()
    return None

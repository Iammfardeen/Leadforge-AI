"""
Proposal Generator — builds a PDF proposal (pricing, timeline, deliverables,
hosting, maintenance, payment terms) with a digital signature area.

PDF rendering logic lives in app/services/proposal_pdf.py.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import proposal_pdf as proposal_pdf_service

router = APIRouter(prefix="/proposals", tags=["proposals"])


class ProposalCreateRequest(BaseModel):
    pricing: dict
    timeline: dict
    deliverables: list[str]
    hosting_details: str | None = None
    maintenance_details: str | None = None
    payment_terms: str | None = None


@router.post("/{lead_id}")
def create_proposal(lead_id: str, payload: ProposalCreateRequest, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    row = {**payload.model_dump(), "lead_id": lead_id, "user_id": user.id, "status": "draft"}
    insert_resp = db.table("proposals").insert(row).execute()
    proposal = insert_resp.data[0]

    try:
        pdf_path = proposal_pdf_service.render_pdf(proposal, lead_resp.data)
        db.table("proposals").update({"pdf_storage_path": pdf_path}).eq("id", proposal["id"]).execute()
        proposal["pdf_storage_path"] = pdf_path
    except NotImplementedError:
        pass  # PDF rendering arrives in feature-build phase; proposal row still saved

    return proposal


@router.get("/{lead_id}")
def list_proposals(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("proposals")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"proposals": resp.data}


@router.patch("/{proposal_id}/status")
def update_proposal_status(proposal_id: str, status: str, user: CurrentUser = Depends(get_current_user)):
    valid_statuses = {"draft", "sent", "viewed", "accepted", "declined", "expired"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    db = get_supabase_admin()
    resp = db.table("proposals").update({"status": status}).eq("id", proposal_id).eq("user_id", user.id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return resp.data[0]

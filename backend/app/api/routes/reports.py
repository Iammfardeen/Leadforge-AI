"""
Reports — aggregate stats for the dashboard and Reports page.

All queries are scoped to the current user via RLS-equivalent filtering
(explicit .eq("user_id", ...) since we use the service-role client here).
"""
from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
def summary(user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()

    leads_resp = db.table("leads").select("id,status,lead_score").eq("user_id", user.id).execute()
    leads = leads_resp.data or []

    analyzed_resp = (
        db.table("website_analyses").select("id", count="exact").eq("user_id", user.id).execute()
    )
    messages_resp = (
        db.table("whatsapp_messages").select("id", count="exact").eq("user_id", user.id).execute()
    )
    proposals_resp = db.table("proposals").select("id,status").eq("user_id", user.id).execute()

    total_leads = len(leads)
    won = sum(1 for l in leads if l.get("status") == "won")
    meetings = sum(1 for l in leads if l.get("status") in ("meeting", "proposal_sent", "won"))
    scores = [l["lead_score"] for l in leads if l.get("lead_score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    conversion_rate = round((won / total_leads) * 100, 1) if total_leads else 0.0

    return {
        "total_leads": total_leads,
        "analyzed": analyzed_resp.count or 0,
        "messages_generated": messages_resp.count or 0,
        "meetings": meetings,
        "clients_won": won,
        "proposals_sent": sum(1 for p in (proposals_resp.data or []) if p.get("status") != "draft"),
        "conversion_rate_percent": conversion_rate,
        "average_lead_score": avg_score,
    }


@router.get("/timeseries")
def timeseries(interval: str = "daily", user: CurrentUser = Depends(get_current_user)):
    """
    interval: 'daily' | 'weekly' | 'monthly'
    Returns lead creation counts bucketed by the requested interval, for the
    Reports page charts (Recharts on the frontend).
    """
    db = get_supabase_admin()
    resp = db.table("leads").select("created_at").eq("user_id", user.id).execute()
    rows = resp.data or []

    buckets: dict[str, int] = {}
    for row in rows:
        created = row["created_at"][:10]  # YYYY-MM-DD
        if interval == "monthly":
            key = created[:7]  # YYYY-MM
        elif interval == "weekly":
            key = created[:10]  # placeholder: real ISO-week bucketing added in feature-build phase
        else:
            key = created
        buckets[key] = buckets.get(key, 0) + 1

    series = [{"date": k, "count": v} for k, v in sorted(buckets.items())]
    return {"interval": interval, "series": series}

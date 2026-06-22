"""Shared Pydantic schemas for the Leads domain."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LeadSearchRequest(BaseModel):
    city: str
    category: str
    max_results: int = Field(default=20, ge=1, le=60)


class LeadBase(BaseModel):
    business_name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    google_rating: Optional[float] = None
    review_count: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    business_age_years: Optional[int] = None
    has_website: bool = False
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    google_place_id: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    follow_up_at: Optional[datetime] = None
    lead_score: Optional[int] = Field(default=None, ge=0, le=100)


class Lead(LeadBase):
    id: str
    user_id: str
    status: str
    notes: Optional[str] = None
    tags: list[str] = []
    lead_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

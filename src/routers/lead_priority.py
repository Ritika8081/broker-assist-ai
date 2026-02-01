from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Optional
from src.services.lead_scoring import score_leads


class Lead(BaseModel):
    lead_id: str
    source: Optional[str] = None
    budget: int
    city: Optional[str] = None
    property_type: Optional[str] = None
    last_activity_minutes_ago: int
    past_interactions: int
    notes: str
    status: str


class LeadPriorityRequest(BaseModel):
    leads: List[Lead]
    max_results: Optional[int] = 10


router = APIRouter()


@router.post("/lead-priority")
def lead_priority(payload: LeadPriorityRequest):
    leads = [lead.dict() for lead in payload.leads]
    max_results = payload.max_results
    return score_leads(leads, max_results)

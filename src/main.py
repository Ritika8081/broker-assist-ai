from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from src.services.lead_scoring import score_leads
from src.services.call_evaluator import evaluate_call

# Initialize FastAPI app
app = FastAPI(title="Fixit - Real Estate AI", version="1.0")

# Request/Response Models
class Lead(BaseModel):
    lead_id: str
    source: str
    budget: float
    city: str
    property_type: str
    last_activity_minutes_ago: int
    past_interactions: int
    notes: str
    status: str

class LeadPriorityRequest(BaseModel):
    leads: List[Lead]
    max_results: int = 10

class CallEvalRequest(BaseModel):
    call_id: str
    lead_id: str
    transcript: str
    duration_seconds: int

# Root endpoint - health check
@app.get("/")
async def root():
    return {
        "message": "Fixit Real Estate AI System",
        "version": "1.0",
        "endpoints": [
            "POST /api/v1/lead-priority",
            "POST /api/v1/call-eval"
        ]
    }

# Lead prioritization endpoint - returns ranked leads with scores
@app.post("/api/v1/lead-priority")
async def lead_priority(request: LeadPriorityRequest):
    """Rank leads by priority score and bucket."""
    leads_dict = [lead.dict() for lead in request.leads]
    ranked = score_leads(leads_dict, request.max_results)
    return {
        'status': 'success',
        'total_leads': len(request.leads),
        'processed': len(ranked),
        'leads': ranked
    }

# Call quality evaluation endpoint - analyzes transcript with Phi LLM
@app.post("/api/v1/call-eval")
async def call_evaluation(request: CallEvalRequest):
    """Evaluate call quality and provide metrics."""
    result = evaluate_call(request.dict())
    return {
        'status': 'success',
        'data': result
    }

# Health check endpoint - useful for Docker/monitoring
@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "model": "phi"}
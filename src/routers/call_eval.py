from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.services.call_evaluator import evaluate_call


router = APIRouter()


class CallIn(BaseModel):
    call_id: str
    lead_id: Optional[str] = None
    transcript: str
    duration_seconds: Optional[int] = 0

@router.post("/call-eval")
def call_eval(payload: CallIn):
    return evaluate_call(payload.dict())
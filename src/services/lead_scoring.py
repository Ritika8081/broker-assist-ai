# src/services/lead_scoring.py

import json
from pathlib import Path

from ..models.llm_client import call_llm


PROMPT_PATH = Path(__file__).resolve().parents[1] / "models" / "prompts" / "lead_notes_prompt.txt"


def interpret_notes(notes: str) -> dict:
    if not notes:
        return {"intent_level": 0.0, "urgency_level": 0.0, "constraints": ""}

    try:
        prompt = PROMPT_PATH.read_text(encoding="utf-8") + f"\n\nNotes: {notes}\n"
        out, _ = call_llm(prompt)
        parsed = json.loads(out)
        return {
            "intent_level": float(parsed.get("intent_level", 0.0)),
            "urgency_level": float(parsed.get("urgency_level", 0.0)),
            "constraints": str(parsed.get("constraints", ""))
        }
    except Exception:
        return {"intent_level": 0.0, "urgency_level": 0.0, "constraints": ""}


def score_single_lead(lead):
    score = 0.0
    reasons = []

    budget = lead.get("budget", 0)
    last_activity = lead.get("last_activity_minutes_ago", 999999)
    past_interactions = lead.get("past_interactions", 0)
    status = (lead.get("status", "") or "").lower()
    notes = lead.get("notes", "")

    # Budget signal
    if budget > 5000000:
        score += 0.3
        reasons.append("High budget")

    # Recency signal
    if last_activity < 1000:
        score += 0.3
        reasons.append("Recent activity")

    # Engagement
    if past_interactions >= 3:
        score += 0.2
        reasons.append("Multiple interactions")

    # Status
    if status == "follow_up":
        score += 0.2
        reasons.append("Follow-up stage")

    # Notes (OSS LLM interpretation)
    signals = interpret_notes(notes)
    if signals["intent_level"] >= 0.7:
        score += 0.1
        reasons.append("High intent (notes)")
    if signals["urgency_level"] >= 0.7:
        score += 0.1
        reasons.append("High urgency (notes)")
    if signals["constraints"]:
        reasons.append(f"Constraints: {signals['constraints']}")

    # Bucket
    if score >= 0.7:
        bucket = "hot"
    elif score >= 0.4:
        bucket = "warm"
    else:
        bucket = "cold"

    return {
        "lead_id": lead["lead_id"],
        "priority_score": round(score, 2),
        "priority_bucket": bucket,
        "reasons": reasons
    }


def score_leads(leads, max_results=None):
    """
    Assigns a priority_bucket and priority_score to each lead using raw CSV fields.
    Simple logic:
    - hot: score >= 0.7
    - warm: score 0.4-0.7
    - cold: score < 0.4
    """
    results = [score_single_lead(lead) for lead in leads]
    
    # Sort by priority_score descending
    results.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Limit results if max_results is specified
    if max_results is not None:
        results = results[:max_results]
    
    return results

# src/services/lead_scoring.py
"""Lead prioritization service using hybrid deterministic + LLM approach."""

from typing import List, Dict
import json
from src.models.llm_client import call_llm_with_retry, extract_json_from_response, load_prompt_template

def interpret_notes_with_llm(notes: str) -> Dict:
    """Use Phi LLM to interpret lead notes for intent and urgency with retry logic."""
    if not notes:
        return {"intent_score": 0.5, "urgency_score": 0.5}
    
    # Load prompt from template file
    from src.models.llm_client import load_prompt_template
    prompt_template = load_prompt_template('lead_notes_prompt')
    if not prompt_template:
        # Fallback to hardcoded prompt if file not found
        prompt_template = """Analyze this real estate lead note and return JSON:

Note: {notes}

Return JSON with:
- intent_score: 0-1 (how serious is the buyer)
- urgency_score: 0-1 (how time-sensitive is this lead)

Example: {{"intent_score": 0.8, "urgency_score": 0.6}}"""
    
    prompt = prompt_template.format(notes=notes)
    
    # Call LLM with retry logic (max 3 attempts)
    llm_response = call_llm_with_retry(prompt, model='phi', max_retries=3)
    
    if llm_response:
        parsed = extract_json_from_response(llm_response['content'])
        if parsed:
            return {
                "intent_score": float(parsed.get("intent_score", 0.5)),
                "urgency_score": float(parsed.get("urgency_score", 0.5))
            }
    
    return {"intent_score": 0.5, "urgency_score": 0.5}

# Hybrid scoring: deterministic rules + LLM analysis
def score_single_lead(lead: Dict) -> Dict:
    """Score a single lead using hybrid deterministic + LLM approach."""
    
    # Recency: penalize leads inactive for long periods
    minutes_ago = lead.get('last_activity_minutes_ago', 999999)
    if minutes_ago < 60:
        recency_score = 1.0
    elif minutes_ago < 360:
        recency_score = 0.7
    elif minutes_ago < 1440:
        recency_score = 0.4
    else:
        recency_score = 0.1
    
    # Interaction scoring (0-1)
    interactions = lead.get('past_interactions', 0)
    interaction_score = min(interactions / 5.0, 1.0)
    
    # Intent scoring: deterministic + LLM-based
    notes_lower = lead.get('notes', '').lower()
    intent_keywords = ['serious', 'hot', 'interested', 'engaged', 'visit', 'weekend', 'ready', 'visiting']
    keyword_intent = 0.9 if any(kw in notes_lower for kw in intent_keywords) else 0.4
    
    # Use LLM to interpret notes if available (especially for complex notes)
    llm_intent = 0.5
    llm_used = False
    if len(notes_lower) > 10:  # Only use LLM for meaningful notes
        llm_analysis = interpret_notes_with_llm(lead.get('notes', ''))
        llm_intent = llm_analysis.get("intent_score", 0.5)
        llm_used = True
    else:
        llm_intent = keyword_intent
    
    # Combine keyword and LLM intent (blend them)
    if llm_used:
        intent_score = (keyword_intent * 0.4 + llm_intent * 0.6)  # Weight LLM more
    else:
        intent_score = keyword_intent
    
    # Combined weighted score
    priority_score = (recency_score * 0.4) + (interaction_score * 0.3) + (intent_score * 0.3)
    priority_score = round(min(priority_score, 1.0), 2)
    
    # Determine bucket
    if priority_score >= 0.7:
        bucket = "hot"
    elif priority_score >= 0.4:
        bucket = "warm"
    else:
        bucket = "cold"
    
    # Reasons with explicit LLM mention
    reasons = []
    if recency_score >= 0.7:
        reasons.append(f"Recent activity ({minutes_ago} min ago)")
    if interaction_score >= 0.6:
        reasons.append(f"High engagement ({interactions} interactions)")
    if intent_score >= 0.7:
        llm_indicator = " via Phi LLM" if llm_used else ""
        reasons.append(f"Strong purchase intent signals{llm_indicator}")
    if bucket == "hot" and not reasons:
        reasons.append("Hot lead - High priority")
    
    return {
        'lead_id': lead.get('lead_id'),
        'source': lead.get('source'),
        'city': lead.get('city'),
        'budget': lead.get('budget'),
        'priority_score': priority_score,
        'priority_bucket': bucket,
        'reasons': reasons if reasons else ["Moderate lead potential"],
        'llm_analysis': "phi" if llm_used else None,
        'model_metadata': {
            'model_name': 'phi',
            'analysis_type': 'llm-based' if llm_used else 'deterministic-only',
            'uses_llm': llm_used
        }
    }

def score_leads(leads: List[Dict], max_results: int = None) -> List[Dict]:
    """Rank multiple leads and return top results."""
    scored = [score_single_lead(lead) for lead in leads]
    # Sort by priority score descending
    sorted_leads = sorted(scored, key=lambda x: x['priority_score'], reverse=True)
    
    if max_results is not None:
        sorted_leads = sorted_leads[:max_results]
    
    return sorted_leads

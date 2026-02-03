import time
import json
from typing import Dict, List
from models.llm_client import call_llm_with_retry, extract_json_from_response, load_prompt_template

# Call quality evaluation with Phi LLM
def evaluate_call(call: Dict) -> Dict:
    """Evaluate call quality using Phi LLM via Ollama with retry logic."""
    
    start_time = time.time()
    
    transcript = call.get("transcript", "")
    call_id = call.get("call_id", "")
    duration_seconds = call.get("duration_seconds", 0)
    
    latency = 0
    
    # Try LLM analysis first with retry logic
    if transcript:
        # Load prompt template from file
        prompt_template = load_prompt_template('call_eval_prompt')
        if not prompt_template:
            # Fallback to hardcoded if file not found
            prompt_template = """Analyze this sales call transcript and provide JSON evaluation:

Transcript: {transcript}

Return JSON with these fields (0-1 scale):
- rapport_building: float (rapport and positive interaction)
- need_discovery: float (understanding customer needs)
- closing_attempt: float (attempt to close or schedule)
- compliance_risk: float (pressure tactics, false claims)
- quality_score: float (overall 0-1)
- summary: string (1-2 sentence summary)
- next_actions: list of 1-3 recommended actions

Example:
{{"rapport_building": 0.8, "need_discovery": 0.9, "closing_attempt": 0.7, "compliance_risk": 0.1, "quality_score": 0.8, "summary": "Good call", "next_actions": ["Follow up"]}}"""
        
        prompt = prompt_template.format(transcript=transcript)
        
        # Call LLM with retry logic (max 3 attempts)
        llm_response = call_llm_with_retry(prompt, model='phi', max_retries=3)
        
        if llm_response:
            latency = llm_response['latency']
            parsed = extract_json_from_response(llm_response['content'])
            
            if parsed:
                return {
                    "call_id": call_id,
                    "quality_score": float(parsed.get("quality_score", 0.5)),
                    "labels": {
                        "rapport_building": float(parsed.get("rapport_building", 0.5)),
                        "need_discovery": float(parsed.get("need_discovery", 0.5)),
                        "closing_attempt": float(parsed.get("closing_attempt", 0.5)),
                        "compliance_risk": float(parsed.get("compliance_risk", 0.1))
                    },
                    "summary": parsed.get("summary", "Call analyzed"),
                    "next_actions": parsed.get("next_actions", ["Follow up"]),
                    "model_metadata": {
                        "model_name": "phi",
                        "latency_seconds": round(latency, 3),
                        "input_length": len(transcript),
                        "duration_seconds": duration_seconds,
                        "analysis_type": "llm-based",
                        "retry_attempt": llm_response.get('attempt', 1)
                    }
                }
    
    # Fallback: keyword-based analysis if LLM unavailable
    latency = time.time() - start_time
    transcript_lower = transcript.lower()
    
    # Keyword scoring for each dimension
    rapport_keywords = ['thanks', 'great', 'perfect', 'wonderful', 'excellent', 'amazing', 'pleasure', 'glad']
    rapport_score = min(sum(1 for kw in rapport_keywords if kw in transcript_lower) / 3, 1.0)
    
    discovery_keywords = ['what', 'tell', 'budget', 'location', 'interested', 'property', 'requirements', 'looking']
    discovery_score = min(sum(1 for kw in discovery_keywords if kw in transcript_lower) / 4, 1.0)
    
    closing_keywords = ['visit', 'schedule', 'tomorrow', 'weekend', 'arrange', 'booking', 'ready', 'book']
    closing_score = min(sum(1 for kw in closing_keywords if kw in transcript_lower) / 3, 1.0)
    
    risk_keywords = ['pressure', 'discount', 'limited', 'urgent', 'now']
    compliance_risk = min(sum(1 for kw in risk_keywords if kw in transcript_lower) / 5, 0.3)
    
    # Weighted quality score: rapport(30%) + discovery(30%) + closing(40%)
    quality_score = round((rapport_score * 0.3 + discovery_score * 0.3 + closing_score * 0.4), 2)
    
    # Generate summary based on score bands
    if quality_score >= 0.8:
        summary = "Excellent call - Strong rapport, good discovery, clear closing attempt"
    elif quality_score >= 0.6:
        summary = "Good call - Positive engagement, adequate discovery, closing attempted"
    elif quality_score >= 0.4:
        summary = "Average call - Some engagement issues, needs better discovery"
    else:
        summary = "Poor call - Weak rapport, minimal discovery, no closing attempt"
    
    # Generate coaching recommendations
    next_actions = []
    if quality_score < 0.6:
        next_actions.append("Review call with agent for coaching")
    if closing_score < 0.5:
        next_actions.append("Coach on closing techniques")
    if quality_score >= 0.8:
        next_actions.append("Share as best practice example")
    if not next_actions:
        next_actions.append("Follow up with lead")
    
    return {
        "call_id": call_id,
        "quality_score": quality_score,
        "labels": {
            "rapport_building": round(rapport_score, 2),
            "need_discovery": round(discovery_score, 2),
            "closing_attempt": round(closing_score, 2),
            "compliance_risk": round(compliance_risk, 2)
        },
        "summary": summary,
        "next_actions": next_actions,
        "model_metadata": {
            "model_name": "phi",
            "latency_seconds": round(latency, 3),
            "input_length": len(transcript),
            "duration_seconds": duration_seconds,
            "analysis_type": "keyword-based-fallback",
            "retry_attempt": 0
        }
    }
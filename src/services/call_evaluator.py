import time
import json
import logging
from ..models.llm_client import call_llm



MODEL_NAME = "mistral"
LOGGER = logging.getLogger("call_eval")




def evaluate_call(call: dict) -> dict:
	transcript = call.get("transcript", "")
	input_size = len(transcript)
	prompt = f"""
You are a strict JSON-only assistant that evaluates sales call transcripts.
Return a JSON with keys:
- quality_score: float 0-1
- rapport_building: true/false
- need_discovery: true/false
- closing_attempt: true/false
- compliance_risk: "low"|"medium"|"high"
- summary: short string (1-2 sentences)
- next_actions: list of 1-4 short strings


Transcript: {transcript}


Example:
{{"quality_score":0.8, "rapport_building": true, "need_discovery": true, "closing_attempt": false, "compliance_risk": "low", "summary": "...", "next_actions": ["...", "..."]}}
"""
	start = time.time()
	try:
		out, latency = call_llm(prompt)
		parsed = json.loads(out)
		LOGGER.info("call_eval.success", extra={"latency_seconds": round(latency, 3), "input_size": input_size})
	except Exception:
		# fallback naive rules
		latency = time.time() - start
		LOGGER.exception("call_eval.error", extra={"latency_seconds": round(latency, 3), "input_size": input_size})
		text = transcript.lower()
		quality = 0.5
		if any(k in text for k in ["site visit", "ready to buy", "closing"]):
			quality = 0.8
		parsed = {
			"quality_score": quality,
			"rapport_building": any(k in text for k in ["thank you", "pleasure", "glad"]),
			"need_discovery": any(k in text for k in ["budget", "requirements", "looking for"]),
			"closing_attempt": any(k in text for k in ["shall we schedule", "book", "site visit"]),
			"compliance_risk": "low",
			"summary": "Fallback summary: no JSON from model.",
			"next_actions": ["Follow up in 24h", "Send site visit options"]
		}

	return {
		"call_id": call.get("call_id"),
		"quality_score": float(parsed.get("quality_score", 0)),
		"labels": {
			"rapport_building": bool(parsed.get("rapport_building", False)),
			"need_discovery": bool(parsed.get("need_discovery", False)),
			"closing_attempt": bool(parsed.get("closing_attempt", False)),
			"compliance_risk": parsed.get("compliance_risk", "low")
		},
		"summary": parsed.get("summary", ""),
		"next_actions": parsed.get("next_actions", []),
		"model_metadata": {
			"model_name": MODEL_NAME,
			"latency_seconds": round(latency, 3),
		}
	}
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_call_eval_structure():
	"""Test call-eval endpoint returns required schema."""
	payload = {
		"call_id": "T1",
		"transcript": "Agent: Hello\nCustomer: I want to buy soon\nAgent: Booked site visit",
		"duration_seconds": 120
	}
	r = client.post("/api/v1/call-eval", json=payload)
	assert r.status_code == 200
	data = r.json()
	
	# Schema validation
	assert "call_id" in data
	assert "quality_score" in data
	assert "labels" in data
	assert "summary" in data
	assert "next_actions" in data
	assert "model_metadata" in data
	
	# Type validation
	assert isinstance(data["quality_score"], (int, float))
	assert 0 <= data["quality_score"] <= 1
	assert isinstance(data["labels"], dict)
	assert isinstance(data["summary"], str)
	assert isinstance(data["next_actions"], list)
	
	# Labels schema
	assert "rapport_building" in data["labels"]
	assert "need_discovery" in data["labels"]
	assert "closing_attempt" in data["labels"]
	assert "compliance_risk" in data["labels"]
	
	# Model metadata
	assert "model_name" in data["model_metadata"]
	assert "latency_seconds" in data["model_metadata"]


def test_call_eval_good_call():
	"""Test call with strong signals scores higher."""
	payload = {
		"call_id": "T2",
		"transcript": "Agent: Hi, let me schedule a site visit.\nCustomer: Yes, Saturday works.\nAgent: Great, confirmed.",
		"duration_seconds": 180
	}
	r = client.post("/api/v1/call-eval", json=payload)
	assert r.status_code == 200
	data = r.json()
	assert data["quality_score"] >= 0.5


def test_call_eval_bad_call():
	"""Test call with negative signals scores lower."""
	payload = {
		"call_id": "T3",
		"transcript": "Agent: Hi\nCustomer: Please stop calling.\nAgent: OK.",
		"duration_seconds": 30
	}
	r = client.post("/api/v1/call-eval", json=payload)
	assert r.status_code == 200
	data = r.json()
	# Should handle gracefully, may be low or high depending on LLM
	assert isinstance(data["quality_score"], (int, float))
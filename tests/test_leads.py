from src.services.lead_scoring import score_leads


def test_scoring_hot():
	"""Test a lead with high score signals → hot bucket."""
	lead = {
		"lead_id": "T1",
		"budget": 10000000,
		"last_activity_minutes_ago": 10,
		"past_interactions": 3,
		"notes": "Ready to buy, closing this week",
		"status": "follow_up"
	}
	res = score_leads([lead])[0]
	assert res["priority_score"] >= 0.7
	assert res["priority_bucket"] == "hot"
	assert "reasons" in res
	assert len(res["reasons"]) > 0


def test_scoring_cold():
	"""Test a lead with low score signals → cold bucket."""
	lead = {
		"lead_id": "T2",
		"budget": 2000000,
		"last_activity_minutes_ago": 3000,
		"past_interactions": 0,
		"notes": "Just browsing",
		"status": "new"
	}
	res = score_leads([lead])[0]
	assert res["priority_score"] < 0.4
	assert res["priority_bucket"] == "cold"


def test_scoring_warm():
	"""Test a lead in middle range → warm bucket."""
	lead = {
		"lead_id": "T3",
		"budget": 5000000,
		"last_activity_minutes_ago": 500,
		"past_interactions": 1,
		"notes": "Interested but comparing",
		"status": "contacted"
	}
	res = score_leads([lead])[0]
	assert 0.4 <= res["priority_score"] < 0.7
	assert res["priority_bucket"] == "warm"


def test_output_schema():
	"""Test that output has required schema."""
	lead = {
		"lead_id": "T4",
		"budget": 5000000,
		"last_activity_minutes_ago": 100,
		"past_interactions": 2,
		"notes": "Test",
		"status": "follow_up"
	}
	res = score_leads([lead])[0]
	assert "lead_id" in res
	assert "priority_score" in res
	assert "priority_bucket" in res
	assert "reasons" in res
	assert isinstance(res["reasons"], list)
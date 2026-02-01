# broker-assist-ai

**Product:** AI-powered lead prioritization and call quality evaluation for real estate agents.

This repo implements a hybrid rule+LLM system for:

- **Lead Prioritization** — Rank leads as hot/warm/cold using budget, recency, engagement, status, and notes intent.
- **Call Quality Evaluation** — Assess call transcripts for quality, rapport, need discovery, closing, and compliance.

---

## Quick Start (Local)

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
git clone https://github.com/Ritika8081/broker-assist-ai.git
cd broker-assist-ai
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python scripts/generate_data.py
```

### Run

```bash
uvicorn src.main:app --reload
```

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

---

## Docker

### Build & Run

```bash
docker build -t broker-assist-ai .
docker run -p 8000:8000 broker-assist-ai
```

---

## Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Example API Calls

### Lead Priority

```bash
curl -X POST "http://localhost:8000/api/v1/lead-priority" \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [{
      "lead_id": "L001",
      "budget": 5000000,
      "city": "Delhi",
      "property_type": "2BHK",
      "last_activity_minutes_ago": 100,
      "past_interactions": 3,
      "notes": "Urgent need, loan pre-approved",
      "status": "follow_up"
    }],
    "max_results": 5
  }'
```

### Call Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/call-eval" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "C001",
    "transcript": "Agent: Hello from ABC Realty.\nClient: I am interested.\nAgent: Can we schedule a visit?\nClient: Saturday works.",
    "duration_seconds": 180
  }'
```

---

## Model & Architecture

### LLM: Mistral (via Ollama)

**Why:**

- Open-source, cost-effective, privacy-preserving
- ~1–2 sec inference, good instruction-following
- Runs locally on port 11434

**Setup:**

```bash
# Download Ollama: https://ollama.ai
ollama pull mistral
# Runs automatically on localhost:11434
```

### Scoring Logic

**Lead Priority:**

- Budget > 5M → +0.3
- Recent activity (< 1000 mins) → +0.3
- Multiple interactions (≥ 3) → +0.2
- Follow-up status → +0.2
- LLM notes analysis → +0.2 max

Buckets: hot (≥0.7), warm (0.4–0.7), cold (<0.4)

**Call Quality:**

- LLM analyzes transcript
- Outputs: quality_score (0–1), labels, summary, next_actions
- Retry logic on failure
- Fallback rule-based if LLM fails

---

## Trade-offs

| Decision                     | Rationale                              |
| ---------------------------- | -------------------------------------- |
| Mistral over ChatGPT         | Cost, privacy, local control           |
| Retry logic in LLM client    | Graceful failure handling              |
| Fallback rule-based eval     | System resilience                      |
| Simple thresholds (0.7, 0.4) | Explainability & tuning ease           |
| No fine-tuning               | Time constraint; base model sufficient |

---

## Project Structure

```
src/
  ├─ main.py
  ├─ routers/
  │  ├─ lead_priority.py
  │  └─ call_eval.py
  ├─ services/
  │  ├─ lead_scoring.py
  │  └─ call_evaluator.py
  └─ models/
     ├─ llm_client.py
     └─ prompts/
data/
  ├─ leads.csv
  ├─ calls.json
  ├─ eval_leads_labels.csv
  └─ eval_calls_labels.csv
tests/
  ├─ test_leads.py
  └─ test_calls.py
scripts/
  ├─ generate_data.py
  ├─ evaluate_leads.py
  └─ evaluate_calls.py
Dockerfile
requirements.txt
README.md
evaluation_leads.md
evaluation_calls.md
```

---

## Results (Part C)

**Lead Prioritisation:** Accuracy 35%, Macro F1 0.30 → See [evaluation_leads.md](evaluation_leads.md)

**Call Quality:** Accuracy 50%, F1 0.29 → See [evaluation_calls.md](evaluation_calls.md)

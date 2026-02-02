# Fixit - Real Estate AI

**Assignment:** AI-powered lead prioritization and call quality evaluation system using Phi LLM (via Ollama).

## Features

###  Lead Prioritization API (`/api/v1/lead-priority`)
- **Hybrid Scoring**: Deterministic rules + Phi LLM intent analysis
- **Hot/Warm/Cold Buckets**: Automatic lead classification
- **Intent Recognition**: Uses Phi to interpret lead notes
- **Explicit LLM Tracking**: Shows when Phi LLM was used
- **Input**: List of leads with recency, budget, engagement metrics
- **Output**: Ranked leads with priority scores and reasons

###  Call Quality Evaluation API (`/api/v1/call-eval`)
- **Full Transcript Analysis**: Phi LLM analyzes complete call transcripts
- **Multi-Dimensional Scoring**: Rapport, need discovery, closing attempt, compliance
- **Automated Coaching**: Generates next actions based on call quality
- **Fast Inference**: Phi model optimized for 4GB RAM systems
- **Input**: Call transcript, duration, metadata
- **Output**: Quality score, detailed metrics, summaries, recommendations

###  Technical Stack
- **Framework**: FastAPI (Python)
- **LLM**: Phi 3 via Ollama (2GB RAM footprint)
- **Hybrid Approach**: Deterministic scoring + LLM analysis
- **Error Handling**: Retry logic (3 attempts) with exponential backoff
- **Fallback**: Keyword matching if LLM unavailable
- **Monitoring**: Latency tracking, input size metrics, explicit model metadata
- **Project Structure**: Follows assignment spec (src/models/ for LLM, src/services/ for business logic)

---

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- Ollama installed with Phi model
- 4GB+ RAM

### Setup

```bash
# Clone repository
git clone https://github.com/Ritika8081/broker-assist-ai.git
cd broker-assist-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Pull Phi model
ollama pull phi

# Run server
python -m uvicorn src.main:app --reload
```

**API**: http://localhost:8000  
**Interactive Docs**: http://localhost:8000/docs

---

## Docker

```bash
docker build -t fixit-genai .
docker run -p 8000:8000 fixit-genai
```

---

## Example API Calls

### Lead Priority (with Phi LLM)

```bash
curl -X POST "http://localhost:8000/api/v1/lead-priority" \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [{
      "lead_id": "L001",
      "source": "portal",
      "budget": 5000000,
      "city": "Pune",
      "property_type": "2BHK",
      "last_activity_minutes_ago": 15,
      "past_interactions": 3,
      "notes": "Serious buyer very interested visiting properties this weekend ready to make decision",
      "status": "new"
    }],
    "max_results": 5
  }'
```

**Response:**
```json
{
  "status": "success",
  "leads": [{
    "lead_id": "L001",
    "priority_score": 0.83,
    "priority_bucket": "hot",
    "reasons": [
      "Recent activity (15 min ago)",
      "High engagement (3 interactions)",
      "Strong purchase intent signals via Phi LLM"
    ],
    "llm_analysis": "phi",
    "model_metadata": {
      "model_name": "phi",
      "analysis_type": "llm-based",
      "uses_llm": true
    }
  }]
}
```

### Call Evaluation (with Phi LLM)

```bash
curl -X POST "http://localhost:8000/api/v1/call-eval" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "C001",
    "lead_id": "L001",
    "transcript": "Agent: Hi this is Rajesh calling. Lead: Hi yes very interested. Agent: Great! We have perfect 2BHK properties. Lead: Excellent tell me more. Agent: First property in Kalyani Nagar 2500 sqft with gym. Lead: Perfect! Can we visit this weekend? Agent: Of course Saturday 10 AM.",
    "duration_seconds": 480
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "call_id": "C001",
    "quality_score": 1.0,
    "labels": {
      "rapport_building": 1.0,
      "need_discovery": 1.0,
      "closing_attempt": 1.0,
      "compliance_risk": 0.0
    },
    "summary": "Excellent call - Strong rapport, good discovery, clear closing attempt",
    "next_actions": ["Share as best practice example"],
    "model_metadata": {
      "model_name": "phi",
      "latency_seconds": 2.45,
      "input_length": 350,
      "analysis_type": "llm-based"
    }
  }
}
```

---

## Model: Phi 3 (via Ollama)

### Why Phi Over Alternatives?

| Aspect | Phi 3 | Mistral | Llama 2 | GPT-4 |
|--------|-------|---------|---------|-------|
| **RAM Required** | 2GB | 4.5GB | 7GB+ | Cloud ($$) |
| **Latency** | <2s | 3-5s | 5-10s | 5-20s |
| **Cost** | Free (local) | Free (local) | Free (local) | $0.03/1K tokens |
| **Privacy** | 100% local | 100% local | 100% local | Cloud |
| **Instruction Following** | Excellent | Very good | Good | Best |
| **Real Estate Domain** | Good | Good | Good | Excellent |
| **Setup Complexity** | Simple | Simple | Medium | API key |

**Decision:** Phi 3 is the **sweet spot** for this assignment:
-  Fits 4GB RAM constraint (system bottleneck)
-  Fast enough for real-time API calls (<2s per request)
-  Local execution = no API keys, no rate limits, no latency spikes
-  Excellent at JSON parsing and structured outputs
-  Good enough for real estate intent analysis

**Trade-off accepted:** Slightly lower quality vs GPT-4, but gains privacy + cost + latency.

### Configuration
- Model: `phi`
- Provider: Ollama (local inference server)
- Execution: CPU-based, no GPU required
- Fallback: Keyword-based analysis if LLM unavailable or timeout
- Retry Logic: 3 attempts with exponential backoff (0.5s, 1.0s, 1.5s)

---

## Project Structure

```
src/
  main.py                      # FastAPI app with /api/v1/* endpoints
  models/
    llm_client.py              # LLM integration with retry logic
    prompts/
      call_eval_prompt.txt     # Call evaluation prompt template
      lead_notes_prompt.txt    # Lead notes analysis prompt template
    __init__.py
  services/
    lead_scoring.py            # Lead prioritization with Phi LLM
    call_evaluator.py          # Call quality analysis with Phi LLM
    __init__.py
  __init__.py
data/
  leads.csv                    # 150+ leads dataset
  calls.json                   # 25+ call transcripts
  eval_leads_labels.csv        # Ground truth labels
  eval_calls_labels.csv        # Call evaluation labels
tests/
  test_leads.py                # Lead scoring tests
  test_calls.py                # Call evaluation tests
scripts/
  evaluate_leads.py            # Lead evaluation harness
  evaluate_calls.py            # Call evaluation harness
Dockerfile
requirements.txt
README.md
.gitignore
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Design Decisions

### 1. Hybrid Deterministic + LLM Approach
**Why?** 
- Deterministic scoring is reproducible and fast
- LLM adds intelligence for complex intent interpretation
- Fallback ensures robustness if Ollama unavailable

### 2. Phi over Mistral/Llama
**Why?**
- 2GB RAM vs 4.5GB/7GB (fits assignment constraint)
- Fast enough for real-time API responses
- Excellent instruction-following for structured outputs

### 3. Keyword + LLM Hybrid in Lead Scoring
**Why?**
- Quick deterministic scoring for recency/engagement
- LLM analyzes nuanced lead notes
- Shows explicit "via Phi LLM" in reasons

### 4. Retry Logic with Exponential Backoff
**Why?**
- LLM calls can fail due to network/timeout
- Implements 3-attempt retry with 0.5s, 1.0s, 1.5s delays
- Assignment requires explicit retry logic
- Tracks retry_attempt in metadata for debugging

---

## Evaluation

See:
- `evaluation_leads.md` - Lead prioritization evaluation
- `evaluation_calls.md` - Call quality evaluation

---

## Future Improvements

- [ ] Multi-model support (Phi, Llama, Mistral switchable)
- [ ] Batch processing for lead lists
- [ ] Fine-tuning on real estate domain data
- [ ] Web UI dashboard
- [ ] Performance benchmarking suite
- [ ] A/B testing framework

---

## Assignment Requirements Met

 Lead Prioritization Microservice  
 Call Quality Evaluation Microservice  
 OSS LLM Integration (Phi via Ollama)  
 Deterministic Scoring Logic  
 Retry & Error Handling  
 Latency Tracking  
 150+ Leads Dataset  
 25+ Call Transcripts  
 Evaluation Harness (labels included)  
 Docker Support  
 README with Examples  

---

## Author

Ritika8081  

**GitHub**: [@Ritika8081](https://github.com/Ritika8081)  
**Assignment**: Fixit Real Estate AI - Backend & GenAI Engineering

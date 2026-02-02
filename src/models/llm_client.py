# src/models/llm_client.py
"""LLM client for Phi model integration via Ollama."""

import time
import json
import os
from typing import Dict, Optional

# Check if ollama is available for local inference
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def load_prompt_template(template_name: str) -> str:
    """Load prompt template from file."""
    # Construct path to prompts folder
    prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    prompt_file = os.path.join(prompt_dir, f'{template_name}.txt')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def call_llm_with_retry(prompt: str, model: str = "phi", max_retries: int = 3) -> Optional[Dict]:
    """Call Ollama LLM with retry logic (3 attempts with exponential backoff)."""
    if not OLLAMA_AVAILABLE:
        return None
    
    # Retry loop with exponential backoff strategy
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                stream=False
            )
            latency = time.time() - start_time
            
            return {
                'content': response['message']['content'],
                'latency': latency,
                'model': model,
                'attempt': attempt + 1
            }
        except Exception as e:
            print(f"LLM attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt == max_retries - 1:
                return None
            # Wait 0.5s, 1.0s, 1.5s between retries (exponential backoff)
            time.sleep(0.5 * (attempt + 1))
    
    return None


def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """Extract and parse JSON object from LLM response text."""
    try:
        # Find JSON object boundaries in response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return None
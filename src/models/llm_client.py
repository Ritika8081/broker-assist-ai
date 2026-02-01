import subprocess
import time


DEFAULT_MODEL = "mistral"
RETRIES = 2




def call_llm(prompt: str, model: str = DEFAULT_MODEL):
	"""Call local Ollama model via subprocess. Returns (output_text, latency_seconds).
	Fallbacks are handled by caller.
	"""
	last_err = None
	for attempt in range(RETRIES + 1):
		start = time.time()
		try:
			# Using ollama run <model> and passing prompt via stdin
			proc = subprocess.run(
				["ollama", "run", model],
				input=prompt,
				text=True,
				capture_output=True,
				timeout=20
			)
			latency = time.time() - start
			out = proc.stdout.strip()
			if out:
				return out, latency
			else:
				last_err = proc.stderr.decode() if proc.stderr else "no output"
		except Exception as e:
			last_err = str(e)
		# simple backoff
		time.sleep(0.5 * (attempt + 1))
	raise RuntimeError(f"LLM call failed after retries: {last_err}")
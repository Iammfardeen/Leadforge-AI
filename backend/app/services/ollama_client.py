"""
Thin wrapper around Groq's hosted Llama API.

Originally this called a local Ollama container. For free, always-on
deployment (no machine running Ollama 24/7 required), it now calls Groq's
OpenAI-compatible Chat Completions endpoint instead — same Llama family of
models, hosted, free tier, no credit card. The public interface (OllamaError,
generate, generate_json) is unchanged so every caller (ai_report.py,
mockup.py, whatsapp.py) needed zero changes.

Get a free key at https://console.groq.com (no credit card) and set it as
GROQ_API_KEY in your environment.

Usage:
    from app.services.ollama_client import generate
    text = generate("Summarize this business: ...")
"""
import json

import httpx

from app.core.config import get_settings

settings = get_settings()

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class OllamaError(Exception):
    """Raised on any failure talking to the LLM backend (kept this name so
    existing callers/except blocks didn't need to change)."""
    pass


def generate(prompt: str, model: str | None = None, json_mode: bool = False, timeout: float = 60.0) -> str:
    """
    Sends a single-turn prompt to Groq and returns the generated text.
    Set json_mode=True when you expect the model to return JSON — Groq's
    JSON object mode constrains output accordingly, but the caller is still
    responsible for json.loads()-ing and validating the result.
    """
    if not settings.GROQ_API_KEY:
        raise OllamaError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
            "and set it as an environment variable on your backend host."
        )

    payload = {
        "model": model or settings.GROQ_DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(GROQ_CHAT_URL, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        raise OllamaError(f"Could not reach Groq's API ({exc})") from exc

    if resp.status_code == 429:
        raise OllamaError(
            "Groq rate limit hit (free tier). Wait a bit and retry, or "
            f"raw response: {resp.text[:300]}"
        )
    if resp.status_code != 200:
        raise OllamaError(f"Groq returned {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError) as exc:
        raise OllamaError(f"Unexpected Groq response shape: {data}") from exc


def generate_json(prompt: str, model: str | None = None, timeout: float = 60.0) -> dict:
    raw = generate(prompt, model=model, json_mode=True, timeout=timeout)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OllamaError(f"Groq did not return valid JSON: {raw[:500]}") from exc

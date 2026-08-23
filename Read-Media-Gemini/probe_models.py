import os

import requests
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PRIMARY_PROVIDER", "vectorengine").lower()

if PROVIDER == "vectorengine":
    API_KEY = os.getenv("VECTORENGINE_API_KEY", "")
    BASE_URL = os.getenv("VECTORENGINE_BASE_URL", "https://api.vectorengine.ai/v1/chat/completions")
else:
    API_KEY = os.getenv("KIE_API_KEY", "")
    BASE_URL = os.getenv("KIE_BASE_URL", "https://api.kie.ai/gemini-3-flash/v1/chat/completions")

MODELS_TO_TEST = [
    "gemini-3-flash",
    "gemini-3-flash-preview",
    "gemini-3-flash-preview-001",
    "gemini-3-flash-latest",
    "google/gemini-3-flash-preview",
]


def test_model(model_name):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
        "max_tokens": 10,
    }
    try:
        resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=10)
        preview = resp.text[:120].replace("\n", " ")
        print(f"Model: {model_name:<30} Status: {resp.status_code} Body: {preview}")
    except Exception as exc:
        print(f"Model: {model_name:<30} Error: {exc}")


if __name__ == "__main__":
    if not API_KEY:
        print(f"Error: API_KEY for {PROVIDER} not set. Add it to .env before probing models.")
        raise SystemExit(1)

    print(f"Probing {BASE_URL} for provider {PROVIDER}...")
    for model in MODELS_TO_TEST:
        test_model(model)

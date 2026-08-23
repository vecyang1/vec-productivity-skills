import os
import requests

api_key = os.getenv("VECTORENGINE_API_KEY")
base_url = "https://api.vectorengine.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "gemini-3-flash-preview",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 10
}

resp = requests.post(base_url, headers=headers, json=payload)
print(f"OpenAI Format Status: {resp.status_code}")
print(f"OpenAI Format Response: {resp.text[:200]}")

import os
import requests
import json

api_key = os.getenv("VECTORENGINE_API_KEY", "")
base_url = os.getenv("VECTORENGINE_BASE_URL", "https://api.vectorengine.ai")
model = "gemini-3-flash-preview"

url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{"text": "Hello, can you hear me? Answer in 1 short sentence."}]
    }]
}

headers = {"Content-Type": "application/json"}

try:
    if not api_key:
        print("No VECTORENGINE_API_KEY set, simulating request URL structure...")
        print(f"URL: {url}")
    else:
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")


import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import chat
import logging
logging.basicConfig(level=logging.INFO)

API_KEY = "sk-zIrs32KCaUo9ZsQLBmKnVkFJRqSbCzXFTUEWN3pIIvjE5W2E"
BASE_URL = "https://api.vectorengine.ai"
MODEL = "gemini-3-flash-preview"

print("\n>>> Testing Vector Engine (Google SDK path)...")
try:
    client = chat.create_client_vectorengine(API_KEY, BASE_URL)
    result = chat.generate_content_sdk(client, MODEL, "Say exactly: 'SDK works'", [], 0.0)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

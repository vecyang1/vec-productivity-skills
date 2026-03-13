import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import chat
import logging

logging.basicConfig(level=logging.INFO)

def test_vectorengine():
    print("\n>>> Testing Vector Engine (SDK)...")
    try:
        client = chat.create_client_vectorengine("test", "https://api.vectorengine.ai")
        # Since we use fake key, it will throw an auth logic but it tests structure
        result = chat.generate_content_sdk(client, "gemini-3-flash-preview", "Hello from VectorEngine test", [], 0.0)
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"Error: {e}")
    return False

def test_gemini():
    print("\n>>> Testing Antigravity Proxy (SDK)...")
    try:
        client = chat.create_client_proxy("fake_key", "http://localhost:8045")
        result = chat.generate_content_sdk(client, "gemini-3-flash-preview", "Hello from Proxy test", [], 0.0)
        print(f"Result: {result}")
        if result: return True
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    ve_ok = test_vectorengine()
    gemini_ok = test_gemini()
    
    print(f"\nSummary:\nVector Engine Structure: {'OK' if ve_ok else 'FAIL'}\nProxy Structure: {'OK' if gemini_ok else 'FAIL'}")

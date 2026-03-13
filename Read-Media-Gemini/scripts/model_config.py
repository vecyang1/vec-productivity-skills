import os
from dotenv import load_dotenv

def get_provider_config():
    """
    Source of truth for model and provider configuration for Read-Media-Gemini.
    Tracks and calls the latest provider/url/model name.
    """
    load_dotenv()
    
    ve_key = os.getenv("VECTORENGINE_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    # Read-Media-Gemini uses the full flash model, NOT the lite model
    target_model = os.getenv("READ_MEDIA_MODEL", "gemini-3-flash-preview")
    
    # Priority 1: Vector Engine (cheaper, official proxy)
    if ve_key:
        return {
            "provider": "vectorengine",
            "api_key": ve_key,
            "base_url": "https://api.vectorengine.ai", # SDK handles /v1beta/models/...
            "model": target_model
        }
    # Priority 2: Google Direct
    elif google_key:
        return {
            "provider": "google",
            "api_key": google_key,
            "base_url": None, # SDK defaults to Google's URL
            "model": target_model
        }
    else:
        return None

if __name__ == "__main__":
    config = get_provider_config()
    if config:
        print(f"Provider: {config['provider']}")
        print(f"Base URL: {config['base_url']}")
        print(f"Model: {config['model']}")
    else:
        print("No provider configured. Please set VECTORENGINE_API_KEY or GOOGLE_API_KEY in .env")
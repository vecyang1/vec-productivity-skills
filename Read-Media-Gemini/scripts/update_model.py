import os
import requests
import re
from dotenv import load_dotenv

# Load env to get key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not set.")
    exit(1)

def get_latest_flash_model():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching models: {e}")
        return None

    # Filter for 'flash' models
    flash_models = []
    for m in data.get('models', []):
        name = m['name'].replace('models/', '')
        if 'flash' in name.lower():
            flash_models.append(name)

    if not flash_models:
        print("No 'flash' models found.")
        return None

    print(f"Found Flash models: {flash_models}")

    # Sort logic: find the highest version number
    # Simple heuristic: extract the first float/version number
    def parse_version(name):
        # Look for patterns like gemini-1.5, gemini-2.0
        match = re.search(r'gemini-(\d+\.?\d*)', name)
        if match:
            return float(match.group(1))
        return 0.0

    # Sort by version descending, then by length (prefer longer names often imply subtypes, or actually shorter is usually better generic? 
    # Actually user wants "latest". 
    # If we have gemini-1.5-flash and gemini-1.5-flash-latest, usually 'latest' points to specific alias.
    # But usually version comes first.
    
    # Let's clean sort:
    # 1. Version (3.0 > 2.5 > 1.5)
    # 2. 'preview' vs 'latest' vs stable. 
    # Usually we want the highest version number.
    
    flash_models.sort(key=lambda x: parse_version(x), reverse=True)
    
    # Pick the top one
    best_model = flash_models[0]
    
    # Refinement: If multiple share the highest version (e.g. 1.5-flash, 1.5-flash-001)
    # Prefer non-001/002 unless only those exist? 
    # Actually user mentioned "gemini-3-flash-preview".
    # If 3.0 exists, it will be top.
    
    return best_model

def update_env(model_name):
    env_path = ".env"
    
    # Read existing
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    # Update or Append
    found = False
    new_lines = []
    for line in lines:
        if line.startswith("GOOGLE_MODEL="):
            new_lines.append(f"GOOGLE_MODEL={model_name}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        new_lines.append(f"GOOGLE_MODEL={model_name}\n")
        
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print(f"Updated .env with GOOGLE_MODEL={model_name}")

if __name__ == "__main__":
    latest = get_latest_flash_model()
    if latest:
        print(f"Selected Latest Flash Model: {latest}")
        update_env(latest)
    else:
        print("Could not determine latest flash model.")

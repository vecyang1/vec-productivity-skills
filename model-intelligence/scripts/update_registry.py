import json
import sys
import os
from datetime import datetime

def update_registry(provider, model_data):
    registry_path = os.path.join(os.path.dirname(__file__), '../references/model_registry.json')
    
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    except FileNotFoundError:
        registry = {"openai": [], "gemini": [], "last_updated": ""}

    if provider not in registry:
        registry[provider] = []

    # Check if model already exists and update, or add new
    existing_model = next((m for m in registry[provider] if m['name'] == model_data['name']), None)
    if existing_model:
        existing_model.update(model_data)
    else:
        registry[provider].append(model_data)

    registry['last_updated'] = datetime.now().strftime("%Y-%m-%d")

    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Successfully updated {provider} model: {model_data['name']}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_registry.py <provider> '<json_model_data>'")
        sys.exit(1)
    
    provider = sys.argv[1]
    try:
        model_data = json.loads(sys.argv[2])
        update_registry(provider, model_data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON data provided.")
        sys.exit(1)

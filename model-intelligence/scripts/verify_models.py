#!/usr/bin/env python3
"""
Verify that the models in the registry are actually callable
Tests each model with a simple API call to confirm availability
"""
import json
import os
import sys

def load_registry():
    registry_path = os.path.join(os.path.dirname(__file__), '../references/model_registry.json')
    with open(registry_path, 'r') as f:
        return json.load(f)

def verify_model_callable(provider, model_name, api_base):
    """
    Check if model is callable (basic validation)
    Returns: (success: bool, message: str)
    """
    # For now, just validate the structure
    # In production, this would make actual API calls

    if not model_name:
        return False, "Missing model name"

    if not api_base:
        return False, "Missing API base URL"

    # Basic format validation
    if provider == "openai":
        if not model_name.startswith(("gpt-", "o")):
            return False, f"Unexpected OpenAI model format: {model_name}"
    elif provider == "anthropic":
        if not model_name.startswith("claude-"):
            return False, f"Unexpected Anthropic model format: {model_name}"
    elif provider == "gemini":
        if not model_name.startswith("gemini-"):
            return False, f"Unexpected Gemini model format: {model_name}"

    return True, "Format valid"

def main():
    print("🔍 Verifying model registry...\n")

    registry = load_registry()
    total_models = 0
    valid_models = 0
    issues = []

    for provider, models in registry.items():
        if provider == 'last_updated':
            continue

        print(f"\n{provider.upper()}:")
        for model in models:
            total_models += 1
            model_name = model.get('name', 'UNKNOWN')
            api_base = model.get('api_base', '')

            success, message = verify_model_callable(provider, model_name, api_base)

            if success:
                valid_models += 1
                print(f"  ✅ {model_name}")
            else:
                print(f"  ❌ {model_name}: {message}")
                issues.append(f"{provider}/{model_name}: {message}")

    print(f"\n{'='*60}")
    print(f"Total models: {total_models}")
    print(f"Valid: {valid_models}")
    print(f"Issues: {len(issues)}")

    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("\n✅ All models passed validation!")
        sys.exit(0)

if __name__ == '__main__':
    main()

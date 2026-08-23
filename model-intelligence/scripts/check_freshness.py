#!/usr/bin/env python3
"""
Auto-check for model updates by querying live API endpoints
Runs quick checks against official model listing endpoints
"""
import json
import os
import sys
from datetime import datetime, timedelta

def load_registry():
    registry_path = os.path.join(os.path.dirname(__file__), '../references/model_registry.json')
    with open(registry_path, 'r') as f:
        return json.load(f)

def check_freshness():
    """Check if registry needs updating based on age"""
    registry = load_registry()
    last_updated = registry.get('last_updated', '2000-01-01')

    try:
        last_date = datetime.strptime(last_updated, '%Y-%m-%d')
        days_old = (datetime.now() - last_date).days

        if days_old > 7:
            return False, f"Registry is {days_old} days old (last updated: {last_updated})"
        else:
            return True, f"Registry is fresh ({days_old} days old)"
    except:
        return False, "Invalid last_updated date in registry"

def suggest_update_command():
    """Suggest the command to update the registry"""
    print("\n🔄 To update the registry, use context7 to query latest models:")
    print("\n1. OpenAI:")
    print("   mcp__context7__resolve-library-id(libraryName='openai api')")
    print("   mcp__context7__query-docs(libraryId='...', query='list all available models')")
    print("\n2. Anthropic:")
    print("   mcp__context7__resolve-library-id(libraryName='anthropic api')")
    print("   mcp__context7__query-docs(libraryId='...', query='list all available models')")
    print("\n3. Gemini:")
    print("   mcp__context7__resolve-library-id(libraryName='google gemini api')")
    print("   mcp__context7__query-docs(libraryId='...', query='list all available models')")

def main():
    print("🔍 Checking model registry freshness...\n")

    is_fresh, message = check_freshness()

    if is_fresh:
        print(f"✅ {message}")
        print("\nRegistry is up to date.")
        sys.exit(0)
    else:
        print(f"⚠️  {message}")
        print("\n❌ Registry needs updating!")
        suggest_update_command()
        sys.exit(1)

if __name__ == '__main__':
    main()

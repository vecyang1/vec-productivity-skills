#!/usr/bin/env python3
"""Smart model reference scanner with update capability."""

import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
MODEL_REGISTRY = Path.home() / ".gemini/antigravity/skills/model-intelligence/references/model_registry.json"

MODEL_PATTERNS = [
    r'\bgpt-[0-9](?:\.[0-9])?(?:-[a-z]+)*\b',
    r'\bclaude-(?:opus|sonnet|haiku)-[0-9](?:-[0-9]+)*\b',
    r'\bgemini-[0-9](?:\.[0-9])?-[a-z]+(?:-[a-z]+)*\b',
    r'\bo[0-9](?:-[a-z]+)?\b',
]

EXCLUDE_PATTERNS = [
    r'text-[a-z-]+', r'Text-to-[A-Z]', r'[A-Z][a-z]+-native',
    r'[A-Z][a-z]+-specific', r'-sdk\b', r'-cli\b', r'-code\b',
    r'-guide\b', r'-auth\b',
]

def load_registry():
    if not MODEL_REGISTRY.exists():
        print(f"Error: Model registry not found")
        sys.exit(1)

    with open(MODEL_REGISTRY) as f:
        data = json.load(f)

    current_models = set()
    model_families = {}

    for provider_key, models in data.items():
        if isinstance(models, list):
            for model in models:
                name = model['name']
                current_models.add(name)
                family_match = re.match(r'([a-z]+-[a-z]+)-', name)
                if family_match:
                    family = family_match.group(1)
                    if family not in model_families:
                        model_families[family] = []
                    model_families[family].append(name)

    return current_models, model_families, data

def is_false_positive(model_ref):
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, model_ref, re.IGNORECASE):
            return True
    return False

def find_upgrade_suggestion(model_ref, current_models, model_families):
    family_match = re.match(r'([a-z]+-[a-z]+)-', model_ref)
    if not family_match:
        return None
    family = family_match.group(1)
    if family not in model_families:
        return None
    if model_ref in current_models:
        return None
    if model_families[family]:
        return model_families[family][0]
    return None

def scan_skill(skill_path, current_models, model_families):
    findings = []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return findings

    content = skill_md.read_text()
    found_models = set()

    for pattern in MODEL_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        found_models.update(matches)

    for model in found_models:
        if is_false_positive(model):
            continue
        if model not in current_models:
            suggestion = find_upgrade_suggestion(model, current_models, model_families)
            findings.append({
                'skill': skill_path.name,
                'model': model,
                'suggestion': suggestion,
                'status': 'outdated' if suggestion else 'unknown'
            })

    return findings

def update_skill_models(findings, auto_yes=False):
    """Update outdated models after permission."""
    print("\n🔄 Ready to update:\n")
    for f in findings:
        print(f"  {f['skill']}: {f['model']} → {f['suggestion']}")
    
    if not auto_yes:
        try:
            response = input("\nProceed? (yes/no): ").strip().lower()
            if response != 'yes':
                print("Cancelled.")
                return
        except EOFError:
            print("\nNon-interactive mode. Use --yes to auto-approve.")
            return
    
    updated = 0
    for f in findings:
        skill_md = SKILLS_DIR / f['skill'] / "skill.md"
        if not skill_md.exists():
            continue
        
        content = skill_md.read_text()
        new_content = content.replace(f['model'], f['suggestion'])
        
        if new_content != content:
            skill_md.write_text(new_content)
            print(f"✓ {f['skill']}")
            updated += 1
    
    print(f"\n✅ Updated {updated} skills")

def main():
    update_mode = '--update' in sys.argv
    auto_yes = '--yes' in sys.argv
    
    print("Loading model registry...")
    current_models, model_families, _ = load_registry()
    print(f"Found {len(current_models)} current models\n")

    all_findings = []
    for skill_path in SKILLS_DIR.iterdir():
        if skill_path.is_dir() and not skill_path.name.startswith('.'):
            all_findings.extend(scan_skill(skill_path, current_models, model_families))

    if not all_findings:
        print("✓ All model references are current")
        return

    outdated = [f for f in all_findings if f['status'] == 'outdated']
    unknown = [f for f in all_findings if f['status'] == 'unknown']

    print(f"📊 Found {len(all_findings)} references needing attention:\n")

    if outdated:
        print(f"⚠️  {len(outdated)} OUTDATED:\n")
        for f in outdated:
            print(f"  {f['skill']}: {f['model']} → {f['suggestion']}")

    if unknown:
        print(f"\n❓ {len(unknown)} UNKNOWN:\n")
        for f in unknown:
            print(f"  {f['skill']}: {f['model']}")

    if update_mode and outdated:
        update_skill_models(outdated, auto_yes)
    elif not update_mode:
        print("\nRun with --update to update (requires permission)")

if __name__ == "__main__":
    main()

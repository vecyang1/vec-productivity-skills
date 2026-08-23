#!/usr/bin/env python3
"""
Interactive domain browser for skills.

Usage:
    python3 browse_domains.py
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DOMAIN_MAP = SCRIPT_DIR.parent / "references" / "skill_domain_map.json"

def load_domain_map():
    with open(DOMAIN_MAP, 'r') as f:
        return json.load(f)

def show_skill_details(data, skill_name):
    if skill_name not in data['skills']:
        print(f"❌ Skill '{skill_name}' not found")
        return

    skill = data['skills'][skill_name]
    print(f"\n{'='*70}")
    print(f"📦 {skill_name}")
    print(f"{'='*70}")
    print(f"\n📁 Domain: {skill.get('primary_domain', 'Unknown')}")
    print(f"\n📝 Description:")
    print(f"   {skill.get('description', 'No description')}")

    if skill.get('tags'):
        print(f"\n🏷️  Tags: {', '.join(skill['tags'])}")

    if skill.get('dependencies'):
        print(f"\n🔗 Dependencies: {', '.join(skill['dependencies'][:5])}")
        if len(skill['dependencies']) > 5:
            print(f"   ... and {len(skill['dependencies']) - 5} more")

    if skill.get('output_formats'):
        print(f"\n📤 Output Formats: {', '.join(skill['output_formats'])}")

    print(f"\n{'='*70}\n")

def browse_domain(data, domain):
    if domain not in data['domains']:
        print(f"❌ Domain '{domain}' not found")
        return

    skills = data['domains'][domain]
    print(f"\n📁 {domain} ({len(skills)} skills)")
    print("="*70)

    for i, skill in enumerate(skills, 1):
        desc = data['skills'][skill].get('description', '')[:60]
        print(f"{i:3}. {skill:30} {desc}...")

    print("\nEnter skill number for details, 'b' to go back, or 'q' to quit: ", end='')
    choice = input().strip()

    if choice.lower() == 'q':
        return 'quit'
    elif choice.lower() == 'b':
        return 'back'
    elif choice.isdigit() and 1 <= int(choice) <= len(skills):
        show_skill_details(data, skills[int(choice) - 1])
        input("\nPress Enter to continue...")
        return browse_domain(data, domain)
    else:
        print("Invalid choice")
        return browse_domain(data, domain)

def main():
    data = load_domain_map()

    print("\n" + "="*70)
    print("🗂️  SKILL DOMAIN BROWSER")
    print("="*70)
    print(f"\nTotal Skills: {data['total_skills']}")
    print(f"Domains: {len(data['domains'])}")
    print(f"Tags: {len(data['tags'])}")

    while True:
        print("\n📁 Available Domains:\n")
        domains = sorted(data['domain_counts'].items(), key=lambda x: -x[1])
        for i, (domain, count) in enumerate(domains, 1):
            print(f"{i:2}. {domain:30} ({count} skills)")

        print("\nEnter domain number to browse, or 'q' to quit: ", end='')
        choice = input().strip()

        if choice.lower() == 'q':
            print("\n👋 Goodbye!\n")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(domains):
            domain = domains[int(choice) - 1][0]
            result = browse_domain(data, domain)
            if result == 'quit':
                print("\n👋 Goodbye!\n")
                break
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    main()

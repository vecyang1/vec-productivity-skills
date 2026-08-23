#!/usr/bin/env python3
"""Unified skill query tool - replaces query_by_domain.py and query_relationships.py"""

import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DOMAIN_MAP = SCRIPT_DIR.parent / "references/skill_domain_map.json"
RELATIONSHIPS = SCRIPT_DIR.parent / "references/skill_relationships.json"

def load_data():
    with open(DOMAIN_MAP) as f:
        domain_data = json.load(f)
    with open(RELATIONSHIPS) as f:
        rel_data = json.load(f)

    # Convert skills dict to list
    all_skills = list(domain_data["skills"].values())

    return all_skills, rel_data

def query_by_domain(skills, domain=None, tags=None, all_tags=False):
    """Query skills by domain or tags."""
    if domain:
        skills = [s for s in skills if s["primary_domain"] == domain]

    if tags:
        if all_tags:
            skills = [s for s in skills if all(t in s["tags"] for t in tags)]
        else:
            skills = [s for s in skills if any(t in s["tags"] for t in tags)]

    return skills

def query_by_skill(rel_data, skill_name):
    """Query relationships for a specific skill."""
    if skill_name not in rel_data["skills"]:
        return None

    skill = rel_data["skills"][skill_name]
    return {
        "name": skill_name,
        "description": skill.get("description", ""),
        "direct_dependencies": skill.get("direct_dependencies", []),
        "referenced_by": skill.get("referenced_by", []),
        "domain_cluster": skill.get("domain_cluster", ""),
        "tool_ecosystem": skill.get("tool_ecosystem", "")
    }

def list_domains(skills):
    """List all available domains."""
    return sorted(set(s["primary_domain"] for s in skills))

def list_tags(skills):
    """List all available tags."""
    all_tags = set()
    for skill in skills:
        all_tags.update(skill["tags"])
    return sorted(all_tags)

def main():
    parser = argparse.ArgumentParser(description="Query skills by domain, tags, or name")
    parser.add_argument("--domain", help="Filter by domain")
    parser.add_argument("--tag", action="append", help="Filter by tag (can specify multiple)")
    parser.add_argument("--all", action="store_true", help="Require all tags (AND logic)")
    parser.add_argument("--skill", help="Query specific skill relationships")
    parser.add_argument("--list-domains", action="store_true", help="List all domains")
    parser.add_argument("--list-tags", action="store_true", help="List all tags")

    args = parser.parse_args()
    skills, rel_data = load_data()

    if args.list_domains:
        print("\n".join(list_domains(skills)))
        return

    if args.list_tags:
        print("\n".join(list_tags(skills)))
        return

    if args.skill:
        result = query_by_skill(rel_data, args.skill)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"Skill '{args.skill}' not found")
        return

    results = query_by_domain(skills, args.domain, args.tag, args.all)
    print(f"Found {len(results)} skills")
    for skill in results:
        print(f"  {skill['name']}: {skill['description'][:80]}")

if __name__ == "__main__":
    main()

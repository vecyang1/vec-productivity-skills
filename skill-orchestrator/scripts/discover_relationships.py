#!/usr/bin/env python3
"""
Discover relationships between skills by analyzing SKILL.md files.
Identifies direct references, workflow chains, shared domains, and tool dependencies.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
from _metadata_extractor import extract_skill_metadata

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
OUTPUT_FILE = Path(__file__).parent.parent / "references/skill_relationships.json"


def find_skill_references(skill_data: Dict, all_skills: Dict) -> List[str]:
    """Find direct references to other skills in SKILL.md content."""
    references = []
    body = skill_data["body"].lower()

    for other_skill in all_skills.values():
        if other_skill["folder"] == skill_data["folder"]:
            continue

        # Check for skill name mentions
        skill_name = other_skill["name"].lower()
        skill_folder = other_skill["folder"].lower()

        # Look for explicit mentions
        if skill_name in body or skill_folder in body or f"`{skill_folder}`" in skill_data["body"]:
            references.append(other_skill["folder"])

    return references

def extract_domains(skill_data: Dict) -> Set[str]:
    """Extract domain keywords from skill description and content."""
    text = (skill_data["description"] + " " + skill_data["body"]).lower()

    # Domain keywords
    domains = set()
    domain_patterns = {
        "wordpress": ["wordpress", "wp-", "gutenberg"],
        "ecommerce": ["ecommerce", "e-commerce", "shopify", "product", "store"],
        "content": ["content", "writing", "article", "blog"],
        "video": ["video", "youtube", "thumbnail", "editing"],
        "research": ["research", "analysis", "data"],
        "social": ["social", "twitter", "instagram", "facebook"],
        "design": ["design", "ui", "ux", "visual"],
        "marketing": ["marketing", "ads", "campaign", "seo"],
        "development": ["development", "coding", "programming", "api"],
        "notion": ["notion", "database", "workspace"],
        "pdf": ["pdf", "document"],
        "image": ["image", "photo", "picture", "visual"],
        "ai": ["ai", "gemini", "gpt", "claude", "model"],
        "business": ["business", "strategy", "planning"],
    }

    for domain, keywords in domain_patterns.items():
        if any(keyword in text for keyword in keywords):
            domains.add(domain)

    return domains

def extract_tools(skill_data: Dict) -> Set[str]:
    """Extract external tool dependencies from skill content."""
    body = skill_data["body"]
    tools = set()

    # Common tool patterns
    tool_patterns = {
        "notion": r"notion[- ]mcp|notion api",
        "chrome": r"chrome[- ]devtools|puppeteer",
        "gemini": r"gemini[- ]api|google\.generativeai",
        "openai": r"openai|gpt-",
        "ffmpeg": r"ffmpeg",
        "imagemagick": r"imagemagick|convert",
        "git": r"\bgit\b",
        "docker": r"docker",
        "npm": r"\bnpm\b|\byarn\b",
        "python": r"python3|pip",
    }

    for tool, pattern in tool_patterns.items():
        if re.search(pattern, body, re.IGNORECASE):
            tools.add(tool)

    return tools

def discover_relationships():
    """Main function to discover all skill relationships."""
    print("🔍 Discovering skill relationships...")

    # Load all skills
    all_skills = {}
    for skill_path in SKILLS_DIR.iterdir():
        if not skill_path.is_dir() or skill_path.name.startswith((".", "_")):
            continue

        metadata = extract_skill_metadata(skill_path)
        if metadata:
            all_skills[skill_path.name] = metadata

    print(f"   Found {len(all_skills)} skills")

    # Build relationship graph
    relationships = {}

    for folder, skill_data in all_skills.items():
        print(f"   Analyzing {folder}...")

        relationships[folder] = {
            "name": skill_data["name"],
            "description": skill_data["description"],
            "direct_references": find_skill_references(skill_data, all_skills),
            "domains": list(extract_domains(skill_data)),
            "tools": list(extract_tools(skill_data)),
        }

    # Find domain clusters
    domain_clusters = defaultdict(list)
    for folder, data in relationships.items():
        for domain in data["domains"]:
            domain_clusters[domain].append(folder)

    # Find tool ecosystems
    tool_ecosystems = defaultdict(list)
    for folder, data in relationships.items():
        for tool in data["tools"]:
            tool_ecosystems[tool].append(folder)

    # Build output
    output = {
        "skills": relationships,
        "domain_clusters": dict(domain_clusters),
        "tool_ecosystems": dict(tool_ecosystems),
        "metadata": {
            "total_skills": len(all_skills),
            "total_domains": len(domain_clusters),
            "total_tools": len(tool_ecosystems),
        }
    }

    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))

    print(f"\n✅ Relationships saved to {OUTPUT_FILE}")
    print(f"   {len(all_skills)} skills analyzed")
    print(f"   {len(domain_clusters)} domain clusters found")
    print(f"   {len(tool_ecosystems)} tool ecosystems found")

if __name__ == "__main__":
    discover_relationships()

#!/usr/bin/env python3
"""
Regenerate skill domain mapping database.

This script scans all skills in both Gemini and Claude directories,
extracts metadata, and regenerates the domain mapping database.

Usage:
    python3 regenerate_domain_map.py [--verbose]
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
import argparse
from _metadata_extractor import extract_skill_metadata

SCRIPT_DIR = Path(__file__).parent
SKILL_ORCHESTRATOR = SCRIPT_DIR.parent
GEMINI_SKILLS = Path.home() / ".gemini" / "antigravity" / "skills"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
OUTPUT_FILE = SKILL_ORCHESTRATOR / "references" / "skill_domain_map.json"

# Domain classification patterns
DOMAIN_PATTERNS = {
    "AI & ML": [
        r"\bai\b", r"\bml\b", r"machine learning", r"model", r"training",
        r"gemini", r"claude", r"gpt", r"llm", r"neural", r"deep learning"
    ],
    "Content Creation": [
        r"content", r"writing", r"copywriting", r"article", r"blog",
        r"research", r"seo", r"marketing copy"
    ],
    "Image & Design": [
        r"image", r"photo", r"design", r"visual", r"graphic",
        r"banner", r"logo", r"illustration", r"upscale"
    ],
    "Video & Media": [
        r"video", r"audio", r"media", r"transcribe", r"subtitle",
        r"youtube", r"tiktok", r"editing"
    ],
    "Web Development": [
        r"wordpress", r"wp-", r"web", r"frontend", r"backend",
        r"react", r"nextjs", r"stitch", r"html", r"css"
    ],
    "Development & Code": [
        r"development", r"coding", r"programming", r"git", r"github",
        r"cli", r"api", r"sdk", r"framework"
    ],
    "E-commerce": [
        r"ecommerce", r"e-commerce", r"product", r"shopify",
        r"landing page", r"conversion", r"sales"
    ],
    "Automation & Integration": [
        r"automation", r"integration", r"workflow", r"sync",
        r"mcp", r"connect", r"api integration"
    ],
    "Data & Analytics": [
        r"data", r"analytics", r"analysis", r"metrics",
        r"tracking", r"statistics", r"database"
    ],
    "Business & Productivity": [
        r"business", r"productivity", r"planning", r"strategy",
        r"operations", r"management", r"consulting"
    ],
    "Research & Knowledge": [
        r"research", r"knowledge", r"learning", r"study",
        r"academic", r"education", r"notebooklm"
    ],
    "Infrastructure & DevOps": [
        r"infrastructure", r"devops", r"dns", r"hosting",
        r"cloud", r"deployment", r"server", r"vps"
    ],
    "Social Media": [
        r"social media", r"twitter", r"reddit", r"instagram",
        r"facebook", r"tiktok", r"小红书"
    ]
}

# Tag extraction patterns
TAG_PATTERNS = {
    "python": r"\bpython\b",
    "nodejs": r"\bnode\.?js\b|\bnode\b",
    "go": r"\bgolang\b|\bgo\b",
    "bash": r"\bbash\b|\bshell\b",
    "javascript": r"\bjavascript\b|\bjs\b",
    "typescript": r"\btypescript\b|\bts\b",
    "react": r"\breact\b",
    "nextjs": r"\bnext\.?js\b",
    "wordpress": r"\bwordpress\b|\bwp-",
    "notion": r"\bnotion\b",
    "youtube": r"\byoutube\b",
    "google": r"\bgoogle\b",
    "github": r"\bgithub\b",
    "twitter": r"\btwitter\b|\bx\.com\b",
    "reddit": r"\breddit\b",
    "research": r"\bresearch\b",
    "generation": r"\bgenerat(e|ion|ing)\b",
    "optimization": r"\boptimiz(e|ation|ing)\b",
    "automation": r"\bautomat(e|ion|ing)\b",
    "analysis": r"\banalys(is|e|ing)\b",
    "text": r"\btext\b",
    "image": r"\bimage\b|\bphoto\b",
    "video": r"\bvideo\b",
    "audio": r"\baudio\b",
    "data": r"\bdata\b"
}

def classify_domain_and_tags(metadata):
    """Classify domain and extract tags using shared metadata."""
    content_lower = metadata["content"].lower()

    # Classify domain
    primary_domain = ""
    max_matches = 0
    for domain, patterns in DOMAIN_PATTERNS.items():
        matches = sum(1 for pattern in patterns if re.search(pattern, content_lower))
        if matches > max_matches:
            max_matches = matches
            primary_domain = domain

    # Extract tags
    tags = [tag for tag, pattern in TAG_PATTERNS.items() if re.search(pattern, content_lower)]

    return primary_domain, tags

    # Extract dependencies (other skills mentioned)
    # Extract dependencies and output formats
    content_lower = metadata["content"].lower()

    dependencies = []
    skill_mentions = re.findall(r'`([a-z0-9-]+)`', metadata["content"])
    for mention in skill_mentions:
        if mention != metadata["folder"] and '-' in mention:
            dependencies.append(mention)

    # Determine output formats
    output_formats = []
    if re.search(r'\bjson\b', content_lower):
        output_formats.append('json')
    if re.search(r'\bmarkdown\b|\b\.md\b', content_lower):
        output_formats.append('markdown')
    if re.search(r'\bimage\b|\bpng\b|\bjpg\b', content_lower):
        output_formats.append('image')
    if re.search(r'\bvideo\b|\bmp4\b', content_lower):
        output_formats.append('video')
    if re.search(r'\baudio\b|\bmp3\b', content_lower):
        output_formats.append('audio')

    return {
        "name": metadata["name"],
        "description": metadata["description"],
        "primary_domain": primary_domain,
        "tags": sorted(list(set(tags))),
        "dependencies": sorted(list(set(dependencies)))[:10],
        "output_formats": sorted(list(set(output_formats)))
    }

def scan_skills_directory(directory):
    """Scan a skills directory and extract metadata."""
    skills = []

    if not directory.exists():
        print(f"⚠️  Directory not found: {directory}")
        return skills

    for item in directory.iterdir():
        # Skip files, only process directories
        if not item.is_dir():
            continue

        # Skip hidden directories and special files
        if item.name.startswith('.') or item.name in ['node_modules', '__pycache__']:
            continue

        metadata = extract_skill_metadata(item)
        if metadata:
            domain, tags = classify_domain_and_tags(metadata)
            skill_data = {
                "name": metadata["name"],
                "description": metadata["description"],
                "primary_domain": domain,
                "tags": tags,
                "dependencies": [],
                "output_formats": []
            }

            # Extract dependencies
            skill_mentions = re.findall(r'`([a-z0-9-]+)`', metadata["content"])
            for mention in skill_mentions:
                if mention != item.name and '-' in mention:
                    skill_data["dependencies"].append(mention)

            # Extract output formats
            content_lower = metadata["content"].lower()
            if re.search(r'\bjson\b', content_lower):
                skill_data["output_formats"].append('json')
            if re.search(r'\bmarkdown\b|\b\.md\b', content_lower):
                skill_data["output_formats"].append('markdown')
            if re.search(r'\bimage\b|\bpng\b|\bjpg\b', content_lower):
                skill_data["output_formats"].append('image')
            if re.search(r'\bvideo\b|\bmp4\b', content_lower):
                skill_data["output_formats"].append('video')
            if re.search(r'\baudio\b|\bmp3\b', content_lower):
                skill_data["output_formats"].append('audio')

            skill_data["dependencies"] = sorted(list(set(skill_data["dependencies"])))[:10]
            skill_data["output_formats"] = sorted(list(set(skill_data["output_formats"])))

            skills.append(skill_data)

    return skills

def merge_skills(gemini_skills, claude_skills):
    """Merge skills from both directories, preferring Gemini."""
    skills_map = {}

    # Add Gemini skills first (source of truth)
    for skill in gemini_skills:
        skills_map[skill['name']] = skill

    # Add Claude skills that don't exist in Gemini
    for skill in claude_skills:
        if skill['name'] not in skills_map:
            skills_map[skill['name']] = skill

    return skills_map

def create_domain_map(skills_map):
    """Create domain mapping structure."""
    domain_map = defaultdict(list)
    tag_index = defaultdict(list)

    for name, skill in sorted(skills_map.items()):
        domain = skill.get('primary_domain', 'Uncategorized')
        domain_map[domain].append(name)

        for tag in skill.get('tags', []):
            tag_index[tag].append(name)

    return {
        'total_skills': len(skills_map),
        'domains': {domain: sorted(skills) for domain, skills in domain_map.items()},
        'domain_counts': {domain: len(skills) for domain, skills in domain_map.items()},
        'tags': {tag: sorted(skills) for tag, skills in tag_index.items()},
        'tag_counts': {tag: len(skills) for tag, skills in tag_index.items()},
        'skills': {name: skill for name, skill in sorted(skills_map.items())}
    }

def main():
    parser = argparse.ArgumentParser(description='Regenerate skill domain mapping')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    print("🔄 Regenerating skill domain mapping...")
    print()

    # Scan both directories
    print(f"📁 Scanning Gemini skills: {GEMINI_SKILLS}")
    gemini_skills = scan_skills_directory(GEMINI_SKILLS)
    print(f"   Found: {len(gemini_skills)} skills")

    print(f"📁 Scanning Claude skills: {CLAUDE_SKILLS}")
    claude_skills = scan_skills_directory(CLAUDE_SKILLS)
    print(f"   Found: {len(claude_skills)} skills")
    print()

    # Merge skills
    print("🔀 Merging skills (Gemini as source of truth)...")
    skills_map = merge_skills(gemini_skills, claude_skills)
    print(f"   Total unique skills: {len(skills_map)}")
    print()

    # Create domain map
    print("🗂️  Creating domain mapping...")
    domain_map = create_domain_map(skills_map)
    print(f"   Domains: {len(domain_map['domains'])}")
    print(f"   Tags: {len(domain_map['tags'])}")
    print()

    # Save to file
    print(f"💾 Saving to: {OUTPUT_FILE}")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(domain_map, f, indent=2, ensure_ascii=False)

    file_size = OUTPUT_FILE.stat().st_size / 1024
    print(f"   File size: {file_size:.1f} KB")
    print()

    # Summary
    print("✅ Domain mapping regenerated successfully!")
    print()
    print("📊 Summary:")
    print(f"   Total skills: {domain_map['total_skills']}")
    print(f"   Domains: {len(domain_map['domains'])}")
    print(f"   Tags: {len(domain_map['tags'])}")
    print()

    if args.verbose:
        print("📁 Top 5 Domains:")
        for domain, count in sorted(domain_map['domain_counts'].items(), key=lambda x: -x[1])[:5]:
            print(f"   {domain:30} {count:3} skills")
        print()

        print("🏷️  Top 10 Tags:")
        for tag, count in sorted(domain_map['tag_counts'].items(), key=lambda x: -x[1])[:10]:
            print(f"   {tag:20} {count:3} skills")
        print()

    print("🚀 Query tools:")
    print(f"   python3 {SCRIPT_DIR}/query_by_domain.py --list-domains")
    print(f"   python3 {SCRIPT_DIR}/browse_domains.py")

if __name__ == '__main__':
    main()

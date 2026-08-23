#!/usr/bin/env python3
"""Shared metadata extraction for skill-orchestrator."""

import re
from pathlib import Path
from typing import Dict, Optional

def extract_skill_metadata(skill_path: Path) -> Optional[Dict]:
    """Extract metadata from SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None

    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception:
        return None

    # Extract frontmatter
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)

    name = skill_path.name
    description = ""

    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        desc_match = re.search(r'description:\s*(.+?)(?:\n[a-z]+:|$)', frontmatter, re.DOTALL)

        if name_match:
            name = name_match.group(1).strip()
        if desc_match:
            description = desc_match.group(1).strip().replace('\n', ' ')

    # Fallback: first non-header line
    if not description:
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                description = line[:200]
                break

    # Extract body (after frontmatter)
    body = content[frontmatter_match.end():].strip() if frontmatter_match else content

    return {
        "name": name,
        "folder": skill_path.name,
        "description": description,
        "body": body,
        "content": content
    }

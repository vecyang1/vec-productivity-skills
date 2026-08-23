#!/usr/bin/env python3
"""
Audit design language consistency across related skills.
Checks terminology, tone, structure, and output formats.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

RELATIONSHIPS_FILE = Path(__file__).parent.parent / "references/skill_relationships.json"
OUTPUT_FILE = Path(__file__).parent.parent / "references/design_audit_report.md"
SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"

def load_skill_content(skill_folder: str) -> str:
    """Load SKILL.md content for a skill."""
    skill_md = SKILLS_DIR / skill_folder / "SKILL.md"
    if skill_md.exists():
        return skill_md.read_text()
    return ""

def analyze_tone(content: str) -> Dict:
    """Analyze tone characteristics of skill content."""
    # Formal indicators
    formal_words = ["utilize", "implement", "execute", "configure", "validate"]
    formal_count = sum(content.lower().count(word) for word in formal_words)

    # Casual indicators
    casual_words = ["let's", "you'll", "we'll", "just", "simply"]
    casual_count = sum(content.lower().count(word) for word in casual_words)

    # Technical indicators
    technical_patterns = [r'\b[A-Z]{2,}\b', r'`[^`]+`', r'```']
    technical_count = sum(len(re.findall(pattern, content)) for pattern in technical_patterns)

    return {
        "formal_score": formal_count,
        "casual_score": casual_count,
        "technical_score": technical_count,
        "tone": "formal" if formal_count > casual_count else "casual",
    }

def extract_terminology(content: str) -> Dict[str, int]:
    """Extract key terminology and frequency."""
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

    # Extract words (3+ chars, alphanumeric)
    words = re.findall(r'\b[a-z]{3,}\b', content.lower())

    # Count frequency
    freq = defaultdict(int)
    for word in words:
        freq[word] += 1

    # Return top terms
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20])

def analyze_structure(content: str) -> Dict:
    """Analyze structural patterns."""
    # Count headers
    headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

    # Count code blocks
    code_blocks = len(re.findall(r'```', content)) // 2

    # Count lists
    lists = len(re.findall(r'^\s*[-*]\s+', content, re.MULTILINE))

    return {
        "header_count": len(headers),
        "code_block_count": code_blocks,
        "list_count": lists,
        "headers": headers[:10],
    }

def audit_workflow(workflow_skills: List[str]) -> Dict:
    """Audit design language consistency for a workflow."""
    print(f"   Auditing {len(workflow_skills)} skills...")

    results = {}
    for skill in workflow_skills:
        content = load_skill_content(skill)
        if not content:
            continue

        results[skill] = {
            "tone": analyze_tone(content),
            "terminology": extract_terminology(content),
            "structure": analyze_structure(content),
        }

    return results

def generate_audit_report(workflow_name: str, results: Dict) -> str:
    """Generate markdown audit report."""
    md = f"# Design Language Audit: {workflow_name}\n\n"
    md += f"**Date:** {Path(__file__).stat().st_mtime}\n\n"
    md += f"**Skills Audited:** {len(results)}\n\n"

    # Tone consistency
    md += "## Tone Analysis\n\n"
    tones = [r["tone"]["tone"] for r in results.values()]
    tone_counts = {t: tones.count(t) for t in set(tones)}

    md += "| Skill | Tone | Formal Score | Casual Score | Technical Score |\n"
    md += "|-------|------|--------------|--------------|------------------|\n"

    for skill, data in results.items():
        tone_data = data["tone"]
        md += f"| `{skill}` | {tone_data['tone']} | {tone_data['formal_score']} | {tone_data['casual_score']} | {tone_data['technical_score']} |\n"

    md += f"\n**Consistency:** "
    if len(tone_counts) == 1:
        md += "✅ All skills use consistent tone\n\n"
    else:
        md += f"⚠️  Mixed tones detected: {tone_counts}\n\n"

    # Terminology overlap
    md += "## Terminology Analysis\n\n"
    all_terms = set()
    for data in results.values():
        all_terms.update(data["terminology"].keys())

    common_terms = []
    for term in all_terms:
        count = sum(1 for data in results.values() if term in data["terminology"])
        if count >= len(results) * 0.5:  # Used in 50%+ of skills
            common_terms.append((term, count))

    md += "**Common Terms** (used in 50%+ of skills):\n\n"
    for term, count in sorted(common_terms, key=lambda x: x[1], reverse=True)[:15]:
        md += f"- `{term}` ({count}/{len(results)} skills)\n"

    # Structure consistency
    md += "\n## Structure Analysis\n\n"
    md += "| Skill | Headers | Code Blocks | Lists |\n"
    md += "|-------|---------|-------------|-------|\n"

    for skill, data in results.items():
        struct = data["structure"]
        md += f"| `{skill}` | {struct['header_count']} | {struct['code_block_count']} | {struct['list_count']} |\n"

    # Recommendations
    md += "\n## Recommendations\n\n"

    if len(tone_counts) > 1:
        md += "### Tone Consistency\n"
        md += f"- Mixed tones detected. Consider standardizing to: {max(tone_counts, key=tone_counts.get)}\n\n"

    md += "### Terminology\n"
    md += "- Review common terms for consistency\n"
    md += "- Ensure same concepts use same terminology across skills\n\n"

    return md

def audit_design_language(workflow_name: str = None):
    """Main function to audit design language."""
    print("🎨 Auditing design language...")

    # Load relationships
    if not RELATIONSHIPS_FILE.exists():
        print("❌ Relationships file not found. Run discover_relationships.py first.")
        return

    data = json.loads(RELATIONSHIPS_FILE.read_text())

    # Determine which skills to audit
    if workflow_name:
        # Audit specific workflow
        from map_workflows import WORKFLOW_PATTERNS
        if workflow_name not in WORKFLOW_PATTERNS:
            print(f"❌ Workflow '{workflow_name}' not found")
            return

        skills_to_audit = WORKFLOW_PATTERNS[workflow_name]["skills"]
    else:
        # Audit all skills
        skills_to_audit = list(data["skills"].keys())[:20]  # Limit to 20 for performance

    # Run audit
    results = audit_workflow(skills_to_audit)

    # Generate report
    report = generate_audit_report(workflow_name or "All Skills", results)

    # Save report
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report)

    print(f"\n✅ Audit report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else None
    audit_design_language(workflow)

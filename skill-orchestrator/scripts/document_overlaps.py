#!/usr/bin/env python3
"""
Overlap Documentation Script
Documents functional overlaps between skill groups without proposing consolidation.
"""

import os
import json
from pathlib import Path

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
RELATIONSHIPS_FILE = Path(__file__).parent.parent / "references/skill_relationships.json"
OUTPUT_FILE = Path(__file__).parent.parent / "references/skill_overlaps.md"

# Skill groups identified for overlap analysis
SKILL_GROUPS = {
    "WordPress Management": [
        "wp-cli-expert", "wp-wpcli-and-ops", "wp-site-manager", "wp-project-triage",
        "wp-block-development", "wp-block-themes", "wp-plugin-development",
        "wp-rest-api", "wp-interactivity-api", "wp-performance", "wp-phpstan",
        "wp-playground", "wpds", "wp-world-inspire-lab-wi", "wordpress-router"
    ],
    "E-Commerce Landing Pages": [
        "ecommerce-landing-page", "ecommerce-lp-generator"
    ],
    "Image Enhancement": [
        "image-enhancer", "repair-old-photos", "topaz-photo-ai-upscaler"
    ],
    "Life Coaching": [
        "elon-musk-life-coach", "lifestyle-aesthetic-designer", "consultant-friend"
    ]
}

def read_skill_description(skill_name):
    """Extract description from SKILL.md."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return "No description available"

    try:
        content = skill_path.read_text()
        # Extract description from frontmatter or first paragraph
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('description:'):
                return line.replace('description:', '').strip().strip('"\'')
            elif i > 10 and line.strip() and not line.startswith('#') and not line.startswith('---'):
                return line.strip()
        return "No description found"
    except Exception as e:
        return f"Error: {e}"

def analyze_skill_capabilities(skill_name):
    """Analyze skill capabilities from SKILL.md."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return []

    try:
        content = skill_path.read_text().lower()
        capabilities = []

        # Common capability keywords
        keywords = {
            "create": "creation",
            "generate": "generation",
            "build": "building",
            "deploy": "deployment",
            "manage": "management",
            "configure": "configuration",
            "optimize": "optimization",
            "debug": "debugging",
            "test": "testing",
            "analyze": "analysis",
            "enhance": "enhancement",
            "restore": "restoration",
            "upscale": "upscaling",
            "coach": "coaching",
            "design": "design",
            "develop": "development"
        }

        for keyword, capability in keywords.items():
            if keyword in content:
                capabilities.append(capability)

        return list(set(capabilities))
    except:
        return []

def load_relationships():
    """Load skill relationships data."""
    if not RELATIONSHIPS_FILE.exists():
        return {}
    try:
        with open(RELATIONSHIPS_FILE) as f:
            data = json.load(f)
            return data.get("skills", {})
    except:
        return {}

def generate_overlap_matrix(group_name, skills):
    """Generate overlap matrix for a skill group."""
    matrix = []
    matrix.append(f"### {group_name}\n\n")
    matrix.append(f"**Skills in group:** {len(skills)}\n\n")

    # Skill descriptions
    matrix.append("#### Skill Descriptions\n\n")
    for skill in skills:
        desc = read_skill_description(skill)
        matrix.append(f"**{skill}**\n")
        matrix.append(f"- {desc}\n\n")

    # Capability matrix
    matrix.append("#### Capability Matrix\n\n")
    skill_capabilities = {skill: analyze_skill_capabilities(skill) for skill in skills}

    # Find common capabilities
    all_capabilities = set()
    for caps in skill_capabilities.values():
        all_capabilities.update(caps)

    if all_capabilities:
        matrix.append("| Skill | " + " | ".join(sorted(all_capabilities)) + " |\n")
        matrix.append("|-------|" + "|".join(["---"] * len(all_capabilities)) + "|\n")

        for skill in skills:
            caps = skill_capabilities[skill]
            row = [skill]
            for cap in sorted(all_capabilities):
                row.append("✓" if cap in caps else "")
            matrix.append("| " + " | ".join(row) + " |\n")
        matrix.append("\n")

    # Overlap analysis
    matrix.append("#### Overlap Analysis\n\n")

    # Find pairs with high overlap
    overlaps = []
    for i, skill1 in enumerate(skills):
        for skill2 in skills[i+1:]:
            caps1 = set(skill_capabilities[skill1])
            caps2 = set(skill_capabilities[skill2])
            if caps1 and caps2:
                overlap = len(caps1 & caps2) / len(caps1 | caps2) * 100
                if overlap > 30:
                    overlaps.append((skill1, skill2, overlap, caps1 & caps2))

    if overlaps:
        overlaps.sort(key=lambda x: x[2], reverse=True)
        for skill1, skill2, overlap, common_caps in overlaps:
            matrix.append(f"**{skill1}** ↔ **{skill2}**: {overlap:.0f}% overlap\n")
            matrix.append(f"- Common capabilities: {', '.join(sorted(common_caps))}\n\n")
    else:
        matrix.append("No significant overlaps detected (>30% capability overlap).\n\n")

    # Use case boundaries
    matrix.append("#### When to Use Which Skill\n\n")
    matrix.append("**Decision Guidelines:**\n\n")

    # Group-specific guidelines
    if group_name == "WordPress Management":
        matrix.append("- **wp-cli-expert / wp-wpcli-and-ops**: Direct WP-CLI command execution\n")
        matrix.append("- **wp-site-manager**: Full site deployment and management\n")
        matrix.append("- **wp-project-triage**: Diagnostic and inspection workflows\n")
        matrix.append("- **wp-block-development / wp-block-themes**: Gutenberg block/theme development\n")
        matrix.append("- **wp-plugin-development**: Plugin architecture and development\n")
        matrix.append("- **wp-rest-api**: REST API extension and debugging\n")
        matrix.append("- **wp-performance**: Performance optimization and profiling\n")
        matrix.append("- **wp-playground**: Fast prototyping without server setup\n\n")

    elif group_name == "E-Commerce Landing Pages":
        matrix.append("- **ecommerce-landing-page**: Comprehensive landing page design with product analysis\n")
        matrix.append("- **ecommerce-lp-generator**: Grid-based generation for consistency and efficiency\n\n")

    elif group_name == "Image Enhancement":
        matrix.append("- **image-enhancer**: General image quality improvement\n")
        matrix.append("- **repair-old-photos**: Specialized restoration for damaged/old photos\n")
        matrix.append("- **topaz-photo-ai-upscaler**: Professional AI upscaling using Topaz Photo AI\n\n")

    elif group_name == "Life Coaching":
        matrix.append("- **elon-musk-life-coach**: Elon Musk's perspective and principles\n")
        matrix.append("- **lifestyle-aesthetic-designer**: Proactive day design and aesthetic coaching\n")
        matrix.append("- **consultant-friend**: Strategic McKinsey-style business advisory\n\n")

    matrix.append("---\n\n")
    return "".join(matrix)

def generate_report():
    """Generate comprehensive overlap documentation."""
    report = []
    report.append("# Skill Overlap Documentation\n\n")
    report.append(f"Generated: {Path(__file__).name}\n")
    report.append(f"Total skill groups analyzed: {len(SKILL_GROUPS)}\n\n")

    report.append("## Overview\n\n")
    report.append("This document identifies and documents functional overlaps between skill groups ")
    report.append("without proposing consolidation. The goal is to help users understand when to use ")
    report.append("which skill and how skills complement each other.\n\n")

    report.append("## Skill Groups\n\n")

    for group_name, skills in SKILL_GROUPS.items():
        report.append(generate_overlap_matrix(group_name, skills))

    report.append("## Summary\n\n")
    report.append("### Key Findings\n\n")

    total_skills = sum(len(skills) for skills in SKILL_GROUPS.values())
    report.append(f"- **Total skills analyzed:** {total_skills}\n")
    report.append(f"- **Skill groups:** {len(SKILL_GROUPS)}\n")
    report.append("- **Largest group:** WordPress Management (15 skills)\n")
    report.append("- **Overlap type:** Complementary (skills serve different aspects of same domain)\n\n")

    report.append("### Recommendations\n\n")
    report.append("1. **No consolidation needed** - Skills serve distinct use cases within their domains\n")
    report.append("2. **Document workflows** - Show how skills work together in multi-step processes\n")
    report.append("3. **Improve discovery** - Help users find the right skill for their specific need\n")
    report.append("4. **Cross-reference** - Add \"See also\" sections in SKILL.md files\n\n")

    return "".join(report)

def main():
    """Main execution."""
    print("Documenting skill overlaps...")
    report = generate_report()

    OUTPUT_FILE.write_text(report)
    print(f"✓ Report generated: {OUTPUT_FILE}")
    print(f"  Analyzed {len(SKILL_GROUPS)} skill groups")
    print(f"  Total skills: {sum(len(skills) for skills in SKILL_GROUPS.values())}")

if __name__ == "__main__":
    main()

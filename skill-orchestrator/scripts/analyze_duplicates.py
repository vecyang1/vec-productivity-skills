#!/usr/bin/env python3
"""
Duplicate Analysis Script
Analyzes duplicate and redundant skills, providing detailed comparison and deletion recommendations.
"""

import os
import json
from pathlib import Path
from difflib import SequenceMatcher

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
OUTPUT_FILE = Path(__file__).parent.parent / "references/duplicate_analysis.md"

# Duplicate candidates identified in the plan
DUPLICATES = [
    ("stitch-enhance-prompt2", "stitch-enhance-prompt", "symlink duplicate"),
    ("stitch-react-components 2", "stitch-react-components", "symlink duplicate"),
    ("heic-converter", "heif-converter", "incomplete symlink"),
    ("continuous-learning", "continuous-learning-v2", "deprecated version"),
    ("to-notebooklm-artifacts", "media-to-notebooklm-artifacts", "older version"),
]

def read_skill_md(skill_name):
    """Read SKILL.md content for a skill."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return None
    try:
        return skill_path.read_text()
    except Exception as e:
        return f"Error reading: {e}"

def calculate_similarity(text1, text2):
    """Calculate text similarity percentage."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1, text2).ratio() * 100

def check_symlink(skill_name):
    """Check if skill is a symlink and return target."""
    skill_path = SKILLS_DIR / skill_name
    if skill_path.is_symlink():
        return str(skill_path.readlink())
    return None

def analyze_skill_structure(skill_name):
    """Analyze skill directory structure."""
    skill_path = SKILLS_DIR / skill_name
    if not skill_path.exists():
        return {"exists": False}

    structure = {
        "exists": True,
        "is_symlink": skill_path.is_symlink(),
        "has_skill_md": (skill_path / "SKILL.md").exists(),
        "has_scripts": (skill_path / "scripts").exists(),
        "has_references": (skill_path / "references").exists(),
        "has_assets": (skill_path / "assets").exists(),
    }

    if structure["has_scripts"]:
        scripts_dir = skill_path / "scripts"
        structure["script_count"] = len(list(scripts_dir.glob("*.py"))) + len(list(scripts_dir.glob("*.sh")))
    else:
        structure["script_count"] = 0

    return structure

def generate_report():
    """Generate comprehensive duplicate analysis report."""
    report = []
    report.append("# Duplicate Skills Analysis Report\n")
    report.append(f"Generated: {Path(__file__).name}\n")
    report.append(f"Total candidates analyzed: {len(DUPLICATES)}\n\n")

    report.append("## Executive Summary\n\n")
    report.append("This report analyzes 5 duplicate/redundant skill candidates:\n")
    report.append("- 3 symlink duplicates (HIGH priority deletion)\n")
    report.append("- 2 deprecated versions (HIGH priority deletion)\n\n")

    report.append("---\n\n")

    for idx, (skill1, skill2, reason) in enumerate(DUPLICATES, 1):
        report.append(f"## {idx}. {skill1} vs {skill2}\n\n")
        report.append(f"**Duplicate Type:** {reason}\n\n")

        # Check symlinks
        symlink1 = check_symlink(skill1)
        symlink2 = check_symlink(skill2)

        if symlink1:
            report.append(f"**{skill1}** is a symlink → `{symlink1}`\n\n")
        if symlink2:
            report.append(f"**{skill2}** is a symlink → `{symlink2}`\n\n")

        # Analyze structure
        struct1 = analyze_skill_structure(skill1)
        struct2 = analyze_skill_structure(skill2)

        report.append("### Directory Structure Comparison\n\n")
        report.append("| Feature | " + skill1 + " | " + skill2 + " |\n")
        report.append("|---------|" + "-" * len(skill1) + "|" + "-" * len(skill2) + "|\n")
        report.append(f"| Exists | {struct1.get('exists', False)} | {struct2.get('exists', False)} |\n")
        report.append(f"| Is Symlink | {struct1.get('is_symlink', False)} | {struct2.get('is_symlink', False)} |\n")
        report.append(f"| Has SKILL.md | {struct1.get('has_skill_md', False)} | {struct2.get('has_skill_md', False)} |\n")
        report.append(f"| Has scripts/ | {struct1.get('has_scripts', False)} | {struct2.get('has_scripts', False)} |\n")
        report.append(f"| Script Count | {struct1.get('script_count', 0)} | {struct2.get('script_count', 0)} |\n")
        report.append(f"| Has references/ | {struct1.get('has_references', False)} | {struct2.get('has_references', False)} |\n\n")

        # Read and compare SKILL.md content
        content1 = read_skill_md(skill1)
        content2 = read_skill_md(skill2)

        if content1 and content2:
            similarity = calculate_similarity(content1, content2)
            report.append(f"### Content Similarity: {similarity:.1f}%\n\n")

            if similarity > 90:
                report.append("**Analysis:** Nearly identical content - clear duplicate.\n\n")
            elif similarity > 70:
                report.append("**Analysis:** High similarity - likely duplicate with minor variations.\n\n")
            elif similarity > 50:
                report.append("**Analysis:** Moderate similarity - may have overlapping functionality.\n\n")
            else:
                report.append("**Analysis:** Low similarity - may serve different purposes.\n\n")

        # Recommendation
        report.append("### Recommendation\n\n")

        if "symlink" in reason.lower():
            report.append(f"**Action:** DELETE `{skill1}` (symlink duplicate)\n\n")
            report.append(f"**Reason:** This is a symlink pointing to external location. The canonical version `{skill2}` should be used.\n\n")
            report.append(f"**Impact:** None - symlink removal has no functional impact.\n\n")
            report.append(f"**Command:**\n```bash\nrm ~/.gemini/antigravity/skills/{skill1}\n```\n\n")

        elif "deprecated" in reason.lower() or "older" in reason.lower():
            report.append(f"**Action:** DELETE `{skill1}` (deprecated/older version)\n\n")
            report.append(f"**Reason:** Superseded by `{skill2}` which has better architecture/features.\n\n")
            report.append(f"**Impact:** Low - users should migrate to newer version.\n\n")
            report.append(f"**Command:**\n```bash\nrm -rf ~/.gemini/antigravity/skills/{skill1}\n```\n\n")

        report.append("---\n\n")

    # Summary table
    report.append("## Deletion Summary\n\n")
    report.append("| Skill to Delete | Reason | Priority | Command |\n")
    report.append("|----------------|--------|----------|----------|\n")

    for skill1, skill2, reason in DUPLICATES:
        priority = "HIGH" if "symlink" in reason.lower() or "deprecated" in reason.lower() else "MEDIUM"
        cmd = f"`rm {skill1}`" if "symlink" in reason.lower() else f"`rm -rf {skill1}`"
        report.append(f"| {skill1} | {reason} | {priority} | {cmd} |\n")

    report.append("\n## Next Steps\n\n")
    report.append("1. Review each duplicate candidate above\n")
    report.append("2. Verify no active dependencies on skills marked for deletion\n")
    report.append("3. Execute deletion commands for approved candidates\n")
    report.append("4. Update `installation_log.md` with deletion entries\n")
    report.append("5. Commit changes to skills repository\n")

    return "".join(report)

def main():
    """Main execution."""
    print("Analyzing duplicate skills...")
    report = generate_report()

    OUTPUT_FILE.write_text(report)
    print(f"✓ Report generated: {OUTPUT_FILE}")
    print(f"  Analyzed {len(DUPLICATES)} duplicate candidates")

if __name__ == "__main__":
    main()

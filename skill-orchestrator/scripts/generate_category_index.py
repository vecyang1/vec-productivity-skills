#!/usr/bin/env python3
"""
Category Index Generator
Organizes all 216 skills into 10 logical categories for easy browsing.
"""

import os
from pathlib import Path

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
OUTPUT_FILE = Path.home() / ".gemini/antigravity/skills/CATEGORIES.md"

# 10 major categories with their skills
CATEGORIES = {
    "Content Creation": {
        "description": "Writing, research, copywriting, and content strategy",
        "skills": [
            "content-research-writer", "my-creative-writer", "honest-deep-researcher",
            "google-deep-research", "psychological-copywriter", "performance-ads-writer",
            "interview-to-article", "general-song-writer", "naturalize-text-localize",
            "youtube-title", "youtube-video-hook", "youtube-plan-new-video",
            "youtube-research-video-topic", "xhs-note-creator-template",
            "local-store-promotion", "seven-figure-course-builder",
            "japan-med-content-matrix", "creator-monetization-engine",
            "internal-comms", "competitive-ads-extractor", "reverse-prompt-engineer",
            "visual-prompt-engineer-patten", "music-video-title-generator",
            "curation-expert", "interview-user", "best-minds", "general-analysis-5w1h",
            "know-an-industry-fast", "academic-navigator", "language-teacher",
            "prd", "changelog-generator", "simplify", "context-engineering-collection",
            "prompt-lookup", "strategic-compact", "iterative-retrieval",
            "stitch-enhance-prompt", "design-md", "stitch-design-md"
        ]
    },
    "Visual & Media Production": {
        "description": "Design, images, video, audio generation and editing",
        "skills": [
            "smart-illustrator", "Nano-Banana", "seedream-4-5", "sora2-video-gen",
            "image-enhancer", "topaz-photo-ai-upscaler", "repair-old-photos",
            "ecommerce-product-refine", "remove-bg", "gemini-watermark-remover",
            "svg-generator", "svg-icon-search", "reference-photo-expander",
            "article-broll-illustrator", "theme-serial-gen", "youtube-thumbnail",
            "opc-banner-creator", "opc-logo-creator", "ecommerce-kv",
            "aippt-enterprise", "mermaid-visualizer", "excalidraw-diagram",
            "obsidian-canvas-creator", "obsidian-json-canvas", "theme-factory",
            "videocut", "gyroflow-stabilizer", "music-video-prep", "remotion",
            "remotion-ads-producer", "manim-math-animator", "transcribe-media",
            "Read-Media-Gemini", "video-downloader", "heif-converter",
            "document-skills", "tts-elevenlabs", "media-organizer",
            "to-notebooklm-artifacts", "media-to-notebooklm-artifacts",
            "zstmfhy-zlibrary-to-notebooklm"
        ]
    },
    "Web & App Development": {
        "description": "Frontend, backend, WordPress, and deployment",
        "skills": [
            "stitch", "stitch-loop", "stitch-react-components", "frontend-design",
            "frontend-patterns", "backend-patterns", "cache-components",
            "vercel-react-best-practices", "coding-standards", "tdd-workflow",
            "web-design-guidelines", "vercel-deployment-guide", "vps-proxy-setup",
            "china-global-deployment", "site-url-extractor", "web-metadata-extractor",
            "site-accessibility-judge-China-oversea", "chrome-devtools",
            "wp-cli-expert", "wp-wpcli-and-ops", "wp-site-manager",
            "wp-project-triage", "wp-block-development", "wp-block-themes",
            "wp-plugin-development", "wp-rest-api", "wp-interactivity-api",
            "wp-performance", "wp-phpstan", "wp-playground", "wpds",
            "wp-world-inspire-lab-wi", "wordpress-router", "security-review",
            "postgres-patterns", "init-blast-method", "init-vault-method"
        ]
    },
    "E-Commerce & Business": {
        "description": "Product, marketing, operations, and business strategy",
        "skills": [
            "cross-border-product-selector", "cross-border-ai-strategist",
            "ecommerce-landing-page", "ecommerce-lp-generator", "surecart-manager",
            "amazon-operations-director", "etsy-seller-general", "dtc-brand-library",
            "seller-browser-safe", "trademark-guard-brand-name-domain",
            "opc-domain-hunter", "executing-marketing-campaigns",
            "Post-Social-Media-With-GetLate-API-Repurpose-Distribute",
            "scientific-business-guide", "consultant-friend", "startup-metrics-framework",
            "market-sizing-analysis", "team-composition-analysis",
            "creating-financial-models", "business-model-xray",
            "company-asset-isolation", "personal-asset-manager",
            "japan-tax-planning", "baoyang-guide"
        ]
    },
    "Data & Research": {
        "description": "Analysis, research, scraping, and data processing",
        "skills": [
            "honest-deep-researcher", "google-deep-research", "web-search-manager",
            "competitive-ads-extractor", "opc-twitter", "opc-reddit",
            "opc-producthunt", "opc-seo-geo", "site-url-extractor",
            "web-metadata-extractor", "notebooklm-py", "model-intelligence",
            "wheel-check", "eval-harness"
        ]
    },
    "Productivity & Automation": {
        "description": "Workflows, automation, and productivity tools",
        "skills": [
            "planning-with-files", "skill-orchestrator", "skill-creator",
            "skill-improver", "skill-lookup", "skill-github-importer",
            "skill-from-code", "file-organizer", "media-organizer",
            "package-tracker", "connect", "environment-manager",
            "system-git-discovery-sync", "claude-code-agile-updater",
            "continuous-learning", "continuous-learning-v2", "evolver"
        ]
    },
    "Personal Development": {
        "description": "Coaching, learning, and personal growth",
        "skills": [
            "elon-musk-life-coach", "lifestyle-aesthetic-designer",
            "consultant-friend", "life-learning-companion",
            "life-trajectory-deduction", "social-dynamics-mastery",
            "family-health-guardian", "guitar-learning", "polyamory-rules",
            "historical-mirror", "visa-itinerary-pro", "travel-deal-hunter",
            "city-cost-compare-nomad", "qingdouyun-manual"
        ]
    },
    "Infrastructure & DevOps": {
        "description": "DNS, hosting, cloud, and infrastructure management",
        "skills": [
            "godaddy-dns-manager", "cloudflare-dns-manager", "vps-proxy-setup",
            "china-global-deployment", "google-cloud-integration",
            "clash-verge-guide", "email-management", "onecontext-manager",
            "clawdbot-repair", "302ai-integration", "mcp-flight-search"
        ]
    },
    "AI & Model Integration": {
        "description": "Models, prompts, training, and AI tools",
        "skills": [
            "model-intelligence", "codex-config", "rl-training-ppo",
            "reverse-prompt-engineer", "visual-prompt-engineer-patten",
            "prompt-lookup", "context-engineering-collection",
            "claude-cli-guide", "claude-code-agent-teams", "gsd-framework-guide",
            "evolver", "eval-harness"
        ]
    },
    "Meta & System": {
        "description": "Framework, documentation, and system management",
        "skills": [
            "skill-orchestrator", "skill-creator", "skill-improver",
            "skill-lookup", "skill-github-importer", "skill-from-code",
            "template-skill", "notion-mcp-connector", "google-docs-mcp-server",
            "mcp-builder", "mcp-integration", "keybindings-help", "alias",
            "memory:context-vault", "gsd-framework-guide"
        ]
    }
}

def read_skill_description(skill_name):
    """Extract description from SKILL.md."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return "No description available"

    try:
        content = skill_path.read_text()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('description:'):
                desc = line.replace('description:', '').strip().strip('"\'')
                return desc[:120] + "..." if len(desc) > 120 else desc
            elif i > 10 and line.strip() and not line.startswith('#') and not line.startswith('---'):
                desc = line.strip()
                return desc[:120] + "..." if len(desc) > 120 else desc
        return "No description found"
    except:
        return "Error reading description"

def generate_category_section(category_name, category_data):
    """Generate markdown section for a category."""
    section = []
    section.append(f"## {category_name}\n\n")
    section.append(f"**Description:** {category_data['description']}\n\n")
    section.append(f"**Skills in category:** {len(category_data['skills'])}\n\n")

    # Sort skills alphabetically
    sorted_skills = sorted(category_data['skills'])

    for skill in sorted_skills:
        desc = read_skill_description(skill)
        section.append(f"### {skill}\n")
        section.append(f"{desc}\n\n")

    section.append("---\n\n")
    return "".join(section)

def generate_quick_reference():
    """Generate quick reference table."""
    table = []
    table.append("## Quick Reference\n\n")
    table.append("| Category | Skills | Description |\n")
    table.append("|----------|--------|-------------|\n")

    for category_name, category_data in CATEGORIES.items():
        skill_count = len(category_data['skills'])
        desc = category_data['description']
        table.append(f"| {category_name} | {skill_count} | {desc} |\n")

    table.append("\n")
    return "".join(table)

def generate_index():
    """Generate complete category index."""
    report = []
    report.append("# Skill Category Index\n\n")
    report.append(f"Generated: {Path(__file__).name}\n")

    total_skills = sum(len(cat['skills']) for cat in CATEGORIES.values())
    report.append(f"Total skills: {total_skills} | Categories: {len(CATEGORIES)}\n\n")

    report.append("## Overview\n\n")
    report.append("This index organizes all skills into 10 logical categories for easy browsing and discovery. ")
    report.append("Use this index to find skills by domain or purpose.\n\n")

    # Quick reference table
    report.append(generate_quick_reference())

    # Table of contents
    report.append("## Table of Contents\n\n")
    for i, category_name in enumerate(CATEGORIES.keys(), 1):
        anchor = category_name.lower().replace(" ", "-").replace("&", "")
        report.append(f"{i}. [{category_name}](#{anchor})\n")
    report.append("\n---\n\n")

    # Generate each category section
    for category_name, category_data in CATEGORIES.items():
        report.append(generate_category_section(category_name, category_data))

    # Search tips
    report.append("## Search Tips\n\n")
    report.append("### By Purpose\n")
    report.append("- **Creating content?** → Content Creation\n")
    report.append("- **Designing visuals?** → Visual & Media Production\n")
    report.append("- **Building websites?** → Web & App Development\n")
    report.append("- **Running e-commerce?** → E-Commerce & Business\n")
    report.append("- **Researching topics?** → Data & Research\n\n")

    report.append("### By Workflow\n")
    report.append("See `skill-orchestrator/references/workflow_cooperation.md` for detailed workflow maps:\n")
    report.append("- Writing Workflow (内容创作)\n")
    report.append("- 配图 Workflow (Illustration/Visual)\n")
    report.append("- 剪辑 Workflow (Video Editing)\n")
    report.append("- 网站 Workflow (Website Development)\n\n")

    report.append("### By Relationship\n")
    report.append("Use `skill-orchestrator` to discover skill relationships:\n")
    report.append("```bash\n")
    report.append("python3 ~/.gemini/antigravity/skills/skill-orchestrator/scripts/query_relationships.py <skill-name>\n")
    report.append("```\n\n")

    return "".join(report)

def main():
    """Main execution."""
    print("Generating category index...")
    index = generate_index()

    OUTPUT_FILE.write_text(index)
    print(f"✓ Index generated: {OUTPUT_FILE}")

    total_skills = sum(len(cat['skills']) for cat in CATEGORIES.values())
    print(f"  Total skills: {total_skills}")
    print(f"  Categories: {len(CATEGORIES)}")

    for category_name, category_data in CATEGORIES.items():
        print(f"  - {category_name}: {len(category_data['skills'])} skills")

if __name__ == "__main__":
    main()

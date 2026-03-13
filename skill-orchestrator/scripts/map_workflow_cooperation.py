#!/usr/bin/env python3
"""
Workflow Cooperation Mapping Script
Maps how skills cooperate within 4 parallel workflows: Writing, 配图, 剪辑, 网站
"""

import os
import json
from pathlib import Path

SKILLS_DIR = Path.home() / ".gemini/antigravity/skills"
RELATIONSHIPS_FILE = Path(__file__).parent.parent / "references/skill_relationships.json"
OUTPUT_FILE = Path(__file__).parent.parent / "references/workflow_cooperation.md"

# 4 parallel workflows with their skills
WORKFLOWS = {
    "Writing Workflow (内容创作)": {
        "description": "Research → Write → Refine → Distribute pipeline for content creation",
        "phases": {
            "Research": [
                "honest-deep-researcher", "google-deep-research", "web-search-manager",
                "youtube-research-video-topic", "competitive-ads-extractor"
            ],
            "Write": [
                "content-research-writer", "my-creative-writer", "psychological-copywriter",
                "performance-ads-writer", "interview-to-article", "general-song-writer"
            ],
            "Refine": [
                "naturalize-text-localize", "simplify", "reverse-prompt-engineer"
            ],
            "Distribute": [
                "youtube-title", "youtube-video-hook", "youtube-plan-new-video",
                "youtube-thumbnail", "xhs-note-creator-template", "local-store-promotion",
                "Post-Social-Media-With-GetLate-API-Repurpose-Distribute"
            ],
            "Specialized": [
                "seven-figure-course-builder", "japan-med-content-matrix",
                "creator-monetization-engine", "internal-comms"
            ]
        }
    },
    "配图 Workflow (Illustration/Visual)": {
        "description": "Generate → Enhance → Export pipeline for visual content",
        "phases": {
            "Generate": [
                "smart-illustrator", "Nano-Banana", "seedream-4-5", "sora2-video-gen",
                "svg-generator", "svg-icon-search", "reference-photo-expander",
                "article-broll-illustrator", "theme-serial-gen"
            ],
            "Enhance": [
                "image-enhancer", "topaz-photo-ai-upscaler", "repair-old-photos",
                "ecommerce-product-refine", "remove-bg", "gemini-watermark-remover"
            ],
            "Design Systems": [
                "mermaid-visualizer", "excalidraw-diagram", "obsidian-canvas-creator",
                "obsidian-json-canvas", "theme-factory"
            ],
            "Specialized": [
                "youtube-thumbnail", "opc-banner-creator", "opc-logo-creator",
                "ecommerce-kv", "aippt-enterprise", "reverse-prompt-engineer",
                "visual-prompt-engineer-patten"
            ],
            "Format Conversion": [
                "heif-converter", "document-skills"
            ]
        }
    },
    "剪辑 Workflow (Video Editing)": {
        "description": "Transcribe → Edit → Generate → Optimize pipeline for video production",
        "phases": {
            "Transcribe": [
                "transcribe-media", "Read-Media-Gemini"
            ],
            "Edit": [
                "videocut", "gyroflow-stabilizer", "music-video-prep"
            ],
            "Generate": [
                "remotion", "remotion-ads-producer", "sora2-video-gen", "manim-math-animator"
            ],
            "Optimize": [
                "gemini-watermark-remover", "video-downloader"
            ]
        }
    },
    "网站 Workflow (Website Development)": {
        "description": "Design → Code → Test → Deploy pipeline for web development",
        "phases": {
            "Design": [
                "stitch", "stitch-loop", "stitch-enhance-prompt", "stitch-react-components",
                "stitch-design-md", "design-md", "frontend-design", "web-design-guidelines"
            ],
            "WordPress": [
                "wp-cli-expert", "wp-wpcli-and-ops", "wp-site-manager", "wp-project-triage",
                "wp-block-development", "wp-block-themes", "wp-plugin-development",
                "wp-rest-api", "wp-interactivity-api", "wp-performance", "wp-phpstan",
                "wp-playground", "wpds", "wp-world-inspire-lab-wi", "wordpress-router"
            ],
            "Development": [
                "frontend-patterns", "backend-patterns", "cache-components",
                "vercel-react-best-practices", "coding-standards", "tdd-workflow"
            ],
            "Deployment": [
                "vercel-deployment-guide", "vps-proxy-setup", "china-global-deployment",
                "godaddy-dns-manager", "cloudflare-dns-manager"
            ],
            "Utilities": [
                "site-url-extractor", "web-metadata-extractor", "site-accessibility-judge-China-oversea",
                "chrome-devtools"
            ]
        }
    }
}

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

def read_skill_description(skill_name):
    """Extract description from SKILL.md."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return "No description"

    try:
        content = skill_path.read_text()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('description:'):
                desc = line.replace('description:', '').strip().strip('"\'')
                return desc[:100] + "..." if len(desc) > 100 else desc
            elif i > 10 and line.strip() and not line.startswith('#') and not line.startswith('---'):
                desc = line.strip()
                return desc[:100] + "..." if len(desc) > 100 else desc
        return "No description"
    except:
        return "Error reading"

def find_skill_connections(skill_name, relationships):
    """Find which skills this skill connects to."""
    if skill_name not in relationships:
        return []
    return relationships[skill_name].get("direct_references", [])

def generate_workflow_map(workflow_name, workflow_data, relationships):
    """Generate cooperation map for a workflow."""
    report = []
    report.append(f"## {workflow_name}\n\n")
    report.append(f"**Description:** {workflow_data['description']}\n\n")

    # Count total skills
    total_skills = sum(len(skills) for skills in workflow_data['phases'].values())
    report.append(f"**Total skills:** {total_skills}\n\n")

    # Phase breakdown
    report.append("### Workflow Phases\n\n")

    for phase_name, skills in workflow_data['phases'].items():
        report.append(f"#### {phase_name} ({len(skills)} skills)\n\n")

        for skill in skills:
            desc = read_skill_description(skill)
            report.append(f"**{skill}**\n")
            report.append(f"- {desc}\n")

            # Find connections to other skills in workflow
            connections = find_skill_connections(skill, relationships)
            workflow_connections = [c for c in connections if any(c in phase_skills for phase_skills in workflow_data['phases'].values())]

            if workflow_connections:
                report.append(f"- Connects to: {', '.join(workflow_connections)}\n")

            report.append("\n")

    # Cooperation chains
    report.append("### Common Cooperation Chains\n\n")

    if workflow_name.startswith("Writing"):
        report.append("1. **Deep Research → Content Writing**\n")
        report.append("   - `honest-deep-researcher` → `content-research-writer` → `my-creative-writer`\n")
        report.append("   - Research findings feed directly into content creation\n\n")

        report.append("2. **Content → Platform Distribution**\n")
        report.append("   - `my-creative-writer` → `youtube-title` + `youtube-thumbnail` → `Post-Social-Media-With-GetLate-API-Repurpose-Distribute`\n")
        report.append("   - Single content piece adapted for multiple platforms\n\n")

        report.append("3. **Interview → Article**\n")
        report.append("   - `interview-to-article` → `naturalize-text-localize` → platform-specific skills\n")
        report.append("   - Interview transcripts transformed into polished articles\n\n")

    elif "配图" in workflow_name:
        report.append("1. **Generate → Enhance → Export**\n")
        report.append("   - `smart-illustrator` / `seedream-4-5` → `image-enhancer` → `remove-bg`\n")
        report.append("   - AI generation followed by quality enhancement\n\n")

        report.append("2. **Photo Restoration Pipeline**\n")
        report.append("   - `repair-old-photos` → `topaz-photo-ai-upscaler` → final export\n")
        report.append("   - Restore damaged photos then upscale for modern use\n\n")

        report.append("3. **Consistent Series Generation**\n")
        report.append("   - `reference-photo-expander` / `theme-serial-gen` → `image-enhancer`\n")
        report.append("   - Generate consistent image series for branding\n\n")

    elif "剪辑" in workflow_name:
        report.append("1. **Transcribe → Edit → Export**\n")
        report.append("   - `transcribe-media` → `videocut` → final video\n")
        report.append("   - Transcription drives intelligent editing decisions\n\n")

        report.append("2. **Stabilize → Edit → Generate**\n")
        report.append("   - `gyroflow-stabilizer` → `videocut` → `remotion`\n")
        report.append("   - Fix shaky footage before editing and effects\n\n")

        report.append("3. **Programmatic Video Generation**\n")
        report.append("   - `stitch` → `remotion` / `remotion-ads-producer`\n")
        report.append("   - Design system feeds into programmatic video creation\n\n")

    elif "网站" in workflow_name:
        report.append("1. **Design → Code → Deploy**\n")
        report.append("   - `stitch` → `stitch-react-components` → `vercel-deployment-guide`\n")
        report.append("   - Design system to production-ready code\n\n")

        report.append("2. **WordPress Full Stack**\n")
        report.append("   - `wp-project-triage` → `wp-block-development` / `wp-plugin-development` → `wp-site-manager`\n")
        report.append("   - Inspect → Develop → Deploy WordPress projects\n\n")

        report.append("3. **Performance Optimization**\n")
        report.append("   - `site-accessibility-judge-China-oversea` → `wp-performance` / `vercel-react-best-practices` → redeploy\n")
        report.append("   - Diagnose issues then apply targeted optimizations\n\n")

    report.append("### Entry Points\n\n")
    report.append("**Where to start in this workflow:**\n\n")

    first_phase = list(workflow_data['phases'].keys())[0]
    first_skills = workflow_data['phases'][first_phase][:3]

    for skill in first_skills:
        report.append(f"- **{skill}**: {read_skill_description(skill)}\n")

    report.append("\n### Integration Points\n\n")
    report.append("**How this workflow connects to others:**\n\n")

    if workflow_name.startswith("Writing"):
        report.append("- **→ 配图**: Content needs illustrations (`smart-illustrator`, `article-broll-illustrator`)\n")
        report.append("- **→ 剪辑**: Written scripts become video content (`remotion`, `sora2-video-gen`)\n")
        report.append("- **→ 网站**: Content published on websites (`wp-site-manager`, `stitch`)\n\n")

    elif "配图" in workflow_name:
        report.append("- **← Writing**: Illustrations support written content\n")
        report.append("- **→ 剪辑**: Images become video B-roll or thumbnails\n")
        report.append("- **→ 网站**: Visual assets deployed to websites\n\n")

    elif "剪辑" in workflow_name:
        report.append("- **← Writing**: Scripts and content feed video production\n")
        report.append("- **← 配图**: Visual assets used in video editing\n")
        report.append("- **→ 网站**: Videos embedded in web projects\n\n")

    elif "网站" in workflow_name:
        report.append("- **← Writing**: Content management and publishing\n")
        report.append("- **← 配图**: Visual assets and design systems\n")
        report.append("- **← 剪辑**: Video content embedding and optimization\n\n")

    report.append("---\n\n")
    return "".join(report)

def generate_report():
    """Generate comprehensive workflow cooperation documentation."""
    relationships = load_relationships()

    report = []
    report.append("# Workflow Cooperation Maps\n\n")
    report.append(f"Generated: {Path(__file__).name}\n")
    report.append(f"Total workflows documented: {len(WORKFLOWS)}\n\n")

    report.append("## Overview\n\n")
    report.append("This document maps how skills cooperate within 4 parallel workflows. ")
    report.append("Each workflow represents an independent pipeline for different creative/technical purposes.\n\n")

    report.append("### The 4 Parallel Workflows\n\n")
    for workflow_name, workflow_data in WORKFLOWS.items():
        total = sum(len(skills) for skills in workflow_data['phases'].values())
        report.append(f"1. **{workflow_name}** ({total} skills)\n")
        report.append(f"   - {workflow_data['description']}\n\n")

    report.append("---\n\n")

    # Generate map for each workflow
    for workflow_name, workflow_data in WORKFLOWS.items():
        report.append(generate_workflow_map(workflow_name, workflow_data, relationships))

    # Summary
    report.append("## Summary\n\n")

    total_skills = sum(sum(len(skills) for skills in w['phases'].values()) for w in WORKFLOWS.values())
    report.append(f"### Statistics\n\n")
    report.append(f"- **Total skills across all workflows:** {total_skills}\n")
    report.append(f"- **Total workflows:** {len(WORKFLOWS)}\n")
    report.append(f"- **Average skills per workflow:** {total_skills // len(WORKFLOWS)}\n\n")

    report.append("### Key Insights\n\n")
    report.append("1. **Workflows are independent** - Each serves a distinct creative/technical purpose\n")
    report.append("2. **Workflows are interconnected** - Output from one workflow feeds into others\n")
    report.append("3. **Phase-based structure** - Each workflow has clear phases (research, create, refine, deploy)\n")
    report.append("4. **Skill cooperation** - Skills within phases work together seamlessly\n\n")

    report.append("### Usage Recommendations\n\n")
    report.append("1. **Start at entry points** - Begin with first-phase skills for your workflow\n")
    report.append("2. **Follow cooperation chains** - Use documented chains for common tasks\n")
    report.append("3. **Cross-workflow integration** - Leverage integration points to combine workflows\n")
    report.append("4. **Specialize when needed** - Use specialized skills for specific use cases\n\n")

    return "".join(report)

def main():
    """Main execution."""
    print("Mapping workflow cooperation...")
    report = generate_report()

    OUTPUT_FILE.write_text(report)
    print(f"✓ Report generated: {OUTPUT_FILE}")
    print(f"  Documented {len(WORKFLOWS)} workflows")

    for workflow_name, workflow_data in WORKFLOWS.items():
        total = sum(len(skills) for skills in workflow_data['phases'].values())
        print(f"  - {workflow_name}: {total} skills")

if __name__ == "__main__":
    main()

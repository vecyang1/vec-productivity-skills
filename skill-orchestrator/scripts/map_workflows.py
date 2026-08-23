#!/usr/bin/env python3
"""
Map workflows by analyzing skill relationships and creating workflow chains.
Identifies sequential, parallel, and conditional workflow patterns.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set

RELATIONSHIPS_FILE = Path(__file__).parent.parent / "references/skill_relationships.json"
OUTPUT_FILE = Path(__file__).parent.parent / "references/workflows.md"

# Known workflow patterns (can be extended)
WORKFLOW_PATTERNS = {
    "content-creation": {
        "name": "Content Creation Pipeline",
        "skills": ["honest-deep-researcher", "content-research-writer", "performance-ads-writer"],
        "purpose": "Research → Write → Distribute content",
        "design_language": "Creative/Casual",
    },
    "ecommerce-launch": {
        "name": "E-commerce Product Launch",
        "skills": ["cross-border-product-selector", "ecommerce-lp-generator", "performance-ads-writer"],
        "purpose": "Select product → Create landing page → Launch ads",
        "design_language": "Business/Strategic",
    },
    "wordpress-development": {
        "name": "WordPress Development Workflow",
        "skills": ["wp-project-triage", "wp-block-development", "wp-phpstan", "wp-performance"],
        "purpose": "Audit → Develop → Test → Optimize",
        "design_language": "Technical/Formal",
    },
    "video-production": {
        "name": "Video Content Production",
        "skills": ["youtube-research-video-topic", "youtube-plan-new-video", "youtube-title", "youtube-thumbnail"],
        "purpose": "Research → Plan → Optimize → Design",
        "design_language": "Creative/Casual",
    },
    "research-to-notebooklm": {
        "name": "Research to NotebookLM Artifacts",
        "skills": ["honest-deep-researcher", "media-to-notebooklm-artifacts"],
        "purpose": "Research → Transform to interactive artifacts",
        "design_language": "Technical/Formal",
    },
}

def load_relationships() -> Dict:
    """Load skill relationships from JSON file."""
    if not RELATIONSHIPS_FILE.exists():
        print("❌ Relationships file not found. Run discover_relationships.py first.")
        return None

    return json.loads(RELATIONSHIPS_FILE.read_text())

def discover_workflow_chains(data: Dict) -> List[Dict]:
    """Discover workflow chains from skill relationships."""
    skills = data["skills"]
    chains = []

    # Find chains by following direct references
    for skill_folder, skill_data in skills.items():
        if skill_data["direct_references"]:
            for ref in skill_data["direct_references"]:
                chain = {
                    "type": "sequential",
                    "skills": [skill_folder, ref],
                    "purpose": f"{skill_data['name']} → {skills[ref]['name']}",
                }
                chains.append(chain)

    return chains

def discover_domain_workflows(data: Dict) -> List[Dict]:
    """Discover workflows based on domain clusters."""
    domain_clusters = data["domain_clusters"]
    workflows = []

    for domain, skill_list in domain_clusters.items():
        if len(skill_list) >= 3:
            workflows.append({
                "type": "domain_cluster",
                "domain": domain,
                "skills": skill_list,
                "purpose": f"Complete {domain} workflow",
            })

    return workflows

def generate_workflow_markdown(workflows: Dict, chains: List, domain_workflows: List) -> str:
    """Generate markdown documentation for all workflows."""
    md = "# Skill Workflows\n\n"
    md += "Complete workflows spanning multiple skills.\n\n"
    md += "## Known Workflows\n\n"

    for workflow_id, workflow in workflows.items():
        md += f"### {workflow['name']}\n\n"
        md += f"**ID:** `{workflow_id}`\n\n"
        md += f"**Purpose:** {workflow['purpose']}\n\n"
        md += f"**Design Language:** {workflow['design_language']}\n\n"
        md += "**Skills:**\n"
        for i, skill in enumerate(workflow['skills'], 1):
            md += f"{i}. `{skill}`\n"
        md += "\n"

        md += "**Execution:**\n"
        md += f"```bash\n"
        md += f"python3 scripts/execute_workflow.py {workflow_id}\n"
        md += "```\n\n"

    md += "## Discovered Chains\n\n"
    md += "Sequential skill chains discovered from direct references.\n\n"

    for chain in chains[:10]:  # Limit to top 10
        md += f"- {' → '.join([f'`{s}`' for s in chain['skills']])}\n"

    md += "\n## Domain Clusters\n\n"
    md += "Skills grouped by shared domains.\n\n"

    for workflow in domain_workflows:
        if len(workflow['skills']) >= 3:
            md += f"### {workflow['domain'].title()}\n\n"
            md += f"**Skills:** {', '.join([f'`{s}`' for s in workflow['skills'][:5]])}\n\n"

    md += "\n## Creating Custom Workflows\n\n"
    md += "Add custom workflows to `WORKFLOW_PATTERNS` in `map_workflows.py`.\n\n"
    md += "```python\n"
    md += '"my-workflow": {\n'
    md += '    "name": "My Custom Workflow",\n'
    md += '    "skills": ["skill-1", "skill-2", "skill-3"],\n'
    md += '    "purpose": "What this workflow accomplishes",\n'
    md += '    "design_language": "Technical/Formal",\n'
    md += "}\n"
    md += "```\n"

    return md

def map_workflows():
    """Main function to map all workflows."""
    print("🗺️  Mapping workflows...")

    data = load_relationships()
    if not data:
        return

    # Discover workflow chains
    chains = discover_workflow_chains(data)
    print(f"   Found {len(chains)} sequential chains")

    # Discover domain workflows
    domain_workflows = discover_domain_workflows(data)
    print(f"   Found {len(domain_workflows)} domain clusters")

    # Generate markdown
    markdown = generate_workflow_markdown(WORKFLOW_PATTERNS, chains, domain_workflows)

    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(markdown)

    print(f"\n✅ Workflows saved to {OUTPUT_FILE}")
    print(f"   {len(WORKFLOW_PATTERNS)} known workflows")
    print(f"   {len(chains)} discovered chains")
    print(f"   {len(domain_workflows)} domain clusters")

if __name__ == "__main__":
    map_workflows()

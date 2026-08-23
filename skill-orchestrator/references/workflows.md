# Skill Workflows

Complete workflows spanning multiple skills.

## Known Workflows

### Content Creation Pipeline

**ID:** `content-creation`

**Purpose:** Research → Write → Distribute content

**Design Language:** Creative/Casual

**Skills:**
1. `honest-deep-researcher`
2. `content-research-writer`
3. `performance-ads-writer`

**Execution:**
```bash
python3 scripts/execute_workflow.py content-creation
```

### E-commerce Product Launch

**ID:** `ecommerce-launch`

**Purpose:** Select product → Create landing page → Launch ads

**Design Language:** Business/Strategic

**Skills:**
1. `cross-border-product-selector`
2. `ecommerce-lp-generator`
3. `performance-ads-writer`

**Execution:**
```bash
python3 scripts/execute_workflow.py ecommerce-launch
```

### WordPress Development Workflow

**ID:** `wordpress-development`

**Purpose:** Audit → Develop → Test → Optimize

**Design Language:** Technical/Formal

**Skills:**
1. `wp-project-triage`
2. `wp-block-development`
3. `wp-phpstan`
4. `wp-performance`

**Execution:**
```bash
python3 scripts/execute_workflow.py wordpress-development
```

### Video Content Production

**ID:** `video-production`

**Purpose:** Research → Plan → Optimize → Design

**Design Language:** Creative/Casual

**Skills:**
1. `youtube-research-video-topic`
2. `youtube-plan-new-video`
3. `youtube-title`
4. `youtube-thumbnail`

**Execution:**
```bash
python3 scripts/execute_workflow.py video-production
```

### Research to NotebookLM Artifacts

**ID:** `research-to-notebooklm`

**Purpose:** Research → Transform to interactive artifacts

**Design Language:** Technical/Formal

**Skills:**
1. `honest-deep-researcher`
2. `media-to-notebooklm-artifacts`

**Execution:**
```bash
python3 scripts/execute_workflow.py research-to-notebooklm
```

## Discovered Chains

Sequential skill chains discovered from direct references.

- `content-research-writer` → `connect`
- `Read-Media-Gemini` → `agentic-vision-gemini`
- `Read-Media-Gemini` → `connect`
- `monetization-first-development` → `ecommerce-landing-page`
- `monetization-first-development` → `opc-twitter`
- `monetization-first-development` → `opc-reddit`
- `monetization-first-development` → `executing-marketing-campaigns`
- `monetization-first-development` → `performance-ads-writer`
- `monetization-first-development` → `prd`
- `monetization-first-development` → `frontend-design`

## Domain Clusters

Skills grouped by shared domains.

### Ecommerce

**Skills:** `content-research-writer`, `planning-with-files`, `monetization-first-development`, `wp-wpcli-and-ops`, `youtube-title`

### Ai

**Skills:** `content-research-writer`, `youtube-thumbnail`, `skill-lookup`, `gemini-watermark-remover`, `Read-Media-Gemini`

### Content

**Skills:** `content-research-writer`, `skill-lookup`, `planning-with-files`, `monetization-first-development`, `wp-wpcli-and-ops`

### Design

**Skills:** `content-research-writer`, `youtube-thumbnail`, `skill-lookup`, `gemini-watermark-remover`, `Read-Media-Gemini`

### Social

**Skills:** `content-research-writer`, `monetization-first-development`, `cross-border-product-selector`, `memory:context-vault`, `stitch-enhance-prompt`

### Research

**Skills:** `content-research-writer`, `skill-lookup`, `Read-Media-Gemini`, `planning-with-files`, `monetization-first-development`

### Pdf

**Skills:** `content-research-writer`, `youtube-thumbnail`, `skill-lookup`, `gemini-watermark-remover`, `planning-with-files`

### Image

**Skills:** `youtube-thumbnail`, `gemini-watermark-remover`, `Read-Media-Gemini`, `planning-with-files`, `monetization-first-development`

### Video

**Skills:** `youtube-thumbnail`, `gemini-watermark-remover`, `Read-Media-Gemini`, `document-skills`, `youtube-title`

### Marketing

**Skills:** `youtube-thumbnail`, `monetization-first-development`, `cross-border-product-selector`, `system-git-discovery-sync`, `memory:context-vault`

### Development

**Skills:** `skill-lookup`, `Read-Media-Gemini`, `planning-with-files`, `monetization-first-development`, `document-skills`

### Business

**Skills:** `planning-with-files`, `my-creative-writer`, `cross-border-product-selector`, `youtube-research-video-topic`, `claude-cli-guide`

### Wordpress

**Skills:** `wp-wpcli-and-ops`, `wpds`, `wp-block-themes`, `wp-project-triage`, `wp-block-development`

### Notion

**Skills:** `videocut`, `postgres-patterns`, `ecommerce-landing-page`, `coding-standards`, `eval-harness`


## Creating Custom Workflows

Add custom workflows to `WORKFLOW_PATTERNS` in `map_workflows.py`.

```python
"my-workflow": {
    "name": "My Custom Workflow",
    "skills": ["skill-1", "skill-2", "skill-3"],
    "purpose": "What this workflow accomplishes",
    "design_language": "Technical/Formal",
}
```

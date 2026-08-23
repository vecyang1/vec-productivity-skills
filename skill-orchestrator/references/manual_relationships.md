# Manual Skill Relationships

This document tracks manually registered skill relationships that aren't auto-discovered by the relationship discovery system.

## Registered: 2026-03-04

### Content Creation → Distribution Workflow

**knowledge-card-generator ↔ creator-monetization-engine** (bidirectional workflow)
- knowledge-card-generator creates visual content that creator-monetization-engine distributes across platforms
- Bidirectional: both skills reference each other in their workflows

**knowledge-card-generator → visual-prompt-engineer-patten** (dependency)
- knowledge-card-generator uses visual-prompt-engineer to generate optimized prompts for image generation

**creator-monetization-engine → visual-prompt-engineer-patten** (workflow)
- creator-monetization-engine leverages visual-prompt-engineer for platform-specific content optimization

### Image Ratio Fallback Handlers

**knowledge-card-generator → Nano-Banana** (fallback)
- **Condition**: `ratio_mismatch`
- **Description**: When knowledge-card-generator produces images with non-ideal ratios, Nano-Banana can regenerate or resize to platform-specific dimensions
- **Examples**: 3:4 for Xiaohongshu, 16:9 for YouTube, 1:1 for Instagram

**creator-monetization-engine → Nano-Banana** (fallback)
- **Condition**: `platform_ratio_required`
- **Description**: When creator-monetization-engine needs platform-fit images, Nano-Banana handles ratio conversion and regeneration

## Platform-Specific Ratios

| Platform | Recommended Ratio | Dimensions | Use Case |
|----------|------------------|------------|----------|
| Xiaohongshu (小红书) | 3:4 (vertical) | 1080 x 1440 px | Feed posts, maximum visibility |
| YouTube | 16:9 (horizontal) | 1920 x 1080 px | Video thumbnails |
| Instagram Feed | 1:1 (square) | 1080 x 1080 px | Standard posts |
| Instagram Stories | 9:16 (vertical) | 1080 x 1920 px | Full-screen stories |
| Twitter/X | 16:9 (horizontal) | 1200 x 675 px | Timeline posts |
| LinkedIn | 1.91:1 (horizontal) | 1200 x 627 px | Shared links |

## Usage

To register new manual relationships:

```bash
python3 scripts/register_manual_relationships.py
```

To query relationships:

```bash
python3 scripts/query_relationships.py <skill-name>
```

To view relationships directly from JSON:

```bash
cd references
python3 -c "import json; data = json.load(open('skill_relationships.json')); print(json.dumps(data.get('<skill-name>', {}), indent=2))"
```

## Notes

- Manual relationships are marked with `"manual": true` in the JSON
- Fallback handlers are stored in a separate `fallback_handlers` array
- Conditions are optional metadata that describe when the fallback should trigger
- Bidirectional relationships create reverse entries automatically

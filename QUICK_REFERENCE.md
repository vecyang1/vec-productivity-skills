# Vec's Claude Skills - Quick Reference

## 📦 Repository
**Main Repo**: https://github.com/vecyang1/vec-claude-skills

## 🎯 Included Skills

### 1. Agent Teams Dashboard
- **Path**: `agent-teams-dashboard/`
- **Type**: Management & Coordination
- **MCP**: ✅ Yes
- **Use**: Team monitoring, task distribution, performance analytics

### 2. Skill Improver
- **Path**: `skill-improver/`
- **Type**: Meta-skill
- **MCP**: ❌ No
- **Use**: Skill quality assessment, optimization, documentation

### 3. Notion MCP Connector
- **Path**: `notion-mcp-connector/`
- **Type**: Integration
- **MCP**: ✅ Yes (Enhanced + Local)
- **Use**: Notion automation, database management, workflows

## 🚀 Installation

```bash
# Clone the unified collection
git clone https://github.com/vecyang1/vec-claude-skills.git ~/vec-claude-skills

# Install all skills
ln -s ~/vec-claude-skills/* ~/.claude/skills/

# Or install individual skills
ln -s ~/vec-claude-skills/notion-mcp-connector ~/.claude/skills/notion-mcp-connector
```

## 📝 Local Setup

Your current setup:
- **Unified Collection**: `~/Documents/Shared/vec-claude-skills/`
- **Symlinks**: `~/.claude/skills/` → points to unified collection
- **Original Skills**: `~/.gemini/antigravity/skills/` (keep as backup)

## 🔄 Updates

```bash
cd ~/Documents/Shared/vec-claude-skills
git pull origin main
```

## 🌐 Public URLs

- **Main Collection**: https://github.com/vecyang1/vec-claude-skills
- **Agent Teams**: https://github.com/vecyang1/agent-teams-dashboard (standalone)
- **Skill Improver**: https://github.com/vecyang1/skill-improver (standalone)
- **Notion Connector**: https://github.com/vecyang1/notion-mcp-connector (deprecated, redirects to collection)

## ✅ Migration Complete

All three skills are now unified in one repository with:
- Consistent structure and documentation
- Easy installation and updates
- Community-ready with proper licensing
- Deprecation notices on old repos

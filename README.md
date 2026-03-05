# Vec's Productivity Skills

A curated collection of production-ready productivity skills for Claude Code, created and maintained by [Vec Yang](https://github.com/vecyang1).

## 🎯 Skills Included

### 1. [Agent Teams Dashboard](./agent-teams-dashboard/)
Comprehensive dashboard and management system for Claude Code Agent Teams.

**Features:**
- Real-time team monitoring and coordination
- Task distribution and progress tracking
- Performance analytics and insights
- Team composition analysis

**Use Cases:**
- Managing multiple parallel agents
- Complex multi-step workflows
- Collaborative AI development

[📖 Full Documentation](./agent-teams-dashboard/README.md)

---

### 2. [Skill Improver](./skill-improver/)
Meta-skill for auditing, improving, and optimizing Claude Code skills.

**Features:**
- Automated skill quality assessment
- Best practices validation
- Performance optimization suggestions
- Documentation enhancement

**Use Cases:**
- Skill development and refinement
- Quality assurance for custom skills
- Skill maintenance and updates

[📖 Full Documentation](./skill-improver/README.md)

---

### 3. [Notion MCP Connector](./notion-mcp-connector/)
Comprehensive Notion integration via Model Context Protocol (MCP) and Direct API.

**Features:**
- Enhanced MCP support with semantic search
- CLI tools for bulk operations
- Local MCP server with domain helpers
- Rich property handling and templates

**Use Cases:**
- Notion workspace automation
- Database management and queries
- Content synchronization
- Workflow automation

[📖 Full Documentation](./notion-mcp-connector/README.md)

---

## 🚀 Quick Start

### Installation

#### Option 1: Install All Skills
```bash
# Clone the repository
git clone https://github.com/vecyang1/vec-productivity-skills.git

# Symlink to Claude skills directory
ln -s $(pwd)/vec-productivity-skills/* ~/.claude/skills/
```

#### Option 2: Install Individual Skills
```bash
# Clone the repository
git clone https://github.com/vecyang1/vec-productivity-skills.git

# Symlink specific skill
ln -s $(pwd)/vec-productivity-skills/notion-mcp-connector ~/.claude/skills/notion-mcp-connector
```

### Usage

Each skill can be invoked in Claude Code:
- Via skill name reference in prompts
- Through MCP tools (if applicable)
- Using CLI scripts directly

See individual skill documentation for detailed usage instructions.

---

## 📋 Requirements

- **Claude Code**: Latest version recommended
- **Python**: 3.8+ (for Python-based skills)
- **Node.js**: 16+ (for Node-based skills)
- **Dependencies**: See individual skill requirements

---

## 🛠️ Development

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Skill Structure

Each skill follows this structure:
```
skill-name/
├── SKILL.md          # Main skill documentation
├── README.md         # Detailed usage guide
├── scripts/          # Executable scripts
├── references/       # Reference documentation
└── .mcp.json        # MCP configuration (if applicable)
```

---

## 📚 Resources

- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Skill Development Guide](https://docs.anthropic.com/claude/docs/skills)

---

## 🤝 Community

- **Author**: [Vec Yang](https://github.com/vecyang1)
- **Issues**: [GitHub Issues](https://github.com/vecyang1/vec-productivity-skills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vecyang1/vec-productivity-skills/discussions)

---

## 📄 License

MIT License - see individual skill directories for specific license information.

---

## 🌟 Acknowledgments

Built for the Claude Code community. Special thanks to:
- Anthropic for Claude Code and enhanced MCPs
- The open-source community for inspiration and feedback

---

## 📊 Skill Comparison

| Skill | Type | Complexity | Dependencies | MCP Support |
|-------|------|------------|--------------|-------------|
| Agent Teams Dashboard | Management | Medium | Python | ✅ |
| Skill Improver | Meta | Low | Python | ❌ |
| Notion MCP Connector | Integration | Medium | Python, requests | ✅ |

---

## 🔄 Updates

Check [CHANGELOG.md](./CHANGELOG.md) for version history and updates.

**Latest Version**: 1.0.0 (2026-03-05)

---

## 💡 Tips

- Start with individual skills to understand their capabilities
- Combine skills for powerful workflows (e.g., Agent Teams + Notion for project management)
- Customize skills for your specific use cases
- Share your improvements back to the community

---

**Happy Coding! 🚀**

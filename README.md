# Vec's Productivity Skills

A curated collection of production-ready productivity skills for Claude Code, created and maintained by [Vec Yang](https://github.com/vecyang1).

## 🎯 Skills Included

### 1. [Skill Improver](./skill-improver/)
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

### 2. [Notion MCP Connector](./notion-mcp-connector/)
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

### 3. [Post Social Media with Zernio API](./post-social-media-with-zernio-api/)
Privacy-safe, direct Zernio publishing with exact destinations, dry runs, and
idempotent request receipts.

**Features:**
- Read-only exact-account preflight
- Caption-preserving dry-run payload review
- Explicit-confirmation publishing with `x-request-id`
- Built-in public-release privacy scanner

**Use Cases:**
- Publishing an approved post to one or more named social accounts
- Safely retrying an uncertain post request without creating duplicates

[📖 Full Documentation](./post-social-media-with-zernio-api/README.md)

---

### 4. [YouTube Channel Scraper](./youtube-channel-scraper/)
High-performance scraper for extracting all video metadata from a YouTube channel.

**Features:**
- Blazing fast playlist parsing (~15 seconds for 500+ videos)
- Extracts views, durations, upload dates, and URLs
- Auto-generates summary statistics and CSV files
- Perfect for creator research and monetization analysis

**Use Cases:**
- Scraping competitor channels
- Bulk evaluating video performance

[📖 Full Documentation](./youtube-channel-scraper/README.md)

---

### 5. [Video Downloader](./video-downloader/)
Reliable batch downloading utility and skill for YouTube videos and audio.

**Features:**
- Parallel worker batch downloading from CSV
- Android bypass for HTTP 403 blocks
- Customizable formats (MP3 audio, MP4 video up to 4K)
- Fault-tolerant retries and continuation archives

**Use Cases:**
- Archiving channels for offline research
- Bulk extracting MP3s for background processing

[📖 Full Documentation](./video-downloader/SKILL.md)

---

### 6. [Scheduled Task Rescheduler](./scheduled-task-rescheduler/)
Safely reschedule, rename, rebuild, split, or merge recurring agent tasks without losing state — across Antigravity, Codex, Claude Code, LaunchAgent, cron, and n8n.

**Features:**
- Lineage-preserving reschedules (rename, new-ID, split, merge, runtime swap)
- Incremental-by-default loop with checkpoints and success markers
- Antigravity two-layer config activation with a verification gate
- Deliberate catch-up and midnight-credit policy
- Zero-dependency cadence-card validator

**Use Cases:**
- Moving a nightly job to a new time without orphaning its checkpoint
- Activating Antigravity scheduled tasks via direct config editing
- Deciding whether a missed run should catch up or be skipped

[📖 Full Documentation](./scheduled-task-rescheduler/README.md)

---

### 7. [Feishu / Lark CLI Operator](./feishu-lark-cli/)
Route Feishu/Lark work through the official `lark-cli` — Docs, Drive, Base, Sheets, Wiki — and diagnose custom Base Block errors as the tenant-identity problems they usually are.

**Features:**
- User vs. bot identity baselines, including the `--no-wait` / `--device-code` login flow for agent harnesses
- Intent → command routing paired with the CLI's embedded, version-matched guides
- High-risk-write contract: exit `10` + `confirmation_required` means ask, never auto-`--yes`
- Dry-run diff technique for telling honoured flags from silently ignored ones
- Version-independent wrapper for when a Node upgrade breaks the global shim

**Use Cases:**
- Searching and editing Feishu Docs safely from the command line
- Resolving `internal features of other enterprises` without re-releasing a Block
- Keeping `lark-cli` working across Node and package-manager upgrades

[📖 Full Documentation](./feishu-lark-cli/README.md)

---

### 8. [Squirrly SEO Operations](./squirrly-ops/)
A multi-brand CLI over the Squirrly SEO cloud API — built by reading the vendor's WordPress plugin source, because **Squirrly publishes no API documentation**. The endpoint map here may be the only written description of this interface.

**Features:**
- 76 endpoint/verb pairs documented with parameters, response shape and risk
- Brand registry holding *pointers* to credentials, never credentials; `env://` or 1Password Service Account
- Writes behind two independent locks, because the quota is metered and real
- Entitlement-blocked endpoints stay listed with a `gate` and a reason, so "my plan cannot" never gets misread as "this API cannot"
- 105 hermetic unit tests plus a red-capable 10-stage live e2e check

**Use Cases:**
- Reading SEO health checks, keyword briefcase, focus pages and AI-visibility across several brands
- Auditing what a WordPress SEO plugin is actually emitting on live pages
- Any undocumented-vendor-API project — the gotchas section is largely transferable

[📖 Full Documentation](./squirrly-ops/SKILL.md)

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

**AGPL-3.0-or-later** — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).

Use it, modify it, run it. If you distribute a modified version — or offer one
to users over a network — publish your source under the same terms.

Three subdirectories carry their own LICENSE file and are **not** covered by the
above: `skill-creator/` (Apache-2.0, third-party), `skill-improver/` (MIT,
third-party), and `notion-mcp-connector/` (MIT, retained deliberately). Keep
each LICENSE with its directory if you redistribute.

> This repository was MIT-licensed until 2026-08-17. Copies taken before that
> date keep their MIT grant; it is not revoked.

---

## 🌟 Acknowledgments

Built for the Claude Code community. Special thanks to:
- Anthropic for Claude Code and enhanced MCPs
- The open-source community for inspiration and feedback

---

## 📊 Skill Comparison

| Skill | Type | Complexity | Dependencies | MCP Support |
|-------|------|------------|--------------|-------------|
| Skill Improver | Meta | Low | Python | ❌ |
| Notion MCP Connector | Integration | Medium | Python, requests | ✅ |
| Zernio Social Publishing | Integration | Low | Python (stdlib only) | ❌ |
| YouTube Channel Scraper | Data Extraction | Low | Python, yt-dlp | ❌ |
| Video Downloader | Utility | Medium | Python, yt-dlp | ❌ |
| Scheduled Task Rescheduler | Workflow | Low | Python (stdlib only) | ❌ |
| Feishu / Lark CLI Operator | Integration | Low | Node.js 18+, `@larksuite/cli` | ❌ |
| Squirrly SEO Operations | Integration | Medium | Python (stdlib only) | ❌ |

---

## 🔄 Updates

Check [CHANGELOG.md](./CHANGELOG.md) for version history and updates.

**Latest Version**: 1.1.0 (2026-06-19)

---

## 💡 Tips

- Start with individual skills to understand their capabilities
- Combine skills for powerful workflows (e.g., Squirrly audits feeding a content pipeline)
- Customize skills for your specific use cases
- Share your improvements back to the community

---

**Happy Coding! 🚀**

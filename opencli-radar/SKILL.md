---
name: opencli-radar
description: Multi-source ecosystem radar and diagnostic-first audit tool for OpenCLI. Discovers community plugins, parses licenses (AGPL vs MIT vs Proprietary), verifies installation safety (--ignore-scripts), and prevents redundant adapter development. Use when searching for OpenCLI plugins, checking if a website has an existing CLI adapter, auditing community plugins, or running ecosystem census.
---

# OpenCLI Ecosystem Radar & Diagnostic Engine

## Skill Metadata

- **Origin:** `community`
- **Source:** `vecyang1/vec-productivity-skills/opencli-radar`
- **Author:** Vec Yang
- **Created:** 2026-10-08
- **Updated:** 2026-10-08
- **Review status:** `reviewed`

## Purpose & Operating Philosophy

OpenCLI is an extensible host platform for turning any browser-based web application into a typed command-line interface. While the official `jackwener/OpenCLI-Hub` registry lists only a handful of plugins (~3), over **199+ community plugins and adapters** exist across GitHub and npm.

This skill provides a **Diagnostic-First** radar engine to inspect, triage, and audit the entire OpenCLI ecosystem before writing custom code.

### Core Invariants

1. **Anti-Fragmentation ("不要分散地制造轮子")**:
   - Always search before authoring. Prioritize: `reuse local -> install community -> fork & vendor -> build new`.
   - Never write a one-off adapter if an active, licensed community plugin already solves the problem.
2. **Diagnostic-First ("对账器优先")**:
   - Do not just say whether a plugin exists. Output a structured, verifiable diagnostic report showing:
     - Matched source (Local built-in, Local custom in `~/.opencli/clis/`, GitHub convention, NPM).
     - License classification (AGPL-3.0, MIT, Apache-2.0, or Unlicensed All Rights Reserved).
     - Maintenance health (days since last push, star count).
     - Exact actionable command to execute.
3. **Completeness & Anti-Truncation ("分页防截断")**:
   - Official hub tables capture only **~1.5%** of all existing plugins.
   - The radar queries GitHub REST API across `opencli-plugin in:name`, `opencli-adapter in:name`, and high-star repos with complete pagination traversal and deduplication.

---

## Command Reference

The radar engine is packaged in `scripts/opencli_radar.py` (and exposed via the global `opencli-radar` CLI):

### 1. Site Diagnosis (`diagnose`)

Diagnose whether a target website or URL is supported, how it is supported, and what to do next:

```bash
# Diagnose by domain URL
python3 scripts/opencli_radar.py diagnose https://x.com

# Diagnose by platform slug or alias
python3 scripts/opencli_radar.py diagnose goofish
python3 scripts/opencli_radar.py diagnose claspo
python3 scripts/opencli_radar.py diagnose clarity

# Machine-readable JSON output
python3 scripts/opencli_radar.py diagnose github.com --json
```

#### Diagnostic Verdicts & Actions

| Verdict | Condition | Actionable Command | Rationale |
| :--- | :--- | :--- | :--- |
| **`REUSE_LOCAL`** | Found in local OpenCLI built-in or `~/.opencli/clis/` | `opencli <site> <command>` | Already operational locally. Zero installation needed. |
| **`INSTALL`** | Active open-source licensed repository found | `opencli plugin install github:<owner>/<repo>` | Maintained community plugin with compliant OSS license. |
| **`FORK_AND_VENDOR`** | Open-source licensed, but dormant (>1 yr, <5★) | `git clone <repo_url> ~/.opencli/clis/<site>` | Safe to vendor locally to avoid upstream dependency rot. |
| **`READ_ONLY`** | Unlicensed (All Rights Reserved) or non-standard | `opencli browser init <site>/<cmd>` *(prior art only)* | Use as architectural reference only; do NOT vendor or fork directly. |
| **`BUILD_NEW`** | No local or community adapter found | `opencli browser init <site>/<cmd>` | Safe to scaffold a brand-new adapter. |

---

### 2. Community Search (`query`)

Search community plugins by keyword or partial name:

```bash
# Search for video, social, or ecommerce plugins
python3 scripts/opencli_radar.py query weixin
python3 scripts/opencli_radar.py query douyin
python3 scripts/opencli_radar.py query shopify
```

---

### 3. Full Ecosystem Census (`census` / `scan`)

Run a comprehensive statistical audit across local, GitHub, and npm sources:

```bash
# Read cached census (1-hour TTL)
python3 scripts/opencli_radar.py census

# Force a live crawl across GitHub search API and NPM
python3 scripts/opencli_radar.py census --fresh
```

#### Measured Census Metrics

- **Total Ingested Repos**: 199 unique community repositories.
- **Official Hub Listed**: 3 plugins (capture rate: ~1.5%).
- **Open-Source Licensed**: ~44.7% (MIT, Apache-2.0, AGPL-3.0, GPL).
- **Unlicensed (All Rights Reserved)**: ~55.3% (requires clean-room reverse engineering or authorization).

---

## Security Boundaries & Safe Installation

> [!WARNING]
> OpenCLI plugins run in-process with access to the user's active Chrome browser session and cookies. Always apply security verification before installing untrusted community code.

1. **Supply Chain Defense (`--ignore-scripts`)**:
   - Community npm or git packages may define malicious `postinstall` or `preinstall` hooks.
   - When installing third-party plugins, always specify `--ignore-scripts` or inspect `package.json` scripts beforehand.
2. **Network Egress Audit**:
   - Before executing a newly installed community plugin, scan for unexpected telemetry or credential exfiltration:
     ```bash
     rg "fetch\(|axios|http\.request|webhook" ~/.opencli/clis/<plugin>/
     ```
3. **Session Cookie Isolation**:
   - Do not run unverified community plugins against browser profiles containing sensitive banking or primary enterprise accounts. Default to isolated agent profiles (e.g. Chrome Profile 2).

---

## Cross-Skill Ecosystem Navigation

`opencli-radar` functions as an integral part of the OpenCLI development and execution toolchain:

| Skill | Role | When to Use |
| :--- | :--- | :--- |
| **`opencli-radar`** *(This Skill)* | Ecosystem Discovery & License Triage | Checking if an adapter exists before writing code; auditing licenses |
| **`opencli-usage`** | Daily Execution & Command Guide | Running existing commands on supported platforms (188+ sites) |
| **`opencli-adapter-author`** | Adapter Development & Scaffolding | Writing new adapters when `opencli-radar` returns `BUILD_NEW` |
| **`wheel-check`** | Workspace-Wide Duplicate Prevention | Top-level routing before building any local CLI, script, or tool |

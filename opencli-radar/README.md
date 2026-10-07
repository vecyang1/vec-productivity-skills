# OpenCLI Radar 🎯

Multi-source ecosystem radar, pagination verifier, and diagnostic-first audit tool for the OpenCLI plugin ecosystem.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenCLI Ecosystem](https://img.shields.io/badge/OpenCLI-199%2B%20Plugins-orange.svg)](https://github.com/jackwener/OpenCLI)

---

## Why OpenCLI Radar?

While the official OpenCLI registry lists only a few plugins, over **199+ community plugins and adapters** exist across GitHub and npm. Developers frequently reinvent adapters from scratch because they cannot find existing community work, or they unknowingly install unlicensed / unmaintained plugins.

**OpenCLI Radar** solves this with a **Diagnostic-First** engine:
1. **Multi-Source Discovery**: Simultaneously searches local estate, GitHub repositories (`opencli-plugin-*`, `opencli-adapter-*`, high-star repos), official Hub, and npm registry.
2. **License & Risk Triage**: Automatically parses repository licenses (MIT, Apache, AGPL vs. Unlicensed All Rights Reserved) and maintenance activity.
3. **Actionable Verdicts**: Tells you exactly whether to reuse local, install community, fork and vendor, or build from scratch.
4. **Supply Chain Defense**: Warns about in-process browser risks and enforces safe installation flags (`--ignore-scripts`).

---

## Quick Start

### 1. Diagnose a Target Site or URL

Check whether an adapter already exists for any platform:

```bash
# By domain URL
python3 scripts/opencli_radar.py diagnose https://x.com

# By platform slug or alias
python3 scripts/opencli_radar.py diagnose goofish
python3 scripts/opencli_radar.py diagnose claspo
python3 scripts/opencli_radar.py diagnose github.com

# Machine-readable JSON
python3 scripts/opencli_radar.py diagnose twitter --json
```

### 2. Search Community Plugins

Search the ingested ecosystem by keyword:

```bash
python3 scripts/opencli_radar.py query weixin
python3 scripts/opencli_radar.py query douyin
```

### 3. Run Live Ecosystem Census

Inspect full ecosystem statistics across GitHub and npm:

```bash
python3 scripts/opencli_radar.py census
```

---

## Verdict Reference

| Verdict | Meaning | Actionable Output |
| :--- | :--- | :--- |
| **`REUSE_LOCAL`** | Already installed in your local OpenCLI setup | `opencli <site> <command>` |
| **`INSTALL`** | Active, open-source licensed community plugin | `opencli plugin install github:<repo>` |
| **`FORK_AND_VENDOR`** | Open-source licensed, but inactive (>1 year) | `git clone <repo> ~/.opencli/clis/<site>` |
| **`READ_ONLY`** | Unlicensed (All Rights Reserved) | Prior art reference only; do not vendor directly |
| **`BUILD_NEW`** | No local or community adapter found | `opencli browser init <site>/<cmd>` |

---

## Running Tests

```bash
python3 tests/test_opencli_radar.py
```

---

## License

This project is licensed under the [GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)](../../LICENSE).

# Feishu / Lark CLI Operator

A routing and safety skill for driving [Feishu / Lark](https://www.larksuite.com/)
through the official `lark-cli`. It covers Docs, Drive, Base, Sheets, Wiki, and
Markdown surfaces, and it takes a firm position on the one class of problem
that wastes the most time: custom Base Block errors that look like build
failures and are actually tenant-identity failures.

## Install

```bash
git clone https://github.com/vecyang1/vec-productivity-skills.git
ln -s "$(pwd)/vec-productivity-skills/feishu-lark-cli" \
  ~/.claude/skills/feishu-lark-cli
```

Then install the CLI itself:

```bash
npm install -g @larksuite/cli
lark-cli doctor
```

Requires Node.js 18+. No Python, no other dependencies.

## What is included

- Auth baselines for user vs. bot identity, including the `--no-wait` /
  `--device-code` flow for agent harnesses that cannot block on a browser.
- A routing table from user intent to command family, paired with the CLI's
  **embedded, version-matched** guides (`lark-cli skills read lark-doc`), which
  outrank any local copy when they disagree.
- The high-risk-write contract: exit `10` plus a `confirmation_required`
  envelope means stop and ask, never auto-retry with `--yes`.
- A worked example of a flag that parses but does nothing (`--api-version`),
  and the dry-run diff technique that tells honoured flags from ignored ones.
- Output-handling rules — `--dry-run` payloads embed `app_id` and
  `user_open_id`, so they are not safe to paste into public issues verbatim.
- A version-independent `lark-cli` wrapper for when a Node upgrade breaks the
  global shim, resolving npm's `npx-cli.js` through the active Node rather than
  a hardcoded install path.

See [SKILL.md](SKILL.md) for the operational contract and
[references/troubleshooting.md](references/troubleshooting.md) for recovery paths.

## Scope

This skill routes *away* from itself where appropriate. Releasing a custom Base
record-view extension is a `@lark-opdev/cli` lifecycle owned by that
extension's own project; `lark-cli base` is for targeting and readback only.

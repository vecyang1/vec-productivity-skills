# Post Social Media with Zernio API

A compact, privacy-safe skill for directly publishing an explicitly approved
social post through [Zernio](https://zernio.com/). It uses only the Python
standard library and defaults to read-only or dry-run actions.

## Install

```bash
git clone https://github.com/vecyang1/vec-productivity-skills.git
ln -s "$(pwd)/vec-productivity-skills/post-social-media-with-zernio-api" \
  ~/.claude/skills/post-social-media-with-zernio-api
```

Set `ZERNIO_API_KEY` in the environment supplied by your secret manager. Do
not commit an `.env` file or pass a key as a command-line argument.

## What is included

- Exact-account, read-only connection verification
- Dry-run payload construction that preserves the approved caption
- Explicit-confirmation immediate publishing with `x-request-id` receipts
- A scanner that checks the package working tree and reachable Git history for
  credentials, local paths, personal email addresses, and concrete account IDs

See [SKILL.md](SKILL.md) for the operational contract and commands.

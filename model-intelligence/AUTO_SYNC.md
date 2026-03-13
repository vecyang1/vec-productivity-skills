# Model Intelligence Auto-Sync Setup

## Daily Automation

The system auto-syncs models daily from:
- **Artificial Analysis API**: Intelligence metrics, performance, pricing (primary source)

## Setup Cron Job

```bash
# Add to crontab (runs twice daily at 9 AM and 9 PM)
crontab -e

# Add this line:
0 9,21 * * * ~/.claude/skills/model-intelligence/scripts/daily_sync.sh
```

## Logs

Sync logs are stored in:
```
/Users/vecsatfoxmailcom/Documents/A-coding/latest-ai-model-sync/model-sync-YYYYMMDD-HHMM.log
```

## What Gets Updated

1. **Registry** (`references/model_registry.json`):
   - Context windows, max output tokens
   - Pricing (input/output per 1M tokens)
   - Model availability

2. **Memory** (`~/.claude/projects/-Users-vecsatfoxmailcom/memory/MEMORY.md`):
   - Last updated timestamp
   - Top agent model rankings

## API Key Setup

Create `.env` file:
```bash
echo "AA_API_KEY=aa_ktumuYkNLMYvZdymJrpbvKsJvhYMOrTP" > ~/.claude/skills/model-intelligence/.env
```

## Logs

Check sync logs:
```bash
tail -f /tmp/model-sync.log
```

## Current Status

- **LiteLLM**: ✓ Working (668 models)
- **AA API**: ✓ Working (419 models, benchmarks)
- **GDPval-AA**: Manual update (cached in registry)
- **Last sync**: 2026-03-04

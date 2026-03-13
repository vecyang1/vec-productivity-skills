#!/bin/bash
# Twice-daily model sync from Artificial Analysis API
# Add to crontab:
# 0 9,21 * * * ~/.claude/skills/model-intelligence/scripts/daily_sync.sh

SYNC_DIR="/Users/vecsatfoxmailcom/Documents/A-coding/latest-ai-model-sync"
LOG_FILE="$SYNC_DIR/model-sync-$(date +%Y%m%d-%H%M).log"

cd ~/.claude/skills/model-intelligence
python3 scripts/sync_from_aa.py > "$LOG_FILE" 2>&1

#!/bin/bash
# Weekly model reference scanner
# Add to crontab: 0 9 * * 1 ~/.gemini/antigravity/skills/skill-orchestrator/scripts/schedule_model_scan.sh

SCRIPT_DIR="$HOME/.gemini/antigravity/skills/skill-orchestrator/scripts"
LOG_DIR="$HOME/.gemini/antigravity/skills/skill-orchestrator/references"

# Run scan and log
python3 "$SCRIPT_DIR/scan_model_references.py" 2>&1 | tee "$LOG_DIR/model_scan_$(date +%Y%m%d_%H%M%S).log"

# Keep only last 10 logs
cd "$LOG_DIR" && ls -t model_scan_*.log | tail -n +11 | xargs -r rm

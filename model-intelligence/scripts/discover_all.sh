#!/bin/bash
# Unified model discovery - shows all providers

echo "════════════════════════════════════════════════════════════"
echo "CLAUDE MODELS"
echo "════════════════════════════════════════════════════════════"
python3 ~/.claude/skills/model-intelligence/scripts/discover_claude.py
echo ""

echo "════════════════════════════════════════════════════════════"
echo "OPENAI MODELS (Latest)"
echo "════════════════════════════════════════════════════════════"
python3 ~/.claude/skills/model-intelligence/scripts/discover_openai.py 2>/dev/null
echo ""

python3 ~/.claude/skills/model-intelligence/scripts/discover_gemini_all.py

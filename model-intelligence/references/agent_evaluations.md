# Agent Performance Evaluations

## Overview
Tracks AI model performance on real-world productivity and agent tasks.

## Evaluation Sources

### GDPval-AA (Artificial Analysis)
- **URL**: https://artificialanalysis.ai/evaluations/gdpval-aa
- **Metric**: ELO score (higher = better)
- **Tests**: Real-world tasks across 44 occupations, 9 industries
- **Capabilities**: Shell access, web browsing, agentic loop
- **API**: https://artificialanalysis.ai/api/v2/data/llms/models (requires free API key)
- **Rate limit**: 1,000 requests/day

### Vending-Bench 2 (Andon Labs)
- **URL**: https://andonlabs.com/evals/vending-bench-2
- **Metric**: Money balance after 1 year (higher = better)
- **Tests**: Long-horizon agent task (vending machine business simulation)
- **Scale**: 3,000-6,000 messages, 60-100M tokens per run
- **Evaluates**: Supplier negotiation, supply chain management, financial optimization

## Current Top Performers (2026-03-04)

| Rank | Model | GDPval ELO | Vending Balance | Best For |
|------|-------|------------|-----------------|----------|
| 1 | Claude Sonnet 4.6 | 1633 | $7,204 | Productivity, cost-performance |
| 2 | Claude Opus 4.6 | 1606 | $8,018 | Long-horizon, complex reasoning |
| 3 | GPT-5.3 Codex | 1462 | $5,940 | Coding, technical workflows |
| 4 | GPT-5.2 | 1462 | - | General productivity |
| 5 | Gemini 3.1 Pro | - | $5,478 | Negotiation, persistence |

## Key Insights

**Claude 4.6 dominance**: Anthropic models occupy top positions on both benchmarks
**Cost-performance**: Claude Sonnet 4.6 offers best balance (#1 ELO, competitive balance)
**Long-horizon**: Claude Opus 4.6 maintains coherence over 60-100M tokens
**Negotiation**: Gemini 3 Pro excels as "persistent negotiator"

## CLI Tools

```bash
# Fetch latest GDPval-AA rankings
python3 scripts/fetch_gdpval.py

# Query agent-capable models
python3 scripts/query_models.py --agent-capable

# Auto-update registry and memory
python3 scripts/auto_update_models.py
```

## API Setup (Optional)

Get free API key from Artificial Analysis:
1. Create account at https://artificialanalysis.ai
2. Generate API key from dashboard
3. Export: `export AA_API_KEY="your_key"`
4. Run: `python3 scripts/fetch_gdpval.py`

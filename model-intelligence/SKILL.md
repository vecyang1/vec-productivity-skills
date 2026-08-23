---
name: model-intelligence
description: Comprehensive model selection, benchmarking, and recommendation system. Provides up-to-date information on AI models with human-judged quality (Arena.ai), automated benchmarks (Vals AI, AA API), and weighted scoring across use cases. Use for model recommendations, benchmark queries, and latest model data.
---

# Model Intelligence

Stay current with AI models through multiple data sources: human-judged quality (Arena.ai), automated benchmarks (Vals AI, APEX-Agents, GDPval-AA), and comprehensive categorization by capability and domain.

## Core Purpose: Accurate Model Names

**CRITICAL**: Agent knowledge is always behind. This skill's PRIMARY role is providing current, accurate model names for API calls and configurations.

### Current Model Names (as of 2026-03-13)

**OpenAI:**
- Latest: `gpt-5.4` (released 2026-03-06)
- Coding: `gpt-5.3-codex`
- Flagship: `gpt-5.2`
- Budget: `gpt-5-mini`, `gpt-5-nano`
- Reasoning: `o3`, `o3-mini`

**Anthropic:**
- Latest: `claude-opus-4-6`, `claude-sonnet-4-6`
- Budget: `claude-haiku-4-5-20251001`
- ⚠️ Deprecated: `claude-3-5-*` series (use 4-6 instead)
- ⚠️ Old naming: `claude-opus-4-6-20250219` (use simple name without date)

**Google Gemini:**
- Latest Pro: `gemini-3.1-pro-preview`
- Latest Flash: `gemini-3-flash-preview`
- Image Gen: `gemini-3.1-flash-image-preview` (Nano Banana 2)
- ⚠️ Retiring: `gemini-2.0-flash` (March 31, 2026)

**Zhipu AI (智谱):**
- Latest: `glm-5` (tested 2026-03-13)
- Budget: `glm-4-flash`
- ⚠️ Concurrency: ≤6 agents recommended (see benchmarks)

**Before using ANY model name:**
```bash
python3 scripts/check_freshness.py
# If stale → run discover_new_models.py (auto-scrapes vals.ai)
```

**Auto-Discovery (Daily via Cron):**
```bash
python3 scripts/discover_new_models.py
# Scrapes vals.ai/models for top 5 latest from each provider
# Updates registry + memory automatically
```

**Direct API Queries (Standardized):**
All discovery scripts merge API data with local registry for complete information.

```bash
# Gemini models
python3 scripts/discover_gemini_all.py          # List all (categorized)
python3 scripts/discover_gemini_all.py --model gemini-3-flash-preview
# Alias: gg

# OpenAI models
python3 scripts/discover_openai.py              # List all GPT models
python3 scripts/discover_openai.py --model gpt-5.4-pro
# Alias: oo

# Claude models
python3 scripts/discover_claude.py              # List all Claude models
python3 scripts/discover_claude.py --model claude-opus-4-6
# Alias: cc
```

**Output includes:** context_window, max_output, vision, tier, release_date, knowledge_cutoff, cost, agent_performance (where available)

## Quick Start

```bash
# Get model recommendation
python3 scripts/recommend_model.py --purpose "coding"
python3 scripts/recommend_model.py --industry "finance"

# Query benchmarks
python3 scripts/query_benchmarks.py --use-case "coding"
python3 scripts/query_arena.py --category text --top 5

# Check freshness
python3 scripts/check_freshness.py
```

## Workflow Diagram

```
USER QUERY: "Best model for [use case]?"
           ↓
    recommend_model.py
           ↓
    ┌──────┴──────┐
    ↓             ↓
Purpose Map   Industry Map
    └──────┬──────┘
           ↓
    DATA SOURCES (by freshness)
    ├─ Arena.ai (Real-time, Human ELO)
    ├─ Vals AI (Hours, WebFetch)
    ├─ AA API (Days, Stable)
    └─ Registry (Cached)
           ↓
    BENCHMARK CATEGORIES
    ├─ Capability: Coding, Vision, Writing
    └─ Domain: Finance, Legal, Healthcare
           ↓
    WEIGHTED SCORING
    (e.g., Coding = SWE-bench 50% + LiveCodeBench 30%)
           ↓
    TOP 3 RECOMMENDATIONS
```

## Data Sources (Ranked by Freshness)

### 1. Arena.ai - Human-Judged (Real-time)
- **URL**: https://arena.ai/leaderboard
- **Method**: Human voting, ELO-based ranking
- **Freshness**: Continuous updates (hours)
- **Best for**: Creative writing, text quality, subjective tasks
- **Scripts**: `fetch_arena.py`, `query_arena.py`
- **Top model (Text)**: Claude Opus 4.6 (1504 ELO, 8,945 votes)

### 2. Artificial Analysis API - Automated (Days, API-based)
- **URL**: https://artificialanalysis.ai/models
- **Method**: API with authentication (reliable, stable)
- **Freshness**: Days to weeks (needs benchmarking time)
- **Best for**: Stable, verified data; agent performance (GDPval-AA)
- **Scripts**: `sync_from_aa.py`, `fetch_gdpval.py`
- **Key benchmarks**: GDPval-AA (productivity/agentic work)
- **Why prioritized**: API-based = reliable, not scraping

### 3. Vals AI - Automated Benchmarks (Hours, WebFetch)
- **URL**: https://www.vals.ai/benchmarks
- **Method**: WebFetch scraping
- **Freshness**: Hours to days after release
- **Best for**: Latest models, comprehensive domain benchmarks
- **Categories**: Finance, Legal, Healthcare, Coding, Academic

### 4. Local Registry (Cached)
- **File**: `references/model_registry.json`
- **Freshness**: Updated manually or via cron
- **Best for**: Quick lookups, offline access

## Benchmark Categories

### Capability-Based (What ability?)
1. **Multimodal**: MMMU (70%) + MedScribe (30%)
2. **Agentic Coding**: SWE-bench (50%) + LiveCodeBench (30%) + Vibe (20%)
3. **Office Work & Money Creation**: APEX-Agents (35%) + Vending-Bench 2 (30%) + GDPval-AA (35%)
4. **Long-Horizon**: Vending-Bench 2 (50%) + GDPval-AA (50%)
5. **Academic**: GPQA (40%) + MMLU Pro (35%) + AIME (25%)
6. **Creative Writing**: Arena.ai Text (human-judged ELO)

### Domain-Based (What field?)
- **Legal**: CaseLaw v2, LegalBench
- **Finance**: CorpFin, TaxEval, Finance Agent, MortgageTax
- **Healthcare**: MedCode, MedScribe, MedQA
- **Math**: AIME, ProofBench
- **Education**: SAGE

## Key Scripts

### Recommendation & Query
- `recommend_model.py` - Get recommendations by purpose/industry
- `query_benchmarks.py` - Query benchmarks by use case/domain
- `query_models.py` - Query models by capabilities
- `query_arena.py` - Query Arena.ai human-judged rankings

### Data Fetching
- `fetch_arena.py` - Fetch Arena.ai leaderboard (requires WebFetch)
- `sync_from_aa.py` - Sync from Artificial Analysis API
- `fetch_gdpval.py` - Fetch GDPval-AA benchmark
- `auto_update_models.py` - Auto-update registry & memory

### Utilities
- `check_freshness.py` - Check if data is stale (>7 days)
- `verify_models.py` - Verify models are callable

## Usage Examples

```bash
# Find best coding model
python3 scripts/recommend_model.py --purpose "coding"

# Check finance benchmarks
python3 scripts/query_benchmarks.py --domain "finance"

# Get human-judged text quality
python3 scripts/query_arena.py --category text --top 5

# Find latest models
python3 scripts/recommend_model.py --latest
```

## CRITICAL: Proactive Freshness Check

**BEFORE using any model name in configurations, recommendations, or API calls:**
```bash
python3 scripts/check_freshness.py
```

If registry is >7 days old or user mentions unknown models → immediately trigger update workflow.

## Workflows

### 1. Check Model Registry & Query by Capabilities
When the user asks for available models or recommendations:

**Quick lookup:**
```bash
python3 scripts/query_models.py --list-all
```

**Query by capabilities:**
```bash
# Find cheap models with vision
python3 scripts/query_models.py --tier cheap --vision

# Find models with 1M+ context
python3 scripts/query_models.py --context-min 1000000

# Find reasoning models
python3 scripts/query_models.py --tier reasoning

# Find models with agent performance data
python3 scripts/query_models.py --agent-capable

# Natural language recommendations
python3 scripts/query_models.py --recommend "I need a cheap model with vision for image analysis"
python3 scripts/query_models.py --recommend "powerful model for complex reasoning"
python3 scripts/query_models.py --recommend "coding model with large context"
python3 scripts/query_models.py --recommend "best model for long-horizon agent tasks"
```

**Manual lookup:**
1.  Read `references/model_registry.json` to see currently stored models.
2.  Suggest models based on the user's criteria (e.g., "cheap", "powerful", "latest").

### 2. Auto-Update Models & Memory (FASTEST)
For routine updates with latest evaluation data:

```bash
python3 scripts/auto_update_models.py
```

This script:
- Updates registry timestamp
- Syncs top agent models to memory (token-friendly)
- Outputs only essential changes

### 3. Update Model Intelligence (PRIMARY METHOD: vals.ai)
**PREFERRED: Scrape vals.ai for latest models**
```bash
python3 scripts/discover_new_models.py
```
This auto-scrapes vals.ai/models via WebFetch and updates registry with top 5 latest from each provider.

**FALLBACK: Manual update via context7 MCP**
1. Use `mcp__context7__resolve-library-id` to find official API library
2. Use `mcp__context7__query-docs` to query model names
3. Extract exact model IDs from official documentation

**Save the data:**
```bash
python3 scripts/update_registry.py <provider> '{"name": "...", "tier": "...", ...}'
```

### 3. Model Tiers & Recommendations
Recommend models based on the `tier` field in `model_registry.json`:
*   **Cheap / Mini**: Use for simple text tasks, basic filtering, or when budget is tight (e.g., `gpt-4o-mini`, `gemini-1.5-flash`).
*   **Balanced**: The sweet spot for most complex coding or visual tasks.
*   **Powerful**: Use for enterprise-grade reasoning or highly complex multi-turn logic (e.g., `o1`, `gpt-4o`).

## References
- [model_registry.json](references/model_registry.json): The structured database of known models.
- [model_name_mapping.md](references/model_name_mapping.md): Marketing names → API model names mapping.
- [agent_evaluations.md](references/agent_evaluations.md): Agent performance benchmarks and evaluation sources.

## Scripts
- `scripts/update_registry.py`: Adds or updates a model in the registry.
- `scripts/query_models.py`: Query models by capabilities (tier, vision, context window, etc.) or get natural language recommendations.
- `scripts/auto_update_models.py`: Auto-sync registry and memory with latest agent performance data.
- `scripts/fetch_gdpval.py`: Fetch latest GDPval-AA rankings from Artificial Analysis (requires AA_API_KEY or uses cached data).
- `scripts/check_freshness.py`: Check if registry is stale (>7 days old).
- `scripts/verify_models.py`: Verify all models are callable via their APIs.

## Key Capabilities to Track
When updating the registry, capture these important capabilities:
- **context_window**: Maximum input tokens (e.g., 1000000 for 1M)
- **max_output**: Maximum output tokens (e.g., 128000)
- **vision**: Boolean - supports multimodal input (images, video)
- **tier**: cheap, balanced, powerful, reasoning, powerful-agentic, etc.
- **release_date**: Model release date (YYYY-MM-DD format)
- **knowledge_cutoff**: Training data cutoff date (YYYY-MM format)
- **cost**: Pricing per million tokens (input/output) if available
- **agent_performance**: Agent evaluation metrics
  - **gdpval_aa_elo**: ELO score from GDPval-AA benchmark (real-world productivity tasks)
  - **vending_bench_2_balance**: Money balance from Vending-Bench 2 (long-horizon agent simulation)
  - **best_for**: List of task types the model excels at
  - **strengths**: Key capabilities demonstrated in evaluations

## Agent Performance Benchmarks
The registry tracks performance on two key agent evaluations:

**GDPval-AA** (https://artificialanalysis.ai/evaluations/gdpval-aa)
- Real-world tasks across 44 occupations and 9 industries
- Models have shell access and web browsing in agentic loop
- Metric: ELO score (higher is better)
- Top performers: Claude Sonnet 4.6 (1633), Claude Opus 4.6 (1606)

**Vending-Bench 2** (https://andonlabs.com/evals/vending-bench-2)
- Long-horizon agent task: 1-year vending machine business simulation
- 3000-6000 messages, 60-100M tokens per run
- Tests: supplier negotiation, supply chain management, financial optimization
- Metric: Money balance after 1 year (higher is better)
- Top performers: Claude Opus 4.6 ($8,017), Claude Sonnet 4.6 ($7,204)

These capabilities enable intelligent model selection based on task requirements.

## Model Latency & Throughput (Speed Benchmarks)

Updated benchmarks for Gemini models tested on local Antigravity proxy (2026-03-11):

| Model | TTFT (s) | Throughput (t/s) | Best For |
| :--- | :--- | :--- | :--- |
| **Gemini 3.1 Pro High** | 3.90s | ~30 t/s | Quality/Coding |
| **Gemini 3 Flash** | 2.44s | ~50 t/s | **Ultra-Low Latency** |
| **Gemini 2.5 Flash Thinking** | 4.30s | **~88 t/s** | **High Vol. Generation** |

*Note: TTFT = Time to First Token. Benchmarked via `scripts/speed_test.py`.*

## Parallel Agent Concurrency Limits

**CRITICAL**: High concurrency causes throughput degradation. Tested 2026-03-13.

### GLM-5 (Zhipu AI) Concurrency Benchmarks

| Concurrent Agents | Fastest | Slowest | Variance | Degradation |
|-------------------|---------|---------|----------|-------------|
| 3 | 5,103ms | 5,170ms | 67ms | None (1.01x) |
| 8 | 1,421ms | 2,385ms | 964ms | Mild (1.68x) |
| **12** | 750ms | 2,584ms | 1,834ms | **Severe (3.45x)** |

### Throughput Under Load (12 concurrent, 100-word generation)

| Lane | Agents | Throughput | Notes |
|------|--------|------------|-------|
| ⚡ Fast | 2/12 | 36 t/s | Priority queue |
| ✓ Normal | 7/12 | 28-30 t/s | Standard |
| 🐢 Throttled | 3/12 | 14-16 t/s | **50% slower** |

### Production Recommendations

```
Safe Concurrency:  ≤6 agents  → Stable ~30+ t/s
Max Tolerance:     12 agents  → 25% throttled to ~15 t/s
Critical Point:    ~8 agents  → Queue + throttling begins
```

### Key Findings

1. **Both latency AND throughput degrade** under high concurrency
2. **Throttling is real** - not just queue delay, actual token/s reduction
3. **Load balancing uneven** - some requests routed to slower instances
4. **Rule of thumb**: Keep parallel agents ≤6 for consistent performance

See `references/parallel_agent_benchmarks.md` for full test data.

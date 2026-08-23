# Model Intelligence Skill - Improvement Proposals

## Current Status (2026-03-06)

**Strengths:**
- Quick model lookup with pricing (`model_info.py`)
- Multiple data sources: Arena.ai (human-judged), AA API (reliable), Vals AI (comprehensive)
- Weighted benchmark scoring (综合分析 approach)
- Personal priority mapping for 6 use cases
- Fetchable benchmarks (API or WebFetch)
- Manual pricing updates (fast, reliable)

**Gaps:**
- No bias indicator for vendor benchmarks
- No model comparison tool
- Limited OpenAI benchmark coverage (only fetchable ones)

---

## Proposed Improvements

### 1. Model Comparison Tool ⭐⭐⭐

**Problem:** Can't compare multiple models side-by-side

**Solution:**
```bash
python3 scripts/compare_models.py gpt-5.4 claude-opus-4-6 gemini-3.1-pro
```

**Output:**
```
| Spec           | GPT-5.4    | Claude Opus 4.6 | Gemini 3.1 Pro |
|----------------|------------|-----------------|----------------|
| Input Price    | $2.50/M    | N/A             | N/A            |
| Cached Input   | $0.25/M    | N/A             | N/A            |
| Output Price   | $15.00/M   | N/A             | N/A            |
| Context        | 272K       | 1M              | 1M             |
| Vision         | ✓          | ✓               | ✓              |
| GDPval-AA      | 83.0%      | 1606 ELO        | N/A            |
| Vending-Bench  | N/A        | $8,017          | $5,478         |
```

---

### 2. Benchmark Bias Indicator ⭐⭐⭐

**Problem:** OpenAI benchmarks may favor OpenAI models (bias)

**Solution:** Tag benchmarks by source
```json
{
  "benchmark": "BrowseComp",
  "source": "openai",
  "bias_risk": "medium",
  "third_party": false
}
```

**Categories:**
- `third_party` (Arena.ai, Vals AI, AA API) - ✓ Low bias
- `vendor` (OpenAI, Anthropic, Google) - ⚠️ Medium bias
- `internal` (not public) - ✗ High bias, exclude

**Display:** Show bias indicator in recommendations
```
BrowseComp (OpenAI ⚠️)
GDPval-AA (AA API ✓)
```

**Solution:** Add fetchability metadata

---

### 3. Add Fetchable OpenAI Benchmarks ⭐⭐

**From OpenAI benchmarks (user provided), add these fetchable ones:**

✅ **Can add (check if public leaderboard exists):**
- OSWorld-Verified (computer use)
- ARC-AGI-1/2 (abstract reasoning)
- Toolathlon (tool use)
- MCP Atlas (tool use)

✅ **Already have equivalent:**
- SWE-Bench Pro → have SWE-bench
- MMMU Pro → have MMMU
- GPQA Diamond → have GPQA
- FinanceAgent v1.1 → have Finance Agent

❌ **Not fetchable (internal):**
- Investment Banking Modeling
- OpenAI MRCR v2
- Graphwalks
- Frontier Science Research

---

## Priority Ranking

**High Priority (implement first):**
1. ⭐⭐⭐ Model comparison tool
2. ⭐⭐⭐ Bias indicator for benchmarks

**Medium Priority:**
3. ⭐⭐ Add fetchable OpenAI benchmarks (OSWorld, ARC-AGI, Toolathlon, MCP Atlas)

---

## Implementation Plan

**Phase 1 (Quick wins):**
- Create model comparison tool
- Add bias tags to existing benchmarks
- Test fetchability of OSWorld, ARC-AGI, Toolathlon, MCP Atlas

**Phase 2 (Expansion):**
- Add verified fetchable benchmarks
- Create benchmark registry with metadata
- Document manual pricing update workflow


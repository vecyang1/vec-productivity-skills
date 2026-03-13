# Personal Benchmark Priorities

Focused benchmarks for specific use cases, all with live data sources.

## 1. Daily Work / Productivity / Money Creation

**Primary: APEX-Agents** (Professional Work)
- URL: https://www.mercor.com/apex/apex-agents-leaderboard/
- Tests: Lawyer, banker, consultant scenarios (480 tasks)
- Fetch: WebFetch
- Top: GPT 5.4 xHigh (35.9%), GPT 5.2 xHigh (34.3%)
- **Why**: Real professional work, money-making scenarios

**Secondary: Vending-Bench 2** (Money Creation)
- URL: https://andonlabs.com/evals/vending-bench-2
- Tests: 1-year vending machine business simulation (60-100M tokens)
- Fetch: WebFetch
- Top: Claude Opus 4.6 ($8,017), Claude Sonnet 4.6 ($7,204), Gemini 3.1 Pro ($5,478)
- **Why**: Direct money creation indicator, real business decisions

**Tertiary: GDPval-AA** (Productivity & Agentic Work)
- URL: https://artificialanalysis.ai/evaluations/gdpval-aa
- Tests: Real-world tasks across 44 occupations with agentic workflows
- Fetch: API (Artificial Analysis)
- Top: Claude Sonnet 4.6 (1633 ELO), Claude Opus 4.6 (1606 ELO)
- **Why**: API-based reliability, real productivity tasks

**Recommendation**: Claude Opus 4.6 for complex work & money creation, Claude Sonnet 4.6 for balanced productivity

---

## 2. Multimodal (Video/Image Understanding & Reasoning)

**Primary: Arena.ai Vision** (Human-Judged)
- URL: https://arena.ai/leaderboard/vision
- Tests: Human voting on image/video understanding
- Fetch: WebFetch
- Top: Gemini 3 Pro (1288 ELO), Gemini 3.1 Pro (1278 ELO)
- **Why**: Human judgment on real visual tasks

**Secondary: Vals AI MMMU** (Academic Multimodal)
- URL: https://www.vals.ai/benchmarks/mmmu
- Tests: Graduate-level visual reasoning (1,700 questions)
- Fetch: WebFetch (Vals AI)
- Top: Gemini 3.1 Pro (88.2%), Gemini 3 Flash (87.6%)
- **Why**: Deep visual reasoning, extraction

**Recommendation**: Gemini 3.1 Pro for video/image understanding, Gemini 3 Flash for speed

---

## 3. Writing (Social Media / Articles - Vivid as Human)

**Primary: Arena.ai Text** (Human-Judged Writing)
- URL: https://arena.ai/leaderboard/text
- Tests: Human voting on text quality, naturalness
- Fetch: WebFetch
- Top: Claude Opus 4.6 (1504 ELO), Gemini 3.1 Pro (1500 ELO)
- **Why**: MOST IMPORTANT - humans judge which writing feels natural/vivid

**No secondary needed** - Arena.ai Text is the gold standard for human-like writing

**Recommendation**: Claude Opus 4.6 for vivid, human-like writing

---

## 4. Image Editing

**Primary: Arena.ai Image Edit** (Human-Judged)
- URL: https://arena.ai/leaderboard/image-edit
- Tests: Human voting on image editing quality
- Fetch: WebFetch
- Top: ChatGPT Image Latest (1406 ELO), Gemini 3.1 Flash Image (1396 ELO)
- **Why**: Human judgment on editing results

**Recommendation**: Gemini 3.1 Flash Image (Nano Banana 2) for image editing

---

## 5. Frontend Web Design

**Primary: Vals AI Vibe Code Bench** (Web Apps)
- URL: https://www.vals.ai/benchmarks/vibe-code-bench
- Tests: Build web applications from scratch
- Fetch: WebFetch (Vals AI)
- Top: GPT 5.4 (67.4%), Claude Opus 4.6 (67.4%)
- **Why**: Direct web app building test

**Secondary: Arena.ai Code** (UI Code Quality)
- URL: https://arena.ai/leaderboard/code
- Tests: Human-judged code quality
- Fetch: WebFetch
- Top: Claude Opus 4.6 Thinking (1556 ELO)
- **Why**: Human judgment on code aesthetics

**Note**: User observation - Gemini usually wins for frontend
**Recommendation**: Try Gemini 3.1 Pro first (user experience), fallback to GPT 5.4

---

## 6. Healthcare (Lowest Hallucination)

**Primary: Vals AI MedQA** (Medical Knowledge)
- URL: https://www.vals.ai/benchmarks/medqa
- Tests: Medical exam questions (accuracy = low hallucination)
- Fetch: WebFetch (Vals AI)
- Top: Claude Opus 4.6 (96.1%), Gemini 3.1 Pro (95.8%)
- **Why**: High accuracy = low hallucination rate

**Secondary: Vals AI MedScribe** (Medical Documentation)
- URL: https://www.vals.ai/benchmarks/medscribe
- Tests: Medical documentation accuracy
- Fetch: WebFetch (Vals AI)
- Top: GPT 5.1 (77.6%)
- **Why**: Real medical task accuracy

**Recommendation**: Claude Opus 4.6 for healthcare (96.1% MedQA, lowest hallucination)

---

## Quick Reference Table

| Use Case | Best Model | Benchmark | ELO/Score |
|----------|-----------|-----------|-----------|
| Daily Work | Claude Opus 4.6 | Vending-Bench 2 | $8,017 |
| Daily Work | Claude Sonnet 4.6 | GDPval-AA | 1633 ELO |
| Multimodal | Gemini 3.1 Pro | Arena Vision | 1278 ELO |
| Writing | Claude Opus 4.6 | Arena Text | 1504 ELO |
| Image Edit | Gemini 3.1 Flash | Arena Image Edit | 1396 ELO |
| Frontend | Gemini 3.1 Pro | Vibe Code | User pref |
| Healthcare | Claude Opus 4.6 | MedQA | 96.1% |

## Fetch Commands

```bash
# Fetch all priority benchmarks
python3 scripts/fetch_arena.py --category text
python3 scripts/fetch_arena.py --category vision
python3 scripts/fetch_arena.py --category code
python3 scripts/fetch_arena.py --category image-edit

# Query specific use case
python3 scripts/query_arena.py --category text --top 3
python3 scripts/query_arena.py --category vision --top 3
```

## Last Updated
2026-03-06

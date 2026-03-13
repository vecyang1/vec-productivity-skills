# Benchmark Selection Guide

Quick reference for choosing the right benchmarks for comprehensive model evaluation.

**Philosophy**: Use 2-3 benchmarks per category to triangulate performance. Single benchmarks can be gamed or have blind spots.

## Use Case → Benchmark Mapping

### 1. Multimodal Ability (Vision/Image/Video)

**Primary: MMMU** (Multimodal Multi-task Understanding) — Weight: 70%
- URL: https://www.vals.ai/benchmarks/mmmu
- Tests: Graduate-level questions with interleaved text + images (1,700 questions, 30 subjects)
- Metric: Accuracy (0-100%)
- Best for: Visual reasoning, cross-modal understanding
- Top: Gemini 3.1 Pro (88.2%), Gemini 3 Flash (87.6%), GPT 5.4 (87.5%)
- **Why 70%**: Most comprehensive multimodal benchmark, large dataset, academic rigor

**Secondary: MedScribe** (Medical image analysis) — Weight: 30%
- Tests: Medical documentation from visual inputs
- Best for: Domain-specific vision tasks
- Top: Claude Opus 4.6 (77.6%)
- **Why 30%**: Real-world application test, domain-specific validation

**Composite Score Formula**: `(MMMU × 0.7) + (MedScribe × 0.3)`

### 2. Agentic Coding

**Primary: SWE-bench** (Software Engineering Benchmark) — Weight: 50%
- Tests: Real GitHub issues requiring code changes
- Metric: % of issues resolved
- Best for: Autonomous debugging, multi-file edits
- Top: Claude Opus 4.6 (77.2%)
- **Why 50%**: Gold standard for real-world coding autonomy

**Secondary: LiveCodeBench** — Weight: 30%
- Tests: Recent coding problems (constantly updated)
- Best for: Current language features, avoiding training contamination
- Top: Claude Opus 4.6 (84.1%)
- **Why 30%**: Freshness matters, prevents overfitting to old benchmarks

**Tertiary: Vibe Code Bench** — Weight: 20%
- Tests: End-to-end coding workflows
- Top: Claude Opus 4.6 (67.4%)
- **Why 20%**: Workflow complexity, but smaller dataset

**Composite Score Formula**: `(SWE-bench × 0.5) + (LiveCodeBench × 0.3) + (Vibe × 0.2)`

### 3. Real-World Office Work & Money Creation

**Primary: APEX-Agents** — Weight: 35%
- URL: https://www.mercor.com/apex/apex-agents-leaderboard/
- Tests: Professional scenarios (lawyer, banker, consultant) - 480 tasks, 33 worlds
- Metric: Pass@1 and Mean Score (0-60%)
- Top: GPT 5.4 xHigh (35.9%), GPT 5.2 xHigh (34.3%)
- **Why 35%**: Most realistic professional work simulation, expert-designed rubrics
- **Fetchable**: Yes (WebFetch)

**Secondary: Vending-Bench 2** — Weight: 30%
- URL: https://andonlabs.com/evals/vending-bench-2
- Tests: 1-year vending machine business simulation (3000-6000 messages, 60-100M tokens)
- Metric: Money balance after 1 year (higher is better)
- Top: Claude Opus 4.6 ($8,017), Claude Sonnet 4.6 ($7,204), Gemini 3.1 Pro ($5,478)
- **Why 30%**: Direct money creation indicator, long-horizon coherence, real business decisions
- **Fetchable**: Yes (WebFetch)

**Tertiary: GDPval-AA** (Artificial Analysis) — Weight: 35%
- URL: https://artificialanalysis.ai/evaluations/gdpval-aa
- Tests: Real-world tasks across 44 occupations and 9 industries with shell access and web browsing
- Metric: ELO score (higher is better)
- Top: Claude Sonnet 4.6 (1633), Claude Opus 4.6 (1606), GPT 5.3 Codex (1462)
- **Why 35%**: API-based (reliable), real productivity tasks, agentic workflows
- **Fetchable**: Yes (API)

**Composite Score Formula**: `(APEX × 0.35) + (Vending_normalized × 0.3) + (GDPval_normalized × 0.35)`
*Note: Normalize Vending balance to 0-100 scale: `(balance / 10000) × 100`; Normalize GDPval ELO: `(ELO - 1000) / 10`*

**Alternative: Vals Index** (Composite benchmark covering finance, law, coding)
- URL: https://www.vals.ai/benchmarks/vals_index
- Can be used as standalone indicator for professional work quality
- Top: Claude Opus 4.6 (64.6%)
- See section 5 for detailed breakdown

### 4. Long-Horizon Coherence

**Primary: Vending-Bench 2** — Weight: 50%
- URL: https://andonlabs.com/evals/vending-bench-2
- Tests: 1-year business simulation (3000-6000 messages, 60-100M tokens)
- Metric: Money balance after 1 year
- Top: Claude Opus 4.6 ($8,017), Claude Sonnet 4.6 ($7,204)
- **Why 50%**: Ultimate long-horizon test, maintains coherence over 60-100M tokens
- **Fetchable**: Yes (WebFetch)

**Secondary: GDPval-AA** (Artificial Analysis) — Weight: 50%
- URL: https://artificialanalysis.ai/evaluations/gdpval-aa
- Tests: Real-world agentic tasks with extended workflows
- Metric: ELO score
- Top: Claude Sonnet 4.6 (1633), Claude Opus 4.6 (1606)
- **Why 50%**: API-based reliability, real productivity scenarios
- **Fetchable**: Yes (API)

**Composite Score Formula**: `(Vending_normalized × 0.5) + (GDPval_normalized × 0.5)`
*Note: Normalize Vending: `(balance / 10000) × 100`; Normalize GDPval: `(ELO - 1000) / 10`*

### 5. Professional Domains (Finance/Law/Medical)

**Primary: Vals Index** (Composite) — Weight: 100% (already weighted internally)
- URL: https://www.vals.ai/benchmarks/vals_index
- Tests: **Pre-weighted composite** of finance, law, and coding benchmarks
- Metric: Accuracy (0-100%)
- Top: Claude Opus 4.6 (64.6%)
- **Why 100%**: Already a composite index with internal weighting across domains

**Internal Vals Index Components** (for reference, not separate scoring):
- **Law**: CaseLaw v2 (legal reasoning) - Claude Opus 4.6 (63.8%)
- **Finance**: CorpFin (corporate finance) - Claude Opus 4.6 (65.3%)
- **Tax**: TaxEval v2 (tax code) - Claude Opus 4.6 (74.0%)
- **Medical**: MedQA (medical knowledge) - Claude Opus 4.6 (96.1%)
- **Coding**: MedCode (medical coding) - Claude Opus 4.6 (41.3%)

**Note**: Vals Index is already a weighted composite. Use it directly without further weighting. For domain-specific evaluation, use individual sub-benchmarks.

### 6. Academic Reasoning

**Primary: GPQA** (Graduate-level science Q&A) — Weight: 40%
- Tests: PhD-level questions in physics, chemistry, biology
- Top: Claude Opus 4.6 (91.7%)
- **Why 40%**: Deepest reasoning test, expert-level science

**Secondary: MMLU Pro** (Massive Multitask Language Understanding) — Weight: 35%
- Tests: Expert-level knowledge across 57 subjects
- Top: Claude Opus 4.6 (87.5%)
- **Why 35%**: Broadest knowledge coverage, standardized benchmark

**Tertiary: AIME** (Math competition) — Weight: 25%
- Tests: Advanced mathematics
- Top: Claude Opus 4.6 (96.7%)
- **Why 25%**: Pure reasoning without knowledge retrieval

**Composite Score Formula**: `(GPQA × 0.4) + (MMLU_Pro × 0.35) + (AIME × 0.25)`

### 7. Web Research & Information Retrieval

**Primary: BrowseComp** — Weight: 100%
- Tests: Persistent web browsing to find hard-to-locate information
- Metric: Accuracy (0-100%)
- Best for: Agentic web research, information retrieval, automation
- Top: GPT 5.4 Pro (89.3%), GPT 5.4 (+17% over GPT 5.2)
- **Why 100%**: Direct measure of web research automation capability
- **Fetchable**: TBD (check if public leaderboard exists)

**Note**: Single benchmark category - add secondary benchmark when more web research benchmarks emerge.

## Quick Decision Tree

```
Need to evaluate...
├─ Vision/multimodal? → MMMU
├─ Coding autonomously? → SWE-bench
├─ Professional work (lawyer/banker/consultant)? → APEX-Agents
├─ General productivity/tool use? → GDPval-AA
├─ Long conversations (coherence)? → Vending-Bench 2
├─ Web research/information retrieval? → BrowseComp
└─ Domain expertise (finance/law/medical)? → Vals Index
```

## Alternative View: Domain-Based Categorization (Vals AI)

**Source**: https://www.vals.ai/benchmarks

Vals AI organizes benchmarks by professional domain rather than capability. Use this when evaluating domain-specific AI applications.

### Legal Domain
- **CaseLaw v2**: Canadian court cases (Top: GPT 5.1)
- **LegalBench**: Wide range of legal reasoning tasks (Top: Gemini 3.1 Pro)

### Finance Domain
- **CorpFin v2**: Long-context credit agreements (Top: Kimi K2.5)
- **Finance Agent v1.1**: Financial analyst tasks (Top: Claude Sonnet 4.6)
- **MortgageTax**: Tax certificates as images (Top: Gemini 3.1 Pro)
- **TaxEval v2**: Tax questions (Top: Claude Sonnet 4.6)

### Healthcare Domain
- **MedCode**: Medical billing process (Top: Gemini 3.1 Pro)
- **MedScribe**: Doctor administrative work (Top: GPT 5.1)

### Math Domain
- **AIME**: High-school math competition (Top: Gemini 3.1 Pro)
- **ProofBench**: Formally verified math proofs (Top: GPT 5.4)

### Coding Domain
- **IOI**: International Olympiad in Informatics (Top: GPT 5.4)
- **LiveCodeBench**: Recent coding problems (Top: Gemini 3.1 Pro)
- **SWE-bench**: Production software engineering (Top: Claude Opus 4.6)
- **Terminal-Bench 2.0**: Terminal-based tasks (Top: Gemini 3.1 Pro)
- **Vibe Code Bench v1.1**: Build web apps from scratch (Top: GPT 5.4)

### Education Domain
- **SAGE**: Student Assessment with Generative Evaluation (Top: Claude Opus 4.5)

### Composite Indices
- **Vals Index**: Finance + Law + Coding (Top: Claude Sonnet 4.6)
- **Vals Multimodal Index**: Finance + Law + Coding + Education (Top: Claude Sonnet 4.6)

**When to use domain-based view:**
- Building domain-specific AI (legal AI, medical AI, finance AI)
- Comparing models within a single professional field
- Regulatory/compliance requirements for specific industries

**When to use capability-based view (main guide above):**
- Evaluating general-purpose models
- Testing specific AI capabilities (vision, coding, reasoning)
- Comparing models across different use cases

## Creative Writing & Social Media Content

**Primary Benchmark: Arena.ai Leaderboard** (Human-judged, ELO-based)
- URL: https://arena.ai/leaderboard
- **Method**: Human voting on model outputs (crowdsourced evaluation)
- **Categories**: Text, Code, Vision, Document, Search, Text-to-Image, Image Edit, Text-to-Video, Image-to-Video
- **Why it matters**: Real human preferences, not automated metrics
- **Updated**: Continuously (15 hours ago for Text, 1 day ago for Code)

### Text Category (Human-Judged Writing Quality)

**Top performers** (as of 2026-03-06):
1. **Claude Opus 4.6** - 1504 ELO (8,945 votes)
2. **Gemini 3.1 Pro Preview** - 1500 ELO (4,042 votes)
3. **Claude Opus 4.6 Thinking** - 1500 ELO (8,073 votes)
4. **Grok 4.20 Beta1** - 1493 ELO (5,071 votes)
5. **Gemini 3 Pro** - 1485 ELO (39,673 votes)
6. **GPT 5.2 Chat Latest** - 1481 ELO (5,502 votes)
7. **GPT 5.4 High** - 1480 ELO (2,290 votes)

### Model Recommendations (Based on Human Feedback)

**For Creative Writing (Long-form):**
1. **Claude Opus 4.6** - #1 on Arena Text (1504 ELO), most natural prose
2. **Gemini 3.1 Pro** - #2 on Arena Text (1500 ELO), creative but verbose
3. **GPT 5.4** - #7 on Arena Text (1480 ELO), versatile

**For Social Media (Short-form, Engaging):**
1. **Claude Opus 4.6** - Highest human preference for text
2. **Gemini 3 Pro** - Strong performance, 39K+ votes
3. **Claude Sonnet 4.6** - Conversational, cost-effective

**For Marketing Copy / Ads:**
1. **Claude Opus 4.6** - Top human-judged text quality
2. **GPT 5.2** - Persuasive, understands conversion goals
3. **Grok 4.20** - High ELO (1493), creative outputs

### Why Arena.ai is Better Than Automated Benchmarks

Unlike technical benchmarks, Arena.ai measures what humans actually prefer:
- **Subjectivity captured**: Humans vote on which output they prefer
- **Real-world relevance**: Tests actual use cases (chat, writing, creative tasks)
- **Continuous updates**: New models added within hours/days
- **Large sample size**: Thousands of votes per model (e.g., Gemini 3 Pro: 39,673 votes)
- **ELO ranking**: Competitive ranking system like chess

### Evaluation Approach

Since Arena.ai exists, use it as the primary benchmark for creative/writing tasks:
1. **Arena.ai Text category**: Primary metric for writing quality
2. **A/B testing**: Generate content with top Arena models, test with real audience
3. **Human review**: Subject matter experts rate quality, tone, engagement
4. **Engagement metrics**: CTR, likes, shares, comments (for social media)

**Recommendation**: For creative writing tasks, prioritize Arena.ai ELO scores over automated benchmarks. Models with strong reasoning (GPQA, MMLU Pro) often produce better creative content due to deeper understanding of context and nuance.

## Getting Latest Model Data

**Challenge**: Model releases happen faster than benchmark APIs update.

### Three Approaches (by freshness):

1. **Manual WebFetch** (Most current, same-day):
   - Vals AI: https://www.vals.ai/benchmarks/vals_index
   - Artificial Analysis: https://artificialanalysis.ai/models
   - Use WebFetch tool to scrape latest leaderboards

2. **Vals AI Website** (Fast, hours to days):
   - Updates quickly after major releases
   - Has GPT-5.4, latest Gemini models
   - Good for cutting-edge model comparisons

3. **Artificial Analysis API** (Stable, days to weeks):
   - Script: `python3 scripts/sync_from_aa.py`
   - Reliable but delayed (needs benchmarking time)
   - Best for verified, stable data

### Quick Model Recommendations

Use the recommendation script:
```bash
# By purpose
python3 scripts/recommend_model.py --purpose "coding"
python3 scripts/recommend_model.py --purpose "vision"
python3 scripts/recommend_model.py --purpose "writing"

# By industry
python3 scripts/recommend_model.py --industry "finance"
python3 scripts/recommend_model.py --industry "legal"

# Check for latest models
python3 scripts/recommend_model.py --latest
```

## Notes

- **Don't use multiple benchmarks for the same category** - pick the most representative one
- **MMMU** replaced older vision benchmarks (better graduate-level reasoning)
- **APEX-Agents** is newer (2025) and more realistic than older agent benchmarks
- **Vals Index** is composite - check sub-benchmarks for specific domains
- All benchmarks updated regularly - check URLs for latest scores

## Last Updated
2026-03-06

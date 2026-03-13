## Parallel Agent Speed Test - 2026-03-13

**Model**: GLM-5 (Zhipu AI)
**Test**: 3 parallel haiku agents, simple response task

| Agent | Duration (ms) | Task |
|-------|---------------|------|
| Agent A | 5,110 | Echo response |
| Agent B | 5,170 | Echo response |
| Agent C | 5,103 | Echo response |

**Parallel Total**: ~5.2s (all completed nearly simultaneously)
**Sequential Equivalent**: ~15.4s (if run one after another)
**Speedup**: ~3x

**Observations**:
- All 3 agents completed within 70ms of each other
- True parallel execution achieved
- Token overhead per agent: ~35,578 tokens (includes system prompt)
- Network latency dominant factor

---

## Critical Point Test - 2026-03-13 (12 Concurrent)

**Model**: GLM-5 (Zhipu AI) | **Agents**: 12 parallel haiku

| Agent | Duration (ms) | Status |
|-------|---------------|--------|
| Q12 | 750 | ⚡ Fast |
| Q11 | 775 | ⚡ Fast |
| Q3 | 1,098 | Normal |
| Q10 | 1,137 | Normal |
| Q8 | 1,160 | Normal |
| Q1 | 1,178 | Normal |
| Q2 | 1,233 | Normal |
| Q5 | 1,249 | Normal |
| Q4 | 1,250 | Normal |
| Q6 | 2,215 | 🐢 Slow |
| Q7 | 2,576 | 🐢 Slow |
| Q9 | 2,584 | 🐢 Slow |

### Analysis

| Metric | 3 Agents | 8 Agents | 12 Agents |
|--------|----------|----------|-----------|
| **Fastest** | 5,103ms | 1,421ms | 750ms |
| **Slowest** | 5,170ms | 2,385ms | 2,584ms |
| **Variance** | 67ms | 964ms | 1,834ms |
| **Spread Ratio** | 1.01x | 1.68x | **3.45x** |

### 结论 (Conclusions)

1. **临界点**: 8-12 并发开始出现明显排队
2. **降速现象**: 存在！部分请求被队列延迟
3. **最优并发**: 建议 ≤6 个并发保持稳定
4. **最大容忍**: 12并发时最慢请求比最快慢3.4倍

**建议**: 生产环境控制在 6 个并发以内


## Throughput Degradation Test - 2026-03-13 (12 Concurrent, 100-word gen)

| Agent | Duration | Throughput | Lane |
|-------|----------|------------|------|
| T12 Gold | 3,584ms | 36.3 t/s | ⚡ Fast |
| T11 Brown | 3,610ms | 36.0 t/s | ⚡ Fast |
| T1 Blue | 4,244ms | 30.6 t/s | Normal |
| T7 Pink | 4,332ms | 30.0 t/s | Normal |
| T8 Black | 4,413ms | 29.5 t/s | Normal |
| T9 White | 4,525ms | 28.7 t/s | Normal |
| T5 Purple | 4,527ms | 28.7 t/s | Normal |
| T6 Orange | 4,565ms | 28.5 t/s | Normal |
| T2 Red | 4,566ms | 28.5 t/s | Normal |
| T4 Yellow | 8,914ms | 14.6 t/s | 🐢 Throttled |
| T10 Gray | 8,718ms | 14.9 t/s | 🐢 Throttled |
| T3 Green | 8,086ms | 16.1 t/s | 🐢 Throttled |

### 结论: 高并发下吞吐量确实下降

- **快车道 (9/12)**: 28-36 t/s
- **慢车道 (3/12)**: 14-16 t/s (被节流 ~50%)
- **退化系数**: 2.5x

**这是真正的吞吐量节流，不只是排队延迟。**


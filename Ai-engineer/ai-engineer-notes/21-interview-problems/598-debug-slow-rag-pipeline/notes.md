---

# 598. Debug Slow RAG Pipeline
# हिंदी में: Slow RAG Pipeline Debug करना

---

## 🔵 Simple Definition (English)
A RAG pipeline has many stages (embed, search, rerank, generate). Debugging slowness means timing each stage, finding the bottleneck, and fixing it by parallelising, caching, reducing work, or streaming.

## 🔵 सरल परिभाषा (Hindi)
RAG pipeline में कई stages होते हैं (embed, search, rerank, generate)। Slowness debug करने का मतलब है हर stage का समय नापना, bottleneck ढूँढना और parallel करके, cache करके, काम घटाकर या streaming से ठीक करना।

---

## 🔴 Problem it Solves
Users abandon after a few seconds. Guessing ("the LLM is slow") wastes effort; often the real cost is a sequential step that could run in parallel, a reranker over too many documents, or a cold vector index.

## 🔴 यह क्यों बना? (Hindi)
Users कुछ seconds बाद छोड़ देते हैं। अंदाज़ा लगाना ("LLM slow है") समय बर्बाद करता है; अक्सर असली कारण sequential steps, ज़्यादा documents का reranking या cold index होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure end-to-end latency (p50, p95, p99), not averages only
Step 2 → Add per-stage timers (embed, search, rerank, LLM first token, LLM total)
Step 3 → Rank stages by share of total time
Step 4 → Fix the biggest: parallelise independent calls, cache, cut top-k, smaller model
Step 5 → Stream the LLM output to improve perceived latency
Step 6 → Re-measure; keep timers in production dashboards
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → End-to-end latency नापो (p50, p95, p99), सिर्फ average नहीं
Step 2 → हर stage का timer लगाओ
Step 3 → Stages को total time के हिस्से से rank करो
Step 4 → सबसे बड़े को ठीक करो: independent calls parallel, cache, top-k कम, छोटा model
Step 5 → Perceived latency के लिए output stream करो
Step 6 → दोबारा नापो; timers production dashboard में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a classification takes 3.5 s. Timers show: vector search 80 ms, keyword search 70 ms (run after it, not with it), reranking 40 documents with a cross-encoder 1.2 s, LLM 1.8 s. Fixes: run dense and keyword search together, rerank only the top 10, stream the answer. The mock in `main.py` shows the same idea at small scale.

**Zomato-style**: restaurant search combines geo filter, vector search and ranking; moving the geo filter into the index query removes a post-filter step.

## 🟡 Real Example Hindi mein
**Tariff System**: classification 3.5 s लेता है। Timers: vector search 80 ms, keyword search 70 ms (अलग से, साथ नहीं), 40 documents का reranking 1.2 s, LLM 1.8 s। Fix: dense और keyword search साथ चलाओ, सिर्फ top 10 rerank करो, answer stream करो।

**Zomato**: Restaurant search में geo filter को index query में डालने से post-filter step हट जाता है।

---

## 💻 Code Example — Basic
```python
# Time a function with perf_counter (pure Python)
import time

def timed(label: str, fn, *args):
    """Run fn and print how long it took."""
    t0 = time.perf_counter()                     # high-resolution start time
    result = fn(*args)                           # the work being measured
    print(f"{label}: {(time.perf_counter() - t0) * 1000:.1f} ms")  # elapsed ms
    return result                                # pass the result through

timed("sum", sum, range(1_000_000))              # measure a sample task
```

## 💻 Code Example — Advanced
Full file: `main.py` (async `Profiler` context manager, a slow sequential pipeline, a faster one using `asyncio.gather`). Observed output (simulated sleeps; timings vary):
```
--- slow_pipeline: 756 ms total
llm               401 ms   53%
rerank            151 ms   20%
vector             81 ms   11%
keyword            71 ms    9%
embed              51 ms    7%
--- fast_pipeline: 686 ms total
llm               401 ms   59%
rerank            151 ms   22%
retrieve          133 ms   19%
```
```python
# Excerpt from main.py
@asynccontextmanager
async def stage(self, name: str):
    t0 = time.perf_counter()                     # start timer
    try:
        yield                                    # run the stage body
    finally:                                     # record even when the stage raises
        self.stages[name] = time.perf_counter() - t0

# Independent work runs concurrently:
v_docs, k_docs = await asyncio.gather(_dense(q), keyword_search(q))
```
The saving here is small because the LLM dominates; the lesson is the method (measure, rank, fix the largest).

---

## 🟠 FastAPI Integration
```python
import time
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_timing(request: Request, call_next):
    t0 = time.perf_counter()                            # start per-request timer
    response = await call_next(request)                 # run the route
    ms = (time.perf_counter() - t0) * 1000              # total milliseconds
    response.headers["X-Process-Time-ms"] = f"{ms:.0f}" # expose for debugging
    return response
```
For streaming answers use `fastapi.responses.StreamingResponse` so users see the first token early. Never call blocking code (sync HTTP, heavy CPU) inside `async def` routes; use `run_in_threadpool`/`asyncio.to_thread`.

---

## 🔗 LangChain / LangGraph Connection
`RunnableParallel` runs branches concurrently; LangSmith traces show per-step latency.

```python
from langchain_core.runnables import RunnableLambda, RunnableParallel

dense = RunnableLambda(lambda q: [f"dense:{q}"])         # stand-in retrievers
keyword = RunnableLambda(lambda q: [f"keyword:{q}"])

retrieve = RunnableParallel(dense=dense, keyword=keyword)  # both run concurrently
print(retrieve.invoke("laptop"))                         # {'dense': [...], 'keyword': [...]}
```
In LangGraph, fan-out edges from one node to two nodes run them in the same step.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Optimising without measuring.
✅ Correct: add timers first.

❌ Mistake 2: Sequential awaits for independent calls.
```python
# Wrong
a = await dense(q)
b = await keyword(q)
# Right
a, b = await asyncio.gather(dense(q), keyword(q))
```

❌ Mistake 3: Reranking 100 candidates "for quality"; rerank cost grows with candidates. Retrieve wide, rerank only top N (e.g. 10-20).

---

## 🧠 Tricky Interview Question
**Q**: "p50 latency is 1.5 s but p99 is 12 s. What do you investigate?"

**Answer**: Tail latency has different causes than the median: provider rate limits and retries, cold starts, occasional huge inputs (many chunks, long documents), a slow shard or index merge, queueing under load, no timeouts. Look at traces of the slowest requests, add timeouts with fallbacks, cap input tokens, use connection pooling, and set concurrency limits.

---

## ⚫ Interview Questions + Answers

Q1: What are the stages of RAG latency?
A1: Query embedding, retrieval, optional rerank, prompt build, LLM time-to-first-token, and generation time.

Q2: Why does streaming help?
A2: It lowers perceived latency: users read while the rest is generated; total time is unchanged.

Q3: How does top-k affect speed?
A3: More chunks mean slower reranking and a longer prompt, so higher LLM latency and cost.

Q4: What can be cached?
A4: Query embeddings, retrieval results for frequent queries, final answers (semantic cache), and static prompt prefixes.

Q5 (Hard): Latency doubled after adding 10x more documents. What now?
A5: Check the index type and parameters (HNSW ef_search, IVF nprobe), memory fit, filter strategy (pre- vs post-filter), sharding, and chunk count per query; consider approximate search tuning, metadata pre-filters, hybrid candidate generation, and measuring recall to ensure speed gains do not hurt quality.

---

## 🔷 When to Use + When Not to Use
✅ Use profiling when:
- Users report slowness; before scaling hardware

❌ Avoid micro-optimising when:
- The LLM call dominates and cannot be reduced; focus on streaming and model choice

---

## 📊 Visual Diagram
```
 Before (sequential):
 |embed|vector|keyword|rerank(40)|========= LLM =========|

 After:
 |embed|vector|                      (keyword in parallel)
 |keyword|
        |rerank(10)|================ LLM (streamed) ===========>
```

---

## 💰 Cost Impact
Latency fixes often cut cost: fewer reranked documents means less reranker compute, lower top-k means fewer prompt tokens (for 10 chunks x 300 tokens = 3,000 input tokens; 5 chunks halves it), and caching avoids repeat LLM calls entirely. Parallel calls do not change token cost but reduce wall time. Use a smaller model for easy queries via routing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Time to respond | जवाब आने में लगा समय |
| p95 / p99 | Slowest 5% / 1% cutoffs | सबसे धीमे 5%/1% की सीमा |
| Bottleneck | Slowest stage | सबसे धीमा हिस्सा |
| Reranker | Re-scores candidates | Candidates को दोबारा score करने वाला |
| Time to first token | Delay before streaming starts | पहला token आने तक का समय |

---

## ⚡ 3-Line Summary
English: Time every stage, fix the biggest first. Parallelise independent calls, cut top-k and rerank size, cache, and stream. Watch p95/p99, not only averages.
Hindi: हर stage का समय नापो, सबसे बड़े को पहले ठीक करो। Independent calls parallel करो, top-k और rerank घटाओ, cache और stream करो। सिर्फ average नहीं, p95/p99 देखो।

---

## ➡️ Next Topic
**599. Debug High Token Usage** — next, find where tokens (and money) are being wasted.

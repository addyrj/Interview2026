---

# 153. Vector DB Performance
# हिंदी में: Vector DB Performance (Speed, Recall, Throughput)

---

## 🔵 Simple Definition (English)
Vector DB performance is measured by three things: latency (how fast one query returns, usually p95/p99), throughput (queries per second) and recall (how many true neighbours are found). Tuning means balancing these three against memory and cost.

## 🔵 सरल परिभाषा (Hindi)
Vector DB performance तीन चीज़ों से नापी जाती है: latency (एक query कितनी जल्दी लौटे, आमतौर पर p95/p99), throughput (प्रति सेकंड queries) और recall (कितने सही neighbours मिले)। Tuning का मतलब है इन तीनों को memory और cost के साथ संतुलित करना।

---

## 🔴 Problem it Solves
A RAG demo works with 10K chunks, then production slows down: p99 jumps to 2 seconds, CPU is pinned, and answers get worse after "optimisation". Without measurements, teams guess. A performance method finds the real bottleneck.

## 🔴 यह क्यों बना? (Hindi)
RAG demo 10K chunks पर चलता है, फिर production में धीमा हो जाता है: p99 2 सेकंड, CPU full, और "optimisation" के बाद answers बिगड़ जाते हैं। नाप के बिना teams अंदाज़ा लगाती हैं। Performance method असली bottleneck ढूँढता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a benchmark set: 200+ real queries with known relevant ids
Step 2 → Baseline: exact search gives ground truth and recall = 1.0
Step 3 → Measure ANN: recall@10, p50/p95/p99 latency, QPS at target concurrency
Step 4 → Find the bottleneck: embedding API? network? index? filter? serialization?
Step 5 → Tune: ef_search / nprobe, index params, pool size, batch, cache, hardware
Step 6 → Re-measure and set alerts (p95 > SLA, recall drop)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Benchmark set बनाओ: 200+ असली queries, सही ids के साथ
Step 2 → Baseline: exact search ground truth देता है, recall = 1.0
Step 3 → ANN नापो: recall@10, p50/p95/p99 latency, target concurrency पर QPS
Step 4 → Bottleneck ढूँढो: embedding API? network? index? filter? serialization?
Step 5 → Tune करो: ef_search / nprobe, index params, pool size, batch, cache, hardware
Step 6 → दोबारा नापो और alerts लगाओ (p95 > SLA, recall गिरना)
```

---

## 🟡 Real World Example
**Tariff Classification System**: end-to-end request is 2.4 s. Profiling shows: query embedding 180 ms, vector search 12 ms, reranker 300 ms, LLM 1.9 s. The vector DB is not the bottleneck, so spending a week tuning HNSW would be wasted. Streaming the LLM output and caching embeddings gives the real win.

**Zomato AI**: lunch-hour spike to 2,000 QPS; the pool was 5 connections, so requests queued. Increasing the pool and adding read replicas fixed p99.

## 🟡 Real Example Hindi mein
**Tariff System**: end-to-end request 2.4 s है। Profiling: query embedding 180 ms, vector search 12 ms, reranker 300 ms, LLM 1.9 s। Vector DB bottleneck नहीं है, तो HNSW tuning में हफ़्ता लगाना बेकार होता। LLM output stream करना और embeddings cache करना असली फायदा देता है।

**Zomato AI**: lunch-hour में 2,000 QPS का spike; pool सिर्फ़ 5 connections का था, requests queue में लगीं। Pool बढ़ाने और read replicas से p99 ठीक हुआ।

---

## 💻 Code Example — Basic
```python
# Runs offline: measure latency percentiles and recall for any search function
import random
import statistics
import time
from typing import Callable

random.seed(1)


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)  # sort ascending
    idx = min(len(ordered) - 1, int(len(ordered) * p))  # index of the percentile
    return ordered[idx]


def recall_at_k(ann: list[int], exact: list[int]) -> float:
    return len(set(ann) & set(exact)) / len(exact)  # overlap ratio


def benchmark(search: Callable[[int], list[int]], truth: Callable[[int], list[int]], n: int = 200) -> dict:
    lat: list[float] = []  # latencies in ms
    rec: list[float] = []  # recalls
    for q in range(n):  # q is a query id in this toy
        t = time.perf_counter()
        got = search(q)  # run ANN search
        lat.append((time.perf_counter() - t) * 1000)
        rec.append(recall_at_k(got, truth(q)))
    return {"p50_ms": round(statistics.median(lat), 3), "p95_ms": round(percentile(lat, 0.95), 3),
            "p99_ms": round(percentile(lat, 0.99), 3), "recall@10": round(statistics.mean(rec), 3)}


# Toy "engines": truth returns ids 0..9; ANN misses ~10% of them and takes a tiny random time
truth_fn = lambda q: list(range(10))
ann_fn = lambda q: [i for i in range(10) if random.random() > 0.1]
print(benchmark(ann_fn, truth_fn))  # example output shape: {'p50_ms': ..., 'recall@10': ~0.9}
```

## 💻 Code Example — Advanced
```python
# Production: concurrent load test against your real async search function
import asyncio
import statistics
import time
from typing import Awaitable, Callable


async def load_test(search: Callable[[str], Awaitable[list]], queries: list[str],
                    concurrency: int = 20, rounds: int = 5) -> dict[str, float]:
    sem = asyncio.Semaphore(concurrency)  # cap in-flight requests
    latencies: list[float] = []
    errors = 0

    async def one(q: str) -> None:
        nonlocal errors
        async with sem:  # wait for a free slot
            t = time.perf_counter()
            try:
                await asyncio.wait_for(search(q), timeout=2.0)  # hard timeout protects the test
                latencies.append((time.perf_counter() - t) * 1000)
            except Exception:  # timeouts and backend errors both count
                errors += 1

    start = time.perf_counter()
    await asyncio.gather(*(one(q) for _ in range(rounds) for q in queries))  # fire everything
    elapsed = time.perf_counter() - start
    latencies.sort()
    pick = lambda p: latencies[min(len(latencies) - 1, int(len(latencies) * p))] if latencies else float("nan")
    return {
        "qps": round(len(latencies) / elapsed, 1),
        "p50_ms": round(pick(0.50), 1), "p95_ms": round(pick(0.95), 1), "p99_ms": round(pick(0.99), 1),
        "error_rate": round(errors / max(1, errors + len(latencies)), 4),
        "mean_ms": round(statistics.fmean(latencies), 1) if latencies else float("nan"),
    }


async def fake_search(q: str) -> list[str]:
    await asyncio.sleep(0.01)  # replace with: await hybrid_search(pool, q, vec)
    return ["8518.30"]


if __name__ == "__main__":
    print(asyncio.run(load_test(fake_search, ["earbuds", "t-shirt", "laptop"] * 10)))
```

---

## 🟠 FastAPI Integration
```python
import time
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)  # run the route
    ms = (time.perf_counter() - start) * 1000
    response.headers["Server-Timing"] = f"total;dur={ms:.1f}"  # visible in browser devtools
    return response  # export `ms` to Prometheus/OpenTelemetry in production


@app.get("/tariff/search")
async def search(q: str) -> dict:
    t0 = time.perf_counter()
    # emb = await embed(q); t1 = time.perf_counter()   # time each stage separately
    # hits = await store.query(emb);  t2 = time.perf_counter()
    return {"stages_ms": {"total": round((time.perf_counter() - t0) * 1000, 2)}}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Measure each LangGraph node with a tiny decorator (works for any node function)
import functools
import time


def timed(name: str):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(state):
            t = time.perf_counter()
            out = await fn(state)  # run the node
            out.setdefault("timings", {})[name] = round((time.perf_counter() - t) * 1000, 1)
            return out
        return wrapper
    return deco

# graph.add_node("retrieve", timed("retrieve")(retrieve_node))
# LangSmith traces also show per-step latency and token usage without extra code.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reporting average latency
```python
# Wrong: mean hides slow tail; users feel p99
print(statistics.mean(lat))
# Right: report p50, p95, p99 and error rate
```

❌ Mistake 2: Raising speed without checking recall
```python
# Wrong: ef_search 10 -> faster, never measured recall (dropped to 0.78)
# Right: sweep ef_search in (10, 40, 80, 160), plot recall vs p95, pick the knee of the curve
```

---

## 🧠 Tricky Interview Question

**Q**: "Single-query latency is 8 ms, but under 200 concurrent users p99 reaches 3 seconds. Why, and what do you check?"

**Answer**: Latency under load is dominated by queuing, not by the index. Check: connection pool size (requests wait for a free connection), CPU saturation (HNSW search is CPU-bound, so QPS is limited by cores), memory (index not fully in RAM causes disk reads), synchronous code blocking the event loop in the API, and lock contention during writes or index builds. Fixes: bigger pool with a limit, read replicas, caching, batching embeddings, async clients, and separating ingestion from query nodes.

---

## ⚫ Interview Questions + Answers

Q1: What is p95 latency?
A1: 95 percent of requests finish faster than this value. It reflects typical worst-case user experience better than the average.

Q2: What is recall@k?
A2: The fraction of the true top-k neighbours (from exact search) that the ANN index returned.

Q3: Which knob trades recall for speed in HNSW?
A3: `ef_search` at query time (and `m`/`ef_construction` at build time).

Q4: Why keep the index in RAM?
A4: ANN graph walks do random access; reading from disk makes each hop slow and p99 explodes.

Q5: How do you scale a vector DB to 10x traffic?
A5: First cache and cut work (embedding cache, smaller k). Then add read replicas or shards, increase pool limits, use quantization to fit RAM, batch writes, separate ingestion from serving, and verify recall at each step with the benchmark set.

---

## 🔷 When to Use + When Not to Use
✅ Use performance work when:
- You have an SLA, rising traffic or growing data

❌ Avoid when:
- Vector search is under 5 percent of total request time (optimise the LLM call, prompts or streaming instead)

---

## 📊 Visual Diagram
```
 Request timeline (ms)
 |embed 180|vector 12|rerank 300|---------- LLM 1900 ----------|
  ^ cache    ^ fine     ^ batch/skip  ^ stream, smaller prompt, cheaper model

 Recall vs speed (ef_search)
 recall 1.0 |            ____------
            |       ___--
            |   _--     <- pick the knee
        0.7 |__-
            +-----------------------> ef_search / latency
```

---

## 💰 Cost Impact
- Faster searches rarely change token cost; better recall does, because you can use a smaller k. Each avoided 300-token chunk saves input tokens on every request.
- Throughput tuning cuts hardware cost: caching 30 percent of queries removes about 30 percent of embedding calls and DB work.
- Over-provisioning hides inefficiency; measure CPU per query before adding nodes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Time for one request | एक request का समय |
| Throughput / QPS | Requests per second | प्रति सेकंड requests |
| p99 | 99th percentile latency | 99वाँ percentile latency |
| Recall | Correct neighbours found | मिले सही neighbours |
| Ground truth | Exact-search reference | Exact search का संदर्भ |
| Connection pool | Reused DB connections | DB connections का pool |

---

## ⚡ 3-Line Summary
English: Measure p95/p99 latency, QPS and recall@k against exact search before tuning. Find the real bottleneck across embedding, network, index and LLM. Tune one knob at a time and re-measure.
Hindi: Tuning से पहले p95/p99 latency, QPS और recall@k को exact search के मुक़ाबले नापो। Embedding, network, index और LLM में असली bottleneck ढूँढो। एक बार में एक knob बदलो और दोबारा नापो।

---

## ➡️ Next Topic
**154. Vector DB Cost Optimization** — storage, RAM, quantization and caching to cut the bill.

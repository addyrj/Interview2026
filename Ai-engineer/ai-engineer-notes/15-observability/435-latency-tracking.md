---

# 435. Latency Tracking
# हिंदी में: Latency Tracking (कितना समय लग रहा है)

---

## 🔵 Simple Definition (English)
Latency tracking is measuring how long each part of an AI request takes: total time, **time to first token (TTFT)**, per-step time (retrieval, LLM, tools) and generation speed (tokens per second). You report percentiles (p50, p95, p99), not averages, and break them down by model, route and step.

## 🔵 सरल परिभाषा (Hindi)
Latency tracking का मतलब है AI request के हर हिस्से का समय नापना: total time, **पहला token आने का समय (TTFT)**, हर step का समय (retrieval, LLM, tools) और generation speed (tokens/sec)। Average नहीं, percentiles (p50, p95, p99) report करते हैं और model, route, step के हिसाब से तोड़ते हैं।

---

## 🔴 Problem it Solves
- Users leave when chat feels slow; LLM latency varies 10x between calls.
- A slow answer could be the vector DB, the network, queueing, a long prompt, or a long output. Without per-step timing you guess.
- Averages hide the slow tail that angry users experience.

## 🔴 यह क्यों बना? (Hindi)
- Chat धीमा लगे तो users चले जाते हैं; LLM latency हर call में 10 गुना बदल सकती है।
- धीमा जवाब vector DB, network, queue, लंबे prompt या लंबे output की वजह से हो सकता है। Step-wise timing के बिना अंदाज़ा लगाना पड़ता है।
- Average धीमी tail को छुपा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use a monotonic clock (time.perf_counter), never wall clock
Step 2 → Time each step: embed, retrieve, rerank, LLM, post-process
Step 3 → For streaming LLM calls record TTFT (first chunk) and total time
Step 4 → tokens_per_second = output_tokens / (total - TTFT)
Step 5 → Record into histograms with labels (model, route, step)
Step 6 → Dashboard p50/p95/p99 and a stacked per-step breakdown
Step 7 → Alert on p95 > SLO; investigate the dominant step first
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Monotonic clock (time.perf_counter) use करो, wall clock नहीं
Step 2 → हर step का समय नापो: embed, retrieve, rerank, LLM, post-process
Step 3 → Streaming में TTFT (पहला chunk) और total time record करो
Step 4 → tokens_per_second = output_tokens / (total - TTFT)
Step 5 → Histogram में labels (model, route, step) के साथ रखो
Step 6 → Dashboard में p50/p95/p99 और step-wise stacked breakdown
Step 7 → p95 > SLO पर alert; सबसे बड़े step की जाँच पहले करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: p95 total latency is 5.2 s, target is 3 s. Step breakdown: embedding 120 ms, vector search 250 ms, rerank 1,900 ms, LLM 2,800 ms. The reranker (a cross-encoder on 50 chunks) is the surprise. Cutting to 15 chunks reduces rerank to 600 ms, and a shorter prompt cuts LLM time to 1,900 ms. New p95 is 2.9 s.

**Zomato-style**: chat assistant measured by TTFT (target < 800 ms) because streaming text hides total time.

## 🟡 Real Example Hindi mein
**Tariff System**: p95 total latency 5.2 s है, target 3 s। Breakdown: embedding 120 ms, vector search 250 ms, rerank 1,900 ms, LLM 2,800 ms। Reranker (50 chunks पर cross-encoder) चौंकाने वाला निकला। 15 chunks करने से rerank 600 ms और छोटे prompt से LLM 1,900 ms हुआ। नया p95 2.9 s।

---

## 💻 Code Example — Basic
A timing context manager and percentile report (pure Python, run directly).

```python
# Step timer + percentile report
import time                                        # clock
from contextlib import contextmanager              # for 'with' timer
from collections import defaultdict                # store samples
from statistics import quantiles                   # percentiles
from typing import Iterator                        # type hint

SAMPLES: dict[str, list[float]] = defaultdict(list)  # step name -> list of ms


@contextmanager
def timed(step: str) -> Iterator[None]:
    start = time.perf_counter()                    # monotonic start
    try:
        yield                                      # run the block
    finally:                                       # record even if the block fails
        SAMPLES[step].append((time.perf_counter() - start) * 1000)


def handle_request() -> None:
    with timed("retrieve"):
        time.sleep(0.02)                           # fake DB
    with timed("llm"):
        time.sleep(0.05)                           # fake LLM


for _ in range(30):                                # simulate 30 requests
    handle_request()

for step, vals in SAMPLES.items():                 # report
    q = quantiles(vals, n=20)                      # 19 cut points (5% steps)
    print(f"{step}: p50={q[9]:.0f}ms p95={q[18]:.0f}ms n={len(vals)}")
```

## 💻 Code Example — Advanced
Streaming TTFT + tokens/sec with the async OpenAI client, error handling, and a timeout.

```python
# Measure TTFT, total latency and tokens/sec on a streaming call
import asyncio                                             # timeouts + run
import time                                                # clock
from dataclasses import dataclass                          # result type
from typing import Optional                                # hints

from openai import AsyncOpenAI, APIError, APITimeoutError  # client + errors

client = AsyncOpenAI(timeout=20.0, max_retries=0)          # explicit timeout; we handle retries ourselves


@dataclass
class LatencyReport:                                       # result of one call
    ttft_ms: Optional[float]                               # None if no token arrived
    total_ms: float
    out_tokens: int
    tps: float                                             # tokens per second after first token
    text: str


async def stream_with_latency(prompt: str, model: str = "gpt-4o-mini") -> LatencyReport:
    start = time.perf_counter()                            # request start
    first: Optional[float] = None                          # time of first content chunk
    parts: list[str] = []                                  # collected text
    out_tokens = 0                                         # filled from usage chunk
    try:
        stream = await client.chat.completions.create(
            model=model, stream=True, max_tokens=120,
            stream_options={"include_usage": True},        # final chunk has usage
            messages=[{"role": "user", "content": prompt}],
        )
        async for chunk in stream:
            if chunk.usage:                                # last chunk: usage only
                out_tokens = chunk.usage.completion_tokens
            if chunk.choices and chunk.choices[0].delta.content:
                if first is None:
                    first = time.perf_counter()            # first token arrived
                parts.append(chunk.choices[0].delta.content)
    except (APITimeoutError, APIError) as exc:             # provider problems
        raise RuntimeError(f"LLM stream failed: {exc}") from exc
    end = time.perf_counter()
    ttft = (first - start) * 1000 if first else None
    gen_time = (end - first) if first else 0.0             # time spent generating
    tps = out_tokens / gen_time if gen_time > 0 else 0.0
    return LatencyReport(ttft, (end - start) * 1000, out_tokens, tps, "".join(parts))


if __name__ == "__main__":
    print(asyncio.run(stream_with_latency("Explain HS codes in one line.")))
```

---

## 🟠 FastAPI Integration
A middleware measures every request, and a `Server-Timing` header exposes step times to browser dev tools.

```python
# FastAPI middleware + Server-Timing header
import time                                                    # clock
from fastapi import FastAPI, Request                           # framework
from pydantic import BaseModel

app = FastAPI()


@app.middleware("http")
async def latency_mw(request: Request, call_next):
    start = time.perf_counter()                                # begin
    request.state.steps = {}                                   # per-request step times
    response = await call_next(request)                        # run the handler
    total = (time.perf_counter() - start) * 1000
    parts = [f"{k};dur={v:.1f}" for k, v in request.state.steps.items()]
    parts.append(f"total;dur={total:.1f}")
    response.headers["Server-Timing"] = ", ".join(parts)       # visible in browser devtools
    return response


class Req(BaseModel):
    product: str


@app.post("/classify")
async def classify(req: Req, request: Request) -> dict[str, str]:
    t = time.perf_counter()
    # ... retrieval call here ...
    request.state.steps["retrieve"] = (time.perf_counter() - t) * 1000
    t = time.perf_counter()
    # ... LLM call here ...
    request.state.steps["llm"] = (time.perf_counter() - t) * 1000
    return {"hs_code": "8518.22"}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain run callbacks give per-node start and end events; LangSmith, Langfuse and Phoenix use them to build timelines. You can also stream with `astream_events` and time the first event.

```python
# TTFT with LangChain astream
import time
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


async def ttft(prompt: str) -> float:
    start = time.perf_counter()
    async for chunk in llm.astream(prompt):          # yields message chunks
        if chunk.content:
            return (time.perf_counter() - start) * 1000   # first non-empty chunk
    return -1.0

# LangGraph: stream_mode="updates" yields after each node; time between updates = node latency.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `time.time()` and averages
✅ Correct: `time.perf_counter()` and percentiles.

```python
# Wrong
start = time.time(); ...; avg = sum(xs) / len(xs)
# Right
start = time.perf_counter(); ...; p95 = quantiles(xs, n=100)[94]
```

❌ Mistake 2: Blocking call inside async code, so latency looks like the LLM is slow
✅ Correct: use async clients or `asyncio.to_thread`.

```python
# Wrong: blocks the event loop; every concurrent request gets slower
import requests
async def f(): return requests.get(url).text
# Right
import httpx
async def f():
    async with httpx.AsyncClient() as c:
        return (await c.get(url)).text
```

---

## 🧠 Tricky Interview Question
**Q**: "Latency doubles at 9 PM, but the LLM provider status page shows no issue and your per-call LLM time is unchanged. Where is the time going?"

**Answer**: Probably queueing/saturation in your own service: the event loop or worker pool is full, or you hit client connection-pool/semaphore limits and requests wait before the call starts. Measure queue time (time from request arrival to start of work) separately from service time. Check in-flight gauge, CPU/event-loop lag, connection pool size, and provider 429 retries with backoff, which add waiting that does not show up as LLM time.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is p95 latency?
A1: 95% of requests finish faster than this value; 5% are slower. It shows the tail experience.

Q2 (Easy): What is TTFT and why does it matter?
A2: Time to first token. With streaming, users judge speed by when text starts appearing.

Q3 (Medium): What increases LLM latency?
A3: Longer input (prefill), longer output (each token is sequential), larger models, provider load, cold start, and network distance. Output length is usually the biggest lever.

Q4 (Medium): How can you reduce latency without changing the model?
A4: Stream, cap `max_tokens`, shorten the prompt, cache results, run independent steps in parallel with `asyncio.gather`, reduce rerank candidates, use prompt caching, and place services near the provider region.

Q5 (Hard): How do you prove which step causes a p99 regression after a release?
A5: Compare per-step histograms before and after, using version labels, and look at traces of slowest requests (exemplars). Check whether the shift is in all requests (code or prompt change) or only a fraction (data-dependent, e.g. long documents). Reproduce with the golden set under load and bisect the change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- User-facing chat or API with a latency SLO
- Multi-step RAG or agent pipelines

❌ Avoid when:
- Offline batch jobs where throughput and cost matter, not per-request latency

---

## 📊 Visual Diagram
```
 t=0                                                         t=2.9s
 │ embed │ vector search │ rerank │      LLM prefill + decode      │
 │ 120ms │     250ms     │ 600ms  │ wait │▓▓▓▓▓▓▓▓▓ tokens ▓▓▓▓▓▓▓▓│
                                         ▲
                                       TTFT = 1.3 s
 tokens/sec = out_tokens / (total - TTFT)
```

---

## 💰 Cost Impact
- Measuring latency costs nothing in tokens.
- Latency and cost are linked: shorter prompts and capped outputs cut both. A 20% cut in output tokens reduces both generation time and output cost (the pricier token type).
- Parallelism is free in tokens but may raise your rate-limit usage; faster models (mini tier) are cheaper and quicker for easy tasks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Time to complete a request | Request पूरी होने में लगा समय |
| TTFT | Time to first token | पहले token तक का समय |
| p50/p95/p99 | Percentile latencies | Percentile latency |
| Tokens/sec | Generation speed | Generation की गति |
| Queue time | Wait before work starts | काम शुरू होने से पहले इंतज़ार |
| Tail latency | Slowest requests | सबसे धीमी requests |
| Monotonic clock | Clock that never goes backward | कभी पीछे न जाने वाली clock |

---

## ⚡ 3-Line Summary
English: Time every step with a monotonic clock, record TTFT and tokens per second for streams, and report percentiles by step. The tail (p95/p99) is what users feel. Fix the dominant step first: usually output length, rerank or queueing.
Hindi: हर step को monotonic clock से नापो, streams के लिए TTFT और tokens/sec रखो और step के हिसाब से percentiles report करो। Users tail (p95/p99) महसूस करते हैं। सबसे बड़े step को पहले ठीक करो: अक्सर output length, rerank या queueing।

---

## ➡️ Next Topic
**436. Error Tracking in AI Apps** — classifying provider errors, timeouts, bad outputs and silent failures.

---

# 459. Cache Monitoring
# हिंदी में: Cache Monitoring (Cache की निगरानी)

---

## 🔵 Simple Definition (English)
Cache monitoring means measuring how well your LLM cache works: hit rate, miss rate, latency saved, money saved, and wrong-answer rate. A cache you do not measure is a cache you cannot trust. Monitoring tells you if the cache is saving tokens or silently returning stale answers.

## 🔵 सरल परिभाषा (Hindi)
Cache monitoring का मतलब है यह मापना कि आपका LLM cache कितना अच्छा काम कर रहा है: hit rate, miss rate, बचा हुआ latency, बचे हुए पैसे और गलत जवाबों की दर। जिस cache को आप measure नहीं करते उस पर भरोसा नहीं कर सकते। Monitoring बताती है कि cache tokens बचा रहा है या चुपचाप पुराने जवाब दे रहा है।

---

## 🔴 Problem it Solves
Teams add a semantic cache, see "it works" in a demo, and never look again. Then the similarity threshold is too loose and users get wrong HS codes, or the hit rate is 3% and the cache only adds Redis cost. Without metrics you cannot tune the threshold, TTL, or cache size.

## 🔴 यह क्यों बना? (Hindi)
Teams semantic cache लगाकर demo में देखती हैं कि "चल रहा है" और फिर कभी नहीं देखतीं। बाद में similarity threshold ढीला होने से users को गलत HS code मिलते हैं, या hit rate सिर्फ 3% होता है और cache सिर्फ Redis का खर्च बढ़ाता है। Metrics के बिना threshold, TTL और cache size tune नहीं हो सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap every cache lookup: record hit / miss / error + latency
Step 2 → On a hit, record tokens and dollars that were NOT spent
Step 3 → Sample some hits and re-check them against a fresh LLM answer (quality)
Step 4 → Export counters to Prometheus / Datadog / Langfuse
Step 5 → Dashboard: hit rate, p95 latency, $ saved, stale-answer rate, evictions
Step 6 → Alerts: hit rate drops, errors rise, memory near limit
Step 7 → Tune threshold, TTL, key design based on the numbers
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर cache lookup को wrap करो: hit / miss / error + latency record करो
Step 2 → Hit पर record करो कि कितने tokens और dollars खर्च नहीं हुए
Step 3 → कुछ hits को fresh LLM जवाब से दोबारा check करो (quality)
Step 4 → Counters को Prometheus / Datadog / Langfuse में भेजो
Step 5 → Dashboard: hit rate, p95 latency, बचे $, stale-answer rate, evictions
Step 6 → Alerts: hit rate गिरे, errors बढ़ें, memory limit के पास हो
Step 7 → इन numbers के आधार पर threshold, TTL, key design tune करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers ask "HS code for cotton t-shirts" thousands of times. After adding a semantic cache, the dashboard shows hit rate 42%, average saved cost $0.0004 per hit, and a sampled stale-answer rate of 6%. The 6% is high because the customs rule changed last week, so the team lowers the TTL from 30 days to 3 days and flushes the affected keys.

**Zomato AI**: "Best biryani near me" has a low hit rate because the key includes location. Monitoring shows this, so the team removes the exact GPS from the key and uses a locality id. Hit rate rises from 8% to 35%.

## 🟡 Real Example Hindi mein
**Tariff System**: Importers हज़ारों बार पूछते हैं "cotton t-shirts का HS code"। Semantic cache के बाद dashboard दिखाता है hit rate 42%, हर hit पर औसतन $0.0004 की बचत और sampled stale-answer rate 6%। 6% ज़्यादा है क्योंकि पिछले हफ्ते customs rule बदला था, इसलिए team TTL 30 दिन से घटाकर 3 दिन करती है और affected keys flush करती है।

**Zomato AI**: "Best biryani near me" का hit rate कम है क्योंकि key में location है। Monitoring से यह दिखा तो team ने exact GPS हटाकर locality id लगाई। Hit rate 8% से 35% हो गया।

---

## 💻 Code Example — Basic
```python
# Basic cache stats tracker - pure Python, runs directly
from dataclasses import dataclass  # simple data container


@dataclass
class CacheStats:
    """Counts hits and misses and computes hit rate."""

    hits: int = 0  # number of cache hits
    misses: int = 0  # number of cache misses
    tokens_saved: int = 0  # tokens we did not pay for

    def record_hit(self, tokens: int) -> None:
        self.hits += 1  # one more hit
        self.tokens_saved += tokens  # add the saved tokens

    def record_miss(self) -> None:
        self.misses += 1  # one more miss

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses  # all lookups
        return self.hits / total if total else 0.0  # avoid divide by zero


stats = CacheStats()  # create tracker
cache: dict[str, str] = {}  # tiny in-memory cache

for q in ["hs code tshirt", "hs code tshirt", "hs code laptop", "hs code tshirt"]:
    if q in cache:  # lookup
        stats.record_hit(tokens=700)  # a hit saves ~700 tokens
    else:
        stats.record_miss()  # a miss goes to the LLM
        cache[q] = "6109.10"  # store fake answer

print(f"hit_rate={stats.hit_rate:.2f} tokens_saved={stats.tokens_saved}")  # 0.50 and 1400
```

## 💻 Code Example — Advanced
```python
# Production style: instrumented cache with latency, cost, errors, async
import asyncio  # async runtime
import logging  # structured logs
import time  # latency timing
from dataclasses import dataclass, field  # data containers
from typing import Awaitable, Callable, Optional  # type hints

logger = logging.getLogger("cache_monitor")  # module logger

PRICE_IN = 0.15 / 1_000_000  # gpt-4o-mini input $/token
PRICE_OUT = 0.60 / 1_000_000  # gpt-4o-mini output $/token


@dataclass
class Metrics:
    hits: int = 0
    misses: int = 0
    errors: int = 0
    usd_saved: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)  # for percentiles

    def p95(self) -> float:
        if not self.latencies_ms:  # nothing recorded yet
            return 0.0
        data = sorted(self.latencies_ms)  # sort ascending
        return data[min(len(data) - 1, int(len(data) * 0.95))]  # 95th percentile

    def snapshot(self) -> dict[str, float]:
        total = self.hits + self.misses  # all lookups
        return {
            "hit_rate": self.hits / total if total else 0.0,
            "errors": float(self.errors),
            "usd_saved": round(self.usd_saved, 6),
            "p95_ms": round(self.p95(), 2),
        }


class MonitoredCache:
    """Wraps any LLM call with a cache and records metrics."""

    def __init__(self, ttl_s: int = 3600) -> None:
        self.store: dict[str, tuple[float, str, int, int]] = {}  # key -> (expiry, text, in, out)
        self.ttl_s = ttl_s  # time to live
        self.m = Metrics()  # metrics object

    async def get_or_call(
        self, key: str, call: Callable[[], Awaitable[tuple[str, int, int]]]
    ) -> str:
        start = time.perf_counter()  # start timer
        try:
            entry: Optional[tuple[float, str, int, int]] = self.store.get(key)  # lookup
            if entry and entry[0] > time.time():  # valid and not expired
                self.m.hits += 1  # count hit
                self.m.usd_saved += entry[2] * PRICE_IN + entry[3] * PRICE_OUT  # money saved
                return entry[1]  # return cached text
            self.m.misses += 1  # count miss
            text, tin, tout = await call()  # real LLM call
            self.store[key] = (time.time() + self.ttl_s, text, tin, tout)  # save with TTL
            return text
        except Exception as exc:  # never let monitoring break the request
            self.m.errors += 1  # count error
            logger.exception("cache path failed: %s", exc)  # log it
            raise
        finally:
            self.m.latencies_ms.append((time.perf_counter() - start) * 1000)  # record latency


async def fake_llm() -> tuple[str, int, int]:
    await asyncio.sleep(0.01)  # pretend network
    return "6109.10", 600, 100  # text, input tokens, output tokens


async def main() -> None:
    cache = MonitoredCache(ttl_s=60)  # create cache
    for _ in range(5):  # same question 5 times
        await cache.get_or_call("hs:tshirt", fake_llm)
    print(cache.m.snapshot())  # 1 miss, 4 hits


if __name__ == "__main__":
    asyncio.run(main())  # run the demo
```

---

## 🟠 FastAPI Integration
Expose the metrics at `/metrics` (Prometheus style) or `/cache/stats` (JSON) so dashboards and alerts can read them.

```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # request model

app = FastAPI()  # app instance
cache = MonitoredCache(ttl_s=300)  # from the advanced example


class Ask(BaseModel):
    question: str  # user question


@app.post("/classify")
async def classify(body: Ask) -> dict[str, str]:
    async def call() -> tuple[str, int, int]:
        return "6109.10", 600, 100  # replace with a real LLM call

    answer = await cache.get_or_call(f"hs:{body.question.lower().strip()}", call)  # cached call
    return {"answer": answer}


@app.get("/cache/stats")
async def stats() -> dict[str, float]:
    return cache.m.snapshot()  # hit rate, p95, dollars saved
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a global cache (`set_llm_cache`). You can subclass `BaseCache` or wrap `InMemoryCache` to count hits. LangSmith and Langfuse traces also show cache hits as very fast runs with zero tokens.

```python
from langchain_core.caches import InMemoryCache  # built-in cache
from langchain_core.globals import set_llm_cache  # global switch


class CountingCache(InMemoryCache):
    hits = 0  # class level counters
    misses = 0

    def lookup(self, prompt: str, llm_string: str):  # called before every LLM call
        result = super().lookup(prompt, llm_string)  # real lookup
        if result is None:
            CountingCache.misses += 1  # miss
        else:
            CountingCache.hits += 1  # hit
        return result


set_llm_cache(CountingCache())  # all LangChain / LangGraph LLM nodes now report hits
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Watching only the hit rate
✅ Correct: Also track the wrong-answer rate. A 90% hit rate with a loose threshold can be 90% wrong.

```python
# Wrong - only hit rate
print(stats.hit_rate)

# Right - sample hits and compare with a fresh answer
import random
if random.random() < 0.02:  # audit 2% of hits
    fresh = "6109.10"  # call the LLM again here
    stale = fresh != cached_answer  # count this as stale/wrong
```

❌ Mistake 2: Unbounded metric labels
✅ Correct: Never use the raw user question as a metric label. It creates millions of time series.

```python
# Wrong
counter.labels(question=user_question).inc()
# Right
counter.labels(route="classify", result="hit").inc()
```

---

## 🧠 Tricky Interview Question
**Q**: "Your cache hit rate is 60% but the finance team says LLM cost did not drop. Why?"

**Answer**: Hits may be on cheap, short queries while expensive long-context queries always miss. Hit rate counts requests, not dollars. Track dollars saved and token-weighted hit rate. Also check that cache writes (embedding calls, vector DB cost) are not eating the savings.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is cache hit rate?
A1: hits divided by total lookups. 40 hits out of 100 lookups is 0.40.

Q2: [Easy] Why monitor an LLM cache?
A2: To know if it saves money, stays fast, and does not return wrong or stale answers.

Q3: [Medium] Which metrics would you put on the dashboard?
A3: Hit rate, token-weighted hit rate, dollars saved, p50/p95 latency for hits and misses, eviction count, memory use, error rate, and sampled stale-answer rate.

Q4: [Medium] How do you detect a bad semantic-cache threshold?
A4: Sample hits, re-run them through the LLM, and compare answers. Plot similarity score vs correctness. Choose the threshold where wrong answers stay below your target.

Q5: [Hard] How would you alert on cache problems without noise?
A5: Alert on a sustained drop versus a rolling baseline (for example a 7-day same-hour average), not a fixed number. Add a separate alert for stale-answer rate and for Redis latency. Use hysteresis so one slow minute does not page anyone.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run any production cache in front of an LLM
- You tune threshold, TTL or key design
- You must prove ROI of the cache

❌ Avoid when:
- A throwaway prototype with a handful of users (logs are enough)
- You would add heavy metrics that cost more than the cache saves

---

## 📊 Visual Diagram
```
Request ─► [Cache lookup] ──hit──► answer ─► metrics: hit++, $saved
                │
              miss
                ▼
            [LLM call] ─► store in cache ─► metrics: miss++, tokens used
                                   │
                                   ▼
            [Metrics store] ─► Dashboard + Alerts
            (hit rate, p95, $ saved, stale rate)
```

---

## 💰 Cost Impact
Monitoring itself is almost free (counters in memory). A sampled audit (2% of hits re-run) adds about 2% of the saved cost back as spend, a cheap price for catching wrong answers. Example: 100K hits/day at 700 tokens on gpt-4o-mini saves about $10.50/day input plus output savings; auditing 2K hits costs about $0.30/day. Optimise by sampling instead of checking every hit, and by using a cheap model as the judge.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hit rate | hits / total lookups | कितनी बार cache से जवाब मिला |
| Miss | Lookup not found | cache में नहीं मिला |
| TTL | Time before entry expires | entry कब तक valid |
| p95 latency | 95% requests faster than this | 95% requests इससे तेज़ |
| Eviction | Removing entries when full | जगह भरने पर entry हटाना |
| Stale answer | Outdated cached answer | पुराना जवाब |

---

## ⚡ 3-Line Summary
English: Cache monitoring measures hit rate, latency, dollars saved and wrong-answer rate. Hit rate alone is misleading, so sample hits and audit quality. Use the numbers to tune threshold, TTL and keys.
Hindi: Cache monitoring hit rate, latency, बचे dollars और गलत-जवाब की दर मापती है। सिर्फ hit rate गुमराह कर सकता है, इसलिए hits को sample करके quality audit करो। इन numbers से threshold, TTL और keys tune करो।

---

## ➡️ Next Topic
**460. Caching Best Practices** - a checklist that combines everything from this section: keys, TTL, invalidation, privacy and safe defaults.

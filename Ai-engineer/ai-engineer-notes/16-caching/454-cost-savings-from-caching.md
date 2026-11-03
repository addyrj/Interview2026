
---

# 454. Cost Savings from Caching
# हिंदी में: Caching से Cost की बचत

---

## 🔵 Simple Definition (English)
Caching saves money by reusing a previous result instead of paying for a new LLM call. Savings = hit rate x cost of a call, minus the cost of running the cache itself (embeddings, Redis/Qdrant, engineering time). There are three layers: response cache, semantic cache, and provider **prompt caching** (cheaper repeated prefix tokens).

## 🔵 सरल परिभाषा (Hindi)
Caching पुराने result को दोबारा use करके नई LLM call का पैसा बचाता है। बचत = hit rate x एक call की cost, minus cache चलाने की cost (embeddings, Redis/Qdrant, engineering time)। तीन layers हैं: response cache, semantic cache और provider **prompt caching** (दोहराए गए prefix tokens सस्ते)।

---

## 🔴 Problem it Solves
Teams add a cache "because it is good" without measuring. Some caches save thousands of dollars; others cost more than they save (low hit rate, extra embedding calls, infra). We need a simple model to **predict and verify** savings before and after building.

## 🔴 यह क्यों बना? (Hindi)
Teams बिना measure किए cache जोड़ देती हैं। कुछ caches हज़ारों dollars बचाते हैं, कुछ बचत से ज़्यादा खर्च करवाते हैं (कम hit rate, extra embedding, infra)। हमें एक simple model चाहिए जो savings पहले **predict** और बाद में **verify** करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure baseline: requests/day, avg input tokens, avg output tokens, model price
Step 2 → Baseline cost = requests x (in x price_in + out x price_out)
Step 3 → Estimate hit rate h from logs (how many queries are repeats/paraphrases)
Step 4 → Cached cost = (1-h) x LLM cost + requests x cache_lookup_cost + infra
Step 5 → Savings = Baseline - Cached cost
Step 6 → Break-even h* = lookup_cost / llm_cost (hit rate needed to just break even)
Step 7 → Monitor real hit rate and $ saved per day; adjust threshold/TTL
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Baseline measure करो: requests/day, avg input/output tokens, model price
Step 2 → Baseline cost = requests x (in x price_in + out x price_out)
Step 3 → Logs से hit rate h estimate करो
Step 4 → Cached cost = (1-h) x LLM cost + lookup cost + infra
Step 5 → Savings = Baseline - Cached cost
Step 6 → Break-even h* = lookup_cost / llm_cost
Step 7 → असली hit rate और रोज़ की बचत monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200K classification requests/day, 1,500 input tokens (system prompt + retrieved chunks) and 250 output tokens on a mid-priced model. Many importers ask about the same top 500 products. A semantic cache with a 35% hit rate plus provider prompt caching for the 1,000-token static system prompt gives two savings stacked. **Amazon-style**: product Q&A ("Is this waterproof?") repeats heavily per product, so hit rates can be much higher than in free-form chat.

## 🟡 Real Example Hindi mein
**Tariff System**: रोज़ 200K requests, 1,500 input और 250 output tokens। ज़्यादातर importers वही top 500 products पूछते हैं। 35% semantic cache hit और 1,000-token static system prompt पर provider prompt caching, दोनों की बचत जुड़ती है। **Amazon-style**: product Q&A बार-बार repeat होते हैं, इसलिए hit rate ऊँचा रहता है।

---

## 💻 Code Example — Basic
```python
# Basic savings calculator (pure Python, runs offline). Prices are ILLUSTRATIVE.
def llm_cost(in_tok: int, out_tok: int, p_in: float, p_out: float) -> float:
    # price is dollars per 1M tokens, so divide by 1,000,000
    return in_tok * p_in / 1_000_000 + out_tok * p_out / 1_000_000

def savings(requests: int, hit_rate: float, per_call: float, lookup: float) -> float:
    baseline = requests * per_call                         # no cache at all
    with_cache = requests * (1 - hit_rate) * per_call + requests * lookup  # misses + lookups
    return baseline - with_cache                           # positive = cache pays off

per_call = llm_cost(1500, 250, p_in=0.15, p_out=0.60)      # illustrative mini-model prices
lookup = 20 * 0.02 / 1_000_000                             # ~20 embed tokens at $0.02/1M
print(f"cost per call: ${per_call:.6f}")                   # cost of one LLM call
print(f"daily saving: ${savings(200_000, 0.35, per_call, lookup):.2f}")  # at 35% hit rate
print(f"break-even hit rate: {lookup / per_call:.4%}")     # tiny: caches pay off fast
```

## 💻 Code Example — Advanced
```python
# Production: track real $ saved per request, async, with error handling
import time                                                # latency measurement
from dataclasses import dataclass, field                   # simple stats container
from typing import Awaitable, Callable, Optional           # type hints

@dataclass
class CacheStats:
    hits: int = 0                                          # number of cache hits
    misses: int = 0                                        # number of cache misses
    saved_usd: float = 0.0                                 # money not spent
    spent_usd: float = 0.0                                 # money spent on misses
    latency_saved_ms: float = field(default=0.0)           # rough time saved

    @property
    def hit_rate(self) -> float:                           # hits / total
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

class CostTracker:
    def __init__(self, p_in: float, p_out: float) -> None:
        self.p_in, self.p_out = p_in, p_out                # $ per 1M tokens
        self.stats = CacheStats()                          # running totals

    def cost(self, in_tok: int, out_tok: int) -> float:
        return (in_tok * self.p_in + out_tok * self.p_out) / 1_000_000

    async def call(
        self,
        get: Callable[[str], Awaitable[Optional[dict]]],   # cache lookup
        llm: Callable[[str], Awaitable[dict]],             # LLM call (returns answer + usage)
        put: Callable[[str, dict], Awaitable[None]],       # cache write
        q: str,
    ) -> dict:
        t0 = time.perf_counter()                           # start timer
        try:
            hit = await get(q)                             # try cache
        except Exception:
            hit = None                                     # cache error = miss
        if hit:
            self.stats.hits += 1                           # count hit
            # tokens stored with the entry tell us what we avoided paying:
            self.stats.saved_usd += self.cost(hit["in_tok"], hit["out_tok"])
            return hit
        res = await llm(q)                                 # real LLM call
        self.stats.misses += 1                             # count miss
        self.stats.spent_usd += self.cost(res["in_tok"], res["out_tok"])
        try:
            await put(q, res)                              # fill cache
        except Exception:
            pass                                           # write failure is not fatal
        return res
```

---

## 🟠 FastAPI Integration
Expose the stats so finance and engineers can see savings in real time.

```python
from fastapi import FastAPI                                # web framework

app = FastAPI()
tracker = CostTracker(p_in=0.15, p_out=0.60)               # illustrative prices

@app.get("/metrics/cache-savings")
async def cache_savings() -> dict:
    s = tracker.stats                                      # current counters
    return {
        "hit_rate": round(s.hit_rate, 4),                  # fraction of hits
        "saved_usd": round(s.saved_usd, 4),                # avoided spend
        "spent_usd": round(s.spent_usd, 4),                # actual spend
        "net_saving_pct": round(100 * s.saved_usd / max(s.saved_usd + s.spent_usd, 1e-9), 1),
    }
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `get_openai_callback()` reports tokens and cost per call; with `set_llm_cache(...)` a hit makes no API call, so the callback shows zero tokens for it. Compare cost with and without cache on the same test set.

```python
from langchain_core.globals import set_llm_cache           # global cache switch
from langchain_core.caches import InMemoryCache            # simple cache for tests
from langchain_openai import ChatOpenAI                    # chat model

set_llm_cache(InMemoryCache())                             # enable caching
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)       # temp 0 for cacheable output
await llm.ainvoke("HS code for laptop?")                   # miss: tokens billed
await llm.ainvoke("HS code for laptop?")                   # hit: no API call, no tokens
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Counting only hit rate, ignoring cost of a hit
```python
# Wrong — "60% hit rate = 60% savings"
saving = 0.60 * baseline

# Correct — subtract lookup/embedding/infra cost and account for token size per hit
saving = baseline - ((1 - h) * baseline + requests * lookup + infra)
```

❌ Mistake 2: Mixing up the two kinds of savings
```python
# Wrong — assuming prompt caching removes the call; it only discounts repeated prefix tokens
# Correct — response/semantic cache removes the call; provider prompt caching reduces the
# price of the static prefix (illustratively ~90% cheaper reads on Anthropic, ~50% on OpenAI).
```

❌ Mistake 3: Measuring savings on test traffic
```python
# Wrong — synthetic queries repeat 100% so hit rate looks great
# Correct — replay a sample of real production logs
```

---

## 🧠 Tricky Interview Question
**Q**: "Cache hit rate is 50% yet your LLM bill dropped only 15%. Why?"

**Answer**: Hits are not equal. Cheap short queries are cached more often, while long expensive requests (big RAG context, many output tokens) miss. Weighted by tokens, the savings are lower than the count-based hit rate. Also output-token-heavy calls cost more per token. Report a **cost-weighted hit rate** (saved dollars / baseline dollars), not just a count-based one. Other causes: embedding costs, TTL evictions, and cache writes for entries never reused.

---

## ⚫ Interview Questions + Answers

Q1: What are the main caching layers for LLM apps?
A1: Exact response cache (Redis), semantic cache (vector DB), and provider prompt caching (discounted repeated prefix tokens).

Q2: What is break-even hit rate?
A2: The hit rate where savings equal cache overhead: `lookup_cost / llm_cost_per_call`. Usually very low, because lookups are much cheaper than LLM calls.

Q3: How would you forecast savings before building a cache?
A3: Take 1-2 weeks of production logs, normalise and cluster queries (exact and by embedding), compute the share of repeats, multiply by token costs, subtract overhead.

Q4: How does prompt caching differ from response caching?
A4: Prompt caching still calls the model with new output but charges less for the repeated prefix and cuts latency. Response caching skips the call entirely, but can return stale or wrong answers.

Q5: (Hard) Design a system to prove cache ROI to finance.
A5: Log per request: cache status, tokens, model, tenant. Compute counterfactual cost for hits using stored token counts. Run an A/B holdout (say 2% of traffic bypasses the cache) to measure true savings and check answer quality. Dashboard: cost-weighted hit rate, $ saved, p95 latency, quality score of cached vs fresh.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large volume with repeated or similar queries
- Long static prefixes (system prompt, tool definitions, documents)
- You can measure hit rate and quality

❌ Avoid when:
- Low volume (savings smaller than engineering effort)
- Highly personalised or real-time answers
- Quality risk of a stale answer is bigger than the savings

---

## 📊 Visual Diagram
```
 Baseline:  1000 req x $0.001 = $1.00
 
 With cache (hit rate 40%):
   400 hits   x $0.00002 (lookup)  = $0.008
   600 misses x $0.001   (LLM)     = $0.600
   infra                           = $0.050
                                    --------
   Total                           = $0.658    -> saving ~34%
```
(Numbers are illustrative.)

---

## 💰 Cost Impact
- Token usage: hits use 0 LLM tokens; misses use full input + output tokens plus a small embedding.
- Biggest levers: raise hit rate on **expensive** queries, shorten output (`max_tokens`), put static content first for provider prompt caching, route easy queries to a small model.
- Always compute **net** savings: baseline minus (misses + lookups + infra).
- All prices here are illustrative; verify current rates.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hit rate | Share of requests served from cache | cache से मिले requests का हिस्सा |
| Break-even | Point where savings equal overhead | जहाँ बचत = खर्च |
| Cost-weighted hit rate | Hit rate by dollars, not count | dollar के हिसाब से hit rate |
| Prompt caching | Discounted repeated prefix tokens | दोहराए prefix पर छूट |
| Holdout | Traffic that skips cache for measuring | तुलना के लिए बिना cache traffic |
| Overhead | Cost of running the cache | cache चलाने का खर्च |

---

## ⚡ 3-Line Summary
English: Savings come from hit rate times the cost of a call, minus cache overhead. Measure cost-weighted hit rate on real logs, not toy traffic. Combine response/semantic caching with provider prompt caching for the biggest effect.
Hindi: बचत = hit rate x call की cost, minus cache का overhead। असली logs पर cost-weighted hit rate measure करो, नकली traffic पर नहीं। Response/semantic cache और provider prompt caching मिलाकर सबसे ज़्यादा बचत मिलती है।

---

## ➡️ Next Topic
**455. Cache Hit Rate Optimization** — now that we know hits equal savings, how to increase the hit rate safely.

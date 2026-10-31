---

# 460. Caching Best Practices
# हिंदी में: Caching के Best Practices

---

## 🔵 Simple Definition (English)
Caching best practices are rules that make an LLM cache safe and useful: build good keys, set TTLs, invalidate when data changes, never mix users' private data, and always measure. Done right, caching cuts cost and latency. Done wrong, it returns wrong or leaked answers.

## 🔵 सरल परिभाषा (Hindi)
Caching best practices वे नियम हैं जो LLM cache को सुरक्षित और उपयोगी बनाते हैं: अच्छी keys बनाओ, TTL सेट करो, data बदलने पर invalidate करो, users का private data कभी mix मत करो, और हमेशा measure करो। सही करने पर cost और latency घटती है; गलत करने पर गलत या leak हुए जवाब मिलते हैं।

---

## 🔴 Problem it Solves
Naive caching causes real incidents: user A's answer shown to user B, a changed tariff rate served for weeks, a new prompt version still hitting old cached outputs, or a cache stampede when a hot key expires. Best practices prevent these known failures.

## 🔴 यह क्यों बना? (Hindi)
Naive caching से असली incidents होते हैं: user A का जवाब user B को दिखना, बदली हुई tariff दर हफ्तों तक पुरानी दिखना, नया prompt version होने पर भी पुराने cached outputs मिलना, या hot key expire होने पर cache stampede। Best practices इन जानी-पहचानी गलतियों को रोकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide WHAT is cacheable (deterministic, non-personal, repeated)
Step 2 → Build key = hash(model + prompt_version + normalized input + params + tenant)
Step 3 → Set TTL by data volatility (rates: short, definitions: long)
Step 4 → Add jitter to TTL and a lock to stop stampedes
Step 5 → Invalidate on events (rule update, prompt change, model change)
Step 6 → Never cache errors, refusals or low-confidence outputs
Step 7 → Monitor hit rate and audit quality
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → तय करो क्या cache हो सकता है (deterministic, non-personal, बार-बार आने वाला)
Step 2 → key = hash(model + prompt_version + normalized input + params + tenant)
Step 3 → Data कितना बदलता है उसके हिसाब से TTL (rates: छोटा, definitions: लंबा)
Step 4 → TTL में jitter और stampede रोकने के लिए lock लगाओ
Step 5 → Events पर invalidate करो (rule update, prompt change, model change)
Step 6 → Errors, refusals, low-confidence outputs कभी cache मत करो
Step 7 → Hit rate monitor करो और quality audit करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Key = `tariff:v3:gpt-4o-mini:t0:tenant42:sha256(normalized description)`. The `v3` is the prompt version; when the prompt changes to `v4`, old entries are naturally ignored. Duty-rate answers get a 24-hour TTL; HS-chapter definitions get 30 days. When customs publishes a new notification, an event deletes keys with the prefix `tariff:rates:`.

**Amazon AI**: Product Q&A answers are cached per product id, but answers that use a customer's order history are never cached.

## 🟡 Real Example Hindi mein
**Tariff System**: Key = `tariff:v3:gpt-4o-mini:t0:tenant42:sha256(normalized description)`। `v3` prompt version है; prompt `v4` होने पर पुरानी entries अपने आप ignore हो जाती हैं। Duty-rate जवाबों की TTL 24 घंटे, HS-chapter definitions की 30 दिन। Customs नया notification निकाले तो event `tariff:rates:` prefix वाली keys delete करता है।

**Amazon AI**: Product Q&A जवाब product id के हिसाब से cache होते हैं, लेकिन जो जवाब customer की order history use करते हैं वे कभी cache नहीं होते।

---

## 💻 Code Example — Basic
```python
# Basic: safe cache key + TTL cache. Pure Python, runs directly.
import hashlib  # for stable hashing
import time  # for TTL


def make_key(model: str, prompt_version: str, text: str, tenant: str) -> str:
    normalized = " ".join(text.lower().split())  # lowercase, collapse spaces
    digest = hashlib.sha256(normalized.encode()).hexdigest()[:16]  # short stable hash
    return f"{tenant}:{model}:{prompt_version}:{digest}"  # tenant keeps users apart


class TTLCache:
    def __init__(self) -> None:
        self.data: dict[str, tuple[float, str]] = {}  # key -> (expiry, value)

    def set(self, key: str, value: str, ttl_s: int) -> None:
        self.data[key] = (time.time() + ttl_s, value)  # store with expiry

    def get(self, key: str) -> str | None:
        item = self.data.get(key)  # fetch
        if item is None or item[0] < time.time():  # missing or expired
            self.data.pop(key, None)  # clean up
            return None
        return item[1]  # still valid


c = TTLCache()  # new cache
k1 = make_key("gpt-4o-mini", "v3", "Cotton  T-Shirt", "tenant42")
k2 = make_key("gpt-4o-mini", "v3", "cotton t-shirt", "tenant42")
print(k1 == k2)  # True: normalization makes both queries share one entry
c.set(k1, "6109.10", ttl_s=60)  # cache the answer
print(c.get(k2))  # 6109.10
```

## 💻 Code Example — Advanced
```python
# Production: jitter TTL, stampede lock, never-cache rules, async
import asyncio  # async primitives
import random  # TTL jitter
import time  # clock
from typing import Awaitable, Callable  # type hints


class SafeCache:
    def __init__(self) -> None:
        self.data: dict[str, tuple[float, str]] = {}  # storage
        self.locks: dict[str, asyncio.Lock] = {}  # per-key lock

    def _ttl(self, base_s: int) -> float:
        return base_s * random.uniform(0.9, 1.1)  # +-10% so keys do not expire together

    def _get(self, key: str) -> str | None:
        item = self.data.get(key)  # lookup
        if item and item[0] > time.time():  # valid
            return item[1]
        return None

    @staticmethod
    def cacheable(answer: str, confidence: float) -> bool:
        if not answer or answer.startswith("ERROR"):  # never cache errors
            return False
        if "cannot help" in answer.lower():  # never cache refusals
            return False
        return confidence >= 0.8  # only confident answers

    async def get_or_compute(
        self,
        key: str,
        compute: Callable[[], Awaitable[tuple[str, float]]],
        ttl_s: int,
    ) -> str:
        hit = self._get(key)  # fast path
        if hit is not None:
            return hit
        lock = self.locks.setdefault(key, asyncio.Lock())  # one lock per key
        async with lock:  # only one coroutine recomputes
            hit = self._get(key)  # re-check after waiting
            if hit is not None:
                return hit
            try:
                answer, conf = await asyncio.wait_for(compute(), timeout=20)  # bounded LLM call
            except asyncio.TimeoutError:
                return "ERROR: timeout"  # not cached
            if self.cacheable(answer, conf):  # apply rules
                self.data[key] = (time.time() + self._ttl(ttl_s), answer)
            return answer


async def llm() -> tuple[str, float]:
    await asyncio.sleep(0.05)  # fake latency
    return "6109.10", 0.93


async def main() -> None:
    cache = SafeCache()
    # 10 concurrent identical requests -> only 1 LLM call because of the lock
    results = await asyncio.gather(*[cache.get_or_compute("k", llm, 60) for _ in range(10)])
    print(set(results))  # {'6109.10'}


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Header  # framework + header access
from pydantic import BaseModel  # validation

app = FastAPI()
cache = SafeCache()  # from the advanced example


class Req(BaseModel):
    description: str  # product text


@app.post("/classify")
async def classify(body: Req, x_tenant: str = Header(...)) -> dict[str, str]:
    key = make_key("gpt-4o-mini", "v3", body.description, x_tenant)  # tenant-scoped key

    async def compute() -> tuple[str, float]:
        return "6109.10", 0.9  # replace with a real LLM call

    return {"hs_code": await cache.get_or_compute(key, compute, ttl_s=86_400)}


@app.delete("/cache/{prefix}")
async def invalidate(prefix: str) -> dict[str, int]:
    keys = [k for k in cache.data if k.startswith(prefix)]  # find by prefix
    for k in keys:
        cache.data.pop(k, None)  # delete
    return {"deleted": len(keys)}  # protect this route with auth in real life
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `set_llm_cache` caches by (prompt, llm_string), and `llm_string` already includes model parameters. For LangGraph, cache a node's result (for example a retrieval node) with a key based on its inputs, and put the prompt version in the key.

```python
from langchain_core.caches import InMemoryCache  # simple cache
from langchain_core.globals import set_llm_cache  # global setting
from langchain_openai import ChatOpenAI  # chat model

set_llm_cache(InMemoryCache())  # use RedisCache or SQLiteCache in production
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature 0 = cacheable
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Key without tenant or prompt version
✅ Correct: Include both.

```python
# Wrong
key = text
# Right
key = f"{tenant}:{prompt_version}:{model}:{sha256(text)}"
```

❌ Mistake 2: Caching high-temperature or personalised output
✅ Correct: Cache only temperature 0 / deterministic, non-personal outputs.

```python
# Wrong
cache.set(key, creative_story)  # temperature 1.0, different every time
# Right
if temperature == 0 and not uses_user_data:
    cache.set(key, answer)
```

---

## 🧠 Tricky Interview Question
**Q**: "You deploy a new system prompt but users still see old-style answers for a day. Why, and how to prevent it?"

**Answer**: The cache key did not include the prompt version, so old entries were still valid. Include a prompt/version hash in the key (or bump a namespace). Then a prompt release naturally orphans old entries; they expire by TTL.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What should go in a cache key for LLM calls?
A1: Model, prompt version, normalized input, key parameters (temperature), and tenant/user scope.

Q2: [Easy] What is TTL?
A2: Time to live: how long an entry stays valid before it expires.

Q3: [Medium] What is a cache stampede and the fix?
A3: Many requests recompute the same expired key at once. Fix with per-key locks, TTL jitter, and serving stale data while refreshing in the background.

Q4: [Medium] What should never be cached?
A4: Errors, refusals, low-confidence answers, personalised answers, and anything with secrets or PII unless scoped and encrypted.

Q5: [Hard] Design invalidation for a tariff system when rules change daily.
A5: Version keys by a "rules_version" stored in the key; bump it when a new notification is ingested. Keep short TTLs for rate answers, long TTLs for static definitions, and add an event-driven prefix delete. Audit a sample of hits against fresh answers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Queries repeat (FAQs, classification of common goods)
- Output is deterministic at temperature 0
- Latency and cost matter

❌ Avoid when:
- Answers depend on private user context
- Data changes every few seconds
- You cannot invalidate reliably

---

## 📊 Visual Diagram
```
 input ─► normalize ─► key = tenant|model|prompt_v|hash
                         │
                    ┌────▼────┐   hit    ┌────────┐
                    │  Cache  ├─────────►│ return │
                    └────┬────┘          └────────┘
                      miss│ (lock + jitter)
                         ▼
                      LLM call ─► cacheable? ─yes─► store with TTL
                                       │no
                                       └─► return only
```

---

## 💰 Cost Impact
A good cache can remove 30-60% of repeated calls. At 1M queries/month with 700 tokens on gpt-4o-mini (about $0.0002 per call), a 40% hit rate saves about $80/month; on gpt-4o the same traffic saves far more. Bad keys cost money too: a missing normalization step can halve the hit rate. Optimise by normalizing input, using long TTLs for static data, and combining with provider prompt caching for the misses.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache key | Unique id of a request | request की पहचान |
| Normalization | Clean input to one form | input को एक जैसा बनाना |
| Invalidation | Remove outdated entries | पुरानी entries हटाना |
| Jitter | Random TTL offset | TTL में random अंतर |
| Stampede | Many recomputes at once | एक साथ कई recompute |
| Tenant | One customer/org | एक customer/organization |

---

## ⚡ 3-Line Summary
English: Build keys from model, prompt version, normalized input and tenant. Use TTL with jitter, locks and event-based invalidation. Never cache errors, refusals or personal data, and always measure.
Hindi: Keys model, prompt version, normalized input और tenant से बनाओ। TTL के साथ jitter, locks और event-based invalidation use करो। Errors, refusals या personal data कभी cache मत करो, और हमेशा measure करो।

---

## ➡️ Next Topic
**461. AI Safety - Why Critical** - caching is done, so we start the guardrails section: why safe behaviour matters before shipping an LLM.

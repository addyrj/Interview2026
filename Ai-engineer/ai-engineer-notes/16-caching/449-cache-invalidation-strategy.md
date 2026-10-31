---

# 449. Cache Invalidation Strategy
# हिंदी में: Cache Invalidation की रणनीति

---

## 🔵 Simple Definition (English)
Cache invalidation is deciding when a cached LLM answer is no longer valid and must be removed or refreshed. Reasons: the underlying data changed, the prompt or model changed, the answer was wrong, or time passed. It is famously hard because a stale answer looks exactly like a fresh one.

## 🔵 सरल परिभाषा (Hindi)
Cache invalidation का मतलब है तय करना कि cached LLM जवाब कब अमान्य हो गया और उसे हटाना या ताज़ा करना है। कारण: असली data बदल गया, prompt या model बदला, जवाब गलत निकला, या समय बीत गया। यह मुश्किल इसलिए है कि पुराना जवाब बिल्कुल ताज़े जैसा दिखता है।

---

## 🔴 Problem it Solves
- Customs duty rates change on a budget day; cached answers still show the old rate: legal and money risk.
- You improve the prompt, but users keep getting answers from the old prompt.
- A bad answer got cached and is served 10,000 times.

## 🔴 यह क्यों बना? (Hindi)
- Budget के दिन customs duty rates बदलते हैं; cached जवाब पुराना rate दिखाते हैं: कानूनी और पैसे का जोखिम।
- आपने prompt सुधारा, पर users को पुराने prompt के जवाब मिलते रहते हैं।
- एक गलत जवाब cache हो गया और 10,000 बार दिया गया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide freshness rules per data type (rates: short TTL, product definitions: long TTL)
Step 2 → Version the key: llm:{prompt_v}:{model}:{data_v}:{hash}
Step 3 → Time-based: TTL expires entries automatically
Step 4 → Event-based: when source data changes, bump data_v or delete tagged keys
Step 5 → Manual: admin endpoint to purge by tag/tenant/pattern, used for bad answers
Step 6 → Soft expiry: serve stale while refreshing in background (stale-while-revalidate)
Step 7 → Monitor: log age of served answers and purge counts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर data type के लिए freshness नियम (rates: छोटा TTL, product definitions: लंबा TTL)
Step 2 → Key में version डालो: llm:{prompt_v}:{model}:{data_v}:{hash}
Step 3 → Time-based: TTL से entries अपने-आप expire
Step 4 → Event-based: source data बदले तो data_v बढ़ाओ या tagged keys delete करो
Step 5 → Manual: tag/tenant/pattern से purge करने वाला admin endpoint, गलत जवाब के लिए
Step 6 → Soft expiry: पुराना जवाब दो और background में refresh (stale-while-revalidate)
Step 7 → Monitor: दिए गए जवाबों की उम्र और purge की गिनती log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The customs authority publishes schedule version "2026-04". Our key contains `data_v=2026-04`. When the new schedule arrives we change one config value and all old answers become unreachable instantly (no mass delete). Old keys die by TTL. If a broker reports a wrong HS code, an admin purges the tag `product:steel-bottle`.
**Amazon-style**: Product price/stock summaries use 5-minute TTL plus an event purge when the catalogue service publishes "price changed".

## 🟡 Real Example Hindi mein
**Tariff System**: Customs authority schedule का version "2026-04" जारी करती है। हमारी key में `data_v=2026-04` है। नया schedule आने पर एक config value बदलते हैं और पुराने सारे जवाब तुरंत पहुँच से बाहर हो जाते हैं (mass delete नहीं)। पुरानी keys TTL से मर जाती हैं। कोई broker गलत HS code बताए तो admin tag `product:steel-bottle` purge कर देता है।
**Amazon-style**: Product price/stock summaries का TTL 5 मिनट, और catalogue service "price changed" event भेजे तो purge।

---

## 💻 Code Example — Basic
```python
# Basic: version-in-key + tag purge + TTL, all in pure Python (offline, runnable).
import hashlib  # hashing for keys
import time  # expiry


class Cache:
    def __init__(self) -> None:
        self.data: dict[str, tuple[str, float]] = {}  # key -> (value, expiry time)
        self.tags: dict[str, set[str]] = {}  # tag -> set of keys

    def set(self, key: str, value: str, ttl: int, tags: list[str]) -> None:
        self.data[key] = (value, time.time() + ttl)  # store with expiry
        for t in tags:  # remember which keys belong to each tag
            self.tags.setdefault(t, set()).add(key)

    def get(self, key: str) -> str | None:
        v = self.data.get(key)  # fetch entry
        if not v or time.time() > v[1]:  # missing or expired
            self.data.pop(key, None)  # clean up
            return None
        return v[0]

    def purge_tag(self, tag: str) -> int:
        keys = self.tags.pop(tag, set())  # keys under this tag
        for k in keys:
            self.data.pop(k, None)  # delete each
        return len(keys)  # how many removed


PROMPT_V, DATA_V = "p3", "2026-04"  # bump either to invalidate everything


def key(question: str) -> str:
    h = hashlib.sha256(question.lower().encode()).hexdigest()[:16]  # short hash
    return f"llm:{PROMPT_V}:{DATA_V}:{h}"  # versioned key


if __name__ == "__main__":
    c = Cache()  # new cache
    k = key("hs code steel bottle")
    c.set(k, "7323.93", ttl=60, tags=["product:steel-bottle"])  # store answer
    print(c.get(k))  # hit
    print("purged:", c.purge_tag("product:steel-bottle"))  # admin purge by tag
    print(c.get(k))  # None after purge
    DATA_V = "2026-05"  # new schedule -> new keys, old ones unreachable
    print(key("hs code steel bottle") == k)  # False
```

## 💻 Code Example — Advanced
```python
# Production: Redis with tag sets, version bump, stale-while-revalidate, async + error handling.
from __future__ import annotations

import asyncio  # background refresh
import json  # serialisation
import logging  # logging
import time  # timestamps
from typing import Awaitable, Callable

import redis.asyncio as redis  # async redis

log = logging.getLogger("invalidate")  # logger


class VersionedCache:
    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self.r = redis.from_url(url, decode_responses=True)  # shared pool

    async def data_version(self) -> str:
        return await self.r.get("cfg:data_v") or "0"  # current data version (bumped on updates)

    async def bump_version(self) -> int:
        return await self.r.incr("cfg:data_v")  # atomic: invalidates all keys that contain old version

    async def purge_tag(self, tag: str) -> int:
        members = await self.r.smembers(f"tag:{tag}")  # keys for this tag
        if members:
            await self.r.delete(*members)  # delete all keys
        await self.r.delete(f"tag:{tag}")  # delete tag set
        return len(members)

    async def get_or_compute(
        self,
        base_key: str,
        compute: Callable[[], Awaitable[str]],  # async function calling the LLM
        ttl: int = 3600,  # hard expiry
        soft_ttl: int = 600,  # after this, refresh in background
        tags: list[str] | None = None,
    ) -> str:
        key = f"llm:{await self.data_version()}:{base_key}"  # versioned key
        try:
            raw = await self.r.get(key)  # try cache
        except redis.RedisError as exc:
            log.warning("redis down: %s", exc)
            return await compute()  # fail open
        if raw:
            entry = json.loads(raw)  # {"v":..., "t":...}
            if time.time() - entry["t"] > soft_ttl:  # stale but usable
                asyncio.create_task(self._refresh(key, compute, ttl, tags))  # refresh without blocking user
            return entry["v"]  # serve stale-while-revalidate
        return await self._refresh(key, compute, ttl, tags)  # cold miss

    async def _refresh(self, key: str, compute, ttl: int, tags: list[str] | None) -> str:
        value = await compute()  # call LLM
        try:
            await self.r.set(key, json.dumps({"v": value, "t": time.time()}), ex=ttl)  # save with timestamp
            for t in tags or []:
                await self.r.sadd(f"tag:{t}", key)  # index by tag
        except redis.RedisError as exc:
            log.warning("cache write failed: %s", exc)
        return value
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Header, HTTPException  # web
from pydantic import BaseModel

app = FastAPI()
vc = VersionedCache()  # from the code above


class In(BaseModel):
    product: str


@app.post("/classify")
async def classify(body: In) -> dict:
    async def compute() -> str:
        return await call_llm(body.product)  # your async LLM function
    answer = await vc.get_or_compute(body.product.lower(), compute, tags=[f"product:{body.product.lower()}"])
    return {"answer": answer}


def admin(x_admin_token: str = Header(...)) -> None:
    if x_admin_token != "change-me":  # use real secret management in production
        raise HTTPException(status_code=403)


@app.post("/admin/purge/{tag}", dependencies=[Depends(admin)])
async def purge(tag: str) -> dict:
    return {"purged": await vc.purge_tag(tag)}  # manual invalidation endpoint


@app.post("/admin/new-schedule", dependencies=[Depends(admin)])
async def new_schedule() -> dict:
    return {"data_version": await vc.bump_version()}  # invalidate everything at once
```

---

## 🔗 LangChain / LangGraph Connection
`set_llm_cache` keys include the prompt and model string, so editing a prompt template invalidates automatically. But changes in retrieved data or parsing are NOT in the key. Call `get_llm_cache().clear()` on deploys, or build a custom cache by subclassing `BaseCache` and adding a version prefix.

```python
from langchain_core.caches import BaseCache  # interface
from langchain_core.globals import get_llm_cache  # accessor
# On deploy / new schedule:
cache = get_llm_cache()  # current global cache
if cache is not None:
    cache.clear()  # drop every entry (simple but blunt)
# Better: subclass BaseCache and include DATA_V inside lookup/update keys.
```
In LangGraph, node `CachePolicy(key_func=...)` lets you add a data version to the node cache key.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `KEYS *` / `FLUSHALL` to invalidate in production
✅ Correct: Use version bump or tag sets; never block Redis with a full scan.

```python
# Wrong
for k in await r.keys("llm:*"): await r.delete(k)   # blocks Redis, deletes everything
# Right
await r.incr("cfg:data_v")                          # O(1), old keys unreachable
```

❌ Mistake 2: Caching error or refusal answers
✅ Correct: Cache only validated successful outputs.

```python
# Wrong
await r.set(k, answer)               # even if answer == "Sorry, I can't"
# Right
if is_valid_hs_code(answer):
    await r.set(k, answer, ex=ttl)
```

---

## 🧠 Tricky Interview Question
**Q**: "You bump the data version at midnight; at 00:00:01 every key misses and the LLM provider rate-limits you. What went wrong and how do you prevent it?"

**Answer**: Global invalidation causes a thundering herd: all traffic misses at once. Fixes: warm the cache for top-N queries before switching the version, use request coalescing (single-flight lock per key), stale-while-revalidate during rollout, a gradual rollout of the new version per tenant or percentage, and a rate limiter or queue in front of the LLM.

---

## ⚫ Interview Questions + Answers

Q1: Name three ways to invalidate a cache. (Easy)
A1: TTL expiry, explicit delete/purge (by key or tag), and versioned keys where a version bump makes old entries unreachable.

Q2: Why include prompt version and model in the key? (Easy)
A2: Different prompts or models produce different answers; without them users would get answers made by an old prompt or model.

Q3: What is stale-while-revalidate? (Medium)
A3: Serve the old cached value immediately and refresh it in the background, so users see low latency and the cache gets fresh data soon.

Q4: Compare version bump and tag purge. (Medium)
A4: Version bump: O(1), global, leaves garbage until TTL. Tag purge: targeted, needs extra index storage and deletes cost O(n). Use both: version for big changes, tags for targeted fixes.

Q5: How do you invalidate semantic-cache entries when a source document changes? (Hard)
A5: Store metadata with each entry (source doc ids, doc version). On document update, delete by metadata filter in the vector store (for example `doc_id` in payload), or include the doc version in the filter at query time so only entries built from the current version match. Also keep TTLs because related questions may depend on the document indirectly.

---

## 🔷 When to Use + When Not to Use
✅ Use explicit invalidation when:
- Data changes on a known event (rates, price, policy)
- Wrong answers must be removable quickly
- You deploy new prompts/models often

❌ Avoid complex invalidation when:
- Data never changes (pure definitions): simple long TTL is enough
- Cache is only for dev/testing

---

## 📊 Visual Diagram
```
 key = llm : prompt_v : model : data_v : hash(question)
                │         │        │
   edit prompt ─┘         │        └─ new tariff schedule
   switch model ──────────┘
 Events:  schedule update ──► INCR data_v ──► old keys unreachable ──► die by TTL
          bad answer ───────► purge_tag("product:x") ──► deleted now
          age > soft_ttl ───► serve stale + refresh in background
```

---

## 💰 Cost Impact
**Token usage**: Every invalidation turns future hits into misses and costs tokens again. A full flush for 100,000 daily lookups at 750 tokens could cost an extra ~75M tokens in a day (about $11 on gpt-4o-mini input alone) plus output.
**Optimisation**: targeted purges over global flushes, warm top queries, stale-while-revalidate, longer TTL for stable data, and single-flight locks so duplicates do not each call the LLM.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Invalidation | Removing or refreshing stale entries | पुरानी entries हटाना/ताज़ा करना |
| TTL | Auto-expiry time | अपने-आप expire होने का समय |
| Versioned key | Key with a version part | version वाली key |
| Tag purge | Delete all keys with a label | label वाली सब keys delete |
| Stale-while-revalidate | Serve old, refresh in background | पुराना दो, पीछे ताज़ा करो |
| Thundering herd | Everyone misses at once | सब एक साथ miss |

---

## ⚡ 3-Line Summary
English: Invalidate by TTL, by versioned keys, and by targeted purges. Put prompt, model and data versions in the key so changes expire answers automatically. Avoid mass flushes that cause thundering herds.
Hindi: TTL, versioned keys और targeted purge से invalidate करो। Key में prompt, model और data version रखो ताकि बदलाव पर जवाब अपने-आप बेकार हो जाएँ। Mass flush से बचो क्योंकि उससे thundering herd होता है।

---

## ➡️ Next Topic
**450. Cache TTL for LLM** — how to choose the right expiry time for each kind of LLM answer.

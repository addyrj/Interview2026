---

# 450. Cache TTL for LLM
# हिंदी में: LLM के लिए Cache TTL

---

## 🔵 Simple Definition (English)
TTL (time to live) is how many seconds a cached LLM answer stays valid before it is deleted automatically. Short TTL means fresher but more LLM calls. Long TTL means cheaper but riskier stale answers. The right TTL depends on how fast the underlying truth changes and how costly a wrong answer is.

## 🔵 सरल परिभाषा (Hindi)
TTL (time to live) वह समय (सेकंड में) है जितनी देर cached LLM जवाब मान्य रहता है, फिर अपने-आप delete हो जाता है। छोटा TTL = ज़्यादा ताज़ा पर ज़्यादा LLM calls। लंबा TTL = सस्ता पर पुराने जवाब का जोखिम। सही TTL इस पर निर्भर है कि असली सच्चाई कितनी जल्दी बदलती है और गलत जवाब कितना महंगा पड़ेगा।

---

## 🔴 Problem it Solves
- Without TTL the cache grows forever and answers go stale.
- One TTL for everything is wrong: a product definition can live for days, live stock for seconds.
- Many keys created together expire together and cause a burst of LLM calls.

## 🔴 यह क्यों बना? (Hindi)
- TTL के बिना cache बढ़ता रहता है और जवाब पुराने हो जाते हैं।
- सब चीज़ों के लिए एक TTL गलत है: product definition दिनों चल सकती है, live stock सेकंडों में बदलता है।
- साथ बनी बहुत सी keys साथ expire होकर LLM calls का तूफ़ान ला देती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify each endpoint by volatility (static / slow / fast / real-time)
Step 2 → Map class to TTL: static 7d, slow 24h, fast 5-15m, real-time 0 (no cache)
Step 3 → Set TTL at write time: SET key value EX ttl
Step 4 → Add random jitter (+-10 percent) so keys do not expire together
Step 5 → Sliding TTL (optional): refresh TTL on every hit for popular keys, with a max age cap
Step 6 → Measure hit rate vs staleness complaints; adjust
Step 7 → Align TTL with provider cache TTL where relevant (Anthropic 5m/1h prompt cache)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर endpoint को volatility से बाँटो (static / slow / fast / real-time)
Step 2 → वर्ग से TTL: static 7 दिन, slow 24 घंटे, fast 5-15 मिनट, real-time 0 (cache नहीं)
Step 3 → Write के समय TTL: SET key value EX ttl
Step 4 → +-10 प्रतिशत random jitter जोड़ो ताकि keys साथ expire न हों
Step 5 → Sliding TTL (वैकल्पिक): popular keys पर हर hit TTL बढ़ाओ, पर अधिकतम उम्र की सीमा रखो
Step 6 → Hit rate और staleness की शिकायतें नापो; समायोजित करो
Step 7 → ज़रूरत हो तो provider की cache TTL (Anthropic 5m/1h) से मिलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: HS code for "stainless steel bottle" changes only when the schedule changes (yearly), TTL 7 days with a version key. "Current duty rate for HS 7323" may change on budget day: TTL 1 hour. "Is shipment X cleared today?" is real-time and uses no cache.
**Zomato AI**: Restaurant description summary 12 hours; "is it open now / delivery time" never cached by LLM answer; fetched live and given to the LLM as context.

## 🟡 Real Example Hindi mein
**Tariff System**: "stainless steel bottle" का HS code सिर्फ़ schedule बदलने पर बदलता है (साल में एक बार), TTL 7 दिन और version key। "HS 7323 की मौजूदा duty rate" budget के दिन बदल सकती है: TTL 1 घंटा। "Shipment X आज clear हुआ?" real-time है, cache नहीं।
**Zomato AI**: Restaurant description summary 12 घंटे; "अभी खुला है / delivery time" का LLM जवाब कभी cache नहीं, live data निकालकर context में दो।

---

## 💻 Code Example — Basic
```python
# Basic: a TTL policy table and a tiny TTL cache with jitter. Pure Python, runs offline.
import random  # jitter
import time  # clock

TTL_POLICY: dict[str, int] = {  # seconds per data class
    "static": 7 * 86_400,  # product definitions
    "slow": 86_400,  # explanations, summaries
    "fast": 900,  # rates, prices
    "realtime": 0,  # never cache
}


def jittered(ttl: int, pct: float = 0.1) -> int:
    if ttl == 0:
        return 0  # nothing to jitter
    return int(ttl * random.uniform(1 - pct, 1 + pct))  # +-10 percent


class TTLCache:
    def __init__(self) -> None:
        self.d: dict[str, tuple[str, float]] = {}  # key -> (value, expires)

    def set(self, key: str, value: str, klass: str) -> bool:
        ttl = jittered(TTL_POLICY[klass])  # pick TTL by class
        if ttl <= 0:
            return False  # not cached
        self.d[key] = (value, time.time() + ttl)  # store
        return True

    def get(self, key: str) -> str | None:
        item = self.d.get(key)  # lookup
        if item is None or item[1] < time.time():  # missing or expired
            self.d.pop(key, None)
            return None
        return item[0]


if __name__ == "__main__":
    c = TTLCache()
    print(c.set("hs:steel-bottle", "7323.93", "static"))  # True
    print(c.set("clearance:X1", "cleared", "realtime"))  # False
    print(c.get("hs:steel-bottle"))  # 7323.93
    print([jittered(900) for _ in range(3)])  # three different TTLs near 900
```

## 💻 Code Example — Advanced
```python
# Production: per-route TTL, sliding TTL with max age, async Redis, error handling.
from __future__ import annotations

import json  # serialisation
import logging  # logging
import random  # jitter
import time  # timestamps
from dataclasses import dataclass

import redis.asyncio as redis  # async client

log = logging.getLogger("ttl")  # logger


@dataclass(frozen=True)
class TTLRule:
    ttl: int  # base TTL seconds
    sliding: bool = False  # extend on hit?
    max_age: int = 0  # absolute cap for sliding (0 = no cap)


RULES: dict[str, TTLRule] = {
    "hs_code": TTLRule(ttl=7 * 86_400, sliding=True, max_age=30 * 86_400),  # popular codes stay, capped
    "duty_rate": TTLRule(ttl=3_600),  # changes rarely but matters
    "summary": TTLRule(ttl=43_200),
}


class TTLStore:
    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self.r = redis.from_url(url, decode_responses=True)

    async def get(self, kind: str, key: str) -> str | None:
        rule = RULES[kind]  # fail loudly on unknown kind (KeyError) during development
        full = f"{kind}:{key}"
        try:
            raw = await self.r.get(full)
            if raw is None:
                return None
            obj = json.loads(raw)  # {"v": value, "born": ts}
            if rule.sliding:
                age = time.time() - obj["born"]  # age since first write
                if rule.max_age and age >= rule.max_age:
                    await self.r.delete(full)  # too old: force refresh
                    return None
                await self.r.expire(full, self._ttl(rule))  # extend life on every hit
            return obj["v"]
        except redis.RedisError as exc:
            log.warning("get failed: %s", exc)
            return None  # fail open

    async def set(self, kind: str, key: str, value: str) -> None:
        rule = RULES[kind]
        try:
            await self.r.set(f"{kind}:{key}", json.dumps({"v": value, "born": time.time()}), ex=self._ttl(rule))
        except redis.RedisError as exc:
            log.warning("set failed: %s", exc)

    @staticmethod
    def _ttl(rule: TTLRule) -> int:
        return max(1, int(rule.ttl * random.uniform(0.9, 1.1)))  # jitter
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema

app = FastAPI()
store = TTLStore()


class In(BaseModel):
    kind: str = "hs_code"  # hs_code | duty_rate | summary
    query: str


@app.post("/ask")
async def ask(body: In) -> dict:
    hit = await store.get(body.kind, body.query.lower())  # check cache
    if hit is not None:
        return {"answer": hit, "cached": True, "ttl_class": body.kind}
    answer = await call_llm(body.kind, body.query)  # your async LLM call
    await store.set(body.kind, body.query.lower(), answer)  # cache with the rule for this kind
    return {"answer": answer, "cached": False, "ttl_class": body.kind}
```
Return a `Cache-Control: max-age` header too when the client or CDN may cache.

---

## 🔗 LangChain / LangGraph Connection
`RedisCache(redis_=client, ttl=3600)` applies one TTL to all LLM calls. For different TTLs per chain create separate cache instances or use LangGraph node-level `CachePolicy(ttl=...)`.

```python
from langgraph.types import CachePolicy  # per-node cache policy
# builder.add_node("rate_lookup", rate_node, cache_policy=CachePolicy(ttl=3600))      # 1 hour
# builder.add_node("hs_classify", hs_node,   cache_policy=CachePolicy(ttl=7 * 86400)) # 7 days
# graph = builder.compile(cache=InMemoryCache())  # cache backend must be given at compile
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One huge TTL for all data
✅ Correct: TTL by data class.

```python
# Wrong
await r.set(k, v, ex=30 * 86400)   # rates cached for a month
# Right
await r.set(k, v, ex=RULES["duty_rate"].ttl)
```

❌ Mistake 2: Sliding TTL with no max age
✅ Correct: A hot key could live forever and never refresh. Always cap absolute age.

```python
# Wrong
await r.expire(k, 86400)                     # every hit extends forever
# Right
if age >= max_age: await r.delete(k)         # then refresh from LLM
```

---

## 🧠 Tricky Interview Question
**Q**: "Your cache TTL is 1 hour. A very popular query is cached at 10:00:00. At 11:00:00 the key expires and 2,000 concurrent users ask it. What happens, and how do you fix it?"

**Answer**: Cache stampede: all 2,000 miss and call the LLM at once (cost, rate limits, slow). Fixes: single-flight lock so one request recomputes while others wait or receive the stale value, probabilistic early refresh (refresh slightly before expiry), stale-while-revalidate, and jitter so many keys do not expire together.

---

## ⚫ Interview Questions + Answers

Q1: What is TTL? (Easy)
A1: Time to live: the number of seconds after which a cache entry is removed automatically.

Q2: Why add jitter? (Easy)
A2: To spread expirations so many keys do not expire at the same time and cause a burst of LLM calls.

Q3: How do you choose TTL for an LLM feature? (Medium)
A3: By volatility of the facts, cost of a stale answer, and cost of recomputing. Static facts: days. Business rates: minutes to hours. Real-time facts: do not cache the LLM answer.

Q4: Sliding vs fixed TTL? (Medium)
A4: Fixed expires a set time after write. Sliding extends on each access, good for popular items, but needs a max age or data can stay stale forever.

Q5: How does cache TTL relate to provider prompt-cache TTL? (Hard)
A5: They are different layers. Your response cache TTL decides how long answers are reused. Provider prompt cache (Anthropic 5 min or 1 hour, OpenAI minutes) only reduces input-token cost for the prefix. Choose the Anthropic TTL based on request spacing: if calls arrive every few minutes the 5-minute cache is refreshed by reads; for sparse traffic pay for the 1-hour write only if reads per hour justify the higher write price.

---

## 🔷 When to Use + When Not to Use
✅ Use long TTL when:
- Facts are stable (definitions, taxonomy)
- Recompute is expensive (large context)

❌ Use short or no TTL when:
- Data is volatile or legally sensitive (rates, compliance)
- The answer depends on the current time or live state

---

## 📊 Visual Diagram
```
 write ──────────────► time ───────────────────────────────►
 static   |██████████████████████████████████ 7 days ██████|x
 slow     |██████████ 24h ██████|x
 fast     |██ 15m ██|x
 realtime |x (not cached)
 jitter:  x lands at 0.9..1.1 of the TTL, so keys expire at different moments
 sliding: each hit pushes x to the right, but never past max_age
```

---

## 💰 Cost Impact
**Token usage**: Cost is roughly misses x tokens per call, and misses grow as TTL shrinks. Example: 20,000 requests a day for 2,000 distinct questions, 800 tokens each. With a 24h TTL: about 2,000 misses a day (1.6M tokens). With a 5-minute TTL most repeats expire, perhaps 10,000 misses (8M tokens), 5x more.
**Optimisation**: longest safe TTL per class, jitter, sliding with a cap for hot keys, and keep real-time facts out of cached answers by injecting them as live context.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Lifetime of a cache entry | entry की उम्र |
| Jitter | Random variation in TTL | TTL में random फ़र्क |
| Sliding TTL | TTL extends on access | हर access पर TTL बढ़ना |
| Max age | Absolute cap on lifetime | अधिकतम उम्र की सीमा |
| Stampede | Many requests recompute together | कई requests साथ recompute |
| Volatility | How fast data changes | data कितनी जल्दी बदलता है |

---

## ⚡ 3-Line Summary
English: Pick TTL by how fast the truth changes and how costly stale answers are. Add jitter and a max age for sliding TTLs. Never cache real-time facts as LLM answers.
Hindi: TTL इस हिसाब से चुनो कि सच्चाई कितनी जल्दी बदलती है और पुराने जवाब का नुकसान कितना है। Jitter लगाओ और sliding TTL में max age रखो। Real-time facts को LLM जवाब बनाकर cache मत करो।

---

## ➡️ Next Topic
**451. Cache Key Design** — what exactly goes into a key so that hits are safe and frequent.

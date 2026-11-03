
# 442. Exact Match Caching
# हिंदी में: Exact Match Caching

---

## 🔵 Simple Definition (English)
Exact match caching returns a stored answer only when the new request is identical to an earlier one after normalisation (same model, same parameters, same text). It uses a hash of the request as the key. It is fast, cheap and never returns a "similar but wrong" answer.

## 🔵 सरल परिभाषा (Hindi)
Exact match caching तभी stored answer लौटाता है जब नई request, normalisation के बाद, पहले वाली request से बिल्कुल एक जैसी हो (same model, same parameters, same text)। Request का hash key बनता है। यह तेज़, सस्ता है और कभी "मिलता-जुलता पर ग़लत" answer नहीं देता।

---

## 🔴 Problem it Solves
Many production requests are literally identical: the same product description sent by retries, batch re-runs, or a popular FAQ. Calling the LLM each time wastes money. A key-value lookup solves this with almost zero risk and no embedding cost.

## 🔴 यह क्यों बना? (Hindi)
Production की कई requests शब्दशः एक जैसी होती हैं: retries, batch re-runs या popular FAQ से वही product description। हर बार LLM call पैसे बर्बाद करती है। Key-value lookup लगभग zero risk और बिना embedding cost के यह हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise input: strip, lowercase (if meaning-safe), collapse whitespace, sort JSON keys
Step 2 → Build canonical key material: model + temperature + system prompt version + messages + tools
Step 3 → Hash it (SHA-256) -> fixed-length key, optionally with a namespace prefix ("tariff:v3:...")
Step 4 → GET key from store (dict / Redis)
Step 5 → HIT -> return value ; MISS -> call LLM
Step 6 → SET key with TTL (e.g. 24h) and optional tags for invalidation
Step 7 → Log hit/miss, tokens saved
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Input normalise करो: strip, lowercase (अर्थ सुरक्षित हो तो), whitespace collapse, JSON keys sort
Step 2 → Canonical key material: model + temperature + system prompt version + messages + tools
Step 3 → Hash (SHA-256) -> fixed-length key, चाहें तो namespace prefix ("tariff:v3:...")
Step 4 → Store (dict / Redis) से GET key
Step 5 → HIT -> value लौटाओ ; MISS -> LLM call
Step 6 → Key को TTL (जैसे 24h) और optional tags के साथ SET करो
Step 7 → Hit/miss और बचे tokens log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A nightly job re-classifies 200,000 catalogue items; 40% have identical descriptions to yesterday. Exact cache keyed on `tariff_schedule_version + model + normalised description` returns the stored HS code instantly. When the schedule version changes, keys change and the cache refreshes naturally.

**Amazon-style listings**: Identical seller titles repeated across variants (size, colour) map to the same category answer.

## 🟡 Real Example Hindi mein
**Tariff System**: Nightly job 200,000 catalogue items दोबारा classify करता है; 40% के descriptions कल जैसे ही हैं। `tariff_schedule_version + model + normalised description` वाला exact cache stored HS code तुरंत लौटाता है। Schedule version बदलते ही keys बदलती हैं और cache अपने आप refresh हो जाता है।

**Amazon-style listings**: Variants (size, colour) में दोहराए गए identical seller titles एक ही category answer पर map होते हैं।

---

## 💻 Code Example — Basic
```python
# Pure-Python exact-match cache with canonical keys (run directly)
import hashlib  # hashing
import json  # canonical serialisation
from typing import Any  # type hints


def canonical_key(model: str, messages: list[dict[str, str]], **params: Any) -> str:
    """Build a stable key: same logical request -> same key."""
    payload = {
        "model": model,  # which model
        "params": params,  # temperature, max_tokens...
        "messages": [{"role": m["role"], "content": " ".join(m["content"].split())} for m in messages],  # collapse spaces
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)  # sorted keys = deterministic
    return "tariff:v1:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()  # namespaced hash


if __name__ == "__main__":
    a = canonical_key("m", [{"role": "user", "content": "HS code  for earbuds"}], temperature=0)  # extra space
    b = canonical_key("m", [{"role": "user", "content": "HS code for earbuds"}], temperature=0)  # clean
    c = canonical_key("m", [{"role": "user", "content": "HS code for earbuds"}], temperature=0.7)  # other params
    print(a == b)  # True: whitespace normalised
    print(a == c)  # False: different temperature must not share a key
```

## 💻 Code Example — Advanced
```python
# Redis-backed exact cache (redis-py asyncio). Requires a running Redis; names follow redis-py >= 4.2.
import hashlib  # hashing
import json  # serialisation
import logging  # logs
from typing import Any, Awaitable, Callable  # types

import redis.asyncio as redis  # async Redis client

logger = logging.getLogger("exact-cache")  # logger


class ExactCache:
    def __init__(self, url: str = "redis://localhost:6379/0", ttl: int = 86_400, ns: str = "tariff:v1") -> None:
        self.r = redis.from_url(url, decode_responses=True)  # client
        self.ttl = ttl  # seconds
        self.ns = ns  # namespace (bump to invalidate everything)

    def key(self, model: str, prompt: str, **params: Any) -> str:
        blob = json.dumps({"m": model, "p": params, "q": " ".join(prompt.split())}, sort_keys=True)  # canonical
        return f"{self.ns}:{hashlib.sha256(blob.encode()).hexdigest()}"  # namespaced key

    async def get_or_call(
        self, model: str, prompt: str, llm: Callable[[str], Awaitable[str]], **params: Any
    ) -> tuple[str, bool]:
        k = self.key(model, prompt, **params)  # compute key
        try:
            hit = await self.r.get(k)  # try cache
            if hit is not None:  # found
                return hit, True  # (answer, cached)
        except redis.RedisError as exc:  # cache down must not break the app
            logger.warning("cache read failed: %s", exc)  # log and fall through
        answer = await llm(prompt)  # real call
        try:
            await self.r.set(k, answer, ex=self.ttl)  # store with TTL
        except redis.RedisError as exc:  # ignore write failures
            logger.warning("cache write failed: %s", exc)  # log
        return answer, False  # (answer, not cached)
```
Fail open: if Redis is down, call the LLM. Token usage on a hit: 0.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
# cache = ExactCache()  # created at startup in real code (see the advanced example)


class Req(BaseModel):
    description: str  # product text


async def fake_llm(prompt: str) -> str:
    return "8518.30"  # stand-in for the model


@app.post("/classify")
async def classify(req: Req) -> dict:
    # answer, cached = await cache.get_or_call("gpt-4o-mini", req.description, fake_llm, temperature=0)
    answer, cached = await fake_llm(req.description), False  # placeholder so the route is self-contained
    return {"hs_code": answer, "cached": cached}  # expose cached flag for metrics
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `InMemoryCache`, `SQLiteCache` and `RedisCache` (from `langchain-community`) are exact-match caches keyed on the prompt plus model parameters.

```python
from langchain_core.caches import InMemoryCache  # exact-match cache
from langchain_core.globals import set_llm_cache  # global setter
from langchain_openai import ChatOpenAI  # LLM

set_llm_cache(InMemoryCache())  # turn on exact caching
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # deterministic
llm.invoke("HS code for cotton t-shirt?")  # miss
llm.invoke("HS code for cotton t-shirt?")  # exact repeat -> hit
```
Note: a one-character difference ("t-shirt" vs "tshirt") is a miss: this is the weakness of exact matching.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Python's built-in `hash()` as the key
✅ Correct: `hash()` of strings changes between processes (hash randomisation). Use SHA-256.
```python
# Wrong
key = hash(prompt)
# Right
key = hashlib.sha256(prompt.encode()).hexdigest()
```

❌ Mistake 2: Over-normalising and merging different meanings
✅ Correct: Lowercasing is fine for most text, but not for case-sensitive codes or IDs. Normalise only what is meaning-safe.
```python
# Wrong: key from prompt.lower() when part numbers like "AbC-12" and "abc-12" differ
# Right: keep IDs as is, normalise only whitespace around them
```

---

## 🧠 Tricky Interview Question
**Q**: "Your exact cache hit rate is only 8% although users ask similar things all day. How can you raise it without semantic search?"

**Answer**: Improve key design: normalise whitespace, punctuation and casing; strip volatile parts (timestamps, request ids, user names) from the prompt before hashing and put them outside the cached call; canonicalise structured inputs (sort JSON keys, round numbers); split a big prompt into a cacheable stable part and a small dynamic part; and cache at sub-task level (for example "classify this product title") rather than whole conversations. If hit rate is still low, then consider semantic caching (443) knowing its risks.

---

## ⚫ Interview Questions + Answers

Q1: What is exact match caching?
A1: Caching where a stored response is reused only when the normalised request is identical.

Q2: Why include the model and temperature in the key?
A2: Different models or parameters produce different outputs; sharing a key would return wrong results.

Q3: What is the main downside?
A3: Low hit rate for paraphrased questions.

Q4: Why hash the key?
A4: Prompts can be huge; a SHA-256 digest gives a fixed-size, safe key for stores like Redis.

Q5: How do you invalidate entries safely when the tariff schedule updates?
A5: Put a `schedule_version` in the key or namespace so new data uses new keys (old ones expire by TTL), or tag entries and delete by tag. Version-in-key is simplest and atomic.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Requests are repeated verbatim (batch jobs, retries, templates)
- You need zero risk of wrong matches
- Low latency and simple infra are needed

❌ Avoid when:
- Users paraphrase heavily (low hit rate)
- Prompts include unique ids or timestamps you cannot strip
- Answers must reflect live data

---

## 📊 Visual Diagram
```
 "HS code  for Earbuds"
        |
   normalise  --> "hs code for earbuds"
        |
   key = sha256(model | params | text)
        |
     GET key
     /      \
  HIT       MISS
   |          |
 value     call LLM --> SET key (TTL)
```

---

## 💰 Cost Impact
Zero extra model tokens: only a hash and a lookup (microseconds in memory, around a millisecond for Redis). Example: nightly job of 200K items, 40% exact repeats, 600 tokens each: 48M tokens avoided per run. At an illustrative $0.15/1M input (output not counted), that is about $7 per run for the input side alone, and far more with larger models or output tokens.

Optimise: strong normalisation, stable prompt prefixes, sensible TTL, namespaces for versioning, and monitor hit rate by endpoint.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exact match | Identical input only | बिल्कुल वही input |
| Normalisation | Standardise input text | Input को standard करना |
| Canonical form | One agreed representation | एक तय रूप |
| SHA-256 | Hash function | Hash function |
| Namespace | Key prefix for versioning | Versioning के लिए prefix |
| Fail open | If cache fails, continue | Cache fail हो तो भी चलना |
| Hit rate | Share of requests served from cache | Cache से served requests का हिस्सा |

---

## ⚡ 3-Line Summary
English: Exact caching hashes the normalised request and returns the stored answer on identical repeats. It is safe and cheap but has a low hit rate for paraphrases. Include model, params and data version in the key.
Hindi: Exact caching normalised request का hash बनाकर identical repeats पर stored answer लौटाता है। यह सुरक्षित और सस्ता है पर paraphrases पर hit rate कम रहता है। Key में model, params और data version रखो।

---

## ➡️ Next Topic
**443. Semantic Caching** — match by meaning using embeddings to catch paraphrased questions.

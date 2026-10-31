---

# 451. Cache Key Design
# हिंदी में: Cache Key Design

---

## 🔵 Simple Definition (English)
A cache key is the string that identifies one cached LLM answer. A good key contains everything that can change the answer (model, prompt version, messages, parameters, tenant) and nothing that does not (timestamps, request ids). Too specific means no hits; too loose means wrong answers.

## 🔵 सरल परिभाषा (Hindi)
Cache key वह string है जो एक cached LLM जवाब की पहचान करती है। अच्छी key में वह सब होता है जो जवाब बदल सकता है (model, prompt version, messages, parameters, tenant) और वह कुछ नहीं जो नहीं बदलता (timestamp, request id)। ज़्यादा specific key = hits नहीं; ज़्यादा ढीली key = गलत जवाब।

---

## 🔴 Problem it Solves
- Key built from the question only: two tenants or two models share one answer (wrong).
- Key built with a timestamp or request id: nothing ever hits (useless cache).
- Whitespace or casing differences ("Steel Bottle" vs "steel bottle ") create duplicate entries.

## 🔴 यह क्यों बना? (Hindi)
- सिर्फ़ सवाल से बनी key: दो tenants या दो models एक जवाब बाँट लेते हैं (गलत)।
- Timestamp या request id वाली key: कभी hit नहीं (बेकार cache)।
- Whitespace या case का फ़र्क ("Steel Bottle" बनाम "steel bottle ") duplicate entries बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List everything that affects output: model, prompt_version, system, messages,
         temperature, top_p, max_tokens, tools, response schema, tenant, data_version
Step 2 → Normalise inputs: strip, collapse spaces, Unicode NFKC, optional lowercase (only if safe)
Step 3 → Build a canonical dict (fixed field names)
Step 4 → Serialise with sorted keys and compact separators
Step 5 → Hash (SHA-256) so the key has fixed length and hides raw text
Step 6 → Add readable prefix: app:env:tenant:version:hash
Step 7 → Test: same intent -> same key; different params -> different key
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → वह सब लिखो जो output बदलता है: model, prompt_version, system, messages,
         temperature, top_p, max_tokens, tools, response schema, tenant, data_version
Step 2 → Inputs normalise करो: strip, spaces collapse, Unicode NFKC, ज़रूरत हो तभी lowercase
Step 3 → Fixed field names वाला canonical dict बनाओ
Step 4 → sorted keys और compact separators के साथ serialise करो
Step 5 → Hash (SHA-256) करो ताकि key की लंबाई तय रहे और raw text छुपा रहे
Step 6 → पढ़ने लायक prefix जोड़ो: app:env:tenant:version:hash
Step 7 → Test: same intent -> same key; अलग params -> अलग key
```

---

## 🟡 Real World Example
**Tariff Classification System**: Key = `tariff:prod:{tenant}:p4:2026-04:{sha256(model, normalised product text, country, temperature)}`. "Cotton T-Shirt " and "cotton t-shirt" normalise to the same key. Importing to India vs the USA gives different keys because the country is part of the key, which is essential since duty rules differ.
**Amazon-style**: Product Q&A key includes product id and locale, so a Hindi answer is never served to an English user.

## 🟡 Real Example Hindi mein
**Tariff System**: Key = `tariff:prod:{tenant}:p4:2026-04:{sha256(model, normalised product text, country, temperature)}`। "Cotton T-Shirt " और "cotton t-shirt" एक ही key बनते हैं। India बनाम USA में import की keys अलग हैं क्योंकि country key का हिस्सा है, यह ज़रूरी है क्योंकि duty नियम अलग हैं।
**Amazon-style**: Product Q&A key में product id और locale है, इसलिए Hindi जवाब English user को नहीं मिलता।

---

## 💻 Code Example — Basic
```python
# Basic: canonical cache key builder. Pure Python, runs offline.
import hashlib  # SHA-256
import json  # canonical JSON
import re  # whitespace cleanup
import unicodedata  # Unicode normalisation


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # unify look-alike characters
    text = re.sub(r"\s+", " ", text).strip()  # collapse spaces, trim ends
    return text.lower()  # safe here: product names are case-insensitive


def make_key(model: str, text: str, country: str, temperature: float, tenant: str,
             prompt_v: str = "p1") -> str:
    canonical = {  # every field that changes the answer
        "model": model,
        "text": normalise(text),
        "country": country.upper(),
        "temperature": temperature,
        "prompt_v": prompt_v,
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)  # stable
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()  # fixed-length hash
    return f"tariff:{tenant}:{prompt_v}:{digest}"  # readable prefix + hash


if __name__ == "__main__":
    a = make_key("gpt-4o-mini", "Cotton  T-Shirt ", "in", 0.0, "acme")
    b = make_key("gpt-4o-mini", "cotton t-shirt", "IN", 0.0, "acme")
    c = make_key("gpt-4o-mini", "cotton t-shirt", "US", 0.0, "acme")
    d = make_key("gpt-4o-mini", "cotton t-shirt", "IN", 0.0, "other")
    print(a == b)  # True: same intent
    print(b == c)  # False: country differs
    print(b == d)  # False: tenant differs
    print(a)  # show a sample key
```

## 💻 Code Example — Advanced
```python
# Production: typed key builder (pydantic v2), versioned, async get-or-set helper with error handling.
from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel, Field

log = logging.getLogger("keys")


class KeyParts(BaseModel):
    """Everything allowed to influence the answer. Extra fields are rejected on purpose."""
    model_config = {"extra": "forbid"}  # forbid unknown fields -> no accidental volatile data

    tenant: str
    model: str
    prompt_v: str
    data_v: str
    text: str
    country: str = "IN"
    temperature: float = 0.0
    max_tokens: int = Field(default=300, ge=1)
    schema_hash: str = ""  # hash of the response schema/tools if used


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def build_key(p: KeyParts) -> str:
    d: dict[str, Any] = p.model_dump()
    d["text"] = _norm(d["text"])  # normalise only the free text
    d["country"] = d["country"].upper()
    blob = json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"llm:{p.tenant}:{p.prompt_v}:{p.data_v}:{hashlib.sha256(blob.encode()).hexdigest()}"


async def get_or_set(r: redis.Redis, p: KeyParts, compute, ttl: int = 86_400) -> tuple[str, bool]:
    key = build_key(p)  # deterministic key
    try:
        hit = await r.get(key)
        if hit is not None:
            return hit, True  # cache hit
    except redis.RedisError as exc:
        log.warning("get failed: %s", exc)
    value = await compute()  # call the LLM
    try:
        await r.set(key, value, ex=ttl)
    except redis.RedisError as exc:
        log.warning("set failed: %s", exc)
    return value, False
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()
rds = redis.from_url("redis://localhost:6379/0", decode_responses=True)


class In(BaseModel):
    product: str
    country: str = "IN"


@app.post("/classify")
async def classify(body: In, x_tenant: str = Header(...)) -> dict:
    parts = KeyParts(  # tenant comes from auth header, never from the prompt text
        tenant=x_tenant, model="gpt-4o-mini", prompt_v="p4", data_v="2026-04",
        text=body.product, country=body.country,
    )
    answer, hit = await get_or_set(rds, parts, lambda: call_llm(body.product, body.country))
    return {"answer": answer, "cache_hit": hit}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's default key is `(prompt string, llm_string)`. It does not contain tenant or data version. To control keys, subclass `BaseCache`:

```python
from langchain_core.caches import BaseCache  # base class
from langchain_core.outputs import Generation  # cached value type


class TenantCache(BaseCache):
    def __init__(self, store: dict, tenant: str, data_v: str) -> None:
        self.store, self.tenant, self.data_v = store, tenant, data_v  # simple dict backend

    def _k(self, prompt: str, llm_string: str) -> str:
        return f"{self.tenant}:{self.data_v}:{hash((prompt, llm_string))}"  # add tenant + version

    def lookup(self, prompt: str, llm_string: str):
        return self.store.get(self._k(prompt, llm_string))  # return list[Generation] or None

    def update(self, prompt: str, llm_string: str, return_val) -> None:
        self.store[self._k(prompt, llm_string)] = return_val  # store generations

    def clear(self, **kwargs) -> None:
        self.store.clear()  # wipe all
```
(For production use a stable hash such as SHA-256, since Python's `hash()` of strings changes per process.) LangGraph `CachePolicy(key_func=...)` plays the same role per node.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Python `hash()` for keys
✅ Correct: `hash()` of strings is randomised per process (PYTHONHASHSEED), so keys differ across pods and restarts. Use hashlib.

```python
# Wrong
key = str(hash(prompt))
# Right
key = hashlib.sha256(prompt.encode()).hexdigest()
```

❌ Mistake 2: Putting volatile fields in the key
✅ Correct: Leave out timestamps, request ids, trace ids, random seeds.

```python
# Wrong
key = f"{prompt}:{time.time()}"       # never hits
# Right
key = build_key(parts)                # only answer-affecting fields
```

---

## 🧠 Tricky Interview Question
**Q**: "Two different users ask 'summarise my last shipment'. The prompt text is identical, and your cache returns user A's summary to user B. What design error caused this and how do you fix it?"

**Answer**: The key contained only the text, but the answer depends on hidden context (user's data pulled by a tool or retrieval). Anything that influences the output must be in the key, including user or tenant id and the data version, or the call must be marked non-cacheable. Fix: add tenant and user scope, or skip caching for personalised prompts, and audit for data leaks.

---

## ⚫ Interview Questions + Answers

Q1: Why hash the prompt for the key? (Easy)
A1: Fixed length, safe characters, and raw text (which may be private) is not exposed in Redis keys or logs.

Q2: What happens if temperature is not in the key? (Easy)
A2: A temperature 0 answer could be served for a temperature 1 request, or the opposite. Parameters that change output belong in the key.

Q3: How does normalisation affect hit rate and safety? (Medium)
A3: It raises hit rate by merging trivially different inputs. Over-normalising (for example lowercasing case-sensitive codes like "IN" vs "in" in IDs) can merge different intents, so normalise only fields where it is semantically safe.

Q4: Why use a key prefix with versions? (Medium)
A4: It allows invalidation by version bump, easy debugging (SCAN by prefix), and per-tenant metrics and eviction.

Q5: Design keys for RAG answers. (Hard)
A5: Include normalised question, model, prompt version, tenant, retrieval config (top_k, embedding model) and an index/data version (or a hash of the retrieved chunk ids). Without the chunk ids or index version, an answer can stay cached after the knowledge base changes. Trade-off: including chunk ids lowers hit rate but guarantees the answer matches the evidence, so choose it for high-stakes domains such as customs.

---

## 🔷 When to Use + When Not to Use
✅ Use strict keys when:
- Several tenants, models, languages or prompt versions share a cache
- Wrong answers are costly (legal, finance, customs)

❌ Avoid over-specific keys when:
- Hit rate matters and fields do not change the answer (trace ids, whitespace)

---

## 📊 Visual Diagram
```
 raw request ─► normalise ─► canonical dict ─► sorted JSON ─► SHA-256
                                                  │              │
   fields IN key:  tenant, model, prompt_v,       │              ▼
   data_v, text, country, temperature, tools      │   tariff:acme:p4:2026-04:9f2c...
   fields NOT in key: timestamp, request_id ──────┘ (excluded)
```

---

## 💰 Cost Impact
**Token usage**: A bad key wastes tokens in two ways. Too specific: hit rate near 0, you pay full tokens every time. Too loose: wrong answers cause retries and support cost.
Example: 100,000 requests a day, 700 tokens each, key fixes lift hits from 10 to 45 percent: 35,000 fewer calls, about 24.5M tokens a day saved.
**Optimisation**: measure hit rate per key component (drop one field and see), normalise safely, and keep keys versioned.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache key | ID of a cached answer | cached जवाब की पहचान |
| Canonical form | One standard representation | एक मानक रूप |
| Normalisation | Cleaning input before hashing | hash से पहले input साफ़ करना |
| Namespace/prefix | Group label in key | key में group का नाम |
| Collision | Two inputs same key | दो inputs की एक key |
| Cache poisoning | Wrong data stored under a key | key के नीचे गलत data |

---

## ⚡ 3-Line Summary
English: A cache key must include every field that changes the answer and no volatile fields. Normalise text, serialise canonically, and hash with SHA-256 (never Python hash). Add tenant and version parts for safety and invalidation.
Hindi: Cache key में वह हर field हो जो जवाब बदलता है और कोई volatile field नहीं। Text normalise करो, canonical serialise करो और SHA-256 से hash करो (Python hash कभी नहीं)। सुरक्षा और invalidation के लिए tenant और version जोड़ो।

---

## ➡️ Next Topic
**452. Semantic Cache with Redis** — when keys are meaning-based vectors instead of exact hashes.

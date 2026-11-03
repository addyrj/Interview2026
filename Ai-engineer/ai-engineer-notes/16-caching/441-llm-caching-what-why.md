
# 441. LLM Caching — What + Why
# हिंदी में: LLM Caching — क्या है और क्यों

---

## 🔵 Simple Definition (English)
LLM caching stores the result of an earlier model call and reuses it when the same (or a very similar) request comes again, instead of calling the model. It saves money (no tokens billed) and time (milliseconds instead of seconds).

## 🔵 सरल परिभाषा (Hindi)
LLM caching पिछली model call का result store करके, वही (या मिलता-जुलता) request दोबारा आने पर model call की जगह उसे reuse करता है। इससे पैसे बचते हैं (tokens bill नहीं होते) और समय भी (seconds की जगह milliseconds)।

---

## 🔴 Problem it Solves
Real traffic repeats. Many users ask "HS code for iPhone 15?" every day. Without a cache you pay for the same tokens again and wait for the same slow generation again. LLM calls cost money per token, take 1-10 seconds, and have rate limits. Caching cuts all three.

## 🔴 यह क्यों बना? (Hindi)
असली traffic दोहराता है। बहुत से users रोज़ "iPhone 15 का HS code?" पूछते हैं। Cache के बिना वही tokens दोबारा pay करने पड़ते हैं और वही धीमी generation दोबारा इंतज़ार करनी पड़ती है। LLM calls per-token पैसे लेती हैं, 1-10 seconds लेती हैं और rate limits होती हैं। Caching तीनों घटाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives
Step 2 → Build a cache key (from normalized prompt + model + parameters)
Step 3 → Look up the key in the cache (memory, Redis, etc.)
Step 4 → HIT  -> return stored response immediately (no LLM call, ~0 tokens)
Step 5 → MISS -> call the LLM, get the response
Step 6 → Store response with a TTL (time to live)
Step 7 → Return response; track hit rate, tokens and money saved
```

Types: exact-match cache (topic 442), semantic cache (443), provider prompt caching (reuses the repeated prompt prefix inside the provider, topics 447-448).

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आती है
Step 2 → Cache key बनाओ (normalized prompt + model + parameters से)
Step 3 → Cache (memory, Redis आदि) में key देखो
Step 4 → HIT  -> stored response तुरंत लौटाओ (LLM call नहीं, ~0 tokens)
Step 5 → MISS -> LLM call करो, response लो
Step 6 → Response को TTL (time to live) के साथ store करो
Step 7 → Response लौटाओ; hit rate, tokens और बचे पैसे track करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 100,000 daily queries, but only 30,000 are unique (importers repeat common products like "cotton t-shirt", "mobile charger"). Caching answers for unique queries means 70,000 calls are served free and instantly. Tariff rules change rarely, so a TTL of a few days or a version tag in the key is safe.

**Zomato AI**: "Best biryani near me" style FAQs and menu summaries repeat across thousands of users; cache them per city and per menu version.

## 🟡 Real Example Hindi mein
**Tariff System**: रोज़ 100,000 queries, पर unique सिर्फ़ 30,000 (importers "cotton t-shirt", "mobile charger" जैसे common products दोहराते हैं)। Unique queries के answers cache करने से 70,000 calls free और instant मिलती हैं। Tariff rules कम बदलते हैं, इसलिए कुछ दिनों का TTL या key में version tag सुरक्षित है।

**Zomato AI**: "Best biryani near me" जैसे FAQs और menu summaries हज़ारों users में दोहराते हैं; इन्हें city और menu version के हिसाब से cache करो।

---

## 💻 Code Example — Basic
```python
# Pure-Python LLM cache with hit/miss counting (run directly)
import hashlib  # stable hashing for keys
from typing import Callable  # type hints

CACHE: dict[str, str] = {}  # in-memory store
STATS = {"hits": 0, "misses": 0}  # counters


def make_key(model: str, prompt: str) -> str:
    """Normalise the prompt and hash it with the model name."""
    normalised = " ".join(prompt.lower().split())  # lowercase + collapse spaces
    return hashlib.sha256(f"{model}|{normalised}".encode()).hexdigest()  # fixed-size key


def cached_call(model: str, prompt: str, llm: Callable[[str], str]) -> str:
    """Return cached answer if present, otherwise call llm and store."""
    key = make_key(model, prompt)  # build key
    if key in CACHE:  # HIT
        STATS["hits"] += 1  # count it
        return CACHE[key]  # free answer
    STATS["misses"] += 1  # MISS
    answer = llm(prompt)  # pay for the real call
    CACHE[key] = answer  # remember for next time
    return answer  # return fresh answer


if __name__ == "__main__":
    fake_llm = lambda p: "8518.30"  # stand-in for a paid model call
    cached_call("m", "HS code for earbuds", fake_llm)  # miss
    cached_call("m", "hs code  for EARBUDS", fake_llm)  # hit (normalised)
    print(STATS)  # {'hits': 1, 'misses': 1}
```

## 💻 Code Example — Advanced
```python
# Production-style async cache with TTL, single-flight (no duplicate concurrent calls), error handling
import asyncio  # async primitives
import hashlib  # hashing
import logging  # logging
import time  # TTL clock
from typing import Awaitable, Callable  # types

logger = logging.getLogger("llm-cache")  # logger


class TTLCache:
    """Small async-safe TTL cache that avoids duplicate in-flight calls."""

    def __init__(self, ttl_seconds: float = 3600.0, max_items: int = 10_000) -> None:
        self.ttl = ttl_seconds  # entry lifetime
        self.max_items = max_items  # memory bound
        self.data: dict[str, tuple[float, str]] = {}  # key -> (expires_at, value)
        self.inflight: dict[str, asyncio.Future[str]] = {}  # key -> pending result

    @staticmethod
    def key(model: str, prompt: str, temperature: float) -> str:
        raw = f"{model}|{temperature}|{' '.join(prompt.lower().split())}"  # include params
        return hashlib.sha256(raw.encode()).hexdigest()  # hash

    async def get_or_call(
        self, model: str, prompt: str, temperature: float,
        llm: Callable[[str], Awaitable[str]],
    ) -> str:
        k = self.key(model, prompt, temperature)  # cache key
        entry = self.data.get(k)  # lookup
        if entry and entry[0] > time.monotonic():  # valid hit
            return entry[1]  # return cached
        if k in self.inflight:  # same request already running
            return await self.inflight[k]  # wait for it, no second LLM call
        fut: asyncio.Future[str] = asyncio.get_running_loop().create_future()  # placeholder
        self.inflight[k] = fut  # register
        try:
            value = await llm(prompt)  # real call
            if len(self.data) >= self.max_items:  # enforce bound
                self.data.pop(next(iter(self.data)))  # drop oldest inserted
            self.data[k] = (time.monotonic() + self.ttl, value)  # store with expiry
            fut.set_result(value)  # wake waiters
            return value  # return fresh
        except Exception as exc:  # LLM failed
            logger.error("llm call failed: %s", exc)  # log
            fut.set_exception(exc)  # propagate to waiters
            raise  # and to caller
        finally:
            self.inflight.pop(k, None)  # clean up
```
Only cache deterministic-enough calls (temperature 0 or low). Token usage: a hit uses 0 input and 0 output tokens.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
cache: dict[str, str] = {}  # swap for Redis in production


class Q(BaseModel):
    query: str  # user question


@app.post("/ask")
async def ask(q: Q) -> dict:
    key = " ".join(q.query.lower().split())  # normalised key
    if key in cache:  # hit
        return {"answer": cache[key], "cached": True}  # instant
    answer = "8518.30"  # placeholder for `await llm.ainvoke(...)`
    cache[key] = answer  # store
    return {"answer": answer, "cached": False}  # fresh
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a global LLM cache. Set it once and repeated identical calls to the same model with the same parameters are served from cache.

```python
from langchain_core.caches import InMemoryCache  # simple cache
from langchain_core.globals import set_llm_cache  # global switch
from langchain_openai import ChatOpenAI  # LLM

set_llm_cache(InMemoryCache())  # enable caching for all LangChain LLM calls
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature 0 caches best
llm.invoke("HS code for earbuds?")  # miss: calls API
llm.invoke("HS code for earbuds?")  # hit: no API call
```
LangGraph supports node-level caching and checkpointing; check the current docs for the exact API.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Cache key ignores model or parameters
✅ Correct: Include model, temperature, system prompt version in the key.
```python
# Wrong
key = prompt
# Right
key = f"{model}|{temperature}|{prompt_version}|{prompt}"
```

❌ Mistake 2: Caching personalised or private answers in a shared cache
✅ Correct: Scope the key by user or tenant, or do not cache such calls.
```python
# Wrong: key = question  -> user A's data served to user B
# Right: key = f"{tenant_id}|{question}"
```

---

## 🧠 Tricky Interview Question
**Q**: "You added caching and the bill dropped 60%, but a customer reports a stale HS code after a tariff update. What went wrong and how do you fix it?"

**Answer**: Stale cache: entries outlived the facts. Fix: use a TTL matched to data freshness, include a data version (for example `tariff_schedule_version`) in the key so a new schedule naturally misses, and support explicit invalidation (purge by tag when rules update). Keep monitoring hit rate versus complaint rate. Never cache without an invalidation story.

---

## ⚫ Interview Questions + Answers

Q1: What is LLM caching?
A1: Reusing stored model responses for repeated requests to save cost and latency.

Q2: What does TTL mean?
A2: Time to live: how long a cached entry stays valid before it expires.

Q3: Exact vs semantic cache?
A3: Exact matches identical normalised input (fast, safe, lower hit rate). Semantic matches by embedding similarity (higher hit rate, risk of wrong matches).

Q4: Why is caching harder at high temperature?
A4: Outputs are meant to vary; caching freezes one sample. Use it mainly for deterministic or factual tasks.

Q5: How do you measure whether caching is worth it?
A5: Track hit rate, tokens and dollars saved, latency p95, and quality incidents from stale or wrong hits. Value = hit_rate x (avg call cost) minus cache infra cost and staleness risk. Run an A/B test or shadow comparison before widening scope.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many repeated or near-repeated queries (FAQs, classification of common items)
- Answers are stable for hours or days
- Latency and cost matter

❌ Avoid when:
- Every request is unique or personalised
- Answers must be real-time (stock prices, live inventory)
- High temperature creative generation where variety is the goal

---

## 📊 Visual Diagram
```
 Request --> build key --> cache lookup
                              |
                 +------------+-------------+
                 | HIT                      | MISS
                 v                          v
          return stored answer       call LLM (tokens billed)
          (0 tokens, ~ms)                   |
                                      store with TTL
                                            |
                                      return answer
```

---

## 💰 Cost Impact
Savings = hit_rate x calls x cost per call. Example (illustrative): 100K calls/day x 700 tokens avg. With a 70% hit rate, 70K calls cost nothing in tokens: if a call costs $0.0002, that is about $14/day or about $420/month saved, plus much faster responses. Larger models and longer prompts make savings bigger.

Optimise: normalise inputs to raise hit rate, tune TTL, cache only deterministic calls, track the hit rate by endpoint, and combine with provider prompt caching for long shared prefixes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Stored previous results | पहले के results का store |
| Hit | Answer found in cache | Cache में answer मिला |
| Miss | Not found, call LLM | नहीं मिला, LLM call |
| TTL | How long an entry lives | Entry कितनी देर valid |
| Cache key | Identifier of a request | Request की पहचान |
| Invalidation | Removing stale entries | पुरानी entries हटाना |
| Hit rate | Hits divided by requests | Hits / कुल requests |

---

## ⚡ 3-Line Summary
English: Caching reuses earlier LLM answers for repeated requests, saving tokens and latency. Build keys carefully, set TTLs and plan invalidation. Do not cache personalised or real-time answers.
Hindi: Caching दोहराई गई requests के लिए पुराने LLM answers reuse करता है, tokens और latency बचाता है। Keys सावधानी से बनाओ, TTL रखो और invalidation सोचो। Personalised या real-time answers cache मत करो।

---

## ➡️ Next Topic
**442. Exact Match Caching** — the simplest and safest cache: key design, normalisation and storage choices.

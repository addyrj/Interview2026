---

# 268. LangChain Caching
# हिंदी में: LangChain Caching (वही सवाल दोबारा, पैसा एक बार)

---

## 🔵 Simple Definition (English)
LangChain caching stores the answer of an LLM call, so the same prompt with the same model settings is answered from memory/disk/Redis instead of calling the provider again. You turn it on globally with `set_llm_cache(...)`. It saves money and gives near-zero latency on repeats.

## 🔵 सरल परिभाषा (Hindi)
LangChain caching LLM call का answer store कर लेता है, ताकि वही prompt और वही model settings आने पर provider को दोबारा call किए बिना memory/disk/Redis से जवाब मिल जाए। `set_llm_cache(...)` से global रूप से on होता है। इससे पैसा बचता है और repeat queries पर latency लगभग शून्य हो जाती है।

---

## 🔴 Problem it Solves
Many production queries repeat: "HS code for iPhone 15?" is asked 500 times a day. Each call costs tokens and 1-3 seconds. Without a cache you pay the same price again and again for an identical answer. During development, re-running a notebook also re-bills every call.

## 🔴 यह क्यों बना? (Hindi)
Production में बहुत से queries repeat होते हैं: "iPhone 15 का HS code?" दिन में 500 बार पूछा जाता है। हर call में tokens का पैसा और 1-3 सेकंड लगते हैं। Cache के बिना एक ही जवाब के लिए बार-बार पैसा देना पड़ता है। Development में notebook दोबारा चलाने पर भी हर call दोबारा bill होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → set_llm_cache(InMemoryCache() | SQLiteCache(...) | RedisCache(...))
Step 2 → A chat model gets called with messages + its settings (model name, temperature...)
Step 3 → LangChain builds the cache key = (prompt text, "llm string" of the model + params)
Step 4 → Key found (HIT)  -> return stored generation, NO API call, 0 tokens
Step 5 → Key missing (MISS) -> call provider, store the result under the key
Step 6 → Different temperature/model/stop words -> different key -> separate entries
Step 7 → Exact match only. For "similar question" matching use a semantic cache (embeddings)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → set_llm_cache(InMemoryCache() | SQLiteCache(...) | RedisCache(...))
Step 2 → Chat model को messages + settings (model name, temperature...) के साथ call किया जाता है
Step 3 → LangChain cache key बनाता है = (prompt text, model + params की "llm string")
Step 4 → Key मिली (HIT)  -> stored जवाब लौटता है, API call नहीं, 0 tokens
Step 5 → Key नहीं मिली (MISS) -> provider call होती है, result key के नीचे store होता है
Step 6 → temperature/model/stop बदले -> key बदली -> अलग entry
Step 7 → सिर्फ exact match। "मिलते-जुलते सवाल" के लिए semantic cache (embeddings) चाहिए
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers ask the same products again and again ("lithium battery", "cotton t-shirt", "wireless earbuds"). Normalize the query (lowercase, trim), then cache with Redis and a TTL of 24 hours (tariff rules change rarely, but not never - when a new tariff schedule is published, flush the cache). Result: 60% hit rate -> 60% fewer paid calls and a 2 s -> 5 ms response on hits.

**Zomato-style**: "Describe this dish" generated once per dish, cached forever (until the menu changes). **Amazon-style**: Product-summary generation cached per (product_id, review_count_bucket).

## 🟡 Real Example Hindi mein
**Tariff System**: Importers वही products बार-बार पूछते हैं ("lithium battery", "cotton t-shirt", "wireless earbuds")। Query normalize करो (lowercase, trim), फिर Redis में 24 घंटे के TTL के साथ cache करो (tariff rules कम बदलते हैं पर बदलते हैं - नया tariff schedule आए तो cache flush करो)। नतीजा: 60% hit rate -> 60% कम paid calls, और hit पर 2 s -> 5 ms।

**Zomato-style**: "इस dish का description" एक बार बनाकर cache (menu बदलने तक)। **Amazon-style**: Product summary (product_id, review_count bucket) के हिसाब से cache।

---

## 💻 Code Example — Basic
```python
# Basic LLM caching -- runs OFFLINE with a fake chat model (no API key)
# pip install langchain-core
from langchain_core.caches import InMemoryCache                    # simple dict-based cache
from langchain_core.globals import set_llm_cache                   # global on/off switch
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # fake LLM
from langchain_core.messages import AIMessage                      # message type

# The fake model returns DIFFERENT texts on each REAL call, so we can see cache hits clearly
replies = iter([                                                   # one item per real (uncached) call
    AIMessage(content="answer #1 (real call)"),
    AIMessage(content="answer #2 (real call)"),
    AIMessage(content="answer #3 (real call)"),
])
llm = GenericFakeChatModel(messages=replies)                       # fake chat model

set_llm_cache(InMemoryCache())                                     # turn caching ON globally

q1 = llm.invoke("HS code for earbuds?")                            # MISS -> real call -> answer #1
q2 = llm.invoke("HS code for earbuds?")                            # HIT  -> same text -> answer #1
q3 = llm.invoke("HS code for laptops?")                            # MISS (different prompt) -> answer #2
print(q1.content)                                                  # answer #1 (real call)
print(q2.content)                                                  # answer #1 (real call)  <- cached
print(q3.content)                                                  # answer #2 (real call)

set_llm_cache(None)                                                # turn caching OFF
q4 = llm.invoke("HS code for earbuds?")                            # real call again -> answer #3
print(q4.content)                                                  # answer #3 (real call)
```

## 💻 Code Example — Advanced
```python
# Production: Redis cache with TTL + app-level normalized cache + async + safe fallback
# pip install langchain-openai langchain-community redis
import hashlib                                                     # stable hash for keys
import json                                                        # serialize values
import logging                                                     # logging
import re                                                          # normalize text

import redis.asyncio as aioredis                                   # async redis client
from langchain_community.cache import RedisCache                   # LangChain Redis LLM cache
from langchain_core.globals import set_llm_cache                   # global switch
from langchain_core.output_parsers import StrOutputParser          # to str
from langchain_core.prompts import ChatPromptTemplate              # prompt
from langchain_openai import ChatOpenAI                            # model
import redis                                                       # sync client (RedisCache uses sync)

logger = logging.getLogger("tariff.cache")                         # logger

# --- Layer 1: LangChain's LLM cache (exact prompt + params), with 24h TTL ---
try:
    sync_client = redis.Redis.from_url("redis://localhost:6379/0") # connect (lazy)
    set_llm_cache(RedisCache(redis_=sync_client, ttl=24 * 3600))   # entries expire after 24 hours
except Exception as exc:                                           # redis misconfigured
    logger.warning("cache disabled: %s", exc)                      # run without cache, do not crash

# temperature=0 is important: caching a creative (random) answer freezes one random sample
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=200)
prompt = ChatPromptTemplate.from_messages([("system", "Return HS code + one line reason."), ("user", "{product}")])
chain = prompt | llm | StrOutputParser()                           # LCEL chain

# --- Layer 2: application cache on NORMALIZED input (improves hit rate) ---
aredis = aioredis.from_url("redis://localhost:6379/1", decode_responses=True)  # async client, other DB

def normalize(text: str) -> str:                                   # "  Wireless   EARBUDS! " -> "wireless earbuds"
    text = re.sub(r"[^\w\s]", " ", text.lower())                   # drop punctuation, lowercase
    return re.sub(r"\s+", " ", text).strip()                       # collapse spaces

def cache_key(product: str, version: str = "tariff-2025-v1") -> str:
    digest = hashlib.sha256(normalize(product).encode()).hexdigest()[:24]  # short stable hash
    return f"hs:{version}:{digest}"                                # version lets you invalidate all at once

async def classify_cached(product: str) -> dict[str, object]:
    key = cache_key(product)                                       # build key
    try:
        hit = await aredis.get(key)                                # try the cache
        if hit:                                                    # found
            return {**json.loads(hit), "cached": True}             # zero tokens spent
    except Exception as exc:                                       # cache down -> continue without it
        logger.warning("cache read failed: %s", exc)               # log only
    answer = await chain.ainvoke({"product": product})             # real LLM call
    try:
        await aredis.set(key, json.dumps({"answer": answer}), ex=24 * 3600)  # store with TTL
    except Exception as exc:                                       # never fail the request for cache
        logger.warning("cache write failed: %s", exc)              # log only
    return {"answer": answer, "cached": False}                     # fresh answer
```

---

## 🟠 FastAPI Integration
Cache at the edge of your API: normalize -> check cache -> LLM -> store. Return a `cached` flag and token usage so you can measure hit rate. Provide an admin endpoint to bump the cache version after tariff updates.

```python
# FastAPI route using the app-level cache (classify_cached from Advanced)
from fastapi import FastAPI, Header, HTTPException                 # framework
from pydantic import BaseModel, Field                              # validation

app = FastAPI()                                                    # app
CACHE_VERSION = {"v": "tariff-2025-v1"}                            # mutable holder for the demo

class Req(BaseModel):                                              # input
    product: str = Field(min_length=2, max_length=300)             # limits

@app.post("/classify")                                             # main route
async def classify(req: Req) -> dict[str, object]:
    return await classify_cached(req.product)                      # cache-first

@app.post("/admin/cache/bump")                                     # invalidate everything cheaply
async def bump(new_version: str, x_admin_token: str = Header(...)) -> dict[str, str]:
    if x_admin_token != "change-me":                               # use a real secret check in prod
        raise HTTPException(status_code=403, detail="forbidden")   # block others
    CACHE_VERSION["v"] = new_version                               # old keys become unreachable
    return {"version": new_version}                                # confirm
```

---

## 🔗 LangChain / LangGraph Connection
- **Cache backends**: `InMemoryCache` (dev, lost on restart), `SQLiteCache` (from `langchain_community.cache`, a file - good for notebooks/local), `RedisCache` (shared across servers, supports TTL), `RedisSemanticCache` / `GPTCache` (semantic: similar questions hit).
- **Per-model**: `ChatOpenAI(cache=True/False/BaseCache)` overrides the global cache for one model.
- **Embeddings**: `CacheBackedEmbeddings` caches embedding vectors in a key-value store - big saving in RAG indexing.
- **Provider prompt caching** (OpenAI automatic, Anthropic `cache_control`) is a *different* thing: it discounts repeated prompt *prefixes* inside the provider; it does not return a stored answer.
- **LangGraph**: node-level caching with `CachePolicy` (`builder.add_node("n", fn, cache_policy=CachePolicy(ttl=60))` plus `compile(cache=InMemoryCache())`) skips re-running an unchanged node.

```python
# SQLite cache for local development (a file survives restarts)
from langchain_community.cache import SQLiteCache                  # file-based cache
from langchain_core.globals import set_llm_cache                   # switch
set_llm_cache(SQLiteCache(database_path=".langchain.db"))          # re-running a notebook is now free
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching with high temperature
```python
# Wrong -- the first random answer is frozen forever for this prompt
llm = ChatOpenAI(temperature=1.0)

# Right -- deterministic tasks (classification, extraction) use temperature=0
llm = ChatOpenAI(temperature=0)
```

❌ Mistake 2: No TTL / no version -> stale answers after a tariff update
```python
# Wrong
RedisCache(redis_=client)                   # entries live forever

# Right
RedisCache(redis_=client, ttl=86400)        # expire daily + include a data version in keys
```

❌ Mistake 3: Caching user-specific or private data in a shared cache (a prompt containing user A's invoice number answered to user B). Include a tenant/user id in the key or do not cache such calls.

❌ Mistake 4: Expecting `"iPhone 15 HS code"` to match `"HS code of iPhone15"` - LLM cache is exact match. Normalize first or use a semantic cache.

---

## 🧠 Tricky Interview Question

**Q**: "You enabled `set_llm_cache(InMemoryCache())` in a FastAPI app running 4 uvicorn workers on 2 pods. Hit rate is far lower than the repeat rate in the logs. Why?"

**Answer**: `InMemoryCache` lives in each process's memory. With 4 workers x 2 pods there are 8 separate caches, each starting cold, and each is lost on restart/deploy. A query that repeats is only a hit if it lands on the same process. Fix: use a shared cache (Redis) so all workers see the same entries, add a TTL, and normalize inputs. Also check that the cache key really is identical: a changing field in the prompt (timestamp, request id, random few-shot order) makes every key unique.

---

## ⚫ Interview Questions + Answers

Q1: What does `set_llm_cache` do?
A1: It sets a global cache used by chat models and LLMs. Before calling the provider, LangChain checks the cache with a key made from the prompt and the model's parameters. Hit = no API call.

Q2: What is in the cache key?
A2: The prompt (messages) plus the "llm string" - model name and parameters like temperature, stop words. Change any of them and it is a different key.

Q3: Exact cache vs semantic cache?
A3: Exact: string-equal prompt only; fast and safe. Semantic: embed the prompt and return the answer of a *similar* earlier prompt if similarity is above a threshold; higher hit rate but a risk of wrong answers (e.g. "HS code for lithium battery 3.7V" vs "...48V" may differ in duty). For classification of regulated data prefer exact + normalization.

Q4: How do you invalidate cache when the tariff schedule changes?
A4: Put a data version in the key (`hs:tariff-2025-v2:...`) and bump it - old keys are never read and expire by TTL. Alternatively delete by prefix/`FLUSHDB` on a dedicated Redis DB. TTL is the safety net.

Q5 (Hard): How is LLM response caching different from provider prompt caching, and how would you use both?
A5: Response caching (LangChain/Redis) returns a *stored final answer* for an identical request: cost 0, no provider call. Prompt caching (OpenAI automatic for long prefixes, Anthropic `cache_control`) still runs the model but charges less (e.g. up to ~90% discount on cached input tokens) for a repeated *prefix* such as a long system prompt + tariff rules. Use both: response cache for exact repeats; prompt cache for the large static prefix when the question part differs. Keep static content first in the prompt and variable content last so the prefix is reusable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deterministic tasks (temperature 0): classification, extraction, FAQ
- High repeat rate of questions
- Development/testing (SQLiteCache) to avoid re-billing
- Embedding generation for stable documents

❌ Avoid when:
- Creative/varied output is desired (each answer should differ)
- Prompts contain private or time-sensitive data (stock price, "today's rate")
- Answers must always reflect the latest data and you cannot invalidate reliably

---

## 📊 Visual Diagram
```
 user query ──► normalize ──► build key (prompt + model params + data version)
                                   │
                         ┌─────────▼─────────┐
                         │  Redis / SQLite   │
                         └───┬───────────┬───┘
                    HIT      │           │      MISS
              ┌──────────────▼┐        ┌─▼──────────────┐
              │ return stored │        │ call LLM API   │──► store with TTL
              │ answer (0 tok)│        │ (tokens billed)│        │
              └───────────────┘        └───────┬────────┘        │
                       ▲                       ▼                 │
                       └──────────── answer ◄──────────◄─────────┘
```

---

## 💰 Cost Impact
- Cache hit = **0 tokens, ~0 cost, ~5 ms**. Cost saved = hit_rate x cost_per_call x volume.
- Example: 100K queries/day, 500 in + 200 out on gpt-4o-mini = $0.000195/query = $19.50/day. With 60% hit rate: $7.80/day -> saves ~$350/month. On gpt-4o ($8 per 1K queries) the same hit rate saves ~$480/day.
- Redis cost (small instance) is tiny compared to LLM cost - break-even is almost immediate.
- Optimize: normalize inputs (raises hit rate), TTL by data volatility, `temperature=0`, version keys, monitor `hit_rate` metric. Add provider prompt caching for the long static system prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Stored answers for reuse | पहले से रखे जवाब |
| Hit / Miss | Found / not found in cache | मिला / नहीं मिला |
| TTL | Time before entry expires | Entry की उम्र |
| Cache key | Identifier built from prompt + params | Cache पहचान |
| Semantic cache | Match by meaning using embeddings | अर्थ के आधार पर cache |
| Invalidation | Removing stale entries | पुराने entries हटाना |
| Prompt caching | Provider discount on repeated prefix | Provider की prefix discount |

---

## ⚡ 3-Line Summary
English: `set_llm_cache` makes repeated identical calls free and instant. Use Redis with TTL and a data version in production, `temperature=0`, and normalized inputs. Exact cache is safe; semantic cache raises hits but risks wrong answers.
Hindi: `set_llm_cache` से वही call दोबारा मुफ्त और तुरंत मिलती है। Production में Redis, TTL, data version, `temperature=0` और normalized input use करो। Exact cache सुरक्षित है; semantic cache hits बढ़ाता है पर गलत जवाब का जोखिम रहता है।

---

## ➡️ Next Topic
**269. LangChain Tracing** - see every prompt, token and latency inside a chain with LangSmith and callbacks, to debug and measure cost.

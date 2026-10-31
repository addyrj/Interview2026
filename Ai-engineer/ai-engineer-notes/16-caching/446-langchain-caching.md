---

# 446. LangChain Caching
# हिंदी में: LangChain Caching

---

## 🔵 Simple Definition (English)
LangChain has a built-in LLM cache. You call `set_llm_cache(...)` once, and every chat model call with the same prompt and model settings is answered from the cache instead of the API. Backends include in-memory, SQLite, Redis and semantic (vector) caches.

## 🔵 सरल परिभाषा (Hindi)
LangChain में LLM cache built-in है। एक बार `set_llm_cache(...)` call करो, फिर वही prompt और model settings वाली हर chat model call API की जगह cache से जवाब पाती है। Backends: in-memory, SQLite, Redis और semantic (vector) cache।

---

## 🔴 Problem it Solves
- Writing cache code around every `llm.invoke` is repetitive and easy to forget.
- During development, re-running the same chain burns tokens and time.
- Teams want to swap storage (memory to Redis) without changing chain code.

## 🔴 यह क्यों बना? (Hindi)
- हर `llm.invoke` के चारों तरफ़ cache code लिखना दोहराव वाला है और भूलना आसान है।
- Development में वही chain बार-बार चलाने से tokens और समय बर्बाद होता है।
- Teams चाहती हैं कि chain code बदले बिना storage (memory से Redis) बदल सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → set_llm_cache(cache) registers a global cache object
Step 2 → chain calls model.invoke(prompt)
Step 3 → BaseChatModel builds a key = (serialised prompt/messages, llm_string)
         llm_string contains model name + parameters (temperature etc.)
Step 4 → cache.lookup(prompt, llm_string)
Step 5 → HIT → returns stored Generations, no API call
Step 6 → MISS → API call, then cache.update(prompt, llm_string, result)
Step 7 → Per-model override: ChatOpenAI(cache=False) skips it
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → set_llm_cache(cache) एक global cache object register करता है
Step 2 → chain model.invoke(prompt) call करती है
Step 3 → BaseChatModel key बनाता है = (serialised prompt/messages, llm_string)
         llm_string में model name + parameters (temperature आदि) होते हैं
Step 4 → cache.lookup(prompt, llm_string)
Step 5 → HIT → stored Generations लौटते हैं, API call नहीं
Step 6 → MISS → API call, फिर cache.update(prompt, llm_string, result)
Step 7 → Model-level override: ChatOpenAI(cache=False) cache छोड़ देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A LangChain pipeline does "extract product attributes" then "classify to HS code". While developers iterate on the second prompt, the first step's results come from a SQLite cache, saving 40 percent of tokens during testing. In production a Redis cache with TTL serves repeated product lookups.
**Zomato AI**: The "summarise 200 reviews" step is cached per restaurant for a few hours.

## 🟡 Real Example Hindi mein
**Tariff System**: LangChain pipeline में पहले "product attributes निकालो" फिर "HS code classify करो"। Developers दूसरे prompt पर काम करते हैं तो पहले step का result SQLite cache से आता है, testing में 40 प्रतिशत tokens बचते हैं। Production में TTL वाला Redis cache बार-बार आने वाले product lookups को serve करता है।
**Zomato AI**: "200 reviews की summary" वाला step restaurant के हिसाब से कुछ घंटे cache होता है।

---

## 💻 Code Example — Basic
```python
# Basic: LangChain InMemoryCache with a fake chat model so it runs offline.
# pip install langchain-core
from langchain_core.caches import InMemoryCache  # simple dict-based cache
from langchain_core.globals import set_llm_cache  # register global cache
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # offline model
from langchain_core.messages import AIMessage  # message type for fake replies

set_llm_cache(InMemoryCache())  # turn caching on for all models

# The fake model yields a DIFFERENT message each real call, so a repeated answer proves caching.
replies = iter([AIMessage(content="answer #1"), AIMessage(content="answer #2")])  # two scripted replies
llm = GenericFakeChatModel(messages=replies)  # model that reads from the iterator

first = llm.invoke("HS code for steel bottle?")  # miss -> consumes reply #1
second = llm.invoke("HS code for steel bottle?")  # hit -> same text, iterator not advanced
third = llm.invoke("HS code for copper wire?")  # new prompt -> miss -> reply #2

print(first.content)  # answer #1
print(second.content)  # answer #1 (served from cache)
print(third.content)  # answer #2
```

## 💻 Code Example — Advanced
```python
# Production: pick cache backend by environment, async calls, TTL, per-call bypass, usage logging.
# pip install langchain-openai langchain-community redis
from __future__ import annotations

import logging  # log failures
import os  # read env vars
from typing import Optional

from langchain_community.cache import InMemoryCache, RedisCache, SQLiteCache  # backends
from langchain_core.caches import BaseCache  # common interface
from langchain_core.globals import set_llm_cache  # global setter
from langchain_core.prompts import ChatPromptTemplate  # prompt template
from langchain_openai import ChatOpenAI  # chat model

log = logging.getLogger("lc_cache")  # logger


def build_cache() -> Optional[BaseCache]:
    env = os.getenv("APP_ENV", "dev")  # dev / test / prod
    try:
        if env == "prod":
            import redis  # imported lazily so dev needs no Redis

            client = redis.Redis.from_url(os.environ["REDIS_URL"])  # sync client required by RedisCache
            return RedisCache(redis_=client, ttl=86_400)  # 1 day TTL
        if env == "dev":
            return SQLiteCache(database_path=".langchain.db")  # survives restarts, local file
        return InMemoryCache()  # tests: isolated, fast
    except Exception as exc:  # never crash startup because of the cache
        log.error("cache init failed, running without cache: %s", exc)
        return None


set_llm_cache(build_cache())  # None disables caching globally

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature 0 -> deterministic -> cacheable
fresh_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, cache=False)  # this instance bypasses cache

prompt = ChatPromptTemplate.from_messages(
    [("system", "Return only the HS code."), ("human", "{product}")]
)  # template
chain = prompt | llm  # LCEL chain


async def classify(product: str) -> str:
    try:
        msg = await chain.ainvoke({"product": product})  # async call, cache applies automatically
        return str(msg.content)  # text answer
    except Exception as exc:  # network / API errors
        log.error("classify failed: %s", exc)
        raise
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # schema

app = FastAPI()  # app (set_llm_cache already called at import time above)


class In(BaseModel):
    product: str  # product text


@app.post("/hs-code")
async def hs_code(body: In) -> dict[str, str]:
    try:
        return {"hs_code": await classify(body.product)}  # uses cache transparently
    except Exception as exc:
        raise HTTPException(status_code=502, detail="model error") from exc  # clean error to client
```
Note: `RedisCache` uses the sync redis client, so blocking calls happen inside the model call. For very high traffic use `langchain_community.cache.AsyncRedisCache` with `redis.asyncio` or cache at the API layer (topic 444).

---

## 🔗 LangChain / LangGraph Connection
- LCEL chains and LangGraph nodes that call a chat model all use the global LLM cache.
- Semantic option: `RedisSemanticCache(redis_url=..., embedding=OpenAIEmbeddings(), score_threshold=0.2)` (distance threshold: lower is stricter).
- LangGraph also supports node-level caching: `builder.add_node("classify", fn, cache_policy=CachePolicy(ttl=300))` and `graph.compile(cache=InMemoryCache())` caches whole node outputs by input.

```python
from langgraph.cache.memory import InMemoryCache as GraphCache  # LangGraph's own cache
from langgraph.graph import StateGraph  # graph builder
from langgraph.types import CachePolicy  # per-node policy
# builder.add_node("classify", classify_node, cache_policy=CachePolicy(ttl=300))
# graph = builder.compile(cache=GraphCache())
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching with high temperature and expecting variety
✅ Correct: use temperature 0 for cached chains, or `cache=False` where variety matters.

```python
# Wrong: creative writer, but cached forever
ChatOpenAI(temperature=1.0)
# Right: bypass for creative calls
ChatOpenAI(temperature=1.0, cache=False)
```

❌ Mistake 2: Changing the prompt text but forgetting old cache entries are still valid for the old key
✅ Correct: keys include the rendered prompt, so edits create new keys; but changes in tools or post-processing are NOT in the key. Clear the cache on such deploys.

```python
# Wrong: change parser logic, keep stale cached raw outputs
# Right: clear after deploy
from langchain_core.globals import get_llm_cache
get_llm_cache().clear()
```

---

## 🧠 Tricky Interview Question
**Q**: "You enabled `InMemoryCache` in a FastAPI app on Kubernetes with 6 pods. Hit rate is only 15 percent although traffic repeats a lot. Why, and what do you change?"

**Answer**: Each pod has its own memory, so a prompt cached in pod A misses in pod B (expected hit rate about 1/6 of ideal at first), and every deploy empties it. Move to a shared backend such as Redis, add TTL, and keep keys stable. Also check that the prompt contains no timestamps or request IDs that make every key unique.

---

## ⚫ Interview Questions + Answers

Q1: How do you enable caching in LangChain? (Easy)
A1: `from langchain_core.globals import set_llm_cache` then `set_llm_cache(InMemoryCache())` (or SQLite/Redis).

Q2: What is the cache key made of? (Easy)
A2: The prompt (or serialised messages) plus an `llm_string` that has the model and its parameters.

Q3: How is semantic caching different from InMemoryCache in LangChain? (Medium)
A3: InMemoryCache needs identical prompt and params. Semantic caches (for example `RedisSemanticCache`) embed the prompt and return the answer of a close-enough earlier prompt using a score threshold.

Q4: How do you disable cache for one call? (Medium)
A4: Create the model with `cache=False`, or set the global cache to `None`.

Q5: What are the limits of LangChain's LLM cache for a multi-tenant production API? (Hard)
A5: Keys do not include tenant/user, so two tenants with the same prompt share answers, which is dangerous for private context. There is no built-in per-tenant namespace, TTL support varies by backend, and streaming/tool-call results may behave differently. For strict isolation implement caching at the API layer with tenant-prefixed keys (topics 451 and 457).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Developing and testing chains (save tokens)
- Deterministic extraction/classification steps
- You want one-line caching with swappable backends

❌ Avoid when:
- Prompts include per-user private data and no tenant isolation exists
- Output must be creative or fresh each time
- You need fine control over keys, TTL per request and metrics

---

## 📊 Visual Diagram
```
 chain.invoke(input)
        │
        ▼
 ┌──────────────────────┐
 │ ChatModel._generate  │
 └──────────┬───────────┘
            │ key=(prompt, llm_string)
            ▼
   ┌─────────────────┐  hit  ┌────────────────┐
   │ global LLMCache │─────► │ stored result  │
   │ Memory/SQLite/  │       └────────────────┘
   │ Redis/Semantic  │ miss
   └────────┬────────┘  │
            ▼           ▼
        update ◄── real API call (tokens)
```

---

## 💰 Cost Impact
**Token usage**: hits skip both input and output tokens. A dev loop that reruns a 1,200-token chain 50 times costs 60,000 input tokens uncached but only 1,200 with cache.
**Optimisation**: SQLite cache for development, Redis with TTL for production, temperature 0, stable prompt templates (no timestamps), and per-model `cache=False` only where needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| set_llm_cache | Registers global LLM cache | global cache चालू करने का function |
| llm_string | Model name plus parameters in key | key में model और params |
| InMemoryCache | Process-local dict cache | process के अंदर का cache |
| SQLiteCache | File-based persistent cache | file में रहने वाला cache |
| RedisSemanticCache | Embedding-based Redis cache | embedding वाला Redis cache |
| CachePolicy | LangGraph node cache setting | LangGraph node की cache setting |

---

## ⚡ 3-Line Summary
English: `set_llm_cache` adds caching to every LangChain/LangGraph model call with swappable backends. Use SQLite in dev, Redis in prod, and temperature 0. It does not isolate tenants, so be careful with private data.
Hindi: `set_llm_cache` से हर LangChain/LangGraph model call में caching जुड़ जाती है और backend बदला जा सकता है। Dev में SQLite, prod में Redis और temperature 0 रखो। यह tenants को अलग नहीं करता, इसलिए private data में सावधान रहो।

---

## ➡️ Next Topic
**447. Prompt Caching (Anthropic Native)** — provider-side caching of long prompt prefixes, which is different from caching full answers.

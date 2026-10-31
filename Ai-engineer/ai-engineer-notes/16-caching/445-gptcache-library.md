---

# 445. GPTCache Library
# हिंदी में: GPTCache Library

---

## 🔵 Simple Definition (English)
GPTCache is an open-source Python library (by Zilliz) that caches LLM responses. It can match a new question to an old one by meaning (semantic cache) using embeddings plus a vector store, so "HS code for steel bottle" and "tariff code of a steel flask" can share one answer.

## 🔵 सरल परिभाषा (Hindi)
GPTCache एक open-source Python library (Zilliz की) है जो LLM के जवाब cache करती है। यह embeddings और vector store की मदद से नए सवाल को पुराने सवाल से अर्थ (meaning) के आधार पर मिला सकती है, इसलिए "steel bottle का HS code" और "steel flask का tariff code" एक ही जवाब share कर सकते हैं।

---

## 🔴 Problem it Solves
- Exact-match caches (topic 444) miss when wording changes by even one word.
- Building embedding + vector search + similarity threshold + eviction yourself takes time.
- GPTCache bundles these parts as pluggable modules: embedding, scalar storage, vector store, similarity evaluation, eviction.

## 🔴 यह क्यों बना? (Hindi)
- Exact-match cache तब fail होता है जब सवाल का एक शब्द भी बदल जाए।
- Embedding + vector search + similarity threshold + eviction खुद बनाने में समय लगता है।
- GPTCache ये सब हिस्से plug-and-play modules में देता है: embedding, scalar storage, vector store, similarity evaluation, eviction।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Query arrives
Step 2 → Pre-processor picks the text to cache on (e.g. last user message)
Step 3 → Embedding model turns text into a vector
Step 4 → Vector store (FAISS/Milvus/Chroma...) finds nearest stored questions
Step 5 → Similarity evaluator checks score against a threshold
Step 6 → Score good enough → return stored answer (HIT)
Step 7 → Else call LLM, then save question vector + answer (MISS)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Query आती है
Step 2 → Pre-processor तय करता है किस text पर cache होगा (जैसे आख़िरी user message)
Step 3 → Embedding model text को vector बनाता है
Step 4 → Vector store (FAISS/Milvus/Chroma...) सबसे पास के पुराने सवाल ढूँढता है
Step 5 → Similarity evaluator score को threshold से मिलाता है
Step 6 → Score काफ़ी अच्छा → stored जवाब लौटाओ (HIT)
Step 7 → वरना LLM call करो, फिर सवाल का vector + जवाब save करो (MISS)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs brokers type the same product in many styles: "ladies cotton kurta", "women's cotton kurti", "cotton kurta for women". GPTCache with a threshold of about 0.85 maps all three to one cached HS-code answer, so only the first one pays for tokens.
**Amazon-style support bot**: "Where is my order?" appears in hundreds of phrasings; one semantic cache entry serves them all.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs brokers एक ही product अलग तरह से लिखते हैं: "ladies cotton kurta", "women's cotton kurti", "cotton kurta for women"। लगभग 0.85 threshold वाला GPTCache तीनों को एक cached HS-code जवाब से जोड़ देता है, सिर्फ़ पहली call पर tokens लगते हैं।
**Amazon-style support bot**: "मेरा order कहाँ है?" सैकड़ों तरीकों से पूछा जाता है; एक semantic cache entry सबको जवाब देती है।

---

## 💻 Code Example — Basic
```python
# Basic: the SAME idea GPTCache implements, in pure Python so it runs offline.
# Real GPTCache replaces embed() with ONNX/OpenAI embeddings and the list with FAISS.
import math  # for cosine similarity
import re  # to tokenise words


def embed(text: str) -> dict[str, float]:
    words = re.findall(r"[a-z]+", text.lower())  # lowercase words only
    vec: dict[str, float] = {}  # sparse bag-of-words vector
    for w in words:  # count each word
        vec[w] = vec.get(w, 0.0) + 1.0
    return vec  # toy "embedding"


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a[k] * b.get(k, 0.0) for k in a)  # dot product
    na = math.sqrt(sum(v * v for v in a.values()))  # norm of a
    nb = math.sqrt(sum(v * v for v in b.values()))  # norm of b
    return dot / (na * nb) if na and nb else 0.0  # avoid divide-by-zero


class MiniSemanticCache:
    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold  # minimum similarity for a hit
        self.items: list[tuple[dict[str, float], str]] = []  # (vector, answer)

    def get(self, q: str) -> str | None:
        qv = embed(q)  # embed the query
        best, best_score = None, 0.0  # track the best match
        for vec, ans in self.items:  # linear search (FAISS does this fast)
            s = cosine(qv, vec)  # similarity score
            if s > best_score:
                best, best_score = ans, s
        return best if best_score >= self.threshold else None  # threshold gate

    def put(self, q: str, answer: str) -> None:
        self.items.append((embed(q), answer))  # store vector + answer


if __name__ == "__main__":
    cache = MiniSemanticCache()  # create cache
    cache.put("hs code for women cotton kurta", "HS 6204.42")  # seed one entry
    print(cache.get("hs code for cotton kurta women"))  # similar -> hit
    print(cache.get("hs code for diesel engine"))  # different -> None
```

## 💻 Code Example — Advanced
```python
# Production-style GPTCache usage with the generic API (adapter-independent).
# pip install gptcache   (it pulls onnxruntime, faiss/sqlite via extras; check versions for your Python)
# Note: GPTCache's OpenAI adapter was written for the legacy openai<1 SDK, so we use the
# framework-neutral get()/put() API and call the LLM ourselves with the modern async client.
from __future__ import annotations

import asyncio  # to run blocking cache calls off the event loop
import logging  # log failures
from typing import Optional

from gptcache.adapter.api import get, init_similar_cache, put  # generic cache API
from gptcache.processor.pre import get_prompt  # pre-processor: use the raw string as cache text
from openai import AsyncOpenAI  # modern async client

log = logging.getLogger("gptcache_demo")  # logger


def setup_cache(cache_dir: str = "tariff_cache") -> None:
    # Creates ONNX embedding + SQLite (scalar) + FAISS (vector) + distance evaluation.
    init_similar_cache(data_dir=cache_dir, pre_func=get_prompt)  # defaults are good for a start


class SemanticLLM:
    def __init__(self) -> None:
        self.client = AsyncOpenAI()  # reads OPENAI_API_KEY
        setup_cache()  # init once at construction

    async def ask(self, question: str) -> dict[str, str]:
        loop = asyncio.get_running_loop()  # event loop for executor
        try:
            cached: Optional[str] = await loop.run_in_executor(None, get, question)  # blocking -> thread
        except Exception as exc:  # cache must never break the request
            log.warning("cache get failed: %s", exc)
            cached = None
        if cached:  # semantic hit
            return {"answer": cached, "source": "cache"}

        resp = await self.client.chat.completions.create(  # miss -> real LLM call
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            temperature=0,
            max_tokens=200,
        )
        answer = resp.choices[0].message.content or ""  # extract text
        if answer:  # never cache empty output
            try:
                await loop.run_in_executor(None, put, question, answer)  # store pair
            except Exception as exc:
                log.warning("cache put failed: %s", exc)
        return {"answer": answer, "source": "llm"}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # request schema

app = FastAPI()  # app
llm = SemanticLLM()  # built once at import (init_similar_cache is heavy)


class Q(BaseModel):
    question: str  # product / tariff question


@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    return await llm.ask(q.question)  # response includes "source": cache or llm
```
Tip: GPTCache calls are blocking, so we run them in an executor. Run one cache directory per service and persist it on a volume.

---

## 🔗 LangChain / LangGraph Connection
LangChain has a `GPTCache` wrapper in `langchain_community.cache`. You give it a function that initialises a `gptcache.Cache` per LLM string.

```python
import hashlib  # to name each cache folder
from gptcache import Cache  # GPTCache object
from gptcache.adapter.api import init_similar_cache  # similar-cache initialiser
from langchain_community.cache import GPTCache  # LangChain wrapper
from langchain_core.globals import set_llm_cache  # global switch


def init_gptcache(cache_obj: Cache, llm: str) -> None:
    h = hashlib.md5(llm.encode()).hexdigest()  # one folder per model config
    init_similar_cache(cache_obj=cache_obj, data_dir=f"similar_cache_{h}")  # semantic cache


set_llm_cache(GPTCache(init_gptcache))  # now all LangChain/LangGraph LLM calls are semantically cached
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Threshold too low
✅ Correct: Tune the threshold on real data. "Import duty on laptops" vs "Import duty on lap desks" can look similar but need different answers.

```python
# Wrong: accepts almost anything -> wrong HS code returned
if score >= 0.4: return cached
# Right: strict threshold + review of near misses
if score >= 0.88: return cached
```

❌ Mistake 2: One global cache for all users and all prompts
✅ Correct: Separate caches (or metadata filters) per tenant and per prompt version.

```python
# Wrong: same folder for every model/prompt
init_similar_cache(data_dir="cache")
# Right: folder per prompt version
init_similar_cache(data_dir=f"cache_v{PROMPT_VERSION}")
```

---

## 🧠 Tricky Interview Question
**Q**: "Your semantic cache returns the HS code for 'wooden table' when a user asks about 'wooden table with glass top'. Hit rate is 80 percent. Is this a success?"

**Answer**: No. A high hit rate with wrong answers is a quality bug (false positives). Measure precision of hits with a labelled set, raise the threshold, add a cross-encoder or a cheap LLM verification for borderline scores, and include key attributes (material, parts) as exact metadata filters. Hit rate must be reported together with answer accuracy.

---

## ⚫ Interview Questions + Answers

Q1: What does GPTCache do? (Easy)
A1: It caches LLM responses and can return them for semantically similar queries using embeddings and a vector store.

Q2: Name the main modules in GPTCache. (Easy)
A2: Pre-processor, embedding generator, cache storage (scalar), vector store, similarity evaluator, post-processor, eviction manager.

Q3: What is the difference between exact and semantic caching? (Medium)
A3: Exact needs identical text (hash match): fast, 100 percent safe, low hit rate. Semantic matches by meaning: higher hit rate, risk of false positives, needs embeddings and a threshold.

Q4: Where does the embedding cost come from, and is it worth it? (Medium)
A4: Each lookup embeds the query (a local ONNX model is free but uses CPU; OpenAI embeddings cost tiny per token). It is worth it when LLM calls cost much more than embedding, which is usually true by 100x or more.

Q5: How would you evaluate and keep a semantic cache safe in production? (Hard)
A5: Build a labelled pair set (same-intent vs different-intent). Sweep the threshold, plot precision vs hit rate, choose the point meeting your accuracy SLA. Log every hit with score, sample for human review, add per-tenant namespaces and TTL, invalidate on prompt or data-version change, and fall back to the LLM for scores in a grey zone.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users phrase the same intent in many ways (support bots, FAQ, product lookup)
- You want a fast prototype of semantic caching without writing vector code

❌ Avoid when:
- Answers depend on exact numbers or user-specific data
- You need strong maintenance guarantees (check the project's release activity before betting on it)
- Exact-match caching already gives a high hit rate

---

## 📊 Visual Diagram
```
 query ─► pre-processor ─► embedding ─► vector search (FAISS/Milvus)
                                              │
                                  score >= threshold ?
                                   │yes                 │no
                                   ▼                    ▼
                          stored answer (HIT)     LLM call (MISS)
                                                        │
                                          save vector + answer
```

---

## 💰 Cost Impact
**Token usage**: a hit costs 0 LLM tokens and one embedding (often local and free). A miss costs the normal prompt and completion tokens plus the embedding.
Example: 50,000 queries a day, 600 tokens each, gpt-4o-mini input at $0.15 per 1M tokens: 30M tokens = $4.50 input per day (plus output). A 35 percent semantic hit rate removes about $1.6 a day input cost and also the output cost.
**Optimisation**: use a local embedding model, tune the threshold, add TTL, cache only temperature 0 flows.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic cache | Match by meaning, not text | अर्थ के आधार पर cache |
| Embedding | Vector representing text meaning | text के अर्थ का vector |
| Similarity threshold | Minimum score for a hit | hit के लिए न्यूनतम score |
| False positive | Wrong cached answer returned | गलत cached जवाब मिलना |
| Evaluator | Component that scores similarity | similarity नापने वाला हिस्सा |
| Eviction | Removing old entries | पुरानी entries हटाना |

---

## ⚡ 3-Line Summary
English: GPTCache gives semantic caching with pluggable embedding, storage and vector modules. The key tuning knob is the similarity threshold, which trades hit rate against wrong answers. Use its generic get/put API with a modern async client.
Hindi: GPTCache में embedding, storage और vector modules जोड़कर semantic caching मिलती है। असली tuning threshold की है, जो hit rate और गलत जवाबों के बीच संतुलन बनाता है। Modern async client के साथ इसकी generic get/put API इस्तेमाल करो।

---

## ➡️ Next Topic
**446. LangChain Caching** — the built-in cache layer in LangChain (in-memory, SQLite, Redis, semantic) and how to switch between them.

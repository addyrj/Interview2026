---

# 591. Build Caching Layer for LLM
# हिंदी में: LLM के लिए Caching Layer बनाना

---

## 🔵 Simple Definition (English)
An LLM cache stores answers so repeated or near-identical questions skip the model call. `main.py` combines an exact-match cache (normalised text key), a semantic cache (embedding similarity above a threshold), a TTL for expiry, and hit/miss counters.

## 🔵 सरल परिभाषा (Hindi)
LLM cache जवाब सहेजता है ताकि दोहराए या मिलते-जुलते सवालों पर model call न हो। `main.py` में exact-match cache (normalised text key), semantic cache (threshold से ऊपर embedding similarity), expiry के लिए TTL, और hit/miss counters हैं।

---

## 🔴 Problem it Solves
Users ask the same thing again and again with tiny wording changes ("HS code for smartphone?" vs "hs code for smartphone"). Each repeat costs tokens and 1-3 seconds. Exact string caching misses these variants.

## 🔴 यह क्यों बना? (Hindi)
Users वही सवाल बार-बार थोड़े अलग शब्दों में पूछते हैं। हर repeat पर tokens और 1-3 सेकंड लगते हैं। सिर्फ़ exact string caching इन variants को पकड़ नहीं पाती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → norm(prompt): lowercase, keep word characters, single spaces
Step 2 → Exact lookup: key = norm(prompt); live entry -> hits_exact += 1
Step 3 → Else embed prompt (fake_embed: hashed bag of words, unit length)
Step 4 → Among unexpired entries find best cosine similarity
Step 5 → similarity >= threshold (0.8) -> hits_semantic += 1, reuse answer
Step 6 → Else misses += 1, call the LLM, put(answer) with expiry = now + ttl
Step 7 → Failures are never cached
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → norm(prompt): lowercase, सिर्फ़ word characters, single space
Step 2 → Exact lookup: key = norm(prompt); live entry मिले -> hits_exact += 1
Step 3 → नहीं तो prompt का embedding (fake_embed: hashed bag of words)
Step 4 → बिना expire हुई entries में सबसे अच्छी cosine similarity ढूँढो
Step 5 → similarity >= threshold (0.8) -> hits_semantic += 1, वही answer
Step 6 → नहीं तो misses += 1, LLM call, put() में expiry = now + ttl
Step 7 → Failures कभी cache नहीं होते
```

---

## 🟡 Real World Example
**Tariff Classification System**: brokers keep asking the HS code for "smartphone". In the run: 4 questions, only 2 LLM calls. Question 2 is an exact hit after normalisation, question 3 ("...for a smartphone please") is a semantic hit, and "laptop" is a miss.

**Other**: Zomato FAQ bot ("refund policy?" in 100 phrasings), Amazon product Q&A.

## 🟡 Real Example Hindi mein
**Tariff System**: brokers बार-बार "smartphone" का HS code पूछते हैं। Run में 4 सवाल पर सिर्फ़ 2 LLM calls। सवाल 2 normalisation के बाद exact hit, सवाल 3 ("...for a smartphone please") semantic hit, और "laptop" miss।

**Other**: Zomato FAQ bot ("refund policy?" के 100 तरीके), Amazon product Q&A।

---

## 💻 Code Example — Basic
```python
import re

cache: dict[str, str] = {}


def norm(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.lower()))     # "HS code?" -> "hs code"


def ask(prompt: str) -> str:
    key = norm(prompt)
    if key in cache:                                      # exact hit
        return cache[key]
    cache[key] = "HS 8517.13"                             # pretend LLM answer
    return cache[key]


print(ask("HS code for smartphone?"), ask("hs code for smartphone"))
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
HS code for smartphone? -> HS 8517.13
hs code for smartphone -> HS 8517.13
HS code for a smartphone please -> HS 8517.13
HS code for laptop -> HS 8517.13
llm calls: 2 | exact: 1 semantic: 1 miss: 2
```
Note the answer for "laptop" is the same string only because `mock_llm` always returns "HS 8517.13". Excerpt from `main.py`:
```python
import time
from dataclasses import dataclass, field


@dataclass
class Entry:
    answer: str
    expires: float
    vec: list[float]


@dataclass
class LLMCache:
    ttl: float = 3600.0
    threshold: float = 0.8
    store: dict[str, Entry] = field(default_factory=dict)
    hits_exact: int = 0
    hits_semantic: int = 0
    misses: int = 0

    def get(self, prompt: str, now: float | None = None) -> str | None:
        now = time.time() if now is None else now          # injectable clock for tests
        e = self.store.get(" ".join(prompt.lower().split()))   # main.py uses norm()
        if e and e.expires > now:                          # TTL check
            self.hits_exact += 1
            return e.answer
        # semantic step (fake_embed + cosine >= threshold) is in main.py
        self.misses += 1
        return None
```

---

## 🟠 FastAPI Integration
Cache-aside in the route; keep one cache per tenant and expose stats.

```python
from fastapi import FastAPI

from main import LLMCache, cached_ask                     # our module

app = FastAPI()
cache = LLMCache(ttl=3600, threshold=0.9)                 # stricter threshold in prod


@app.get("/classify")
async def classify(q: str) -> dict:
    return {"answer": await cached_ask(cache, q)}


@app.get("/cache/stats")
async def stats() -> dict:
    return {"exact": cache.hits_exact, "semantic": cache.hits_semantic, "miss": cache.misses}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a global LLM cache; every `invoke` checks it first.

```python
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

set_llm_cache(InMemoryCache())                            # exact-match caching for all LLM calls
# Semantic: RedisSemanticCache(embedding=..., redis_url=..., score_threshold=0.2)
```
LangGraph nodes can also be cached per node inputs (node-level cache policies).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A semantic threshold that is too low returns wrong answers (for example "smartphone" vs "smartphone case").
✅ Correct: tune threshold on labelled pairs; start high (0.9+).

```python
# Wrong
threshold = 0.5
# Right
threshold = 0.9   # validate on real near-duplicate and near-different pairs
```

❌ Mistake 2: Sharing one cache across users/tenants, leaking private answers.
✅ Correct: include tenant id (and model/prompt version) in the key.

❌ Mistake 3: Caching errors or time-sensitive answers forever. Use a TTL and cache only successes.

---

## 🧠 Tricky Interview Question
**Q**: "Cache hit rate is 70% but users complain about stale duty rates. Why, and what do you do?"

**Answer**: TTL is 3600s by default and the tariff data changed within that window, or the key ignores the data version. Fix: put the knowledge/prompt/model version in the key (so a data update invalidates automatically), shorten TTL for volatile answers, add explicit invalidation on data change. A high hit rate is not the goal; correct hits are.

---

## ⚫ Interview Questions + Answers

Q1: Exact vs semantic cache?
A1: Exact matches the normalised text key (fast, safe). Semantic matches by embedding similarity (higher hit rate, risk of wrong matches).

Q2: Why check exact first?
A2: It is O(1) and free; embeddings cost compute and possibly money.

Q3: Why is `now` a parameter?
A3: Makes TTL logic testable without sleeping.

Q4: Why not cache failures?
A4: You would serve errors for the whole TTL; `cached_ask` only stores successful answers.

Q5 (Hard): Design a cache for a multi-instance service.
A5: Shared store (Redis) for exact keys with TTL; vector index (Redis/Qdrant) for semantic lookups; key includes tenant, model and prompt version; add single-flight locks so concurrent identical misses make one LLM call; monitor hit rate and a sample of semantic hits for correctness.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many repeated or paraphrased questions
- Answers are stable (FAQs, classification of the same product)

❌ Avoid when:
- Answers are personalised or time-sensitive
- Prompts contain unique user data (hit rate near zero)

---

## 📊 Visual Diagram
```
 prompt ─► norm ─► exact key in store & not expired? ─ yes ─► answer (exact hit)
                          │ no
                          ▼
                 fake_embed ─► best cosine among live entries
                          │ >= 0.8 ─────────────────► answer (semantic hit)
                          │ < 0.8
                          ▼
                    mock_llm ─► put(answer, expires=now+ttl) ─► answer (miss)
```

---

## 💰 Cost Impact
A hit costs nothing (no tokens) and saves latency. In the observed run: 4 requests, 2 LLM calls, so 50% fewer calls. Savings scale with hit rate: at 40% hit rate you cut roughly 40% of LLM spend. Semantic caching adds an embedding cost per lookup (small versus a chat call).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Time an entry stays valid | Entry कितनी देर वैध रहती है |
| Exact cache | Same normalised text | हू-ब-हू मिलान |
| Semantic cache | Similar meaning via embeddings | मिलते-जुलते अर्थ का मिलान |
| Cosine similarity | Closeness of two vectors | दो vectors की समानता |
| Cache-aside | Check cache, else compute and store | पहले cache देखो, वरना बनाकर रखो |

---

## ⚡ 3-Line Summary
English: Check an exact cache, then a semantic cache, and only then call the LLM. Use TTL and versioned keys to avoid stale answers. Track hit rate and never cache failures.
Hindi: पहले exact cache, फिर semantic cache देखो, तब ही LLM call करो। Stale जवाबों से बचने को TTL और versioned keys रखो। Hit rate track करो और failures कभी cache न करो।

---

## ➡️ Next Topic
**592. Build Guardrails Layer** — caching saves money; guardrails keep inputs and outputs safe.

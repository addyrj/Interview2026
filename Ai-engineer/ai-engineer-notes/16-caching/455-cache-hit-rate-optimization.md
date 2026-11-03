
---

# 455. Cache Hit Rate Optimization
# हिंदी में: Cache Hit Rate बढ़ाना

---

## 🔵 Simple Definition (English)
Hit rate is the percentage of requests answered from cache. Optimising it means making more requests **look the same** to the cache (normalisation), tuning the similarity threshold, choosing good TTLs, warming the cache with popular queries, and removing noise from the cache key, all without returning wrong answers.

## 🔵 सरल परिभाषा (Hindi)
Hit rate वह प्रतिशत है जितने requests cache से answer होते हैं। इसे बढ़ाने का मतलब है requests को cache के लिए **एक जैसा** बनाना (normalisation), similarity threshold tune करना, सही TTL चुनना, popular queries से cache warm करना और cache key से noise हटाना, बिना ग़लत answers दिए।

---

## 🔴 Problem it Solves
A cache with a 10% hit rate barely pays for itself. Common causes: timestamps or user IDs inside the prompt, different casing/whitespace, short TTLs, too-strict thresholds, and a cold cache after every deploy. Each avoidable miss is paid in tokens and latency.

## 🔴 यह क्यों बना? (Hindi)
10% hit rate वाला cache मुश्किल से अपना खर्च निकालता है। आम कारण: prompt में timestamp या user ID, अलग casing/whitespace, छोटा TTL, बहुत सख़्त threshold, और हर deploy के बाद ठंडा cache। हर avoidable miss पर tokens और latency लगती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Log every request: key, hit/miss, reason for miss
Step 2 → Find top miss reasons (near-duplicate queries, expired TTL, noisy key)
Step 3 → Normalise: lowercase, trim, collapse spaces, strip volatile fields
Step 4 → Split the prompt: static part (cache prefix) vs dynamic part
Step 5 → Tune similarity threshold using a labelled precision/recall curve
Step 6 → Set TTL by data volatility (rates: days, FAQs: weeks)
Step 7 → Warm the cache with the top-N frequent queries after deploy
Step 8 → Re-measure hit rate AND answer quality
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर request log करो: key, hit/miss, miss का कारण
Step 2 → Top miss कारण खोजो (near-duplicates, expired TTL, noisy key)
Step 3 → Normalise: lowercase, trim, extra spaces हटाओ, volatile fields हटाओ
Step 4 → Prompt को static और dynamic हिस्सों में बाँटो
Step 5 → Labelled data से threshold tune करो
Step 6 → Data कितना बदलता है उसके हिसाब से TTL रखो
Step 7 → Deploy के बाद top-N queries से cache warm करो
Step 8 → Hit rate और answer quality दोनों दोबारा measure करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Raw queries "HS code for  iPhone 15 (requested 2025-01-03 10:22)" never repeat because of the timestamp. After stripping timestamps, lowercasing and removing filler words, hit rate rises from 8% to 31%. Warming the cache nightly with the top 1,000 product descriptions raises it further. **Zomato-style**: round delivery location to a zone or pincode in the key, so "near me" queries from the same area share answers.

## 🟡 Real Example Hindi mein
**Tariff System**: "HS code for  iPhone 15 (requested 2025-01-03 10:22)" timestamp की वजह से कभी repeat नहीं होता। Timestamp हटाने, lowercase करने और filler words हटाने से hit rate 8% से 31% हो जाता है। रोज़ रात top 1,000 products से cache warm करने पर और बढ़ता है। **Zomato-style**: key में location को zone/pincode तक round करो।

---

## 💻 Code Example — Basic
```python
# Basic: normalisation raises hit rate (pure Python, runs offline)
import re                                                  # regex for cleaning

STOP = {"please", "pls", "kindly", "tell", "me", "the", "a"}   # filler words to drop

def normalize(q: str) -> str:
    q = q.lower().strip()                                  # lowercase and trim
    q = re.sub(r"\(.*?\)", " ", q)                         # drop text in brackets (timestamps)
    q = re.sub(r"[^a-z0-9\s]", " ", q)                     # drop punctuation
    words = [w for w in q.split() if w not in STOP]        # remove filler words
    return " ".join(words)                                 # single-space join

cache: dict[str, str] = {}                                 # key -> answer
hits = misses = 0                                          # counters

for q in ["HS code for iPhone 15?", "hs code for  iphone 15 please", "HS code for iPhone 15 (10:22)"]:
    key = normalize(q)                                     # build normalised key
    if key in cache:
        hits += 1                                          # found: hit
    else:
        misses += 1                                        # not found: miss
        cache[key] = "8517.13"                             # pretend LLM answer
print(f"hits={hits} misses={misses}")                      # 2 hits, 1 miss after normalisation
```

## 💻 Code Example — Advanced
```python
# Production: hit-rate analysis, miss reasons and cache warming (async)
import asyncio                                             # concurrency for warming
from collections import Counter                            # count miss reasons
from typing import Awaitable, Callable, Optional           # type hints

class HitRateOptimizer:
    def __init__(self) -> None:
        self.reasons: Counter[str] = Counter()             # miss reason -> count
        self.total = 0                                     # all requests
        self.hits = 0                                      # hit requests

    def record(self, hit: bool, reason: str = "") -> None:
        self.total += 1                                    # one more request
        if hit:
            self.hits += 1                                 # one more hit
        else:
            self.reasons[reason or "unknown"] += 1         # why we missed

    def report(self) -> dict:
        rate = self.hits / self.total if self.total else 0.0   # avoid divide by zero
        return {"hit_rate": round(rate, 3), "top_miss_reasons": self.reasons.most_common(3)}

async def warm_cache(
    top_queries: list[str],                                # most frequent queries
    llm: Callable[[str], Awaitable[str]],                  # async LLM call
    put: Callable[[str, str], Awaitable[None]],            # async cache write
    concurrency: int = 5,                                  # protect rate limits
) -> int:
    sem = asyncio.Semaphore(concurrency)                   # limit parallel calls
    done = 0                                               # successful warms

    async def one(q: str) -> None:
        nonlocal done
        async with sem:                                    # wait for a slot
            try:
                await put(q, await llm(q))                 # compute and store
                done += 1                                  # count success
            except Exception:
                pass                                       # skip failures, keep going

    await asyncio.gather(*(one(q) for q in top_queries))   # run all warmers
    return done                                            # how many were warmed
```

---

## 🟠 FastAPI Integration
Normalise in one place (a dependency or middleware helper) and record miss reasons.

```python
from fastapi import FastAPI                                # framework
from pydantic import BaseModel                             # schema

app = FastAPI()
opt = HitRateOptimizer()                                   # from the advanced example
store: dict[str, str] = {}                                 # replace with Redis/Qdrant

class Q(BaseModel):
    question: str                                          # user text

@app.post("/ask")
async def ask(body: Q) -> dict:
    key = normalize(body.question)                         # same normaliser everywhere
    if key in store:
        opt.record(True)                                   # log hit
        return {"answer": store[key], "cached": True}
    opt.record(False, "new_query")                         # log miss with reason
    store[key] = "answer from LLM"                         # placeholder for the LLM call
    return {"answer": store[key], "cached": False}

@app.get("/metrics/hit-rate")
async def hit_rate() -> dict:
    return opt.report()                                    # expose to dashboards
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain, `set_llm_cache` keys on the exact prompt plus model parameters, so putting volatile data (timestamps) in the prompt kills hits. Build prompts with `ChatPromptTemplate` so the static template stays identical, and normalise user input **before** it enters the template.

```python
from langchain_core.prompts import ChatPromptTemplate      # prompt templates

prompt = ChatPromptTemplate.from_messages([
    ("system", "You classify goods into HS codes."),       # static: identical every call
    ("human", "{question}"),                               # only this part changes
])
chain = prompt | llm                                       # llm with set_llm_cache enabled
await chain.ainvoke({"question": normalize(raw_question)}) # normalised input = more hits
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Volatile data in the key
```python
# Wrong — current time makes every key unique:
key = f"{question}|{datetime.now()}"

# Correct — only stable inputs in the key:
key = normalize(question)
```

❌ Mistake 2: Lowering threshold blindly to chase hit rate
```python
# Wrong — 0.80 threshold: more hits, but wrong answers
# Correct — pick threshold from a labelled precision curve (e.g. precision >= 99%)
```

❌ Mistake 3: Over-normalising
```python
# Wrong — removing numbers: "iphone 15" and "iphone 12" collide
q = re.sub(r"\d+", "", q)
# Correct — keep identifiers, numbers, units; drop only filler and volatile fields
```

---

## 🧠 Tricky Interview Question
**Q**: "You raised the hit rate from 30% to 70%, and customer complaints went up. What happened and what do you do?"

**Answer**: Optimising for hit rate alone traded precision for volume: the threshold was probably lowered or normalisation merged distinct queries. Hit rate is a means, not a goal. Track **precision of hits** (sampled and judged, or user thumbs-down on cached answers) next to the hit rate. Roll back to the best precision-constrained point, add metadata filters, keep identifiers in the key, and introduce a "verify" step (cheap model or rules) for risky categories.

---

## ⚫ Interview Questions + Answers

Q1: What lowers cache hit rate the most?
A1: Noisy keys (timestamps, IDs), short TTLs, strict thresholds, and cold caches after deploys.

Q2: What is cache warming?
A2: Pre-populating the cache with the most frequent queries before users arrive, e.g. after a deploy or nightly.

Q3: How do you split a prompt to improve provider prompt caching?
A3: Put the static parts (system prompt, tools, reference docs) first and dynamic user input last. Provider caches match on the prefix, so any change early in the prompt invalidates everything after it.

Q4: How do you set the TTL?
A4: By how fast the underlying data changes and the cost of staleness. Tariff rates might use days; static FAQs weeks. Use event-based invalidation for known updates.

Q5: (Hard) How do you increase hit rate for personalised queries without leaking data?
A5: Split the answer into a shared, cacheable part (general tariff info) and a personalised part (user's shipment), cache the first globally and compose the second at request time. Or key by segment (country, plan) instead of by user.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Hit rate is below what your traffic repetition suggests
- You can sample cached answers to check precision
- Prompts have a stable static prefix

❌ Avoid when:
- Queries are unique by nature (open-ended creative tasks)
- Correctness cost is high and you cannot verify cached answers

---

## 📊 Visual Diagram
```
 Raw query  ──► normalise ──► strip volatile ──► key
                                   │
   Miss reasons dashboard  ◄───────┤
   - noisy key      40%            ▼
   - TTL expired    25%      cache lookup ──► hit ──► answer
   - new query      35%            │
                                   └─► miss ──► LLM ──► store
   Warm cache nightly with top-N  ─────────────────────┘
```

---

## 💰 Cost Impact
- Every extra 10 points of hit rate removes 10% of LLM calls (at similar token sizes).
- Normalisation and prefix-ordering cost almost nothing, so they are the best first moves. Warming costs LLM tokens up front: only warm queries with high expected reuse.
- Token usage: a hit uses 0 LLM tokens; a miss uses full input + output tokens.
- Prices vary by provider and are illustrative in these notes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Normalisation | Make equal queries look identical | queries को एक जैसा बनाना |
| Cache warming | Pre-fill cache with popular queries | cache पहले से भरना |
| Cold start | Empty cache after restart | खाली cache |
| Miss reason | Why a request missed | miss का कारण |
| Precision of hits | How many hits are correct | सही hits का प्रतिशत |
| Static prefix | Unchanging start of a prompt | prompt का स्थिर हिस्सा |

---

## ⚡ 3-Line Summary
English: Raise hit rate by cleaning keys, ordering prompts static-first, tuning thresholds and TTLs, and warming the cache. Always track hit precision, not only hit rate. Start with cheap wins like normalisation.
Hindi: Keys साफ़ करके, prompt में static हिस्सा पहले रखकर, threshold और TTL tune करके और cache warm करके hit rate बढ़ाओ। सिर्फ़ hit rate नहीं, hits की precision भी track करो। शुरुआत normalisation जैसे सस्ते उपायों से करो।

---

## ➡️ Next Topic
**456. Streaming + Caching** — how to cache answers when the user receives them token by token.

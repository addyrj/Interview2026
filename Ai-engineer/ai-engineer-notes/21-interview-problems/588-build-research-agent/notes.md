---

# 588. Build Research Agent
# हिंदी में: Research Agent बनाना

---

## 🔵 Simple Definition (English)
A research agent breaks a topic into sub-questions, searches for each one in parallel, removes duplicate sources, and writes a report where every claim carries a [n] citation.

## 🔵 सरल परिभाषा (Hindi)
Research agent किसी topic को sub-questions में बाँटता है, हर एक की search parallel चलाता है, duplicate sources हटाता है, और ऐसा report लिखता है जिसकी हर बात पर [n] citation होता है।

---

## 🔴 Problem it Solves
A single search query rarely covers a broad topic, and running sub-searches one after another is slow. One failing or hanging search can break the whole run. Reports without sources cannot be trusted.

## 🔴 यह क्यों बना? (Hindi)
एक search query बड़े topic को cover नहीं करती, और sub-searches एक-एक करके चलाना धीमा है। एक search के fail या hang होने से पूरा run टूट सकता है। बिना sources के report पर भरोसा नहीं किया जा सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → plan(topic): make sub-questions (us/india/eu/mars tariff <topic>)
Step 2 → asyncio.gather runs safe_search for all of them at once
Step 3 → safe_search wraps web_search in wait_for(timeout=1.0), errors -> []
Step 4 → Dedupe results by URL with seen.setdefault(url, source)
Step 5 → synthesize(): one line per source with [i], then a Sources list
Step 6 → No evidence at all -> "No evidence found."
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → plan(topic): sub-questions बनाओ (us/india/eu/mars tariff <topic>)
Step 2 → asyncio.gather से सारे safe_search एक साथ चलाओ
Step 3 → safe_search, web_search को wait_for(timeout=1.0) में लपेटता है, error पर []
Step 4 → URL से dedupe करो: seen.setdefault(url, source)
Step 5 → synthesize(): हर source की एक line [i] के साथ, फिर Sources list
Step 6 → कोई evidence न हो तो "No evidence found."
```

---

## 🟡 Real World Example
**Tariff Classification System**: a trade analyst asks "smartphones". The agent searches US, India, EU and a bogus "mars" query at once. Mars returns nothing and is ignored; the EU search also returns the India page, which is deduped. Report: 3 cited facts.

**Other**: Amazon market-research bots, Zomato competitor-pricing summaries.

## 🟡 Real Example Hindi mein
**Tariff System**: trade analyst "smartphones" पूछता है। Agent US, India, EU और एक बेकार "mars" query साथ में चलाता है। Mars से कुछ नहीं आता, ignore होता है; EU search India वाला page भी लाता है, जो dedupe हो जाता है। Report में 3 cited facts।

**Other**: Amazon market-research bots, Zomato competitor-pricing summaries।

---

## 💻 Code Example — Basic
```python
import asyncio


async def search(q: str) -> str:
    await asyncio.sleep(0.01)                             # simulate network latency
    return f"result for {q}"


async def main() -> None:
    qs = ["us tariff", "india tariff", "eu tariff"]
    results = await asyncio.gather(*(search(q) for q in qs))  # all three run concurrently
    print(results)


asyncio.run(main())
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
Report: smartphones
- US duty on smartphones is mostly 0 percent under ITA. [1]
- India levies about 20 percent duty on smartphones. [2]
- EU applies 0 percent on most smartphones. [3]

Sources:
[1] https://example.org/a
[2] https://example.org/b
[3] https://example.org/c
```
Excerpt from `main.py` (isolation + dedupe):
```python
import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    url: str
    snippet: str


async def web_search(query: str) -> list[Source]:
    await asyncio.sleep(0.01)
    return []                                             # real version looks up INDEX


async def safe_search(query: str) -> list[Source]:
    """Timeout + error isolation per sub-question."""
    try:
        return await asyncio.wait_for(web_search(query), timeout=1.0)
    except (asyncio.TimeoutError, Exception):
        return []                                         # one bad search never kills the run


def plan(topic: str) -> list[str]:
    return [f"{c} tariff {topic}" for c in ("us", "india", "eu", "mars")]


async def research(topic: str) -> list[Source]:
    results = await asyncio.gather(*(safe_search(q) for q in plan(topic)))
    seen: dict[str, Source] = {}
    for group in results:
        for src in group:
            seen.setdefault(src.url, src)                 # keep first copy per URL
    return list(seen.values())
```

---

## 🟠 FastAPI Integration
Long research is slow, so return quickly or stream. This simple version awaits the result with a global timeout.

```python
import asyncio

from fastapi import FastAPI, HTTPException

from main import research                                 # our module

app = FastAPI()


@app.get("/research")
async def research_endpoint(topic: str) -> dict:
    try:
        report = await asyncio.wait_for(research(topic), timeout=20)  # overall budget
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="research timed out")
    return {"report": report}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph's `Send` API fans out one node per sub-question and merges results with a reducer: the graph version of `asyncio.gather` plus dedupe.

```python
import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict):
    topic: str
    sources: Annotated[list[dict], operator.add]          # reducer merges parallel results
    report: str


# planner node -> Send("search", {"q": q}) for each q -> synthesize node
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Searching sequentially with a `for` loop and `await`.
✅ Correct: `asyncio.gather` for independent searches.

```python
# Wrong
for q in queries:
    results.append(await web_search(q))
# Right
results = await asyncio.gather(*(safe_search(q) for q in queries))
```

❌ Mistake 2: No per-search timeout; one hung call blocks everything.
✅ Correct: `asyncio.wait_for(..., timeout)` inside `safe_search`.

❌ Mistake 3: Reports without citations or with duplicate sources inflating confidence.

---

## 🧠 Tricky Interview Question
**Q**: "Two sources disagree (US: 0 percent, India: 20 percent). Is that a bug in the agent?"

**Answer**: No, here the sub-questions are about different countries, so both are correct. But if two sources answer the same question differently, the synthesiser must not average or pick silently: show both with citations, prefer authoritative/newer sources, and flag the conflict. Note `safe_search` swallows errors, so also log them, otherwise missing evidence looks like "nothing exists".

---

## ⚫ Interview Questions + Answers

Q1: Why `asyncio.gather`?
A1: Searches are IO-bound and independent; running them concurrently cuts total latency to roughly the slowest one.

Q2: What does `seen.setdefault(url, src)` do?
A2: Keeps the first source per URL, removing duplicates found by several queries.

Q3: Why is the "mars" query in `plan`?
A3: It demonstrates that a sub-question with no results is handled gracefully (empty list, no crash).

Q4: Why must every claim have a [n]?
A4: So readers can verify and so we can detect unsupported claims.

Q5 (Hard): How do you stop the agent from running unbounded?
A5: Cap sub-questions, depth/iterations, total time and token budget; use per-call timeouts, bounded concurrency with a semaphore, and stop when new searches add no new sources.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Broad questions needing multiple sources
- Reports that must be cited

❌ Avoid when:
- A single lookup answers it (just search once)

---

## 📊 Visual Diagram
```
 topic ─► plan() ─► [q1, q2, q3, q4]
                        │  asyncio.gather
          ┌─────────┬───┴─────┬─────────┐
          ▼         ▼         ▼         ▼
      safe_search safe_search ...   (timeout / error -> [])
          └─────────┴───┬─────┴─────────┘
                        ▼
                dedupe by URL
                        ▼
        synthesize ─► report with [n] + Sources
```

---

## 💰 Cost Impact
Each sub-question multiplies search calls and, in production, LLM tokens for reading results. Parallelism lowers latency, not cost. Limit the number of sub-questions, truncate snippets, dedupe before synthesis, and use a small model for planning.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fan-out | Run many tasks at once | कई काम एक साथ चलाना |
| Dedupe | Remove duplicates | Duplicate हटाना |
| Citation | [n] pointing to a source | Source का संदर्भ |
| Timeout | Stop waiting after a limit | इंतज़ार की सीमा |
| Synthesis | Combining findings into a report | नतीजों को मिलाकर report बनाना |

---

## ⚡ 3-Line Summary
English: Plan sub-questions, search them concurrently with timeouts, dedupe by URL. Write the report with numbered citations. Failures must not kill the run.
Hindi: Sub-questions बनाओ, timeout के साथ concurrently search करो, URL से dedupe करो। Report numbered citations के साथ लिखो। एक failure पूरा run न तोड़े।

---

## ➡️ Next Topic
**589. Build RAG Evaluation Pipeline** — once agents answer, we need numbers to prove retrieval and answers are good.

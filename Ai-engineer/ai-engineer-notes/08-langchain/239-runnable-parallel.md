---

# 239. RunnableParallel
# हिंदी में: RunnableParallel

---

## 🔵 Simple Definition (English)
`RunnableParallel` runs several Runnables at the same time on the same input and returns a dict of their results. A plain dict inside an LCEL chain is automatically a RunnableParallel.

## 🔵 सरल परिभाषा (Hindi)
`RunnableParallel` एक ही input पर कई Runnables को एक साथ चलाता है और उनके results का dict लौटाता है। LCEL chain के अंदर सादा dict अपने-आप RunnableParallel बन जाता है।

---

## 🔴 Problem it Solves
Many apps need several independent calls: retrieve docs, fetch user profile, classify intent, call a duty API. Running them one after another adds their latencies. Parallel execution makes total time about the slowest branch, not the sum.

## 🔴 यह क्यों बना? (Hindi)
कई apps में कई independent calls चाहिए: docs retrieve, user profile, intent classify, duty API। एक के बाद एक चलाने पर latency जुड़ती जाती है। Parallel में कुल समय सबसे धीमी branch जितना होता है, जोड़ जितना नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define branches: RunnableParallel(a=r1, b=r2) or {"a": r1, "b": r2}
Step 2 → invoke(x): every branch receives the same x
Step 3 → Sync: branches run in a thread pool; async: asyncio.gather
Step 4 → Wait for all branches
Step 5 → Return {"a": out1, "b": out2}
Step 6 → If any branch raises, the whole call raises (unless handled inside)
Step 7 → Pipe the dict to the next step (prompt, merger function)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Branches तय: RunnableParallel(a=r1, b=r2) या {"a": r1, "b": r2}
Step 2 → invoke(x): हर branch को वही x मिलता है
Step 3 → Sync में thread pool; async में asyncio.gather
Step 4 → सभी branches का इंतज़ार
Step 5 → {"a": out1, "b": out2} लौटता है
Step 6 → कोई branch fail हो तो पूरा call fail (जब तक अंदर handle न हो)
Step 7 → Dict को अगले step (prompt, merger) में pipe करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: for each product we simultaneously (1) retrieve HS heading chunks, (2) fetch current BCD/IGST rates from the duty API, (3) check restricted-goods list. Total time 600 ms (slowest) instead of 1,500 ms. **Zomato AI**: parallel lookup of restaurant info, user preferences and live ETA before writing the recommendation.

## 🟡 Real Example Hindi mein
**Tariff System**: हर product के लिए एक साथ (1) HS heading chunks retrieve, (2) duty API से BCD/IGST rates, (3) restricted-goods list check। कुल समय 600 ms (सबसे धीमी) बनाम 1,500 ms। **Zomato AI**: recommendation लिखने से पहले restaurant info, user preferences और live ETA parallel में।

---

## 💻 Code Example — Basic
```python
# Runs offline: prove parallel branches overlap in time
import time
from langchain_core.runnables import RunnableParallel, RunnableLambda

def slow(name: str, secs: float):
    def _f(x: str) -> str:
        time.sleep(secs)  # simulate IO
        return f"{name}:{x}"
    return RunnableLambda(_f)

par = RunnableParallel(docs=slow("docs", 0.5), rate=slow("rate", 0.5), restricted=slow("restricted", 0.5))

t0 = time.perf_counter()
print(par.invoke("earbuds"))  # dict with three keys
print(f"parallel took {time.perf_counter() - t0:.2f}s (sequential would be ~1.5s)")

# Merge step after parallel:
merge = par | RunnableLambda(lambda d: " | ".join(d.values()))
print(merge.invoke("shoes"))
```

## 💻 Code Example — Advanced
```python
# Async parallel with per-branch timeouts + graceful degradation
import asyncio
import httpx
from langchain_core.runnables import RunnableParallel, RunnableLambda

async def fetch_docs(product: str) -> list[str]:
    await asyncio.sleep(0.2)  # replace with: await retriever.ainvoke(product)
    return [f"doc about {product}"]

async def fetch_rate(product: str) -> dict:
    async with httpx.AsyncClient(timeout=2.0) as c:
        r = await c.get("http://duty.internal/rate", params={"q": product})
        r.raise_for_status()
        return r.json()

def safe(fn, default, timeout: float = 3.0):
    """Wrap an async function: on error/timeout return default instead of failing everything."""
    async def _wrapped(x: str):
        try:
            return await asyncio.wait_for(fn(x), timeout=timeout)
        except Exception as exc:  # timeout, HTTP error...
            return {"_error": str(exc), "value": default}
    return RunnableLambda(_wrapped)

gather = RunnableParallel(
    docs=safe(fetch_docs, []),
    rate=safe(fetch_rate, None),
)

async def enrich(product: str) -> dict:
    return await gather.ainvoke(product, config={"max_concurrency": 5})
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/enrich")
async def enrich_route(product: str) -> dict:
    data = await enrich(product)  # parallel fan-out inside one request
    return data
# FastAPI runs async handlers on the event loop; async branches avoid blocking threads.
```

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, parallelism is expressed by fanning out edges from one node to several nodes (they run in the same superstep) and merging with reducers on state keys. Use RunnableParallel inside a single node when branches are small and tied together.

```python
# graph.add_edge("start", "retrieve"); graph.add_edge("start", "rates")   # both run in parallel
# State reducers (Annotated[list, operator.add]) merge their outputs.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting branches to see each other
```python
# Wrong: {"docs": retriever, "ctx": lambda x: x["docs"]}   # x is the original input, no 'docs' yet
# Right: chain sequentially with assign
RunnablePassthrough.assign(docs=retriever).assign(ctx=lambda d: fmt(d["docs"]))
```

❌ Mistake 2: Blocking calls in async branches
```python
# Wrong: async def f(x): return requests.get(...).json()   # blocks the loop; no real parallelism
# Right: use httpx.AsyncClient / aiohttp
```

---

## 🧠 Tricky Interview Question
**Q**: "You ran 3 sync branches in RunnableParallel but latency is still the sum. Why?"

**Answer**: Sync branches use a thread pool, which helps only for IO that releases the GIL. CPU-bound Python code stays serialized by the GIL, and a blocking C extension may hold it. Also `max_concurrency=1` in config serializes. Use async IO, processes for CPU work, or check config.

---

## ⚫ Interview Questions + Answers

Q1: What does RunnableParallel return? (Easy)
A1: A dict mapping each key to its branch's output.

Q2: How do you create one? (Easy)
A2: `RunnableParallel(a=r1, b=r2)` or a dict literal in a chain.

Q3: What happens if one branch fails? (Medium)
A3: The exception propagates and the whole parallel step fails. Wrap branches (try/except, `.with_fallbacks`) to degrade gracefully.

Q4: How to limit concurrency? (Medium)
A4: Pass `config={"max_concurrency": N}`.

Q5: Compare with LangGraph fan-out. (Hard)
A5: RunnableParallel is inline, stateless, all branches share one input, result is a dict. LangGraph fan-out is graph-level, with shared state, reducers, checkpointing, and per-node retries. Choose by complexity and need for durability.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Independent lookups on the same input
- Reducing end-to-end latency in RAG

❌ Avoid when:
- Steps depend on each other
- Rate limits would be exceeded

---

## 📊 Visual Diagram
```
              input x
     ┌───────────┼───────────┐
     ▼           ▼           ▼
  retriever   duty API   restricted-list
     │           │           │
     └───────────┼───────────┘
                 ▼
  {"docs":..., "rate":..., "restricted":...} ─► prompt
  time = max(branches), not sum
```

---

## 💰 Cost Impact
Parallel does not change tokens per call but it raises request burst: more concurrent LLM calls can hit rate limits (429s) and retries cost extra tokens. Use `max_concurrency`. Non-LLM branches (DB, APIs) are cheap. Latency saving can also reduce infrastructure time per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RunnableParallel | Run branches together | साथ-साथ चलाना |
| Fan-out | Split into branches | शाखाओं में बाँटना |
| Fan-in | Merge results | नतीजे मिलाना |
| max_concurrency | Parallel limit | अधिकतम parallel |
| Reducer | State merge rule | State मिलाने का नियम |

---

## ⚡ 3-Line Summary
English: RunnableParallel runs branches concurrently with the same input and returns a dict. Latency becomes the slowest branch. Handle failures per branch and cap concurrency.
Hindi: RunnableParallel एक ही input पर branches साथ चलाता है और dict देता है। Latency सबसे धीमी branch जितनी होती है। हर branch की failure संभालो और concurrency सीमित रखो।

---

## ➡️ Next Topic
**240. RunnableLambda** — wrapping your own functions as chain steps.

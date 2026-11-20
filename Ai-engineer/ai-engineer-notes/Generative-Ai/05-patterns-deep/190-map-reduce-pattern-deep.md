---

# 190. Map-Reduce Pattern — Deep
# हिंदी में: Map-Reduce Pattern (बाँटो, समानांतर चलाओ, जोड़ो) — विस्तार से
# Framework: All (LangGraph `Send` shown in code)
# Already Known: No

> Verified offline with fake LLM calls (no API key). Python 3.13, langgraph 1.2.22, langchain-core 1.8.1, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
Map-Reduce splits a large input into many independent chunks, runs the same agent on each chunk in parallel (the "map" step), then combines all partial results into one answer (the "reduce" step). It is the standard way to handle input that does not fit in one context window.

## 🔵 सरल परिभाषा (Hindi)
Map-Reduce बड़े input को कई स्वतंत्र टुकड़ों में बाँटता है, हर टुकड़े पर वही agent समानांतर चलाता है ("map" step), फिर सारे आंशिक नतीजों को एक जवाब में जोड़ता है ("reduce" step)। जो input एक context window में नहीं समाता, उसे सँभालने का यह मानक तरीका है।

---

## 🔴 Problem it Solves
A 2,000-page tariff schedule or 500 customs declarations do not fit in one prompt, and even if they fit, models lose detail in very long contexts and a single serial pass is slow. Map-Reduce gives parallelism (lower latency), bounded context per call, and isolation of failures to one chunk.

## 🔴 यह क्यों बना? (Hindi)
2,000 पन्नों की tariff schedule या 500 customs declarations एक prompt में नहीं आते, और आ भी जाएँ तो बहुत लंबे context में model विवरण खो देता है और एक serial pass धीमा होता है। Map-Reduce parallelism (कम latency), हर call में सीमित context और failure को एक टुकड़े तक सीमित रखने की सुविधा देता है।

---

## 🟢 How it Works

```
Step 1 → SPLIT: cut input into chunks (by page / row / token size) with small overlap
Step 2 → MAP: run the same prompt on every chunk concurrently (bounded concurrency)
Step 3 → Each map call returns a SMALL structured partial result (not prose)
Step 4 → Drop or retry failed chunks; keep chunk ids so nothing is silently lost
Step 5 → REDUCE: merge partials (deterministic code first, LLM merge only if needed)
Step 6 → If partials are still too big: hierarchical reduce (reduce in groups, then reduce again)
Step 7 → Return final answer + coverage report (chunks ok / failed)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → SPLIT: input को टुकड़ों में काटो (page / row / token size से) थोड़े overlap के साथ
Step 2 → MAP: हर टुकड़े पर वही prompt एक साथ चलाओ (सीमित concurrency)
Step 3 → हर map call एक छोटा structured आंशिक नतीजा लौटाए (गद्य नहीं)
Step 4 → Fail हुए टुकड़ों को हटाओ या retry करो; chunk id रखो ताकि कुछ चुपचाप न खो जाए
Step 5 → REDUCE: partials जोड़ो (पहले deterministic code, ज़रूरत हो तभी LLM merge)
Step 6 → Partials फिर भी बड़े हों तो hierarchical reduce (समूहों में reduce, फिर दोबारा)
Step 7 → अंतिम जवाब + coverage report लौटाओ (कितने chunks ठीक / fail)
```

---

## 🟡 Real World Example
**Tariff Agent**: A user uploads a 300-line commercial invoice. The map step classifies each line item to an HS code in parallel (chunks of 10 lines). The reduce step totals the estimated duty per HS chapter and lists lines needing review. Also: Research Agent summarizing 50 papers (summary per paper, then combined brief), Code Agent reviewing every file in a repo.

## 🟡 Real Example Hindi mein
**Tariff Agent**: User 300 पंक्तियों वाला commercial invoice upload करता है। Map step में हर line item (10 पंक्तियों के chunks) को समानांतर में HS code मिलता है। Reduce step हर HS chapter का अनुमानित duty जोड़ता है और समीक्षा-योग्य lines की सूची देता है। अन्य: Research Agent जो 50 papers का सारांश बनाता है (हर paper का सारांश, फिर संयुक्त brief), Code Agent जो repo की हर file review करता है।

---

## 💻 Code Example — Basic
```python
# Basic map-reduce over invoice lines using plain Python and a fake "LLM". Offline.
from collections import defaultdict               # group totals by HS chapter

LINES = ["bluetooth speaker", "laptop", "usb cable", "smart watch", "laptop stand"]


def split(items: list[str], size: int) -> list[list[str]]:   # SPLIT step
    return [items[i:i + size] for i in range(0, len(items), size)]


def fake_llm_classify(item: str) -> dict[str, str]:           # stand-in for an LLM call
    table = {"speaker": "8518", "laptop": "8471", "cable": "8544", "watch": "8517"}
    for key, code in table.items():                           # crude keyword match
        if key in item:
            return {"item": item, "chapter": code}
    return {"item": item, "chapter": "UNKNOWN"}


def map_chunk(chunk: list[str]) -> list[dict[str, str]]:      # MAP: one chunk -> partial result
    return [fake_llm_classify(x) for x in chunk]


def reduce_all(partials: list[list[dict[str, str]]]) -> dict[str, int]:  # REDUCE
    counts: dict[str, int] = defaultdict(int)
    for part in partials:                                     # deterministic merge, no LLM needed
        for row in part:
            counts[row["chapter"]] += 1
    return dict(counts)


if __name__ == "__main__":
    chunks = split(LINES, 2)                                  # 3 chunks
    partials = [map_chunk(c) for c in chunks]                 # (sequential here; parallel below)
    print(reduce_all(partials))                               # {'8518': 1, '8471': 2, ...}
```

## 💻 Code Example — Advanced
```python
# Advanced: LangGraph map-reduce using Send (dynamic fan-out) with a reducer,
# async map nodes, FastAPI endpoint, coverage report. Offline (fake LLM).
import operator                                   # list-append reducer
from typing import Annotated, TypedDict
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # offline client
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send                  # dynamic fan-out primitive
from pydantic import BaseModel


class Overall(TypedDict):                         # graph state
    chunks: list[list[str]]
    partials: Annotated[list[dict], operator.add]  # reducer merges parallel writes
    summary: dict


class MapIn(TypedDict):                           # input of each parallel map task
    chunk_id: int
    items: list[str]


TABLE = {"speaker": "8518", "laptop": "8471", "cable": "8544", "watch": "8517"}


def fan_out(state: Overall) -> list[Send]:        # one Send per chunk -> parallel map tasks
    return [Send("map_chunk", {"chunk_id": i, "items": c})
            for i, c in enumerate(state["chunks"])]


async def map_chunk(inp: MapIn) -> dict:          # MAP node (fake async LLM per chunk)
    try:
        rows = []
        for item in inp["items"]:
            ch = next((c for k, c in TABLE.items() if k in item), "UNKNOWN")
            rows.append({"item": item, "chapter": ch})
        return {"partials": [{"chunk_id": inp["chunk_id"], "ok": True, "rows": rows}]}
    except Exception as exc:                      # one bad chunk must not kill the run
        return {"partials": [{"chunk_id": inp["chunk_id"], "ok": False, "error": str(exc)}]}


async def reduce_node(state: Overall) -> dict:    # REDUCE node
    counts: dict[str, int] = {}
    ok = [p for p in state["partials"] if p["ok"]]
    for p in ok:
        for r in p["rows"]:
            counts[r["chapter"]] = counts.get(r["chapter"], 0) + 1
    return {"summary": {"by_chapter": counts,
                        "chunks_ok": len(ok),
                        "chunks_failed": len(state["partials"]) - len(ok)}}


b = StateGraph(Overall)
b.add_node("map_chunk", map_chunk)
b.add_node("reduce", reduce_node)
b.add_conditional_edges(START, fan_out, ["map_chunk"])   # fan-out from START
b.add_edge("map_chunk", "reduce")                        # all map tasks finish, then reduce
b.add_edge("reduce", END)
graph = b.compile()


class Req(BaseModel):
    items: list[str]
    chunk_size: int = 2


app = FastAPI()


@app.post("/invoice")
async def invoice(req: Req) -> dict:
    chunks = [req.items[i:i + req.chunk_size] for i in range(0, len(req.items), req.chunk_size)]
    out = await graph.ainvoke({"chunks": chunks, "partials": [], "summary": {}})
    approx_tokens = sum(len(i) for i in req.items) // 4 + 20 * len(chunks)  # rough estimate
    return {**out["summary"], "approx_tokens": approx_tokens}


if __name__ == "__main__":
    items = ["bluetooth speaker", "laptop", "usb cable", "smart watch", "laptop stand"]
    print(TestClient(app).post("/invoice", json={"items": items}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Fan-out | `Send` for dynamic parallel tasks | Several tasks/agents, or your own loop | `asyncio.gather` over runs | Parallel agent runs / your code |
| Merge | Reducer on state + reduce node | Aggregator task/agent | Your Python | Aggregator agent / your code |
| Dynamic number of chunks | Yes (Send per chunk) | Own code | Own code | Own code |
| Failure handling | Per-node code | Per-task | try/except per call | try/except per agent |
| Best for | Dynamic fan-out inside a graph | Fixed role teams | Simple parallel calls | Parallel debate-style work |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Chunks that cut a record in half (a table row, a sentence).
✅ Correct: Split on natural boundaries with a small overlap.

❌ Mistake 2: Map outputs are long prose, so the reduce step overflows.
✅ Correct: Map returns small structured JSON; reduce deterministically when possible.

❌ Mistake 3: Unbounded parallelism triggers 429 rate limits.
✅ Correct: Use a semaphore or batch size; retry with backoff.

❌ Mistake 4: Silently dropping failed chunks.
✅ Correct: Track chunk ids and return a coverage report.

---

## 🧠 Tricky Interview Question
Your map-reduce summary of 500 documents misses a fact that only appears when two documents are read together. Why, and how do you fix it?

Answer: Map isolates chunks, so cross-chunk relationships are invisible to map calls, and the reduce step only sees compressed partials. Fixes: (1) map extracts structured facts and entities, not summaries, so reduce can join them; (2) use overlapping windows or group related documents (by customer or shipment id) into the same chunk before mapping; (3) add a second pass: reduce finds candidate links, then a targeted "refine" call reads the original source passages; (4) hierarchical reduce with rich intermediate state. Map-reduce suits decomposable tasks; if the task needs global reasoning, consider a retrieval-based or iterative refine approach.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What are map and reduce in LLM workflows?
A1: Map applies the same prompt to each chunk in parallel; reduce combines the partial outputs into the final answer.

Q2: (Medium) Map-reduce vs refine vs stuff?
A2: Stuff: put everything in one prompt (simple, limited by context). Map-reduce: parallel, scalable, loses cross-chunk links. Refine: sequential, carries a running answer across chunks, better coherence but slow.

Q3: (Hard) What do you do when reduce input is too big?
A3: Hierarchical (tree) reduce: reduce groups of partials, then reduce the results again; or have map emit compact structured data and merge with code.

Q4: (Hard) How do you control cost and rate limits?
A4: Bounded concurrency, small chunk prompts, a cheaper model for map, caching per chunk hash, retries with backoff, and a token budget per job.

Q5: (System Design) Design a service that processes 10,000 invoices per day with 200 lines each.
A5: Queue-based workers; chunk per invoice section; map with a cheap model and strict JSON schema; per-chunk idempotency key and cache; reduce in code; results store with coverage and failures; dead-letter queue for failed chunks; metrics for tokens per invoice and failure rate.

---

## 💰 Cost Impact
- Token formula (approximate): `total ≈ Σ chunks (prompt + chunk_tokens + output) + reduce_tokens`. Overlap adds `overlap/chunk_size` extra tokens. Parallelism reduces latency but not token cost.
- Tips: cheap model for map, short structured outputs, deterministic reduce, cache by chunk hash, tune chunk size (too small repeats the prompt overhead).
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Input is large and splits into independent pieces
- You need lower latency through parallelism
- Partial results are small and mergeable

❌ Avoid when:
- Pieces depend on each other (needs global reasoning)
- Input already fits comfortably in one call
- Strict ordering is required

---

## 📊 Visual Diagram
```
                 +--> [Map: chunk 0] --+
 big input       |                     |
 --> [Split] --> +--> [Map: chunk 1] --+--> [Reduce] --> final answer
                 |                     |       |
                 +--> [Map: chunk N] --+       +--> coverage (ok / failed)
         (parallel, bounded concurrency)     (code first, LLM if needed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Map | Same task per chunk | प्रत्येक टुकड़े पर काम |
| Reduce | Combine partials | नतीजे जोड़ना |
| Chunk | Piece of input | टुकड़ा |
| Fan-out | Start many parallel tasks | शाखाओं में बाँटना |
| Hierarchical reduce | Reduce in rounds | स्तरीय reduce |
| Coverage | Share of chunks done | कवरेज |

---

## ⚡ 3-Line Summary
English: Split big input, run the same agent on each chunk in parallel, then merge the partial results.
Keep map outputs small and structured, and bound concurrency.
It loses cross-chunk links, so choose it only for decomposable tasks.

Hindi: बड़े input को बाँटो, हर टुकड़े पर वही agent समानांतर चलाओ, फिर आंशिक नतीजे जोड़ो।
Map के output छोटे और structured रखो और concurrency सीमित रखो।
इसमें chunks के बीच के संबंध खो जाते हैं, इसलिए सिर्फ़ बाँटे जा सकने वाले कामों में इस्तेमाल करो।

---

## ➡️ Next Topic
191. Scatter-Gather Pattern: send the SAME request to different specialists in parallel and gather their different views.

---

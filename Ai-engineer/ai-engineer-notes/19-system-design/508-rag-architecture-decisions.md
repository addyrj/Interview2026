---

# 508. RAG Architecture Decisions
# हिंदी में: RAG Architecture के फैसले

---

## 🔵 Simple Definition (English)
RAG architecture decisions are the choices that shape a RAG system: naive vs advanced vs agentic RAG, single vs multi-index, long context vs retrieval, sync vs streaming, and where to put verification. Each choice trades quality against latency, cost and complexity.

## 🔵 सरल परिभाषा (Hindi)
RAG architecture decisions वो choices हैं जो RAG system का आकार तय करती हैं: naive vs advanced vs agentic RAG, single vs multi index, long context vs retrieval, sync vs streaming, और verification कहाँ लगे। हर choice quality, latency, cost और complexity के बीच trade-off है।

---

## 🔴 Problem it Solves
Teams copy a tutorial architecture and later find it fails on multi-hop questions, tables or ambiguous queries, or is too slow and costly for simple ones. Making decisions explicitly matches architecture to the question types.

## 🔴 यह क्यों बना? (Hindi)
Teams tutorial वाला architecture copy करती हैं और बाद में पता चलता है कि multi-hop, tables या ambiguous queries पर fail होता है, या simple queries के लिए बहुत धीमा और महँगा है। Decisions साफ़ रखने से architecture सवालों के type से match होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify your questions: lookup, multi-hop, comparison, aggregation, chit-chat
Step 2 → Start with Naive RAG: retrieve top-k -> generate
Step 3 → Measure failures (retrieval miss? wrong chunk? bad generation?)
Step 4 → Upgrade only the failing part:
         retrieval miss  -> query rewrite, hybrid search, better chunking
         noisy context   -> reranking, compression
         multi-hop       -> agentic loop (retrieve, reason, retrieve again)
         hallucination   -> citation verification, grader node
Step 5 → Add a router so simple queries take the cheap path
Step 6 → Re-run evals and compare cost/latency
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सवालों का type पहचानो: lookup, multi-hop, comparison, aggregation
Step 2 → Naive RAG से शुरू करो
Step 3 → Failures measure करो (retrieval miss? गलत chunk? generation?)
Step 4 → सिर्फ failing हिस्सा upgrade करो
Step 5 → Router जोड़ो ताकि simple queries सस्ते path से जाएँ
Step 6 → Evals दोबारा चलाओ, cost/latency compare करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "HS code for a cotton shirt" is a simple lookup: naive hybrid RAG is enough. "Is this mixed-fibre garment classified by weight or by use, considering Section XI notes and last year's ruling?" is multi-hop: an agentic loop retrieves section notes, then rulings, then reasons. A router classifier sends 85% of queries (illustrative) to the cheap path.
**Zomato-style example**: "Best biryani near me" is a simple search; "vegetarian places open late under 500 rupees for 4 people" needs structured filters plus retrieval.

## 🟡 Real Example Hindi mein
**Tariff System**: "Cotton shirt का HS code" simple lookup है, naive hybrid RAG काफी है। "Mixed-fibre garment weight से classify होगा या use से, Section XI notes और पिछले साल के ruling को देखकर?" multi-hop है: agentic loop पहले notes, फिर rulings लाता है और reason करता है। Router 85% queries को सस्ते path पर भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic: a rule-based router that picks an architecture (pure Python, offline)
def route(question: str) -> str:  # return which RAG path to use
    q = question.lower()  # normalise
    multi_hop_words = ("and", "compare", "versus", "considering", "why")  # crude signals
    if len(q.split()) > 18 or any(w in q.split() for w in multi_hop_words):  # complex?
        return "agentic"  # multi-step path
    if "code for" in q or "hs code" in q:  # simple lookup
        return "naive"  # cheap path
    return "advanced"  # default: hybrid + rerank


for q in ["HS code for cotton shirt", "Compare duty on silk versus polyester shirts",
          "Tell me about tariffs"]:  # sample questions
    print(q, "->", route(q))  # show decision
```

## 💻 Code Example — Advanced
```python
# Advanced: async router with fallback chain, timeouts and per-path cost tracking
import asyncio  # async runtime
from typing import Awaitable, Callable  # type hints

PATH_COST = {"naive": 1.0, "advanced": 2.5, "agentic": 8.0}  # relative cost units (illustrative)


async def naive(q: str) -> str:  # cheap path
    await asyncio.sleep(0.01)  # simulate work
    return f"naive:{q}"  # result


async def advanced(q: str) -> str:  # hybrid + rerank path
    await asyncio.sleep(0.03)  # simulate more work
    return f"advanced:{q}"  # result


async def agentic(q: str) -> str:  # loop path
    await asyncio.sleep(0.08)  # simulate several steps
    return f"agentic:{q}"  # result


PATHS: dict[str, Callable[[str], Awaitable[str]]] = {"naive": naive, "advanced": advanced, "agentic": agentic}


async def run(q: str, path: str, timeout: float = 1.0) -> tuple[str, float]:  # run chosen path
    order = [path] + [p for p in ("advanced", "naive") if p != path]  # fallback to cheaper paths
    for p in order:  # try in order
        try:
            out = await asyncio.wait_for(PATHS[p](q), timeout)  # guarded call
            return out, PATH_COST[p]  # result and cost
        except asyncio.TimeoutError:  # too slow
            continue  # next fallback
    return "unavailable", 0.0  # all failed


if __name__ == "__main__":
    print(asyncio.run(run("compare silk vs polyester duty", "agentic")))  # run
```

---

## 🟠 FastAPI Integration
Put the router in a dependency so routes stay thin. Return which path was used in a header or field for debugging and cost reports.

```python
from fastapi import FastAPI  # app
from pydantic import BaseModel  # schema

app = FastAPI()  # app


class Ask(BaseModel):  # request
    question: str  # input


def choose(q: str) -> str:  # simple router (replace with a classifier)
    return "agentic" if len(q.split()) > 18 else "naive"  # rule


@app.post("/ask")  # route
async def ask(body: Ask) -> dict[str, str]:
    path = choose(body.question)  # pick path
    return {"path": path, "answer": f"[{path}] stub"}  # return with path for observability
```

---

## 🔗 LangChain / LangGraph Connection
Naive RAG = LCEL chain (retriever | prompt | llm). Advanced adds query rewriting and a reranker. Agentic RAG = LangGraph with conditional edges (grade documents, then answer or re-retrieve).

```python
from langgraph.graph import StateGraph, END  # graph builder
from typing import TypedDict  # state type


class S(TypedDict):  # state
    q: str  # question
    good: bool  # did retrieval pass grading
    tries: int  # loop counter


def grade(s: S) -> str:  # conditional edge
    return "answer" if s["good"] or s["tries"] >= 2 else "retrieve"  # stop condition prevents infinite loops


g = StateGraph(S)  # graph
g.add_node("retrieve", lambda s: {"tries": s["tries"] + 1, "good": s["tries"] >= 1})  # stub retrieval
g.add_node("answer", lambda s: {})  # stub answer
g.set_entry_point("retrieve")  # start
g.add_conditional_edges("retrieve", grade, {"answer": "answer", "retrieve": "retrieve"})  # loop or finish
g.add_edge("answer", END)  # end
print(g.compile().invoke({"q": "x", "good": False, "tries": 0}))  # run
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using agentic RAG for everything
✅ Correct: route; agentic is 3-10x costlier and slower.
```python
# Wrong
answer = await agentic(q)  # for all queries
# Right
answer = await PATHS[route(q)](q)  # cheap path when possible
```

❌ Mistake 2: Loops with no stop condition
✅ Correct: cap iterations and tokens.
```python
# Wrong
while not good: retrieve()  # may loop forever
# Right
for _ in range(3):  # hard cap
    if good: break
```

---

## 🧠 Tricky Interview Question
**Q**: "With a 1M-token context model, why still build RAG?"

**Answer**: Cost, latency and accuracy. Sending a million tokens per query is expensive and slow, models can miss details in very long contexts ("lost in the middle"), there is no per-user access control, and you cannot cite or update easily. Long context is good for small, one-off document sets; RAG is better for large, changing, permissioned corpora. Hybrid works too: retrieve generously, then pass a larger context.

---

## ⚫ Interview Questions + Answers

Q1: What is naive RAG? (Easy)
A1: Embed query, fetch top-k chunks, stuff into prompt, generate. No rewriting, reranking or verification.

Q2: What is agentic RAG? (Easy)
A2: The LLM decides to retrieve, grade results and retrieve again or use tools in a loop until it can answer.

Q3: When add query rewriting? (Medium)
A3: When user queries are short, ambiguous or conversational, so raw embedding search misses; rewrite or expand with chat history.

Q4: How do you decide between one index and many? (Medium)
A4: Many indices (or filters) when sources differ in schema, access, freshness or domain. One index is simpler. Route with metadata or a classifier.

Q5: How do you prove an upgrade is worth it? (Hard)
A5: A/B on a golden set: compare recall, faithfulness, p95 latency and cost per query. Adopt only if gains exceed cost, ideally for the query slice that fails today.

---

## 🔷 When to Use + When Not to Use
✅ Use agentic/advanced when:
- Multi-hop, comparison or ambiguous questions
- High cost of wrong answers

❌ Avoid when:
- Simple FAQ lookup; naive or cached answer is enough
- Strict latency budgets

---

## 📊 Visual Diagram
```
            ┌─────────────┐
 question ─▶│   Router    │
            └─┬────┬────┬─┘
        simple│    │mid │complex
              ▼    ▼    ▼
          Naive  Advanced  Agentic loop
          RAG    (rewrite  (retrieve → grade →
                 +rerank)   retrieve again)
              └────┴────┬────┘
                        ▼
                 Answer + citations
```

---

## 💰 Cost Impact
Naive: 1 LLM call. Advanced: 1-2 calls plus a reranker. Agentic: 3-10 calls, so tokens multiply. Example (illustrative): 2,000 tokens x 5 calls = 10,000 tokens per question.
Optimise: route by difficulty, cap loop steps, use small models for grading and rewriting, cache retrieval results, and stop early when confidence is high.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Naive RAG | Retrieve then generate | सरल RAG |
| Agentic RAG | LLM-driven retrieval loop | एजेंट वाला RAG |
| Router | Chooses path per query | रास्ता चुनने वाला |
| Multi-hop | Needs several lookups | कई चरण वाला सवाल |
| Query rewriting | Improve query before search | query सुधारना |
| Grader | Judges retrieved docs | docs जाँचने वाला |

---

## ⚡ 3-Line Summary
English: Start with naive RAG and upgrade only the part your evals show failing.
Use a router so cheap queries stay cheap and hard ones get agentic loops.
Always cap loops and compare cost against quality.
Hindi: Naive RAG से शुरू करो, सिर्फ evals में failing हिस्सा upgrade करो।
Router से सस्ते queries सस्ते रहें और कठिन वाले agentic loop पाएँ।
Loops cap करो और cost को quality से compare करो।

---

## ➡️ Next Topic
**509. LLM Selection for Production** — choosing the right model for each path.

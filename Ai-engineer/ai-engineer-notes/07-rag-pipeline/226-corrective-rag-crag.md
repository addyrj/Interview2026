---

# 226. Corrective RAG (CRAG)
# हिंदी में: Corrective RAG (सुधारने वाला RAG)

---

## 🔵 Simple Definition (English)
Corrective RAG (CRAG) adds a retrieval evaluator after the retriever. If the retrieved chunks are Correct, it keeps (and refines) them. If Incorrect, it throws them away and searches elsewhere (e.g., web). If Ambiguous, it combines both.

## 🔵 सरल परिभाषा (Hindi)
CRAG में retriever के बाद एक evaluator लगता है। Chunks सही (Correct) हों तो रखता और refine करता है। गलत (Incorrect) हों तो फेंककर कहीं और (जैसे web) search करता है। संदिग्ध (Ambiguous) हो तो दोनों मिलाता है।

---

## 🔴 Problem it Solves
Plain RAG fails silently when the knowledge base does not contain the answer: it still passes the "closest" chunks to the LLM, which then hallucinates. CRAG detects low-quality retrieval and corrects it with a fallback source.

## 🔴 यह क्यों बना? (Hindi)
जब knowledge base में answer ही नहीं होता, plain RAG चुपचाप fail होता है: सबसे "नज़दीकी" chunks LLM को दे देता है और वह hallucinate करता है। CRAG खराब retrieval पहचानकर fallback source से सुधार करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve top-k chunks from the vector store
Step 2 → Evaluator scores each chunk (relevant / irrelevant)
Step 3 → Decide action:
           all/most relevant   → CORRECT
           none relevant       → INCORRECT
           mixed               → AMBIGUOUS
Step 4 → CORRECT: keep + strip irrelevant sentences (knowledge refinement)
Step 5 → INCORRECT: rewrite query -> web search (or other KB)
Step 6 → AMBIGUOUS: use refined chunks + web results
Step 7 → Generate answer from the final context
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Vector store से top-k chunks लाओ
Step 2 → Evaluator हर chunk को score करता है
Step 3 → Action तय करो: Correct / Incorrect / Ambiguous
Step 4 → Correct: chunks रखो + फालतू sentences हटाओ (refinement)
Step 5 → Incorrect: query rewrite -> web search
Step 6 → Ambiguous: refined chunks + web results दोनों
Step 7 → Final context से answer generate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks about a brand-new 2026 duty change on lithium cells. Our KB (indexed in 2025) has only old notifications, so the evaluator marks everything Incorrect. CRAG rewrites the query ("India customs notification lithium-ion cells 2026") and calls a web/government-gazette search tool, then answers with a citation. **Amazon-style**: product Q&A over seller docs falls back to the live catalog API when docs are stale.

## 🟡 Real Example Hindi mein
**Tariff System**: User 2026 में lithium cells की नई duty change पूछता है। हमारा KB 2025 में index हुआ था, इसलिए evaluator सब Incorrect बोलता है। CRAG query rewrite करके web/gazette search tool चलाता है और citation के साथ जवाब देता है।

---

## 💻 Code Example — Basic
```python
# Offline CRAG decision logic with mocked evaluator and web search
from typing import Literal

Action = Literal["correct", "incorrect", "ambiguous"]  # three outcomes

KB: list[str] = [
    "Notification 2024: BCD on mobile phones is 20 percent.",
    "Chapter 85 covers electrical machinery.",
]

def score_chunk(query: str, chunk: str) -> float:
    # Mock evaluator: fraction of query words present in chunk
    q = set(query.lower().split())  # query word set
    c = set(chunk.lower().replace(".", "").split())  # chunk word set
    return len(q & c) / max(len(q), 1)  # 0.0 .. 1.0

def decide(scores: list[float], hi: float = 0.5, lo: float = 0.2) -> Action:
    best = max(scores, default=0.0)  # best chunk decides
    if best >= hi:
        return "correct"  # confident
    if best < lo:
        return "incorrect"  # nothing useful
    return "ambiguous"  # in between

def web_search(query: str) -> list[str]:
    # Mock web search result
    return [f"[web] Latest gazette info about: {query}"]

def crag(query: str) -> list[str]:
    scores = [score_chunk(query, c) for c in KB]  # Step 2
    action = decide(scores)  # Step 3
    print(f"action={action} scores={[round(s, 2) for s in scores]}")
    good = [c for c, s in zip(KB, scores) if s >= 0.2]  # keep partly relevant chunks
    if action == "correct":
        return good  # Step 4
    if action == "incorrect":
        return web_search(query)  # Step 5
    return good + web_search(query)  # Step 6

print(crag("BCD on mobile phones"))
print(crag("lithium cells duty 2026"))
```

## 💻 Code Example — Advanced
```python
# Async CRAG with LangChain grader + fallback tool + error handling
import asyncio
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

class Relevance(BaseModel):
    score: Literal["yes", "no"]  # binary relevance

grader = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Relevance)
grade_prompt = ChatPromptTemplate.from_template(
    "Q: {q}\nDoc: {d}\nDoes the doc contain info useful to answer Q? yes/no"
)
rewrite_prompt = ChatPromptTemplate.from_template(
    "Rewrite as a concise web search query: {q}"
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def grade(q: str, d: Document) -> bool:
    r = await (grade_prompt | grader).ainvoke({"q": q, "d": d.page_content})  # one LLM call
    return r.score == "yes"

async def web_fallback(q: str, search_tool) -> list[Document]:
    new_q = (await (rewrite_prompt | llm).ainvoke({"q": q})).content  # rewrite for search
    try:
        hits = await search_tool.ainvoke(new_q)  # e.g. TavilySearchResults
    except Exception:
        return []  # fallback failed: do not crash
    return [Document(page_content=h["content"], metadata={"url": h.get("url")}) for h in hits]

async def corrective_retrieve(q: str, retriever, search_tool) -> list[Document]:
    docs = await retriever.ainvoke(q)  # Step 1
    flags = await asyncio.gather(*(grade(q, d) for d in docs))  # Step 2 in parallel
    good = [d for d, f in zip(docs, flags) if f]  # keep relevant
    ratio = len(good) / max(len(docs), 1)
    if ratio >= 0.6:
        return good  # CORRECT
    web = await web_fallback(q, search_tool)  # INCORRECT or AMBIGUOUS needs help
    return web if ratio == 0 else good + web  # incorrect -> web only; ambiguous -> merge
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/tariff/crag")
async def crag_endpoint(body: Q) -> dict:
    docs = await corrective_retrieve(body.question, retriever, search_tool)  # advanced code above
    ctx = "\n".join(d.page_content for d in docs)  # build context
    ans = await llm.ainvoke(f"Use context only.\n{ctx}\nQ: {body.question}")  # generate
    return {"answer": ans.content, "sources": [d.metadata.get("url") for d in docs]}  # cite
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph has an official CRAG tutorial: nodes `retrieve -> grade_documents -> (transform_query -> web_search) -> generate`, with a conditional edge after grading.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class S(TypedDict):
    question: str
    docs: list[str]
    need_web: bool

g = StateGraph(S)
g.add_node("retrieve", lambda s: {"docs": []})
g.add_node("grade", lambda s: {"need_web": len(s["docs"]) == 0})
g.add_node("web", lambda s: {"docs": ["web result"]})
g.add_node("generate", lambda s: {})
g.set_entry_point("retrieve")
g.add_edge("retrieve", "grade")
g.add_conditional_edges("grade", lambda s: "web" if s["need_web"] else "generate")  # route
g.add_edge("web", "generate")
g.add_edge("generate", END)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Web fallback with the raw user question
```python
# Wrong
hits = search("hmm what about that duty thing for batteries?")
# Right: rewrite to a keyword query first
hits = search("India customs duty lithium-ion battery notification")
```

❌ Mistake 2: Trusting web results blindly
```python
# Wrong: context = web_hits
# Right: grade web hits too, prefer allow-listed domains (cbic.gov.in), keep URLs for citations
```

---

## 🧠 Tricky Interview Question
**Q**: "CRAG's evaluator says 'Correct' but the answer is still wrong. Why?"

**Answer**: The evaluator checks relevance, not truth. An outdated notification is perfectly relevant yet wrong. Add freshness metadata (effective_date), filter/boost by date, and prefer authoritative sources. Also evaluator thresholds may be too lenient: calibrate on a labelled set.

---

## ⚫ Interview Questions + Answers

Q1: What are CRAG's three actions? (Easy)
A1: Correct (use retrieved docs), Incorrect (discard, use web search), Ambiguous (combine both).

Q2: How is CRAG different from Self-RAG? (Easy)
A2: CRAG focuses on correcting retrieval with an external fallback; Self-RAG focuses on LLM reflection about retrieval, relevance and support.

Q3: What is knowledge refinement? (Medium)
A3: Splitting a retrieved doc into strips (sentences) and keeping only the relevant strips so noise tokens do not reach the generator.

Q4: What evaluator would you pick? (Medium)
A4: Original paper uses a fine-tuned T5 evaluator. In practice: small LLM with structured output, or a cross-encoder reranker score with thresholds. Cross-encoders are cheaper and faster.

Q5: How to prevent web fallback from becoming a cost/security risk? (Hard)
A5: Rate-limit fallback, allow-list domains, sanitize content against prompt injection, cap tokens from web, cache results, log every fallback (a high fallback rate signals KB gaps to fix by re-indexing).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- KB may be incomplete or stale
- A trusted secondary source exists (web, API)

❌ Avoid when:
- Closed domain where "I do not know" is the right answer
- Strict data-privacy rules forbid external search

---

## 📊 Visual Diagram
```
Query ─► Retrieve ─► Evaluator
                      │
        ┌─────────────┼───────────────┐
     Correct       Ambiguous       Incorrect
        │             │               │
     Refine       Refine + Web       Web
        └─────────────┼───────────────┘
                      ▼
                  Generate ─► Answer (+citations)
```

---

## 💰 Cost Impact
Extra cost = k grader calls (~300 tokens each) + occasional rewrite (~100 tokens) + web tool fees + larger context when merging. If 20% of queries hit fallback, average cost rises roughly 25-40%. Optimise with cross-encoder graders (no LLM tokens), caching fallback results, and fixing KB gaps so fallback rate falls over time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CRAG | Corrective RAG | सुधारने वाला RAG |
| Evaluator | Scores retrieval quality | Quality जाँचने वाला |
| Fallback | Backup source | बैकअप स्रोत |
| Refinement | Keep only useful strips | काम की पंक्तियाँ रखना |
| Query rewrite | Reformulate for search | Query दोबारा लिखना |

---

## ⚡ 3-Line Summary
English: CRAG grades retrieved chunks and decides Correct, Incorrect or Ambiguous. Bad retrieval triggers a fallback such as web search. This avoids hallucinating from irrelevant context.
Hindi: CRAG retrieved chunks को grade करके Correct, Incorrect या Ambiguous तय करता है। खराब retrieval पर web search जैसा fallback चलता है। इससे irrelevant context से hallucination नहीं होता।

---

## ➡️ Next Topic
**227. RAG Fusion** — improve recall by generating multiple query variants and merging results with Reciprocal Rank Fusion.

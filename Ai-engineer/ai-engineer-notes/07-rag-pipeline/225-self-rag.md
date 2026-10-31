---

# 225. Self-RAG
# हिंदी में: Self-RAG (खुद को जाँचने वाला RAG)

---

## 🔵 Simple Definition (English)
Self-RAG is a RAG pattern where the LLM decides by itself: "Do I need to retrieve?", "Are these documents relevant?", and "Is my answer supported by them?". It adds self-reflection steps (critique) around normal retrieve-then-generate.

## 🔵 सरल परिभाषा (Hindi)
Self-RAG में LLM खुद तय करता है: "क्या retrieval चाहिए?", "क्या ये documents relevant हैं?", "क्या मेरा answer documents से support होता है?"। यानी normal RAG के चारों तरफ self-critique के steps जुड़ जाते हैं।

---

## 🔴 Problem it Solves
Plain RAG always retrieves, even for "hi" or "2+2". It also blindly trusts whatever the retriever returns. If the top-k chunks are irrelevant, the LLM still writes a confident (hallucinated) answer. Self-RAG adds checks so bad context is dropped and unsupported answers are rejected or regenerated.

## 🔴 यह क्यों बना? (Hindi)
Plain RAG हमेशा retrieve करता है, "hi" पर भी। Retriever जो भी लाए उस पर आँख बंद करके भरोसा करता है। Chunks irrelevant हों तब भी LLM confident (गलत) answer लिख देता है। Self-RAG checks जोड़ता है ताकि बेकार context हटे और unsupported answer reject/regenerate हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide: does this query need retrieval? (yes/no)
Step 2 → If yes: retrieve top-k chunks
Step 3 → Grade each chunk: relevant / not relevant (drop irrelevant)
Step 4 → Generate answer from relevant chunks only
Step 5 → Check groundedness: is every claim supported by chunks?
Step 6 → Check usefulness: does the answer address the question?
Step 7 → If it fails 5 or 6: rewrite query / regenerate (max N loops)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → तय करो: retrieval चाहिए या नहीं?
Step 2 → हाँ तो top-k chunks लाओ
Step 3 → हर chunk को grade करो: relevant / not relevant (irrelevant हटाओ)
Step 4 → सिर्फ relevant chunks से answer बनाओ
Step 5 → Groundedness check: क्या हर दावा chunks में है?
Step 6 → Usefulness check: क्या answer सवाल का जवाब देता है?
Step 7 → fail हो तो query rewrite / regenerate (max N बार)
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "HS code for stainless steel water bottle?". The retriever returns chunks about Chapter 73 (steel articles) and one about Chapter 22 (beverages). The grader drops the beverage chunk. The generator answers 7323/7324. The groundedness check confirms the code appears in the retrieved text. If the user just says "thanks", Step 1 says "no retrieval" and saves cost. **Zomato AI**: "Where is my order?" needs an order-DB call, not a menu search; "Hi" needs nothing.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "Steel water bottle का HS code?"। Retriever Chapter 73 के chunks और Chapter 22 (beverages) का एक chunk लाता है। Grader beverage chunk हटा देता है। Generator 7323/7324 बताता है। Groundedness check देखता है कि code retrieved text में है। User सिर्फ "thanks" बोले तो Step 1 "retrieval नहीं" कहता है, cost बचती है।

---

## 💻 Code Example — Basic
```python
# Pure-Python Self-RAG skeleton with mocked "LLM" decisions (runs offline)
from typing import Callable

# Tiny knowledge base: id -> text
DOCS: dict[str, str] = {
    "d1": "HS 7323: table, kitchen or household articles of iron or steel.",
    "d2": "HS 2202: waters, including mineral waters, sweetened beverages.",
    "d3": "HS 8517: telephone sets and smartphones.",
}

def needs_retrieval(query: str) -> bool:
    # Mock of an LLM "retrieve?" token: skip chit-chat
    return query.lower().strip() not in {"hi", "hello", "thanks"}  # simple rule

def retrieve(query: str, k: int = 2) -> list[str]:
    # Mock retriever: score by shared words
    q = set(query.lower().split())  # query words
    scored = sorted(DOCS.values(), key=lambda d: -len(q & set(d.lower().split())))  # best first
    return scored[:k]  # top-k

def is_relevant(query: str, chunk: str) -> bool:
    # Mock of an LLM relevance grader: needs at least one overlapping word
    return len(set(query.lower().split()) & set(chunk.lower().replace(",", "").split())) > 0

def generate(query: str, chunks: list[str]) -> str:
    # Mock generator: echoes the best chunk
    return f"Based on tariff data: {chunks[0]}" if chunks else "I do not know."

def is_grounded(answer: str, chunks: list[str]) -> bool:
    # Mock groundedness: answer must contain text from some chunk
    return any(c in answer for c in chunks)

def self_rag(query: str, max_loops: int = 2) -> str:
    if not needs_retrieval(query):  # Step 1
        return "You're welcome!"  # no retrieval, no cost
    for _ in range(max_loops):  # Step 7 loop
        chunks = [c for c in retrieve(query) if is_relevant(query, c)]  # Steps 2-3
        answer = generate(query, chunks)  # Step 4
        if chunks and is_grounded(answer, chunks):  # Step 5
            return answer  # accept
        query = query + " steel"  # crude "rewrite" before retrying
    return "I could not find a supported answer."  # safe fallback

print(self_rag("thanks"))
print(self_rag("household articles of steel"))
print(self_rag("quantum banana"))
```

## 💻 Code Example — Advanced
```python
# Production Self-RAG with LangChain structured graders, async + error handling
import asyncio
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class Grade(BaseModel):
    """Binary grade returned by the LLM."""
    verdict: Literal["yes", "no"] = Field(description="yes or no")  # constrained output

# Cheap model for grading (many calls), structured output = no parsing bugs
grader_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Grade)
gen_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

relevance_prompt = ChatPromptTemplate.from_template(
    "Question: {q}\nChunk: {c}\nIs the chunk relevant to the question? yes/no"
)
grounded_prompt = ChatPromptTemplate.from_template(
    "Chunks:\n{ctx}\nAnswer: {a}\nIs every claim in the answer supported by chunks? yes/no"
)
answer_prompt = ChatPromptTemplate.from_template(
    "Answer ONLY from context. Say 'unknown' if missing.\nContext:\n{ctx}\nQ: {q}"
)

async def grade_chunk(q: str, c: str) -> bool:
    res = await (relevance_prompt | grader_llm).ainvoke({"q": q, "c": c})  # async call
    return res.verdict == "yes"

async def self_rag(q: str, retriever, max_loops: int = 2) -> dict:
    for attempt in range(max_loops):
        try:
            docs = await retriever.ainvoke(q)  # retrieve
            flags = await asyncio.gather(*(grade_chunk(q, d.page_content) for d in docs))  # parallel grading
            good = [d.page_content for d in docs if flags[docs.index(d)]]  # keep relevant only
            if not good:
                q = f"{q} (rephrase with tariff terminology)"  # trivial rewrite; use an LLM in prod
                continue
            ctx = "\n---\n".join(good)
            ans = (await (answer_prompt | gen_llm).ainvoke({"ctx": ctx, "q": q})).content
            g = await (grounded_prompt | grader_llm).ainvoke({"ctx": ctx, "a": ans})
            if g.verdict == "yes":
                return {"answer": ans, "attempts": attempt + 1, "sources": len(good)}
        except Exception as exc:  # network / rate limit / parsing
            if attempt == max_loops - 1:
                return {"answer": "Service error, please retry.", "error": str(exc)}
    return {"answer": "No grounded answer found.", "attempts": max_loops}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Ask(BaseModel):
    query: str  # user question

@app.post("/tariff/self-rag")
async def ask(body: Ask) -> dict:
    # `retriever` is built at startup (vector store .as_retriever(search_kwargs={"k": 4}))
    if len(body.query) > 500:
        raise HTTPException(status_code=422, detail="Query too long")  # guard token cost
    result = await self_rag(body.query, retriever)  # from the advanced code above
    return result  # includes attempts so you can monitor loop count
```

---

## 🔗 LangChain / LangGraph Connection
Self-RAG is naturally a **LangGraph** state machine: nodes = `retrieve`, `grade_documents`, `generate`, `check_grounding`; conditional edges decide to loop or end.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict):
    question: str
    docs: list[str]
    answer: str
    grounded: bool

g = StateGraph(S)
g.add_node("retrieve", lambda s: {"docs": ["..."]})  # fetch chunks
g.add_node("generate", lambda s: {"answer": "..."})  # write answer
g.add_node("check", lambda s: {"grounded": True})  # groundedness grader
g.set_entry_point("retrieve")
g.add_edge("retrieve", "generate")
g.add_edge("generate", "check")
g.add_conditional_edges("check", lambda s: END if s["grounded"] else "retrieve")  # loop back
app_graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unbounded self-correction loop
```python
# Wrong: while not grounded: regenerate()   # may loop forever, burns tokens
# Right:
for attempt in range(2):  # hard cap
    ...
```

❌ Mistake 2: Using the big model for every grader call
```python
# Wrong
grader = ChatOpenAI(model="gpt-4o")
# Right: small model + structured output for yes/no grading
grader = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Grade)
```

---

## 🧠 Tricky Interview Question
**Q**: "Self-RAG made answers more accurate but latency doubled and the bill rose 3x. What do you do?"

**Answer**: Each grader is an extra LLM call. Fixes: (1) run chunk grading in parallel (`asyncio.gather`), (2) use a small model or a fine-tuned cross-encoder/classifier for grading, (3) skip grading when retriever scores are very high, (4) cap loops at 1-2, (5) apply Self-RAG only to high-risk queries (e.g., legal duty rates) and use plain RAG elsewhere, (6) cache grades per (query, chunk) pair.

---

## ⚫ Interview Questions + Answers

Q1: What does Self-RAG add over plain RAG? (Easy)
A1: Self-reflection: decide if retrieval is needed, grade retrieved chunks, and check that the answer is grounded and useful.

Q2: What is "groundedness"? (Easy)
A2: Whether each claim in the answer is supported by the retrieved context. Ungrounded = hallucination.

Q3: Original paper vs the LangGraph version? (Medium)
A3: The paper trains one LLM to emit special reflection tokens ([Retrieve], [IsRel], [IsSup], [IsUse]). Practical systems usually emulate this with prompts or structured-output graders around a normal LLM, which needs no fine-tuning.

Q4: How do you evaluate that Self-RAG helps? (Medium)
A4: Build a labelled set; compare faithfulness, answer relevance, and "correct refusal rate" with and without Self-RAG (RAGAS or custom). Track latency and cost per query too.

Q5: Design Self-RAG for a 50k-chunk tariff corpus with 2s p95. (Hard)
A5: Retrieve k=6 with hybrid search + reranker, parallel-grade with a small model (or skip grading if rerank score > threshold), single generation, one groundedness check streamed after the answer, max 1 retry, cache by normalized query, and fall back to "needs human review" rather than looping.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Wrong answers are costly (legal, customs, medical)
- Query mix includes chit-chat and factual queries
- Retriever quality is inconsistent

❌ Avoid when:
- Strict low latency / very high QPS with cheap queries
- Corpus is tiny and retrieval is already near-perfect

---

## 📊 Visual Diagram
```
Query ─► Need retrieval? ──no──► Direct answer
              │yes
              ▼
          Retrieve k ─► Grade chunks ─► (drop bad)
                                │
                                ▼
                            Generate
                                │
                     Grounded & useful? ──no──► Rewrite query ─┐
                                │yes                            │
                                ▼                               │
                             Return  ◄───── (max N loops) ──────┘
```

---

## 💰 Cost Impact
Tokens per query = retrieval-free path (0 retrieval tokens for chit-chat) OR generation + (k graders x ~300 tokens) + groundedness (~k chunks tokens). Example: k=4, grader 300 tokens each = 1,200 extra input tokens, about $0.00018 on gpt-4o-mini. Optimise: small grader model, parallel calls, skip graders on high scores, cache grades, cap loops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Self-RAG | RAG with self-critique | खुद जाँचने वाला RAG |
| Grader | LLM that scores relevance | Relevance जाँचने वाला |
| Groundedness | Answer backed by context | Context से समर्थित |
| Reflection token | Special decision token | Decision token |
| Hallucination | Made-up facts | गढ़े हुए तथ्य |

---

## ⚡ 3-Line Summary
English: Self-RAG lets the LLM decide when to retrieve and critique chunks and answers. It reduces hallucination by dropping bad context and rejecting ungrounded answers. It costs extra LLM calls, so cap loops and use small graders.
Hindi: Self-RAG में LLM तय करता है कब retrieve करना है और chunks/answers को critique करता है। Bad context हटाकर और ungrounded answer reject करके hallucination घटता है। Extra LLM calls लगती हैं, इसलिए loops cap करो और छोटे graders लो।

---

## ➡️ Next Topic
**226. Corrective RAG (CRAG)** — a sibling pattern that grades retrieval and falls back to web search when the corpus fails.

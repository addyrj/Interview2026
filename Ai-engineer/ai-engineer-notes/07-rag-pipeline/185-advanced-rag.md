---

# 185. Advanced RAG
# हिंदी में: Advanced RAG (उन्नत RAG)

---

## 🔵 Simple Definition (English)
Advanced RAG is Naive RAG (embed, retrieve top-k, generate) plus extra stages **before** retrieval (query rewriting), **during** retrieval (hybrid search, metadata filters) and **after** retrieval (reranking, context compression). Each stage fixes one known failure of plain RAG.

## 🔵 सरल परिभाषा (Hindi)
Advanced RAG = Naive RAG (embed, top-k retrieve, generate) + retrieval से **पहले** (query rewrite), **दौरान** (hybrid search, metadata filter) और **बाद में** (rerank, context compression) के extra stages। हर stage plain RAG की एक known problem ठीक करता है।

---

## 🔴 Problem it Solves
Naive RAG breaks in production: vague user queries retrieve wrong chunks, pure vector search misses exact codes like "HS 8517.13", top-k contains noise, and the LLM gets a bloated, distracting context ("lost in the middle"). Quality cannot be improved only by changing the LLM. We need to improve what the LLM *sees*.

## 🔴 यह क्यों बना? (Hindi)
Naive RAG production में fail होता है: vague query गलत chunks लाती है, सिर्फ vector search "HS 8517.13" जैसे exact code miss करता है, top-k में noise आ जाता है, और LLM को लंबा distracting context मिलता है। सिर्फ LLM बदलने से quality नहीं सुधरती; LLM जो *देखता* है उसे सुधारना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → PRE-RETRIEVAL: rewrite / expand / decompose the user query
Step 2 → Extract metadata filters (country, year, chapter) from the query
Step 3 → RETRIEVAL: hybrid search (BM25 + dense) with the filters, fetch top-20
Step 4 → POST-RETRIEVAL: rerank (cross-encoder) and keep the best 4-5
Step 5 → Compress / deduplicate chunks, order them (best first and last)
Step 6 → GENERATION: grounded prompt with citations, low temperature
Step 7 → Verify answer is supported by context; log tokens + latency
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Retrieval से पहले query को rewrite / expand / decompose करो
Step 2 → Query से metadata filters (country, year, chapter) निकालो
Step 3 → Hybrid search (BM25 + dense) filters के साथ, top-20 लाओ
Step 4 → Rerank करके सिर्फ best 4-5 रखो
Step 5 → Chunks compress और dedupe करो, सही क्रम में लगाओ
Step 6 → Citations वाला grounded prompt, कम temperature
Step 7 → जाँचो कि answer context से supported है; tokens + latency log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "duty on that charger thing for laptops from China". Naive RAG retrieves random electronics chunks. Advanced RAG: (1) rewrites to "import duty on laptop power adapters originating in China", (2) filters `country=CN`, `chapter=85`, (3) hybrid search catches "8504.40" exactly, (4) reranker puts the "static converters" chunk first, (5) the LLM answers with a citation.
**Zomato AI**: "something spicy under 300 near me" becomes a rewritten query plus filters `price<300`, `city`, then rerank by dish relevance.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "China से laptop के charger जैसी चीज़ पर duty"। Naive RAG random electronics chunks लाता है। Advanced RAG query को साफ़ करता है, `country=CN`, `chapter=85` filter लगाता है, hybrid search से "8504.40" exact पकड़ता है, reranker सही chunk ऊपर रखता है, और LLM citation के साथ जवाब देता है।
**Zomato AI**: "300 से कम में कुछ spicy" -> rewritten query + `price<300` filter -> dish relevance से rerank।

---

## 💻 Code Example — Basic
```python
# Basic Advanced-RAG skeleton: rewrite -> retrieve -> rerank (pure Python, runs directly)
from typing import Dict, List

# Tiny in-memory knowledge base (id -> text)
DOCS: Dict[str, str] = {
    "d1": "HS 8504.40 static converters such as laptop power adapters duty 0 percent",
    "d2": "HS 8517.13 smartphones duty 0 percent under ITA agreement",
    "d3": "HS 6403.99 leather footwear duty 20 percent",
}

def rewrite(query: str) -> str:
    """Pre-retrieval: expand slang into search-friendly words."""
    # Replace casual phrase with domain vocabulary
    return query.lower().replace("charger thing", "power adapter static converter")

def tokenize(text: str) -> List[str]:
    """Lowercase word split (keeps dots in HS codes)."""
    return text.lower().split()

def retrieve(query: str, k: int = 3) -> List[str]:
    """Retrieval: score docs by word overlap with the query."""
    q = set(tokenize(query))  # query words as a set
    scored = [(len(q & set(tokenize(t))), d) for d, t in DOCS.items()]  # overlap score
    scored.sort(reverse=True)  # best first
    return [d for s, d in scored[:k] if s > 0]  # drop zero-score docs

def rerank(query: str, ids: List[str]) -> List[str]:
    """Post-retrieval: toy reranker, favour docs sharing more query words."""
    q = set(tokenize(query))  # query words
    return sorted(ids, key=lambda d: -len(q & set(tokenize(DOCS[d]))))  # stable sort

if __name__ == "__main__":
    user_query = "duty on charger thing for laptop"  # vague user input
    better = rewrite(user_query)  # step 1
    hits = retrieve(better)  # step 2
    final = rerank(better, hits)[:2]  # step 3, keep top 2
    print("rewritten:", better)  # show rewrite
    print("context  :", [DOCS[d] for d in final])  # show context for the LLM
```

## 💻 Code Example — Advanced
```python
# Production-style async Advanced RAG with injected components, error handling, token tracking
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List

logger = logging.getLogger("advanced_rag")  # module logger

# Type aliases for pluggable stages
RewriteFn = Callable[[str], Awaitable[str]]
RetrieveFn = Callable[[str, int], Awaitable[List[str]]]
RerankFn = Callable[[str, List[str], int], Awaitable[List[str]]]
GenerateFn = Callable[[str, List[str]], Awaitable[str]]

@dataclass
class RagResult:
    """Structured result returned to callers."""
    answer: str  # final answer text
    contexts: List[str]  # chunks actually used
    approx_tokens: int  # rough prompt size (words * 1.3)
    steps: List[str] = field(default_factory=list)  # audit trail

class AdvancedRAG:
    """Pre-retrieval, retrieval, post-retrieval, generation; each stage swappable."""

    def __init__(self, rewrite: RewriteFn, retrieve: RetrieveFn,
                 rerank: RerankFn, generate: GenerateFn, fetch_k: int = 20, final_k: int = 4) -> None:
        self.rewrite, self.retrieve = rewrite, retrieve  # store stage functions
        self.rerank, self.generate = rerank, generate  # store stage functions
        self.fetch_k, self.final_k = fetch_k, final_k  # recall vs precision knobs

    async def run(self, query: str) -> RagResult:
        steps: List[str] = []  # audit trail
        try:
            q2 = await self.rewrite(query)  # pre-retrieval
        except Exception as exc:  # rewrite failure must not kill the request
            logger.warning("rewrite failed: %s", exc)
            q2 = query  # fall back to the raw query
        steps.append(f"rewrite:{q2}")
        candidates = await self.retrieve(q2, self.fetch_k)  # wide recall
        steps.append(f"retrieved:{len(candidates)}")
        if not candidates:  # nothing found: refuse, do not hallucinate
            return RagResult("I could not find this in the tariff documents.", [], 0, steps)
        best = await self.rerank(q2, candidates, self.final_k)  # precision
        steps.append(f"reranked:{len(best)}")
        answer = await self.generate(query, best)  # grounded generation
        approx = int(sum(len(c.split()) for c in best) * 1.3) + 50  # rough token estimate
        return RagResult(answer, best, approx, steps)

# ---- offline demo stages (replace with real LLM / vector DB calls) ----
async def _rw(q: str) -> str: return q.lower()
async def _rt(q: str, k: int) -> List[str]: return ["8504.40 power adapters duty 0", "6403.99 footwear duty 20"][:k]
async def _rr(q: str, c: List[str], k: int) -> List[str]: return sorted(c, key=lambda x: -len(set(q.split()) & set(x.split())))[:k]
async def _gen(q: str, c: List[str]) -> str: return f"Based on: {c[0]}"

if __name__ == "__main__":
    rag = AdvancedRAG(_rw, _rt, _rr, _gen)  # wire stages
    print(asyncio.run(rag.run("duty on power adapters")))  # run once
```

---

## 🟠 FastAPI Integration
Build the `AdvancedRAG` object once at startup (lifespan) and call `await rag.run()` inside async routes. Return `contexts` so the UI can show sources, and `steps` for debugging.

```python
# FastAPI + Advanced RAG route
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()  # app instance

class AskRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)  # validated input

class AskResponse(BaseModel):
    answer: str  # final answer
    sources: list[str]  # chunks used
    approx_tokens: int  # cost signal

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    try:
        result = await rag.run(req.query)  # rag built at startup (see Advanced example)
    except Exception as exc:  # never leak internals
        raise HTTPException(status_code=502, detail="RAG pipeline failed") from exc
    return AskResponse(answer=result.answer, sources=result.contexts, approx_tokens=result.approx_tokens)
```

---

## 🔗 LangChain / LangGraph Connection
LCEL expresses the stages as a pipe. LangGraph is better when you need loops (e.g., "if retrieval is weak, rewrite and retry"). Each node = one stage; a conditional edge decides to retry.

```python
# LCEL pipeline: rewrite -> retrieve -> prompt -> LLM (requires langchain-core, langchain-openai)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # deterministic answers
rewrite_chain = (
    ChatPromptTemplate.from_template("Rewrite as a tariff search query: {q}")
    | llm | StrOutputParser()
)  # pre-retrieval stage
retriever = RunnableLambda(lambda q: ["8504.40 power adapters duty 0"])  # stand-in for vectorstore.as_retriever()
answer_prompt = ChatPromptTemplate.from_template("Context: {ctx}\nQuestion: {q}\nAnswer with citation.")
chain = (
    {"q": RunnablePassthrough()}
    | RunnablePassthrough.assign(rewritten=rewrite_chain)  # adds rewritten query
    | RunnablePassthrough.assign(ctx=lambda x: retriever.invoke(x["rewritten"]))  # retrieval
    | answer_prompt | llm | StrOutputParser()
)
# print(chain.invoke("duty on charger thing"))  # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding every technique at once (rewrite, HyDE, rerank, compression) without measuring.
✅ Correct: Add one stage, measure with an eval set (recall@k, faithfulness), keep it only if it helps.

```python
# Wrong: 5 extra LLM calls per query, latency 6s, no evidence it helps
# Right: baseline -> + hybrid -> + rerank; compare recall@5 each time
```

❌ Mistake 2: Reranking only the top-4 results.
✅ Correct: Retrieve wide (20-50), rerank, then cut to 4-5. Reranking cannot recover a chunk that was never retrieved.

```python
# Wrong
hits = retrieve(q, k=4); best = rerank(q, hits)
# Right
hits = retrieve(q, k=30); best = rerank(q, hits)[:5]
```

---

## 🧠 Tricky Interview Question
**Q**: "You added a reranker but answer quality did not improve. Why?"

**Answer**: Reranking only reorders what retrieval returned. If the right chunk is not in the candidate set (low recall), the reranker has nothing to promote. Check recall@50 first. Fix retrieval (hybrid search, better chunking, query rewriting, metadata filters), then reranking helps. Also check that the context order and prompt are not the bottleneck.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Naive and Advanced RAG?
A1: Naive RAG is index, retrieve top-k, generate. Advanced RAG adds pre-retrieval (query rewriting), retrieval (hybrid, filters) and post-retrieval (rerank, compress) stages.

Q2: Name three pre-retrieval techniques.
A2: Query rewriting, multi-query/expansion, HyDE, step-back prompting, query decomposition, metadata extraction.

Q3: Why retrieve 20 chunks but send only 4 to the LLM?
A3: Wide retrieval gives high recall; reranking gives precision. Sending fewer, better chunks reduces tokens, cost, latency and the "lost in the middle" effect.

Q4: How do you decide which advanced technique to add?
A4: Do error analysis on failures. Missing exact codes -> hybrid. Vague queries -> rewrite. Noisy top-k -> rerank. Long chunks -> compression. Measure each change on a labeled eval set.

Q5: How would you design a retry loop for weak retrieval?
A5: Use LangGraph: retrieve node, grade node (LLM or score threshold), conditional edge back to a rewrite node with a max-iteration cap (2-3). If still weak, return "not found" instead of guessing. Track tokens per loop to bound cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naive RAG has measurable failures (wrong chunks, missed exact terms)
- Queries are vague, multi-part or multilingual
- Accuracy matters more than a few hundred ms (legal, tariff, medical)

❌ Avoid when:
- Small corpus (<100 chunks) where naive RAG already scores well
- Strict low-latency budget with no evals to justify extra stages
- Prototype stage with no baseline numbers

---

## 📊 Visual Diagram
```
User query
   │
   ▼
┌─────────────── PRE-RETRIEVAL ───────────────┐
│ rewrite · expand · decompose · filters      │
└──────────────────────┬──────────────────────┘
                       ▼
┌──────────────── RETRIEVAL ──────────────────┐
│ BM25 + Dense (hybrid) + metadata filter     │  top-20
└──────────────────────┬──────────────────────┘
                       ▼
┌────────────── POST-RETRIEVAL ───────────────┐
│ rerank -> compress -> dedupe -> order       │  top-4
└──────────────────────┬──────────────────────┘
                       ▼
               LLM (grounded) -> Answer + citations
```

---

## 💰 Cost Impact
Extra stages add tokens: rewrite (~100 tokens), multi-query (3x retrieval, ~150 tokens), reranker (no LLM tokens if cross-encoder), compression (LLM call, ~500 tokens). Typical added cost: 0.0001-0.0005 USD per query with gpt-4o-mini, but fewer context tokens (4 chunks instead of 10) usually pays it back.
Optimize: use a small model for rewrite, cache rewrites, use cross-encoder (not LLM) reranking, skip stages with a cheap router when the query is already clear.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pre-retrieval | Work done on the query before search | Search से पहले query सुधारना |
| Post-retrieval | Work done on results after search | Search के बाद results सुधारना |
| Recall@k | Share of relevant chunks found in top-k | Top-k में सही chunks का हिस्सा |
| Reranking | Re-scoring candidates with a stronger model | Candidates को दोबारा score करना |
| Context compression | Shrinking chunks to relevant parts | Context छोटा करना |
| Lost in the middle | LLM ignores mid-context info | बीच के context को LLM भूल जाता है |

---

## ⚡ 3-Line Summary
English: Advanced RAG adds stages before, during and after retrieval to fix naive RAG failures.
Always retrieve wide, rerank narrow, and measure every stage with an eval set.
Extra stages cost tokens, so add only those that your error analysis justifies.
Hindi: Advanced RAG, retrieval से पहले, दौरान और बाद में stages जोड़कर naive RAG की कमियाँ ठीक करता है।
हमेशा wide retrieve करो, narrow rerank करो, और हर stage को eval set से measure करो।
Extra stages tokens खर्च करते हैं, इसलिए सिर्फ वही जोड़ो जो error analysis सही ठहराए।

---

## ➡️ Next Topic
**186. Modular RAG**: instead of one fixed pipeline, treat every stage as a swappable module with routing, so different queries take different paths.

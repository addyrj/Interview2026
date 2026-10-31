---

# 201. Multi-Query Retrieval
# हिंदी में: Multi-Query Retrieval

---

## 🔵 Simple Definition (English)
Multi-query retrieval asks an LLM to rewrite the user question into several different versions (for example 3-5), retrieves chunks for each version, and merges the results (union or RRF). Different phrasings hit different chunks, so recall goes up.

## 🔵 सरल परिभाषा (Hindi)
Multi-query retrieval में LLM user के सवाल को कई अलग versions (जैसे 3-5) में rewrite करता है, हर version के लिए chunks retrieve होते हैं, और results merge होते हैं (union या RRF)। अलग शब्दों से अलग chunks मिलते हैं, इसलिए recall बढ़ता है।

---

## 🔴 Problem it Solves
Retrieval is sensitive to wording. "Tax on imported earbuds" may miss a chunk titled "Customs duty on wireless headsets". One query = one point in embedding space; if the answer chunk is a bit away from that point, it is lost. Several paraphrases cover a wider area around the user intent.

## 🔴 यह क्यों बना? (Hindi)
Retrieval शब्दों के प्रति संवेदनशील है। "Imported earbuds पर tax" शायद "Wireless headsets पर customs duty" वाला chunk miss कर दे। एक query = embedding space में एक बिंदु; जवाब वाला chunk उससे थोड़ा दूर हो तो खो जाता है। कई paraphrases user की मंशा के आसपास बड़ा क्षेत्र cover करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive the user question
Step 2 → LLM generates N alternative queries (different wording, angle, specificity)
Step 3 → Retrieve top-k for the original + each alternative (in parallel)
Step 4 → Merge: unique union, or RRF across the N lists (better)
Step 5 → Optional rerank with the ORIGINAL question
Step 6 → Send the best 4-5 chunks to the generator
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → User का सवाल लो
Step 2 → LLM N वैकल्पिक queries बनाता है (अलग शब्द, कोण, specificity)
Step 3 → Original + हर alternative के लिए top-k retrieve करो (parallel)
Step 4 → Merge: unique union या N lists पर RRF (बेहतर)
Step 5 → Optional: ORIGINAL सवाल से rerank
Step 6 → Generator को best 4-5 chunks भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User: "tax on imported earbuds". Generated queries: (1) "customs duty on wireless earphones HS 8518.30", (2) "import tariff Bluetooth headsets", (3) "duty rate for in-ear audio devices". Together they retrieve the heading text, the explanatory note and the country-specific rate table, which one query alone missed.
**Amazon AI**: "good laptop for coding under 60k" -> "developer laptop 16GB RAM budget", "best programming notebook India", etc.

## 🟡 Real Example Hindi mein
**Tariff System**: User: "imported earbuds पर tax"। Generated queries: (1) "customs duty on wireless earphones HS 8518.30", (2) "import tariff Bluetooth headsets", (3) "duty rate for in-ear audio devices"। तीनों मिलकर heading text, explanatory note और country-specific rate table लाती हैं, जो अकेली query miss कर देती थी।
**Amazon AI**: "coding के लिए 60k से कम अच्छा laptop" -> "developer laptop 16GB RAM budget", "best programming notebook India" आदि।

---

## 💻 Code Example — Basic
```python
# Multi-query retrieval with a stub "LLM" and a toy retriever (pure Python, runs directly)
from collections import defaultdict
from typing import Dict, List

DOCS: Dict[str, str] = {
    "d1": "customs duty on wireless earphones hs 8518.30",
    "d2": "import tariff for bluetooth headsets explanatory note",
    "d3": "duty on leather footwear hs 6403.99",
    "d4": "rate table in ear audio devices india",
}

def generate_queries(question: str, n: int = 3) -> List[str]:
    """Stand-in for an LLM call: returns paraphrases (a real system prompts a model)."""
    return [question,
            "customs duty on wireless earphones hs 8518.30",
            "import tariff bluetooth headsets",
            "duty rate in ear audio devices"][: n + 1]  # original + n variants

def retrieve(query: str, k: int = 2) -> List[str]:
    """Toy keyword-overlap retriever returning ranked doc ids."""
    q = set(query.lower().split())
    scored = sorted(DOCS, key=lambda d: -len(q & set(DOCS[d].split())))  # most overlap first
    return [d for d in scored if q & set(DOCS[d].split())][:k]  # drop zero-overlap docs

def rrf(lists: List[List[str]], k: int = 60) -> List[str]:
    s: Dict[str, float] = defaultdict(float)
    for lst in lists:
        for r, d in enumerate(lst, start=1):
            s[d] += 1 / (k + r)
    return sorted(s, key=s.get, reverse=True)

if __name__ == "__main__":
    q = "tax on imported earbuds"
    print("single query :", retrieve(q))  # finds little (no shared words)
    lists = [retrieve(x) for x in generate_queries(q)]  # one retrieval per query
    print("multi-query  :", rrf(lists)[:4])  # fused result covers d1, d2, d4
```

## 💻 Code Example — Advanced
```python
# Async multi-query retriever: LLM generation with validation, parallel retrieval, RRF, caps, fallback
import asyncio
import json
import logging
from typing import Awaitable, Callable

logger = logging.getLogger("multiquery")  # logger
LLM = Callable[[str], Awaitable[str]]  # prompt -> text
Retriever = Callable[[str, int], Awaitable[list[str]]]  # (query, k) -> ranked chunk ids

PROMPT = ("Generate {n} different search queries for the question below. "
          "Vary wording and specificity. Return a JSON list of strings only.\nQuestion: {q}")  # ~60 tokens

class MultiQueryRetriever:
    def __init__(self, llm: LLM, retriever: Retriever, n: int = 3, per_query_k: int = 20, rrf_k: int = 60) -> None:
        self.llm, self.retriever, self.n = llm, retriever, n  # deps
        self.per_query_k, self.rrf_k = per_query_k, rrf_k  # settings
        self.cache: dict[str, list[str]] = {}  # question -> generated queries

    async def expand(self, question: str) -> list[str]:
        if question in self.cache:
            return self.cache[question]  # avoid repeat LLM call
        try:
            raw = await asyncio.wait_for(self.llm(PROMPT.format(n=self.n, q=question)), 8)  # bounded time
            variants = [v.strip() for v in json.loads(raw) if isinstance(v, str) and v.strip()]  # validate
        except Exception as exc:  # bad JSON, timeout, provider error
            logger.warning("expansion failed, using original only: %r", exc)
            variants = []
        queries = list(dict.fromkeys([question, *variants[: self.n]]))  # original first, dedupe, cap
        self.cache[question] = queries
        return queries

    async def search(self, question: str, k: int = 5) -> list[str]:
        queries = await self.expand(question)  # step 1-2
        results = await asyncio.gather(*(self.retriever(q, self.per_query_k) for q in queries), return_exceptions=True)
        lists = [r for r in results if isinstance(r, list)]  # skip failed retrievals
        scores: dict[str, float] = {}
        for lst in lists:
            for rank, cid in enumerate(lst, start=1):
                scores[cid] = scores.get(cid, 0.0) + 1 / (self.rrf_k + rank)  # RRF
        return sorted(scores, key=scores.get, reverse=True)[:k]

async def fake_llm(prompt: str) -> str:
    return json.dumps(["customs duty on wireless earphones", "import tariff bluetooth headsets"])

async def fake_retriever(q: str, k: int) -> list[str]:
    return ["d1", "d2"] if "earphones" in q else ["d2", "d4"]

if __name__ == "__main__":
    mq = MultiQueryRetriever(fake_llm, fake_retriever)
    print(asyncio.run(mq.search("tax on imported earbuds")))
```

---

## 🟠 FastAPI Integration
Multi-query adds an LLM call to the request path. Use a fast small model, a strict timeout and a cache. Return the generated queries when `debug=true`.

```python
# FastAPI endpoint using the MultiQueryRetriever
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # app
mq = MultiQueryRetriever(real_llm, real_retriever)  # build once (real_llm = async call to gpt-4o-mini)

class Q(BaseModel):
    question: str
    debug: bool = False

@app.post("/retrieve")
async def retrieve(q: Q) -> dict:
    ids = await mq.search(q.question, k=5)  # uses cache + parallel retrieval
    out: dict = {"chunk_ids": ids}
    if q.debug:
        out["queries"] = await mq.expand(q.question)  # served from cache
    return out
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides `MultiQueryRetriever.from_llm(retriever=..., llm=...)`, which generates 3 queries and returns the unique union of the results. Customise the prompt via `prompt=`. For RRF fusion, build your own chain (see 200). In LangGraph, make "expand_queries" a node whose output list feeds parallel "retrieve" nodes (via `Send` or a loop).

```python
# LangChain MultiQueryRetriever (needs langchain, langchain-openai, a vector store, OPENAI_API_KEY)
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

# base = vectorstore.as_retriever(search_kwargs={"k": 4})
# mq = MultiQueryRetriever.from_llm(retriever=base, llm=ChatOpenAI(model="gpt-4o-mini", temperature=0))
# docs = mq.invoke("tax on imported earbuds")        # returns unique union of results
# import logging; logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)  # see generated queries
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Generating 10 queries "to be safe".
✅ Correct: 3-4 is usually enough; more adds cost, latency and noise.

```python
# Wrong
n = 10     # 10 retrievals + big union -> noisy, slow
# Right
n = 3      # measure recall gain before increasing
```

❌ Mistake 2: Dropping the original question from the query set.
✅ Correct: Always include the original; rewrites can drift from user intent.

```python
# Wrong
queries = generated
# Right
queries = [question, *generated]
```

---

## 🧠 Tricky Interview Question
**Q**: "Multi-query raised recall@20 but final answer quality did not improve, and latency doubled. What happened?"

**Answer**: Extra candidates only help if the system can rank them well. Check whether the added chunks are relevant (precision at the top) and whether a reranker uses the original question. If not, noise displaces good chunks in the final top-5. Also the LLM call plus N retrievals adds latency; parallelise retrievals, use a small model and cache. Measure the end-to-end metric (answer correctness), not only recall; if recall@5 after rerank does not improve, drop the technique or apply it only to low-confidence queries.

---

## ⚫ Interview Questions + Answers

Q1: What is multi-query retrieval?
A1: Generating several rewrites of a question with an LLM, retrieving for each and merging the results.

Q2: How do you merge results?
A2: Union with dedupe (LangChain default) or Reciprocal Rank Fusion, which rewards chunks found by several queries.

Q3: What does it cost?
A3: One small LLM call (about 100-150 tokens total) plus N retrievals (N query embeddings, negligible).

Q4: Difference between multi-query, HyDE and step-back?
A4: Multi-query: many paraphrases. HyDE: embeds a hypothetical answer. Step-back: asks a more general question first. All are pre-retrieval query transformations.

Q5: How do you avoid query drift and decide when to use it?
A5: Always include the original query, ask for varied but faithful rewrites, rerank by the original question, and use a router (only for short/ambiguous queries or when top retrieval scores are low) so well-formed queries skip the extra call.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users write short, vague or oddly worded queries
- Vocabulary differs between users and documents
- Recall is the bottleneck

❌ Avoid when:
- Latency budget is tight (<500 ms)
- Queries already precise (codes, IDs)
- No reranker to filter the extra noise

---

## 📊 Visual Diagram
```
 "tax on imported earbuds"
          │ LLM (gpt-4o-mini, ~150 tokens)
          ▼
 ┌─ q0 original ───────────────┐
 ├─ q1 "customs duty wireless earphones HS 8518.30" ─┤
 ├─ q2 "import tariff Bluetooth headsets" ───────────┤   parallel retrieval
 └─ q3 "duty rate in-ear audio devices" ─────────────┘
          ▼ lists
        RRF fusion ─► rerank (original question) ─► top-5
```

---

## 💰 Cost Impact
Extra LLM call: ~60 prompt + ~80 output tokens on gpt-4o-mini = about 0.00006 USD per query; embeddings for 4 queries = ~80 tokens (negligible). Latency +300-800 ms for generation (retrievals run in parallel). If it lets you send 4 chunks instead of 8, you save about 0.0002 USD.
Optimize: cache expansions, small model, n=3, route only vague queries, limit `max_tokens` of the expansion.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-query | Several rewrites of one question | एक सवाल के कई rewrites |
| Query drift | Rewrite changes the intent | Rewrite से मंशा बदल जाना |
| Union | Combined unique results | मिलाए गए unique results |
| RRF | Rank-based fusion | Rank आधारित fusion |
| Recall | Share of relevant items found | मिले हुए सही items का हिस्सा |
| Paraphrase | Same meaning, different words | वही अर्थ, अलग शब्द |

---

## ⚡ 3-Line Summary
English: Multi-query retrieval rewrites a question into several variants, retrieves for each and fuses the results.
It raises recall for vague or oddly worded queries at the cost of one cheap LLM call.
Keep the original query, cap N at about 3, cache, and rerank.
Hindi: Multi-query retrieval सवाल को कई variants में rewrite करता है, हर एक पर retrieve करके results fuse करता है।
Vague या अजीब शब्दों वाली queries पर recall बढ़ता है, कीमत एक सस्ती LLM call।
Original query रखो, N लगभग 3 रखो, cache करो और rerank करो।

---

## ➡️ Next Topic
**202. HyDE (Hypothetical Document Embeddings)**: instead of rewriting the question, write a fake answer and search with it.

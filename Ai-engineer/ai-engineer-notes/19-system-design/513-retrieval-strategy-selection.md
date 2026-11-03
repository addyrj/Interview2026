---

# 513. Retrieval Strategy Selection
# हिंदी में: Retrieval Strategy का चुनाव

---

## 🔵 Simple Definition (English)
Retrieval strategy selection is choosing how to find relevant chunks: dense (vector) search, sparse (keyword/BM25) search, hybrid (both merged), metadata filters, query rewriting, and how many results (k) to fetch. The goal is high recall at low latency.

## 🔵 सरल परिभाषा (Hindi)
Retrieval strategy selection का मतलब है relevant chunks खोजने का तरीका चुनना: dense (vector), sparse (keyword/BM25), hybrid (दोनों मिलाकर), metadata filters, query rewriting, और कितने results (k) लाने हैं। लक्ष्य: कम latency पर ज़्यादा recall।

---

## 🔴 Problem it Solves
Dense search understands meaning but can miss exact tokens like part numbers or "HS 8517.13". Keyword search finds exact tokens but misses paraphrases. Using only one fails on half of real queries.

## 🔴 यह क्यों बना? (Hindi)
Dense search meaning समझता है पर "HS 8517.13" जैसे exact tokens miss कर सकता है। Keyword search exact tokens पकड़ता है पर paraphrase miss करता है। सिर्फ एक इस्तेमाल करने पर आधे real queries fail होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Study query types: exact codes, natural language, short keywords, multi-part
Step 2 → Dense retriever: embed query -> nearest vectors
Step 3 → Sparse retriever: BM25 over text (exact terms, codes, names)
Step 4 → Merge results: Reciprocal Rank Fusion (RRF) or weighted scores
Step 5 → Apply metadata filters (country, year, tenant) inside the search
Step 6 → Choose k (e.g. fetch 30, rerank to 5) based on recall@k eval
Step 7 → Add query rewriting / multi-query only if recall is still low
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Query types देखो: exact codes, natural language, short keywords
Step 2 → Dense: query embed करो → nearest vectors
Step 3 → Sparse: BM25 (exact terms, codes, names)
Step 4 → Results merge करो: RRF या weighted score
Step 5 → Metadata filters search के अंदर लगाओ
Step 6 → recall@k eval से k चुनो (30 लाओ, rerank करके 5)
Step 7 → Recall फिर भी कम हो तभी query rewriting / multi-query
```

---

## 🟡 Real World Example
**Tariff Classification System**: The query "8517.13 smartphone exclusions" has an exact code (sparse wins) and natural language (dense wins). Hybrid with RRF retrieves the heading text containing "8517.13" and the semantically related note about excluded parts. Filter: country = IN, tariff_year = 2025.
**Zomato-style example**: "Paneer butter masala under 300" mixes semantic dish similarity with a structured price filter.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "8517.13 smartphone exclusions" में exact code (sparse जीतता है) और natural language (dense जीतता है) दोनों हैं। RRF वाला hybrid "8517.13" वाला heading text और excluded parts वाला semantic note दोनों लाता है। Filter: country = IN, tariff_year = 2025।

---

## 💻 Code Example — Basic
```python
# Basic: reciprocal rank fusion of two ranked lists (pure Python, offline)
def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:  # merge ranked id lists
    scores: dict[str, float] = {}  # id -> fused score
    for ranking in rankings:  # each retriever's list
        for rank, doc_id in enumerate(ranking, start=1):  # rank starts at 1
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)  # RRF formula
    return sorted(scores, key=scores.get, reverse=True)  # best first


dense = ["note_exclusions", "heading_8517", "chapter_85"]  # from vector search
sparse = ["heading_8517", "code_table", "note_exclusions"]  # from BM25
print(rrf([dense, sparse]))  # items found by both float to the top
```

## 💻 Code Example — Advanced
```python
# Advanced: async hybrid retriever running dense and sparse in parallel, with filters and timeouts
import asyncio  # async runtime
from dataclasses import dataclass  # result record

CORPUS = {  # id -> (text, country)
    "d1": ("Smartphones heading 8517.13 telephone sets", "IN"),
    "d2": ("Excluded parts of cellular telephones", "IN"),
    "d3": ("Cotton shirts knitted", "US"),
}


@dataclass
class Hit:  # search result
    id: str  # doc id
    score: float  # fused score


async def sparse(q: str, country: str) -> list[str]:  # keyword overlap (stand-in for BM25)
    await asyncio.sleep(0.005)  # simulate latency
    toks = set(q.lower().split())  # query tokens
    scored = [(i, len(toks & set(t.lower().split()))) for i, (t, c) in CORPUS.items() if c == country]  # filter first
    return [i for i, s in sorted(scored, key=lambda x: -x[1]) if s > 0]  # ranked ids


async def dense(q: str, country: str) -> list[str]:  # fake semantic search
    await asyncio.sleep(0.01)  # simulate latency
    return [i for i, (t, c) in CORPUS.items() if c == country and "phone" in t.lower()]  # toy semantics


async def hybrid(q: str, country: str, k: int = 3) -> list[Hit]:  # merge both
    results = await asyncio.gather(  # run in parallel, tolerate failures
        asyncio.wait_for(dense(q, country), 2), asyncio.wait_for(sparse(q, country), 2),
        return_exceptions=True)  # exceptions returned, not raised
    fused: dict[str, float] = {}  # scores
    for lst in results:  # each retriever
        if isinstance(lst, Exception):  # one retriever failed
            continue  # degrade gracefully
        for rank, i in enumerate(lst, 1):  # rank from 1
            fused[i] = fused.get(i, 0.0) + 1 / (60 + rank)  # RRF
    return [Hit(i, s) for i, s in sorted(fused.items(), key=lambda x: -x[1])][:k]  # top k


if __name__ == "__main__":
    print(asyncio.run(hybrid("8517.13 smartphones phone", "IN")))  # run
```

---

## 🟠 FastAPI Integration
Expose retrieval as its own endpoint (useful for debugging) and let `/ask` call the same function. Accept filters in the schema and validate them.

```python
from fastapi import FastAPI  # app
from pydantic import BaseModel, Field  # schema

app = FastAPI()  # app


class Search(BaseModel):  # request
    query: str  # query
    country: str = Field(min_length=2, max_length=2)  # filter
    k: int = Field(default=5, ge=1, le=50)  # bounded k


@app.post("/retrieve")  # route
async def retrieve(s: Search) -> dict[str, list[str]]:
    return {"ids": ["d1", "d2"][: s.k]}  # replace with the hybrid retriever
```

---

## 🔗 LangChain / LangGraph Connection
LangChain offers `EnsembleRetriever` (RRF over several retrievers), `BM25Retriever` (needs `rank_bm25`), `MultiQueryRetriever` and `SelfQueryRetriever` for metadata filters.

```python
# Real API shapes (needs langchain-community, rank_bm25 and a vector store to run end to end):
# from langchain.retrievers import EnsembleRetriever
# from langchain_community.retrievers import BM25Retriever
# bm25 = BM25Retriever.from_texts(texts); bm25.k = 10
# dense = vectorstore.as_retriever(search_kwargs={"k": 10, "filter": {"country": "IN"}})
# hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.4, 0.6])
# docs = hybrid.invoke("8517.13 smartphone exclusions")
from langchain_core.retrievers import BaseRetriever  # real base class for custom retrievers
print(BaseRetriever.__name__)  # custom retrievers subclass this
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dense only for code-heavy queries
✅ Correct: add sparse/hybrid.
```python
# Wrong
docs = dense_search("8517.13")  # embedding may blur the number
# Right
docs = rrf([dense_search(q), bm25_search(q)])  # exact match covered
```

❌ Mistake 2: Large k pasted into the prompt
✅ Correct: retrieve many, rerank, send few.
```python
# Wrong
prompt = "\n".join(retrieve(q, k=30))  # tokens explode
# Right
prompt = "\n".join(rerank(q, retrieve(q, k=30))[:5])  # tight context
```

---

## 🧠 Tricky Interview Question
**Q**: "Recall@5 is 0.6 but recall@50 is 0.95. What does that tell you and what do you do?"

**Answer**: Relevant chunks are being found but ranked low. First-stage retrieval is fine; ranking is the problem. Fetch 50, add a cross-encoder reranker to promote the right ones into the top 5, and verify with recall@5 after reranking. Increasing k alone would add tokens and noise.

---

## ⚫ Interview Questions + Answers

Q1: Dense vs sparse retrieval? (Easy)
A1: Dense uses embeddings and finds similar meaning; sparse (BM25) matches exact words and rare terms.

Q2: What is hybrid search? (Easy)
A2: Running dense and sparse retrieval and merging results, commonly with RRF.

Q3: What is RRF? (Medium)
A3: Reciprocal Rank Fusion: each document scores sum of 1/(k + rank) across lists, rewarding documents that rank well in several lists; it needs no score normalisation.

Q4: What is MMR? (Medium)
A4: Maximal Marginal Relevance picks results that are relevant yet diverse, reducing duplicates.

Q5: How do you decide k and measure retrieval? (Hard)
A5: Use a labelled query set, measure recall@k, MRR and nDCG at several k values, then pick k at the knee considering token budget and reranker cost; monitor in production with click/feedback and sampled audits.

---

## 🔷 When to Use + When Not to Use
✅ Hybrid when:
- Mixed exact identifiers and natural language (codes, SKUs, names)

❌ Avoid extras when:
- Small corpus, plain dense search already hits the quality bar

---

## 📊 Visual Diagram
```
 query ─┬─▶ Dense (vectors) ──┐
        │                     ├─▶ RRF merge ─▶ top 30 ─▶ (rerank) ─▶ top 5
        └─▶ Sparse (BM25) ────┘
        filters: country, year, tenant applied inside both
```

---

## 💰 Cost Impact
Retrieval itself is cheap compared with LLM tokens, but sparse index adds storage and hybrid adds a second query. Larger k raises reranker cost and prompt tokens: sending 10 instead of 5 chunks of 300 tokens adds 1,500 input tokens per query (illustrative).
Optimise: retrieve wide, rerank, send few; cache frequent queries; use cheap query rewriting model; skip rewriting for exact-code queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dense retrieval | Vector similarity search | वेक्टर खोज |
| Sparse/BM25 | Keyword scoring | keyword आधारित खोज |
| Hybrid | Both combined | दोनों का मेल |
| RRF | Rank fusion method | rank मिलाने की विधि |
| MMR | Relevance with diversity | विविधता सहित relevance |
| k | Number of results | results की संख्या |

---

## ⚡ 3-Line Summary
English: Use dense for meaning and sparse for exact terms; hybrid with RRF covers both.
Apply metadata filters inside search and choose k by recall eval.
Retrieve wide, rerank, and send only a few chunks to the LLM.
Hindi: Meaning के लिए dense, exact terms के लिए sparse; RRF वाला hybrid दोनों संभालता है।
Metadata filters search के अंदर लगाओ और k recall eval से चुनो।
चौड़ा retrieve करो, rerank करो, LLM को कम chunks भेजो।

---

## ➡️ Next Topic
**514. Reranking Decision** — when a second-stage ranker is worth its cost.

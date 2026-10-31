---

# 248. EnsembleRetriever
# हिंदी में: EnsembleRetriever (Hybrid Search — कई Retrievers का मेल)

---

## 🔵 Simple Definition (English)
`EnsembleRetriever` runs several retrievers on the same query and merges their ranked lists with **Reciprocal Rank Fusion (RRF)**, using optional weights. The classic use is **hybrid search**: BM25 (keyword, exact match) + vector search (meaning). You get the strengths of both.

## 🔵 सरल परिभाषा (Hindi)
`EnsembleRetriever` एक ही query पर कई retrievers चलाता है और उनकी ranked lists को **Reciprocal Rank Fusion (RRF)** से weights के साथ मिलाता है। सबसे common use है **hybrid search**: BM25 (keyword, exact match) + vector search (meaning)। दोनों की ताक़त एक साथ मिलती है।

---

## 🔴 Problem it Solves
- Vector search understands meaning but is weak on exact tokens: "8507.60", "SKU-9921", "Section 301".
- Keyword search (BM25) nails exact tokens but cannot match "charger" with "static converter".

Neither alone is good for a tariff system where users ask both "what is 8507.60?" and "something to charge my phone". Their scores are on different scales (cosine vs BM25), so you cannot just add them — you need a rank-based fusion.

## 🔴 यह क्यों बना? (Hindi)
- Vector search मतलब समझता है पर exact tokens ("8507.60", "SKU-9921") में कमज़ोर है।
- Keyword search (BM25) exact tokens पकड़ता है पर "charger" और "static converter" को नहीं जोड़ पाता।

Tariff system में दोनों तरह के सवाल आते हैं। दोनों के scores की scale अलग है (cosine vs BM25), इसलिए सीधे जोड़ नहीं सकते — rank-based fusion चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build retrievers: bm25 (keywords) and vector (semantic)
Step 2 → EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])
Step 3 → On invoke(query): every retriever runs (in parallel with ainvoke)
Step 4 → Each returns an ordered list. Rank r gets score  weight / (c + r)   (c = 60 default)
Step 5 → Scores for the same document are summed across retrievers
Step 6 → Documents are sorted by total score; duplicates merged (by page_content, or id_key)
Step 7 → Combined top list goes to the LLM
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Retrievers बनाओ: bm25 (keywords) और vector (semantic)
Step 2 → EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])
Step 3 → invoke(query) पर सभी retrievers चलते हैं
Step 4 → हर list में rank r को score मिलता है:  weight / (c + r)   (c = 60 default)
Step 5 → एक ही document का score सभी retrievers से जोड़ा जाता है
Step 6 → Total score से sort, duplicates merge
Step 7 → Combined top list LLM को जाती है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query A: "8507.60 duty rate" — BM25 finds the exact code chunk at rank 1, vector search ranks it 7th. Query B: "device to charge my phone while travelling" — vector search finds "power banks", BM25 finds nothing. The ensemble returns the right chunk for both because each retriever contributes its own strength.

**Amazon AI**: Product search — "iPhone 15 Pro 256GB" (exact model tokens → BM25) and "good camera phone under 50k" (semantic → vectors).

## 🟡 Real Example Hindi mein
**Tariff System**: Query A: "8507.60 duty rate" — BM25 को exact code वाला chunk rank 1 पर मिलता है, vector में वह 7वें पर है। Query B: "सफ़र में फ़ोन charge करने की चीज़" — vector "power banks" ढूँढता है, BM25 कुछ नहीं। Ensemble दोनों के लिए सही chunk देता है।

**Amazon AI**: Product search — "iPhone 15 Pro 256GB" (exact tokens → BM25) और "50k के अंदर अच्छा camera phone" (semantic → vectors)।

---

## 💻 Code Example — Basic
```python
# Basic: EnsembleRetriever merging an exact-match and a synonym-aware retriever (offline)
# pip install langchain-core langchain-classic
from langchain_core.documents import Document                          # doc type
from langchain_core.retrievers import BaseRetriever                    # base retriever
from langchain_classic.retrievers import EnsembleRetriever             # the fusion retriever


class ExactRetriever(BaseRetriever):                                   # stands in for BM25
    docs: list[Document]                                               # corpus

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        words = set(query.lower().split())                             # query tokens
        hits = [(len(words & set(d.page_content.lower().split())), d) for d in self.docs]
        hits.sort(key=lambda p: p[0], reverse=True)                    # best first
        return [d for s, d in hits if s > 0]                           # only real matches


class SynonymRetriever(BaseRetriever):                                 # stands in for vector search
    docs: list[Document]                                               # corpus
    synonyms: dict[str, str]                                           # fake "meaning" table

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        expanded = " ".join(self.synonyms.get(w, w) for w in query.lower().split())  # map words to concepts
        return ExactRetriever(docs=self.docs).invoke(expanded)         # reuse exact match on concepts


corpus = [                                                             # tiny tariff corpus
    Document(page_content="8507.60 lithium-ion accumulators duty 2.7 percent"),
    Document(page_content="8504 static converters used as phone charger power banks"),
    Document(page_content="0901 coffee roasted"),
]
exact = ExactRetriever(docs=corpus)                                    # keyword side
semantic = SynonymRetriever(docs=corpus, synonyms={"charge": "charger", "travelling": "power"})  # meaning side

ensemble = EnsembleRetriever(retrievers=[exact, semantic], weights=[0.5, 0.5])  # fuse with RRF
for q in ["8507.60", "charge travelling"]:                             # one exact query, one vague query
    print(q, "->", [d.page_content[:6] for d in ensemble.invoke(q)])   # merged ranked list
```

## 💻 Code Example — Advanced
```python
# Production hybrid search: BM25 + vector store, weights, async, error handling
# pip install langchain-core langchain-classic langchain-community rank_bm25 langchain-openai langchain-chroma
import asyncio                                                         # async demo
import logging                                                         # logs
from langchain_core.documents import Document                          # doc type
from langchain_core.retrievers import BaseRetriever                    # type hint
from langchain_core.vectorstores import VectorStore                    # vector store type
from langchain_community.retrievers import BM25Retriever               # keyword retriever (needs rank_bm25)
from langchain_classic.retrievers import EnsembleRetriever             # fusion

logger = logging.getLogger("tariff.hybrid")                            # logger


def build_hybrid(chunks: list[Document], store: VectorStore, k: int = 5) -> EnsembleRetriever:
    """BM25 for exact codes + vectors for meaning; fused with RRF."""
    if not chunks:                                                     # BM25 cannot index nothing
        raise ValueError("chunks must not be empty")
    bm25 = BM25Retriever.from_documents(chunks)                        # in-memory keyword index
    bm25.k = k                                                         # top-k from keyword side
    vector = store.as_retriever(search_kwargs={"k": k})                # top-k from vector side
    return EnsembleRetriever(
        retrievers=[bm25, vector],                                     # order matches weights
        weights=[0.4, 0.6],                                            # tune using eval set
        id_key="doc_id",                                               # dedupe on metadata id (if present)
    )


async def hybrid_search(r: BaseRetriever, query: str) -> list[Document]:
    """Async search; never crash the API because one retriever failed."""
    try:
        return await asyncio.wait_for(r.ainvoke(query), timeout=5.0)   # retrievers run concurrently
    except Exception:                                                  # any backend problem
        logger.exception("hybrid search failed for %r", query)         # log it
        return []                                                      # empty -> caller handles
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Query                            # FastAPI
from langchain_classic.retrievers import EnsembleRetriever

app = FastAPI()                                                        # app


def get_hybrid() -> EnsembleRetriever:
    raise NotImplementedError                                          # build once in lifespan, return it


@app.get("/search")                                                    # hybrid search endpoint
async def search(
    q: str = Query(min_length=2, max_length=300),                      # validated query param
    r: EnsembleRetriever = Depends(get_hybrid),                        # injected retriever
) -> list[dict]:
    docs = await r.ainvoke(q)                                          # BM25 + vector concurrently
    return [{"text": d.page_content, "meta": d.metadata} for d in docs[:5]]  # cap result size
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Ensemble is itself a Retriever, so it composes with everything else:
hybrid = EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])
compressed = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=hybrid)  # topic 246
chain = {"context": compressed | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# LangGraph: a "router" node can pick weights per query type:
#   code-like query -> weights [0.8, 0.2];  natural language -> [0.3, 0.7]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Weights not matching retriever order
```python
# Wrong — you think 0.7 is for vectors but it is for BM25:
EnsembleRetriever(retrievers=[bm25, vector], weights=[0.7, 0.3])  # intended: vector 0.7

# Correct — same order in both lists:
EnsembleRetriever(retrievers=[bm25, vector], weights=[0.3, 0.7])
```

❌ Mistake 2: Adding raw scores yourself
```python
# Wrong — BM25 scores (0-30) and cosine (0-1) are not comparable:
score = bm25_score + cosine_score

# Correct — fuse by RANK (RRF), which EnsembleRetriever does for you.
```

❌ Mistake 3: Forgetting that BM25 index lives in memory
```python
# Wrong — rebuilding BM25Retriever.from_documents() on every request (slow):
@app.get("/s")
async def s(q: str):
    return BM25Retriever.from_documents(chunks).invoke(q)

# Correct — build once at startup and reuse; for millions of docs use a search engine
# (Elasticsearch / OpenSearch / pgvector + full-text) instead of in-memory BM25.
```

---

## 🧠 Tricky Interview Question

**Q**: "Hybrid search made results worse on your eval set. How can that happen and what do you do?"

**Answer**: RRF only uses ranks, so a weak retriever with a high weight can push bad documents up. Causes: BM25 tokenization is poor for your language (Hindi, codes with dots), weights are not tuned, or both retrievers return the same duplicate chunks with slightly different text so dedupe fails (set `id_key`). Debug by evaluating each retriever alone (recall@k), then tune weights and `c` on a labelled query set, and consider a cross-encoder re-ranker after the ensemble. Hybrid is not automatically better — it must be measured.

---

## ⚫ Interview Questions + Answers

Q1: What is hybrid search? (Easy)
A1: Combining keyword search (BM25) and semantic vector search so that both exact-term and meaning-based queries work well.

Q2: What does EnsembleRetriever return? (Easy)
A2: A single re-ranked list of unique documents produced by fusing the lists of its child retrievers.

Q3: Explain Reciprocal Rank Fusion. (Medium)
A3: Each retriever gives ranks. A document at rank r gets `weight / (c + r)` from that retriever (c is a smoothing constant, 60 by default). Scores for the same document are summed. It ignores raw score scales, so it can combine BM25 and cosine similarity safely.

Q4: How do you choose the weights? (Medium)
A4: Build a labelled set of queries with the correct chunks, compute recall@k / MRR for several weight pairs (grid search), and pick the best. Different query types may deserve different weights, which you can route per query.

Q5: Design hybrid search for 10M chunks. (Hard)
A5: In-memory BM25 will not scale. Use a database with both: OpenSearch/Elasticsearch (BM25 + kNN) or Postgres (full-text + pgvector). Run the two queries concurrently, fuse with RRF, filter by metadata first (country, chapter), re-rank top 50 with a cross-encoder, and cache frequent queries. Monitor recall and latency per stage.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Queries mix exact tokens (codes, names, IDs) and natural language
- Domain has jargon the embedding model may not know
- Pure vector search misses obvious keyword matches

❌ Avoid when:
- Queries are always purely semantic and the corpus is small
- You cannot afford running two searches (latency/infra)
- You have no eval set — you cannot tune it

---

## 📊 Visual Diagram
```
                 Query: "8507.60 charger"
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   BM25 (keywords)                  Vector (meaning)
   1. doc A  2. doc C               1. doc B  2. doc A
          │                                 │
          └────────────► RRF ◄──────────────┘
              score(d) = Σ  weight / (60 + rank)
                           │
                           ▼
              Final: 1. doc A  2. doc B  3. doc C
```

---

## 💰 Cost Impact
Retrieval itself adds little: BM25 is free (CPU), vector search costs one query embedding (~20 tokens). The risk is context size: if each retriever returns k=5 and you pass all unique results, you may send up to 10 chunks (5,000 tokens) instead of 5 (2,500 tokens). On gpt-4o-mini, +2,500 tokens × 100K queries/day = +250M tokens ≈ +$37/day.

Optimise: truncate the fused list to the top 4-5, add a re-ranker/compressor, use metadata filters before search, and cache results per normalised query.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hybrid search | Keyword + semantic together | Keyword और meaning दोनों |
| BM25 | Keyword ranking algorithm | Keyword-based ranking |
| RRF | Reciprocal Rank Fusion | Rank के आधार पर merge |
| Weights | Importance of each retriever | हर retriever का महत्व |
| MRR | Mean Reciprocal Rank metric | पहला सही result कितना ऊपर |
| Cross-encoder | Accurate but slow re-ranker | सटीक re-ranking model |

---

## ⚡ 3-Line Summary
English: EnsembleRetriever fuses several retrievers by rank (RRF), the standard way to do hybrid BM25 + vector search. It handles both exact codes and fuzzy meaning. Tune weights with an eval set and cap the final list to control tokens.
Hindi: EnsembleRetriever कई retrievers को rank (RRF) से मिलाता है, यही BM25 + vector hybrid search का standard तरीका है। यह exact codes और fuzzy meaning दोनों संभालता है। Eval set से weights tune करो और final list छोटी रखो ताकि tokens कम लगें।

---

## ➡️ Next Topic
**249. Chat Models in LangChain** — the LLM side of the chain: one uniform interface for OpenAI, Anthropic and others.

---

# 577. Build Semantic Search
# हिंदी में: Semantic Search बनाओ

---

## 🔵 Simple Definition (English)
Semantic search finds documents by meaning, not exact words. Text is converted to vectors (embeddings); the query vector is compared with document vectors, and the closest ones are returned. "cell phone" can match "smartphone".

## 🔵 सरल परिभाषा (Hindi)
Semantic search documents को meaning से ढूँढता है, exact words से नहीं। Text को vectors (embeddings) में बदला जाता है; query vector की तुलना document vectors से होती है और सबसे नज़दीकी लौटाए जाते हैं। "cell phone" का match "smartphone" से हो सकता है।

---

## 🔴 Problem it Solves
Keyword search (SQL LIKE, BM25) fails when users use different words than the document: "mobile handset" vs "smartphone". Customs officers do not know official HS wording. We need search that understands similar meaning, and the retrieval step that RAG depends on.

## 🔴 यह क्यों बना? (Hindi)
Keyword search तब fail होता है जब user अलग शब्द इस्तेमाल करे: "mobile handset" बनाम "smartphone"। Officers को official HS शब्द नहीं पता होते। हमें ऐसा search चाहिए जो मिलते-जुलते मतलब समझे, और RAG का retrieval step भी यही है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect documents (HS code descriptions)
Step 2 → Embed each document into a vector (once, offline)
Step 3 → Store vectors in an index (memory / Qdrant / pgvector / FAISS)
Step 4 → At query time embed the query with the SAME model
Step 5 → Compute similarity (cosine) between query and every vector (or ANN index)
Step 6 → Sort, apply score threshold, return top-k
Step 7 → (Optional) rerank, then feed to an LLM (RAG)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Documents इकट्ठा करो (HS code descriptions)
Step 2 → हर document का vector बनाओ (एक बार, offline)
Step 3 → Vectors को index में रखो (memory / Qdrant / pgvector / FAISS)
Step 4 → Query आने पर उसी model से query embed करो
Step 5 → Query और vectors के बीच cosine similarity निकालो (या ANN index)
Step 6 → Sort करो, score threshold लगाओ, top-k लौटाओ
Step 7 → (Optional) rerank करो, फिर LLM को दो (RAG)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Index 10,000 HS descriptions. An officer types "cellular mobile phone". Search returns 8517.13 (smartphones) at the top, then the LLM confirms the final code. Without semantic search the LLM would have to guess from memory.

**Amazon-style**: A shopper types "shoes for running in rain" and gets waterproof running shoes even if no title contains those exact words.

## 🟡 Real Example Hindi mein
**Tariff System**: 10,000 HS descriptions index करो। Officer "cellular mobile phone" लिखता है। Search सबसे ऊपर 8517.13 (smartphones) लौटाता है, फिर LLM final code confirm करता है।

**Amazon-style**: Shopper "shoes for running in rain" लिखता है और waterproof running shoes मिलते हैं, भले ही title में ये exact शब्द न हों।

---

## 💻 Code Example — Basic
Full file: `main.py`. It uses a toy hashed bag-of-words embedder, so it only matches shared words (a real embedding model matches synonyms too). Observed output on my run: 8517.13 scored 0.516 for "cellular mobile phone", the laptop doc scored 0.000.

```python
import math  # for vector length

def embed(words: list[str], vocab: list[str]) -> list[float]:
    """Count-vector over a tiny vocabulary, normalised."""
    vec = [float(words.count(w)) for w in vocab]  # count each vocab word
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0  # length, avoid zero
    return [v / norm for v in vec]  # unit vector

vocab = ["phone", "mobile", "laptop", "coffee"]  # tiny vocabulary
docs = {"8517.13": ["mobile", "phone"], "8471.30": ["laptop"]}  # documents
query = embed(["mobile", "phone"], vocab)  # query vector
scores = {k: sum(a * b for a, b in zip(query, embed(v, vocab))) for k, v in docs.items()}  # dot = cosine
print(max(scores, key=scores.get))  # best match: 8517.13
```

## 💻 Code Example — Advanced
Reference using the OpenAI embeddings API and numpy (needs API key and `pip install openai numpy`; not run here). Model name is illustrative; use a current embedding model.

```python
from __future__ import annotations

import numpy as np  # fast vector math
from openai import AsyncOpenAI  # async client

client = AsyncOpenAI()  # reads OPENAI_API_KEY from env
MODEL = "text-embedding-3-small"  # illustrative embedding model name


async def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed many texts in ONE request (batching saves latency)."""
    if not texts:  # nothing to do
        return np.zeros((0, 0))
    resp = await client.embeddings.create(model=MODEL, input=texts)  # network call
    mat = np.array([d.embedding for d in resp.data], dtype=np.float32)  # to matrix
    return mat / np.linalg.norm(mat, axis=1, keepdims=True)  # normalise rows


class Index:
    def __init__(self, ids: list[str], vecs: np.ndarray) -> None:
        self.ids, self.vecs = ids, vecs  # store ids and normalised vectors

    async def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        q = (await embed_texts([query]))[0]  # query vector
        scores = self.vecs @ q  # cosine for all docs at once
        top = np.argsort(-scores)[:k]  # indices of best k
        return [(self.ids[i], float(scores[i])) for i in top]  # (id, score) pairs
```

---

## 🟠 FastAPI Integration
Build the index at startup (lifespan), not per request. Use `async` routes and push CPU-heavy work to a thread, as `main.py` does with `asyncio.to_thread`.

```python
from contextlib import asynccontextmanager  # startup/shutdown hook
from fastapi import FastAPI, Query  # framework

index: Index | None = None  # filled at startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    global index  # assign module-level variable
    ids = ["8517.13", "8471.30"]  # load from DB in real life
    vecs = await embed_texts(["smartphones", "laptop computers"])  # embed once
    index = Index(ids, vecs)  # ready to serve
    yield  # app runs here


app = FastAPI(lifespan=lifespan)


@app.get("/search")
async def search(q: str = Query(min_length=2), k: int = Query(5, ge=1, le=20)):
    assert index is not None  # guard
    return [{"id": i, "score": s} for i, s in await index.search(q, k)]  # JSON list
```

---

## 🔗 LangChain / LangGraph Connection
LangChain wraps this as `Embeddings` + `VectorStore`. A retriever (`vectorstore.as_retriever()`) is a Runnable you can drop into a chain or a LangGraph "retrieve" node.

```python
from langchain_openai import OpenAIEmbeddings  # embedding wrapper
from langchain_core.vectorstores import InMemoryVectorStore  # simple store

emb = OpenAIEmbeddings(model="text-embedding-3-small")  # illustrative model name
store = InMemoryVectorStore(emb)  # in-memory vector store
store.add_texts(["smartphones", "laptop computers"])  # embeds and stores
docs = store.similarity_search("cell phone", k=1)  # top-1 by meaning
print(docs[0].page_content)  # needs API key to run
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Different embedding models for documents and query
✅ Correct: same model and version for both; re-index when you change it.

```python
# Wrong
doc_vecs = embed_with_model_a(docs)
q_vec = embed_with_model_b(query)

# Right
doc_vecs = embed(docs, model=MODEL)
q_vec = embed([query], model=MODEL)
```

❌ Mistake 2: Re-embedding the corpus on every request
✅ Correct: embed once, store, only embed the query.

```python
# Wrong: slow and costly
async def search(q): vecs = await embed_texts(all_docs)

# Right: use the prebuilt index
async def search(q): return await index.search(q)
```

---

## 🧠 Tricky Interview Question
**Q**: "Semantic search returns 'HS 8517.13' for 'phone' but misses the exact code the user typed, '8517.13'. Why, and how do you fix it?"

**Answer**: Embeddings capture meaning, not exact identifiers; codes, SKUs and rare tokens embed poorly. Fix with hybrid search: combine keyword/BM25 (exact match) with vector similarity and merge scores (for example Reciprocal Rank Fusion). Or detect code-shaped queries with a regex and do a direct lookup first. This is exactly why the next problem in the series is hybrid search.

---

## ⚫ Interview Questions + Answers

Q1: What is an embedding?
A1: A list of numbers (vector) representing the meaning of text, so that similar meanings are close in space.

Q2: Why cosine similarity?
A2: It compares direction, not length, so long and short texts are comparable. With normalised vectors it equals a dot product, which is fast.

Q3: What is chunking and why does it matter?
A3: Splitting long documents into smaller pieces (for example 200-500 tokens with some overlap) before embedding. Too big dilutes meaning; too small loses context.

Q4: How do you scale beyond brute force?
A4: Use an approximate nearest neighbour index (HNSW, IVF) in a vector database such as Qdrant, pgvector or FAISS. It trades a little recall for much lower latency.

Q5 (Hard): How would you evaluate and improve search quality?
A5: Build a labelled set of query to correct-code pairs, measure recall@k and MRR, then compare changes: embedding model, chunking, hybrid search, reranker (cross-encoder). Track per-segment results (Hindi queries, code queries) because averages hide failures.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users phrase things differently from the documents
- Multilingual or fuzzy queries
- First step of a RAG pipeline

❌ Avoid when:
- Exact lookup by ID/code is enough (use SQL)
- Tiny corpus where keyword search already works
- Strict legal exactness required with no ranking tolerance

---

## 📊 Visual Diagram
```
 OFFLINE                              ONLINE
 docs ──▶ embed ──▶ [ Vector Index ]   query ──▶ embed
                          ▲                        │
                          └──── cosine / ANN ◀─────┘
                                     │
                              top-k + threshold
                                     │
                                  results
```

---

## 💰 Cost Impact
Token usage: embedding the corpus is a one-time cost of (total document tokens). Each query costs only the query tokens (about 5-20 tokens), which is tiny. Embedding prices are much lower than chat-model prices but change over time; check the provider page (illustrative only).

Example: 10,000 docs x 50 tokens = 500,000 tokens once. 100,000 queries/day x 10 tokens = 1,000,000 tokens/day.

Optimise: batch embedding requests, cache query embeddings for repeated queries, re-embed only changed documents (hash the text), use a smaller embedding dimension if your provider supports it, and retrieve fewer chunks (small k) so the LLM prompt that follows stays short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector of a text's meaning | Text के meaning का vector |
| Cosine similarity | Angle-based closeness score | Angle पर आधारित समानता score |
| Top-k | Best k results | सबसे अच्छे k नतीजे |
| ANN | Approximate nearest neighbour | अनुमानित सबसे नज़दीकी खोज |
| Chunking | Splitting docs into pieces | Documents को टुकड़ों में बाँटना |
| Recall@k | Share of correct items in top-k | Top-k में सही items का अनुपात |

---

## ⚡ 3-Line Summary
English: Semantic search embeds documents and queries and returns the closest vectors by cosine similarity. Embed documents once, use the same model for queries, and add a score threshold. Add keyword search for exact codes (hybrid).
Hindi: Semantic search documents और queries को embed करके cosine similarity से सबसे नज़दीकी vectors लौटाता है। Documents एक बार embed करो, query के लिए वही model रखो और score threshold लगाओ। Exact codes के लिए keyword search जोड़ो (hybrid)।

---

## ➡️ Next Topic
**578. Build Hybrid Search** — combine keyword (BM25) and vector search so both exact codes and fuzzy meaning work.

---

# 244. Vector Stores in LangChain
# हिंदी में: LangChain में Vector Stores

---

## 🔵 Simple Definition (English)
A LangChain `VectorStore` stores documents with their embeddings and supports similarity search. Common methods: `add_documents`, `similarity_search`, `similarity_search_with_score`, `max_marginal_relevance_search`, and `as_retriever()`. Implementations: FAISS, Chroma, pgvector, Pinecone, Qdrant, and more.

## 🔵 सरल परिभाषा (Hindi)
LangChain का `VectorStore` documents को उनके embeddings के साथ रखता है और similarity search करता है। मुख्य methods: `add_documents`, `similarity_search`, `similarity_search_with_score`, `max_marginal_relevance_search`, `as_retriever()`। Implementations: FAISS, Chroma, pgvector, Pinecone, Qdrant आदि।

---

## 🔴 Problem it Solves
Comparing a query vector to millions of stored vectors by brute force is slow, and each database has a different API. Vector stores provide approximate nearest neighbour indexes (HNSW, IVF) and LangChain wraps them in one interface so retrievers and chains work with any backend.

## 🔴 यह क्यों बना? (Hindi)
Query vector की तुलना लाखों stored vectors से brute force में धीमी है, और हर database की API अलग है। Vector stores ANN indexes (HNSW, IVF) देते हैं और LangChain उन्हें एक interface में लपेटता है ताकि retrievers और chains किसी भी backend के साथ चलें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create store with an Embeddings object (Chroma / FAISS / PGVector)
Step 2 → add_documents(chunks): embeds text, saves vector + text + metadata
Step 3 → Query: similarity_search("earbuds", k=4, filter={...})
Step 4 → Store embeds the query, runs ANN search, returns top-k Documents
Step 5 → MMR search: balance relevance and diversity (reduce duplicates)
Step 6 → retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 5})
Step 7 → Persist / upsert / delete by ids; monitor index size and latency
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Embeddings object के साथ store बनाओ (Chroma / FAISS / PGVector)
Step 2 → add_documents(chunks): text embed करके vector + text + metadata save
Step 3 → Query: similarity_search("earbuds", k=4, filter={...})
Step 4 → Store query embed करके ANN search चलाता है, top-k Documents देता है
Step 5 → MMR search: relevance और diversity का संतुलन (duplicates कम)
Step 6 → retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 5})
Step 7 → ids से persist / upsert / delete; index size और latency monitor
```

---

## 🟡 Real World Example
**Tariff Classification System**: pgvector inside our existing Postgres stores 200k chunks with metadata (`chapter`, `country`, `effective_date`). A query filters `country='IN'` and `effective_date <= today`, then does vector search for the top-8. One DB means transactions and backups are shared with order data. **Amazon-style** catalog search might use a managed service (OpenSearch/Pinecone) for scale.

## 🟡 Real Example Hindi mein
**Tariff System**: हमारे मौजूदा Postgres में pgvector 200k chunks को metadata (`chapter`, `country`, `effective_date`) के साथ रखता है। Query पहले `country='IN'` और `effective_date <= today` filter करती है, फिर top-8 vector search। एक ही DB होने से transactions और backups साझा रहते हैं।

---

## 💻 Code Example — Basic
```python
# Runs offline: a tiny in-memory VectorStore using langchain-core's InMemoryVectorStore + a toy embedder
import math
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore

class Toy(Embeddings):
    def _v(self, t: str) -> list[float]:
        v = [0.0] * 16
        for w in t.lower().split():
            v[sum(map(ord, w)) % 16] += 1.0  # deterministic bucket per word
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._v(t) for t in texts]
    def embed_query(self, text: str) -> list[float]:
        return self._v(text)

vs = InMemoryVectorStore(embedding=Toy())  # create store
vs.add_documents([
    Document(page_content="headphones earphones wireless", metadata={"hs": "8518", "country": "IN"}),
    Document(page_content="leather shoes footwear", metadata={"hs": "6403", "country": "IN"}),
    Document(page_content="smartphone telephone", metadata={"hs": "8517", "country": "US"}),
])
for d, score in vs.similarity_search_with_score("wireless earphones", k=2):  # top-2 with scores
    print(d.metadata["hs"], round(score, 3), d.page_content)
retriever = vs.as_retriever(search_kwargs={"k": 1})  # Retriever = Runnable
print(retriever.invoke("shoes")[0].metadata)
```

## 💻 Code Example — Advanced
```python
# pgvector production store: metadata filtering, upsert by id, MMR, async, error handling
# pip install langchain-postgres psycopg[binary]
import asyncio
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = PGVector(
    embeddings=emb,
    collection_name="tariff_chunks",
    connection="postgresql+psycopg://user:pass@localhost:5432/tariff",
    use_jsonb=True,  # metadata stored as JSONB (filterable)
)

async def upsert(chunks: list[Document]) -> int:
    ids = [f"{c.metadata['file']}:{c.metadata.get('page', 0)}:{i}" for i, c in enumerate(chunks)]  # deterministic ids
    try:
        await vs.aadd_documents(chunks, ids=ids)  # same id -> update, not duplicate
    except Exception as exc:
        raise RuntimeError(f"vector upsert failed: {exc}") from exc
    return len(ids)

async def search(q: str, country: str = "IN", k: int = 6) -> list[Document]:
    try:
        return await vs.amax_marginal_relevance_search(  # diverse results
            q, k=k, fetch_k=30, filter={"country": {"$eq": country}}
        )
    except Exception:
        return []  # fail soft; caller can fall back to BM25

# retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 30, "filter": {"country": "IN"}})
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/search")
async def search_route(q: str = Query(..., min_length=2, max_length=300), country: str = "IN") -> dict:
    docs = await search(q, country)  # async vector search
    return {"results": [{"text": d.page_content, "meta": d.metadata} for d in docs]}
```

---

## 🔗 LangChain / LangGraph Connection
`vs.as_retriever()` returns a `VectorStoreRetriever` (a Runnable) that plugs into LCEL RAG chains: `{"context": retriever | fmt, "question": RunnablePassthrough()} | prompt | llm`. LangGraph nodes call `retriever.ainvoke` in a `retrieve` node. Advanced retrievers (MultiQuery, ContextualCompression, ParentDocument, SelfQuery) wrap a vector store.

```python
# graph.add_node("retrieve", lambda s: {"docs": retriever.invoke(s["question"])})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No metadata filter, so wrong-tenant or wrong-country results leak in
```python
# Wrong: vs.similarity_search(q, k=5)
# Right: vs.similarity_search(q, k=5, filter={"tenant_id": user.tenant})
```

❌ Mistake 2: Duplicate inserts on every deploy
```python
# Wrong: vs.add_documents(chunks)  # run daily -> duplicates
# Right: deterministic ids (upsert) or LangChain indexing API with RecordManager (cleanup="incremental")
```

---

## 🧠 Tricky Interview Question
**Q**: "Vector search returns the top-5 chunks that are near duplicates of each other, so the answer misses other relevant info. Fix?"

**Answer**: Use MMR (`search_type="mmr"` with `fetch_k` larger than `k` and `lambda_mult` ~0.5) to trade a bit of relevance for diversity; dedupe at ingestion; or fetch more and rerank/cluster. Also check that overlap is not too large.

---

## ⚫ Interview Questions + Answers

Q1: What does `as_retriever()` do? (Easy)
A1: Wraps the vector store as a Retriever Runnable so it works in chains/graphs.

Q2: What is similarity_search_with_score returning? (Easy)
A2: (Document, score) pairs; meaning depends on the backend (distance: lower is better; similarity: higher is better).

Q3: FAISS vs Chroma vs pgvector? (Medium)
A3: FAISS: fast local library, no metadata filtering built-in at scale. Chroma: easy embedded DB with metadata. pgvector: Postgres extension: SQL filters, transactions, one infra. Managed (Pinecone/Qdrant Cloud): scale and ops handled.

Q4: What are HNSW and IVF? (Medium)
A4: ANN indexes. HNSW: graph-based, high recall, more memory. IVF: clusters vectors and searches nearest clusters, tunable with nprobe.

Q5: Plan a zero-downtime embedding model migration. (Hard)
A5: Create a new collection/index with the new model, backfill via batch job (batch embeddings), dual-write new docs, evaluate the golden set against both, switch the read alias, keep old index for rollback, then delete.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Semantic retrieval for RAG with metadata filtering

❌ Avoid when:
- Exact keyword/ID lookups (use SQL/BM25) or tiny corpora that fit in the prompt

---

## 📊 Visual Diagram
```
 chunks ─► Embeddings ─► vectors ─┐
                                  ▼
                  ┌──────── VectorStore ────────┐
                  │ vector + text + metadata    │  ANN index (HNSW/IVF)
                  └──────────────┬──────────────┘
 query ─► embed ─► similarity_search(k, filter) ─► top-k Documents ─► LLM
```

---

## 💰 Cost Impact
Costs: embedding tokens (one-time + updates), storage (768-1536 floats x 4 bytes = 3-6 KB per vector; 1M vectors is about 3-6 GB plus index), and DB compute. Query tokens come from the k chunks you send to the LLM: lower k, rerank, compress. Optimise: shorter dimensions, quantization (scalar/binary), metadata pre-filtering, and upserts instead of full re-embeds.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vector store | DB for embeddings | Embeddings का database |
| ANN | Approximate nearest neighbour | अनुमानित नज़दीकी खोज |
| HNSW | Graph ANN index | Graph वाला index |
| MMR | Relevance + diversity | प्रासंगिकता + विविधता |
| Upsert | Insert or update | जोड़ो या अपडेट करो |

---

## ⚡ 3-Line Summary
English: A VectorStore keeps documents plus embeddings and answers similarity queries, exposed as a retriever. Use metadata filters, upserts with stable ids, and MMR for diversity. Pick FAISS/Chroma for prototypes and pgvector or managed stores for production.
Hindi: VectorStore documents और embeddings रखता है और similarity queries का जवाब देता है, retriever के रूप में। Metadata filters, stable ids वाले upserts और diversity के लिए MMR इस्तेमाल करो। Prototype में FAISS/Chroma, production में pgvector या managed stores।

---

## ➡️ Next Topic
**245. Retrievers in LangChain** — the Retriever abstraction on top of vector stores and more.

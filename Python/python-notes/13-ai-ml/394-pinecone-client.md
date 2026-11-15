---

# 394. pinecone-client
# हिंदी में: Pinecone Client (Managed Vector Database)

---

## 🔵 Simple Definition (English)
Pinecone is a managed cloud vector database. The Python client lets you store embeddings (lists of numbers) with an id and metadata, and later ask "which stored vectors are closest to this one?". You do not run any server yourself.

Note: the PyPI package was renamed from `pinecone-client` to `pinecone`. Install with `pip install pinecone` (tested with v10.3.0).

## 🔵 सरल परिभाषा (Hindi)
Pinecone एक managed cloud vector database है। Python client से आप embeddings (numbers की list) को id और metadata के साथ store करते हैं, और बाद में पूछते हैं "इस vector के सबसे पास कौन से stored vectors हैं?"। कोई server खुद चलाना नहीं पड़ता।

ध्यान दें: PyPI package का नाम `pinecone-client` से बदलकर `pinecone` हो गया है। `pip install pinecone` करें (v10.3.0 पर जांचा गया)।

---

## 🔴 Problem it Solves
In a RAG chatbot you turn thousands of documents into embeddings and need to find the 5 most similar ones in milliseconds. Searching in a normal SQL table means comparing the query with every row. Running your own vector search (FAISS, pgvector) means you handle scaling, backups, sharding and uptime. Pinecone gives you an API with auto-scaling, persistence, metadata filtering and namespaces.

## 🔴 यह क्यों बना? (Hindi)
RAG chatbot में हजारों documents के embeddings बनते हैं और milliseconds में सबसे मिलते-जुलते 5 चाहिए। सामान्य SQL table में query को हर row से compare करना पड़ता है। अपना vector search (FAISS, pgvector) चलाने का मतलब scaling, backup, sharding और uptime खुद संभालना। Pinecone एक API देता है जिसमें auto-scaling, persistence, metadata filtering और namespaces मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Pinecone client with your API key (from an environment variable)
Step 2 → create_index(name, dimension, metric, spec): dimension MUST equal the embedding size
Step 3 → Get a data handle: index = pc.Index(name)
Step 4 → upsert(vectors=[{id, values, metadata}], namespace=...) inserts or overwrites by id
Step 5 → query(vector=..., top_k=..., filter=..., include_metadata=True) returns nearest matches
Step 6 → Each match has id, score and metadata; you take the metadata text and feed it to the LLM
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → API key (environment variable से) लेकर Pinecone client बनाओ
Step 2 → create_index(name, dimension, metric, spec): dimension embedding के size के बराबर होना ही चाहिए
Step 3 → data handle लो: index = pc.Index(name)
Step 4 → upsert(vectors=[{id, values, metadata}], namespace=...) id के आधार पर insert या overwrite करता है
Step 5 → query(vector=..., top_k=..., filter=..., include_metadata=True) सबसे पास के matches देता है
Step 6 → हर match में id, score और metadata होता है; metadata का text LLM को दे देते हैं
```

---

## 🟡 Real World Example
A Swiggy-style support bot stores 50,000 FAQ chunks as embeddings. Each vector has metadata like `{"topic": "refund", "lang": "hi"}`. When a user asks "mera paisa wapas kab aayega?", the app embeds the question, queries Pinecone with `filter={"topic": "refund"}` and `top_k=4`, then passes the matching FAQ text to the LLM. Each customer (tenant) can have its own namespace so data never mixes.

## 🟡 Real Example Hindi mein
Swiggy जैसा support bot 50,000 FAQ chunks को embeddings के रूप में store करता है। हर vector के साथ metadata होता है जैसे `{"topic": "refund", "lang": "hi"}`। जब user पूछता है "mera paisa wapas kab aayega?", app सवाल का embedding बनाता है, `filter={"topic": "refund"}` और `top_k=4` के साथ Pinecone से query करता है, और मिले FAQ text को LLM को देता है। हर customer (tenant) का अलग namespace हो सकता है ताकि data मिले नहीं।

---

## 💻 Code Example — Basic
```python
# Basic Pinecone client (REAL cloud API: needs PINECONE_API_KEY, so NOT run here)
import os                                          # read the API key from the environment
from pinecone import Pinecone, ServerlessSpec      # pip install pinecone

pc: Pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])   # never hard-code keys
name: str = "faq-demo"                             # index name

if not pc.has_index(name):                         # create only once
    pc.create_index(
        name=name,
        dimension=3,                               # must equal your embedding size (e.g. 1536)
        metric="cosine",                           # cosine / dotproduct / euclidean
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),   # serverless index
    )

index = pc.Index(name)                             # data-plane handle (resolves the index host)
index.upsert(                                      # insert or overwrite by id
    vectors=[
        {"id": "doc1", "values": [1.0, 0.0, 0.0], "metadata": {"topic": "refund"}},
        {"id": "doc2", "values": [0.0, 1.0, 0.0], "metadata": {"topic": "delivery"}},
    ],
    namespace="prod",                              # namespaces partition data inside one index
)
res = index.query(                                 # nearest-neighbour search
    vector=[0.9, 0.1, 0.0],
    top_k=1,
    include_metadata=True,
    namespace="prod",
)
print(res.matches[0].id, res.matches[0].score)     # doc1 and a cosine score near 0.99

# Expected output (cannot be executed without an account; score is approximate):
# doc1 0.9939
```

## 💻 Code Example — Advanced
```python
# Production style: thin wrapper with batching, filters, retry. The wrapper is tested with an
# in-memory FAKE index (same method names as pinecone's Index) so it runs without a cloud account.
import math
import os
import time
from collections.abc import Iterator, Sequence
from typing import Any, Protocol


class IndexLike(Protocol):                         # anything with these methods works (real or fake)
    def upsert(self, *, vectors: Sequence[dict[str, Any]], namespace: str = "") -> Any: ...
    def query(self, *, vector: Sequence[float], top_k: int, namespace: str = "",
              filter: dict[str, Any] | None = None, include_metadata: bool = False) -> Any: ...


def batched(items: Sequence[dict[str, Any]], size: int) -> Iterator[Sequence[dict[str, Any]]]:
    for i in range(0, len(items), size):           # Pinecone limits request size (~2 MB / 1000 vectors)
        yield items[i:i + size]


class Retriever:
    def __init__(self, index: IndexLike, namespace: str = "prod", retries: int = 3) -> None:
        self.index, self.ns, self.retries = index, namespace, retries

    def _retry(self, fn, *a, **kw):
        for attempt in range(self.retries):        # network calls fail: retry with backoff
            try:
                return fn(*a, **kw)
            except ConnectionError:
                if attempt == self.retries - 1:
                    raise                          # give up after last attempt
                time.sleep(0.01 * 2 ** attempt)    # 10ms, 20ms, ...

    def add(self, docs: list[dict[str, Any]], batch: int = 2) -> int:
        n = 0
        for chunk in batched(docs, batch):
            self._retry(self.index.upsert, vectors=chunk, namespace=self.ns)
            n += len(chunk)
        return n

    def search(self, vec: list[float], k: int = 2, topic: str | None = None) -> list[tuple[str, float]]:
        flt = {"topic": {"$eq": topic}} if topic else None      # metadata filter syntax
        res = self._retry(self.index.query, vector=vec, top_k=k, namespace=self.ns,
                          filter=flt, include_metadata=True)
        return [(m["id"], round(m["score"], 3)) for m in res["matches"]]


class FakeIndex:
    """Minimal in-memory stand-in with cosine scoring."""
    def __init__(self) -> None:
        self.data: dict[str, dict[str, Any]] = {}
        self.fail_once = True                      # first query raises to test retry
        self.upsert_calls = 0

    def upsert(self, *, vectors, namespace=""):
        self.upsert_calls += 1
        for v in vectors:
            self.data[v["id"]] = v

    def query(self, *, vector, top_k, namespace="", filter=None, include_metadata=False):
        if self.fail_once:
            self.fail_once = False
            raise ConnectionError("temporary")
        def cos(a, b): return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))
        rows = [v for v in self.data.values()
                if not filter or v["metadata"]["topic"] == filter["topic"]["$eq"]]
        rows.sort(key=lambda v: cos(vector, v["values"]), reverse=True)
        return {"matches": [{"id": v["id"], "score": cos(vector, v["values"])} for v in rows[:top_k]]}


fake = FakeIndex()
r = Retriever(fake)
docs = [
    {"id": "a", "values": [1, 0, 0], "metadata": {"topic": "refund"}},
    {"id": "b", "values": [0.9, 0.4, 0], "metadata": {"topic": "refund"}},
    {"id": "c", "values": [0, 1, 0], "metadata": {"topic": "delivery"}},
    {"id": "d", "values": [0, 0, 1], "metadata": {"topic": "menu"}},
    {"id": "e", "values": [0.1, 0.9, 0], "metadata": {"topic": "delivery"}},
]
print(r.add(docs), fake.upsert_calls)              # 5 vectors in 3 batches of <=2
print(r.search([1, 0.1, 0], k=2))                  # survives one ConnectionError via retry
print(r.search([1, 0.1, 0], k=2, topic="delivery"))
print(os.environ.get("PINECONE_API_KEY") is None)  # real code reads key from env

# Output (really executed, against the fake):
# 5 3
# [('a', 0.995), ('b', 0.95)]
# [('e', 0.209), ('c', 0.1)]
# True
```
Verification: the real `Pinecone` / `Index` method names and signatures (`create_index`, `has_index`, `upsert`, `query(top_k=, filter=, include_metadata=, namespace=)`) were checked by introspection on pinecone 10.3.0. Calls to the real cloud service were NOT run. The retry wrapper above was run against the fake index only. In real code catch Pinecone's own exceptions (for example `pinecone.exceptions.PineconeException` subclasses), not only `ConnectionError`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / TypeScript |
|---------|--------|------------------------|
| Package | `pip install pinecone` | `npm i @pinecone-database/pinecone` |
| Client | `Pinecone(api_key=...)` | `new Pinecone({ apiKey })` |
| Index handle | `pc.Index("name")` | `pc.index("name")` |
| Upsert | `index.upsert(vectors=[...])` | `await index.upsert([...])` |
| Query | `index.query(vector=..., top_k=3)` | `await index.query({ vector, topK: 3 })` |
| Async | separate async client / run in thread | all calls return Promises |

```python
# Python way — keyword arguments, snake_case
res = index.query(vector=[0.1, 0.2, 0.3], top_k=3, include_metadata=True)
for m in res.matches:                              # attribute access on the response object
    print(m.id, m.score)
```
```javascript
// JavaScript way — one options object, camelCase
const res = await index.query({ vector: [0.1, 0.2, 0.3], topK: 3, includeMetadata: true });
for (const m of res.matches) console.log(m.id, m.score);   // same shape
```

Key difference: Python uses `top_k` / `include_metadata` (snake_case) and keyword-only arguments; JS uses `topK` / `includeMetadata` in one object. Both are just a thin wrapper over the same REST API.

---

## 🟠 FastAPI Connection
In a FastAPI RAG service, create the Pinecone client once (at startup via `lifespan` or a cached dependency), not per request. The Pinecone data calls are blocking, so use a plain `def` endpoint (FastAPI runs it in a threadpool) or wrap the call with `run_in_threadpool` inside an `async def` route.

```python
# FastAPI example — retrieval endpoint (needs a real key and index; NOT run here)
import os
from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException
from pinecone import Pinecone

app: FastAPI = FastAPI()


@lru_cache                                          # one client for the whole process
def get_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(os.environ.get("PINECONE_INDEX", "faq-demo"))


@app.post("/search")
def search(vector: list[float], top_k: int = 3, index=Depends(get_index)) -> list[dict]:
    if len(vector) != 3:                            # fail fast: dimension must match the index
        raise HTTPException(status_code=422, detail="vector must have 3 numbers")
    res = index.query(vector=vector, top_k=top_k, include_metadata=True)
    return [{"id": m.id, "score": m.score, "meta": m.metadata} for m in res.matches]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dimension of the index does not match the embedding model
✅ Correct: read the dimension from the model (OpenAI `text-embedding-3-small` = 1536 by default) and create the index with the same number

```python
# Wrong: index created with dimension=768, but embeddings are 1536 numbers -> request error
pc.create_index(name="x", dimension=768, metric="cosine", spec=spec)
# Right: one constant used everywhere
EMBED_DIM: int = 1536
pc.create_index(name="x", dimension=EMBED_DIM, metric="cosine", spec=spec)
```

❌ Mistake 2: Storing the full document text in metadata (limit is ~40 KB per vector) or not storing the text at all
✅ Correct: store a short text snippet or a document id in metadata; keep the full text in your database

```python
# Wrong
index.upsert(vectors=[{"id": "1", "values": v, "metadata": {"text": huge_pdf_text}}])
# Right
index.upsert(vectors=[{"id": "1", "values": v, "metadata": {"doc_id": 42, "chunk": 7}}])
```

❌ Mistake 3: Querying the wrong namespace (it silently returns zero matches)
✅ Correct: always pass the same `namespace` to `upsert` and `query`

```python
index.upsert(vectors=vecs, namespace="tenant-a")
# Wrong: default namespace is "" -> empty result, no error
index.query(vector=q, top_k=3)
# Right
index.query(vector=q, top_k=3, namespace="tenant-a")
```

---

## 🧠 Tricky Interview Question

```python
# What happens?
index.upsert(vectors=[{"id": "a", "values": [1, 0, 0]}])
index.upsert(vectors=[{"id": "a", "values": [0, 1, 0]}])
stats = index.describe_index_stats()
print(stats.total_vector_count)
```
Answer: `1`. `upsert` means "update or insert". The second call overwrites the vector stored under id `"a"`, it does not add a second one. Note that Pinecone is eventually consistent: right after an upsert, `describe_index_stats()` or a query may take a moment to show the change. Also, after overwriting, a query for `[1, 0, 0]` will no longer find `"a"` as a perfect match. (Semantics from Pinecone's documented behaviour; not run here.)

---

## ⚫ Interview Questions + Answers

Q1: What is a vector database and why not use SQL?
A1: It stores embeddings and answers nearest-neighbour queries with approximate indexes (like HNSW) in milliseconds. SQL `WHERE` and `ORDER BY` cannot rank by meaning. (pgvector adds it to Postgres.)

Q2: What does `upsert` do?
A2: Inserts a vector if the id is new, overwrites it if the id exists. It is idempotent: sending the same batch twice gives the same state, which makes retries safe.

Q3: What are namespaces?
A3: Partitions inside one index. Queries only search one namespace. Typical use is multi-tenant SaaS (one namespace per customer) or separating dev/prod data without paying for two indexes.

Q4: Which metric should I choose?
A4: Use the metric the embedding model was trained for. For OpenAI and most text models, `cosine`. Normalised vectors give the same ranking with `dotproduct`. `euclidean` is for models trained with L2 distance.

Q5: How do you combine semantic search with filters?
A5: Pass `filter={"topic": {"$eq": "refund"}}`. Pinecone applies the metadata filter during the search, so you still get `top_k` results from the allowed subset.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a managed vector store with no ops work
- You need metadata filtering and multi-tenancy (namespaces)
- Data is large (millions of vectors) and must stay fast

❌ Avoid when:
- A few thousand vectors on one machine: FAISS or `numpy` is free and enough
- Your data must stay on-premises (use pgvector, Qdrant or Milvus self-hosted)
- You need strong read-after-write consistency immediately

---

## 📊 Visual Diagram
```
 documents ──► embedding model ──► vectors (1536 numbers each)
                                        │ upsert(id, values, metadata, namespace)
                                        ▼
                               ┌─────────────────┐
 user question ─► embedding ─► │ Pinecone index  │ ─► top_k matches (id, score, metadata)
                  query()      │ ns: tenant-a    │            │
                               │ ns: tenant-b    │            ▼
                               └─────────────────┘      prompt + context ─► LLM ─► answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | List of numbers representing meaning | अर्थ को दर्शाने वाली numbers की list |
| Index | Container of vectors with fixed dimension | Vectors का container (fixed dimension) |
| Namespace | Partition inside an index | Index के अंदर अलग हिस्सा |
| Upsert | Insert or overwrite by id | id से insert या overwrite |
| top_k | How many nearest results to return | कितने सबसे पास के results चाहिए |
| Metadata filter | Condition on stored fields during search | Search के दौरान fields पर शर्त |

---

## ⚡ 3-Line Summary
English: Pinecone is a managed vector database; the `pinecone` Python client creates an index, upserts vectors with metadata and queries nearest neighbours. The index dimension must equal your embedding size, and upsert overwrites by id. Create the client once and use namespaces and filters for multi-tenant RAG.
Hindi: Pinecone एक managed vector database है; `pinecone` Python client index बनाता है, metadata के साथ vectors upsert करता है और nearest neighbours query करता है। Index की dimension embedding के size के बराबर होनी चाहिए, और upsert id के आधार पर overwrite करता है। Client एक बार बनाएं और multi-tenant RAG के लिए namespaces व filters इस्तेमाल करें।

---

## ➡️ Next Topic
**395. FAISS** — Facebook's open-source library for vector similarity search that runs inside your own process, no cloud needed.

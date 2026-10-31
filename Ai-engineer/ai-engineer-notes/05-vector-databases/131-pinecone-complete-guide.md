---

# 131. Pinecone — Complete Guide
# हिंदी में: Pinecone — पूरी Guide

---

## 🔵 Simple Definition (English)
Pinecone is a fully managed, cloud vector database. You create an index, upsert vectors with metadata, and query for the nearest ones through a simple API. Pinecone handles indexing, scaling, replication and updates, so you run no servers. Its building blocks are: project, index, namespace, vector (id + values + metadata).

## 🔵 सरल परिभाषा (Hindi)
Pinecone एक fully managed cloud vector database है। आप index बनाते हैं, metadata के साथ vectors upsert करते हैं और simple API से सबसे पास वाले vectors query करते हैं। Indexing, scaling, replication और updates Pinecone संभालता है, कोई server नहीं चलाना पड़ता। Building blocks: project, index, namespace, vector (id + values + metadata)।

---

## 🔴 Problem it Solves
Running your own vector DB means choosing an ANN algorithm, sizing RAM, sharding, backups, upgrades and monitoring. Small teams lose weeks on infrastructure instead of product. Pinecone offers production-grade vector search as an API with automatic scaling (serverless) and a pay-for-what-you-use model.

## 🔴 यह क्यों बना? (Hindi)
अपना vector DB चलाने का मतलब है ANN algorithm चुनना, RAM size करना, sharding, backups, upgrades और monitoring। छोटी teams product की जगह infrastructure में हफ़्ते खो देती हैं। Pinecone production-grade vector search को API के रूप में देता है, auto scaling (serverless) और use के हिसाब से pay के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Sign up, get an API key (PINECONE_API_KEY)
Step 2 → pc = Pinecone(api_key=...)  (client)
Step 3 → pc.create_index(name, dimension, metric, spec=ServerlessSpec(cloud, region))
Step 4 → index = pc.Index(name)  (data-plane handle)
Step 5 → index.upsert(vectors=[{id, values, metadata}], namespace="...")
Step 6 → index.query(vector=q, top_k=5, filter={...}, include_metadata=True)
Step 7 → Read matches (id, score, metadata) -> fetch text -> send to LLM
Step 8 → index.delete(ids=[...]) / index.describe_index_stats() for maintenance
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Sign up करो, API key लो (PINECONE_API_KEY)
Step 2 → pc = Pinecone(api_key=...)  (client)
Step 3 → pc.create_index(name, dimension, metric, spec=ServerlessSpec(...))
Step 4 → index = pc.Index(name)  (data-plane handle)
Step 5 → index.upsert(vectors=[{id, values, metadata}], namespace="...")
Step 6 → index.query(vector=q, top_k=5, filter={...}, include_metadata=True)
Step 7 → Matches (id, score, metadata) पढ़ो -> text लाओ -> LLM को दो
Step 8 → index.delete(ids=[...]) / describe_index_stats() maintenance के लिए
```

---

## 🟡 Real World Example
**Tariff Classification System**: one index `tariff-hs` (dimension 1536, cosine). Vectors are HS heading descriptions with metadata `{country, chapter, hs_code, text}`. For each user query the app embeds it, queries top 5 with `filter={"country": "IN"}`, and gives the 5 headings to the LLM, which picks the final code. Separate namespaces hold `rulings` and `headings`.

**Zomato AI**: dish vectors with metadata `{city, veg, price}`; one query returns the 10 closest dishes in Bengaluru under Rs 300.

## 🟡 Real Example Hindi mein
**Tariff System**: एक index `tariff-hs` (dimension 1536, cosine)। Vectors HS heading descriptions हैं, metadata `{country, chapter, hs_code, text}`। हर query embed होती है, `filter={"country": "IN"}` के साथ top 5 आते हैं और LLM final code चुनता है। `rulings` और `headings` के लिए अलग namespaces। **Zomato**: dish vectors में `{city, veg, price}` metadata; एक query बेंगलुरु की 300 रुपये से कम की 10 सबसे similar dishes देती है।

---

## 💻 Code Example — Basic
```python
# Basic: Pinecone quickstart (pip install pinecone). Falls back to a local mock without an API key.
import math                                                  # cosine math for the mock
import os                                                    # read env variables
from typing import Any, Dict, List                           # type hints

API_KEY = os.getenv("PINECONE_API_KEY")                      # None when not configured
DIM = 4                                                      # tiny demo dimension

class MockIndex:
    """Offline stand-in with the same upsert/query shape as the real Pinecone index."""
    def __init__(self) -> None:
        self.rows: Dict[str, Dict[str, Any]] = {}            # id -> {values, metadata}
    def upsert(self, vectors: List[Dict[str, Any]], namespace: str = "") -> None:
        for v in vectors:                                    # store each vector
            self.rows[v["id"]] = v                           # overwrite by id
    def query(self, vector: List[float], top_k: int, include_metadata: bool = True, **_: Any) -> Dict[str, Any]:
        def cos(a: List[float], b: List[float]) -> float:    # cosine similarity
            return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))
        ranked = sorted(self.rows.values(), key=lambda r: -cos(vector, r["values"]))[:top_k]
        return {"matches": [{"id": r["id"], "score": round(cos(vector, r["values"]), 3), "metadata": r["metadata"]} for r in ranked]}

if API_KEY:                                                  # real Pinecone path
    from pinecone import Pinecone, ServerlessSpec            # official SDK (v3+)
    pc = Pinecone(api_key=API_KEY)                           # create client
    if "demo-index" not in pc.list_indexes().names():        # create only once
        pc.create_index(name="demo-index", dimension=DIM, metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"))   # serverless index
    index = pc.Index("demo-index")                           # get the index handle
else:
    index = MockIndex()                                      # offline fallback

index.upsert(vectors=[                                       # write vectors
    {"id": "8518", "values": [0.9, 0.1, 0.0, 0.1], "metadata": {"text": "Headphones", "chapter": 85}},
    {"id": "6205", "values": [0.0, 0.1, 0.9, 0.2], "metadata": {"text": "Shirts", "chapter": 62}},
])
res = index.query(vector=[1.0, 0.0, 0.1, 0.0], top_k=1, include_metadata=True)   # nearest 1
print(res["matches"] if isinstance(res, dict) else res.matches)   # SDK returns an object, mock a dict
```

## 💻 Code Example — Advanced
```python
# Advanced: production wrapper with batching, retries, typed results, async via threads.
import asyncio                                               # async runtime
import logging                                               # logs
import os                                                    # env
import time                                                  # sleep for backoff
from typing import Any, Dict, Iterable, List, Optional       # type hints

from pinecone import Pinecone, ServerlessSpec                # Pinecone SDK
from pydantic import BaseModel                               # pydantic v2

log = logging.getLogger("pinecone-store")                    # logger

class Match(BaseModel):
    id: str                                                  # vector id
    score: float                                             # similarity
    metadata: Dict[str, Any]                                 # stored fields

class PineconeStore:
    def __init__(self, name: str, dim: int, namespace: str = "default") -> None:
        key = os.environ.get("PINECONE_API_KEY")             # never hard-code keys
        if not key:                                          # fail fast and clearly
            raise RuntimeError("PINECONE_API_KEY is not set")
        self.pc = Pinecone(api_key=key)                      # client
        self.namespace = namespace                           # logical partition
        if name not in self.pc.list_indexes().names():       # idempotent create
            self.pc.create_index(name=name, dimension=dim, metric="cosine",
                                 spec=ServerlessSpec(cloud="aws", region="us-east-1"))
            while not self.pc.describe_index(name).status["ready"]:   # wait until ready
                time.sleep(1)
        self.index = self.pc.Index(name)                     # data-plane handle

    @staticmethod
    def _batches(items: List[Dict[str, Any]], n: int = 100) -> Iterable[List[Dict[str, Any]]]:
        for i in range(0, len(items), n):                    # Pinecone recommends <= 100-200 per upsert
            yield items[i:i + n]

    def upsert(self, items: List[Dict[str, Any]], retries: int = 3) -> int:
        total = 0                                            # counts written vectors
        for batch in self._batches(items):                   # per batch
            for attempt in range(retries):                   # simple retry
                try:
                    self.index.upsert(vectors=batch, namespace=self.namespace)   # write
                    total += len(batch)                      # success
                    break
                except Exception as exc:                     # network / rate-limit errors
                    log.warning("upsert retry %d: %s", attempt + 1, exc)
                    time.sleep(2 ** attempt)                 # exponential backoff
            else:
                raise RuntimeError("upsert failed after retries")   # surface permanent failure
        return total

    def query(self, vec: List[float], k: int = 5, flt: Optional[Dict[str, Any]] = None) -> List[Match]:
        res = self.index.query(vector=vec, top_k=k, filter=flt,
                               include_metadata=True, namespace=self.namespace)   # ANN query
        return [Match(id=m.id, score=m.score, metadata=m.metadata or {}) for m in res.matches]

    async def aquery(self, vec: List[float], k: int = 5, flt: Optional[Dict[str, Any]] = None) -> List[Match]:
        return await asyncio.to_thread(self.query, vec, k, flt)   # async-friendly wrapper

# Token usage: Pinecone calls use 0 LLM tokens. Cost units: read units per query, write units per upsert.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException               # FastAPI
from openai import AsyncOpenAI                            # embeddings client
from pydantic import BaseModel                            # request model

app = FastAPI()                                           # app
oai = AsyncOpenAI()                                       # reads OPENAI_API_KEY
store = PineconeStore("tariff-hs", dim=1536, namespace="headings")   # created at startup

class Ask(BaseModel):
    question: str                                         # user question
    country: str | None = None                            # optional metadata filter

@app.post("/tariff/search")                               # semantic search endpoint
async def search(body: Ask) -> dict:
    try:
        emb = await oai.embeddings.create(model="text-embedding-3-small", input=body.question)   # ~20 tokens
        flt = {"country": {"$eq": body.country}} if body.country else None    # Pinecone filter syntax
        hits = await store.aquery(emb.data[0].embedding, k=5, flt=flt)        # vector search
    except Exception as exc:                              # embedding or Pinecone failure
        raise HTTPException(502, f"upstream error: {exc}")
    return {"matches": [h.model_dump() for h in hits]}    # pydantic v2 -> dict
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-pinecone
from langchain_openai import OpenAIEmbeddings            # embeddings
from langchain_pinecone import PineconeVectorStore        # official integration

emb = OpenAIEmbeddings(model="text-embedding-3-small")    # 1536 dims
vs = PineconeVectorStore(index_name="tariff-hs", embedding=emb, namespace="headings")   # uses PINECONE_API_KEY
vs.add_texts(["Headphones 8518.30"], metadatas=[{"country": "IN"}])   # embed + upsert
retriever = vs.as_retriever(search_kwargs={"k": 5, "filter": {"country": "IN"}})       # LCEL retriever
docs = retriever.invoke("wireless earbuds")               # use in a chain or LangGraph node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Index dimension does not match the embedding model
✅ Correct: create the index with the model's exact dimension.

```python
# Wrong: index dimension=768, but text-embedding-3-small returns 1536 -> upsert error
pc.create_index(name="x", dimension=768, metric="cosine", spec=spec)
# Right
pc.create_index(name="x", dimension=1536, metric="cosine", spec=spec)
```

❌ Mistake 2: Storing the full document text in metadata (40 KB per-vector limit; also costs storage)
✅ Correct: store a short snippet or an id, keep the full text in a database.

```python
# Wrong: metadata={"text": whole_chapter}   # can exceed the limit
# Right: metadata={"doc_id": "ch85", "snippet": text[:300]}
```

❌ Mistake 3: Querying right after upsert and expecting to see the data (eventual consistency)
✅ Correct: allow a short delay or poll `describe_index_stats()`.

---

## 🧠 Tricky Interview Question

**Q**: "You upsert 1,000 vectors and immediately query, but get empty results. Is Pinecone broken?"

**Answer**: No. Pinecone is eventually consistent: freshly written vectors become searchable after a short delay (seconds on serverless). Other usual causes: querying a different namespace than you upserted into (namespaces are isolated, and the default namespace is `""`), a filter that matches nothing, or a metric/dimension mismatch. Check `describe_index_stats()` for per-namespace vector counts, and use the same namespace in both calls.

---

## ⚫ Interview Questions + Answers

Q1: What is Pinecone?
A1: A managed vector database offered as an API, with serverless and pod-based deployment, metadata filtering and namespaces.

Q2: What is in a Pinecone vector record?
A2: An `id` (string), `values` (list of floats), optional `metadata` (key-value pairs for filtering) and, for hybrid search, optional `sparse_values`.

Q3: What does upsert do?
A3: Inserts the vector if the id is new, otherwise overwrites it. This makes ingestion idempotent.

Q4: How do namespaces help?
A4: They partition one index into isolated groups (per tenant, per environment). A query only searches within one namespace, which is great for multi-tenancy and faster scans.

Q5: Design a multi-tenant RAG system on Pinecone for 2,000 customers.
A5: Use one serverless index with one namespace per customer (cheap and isolated, deletion is easy by dropping the namespace). Embed with a fixed model recorded in index naming/metadata. Ingest in batches of 100 with retries. At query time always pass the tenant's namespace derived from the authenticated user (never from request input), add metadata filters for document types, and rerank before the LLM. Monitor read/write units per tenant for chargeback, and keep raw text in object storage so you can re-embed when the model changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want zero infrastructure and fast time to production
- Variable or spiky traffic (serverless)
- Multi-tenant apps using namespaces

❌ Avoid when:
- Data must stay on-premise or in a specific region Pinecone does not offer
- You already run Postgres and have small data (pgvector is cheaper)
- You need full control over index internals

---

## 📊 Visual Diagram
```
 App ──embed──► vector
   │
   ▼   HTTPS API
 ┌────────────────────── Pinecone Project ──────────────────────┐
 │  Index "tariff-hs"  (dim=1536, cosine, serverless)           │
 │   ├─ namespace "headings"  [id, values, metadata] ...        │
 │   └─ namespace "rulings"   [id, values, metadata] ...        │
 └──────────────────────────────────────────────────────────────┘
   ▲ upsert(vectors)            │ query(vector, top_k, filter)
   └────────────────────────────┴──► matches (id, score, metadata) ──► LLM
```

---

## 💰 Cost Impact
- Serverless is billed on storage (GB-month), read units and write units; no idle pods. Check the current pricing page because rates change.
- Rough sizing: 1M x 1536 float vectors is ~6 GB. Metadata adds to it, so keep metadata lean.
- Query volume matters more than size for spiky apps; cache frequent queries (for example "iPhone HS code") to avoid reads.
- LLM savings: returning 5 relevant headings (~1,000 tokens) instead of stuffing 30K tokens of tariff text into gpt-4o ($5 / 1M input) saves about $0.145 per query.
- Optimise: lower dimensions with `dimensions=` on text-embedding-3, delete stale vectors, batch upserts, use namespaces to scope reads.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Container of vectors with a fixed dimension | Fixed dimension वाला vectors का container |
| Namespace | Isolated partition in an index | Index के अंदर अलग partition |
| Upsert | Insert or update | डालो या update करो |
| Metadata | Filterable key-value data on a vector | Vector के साथ जुड़ा filterable data |
| Serverless | Pay per use, no pods to manage | उपयोग के हिसाब से भुगतान, pods नहीं |
| Read unit | Billing unit for queries | Query की billing unit |
| Eventual consistency | New data appears after a short delay | नया data थोड़ी देर बाद दिखना |

---

## ⚡ 3-Line Summary
English: Pinecone is a managed vector DB: create an index, upsert vectors with metadata, query top-k with filters. Namespaces isolate tenants; serverless removes capacity planning. Match dimension and metric to your embedding model, and remember eventual consistency.
Hindi: Pinecone managed vector DB है: index बनाओ, metadata के साथ vectors upsert करो, filters के साथ top-k query करो। Namespaces tenants को अलग रखते हैं; serverless से capacity planning नहीं करनी पड़ती। Embedding model से dimension और metric match करो, और eventual consistency याद रखो।

---

## ➡️ Next Topic
**132. Pinecone Index Setup** — dimensions, metrics, serverless regions and creating indexes safely.

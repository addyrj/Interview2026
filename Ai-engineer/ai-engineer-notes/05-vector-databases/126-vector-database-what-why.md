---

# 126. Vector Database — What + Why
# हिंदी में: Vector Database — क्या है और क्यों

---

## 🔵 Simple Definition (English)
A vector database stores embeddings (lists of numbers) together with metadata and finds the "nearest" ones to a query vector very fast. Instead of matching exact words like SQL `WHERE`, it matches meaning. It is the memory layer behind RAG, semantic search and recommendations.

## 🔵 सरल परिभाषा (Hindi)
Vector database embeddings (numbers की list) को metadata के साथ store करता है और query vector के सबसे "पास" वाले vectors बहुत तेज़ी से ढूँढता है। SQL `WHERE` की तरह exact words नहीं, बल्कि meaning match करता है। यह RAG, semantic search और recommendations की memory layer है।

---

## 🔴 Problem it Solves
Comparing a query to every stored vector (brute force) is O(N x d). With 10 million vectors of 1536 dimensions that is ~15 billion multiplications per query, far too slow for a live app. Normal databases cannot index "closeness" in high dimensions. A vector DB adds approximate nearest neighbour (ANN) indexes, metadata filtering, persistence, scaling, updates and deletes.

## 🔴 यह क्यों बना? (Hindi)
Query को हर stored vector से compare करना (brute force) O(N x d) है। 1 करोड़ vectors x 1536 dimensions पर हर query में ~15 अरब गुणा होंगे, live app के लिए बहुत धीमा। Normal databases high dimensions में "closeness" index नहीं कर सकते। Vector DB ANN indexes, metadata filtering, persistence, scaling, update और delete देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a collection/index with dimension + distance metric (cosine / dot / L2)
Step 2 → Embed documents with an embedding model
Step 3 → Upsert (id, vector, metadata) into the database
Step 4 → DB builds an ANN index (HNSW / IVF) so search avoids scanning everything
Step 5 → At query time: embed the user question with the SAME model
Step 6 → DB returns top-k nearest ids with scores (+ optional metadata filter)
Step 7 → App fetches the text of those ids and gives it to the LLM (RAG)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Collection बनाओ: dimension + distance metric (cosine / dot / L2)
Step 2 → Embedding model से documents embed करो
Step 3 → (id, vector, metadata) को upsert करो
Step 4 → DB ANN index (HNSW / IVF) बनाता है ताकि सब कुछ scan न करना पड़े
Step 5 → Query के समय उसी model से question embed करो
Step 6 → DB top-k nearest ids + scores लौटाता है (optional metadata filter)
Step 7 → App उन ids का text निकालकर LLM को देता है (RAG)
```

---

## 🟡 Real World Example
**Tariff Classification System**: 200,000 HS-code descriptions and past rulings are embedded and stored. A user types "wireless earbuds with charging case"; the DB returns the 5 closest heading descriptions in ~20 ms, filtered by `country="IN"`. The LLM then picks the final code from just those 5.

**Zomato AI**: "cheap spicy biryani near me" becomes a vector; the DB finds similar dishes and filters by `city`, `veg=false`, `price<300`.

## 🟡 Real Example Hindi mein
**Tariff System**: 2 लाख HS-code descriptions और पुराने rulings embed करके store किए गए हैं। User "wireless earbuds with charging case" लिखता है; DB ~20 ms में 5 सबसे पास वाले headings देता है, `country="IN"` filter के साथ। LLM सिर्फ़ उन 5 में से final code चुनता है। **Zomato**: "सस्ती तीखी बिरयानी" vector बनता है, DB similar dishes ढूँढता है और city/price filter लगाता है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny in-memory "vector database" in pure Python (brute-force search)
import math                                        # sqrt for cosine
from dataclasses import dataclass, field           # simple record class
from typing import Any, Dict, List, Tuple          # type hints

@dataclass
class Record:
    id: str                                        # unique id
    vector: List[float]                            # embedding
    metadata: Dict[str, Any] = field(default_factory=dict)  # filterable fields

class TinyVectorDB:
    def __init__(self) -> None:
        self.rows: Dict[str, Record] = {}          # id -> record

    def upsert(self, rec: Record) -> None:
        self.rows[rec.id] = rec                    # insert or overwrite by id

    @staticmethod
    def _cos(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))     # dot product
        na = math.sqrt(sum(x * x for x in a))      # norm of a
        nb = math.sqrt(sum(y * y for y in b))      # norm of b
        return dot / (na * nb) if na and nb else 0.0  # guard zero vectors

    def query(self, vec: List[float], k: int = 2, where: Dict[str, Any] | None = None) -> List[Tuple[str, float]]:
        scored = []                                # (id, score) list
        for r in self.rows.values():               # scan every record (brute force)
            if where and any(r.metadata.get(key) != val for key, val in where.items()):
                continue                           # skip rows failing the metadata filter
            scored.append((r.id, self._cos(vec, r.vector)))  # compute similarity
        return sorted(scored, key=lambda t: t[1], reverse=True)[:k]  # best k

db = TinyVectorDB()                                # create the store
db.upsert(Record("h1", [0.9, 0.1, 0.0], {"country": "IN"}))   # electronics heading
db.upsert(Record("h2", [0.1, 0.9, 0.0], {"country": "IN"}))   # food heading
db.upsert(Record("h3", [0.8, 0.2, 0.1], {"country": "US"}))   # electronics, other country
print(db.query([1.0, 0.0, 0.0], k=2, where={"country": "IN"}))  # h1 first, then h2
```

## 💻 Code Example — Advanced
```python
# Advanced: a typed repository interface so the app is not locked to one vector DB.
# Swap implementations (Pinecone / Qdrant / pgvector) without touching business code.
import asyncio                                         # async support
import logging                                         # logging
from abc import ABC, abstractmethod                    # interface definition
from typing import Any, Dict, List, Optional           # type hints

from pydantic import BaseModel, Field                  # pydantic v2 data models

log = logging.getLogger("vectorstore")                 # logger

class Chunk(BaseModel):
    id: str                                            # chunk id
    text: str                                          # original text (stored beside vector)
    vector: List[float]                                # embedding
    metadata: Dict[str, Any] = Field(default_factory=dict)  # filters like country, chapter

class Hit(BaseModel):
    id: str                                            # matched id
    score: float                                       # similarity score
    metadata: Dict[str, Any]                           # payload for display / filtering

class VectorStore(ABC):
    """Contract every backend must follow."""

    @abstractmethod
    async def upsert(self, chunks: List[Chunk]) -> int: ...      # returns number written

    @abstractmethod
    async def search(self, vector: List[float], k: int, where: Optional[Dict[str, Any]] = None) -> List[Hit]: ...

class InMemoryStore(VectorStore):
    """Reference backend for tests (swap for a real one in production)."""

    def __init__(self, dim: int) -> None:
        self.dim = dim                                 # enforce one dimension per store
        self._data: Dict[str, Chunk] = {}              # id -> chunk

    async def upsert(self, chunks: List[Chunk]) -> int:
        for c in chunks:                               # validate every chunk
            if len(c.vector) != self.dim:              # dimension mismatch is the #1 bug
                raise ValueError(f"{c.id}: expected {self.dim} dims, got {len(c.vector)}")
            self._data[c.id] = c                       # store it
        return len(chunks)                             # report count

    async def search(self, vector: List[float], k: int, where: Optional[Dict[str, Any]] = None) -> List[Hit]:
        if len(vector) != self.dim:                    # validate the query too
            raise ValueError("query dimension mismatch")
        hits: List[Hit] = []                           # results list
        for c in self._data.values():                  # brute force, fine for tests
            if where and any(c.metadata.get(a) != b for a, b in where.items()):
                continue                               # metadata filter
            score = sum(x * y for x, y in zip(vector, c.vector))  # dot (vectors assumed unit)
            hits.append(Hit(id=c.id, score=score, metadata=c.metadata))
        hits.sort(key=lambda h: h.score, reverse=True) # best first
        return hits[:k]                                # top-k

async def demo() -> None:
    store = InMemoryStore(dim=3)                       # 3-D for the demo
    await store.upsert([Chunk(id="a", text="phones", vector=[1, 0, 0], metadata={"ch": 85})])
    print(await store.search([1, 0, 0], k=1))          # -> hit "a"

# asyncio.run(demo())  # token usage: 0 here; real use costs only the embedding calls
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException   # FastAPI + dependency injection

app = FastAPI()                                        # app
store = InMemoryStore(dim=3)                           # single shared store

def get_store() -> VectorStore:
    return store                                       # dependency (easy to mock in tests)

@app.post("/search")                                   # semantic search route
async def search(vector: list[float], k: int = 5, s: VectorStore = Depends(get_store)) -> list[Hit]:
    try:
        return await s.search(vector, k)               # delegate to backend
    except ValueError as exc:                          # bad dimension etc.
        raise HTTPException(status_code=422, detail=str(exc))  # client error
```

---

## 🔗 LangChain / LangGraph Connection
LangChain wraps every vector DB in the same `VectorStore` interface, so a retriever node in LangGraph does not care which DB is behind it.

```python
from langchain_core.vectorstores import InMemoryVectorStore   # built-in, no server needed
from langchain_openai import OpenAIEmbeddings                  # embedding model

vs = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))  # create store
vs.add_texts(["Static converters 8504.40", "Smartphones 8517.13"])          # embed + store
retriever = vs.as_retriever(search_kwargs={"k": 2})                          # standard retriever
docs = retriever.invoke("phone charger")                                     # LCEL-compatible
# In LangGraph: `def retrieve(state): return {"docs": retriever.invoke(state["q"])}`
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a vector DB when a SQL `LIKE` or exact lookup is enough
✅ Correct: use vector search only for meaning-based retrieval.

```python
# Wrong: embedding HS codes to find "8517.13" exactly
hits = store.search(embed("8517.13"), k=1)
# Right: exact keys belong in a normal index
row = sql.execute("SELECT * FROM hs WHERE code = %s", ("8517.13",))
```

❌ Mistake 2: Dimension or metric mismatch between index and embedding model
✅ Correct: read the model dimension once and create the index with it.

```python
# Wrong: index dim=768 but model returns 1536 -> insert error
# Right: assert at startup
assert len(embed("probe")) == INDEX_DIM, "index/model dimension mismatch"
```

---

## 🧠 Tricky Interview Question

**Q**: "Why not just store embeddings in a normal Postgres JSON column and compute cosine in Python?"

**Answer**: It works for a few thousand rows, but cost grows linearly: every query scans everything and ships all vectors to the app. A vector DB (or pgvector) builds an ANN index (HNSW/IVF), so queries touch a tiny fraction of data, and pushes metadata filters into the index. The trade-off: ANN is approximate (recall under 100%) and indexes cost memory. Under ~50k vectors brute force is often fine; beyond that use an index.

---

## ⚫ Interview Questions + Answers

Q1: What does a vector database store?
A1: Vectors (embeddings), an id, and metadata (and sometimes the raw text). It indexes vectors for fast similarity search.

Q2: What distance metrics are common?
A2: Cosine similarity (direction), dot product (direction + magnitude) and Euclidean/L2 distance. Use the metric the embedding model was trained for, usually cosine.

Q3: How is a vector DB different from a traditional DB?
A3: Traditional DBs answer exact predicates (`=`, `<`, `LIKE`). A vector DB answers "most similar to this vector" using ANN indexes, and combines that with metadata filters.

Q4: What is the recall vs latency trade-off?
A4: ANN indexes skip most vectors, so they may miss a true neighbour. Tuning parameters (HNSW `ef_search`, IVF `nprobe`) raises recall but increases latency. Teams usually target 95-99% recall.

Q5: How would you choose between Pinecone, Qdrant, Chroma, FAISS and pgvector?
A5: FAISS is a library (no server, no metadata). Chroma is great for prototypes and small apps. pgvector fits when you already run Postgres and need transactions plus under ~10M vectors. Pinecone is fully managed and low-ops. Qdrant/Weaviate are open-source servers with rich filtering and hybrid search. Decide on scale, filtering needs, ops budget, hosting rules (data residency) and cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Semantic search, RAG, recommendations, deduplication
- Millions of vectors with sub-100 ms latency needs
- Need metadata filters with similarity search

❌ Avoid when:
- Exact lookup or small data (a SQL index or in-memory array is simpler)
- You need strict 100% exact recall (use brute force)

---

## 📊 Visual Diagram
```
   Documents ──embed──► vectors ──upsert──►┌─────────────────────────┐
                                           │      VECTOR DATABASE    │
                                           │  ANN index (HNSW/IVF)   │
   User question ─embed─► query vector ───►│  metadata filter        │
                                           └────────────┬────────────┘
                                                        │ top-k ids + scores
                                                        ▼
                                            text chunks ──► LLM ──► answer
```

---

## 💰 Cost Impact
- Storage: 1M vectors x 1536 dims x 4 bytes = ~6 GB of RAM/disk (plus index overhead, HNSW adds ~20-50%).
- Managed DB pricing is by storage + read/write units; self-hosted is by machine size.
- LLM savings: sending only the top 5 chunks (about 1,500 tokens) instead of whole documents (50,000 tokens) turns a ~$0.25 gpt-4o call into ~$0.004. That is the real ROI of a vector DB.
- Optimise: reduce dimensions, use scalar/product quantisation, delete stale vectors, and filter by metadata to shrink the search space.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vector | List of numbers representing meaning | Meaning को दर्शाने वाली numbers की list |
| ANN | Approximate nearest neighbour search | लगभग सबसे पास वाले ढूँढना |
| Metric | How closeness is measured | Closeness नापने का तरीका |
| Top-k | The k best matches | सबसे अच्छे k matches |
| Metadata filter | Constrain search by fields | Fields से search सीमित करना |
| Upsert | Insert or update | नया डालो या पुराना update करो |
| Collection/Index | Container for vectors | Vectors का container |

---

## ⚡ 3-Line Summary
English: A vector database stores embeddings and finds the most similar ones fast using ANN indexes. It adds filtering, persistence and scale that brute force cannot. It is the retrieval engine of RAG.
Hindi: Vector database embeddings store करता है और ANN indexes से सबसे similar vectors तेज़ी से ढूँढता है। यह filtering, persistence और scale देता है जो brute force नहीं दे सकता। यह RAG का retrieval engine है।

---

## ➡️ Next Topic
**127. How Vector Search Works** — distance metrics, brute force vs index, and what actually happens inside a query.

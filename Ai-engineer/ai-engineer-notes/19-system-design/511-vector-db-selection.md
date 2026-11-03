---

# 511. Vector DB Selection
# हिंदी में: Vector Database का चुनाव

---

## 🔵 Simple Definition (English)
Vector DB selection is choosing where to store embeddings and run nearest-neighbour search. Options include pgvector (inside PostgreSQL), managed services (e.g. Pinecone), and dedicated engines (e.g. Qdrant, Weaviate, Milvus). Choose by scale, filtering needs, ops effort, latency and cost.

## 🔵 सरल परिभाषा (Hindi)
Vector DB selection का मतलब है embeddings कहाँ store हों और nearest-neighbour search कहाँ चले। Options: pgvector (PostgreSQL के अंदर), managed services (जैसे Pinecone), dedicated engines (जैसे Qdrant, Weaviate, Milvus)। चुनाव scale, filtering, ops effort, latency और cost से होता है।

---

## 🔴 Problem it Solves
Brute-force similarity over millions of vectors is slow. Specialised indexes (HNSW, IVF) make search fast but bring trade-offs in memory, filtering and updates. A wrong choice causes slow filtered queries, high bills or painful migrations.

## 🔴 यह क्यों बना? (Hindi)
लाखों vectors पर brute-force search धीमा है। HNSW, IVF जैसे indexes search तेज़ करते हैं पर memory, filtering और updates में trade-off आते हैं। गलत चुनाव से धीमी filtered queries, ऊँचे bills या मुश्किल migration होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Count vectors now and in 2 years; note dimension and update rate
Step 2 → List filters needed (tenant, country, date) and hybrid (keyword) needs
Step 3 → Decide ops model: already on Postgres? small team? need managed?
Step 4 → Shortlist 2-3 (e.g. pgvector, Qdrant, Pinecone) and load-test with YOUR data
Step 5 → Measure recall at target latency, filtered-query latency, ingestion speed
Step 6 → Estimate monthly cost (memory, storage, replicas)
Step 7 → Hide behind a repository interface to keep migration possible
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → अभी और 2 साल बाद के vectors गिनो
Step 2 → ज़रूरी filters (tenant, country, date) और hybrid needs लिखो
Step 3 → Ops model तय करो: Postgres पहले से? छोटी team? managed?
Step 4 → 2-3 shortlist करो और अपने data से load-test करो
Step 5 → Recall, filtered-query latency, ingestion speed मापो
Step 6 → Monthly cost estimate करो
Step 7 → Repository interface के पीछे रखो ताकि migration हो सके
```

---

## 🟡 Real World Example
**Tariff Classification System**: 5M chunks, 1,024-dim, filters by country and tariff year, a team already running PostgreSQL. Start with pgvector (one system, SQL filters, transactions). If filtered recall/latency suffers beyond tens of millions of vectors, move to a dedicated engine such as Qdrant with payload indexes.
**Zomato-style example**: Dish-similarity search with 100k items fits easily in pgvector; no need for a big cluster.

## 🟡 Real Example Hindi mein
**Tariff System**: 5M chunks, 1,024-dim, country और tariff year से filter, team पहले से PostgreSQL चला रही है। pgvector से शुरू करो (एक system, SQL filters, transactions)। दसियों million vectors के बाद filtered latency बिगड़े तो Qdrant जैसे dedicated engine पर जाओ।

---

## 💻 Code Example — Basic
```python
# Basic: a minimal in-memory vector store with metadata filter (pure Python, offline)
import math  # sqrt for cosine


class MiniVectorDB:  # teaching-only store; real DBs use ANN indexes
    def __init__(self) -> None:  # init storage
        self.rows: list[tuple[str, list[float], dict[str, str]]] = []  # (id, vector, metadata)

    def upsert(self, id_: str, vec: list[float], meta: dict[str, str]) -> None:  # insert or replace
        self.rows = [r for r in self.rows if r[0] != id_]  # remove old copy
        self.rows.append((id_, vec, meta))  # add new

    def search(self, q: list[float], k: int = 2, where: dict[str, str] | None = None) -> list[str]:
        def cos(a: list[float], b: list[float]) -> float:  # cosine similarity
            d = sum(x * y for x, y in zip(a, b))  # dot
            n = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))  # norms
            return d / n if n else 0.0  # safe divide
        pool = [r for r in self.rows if not where or all(r[2].get(k_) == v for k_, v in where.items())]  # filter first
        pool.sort(key=lambda r: cos(q, r[1]), reverse=True)  # rank
        return [r[0] for r in pool[:k]]  # ids


db = MiniVectorDB()  # create
db.upsert("a", [1, 0], {"country": "IN"})  # add
db.upsert("b", [0.9, 0.1], {"country": "US"})  # add
print(db.search([1, 0], k=1, where={"country": "US"}))  # ['b']
```

## 💻 Code Example — Advanced
```python
# Advanced: repository interface so the DB can be swapped; async + error handling (mock backend)
import asyncio  # async runtime
from abc import ABC, abstractmethod  # interface
from typing import Optional  # optional type


class VectorRepo(ABC):  # contract every backend must satisfy
    @abstractmethod
    async def upsert(self, id_: str, vec: list[float], meta: dict[str, str]) -> None: ...  # write

    @abstractmethod
    async def query(self, vec: list[float], k: int, filt: Optional[dict[str, str]]) -> list[str]: ...  # read


class MemoryRepo(VectorRepo):  # offline backend for tests
    def __init__(self) -> None:  # storage
        self.data: dict[str, tuple[list[float], dict[str, str]]] = {}  # id -> (vec, meta)

    async def upsert(self, id_: str, vec: list[float], meta: dict[str, str]) -> None:
        self.data[id_] = (vec, meta)  # store

    async def query(self, vec: list[float], k: int, filt: Optional[dict[str, str]]) -> list[str]:
        items = [(i, v) for i, (v, m) in self.data.items()
                 if not filt or all(m.get(a) == b for a, b in filt.items())]  # filter first
        items.sort(key=lambda t: sum(x * y for x, y in zip(vec, t[1])), reverse=True)  # dot-product rank
        return [i for i, _ in items[:k]]  # top ids


async def safe_query(repo: VectorRepo, vec: list[float], retries: int = 2) -> list[str]:  # retry wrapper
    for attempt in range(retries + 1):  # attempts
        try:
            return await asyncio.wait_for(repo.query(vec, 3, {"country": "IN"}), timeout=2)  # guarded
        except (asyncio.TimeoutError, ConnectionError):  # transient errors
            await asyncio.sleep(0.05 * (attempt + 1))  # backoff
    return []  # degrade gracefully


async def main() -> None:  # demo
    repo = MemoryRepo()  # backend
    await repo.upsert("n1", [1.0, 0.0], {"country": "IN"})  # add
    print(await safe_query(repo, [1.0, 0.0]))  # ['n1']


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Inject the repository with `Depends` so tests use the in-memory backend and production uses the real one.

```python
from fastapi import FastAPI, Depends  # app + DI
from pydantic import BaseModel  # schema

app = FastAPI()  # app


class Repo:  # placeholder for the real client wrapper
    async def query(self, vec: list[float], k: int) -> list[str]:  # search
        return ["doc-1", "doc-2"][:k]  # stub


def get_repo() -> Repo:  # dependency provider
    return Repo()  # create once in lifespan for real use


class Q(BaseModel):  # request
    vector: list[float]  # query embedding
    k: int = 5  # results


@app.post("/search")  # route
async def search(q: Q, repo: Repo = Depends(get_repo)) -> dict[str, list[str]]:
    return {"ids": await repo.query(q.vector, q.k)}  # results
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has vector store integrations (e.g. `langchain-postgres` PGVector, `langchain-qdrant`, `langchain-pinecone`) behind a common interface (`as_retriever`).

```python
# Real classes exist for each backend; shown with the in-memory store that ships in langchain-core
from langchain_core.vectorstores import InMemoryVectorStore  # real class
from langchain_core.embeddings import DeterministicFakeEmbedding  # real offline fake embeddings

emb = DeterministicFakeEmbedding(size=16)  # fake embeddings for offline use
vs = InMemoryVectorStore(emb)  # store
vs.add_texts(["smartphone heading 8517", "cotton shirt chapter 61"])  # index
print(vs.similarity_search("phone", k=1))  # search
# Swap InMemoryVectorStore for PGVector/Qdrant/Pinecone without changing retriever code.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Benchmarking with unfiltered queries only
✅ Correct: test with your real filters; filtered ANN can be much slower or lose recall.
```python
# Wrong
latency = bench(db.search(q, k=10))  # no filter
# Right
latency = bench(db.search(q, k=10, filter={"tenant": t}))  # real workload
```

❌ Mistake 2: Hard-coding the vendor SDK across the codebase
✅ Correct: use a repository interface.

---

## 🧠 Tricky Interview Question
**Q**: "Why not just use pgvector for everything, or never use it?"

**Answer**: pgvector is excellent for small to mid scale (up to millions of vectors) with transactional consistency and SQL filters, one less system to run. At very large scale, high write rates or heavy filtered ANN, dedicated engines offer better index options, sharding and tuning. Decide using a load test on your data, not slogans.

---

## ⚫ Interview Questions + Answers

Q1: What is a vector database? (Easy)
A1: A store optimised for similarity search over embeddings, usually with approximate nearest neighbour indexes and metadata filtering.

Q2: What is HNSW? (Easy)
A2: Hierarchical Navigable Small World graph: a graph index giving fast approximate nearest-neighbour search with good recall, at higher memory cost.

Q3: What is the trade-off in ANN? (Medium)
A3: Speed and memory versus recall. Parameters like ef_search or nprobe tune the balance.

Q4: Pre-filter vs post-filter? (Medium)
A4: Post-filter searches first then filters, and may return too few results. Pre/in-filter applies the filter during search; better results but implementation dependent.

Q5: How do you size and cost a deployment? (Hard)
A5: Memory about vectors x dimension x bytes plus index overhead (HNSW graph can add significantly), times replicas. Estimate QPS per node from a load test, add shards for capacity, and consider quantisation or disk-based indexes to cut memory.

---

## 🔷 When to Use + When Not to Use
✅ pgvector when:
- You already use Postgres and scale is moderate

✅ Dedicated/managed when:
- Very large scale, heavy filters, or you want no ops

❌ Avoid when:
- Fewer than a few thousand vectors: a simple in-memory index is enough

---

## 📊 Visual Diagram
```
                 Need?
        ┌──────────┼───────────────┐
   small/Postgres  big + ops team   big + no ops
        │              │                │
     pgvector     Qdrant/Milvus     Managed service
        └──── all behind VectorRepo interface ────┘
```

---

## 💰 Cost Impact
Costs: memory (vectors x dimension x 4 bytes, plus index overhead), replicas, storage and managed-service fees. Example (illustrative): 5M x 1,024 x 4 bytes is about 20 GB raw before index overhead.
Optimise: lower dimension, scalar/product quantisation, store payloads outside the vector index, partition by tenant, delete stale vectors, right-size replicas.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ANN | Approximate nearest neighbour | अनुमानित निकटतम खोज |
| HNSW | Graph index | graph आधारित index |
| Payload/metadata | Extra fields to filter | अतिरिक्त fields |
| Shard | Partition of index | index का हिस्सा |
| Replica | Copy for load/availability | प्रतिलिपि |
| Quantisation | Compress vectors | compression |

---

## ⚡ 3-Line Summary
English: Pick a vector DB using scale, filters, ops capacity and a load test on your data.
Start simple (pgvector) and move only when measurements demand it.
Hide the DB behind an interface to keep migration cheap.
Hindi: Scale, filters, ops क्षमता और अपने data पर load test से vector DB चुनो।
सरल (pgvector) से शुरू करो, measurements कहें तभी बदलो।
DB को interface के पीछे रखो ताकि migration सस्ता रहे।

---

## ➡️ Next Topic
**512. Chunking Strategy Selection** — how to split documents before they go into the DB.
